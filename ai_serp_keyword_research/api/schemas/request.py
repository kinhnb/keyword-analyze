"""
Request models for the AI SERP Keyword Research Agent API.

These models are used to validate and structure incoming requests to API endpoints,
ensuring proper input validation and consistent error handling.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator


class AnalyzeRequest(BaseModel):
    """
    Request model for the keyword analysis endpoint.
    
    This model validates and structures the request body for the /analyze endpoint.
    """
    search_term: str = Field(
        ..., 
        min_length=3, 
        max_length=255, 
        description="The search term to analyze"
    )
    max_results: Optional[int] = Field(
        10, 
        ge=1, 
        le=100, 
        description="Maximum number of SERP results to analyze"
    )
    include_raw_data: Optional[bool] = Field(
        False, 
        description="Whether to include raw SERP data in the response"
    )
    
    @validator('search_term')
    def validate_search_term(cls, v):
        """Validate and normalize the search term."""
        v = v.strip()
        
        # Basic validation
        if not v:
            raise ValueError("Search term cannot be empty")
        
        # Simple check for POD graphic tee relevance
        pod_related_terms = ["shirt", "tee", "t-shirt", "graphic", "print", "design", "pod", "apparel"]
        if not any(term in v.lower() for term in pod_related_terms):
            raise ValueError(
                "Search term should be related to Print-on-Demand graphic tees. "
                "Consider adding terms like 'shirt', 'tee', or 'graphic' to your query."
            )
        
        return v
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "search_term": "funny dad graphic tee",
                "max_results": 10,
                "include_raw_data": False
            }
        }


class FeedbackRequest(BaseModel):
    """
    Request model for the analysis feedback endpoint.
    
    This model validates and structures the request body for the /feedback endpoint,
    which is used to collect user feedback on analysis results.
    """
    analysis_id: str = Field(
        ..., 
        description="Unique identifier of the analysis being rated"
    )
    rating: int = Field(
        ..., 
        ge=1, 
        le=5, 
        description="User rating (1-5, where 5 is best)"
    )
    comments: Optional[str] = Field(
        None, 
        max_length=1000, 
        description="Optional feedback comments"
    )
    helpful_recommendations: Optional[List[str]] = Field(
        None, 
        description="IDs of recommendations found particularly helpful"
    )
    unhelpful_recommendations: Optional[List[str]] = Field(
        None, 
        description="IDs of recommendations found unhelpful"
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
                "rating": 4,
                "comments": "Good recommendations but missed some keywords",
                "helpful_recommendations": ["rec-001", "rec-003"],
                "unhelpful_recommendations": ["rec-002"]
            }
        } 