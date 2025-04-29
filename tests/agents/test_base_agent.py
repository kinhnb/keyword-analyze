"""
Unit tests for the BaseAgent abstract class.
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Any

from agents import Agent, function_tool, RunResult

from ai_serp_keyword_research.agents.base import BaseAgent


# Create a concrete implementation of BaseAgent for testing
class TestConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""
    
    def __init__(self):
        super().__init__(
            name="Test Agent",
            description="A test agent implementation",
            output_type=None
        )
    
    def _initialize_agent(self) -> None:
        """Initialize the agent with test configuration."""
        self._agent = Agent(
            name=self.name,
            instructions=self.instructions
        )
    
    @property
    def instructions(self) -> str:
        """Get the detailed instructions for this agent."""
        return "Test instructions for the agent."


class TestBaseAgent:
    """Tests for the BaseAgent abstract class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = TestConcreteAgent()
    
    def test_initialization(self):
        """Test that agent initializes with correct attributes."""
        assert self.agent.name == "Test Agent"
        assert self.agent.description == "A test agent implementation"
        assert self.agent.output_type is None
        assert self.agent._tools == []
        assert self.agent._knowledge_sources == []
    
    def test_add_tool(self):
        """Test adding a tool to the agent."""
        # Create a mock function tool
        mock_tool = MagicMock(spec=function_tool)
        
        # Add tool to agent
        self.agent.add_tool(mock_tool)
        
        # Verify tool was added
        assert mock_tool in self.agent._tools
        assert len(self.agent._tools) == 1
    
    def test_add_knowledge_source(self):
        """Test adding a knowledge source to the agent."""
        # Create a mock knowledge source
        mock_knowledge = MagicMock()
        
        # Add knowledge source to agent
        self.agent.add_knowledge_source(mock_knowledge)
        
        # Verify knowledge source was added
        assert mock_knowledge in self.agent._knowledge_sources
        assert len(self.agent._knowledge_sources) == 1
    
    def test_agent_property_initialization(self):
        """Test that agent property initializes the agent if not already initialized."""
        # Agent should not be initialized yet
        assert self.agent._agent is None
        
        # Accessing the property should initialize the agent
        agent_instance = self.agent.agent
        
        # Verify agent was initialized
        assert agent_instance is not None
        assert self.agent._agent is not None
        assert agent_instance.name == "Test Agent"
    
    @pytest.mark.asyncio
    @patch('ai_serp_keyword_research.agents.base.Runner')
    async def test_run_method(self, mock_runner):
        """Test the run method executes correctly."""
        # Create a mock run result
        mock_result = MagicMock(spec=RunResult)
        
        # Configure mock runner to return the mock result
        mock_runner.run = MagicMock()
        mock_runner.run.return_value = mock_result
        
        # Run the agent
        input_data = "Test input"
        result = await self.agent.run(input_data)
        
        # Verify runner was called correctly
        mock_runner.run.assert_called_once()
        assert result == mock_result
    
    @pytest.mark.asyncio
    @patch('ai_serp_keyword_research.agents.base.Runner')
    async def test_run_with_error(self, mock_runner):
        """Test error handling in the run method."""
        # Configure mock runner to raise an exception
        mock_runner.run = MagicMock()
        mock_runner.run.side_effect = Exception("Test error")
        
        # Run the agent and expect an exception
        with pytest.raises(RuntimeError) as excinfo:
            await self.agent.run("Test input")
        
        # Verify error message
        assert "Error running agent Test Agent" in str(excinfo.value)
        assert "Test error" in str(excinfo.value) 