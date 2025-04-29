"""
Structured output models for the AI SERP Keyword Research Agent API.

These models represent the structured outputs that are returned by the API endpoints,
ensuring consistent and well-documented response formats.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator

from ai_serp_keyword_research.core.models.analysis import IntentType, SerpFeature


class KeywordOutput(BaseModel):
    """Model representing a keyword with relevance metrics in API responses."""
    text: str = Field(..., description="The keyword text")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0.0-1.0)")
    frequency: int = Field(..., ge=0, description="Frequency count in analyzed results")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "text": "funny dad shirt",
                "relevance": 0.92,
                "frequency": 7
            }
        }


class IntentAnalysisOutput(BaseModel):
    """
    Model representing intent analysis results in API responses.
    
    This model provides a simplified view of the intent analysis
    suitable for API responses.
    """
    intent_type: IntentType = Field(
        ..., 
        description="The classified search intent type"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score for the intent classification (0.0-1.0)"
    )
    main_keyword: KeywordOutput = Field(
        ..., 
        description="The primary keyword identified in the analysis"
    )
    secondary_keywords: List[KeywordOutput] = Field(
        ..., 
        description="Secondary keywords identified in the analysis"
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "intent_type": "transactional",
                "confidence": 0.87,
                "main_keyword": {
                    "text": "funny dad shirt",
                    "relevance": 0.92,
                    "frequency": 7
                },
                "secondary_keywords": [
                    {
                        "text": "father's day tee",
                        "relevance": 0.85,
                        "frequency": 4
                    },
                    {
                        "text": "dad gift shirt",
                        "relevance": 0.78,
                        "frequency": 3
                    }
                ]
            }
        }


class MarketGapOutput(BaseModel):
    """
    Model representing market gap analysis results in API responses.
    
    This model provides information about identified market opportunities
    in a format suitable for API responses.
    """
    detected: bool = Field(
        ..., 
        description="Whether a market gap opportunity was detected"
    )
    description: Optional[str] = Field(
        None, 
        description="Description of the identified market gap"
    )
    opportunity_score: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0, 
        description="Opportunity score for the market gap (0.0-1.0)"
    )
    competition_level: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0, 
        description="Competition level in the identified gap (0.0-1.0)"
    )
    
    @validator('description', 'opportunity_score', 'competition_level')
    def check_fields_when_detected(cls, v, values):
        """Ensure required fields are present when gap is detected."""
        if values.get('detected') and v is None:
            field_name = next(name for name, value in values.items() if value is None)
            raise ValueError(f"{field_name} must be provided when a market gap is detected")
        return v
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "detected": True,
                "description": "Limited personalized dad shirts with profession themes",
                "opportunity_score": 0.76,
                "competition_level": 0.42
            }
        }


class SerpFeatureOutput(BaseModel):
    """
    Model representing SERP features in API responses.
    
    This model provides information about detected SERP features
    in a format suitable for API responses.
    """
    feature_type: str = Field(
        ..., 
        description="Type of SERP feature (e.g., 'shopping_ads', 'featured_snippet')"
    )
    position: Optional[int] = Field(
        None, 
        description="Position of the feature in search results (if applicable)"
    )
    details: Optional[Dict] = Field(
        None, 
        description="Additional details about the feature"
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "feature_type": "shopping_ads",
                "position": 1,
                "details": {
                    "product_count": 6,
                    "has_images": True
                }
            }
        }


class RecommendationOutput(BaseModel):
    """
    Model representing an SEO recommendation in API responses.
    
    This model provides information about a specific SEO tactic
    in a format suitable for API responses.
    """
    tactic_type: str = Field(
        ..., 
        description="Type of SEO tactic"
    )
    description: str = Field(
        ..., 
        description="Detailed description of the recommendation"
    )
    priority: int = Field(
        ..., 
        ge=1, 
        le=10, 
        description="Priority level (1=highest priority, 10=lowest)"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score for the recommendation (0.0-1.0)"
    )
    supporting_evidence: Optional[List[str]] = Field(
        None, 
        description="Evidence supporting the recommendation"
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "tactic_type": "product_page_optimization",
                "description": "Add 'funny dad shirt' as a primary keyword in product titles",
                "priority": 1,
                "confidence": 0.92,
                "supporting_evidence": [
                    "3 of top 5 results use 'funny dad shirt' in title",
                    "58% higher CTR observed for listings with this term"
                ]
            }
        }


class FullAnalysisOutput(BaseModel):
    """
    Model representing the complete analysis result in API responses.
    
    This model combines all components of the SERP analysis into a single
    cohesive response suitable for API endpoints.
    """
    # Metadata
    search_term: str = Field(
        ..., 
        description="The search term that was analyzed"
    )
    analysis_id: str = Field(
        ..., 
        description="Unique identifier for this analysis"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, 
        description="Time when the analysis was completed"
    )
    
    # Analysis components
    intent_analysis: IntentAnalysisOutput = Field(
        ..., 
        description="Intent analysis results"
    )
    market_gap: MarketGapOutput = Field(
        ..., 
        description="Market gap analysis results"
    )
    serp_features: List[SerpFeatureOutput] = Field(
        ..., 
        description="SERP features detected in search results"
    )
    recommendations: List[RecommendationOutput] = Field(
        ..., 
        description="Recommended SEO tactics, sorted by priority"
    )
    
    # Processing metadata
    execution_time: Optional[float] = Field(
        None, 
        description="Total execution time in seconds"
    )
    
    @validator('recommendations')
    def sort_recommendations(cls, v):
        """Sort recommendations by priority (ascending)."""
        return sorted(v, key=lambda r: r.priority)
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "search_term": "funny dad shirt",
                "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2023-05-01T12:34:56.789Z",
                "intent_analysis": {
                    "intent_type": "transactional",
                    "confidence": 0.87,
                    "main_keyword": {
                        "text": "funny dad shirt",
                        "relevance": 0.92,
                        "frequency": 7
                    },
                    "secondary_keywords": [
                        {
                            "text": "father's day tee",
                            "relevance": 0.85,
                            "frequency": 4
                        }
                    ]
                },
                "market_gap": {
                    "detected": True,
                    "description": "Limited personalized dad shirts with profession themes",
                    "opportunity_score": 0.76,
                    "competition_level": 0.42
                },
                "serp_features": [
                    {
                        "feature_type": "shopping_ads",
                        "position": 1,
                        "details": {
                            "product_count": 6
                        }
                    },
                    {
                        "feature_type": "image_pack",
                        "position": 3,
                        "details": {
                            "image_count": 8
                        }
                    }
                ],
                "recommendations": [
                    {
                        "tactic_type": "product_page_optimization",
                        "description": "Add 'funny dad shirt' as a primary keyword in product titles",
                        "priority": 1,
                        "confidence": 0.92
                    },
                    {
                        "tactic_type": "content_creation",
                        "description": "Create a gift guide article targeting 'best gifts for dads'",
                        "priority": 2,
                        "confidence": 0.85
                    }
                ],
                "execution_time": 2.45
            }
        } 