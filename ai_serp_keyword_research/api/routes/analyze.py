"""
Analyze endpoints for the AI SERP Keyword Research Agent API.

This module provides endpoints for analyzing search terms and generating SEO recommendations.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse

from ai_serp_keyword_research.api.schemas.request import AnalyzeRequest
from ai_serp_keyword_research.api.schemas.response import AnalyzeResponse, ErrorResponse
from ai_serp_keyword_research.api.schemas.output import FullAnalysisOutput
from ai_serp_keyword_research.core.pipeline import SerpAnalysisPipeline
from ai_serp_keyword_research.data.repositories import SearchAnalysisRepository
from ai_serp_keyword_research.services.cache import CacheService
from ai_serp_keyword_research.orchestration.multi_agent_orchestrator import SerpKeywordAnalysisOrchestrator
from ai_serp_keyword_research.tracing import trace
from ai_serp_keyword_research.utils.logging import app_logger, CorrelationIDFilter, LogContext

# Create router
router = APIRouter(tags=["Analysis"])


@router.post("/analyze", response_model=AnalyzeResponse, responses={
    200: {"model": AnalyzeResponse, "description": "Successful analysis"},
    400: {"model": ErrorResponse, "description": "Invalid input"},
    429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
    500: {"model": ErrorResponse, "description": "Server error"}
})
async def analyze_keyword(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    request_obj: Request,
    cache_service: CacheService = Depends(),
    analysis_repository: SearchAnalysisRepository = Depends(),
    pipeline: SerpAnalysisPipeline = Depends(),
    orchestrator: SerpKeywordAnalysisOrchestrator = Depends(),
) -> AnalyzeResponse:
    """
    Analyze a search term to extract SEO insights and generate recommendations.
    
    This endpoint processes a search term through the SERP analysis pipeline,
    identifies search intent, detects market gaps, and generates SEO recommendations.
    
    Args:
        request: The analysis request containing the search term and options
        background_tasks: FastAPI background tasks handler
        request_obj: The FastAPI request object
        cache_service: Service for caching results
        analysis_repository: Repository for storing analysis results
        pipeline: SERP analysis pipeline
        orchestrator: Multi-agent orchestrator
        
    Returns:
        AnalysisResponse containing the analysis results or error information
    """
    # Get correlation ID from request headers or logging context
    correlation_id = request_obj.headers.get("X-Correlation-ID") or CorrelationIDFilter.get_correlation_id()
    analysis_id = str(uuid.uuid4())
    
    # Log the analysis request with correlation ID
    app_logger.info(
        f"Starting analysis for search term: {request.search_term}",
        extra={
            "correlation_id": correlation_id,
            "analysis_id": analysis_id,
            "search_term": request.search_term,
            "max_results": request.max_results,
            "client_ip": request_obj.client.host,
        }
    )
    
    try:
        # Check cache first
        cached_result = await cache_service.get_analysis_results(request.search_term)
        if cached_result:
            app_logger.info(
                f"Cache hit for search term: {request.search_term}",
                extra={
                    "correlation_id": correlation_id,
                    "analysis_id": cached_result.analysis_id,
                    "cache_hit": True,
                }
            )
            return AnalyzeResponse(
                status="success",
                data=cached_result
            )
        
        app_logger.info(
            f"Cache miss for search term: {request.search_term}",
            extra={"correlation_id": correlation_id, "cache_hit": False}
        )
        
        # Span the entire analysis workflow with tracing
        with trace(f"analyze_keyword_{request.search_term}"):
            # Process through pipeline first to get structured data
            app_logger.debug(
                f"Starting pipeline processing for: {request.search_term}",
                extra={"correlation_id": correlation_id, "analysis_id": analysis_id}
            )
            
            pipeline_result = await pipeline.process(request)
            
            app_logger.debug(
                f"Pipeline processing completed for: {request.search_term}",
                extra={
                    "correlation_id": correlation_id,
                    "analysis_id": analysis_id,
                    "intent_type": pipeline_result.intent_analysis.intent_type,
                    "has_market_gap": pipeline_result.market_gap.detected,
                    "execution_time_ms": pipeline_result.execution_time
                }
            )
            
            # Run multi-agent analysis with the pipeline data
            app_logger.debug(
                f"Starting agent analysis for: {request.search_term}",
                extra={"correlation_id": correlation_id, "analysis_id": analysis_id}
            )
            
            agent_result = await orchestrator.analyze(
                search_term=request.search_term,
                serp_data=pipeline_result.serp_data,
                intent_analysis=pipeline_result.intent_analysis,
                market_gap=pipeline_result.market_gap
            )
            
            app_logger.debug(
                f"Agent analysis completed for: {request.search_term}",
                extra={
                    "correlation_id": correlation_id,
                    "analysis_id": analysis_id,
                    "recommendations_count": len(agent_result.recommendations)
                }
            )
            
            # Combine results into the full analysis output
            timestamp = datetime.utcnow().isoformat() + "Z"
            full_analysis = FullAnalysisOutput(
                search_term=request.search_term,
                analysis_id=analysis_id,
                timestamp=timestamp,
                intent_analysis=agent_result.intent_analysis,
                market_gap=agent_result.market_gap,
                serp_features=pipeline_result.serp_features,
                recommendations=agent_result.recommendations,
                execution_time=pipeline_result.execution_time
            )
            
            # Store in cache for future requests
            app_logger.debug(
                f"Storing analysis in cache: {request.search_term}",
                extra={"correlation_id": correlation_id, "analysis_id": analysis_id}
            )
            
            background_tasks.add_task(
                cache_service.store_analysis_results,
                request.search_term,
                full_analysis
            )
            
            # Store in database (async)
            app_logger.debug(
                f"Storing analysis in database: {request.search_term}",
                extra={"correlation_id": correlation_id, "analysis_id": analysis_id}
            )
            
            background_tasks.add_task(
                analysis_repository.create,
                full_analysis
            )
            
            app_logger.info(
                f"Analysis completed successfully for: {request.search_term}",
                extra={
                    "correlation_id": correlation_id,
                    "analysis_id": analysis_id,
                    "intent_type": agent_result.intent_analysis.intent_type,
                    "has_market_gap": agent_result.market_gap.detected,
                    "recommendations_count": len(agent_result.recommendations),
                    "execution_time_ms": pipeline_result.execution_time
                }
            )
            
            return AnalyzeResponse(
                status="success",
                data=full_analysis
            )
            
    except ValueError as ve:
        # Handle validation errors
        error_msg = str(ve)
        app_logger.warning(
            f"Validation error during analysis: {error_msg}",
            extra={
                "correlation_id": correlation_id,
                "analysis_id": analysis_id,
                "search_term": request.search_term,
                "error_type": "ValidationError"
            }
        )
        return AnalyzeResponse(
            status="error",
            error=error_msg
        )
    except Exception as e:
        # Handle unexpected errors
        error_msg = str(e)
        app_logger.error(
            f"Unexpected error during analysis: {error_msg}",
            extra={
                "correlation_id": correlation_id,
                "analysis_id": analysis_id,
                "search_term": request.search_term,
                "error_type": type(e).__name__,
            },
            exc_info=True
        )
        return AnalyzeResponse(
            status="error",
            error=f"Analysis failed: {error_msg}"
        ) 