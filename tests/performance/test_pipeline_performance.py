"""
Performance tests for the SERP analysis pipeline.
"""
import time
import asyncio
import pytest
import statistics
from unittest.mock import AsyncMock

from ai_serp_keyword_research.core.domain.models import SearchTerm
from ai_serp_keyword_research.core.pipeline.input_validation import InputValidationStage
from ai_serp_keyword_research.core.pipeline.serp_retrieval import SerpRetrievalStage
from ai_serp_keyword_research.core.pipeline.intent_analysis import IntentAnalysisStage
from ai_serp_keyword_research.core.pipeline.market_gap_analysis import MarketGapAnalysisStage
from ai_serp_keyword_research.core.pipeline.recommendation_generation import RecommendationGenerationStage
from ai_serp_keyword_research.core.pipeline.output_formatting import OutputFormattingStage
from ai_serp_keyword_research.core.pipeline.pipeline import SerpAnalysisPipeline, PipelineContext


@pytest.mark.performance
class TestPipelinePerformance:
    """Performance tests for the SERP analysis pipeline."""
    
    @pytest.fixture
    def pipeline_setup(self, mock_redis, sample_serp_data):
        """Set up a pipeline with mocked dependencies for performance testing."""
        # Create mock services
        cache_service = AsyncMock()
        cache_service.get_analysis.return_value = None
        cache_service.store_analysis.return_value = None
        
        serp_provider = AsyncMock()
        serp_provider.fetch_results.return_value = sample_serp_data
        
        # Create stages with mocked dependencies
        input_stage = InputValidationStage(cache_service=cache_service)
        serp_stage = SerpRetrievalStage(serp_provider=serp_provider, cache_service=cache_service)
        intent_stage = IntentAnalysisStage()
        market_gap_stage = MarketGapAnalysisStage()
        recommendation_stage = RecommendationGenerationStage()
        output_stage = OutputFormattingStage(cache_service=cache_service)
        
        # Create pipeline
        pipeline = SerpAnalysisPipeline(
            input_validation_stage=input_stage,
            serp_retrieval_stage=serp_stage,
            intent_analysis_stage=intent_stage,
            market_gap_analysis_stage=market_gap_stage,
            recommendation_generation_stage=recommendation_stage,
            output_formatting_stage=output_stage
        )
        
        return {
            "pipeline": pipeline,
            "search_term": SearchTerm(term="dad graphic tee", max_results=10)
        }
    
    @pytest.mark.asyncio
    async def test_pipeline_execution_time(self, pipeline_setup):
        """Test the execution time of the complete pipeline."""
        pipeline = pipeline_setup["pipeline"]
        search_term = pipeline_setup["search_term"]
        
        # Run multiple iterations to get average performance
        iterations = 5
        execution_times = []
        
        for _ in range(iterations):
            start_time = time.time()
            await pipeline.execute(search_term)
            end_time = time.time()
            execution_time = end_time - start_time
            execution_times.append(execution_time)
        
        # Calculate statistics
        avg_time = statistics.mean(execution_times)
        max_time = max(execution_times)
        min_time = min(execution_times)
        
        # Log performance results
        print(f"\nPipeline Performance Results:")
        print(f"Average execution time: {avg_time:.4f} seconds")
        print(f"Maximum execution time: {max_time:.4f} seconds")
        print(f"Minimum execution time: {min_time:.4f} seconds")
        
        # Verify performance is within acceptable limits
        # This is a placeholder assertion - adjust based on actual requirements
        assert avg_time < 10.0, f"Average execution time {avg_time:.4f}s exceeds threshold of 10.0s"
    
    @pytest.mark.asyncio
    async def test_individual_stage_timing(self, pipeline_setup):
        """Test the execution time of individual pipeline stages."""
        pipeline = pipeline_setup["pipeline"]
        search_term = pipeline_setup["search_term"]
        
        # Prepare context
        context = PipelineContext()
        
        # Test each stage individually
        stages = [
            ("Input Validation", pipeline.input_validation_stage, search_term),
            ("SERP Retrieval", pipeline.serp_retrieval_stage, search_term),
            ("Intent Analysis", pipeline.intent_analysis_stage, {}),  # Mock input for later stages
            ("Market Gap Analysis", pipeline.market_gap_analysis_stage, {}),
            ("Recommendation Generation", pipeline.recommendation_generation_stage, {}),
            ("Output Formatting", pipeline.output_formatting_stage, {})
        ]
        
        results = {}
        
        for stage_name, stage, input_data in stages:
            # Run multiple iterations
            iterations = 5
            stage_times = []
            
            for _ in range(iterations):
                start_time = time.time()
                await stage.process(input_data, context)
                end_time = time.time()
                stage_times.append(end_time - start_time)
            
            # Calculate statistics
            avg_time = statistics.mean(stage_times)
            results[stage_name] = avg_time
        
        # Log results
        print("\nStage Performance Results:")
        for stage_name, avg_time in results.items():
            print(f"{stage_name}: {avg_time:.4f} seconds")
        
        # Identify the slowest stage
        slowest_stage = max(results.items(), key=lambda x: x[1])
        print(f"\nSlowest stage: {slowest_stage[0]} ({slowest_stage[1]:.4f} seconds)")
        
        # Ensure all stages complete within reasonable time
        for stage_name, avg_time in results.items():
            assert avg_time < 5.0, f"{stage_name} average time {avg_time:.4f}s exceeds threshold of 5.0s" 