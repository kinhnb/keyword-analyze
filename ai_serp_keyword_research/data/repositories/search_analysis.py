"""
SearchAnalysis repository for data access.

This module provides the interface and implementation for
accessing SearchAnalysis records in the database.
"""

from abc import abstractmethod
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_serp_keyword_research.data.models.database import SearchAnalysis
from ai_serp_keyword_research.data.repositories.base import BaseRepository, SQLAlchemyRepository


class SearchAnalysisRepository(BaseRepository[SearchAnalysis]):
    """
    Interface for accessing SearchAnalysis records.
    
    Extends the BaseRepository interface with SearchAnalysis-specific
    operations.
    """
    
    @abstractmethod
    async def get_by_search_term(self, search_term: str) -> Optional[SearchAnalysis]:
        """
        Get a search analysis by its search term.
        
        Args:
            search_term: str - The search term to look up
            
        Returns:
            Optional[SearchAnalysis]: Found record or None
        """
        pass
    
    @abstractmethod
    async def list_by_intent_type(self, intent_type: str) -> List[SearchAnalysis]:
        """
        Get all search analyses with a specific intent type.
        
        Args:
            intent_type: str - The intent type to filter by
            
        Returns:
            List[SearchAnalysis]: List of matching records
        """
        pass
    
    @abstractmethod
    async def list_market_gaps(self) -> List[SearchAnalysis]:
        """
        Get all search analyses that identified market gaps.
        
        Returns:
            List[SearchAnalysis]: List of records with market gaps
        """
        pass


class SQLSearchAnalysisRepository(SQLAlchemyRepository[SearchAnalysis], SearchAnalysisRepository):
    """
    SQLAlchemy implementation of the SearchAnalysisRepository.
    
    Provides concrete implementations of the SearchAnalysisRepository
    interface using SQLAlchemy.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            session: AsyncSession - SQLAlchemy async session
        """
        super().__init__(session, SearchAnalysis)
    
    async def get_by_search_term(self, search_term: str) -> Optional[SearchAnalysis]:
        """
        Get a search analysis by its search term.
        
        Args:
            search_term: str - The search term to look up
            
        Returns:
            Optional[SearchAnalysis]: Found record or None
        """
        query = select(self._model_class).where(self._model_class.search_term == search_term)
        result = await self._session.execute(query)
        return result.scalars().first()
    
    async def list_by_intent_type(self, intent_type: str) -> List[SearchAnalysis]:
        """
        Get all search analyses with a specific intent type.
        
        Args:
            intent_type: str - The intent type to filter by
            
        Returns:
            List[SearchAnalysis]: List of matching records
        """
        query = select(self._model_class).where(self._model_class.intent_type == intent_type)
        result = await self._session.execute(query)
        return result.scalars().all()
    
    async def list_market_gaps(self) -> List[SearchAnalysis]:
        """
        Get all search analyses that identified market gaps.
        
        Returns:
            List[SearchAnalysis]: List of records with market gaps
        """
        query = select(self._model_class).where(self._model_class.has_market_gap == True)
        result = await self._session.execute(query)
        return result.scalars().all() 