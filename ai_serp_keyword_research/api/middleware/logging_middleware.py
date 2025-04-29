"""
Logging middleware for the AI SERP Keyword Research Agent API.

This middleware adds request/response logging and correlation ID tracking.
"""

import time
import uuid
import logging
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from ai_serp_keyword_research.utils.logging import app_logger, CorrelationIDFilter, LogContext


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging API requests and responses.
    
    This middleware logs details about incoming requests and outgoing responses,
    including timing information, status codes, and correlation IDs for request tracing.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[list] = None,
        log_request_body: bool = False,
        log_response_body: bool = False
    ):
        """
        Initialize logging middleware with specified configurations.
        
        Args:
            app: The ASGI application
            exclude_paths: List of paths to exclude from logging
            log_request_body: Whether to log request bodies
            log_response_body: Whether to log response bodies
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
    
    async def set_body(self, request: Request) -> bytes:
        """
        Read and store request body.
        
        Args:
            request: The request to read
            
        Returns:
            Request body as bytes
        """
        body = await request.body()
        
        # Create a custom receive function that returns the stored body
        async def receive():
            return {"type": "http.request", "body": body}
        
        # Replace request's receive function
        request._receive = receive
        
        return body
    
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process a request with logging.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint to call
            
        Returns:
            The response from the next middleware or endpoint
        """
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Generate correlation ID for request tracking
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        
        # Set up logging context with correlation ID
        with LogContext(correlation_id=correlation_id):
            # Record start time
            start_time = time.time()
            
            # Log request details
            log_data = {
                "request_id": correlation_id,
                "request_method": request.method,
                "request_path": request.url.path,
                "request_query": str(request.query_params),
                "request_headers": {
                    k: v for k, v in request.headers.items()
                    if k.lower() not in ["authorization", "x-api-key"]  # Exclude sensitive headers
                },
                "client_ip": request.client.host,
                "client_port": request.client.port
            }
            
            # Log request body if configured
            if self.log_request_body:
                try:
                    body = await self.set_body(request)
                    log_data["request_body"] = body.decode("utf-8")
                except Exception as e:
                    log_data["request_body_error"] = str(e)
            
            app_logger.info(f"Request received: {request.method} {request.url.path}", extra=log_data)
            
            try:
                # Process the request
                response = await call_next(request)
                
                # Calculate request duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Add correlation ID to response headers
                response.headers["X-Correlation-ID"] = correlation_id
                
                # Log response details
                log_data = {
                    "request_id": correlation_id,
                    "response_status": response.status_code,
                    "response_headers": {
                        k: v for k, v in response.headers.items()
                        if k.lower() not in ["authorization"]  # Exclude sensitive headers
                    },
                    "duration_ms": round(duration_ms, 2)
                }
                
                # Log response body if configured
                if self.log_response_body:
                    # This is more complex as we need to read the response body
                    # without consuming it, which depends on the response type
                    # and is not always possible in a middleware context
                    pass
                
                log_level = logging.INFO if response.status_code < 400 else logging.ERROR
                app_logger.log(
                    log_level,
                    f"Response sent: {response.status_code} in {round(duration_ms, 2)}ms",
                    extra=log_data
                )
                
                return response
            except Exception as e:
                # Log exception
                duration_ms = (time.time() - start_time) * 1000
                app_logger.exception(
                    f"Request failed: {str(e)} in {round(duration_ms, 2)}ms",
                    extra={"request_id": correlation_id, "duration_ms": round(duration_ms, 2)}
                )
                raise  # Re-raise the exception for the default exception handler


class ContextualLoggingMiddleware:
    """
    Middleware for adding contextual logging to the application.
    
    This middleware integrates with logging to provide request-level context
    and correlation IDs for tracing requests across components.
    """
    
    def __init__(self, app: ASGIApp):
        """
        Initialize the contextual logging middleware.
        
        Args:
            app: The ASGI application
        """
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """
        ASGI callable for processing a request.
        
        Args:
            scope: ASGI scope
            receive: ASGI receive function
            send: ASGI send function
        """
        if scope["type"] != "http":
            # Pass through for WebSocket, lifespan, etc.
            await self.app(scope, receive, send)
            return
        
        # Extract headers from scope
        headers = dict(scope.get("headers", []))
        
        # Get or generate correlation ID
        correlation_id = None
        if b"x-correlation-id" in headers:
            correlation_id = headers[b"x-correlation-id"].decode("utf-8")
        
        # Set correlation ID for logging
        CorrelationIDFilter.set_correlation_id(correlation_id)
        
        # Process request with correlation ID
        try:
            await self.app(scope, receive, send)
        finally:
            # Clear correlation ID after request is processed
            CorrelationIDFilter.clear_correlation_id() 