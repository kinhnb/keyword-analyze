"""
Response models for the AI SERP Keyword Research Agent API.

These models define the structure of responses returned by API endpoints,
ensuring consistent and well-documented response formats.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from ai_serp_keyword_research.api.schemas.output import FullAnalysisOutput


class AnalyzeResponse(BaseModel):
    """
    Response model for the keyword analysis endpoint.
    
    This model structures the response from the /analyze endpoint.
    """
    status: str = Field(..., description="Response status (success or error)")
    data: Optional[FullAnalysisOutput] = Field(None, description="Analysis results")
    error: Optional[str] = Field(None, description="Error message if status is error")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "status": "success",
                "data": {
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
                        }
                    ],
                    "recommendations": [
                        {
                            "tactic_type": "product_page_optimization",
                            "description": "Add 'funny dad shirt' as a primary keyword in product titles",
                            "priority": 1,
                            "confidence": 0.92
                        }
                    ],
                    "execution_time": 2.45
                },
                "error": None
            }
        }


class FeedbackResponse(BaseModel):
    """
    Response model for the analysis feedback endpoint.
    
    This model structures the response from the /feedback endpoint.
    """
    status: str = Field(..., description="Response status (success or error)")
    message: str = Field(..., description="Response message")
    feedback_id: Optional[str] = Field(None, description="Unique identifier for the feedback submission")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Feedback recorded successfully",
                "feedback_id": "fb-12345"
            }
        }


class ErrorResponse(BaseModel):
    """
    Response model for error responses.
    
    This model provides a consistent structure for error responses across all endpoints.
    """
    status: str = Field("error", description="Error status")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "status": "error",
                "error": "Invalid search term",
                "details": {
                    "search_term": "Value must be related to POD graphic tees"
                }
            }
        }


class HealthResponse(BaseModel):
    """
    Response model for the health check endpoint.
    
    This model structures the response from the /health endpoint,
    providing information about the service health and its dependencies.
    """
    status: str = Field(..., description="Service status (healthy, degraded, or unhealthy)")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current server timestamp")
    dependencies: Dict[str, str] = Field(
        ..., 
        description="Status of service dependencies"
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2023-05-01T12:34:56.789Z",
                "dependencies": {
                    "database": "connected",
                    "redis": "connected",
                    "serp_api": "operational"
                }
            }
        } 