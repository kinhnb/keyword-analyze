"""
Integration tests for the complete AI SERP Keyword Research Agent system.

These tests verify that all components work together correctly in the full system flow:
1. API endpoint receives a request
2. Request is processed through the pipeline
3. Agents are orchestrated correctly
4. Response is returned with proper structure
"""
import pytest
import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from ai_serp_keyword_research.api.main import app
from ai_serp_keyword_research.api.dependencies import get_cache_service, get_serp_provider
from ai_serp_keyword_research.api.dependencies import get_agent_orchestrator
from tests.fixtures import (
    SERP_RESULT_TRANSACTIONAL,
    INTENT_ANALYSIS_TRANSACTIONAL,
    MARKET_GAP_PRESENT,
    RECOMMENDATIONS_TRANSACTIONAL,
    API_RESPONSE_EXAMPLE
)


@pytest.mark.integration
class TestSystemIntegration:
    """Integration tests for the full system flow."""
    
    @pytest.fixture
    def test_client(self):
        """Create a FastAPI test client."""
        with TestClient(app) as client:
            yield client
    
    @pytest.fixture
    def mock_serp_provider(self):
        """Mock the SERP provider to return test data."""
        mock_provider = AsyncMock()
        mock_provider.fetch_results = AsyncMock(return_value=SERP_RESULT_TRANSACTIONAL)
        return mock_provider
    
    @pytest.fixture
    def mock_cache_service(self):
        """Mock the cache service."""
        mock_service = AsyncMock()
        mock_service.get_analysis = AsyncMock(return_value=None)  # No cached results
        mock_service.store_analysis = AsyncMock()
        return mock_service
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Mock the agent orchestrator."""
        mock_orch = AsyncMock()
        mock_orch.analyze_search_term = AsyncMock(return_value={
            "intent_analysis": INTENT_ANALYSIS_TRANSACTIONAL,
            "market_gap": MARKET_GAP_PRESENT,
            "recommendations": RECOMMENDATIONS_TRANSACTIONAL
        })
        return mock_orch
    
    @pytest.fixture(autouse=True)
    def setup_dependencies(self, mock_serp_provider, mock_cache_service, mock_orchestrator):
        """Set up the API dependencies using mocks."""
        app.dependency_overrides[get_serp_provider] = lambda: mock_serp_provider
        app.dependency_overrides[get_cache_service] = lambda: mock_cache_service
        app.dependency_overrides[get_agent_orchestrator] = lambda: mock_orchestrator
        
        yield
        
        # Clean up by removing the overrides
        app.dependency_overrides.clear()
    
    def test_analyze_endpoint_success(self, test_client):
        """Test the analyze endpoint with a successful flow."""
        # Create the test request
        request_data = {
            "search_term": "dad graphic tee",
            "max_results": 10
        }
        
        # Make the API request
        response = test_client.post(
            "/api/v1/analyze",
            json=request_data,
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "analysis" in data
        assert "market_gap" in data
        assert "recommendations" in data
        
        # Verify content
        assert data["analysis"]["intent_type"] == "transactional"
        assert data["market_gap"]["detected"] is True
        assert len(data["recommendations"]) > 0
        
        # Verify recommendation structure
        recommendation = data["recommendations"][0]
        assert "tactic_type" in recommendation
        assert "description" in recommendation
        assert "priority" in recommendation
        assert "confidence" in recommendation
    
    def test_analyze_endpoint_with_cache(self, test_client, mock_cache_service):
        """Test the analyze endpoint with a cached result."""
        # Set up the cache to return a cached result
        mock_cache_service.get_analysis.return_value = API_RESPONSE_EXAMPLE
        
        # Create the test request
        request_data = {
            "search_term": "dad graphic tee",
            "max_results": 10
        }
        
        # Make the API request
        response = test_client.post(
            "/api/v1/analyze",
            json=request_data,
            headers={"X-API-Key": "test-api-key"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify cached data was used
        assert data == API_RESPONSE_EXAMPLE
    
    def test_analyze_endpoint_validation(self, test_client):
        """Test the analyze endpoint with invalid inputs."""
        # Test with empty search term
        request_data = {
            "search_term": "",
            "max_results": 10
        }
        
        response = test_client.post(
            "/api/v1/analyze",
            json=request_data,
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test with too long search term
        request_data = {
            "search_term": "a" * 300,  # Very long search term
            "max_results": 10
        }
        
        response = test_client.post(
            "/api/v1/analyze",
            json=request_data,
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test with negative max_results
        request_data = {
            "search_term": "dad graphic tee",
            "max_results": -5
        }
        
        response = test_client.post(
            "/api/v1/analyze",
            json=request_data,
            headers={"X-API-Key": "test-api-key"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_health_endpoint(self, test_client):
        """Test the health check endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "dependencies" in data
    
    @pytest.mark.asyncio
    async def test_end_to_end_flow(self, mock_orchestrator):
        """Test the end-to-end flow from API to agents to pipeline."""
        # This test runs outside the FastAPI test client to directly test the flow
        from ai_serp_keyword_research.core.domain.models import SearchTerm
        from ai_serp_keyword_research.api.routes.analyze import analyze_search_term
        
        # Create the input
        search_term = SearchTerm(term="dad graphic tee", max_results=10)
        
        # Run the analysis
        result = await analyze_search_term(
            search_term=search_term,
            serp_provider=AsyncMock(),
            cache_service=AsyncMock(get_analysis=AsyncMock(return_value=None)),
            agent_orchestrator=mock_orchestrator
        )
        
        # Verify the orchestrator was called correctly
        mock_orchestrator.analyze_search_term.assert_called_once()
        call_args = mock_orchestrator.analyze_search_term.call_args[0]
        assert call_args[0].term == "dad graphic tee"
        
        # Verify result structure
        assert "analysis" in result
        assert "market_gap" in result
        assert "recommendations" in result 