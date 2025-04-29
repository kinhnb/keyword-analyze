"""
Unit tests for repository implementations.

This module contains tests for the SQLAlchemy repository implementations
to ensure they work correctly with the database.
"""

import os
import uuid
import asyncio
import pytest
from typing import List, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ai_serp_keyword_research.data.models.database import Base, SearchAnalysis, SerpFeature, Recommendation
from ai_serp_keyword_research.data.repositories import (
    SQLSearchAnalysisRepository,
    SQLSerpFeaturesRepository,
    SQLRecommendationsRepository,
)

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create an in-memory SQLite database session for testing.
    
    This fixture creates a new in-memory database for each test,
    sets up the tables, and provides a session for the test.
    
    Yields:
        AsyncSession: An async SQLAlchemy session
    """
    # Create engine and tables
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create a session for the test
    session = async_session()
    try:
        yield session
    finally:
        await session.close()
        # Drop tables after test is complete
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def search_analysis_data() -> dict:
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
def serp_feature_data(search_analysis_data: dict) -> dict:
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
def recommendation_data(search_analysis_data: dict) -> dict:
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


class TestSearchAnalysisRepository:
    """Tests for SearchAnalysisRepository implementation."""
    
    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession, search_analysis_data: dict):
        """Test creating a search analysis record."""
        # Arrange
        repo = SQLSearchAnalysisRepository(db_session)
        
        # Act
        result = await repo.create(**search_analysis_data)
        
        # Assert
        assert result is not None
        assert result.id == search_analysis_data["id"]
        assert result.search_term == search_analysis_data["search_term"]
        assert result.intent_type == search_analysis_data["intent_type"]
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session: AsyncSession, search_analysis_data: dict):
        """Test retrieving a search analysis by ID."""
        # Arrange
        repo = SQLSearchAnalysisRepository(db_session)
        created = await repo.create(**search_analysis_data)
        
        # Act
        result = await repo.get_by_id(created.id)
        
        # Assert
        assert result is not None
        assert result.id == created.id
        assert result.search_term == created.search_term
    
    @pytest.mark.asyncio
    async def test_get_by_search_term(self, db_session: AsyncSession, search_analysis_data: dict):
        """Test retrieving a search analysis by search term."""
        # Arrange
        repo = SQLSearchAnalysisRepository(db_session)
        await repo.create(**search_analysis_data)
        
        # Act
        result = await repo.get_by_search_term(search_analysis_data["search_term"])
        
        # Assert
        assert result is not None
        assert result.id == search_analysis_data["id"]
        assert result.search_term == search_analysis_data["search_term"]
    
    @pytest.mark.asyncio
    async def test_list_by_intent_type(self, db_session: AsyncSession, search_analysis_data: dict):
        """Test listing search analyses by intent type."""
        # Arrange
        repo = SQLSearchAnalysisRepository(db_session)
        await repo.create(**search_analysis_data)
        
        # Create another with different intent
        different_intent = search_analysis_data.copy()
        different_intent["id"] = str(uuid.uuid4())
        different_intent["search_term"] = "mom graphic tee"
        different_intent["intent_type"] = "informational"
        await repo.create(**different_intent)
        
        # Act
        results = await repo.list_by_intent_type("transactional")
        
        # Assert
        assert len(results) == 1
        assert results[0].search_term == search_analysis_data["search_term"]
        assert results[0].intent_type == "transactional"
    
    @pytest.mark.asyncio
    async def test_list_market_gaps(self, db_session: AsyncSession, search_analysis_data: dict):
        """Test listing search analyses with market gaps."""
        # Arrange
        repo = SQLSearchAnalysisRepository(db_session)
        await repo.create(**search_analysis_data)
        
        # Create another without market gap
        no_gap = search_analysis_data.copy()
        no_gap["id"] = str(uuid.uuid4())
        no_gap["search_term"] = "mom graphic tee"
        no_gap["has_market_gap"] = False
        await repo.create(**no_gap)
        
        # Act
        results = await repo.list_market_gaps()
        
        # Assert
        assert len(results) == 1
        assert results[0].search_term == search_analysis_data["search_term"]
        assert results[0].has_market_gap is True


class TestSerpFeaturesRepository:
    """Tests for SerpFeaturesRepository implementation."""
    
    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession, search_analysis_data: dict, serp_feature_data: dict):
        """Test creating a SERP feature record."""
        # Arrange
        analysis_repo = SQLSearchAnalysisRepository(db_session)
        feature_repo = SQLSerpFeaturesRepository(db_session)
        
        # Create parent search analysis first
        await analysis_repo.create(**search_analysis_data)
        
        # Act
        result = await feature_repo.create(**serp_feature_data)
        
        # Assert
        assert result is not None
        assert result.id == serp_feature_data["id"]
        assert result.analysis_id == search_analysis_data["id"]
        assert result.feature_type == serp_feature_data["feature_type"]
    
    @pytest.mark.asyncio
    async def test_list_by_analysis_id(self, db_session: AsyncSession, search_analysis_data: dict, serp_feature_data: dict):
        """Test listing SERP features by analysis ID."""
        # Arrange
        analysis_repo = SQLSearchAnalysisRepository(db_session)
        feature_repo = SQLSerpFeaturesRepository(db_session)
        
        # Create parent search analysis first
        await analysis_repo.create(**search_analysis_data)
        
        # Create feature
        await feature_repo.create(**serp_feature_data)
        
        # Create another feature for the same analysis
        second_feature = serp_feature_data.copy()
        second_feature["id"] = str(uuid.uuid4())
        second_feature["feature_type"] = "featured_snippet"
        await feature_repo.create(**second_feature)
        
        # Act
        results = await feature_repo.list_by_analysis_id(search_analysis_data["id"])
        
        # Assert
        assert len(results) == 2
        assert results[0].analysis_id == search_analysis_data["id"]
        assert results[1].analysis_id == search_analysis_data["id"]
    
    @pytest.mark.asyncio
    async def test_delete_by_analysis_id(self, db_session: AsyncSession, search_analysis_data: dict, serp_feature_data: dict):
        """Test deleting SERP features by analysis ID."""
        # Arrange
        analysis_repo = SQLSearchAnalysisRepository(db_session)
        feature_repo = SQLSerpFeaturesRepository(db_session)
        
        # Create parent search analysis first
        await analysis_repo.create(**search_analysis_data)
        
        # Create features
        await feature_repo.create(**serp_feature_data)
        
        second_feature = serp_feature_data.copy()
        second_feature["id"] = str(uuid.uuid4())
        second_feature["feature_type"] = "featured_snippet"
        await feature_repo.create(**second_feature)
        
        # Act
        result = await feature_repo.delete_by_analysis_id(search_analysis_data["id"])
        
        # Assert
        assert result is True
        features = await feature_repo.list_by_analysis_id(search_analysis_data["id"])
        assert len(features) == 0


class TestRecommendationsRepository:
    """Tests for RecommendationsRepository implementation."""
    
    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession, search_analysis_data: dict, recommendation_data: dict):
        """Test creating a recommendation record."""
        # Arrange
        analysis_repo = SQLSearchAnalysisRepository(db_session)
        recommendation_repo = SQLRecommendationsRepository(db_session)
        
        # Create parent search analysis first
        await analysis_repo.create(**search_analysis_data)
        
        # Act
        result = await recommendation_repo.create(**recommendation_data)
        
        # Assert
        assert result is not None
        assert result.id == recommendation_data["id"]
        assert result.analysis_id == search_analysis_data["id"]
        assert result.tactic_type == recommendation_data["tactic_type"]
        assert result.priority == recommendation_data["priority"]
    
    @pytest.mark.asyncio
    async def test_list_high_priority(self, db_session: AsyncSession, search_analysis_data: dict, recommendation_data: dict):
        """Test listing high-priority recommendations."""
        # Arrange
        analysis_repo = SQLSearchAnalysisRepository(db_session)
        recommendation_repo = SQLRecommendationsRepository(db_session)
        
        # Create parent search analysis first
        await analysis_repo.create(**search_analysis_data)
        
        # Create high-priority recommendation
        await recommendation_repo.create(**recommendation_data)
        
        # Create lower-priority recommendation
        low_priority = recommendation_data.copy()
        low_priority["id"] = str(uuid.uuid4())
        low_priority["priority"] = 3
        await recommendation_repo.create(**low_priority)
        
        # Act
        results = await recommendation_repo.list_high_priority(max_priority=2)
        
        # Assert
        assert len(results) == 1
        assert results[0].priority <= 2
    
    @pytest.mark.asyncio
    async def test_list_high_confidence(self, db_session: AsyncSession, search_analysis_data: dict, recommendation_data: dict):
        """Test listing high-confidence recommendations."""
        # Arrange
        analysis_repo = SQLSearchAnalysisRepository(db_session)
        recommendation_repo = SQLRecommendationsRepository(db_session)
        
        # Create parent search analysis first
        await analysis_repo.create(**search_analysis_data)
        
        # Create high-confidence recommendation
        await recommendation_repo.create(**recommendation_data)
        
        # Create lower-confidence recommendation
        low_confidence = recommendation_data.copy()
        low_confidence["id"] = str(uuid.uuid4())
        low_confidence["confidence"] = 0.6
        await recommendation_repo.create(**low_confidence)
        
        # Act
        results = await recommendation_repo.list_high_confidence(min_confidence=0.8)
        
        # Assert
        assert len(results) == 1
        assert results[0].confidence >= 0.8 