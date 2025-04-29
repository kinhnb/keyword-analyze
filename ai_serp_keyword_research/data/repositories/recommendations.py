"""
Recommendations repository for data access.

This module provides the interface and implementation for
accessing Recommendation records in the database.
"""

from abc import abstractmethod
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_serp_keyword_research.data.models.database import Recommendation
from ai_serp_keyword_research.data.repositories.base import BaseRepository, SQLAlchemyRepository


class RecommendationsRepository(BaseRepository[Recommendation]):
    """
    Interface for accessing Recommendation records.
    
    Extends the BaseRepository interface with Recommendation-specific
    operations.
    """
    
    @abstractmethod
    async def list_by_analysis_id(self, analysis_id: str) -> List[Recommendation]:
        """
        Get all recommendations for a specific search analysis.
        
        Args:
            analysis_id: str - The ID of the search analysis
            
        Returns:
            List[Recommendation]: List of recommendations for the analysis
        """
        pass
    
    @abstractmethod
    async def list_by_tactic_type(self, tactic_type: str) -> List[Recommendation]:
        """
        Get all recommendations of a specific tactic type.
        
        Args:
            tactic_type: str - The type of tactic to filter by
            
        Returns:
            List[Recommendation]: List of matching recommendations
        """
        pass
    
    @abstractmethod
    async def list_high_priority(self, max_priority: int = 2) -> List[Recommendation]:
        """
        Get all high-priority recommendations.
        
        Args:
            max_priority: int - Maximum priority value to include (lower is higher priority)
            
        Returns:
            List[Recommendation]: List of high-priority recommendations
        """
        pass
    
    @abstractmethod
    async def list_high_confidence(self, min_confidence: float = 0.8) -> List[Recommendation]:
        """
        Get all high-confidence recommendations.
        
        Args:
            min_confidence: float - Minimum confidence value to include
            
        Returns:
            List[Recommendation]: List of high-confidence recommendations
        """
        pass
    
    @abstractmethod
    async def delete_by_analysis_id(self, analysis_id: str) -> bool:
        """
        Delete all recommendations for a specific search analysis.
        
        Args:
            analysis_id: str - The ID of the search analysis
            
        Returns:
            bool: True if any records were deleted, False otherwise
        """
        pass


class SQLRecommendationsRepository(SQLAlchemyRepository[Recommendation], RecommendationsRepository):
    """
    SQLAlchemy implementation of the RecommendationsRepository.
    
    Provides concrete implementations of the RecommendationsRepository
    interface using SQLAlchemy.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            session: AsyncSession - SQLAlchemy async session
        """
        super().__init__(session, Recommendation)
    
    async def list_by_analysis_id(self, analysis_id: str) -> List[Recommendation]:
        """
        Get all recommendations for a specific search analysis.
        
        Args:
            analysis_id: str - The ID of the search analysis
            
        Returns:
            List[Recommendation]: List of recommendations for the analysis
        """
        query = select(self._model_class).where(self._model_class.analysis_id == analysis_id)
        result = await self._session.execute(query)
        return result.scalars().all()
    
    async def list_by_tactic_type(self, tactic_type: str) -> List[Recommendation]:
        """
        Get all recommendations of a specific tactic type.
        
        Args:
            tactic_type: str - The type of tactic to filter by
            
        Returns:
            List[Recommendation]: List of matching recommendations
        """
        query = select(self._model_class).where(self._model_class.tactic_type == tactic_type)
        result = await self._session.execute(query)
        return result.scalars().all()
    
    async def list_high_priority(self, max_priority: int = 2) -> List[Recommendation]:
        """
        Get all high-priority recommendations.
        
        Args:
            max_priority: int - Maximum priority value to include (lower is higher priority)
            
        Returns:
            List[Recommendation]: List of high-priority recommendations
        """
        query = select(self._model_class).where(self._model_class.priority <= max_priority)
        result = await self._session.execute(query)
        return result.scalars().all()
    
    async def list_high_confidence(self, min_confidence: float = 0.8) -> List[Recommendation]:
        """
        Get all high-confidence recommendations.
        
        Args:
            min_confidence: float - Minimum confidence value to include
            
        Returns:
            List[Recommendation]: List of high-confidence recommendations
        """
        query = select(self._model_class).where(self._model_class.confidence >= min_confidence)
        result = await self._session.execute(query)
        return result.scalars().all()
    
    async def delete_by_analysis_id(self, analysis_id: str) -> bool:
        """
        Delete all recommendations for a specific search analysis.
        
        Args:
            analysis_id: str - The ID of the search analysis
            
        Returns:
            bool: True if any records were deleted, False otherwise
        """
        query = select(self._model_class).where(self._model_class.analysis_id == analysis_id)
        result = await self._session.execute(query)
        recommendations = result.scalars().all()
        
        if not recommendations:
            return False
        
        for recommendation in recommendations:
            await self._session.delete(recommendation)
        
        await self._session.flush()
        return True 