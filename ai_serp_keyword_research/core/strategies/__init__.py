"""
Intent classification strategies for SERP analysis.

This package provides strategies for classifying search intent
based on SERP data analysis.
"""

from ai_serp_keyword_research.core.strategies.intent_strategy import (
    AbstractIntentStrategy,
    IntentStrategyFactory
)
from ai_serp_keyword_research.core.strategies.transactional_intent import TransactionalIntentStrategy
from ai_serp_keyword_research.core.strategies.informational_intent import InformationalIntentStrategy
from ai_serp_keyword_research.core.strategies.exploratory_intent import ExploratoryIntentStrategy
from ai_serp_keyword_research.core.strategies.navigational_intent import NavigationalIntentStrategy

__all__ = [
    'AbstractIntentStrategy',
    'IntentStrategyFactory',
    'TransactionalIntentStrategy',
    'InformationalIntentStrategy',
    'ExploratoryIntentStrategy',
    'NavigationalIntentStrategy',
    'create_intent_strategy_factory'
]


def create_intent_strategy_factory() -> IntentStrategyFactory:
    """
    Create and configure a strategy factory with all available intent strategies.
    
    Returns:
        IntentStrategyFactory with all strategies registered.
    """
    factory = IntentStrategyFactory()
    
    # Register all available strategies
    factory.register_strategy(TransactionalIntentStrategy())
    factory.register_strategy(InformationalIntentStrategy())
    factory.register_strategy(ExploratoryIntentStrategy())
    factory.register_strategy(NavigationalIntentStrategy())
    
    return factory
