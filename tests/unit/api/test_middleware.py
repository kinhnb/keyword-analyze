"""
Unit tests for the API middleware components of the AI SERP Keyword Research Agent.

This module tests the authentication and rate limiting middleware.
"""

import pytest
import base64
import os
from typing import Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request

from ai_serp_keyword_research.api.middleware.auth import APIKeyMiddleware
from ai_serp_keyword_research.api.middleware.rate_limiter import RateLimitMiddleware
from ai_serp_keyword_research.services.cache import CacheService


# Mock cache service for testing
class MockCacheService:
    """Mock cache service for testing middleware."""
    
    def __init__(self):
        self.data = {}
        self.counters = {}
        self.ttls = {}
    
    async def set(self, key: str, value: Any, expiry_seconds: Optional[int] = None):
        """Mock set operation."""
        self.data[key] = value
        if expiry_seconds:
            self.ttls[key] = expiry_seconds
    
    async def get(self, key: str) -> Any:
        """Mock get operation."""
        return self.data.get(key)
    
    async def delete(self, key: str) -> bool:
        """Mock delete operation."""
        if key in self.data:
            del self.data[key]
            return True
        return False
    
    async def increment_counter(self, key: str, expiry_seconds: int) -> int:
        """Mock increment counter operation."""
        if key not in self.counters:
            self.counters[key] = 0
            self.ttls[key] = expiry_seconds
        self.counters[key] += 1
        return self.counters[key]
    
    async def get_ttl(self, key: str) -> int:
        """Mock get TTL operation."""
        return self.ttls.get(key, 0)
    
    def get_current_timestamp(self) -> int:
        """Mock timestamp."""
        return 1234567890


# Tests for APIKeyMiddleware
class TestAPIKeyMiddleware:
    """Test suite for API key authentication middleware."""
    
    @pytest.fixture
    def app(self):
        """Create a test FastAPI application."""
        app = FastAPI()
        
        @app.get("/")
        def read_root():
            return {"message": "Hello World"}
        
        @app.get("/health")
        def health_check():
            return {"status": "healthy"}
        
        return app
    
    @pytest.fixture
    def mock_cache_service(self):
        """Create a mock cache service."""
        return MockCacheService()
    
    def test_api_key_middleware_exempt_paths(self, app, mock_cache_service):
        """Test that exempt paths skip authentication."""
        middleware = APIKeyMiddleware(
            app=app,
            api_keys=["test-key"],
            cache_service=mock_cache_service
        )
        app.add_middleware(BaseHTTPMiddleware, dispatch=middleware.dispatch)
        
        client = TestClient(app)
        
        # Test exempt path
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_api_key_middleware_missing_key(self, app, mock_cache_service):
        """Test that requests without API key are rejected."""
        middleware = APIKeyMiddleware(
            app=app,
            api_keys=["test-key"],
            cache_service=mock_cache_service
        )
        app.add_middleware(BaseHTTPMiddleware, dispatch=middleware.dispatch)
        
        client = TestClient(app)
        
        # Test missing API key
        response = client.get("/")
        assert response.status_code == 401
        assert response.json()["error"] == "Missing API key"
    
    def test_api_key_middleware_invalid_key(self, app, mock_cache_service):
        """Test that requests with invalid API key are rejected."""
        middleware = APIKeyMiddleware(
            app=app,
            api_keys=["test-key"],
            cache_service=mock_cache_service
        )
        app.add_middleware(BaseHTTPMiddleware, dispatch=middleware.dispatch)
        
        client = TestClient(app)
        
        # Test invalid API key
        response = client.get("/", headers={"X-API-Key": "invalid-key"})
        assert response.status_code == 401
        assert response.json()["error"] == "Invalid API key"
    
    def test_api_key_middleware_valid_key(self, app, mock_cache_service):
        """Test that requests with valid API key are allowed."""
        middleware = APIKeyMiddleware(
            app=app,
            api_keys=["test-key"],
            cache_service=mock_cache_service
        )
        app.add_middleware(BaseHTTPMiddleware, dispatch=middleware.dispatch)
        
        client = TestClient(app)
        
        # Test valid API key
        response = client.get("/", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}
    
    @pytest.mark.asyncio
    async def test_api_key_middleware_key_generation(self, mock_cache_service):
        """Test API key generation and storage."""
        middleware = APIKeyMiddleware(
            app=MagicMock(),
            api_keys=[],
            cache_service=mock_cache_service
        )
        
        key_id, api_key = await middleware.generate_api_key()
        
        # Key should be added to in-memory list
        assert api_key in middleware.api_keys
        
        # Key should be in expected format: uuid-base64string
        assert key_id in api_key
        
        # Key hash should be in cache
        key_hash = middleware._hash_key(api_key)
        key_data = await mock_cache_service.get(f"api_key:{key_hash}")
        assert key_data is not None
        assert key_data.get("valid") is True
    
    @pytest.mark.asyncio
    async def test_api_key_middleware_key_revocation(self, mock_cache_service):
        """Test API key revocation."""
        test_key = "test-revoke-key"
        middleware = APIKeyMiddleware(
            app=MagicMock(),
            api_keys=[test_key],
            cache_service=mock_cache_service
        )
        
        # Revoke the key
        result = await middleware.revoke_api_key(test_key)
        assert result is True
        
        # Key should be removed from in-memory list
        assert test_key not in middleware.api_keys
        
        # Key hash should be removed from cache
        key_hash = middleware._hash_key(test_key)
        key_data = await mock_cache_service.get(f"api_key:{key_hash}")
        assert key_data is None


# Tests for RateLimitMiddleware
class TestRateLimitMiddleware:
    """Test suite for rate limiting middleware."""
    
    @pytest.fixture
    def app(self):
        """Create a test FastAPI application."""
        app = FastAPI()
        
        @app.get("/")
        def read_root():
            return {"message": "Hello World"}
        
        @app.get("/health")
        def health_check():
            return {"status": "healthy"}
        
        return app
    
    @pytest.fixture
    def mock_cache_service(self):
        """Create a mock cache service."""
        return MockCacheService()
    
    def test_rate_limit_middleware_exempt_paths(self, app, mock_cache_service):
        """Test that exempt paths skip rate limiting."""
        middleware = RateLimitMiddleware(
            app=app,
            cache_service=mock_cache_service,
            rate_limit_per_minute=5,
            rate_limit_per_day=10
        )
        app.add_middleware(BaseHTTPMiddleware, dispatch=middleware.dispatch)
        
        client = TestClient(app)
        
        # Test exempt path - should be able to call many times
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}
    
    def test_rate_limit_middleware_minute_limit(self, app, mock_cache_service):
        """Test that minute rate limit is enforced."""
        middleware = RateLimitMiddleware(
            app=app,
            cache_service=mock_cache_service,
            rate_limit_per_minute=3,  # Set a low limit for testing
            rate_limit_per_day=100
        )
        app.add_middleware(BaseHTTPMiddleware, dispatch=middleware.dispatch)
        
        client = TestClient(app)
        client_id = "test-client"
        
        # First 3 requests should succeed
        for i in range(3):
            response = client.get("/", headers={"X-API-Key": client_id})
            assert response.status_code == 200
            assert "X-Rate-Limit-Remaining-Minute" in response.headers
            remaining = int(response.headers["X-Rate-Limit-Remaining-Minute"])
            assert remaining == 3 - (i + 1)
        
        # 4th request should be rate limited
        response = client.get("/", headers={"X-API-Key": client_id})
        assert response.status_code == 429
        assert response.json()["error"] == "Rate limit exceeded"
        assert "Retry-After" in response.headers
    
    def test_rate_limit_middleware_day_limit(self, app, mock_cache_service):
        """Test that daily rate limit is enforced."""
        middleware = RateLimitMiddleware(
            app=app,
            cache_service=mock_cache_service,
            rate_limit_per_minute=100,
            rate_limit_per_day=3  # Set a low limit for testing
        )
        app.add_middleware(BaseHTTPMiddleware, dispatch=middleware.dispatch)
        
        client = TestClient(app)
        client_id = "test-client"
        
        # First 3 requests should succeed
        for i in range(3):
            response = client.get("/", headers={"X-API-Key": client_id})
            assert response.status_code == 200
            assert "X-Rate-Limit-Remaining-Day" in response.headers
            remaining = int(response.headers["X-Rate-Limit-Remaining-Day"])
            assert remaining == 3 - (i + 1)
        
        # 4th request should be rate limited
        response = client.get("/", headers={"X-API-Key": client_id})
        assert response.status_code == 429
        assert response.json()["error"] == "Daily rate limit exceeded"
        assert "Retry-After" in response.headers
    
    def test_rate_limit_middleware_headers(self, app, mock_cache_service):
        """Test that rate limit headers are present in the response."""
        middleware = RateLimitMiddleware(
            app=app,
            cache_service=mock_cache_service,
            rate_limit_per_minute=10,
            rate_limit_per_day=100
        )
        app.add_middleware(BaseHTTPMiddleware, dispatch=middleware.dispatch)
        
        client = TestClient(app)
        
        response = client.get("/", headers={"X-API-Key": "test-client"})
        assert response.status_code == 200
        
        # Check that all rate limit headers are present
        assert "X-Rate-Limit-Limit-Minute" in response.headers
        assert "X-Rate-Limit-Remaining-Minute" in response.headers
        assert "X-Rate-Limit-Reset-Minute" in response.headers
        
        assert "X-Rate-Limit-Limit-Day" in response.headers
        assert "X-Rate-Limit-Remaining-Day" in response.headers
        assert "X-Rate-Limit-Reset-Day" in response.headers
        
        # Verify values
        assert response.headers["X-Rate-Limit-Limit-Minute"] == "10"
        assert response.headers["X-Rate-Limit-Remaining-Minute"] == "9"  # 10 - 1 = 9
        assert response.headers["X-Rate-Limit-Limit-Day"] == "100"
        assert response.headers["X-Rate-Limit-Remaining-Day"] == "99"  # 100 - 1 = 99
    
    def test_custom_key_function(self, app, mock_cache_service):
        """Test that custom key function works."""
        def custom_key_func(request):
            return "custom-" + request.headers.get("X-Custom-ID", "default")
        
        middleware = RateLimitMiddleware(
            app=app,
            cache_service=mock_cache_service,
            rate_limit_per_minute=3,
            rate_limit_per_day=100,
            key_func=custom_key_func
        )
        app.add_middleware(BaseHTTPMiddleware, dispatch=middleware.dispatch)
        
        client = TestClient(app)
        
        # First 3 requests with same custom ID should succeed
        for _ in range(3):
            response = client.get("/", headers={"X-Custom-ID": "test-id"})
            assert response.status_code == 200
        
        # 4th request should be rate limited
        response = client.get("/", headers={"X-Custom-ID": "test-id"})
        assert response.status_code == 429
        
        # But request with different custom ID should succeed
        response = client.get("/", headers={"X-Custom-ID": "other-id"})
        assert response.status_code == 200 