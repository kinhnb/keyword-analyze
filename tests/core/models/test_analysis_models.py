"""
Unit tests for the analysis models in the AI SERP Keyword Research Agent.
"""

import pytest
from pydantic import ValidationError

from ai_serp_keyword_research.core.models.analysis import (
    IntentType,
    SerpFeatureType,
    Keyword,
    SerpFeature,
    IntentAnalysis,
    MarketGap
)


class TestKeywordModel:
    """Test suite for the Keyword model."""
    
    def test_valid_keyword(self):
        """Test creating a Keyword with valid data."""
        keyword = Keyword(text="dad graphic tee", relevance=0.85, frequency=5)
        assert keyword.text == "dad graphic tee"
        assert keyword.relevance == 0.85
        assert keyword.frequency == 5
        
    def test_relevance_bounds(self):
        """Test bounds for relevance score."""
        # Valid bounds
        keyword = Keyword(text="dad tee", relevance=0.0, frequency=1)
        assert keyword.relevance == 0.0
        
        keyword = Keyword(text="dad tee", relevance=1.0, frequency=1)
        assert keyword.relevance == 1.0
        
        # Invalid bounds (too low)
        with pytest.raises(ValidationError) as excinfo:
            Keyword(text="dad tee", relevance=-0.1, frequency=1)
        assert "greater than or equal to 0" in str(excinfo.value)
        
        # Invalid bounds (too high)
        with pytest.raises(ValidationError) as excinfo:
            Keyword(text="dad tee", relevance=1.1, frequency=1)
        assert "less than or equal to 1" in str(excinfo.value)
        
    def test_frequency_bounds(self):
        """Test bounds for frequency."""
        # Valid bounds
        keyword = Keyword(text="dad tee", relevance=0.5, frequency=0)
        assert keyword.frequency == 0
        
        # Invalid bounds (negative)
        with pytest.raises(ValidationError) as excinfo:
            Keyword(text="dad tee", relevance=0.5, frequency=-1)
        assert "greater than or equal to 0" in str(excinfo.value)


class TestSerpFeatureModel:
    """Test suite for the SerpFeature model."""
    
    def test_valid_serp_feature(self):
        """Test creating a SerpFeature with valid data."""
        # Basic feature with just type
        feature = SerpFeature(feature_type=SerpFeatureType.SHOPPING_ADS)
        assert feature.feature_type == SerpFeatureType.SHOPPING_ADS
        assert feature.position is None
        assert feature.data is None
        
        # Feature with all fields
        feature = SerpFeature(
            feature_type=SerpFeatureType.FEATURED_SNIPPET,
            position=1,
            data={"content": "Sample snippet content"}
        )
        assert feature.feature_type == SerpFeatureType.FEATURED_SNIPPET
        assert feature.position == 1
        assert feature.data == {"content": "Sample snippet content"}
        
    def test_data_validation(self):
        """Test data validation for different feature types."""
        # Featured snippet must have content
        with pytest.raises(ValidationError) as excinfo:
            SerpFeature(
                feature_type=SerpFeatureType.FEATURED_SNIPPET,
                data={"wrong_key": "value"}
            )
        assert "Featured snippet data must include 'content'" in str(excinfo.value)
        
        # Shopping ads must have products
        with pytest.raises(ValidationError) as excinfo:
            SerpFeature(
                feature_type=SerpFeatureType.SHOPPING_ADS,
                data={"wrong_key": "value"}
            )
        assert "Shopping ads data must include 'products'" in str(excinfo.value)
        
        # Valid data for featured snippet
        feature = SerpFeature(
            feature_type=SerpFeatureType.FEATURED_SNIPPET,
            data={"content": "Sample content", "extra_field": "value"}
        )
        assert feature.data["content"] == "Sample content"
        
        # Valid data for shopping ads
        feature = SerpFeature(
            feature_type=SerpFeatureType.SHOPPING_ADS,
            data={"products": 3, "extra_field": "value"}
        )
        assert feature.data["products"] == 3


class TestIntentAnalysisModel:
    """Test suite for the IntentAnalysis model."""
    
    def test_valid_intent_analysis(self):
        """Test creating an IntentAnalysis with valid data."""
        analysis = IntentAnalysis(
            intent_type=IntentType.TRANSACTIONAL,
            confidence=0.85,
            main_keyword=Keyword(text="dad graphic tee", relevance=0.95, frequency=8),
            secondary_keywords=[
                Keyword(text="funny dad shirt", relevance=0.85, frequency=5),
                Keyword(text="father's day tee", relevance=0.75, frequency=3)
            ]
        )
        
        assert analysis.intent_type == IntentType.TRANSACTIONAL
        assert analysis.confidence == 0.85
        assert analysis.main_keyword.text == "dad graphic tee"
        assert len(analysis.secondary_keywords) == 2
        
        # Test sorting of secondary keywords by relevance
        assert analysis.secondary_keywords[0].text == "funny dad shirt"
        assert analysis.secondary_keywords[1].text == "father's day tee"
        
    def test_secondary_keywords_sorting(self):
        """Test that secondary keywords are sorted by relevance."""
        analysis = IntentAnalysis(
            intent_type=IntentType.INFORMATIONAL,
            confidence=0.8,
            main_keyword=Keyword(text="graphic tees guide", relevance=0.9, frequency=6),
            secondary_keywords=[
                Keyword(text="low relevance", relevance=0.3, frequency=1),
                Keyword(text="medium relevance", relevance=0.5, frequency=2),
                Keyword(text="high relevance", relevance=0.8, frequency=4)
            ]
        )
        
        # Check that keywords are sorted by relevance in descending order
        assert analysis.secondary_keywords[0].text == "high relevance"
        assert analysis.secondary_keywords[1].text == "medium relevance"
        assert analysis.secondary_keywords[2].text == "low relevance"
        
    def test_main_keyword_relevance_validation(self):
        """Test validation that main keyword has higher relevance than secondary keywords."""
        # Valid - main keyword has higher relevance
        analysis = IntentAnalysis(
            intent_type=IntentType.TRANSACTIONAL,
            confidence=0.8,
            main_keyword=Keyword(text="main keyword", relevance=0.9, frequency=5),
            secondary_keywords=[
                Keyword(text="secondary keyword", relevance=0.8, frequency=3)
            ]
        )
        assert analysis.main_keyword.relevance > analysis.secondary_keywords[0].relevance
        
        # Invalid - secondary keyword has higher relevance
        with pytest.raises(ValidationError) as excinfo:
            IntentAnalysis(
                intent_type=IntentType.TRANSACTIONAL,
                confidence=0.8,
                main_keyword=Keyword(text="main keyword", relevance=0.7, frequency=5),
                secondary_keywords=[
                    Keyword(text="secondary keyword", relevance=0.8, frequency=3)
                ]
            )
        assert "Main keyword must have higher or equal relevance than secondary keywords" in str(excinfo.value)


class TestMarketGapModel:
    """Test suite for the MarketGap model."""
    
    def test_valid_market_gap(self):
        """Test creating a MarketGap with valid data."""
        # No market gap detected
        gap = MarketGap(detected=False)
        assert gap.detected is False
        assert gap.description is None
        assert gap.opportunity_score is None
        
        # Market gap detected with all fields
        gap = MarketGap(
            detected=True,
            description="Limited personalized dad shirts with profession themes",
            opportunity_score=0.75,
            competition_level=0.4,
            related_keywords=[
                Keyword(text="engineer dad shirt", relevance=0.85, frequency=2),
                Keyword(text="doctor dad tee", relevance=0.75, frequency=1)
            ]
        )
        
        assert gap.detected is True
        assert gap.description == "Limited personalized dad shirts with profession themes"
        assert gap.opportunity_score == 0.75
        assert gap.competition_level == 0.4
        assert len(gap.related_keywords) == 2
        
    def test_required_fields_for_detected_gap(self):
        """Test that description and opportunity_score are required when gap is detected."""
        # Missing description
        with pytest.raises(ValidationError) as excinfo:
            MarketGap(
                detected=True,
                opportunity_score=0.75
            )
        assert "When market gap is detected, description and opportunity_score must be provided" in str(excinfo.value)
        
        # Missing opportunity_score
        with pytest.raises(ValidationError) as excinfo:
            MarketGap(
                detected=True,
                description="Some gap description"
            )
        assert "When market gap is detected, description and opportunity_score must be provided" in str(excinfo.value)
        
        # Valid - both required fields provided
        gap = MarketGap(
            detected=True,
            description="Some gap description",
            opportunity_score=0.75
        )
        assert gap.detected is True
        assert gap.description == "Some gap description"
        assert gap.opportunity_score == 0.75 