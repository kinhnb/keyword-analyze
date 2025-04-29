"""
Tracing middleware for the AI SERP Keyword Research Agent API.

This middleware implements request/response tracing for monitoring and debugging.
"""

import time
import uuid
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from ai_serp_keyword_research.tracing import trace


class TracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request/response tracing.
    
    This middleware adds trace context to requests, measures response times,
    and logs request/response details for monitoring and debugging.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[list] = None
    ):
        """
        Initialize tracing middleware.
        
        Args:
            app: The ASGI application
            exclude_paths: List of paths to exclude from detailed tracing
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/favicon.ico"]
        
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process a request through the tracing middleware.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint to call
            
        Returns:
            The response from the next middleware or endpoint
        """
        # Generate a unique trace ID if not already present
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        
        # Calculate path for trace naming
        path = request.url.path
        if path.startswith("/api/"):
            # Use a cleaner name for API endpoints
            path_parts = path.split("/")
            if len(path_parts) >= 4:  # /api/v1/resource
                path = f"{path_parts[3]}"
        
        # Start tracking request processing time
        start_time = time.time()
        
        # Detailed tracing for non-excluded paths
        if not any(request.url.path.startswith(path) for path in self.exclude_paths):
            trace_name = f"{request.method}_{path}"
            with trace(trace_name, {"trace_id": trace_id}):
                response = await self._process_request(request, call_next, trace_id)
        else:
            # Simple processing for excluded paths
            response = await self._process_request(request, call_next, trace_id)
        
        # Calculate request processing time
        process_time = time.time() - start_time
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Add trace ID header for correlation
        response.headers["X-Trace-ID"] = trace_id
        
        return response
    
    async def _process_request(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
        trace_id: str
    ) -> Response:
        """
        Process the request with exception handling.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint to call
            trace_id: The trace ID for this request
            
        Returns:
            The response from the next middleware or endpoint
        """
        try:
            # Add trace ID to request state for use in endpoints
            request.state.trace_id = trace_id
            
            # Process the request
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Log exception details with trace context
            with trace(f"request_error", {"trace_id": trace_id, "error": str(e)}):
                # Re-raise to let exception handlers deal with it
                raise 