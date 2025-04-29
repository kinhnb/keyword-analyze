"""
Intent analysis stage for the SERP analysis pipeline.

This module implements the third stage of the pipeline, which analyzes
SERP data to determine search intent and extract relevant keywords.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple

from ai_serp_keyword_research.core.models.analysis import IntentAnalysis, IntentType, Keyword
from ai_serp_keyword_research.core.pipeline.base import PipelineContext, PipelineStage

# Configure logging
logger = logging.getLogger(__name__)


class IntentAnalysisStage(PipelineStage[Dict[str, Any], IntentAnalysis]):
    """
    Third stage of the SERP analysis pipeline.
    
    This stage is responsible for:
    1. Extracting main and secondary keywords
    2. Analyzing result patterns to determine intent
    3. Classifying intent as transactional, informational, exploratory, or navigational
    4. Assigning a confidence score to the classification
    """
    
    def __init__(self, intent_strategy_factory=None):
        """
        Initialize the intent analysis stage.
        
        Args:
            intent_strategy_factory: Factory for creating intent classification strategies.
                                    If None, basic classification will be used.
        """
        self._intent_strategy_factory = intent_strategy_factory
        
    @property
    def name(self) -> str:
        return "Intent Analysis Stage"
        
    async def process(self, input_data: Dict[str, Any], context: Optional[PipelineContext] = None) -> IntentAnalysis:
        """
        Process SERP data to determine search intent and extract keywords.
        
        Args:
            input_data: The SERP data from the previous stage.
            context: Optional pipeline context for sharing state.
            
        Returns:
            Intent analysis results.
        """
        if context is None:
            context = PipelineContext()
            
        search_term = context.get("normalized_term", "")
        serp_data = input_data
        serp_features = context.get("serp_features", [])
        
        logger.info(f"Analyzing intent for search term: {search_term}")
        
        # Extract keywords from SERP data
        main_keyword, secondary_keywords = await self._extract_keywords(serp_data, search_term)
        
        # Determine intent type and confidence
        # If we have a strategy factory, use it to get the appropriate strategy
        intent_type, confidence, signals = None, 0.0, []
        
        if self._intent_strategy_factory:
            # Use the factory to create a strategy based on initial analysis
            strategy = self._intent_strategy_factory.create_strategy(serp_data)
            intent_analysis = await strategy.analyze(serp_data, serp_features)
            intent_type = intent_analysis.get("intent_type")
            confidence = intent_analysis.get("confidence", 0.0)
            signals = intent_analysis.get("signals", [])
        else:
            # Fallback to basic intent classification
            intent_type, confidence, signals = self._basic_intent_classification(serp_data, serp_features)
            
        # Create and return the intent analysis
        intent_analysis = IntentAnalysis(
            intent_type=intent_type,
            confidence=confidence,
            main_keyword=main_keyword,
            secondary_keywords=secondary_keywords,
            signals=signals
        )
        
        # Store in context
        context.set("intent_analysis", intent_analysis)
        
        return intent_analysis
        
    async def _extract_keywords(self, serp_data: Dict[str, Any], search_term: str) -> Tuple[Keyword, List[Keyword]]:
        """
        Extract main and secondary keywords from SERP data.
        
        Args:
            serp_data: The SERP response data.
            search_term: The original search term.
            
        Returns:
            Tuple containing the main keyword and list of secondary keywords.
        """
        # This is a simplified implementation
        # A more sophisticated approach would use NLP and frequency analysis
        
        # Extract all titles and descriptions from organic results
        organic_results = serp_data.get("organic_results", [])
        
        all_text = search_term + " "  # Start with the search term
        
        for result in organic_results:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            all_text += f" {title} {snippet}"
            
        # Extract and count keywords
        keyword_frequency = {}
        
        # Simple tokenization and counting
        # In a real implementation, this would use more sophisticated NLP techniques
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        for word in words:
            if word not in keyword_frequency:
                keyword_frequency[word] = 0
            keyword_frequency[word] += 1
            
        # Filter out common stop words
        stop_words = {"and", "the", "for", "with", "this", "that", "from", "have", "not"}
        keyword_frequency = {k: v for k, v in keyword_frequency.items() if k not in stop_words}
        
        # Sort by frequency
        keywords_sorted = sorted(keyword_frequency.items(), key=lambda x: x[1], reverse=True)
        
        # For the main keyword, use the original search term or the most frequent keyword
        main_keyword_text = search_term
        main_keyword_freq = keyword_frequency.get(search_term.lower(), 0)
        main_keyword_relevance = 1.0  # Highest relevance for main keyword
        
        # Create the main keyword
        main_keyword = Keyword(
            text=main_keyword_text,
            relevance=main_keyword_relevance,
            frequency=main_keyword_freq
        )
        
        # Create secondary keywords (exclude the main keyword)
        secondary_keywords = []
        
        keyword_count = 0
        for keyword, frequency in keywords_sorted:
            if keyword != main_keyword_text.lower() and keyword_count < 10:
                # Normalize relevance between 0.5 and 0.95 based on frequency
                max_freq = keywords_sorted[0][1] if keywords_sorted else 1
                relevance = 0.5 + (0.45 * (frequency / max_freq))
                
                secondary_keywords.append(
                    Keyword(
                        text=keyword,
                        relevance=relevance,
                        frequency=frequency
                    )
                )
                keyword_count += 1
                
        return main_keyword, secondary_keywords
        
    def _basic_intent_classification(self, serp_data: Dict[str, Any], serp_features: List) -> Tuple[IntentType, float, List[str]]:
        """
        Perform basic intent classification based on SERP data.
        
        Args:
            serp_data: The SERP response data.
            serp_features: List of detected SERP features.
            
        Returns:
            Tuple of (intent_type, confidence, signals).
        """
        # Initialize counters for each intent type
        transactional_signals = []
        informational_signals = []
        exploratory_signals = []
        navigational_signals = []
        
        # Check for shopping ads (strong transactional signal)
        has_shopping_ads = any(feature.feature_type == "shopping_ads" for feature in serp_features)
        if has_shopping_ads:
            transactional_signals.append("Shopping ads present")
            
        # Check for featured snippets (informational signal)
        has_featured_snippet = any(feature.feature_type == "featured_snippet" for feature in serp_features)
        if has_featured_snippet:
            informational_signals.append("Featured snippet present")
            
        # Check for image packs (exploratory signal)
        has_image_pack = any(feature.feature_type == "image_pack" for feature in serp_features)
        if has_image_pack:
            exploratory_signals.append("Image pack present")
            
        # Analyze organic results
        organic_results = serp_data.get("organic_results", [])
        
        # Count different domain types
        ecommerce_domains = 0
        content_domains = 0
        brand_domains = 0
        
        for result in organic_results:
            domain = result.get("domain", "")
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            
            # Check for transactional signals
            if any(term in title or term in snippet for term in ["buy", "shop", "order", "purchase", "price"]):
                transactional_signals.append(f"Transaction terms in result: {domain}")
                ecommerce_domains += 1
                
            # Check for informational signals
            if any(term in title or term in snippet for term in ["how", "what", "why", "guide", "tutorial"]):
                informational_signals.append(f"Informational terms in result: {domain}")
                content_domains += 1
                
            # Check for exploratory signals
            if any(term in title or term in snippet for term in ["ideas", "inspiration", "examples", "collection"]):
                exploratory_signals.append(f"Exploratory terms in result: {domain}")
                
            # Check for navigational signals (specific brand mentions)
            if re.search(r'official|brand|website', title.lower() + " " + snippet.lower()):
                navigational_signals.append(f"Brand terms in result: {domain}")
                brand_domains += 1
                
        # Determine the dominant intent
        intent_signals = {
            IntentType.TRANSACTIONAL: len(transactional_signals),
            IntentType.INFORMATIONAL: len(informational_signals),
            IntentType.EXPLORATORY: len(exploratory_signals),
            IntentType.NAVIGATIONAL: len(navigational_signals)
        }
        
        # Find the intent with the most signals
        dominant_intent = max(intent_signals.items(), key=lambda x: x[1])
        intent_type = dominant_intent[0]
        
        # Calculate confidence based on signal strength
        total_signals = sum(intent_signals.values())
        confidence = dominant_intent[1] / total_signals if total_signals > 0 else 0.5
        
        # Cap confidence at 0.95
        confidence = min(confidence, 0.95)
        
        # Collect all signals for the dominant intent
        if intent_type == IntentType.TRANSACTIONAL:
            signals = transactional_signals
        elif intent_type == IntentType.INFORMATIONAL:
            signals = informational_signals
        elif intent_type == IntentType.EXPLORATORY:
            signals = exploratory_signals
        else:
            signals = navigational_signals
            
        return intent_type, confidence, signals 