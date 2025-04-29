"""
Intent Analyzer Agent implementation for the AI SERP Keyword Research Agent.

This module implements the Intent Analyzer Agent, which specializes in
analyzing SERP data to determine search intent and extract relevant keywords.
"""

from typing import Dict, Any, List, Optional

from agents import Agent
from pydantic import BaseModel

from ai_serp_keyword_research.agents.base import BaseAgent
from ai_serp_keyword_research.tools import (
    analyze_keywords,
    classify_intent,
    detect_serp_patterns
)
from ai_serp_keyword_research.core.models.analysis import IntentAnalysis


class IntentAnalyzerAgent(BaseAgent):
    """
    Intent Analyzer Agent implementation.
    
    This agent specializes in analyzing SERP data to determine search intent
    and extract relevant primary and secondary keywords.
    """
    
    def __init__(self):
        """Initialize the Intent Analyzer Agent."""
        super().__init__(
            name="Intent Analyzer Agent",
            description="Analyzes SERP data to determine search intent and extract keywords",
            output_type=IntentAnalysis
        )
        
    def _initialize_agent(self) -> None:
        """Initialize the agent with tools and configuration."""
        # Add tools specific to the Intent Analyzer Agent
        self.add_tool(analyze_keywords)
        self.add_tool(classify_intent)
        self.add_tool(detect_serp_patterns)
        
        # Create the agent
        self._agent = Agent(
            name=self.name,
            handoff_description="Expert in analyzing search intent and extracting keywords",
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
You are an Intent Analyzer specializing in POD graphic tee search patterns.
Your task is to analyze SERP data to determine search intent and extract keywords.

Follow these steps for your analysis:
1. Review the complete SERP data (titles, descriptions, URLs)
2. Identify patterns in the top 3 results (prioritize these heavily)
3. Use the analyze_keywords tool to extract the main keyword and secondary keywords
4. Use the classify_intent tool to determine the intent type and confidence
5. Use the detect_serp_patterns tool to identify common patterns and themes
6. Classify the intent as one of the following:
   - Transactional: User is looking to purchase (product results dominate)
   - Informational: User is seeking information (blog posts, guides dominate)
   - Navigational: User is looking for a specific site/brand
   - Exploratory: User is browsing for ideas (collection pages dominate)
7. Look for specific POD indicators (terms like "shirt", "tee", "gift")
8. Analyze SERP features to support your intent classification
9. Return a structured analysis with your findings

Important signals to watch for:
- Shopping ads indicate strong transactional intent
- Featured snippets suggest informational intent
- Image packs for apparel suggest visual shopping intent
- "People also ask" boxes indicate informational needs
- E-commerce domains in top results suggest transactional intent
- Content sites in top results suggest informational intent
- Many similar products indicate high competition in transactional space
- Diverse content indicates informational or exploratory intent
""" 