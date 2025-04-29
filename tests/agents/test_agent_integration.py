"""
Integration tests for the agent collaboration.

Tests the multi-agent workflow with handoffs between the main orchestrator
and specialized agents.
"""

import pytest
from unittest.mock import MagicMock, patch
import asyncio

from ai_serp_keyword_research.agents import SEOExpertAgent
from ai_serp_keyword_research.core.models.analysis import IntentType, IntentAnalysis
from ai_serp_keyword_research.core.models.recommendations import RecommendationSet, Recommendation, TacticType
from ai_serp_keyword_research.core.models.analysis import MarketGap, SerpFeature, SerpFeatureType


class TestAgentCollaboration:
    """Integration tests for agent collaboration."""
    
    @pytest.mark.asyncio
    @patch('ai_serp_keyword_research.tools.serp_tools.fetch_serp_data')
    @patch('ai_serp_keyword_research.agents.intent_analyzer.IntentAnalyzerAgent.run')
    @patch('ai_serp_keyword_research.agents.recommendation.RecommendationAgent.run')
    @patch('ai_serp_keyword_research.tools.market_tools.detect_market_gap')
    @patch('ai_serp_keyword_research.tools.feature_tools.extract_serp_features')
    async def test_agent_handoffs(self, mock_extract_features, mock_detect_gap, 
                                mock_rec_run, mock_intent_run, mock_fetch_serp):
        """Test the full agent collaboration workflow with handoffs."""
        # Mock the SERP data retrieval
        mock_serp_data = {
            "search_term": "dad graphic tee",
            "organic_results": [
                {"position": 1, "title": "Best Dad Graphic Tees", "url": "https://example.com/1"},
                {"position": 2, "title": "Funny Dad T-Shirts", "url": "https://example.com/2"},
                {"position": 3, "title": "Father's Day Gift Ideas", "url": "https://example.com/3"}
            ],
            "features": {
                "shopping_ads": True,
                "featured_snippet": False,
                "image_pack": True
            }
        }
        mock_fetch_serp.return_value = mock_serp_data
        
        # Mock the intent analysis results
        intent_result = MagicMock()
        intent_analysis = IntentAnalysis(
            intent_type=IntentType.TRANSACTIONAL,
            confidence=0.85,
            main_keyword={"text": "dad graphic tee", "relevance": 0.95, "frequency": 5},
            secondary_keywords=[
                {"text": "funny dad shirt", "relevance": 0.85, "frequency": 3},
                {"text": "father's day gift", "relevance": 0.75, "frequency": 2}
            ],
            signals=["shopping_ads", "product_pages", "pricing_terms"]
        )
        intent_result.final_output_as.return_value = intent_analysis
        mock_intent_run.return_value = intent_result
        
        # Mock the market gap detection
        market_gap = MarketGap(
            detected=True,
            description="Limited personalized dad graphic tees with profession themes",
            opportunity_score=0.75,
            competition_level=0.45,
            related_keywords=[
                {"text": "profession dad shirt", "relevance": 0.80},
                {"text": "occupation father tee", "relevance": 0.70}
            ]
        )
        mock_detect_gap.return_value = market_gap
        
        # Mock the SERP features extraction
        serp_features = {
            "features": [
                {"type": SerpFeatureType.SHOPPING_ADS, "position": 0},
                {"type": SerpFeatureType.IMAGE_PACK, "position": 3}
            ],
            "feature_count": 2,
            "has_shopping": True,
            "has_featured_snippet": False,
            "commercial_features": 1,
            "informational_features": 0
        }
        mock_extract_features.return_value = serp_features
        
        # Mock the recommendation results
        rec_result = MagicMock()
        recommendations = RecommendationSet(
            recommendations=[
                Recommendation(
                    tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                    description="Create product pages targeting 'profession + dad shirt' keywords",
                    priority=1,
                    confidence=0.85
                ),
                Recommendation(
                    tactic_type=TacticType.CONTENT_CREATION,
                    description="Develop gift guide content around 'best gifts for dads'",
                    priority=2,
                    confidence=0.78
                )
            ],
            intent_based=True,
            market_gap_based=True
        )
        rec_result.final_output_as.return_value = recommendations
        mock_rec_run.return_value = rec_result
        
        # Create the orchestrator agent
        agent = SEOExpertAgent()
        
        # Run the analysis
        search_term = "dad graphic tee"
        result = await agent.run(search_term)
        
        # Verify the flow
        mock_fetch_serp.assert_called_once()
        mock_intent_run.assert_called_once()
        mock_detect_gap.assert_called_once()
        mock_extract_features.assert_called_once()
        mock_rec_run.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('ai_serp_keyword_research.agents.seo_expert.SEOExpertAgent._initialize_agent')
    @patch('ai_serp_keyword_research.agents.intent_analyzer.IntentAnalyzerAgent._initialize_agent')
    @patch('ai_serp_keyword_research.agents.recommendation.RecommendationAgent._initialize_agent')
    async def test_agent_initialization(self, mock_rec_init, mock_intent_init, mock_seo_init):
        """Test that all agents are initialized correctly in the multi-agent system."""
        # Create the orchestrator agent which should initialize the other agents
        agent = SEOExpertAgent()
        
        # Access the agent property to trigger initialization
        _ = agent.agent
        
        # Verify all agents were initialized
        mock_seo_init.assert_called_once()
        
        # Verify that intent and recommendation agents in SEOExpertAgent were initialized
        assert agent._intent_analyzer is not None
        assert agent._recommendation_agent is not None 