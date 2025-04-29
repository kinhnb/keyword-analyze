"""
Rate limiter middleware for the AI SERP Keyword Research Agent API.

This middleware implements rate limiting based on client IP addresses or API keys,
using Redis as a backend for tracking request counts.
"""

import time
from typing import Callable, Dict, Optional, Tuple, Union

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from ai_serp_keyword_research.services.cache import CacheService
from ai_serp_keyword_research.tracing import trace


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting API requests.
    
    This middleware tracks request counts by client identifier (API key or IP address)
    and enforces rate limits based on configured thresholds.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        cache_service: Optional[CacheService] = None,
        rate_limit_per_minute: int = 60,
        rate_limit_per_day: int = 1000,
        exempt_paths: Optional[list] = None,
        key_func: Optional[Callable[[Request], str]] = None
    ):
        """
        Initialize rate limiter with specified limits.
        
        Args:
            app: The ASGI application
            cache_service: Redis client for tracking request counts
            rate_limit_per_minute: Maximum requests allowed per minute
            rate_limit_per_day: Maximum requests allowed per day
            exempt_paths: List of paths exempt from rate limiting
            key_func: Optional function to extract client ID from request
        """
        super().__init__(app)
        self.cache_service = cache_service
        self.rate_limit_per_minute = rate_limit_per_minute
        self.rate_limit_per_day = rate_limit_per_day
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/openapi.json", "/redoc", "/static"]
        self.key_func = key_func or self._default_key_func
    
    def _default_key_func(self, request: Request) -> str:
        """
        Default function to extract client identifier from request.
        
        Prioritizes API key over IP address if available.
        
        Args:
            request: The incoming request
            
        Returns:
            Client identifier for rate limiting
        """
        return request.headers.get("X-API-Key") or request.client.host
    
    async def _check_rate_limit(
        self, 
        key: str, 
        period_seconds: int, 
        limit: int
    ) -> Tuple[int, int, int]:
        """
        Check if a rate limit has been exceeded.
        
        Args:
            key: Redis key for the rate limit counter
            period_seconds: Time period in seconds for the limit
            limit: Maximum number of requests allowed in the period
            
        Returns:
            Tuple of (current_count, remaining_requests, reset_time)
        """
        if not self.cache_service:
            # If no cache service, allow all requests
            return 0, limit, int(time.time()) + period_seconds
        
        # Get current timestamp for TTL calculation
        current_time = int(time.time())
        
        # Check if the key exists and get its value
        count = await self.cache_service.increment_counter(key, period_seconds)
        
        # Calculate remaining requests and reset time
        remaining = max(0, limit - count)
        # Get key TTL to determine reset time
        ttl = await self.cache_service.get_ttl(key)
        reset_time = current_time + (ttl if ttl > 0 else period_seconds)
        
        return count, remaining, reset_time
    
    async def _add_rate_limit_headers(
        self, 
        response: Response,
        minute_remaining: int,
        minute_limit: int,
        minute_reset: int,
        day_remaining: int,
        day_limit: int,
        day_reset: int
    ) -> None:
        """
        Add rate limit headers to the response.
        
        Args:
            response: The response object
            minute_remaining: Remaining requests per minute
            minute_limit: Total requests allowed per minute
            minute_reset: Reset time for minute limit
            day_remaining: Remaining requests per day
            day_limit: Total requests allowed per day
            day_reset: Reset time for day limit
        """
        # Add standard rate limiting headers
        response.headers["X-Rate-Limit-Limit-Minute"] = str(minute_limit)
        response.headers["X-Rate-Limit-Remaining-Minute"] = str(minute_remaining)
        response.headers["X-Rate-Limit-Reset-Minute"] = str(minute_reset)
        
        response.headers["X-Rate-Limit-Limit-Day"] = str(day_limit)
        response.headers["X-Rate-Limit-Remaining-Day"] = str(day_remaining)
        response.headers["X-Rate-Limit-Reset-Day"] = str(day_reset)
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process a request through the rate limiter.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint to call
            
        Returns:
            The response from the next middleware or endpoint
        """
        # Skip rate limiting for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # If no cache service, proceed without rate limiting
        if not self.cache_service:
            return await call_next(request)
        
        # Get client identifier
        client_id = self.key_func(request)
        
        # Create rate limit keys
        minute_key = f"rate_limit:{client_id}:minute"
        day_key = f"rate_limit:{client_id}:day"
        
        with trace("rate_limit_check"):
            # Check minute rate limit
            minute_count, minute_remaining, minute_reset = await self._check_rate_limit(
                minute_key, 60, self.rate_limit_per_minute
            )
            
            # If minute limit exceeded, return 429 response
            if minute_count > self.rate_limit_per_minute:
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "status": "error",
                        "error": "Rate limit exceeded",
                        "details": {
                            "limit_per_minute": self.rate_limit_per_minute,
                            "current_usage": minute_count,
                            "reset_at": minute_reset,
                            "retry_after_seconds": minute_reset - int(time.time())
                        }
                    }
                )
                # Add rate limit headers
                response.headers["Retry-After"] = str(minute_reset - int(time.time()))
                await self._add_rate_limit_headers(
                    response,
                    0, self.rate_limit_per_minute, minute_reset,
                    0, self.rate_limit_per_day, 0  # Day values not needed here
                )
                return response
            
            # Check day rate limit
            day_count, day_remaining, day_reset = await self._check_rate_limit(
                day_key, 86400, self.rate_limit_per_day
            )
            
            # If day limit exceeded, return 429 response
            if day_count > self.rate_limit_per_day:
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "status": "error",
                        "error": "Daily rate limit exceeded",
                        "details": {
                            "limit_per_day": self.rate_limit_per_day,
                            "current_usage": day_count,
                            "reset_at": day_reset,
                            "retry_after_seconds": day_reset - int(time.time())
                        }
                    }
                )
                # Add rate limit headers
                response.headers["Retry-After"] = str(day_reset - int(time.time()))
                await self._add_rate_limit_headers(
                    response,
                    minute_remaining, self.rate_limit_per_minute, minute_reset,
                    0, self.rate_limit_per_day, day_reset
                )
                return response
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to the response
        await self._add_rate_limit_headers(
            response,
            minute_remaining, self.rate_limit_per_minute, minute_reset,
            day_remaining, self.rate_limit_per_day, day_reset
        )
        
        return response 