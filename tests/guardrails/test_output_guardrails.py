"""
Tests for output guardrails.
"""

import pytest
import asyncio
from unittest.mock import MagicMock

from ai_serp_keyword_research.guardrails.output_guardrails import (
    validate_recommendations,
    validate_analysis_completeness,
    recommendation_quality_guardrail,
    analysis_completeness_guardrail,
    RecommendationQualityError,
    AnalysisCompletenessError,
)


class TestRecommendationValidation:
    """Tests for recommendation validation."""
    
    def test_valid_recommendations(self):
        """Test that valid recommendations pass validation."""
        recommendations = [
            {
                "tactic_type": "product_page_optimization",
                "description": "Create a product page targeting 'best dad ever shirt' keyword",
                "priority": 1,
                "confidence": 0.85
            },
            {
                "tactic_type": "content_creation",
                "description": "Develop a gift guide blog post featuring funny dad shirts",
                "priority": 2,
                "confidence": 0.75
            }
        ]
        
        validated = validate_recommendations(recommendations)
        assert len(validated) == 2
        assert validated[0]["priority"] == 1  # Should be sorted by priority
    
    def test_empty_recommendations(self):
        """Test that empty recommendations fail validation."""
        with pytest.raises(RecommendationQualityError):
            validate_recommendations([])
    
    def test_missing_required_field(self):
        """Test that recommendations missing required fields fail validation."""
        recommendations = [
            {
                "tactic_type": "product_page_optimization",
                "description": "Create a product page targeting 'best dad ever shirt' keyword",
                # Missing priority
                "confidence": 0.85
            }
        ]
        
        with pytest.raises(RecommendationQualityError):
            validate_recommendations(recommendations)
    
    def test_invalid_tactic_type(self):
        """Test that recommendations with invalid tactic types fail validation."""
        recommendations = [
            {
                "tactic_type": "invalid_type",
                "description": "Create a product page targeting 'best dad ever shirt' keyword",
                "priority": 1,
                "confidence": 0.85
            }
        ]
        
        with pytest.raises(RecommendationQualityError):
            validate_recommendations(recommendations)
    
    def test_invalid_priority(self):
        """Test that recommendations with invalid priorities fail validation."""
        recommendations = [
            {
                "tactic_type": "product_page_optimization",
                "description": "Create a product page targeting 'best dad ever shirt' keyword",
                "priority": 0,  # Invalid priority, must be >= 1
                "confidence": 0.85
            }
        ]
        
        with pytest.raises(RecommendationQualityError):
            validate_recommendations(recommendations)
    
    def test_invalid_confidence(self):
        """Test that recommendations with invalid confidence scores fail validation."""
        recommendations = [
            {
                "tactic_type": "product_page_optimization",
                "description": "Create a product page targeting 'best dad ever shirt' keyword",
                "priority": 1,
                "confidence": 1.5  # Invalid confidence, must be between 0 and 1
            }
        ]
        
        with pytest.raises(RecommendationQualityError):
            validate_recommendations(recommendations)
    
    def test_short_description(self):
        """Test that recommendations with too-short descriptions fail validation."""
        recommendations = [
            {
                "tactic_type": "product_page_optimization",
                "description": "Too short",
                "priority": 1,
                "confidence": 0.85
            }
        ]
        
        with pytest.raises(RecommendationQualityError):
            validate_recommendations(recommendations)


class TestAnalysisCompleteness:
    """Tests for analysis completeness validation."""
    
    def test_valid_analysis(self):
        """Test that valid analysis passes validation."""
        analysis = {
            "analysis": {
                "main_keyword": "dad graphic tee",
                "secondary_keywords": ["funny dad shirt", "father's day gift"],
                "intent_type": "transactional",
                "confidence": 0.87,
                "serp_features": ["shopping_ads", "image_pack"]
            },
            "market_gap": {
                "detected": True,
                "description": "Limited personalized dad shirts with profession themes"
            },
            "recommendations": [
                {
                    "tactic_type": "product_page_optimization",
                    "description": "Create a product page targeting 'best dad ever shirt' keyword",
                    "priority": 1,
                    "confidence": 0.85
                },
                {
                    "tactic_type": "content_creation",
                    "description": "Develop a gift guide blog post featuring funny dad shirts",
                    "priority": 2,
                    "confidence": 0.75
                }
            ]
        }
        
        validated = validate_analysis_completeness(analysis)
        assert validated is not None
        assert "analysis" in validated
        assert "market_gap" in validated
        assert "recommendations" in validated
    
    def test_missing_section(self):
        """Test that analysis missing required sections fails validation."""
        analysis = {
            "analysis": {
                "main_keyword": "dad graphic tee",
                "secondary_keywords": ["funny dad shirt", "father's day gift"],
                "intent_type": "transactional",
                "confidence": 0.87,
                "serp_features": ["shopping_ads", "image_pack"]
            },
            # Missing market_gap section
            "recommendations": [
                {
                    "tactic_type": "product_page_optimization",
                    "description": "Create a product page targeting 'best dad ever shirt' keyword",
                    "priority": 1,
                    "confidence": 0.85
                }
            ]
        }
        
        with pytest.raises(AnalysisCompletenessError):
            validate_analysis_completeness(analysis)
    
    def test_missing_analysis_field(self):
        """Test that analysis missing required fields fails validation."""
        analysis = {
            "analysis": {
                "main_keyword": "dad graphic tee",
                # Missing secondary_keywords
                "intent_type": "transactional",
                "confidence": 0.87,
                "serp_features": ["shopping_ads", "image_pack"]
            },
            "market_gap": {
                "detected": True,
                "description": "Limited personalized dad shirts with profession themes"
            },
            "recommendations": [
                {
                    "tactic_type": "product_page_optimization",
                    "description": "Create a product page targeting 'best dad ever shirt' keyword",
                    "priority": 1,
                    "confidence": 0.85
                }
            ]
        }
        
        with pytest.raises(AnalysisCompletenessError):
            validate_analysis_completeness(analysis)
    
    def test_missing_market_gap_detected(self):
        """Test that market gap section missing 'detected' field fails validation."""
        analysis = {
            "analysis": {
                "main_keyword": "dad graphic tee",
                "secondary_keywords": ["funny dad shirt", "father's day gift"],
                "intent_type": "transactional",
                "confidence": 0.87,
                "serp_features": ["shopping_ads", "image_pack"]
            },
            "market_gap": {
                # Missing detected field
                "description": "Limited personalized dad shirts with profession themes"
            },
            "recommendations": [
                {
                    "tactic_type": "product_page_optimization",
                    "description": "Create a product page targeting 'best dad ever shirt' keyword",
                    "priority": 1,
                    "confidence": 0.85
                }
            ]
        }
        
        with pytest.raises(AnalysisCompletenessError):
            validate_analysis_completeness(analysis)
    
    def test_missing_gap_description(self):
        """Test that detected market gap without description fails validation."""
        analysis = {
            "analysis": {
                "main_keyword": "dad graphic tee",
                "secondary_keywords": ["funny dad shirt", "father's day gift"],
                "intent_type": "transactional",
                "confidence": 0.87,
                "serp_features": ["shopping_ads", "image_pack"]
            },
            "market_gap": {
                "detected": True
                # Missing description for detected gap
            },
            "recommendations": [
                {
                    "tactic_type": "product_page_optimization",
                    "description": "Create a product page targeting 'best dad ever shirt' keyword",
                    "priority": 1,
                    "confidence": 0.85
                }
            ]
        }
        
        with pytest.raises(AnalysisCompletenessError):
            validate_analysis_completeness(analysis)


class TestGuardrailFunctions:
    """Tests for the guardrail functions."""
    
    @pytest.mark.asyncio
    async def test_recommendation_quality_guardrail_valid(self):
        """Test that valid recommendations pass the guardrail."""
        ctx = MagicMock()
        agent = MagicMock()
        output = {
            "recommendations": [
                {
                    "tactic_type": "product_page_optimization",
                    "description": "Create a product page targeting 'best dad ever shirt' keyword",
                    "priority": 1,
                    "confidence": 0.85
                }
            ]
        }
        
        result = await recommendation_quality_guardrail(ctx, agent, output)
        assert result.tripwire_triggered is False
    
    @pytest.mark.asyncio
    async def test_recommendation_quality_guardrail_invalid(self):
        """Test that invalid recommendations fail the guardrail."""
        ctx = MagicMock()
        agent = MagicMock()
        output = {
            "recommendations": [
                {
                    "tactic_type": "invalid_type",  # Invalid tactic type
                    "description": "Create a product page targeting 'best dad ever shirt' keyword",
                    "priority": 1,
                    "confidence": 0.85
                }
            ]
        }
        
        result = await recommendation_quality_guardrail(ctx, agent, output)
        assert result.tripwire_triggered is True
    
    @pytest.mark.asyncio
    async def test_analysis_completeness_guardrail_valid(self):
        """Test that valid analysis passes the guardrail."""
        ctx = MagicMock()
        agent = MagicMock()
        output = {
            "analysis": {
                "main_keyword": "dad graphic tee",
                "secondary_keywords": ["funny dad shirt", "father's day gift"],
                "intent_type": "transactional",
                "confidence": 0.87
            },
            "market_gap": {
                "detected": False
            },
            "recommendations": [
                {
                    "tactic_type": "product_page_optimization",
                    "description": "Create a product page targeting 'best dad ever shirt' keyword",
                    "priority": 1,
                    "confidence": 0.85
                }
            ]
        }
        
        result = await analysis_completeness_guardrail(ctx, agent, output)
        assert result.tripwire_triggered is False
    
    @pytest.mark.asyncio
    async def test_analysis_completeness_guardrail_invalid(self):
        """Test that invalid analysis fails the guardrail."""
        ctx = MagicMock()
        agent = MagicMock()
        output = {
            "analysis": {
                "main_keyword": "dad graphic tee",
                # Missing secondary_keywords
                "intent_type": "transactional",
                "confidence": 0.87
            },
            "market_gap": {
                "detected": False
            },
            "recommendations": [
                {
                    "tactic_type": "product_page_optimization",
                    "description": "Create a product page targeting 'best dad ever shirt' keyword",
                    "priority": 1,
                    "confidence": 0.85
                }
            ]
        }
        
        result = await analysis_completeness_guardrail(ctx, agent, output)
        assert result.tripwire_triggered is True 