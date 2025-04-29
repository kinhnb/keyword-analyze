"""
Repository module exports.

This module exports the repository interfaces and implementations.
"""

from ai_serp_keyword_research.data.repositories.base import BaseRepository, SQLAlchemyRepository
from ai_serp_keyword_research.data.repositories.search_analysis import (
    SearchAnalysisRepository,
    SQLSearchAnalysisRepository,
)
from ai_serp_keyword_research.data.repositories.serp_features import (
    SerpFeaturesRepository,
    SQLSerpFeaturesRepository,
)
from ai_serp_keyword_research.data.repositories.recommendations import (
    RecommendationsRepository,
    SQLRecommendationsRepository,
)

__all__ = [
    "BaseRepository",
    "SQLAlchemyRepository",
    "SearchAnalysisRepository",
    "SQLSearchAnalysisRepository",
    "SerpFeaturesRepository",
    "SQLSerpFeaturesRepository",
    "RecommendationsRepository",
    "SQLRecommendationsRepository",
]
