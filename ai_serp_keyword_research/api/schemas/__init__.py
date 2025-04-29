"""
Schema models for the AI SERP Keyword Research Agent API.

This package contains Pydantic models used for API request/response serialization,
validation, and documentation.
"""

# Import and re-export output models
from ai_serp_keyword_research.api.schemas.output import (
    KeywordOutput,
    IntentAnalysisOutput,
    MarketGapOutput,
    SerpFeatureOutput,
    RecommendationOutput,
    FullAnalysisOutput
)

# Import and re-export request models
from ai_serp_keyword_research.api.schemas.request import (
    AnalyzeRequest,
    FeedbackRequest
)

# Import and re-export response models
from ai_serp_keyword_research.api.schemas.response import (
    AnalyzeResponse,
    FeedbackResponse,
    ErrorResponse,
    HealthResponse
)

__all__ = [
    # Output models
    'KeywordOutput',
    'IntentAnalysisOutput',
    'MarketGapOutput',
    'SerpFeatureOutput',
    'RecommendationOutput',
    'FullAnalysisOutput',
    
    # Request models
    'AnalyzeRequest',
    'FeedbackRequest',
    
    # Response models
    'AnalyzeResponse',
    'FeedbackResponse',
    'ErrorResponse',
    'HealthResponse'
]
