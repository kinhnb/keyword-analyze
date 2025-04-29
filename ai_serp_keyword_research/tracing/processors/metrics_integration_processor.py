"""
Metrics integration trace processor.

This processor integrates the OpenAI Agents SDK tracing with our metrics collection system.
"""

from agents import TraceProcessor, Trace

from ai_serp_keyword_research.agents.metrics import get_agent_metrics_collector


class MetricsIntegrationProcessor(TraceProcessor):
    """
    Trace processor that forwards trace data to our metrics collection system.
    
    This processor serves as a bridge between the OpenAI Agents SDK tracing
    system and our custom metrics collection infrastructure.
    """
    
    def __init__(self):
        """Initialize the metrics integration processor."""
        self.agent_metrics = get_agent_metrics_collector()
    
    def process_trace(self, trace: Trace) -> None:
        """
        Process a completed trace and forward metrics.
        
        Args:
            trace: The completed trace
        """
        # Forward the trace to our agent metrics collector
        self.agent_metrics.process_trace(trace) 