"""
Transactional intent classification strategy for SERP analysis.

This module implements the strategy for detecting transactional search intent
in SERP data, focusing on buying signals and e-commerce indicators.
"""

import logging
import re
from typing import Dict, List, Any

from ai_serp_keyword_research.core.models.analysis import IntentType
from ai_serp_keyword_research.core.strategies.intent_strategy import AbstractIntentStrategy

# Configure logging
logger = logging.getLogger(__name__)


class TransactionalIntentStrategy(AbstractIntentStrategy):
    """
    Strategy for detecting transactional (purchase-oriented) search intent.
    
    This strategy analyzes SERP data for signals that indicate a user's
    intention to make a purchase, such as:
    - Shopping ads and product carousels
    - E-commerce domains in results
    - Purchase-related terminology in titles and snippets
    - Price mentions and shop-related terms
    - Product-specific terms for the POD graphic tees niche
    """
    
    @property
    def intent_type(self) -> IntentType:
        return IntentType.TRANSACTIONAL
    
    async def analyze(self, serp_data: Dict[str, Any], serp_features: List) -> Dict[str, Any]:
        """
        Analyze SERP data to determine if it matches transactional intent.
        
        Args:
            serp_data: The SERP response data.
            serp_features: List of detected SERP features.
            
        Returns:
            Dict containing intent_type, confidence, and signals.
        """
        logger.info("Analyzing for transactional intent")
        
        # Initialize signals and confidence score
        signals = []
        confidence = 0.0
        base_score = 0.5  # Start with a moderate confidence
        
        # Extract text features from SERP results
        text_features = self.extract_text_features(serp_data)
        
        # Check for shopping ads (strong transactional signal)
        has_shopping_ads = any(feature.feature_type == "shopping_ads" for feature in serp_features)
        if has_shopping_ads:
            signals.append("Shopping ads present")
            base_score += 0.2  # Strong indicator of transactional intent
        
        # Check for product carousels
        has_product_carousel = any(feature.feature_type == "product_carousel" for feature in serp_features)
        if has_product_carousel:
            signals.append("Product carousel present")
            base_score += 0.15  # Strong indicator of transactional intent
        
        # Analyze organic results
        organic_results = serp_data.get("organic_results", [])
        
        # Count e-commerce domains
        ecommerce_domains = 0
        ecommerce_sites = ["amazon", "etsy", "ebay", "walmart", "shopify", "redbubble", 
                          "teepublic", "teespring", "zazzle", "threadless"]
        
        # POD-specific transaction terms
        pod_transaction_terms = [
            "shirt", "tee", "t-shirt", "t shirt", "tshirt", "apparel", 
            "clothing", "merch", "merchandise", "gift", "buy", "shop", 
            "purchase", "order", "add to cart", "checkout"
        ]
        
        # Check top results
        top_results = organic_results[:5] if len(organic_results) >= 5 else organic_results
        for result in top_results:
            domain = result.get("domain", "").lower()
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            
            # Check for e-commerce domains
            if any(shop in domain for shop in ecommerce_sites):
                ecommerce_domains += 1
                signals.append(f"E-commerce domain detected: {domain}")
            
            # Check for transactional terms in title and snippet
            transaction_terms_detected = []
            for term in pod_transaction_terms:
                if term in title or term in snippet:
                    transaction_terms_detected.append(term)
            
            if transaction_terms_detected:
                terms_str = ", ".join(transaction_terms_detected)
                signals.append(f"Transaction terms in result: {terms_str}")
        
        # Adjust confidence based on e-commerce domain count
        # More weight to domains in top results
        if ecommerce_domains > 0:
            domain_factor = min(ecommerce_domains / len(top_results), 1.0)
            base_score += domain_factor * 0.15
        
        # Check for price patterns in text
        price_pattern = r'\$\d+(?:\.\d{2})?'
        price_matches = re.findall(price_pattern, text_features)
        if price_matches:
            signals.append(f"Price mentions detected: {len(price_matches)} instances")
            base_score += min(len(price_matches) * 0.05, 0.15)  # Cap at 0.15
        
        # Check for POD-specific transactional keywords 
        pod_terms_found = []
        pod_specific_terms = ["graphic tee", "custom shirt", "personalized tee", 
                             "funny shirt", "dad shirt", "mom shirt", "gift shirt"]
        
        for term in pod_specific_terms:
            if term in text_features.lower():
                pod_terms_found.append(term)
        
        if pod_terms_found:
            terms_str = ", ".join(pod_terms_found)
            signals.append(f"POD-specific terms: {terms_str}")
            base_score += min(len(pod_terms_found) * 0.03, 0.15)  # Cap at 0.15
        
        # Normalize confidence score between 0.0 and 0.95
        # Cap at 0.95 to account for uncertainty
        confidence = min(max(base_score, 0.0), 0.95)
        
        logger.info(f"Transactional intent confidence: {confidence:.2f}")
        
        return {
            "intent_type": self.intent_type,
            "confidence": confidence,
            "signals": signals
        } 