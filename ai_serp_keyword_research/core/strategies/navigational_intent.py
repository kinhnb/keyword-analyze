"""
Navigational intent classification strategy for SERP analysis.

This module implements the strategy for detecting navigational search intent
in SERP data, focusing on brand-specific and destination-oriented searches.
"""

import logging
import re
from typing import Dict, List, Any

from ai_serp_keyword_research.core.models.analysis import IntentType
from ai_serp_keyword_research.core.strategies.intent_strategy import AbstractIntentStrategy

# Configure logging
logger = logging.getLogger(__name__)


class NavigationalIntentStrategy(AbstractIntentStrategy):
    """
    Strategy for detecting navigational (destination-focused) search intent.
    
    This strategy analyzes SERP data for signals that indicate a user's
    intention to navigate to a specific website or brand, such as:
    - Brand name mentions in query and results
    - Official website indicators
    - Login/account page references
    - Domain match between query and top results
    - Sitelinks for specific destinations
    - Brand-specific modifiers (official, login, account)
    """
    
    @property
    def intent_type(self) -> IntentType:
        return IntentType.NAVIGATIONAL
    
    async def analyze(self, serp_data: Dict[str, Any], serp_features: List) -> Dict[str, Any]:
        """
        Analyze SERP data to determine if it matches navigational intent.
        
        Args:
            serp_data: The SERP response data.
            serp_features: List of detected SERP features.
            
        Returns:
            Dict containing intent_type, confidence, and signals.
        """
        logger.info("Analyzing for navigational intent")
        
        # Initialize signals and confidence score
        signals = []
        confidence = 0.0
        base_score = 0.5  # Start with a moderate confidence
        
        # Extract text features from SERP results
        text_features = self.extract_text_features(serp_data)
        
        # Get search term from context if available
        search_term = serp_data.get("search_term", "")
        
        # Check for sitelinks (strong navigational signal)
        has_sitelinks = any(feature.feature_type == "sitelinks" for feature in serp_features)
        if has_sitelinks:
            signals.append("Sitelinks present")
            base_score += 0.2  # Strong indicator of navigational intent
        
        # Check for knowledge panel with organization
        has_org_knowledge = any(feature.feature_type == "knowledge_panel" and 
                              feature.feature_data.get("type") == "organization" 
                              for feature in serp_features)
        if has_org_knowledge:
            signals.append("Organization knowledge panel present")
            base_score += 0.15  # Strong indicator of navigational intent
        
        # Analyze organic results
        organic_results = serp_data.get("organic_results", [])
        
        # Navigational terms to look for
        navigational_terms = [
            "official", "login", "sign in", "account", "website", "home page",
            "official site", "store", "shop", "portal", "dashboard", "my account"
        ]
        
        # Brand signals - check for consistent brand/domain match in results
        # This is a strong navigational signal
        top_results = organic_results[:3] if len(organic_results) >= 3 else organic_results
        
        if top_results:
            # Check if there's a dominant domain in top results
            domains = [result.get("domain", "").lower() for result in top_results]
            domain_counts = {}
            
            for domain in domains:
                if domain not in domain_counts:
                    domain_counts[domain] = 0
                domain_counts[domain] += 1
            
            # If the same domain appears in multiple top results, likely navigational
            most_common_domain = max(domain_counts.items(), key=lambda x: x[1]) if domain_counts else (None, 0)
            if most_common_domain[1] >= 2:  # Same domain appears at least twice in top 3
                signals.append(f"Dominant domain in top results: {most_common_domain[0]}")
                base_score += 0.2
                
                # Check if search term contains the domain name (very strong signal)
                if most_common_domain[0] and most_common_domain[0] in search_term.lower():
                    signals.append(f"Search term contains domain name: {most_common_domain[0]}")
                    base_score += 0.2
        
        # Check for navigational terms in results
        for result in top_results:
            domain = result.get("domain", "").lower()
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            url = result.get("url", "").lower()
            
            # Check for navigational terms in title and snippet
            nav_terms_detected = []
            for term in navigational_terms:
                if term in title or term in snippet:
                    nav_terms_detected.append(term)
            
            # Check for login or account pages
            if "/login" in url or "/account" in url or "/signin" in url:
                signals.append(f"Login/account page detected: {domain}")
                base_score += 0.1
            
            if nav_terms_detected:
                terms_str = ", ".join(nav_terms_detected)
                signals.append(f"Navigational terms in result: {terms_str}")
        
        # Check for brand-specific POD sites
        pod_brand_sites = [
            "threadless", "teepublic", "redbubble", "teespring", "bonfire",
            "zazzle", "spreadshirt", "printful", "printify", "cafepress"
        ]
        
        for brand in pod_brand_sites:
            # Check if brand appears in search term and results
            if brand in search_term.lower() and any(brand in result.get("domain", "").lower() 
                                                for result in top_results):
                signals.append(f"Brand match between query and results: {brand}")
                base_score += 0.2
                break
        
        # Look for "official" or similar modifiers
        official_pattern = r'\b(official|authorized|website|homepage)\b'
        if re.search(official_pattern, text_features, re.IGNORECASE):
            signals.append("Official website indicators detected")
            base_score += 0.1
        
        # Normalize confidence score between 0.0 and 0.95
        # Cap at 0.95 to account for uncertainty
        confidence = min(max(base_score, 0.0), 0.95)
        
        logger.info(f"Navigational intent confidence: {confidence:.2f}")
        
        return {
            "intent_type": self.intent_type,
            "confidence": confidence,
            "signals": signals
        } 