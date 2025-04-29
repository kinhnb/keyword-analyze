"""
SerpFeature repository for data access.

This module provides the interface and implementation for
accessing SerpFeature records in the database.
"""

from abc import abstractmethod
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_serp_keyword_research.data.models.database import SerpFeature
from ai_serp_keyword_research.data.repositories.base import BaseRepository, SQLAlchemyRepository


class SerpFeaturesRepository(BaseRepository[SerpFeature]):
    """
    Interface for accessing SerpFeature records.
    
    Extends the BaseRepository interface with SerpFeature-specific
    operations.
    """
    
    @abstractmethod
    async def list_by_analysis_id(self, analysis_id: str) -> List[SerpFeature]:
        """
        Get all SERP features for a specific search analysis.
        
        Args:
            analysis_id: str - The ID of the search analysis
            
        Returns:
            List[SerpFeature]: List of SERP features for the analysis
        """
        pass
    
    @abstractmethod
    async def list_by_feature_type(self, feature_type: str) -> List[SerpFeature]:
        """
        Get all SERP features of a specific type.
        
        Args:
            feature_type: str - The type of SERP feature to filter by
            
        Returns:
            List[SerpFeature]: List of matching SERP features
        """
        pass
    
    @abstractmethod
    async def list_by_analysis_and_type(self, analysis_id: str, feature_type: str) -> List[SerpFeature]:
        """
        Get all SERP features of a specific type for a specific search analysis.
        
        Args:
            analysis_id: str - The ID of the search analysis
            feature_type: str - The type of SERP feature to filter by
            
        Returns:
            List[SerpFeature]: List of matching SERP features
        """
        pass
    
    @abstractmethod
    async def delete_by_analysis_id(self, analysis_id: str) -> bool:
        """
        Delete all SERP features for a specific search analysis.
        
        Args:
            analysis_id: str - The ID of the search analysis
            
        Returns:
            bool: True if any records were deleted, False otherwise
        """
        pass


class SQLSerpFeaturesRepository(SQLAlchemyRepository[SerpFeature], SerpFeaturesRepository):
    """
    SQLAlchemy implementation of the SerpFeaturesRepository.
    
    Provides concrete implementations of the SerpFeaturesRepository
    interface using SQLAlchemy.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            session: AsyncSession - SQLAlchemy async session
        """
        super().__init__(session, SerpFeature)
    
    async def list_by_analysis_id(self, analysis_id: str) -> List[SerpFeature]:
        """
        Get all SERP features for a specific search analysis.
        
        Args:
            analysis_id: str - The ID of the search analysis
            
        Returns:
            List[SerpFeature]: List of SERP features for the analysis
        """
        query = select(self._model_class).where(self._model_class.analysis_id == analysis_id)
        result = await self._session.execute(query)
        return result.scalars().all()
    
    async def list_by_feature_type(self, feature_type: str) -> List[SerpFeature]:
        """
        Get all SERP features of a specific type.
        
        Args:
            feature_type: str - The type of SERP feature to filter by
            
        Returns:
            List[SerpFeature]: List of matching SERP features
        """
        query = select(self._model_class).where(self._model_class.feature_type == feature_type)
        result = await self._session.execute(query)
        return result.scalars().all()
    
    async def list_by_analysis_and_type(self, analysis_id: str, feature_type: str) -> List[SerpFeature]:
        """
        Get all SERP features of a specific type for a specific search analysis.
        
        Args:
            analysis_id: str - The ID of the search analysis
            feature_type: str - The type of SERP feature to filter by
            
        Returns:
            List[SerpFeature]: List of matching SERP features
        """
        query = select(self._model_class).where(
            self._model_class.analysis_id == analysis_id,
            self._model_class.feature_type == feature_type
        )
        result = await self._session.execute(query)
        return result.scalars().all()
    
    async def delete_by_analysis_id(self, analysis_id: str) -> bool:
        """
        Delete all SERP features for a specific search analysis.
        
        Args:
            analysis_id: str - The ID of the search analysis
            
        Returns:
            bool: True if any records were deleted, False otherwise
        """
        query = select(self._model_class).where(self._model_class.analysis_id == analysis_id)
        result = await self._session.execute(query)
        features = result.scalars().all()
        
        if not features:
            return False
        
        for feature in features:
            await self._session.delete(feature)
        
        await self._session.flush()
        return True 