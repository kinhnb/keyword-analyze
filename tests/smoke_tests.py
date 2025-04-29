"""
Smoke tests for the AI SERP Keyword Research Agent.

These tests provide a quick verification of basic system functionality without 
requiring full integration testing. They're designed to run quickly and catch 
obvious failures early in the testing process.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from ai_serp_keyword_research.core.domain.models import SearchTerm
from ai_serp_keyword_research.core.pipeline.pipeline import SerpAnalysisPipeline
from ai_serp_keyword_research.agents.seo_expert_agent import SEOExpertAgent
from ai_serp_keyword_research.agents.intent_analyzer_agent import IntentAnalyzerAgent
from ai_serp_keyword_research.agents.recommendation_agent import RecommendationAgent
from ai_serp_keyword_research.api.main import app

from fastapi.testclient import TestClient


@pytest.mark.smoke
def test_app_startup():
    """Verify that the FastAPI application can start up without errors."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_pipeline_initialization():
    """Verify that the pipeline can be initialized with mock components."""
    # Create mock stages
    stages = [AsyncMock() for _ in range(6)]
    
    # Initialize the pipeline
    pipeline = SerpAnalysisPipeline(
        input_validation_stage=stages[0],
        serp_retrieval_stage=stages[1],
        intent_analysis_stage=stages[2],
        market_gap_analysis_stage=stages[3],
        recommendation_generation_stage=stages[4],
        output_formatting_stage=stages[5]
    )
    
    # Verify the pipeline is correctly initialized
    assert pipeline.input_validation_stage == stages[0]
    assert pipeline.serp_retrieval_stage == stages[1]
    assert pipeline.intent_analysis_stage == stages[2]
    assert pipeline.market_gap_analysis_stage == stages[3]
    assert pipeline.recommendation_generation_stage == stages[4]
    assert pipeline.output_formatting_stage == stages[5]


@pytest.mark.smoke
def test_agent_initialization():
    """Verify that the agents can be initialized."""
    # Mock the OpenAI Agents SDK dependencies
    with patch("agents.Agent", return_value=MagicMock()):
        # Test SEO Expert Agent initialization
        seo_agent = SEOExpertAgent()
        assert seo_agent is not None
        
        # Test Intent Analyzer Agent initialization
        intent_agent = IntentAnalyzerAgent()
        assert intent_agent is not None
        
        # Test Recommendation Agent initialization
        recommendation_agent = RecommendationAgent()
        assert recommendation_agent is not None


@pytest.mark.smoke
def test_domain_models():
    """Verify that the domain models can be instantiated and validated."""
    # Test SearchTerm model
    search_term = SearchTerm(term="dad graphic tee", max_results=10)
    assert search_term.term == "dad graphic tee"
    assert search_term.max_results == 10
    
    # Test validation
    with pytest.raises(ValueError):
        # Empty search term should fail validation
        SearchTerm(term="", max_results=10)
    
    with pytest.raises(ValueError):
        # Negative max_results should fail validation
        SearchTerm(term="dad graphic tee", max_results=-5)


@pytest.mark.smoke
def test_api_routes_registered():
    """Verify that the API routes are registered properly."""
    with TestClient(app) as client:
        # Test health endpoint
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # Test analyze endpoint exists (without actually calling it)
        # This just checks the route is registered
        routes = [route.path for route in app.routes]
        assert "/api/v1/analyze" in routes
        
        # Test docs endpoint
        docs_response = client.get("/docs")
        assert docs_response.status_code == 200


if __name__ == "__main__":
    # This allows running the smoke tests directly
    pytest.main(["-v", "-m", "smoke", __file__]) 