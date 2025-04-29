"""
Result models for the AI SERP Keyword Research Agent.

These models represent the final analysis results that combine all components
of the SERP analysis process into a cohesive output.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator, root_validator

from ai_serp_keyword_research.core.models.analysis import IntentAnalysis, MarketGap, SerpFeature
from ai_serp_keyword_research.core.models.recommendations import Recommendation, RecommendationSet


class AnalysisResult(BaseModel):
    """
    Model representing the complete analysis result for a search term.
    
    This is the primary output model that combines intent analysis,
    market gap detection, SERP features, and recommendations.
    """
    # Metadata
    search_term: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="The search term that was analyzed"
    )
    analysis_id: str = Field(..., description="Unique identifier for this analysis")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Time when the analysis was completed"
    )
    
    # Analysis components
    intent_analysis: IntentAnalysis = Field(
        ...,
        description="Intent analysis results"
    )
    market_gap: MarketGap = Field(
        ...,
        description="Market gap analysis results"
    )
    serp_features: List[SerpFeature] = Field(
        ...,
        description="SERP features detected in search results"
    )
    recommendations: RecommendationSet = Field(
        ...,
        description="Recommended SEO tactics"
    )
    
    # Additional data
    raw_data: Optional[Dict] = Field(
        None,
        description="Raw SERP data (if requested)"
    )
    execution_time: Optional[float] = Field(
        None,
        description="Total execution time in seconds"
    )
    
    @validator('serp_features')
    def sort_serp_features(cls, v):
        """Sort SERP features by position if available."""
        # Sort features with position first, then those without position
        sorted_features = sorted(
            [f for f in v if f.position is not None],
            key=lambda f: f.position
        )
        sorted_features.extend([f for f in v if f.position is None])
        return sorted_features
    
    @root_validator
    def validate_consistency(cls, values):
        """Ensure consistency between different analysis components."""
        intent_analysis = values.get('intent_analysis')
        market_gap = values.get('market_gap')
        recommendations = values.get('recommendations')
        
        if intent_analysis and recommendations:
            # Verify recommendations align with intent type
            intent_type = intent_analysis.intent_type
            recommendations_intent_based = recommendations.intent_based
            
            if not recommendations_intent_based:
                raise ValueError("Recommendations must be based on detected intent")
                
        if market_gap and recommendations:
            # If market gap detected, recommendations should reflect that
            market_gap_detected = market_gap.detected
            recommendations_gap_based = recommendations.market_gap_based
            
            if market_gap_detected and not recommendations_gap_based:
                raise ValueError("When market gap detected, recommendations should address it")
                
        return values
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "search_term": "funny dad graphic tee",
                "analysis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "timestamp": "2025-04-10T12:34:56Z",
                "intent_analysis": {
                    "intent_type": "transactional",
                    "confidence": 0.87,
                    "main_keyword": {
                        "text": "dad graphic tee",
                        "relevance": 0.95,
                        "frequency": 8
                    },
                    "secondary_keywords": [
                        {
                            "text": "funny dad shirt",
                            "relevance": 0.85,
                            "frequency": 5
                        }
                    ]
                },
                "market_gap": {
                    "detected": True,
                    "description": "Limited personalized dad shirts with profession themes",
                    "opportunity_score": 0.75,
                    "competition_level": 0.4
                },
                "serp_features": [
                    {
                        "feature_type": "shopping_ads",
                        "position": 1,
                        "data": {
                            "products": 3
                        }
                    }
                ],
                "recommendations": {
                    "recommendations": [
                        {
                            "tactic_type": "product_page_optimization",
                            "description": "Create product pages targeting 'profession + dad shirt' keywords",
                            "priority": 1,
                            "confidence": 0.85
                        }
                    ],
                    "intent_based": True,
                    "market_gap_based": True
                },
                "execution_time": 2.34
            }
        } 