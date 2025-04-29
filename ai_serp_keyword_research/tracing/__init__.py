"""
Tracing module for the application.

This module provides tracing configuration and utilities for the application.
It integrates with the OpenAI Agents SDK tracing functionality.
"""

import os
import logging
from contextlib import contextmanager
from typing import Dict, Any, Optional, List
from enum import Enum, auto

from agents import (
    trace as agents_trace,
    add_trace_processor,
    configure_tracing as agents_configure_tracing,
    TraceProcessor
)

# Set up logging
logger = logging.getLogger("serp_keyword_tracing")

# Trace sampling enum for configuration
class TraceSamplingRate(Enum):
    ALWAYS = auto()  # Sample all traces
    OFTEN = auto()   # Sample 50% of traces
    RARELY = auto()  # Sample 10% of traces
    NEVER = auto()   # Sample no traces

# Mapping of sampling rates to actual values
SAMPLING_RATE_MAP = {
    TraceSamplingRate.ALWAYS: 1.0,
    TraceSamplingRate.OFTEN: 0.5,
    TraceSamplingRate.RARELY: 0.1,
    TraceSamplingRate.NEVER: 0.0
}

# Default environment-specific configurations
DEFAULT_SAMPLE_RATES = {
    "development": TraceSamplingRate.ALWAYS,
    "staging": TraceSamplingRate.OFTEN,
    "production": TraceSamplingRate.RARELY
}

def configure_tracing(
    service_name: str = "serp-keyword-analyzer",
    environment: Optional[str] = None,
    sample_rate: Optional[float] = None,
    include_sensitive_data: bool = False,
    processors: Optional[List[TraceProcessor]] = None,
):
    """
    Configure tracing for the application.
    
    Args:
        service_name: The name of the service for tracing
        environment: The environment (development, staging, production)
        sample_rate: The sample rate for traces (0.0 to 1.0)
        include_sensitive_data: Whether to include sensitive data in traces
        processors: List of custom trace processors to register
    """
    # Determine environment from env var if not provided
    if environment is None:
        environment = os.getenv("APP_ENVIRONMENT", "development")
    
    # Determine sample rate based on environment if not provided
    if sample_rate is None:
        env_sample_rate = DEFAULT_SAMPLE_RATES.get(
            environment, TraceSamplingRate.ALWAYS
        )
        sample_rate = SAMPLING_RATE_MAP[env_sample_rate]
    
    # Configure OpenAI Agents SDK tracing
    agents_configure_tracing(
        service_name=service_name,
        sample_rate=sample_rate,
        trace_include_sensitive_data=include_sensitive_data,
    )
    
    # Register custom trace processors if provided
    if processors:
        for processor in processors:
            add_trace_processor(processor)
    
    logger.info(
        f"Tracing configured for service '{service_name}' in '{environment}' "
        f"with sample rate {sample_rate}"
    )

@contextmanager
def trace(name: str, attributes: Optional[Dict[str, Any]] = None):
    """
    Create a trace for a workflow or operation.
    
    This is a wrapper around the OpenAI Agents SDK trace context manager
    that provides additional logging and error handling.
    
    Args:
        name: The name of the trace
        attributes: Additional attributes to add to the trace
    """
    attributes = attributes or {}
    logger.debug(f"Starting trace: {name}")
    
    try:
        with agents_trace(name, attributes) as trace_context:
            yield trace_context
    except Exception as e:
        logger.error(f"Error in trace '{name}': {str(e)}")
        raise
    finally:
        logger.debug(f"Completed trace: {name}")

def initialize_tracing():
    """
    Initialize tracing with default configuration and processors.
    
    This is a convenience function to set up tracing with standard
    processors for the application.
    """
    from ai_serp_keyword_research.tracing.processors import (
        get_default_processors
    )
    
    environment = os.getenv("APP_ENVIRONMENT", "development")
    service_name = os.getenv("SERVICE_NAME", "serp-keyword-analyzer")
    
    configure_tracing(
        service_name=service_name,
        environment=environment,
        processors=get_default_processors()
    )
    
    logger.info(f"Tracing initialized for {service_name} in {environment}")
