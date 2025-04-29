"""
Unit tests for the recommendation models in the AI SERP Keyword Research Agent.
"""

import pytest
from pydantic import ValidationError

from ai_serp_keyword_research.core.models.recommendations import (
    TacticType,
    Recommendation,
    RecommendationSet
)


class TestRecommendationModel:
    """Test suite for the Recommendation model."""
    
    def test_valid_recommendation(self):
        """Test creating a Recommendation with valid data."""
        # Basic recommendation with required fields
        rec = Recommendation(
            tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
            description="Add 'funny dad shirt' as a primary keyword in product titles",
            priority=1,
            confidence=0.92
        )
        
        assert rec.tactic_type == TacticType.PRODUCT_PAGE_OPTIMIZATION
        assert rec.description == "Add 'funny dad shirt' as a primary keyword in product titles"
        assert rec.priority == 1
        assert rec.confidence == 0.92
        assert rec.supporting_evidence is None
        assert rec.estimated_effort is None
        
        # Recommendation with all fields
        rec = Recommendation(
            tactic_type=TacticType.CONTENT_CREATION,
            description="Create a gift guide article targeting 'best gifts for dads'",
            priority=2,
            confidence=0.85,
            supporting_evidence=[
                "3 of top 5 results are gift guides",
                "High search volume during Father's Day season"
            ],
            estimated_effort=3
        )
        
        assert rec.tactic_type == TacticType.CONTENT_CREATION
        assert rec.description == "Create a gift guide article targeting 'best gifts for dads'"
        assert rec.priority == 2
        assert rec.confidence == 0.85
        assert len(rec.supporting_evidence) == 2
        assert rec.estimated_effort == 3
        
    def test_description_validation(self):
        """Test that descriptions must be actionable."""
        # Valid actionable descriptions
        valid_descriptions = [
            "Add 'funny dad shirt' as a primary keyword in product titles",
            "Create a gift guide article targeting 'best gifts for dads'",
            "Optimize product images with alt text including 'graphic tee'",
            "Update collection page meta descriptions to include 'shirt designs'",
            "Implement schema markup for product listings"
        ]
        
        for desc in valid_descriptions:
            rec = Recommendation(
                tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                description=desc,
                priority=1,
                confidence=0.9
            )
            assert rec.description == desc
            
        # Invalid non-actionable descriptions
        invalid_descriptions = [
            "The competition is high",
            "Search volume trends",
            "POD graphic tees market",
            "Keyword analysis results",
            "Marketplace insights"
        ]
        
        for desc in invalid_descriptions:
            with pytest.raises(ValidationError) as excinfo:
                Recommendation(
                    tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                    description=desc,
                    priority=1,
                    confidence=0.9
                )
            assert "Recommendation description must be actionable" in str(excinfo.value)
            
    def test_description_length(self):
        """Test description length validation."""
        # Too short
        with pytest.raises(ValidationError) as excinfo:
            Recommendation(
                tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                description="Add tags",  # Too short
                priority=1,
                confidence=0.9
            )
        assert "ensure this value has at least 10 characters" in str(excinfo.value)
        
        # Too long
        with pytest.raises(ValidationError) as excinfo:
            Recommendation(
                tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                description="A" * 1001,  # Too long
                priority=1,
                confidence=0.9
            )
        assert "ensure this value has at most 1000 characters" in str(excinfo.value)
        
    def test_priority_bounds(self):
        """Test priority bounds validation."""
        # Valid bounds
        rec = Recommendation(
            tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
            description="Add 'funny dad shirt' as a primary keyword in product titles",
            priority=1,  # Minimum
            confidence=0.9
        )
        assert rec.priority == 1
        
        rec = Recommendation(
            tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
            description="Add 'funny dad shirt' as a primary keyword in product titles",
            priority=10,  # Maximum
            confidence=0.9
        )
        assert rec.priority == 10
        
        # Invalid bounds (too low)
        with pytest.raises(ValidationError) as excinfo:
            Recommendation(
                tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                description="Add 'funny dad shirt' as a primary keyword in product titles",
                priority=0,  # Too low
                confidence=0.9
            )
        assert "greater than or equal to 1" in str(excinfo.value)
        
        # Invalid bounds (too high)
        with pytest.raises(ValidationError) as excinfo:
            Recommendation(
                tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                description="Add 'funny dad shirt' as a primary keyword in product titles",
                priority=11,  # Too high
                confidence=0.9
            )
        assert "less than or equal to 10" in str(excinfo.value)
        
    def test_confidence_bounds(self):
        """Test confidence bounds validation."""
        # Valid bounds
        rec = Recommendation(
            tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
            description="Add 'funny dad shirt' as a primary keyword in product titles",
            priority=1,
            confidence=0.0  # Minimum
        )
        assert rec.confidence == 0.0
        
        rec = Recommendation(
            tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
            description="Add 'funny dad shirt' as a primary keyword in product titles",
            priority=1,
            confidence=1.0  # Maximum
        )
        assert rec.confidence == 1.0
        
        # Invalid bounds (too low)
        with pytest.raises(ValidationError) as excinfo:
            Recommendation(
                tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                description="Add 'funny dad shirt' as a primary keyword in product titles",
                priority=1,
                confidence=-0.1  # Too low
            )
        assert "greater than or equal to 0" in str(excinfo.value)
        
        # Invalid bounds (too high)
        with pytest.raises(ValidationError) as excinfo:
            Recommendation(
                tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                description="Add 'funny dad shirt' as a primary keyword in product titles",
                priority=1,
                confidence=1.1  # Too high
            )
        assert "less than or equal to 1" in str(excinfo.value)


class TestRecommendationSetModel:
    """Test suite for the RecommendationSet model."""
    
    def test_valid_recommendation_set(self):
        """Test creating a RecommendationSet with valid data."""
        rec_set = RecommendationSet(
            recommendations=[
                Recommendation(
                    tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                    description="Add 'funny dad shirt' as a primary keyword in product titles",
                    priority=2,
                    confidence=0.92
                ),
                Recommendation(
                    tactic_type=TacticType.CONTENT_CREATION,
                    description="Create a gift guide article targeting 'best gifts for dads'",
                    priority=1,
                    confidence=0.85
                )
            ],
            intent_based=True,
            market_gap_based=False
        )
        
        assert len(rec_set.recommendations) == 2
        assert rec_set.intent_based is True
        assert rec_set.market_gap_based is False
        
        # Test that recommendations are sorted by priority
        assert rec_set.recommendations[0].tactic_type == TacticType.CONTENT_CREATION
        assert rec_set.recommendations[0].priority == 1
        assert rec_set.recommendations[1].tactic_type == TacticType.PRODUCT_PAGE_OPTIMIZATION
        assert rec_set.recommendations[1].priority == 2
        
    def test_recommendations_sorting(self):
        """Test that recommendations are sorted by priority and confidence."""
        rec_set = RecommendationSet(
            recommendations=[
                # Same priority, different confidence
                Recommendation(
                    tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                    description="Lower confidence recommendation",
                    priority=1,
                    confidence=0.7
                ),
                Recommendation(
                    tactic_type=TacticType.CONTENT_CREATION,
                    description="Higher confidence recommendation",
                    priority=1,
                    confidence=0.9
                ),
                # Different priority
                Recommendation(
                    tactic_type=TacticType.MARKETPLACE_OPTIMIZATION,
                    description="Lower priority recommendation",
                    priority=3,
                    confidence=0.8
                ),
                Recommendation(
                    tactic_type=TacticType.IMAGE_OPTIMIZATION,
                    description="Medium priority recommendation",
                    priority=2,
                    confidence=0.8
                )
            ],
            intent_based=True,
            market_gap_based=True
        )
        
        # Should be sorted by priority first, then by confidence (descending)
        assert rec_set.recommendations[0].priority == 1
        assert rec_set.recommendations[0].confidence == 0.9  # Higher confidence comes first
        
        assert rec_set.recommendations[1].priority == 1
        assert rec_set.recommendations[1].confidence == 0.7
        
        assert rec_set.recommendations[2].priority == 2
        assert rec_set.recommendations[2].confidence == 0.8
        
        assert rec_set.recommendations[3].priority == 3
        assert rec_set.recommendations[3].confidence == 0.8
        
    def test_empty_recommendations_validation(self):
        """Test that RecommendationSet must have at least one recommendation."""
        with pytest.raises(ValidationError) as excinfo:
            RecommendationSet(
                recommendations=[],
                intent_based=True,
                market_gap_based=True
            )
        assert "ensure this value has at least 1 items" in str(excinfo.value) 