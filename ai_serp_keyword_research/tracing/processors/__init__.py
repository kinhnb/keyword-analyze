"""
Trace processors for the application.

This module provides trace processors for the OpenAI Agents SDK tracing system.
"""

from typing import List

from agents import TraceProcessor

from ai_serp_keyword_research.tracing.processors.logging_processor import LoggingTraceProcessor
from ai_serp_keyword_research.tracing.processors.metrics_processor import MetricsTraceProcessor
from ai_serp_keyword_research.tracing.processors.performance_processor import PerformanceTraceProcessor
from ai_serp_keyword_research.tracing.processors.metrics_integration_processor import MetricsIntegrationProcessor


def get_default_processors() -> List[TraceProcessor]:
    """
    Get the default trace processors for the application.
    
    Returns:
        List of default trace processors.
    """
    return [
        LoggingTraceProcessor(),
        MetricsTraceProcessor(),
        PerformanceTraceProcessor(),
        MetricsIntegrationProcessor(),
    ]
