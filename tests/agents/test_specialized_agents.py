"""
Unit tests for the specialized agent implementations.

Tests the three specialized agents used in the SERP keyword research system:
- SEOExpertAgent (orchestrator)
- IntentAnalyzerAgent (intent analysis)
- RecommendationAgent (recommendation generation)
"""

import pytest
from unittest.mock import MagicMock, patch

from agents import Agent, KnowledgeSource

from ai_serp_keyword_research.agents import (
    SEOExpertAgent,
    IntentAnalyzerAgent,
    RecommendationAgent
)
from ai_serp_keyword_research.tools import (
    fetch_serp_data,
    analyze_keywords,
    classify_intent,
    detect_serp_patterns,
    detect_market_gap,
    extract_serp_features,
    generate_recommendations,
    prioritize_tactics,
    format_recommendations
)
from ai_serp_keyword_research.core.models.results import AnalysisResult
from ai_serp_keyword_research.core.models.analysis import IntentAnalysis
from ai_serp_keyword_research.core.models.recommendations import RecommendationSet


class TestSEOExpertAgent:
    """Tests for the SEO Expert Agent implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Patch the specialized agents to prevent their initialization
        with patch('ai_serp_keyword_research.agents.seo_expert.IntentAnalyzerAgent') as mock_intent_agent, \
             patch('ai_serp_keyword_research.agents.seo_expert.RecommendationAgent') as mock_rec_agent:
            # Configure mocks
            mock_intent_agent_instance = MagicMock()
            mock_intent_agent_instance.agent = MagicMock(spec=Agent)
            mock_intent_agent.return_value = mock_intent_agent_instance
            
            mock_rec_agent_instance = MagicMock()
            mock_rec_agent_instance.agent = MagicMock(spec=Agent)
            mock_rec_agent.return_value = mock_rec_agent_instance
            
            # Create agent
            self.agent = SEOExpertAgent()
    
    def test_initialization(self):
        """Test that agent initializes with correct attributes."""
        assert self.agent.name == "SEO Expert Agent"
        assert "orchestrates" in self.agent.description.lower()
        assert self.agent.output_type == AnalysisResult
    
    def test_tools_registration(self):
        """Test that the correct tools are registered with the agent."""
        # Initialize agent (which registers tools)
        agent_instance = self.agent.agent
        
        # Verify that the correct tools were registered
        registered_tools = self.agent._tools
        assert fetch_serp_data in registered_tools
        assert detect_market_gap in registered_tools
        assert extract_serp_features in registered_tools
    
    def test_instructions(self):
        """Test that instructions contain critical elements."""
        instructions = self.agent.instructions
        
        # Check for key steps and guidance
        assert "follow these steps" in instructions.lower()
        assert "serp data" in instructions.lower()
        assert "hand off to the intent analyzer" in instructions.lower()
        assert "hand off to the recommendation agent" in instructions.lower()
        assert "pod graphic tees" in instructions.lower()
        
        # Check for important considerations
        assert "prioritize the top 3 results" in instructions.lower()
        assert "serp features" in instructions.lower()
        assert "transactional intent" in instructions.lower()
        assert "informational/exploratory intent" in instructions.lower()


class TestIntentAnalyzerAgent:
    """Tests for the Intent Analyzer Agent implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = IntentAnalyzerAgent()
    
    def test_initialization(self):
        """Test that agent initializes with correct attributes."""
        assert self.agent.name == "Intent Analyzer Agent"
        assert "search intent" in self.agent.description.lower()
        assert self.agent.output_type == IntentAnalysis
    
    def test_tools_registration(self):
        """Test that the correct tools are registered with the agent."""
        # Initialize agent (which registers tools)
        agent_instance = self.agent.agent
        
        # Verify that the correct tools were registered
        registered_tools = self.agent._tools
        assert analyze_keywords in registered_tools
        assert classify_intent in registered_tools
        assert detect_serp_patterns in registered_tools
    
    def test_handoff_description(self):
        """Test that the handoff description is set correctly."""
        # Initialize agent
        agent_instance = self.agent.agent
        
        # Check handoff description
        assert hasattr(agent_instance, 'handoff_description')
        assert "expert" in agent_instance.handoff_description.lower()
        assert "intent" in agent_instance.handoff_description.lower()
        assert "keywords" in agent_instance.handoff_description.lower()
    
    def test_instructions(self):
        """Test that instructions contain critical elements."""
        instructions = self.agent.instructions
        
        # Check for key steps and concepts
        assert "follow these steps" in instructions.lower()
        assert "analyze_keywords tool" in instructions.lower()
        assert "classify_intent tool" in instructions.lower()
        assert "detect_serp_patterns tool" in instructions.lower()
        
        # Check for intent types
        assert "transactional" in instructions.lower()
        assert "informational" in instructions.lower()
        assert "navigational" in instructions.lower()
        assert "exploratory" in instructions.lower()
        
        # Check for signals
        assert "shopping ads" in instructions.lower()
        assert "featured snippets" in instructions.lower()


class TestRecommendationAgent:
    """Tests for the Recommendation Agent implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = RecommendationAgent()
    
    def test_initialization(self):
        """Test that agent initializes with correct attributes."""
        assert self.agent.name == "Recommendation Agent"
        assert "generates" in self.agent.description.lower()
        assert "recommendations" in self.agent.description.lower()
        assert self.agent.output_type == RecommendationSet
    
    def test_tools_registration(self):
        """Test that the correct tools are registered with the agent."""
        # Initialize agent (which registers tools)
        agent_instance = self.agent.agent
        
        # Verify that the correct tools were registered
        registered_tools = self.agent._tools
        assert generate_recommendations in registered_tools
        assert prioritize_tactics in registered_tools
        assert format_recommendations in registered_tools
    
    def test_handoff_description(self):
        """Test that the handoff description is set correctly."""
        # Initialize agent
        agent_instance = self.agent.agent
        
        # Check handoff description
        assert hasattr(agent_instance, 'handoff_description')
        assert "expert" in agent_instance.handoff_description.lower()
        assert "recommendations" in agent_instance.handoff_description.lower()
        assert "pod" in agent_instance.handoff_description.lower()
    
    def test_instructions(self):
        """Test that instructions contain critical elements."""
        instructions = self.agent.instructions
        
        # Check for key tools
        assert "generate_recommendations tool" in instructions.lower()
        assert "prioritize_tactics tool" in instructions.lower()
        assert "format_recommendations tool" in instructions.lower()
        
        # Check for intent-specific recommendations
        assert "transactional intent" in instructions.lower()
        assert "product page optimization" in instructions.lower()
        assert "informational/exploratory intent" in instructions.lower()
        assert "collection page or content tactics" in instructions.lower()
        
        # Check for market gap handling
        assert "market gaps are detected" in instructions.lower()
        
        # Check for quality requirements
        assert "specific to the pod graphic tee niche" in instructions.lower()
        assert "actionable" in instructions.lower()
        assert "prioritized" in instructions.lower()
        assert "confidence scores" in instructions.lower() 