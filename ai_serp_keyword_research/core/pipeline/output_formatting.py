"""
Output formatting stage for the SERP analysis pipeline.

This module implements the sixth stage of the pipeline, which compiles
all analysis components into a structured output and handles caching.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from ai_serp_keyword_research.core.models.analysis import MarketGap, SerpFeature
from ai_serp_keyword_research.core.models.recommendations import RecommendationSet
from ai_serp_keyword_research.core.models.results import AnalysisResult
from ai_serp_keyword_research.core.pipeline.base import PipelineContext, PipelineStage

# Configure logging
logger = logging.getLogger(__name__)


class OutputFormattingStage(PipelineStage[RecommendationSet, AnalysisResult]):
    """
    Sixth stage of the SERP analysis pipeline.
    
    This stage is responsible for:
    1. Compiling all analysis components into a structured output
    2. Validating the completeness and consistency of the analysis
    3. Formatting the results for API response
    4. Caching the results for future reference
    """
    
    def __init__(self, cache_service=None):
        """
        Initialize the output formatting stage.
        
        Args:
            cache_service: Optional cache service for storing analysis results.
                           If None, caching will be disabled.
        """
        self._cache_service = cache_service
        
    @property
    def name(self) -> str:
        return "Output Formatting Stage"
    
    async def process(self, input_data: RecommendationSet, context: Optional[PipelineContext] = None) -> AnalysisResult:
        """
        Process the input data and return a formatted analysis result.
        
        Args:
            input_data: The recommendation set from the previous stage.
            context: The pipeline context containing all analysis components.
            
        Returns:
            A complete analysis result with all components.
            
        Raises:
            ValueError: If required components are missing from the context.
        """
        if not context:
            raise ValueError("Pipeline context is required for output formatting")
        
        # Fetch all required components from the context
        search_term = context.get("search_term")
        if not search_term:
            raise ValueError("Search term is missing from context")
        
        intent_analysis = context.get("intent_analysis")
        if not intent_analysis:
            raise ValueError("Intent analysis is missing from context")
        
        market_gap = context.get("market_gap")
        if not market_gap:
            raise ValueError("Market gap analysis is missing from context")
        
        serp_features = context.get("serp_features", [])
        
        # Get optional components
        raw_data = context.get("serp_data")
        start_time = context.get("start_time")
        
        # Calculate execution time if start time is available
        execution_time = None
        if start_time:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Generate a unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Create the complete analysis result
        result = AnalysisResult(
            search_term=search_term,
            analysis_id=analysis_id,
            intent_analysis=intent_analysis,
            market_gap=market_gap,
            serp_features=serp_features,
            recommendations=input_data,
            raw_data=raw_data,
            execution_time=execution_time
        )
        
        # Cache the result if caching is enabled
        if self._cache_service:
            try:
                await self._cache_service.store_analysis(search_term, result)
                logger.info(f"Cached analysis result for search term: {search_term}")
            except Exception as e:
                logger.warning(f"Failed to cache analysis result: {str(e)}")
        
        return result 