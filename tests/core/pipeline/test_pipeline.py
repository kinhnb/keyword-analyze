"""
Unit tests for the SERP analysis pipeline.

This module contains tests for the main pipeline orchestrator that coordinates
all stages of the SERP analysis process.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch, MagicMock

from ai_serp_keyword_research.core.models.input import SearchTerm
from ai_serp_keyword_research.core.models.analysis import IntentAnalysis, MarketGap
from ai_serp_keyword_research.core.models.recommendations import RecommendationSet
from ai_serp_keyword_research.core.models.results import AnalysisResult
from ai_serp_keyword_research.core.pipeline.pipeline import SerpAnalysisPipeline
from ai_serp_keyword_research.core.pipeline.base import PipelineContext


class TestSerpAnalysisPipeline:
    """Test suite for the SERP analysis pipeline orchestrator."""
    
    @pytest.fixture
    def mock_stages(self):
        """Create mock pipeline stages."""
        # Create mock stages
        input_validation_stage = AsyncMock()
        input_validation_stage.name = "Input Validation Stage"
        input_validation_stage.process = AsyncMock()
        
        serp_retrieval_stage = AsyncMock()
        serp_retrieval_stage.name = "SERP Retrieval Stage"
        serp_retrieval_stage.process = AsyncMock()
        
        intent_analysis_stage = AsyncMock()
        intent_analysis_stage.name = "Intent Analysis Stage"
        intent_analysis_stage.process = AsyncMock()
        
        market_gap_analysis_stage = AsyncMock()
        market_gap_analysis_stage.name = "Market Gap Analysis Stage"
        market_gap_analysis_stage.process = AsyncMock()
        
        recommendation_generation_stage = AsyncMock()
        recommendation_generation_stage.name = "Recommendation Generation Stage"
        recommendation_generation_stage.process = AsyncMock()
        
        output_formatting_stage = AsyncMock()
        output_formatting_stage.name = "Output Formatting Stage"
        output_formatting_stage.process = AsyncMock()
        
        return {
            'input_validation': input_validation_stage,
            'serp_retrieval': serp_retrieval_stage,
            'intent_analysis': intent_analysis_stage,
            'market_gap_analysis': market_gap_analysis_stage,
            'recommendation_generation': recommendation_generation_stage,
            'output_formatting': output_formatting_stage
        }
    
    @pytest.fixture
    def pipeline(self, mock_stages):
        """Create a pipeline with mock stages."""
        return SerpAnalysisPipeline(
            input_validation_stage=mock_stages['input_validation'],
            serp_retrieval_stage=mock_stages['serp_retrieval'],
            intent_analysis_stage=mock_stages['intent_analysis'],
            market_gap_analysis_stage=mock_stages['market_gap_analysis'],
            recommendation_generation_stage=mock_stages['recommendation_generation'],
            output_formatting_stage=mock_stages['output_formatting']
        )
    
    @pytest.mark.asyncio
    async def test_process_successful_pipeline(self, pipeline, mock_stages):
        """Test successful processing through all pipeline stages."""
        # Setup
        search_term = SearchTerm(term="dad graphic tee", max_results=10)
        
        # Mock return values for each stage
        validated_input = SearchTerm(term="dad graphic tee", max_results=10)
        mock_stages['input_validation'].process.return_value = validated_input
        
        serp_data = {'results': [{'title': 'Test Result'}]}
        mock_stages['serp_retrieval'].process.return_value = serp_data
        
        intent_analysis = Mock(spec=IntentAnalysis)
        mock_stages['intent_analysis'].process.return_value = intent_analysis
        
        market_gap = Mock(spec=MarketGap)
        mock_stages['market_gap_analysis'].process.return_value = market_gap
        
        recommendations = Mock(spec=RecommendationSet)
        mock_stages['recommendation_generation'].process.return_value = recommendations
        
        analysis_result = Mock(spec=AnalysisResult)
        mock_stages['output_formatting'].process.return_value = analysis_result
        
        # Execute
        result = await pipeline.process(search_term)
        
        # Assert
        assert result == analysis_result
        
        # Verify that each stage was called with the correct input
        mock_stages['input_validation'].process.assert_called_once()
        mock_stages['serp_retrieval'].process.assert_called_once_with(validated_input, pytest.ANY)
        mock_stages['intent_analysis'].process.assert_called_once_with(serp_data, pytest.ANY)
        mock_stages['market_gap_analysis'].process.assert_called_once_with(intent_analysis, pytest.ANY)
        mock_stages['recommendation_generation'].process.assert_called_once_with(market_gap, pytest.ANY)
        mock_stages['output_formatting'].process.assert_called_once_with(recommendations, pytest.ANY)
    
    @pytest.mark.asyncio
    async def test_process_with_stage_error(self, pipeline, mock_stages):
        """Test error handling when a pipeline stage fails."""
        # Setup
        search_term = SearchTerm(term="dad graphic tee", max_results=10)
        
        # Make the SERP retrieval stage fail
        mock_stages['serp_retrieval'].process.side_effect = ValueError("API failure")
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Search term analysis failed: API failure"):
            await pipeline.process(search_term)
        
        # Verify that stages were called in order until failure
        mock_stages['input_validation'].process.assert_called_once()
        mock_stages['serp_retrieval'].process.assert_called_once()
        mock_stages['intent_analysis'].process.assert_not_called()
        mock_stages['market_gap_analysis'].process.assert_not_called()
        mock_stages['recommendation_generation'].process.assert_not_called()
        mock_stages['output_formatting'].process.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_context_propagation(self, pipeline, mock_stages):
        """Test that context is properly propagated through all stages."""
        # Setup
        search_term = SearchTerm(term="dad graphic tee", max_results=10)
        
        # Configure mocks to capture context
        contexts = []
        
        def capture_context(data, context):
            contexts.append(context)
            return data
        
        mock_stages['input_validation'].process.side_effect = lambda data, context: capture_context(data, context)
        mock_stages['serp_retrieval'].process.side_effect = lambda data, context: capture_context(data, context)
        mock_stages['intent_analysis'].process.side_effect = lambda data, context: capture_context(data, context)
        mock_stages['market_gap_analysis'].process.side_effect = lambda data, context: capture_context(data, context)
        mock_stages['recommendation_generation'].process.side_effect = lambda data, context: capture_context(data, context)
        mock_stages['output_formatting'].process.side_effect = lambda data, context: capture_context(data, context)
        
        # Execute
        await pipeline.process(search_term)
        
        # Assert
        assert len(contexts) == 6  # One context per stage
        
        # Check that the same context object is passed to each stage
        for i in range(1, 6):
            assert contexts[i] is contexts[0]
        
        # Verify context contains expected keys
        assert contexts[0].contains("search_term")
        assert contexts[0].contains("start_time")
    
    def test_get_context_key_for_stage(self, pipeline):
        """Test the mapping of stage indices to context keys."""
        assert pipeline._get_context_key_for_stage(0) == "validated_input"
        assert pipeline._get_context_key_for_stage(1) == "serp_data"
        assert pipeline._get_context_key_for_stage(2) == "intent_analysis"
        assert pipeline._get_context_key_for_stage(3) == "market_gap"
        assert pipeline._get_context_key_for_stage(4) == "recommendations"
        assert pipeline._get_context_key_for_stage(5) is None
        assert pipeline._get_context_key_for_stage(99) is None
    
    def test_log_error_context(self, pipeline, caplog):
        """Test error context logging."""
        # Setup
        context = PipelineContext()
        context.set("search_term", "dad graphic tee")
        context.set("validated_input", {})
        context.set("serp_data", {})
        error = ValueError("Test error")
        
        # Execute
        with patch('ai_serp_keyword_research.core.pipeline.pipeline.logger') as mock_logger:
            pipeline._log_error_context(context, error)
            
            # Assert
            mock_logger.error.assert_any_call("Pipeline error: Test error")
            mock_logger.error.assert_any_call("Completed stages before error: Input Validation, SERP Retrieval")
            mock_logger.error.assert_any_call("Search term: dad graphic tee") 