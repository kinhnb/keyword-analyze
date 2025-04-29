"""
Tests for intent classification strategies.

This module tests the various strategies for intent classification
to ensure they correctly identify different search intents.
"""

import pytest
from typing import Dict, Any, List

from ai_serp_keyword_research.core.models.analysis import IntentType
from ai_serp_keyword_research.core.strategies import (
    TransactionalIntentStrategy,
    InformationalIntentStrategy,
    ExploratoryIntentStrategy,
    NavigationalIntentStrategy,
    IntentStrategyFactory,
    create_intent_strategy_factory
)


class TestIntentStrategies:
    """Tests for the intent classification strategies."""
    
    @pytest.fixture
    def mock_transactional_serp_data(self) -> Dict[str, Any]:
        """Create mock SERP data with transactional signals."""
        return {
            "search_term": "buy graphic tees",
            "organic_results": [
                {
                    "position": 1,
                    "title": "Buy Funny Graphic Tees Online - 20% Off Today",
                    "url": "https://www.example-shop.com/graphic-tees",
                    "domain": "example-shop.com",
                    "snippet": "Shop our collection of funny graphic tees. Free shipping on orders over $50. Sizes S-3XL available."
                },
                {
                    "position": 2,
                    "title": "Graphic T-Shirts - Amazon.com",
                    "url": "https://www.amazon.com/graphic-tshirts",
                    "domain": "amazon.com",
                    "snippet": "Results 1-48 of 100000+ results for graphic t-shirts. Price: $15.99. Free shipping available."
                },
                {
                    "position": 3,
                    "title": "Graphic Tees for Men and Women - Buy Online | Etsy",
                    "url": "https://www.etsy.com/c/clothing/mens-clothing/shirts-and-tees/t-shirts",
                    "domain": "etsy.com",
                    "snippet": "Shop for unique graphic tees on Etsy. Thousands of designs available. Support independent sellers."
                }
            ]
        }
    
    @pytest.fixture
    def mock_informational_serp_data(self) -> Dict[str, Any]:
        """Create mock SERP data with informational signals."""
        return {
            "search_term": "how to style graphic tees",
            "organic_results": [
                {
                    "position": 1,
                    "title": "10 Ways to Style Graphic Tees - Fashion Blog",
                    "url": "https://www.fashion-blog.com/how-to-style-graphic-tees",
                    "domain": "fashion-blog.com",
                    "snippet": "Learn how to style graphic tees for any occasion. From casual to dressy, these tips will help you create the perfect outfit."
                },
                {
                    "position": 2,
                    "title": "The Ultimate Guide to Styling Graphic T-Shirts - Style Tips",
                    "url": "https://www.styletips.com/guides/graphic-tshirts",
                    "domain": "styletips.com",
                    "snippet": "Our comprehensive guide to styling graphic tees. Learn what works and what doesn't with this essential wardrobe item."
                },
                {
                    "position": 3,
                    "title": "How to Wear Graphic Tees: A Complete Guide - Reddit",
                    "url": "https://www.reddit.com/r/fashion/comments/graphic-tees-guide",
                    "domain": "reddit.com",
                    "snippet": "Read community advice on how to style graphic tees for different body types and occasions. Tips and example outfits included."
                }
            ]
        }
    
    @pytest.fixture
    def mock_exploratory_serp_data(self) -> Dict[str, Any]:
        """Create mock SERP data with exploratory signals."""
        return {
            "search_term": "graphic tee ideas",
            "organic_results": [
                {
                    "position": 1,
                    "title": "50 Creative Graphic Tee Designs for Inspiration",
                    "url": "https://www.designinspiration.com/collection/graphic-tee-ideas",
                    "domain": "designinspiration.com",
                    "snippet": "Browse our curated collection of 50 innovative graphic tee designs. Perfect for finding your next favorite shirt or creative inspiration."
                },
                {
                    "position": 2,
                    "title": "Trending Graphic Tee Designs for 2023 - Style Gallery",
                    "url": "https://www.stylegallery.com/trending/graphic-tees-2023",
                    "domain": "stylegallery.com",
                    "snippet": "Discover this year's hottest graphic tee trends. From retro revival to modern minimalism, explore the latest designs."
                },
                {
                    "position": 3,
                    "title": "25 Unique Graphic Tee Ideas You'll Love - Pinterest",
                    "url": "https://www.pinterest.com/collection/unique-graphic-tees",
                    "domain": "pinterest.com",
                    "snippet": "Get inspired with these 25 unique graphic tee ideas. Save your favorites and discover new design trends."
                }
            ]
        }
    
    @pytest.fixture
    def mock_navigational_serp_data(self) -> Dict[str, Any]:
        """Create mock SERP data with navigational signals."""
        return {
            "search_term": "threadless official site",
            "organic_results": [
                {
                    "position": 1,
                    "title": "Threadless | Artist Shop | Homepage",
                    "url": "https://www.threadless.com/",
                    "domain": "threadless.com",
                    "snippet": "The official home of Threadless. Shop graphic t-shirts designed by artists. Discover new art and artists from our global community."
                },
                {
                    "position": 2,
                    "title": "Login - Threadless",
                    "url": "https://www.threadless.com/login",
                    "domain": "threadless.com",
                    "snippet": "Sign in to your Threadless account. Access your orders, designs, and artist shop."
                },
                {
                    "position": 3,
                    "title": "Threadless - About Us",
                    "url": "https://www.threadless.com/about",
                    "domain": "threadless.com",
                    "snippet": "Learn about Threadless, our mission, and how we support artists worldwide. Official information about our company."
                }
            ]
        }
    
    @pytest.fixture
    def mock_serp_features(self) -> List:
        """Create mock SERP features."""
        return []
    
    async def test_transactional_strategy(self, mock_transactional_serp_data, mock_serp_features):
        """Test the transactional intent strategy with transactional SERP data."""
        strategy = TransactionalIntentStrategy()
        result = await strategy.analyze(mock_transactional_serp_data, mock_serp_features)
        
        assert result["intent_type"] == IntentType.TRANSACTIONAL
        assert result["confidence"] > 0.7  # Should have high confidence
        assert len(result["signals"]) > 0  # Should detect multiple signals
        
        # Test that it detected e-commerce domains
        assert any("amazon" in signal for signal in result["signals"])
        assert any("etsy" in signal for signal in result["signals"])
    
    async def test_informational_strategy(self, mock_informational_serp_data, mock_serp_features):
        """Test the informational intent strategy with informational SERP data."""
        strategy = InformationalIntentStrategy()
        result = await strategy.analyze(mock_informational_serp_data, mock_serp_features)
        
        assert result["intent_type"] == IntentType.INFORMATIONAL
        assert result["confidence"] > 0.7  # Should have high confidence
        assert len(result["signals"]) > 0  # Should detect multiple signals
        
        # Test that it detected informational terms
        assert any("guide" in signal for signal in result["signals"])
        assert any("how to" in signal for signal in result["signals"])
    
    async def test_exploratory_strategy(self, mock_exploratory_serp_data, mock_serp_features):
        """Test the exploratory intent strategy with exploratory SERP data."""
        strategy = ExploratoryIntentStrategy()
        result = await strategy.analyze(mock_exploratory_serp_data, mock_serp_features)
        
        assert result["intent_type"] == IntentType.EXPLORATORY
        assert result["confidence"] > 0.7  # Should have high confidence
        assert len(result["signals"]) > 0  # Should detect multiple signals
        
        # Test that it detected exploratory terms
        assert any("ideas" in signal.lower() for signal in result["signals"])
        assert any("collection" in signal.lower() for signal in result["signals"])
    
    async def test_navigational_strategy(self, mock_navigational_serp_data, mock_serp_features):
        """Test the navigational intent strategy with navigational SERP data."""
        strategy = NavigationalIntentStrategy()
        result = await strategy.analyze(mock_navigational_serp_data, mock_serp_features)
        
        assert result["intent_type"] == IntentType.NAVIGATIONAL
        assert result["confidence"] > 0.7  # Should have high confidence
        assert len(result["signals"]) > 0  # Should detect multiple signals
        
        # Test that it detected navigational signals
        assert any("official" in signal.lower() for signal in result["signals"])
        assert any("domain" in signal.lower() for signal in result["signals"])
    
    async def test_factory_creation(self):
        """Test creating the intent strategy factory."""
        factory = create_intent_strategy_factory()
        
        # Verify all strategies are registered
        assert factory.get_strategy(IntentType.TRANSACTIONAL) is not None
        assert factory.get_strategy(IntentType.INFORMATIONAL) is not None
        assert factory.get_strategy(IntentType.EXPLORATORY) is not None
        assert factory.get_strategy(IntentType.NAVIGATIONAL) is not None
    
    async def test_factory_strategy_selection(self, mock_transactional_serp_data):
        """Test that the factory selects the appropriate strategy based on SERP data."""
        factory = create_intent_strategy_factory()
        
        # Transactional data should result in transactional strategy
        strategy = factory.create_strategy(mock_transactional_serp_data)
        assert strategy.intent_type == IntentType.TRANSACTIONAL 