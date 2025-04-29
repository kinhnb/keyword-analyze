"""
SQLAlchemy database models for the AI SERP Keyword Research Agent.

These models represent the database schema and are used by SQLAlchemy for ORM operations.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class SearchAnalysis(Base):
    """
    Model representing a search term analysis result.
    
    Stores the main analysis data for a search term, including the
    intent classification and confidence score.
    """
    __tablename__ = "search_analyses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    search_term = Column(String(255), nullable=False, unique=True)
    main_keyword = Column(String(255), nullable=False)
    secondary_keywords = Column(JSON, nullable=False)
    intent_type = Column(String(50), nullable=False)
    has_market_gap = Column(Boolean, default=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    serp_features = relationship("SerpFeature", back_populates="search_analysis", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="search_analysis", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SearchAnalysis(id={self.id}, search_term='{self.search_term}', intent_type='{self.intent_type}')>"


class SerpFeature(Base):
    """
    Model representing a SERP feature detected in search results.
    
    Stores information about special features in search results like
    shopping ads, featured snippets, etc.
    """
    __tablename__ = "serp_features"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("search_analyses.id"), nullable=False)
    feature_type = Column(String(50), nullable=False)
    feature_position = Column(Integer)
    feature_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    search_analysis = relationship("SearchAnalysis", back_populates="serp_features")
    
    def __repr__(self):
        return f"<SerpFeature(id={self.id}, type='{self.feature_type}', position={self.feature_position})>"


class Recommendation(Base):
    """
    Model representing an SEO recommendation.
    
    Stores tactical recommendations generated based on the search analysis,
    including priority and confidence scores.
    """
    __tablename__ = "recommendations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("search_analyses.id"), nullable=False)
    tactic_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    search_analysis = relationship("SearchAnalysis", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, type='{self.tactic_type}', priority={self.priority})>" 