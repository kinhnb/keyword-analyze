"""
Project-wide pytest fixtures and configuration.
"""
import os
import uuid
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import fakeredis.aioredis
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from ai_serp_keyword_research.data.models.base import Base
from ai_serp_keyword_research.data.models.search_analysis import SearchAnalysis
from ai_serp_keyword_research.data.models.serp_features import SerpFeature
from ai_serp_keyword_research.data.models.recommendations import Recommendation
from ai_serp_keyword_research.core.domain.models import (
    SearchTerm,
    IntentAnalysis,
    MarketGap,
    Recommendation as RecommendationModel,
)


# Environment setup for testing
os.environ.setdefault("ENVIRONMENT", "test")


# Event loop fixture
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Database fixtures
@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    # Use SQLite in-memory for tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        # Create tables for all models
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, expire_on_commit=False, class_=AsyncSession
    )
    
    async with async_session() as session:
        async with session.begin():
            yield session
            # Rollback at the end of the test
            await session.rollback()


# Redis fixtures
@pytest.fixture
async def fake_redis():
    """Create a fake Redis instance for testing."""
    client = fakeredis.aioredis.FakeRedis()
    yield client
    await client.close()


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    client = AsyncMock(spec=Redis)
    client.ping = AsyncMock(return_value=True)
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock(return_value=True)
    client.delete = AsyncMock(return_value=1)
    client.keys = AsyncMock(return_value=[])
    client.info = AsyncMock(return_value={"used_memory_human": "1M", "uptime_in_seconds": 3600})
    return client


# Domain model fixtures
@pytest.fixture
def search_term():
    """Create a sample SearchTerm object."""
    return SearchTerm(
        term="dad graphic tee",
        max_results=10
    )


@pytest.fixture
def intent_analysis():
    """Create a sample IntentAnalysis object."""
    return IntentAnalysis(
        main_keyword="dad t-shirt",
        secondary_keywords=["funny dad shirt", "father's day gift"],
        intent_type="transactional",
        confidence=0.85
    )


@pytest.fixture
def market_gap():
    """Create a sample MarketGap object."""
    return MarketGap(
        detected=True,
        description="Limited personalized dad shirts with profession themes",
        opportunity_score=0.75
    )


@pytest.fixture
def recommendation_model():
    """Create a sample Recommendation model object."""
    return RecommendationModel(
        tactic_type="product_page_optimization",
        description="Create product pages targeting 'profession + dad shirt' keywords",
        priority=1,
        confidence=0.85
    )


# Database model fixtures
@pytest.fixture
def search_analysis_data():
    """
    Provide sample search analysis data for testing.
    
    Returns:
        dict: Sample search analysis data
    """
    return {
        "id": str(uuid.uuid4()),
        "search_term": "dad graphic tee",
        "main_keyword": "dad t-shirt",
        "secondary_keywords": ["funny dad shirt", "father's day gift"],
        "intent_type": "transactional",
        "has_market_gap": True,
        "confidence": 0.85,
    }


@pytest.fixture
def serp_feature_data(search_analysis_data):
    """
    Provide sample SERP feature data for testing.
    
    Args:
        search_analysis_data: Sample search analysis data
        
    Returns:
        dict: Sample SERP feature data
    """
    return {
        "id": str(uuid.uuid4()),
        "analysis_id": search_analysis_data["id"],
        "feature_type": "shopping_ads",
        "feature_position": 1,
        "feature_data": {"num_ads": 3, "shop_urls": ["example.com"]},
    }


@pytest.fixture
def recommendation_data(search_analysis_data):
    """
    Provide sample recommendation data for testing.
    
    Args:
        search_analysis_data: Sample search analysis data
        
    Returns:
        dict: Sample recommendation data
    """
    return {
        "id": str(uuid.uuid4()),
        "analysis_id": search_analysis_data["id"],
        "tactic_type": "product_page_optimization",
        "description": "Create product pages targeting 'profession + dad shirt' keywords",
        "priority": 1,
        "confidence": 0.85,
    }


# SERP data fixtures
@pytest.fixture
def sample_serp_data():
    """Create sample SERP data for testing."""
    return {
        "search_term": "dad graphic tee",
        "results": [
            {
                "title": "Funny Dad Graphic Tees | Best Gift for Father's Day",
                "description": "Shop our collection of hilarious dad graphic tees. Perfect gift for Father's Day!",
                "url": "https://example.com/funny-dad-tees",
                "position": 1
            },
            {
                "title": "Dad Graphic T-Shirts | Shop Online | Fast Shipping",
                "description": "Find the perfect dad graphic tee. Many designs available with fast shipping.",
                "url": "https://example.com/dad-tshirts",
                "position": 2
            },
            {
                "title": "Custom Dad Graphic Tees | Create Your Own Design",
                "description": "Create custom dad graphic tees with your own text and images. Great for gifts!",
                "url": "https://example.com/custom-dad-tees",
                "position": 3
            }
        ],
        "features": [
            {
                "type": "shopping_ads",
                "position": 1,
                "data": {
                    "products": 3
                }
            },
            {
                "type": "image_pack",
                "position": 4,
                "data": {
                    "images": 8
                }
            }
        ]
    }


# API test fixtures
@pytest.fixture
def test_client():
    """Create a test client for FastAPI."""
    from ai_serp_keyword_research.api.main import app
    from fastapi.testclient import TestClient
    
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_agent_runner():
    """Create a mock Agent Runner."""
    runner = AsyncMock()
    runner.run.return_value = AsyncMock()
    return runner


# Tracing fixtures
@pytest.fixture
def mock_trace_processor():
    """Create a mock trace processor."""
    processor = MagicMock()
    return processor


# Agents fixtures
@pytest.fixture
def mock_agent():
    """Create a mock agent."""
    agent = MagicMock()
    agent.name = "Test Agent"
    agent.instructions = "Test instructions"
    agent.run = AsyncMock()
    return agent


# Environment variable fixtures
@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-openai-key",
        "SERP_API_KEY": "test-serp-key",
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/0",
        "API_RATE_LIMIT": "100",
        "ENVIRONMENT": "test"
    }):
        yield 