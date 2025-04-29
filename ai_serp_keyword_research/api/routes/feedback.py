"""
Feedback endpoints for the AI SERP Keyword Research Agent API.

This module provides endpoints for collecting user feedback on analysis results.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from ai_serp_keyword_research.api.schemas.request import FeedbackRequest
from ai_serp_keyword_research.api.schemas.response import FeedbackResponse, ErrorResponse
from ai_serp_keyword_research.data.repositories import SearchAnalysisRepository
from ai_serp_keyword_research.tracing import trace

# Create router
router = APIRouter(tags=["Feedback"])


@router.post("/feedback", response_model=FeedbackResponse, responses={
    200: {"model": FeedbackResponse, "description": "Feedback received successfully"},
    400: {"model": ErrorResponse, "description": "Invalid feedback data"},
    404: {"model": ErrorResponse, "description": "Analysis not found"},
    500: {"model": ErrorResponse, "description": "Server error"}
})
async def submit_feedback(
    feedback: FeedbackRequest,
    analysis_repository: SearchAnalysisRepository = Depends()
) -> FeedbackResponse:
    """
    Submit feedback on an analysis result.
    
    This endpoint allows users to provide feedback on analysis results,
    helping to improve the quality of recommendations over time.
    
    Args:
        feedback: The feedback data including rating and comments
        analysis_repository: Repository for storing analysis feedback
        
    Returns:
        FeedbackResponse confirming successful submission
    """
    try:
        with trace(f"submit_feedback_{feedback.analysis_id}"):
            # Check if the analysis exists
            analysis = await analysis_repository.get_by_id(feedback.analysis_id)
            if not analysis:
                return FeedbackResponse(
                    status="error",
                    message=f"Analysis with ID {feedback.analysis_id} not found"
                )
            
            # Generate unique ID for this feedback
            feedback_id = str(uuid.uuid4())
            
            # Store the feedback
            await analysis_repository.store_feedback(
                analysis_id=feedback.analysis_id,
                feedback_id=feedback_id,
                rating=feedback.rating,
                comments=feedback.comments,
                helpful_recommendations=feedback.helpful_recommendations,
                unhelpful_recommendations=feedback.unhelpful_recommendations,
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            
            return FeedbackResponse(
                status="success",
                message="Feedback recorded successfully",
                feedback_id=feedback_id
            )
    
    except ValueError as ve:
        return FeedbackResponse(
            status="error",
            message=str(ve)
        )
    
    except Exception as e:
        return FeedbackResponse(
            status="error",
            message=f"Failed to record feedback: {str(e)}"
        ) 