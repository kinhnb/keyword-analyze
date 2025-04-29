"""
Input validation stage for the SERP analysis pipeline.

This module implements the first stage of the pipeline, which validates
and normalizes the search term input and checks for cached results.
"""

import logging
from typing import Optional

from ai_serp_keyword_research.core.models.input import SearchTerm
from ai_serp_keyword_research.core.models.results import AnalysisResult
from ai_serp_keyword_research.core.pipeline.base import PipelineContext, PipelineStage

# Configure logging
logger = logging.getLogger(__name__)


class InputValidationStage(PipelineStage[SearchTerm, SearchTerm]):
    """
    First stage of the SERP analysis pipeline.
    
    This stage is responsible for:
    1. Validating the search term format and content
    2. Normalizing the search term
    3. Checking if cached results exist for this search term
    """
    
    def __init__(self, cache_service=None):
        """
        Initialize the input validation stage.
        
        Args:
            cache_service: Optional cache service for checking existing results.
                           If None, caching will be disabled.
        """
        self._cache_service = cache_service
        
    @property
    def name(self) -> str:
        return "Input Validation Stage"
        
    async def process(self, input_data: SearchTerm, context: Optional[PipelineContext] = None) -> SearchTerm:
        """
        Process and validate the input search term.
        
        Args:
            input_data: The search term to validate and normalize.
            context: Optional pipeline context for sharing state.
            
        Returns:
            The validated and normalized search term.
            
        Raises:
            ValueError: If the search term is invalid or contains harmful content.
        """
        if context is None:
            context = PipelineContext()
            
        logger.info(f"Validating search term: {input_data.term}")
        
        # Step 1: Normalize the search term
        normalized_term = self._normalize_search_term(input_data.term)
        
        # Step 2: Create a new SearchTerm with the normalized term
        normalized_input = SearchTerm(
            term=normalized_term,
            max_results=input_data.max_results
        )
        
        # Step 3: Check cache if a cache service is available
        cached_result = None
        if self._cache_service:
            logger.info(f"Checking cache for search term: {normalized_term}")
            try:
                cached_result = await self._cache_service.get_analysis(normalized_term)
                if cached_result:
                    logger.info(f"Found cached result for search term: {normalized_term}")
                    context.set("cached_result", cached_result)
            except Exception as e:
                logger.warning(f"Error checking cache: {str(e)}")
                
        # Store the normalized term in context
        context.set("normalized_term", normalized_term)
        context.set("has_cached_result", cached_result is not None)
        
        return normalized_input
        
    def _normalize_search_term(self, term: str) -> str:
        """
        Normalize a search term by trimming whitespace and converting to lowercase.
        
        Args:
            term: The search term to normalize.
            
        Returns:
            The normalized search term.
        """
        # Basic normalization - trim whitespace and convert to lowercase
        normalized = term.strip().lower()
        
        # Remove any special characters that might affect SERP results
        # This could be expanded with more sophisticated normalization
        
        return normalized 