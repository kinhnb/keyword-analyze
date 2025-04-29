"""
Base pipeline stage interface for the AI SERP Keyword Research Agent.

This module defines the base interface and abstract classes for pipeline stages
used in processing search terms for SERP analysis.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, TypeVar

# Define input and output type variables for generic typing
InputType = TypeVar('InputType')
OutputType = TypeVar('OutputType')


class PipelineStage(Generic[InputType, OutputType], ABC):
    """
    Abstract base class for pipeline stages.
    
    Each pipeline stage is responsible for a specific part of the SERP analysis
    process and follows a common interface for process execution.
    """
    
    @abstractmethod
    async def process(self, input_data: InputType) -> OutputType:
        """
        Process the input data and return the output.
        
        Args:
            input_data: The input data for this pipeline stage.
            
        Returns:
            The processed output data.
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the name of this pipeline stage.
        
        Returns:
            The stage name as a string.
        """
        pass


class PipelineContext:
    """
    Context object for sharing state between pipeline stages.
    
    This allows stages to access shared data and pass information
    that isn't part of the main pipeline data flow.
    """
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        
    def set(self, key: str, value: Any) -> None:
        """
        Store a value in the context.
        
        Args:
            key: The key to store the value under.
            value: The value to store.
        """
        self._data[key] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from the context.
        
        Args:
            key: The key to retrieve.
            default: The default value to return if key doesn't exist.
            
        Returns:
            The stored value or the default.
        """
        return self._data.get(key, default)
    
    def contains(self, key: str) -> bool:
        """
        Check if a key exists in the context.
        
        Args:
            key: The key to check.
            
        Returns:
            True if the key exists, False otherwise.
        """
        return key in self._data
        
    def remove(self, key: str) -> None:
        """
        Remove a key from the context.
        
        Args:
            key: The key to remove.
        """
        if key in self._data:
            del self._data[key] 