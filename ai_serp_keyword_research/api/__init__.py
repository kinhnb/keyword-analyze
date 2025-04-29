"""
API module for the AI SERP Keyword Research Agent.

This module includes all API-related components, including routers,
middleware, dependency injection, and request/response schemas.
"""

__all__ = ["create_api_router"]

from fastapi import APIRouter
from ai_serp_keyword_research.api.routes import analyze, feedback, health


def create_api_router() -> APIRouter:
    """
    Create and configure the main API router with all endpoints.
    
    Returns:
        APIRouter: Configured API router with all endpoints registered.
    """
    # Create main API router
    api_router = APIRouter(prefix="/api/v1")
    
    # Include all route modules
    api_router.include_router(analyze.router)
    api_router.include_router(feedback.router)
    api_router.include_router(health.router)
    
    return api_router
