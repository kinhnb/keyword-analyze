"""
Recommendation models for the AI SERP Keyword Research Agent.

These models represent the SEO recommendations and tactics generated
based on SERP analysis and market gap detection.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class TacticType(str, Enum):
    """Enumeration of possible SEO tactic types."""
    PRODUCT_PAGE_OPTIMIZATION = "product_page_optimization"
    COLLECTION_PAGE_OPTIMIZATION = "collection_page_optimization"
    CONTENT_CREATION = "content_creation"
    KEYWORD_TARGETING = "keyword_targeting"
    SNIPPET_OPTIMIZATION = "snippet_optimization"
    IMAGE_OPTIMIZATION = "image_optimization"
    PPC_STRATEGY = "ppc_strategy"
    MARKETPLACE_OPTIMIZATION = "marketplace_optimization"
    TECHNICAL_SEO = "technical_seo"
    LINK_BUILDING = "link_building"


class Recommendation(BaseModel):
    """
    Model representing an SEO recommendation or tactic.
    
    Recommendations are actionable tactics that sellers can implement
    to improve their POD graphic tee SEO performance.
    """
    tactic_type: TacticType = Field(..., description="Type of SEO tactic")
    description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Detailed description of the recommendation"
    )
    priority: int = Field(
        ...,
        ge=1,
        le=10,
        description="Priority score (1=highest priority, 10=lowest)"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for this recommendation (0.0 to 1.0)"
    )
    supporting_evidence: Optional[List[str]] = Field(
        None,
        description="Evidence from SERP data that supports this recommendation"
    )
    estimated_effort: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Estimated effort level (1=easy, 5=difficult)"
    )
    
    @validator('description')
    def validate_description(cls, v):
        """Ensure description is actionable and specific."""
        # Check if description contains action words
        action_words = [
            "create", "optimize", "add", "update", "include", "target", 
            "improve", "build", "develop", "implement", "focus"
        ]
        
        if not any(word in v.lower() for word in action_words):
            raise ValueError(
                "Recommendation description must be actionable and include specific steps"
            )
            
        return v
    
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
                ],
                "estimated_effort": 2
            }
        }


class RecommendationSet(BaseModel):
    """
    Model representing a set of prioritized SEO recommendations.
    
    This is typically the final output of the recommendation generation process.
    """
    recommendations: List[Recommendation] = Field(
        ...,
        min_items=1,
        description="List of SEO recommendations"
    )
    intent_based: bool = Field(
        ...,
        description="Whether recommendations are based on search intent"
    )
    market_gap_based: bool = Field(
        ...,
        description="Whether recommendations are based on market gap analysis"
    )
    
    @validator('recommendations')
    def sort_recommendations(cls, v):
        """Sort recommendations by priority (ascending) and confidence (descending)."""
        return sorted(v, key=lambda r: (r.priority, -r.confidence))
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
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
                "intent_based": True,
                "market_gap_based": True
            }
        } 