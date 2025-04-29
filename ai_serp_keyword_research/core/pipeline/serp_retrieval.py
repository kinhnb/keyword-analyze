"""
SERP retrieval stage for the SERP analysis pipeline.

This module implements the second stage of the pipeline, which fetches
SERP data from an external API and extracts relevant features.
"""

import logging
import time
from typing import Dict, List, Optional, Any
import backoff

from ai_serp_keyword_research.core.models.input import SearchTerm
from ai_serp_keyword_research.core.models.analysis import SerpFeature, SerpFeatureType
from ai_serp_keyword_research.core.pipeline.base import PipelineContext, PipelineStage

# Configure logging
logger = logging.getLogger(__name__)


class SerpRetrievalStage(PipelineStage[SearchTerm, Dict[str, Any]]):
    """
    Second stage of the SERP analysis pipeline.
    
    This stage is responsible for:
    1. Calling the SERP API to retrieve search results
    2. Implementing retry/backoff logic for API failures
    3. Parsing the response data
    4. Detecting SERP features
    """
    
    def __init__(self, serp_provider, cache_service=None):
        """
        Initialize the SERP retrieval stage.
        
        Args:
            serp_provider: Service for retrieving SERP data.
            cache_service: Optional cache service for storing SERP results.
                           If None, caching will be disabled.
        """
        self._serp_provider = serp_provider
        self._cache_service = cache_service
        
    @property
    def name(self) -> str:
        return "SERP Retrieval Stage"
        
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def _fetch_serp_data(self, search_term: str, max_results: int) -> Dict[str, Any]:
        """
        Fetch SERP data with exponential backoff retry.
        
        Args:
            search_term: The search term to fetch results for.
            max_results: Maximum number of results to retrieve.
            
        Returns:
            The SERP response data.
            
        Raises:
            Exception: If all retry attempts fail.
        """
        return await self._serp_provider.fetch_results(search_term, max_results)
        
    async def process(self, input_data: SearchTerm, context: Optional[PipelineContext] = None) -> Dict[str, Any]:
        """
        Process the search term and retrieve SERP data.
        
        Args:
            input_data: The validated search term.
            context: Optional pipeline context for sharing state.
            
        Returns:
            Dictionary containing parsed SERP data.
            
        Raises:
            RuntimeError: If SERP retrieval fails after retries.
        """
        if context is None:
            context = PipelineContext()
            
        # If we have cached results, we can skip the API call
        if context.contains("has_cached_result") and context.get("has_cached_result"):
            logger.info("Using cached SERP results")
            return context.get("cached_result")
            
        search_term = input_data.term
        max_results = input_data.max_results
        
        # Check if SERP data is already cached
        serp_data = None
        if self._cache_service:
            try:
                serp_data = await self._cache_service.get_serp_data(search_term)
                if serp_data:
                    logger.info(f"Found cached SERP data for search term: {search_term}")
            except Exception as e:
                logger.warning(f"Error checking SERP cache: {str(e)}")
                
        # If not in cache, fetch from the API
        if not serp_data:
            logger.info(f"Fetching SERP data for search term: {search_term}")
            start_time = time.time()
            
            try:
                serp_data = await self._fetch_serp_data(search_term, max_results)
                
                # Cache the results if we have a cache service
                if self._cache_service:
                    try:
                        await self._cache_service.set_serp_data(search_term, serp_data)
                    except Exception as e:
                        logger.warning(f"Error caching SERP data: {str(e)}")
                        
            except Exception as e:
                logger.error(f"SERP retrieval failed after retries: {str(e)}")
                raise RuntimeError(f"Failed to retrieve SERP data: {str(e)}")
                
            elapsed_time = time.time() - start_time
            logger.info(f"SERP data fetched in {elapsed_time:.2f} seconds")
            
        # Extract SERP features
        serp_features = self._extract_serp_features(serp_data)
        
        # Store results in context
        context.set("serp_data", serp_data)
        context.set("serp_features", serp_features)
        
        return serp_data
        
    def _extract_serp_features(self, serp_data: Dict[str, Any]) -> List[SerpFeature]:
        """
        Extract SERP features from the response data.
        
        Args:
            serp_data: The SERP response data.
            
        Returns:
            List of detected SERP features.
        """
        features = []
        
        # This implementation will depend on the structure of the SERP provider's response
        # Below is a simplified example of how feature extraction might work
        
        # Check for shopping ads
        if "shopping_ads" in serp_data and serp_data["shopping_ads"]:
            position = serp_data.get("shopping_ads_position", 0)
            features.append(
                SerpFeature(
                    feature_type=SerpFeatureType.SHOPPING_ADS,
                    position=position,
                    data={"products": len(serp_data["shopping_ads"])}
                )
            )
            
        # Check for featured snippet
        if "featured_snippet" in serp_data and serp_data["featured_snippet"]:
            features.append(
                SerpFeature(
                    feature_type=SerpFeatureType.FEATURED_SNIPPET,
                    position=0,  # Featured snippets are typically at position 0
                    data={"content": serp_data["featured_snippet"].get("content", "")}
                )
            )
            
        # Check for image pack
        if "image_pack" in serp_data and serp_data["image_pack"]:
            position = serp_data.get("image_pack_position")
            features.append(
                SerpFeature(
                    feature_type=SerpFeatureType.IMAGE_PACK,
                    position=position,
                    data={"images": len(serp_data["image_pack"])}
                )
            )
            
        # Additional feature detection logic would go here
        # This would be expanded based on the specific SERP API response structure
        
        return features 