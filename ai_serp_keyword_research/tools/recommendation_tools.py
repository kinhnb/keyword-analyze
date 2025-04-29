"""
Recommendation generation tools for the AI SERP Keyword Research Agent.

These tools provide functionality to generate, prioritize, and format
SEO recommendations based on SERP analysis and market gap detection.
"""

from typing import Dict, Any, List, Optional
import re

from agents import function_tool
from pydantic import BaseModel, Field

from ai_serp_keyword_research.core.models.recommendations import TacticType


class RecommendationGenerationResult(BaseModel):
    """Model representing recommendation generation results."""
    recommendations: List[Dict[str, Any]] = Field(..., description="Generated recommendations")
    intent_based: bool = Field(..., description="Whether recommendations are based on search intent")
    market_gap_based: bool = Field(..., description="Whether recommendations are based on market gaps")


def generate_intent_recommendations(intent_analysis: Dict[str, Any], serp_features: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate intent-specific recommendations based on intent analysis.
    
    Args:
        intent_analysis: The intent analysis data.
        serp_features: The SERP features data.
        
    Returns:
        List of recommendations.
    """
    recommendations = []
    intent_type = intent_analysis.get("intent_type", "").lower()
    
    # Default to informational if intent_type is missing
    if not intent_type:
        intent_type = "informational"
    
    # Transactional intent recommendations
    if intent_type == "transactional":
        # Product page optimization
        recommendations.append({
            "tactic_type": TacticType.PRODUCT_PAGE_OPTIMIZATION.value,
            "description": f"Optimize product titles to include '{intent_analysis.get('main_keyword', {}).get('text', 'main keyword')}' near the beginning.",
            "priority": 1,
            "confidence": 0.9,
            "supporting_evidence": ["Transactional intent detected with high confidence"]
        })
        
        # Check if shopping ads are present
        if serp_features.get("has_shopping", False):
            recommendations.append({
                "tactic_type": TacticType.PPC_STRATEGY.value,
                "description": "Create shopping ads targeting the primary keyword, highlighting price and unique POD features.",
                "priority": 2,
                "confidence": 0.85,
                "supporting_evidence": ["Shopping ads present in SERP"]
            })
        
        # Secondary keywords optimization
        secondary_keywords = intent_analysis.get("secondary_keywords", [])
        if secondary_keywords:
            recommendations.append({
                "tactic_type": TacticType.KEYWORD_TARGETING.value,
                "description": f"Include secondary keywords ({', '.join([kw.get('text', '') for kw in secondary_keywords[:3]])}) in product descriptions.",
                "priority": 3,
                "confidence": 0.8,
                "supporting_evidence": ["Secondary keywords identified with good relevance scores"]
            })
        
        # Marketplace recommendations
        recommendations.append({
            "tactic_type": TacticType.MARKETPLACE_OPTIMIZATION.value,
            "description": "Optimize marketplace listings (Etsy, Amazon, etc.) with the primary keyword and transactional terms.",
            "priority": 4,
            "confidence": 0.8,
            "supporting_evidence": ["Transactional intent indicates marketplace optimization opportunity"]
        })
    
    # Informational intent recommendations
    elif intent_type == "informational":
        # Content creation
        recommendations.append({
            "tactic_type": TacticType.CONTENT_CREATION.value,
            "description": f"Create an informational blog post about '{intent_analysis.get('main_keyword', {}).get('text', 'main keyword')}' with helpful content.",
            "priority": 1,
            "confidence": 0.9,
            "supporting_evidence": ["Informational intent detected with high confidence"]
        })
        
        # Check if featured snippet is present
        if serp_features.get("has_featured_snippet", False):
            recommendations.append({
                "tactic_type": TacticType.SNIPPET_OPTIMIZATION.value,
                "description": "Create structured content designed to capture the featured snippet position.",
                "priority": 2,
                "confidence": 0.85,
                "supporting_evidence": ["Featured snippet present in SERP"]
            })
        
        # Secondary keywords for content
        secondary_keywords = intent_analysis.get("secondary_keywords", [])
        if secondary_keywords:
            recommendations.append({
                "tactic_type": TacticType.CONTENT_CREATION.value,
                "description": f"Create supporting content around secondary topics ({', '.join([kw.get('text', '') for kw in secondary_keywords[:3]])}).",
                "priority": 3,
                "confidence": 0.8,
                "supporting_evidence": ["Secondary keywords identified with good relevance scores"]
            })
    
    # Exploratory intent recommendations
    elif intent_type == "exploratory":
        # Collection page optimization
        recommendations.append({
            "tactic_type": TacticType.COLLECTION_PAGE_OPTIMIZATION.value,
            "description": f"Create a curated collection page for '{intent_analysis.get('main_keyword', {}).get('text', 'main keyword')}' with diverse options.",
            "priority": 1,
            "confidence": 0.9,
            "supporting_evidence": ["Exploratory intent detected with high confidence"]
        })
        
        # Image optimization
        recommendations.append({
            "tactic_type": TacticType.IMAGE_OPTIMIZATION.value,
            "description": "Optimize product images with descriptive filenames and alt text using the primary keyword.",
            "priority": 2,
            "confidence": 0.85,
            "supporting_evidence": ["Exploratory intent indicates high visual importance"]
        })
        
        # Content for inspiration
        recommendations.append({
            "tactic_type": TacticType.CONTENT_CREATION.value,
            "description": "Create visual inspiration content like \"Top 10 Designs\" or \"Style Guide\" articles.",
            "priority": 3,
            "confidence": 0.8,
            "supporting_evidence": ["Exploratory intent indicates browsing behavior"]
        })
    
    # Navigational intent recommendations
    elif intent_type == "navigational":
        # Brand optimization
        recommendations.append({
            "tactic_type": TacticType.TECHNICAL_SEO.value,
            "description": "Optimize brand pages with structured data to enhance SERP appearance.",
            "priority": 1,
            "confidence": 0.9,
            "supporting_evidence": ["Navigational intent detected with high confidence"]
        })
        
        # Link building
        recommendations.append({
            "tactic_type": TacticType.LINK_BUILDING.value,
            "description": "Build brand mentions and links to strengthen navigational search presence.",
            "priority": 2,
            "confidence": 0.85,
            "supporting_evidence": ["Navigational intent indicates brand-focused searches"]
        })
    
    return recommendations


def generate_market_gap_recommendations(market_gap: Dict[str, Any], intent_type: str) -> List[Dict[str, Any]]:
    """
    Generate market gap-based recommendations.
    
    Args:
        market_gap: The market gap analysis data.
        intent_type: The classified intent type.
        
    Returns:
        List of recommendations.
    """
    if not market_gap.get("detected", False):
        return []
    
    recommendations = []
    gap_description = market_gap.get("description", "")
    opportunity_score = market_gap.get("opportunity_score", 0.5)
    competition_level = market_gap.get("competition_level", 0.5)
    gap_keywords = market_gap.get("related_keywords", [])
    
    # Extract gap themes from description
    gap_themes = []
    theme_matches = re.findall(r'No ([a-z-]+)-themed', gap_description)
    for theme in theme_matches:
        gap_themes.append(theme)
    
    # Quality indicator gaps
    quality_matches = re.findall(r'No mention of ([a-z]+) information', gap_description)
    quality_gaps = []
    for quality in quality_matches:
        quality_gaps.append(quality)
    
    # Generate recommendations based on gap themes
    if gap_themes:
        for i, theme in enumerate(gap_themes[:2]):  # Limit to top 2 themes
            if intent_type == "transactional":
                recommendations.append({
                    "tactic_type": TacticType.PRODUCT_PAGE_OPTIMIZATION.value,
                    "description": f"Create new product listings targeting '{theme}-themed graphic tees' niche.",
                    "priority": i + 1,
                    "confidence": min(opportunity_score, 0.9),
                    "supporting_evidence": [f"Market gap detected: No {theme}-themed graphic tees in results"]
                })
            elif intent_type == "informational":
                recommendations.append({
                    "tactic_type": TacticType.CONTENT_CREATION.value,
                    "description": f"Create content specifically about '{theme}-themed graphic tees' to address information gap.",
                    "priority": i + 1,
                    "confidence": min(opportunity_score, 0.9),
                    "supporting_evidence": [f"Market gap detected: No content addressing {theme}-themed graphic tees"]
                })
    
    # Generate recommendations based on quality gaps
    if quality_gaps:
        for i, quality in enumerate(quality_gaps[:2]):  # Limit to top 2 quality gaps
            if intent_type == "transactional":
                recommendations.append({
                    "tactic_type": TacticType.PRODUCT_PAGE_OPTIMIZATION.value,
                    "description": f"Add detailed {quality} information to product pages to differentiate from competitors.",
                    "priority": len(gap_themes) + i + 1,
                    "confidence": min(opportunity_score - 0.1, 0.85),  # Slightly lower confidence
                    "supporting_evidence": [f"Quality gap detected: No mention of {quality} information in results"]
                })
            elif intent_type == "informational":
                recommendations.append({
                    "tactic_type": TacticType.CONTENT_CREATION.value,
                    "description": f"Create a guide addressing {quality} considerations for graphic tees.",
                    "priority": len(gap_themes) + i + 1,
                    "confidence": min(opportunity_score - 0.1, 0.85),  # Slightly lower confidence
                    "supporting_evidence": [f"Quality gap detected: No content addressing {quality} considerations"]
                })
    
    # If no specific themes or quality gaps were found but a gap was detected
    if not gap_themes and not quality_gaps and market_gap.get("detected", False):
        if intent_type == "transactional":
            recommendations.append({
                "tactic_type": TacticType.PRODUCT_PAGE_OPTIMIZATION.value,
                "description": "Create products targeting the identified market gap opportunity.",
                "priority": 1,
                "confidence": min(opportunity_score - 0.15, 0.8),  # Lower confidence due to ambiguity
                "supporting_evidence": ["General market gap detected in results"]
            })
        elif intent_type == "informational":
            recommendations.append({
                "tactic_type": TacticType.CONTENT_CREATION.value,
                "description": "Create content addressing the identified information gap.",
                "priority": 1,
                "confidence": min(opportunity_score - 0.15, 0.8),  # Lower confidence due to ambiguity
                "supporting_evidence": ["General information gap detected in results"]
            })
    
    return recommendations


@function_tool
async def generate_recommendations(
    intent_analysis: Dict[str, Any],
    market_gap: Dict[str, Any],
    serp_features: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate SEO recommendations based on SERP analysis.
    
    This tool creates tactical recommendations for POD graphic tee optimization
    based on search intent, market gaps, and SERP features.
    
    Args:
        intent_analysis: Intent analysis data with intent type and keywords.
        market_gap: Market gap analysis data.
        serp_features: SERP features data.
        
    Returns:
        Dictionary containing SEO recommendations with priority and confidence scores.
    """
    try:
        # Generate intent-based recommendations
        intent_recommendations = generate_intent_recommendations(intent_analysis, serp_features)
        
        # Generate market gap-based recommendations
        gap_recommendations = []
        intent_type = intent_analysis.get("intent_type", "informational")
        
        if market_gap.get("detected", False):
            gap_recommendations = generate_market_gap_recommendations(market_gap, intent_type)
        
        # Combine all recommendations
        all_recommendations = intent_recommendations + gap_recommendations
        
        # Create response
        result = RecommendationGenerationResult(
            recommendations=all_recommendations,
            intent_based=len(intent_recommendations) > 0,
            market_gap_based=len(gap_recommendations) > 0
        )
        
        return result.dict()
    except Exception as e:
        raise ValueError(f"Recommendation generation failed: {str(e)}")


@function_tool
async def prioritize_tactics(recommendations: List[Dict[str, Any]], intent_type: str) -> List[Dict[str, Any]]:
    """
    Prioritize SEO tactics based on intent type and estimated impact.
    
    This tool reorders and refines recommendations based on the search intent type
    and potential business impact.
    
    Args:
        recommendations: List of recommendation objects to prioritize.
        intent_type: The classified intent type.
        
    Returns:
        Prioritized list of recommendations.
    """
    try:
        if not recommendations:
            return []
        
        # Define impact multipliers based on tactic type and intent
        impact_multipliers = {
            # For transactional intent
            "transactional": {
                "product_page_optimization": 1.0,
                "marketplace_optimization": 0.9,
                "ppc_strategy": 0.85,
                "keyword_targeting": 0.8,
                "image_optimization": 0.75,
                "collection_page_optimization": 0.7,
                "technical_seo": 0.65,
                "content_creation": 0.6,
                "snippet_optimization": 0.5,
                "link_building": 0.4
            },
            # For informational intent
            "informational": {
                "content_creation": 1.0,
                "snippet_optimization": 0.9,
                "keyword_targeting": 0.85,
                "technical_seo": 0.8,
                "link_building": 0.75,
                "collection_page_optimization": 0.7,
                "image_optimization": 0.65,
                "product_page_optimization": 0.6,
                "marketplace_optimization": 0.5,
                "ppc_strategy": 0.4
            },
            # For exploratory intent
            "exploratory": {
                "collection_page_optimization": 1.0,
                "image_optimization": 0.9,
                "content_creation": 0.85,
                "product_page_optimization": 0.8,
                "keyword_targeting": 0.75,
                "technical_seo": 0.7,
                "marketplace_optimization": 0.65,
                "snippet_optimization": 0.6,
                "link_building": 0.5,
                "ppc_strategy": 0.4
            },
            # For navigational intent
            "navigational": {
                "technical_seo": 1.0,
                "link_building": 0.9,
                "product_page_optimization": 0.8,
                "marketplace_optimization": 0.75,
                "keyword_targeting": 0.7,
                "collection_page_optimization": 0.65,
                "content_creation": 0.6,
                "image_optimization": 0.5,
                "snippet_optimization": 0.45,
                "ppc_strategy": 0.4
            }
        }
        
        # Default to informational if intent type is not recognized
        if intent_type not in impact_multipliers:
            intent_type = "informational"
        
        # Calculate adjusted priority for each recommendation
        for recommendation in recommendations:
            tactic_type = recommendation.get("tactic_type", "").lower()
            confidence = recommendation.get("confidence", 0.5)
            original_priority = recommendation.get("priority", 5)
            
            # Get impact multiplier for this tactic type and intent
            multiplier = impact_multipliers[intent_type].get(tactic_type, 0.5)
            
            # Calculate adjusted priority score (lower is higher priority)
            # Formula weights original priority (70%) and adjusts with multiplier and confidence
            adjusted_priority = (original_priority * 0.7) / (multiplier * confidence)
            
            # Store original and adjusted priority
            recommendation["original_priority"] = original_priority
            recommendation["adjusted_priority"] = adjusted_priority
        
        # Sort recommendations by adjusted priority
        prioritized = sorted(recommendations, key=lambda r: r.get("adjusted_priority", 999))
        
        # Reapply integer priorities from 1 to N
        for i, recommendation in enumerate(prioritized):
            recommendation["priority"] = i + 1
            # Remove temporary fields
            if "adjusted_priority" in recommendation:
                del recommendation["adjusted_priority"]
            if "original_priority" in recommendation:
                del recommendation["original_priority"]
        
        return prioritized
    except Exception as e:
        raise ValueError(f"Tactic prioritization failed: {str(e)}")


@function_tool
async def format_recommendations(recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format recommendations for presentation.
    
    This tool takes a list of recommendations and formats them for
    presentation, adding formatting and additional metadata.
    
    Args:
        recommendations: List of recommendation objects to format.
        
    Returns:
        Dictionary containing formatted recommendations and metadata.
    """
    try:
        if not recommendations:
            return {
                "recommendations": [],
                "count": 0,
                "has_high_confidence": False,
                "tactic_types": []
            }
        
        # Count tactic types
        tactic_types = {}
        for recommendation in recommendations:
            tactic_type = recommendation.get("tactic_type", "unknown")
            tactic_types[tactic_type] = tactic_types.get(tactic_type, 0) + 1
        
        # Check for high confidence recommendations
        high_confidence = any(r.get("confidence", 0) >= 0.8 for r in recommendations)
        
        # Format each recommendation
        formatted_recommendations = []
        for recommendation in recommendations:
            # Ensure all required fields are present
            formatted = {
                "tactic_type": recommendation.get("tactic_type", "unknown"),
                "description": recommendation.get("description", "No description provided"),
                "priority": recommendation.get("priority", 999),
                "confidence": recommendation.get("confidence", 0.5)
            }
            
            # Add optional fields if present
            if "supporting_evidence" in recommendation:
                formatted["supporting_evidence"] = recommendation["supporting_evidence"]
                
            if "estimated_effort" in recommendation:
                formatted["estimated_effort"] = recommendation["estimated_effort"]
            
            formatted_recommendations.append(formatted)
        
        # Create response
        result = {
            "recommendations": formatted_recommendations,
            "count": len(formatted_recommendations),
            "has_high_confidence": high_confidence,
            "tactic_types": [{"type": k, "count": v} for k, v in tactic_types.items()]
        }
        
        return result
    except Exception as e:
        raise ValueError(f"Recommendation formatting failed: {str(e)}") 