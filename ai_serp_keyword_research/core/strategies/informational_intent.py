"""
Informational intent classification strategy for SERP analysis.

This module implements the strategy for detecting informational search intent
in SERP data, focusing on knowledge-seeking signals and educational content.
"""

import logging
import re
from typing import Dict, List, Any

from ai_serp_keyword_research.core.models.analysis import IntentType
from ai_serp_keyword_research.core.strategies.intent_strategy import AbstractIntentStrategy

# Configure logging
logger = logging.getLogger(__name__)


class InformationalIntentStrategy(AbstractIntentStrategy):
    """
    Strategy for detecting informational (knowledge-seeking) search intent.
    
    This strategy analyzes SERP data for signals that indicate a user's
    intention to find information or learn about a topic, such as:
    - Featured snippets and knowledge panels
    - "People also ask" sections
    - How-to and guide content in results
    - Educational domains in results
    - Question-based queries and responses
    - Informational terminology in titles and snippets
    """
    
    @property
    def intent_type(self) -> IntentType:
        return IntentType.INFORMATIONAL
    
    async def analyze(self, serp_data: Dict[str, Any], serp_features: List) -> Dict[str, Any]:
        """
        Analyze SERP data to determine if it matches informational intent.
        
        Args:
            serp_data: The SERP response data.
            serp_features: List of detected SERP features.
            
        Returns:
            Dict containing intent_type, confidence, and signals.
        """
        logger.info("Analyzing for informational intent")
        
        # Initialize signals and confidence score
        signals = []
        confidence = 0.0
        base_score = 0.5  # Start with a moderate confidence
        
        # Extract text features from SERP results
        text_features = self.extract_text_features(serp_data)
        
        # Check for featured snippets (strong informational signal)
        has_featured_snippet = any(feature.feature_type == "featured_snippet" for feature in serp_features)
        if has_featured_snippet:
            signals.append("Featured snippet present")
            base_score += 0.2  # Strong indicator of informational intent
        
        # Check for knowledge panel
        has_knowledge_panel = any(feature.feature_type == "knowledge_panel" for feature in serp_features)
        if has_knowledge_panel:
            signals.append("Knowledge panel present")
            base_score += 0.15  # Strong indicator of informational intent
        
        # Check for "people also ask" boxes
        has_related_questions = any(feature.feature_type == "related_questions" for feature in serp_features)
        if has_related_questions:
            signals.append("People also ask present")
            base_score += 0.15  # Strong indicator of informational intent
        
        # Analyze organic results
        organic_results = serp_data.get("organic_results", [])
        
        # Count informational domains
        informational_domains = 0
        info_sites = [
            "wikipedia", "quora", "medium", "blog", "reddit", ".edu", ".gov", 
            "howto", "guide", "tutorial", "learn", "article", "knowledge"
        ]
        
        # Informational terms to look for
        info_terms = [
            "what is", "how to", "guide", "tutorial", "tips", "advice", 
            "explained", "understanding", "meanings", "information about", 
            "benefits of", "definition", "differences between", "ideas for"
        ]
        
        # Check top results
        top_results = organic_results[:5] if len(organic_results) >= 5 else organic_results
        for result in top_results:
            domain = result.get("domain", "").lower()
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            
            # Check for informational domains
            if any(info_site in domain for info_site in info_sites):
                informational_domains += 1
                signals.append(f"Informational domain detected: {domain}")
            
            # Check for informational terms in title and snippet
            info_terms_detected = []
            for term in info_terms:
                if term in title or term in snippet:
                    info_terms_detected.append(term)
            
            if info_terms_detected:
                terms_str = ", ".join(info_terms_detected)
                signals.append(f"Informational terms in result: {terms_str}")
        
        # Adjust confidence based on informational domain count
        if informational_domains > 0:
            domain_factor = min(informational_domains / len(top_results), 1.0)
            base_score += domain_factor * 0.15
        
        # Check for POD graphic tee informational patterns
        pod_info_terms = [
            "best graphic tees", "graphic tee style guide", "how to style graphic tees",
            "types of graphic tees", "graphic tee care", "t-shirt printing methods",
            "graphic tee trends", "t-shirt materials", "history of graphic tees"
        ]
        
        pod_info_found = []
        for term in pod_info_terms:
            if term in text_features.lower():
                pod_info_found.append(term)
        
        if pod_info_found:
            terms_str = ", ".join(pod_info_found)
            signals.append(f"POD informational terms: {terms_str}")
            base_score += min(len(pod_info_found) * 0.03, 0.15)  # Cap at 0.15
        
        # Check for question patterns in text
        question_pattern = r'\b(what|how|why|when|where|which|who)\b.*\?'
        question_matches = re.findall(question_pattern, text_features, re.IGNORECASE)
        if question_matches:
            signals.append(f"Question patterns detected: {len(question_matches)} instances")
            base_score += min(len(question_matches) * 0.05, 0.15)  # Cap at 0.15
        
        # Normalize confidence score between 0.0 and 0.95
        # Cap at 0.95 to account for uncertainty
        confidence = min(max(base_score, 0.0), 0.95)
        
        logger.info(f"Informational intent confidence: {confidence:.2f}")
        
        return {
            "intent_type": self.intent_type,
            "confidence": confidence,
            "signals": signals
        } 