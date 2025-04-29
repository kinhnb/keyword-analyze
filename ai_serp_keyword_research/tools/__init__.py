"""
Function tools for the AI SERP Keyword Research Agent.

These tools provide specialized capabilities for the agent system to perform
SERP analysis, intent classification, and recommendation generation.
"""

from ai_serp_keyword_research.tools.serp_tools import fetch_serp_data
from ai_serp_keyword_research.tools.keyword_tools import analyze_keywords
from ai_serp_keyword_research.tools.intent_tools import classify_intent
from ai_serp_keyword_research.tools.pattern_tools import detect_serp_patterns
from ai_serp_keyword_research.tools.market_tools import detect_market_gap
from ai_serp_keyword_research.tools.feature_tools import extract_serp_features
from ai_serp_keyword_research.tools.recommendation_tools import (
    generate_recommendations,
    prioritize_tactics,
    format_recommendations
)

__all__ = [
    'fetch_serp_data',
    'analyze_keywords',
    'classify_intent',
    'detect_serp_patterns',
    'detect_market_gap',
    'extract_serp_features',
    'generate_recommendations',
    'prioritize_tactics',
    'format_recommendations'
]
