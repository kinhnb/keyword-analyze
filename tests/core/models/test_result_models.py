"""
Unit tests for the result models in the AI SERP Keyword Research Agent.
"""

import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from ai_serp_keyword_research.core.models.analysis import (
    IntentType,
    SerpFeatureType,
    Keyword,
    SerpFeature,
    IntentAnalysis,
    MarketGap
)
from ai_serp_keyword_research.core.models.recommendations import (
    TacticType,
    Recommendation,
    RecommendationSet
)
from ai_serp_keyword_research.core.models.results import AnalysisResult


class TestAnalysisResultModel:
    """Test suite for the AnalysisResult model."""
    
    def test_valid_analysis_result(self):
        """Test creating an AnalysisResult with valid data."""
        # Create components for the analysis result
        intent_analysis = IntentAnalysis(
            intent_type=IntentType.TRANSACTIONAL,
            confidence=0.87,
            main_keyword=Keyword(text="dad graphic tee", relevance=0.95, frequency=8),
            secondary_keywords=[
                Keyword(text="funny dad shirt", relevance=0.85, frequency=5)
            ]
        )
        
        market_gap = MarketGap(
            detected=True,
            description="Limited personalized dad shirts with profession themes",
            opportunity_score=0.75,
            competition_level=0.4
        )
        
        serp_features = [
            SerpFeature(
                feature_type=SerpFeatureType.SHOPPING_ADS,
                position=1,
                data={"products": 3}
            ),
            SerpFeature(
                feature_type=SerpFeatureType.FEATURED_SNIPPET,
                position=3,
                data={"content": "Sample featured snippet content"}
            ),
            SerpFeature(
                feature_type=SerpFeatureType.IMAGE_PACK,
                position=None  # No specific position
            )
        ]
        
        recommendations = RecommendationSet(
            recommendations=[
                Recommendation(
                    tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                    description="Create product pages targeting 'profession + dad shirt' keywords",
                    priority=1,
                    confidence=0.85
                )
            ],
            intent_based=True,
            market_gap_based=True
        )
        
        # Create the complete analysis result
        result = AnalysisResult(
            search_term="funny dad graphic tee",
            analysis_id=str(uuid4()),
            intent_analysis=intent_analysis,
            market_gap=market_gap,
            serp_features=serp_features,
            recommendations=recommendations,
            execution_time=2.34
        )
        
        # Verify basic fields
        assert result.search_term == "funny dad graphic tee"
        assert result.intent_analysis.intent_type == IntentType.TRANSACTIONAL
        assert result.market_gap.detected is True
        assert len(result.serp_features) == 3
        assert len(result.recommendations.recommendations) == 1
        assert result.execution_time == 2.34
        assert isinstance(result.timestamp, datetime)
        
        # Check that SERP features are sorted by position
        assert result.serp_features[0].feature_type == SerpFeatureType.SHOPPING_ADS
        assert result.serp_features[0].position == 1
        assert result.serp_features[1].feature_type == SerpFeatureType.FEATURED_SNIPPET
        assert result.serp_features[1].position == 3
        assert result.serp_features[2].feature_type == SerpFeatureType.IMAGE_PACK
        assert result.serp_features[2].position is None
        
    def test_serp_features_sorting(self):
        """Test that SERP features are sorted properly."""
        result = AnalysisResult(
            search_term="dad graphic tee",
            analysis_id=str(uuid4()),
            intent_analysis=IntentAnalysis(
                intent_type=IntentType.TRANSACTIONAL,
                confidence=0.8,
                main_keyword=Keyword(text="dad tee", relevance=0.9, frequency=7),
                secondary_keywords=[]
            ),
            market_gap=MarketGap(detected=False),
            serp_features=[
                SerpFeature(feature_type=SerpFeatureType.IMAGE_PACK, position=None),
                SerpFeature(feature_type=SerpFeatureType.KNOWLEDGE_PANEL, position=5),
                SerpFeature(feature_type=SerpFeatureType.SHOPPING_ADS, position=1),
                SerpFeature(feature_type=SerpFeatureType.FEATURED_SNIPPET, position=2)
            ],
            recommendations=RecommendationSet(
                recommendations=[
                    Recommendation(
                        tactic_type=TacticType.KEYWORD_TARGETING,
                        description="Target 'dad graphic tee' keywords in product listings",
                        priority=1,
                        confidence=0.9
                    )
                ],
                intent_based=True,
                market_gap_based=False
            )
        )
        
        # Verify features are sorted by position
        assert result.serp_features[0].feature_type == SerpFeatureType.SHOPPING_ADS
        assert result.serp_features[0].position == 1
        assert result.serp_features[1].feature_type == SerpFeatureType.FEATURED_SNIPPET
        assert result.serp_features[1].position == 2
        assert result.serp_features[2].feature_type == SerpFeatureType.KNOWLEDGE_PANEL
        assert result.serp_features[2].position == 5
        assert result.serp_features[3].feature_type == SerpFeatureType.IMAGE_PACK
        assert result.serp_features[3].position is None
        
    def test_consistency_validation(self):
        """Test validation for consistency between components."""
        # Prepare the components
        intent_analysis = IntentAnalysis(
            intent_type=IntentType.TRANSACTIONAL,
            confidence=0.87,
            main_keyword=Keyword(text="dad graphic tee", relevance=0.95, frequency=8),
            secondary_keywords=[]
        )
        
        market_gap = MarketGap(
            detected=True,
            description="Limited personalized dad shirts with profession themes",
            opportunity_score=0.75
        )
        
        # Invalid: market gap detected but recommendations don't address it
        with pytest.raises(ValidationError) as excinfo:
            AnalysisResult(
                search_term="dad graphic tee",
                analysis_id=str(uuid4()),
                intent_analysis=intent_analysis,
                market_gap=market_gap,
                serp_features=[],
                recommendations=RecommendationSet(
                    recommendations=[
                        Recommendation(
                            tactic_type=TacticType.KEYWORD_TARGETING,
                            description="Target 'dad graphic tee' keywords in product listings",
                            priority=1,
                            confidence=0.9
                        )
                    ],
                    intent_based=True,
                    market_gap_based=False  # Should be True since market gap was detected
                )
            )
        assert "When market gap detected, recommendations should address it" in str(excinfo.value)
        
        # Invalid: recommendations not based on detected intent
        with pytest.raises(ValidationError) as excinfo:
            AnalysisResult(
                search_term="dad graphic tee",
                analysis_id=str(uuid4()),
                intent_analysis=intent_analysis,
                market_gap=MarketGap(detected=False),
                serp_features=[],
                recommendations=RecommendationSet(
                    recommendations=[
                        Recommendation(
                            tactic_type=TacticType.KEYWORD_TARGETING,
                            description="Target 'dad graphic tee' keywords in product listings",
                            priority=1,
                            confidence=0.9
                        )
                    ],
                    intent_based=False,  # Should be True since intent was analyzed
                    market_gap_based=False
                )
            )
        assert "Recommendations must be based on detected intent" in str(excinfo.value)
        
        # Valid: all components are consistent
        result = AnalysisResult(
            search_term="dad graphic tee",
            analysis_id=str(uuid4()),
            intent_analysis=intent_analysis,
            market_gap=market_gap,
            serp_features=[],
            recommendations=RecommendationSet(
                recommendations=[
                    Recommendation(
                        tactic_type=TacticType.KEYWORD_TARGETING,
                        description="Target 'dad graphic tee' keywords in product listings",
                        priority=1,
                        confidence=0.9
                    )
                ],
                intent_based=True,
                market_gap_based=True  # Correctly matches market gap detection
            )
        )
        assert result.recommendations.intent_based is True
        assert result.recommendations.market_gap_based is True
        
    def test_search_term_validation(self):
        """Test validation for search term."""
        # Valid search term
        result = AnalysisResult(
            search_term="dad graphic tee",
            analysis_id=str(uuid4()),
            intent_analysis=IntentAnalysis(
                intent_type=IntentType.TRANSACTIONAL,
                confidence=0.8,
                main_keyword=Keyword(text="dad tee", relevance=0.9, frequency=7),
                secondary_keywords=[]
            ),
            market_gap=MarketGap(detected=False),
            serp_features=[],
            recommendations=RecommendationSet(
                recommendations=[
                    Recommendation(
                        tactic_type=TacticType.KEYWORD_TARGETING,
                        description="Target 'dad graphic tee' keywords in product listings",
                        priority=1,
                        confidence=0.9
                    )
                ],
                intent_based=True,
                market_gap_based=False
            )
        )
        assert result.search_term == "dad graphic tee"
        
        # Invalid: search term too short
        with pytest.raises(ValidationError) as excinfo:
            AnalysisResult(
                search_term="aa",  # Too short
                analysis_id=str(uuid4()),
                intent_analysis=IntentAnalysis(
                    intent_type=IntentType.TRANSACTIONAL,
                    confidence=0.8,
                    main_keyword=Keyword(text="dad tee", relevance=0.9, frequency=7),
                    secondary_keywords=[]
                ),
                market_gap=MarketGap(detected=False),
                serp_features=[],
                recommendations=RecommendationSet(
                    recommendations=[
                        Recommendation(
                            tactic_type=TacticType.KEYWORD_TARGETING,
                            description="Target 'dad graphic tee' keywords in product listings",
                            priority=1,
                            confidence=0.9
                        )
                    ],
                    intent_based=True,
                    market_gap_based=False
                )
            )
        assert "ensure this value has at least 3 characters" in str(excinfo.value) 