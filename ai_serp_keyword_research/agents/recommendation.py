"""
Recommendation Agent implementation for the AI SERP Keyword Research Agent.

This module implements the Recommendation Agent, which specializes in
generating targeted SEO recommendations based on intent analysis and market gaps.
"""

from typing import Dict, Any, List, Optional

from agents import Agent
from pydantic import BaseModel

from ai_serp_keyword_research.agents.base import BaseAgent
from ai_serp_keyword_research.tools import (
    generate_recommendations,
    prioritize_tactics,
    format_recommendations
)
from ai_serp_keyword_research.core.models.recommendations import RecommendationSet


class RecommendationAgent(BaseAgent):
    """
    Recommendation Agent implementation.
    
    This agent specializes in generating targeted SEO recommendations
    based on search intent analysis and identified market gaps.
    """
    
    def __init__(self):
        """Initialize the Recommendation Agent."""
        super().__init__(
            name="Recommendation Agent",
            description="Generates SEO tactic recommendations based on intent analysis and market gaps",
            output_type=RecommendationSet
        )
        
    def _initialize_agent(self) -> None:
        """Initialize the agent with tools and configuration."""
        # Add tools specific to the Recommendation Agent
        self.add_tool(generate_recommendations)
        self.add_tool(prioritize_tactics)
        self.add_tool(format_recommendations)
        
        # Create the agent
        self._agent = Agent(
            name=self.name,
            handoff_description="Expert in generating SEO recommendations for POD graphic tees",
            instructions=self.instructions,
            tools=self._tools,
            knowledge=self._knowledge_sources,
            output_type=self.output_type
        )
    
    @property
    def instructions(self) -> str:
        """
        Get the detailed instructions for this agent.
        
        Returns:
            A string containing detailed instructions.
        """
        return """
You are a Recommendation Agent specializing in SEO tactics for POD graphic tees.
Your task is to generate targeted SEO recommendations based on SERP analysis.

Follow these steps to create your recommendations:
1. Review the intent analysis and market gap findings
2. Consider the specific POD graphic tee niche context
3. Use the generate_recommendations tool to create recommendations based on intent and market gaps
4. Use the prioritize_tactics tool to prioritize your recommendations
5. Use the format_recommendations tool to format the final recommendation set
6. For transactional intent:
   - Recommend product page optimization tactics
   - Suggest listing optimization for marketplaces
   - Provide advice on product title/description optimization
7. For informational/exploratory intent:
   - Recommend collection page or content tactics
   - Suggest blog posts, guides, or gift lists
   - Provide advice on category structure
8. When market gaps are detected:
   - Recommend specific ways to address the gap
   - Suggest content or product ideas that fill the gap
   - Prioritize these opportunities
9. Consider SERP features in your recommendations:
   - For featured snippets, recommend Q&A content
   - For shopping ads, suggest PPC strategies
   - For image packs, recommend visual optimization

Always ensure recommendations are:
- Specific to the POD graphic tee niche
- Actionable (with clear next steps)
- Prioritized by potential impact
- Assigned confidence scores
- Tailored to the exact search term analyzed
""" 