"""
Exploratory intent classification strategy for SERP analysis.

This module implements the strategy for detecting exploratory search intent
in SERP data, focusing on browsing signals and discovery-oriented content.
"""

import logging
import re
from typing import Dict, List, Any

from ai_serp_keyword_research.core.models.analysis import IntentType
from ai_serp_keyword_research.core.strategies.intent_strategy import AbstractIntentStrategy

# Configure logging
logger = logging.getLogger(__name__)


class ExploratoryIntentStrategy(AbstractIntentStrategy):
    """
    Strategy for detecting exploratory (browsing/discovery) search intent.
    
    This strategy analyzes SERP data for signals that indicate a user's
    intention to browse and discover options, such as:
    - Image packs and visual content
    - Collection and category pages
    - List-based content (best, top, trending)
    - Variety of options in results
    - Inspiration and idea terminology
    - Multiple product categories
    """
    
    @property
    def intent_type(self) -> IntentType:
        return IntentType.EXPLORATORY
    
    async def analyze(self, serp_data: Dict[str, Any], serp_features: List) -> Dict[str, Any]:
        """
        Analyze SERP data to determine if it matches exploratory intent.
        
        Args:
            serp_data: The SERP response data.
            serp_features: List of detected SERP features.
            
        Returns:
            Dict containing intent_type, confidence, and signals.
        """
        logger.info("Analyzing for exploratory intent")
        
        # Initialize signals and confidence score
        signals = []
        confidence = 0.0
        base_score = 0.5  # Start with a moderate confidence
        
        # Extract text features from SERP results
        text_features = self.extract_text_features(serp_data)
        
        # Check for image packs (strong exploratory signal)
        has_image_pack = any(feature.feature_type == "image_pack" for feature in serp_features)
        if has_image_pack:
            signals.append("Image pack present")
            base_score += 0.2  # Strong indicator of exploratory intent
        
        # Check for visual shopping results
        has_visual_shopping = any(feature.feature_type == "visual_shopping" for feature in serp_features)
        if has_visual_shopping:
            signals.append("Visual shopping results present")
            base_score += 0.15  # Strong indicator of exploratory intent
        
        # Check for collection-type SERP features
        has_collections = any(feature.feature_type in ["collection_carousel", "popular_products"] 
                             for feature in serp_features)
        if has_collections:
            signals.append("Collection-style features present")
            base_score += 0.15  # Strong indicator of exploratory intent
        
        # Analyze organic results
        organic_results = serp_data.get("organic_results", [])
        
        # Exploratory terms to look for
        exploratory_terms = [
            "ideas", "inspiration", "collection", "gallery", "examples", 
            "trends", "trending", "popular", "best", "top", "curated", 
            "discover", "explore", "browse", "variety", "selection", "options"
        ]
        
        # List/collection patterns
        list_patterns = [
            r'\b\d+\s+best\b', r'\b\d+\s+top\b', r'\btop\s+\d+\b', r'\bbest\s+\d+\b',
            r'\bcollection\b', r'\bgallery\b', r'\btrending\b'
        ]
        
        # POD-specific exploratory terms
        pod_exploratory_terms = [
            "graphic tee ideas", "t-shirt collection", "shirt designs",
            "tee styles", "graphic tee trends", "trending designs",
            "popular graphic tees", "best graphic tees", "unique tees",
            "custom tee options", "tee inspiration"
        ]
        
        # Count exploratory signals in results
        exploratory_domains = 0
        top_results = organic_results[:5] if len(organic_results) >= 5 else organic_results
        
        for result in top_results:
            domain = result.get("domain", "").lower()
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            
            # Check for exploratory terms in title and snippet
            exp_terms_detected = []
            for term in exploratory_terms:
                if term in title or term in snippet:
                    exp_terms_detected.append(term)
            
            # Check for list/collection patterns
            list_matches = []
            for pattern in list_patterns:
                if re.search(pattern, title, re.IGNORECASE) or re.search(pattern, snippet, re.IGNORECASE):
                    list_matches.append(pattern)
            
            # Look for collection or category pages
            if "/collection" in result.get("url", "") or "/category" in result.get("url", ""):
                exploratory_domains += 1
                signals.append(f"Collection/category page detected: {domain}")
            
            if exp_terms_detected:
                terms_str = ", ".join(exp_terms_detected)
                signals.append(f"Exploratory terms in result: {terms_str}")
            
            if list_matches:
                signals.append(f"List/collection pattern in result: {domain}")
        
        # Check for POD-specific exploratory patterns
        pod_exp_found = []
        for term in pod_exploratory_terms:
            if term in text_features.lower():
                pod_exp_found.append(term)
        
        if pod_exp_found:
            terms_str = ", ".join(pod_exp_found)
            signals.append(f"POD exploratory terms: {terms_str}")
            base_score += min(len(pod_exp_found) * 0.03, 0.15)  # Cap at 0.15
        
        # Check for diversity in results (different domains, different types of pages)
        # This indicates an exploratory search
        unique_domains = len(set([result.get("domain", "") for result in top_results]))
        domain_diversity_score = unique_domains / len(top_results) if top_results else 0
        
        if domain_diversity_score > 0.6:  # If more than 60% of results are from different domains
            signals.append(f"High domain diversity: {unique_domains} unique domains")
            base_score += 0.1
        
        # Normalize confidence score between 0.0 and 0.95
        # Cap at 0.95 to account for uncertainty
        confidence = min(max(base_score, 0.0), 0.95)
        
        logger.info(f"Exploratory intent confidence: {confidence:.2f}")
        
        return {
            "intent_type": self.intent_type,
            "confidence": confidence,
            "signals": signals
        } 