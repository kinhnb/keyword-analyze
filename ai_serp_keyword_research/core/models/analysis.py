"""
Analysis models for the AI SERP Keyword Research Agent.

These models represent the core analysis components, including intent analysis,
market gap identification, and SERP features detection.
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator


class IntentType(str, Enum):
    """Enumeration of possible search intent types."""
    TRANSACTIONAL = "transactional"
    INFORMATIONAL = "informational"
    EXPLORATORY = "exploratory"
    NAVIGATIONAL = "navigational"


class SerpFeatureType(str, Enum):
    """Enumeration of possible SERP feature types."""
    SHOPPING_ADS = "shopping_ads"
    FEATURED_SNIPPET = "featured_snippet"
    IMAGE_PACK = "image_pack"
    KNOWLEDGE_PANEL = "knowledge_panel"
    LOCAL_PACK = "local_pack"
    VIDEO_RESULTS = "video_results"
    PEOPLE_ALSO_ASK = "people_also_ask"
    RELATED_SEARCHES = "related_searches"
    REVIEWS = "reviews"
    TOP_STORIES = "top_stories"


class Keyword(BaseModel):
    """Model representing a keyword with relevance score."""
    text: str = Field(..., description="The keyword text")
    relevance: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relevance score of the keyword (0.0 to 1.0)"
    )
    frequency: int = Field(
        ...,
        ge=0,
        description="Number of times this keyword appears in the SERP results"
    )


class SerpFeature(BaseModel):
    """
    Model representing a SERP feature detected in search results.
    
    SERP features are special elements in search results like shopping ads,
    featured snippets, etc.
    """
    feature_type: SerpFeatureType = Field(..., description="Type of SERP feature")
    position: Optional[int] = Field(
        None,
        description="Position of the feature in SERP results (if applicable)"
    )
    data: Optional[Dict] = Field(
        None,
        description="Additional data about the feature (structure varies by type)"
    )
    
    @validator('data')
    def validate_data(cls, v, values):
        """Ensure data is appropriate for the feature type."""
        if not v:
            return v
            
        feature_type = values.get('feature_type')
        
        # Different feature types require different data structures
        if feature_type == SerpFeatureType.FEATURED_SNIPPET:
            if 'content' not in v:
                raise ValueError("Featured snippet data must include 'content'")
        elif feature_type == SerpFeatureType.SHOPPING_ADS:
            if 'products' not in v:
                raise ValueError("Shopping ads data must include 'products'")
                
        return v


class IntentAnalysis(BaseModel):
    """
    Model representing the intent analysis for a search term.
    
    This contains the classified intent type, confidence score, and
    extracted keywords relevant to the intent.
    """
    intent_type: IntentType = Field(..., description="Classified intent type")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for intent classification (0.0 to 1.0)"
    )
    main_keyword: Keyword = Field(..., description="Primary keyword identified")
    secondary_keywords: List[Keyword] = Field(
        ...,
        min_items=0,
        max_items=20,
        description="Secondary keywords identified"
    )
    signals: Optional[List[str]] = Field(
        None,
        description="Signals that influenced the intent classification"
    )
    
    @validator('secondary_keywords')
    def validate_secondary_keywords(cls, v):
        """Ensure secondary keywords are sorted by relevance."""
        return sorted(v, key=lambda k: k.relevance, reverse=True)
    
    @root_validator
    def validate_keywords(cls, values):
        """Ensure main_keyword has higher relevance than secondary_keywords."""
        main_keyword = values.get('main_keyword')
        secondary_keywords = values.get('secondary_keywords')
        
        if main_keyword and secondary_keywords:
            for keyword in secondary_keywords:
                if keyword.relevance > main_keyword.relevance:
                    raise ValueError(
                        "Main keyword must have higher or equal relevance than secondary keywords"
                    )
                    
        return values


class MarketGap(BaseModel):
    """
    Model representing a market gap opportunity identified in SERP analysis.
    
    Market gaps are opportunities where existing content doesn't fully address
    user intent or where there's untapped potential in the market.
    """
    detected: bool = Field(..., description="Whether a market gap was detected")
    description: Optional[str] = Field(
        None,
        description="Description of the detected market gap"
    )
    opportunity_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Score representing the opportunity size (0.0 to 1.0)"
    )
    competition_level: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Score representing the competition level (0.0 to 1.0)"
    )
    related_keywords: Optional[List[Keyword]] = Field(
        None,
        description="Keywords related to the market gap opportunity"
    )
    
    @root_validator
    def validate_market_gap(cls, values):
        """Ensure market gap has appropriate fields when detected."""
        detected = values.get('detected')
        description = values.get('description')
        opportunity_score = values.get('opportunity_score')
        
        if detected and (not description or not opportunity_score):
            raise ValueError(
                "When market gap is detected, description and opportunity_score must be provided"
            )
            
        return values 