"""
Base agent abstract class for the AI SERP Keyword Research Agent.

This module defines the abstract base class for all agent implementations,
providing common functionality and interface requirements.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set, Type

from agents import Agent, function_tool, KnowledgeSource, Runner, RunConfig, RunResult
from pydantic import BaseModel


class BaseAgent(ABC):
    """
    Abstract base class for all agent implementations.
    
    This class provides a consistent interface and common functionality
    for specialized agents in the SERP keyword research system.
    """
    
    def __init__(self, name: str, description: str, output_type: Optional[Type[BaseModel]] = None):
        """
        Initialize the base agent.
        
        Args:
            name: Name of the agent.
            description: Short description of the agent's purpose.
            output_type: Optional Pydantic model for structured output.
        """
        self.name = name
        self.description = description
        self.output_type = output_type
        self._agent = None
        self._tools: List[function_tool] = []
        self._knowledge_sources: List[KnowledgeSource] = []
    
    @property
    def agent(self) -> Agent:
        """
        Get the underlying OpenAI Agents SDK Agent instance.
        
        Returns:
            The configured Agent instance.
        """
        if self._agent is None:
            self._initialize_agent()
        return self._agent
    
    @abstractmethod
    def _initialize_agent(self) -> None:
        """
        Initialize the agent with appropriate tools, instructions, and configuration.
        This method should be implemented by each specialized agent class.
        """
        pass
    
    def add_tool(self, tool: function_tool) -> None:
        """
        Add a function tool to this agent.
        
        Args:
            tool: The function tool to add.
        """
        self._tools.append(tool)
    
    def add_knowledge_source(self, knowledge_source: KnowledgeSource) -> None:
        """
        Add a knowledge source to this agent.
        
        Args:
            knowledge_source: The knowledge source to add.
        """
        self._knowledge_sources.append(knowledge_source)
    
    @property
    @abstractmethod
    def instructions(self) -> str:
        """
        Get the detailed instructions for this agent.
        
        Returns:
            A string containing detailed instructions.
        """
        pass
    
    async def run(self, input_data: Any, **kwargs) -> RunResult:
        """
        Run the agent with the provided input data.
        
        Args:
            input_data: The input data for the agent.
            **kwargs: Additional arguments to pass to Runner.run.
            
        Returns:
            The result of the agent run.
        """
        # Default configuration
        default_config = RunConfig(
            max_turns=10,
            timeout_seconds=60
        )
        
        # Override with provided config if any
        config = kwargs.get('config', default_config)
        context = kwargs.get('context', None)
        
        # Run the agent
        try:
            result = await Runner.run(
                self.agent,
                input_data,
                config=config,
                context=context
            )
            
            # Convert to output type if specified
            if self.output_type is not None:
                result.final_output_as(self.output_type)
                
            return result
        except Exception as e:
            # Handle exceptions appropriately
            raise RuntimeError(f"Error running agent {self.name}: {str(e)}") 