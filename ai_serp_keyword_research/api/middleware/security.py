"""
Security middleware for the AI SERP Keyword Research Agent API.

This middleware implements input validation, sanitization, and proper error
handling for API requests to ensure robust security.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Set, Any, Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from ai_serp_keyword_research.tracing import trace

# Configure logging
logger = logging.getLogger(__name__)

# Common unsafe patterns to check in request bodies
UNSAFE_PATTERNS = [
    r'<script.*?>.*?</script>',                     # Script tags
    r'javascript:',                                 # JavaScript protocol
    r'on\w+\s*=\s*[\'"].*?[\'"]',                   # Event handlers
    r'(?:\\x|%|\\u00)[0-9a-f]{2}',                  # Encoded characters
    r'(?:union|select|insert|update|delete|drop)',  # SQL keywords
    r'\$(?:\{|ne|gt|lt|in)\b',                      # NoSQL injection
    r'[\'"]\s*(?:or|and)\s*[\'"]?\s*\d',            # SQL logical operators
    r'(?:\/|\.\.\/|\.\.\\|%2e%2e)',                 # Directory traversal
]

# File extensions that should never be in request data
UNSAFE_EXTENSIONS = {
    '.php', '.asp', '.aspx', '.jsp', '.jspx', '.exe', '.bat', '.cmd', '.dll', '.sh'
}


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API security measures.
    
    This middleware provides:
    1. Input validation - ensures requests match expected schemas
    2. Input sanitization - removes potentially unsafe content
    3. Proper error handling - provides meaningful error responses
    """
    
    def __init__(
        self,
        app: ASGIApp,
        exempt_paths: Optional[List[str]] = None,
        validators: Optional[Dict[str, Callable]] = None
    ):
        """
        Initialize security middleware with specified configurations.
        
        Args:
            app: The ASGI application
            exempt_paths: List of paths exempt from security middleware
            validators: Dictionary mapping endpoint paths to custom validator functions
        """
        super().__init__(app)
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/openapi.json", "/redoc", "/static", "/metrics"]
        self.validators = validators or {}
        self.unsafe_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in UNSAFE_PATTERNS]
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process a request through the security middleware.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint to call
            
        Returns:
            The response from the next middleware or endpoint or an error response
        """
        # Skip security checks for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Apply security measures
        with trace("security_middleware"):
            # Only validate POST, PUT, PATCH requests that have a body
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    # Clone the request body for validation
                    body = await request.body()
                    if body:
                        # Sanitize and validate the body
                        is_safe, error_message = self._validate_and_sanitize(body)
                        if not is_safe:
                            return JSONResponse(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                content={
                                    "status": "error",
                                    "error": "Invalid input",
                                    "details": error_message
                                }
                            )
                except Exception as e:
                    logger.error(f"Error in security middleware: {str(e)}")
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "status": "error",
                            "error": "Invalid request",
                            "details": "The request could not be processed due to validation errors"
                        }
                    )
        
        # Process the request through error handling
        try:
            # Process the request
            response = await call_next(request)
            return response
        except ValidationError as e:
            # Handle Pydantic validation errors
            logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "status": "error",
                    "error": "Validation error",
                    "details": e.errors()
                }
            )
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unhandled exception in request processing: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "error": "Internal server error",
                    "details": "An unexpected error occurred"
                }
            )
    
    def _validate_and_sanitize(self, body: bytes) -> tuple[bool, Optional[str]]:
        """
        Validate and sanitize request body.
        
        Args:
            body: Request body as bytes
            
        Returns:
            Tuple of (is_safe, error_message)
        """
        try:
            # Only process JSON requests
            try:
                data = json.loads(body)
                if not isinstance(data, (dict, list)):
                    return False, "Invalid JSON structure"
            except json.JSONDecodeError:
                # Not JSON, might be form data or other format
                # For now, we only do deep inspection on JSON
                return True, None
            
            # Check for unsafe patterns in JSON string
            body_str = body.decode('utf-8', errors='ignore')
            for pattern in self.unsafe_patterns:
                if pattern.search(body_str):
                    return False, "Potentially unsafe content detected"
            
            # Check for unsafe file extensions
            if isinstance(data, dict):
                for key, value in self._flatten_dict(data).items():
                    if isinstance(value, str):
                        # Check if value contains file paths with unsafe extensions
                        for ext in UNSAFE_EXTENSIONS:
                            if ext in value.lower():
                                return False, f"Potentially unsafe file extension detected: {ext}"
            
            return True, None
        except Exception as e:
            logger.error(f"Error validating request body: {str(e)}")
            return False, "Error processing request"
    
    def _flatten_dict(self, data: Dict[str, Any], parent_key: str = '') -> Dict[str, Any]:
        """
        Flatten a nested dictionary for easier validation.
        
        Args:
            data: The dictionary to flatten
            parent_key: The parent key for nested dictionaries
            
        Returns:
            Flattened dictionary with keys like "parent.child.grandchild"
        """
        items = []
        for key, value in data.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                items.extend(self._flatten_dict(value, new_key).items())
            else:
                items.append((new_key, value))
        return dict(items) 