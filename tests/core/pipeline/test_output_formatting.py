"""
Unit tests for the OutputFormattingStage.

This module contains tests for the final stage of the SERP analysis pipeline
that compiles all analysis components into a structured output.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID

from ai_serp_keyword_research.core.models.analysis import (
    IntentType,
    Keyword,
    IntentAnalysis,
    MarketGap,
    SerpFeature,
    SerpFeatureType
)
from ai_serp_keyword_research.core.models.recommendations import (
    RecommendationSet,
    Recommendation,
    TacticType
)
from ai_serp_keyword_research.core.models.results import AnalysisResult
from ai_serp_keyword_research.core.pipeline.base import PipelineContext
from ai_serp_keyword_research.core.pipeline.output_formatting import OutputFormattingStage


class TestOutputFormattingStage:
    """Test suite for the output formatting pipeline stage."""
    
    @pytest.fixture
    def pipeline_context(self):
        """Create a pipeline context with test data."""
        context = PipelineContext()
        
        # Add search term
        context.set("search_term", "dad graphic tee")
        
        # Add intent analysis
        intent_analysis = IntentAnalysis(
            intent_type=IntentType.TRANSACTIONAL,
            confidence=0.87,
            main_keyword=Keyword(text="dad graphic tee", relevance=0.95, frequency=8),
            secondary_keywords=[
                Keyword(text="funny dad shirt", relevance=0.85, frequency=5)
            ]
        )
        context.set("intent_analysis", intent_analysis)
        
        # Add market gap
        market_gap = MarketGap(
            detected=True,
            description="Limited personalized dad shirts with profession themes",
            opportunity_score=0.75,
            competition_level=0.4
        )
        context.set("market_gap", market_gap)
        
        # Add SERP features
        serp_features = [
            SerpFeature(
                feature_type=SerpFeatureType.SHOPPING_ADS,
                position=1,
                data={"products": 3}
            )
        ]
        context.set("serp_features", serp_features)
        
        # Add SERP data
        context.set("serp_data", {"results": [{"title": "Test Result"}]})
        
        # Add start time
        context.set("start_time", datetime.utcnow())
        
        return context
    
    @pytest.fixture
    def recommendations(self):
        """Create a test recommendation set."""
        return RecommendationSet(
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
    
    @pytest.fixture
    def mock_cache_service(self):
        """Create a mock cache service."""
        cache_service = AsyncMock()
        cache_service.store_analysis = AsyncMock()
        return cache_service
    
    @pytest.mark.asyncio
    async def test_process_with_complete_context(self, pipeline_context, recommendations, mock_cache_service):
        """Test processing with all required context components."""
        # Setup
        stage = OutputFormattingStage(cache_service=mock_cache_service)
        
        # Execute
        result = await stage.process(recommendations, pipeline_context)
        
        # Assert
        assert isinstance(result, AnalysisResult)
        assert result.search_term == "dad graphic tee"
        assert isinstance(result.analysis_id, str)
        assert result.intent_analysis.intent_type == IntentType.TRANSACTIONAL
        assert result.market_gap.detected == True
        assert len(result.serp_features) == 1
        assert result.recommendations.recommendations[0].tactic_type == TacticType.PRODUCT_PAGE_OPTIMIZATION
        assert result.raw_data is not None
        assert result.execution_time is not None
        
        # Verify cache service was called
        mock_cache_service.store_analysis.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_with_missing_context(self, recommendations):
        """Test processing with missing context."""
        # Setup
        stage = OutputFormattingStage()
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Pipeline context is required for output formatting"):
            await stage.process(recommendations, None)
    
    @pytest.mark.asyncio
    async def test_process_with_missing_search_term(self, pipeline_context, recommendations):
        """Test processing with missing search term in context."""
        # Setup
        stage = OutputFormattingStage()
        pipeline_context.remove("search_term")
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Search term is missing from context"):
            await stage.process(recommendations, pipeline_context)
    
    @pytest.mark.asyncio
    async def test_process_with_missing_intent_analysis(self, pipeline_context, recommendations):
        """Test processing with missing intent analysis in context."""
        # Setup
        stage = OutputFormattingStage()
        pipeline_context.remove("intent_analysis")
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Intent analysis is missing from context"):
            await stage.process(recommendations, pipeline_context)
    
    @pytest.mark.asyncio
    async def test_process_with_missing_market_gap(self, pipeline_context, recommendations):
        """Test processing with missing market gap in context."""
        # Setup
        stage = OutputFormattingStage()
        pipeline_context.remove("market_gap")
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Market gap analysis is missing from context"):
            await stage.process(recommendations, pipeline_context)
    
    @pytest.mark.asyncio
    async def test_process_without_caching(self, pipeline_context, recommendations):
        """Test processing without a cache service."""
        # Setup
        stage = OutputFormattingStage(cache_service=None)
        
        # Execute
        result = await stage.process(recommendations, pipeline_context)
        
        # Assert
        assert isinstance(result, AnalysisResult)
        assert result.search_term == "dad graphic tee"
    
    @pytest.mark.asyncio
    async def test_cache_error_handling(self, pipeline_context, recommendations):
        """Test handling of cache errors."""
        # Setup
        mock_cache = AsyncMock()
        mock_cache.store_analysis.side_effect = Exception("Cache error")
        stage = OutputFormattingStage(cache_service=mock_cache)
        
        # Execute (should not raise exception)
        result = await stage.process(recommendations, pipeline_context)
        
        # Assert
        assert isinstance(result, AnalysisResult)
        assert result.search_term == "dad graphic tee"
        # Verify cache was attempted
        mock_cache.store_analysis.assert_called_once() 