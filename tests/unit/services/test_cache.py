"""
Unit tests for the Redis cache service.

This module contains tests for the Redis-based cache service implementation,
including connection management, data caching, and cache invalidation.
"""

import asyncio
import json
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import fakeredis.aioredis
from redis.asyncio import Redis

from ai_serp_keyword_research.services.cache import (
    CacheService,
    RedisConfig,
    SERP_KEY_PREFIX,
    ANALYSIS_KEY_PREFIX,
    RECOMMENDATIONS_KEY_PREFIX,
    DEFAULT_TTL
)
from ai_serp_keyword_research.core.models.analysis import IntentAnalysis, MarketGap
from ai_serp_keyword_research.core.models.recommendations import RecommendationSet, Recommendation
from ai_serp_keyword_research.core.models.results import AnalysisResult


class TestRedisConfig:
    """Test suite for RedisConfig class."""
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        config = RedisConfig()
        
        assert config.url == os.getenv("REDIS_URL", "redis://localhost:6379/0")
        assert config.pool_size == 10
        assert config.socket_timeout == 5
        assert config.socket_connect_timeout == 5
        assert config.retry_on_timeout is True
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        config = RedisConfig(
            url="redis://custom:6380/1",
            pool_size=20,
            socket_timeout=10,
            socket_connect_timeout=15,
            retry_on_timeout=False
        )
        
        assert config.url == "redis://custom:6380/1"
        assert config.pool_size == 20
        assert config.socket_timeout == 10
        assert config.socket_connect_timeout == 15
        assert config.retry_on_timeout is False
    
    @patch("redis.asyncio.from_url")
    def test_create_pool(self, mock_from_url):
        """Test creating a Redis connection pool."""
        mock_client = MagicMock()
        mock_from_url.return_value = mock_client
        
        config = RedisConfig(url="redis://testhost:6379/0")
        result = config.create_pool()
        
        mock_from_url.assert_called_once_with(
            "redis://testhost:6379/0",
            max_connections=10,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            decode_responses=False
        )
        assert result == mock_client


class TestCacheService:
    """Test suite for CacheService class."""
    
    @pytest.fixture
    async def fake_redis(self):
        """Create a fake Redis instance for testing."""
        client = fakeredis.aioredis.FakeRedis()
        yield client
        await client.close()
    
    @pytest.fixture
    async def cache_service(self, fake_redis):
        """Create a CacheService instance with fake Redis for testing."""
        service = CacheService(fake_redis)
        yield service
    
    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        client = AsyncMock(spec=Redis)
        client.ping = AsyncMock(return_value=True)
        client.get = AsyncMock(return_value=None)
        client.set = AsyncMock(return_value=True)
        client.delete = AsyncMock(return_value=1)
        client.keys = AsyncMock(return_value=[])
        client.info = AsyncMock(return_value={"used_memory_human": "1M", "uptime_in_seconds": 3600})
        return client
    
    @pytest.fixture
    def sample_serp_data(self):
        """Create sample SERP data for testing."""
        return {
            "results": [
                {"title": "Test Result 1", "url": "https://example.com/1"},
                {"title": "Test Result 2", "url": "https://example.com/2"}
            ],
            "search_metadata": {
                "query": "test search",
                "page": 1
            }
        }
    
    @pytest.fixture
    def sample_analysis(self):
        """Create a sample AnalysisResult for testing."""
        intent = IntentAnalysis(
            main_keyword="test keyword",
            secondary_keywords=["test", "keyword"],
            intent_type="transactional",
            confidence=0.95
        )
        
        market_gap = MarketGap(
            detected=True,
            description="Test market gap",
            opportunity_score=0.8
        )
        
        recommendations = RecommendationSet(
            items=[
                Recommendation(
                    tactic_type="product_page_optimization",
                    description="Test recommendation",
                    priority=1,
                    confidence=0.9
                )
            ]
        )
        
        return AnalysisResult(
            search_term="test search",
            analysis_id="test-id",
            intent_analysis=intent,
            market_gap=market_gap,
            serp_features=[],
            recommendations=recommendations,
            execution_time=0.5
        )
    
    @patch("ai_serp_keyword_research.services.cache.RedisConfig")
    async def test_create_class_method(self, mock_redis_config, mock_redis):
        """Test creating a CacheService using the create class method."""
        mock_config_instance = MagicMock()
        mock_redis_config.return_value = mock_config_instance
        mock_config_instance.create_pool.return_value = mock_redis
        
        cache_service = await CacheService.create()
        
        assert cache_service.redis == mock_redis
        assert cache_service.default_ttl == DEFAULT_TTL
        mock_redis.ping.assert_awaited_once()
    
    async def test_get_serp_data_not_found(self, cache_service):
        """Test getting SERP data that doesn't exist in the cache."""
        result = await cache_service.get_serp_data("unknown-term")
        assert result is None
    
    async def test_set_and_get_serp_data(self, cache_service, sample_serp_data):
        """Test setting and getting SERP data."""
        search_term = "test-term"
        
        # Set the data
        await cache_service.set_serp_data(search_term, sample_serp_data)
        
        # Get the data
        result = await cache_service.get_serp_data(search_term)
        
        assert result == sample_serp_data
    
    async def test_get_analysis_not_found(self, cache_service):
        """Test getting analysis that doesn't exist in the cache."""
        result = await cache_service.get_analysis("unknown-term")
        assert result is None
    
    async def test_store_and_get_analysis(self, cache_service, sample_analysis):
        """Test storing and getting analysis."""
        search_term = "test-term"
        
        # Store the analysis
        await cache_service.store_analysis(search_term, sample_analysis)
        
        # Get the analysis
        result = await cache_service.get_analysis(search_term)
        
        assert result is not None
        assert result.search_term == sample_analysis.search_term
        assert result.analysis_id == sample_analysis.analysis_id
        assert result.intent_analysis.main_keyword == sample_analysis.intent_analysis.main_keyword
        assert result.market_gap.detected == sample_analysis.market_gap.detected
        assert len(result.recommendations.items) == len(sample_analysis.recommendations.items)
    
    async def test_get_recommendations_not_found(self, cache_service):
        """Test getting recommendations that don't exist in the cache."""
        result = await cache_service.get_recommendations("unknown-term")
        assert result is None
    
    async def test_store_and_get_recommendations(self, cache_service):
        """Test storing and getting recommendations."""
        search_term = "test-term"
        recommendations = {
            "items": [
                {
                    "tactic_type": "content_creation",
                    "description": "Create test content",
                    "priority": 1,
                    "confidence": 0.85
                }
            ]
        }
        
        # Store the recommendations
        await cache_service.store_recommendations(search_term, recommendations)
        
        # Get the recommendations
        result = await cache_service.get_recommendations(search_term)
        
        assert result == recommendations
    
    async def test_invalidate_cache(self, cache_service, sample_serp_data, sample_analysis):
        """Test invalidating all cache entries for a search term."""
        search_term = "test-term"
        
        # Set various cache entries
        await cache_service.set_serp_data(search_term, sample_serp_data)
        await cache_service.store_analysis(search_term, sample_analysis)
        await cache_service.store_recommendations(search_term, {"items": []})
        
        # Verify entries exist
        assert await cache_service.get_serp_data(search_term) is not None
        assert await cache_service.get_analysis(search_term) is not None
        assert await cache_service.get_recommendations(search_term) is not None
        
        # Invalidate the cache
        result = await cache_service.invalidate_cache(search_term)
        assert result is True
        
        # Verify entries no longer exist
        assert await cache_service.get_serp_data(search_term) is None
        assert await cache_service.get_analysis(search_term) is None
        assert await cache_service.get_recommendations(search_term) is None
    
    async def test_ttl_expiration(self, cache_service, sample_serp_data):
        """Test that cache entries expire after TTL."""
        search_term = "test-term"
        short_ttl = 1  # 1 second TTL
        
        # Set the data with a short TTL
        await cache_service.set_serp_data(search_term, sample_serp_data, ttl=short_ttl)
        
        # Verify it exists immediately
        assert await cache_service.get_serp_data(search_term) is not None
        
        # Wait for expiration
        await asyncio.sleep(short_ttl + 0.5)
        
        # Verify it's gone
        assert await cache_service.get_serp_data(search_term) is None
    
    async def test_get_cache_status(self, mock_redis):
        """Test getting cache status information."""
        cache_service = CacheService(mock_redis)
        
        # Mock additional methods for status
        mock_redis.keys.side_effect = lambda prefix: ["key1"] if "serp" in prefix else []
        
        # Get status
        status = await cache_service.get_cache_status()
        
        # Verify result
        assert status["connected"] is True
        assert status["memory_used"] == "1M"
        assert "serp_keys" in status
        assert "analysis_keys" in status
        assert "recommendation_keys" in status
        assert "timestamp" in status
    
    async def test_close(self, mock_redis):
        """Test closing the Redis connection."""
        cache_service = CacheService(mock_redis)
        await cache_service.close()
        
        mock_redis.close.assert_awaited_once()
    
    async def test_error_handling_in_get_serp_data(self, mock_redis):
        """Test error handling in get_serp_data method."""
        mock_redis.get.side_effect = Exception("Redis error")
        cache_service = CacheService(mock_redis)
        
        with pytest.raises(Exception):
            await cache_service.get_serp_data("test-term")
    
    async def test_error_handling_in_set_serp_data(self, mock_redis):
        """Test error handling in set_serp_data method."""
        mock_redis.set.side_effect = Exception("Redis error")
        cache_service = CacheService(mock_redis)
        
        with pytest.raises(Exception):
            await cache_service.set_serp_data("test-term", {"data": "test"})
    
    async def test_error_handling_in_get_cache_status(self, mock_redis):
        """Test error handling in get_cache_status method."""
        mock_redis.info.side_effect = Exception("Redis error")
        cache_service = CacheService(mock_redis)
        
        status = await cache_service.get_cache_status()
        
        assert status["connected"] is False
        assert "error" in status 