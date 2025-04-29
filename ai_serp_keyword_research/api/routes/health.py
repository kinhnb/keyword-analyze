"""
Health check endpoints for the AI SERP Keyword Research Agent API.

This module provides health check endpoints to verify the status of the application and its dependencies.
"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from ai_serp_keyword_research.api.schemas.response import HealthResponse
from ai_serp_keyword_research.services.cache import CacheService
from ai_serp_keyword_research.services.serp_provider import SerpProvider
from ai_serp_keyword_research.data.repositories.base import get_database_status
from ai_serp_keyword_research.tracing import trace


# Create router
router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    cache_service: Optional[CacheService] = Depends(),
    serp_provider: Optional[SerpProvider] = Depends(),
) -> HealthResponse:
    """
    Get the health status of the application and its dependencies.
    
    This endpoint checks the status of all service dependencies and returns
    a comprehensive health report. It's useful for monitoring and alerting.
    
    Args:
        cache_service: Service for caching results
        serp_provider: Service for fetching SERP data
        
    Returns:
        HealthResponse containing the health status of the application and its dependencies
    """
    with trace("health_check"):
        # Check database connection
        db_status = await get_database_status()
        
        # Check Redis connection
        redis_status = "disconnected"
        if cache_service:
            redis_status = await cache_service.get_connection_status()
        
        # Check SERP provider
        serp_status = "unknown"
        if serp_provider:
            serp_status = "available" if await serp_provider.is_available() else "unavailable"
        
        # Determine overall status
        dependencies = {
            "database": db_status,
            "redis": redis_status,
            "serp_api": serp_status
        }
        
        if all(status in ["connected", "available"] for status in dependencies.values()):
            overall_status = "healthy"
        elif any(status in ["disconnected", "unavailable"] for status in dependencies.values()):
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        # Get API version
        version = os.getenv("API_VERSION", "1.0.0")
        
        return HealthResponse(
            status=overall_status,
            version=version,
            timestamp=datetime.utcnow().isoformat() + "Z",
            dependencies=dependencies
        ) 