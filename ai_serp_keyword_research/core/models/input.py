"""
Input models for the AI SERP Keyword Research Agent.

These models are used to validate and structure input data coming into the system,
such as search terms for analysis.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator


class SearchTerm(BaseModel):
    """
    Model representing a search term for SERP analysis.
    
    This is the primary input model used when users request analysis
    of a specific search term related to POD graphic tees.
    """
    term: str = Field(
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
    
    @validator('term')
    def validate_term(cls, v):
        """Validate that the search term contains no harmful content."""
        v = v.strip()
        
        # Basic validation - in real implementation, this would be more robust
        if not v:
            raise ValueError("Search term cannot be empty")
        
        # Ensure the term is related to POD graphic tees in some way
        # This is a simplified check; real implementation would be more sophisticated
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
                "term": "funny dad graphic tee",
                "max_results": 10
            }
        } 