"""
Output guardrails for the AI SERP Keyword Research Agent.

This module provides guardrails to ensure that outputs are complete,
accurate, and high-quality before being returned to the user.
"""

import logging
from typing import Dict, List, Any, Optional
from agents import output_guardrail, GuardrailFunctionOutput

logger = logging.getLogger(__name__)


class RecommendationQualityError(ValueError):
    """Raised when recommendations fail quality checks."""
    pass


class AnalysisCompletenessError(ValueError):
    """Raised when analysis is incomplete."""
    pass


def validate_recommendations(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate recommendations for quality and actionability.
    
    Args:
        recommendations: List of recommendation dictionaries
        
    Returns:
        The validated recommendations
        
    Raises:
        RecommendationQualityError: If the recommendations are low quality
    """
    if not recommendations:
        raise RecommendationQualityError("No recommendations provided")
    
    validated_recommendations = []
    
    for i, rec in enumerate(recommendations):
        # Check required fields
        for field in ["tactic_type", "description", "priority", "confidence"]:
            if field not in rec:
                raise RecommendationQualityError(f"Recommendation {i+1} missing required field: {field}")
        
        # Validate tactic type
        valid_tactic_types = [
            "product_page_optimization", "keyword_optimization", "content_creation",
            "collection_optimization", "listing_improvement", "title_optimization",
            "description_optimization", "tag_optimization", "visual_optimization"
        ]
        if rec["tactic_type"] not in valid_tactic_types:
            raise RecommendationQualityError(
                f"Recommendation {i+1} has invalid tactic type: {rec['tactic_type']}"
            )
        
        # Validate description quality
        description = rec["description"]
        if len(description) < 20:
            raise RecommendationQualityError(
                f"Recommendation {i+1} description is too short: {description}"
            )
        
        # Check for generic descriptions
        generic_phrases = [
            "optimize your", "improve your", "consider using", "make sure to",
            "don't forget to", "remember to", "it's important to"
        ]
        if any(phrase in description.lower() for phrase in generic_phrases):
            # This is not an error, just log a warning
            logger.warning(f"Recommendation {i+1} uses generic phrasing: {description}")
        
        # Validate priority and confidence
        priority = rec["priority"]
        confidence = rec["confidence"]
        
        if not isinstance(priority, int) or priority < 1:
            raise RecommendationQualityError(
                f"Recommendation {i+1} has invalid priority: {priority}"
            )
        
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            raise RecommendationQualityError(
                f"Recommendation {i+1} has invalid confidence score: {confidence}"
            )
        
        # Make sure high priority items have high confidence
        if priority == 1 and confidence < 0.7:
            logger.warning(
                f"Recommendation {i+1} has high priority but low confidence: {confidence}"
            )
        
        # Add to validated list
        validated_recommendations.append(rec)
    
    # Check for variety in recommendations
    tactic_types = [rec["tactic_type"] for rec in validated_recommendations]
    if len(set(tactic_types)) < min(2, len(tactic_types)):
        logger.warning("Recommendations lack variety in tactic types")
    
    # Sort by priority (lower numbers are higher priority)
    validated_recommendations.sort(key=lambda x: (x["priority"], -x["confidence"]))
    
    return validated_recommendations


def validate_analysis_completeness(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that an analysis is complete and ready for delivery.
    
    Args:
        analysis: The analysis dictionary
        
    Returns:
        The validated analysis
        
    Raises:
        AnalysisCompletenessError: If the analysis is incomplete
    """
    # Check for required top-level sections
    required_sections = ["analysis", "market_gap", "recommendations"]
    for section in required_sections:
        if section not in analysis:
            raise AnalysisCompletenessError(f"Analysis missing required section: {section}")
    
    # Check analysis section completeness
    analysis_section = analysis["analysis"]
    required_analysis_fields = ["main_keyword", "secondary_keywords", "intent_type", "confidence"]
    for field in required_analysis_fields:
        if field not in analysis_section:
            raise AnalysisCompletenessError(f"Analysis section missing required field: {field}")
    
    # Check market gap section
    market_gap = analysis["market_gap"]
    if "detected" not in market_gap:
        raise AnalysisCompletenessError("Market gap section missing 'detected' field")
    
    # If a market gap was detected, a description should be provided
    if market_gap.get("detected", False) and "description" not in market_gap:
        raise AnalysisCompletenessError("Market gap detected but no description provided")
    
    # Check recommendations completeness
    recommendations = analysis["recommendations"]
    if not recommendations:
        raise AnalysisCompletenessError("No recommendations provided")
    
    # Validate recommendations quality
    analysis["recommendations"] = validate_recommendations(recommendations)
    
    # Check confidence scores
    confidence = analysis_section.get("confidence", 0)
    if confidence < 0.5:
        logger.warning(f"Analysis has low confidence score: {confidence}")
    
    return analysis


@output_guardrail
async def recommendation_quality_guardrail(ctx: Any, agent: Any, output: Any) -> GuardrailFunctionOutput:
    """
    Guardrail function to validate recommendation quality.
    
    Args:
        ctx: Context information
        agent: The agent that produced the output
        output: The output to check
        
    Returns:
        GuardrailFunctionOutput indicating whether the guardrail was triggered
    """
    try:
        # Extract recommendations from output
        recommendations = None
        
        # Handle different output formats depending on agent
        if hasattr(output, "recommendations"):
            recommendations = output.recommendations
        elif isinstance(output, dict) and "recommendations" in output:
            recommendations = output["recommendations"]
        
        if not recommendations:
            return GuardrailFunctionOutput(
                tripwire_triggered=True,
                output_info={"reason": "No recommendations found in output"}
            )
        
        # Validate recommendations
        try:
            validate_recommendations(recommendations)
            return GuardrailFunctionOutput(tripwire_triggered=False)
        except RecommendationQualityError as e:
            logger.warning(f"Recommendation quality guardrail triggered: {str(e)}")
            return GuardrailFunctionOutput(
                tripwire_triggered=True,
                output_info={"reason": str(e)}
            )
    
    except Exception as e:
        logger.error(f"Error in recommendation quality guardrail: {str(e)}", exc_info=True)
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={"reason": f"Error validating recommendations: {str(e)}"}
        )


@output_guardrail
async def analysis_completeness_guardrail(ctx: Any, agent: Any, output: Any) -> GuardrailFunctionOutput:
    """
    Guardrail function to validate analysis completeness.
    
    Args:
        ctx: Context information
        agent: The agent that produced the output
        output: The output to check
        
    Returns:
        GuardrailFunctionOutput indicating whether the guardrail was triggered
    """
    try:
        # Extract analysis from output
        analysis = None
        
        # Handle different output formats depending on agent
        if hasattr(output, "to_dict"):
            analysis = output.to_dict()
        elif isinstance(output, dict):
            analysis = output
        
        if not analysis:
            return GuardrailFunctionOutput(
                tripwire_triggered=True,
                output_info={"reason": "No analysis found in output"}
            )
        
        # Validate analysis completeness
        try:
            validate_analysis_completeness(analysis)
            return GuardrailFunctionOutput(tripwire_triggered=False)
        except AnalysisCompletenessError as e:
            logger.warning(f"Analysis completeness guardrail triggered: {str(e)}")
            return GuardrailFunctionOutput(
                tripwire_triggered=True,
                output_info={"reason": str(e)}
            )
    
    except Exception as e:
        logger.error(f"Error in analysis completeness guardrail: {str(e)}", exc_info=True)
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={"reason": f"Error validating analysis completeness: {str(e)}"}
        ) 