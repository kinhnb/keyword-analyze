"""
Redis caching service for the AI SERP Keyword Research Agent.

This module implements a Redis-based caching service for storing and retrieving
SERP data, analysis results, and recommendations. It includes connection management
with proper pooling and error handling.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional, Union, List

import redis.asyncio as redis
from pydantic import BaseModel

from ai_serp_keyword_research.core.models.results import AnalysisResult

# Configure logging
logger = logging.getLogger(__name__)

# Default connection values
DEFAULT_REDIS_URL = "redis://localhost:6379/0"
DEFAULT_POOL_SIZE = 10
DEFAULT_TTL = 86400  # 24 hours in seconds

# Key prefixes for different cache types
SERP_KEY_PREFIX = "serp::"
ANALYSIS_KEY_PREFIX = "analysis::"
RECOMMENDATIONS_KEY_PREFIX = "recommendations::"


class RedisConfig:
    """Redis connection configuration."""
    
    def __init__(
        self,
        url: Optional[str] = None,
        pool_size: int = DEFAULT_POOL_SIZE,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
        retry_on_timeout: bool = True
    ):
        """
        Initialize Redis configuration.
        
        Args:
            url: Redis connection URL in the format redis://host:port/db
            pool_size: Maximum number of connections in the pool
            socket_timeout: Socket timeout for Redis operations
            socket_connect_timeout: Timeout for socket connection
            retry_on_timeout: Whether to retry on timeout
        """
        self.url = url or os.getenv("REDIS_URL", DEFAULT_REDIS_URL)
        self.pool_size = pool_size
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.retry_on_timeout = retry_on_timeout
        
    def create_pool(self) -> redis.Redis:
        """
        Create and return a Redis connection pool.
        
        Returns:
            redis.Redis: Redis client with connection pooling
        """
        try:
            logger.info(f"Creating Redis connection pool to {self.url}")
            
            # Create Redis client with connection pooling
            client = redis.from_url(
                self.url,
                max_connections=self.pool_size,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                retry_on_timeout=self.retry_on_timeout,
                decode_responses=False,  # We handle decoding manually for flexibility
            )
            
            return client
        except Exception as e:
            logger.error(f"Failed to create Redis connection pool: {str(e)}")
            raise


class CacheService:
    """
    Redis-based caching service for the SERP analysis pipeline.
    
    This service provides methods for caching and retrieving:
    1. SERP data for search terms
    2. Complete analysis results
    3. Recommendation sets
    
    It handles serialization/deserialization of data and implements
    TTL-based expiration.
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        default_ttl: int = DEFAULT_TTL
    ):
        """
        Initialize the cache service.
        
        Args:
            redis_client: Redis client with connection pooling
            default_ttl: Default time-to-live for cache entries in seconds
        """
        self.redis = redis_client
        self.default_ttl = default_ttl
        
        # Ensure Redis client is properly configured
        if not isinstance(redis_client, redis.Redis):
            logger.warning("Redis client is not of expected type. Caching may not work correctly.")
    
    @classmethod
    async def create(
        cls,
        config: Optional[RedisConfig] = None,
        default_ttl: int = DEFAULT_TTL
    ) -> 'CacheService':
        """
        Create a CacheService instance with a new Redis connection.
        
        Args:
            config: Redis connection configuration
            default_ttl: Default time-to-live for cache entries in seconds
            
        Returns:
            CacheService: A configured cache service instance
        """
        config = config or RedisConfig()
        redis_client = config.create_pool()
        
        # Test the connection
        try:
            await redis_client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
            
        return cls(redis_client, default_ttl)
    
    async def get_serp_data(self, search_term: str) -> Optional[Dict[str, Any]]:
        """
        Get cached SERP data for a search term if available.
        
        Args:
            search_term: The search term to retrieve SERP data for
            
        Returns:
            Optional[Dict[str, Any]]: The cached SERP data or None if not found
            
        Raises:
            Exception: If there's an error retrieving data from Redis
        """
        key = f"{SERP_KEY_PREFIX}{search_term}"
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning(f"Error retrieving SERP data from cache: {str(e)}")
            raise
    
    async def set_serp_data(
        self,
        search_term: str,
        serp_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache SERP data for a search term with TTL.
        
        Args:
            search_term: The search term to cache SERP data for
            serp_data: The SERP data to cache
            ttl: Optional time-to-live in seconds (uses default if None)
            
        Returns:
            bool: True if caching was successful
            
        Raises:
            Exception: If there's an error storing data in Redis
        """
        key = f"{SERP_KEY_PREFIX}{search_term}"
        try:
            serialized_data = json.dumps(serp_data)
            await self.redis.set(key, serialized_data, ex=ttl or self.default_ttl)
            logger.info(f"Cached SERP data for search term: {search_term}")
            return True
        except Exception as e:
            logger.warning(f"Error caching SERP data: {str(e)}")
            raise
    
    async def get_analysis(self, search_term: str) -> Optional[AnalysisResult]:
        """
        Get cached analysis result for a search term if available.
        
        Args:
            search_term: The search term to retrieve analysis for
            
        Returns:
            Optional[AnalysisResult]: The cached analysis or None if not found
            
        Raises:
            Exception: If there's an error retrieving data from Redis
        """
        key = f"{ANALYSIS_KEY_PREFIX}{search_term}"
        try:
            data = await self.redis.get(key)
            if data:
                # Deserialize and convert to AnalysisResult
                analysis_dict = json.loads(data)
                return AnalysisResult.model_validate(analysis_dict)
            return None
        except Exception as e:
            logger.warning(f"Error retrieving analysis from cache: {str(e)}")
            raise
    
    async def store_analysis(
        self,
        search_term: str,
        analysis: AnalysisResult,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache analysis result for a search term with TTL.
        
        Args:
            search_term: The search term to cache analysis for
            analysis: The analysis result to cache
            ttl: Optional time-to-live in seconds (uses default if None)
            
        Returns:
            bool: True if caching was successful
            
        Raises:
            Exception: If there's an error storing data in Redis
        """
        key = f"{ANALYSIS_KEY_PREFIX}{search_term}"
        try:
            serialized_data = analysis.model_dump_json()
            await self.redis.set(key, serialized_data, ex=ttl or self.default_ttl)
            logger.info(f"Cached analysis for search term: {search_term}")
            return True
        except Exception as e:
            logger.warning(f"Error caching analysis: {str(e)}")
            raise
    
    async def get_recommendations(self, search_term: str) -> Optional[Dict[str, Any]]:
        """
        Get cached recommendations for a search term if available.
        
        Args:
            search_term: The search term to retrieve recommendations for
            
        Returns:
            Optional[Dict[str, Any]]: The cached recommendations or None if not found
            
        Raises:
            Exception: If there's an error retrieving data from Redis
        """
        key = f"{RECOMMENDATIONS_KEY_PREFIX}{search_term}"
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning(f"Error retrieving recommendations from cache: {str(e)}")
            raise
    
    async def store_recommendations(
        self,
        search_term: str,
        recommendations: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache recommendations for a search term with TTL.
        
        Args:
            search_term: The search term to cache recommendations for
            recommendations: The recommendations to cache
            ttl: Optional time-to-live in seconds (uses default if None)
            
        Returns:
            bool: True if caching was successful
            
        Raises:
            Exception: If there's an error storing data in Redis
        """
        key = f"{RECOMMENDATIONS_KEY_PREFIX}{search_term}"
        try:
            serialized_data = json.dumps(recommendations)
            await self.redis.set(key, serialized_data, ex=ttl or self.default_ttl)
            logger.info(f"Cached recommendations for search term: {search_term}")
            return True
        except Exception as e:
            logger.warning(f"Error caching recommendations: {str(e)}")
            raise
    
    async def invalidate_cache(self, search_term: str) -> bool:
        """
        Invalidate all cached data for a search term.
        
        Args:
            search_term: The search term to invalidate cache for
            
        Returns:
            bool: True if invalidation was successful
            
        Raises:
            Exception: If there's an error deleting data from Redis
        """
        keys = [
            f"{SERP_KEY_PREFIX}{search_term}",
            f"{ANALYSIS_KEY_PREFIX}{search_term}",
            f"{RECOMMENDATIONS_KEY_PREFIX}{search_term}"
        ]
        
        try:
            # Delete all keys related to this search term
            for key in keys:
                await self.redis.delete(key)
            
            logger.info(f"Invalidated cache for search term: {search_term}")
            return True
        except Exception as e:
            logger.warning(f"Error invalidating cache: {str(e)}")
            raise
    
    async def get_cache_status(self) -> Dict[str, Any]:
        """
        Get current cache status information.
        
        Returns:
            Dict[str, Any]: Cache status information including memory usage,
                            hit/miss statistics, and key counts
        """
        try:
            # Get Redis server information
            info = await self.redis.info()
            
            # Get counts by key prefix
            serp_count = len(await self.redis.keys(f"{SERP_KEY_PREFIX}*"))
            analysis_count = len(await self.redis.keys(f"{ANALYSIS_KEY_PREFIX}*"))
            recommendation_count = len(await self.redis.keys(f"{RECOMMENDATIONS_KEY_PREFIX}*"))
            
            return {
                "connected": True,
                "memory_used": info.get("used_memory_human", "unknown"),
                "keys_total": info.get("db0", {}).get("keys", 0),
                "serp_keys": serp_count,
                "analysis_keys": analysis_count,
                "recommendation_keys": recommendation_count,
                "uptime_seconds": info.get("uptime_in_seconds", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting cache status: {str(e)}")
            return {
                "connected": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def close(self) -> None:
        """
        Close the Redis connection pool.
        
        This should be called when the application is shutting down.
        """
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection pool closed") 