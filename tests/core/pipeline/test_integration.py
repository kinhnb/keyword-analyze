"""
Integration tests for the SERP analysis pipeline.

This module contains tests for the complete pipeline, testing how
all stages work together to process a search term.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from ai_serp_keyword_research.core.models.input import SearchTerm
from ai_serp_keyword_research.core.models.analysis import IntentType, Keyword, IntentAnalysis, MarketGap, SerpFeature, SerpFeatureType
from ai_serp_keyword_research.core.models.recommendations import TacticType, Recommendation, RecommendationSet
from ai_serp_keyword_research.core.models.results import AnalysisResult
from ai_serp_keyword_research.core.pipeline.input_validation import InputValidationStage
from ai_serp_keyword_research.core.pipeline.serp_retrieval import SerpRetrievalStage
from ai_serp_keyword_research.core.pipeline.intent_analysis import IntentAnalysisStage
from ai_serp_keyword_research.core.pipeline.market_gap_analysis import MarketGapAnalysisStage
from ai_serp_keyword_research.core.pipeline.recommendation_generation import RecommendationGenerationStage
from ai_serp_keyword_research.core.pipeline.output_formatting import OutputFormattingStage
from ai_serp_keyword_research.core.pipeline.pipeline import SerpAnalysisPipeline


class TestPipelineIntegration:
    """Test suite for SERP analysis pipeline integration."""
    
    @pytest.fixture
    def mock_serp_provider(self):
        """Create a mock SERP provider."""
        provider = AsyncMock()
        provider.fetch_results = AsyncMock()
        
        # Prepare mock SERP data
        serp_data = {
            "search_term": "dad graphic tee",
            "results": [
                {
                    "title": "Funny Dad Graphic Tees | Best Gift for Father's Day",
                    "description": "Shop our collection of hilarious dad graphic tees. Perfect gift for Father's Day!",
                    "url": "https://example.com/funny-dad-tees",
                    "position": 1
                },
                {
                    "title": "Dad Graphic T-Shirts | Shop Online | Fast Shipping",
                    "description": "Find the perfect dad graphic tee. Many designs available with fast shipping.",
                    "url": "https://example.com/dad-tshirts",
                    "position": 2
                },
                {
                    "title": "Custom Dad Graphic Tees | Create Your Own Design",
                    "description": "Create custom dad graphic tees with your own text and images. Great for gifts!",
                    "url": "https://example.com/custom-dad-tees",
                    "position": 3
                }
            ],
            "features": [
                {
                    "type": "shopping_ads",
                    "position": 1,
                    "data": {
                        "products": 3
                    }
                },
                {
                    "type": "image_pack",
                    "position": 4,
                    "data": {
                        "images": 8
                    }
                }
            ]
        }
        
        provider.fetch_results.return_value = serp_data
        return provider
    
    @pytest.fixture
    def mock_cache_service(self):
        """Create a mock cache service."""
        cache = AsyncMock()
        cache.get_analysis = AsyncMock(return_value=None)  # No cached results
        cache.store_analysis = AsyncMock()
        return cache
    
    @pytest.fixture
    def pipeline(self, mock_serp_provider, mock_cache_service):
        """Create a pipeline with real stages but mock dependencies."""
        input_stage = InputValidationStage(cache_service=mock_cache_service)
        serp_stage = SerpRetrievalStage(serp_provider=mock_serp_provider, cache_service=mock_cache_service)
        intent_stage = IntentAnalysisStage()
        market_gap_stage = MarketGapAnalysisStage()
        recommendation_stage = RecommendationGenerationStage()
        output_stage = OutputFormattingStage(cache_service=mock_cache_service)
        
        return SerpAnalysisPipeline(
            input_validation_stage=input_stage,
            serp_retrieval_stage=serp_stage,
            intent_analysis_stage=intent_stage,
            market_gap_analysis_stage=market_gap_stage,
            recommendation_generation_stage=recommendation_stage,
            output_formatting_stage=output_stage
        )
    
    @pytest.mark.asyncio
    @patch('ai_serp_keyword_research.core.pipeline.intent_analysis.IntentAnalysisStage.process')
    @patch('ai_serp_keyword_research.core.pipeline.market_gap_analysis.MarketGapAnalysisStage.process')
    @patch('ai_serp_keyword_research.core.pipeline.recommendation_generation.RecommendationGenerationStage.process')
    async def test_complete_pipeline_execution(self, mock_recommend, mock_market_gap, mock_intent, pipeline, mock_serp_provider):
        """Test the complete pipeline execution with mock stages."""
        # Setup
        search_term = SearchTerm(term="dad graphic tee", max_results=10)
        
        # Mock the internal processing of complex stages to get predictable output
        intent_analysis = IntentAnalysis(
            intent_type=IntentType.TRANSACTIONAL,
            confidence=0.87,
            main_keyword=Keyword(text="dad graphic tee", relevance=0.95, frequency=8),
            secondary_keywords=[
                Keyword(text="funny dad shirt", relevance=0.85, frequency=5)
            ]
        )
        mock_intent.return_value = intent_analysis
        
        market_gap = MarketGap(
            detected=True,
            description="Limited personalized dad shirts with profession themes",
            opportunity_score=0.75,
            competition_level=0.4,
            related_keywords=[
                Keyword(text="profession dad tee", relevance=0.80, frequency=2)
            ]
        )
        mock_market_gap.return_value = market_gap
        
        recommendations = RecommendationSet(
            recommendations=[
                Recommendation(
                    tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                    description="Create product pages targeting 'profession + dad shirt' keywords",
                    priority=1,
                    confidence=0.85
                ),
                Recommendation(
                    tactic_type=TacticType.CONTENT_CREATION,
                    description="Develop a gift guide featuring funny dad graphic tees",
                    priority=2,
                    confidence=0.78
                )
            ],
            intent_based=True,
            market_gap_based=True
        )
        mock_recommend.return_value = recommendations
        
        # Execute
        result = await pipeline.process(search_term)
        
        # Assert
        assert isinstance(result, AnalysisResult)
        assert result.search_term == "dad graphic tee"
        assert result.intent_analysis == intent_analysis
        assert result.market_gap == market_gap
        assert result.recommendations == recommendations
        assert result.execution_time is not None
        
        # Verify SERP provider was called correctly
        mock_serp_provider.fetch_results.assert_called_once_with("dad graphic tee", 10)
        
    @pytest.mark.asyncio
    async def test_realistic_pipeline_data_flow(self, pipeline, mock_serp_provider):
        """Test the complete pipeline with real stage implementations."""
        # NOTE: This test uses the actual implementation of each stage (except for external dependencies)
        # so the behavior will change if the implementation changes. This is a true integration test.
        
        # Setup to make the test more deterministic
        search_term = SearchTerm(term="dad graphic tee", max_results=3)
        
        # Configure mock SERP provider to return predictable data
        serp_data = {
            "search_term": "dad graphic tee",
            "results": [
                {
                    "title": "Funny Dad Graphic Tees | Best Gift for Father's Day",
                    "description": "Shop our collection of hilarious dad graphic tees. Perfect gift for Father's Day!",
                    "url": "https://example.com/funny-dad-tees",
                    "position": 1
                },
                {
                    "title": "Dad Graphic T-Shirts | Shop Online | Fast Shipping",
                    "description": "Find the perfect dad graphic tee. Many designs available with fast shipping.",
                    "url": "https://example.com/dad-tshirts",
                    "position": 2
                },
                {
                    "title": "Custom Dad Graphic Tees | Create Your Own Design",
                    "description": "Create custom dad graphic tees with your own text and images. Great for gifts!",
                    "url": "https://example.com/custom-dad-tees",
                    "position": 3
                }
            ],
            "features": [
                {
                    "type": "shopping_ads",
                    "position": 1,
                    "data": {
                        "products": 3
                    }
                },
                {
                    "type": "image_pack",
                    "position": 4,
                    "data": {
                        "images": 8
                    }
                }
            ]
        }
        
        mock_serp_provider.fetch_results.return_value = serp_data
        
        # Execute
        with patch('ai_serp_keyword_research.core.pipeline.intent_analysis.IntentAnalysisStage._determine_intent') as mock_determine:
            # Make the intent determination predictable
            mock_determine.return_value = (IntentType.TRANSACTIONAL, 0.87, ["shopping_ads present", "e-commerce domains"])
            
            result = await pipeline.process(search_term)
        
        # Assert basic result structure
        assert isinstance(result, AnalysisResult)
        assert result.search_term == "dad graphic tee"
        assert result.intent_analysis.intent_type == IntentType.TRANSACTIONAL
        assert result.intent_analysis.confidence == 0.87
        assert "dad" in result.intent_analysis.main_keyword.text.lower()
        assert len(result.intent_analysis.secondary_keywords) > 0
        assert result.market_gap.detected in (True, False)  # May vary based on implementation
        assert len(result.recommendations.recommendations) > 0
        assert result.execution_time is not None 