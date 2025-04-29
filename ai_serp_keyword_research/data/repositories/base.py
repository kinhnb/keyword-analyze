"""
Base repository interface for data access.

This module defines the base repository interface that all concrete
repository implementations should follow.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_serp_keyword_research.data.models.database import Base

# Type variable for the model class
T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T], ABC):
    """
    Base repository interface with common CRUD operations.
    
    All repository implementations should inherit from this class
    and implement the abstract methods.
    
    Generic type T should be a SQLAlchemy model class.
    """
    
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        """
        Initialize the repository with a database session and model class.
        
        Args:
            session: AsyncSession - SQLAlchemy async session
            model_class: Type[T] - SQLAlchemy model class
        """
        self._session = session
        self._model_class = model_class
    
    @abstractmethod
    async def create(self, **kwargs) -> T:
        """
        Create a new record in the database.
        
        Args:
            **kwargs: Model field values
            
        Returns:
            T: Created model instance
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """
        Get a record by its ID.
        
        Args:
            id: str - Record ID
            
        Returns:
            Optional[T]: Found model instance or None
        """
        pass
    
    @abstractmethod
    async def list_all(self) -> List[T]:
        """
        Get all records.
        
        Returns:
            List[T]: List of model instances
        """
        pass
    
    @abstractmethod
    async def update(self, id: str, **kwargs) -> Optional[T]:
        """
        Update a record by its ID.
        
        Args:
            id: str - Record ID
            **kwargs: Model field values to update
            
        Returns:
            Optional[T]: Updated model instance or None
        """
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """
        Delete a record by its ID.
        
        Args:
            id: str - Record ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        pass


class SQLAlchemyRepository(BaseRepository[T]):
    """
    SQLAlchemy implementation of the base repository.
    
    This class provides a concrete implementation of the BaseRepository
    interface using SQLAlchemy for database operations.
    """
    
    async def create(self, **kwargs) -> T:
        """
        Create a new record in the database.
        
        Args:
            **kwargs: Model field values
            
        Returns:
            T: Created model instance
        """
        instance = self._model_class(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        # Refresh to get any database-generated values
        await self._session.refresh(instance)
        return instance
    
    async def get_by_id(self, id: str) -> Optional[T]:
        """
        Get a record by its ID.
        
        Args:
            id: str - Record ID
            
        Returns:
            Optional[T]: Found model instance or None
        """
        query = select(self._model_class).where(self._model_class.id == id)
        result = await self._session.execute(query)
        return result.scalars().first()
    
    async def list_all(self) -> List[T]:
        """
        Get all records.
        
        Returns:
            List[T]: List of model instances
        """
        query = select(self._model_class)
        result = await self._session.execute(query)
        return result.scalars().all()
    
    async def update(self, id: str, **kwargs) -> Optional[T]:
        """
        Update a record by its ID.
        
        Args:
            id: str - Record ID
            **kwargs: Model field values to update
            
        Returns:
            Optional[T]: Updated model instance or None
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        await self._session.flush()
        await self._session.refresh(instance)
        return instance
    
    async def delete(self, id: str) -> bool:
        """
        Delete a record by its ID.
        
        Args:
            id: str - Record ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return False
        
        await self._session.delete(instance)
        await self._session.flush()
        return True 