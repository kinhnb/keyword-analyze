"""
Metrics middleware for the API.

This middleware collects API-related metrics like request counts, latencies, and status codes.
"""

import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from fastapi import FastAPI

from ai_serp_keyword_research.metrics.collector import get_metrics_collector


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware that collects API metrics.
    
    This middleware tracks:
    - Request counts by endpoint
    - Request latencies
    - Status code distribution
    - Request size distribution
    - Response size distribution
    """
    
    def __init__(
        self,
        app: FastAPI,
        exempt_paths: list[str] = None
    ):
        """
        Initialize the metrics middleware.
        
        Args:
            app: The FastAPI application
            exempt_paths: List of paths to exempt from metrics collection
        """
        super().__init__(app)
        self.exempt_paths = exempt_paths or []
        self.metrics = get_metrics_collector()
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process a request and collect metrics.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware or endpoint
            
        Returns:
            The response from the downstream handler
        """
        # Check if this path is exempt
        path = request.url.path
        if any(path.startswith(exempt) for exempt in self.exempt_paths):
            return await call_next(request)
        
        # Get the route path if possible (to avoid high cardinality in metrics)
        route_path = path
        if request.scope.get("route"):
            route_path = request.scope["route"].path
        
        # Record request start
        start_time = time.time()
        
        # Create tags for this request
        tags = {
            "method": request.method,
            "path": route_path,
        }
        
        # Increment request counter
        self.metrics.increment_counter("api_requests", tags=tags)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Update tags with status code
            tags["status"] = str(response.status_code)
            
            # Record status code
            self.metrics.increment_counter("api_status_codes", tags=tags)
            
            # Record response size if available
            if hasattr(response, "content_length") and response.content_length is not None:
                self.metrics.record_histogram(
                    "api_response_size_bytes", 
                    response.content_length,
                    tags=tags
                )
            
        except Exception as e:
            # Record server error
            tags["status"] = "500"
            self.metrics.increment_counter("api_status_codes", tags=tags)
            self.metrics.increment_counter("api_errors", tags=tags)
            raise
        finally:
            # Record request duration
            request_time = (time.time() - start_time) * 1000  # Convert to ms
            self.metrics.record_histogram("api_request_duration_ms", request_time, tags=tags)
        
        return response 