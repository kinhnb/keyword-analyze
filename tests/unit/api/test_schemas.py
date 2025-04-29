"""
Unit tests for the API schema models.

These tests ensure that the models correctly validate input data
and handle edge cases appropriately.
"""

import unittest
import pytest
import datetime
from pydantic import ValidationError

from ai_serp_keyword_research.api.schemas import (
    # Output models
    KeywordOutput,
    IntentAnalysisOutput,
    MarketGapOutput,
    SerpFeatureOutput,
    RecommendationOutput,
    FullAnalysisOutput,
    
    # Request models
    AnalyzeRequest,
    FeedbackRequest,
    
    # Response models
    AnalyzeResponse,
    FeedbackResponse,
    ErrorResponse,
    HealthResponse
)

from ai_serp_keyword_research.core.models.analysis import IntentType


class TestOutputModels(unittest.TestCase):
    """Test cases for the output models."""

    def test_keyword_output_validation(self):
        """Test the KeywordOutput model validation."""
        # Valid case
        keyword = KeywordOutput(
            text="funny dad shirt",
            relevance=0.92,
            frequency=7
        )
        assert keyword.text == "funny dad shirt"
        assert keyword.relevance == 0.92
        assert keyword.frequency == 7
        
        # Invalid relevance (too high)
        with pytest.raises(ValidationError):
            KeywordOutput(text="test", relevance=1.5, frequency=1)
        
        # Invalid relevance (too low)
        with pytest.raises(ValidationError):
            KeywordOutput(text="test", relevance=-0.1, frequency=1)
        
        # Invalid frequency (negative)
        with pytest.raises(ValidationError):
            KeywordOutput(text="test", relevance=0.5, frequency=-1)

    def test_intent_analysis_output_validation(self):
        """Test the IntentAnalysisOutput model validation."""
        # Valid case
        main_keyword = KeywordOutput(text="funny dad shirt", relevance=0.92, frequency=7)
        secondary_keywords = [
            KeywordOutput(text="father's day tee", relevance=0.85, frequency=4),
            KeywordOutput(text="dad gift shirt", relevance=0.78, frequency=3)
        ]
        
        intent_analysis = IntentAnalysisOutput(
            intent_type=IntentType.TRANSACTIONAL,
            confidence=0.87,
            main_keyword=main_keyword,
            secondary_keywords=secondary_keywords
        )
        
        assert intent_analysis.intent_type == IntentType.TRANSACTIONAL
        assert intent_analysis.confidence == 0.87
        assert intent_analysis.main_keyword.text == "funny dad shirt"
        assert len(intent_analysis.secondary_keywords) == 2
        
        # Invalid confidence (too high)
        with pytest.raises(ValidationError):
            IntentAnalysisOutput(
                intent_type=IntentType.TRANSACTIONAL,
                confidence=1.5,
                main_keyword=main_keyword,
                secondary_keywords=secondary_keywords
            )

    def test_market_gap_output_validation(self):
        """Test the MarketGapOutput model validation."""
        # Valid case with gap detected
        market_gap = MarketGapOutput(
            detected=True,
            description="Limited personalized dad shirts with profession themes",
            opportunity_score=0.76,
            competition_level=0.42
        )
        
        assert market_gap.detected is True
        assert market_gap.description == "Limited personalized dad shirts with profession themes"
        assert market_gap.opportunity_score == 0.76
        assert market_gap.competition_level == 0.42
        
        # Valid case with no gap detected
        market_gap = MarketGapOutput(detected=False)
        assert market_gap.detected is False
        
        # Invalid case: detected=True but missing required fields
        with pytest.raises(ValidationError):
            MarketGapOutput(
                detected=True,
                # Missing description, opportunity_score, and competition_level
            )
        
        # Invalid opportunity_score (out of range)
        with pytest.raises(ValidationError):
            MarketGapOutput(
                detected=True,
                description="Test gap",
                opportunity_score=1.5,  # Too high
                competition_level=0.5
            )

    def test_serp_feature_output_validation(self):
        """Test the SerpFeatureOutput model validation."""
        # Valid case
        feature = SerpFeatureOutput(
            feature_type="shopping_ads",
            position=1,
            details={"product_count": 6, "has_images": True}
        )
        
        assert feature.feature_type == "shopping_ads"
        assert feature.position == 1
        assert feature.details["product_count"] == 6
        
        # Valid case with minimal fields
        feature = SerpFeatureOutput(feature_type="featured_snippet")
        assert feature.feature_type == "featured_snippet"
        assert feature.position is None
        assert feature.details is None
        
        # Invalid case (missing required field)
        with pytest.raises(ValidationError):
            SerpFeatureOutput()

    def test_recommendation_output_validation(self):
        """Test the RecommendationOutput model validation."""
        # Valid case
        recommendation = RecommendationOutput(
            tactic_type="product_page_optimization",
            description="Add 'funny dad shirt' as a primary keyword in product titles",
            priority=1,
            confidence=0.92,
            supporting_evidence=[
                "3 of top 5 results use 'funny dad shirt' in title",
                "58% higher CTR observed for listings with this term"
            ]
        )
        
        assert recommendation.tactic_type == "product_page_optimization"
        assert recommendation.description == "Add 'funny dad shirt' as a primary keyword in product titles"
        assert recommendation.priority == 1
        assert recommendation.confidence == 0.92
        assert len(recommendation.supporting_evidence) == 2
        
        # Invalid priority (out of range)
        with pytest.raises(ValidationError):
            RecommendationOutput(
                tactic_type="test",
                description="test description",
                priority=11,  # Too high (1-10 allowed)
                confidence=0.5
            )
        
        # Invalid confidence (out of range)
        with pytest.raises(ValidationError):
            RecommendationOutput(
                tactic_type="test",
                description="test description",
                priority=1,
                confidence=1.1  # Too high (0.0-1.0 allowed)
            )

    def test_full_analysis_output_validation(self):
        """Test the FullAnalysisOutput model validation."""
        # Create required nested components
        main_keyword = KeywordOutput(text="funny dad shirt", relevance=0.92, frequency=7)
        secondary_keywords = [
            KeywordOutput(text="father's day tee", relevance=0.85, frequency=4)
        ]
        
        intent_analysis = IntentAnalysisOutput(
            intent_type=IntentType.TRANSACTIONAL,
            confidence=0.87,
            main_keyword=main_keyword,
            secondary_keywords=secondary_keywords
        )
        
        market_gap = MarketGapOutput(
            detected=True,
            description="Limited personalized dad shirts with profession themes",
            opportunity_score=0.76,
            competition_level=0.42
        )
        
        serp_features = [
            SerpFeatureOutput(
                feature_type="shopping_ads",
                position=1,
                details={"product_count": 6}
            ),
            SerpFeatureOutput(
                feature_type="image_pack",
                position=3,
                details={"image_count": 8}
            )
        ]
        
        recommendations = [
            RecommendationOutput(
                tactic_type="product_page_optimization",
                description="Add 'funny dad shirt' as a primary keyword in product titles",
                priority=2,  # Intentionally unsorted
                confidence=0.92
            ),
            RecommendationOutput(
                tactic_type="content_creation",
                description="Create a gift guide article targeting 'best gifts for dads'",
                priority=1,  # Intentionally unsorted
                confidence=0.85
            )
        ]
        
        # Valid case
        result = FullAnalysisOutput(
            search_term="funny dad shirt",
            analysis_id="550e8400-e29b-41d4-a716-446655440000",
            intent_analysis=intent_analysis,
            market_gap=market_gap,
            serp_features=serp_features,
            recommendations=recommendations,
            execution_time=2.45
        )
        
        assert result.search_term == "funny dad shirt"
        assert result.analysis_id == "550e8400-e29b-41d4-a716-446655440000"
        assert isinstance(result.timestamp, datetime.datetime)
        assert result.intent_analysis.intent_type == IntentType.TRANSACTIONAL
        assert result.market_gap.detected is True
        assert len(result.serp_features) == 2
        assert len(result.recommendations) == 2
        assert result.execution_time == 2.45
        
        # Verify recommendations are sorted by priority
        assert result.recommendations[0].priority == 1
        assert result.recommendations[1].priority == 2
        
        # Invalid case (missing required fields)
        with pytest.raises(ValidationError):
            FullAnalysisOutput(
                search_term="funny dad shirt",
                # Missing other required fields
            )


class TestRequestModels(unittest.TestCase):
    """Test cases for the request models."""

    def test_analyze_request_validation(self):
        """Test the AnalyzeRequest model validation."""
        # Valid case
        request = AnalyzeRequest(
            search_term="funny dad graphic tee",
            max_results=10,
            include_raw_data=False
        )
        
        assert request.search_term == "funny dad graphic tee"
        assert request.max_results == 10
        assert request.include_raw_data is False
        
        # Test with optional fields using defaults
        request = AnalyzeRequest(search_term="dad shirt")
        assert request.search_term == "dad shirt"
        assert request.max_results == 10  # Default
        assert request.include_raw_data is False  # Default
        
        # Invalid search term (too short)
        with pytest.raises(ValidationError):
            AnalyzeRequest(search_term="ab")
        
        # Invalid search term (not related to POD tees)
        with pytest.raises(ValidationError):
            AnalyzeRequest(search_term="weather forecast today")
        
        # Invalid max_results (too high)
        with pytest.raises(ValidationError):
            AnalyzeRequest(search_term="dad shirt", max_results=101)
        
        # Invalid max_results (too low)
        with pytest.raises(ValidationError):
            AnalyzeRequest(search_term="dad shirt", max_results=0)

    def test_feedback_request_validation(self):
        """Test the FeedbackRequest model validation."""
        # Valid case with all fields
        request = FeedbackRequest(
            analysis_id="550e8400-e29b-41d4-a716-446655440000",
            rating=4,
            comments="Good recommendations but missed some keywords",
            helpful_recommendations=["rec-001", "rec-003"],
            unhelpful_recommendations=["rec-002"]
        )
        
        assert request.analysis_id == "550e8400-e29b-41d4-a716-446655440000"
        assert request.rating == 4
        assert request.comments == "Good recommendations but missed some keywords"
        assert "rec-001" in request.helpful_recommendations
        assert "rec-002" in request.unhelpful_recommendations
        
        # Valid case with minimal fields
        request = FeedbackRequest(
            analysis_id="550e8400-e29b-41d4-a716-446655440000",
            rating=5
        )
        
        assert request.analysis_id == "550e8400-e29b-41d4-a716-446655440000"
        assert request.rating == 5
        assert request.comments is None
        assert request.helpful_recommendations is None
        assert request.unhelpful_recommendations is None
        
        # Invalid rating (too high)
        with pytest.raises(ValidationError):
            FeedbackRequest(
                analysis_id="test",
                rating=6  # Valid range is 1-5
            )
        
        # Invalid rating (too low)
        with pytest.raises(ValidationError):
            FeedbackRequest(
                analysis_id="test",
                rating=0  # Valid range is 1-5
            )
        
        # Invalid comments (too long)
        with pytest.raises(ValidationError):
            FeedbackRequest(
                analysis_id="test",
                rating=4,
                comments="a" * 1001  # Max length is 1000
            )


class TestResponseModels(unittest.TestCase):
    """Test cases for the response models."""

    def test_analyze_response_validation(self):
        """Test the AnalyzeResponse model validation."""
        # Create a minimal full analysis output
        intent_analysis = IntentAnalysisOutput(
            intent_type=IntentType.TRANSACTIONAL,
            confidence=0.87,
            main_keyword=KeywordOutput(text="test", relevance=0.9, frequency=1),
            secondary_keywords=[]
        )
        
        market_gap = MarketGapOutput(detected=False)
        
        analysis_output = FullAnalysisOutput(
            search_term="test shirt",
            analysis_id="test-id",
            intent_analysis=intent_analysis,
            market_gap=market_gap,
            serp_features=[],
            recommendations=[]
        )
        
        # Valid success response
        response = AnalyzeResponse(
            status="success",
            data=analysis_output,
            error=None
        )
        
        assert response.status == "success"
        assert response.data is not None
        assert response.error is None
        
        # Valid error response
        response = AnalyzeResponse(
            status="error",
            data=None,
            error="Failed to analyze search term"
        )
        
        assert response.status == "error"
        assert response.data is None
        assert response.error == "Failed to analyze search term"
        
        # Invalid case (missing required field)
        with pytest.raises(ValidationError):
            AnalyzeResponse()

    def test_feedback_response_validation(self):
        """Test the FeedbackResponse model validation."""
        # Valid case
        response = FeedbackResponse(
            status="success",
            message="Feedback recorded successfully",
            feedback_id="fb-12345"
        )
        
        assert response.status == "success"
        assert response.message == "Feedback recorded successfully"
        assert response.feedback_id == "fb-12345"
        
        # Valid case without optional field
        response = FeedbackResponse(
            status="success",
            message="Feedback recorded successfully"
        )
        
        assert response.status == "success"
        assert response.message == "Feedback recorded successfully"
        assert response.feedback_id is None
        
        # Invalid case (missing required field)
        with pytest.raises(ValidationError):
            FeedbackResponse(status="success")

    def test_error_response_validation(self):
        """Test the ErrorResponse model validation."""
        # Valid case with details
        response = ErrorResponse(
            error="Invalid search term",
            details={"search_term": "Value must be related to POD graphic tees"}
        )
        
        assert response.status == "error"  # Default value
        assert response.error == "Invalid search term"
        assert response.details["search_term"] == "Value must be related to POD graphic tees"
        
        # Valid case without details
        response = ErrorResponse(error="Service unavailable")
        
        assert response.status == "error"
        assert response.error == "Service unavailable"
        assert response.details is None
        
        # Invalid case (missing required field)
        with pytest.raises(ValidationError):
            ErrorResponse()

    def test_health_response_validation(self):
        """Test the HealthResponse model validation."""
        # Valid case
        response = HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp="2023-05-01T12:34:56.789Z",
            dependencies={
                "database": "connected",
                "redis": "connected",
                "serp_api": "operational"
            }
        )
        
        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert response.timestamp == "2023-05-01T12:34:56.789Z"
        assert response.dependencies["database"] == "connected"
        
        # Invalid case (missing required field)
        with pytest.raises(ValidationError):
            HealthResponse(
                status="healthy",
                version="1.0.0",
                # Missing timestamp and dependencies
            )


if __name__ == "__main__":
    unittest.main() 