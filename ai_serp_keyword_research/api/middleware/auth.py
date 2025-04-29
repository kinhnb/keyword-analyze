"""
Authentication middleware for the AI SERP Keyword Research Agent API.

This middleware implements API key authentication for securing API endpoints.
"""

import os
import uuid
import hashlib
import base64
from typing import Dict, List, Optional, Tuple

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from ai_serp_keyword_research.tracing import trace
from ai_serp_keyword_research.services.cache import CacheService


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API key authentication.
    
    This middleware validates the X-API-Key header against configured valid keys
    and rejects requests with invalid or missing API keys.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        api_keys: Optional[List[str]] = None,
        exempt_paths: Optional[List[str]] = None,
        cache_service: Optional[CacheService] = None
    ):
        """
        Initialize API key middleware with specified configurations.
        
        Args:
            app: The ASGI application
            api_keys: List of valid API keys
            exempt_paths: List of paths exempt from authentication
            cache_service: Redis cache service for storing/validating keys
        """
        super().__init__(app)
        self.api_keys = api_keys or self._load_api_keys_from_env()
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/openapi.json", "/redoc", "/static"]
        self.cache_service = cache_service
        
        # Store keys in cache if available
        if self.cache_service and self.api_keys:
            for key in self.api_keys:
                self._store_key_in_cache(key)
    
    def _load_api_keys_from_env(self) -> List[str]:
        """
        Load API keys from environment variables.
        
        Returns:
            List of valid API keys
        """
        # Get API keys from environment variable (comma-separated)
        env_keys = os.getenv("API_KEYS", "")
        if env_keys:
            return [key.strip() for key in env_keys.split(",")]
        
        # Use a default API key for development if none configured
        if os.getenv("ENV", "development") == "development":
            return ["dev-api-key-1234"]
        
        return []
    
    async def _store_key_in_cache(self, api_key: str) -> None:
        """
        Store API key in cache for faster validation.
        
        Args:
            api_key: The API key to store
        """
        if not self.cache_service:
            return
            
        # Use a hash of the key as the cache key for security
        key_hash = self._hash_key(api_key)
        # Store the key with metadata (can be extended with user info, quotas, etc.)
        await self.cache_service.set(
            f"api_key:{key_hash}",
            {"valid": True, "created_at": self.cache_service.get_current_timestamp()},
            expiry_seconds=None  # No expiration for API keys
        )
    
    async def _validate_key_from_cache(self, api_key: str) -> bool:
        """
        Validate an API key against the cache.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            True if the key is valid, False otherwise
        """
        if not self.cache_service:
            # If no cache service, fall back to in-memory validation
            return api_key in self.api_keys
            
        key_hash = self._hash_key(api_key)
        key_data = await self.cache_service.get(f"api_key:{key_hash}")
        return key_data is not None and key_data.get("valid", False)
    
    def _hash_key(self, api_key: str) -> str:
        """
        Create a hash of the API key for secure storage.
        
        Args:
            api_key: The API key to hash
            
        Returns:
            Hashed representation of the API key
        """
        # Use SHA-256 for key hashing
        key_hash = hashlib.sha256(api_key.encode()).digest()
        # Return as URL-safe base64
        return base64.urlsafe_b64encode(key_hash).decode().rstrip("=")
    
    async def generate_api_key(self) -> Tuple[str, str]:
        """
        Generate a new API key and store it.
        
        Returns:
            Tuple of (key_id, api_key)
        """
        # Generate a unique key ID
        key_id = str(uuid.uuid4())
        # Generate a random API key
        api_key = f"{key_id}-{base64.urlsafe_b64encode(os.urandom(24)).decode().rstrip('=')}"
        
        # Store the key
        self.api_keys.append(api_key)
        if self.cache_service:
            await self._store_key_in_cache(api_key)
            
        return key_id, api_key
    
    async def revoke_api_key(self, api_key: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            api_key: The API key to revoke
            
        Returns:
            True if the key was revoked, False if it wasn't found
        """
        # Remove from memory list
        if api_key in self.api_keys:
            self.api_keys.remove(api_key)
        
        # Remove from cache if available
        if self.cache_service:
            key_hash = self._hash_key(api_key)
            await self.cache_service.delete(f"api_key:{key_hash}")
            return True
            
        return api_key in self.api_keys
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process a request through the authentication middleware.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint to call
            
        Returns:
            The response from the next middleware or endpoint or an error response
        """
        # Skip authentication for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        with trace("api_key_authentication"):
            # Get API key from header
            api_key = request.headers.get("X-API-Key")
            
            # Check if API key is valid
            if not api_key:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "status": "error",
                        "error": "Missing API key",
                        "details": {
                            "header": "X-API-Key header is required for authentication"
                        }
                    }
                )
            
            # Validate the key
            is_valid = await self._validate_key_from_cache(api_key)
            if not is_valid:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "status": "error",
                        "error": "Invalid API key",
                        "details": {
                            "key": "The provided API key is not valid"
                        }
                    }
                )
        
        # Process the request
        response = await call_next(request)
        return response 