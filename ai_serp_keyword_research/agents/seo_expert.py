"""
SEO Expert Agent implementation for the AI SERP Keyword Research Agent.

This module implements the SEO Expert Agent, which serves as the primary
orchestration agent for SERP analysis and coordinates with specialized agents.
"""

from typing import Dict, Any, List, Optional

from agents import Agent, RunContext
from pydantic import BaseModel

from ai_serp_keyword_research.agents.base import BaseAgent
from ai_serp_keyword_research.agents.intent_analyzer import IntentAnalyzerAgent
from ai_serp_keyword_research.agents.recommendation import RecommendationAgent
from ai_serp_keyword_research.tools import (
    fetch_serp_data,
    detect_market_gap,
    extract_serp_features
)
from ai_serp_keyword_research.core.models.results import AnalysisResult


class SEOExpertAgent(BaseAgent):
    """
    SEO Expert Agent implementation.
    
    This agent serves as the primary orchestrator for the SERP analysis process,
    coordinating with specialized agents for intent analysis and recommendation generation.
    """
    
    def __init__(self):
        """Initialize the SEO Expert Agent."""
        super().__init__(
            name="SEO Expert Agent",
            description="Orchestrates the SERP analysis process and coordinates with specialized agents",
            output_type=AnalysisResult
        )
        
        # Initialize specialized agents for handoffs
        self._intent_analyzer = IntentAnalyzerAgent()
        self._recommendation_agent = RecommendationAgent()
        
    def _initialize_agent(self) -> None:
        """Initialize the agent with tools and configuration."""
        # Add tools specific to the SEO Expert Agent
        self.add_tool(fetch_serp_data)
        self.add_tool(detect_market_gap)
        self.add_tool(extract_serp_features)
        
        # Create the agent with handoffs to specialized agents
        self._agent = Agent(
            name=self.name,
            instructions=self.instructions,
            tools=self._tools,
            knowledge=self._knowledge_sources,
            output_type=self.output_type,
            handoffs=[
                self._intent_analyzer.agent,
                self._recommendation_agent.agent
            ]
        )
    
    @property
    def instructions(self) -> str:
        """
        Get the detailed instructions for this agent.
        
        Returns:
            A string containing detailed instructions.
        """
        return """
You are an SEO expert specializing in Print on Demand (POD) graphic tees.
Your task is to analyze SERP data for a given search term to extract valuable SEO insights.

Follow these steps for each analysis:
1. Receive a search term from the user
2. Fetch SERP data using the fetch_serp_data tool
3. Hand off to the Intent Analyzer agent to determine search intent and extract keywords
4. Based on intent analysis, identify if there's a market gap opportunity using the detect_market_gap tool
5. Extract SERP features using the extract_serp_features tool
6. Hand off to the Recommendation agent to generate SEO tactics
7. Compile all insights into a comprehensive analysis
8. Ensure recommendations are specific to the POD graphic tees niche
9. Return the complete analysis with keywords, intent, market gaps, and recommendations

Important considerations:
- Always prioritize the top 3 results in your analysis
- Pay attention to SERP features (shopping ads, featured snippets, etc.)
- For transactional intent, focus on product page optimization
- For informational/exploratory intent, focus on collection page or content optimization
- Always provide specific, actionable recommendations
- For POD graphic tees niche, focus on designs, target audiences, and seasonal trends
""" 