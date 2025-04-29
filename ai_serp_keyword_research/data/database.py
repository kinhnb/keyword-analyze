"""
Database connection management for the AI SERP Keyword Research Agent.

This module provides database connection management with proper connection
pooling using SQLAlchemy's async functionality.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import QueuePool

from ai_serp_keyword_research.data.models.database import Base

# Get database URL from environment variables with a default for development
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:postgres@localhost:5432/serp_analysis"
)

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=bool(os.getenv("SQL_ECHO", "").lower() == "true"),
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Check connection validity before using from pool
)

# Create a session factory
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def create_database_tables():
    """
    Create all database tables defined in the models.
    
    This function creates all tables defined in the SQLAlchemy models
    if they don't already exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_database_tables():
    """
    Drop all database tables defined in the models.
    
    This function is primarily used for testing to clean up the database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session as an async context manager.
    
    Yields an async SQLAlchemy session and handles commit/rollback
    based on exceptions.
    
    Yields:
        AsyncSession: An async SQLAlchemy session.
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database dependency for FastAPI endpoints.
    
    This is a convenience function for use with FastAPI's dependency injection.
    
    Yields:
        AsyncSession: An async SQLAlchemy session.
    """
    async with get_db_session() as session:
        yield session 