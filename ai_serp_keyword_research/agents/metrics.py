"""
Agent metrics collection.

This module provides utilities for collecting metrics related to agent operations.
"""

import time
from typing import Dict, Optional, Any
from contextlib import asynccontextmanager
from agents import Trace, Span

from ai_serp_keyword_research.metrics.collector import get_metrics_collector


class AgentMetricsCollector:
    """
    Collects metrics related to agent operations.
    
    This class provides methods to record metrics about:
    - Agent runs (count, duration, tokens)
    - Tool calls (count, duration)
    - Handoffs (count, success rate)
    - Errors (count by type)
    
    It works in conjunction with the OpenAI Agents SDK tracing system.
    """
    
    def __init__(self):
        """Initialize the agent metrics collector."""
        self.metrics = get_metrics_collector()
    
    def process_trace(self, trace: Trace) -> None:
        """
        Process a completed trace and collect metrics.
        
        Args:
            trace: The completed trace
        """
        # Record workflow execution
        workflow_name = trace.workflow_name or "unknown"
        
        # Create tags
        tags = {"workflow": workflow_name}
        
        # Record trace count and duration
        self.metrics.increment_counter("agent_workflow_executions", tags=tags)
        self.metrics.record_histogram("agent_workflow_duration_ms", trace.duration_ms, tags=tags)
        
        # Check for errors
        if trace.metadata and "error" in trace.metadata:
            error_type = trace.metadata.get("error_type", "unknown")
            error_tags = {**tags, "error_type": error_type}
            self.metrics.increment_counter("agent_workflow_errors", tags=error_tags)
        
        # Process spans for specific metrics
        if trace.spans:
            for span in trace.spans:
                self._process_span(span, workflow_name)
    
    def _process_span(self, span: Span, workflow_name: str) -> None:
        """
        Process a span and collect metrics.
        
        Args:
            span: The span
            workflow_name: Name of the parent workflow
        """
        span_name = span.name
        span_type = "unknown"
        
        # Create base tags
        tags = {
            "workflow": workflow_name,
            "span_name": span_name
        }
        
        # Record span duration
        self.metrics.record_histogram("agent_span_duration_ms", span.duration_ms, tags=tags)
        
        # Handle different span types
        if span_name.startswith("agent_run:"):
            span_type = "agent_run"
            agent_name = span.metadata.get("agent_name", "unknown") if span.metadata else "unknown"
            tags["agent_name"] = agent_name
            
            # Record agent run
            self.metrics.increment_counter("agent_runs", tags=tags)
            
            # Record token usage if available
            if span.metadata:
                if "input_tokens" in span.metadata:
                    self.metrics.record_histogram(
                        "agent_input_tokens", 
                        span.metadata["input_tokens"],
                        tags=tags
                    )
                
                if "output_tokens" in span.metadata:
                    self.metrics.record_histogram(
                        "agent_output_tokens", 
                        span.metadata["output_tokens"],
                        tags=tags
                    )
                
                if "input_tokens" in span.metadata and "output_tokens" in span.metadata:
                    total_tokens = span.metadata["input_tokens"] + span.metadata["output_tokens"]
                    self.metrics.record_histogram("agent_total_tokens", total_tokens, tags=tags)
        
        elif span_name.startswith("tool_call:"):
            span_type = "tool_call"
            tool_name = span.metadata.get("tool_name", "unknown") if span.metadata else "unknown"
            tags["tool_name"] = tool_name
            
            # Record tool call
            self.metrics.increment_counter("agent_tool_calls", tags=tags)
            
            # Check for tool errors
            if span.metadata and "error" in span.metadata:
                error_type = span.metadata.get("error_type", "unknown")
                error_tags = {**tags, "error_type": error_type}
                self.metrics.increment_counter("agent_tool_errors", tags=error_tags)
        
        elif span_name.startswith("handoff:"):
            span_type = "handoff"
            target_agent = span.metadata.get("target_agent", "unknown") if span.metadata else "unknown"
            tags["target_agent"] = target_agent
            
            # Record handoff
            self.metrics.increment_counter("agent_handoffs", tags=tags)
            
            # Check for handoff success
            if span.metadata and "success" in span.metadata:
                success = span.metadata["success"]
                if success:
                    self.metrics.increment_counter("agent_handoff_successes", tags=tags)
                else:
                    self.metrics.increment_counter("agent_handoff_failures", tags=tags)
        
        # Add span type to tags for general span metrics
        tags["span_type"] = span_type
        self.metrics.increment_counter("agent_spans", tags=tags)
    
    @asynccontextmanager
    async def measure_agent_operation(self, operation: str, tags: Optional[Dict[str, str]] = None):
        """
        Context manager to measure the duration of an agent operation.
        
        Args:
            operation: Name of the operation
            tags: Additional tags to associate with this metric
            
        Example:
            async with agent_metrics.measure_agent_operation("keyword_extraction", 
                                                           {"source": "serp_data"}):
                # Perform keyword extraction
                keywords = await extract_keywords(serp_data)
        """
        all_tags = tags.copy() if tags else {}
        
        # Record operation start
        self.metrics.increment_counter(f"agent_operation_{operation}", tags=all_tags)
        
        start_time = time.time()
        try:
            yield
            # Record success
            self.metrics.increment_counter(f"agent_operation_{operation}_success", tags=all_tags)
        except Exception as e:
            # Record error
            error_type = type(e).__name__
            error_tags = {**all_tags, "error_type": error_type}
            self.metrics.increment_counter(f"agent_operation_{operation}_error", tags=error_tags)
            raise
        finally:
            # Record duration
            duration_ms = (time.time() - start_time) * 1000
            self.metrics.record_histogram(f"agent_operation_{operation}_duration_ms", 
                                        duration_ms, 
                                        tags=all_tags)


# Singleton instance
_agent_metrics_collector_instance = None


def get_agent_metrics_collector() -> AgentMetricsCollector:
    """
    Get the singleton agent metrics collector instance.
    
    Returns:
        The agent metrics collector instance
    """
    global _agent_metrics_collector_instance
    if _agent_metrics_collector_instance is None:
        _agent_metrics_collector_instance = AgentMetricsCollector()
    return _agent_metrics_collector_instance 