"""
SERP feature extraction tools for the AI SERP Keyword Research Agent.

These tools provide functionality to extract and categorize SERP features
like shopping ads, featured snippets, image packs, etc.
"""

from typing import Dict, Any, List
import re

from agents import function_tool
from pydantic import BaseModel, Field

from ai_serp_keyword_research.core.models.analysis import SerpFeatureType


class SerpFeatureResult(BaseModel):
    """Model representing SERP feature extraction results."""
    features: List[Dict[str, Any]] = Field(..., description="Extracted SERP features")
    feature_count: int = Field(..., description="Total number of features detected")
    has_shopping: bool = Field(..., description="Whether shopping ads are present")
    has_featured_snippet: bool = Field(..., description="Whether a featured snippet is present")
    commercial_features: int = Field(..., description="Count of commercial-oriented features")
    informational_features: int = Field(..., description="Count of information-oriented features")


def extract_feature_data(serp_results: Dict[str, Any], feature_type: str) -> Dict[str, Any]:
    """
    Extract detailed data for a specific SERP feature.
    
    Args:
        serp_results: The SERP data to analyze.
        feature_type: The type of feature to extract data for.
        
    Returns:
        Dictionary containing detailed feature data.
    """
    features = serp_results.get("features", {})
    
    # Default data structure
    feature_data = {
        "position": None,
        "content": None
    }
    
    # Check if the feature exists
    if not features.get(feature_type, False):
        return feature_data
    
    # Depending on feature type, extract appropriate data
    # In a real implementation, this would use the actual SERP API response structure
    if feature_type == "shopping_ads":
        feature_data["position"] = 1  # Usually at the top
        feature_data["content"] = {
            "products": 3,  # Placeholder for number of products
            "has_images": True
        }
    elif feature_type == "featured_snippet":
        feature_data["position"] = 0  # Above regular results
        feature_data["content"] = {
            "type": "paragraph",  # Could be paragraph, list, table, etc.
            "text": "Example featured snippet content"
        }
    elif feature_type == "image_pack":
        feature_data["position"] = 3  # Typical position
        feature_data["content"] = {
            "images": 8,  # Placeholder for number of images
            "has_carousel": True
        }
    elif feature_type == "knowledge_panel":
        feature_data["position"] = 0  # Usually on the right side
        feature_data["content"] = {
            "title": "Example entity",
            "has_images": True
        }
    elif feature_type == "people_also_ask":
        feature_data["position"] = 2  # Typical position
        feature_data["content"] = {
            "questions": ["Example question 1", "Example question 2"]
        }
    
    return feature_data


def categorize_feature(feature_type: str) -> str:
    """
    Categorize a SERP feature as commercial, informational, or navigational.
    
    Args:
        feature_type: The type of feature to categorize.
        
    Returns:
        The category as a string.
    """
    # Categorize features by their typical intent association
    commercial_features = ["shopping_ads", "local_pack", "reviews"]
    informational_features = ["featured_snippet", "people_also_ask", "knowledge_panel", "related_searches"]
    navigational_features = ["sitelinks"]
    
    if feature_type in commercial_features:
        return "commercial"
    elif feature_type in informational_features:
        return "informational"
    elif feature_type in navigational_features:
        return "navigational"
    else:
        return "other"


@function_tool
async def extract_serp_features(serp_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and categorize SERP features from search results.
    
    This tool identifies special features in SERP results like shopping ads,
    featured snippets, image packs, etc., and provides detailed information
    about each feature.
    
    Args:
        serp_results: The SERP data to analyze for features.
        
    Returns:
        Dictionary containing extracted SERP features with positions and details.
    """
    try:
        # Extract features from the raw data
        features_info = serp_results.get("features", {})
        
        # Convert to a standardized format
        extracted_features = []
        commercial_count = 0
        informational_count = 0
        
        # Check for each possible feature type
        for feature_enum in SerpFeatureType:
            feature_type = feature_enum.value
            feature_present = features_info.get(feature_type, False)
            
            if feature_present:
                # Extract detailed data for this feature
                feature_data = extract_feature_data(serp_results, feature_type)
                
                # Categorize the feature
                category = categorize_feature(feature_type)
                
                # Update category counts
                if category == "commercial":
                    commercial_count += 1
                elif category == "informational":
                    informational_count += 1
                
                # Create feature object
                feature = {
                    "feature_type": feature_type,
                    "position": feature_data["position"],
                    "data": feature_data["content"],
                    "category": category
                }
                
                extracted_features.append(feature)
        
        # If features were provided in a different format, this is a fallback
        if not extracted_features and hasattr(features_info, "keys"):
            for feature_type, is_present in features_info.items():
                if is_present and feature_type in [f.value for f in SerpFeatureType]:
                    # Basic feature data without details
                    category = categorize_feature(feature_type)
                    
                    # Update category counts
                    if category == "commercial":
                        commercial_count += 1
                    elif category == "informational":
                        informational_count += 1
                    
                    feature = {
                        "feature_type": feature_type,
                        "position": None,
                        "data": None,
                        "category": category
                    }
                    
                    extracted_features.append(feature)
        
        # Check for specific features
        has_shopping = any(f["feature_type"] == "shopping_ads" for f in extracted_features)
        has_featured_snippet = any(f["feature_type"] == "featured_snippet" for f in extracted_features)
        
        # Create result
        result = SerpFeatureResult(
            features=extracted_features,
            feature_count=len(extracted_features),
            has_shopping=has_shopping,
            has_featured_snippet=has_featured_snippet,
            commercial_features=commercial_count,
            informational_features=informational_count
        )
        
        return result.dict()
    except Exception as e:
        raise ValueError(f"SERP feature extraction failed: {str(e)}") 