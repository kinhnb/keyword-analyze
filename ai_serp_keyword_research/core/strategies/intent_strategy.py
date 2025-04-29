"""
Intent classification strategies for the SERP analysis pipeline.

This module defines the abstract base class for intent classification strategies
and the strategy factory for creating appropriate strategy instances.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

from ai_serp_keyword_research.core.models.analysis import IntentType

# Configure logging
logger = logging.getLogger(__name__)


class AbstractIntentStrategy(ABC):
    """
    Abstract base class for intent classification strategies.
    
    Implementations should focus on a specific intent type and provide
    specialized analysis logic for that intent.
    """
    
    @property
    @abstractmethod
    def intent_type(self) -> IntentType:
        """Get the intent type this strategy specializes in."""
        pass
    
    @abstractmethod
    async def analyze(self, serp_data: Dict[str, Any], serp_features: List) -> Dict[str, Any]:
        """
        Analyze SERP data to determine if it matches this intent type.
        
        Args:
            serp_data: The SERP response data.
            serp_features: List of detected SERP features.
            
        Returns:
            Dict containing intent_type, confidence, and signals.
        """
        pass
    
    def extract_text_features(self, serp_data: Dict[str, Any]) -> str:
        """
        Extract text features from SERP results for classification.
        
        Args:
            serp_data: The SERP response data.
            
        Returns:
            Combined text from titles and snippets with higher weight for top results.
        """
        results = serp_data.get("organic_results", [])
        # Prioritize top 3 results
        top_results = results[:3] if len(results) >= 3 else results
        
        # Extract text from titles and snippets with higher weight for top results
        text_features = []
        for i, result in enumerate(top_results):
            # Add title and snippet multiple times based on position
            weight = 3 - i if i < 3 else 1
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            for _ in range(weight):
                text_features.append(title)
                text_features.append(snippet)
                
        return " ".join(text_features)


class IntentStrategyFactory:
    """
    Factory for creating intent classification strategies.
    
    This factory determines which strategy to use based on initial
    SERP data analysis or provides a strategy of a specific type.
    """
    
    def __init__(self):
        """Initialize the intent strategy factory with available strategies."""
        self._strategies = {}
        
    def register_strategy(self, strategy: AbstractIntentStrategy) -> None:
        """
        Register a strategy with the factory.
        
        Args:
            strategy: The strategy instance to register.
        """
        self._strategies[strategy.intent_type] = strategy
        
    def create_strategy(self, serp_data: Dict[str, Any]) -> AbstractIntentStrategy:
        """
        Create an appropriate strategy based on initial SERP data analysis.
        
        Args:
            serp_data: The SERP response data.
            
        Returns:
            The most appropriate strategy instance.
        """
        # This is a simple implementation that chooses the most likely strategy
        # based on a basic analysis of the SERP data.
        
        # Count different domain types and signals
        ecommerce_count = 0
        content_count = 0
        exploratory_count = 0
        brand_count = 0
        
        # Analyze top 5 results
        organic_results = serp_data.get("organic_results", [])[:5]
        
        for result in organic_results:
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            
            # Check domain type
            domain = result.get("domain", "")
            
            # E-commerce signals
            if any(shop in domain for shop in ["amazon", "etsy", "ebay", "walmart", "shopify"]):
                ecommerce_count += 1
                
            # Check for transactional terms
            if any(term in title or term in snippet for term in ["buy", "shop", "order", "purchase", "price"]):
                ecommerce_count += 1
                
            # Check for informational terms
            if any(term in title or term in snippet for term in ["how", "what", "why", "guide", "tutorial"]):
                content_count += 1
                
            # Check for exploratory terms
            if any(term in title or term in snippet for term in ["ideas", "inspiration", "examples", "collection"]):
                exploratory_count += 1
                
            # Check for navigational signals
            if any(term in title or term in snippet for term in ["official", "site", "login", "brand", "website"]):
                brand_count += 1
                
        # Determine the most likely intent
        intent_counts = {
            IntentType.TRANSACTIONAL: ecommerce_count,
            IntentType.INFORMATIONAL: content_count,
            IntentType.EXPLORATORY: exploratory_count, 
            IntentType.NAVIGATIONAL: brand_count
        }
        
        most_likely_intent = max(intent_counts.items(), key=lambda x: x[1])[0]
        
        # Return the corresponding strategy
        return self.get_strategy(most_likely_intent)
        
    def get_strategy(self, intent_type: IntentType) -> AbstractIntentStrategy:
        """
        Get a strategy of a specific type.
        
        Args:
            intent_type: The intent type to get a strategy for.
            
        Returns:
            The strategy instance for the specified intent type.
            
        Raises:
            ValueError: If no strategy is registered for the specified intent type.
        """
        if intent_type not in self._strategies:
            raise ValueError(f"No strategy registered for intent type: {intent_type}")
            
        return self._strategies[intent_type] 