"""
SERP analysis pipeline implementation for the AI SERP Keyword Research Agent.

This module implements the main pipeline orchestrator that coordinates
all pipeline stages for analyzing search terms and generating recommendations.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from ai_serp_keyword_research.core.models.input import SearchTerm
from ai_serp_keyword_research.core.models.results import AnalysisResult
from ai_serp_keyword_research.core.pipeline.base import PipelineContext, PipelineStage
from ai_serp_keyword_research.core.pipeline.input_validation import InputValidationStage
from ai_serp_keyword_research.core.pipeline.serp_retrieval import SerpRetrievalStage
from ai_serp_keyword_research.core.pipeline.intent_analysis import IntentAnalysisStage
from ai_serp_keyword_research.core.pipeline.market_gap_analysis import MarketGapAnalysisStage
from ai_serp_keyword_research.core.pipeline.recommendation_generation import RecommendationGenerationStage
from ai_serp_keyword_research.core.pipeline.output_formatting import OutputFormattingStage

# Configure logging
logger = logging.getLogger(__name__)


class SerpAnalysisPipeline:
    """
    Main pipeline orchestrator for SERP analysis.
    
    This class coordinates all pipeline stages, manages the flow of data
    between stages, and handles context sharing and error recovery.
    """
    
    def __init__(
        self,
        input_validation_stage: InputValidationStage,
        serp_retrieval_stage: SerpRetrievalStage,
        intent_analysis_stage: IntentAnalysisStage,
        market_gap_analysis_stage: MarketGapAnalysisStage,
        recommendation_generation_stage: RecommendationGenerationStage,
        output_formatting_stage: OutputFormattingStage
    ):
        """
        Initialize the SERP analysis pipeline with all required stages.
        
        Args:
            input_validation_stage: Stage for validating and normalizing input.
            serp_retrieval_stage: Stage for retrieving SERP data.
            intent_analysis_stage: Stage for analyzing search intent.
            market_gap_analysis_stage: Stage for detecting market gaps.
            recommendation_generation_stage: Stage for generating recommendations.
            output_formatting_stage: Stage for formatting the final output.
        """
        self.stages = [
            input_validation_stage,
            serp_retrieval_stage,
            intent_analysis_stage,
            market_gap_analysis_stage,
            recommendation_generation_stage,
            output_formatting_stage
        ]
        
    async def process(self, search_term: SearchTerm) -> AnalysisResult:
        """
        Process a search term through the complete pipeline.
        
        Args:
            search_term: The search term to analyze.
            
        Returns:
            The complete analysis result.
            
        Raises:
            ValueError: If any pipeline stage fails.
        """
        # Initialize pipeline context
        context = PipelineContext()
        
        # Record start time for performance tracking
        start_time = datetime.utcnow()
        context.set("start_time", start_time)
        
        # Store original search term in context
        context.set("search_term", search_term.term)
        
        # Initialize input data for first stage
        current_data = search_term
        
        try:
            # Process through each stage
            for i, stage in enumerate(self.stages):
                logger.info(f"Processing stage {i+1}/{len(self.stages)}: {stage.name}")
                
                # Process current stage
                current_data = await stage.process(current_data, context)
                
                # Store result in context if not the final stage
                if i < len(self.stages) - 1:
                    context_key = self._get_context_key_for_stage(i)
                    if context_key:
                        context.set(context_key, current_data)
                
                logger.info(f"Completed stage {i+1}/{len(self.stages)}: {stage.name}")
                
            # Final result is the output of the last stage
            result = current_data
            
            # Calculate and log total execution time
            total_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Total pipeline execution time: {total_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            # Log detailed context information for debugging
            self._log_error_context(context, e)
            raise ValueError(f"Search term analysis failed: {str(e)}")
    
    def _get_context_key_for_stage(self, stage_index: int) -> Optional[str]:
        """
        Get the context key for storing the result of a specific stage.
        
        Args:
            stage_index: The index of the stage in the pipeline.
            
        Returns:
            The context key or None if no specific key is needed.
        """
        # Map stage index to context key
        context_keys = {
            0: "validated_input",  # Input Validation Stage
            1: "serp_data",        # SERP Retrieval Stage
            2: "intent_analysis",  # Intent Analysis Stage
            3: "market_gap",       # Market Gap Analysis Stage
            4: "recommendations",  # Recommendation Generation Stage
        }
        
        return context_keys.get(stage_index)
    
    def _log_error_context(self, context: PipelineContext, error: Exception) -> None:
        """
        Log detailed context information when an error occurs.
        
        Args:
            context: The pipeline context at the time of error.
            error: The exception that occurred.
        """
        logger.error(f"Pipeline error: {str(error)}")
        
        # Log which stages were completed
        completed_stages = []
        if context.contains("validated_input"):
            completed_stages.append("Input Validation")
        if context.contains("serp_data"):
            completed_stages.append("SERP Retrieval")
        if context.contains("intent_analysis"):
            completed_stages.append("Intent Analysis")
        if context.contains("market_gap"):
            completed_stages.append("Market Gap Analysis")
        if context.contains("recommendations"):
            completed_stages.append("Recommendation Generation")
            
        logger.error(f"Completed stages before error: {', '.join(completed_stages)}")
        
        # Log search term
        search_term = context.get("search_term")
        if search_term:
            logger.error(f"Search term: {search_term}")
            
        # Additional error context can be added here as needed 