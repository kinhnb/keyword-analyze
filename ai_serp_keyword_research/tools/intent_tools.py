"""
Intent classification tools for the AI SERP Keyword Research Agent.

These tools provide functionality to determine search intent based on
SERP data patterns and features.
"""

from typing import Dict, Any, List, Optional
from enum import Enum

from agents import function_tool
from pydantic import BaseModel, Field

# Import the intent strategy interfaces
from ai_serp_keyword_research.core.strategies.intent_strategy import AbstractIntentStrategy
from ai_serp_keyword_research.core.strategies import IntentStrategyFactory, IntentType


class IntentClassificationResult(BaseModel):
    """Model representing intent classification results."""
    intent_type: str = Field(..., description="Classified intent type")
    confidence: float = Field(..., description="Confidence score for the classification")
    signals: List[str] = Field(..., description="Signals supporting the classification")
    commercial_indicators: Optional[float] = Field(None, description="Commercial intent indicators score")
    informational_indicators: Optional[float] = Field(None, description="Informational intent indicators score")


def detect_basic_intent_signals(serp_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect basic intent signals from SERP results.
    
    Args:
        serp_results: The SERP data to analyze.
        
    Returns:
        Dictionary of detected signals.
    """
    signals = {
        "transactional": [],
        "informational": [],
        "exploratory": [],
        "navigational": []
    }
    
    # Extract features
    features = serp_results.get("features", {})
    
    # Extract organic results
    organic_results = serp_results.get("organic_results", [])
    
    # Check for transactional signals
    if features.get("shopping_ads", False):
        signals["transactional"].append("Shopping ads present")
    
    # Check for informational signals
    if features.get("featured_snippet", False):
        signals["informational"].append("Featured snippet present")
    
    if features.get("people_also_ask", False):
        signals["informational"].append("People also ask present")
    
    # Check for exploratory signals
    if features.get("image_pack", False):
        signals["exploratory"].append("Image pack present")
    
    # Check for navigational signals
    # Look for domain dominance (same domain in multiple top results)
    domains = [result.get("domain", "") for result in organic_results if result.get("domain")]
    domain_counter = {}
    for domain in domains:
        domain_counter[domain] = domain_counter.get(domain, 0) + 1
    
    for domain, count in domain_counter.items():
        if count >= 2 and domain:
            signals["navigational"].append(f"Domain dominance: {domain} appears {count} times")
    
    # Check for transactional terms in titles
    transactional_terms = ["buy", "price", "shop", "discount", "sale", "cheap", "purchase"]
    informational_terms = ["how", "what", "why", "guide", "tutorial", "learn", "info"]
    exploratory_terms = ["ideas", "inspiration", "designs", "examples", "collection", "trends"]
    
    for result in organic_results[:5]:  # Check top 5 results
        title = result.get("title", "").lower()
        
        # Check for transactional terms
        for term in transactional_terms:
            if term in title:
                signals["transactional"].append(f"Transactional term in title: '{term}'")
                break
                
        # Check for informational terms
        for term in informational_terms:
            if term in title:
                signals["informational"].append(f"Informational term in title: '{term}'")
                break
                
        # Check for exploratory terms
        for term in exploratory_terms:
            if term in title:
                signals["exploratory"].append(f"Exploratory term in title: '{term}'")
                break
    
    return signals


@function_tool
async def classify_intent(serp_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify search intent based on SERP results.
    
    This tool analyzes SERP data to determine whether the search intent is
    transactional (purchase-oriented), informational (knowledge-seeking),
    exploratory (browsing), or navigational (destination-focused).
    
    Args:
        serp_results: The SERP data to analyze for intent signals.
        
    Returns:
        Dictionary containing intent classification with confidence and supporting signals.
    """
    try:
        # Create factory to get the appropriate strategy
        factory = IntentStrategyFactory.create()
        
        # Extract search term
        search_term = serp_results.get("search_term", "")
        
        # Select appropriate strategy
        strategy = factory.get_strategy(serp_results)
        
        # Perform intent classification using the strategy
        intent_result = strategy.classify_intent(serp_results)
        
        # In case the strategy isn't available or fails, use basic detection as fallback
        if not intent_result:
            # Basic intent classification
            signals = detect_basic_intent_signals(serp_results)
            
            # Count signals for each intent type
            signal_counts = {intent: len(signals_list) for intent, signals_list in signals.items()}
            
            # Determine the most likely intent based on signal count
            max_count = 0
            intent_type = "informational"  # Default to informational
            
            for intent, count in signal_counts.items():
                if count > max_count:
                    max_count = count
                    intent_type = intent
            
            # Calculate confidence based on signal distribution
            total_signals = sum(signal_counts.values())
            confidence = signal_counts[intent_type] / total_signals if total_signals > 0 else 0.5
            
            # Create result
            intent_result = {
                "intent_type": intent_type,
                "confidence": confidence,
                "signals": signals[intent_type]
            }
        
        # Create response
        result = IntentClassificationResult(
            intent_type=intent_result["intent_type"],
            confidence=intent_result["confidence"],
            signals=intent_result.get("signals", []),
            commercial_indicators=intent_result.get("commercial_indicators"),
            informational_indicators=intent_result.get("informational_indicators")
        )
        
        return result.dict()
    except Exception as e:
        # Fallback to basic classification on error
        try:
            signals = detect_basic_intent_signals(serp_results)
            
            # Determine the most likely intent
            intent_type = "informational"  # Default
            max_signals = 0
            
            for intent, signal_list in signals.items():
                if len(signal_list) > max_signals:
                    max_signals = len(signal_list)
                    intent_type = intent
            
            result = IntentClassificationResult(
                intent_type=intent_type,
                confidence=0.6,  # Lower confidence due to fallback
                signals=signals[intent_type],
                commercial_indicators=None,
                informational_indicators=None
            )
            
            return result.dict()
        except:
            # Last resort fallback
            raise ValueError(f"Intent classification failed: {str(e)}") 