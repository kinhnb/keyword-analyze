"""
Logging trace processor for the application.

This processor logs trace information using the Python logging module.
"""

import logging
import json
from typing import Any, Dict, Optional

from agents import TraceProcessor, Trace, Span


class LoggingTraceProcessor(TraceProcessor):
    """
    Trace processor that logs trace information to the application logs.
    
    This processor outputs trace events, durations, and metadata to the
    application logs at different log levels.
    """
    
    def __init__(
        self,
        logger_name: str = "serp_keyword_tracing",
        include_spans: bool = True,
        include_events: bool = True,
        trace_log_level: int = logging.INFO,
        span_log_level: int = logging.DEBUG,
        event_log_level: int = logging.DEBUG,
    ):
        """
        Initialize the logging trace processor.
        
        Args:
            logger_name: Name of the logger to use
            include_spans: Whether to log span information
            include_events: Whether to log event information
            trace_log_level: Log level for trace completion
            span_log_level: Log level for span details
            event_log_level: Log level for event details
        """
        self.logger = logging.getLogger(logger_name)
        self.include_spans = include_spans
        self.include_events = include_events
        self.trace_log_level = trace_log_level
        self.span_log_level = span_log_level
        self.event_log_level = event_log_level
    
    def _format_metadata(self, metadata: Optional[Dict[str, Any]]) -> str:
        """Format metadata as a JSON string."""
        if not metadata:
            return "{}"
        
        try:
            return json.dumps(metadata, sort_keys=True, default=str)
        except (TypeError, ValueError):
            # Fall back to simple string representation if JSON serialization fails
            return str(metadata)
    
    def process_trace(self, trace: Trace) -> None:
        """
        Process a completed trace.
        
        Logs the trace completion, duration, and any spans/events if configured.
        
        Args:
            trace: The completed trace
        """
        # Log the trace completion
        self.logger.log(
            self.trace_log_level,
            f"Trace completed: {trace.workflow_name} (id: {trace.trace_id}, "
            f"duration: {trace.duration_ms:.2f}ms)"
        )
        
        # Add metadata if present
        if trace.metadata:
            self.logger.log(
                self.trace_log_level,
                f"Trace metadata: {self._format_metadata(trace.metadata)}"
            )
        
        # Log spans if configured
        if self.include_spans and trace.spans:
            for span in trace.spans:
                self.process_span(span, is_part_of_trace=True)
    
    def process_span(self, span: Span, is_part_of_trace: bool = False) -> None:
        """
        Process a span.
        
        Logs the span details and any events if configured.
        
        Args:
            span: The span
            is_part_of_trace: Whether this span is being processed as part of a trace
        """
        # Prefix for spans that are part of a trace being processed
        prefix = "  └─ " if is_part_of_trace else ""
        
        # Log the span
        self.logger.log(
            self.span_log_level,
            f"{prefix}Span: {span.name} (duration: {span.duration_ms:.2f}ms)"
        )
        
        # Add metadata if present
        if span.metadata:
            self.logger.log(
                self.span_log_level,
                f"{prefix}  Span metadata: {self._format_metadata(span.metadata)}"
            )
        
        # Log events if configured
        if self.include_events and span.events:
            for event in span.events:
                event_prefix = f"{prefix}  └─ " if is_part_of_trace else "  └─ "
                self.logger.log(
                    self.event_log_level,
                    f"{event_prefix}Event: {event.name} "
                    f"(at {event.time_offset_ms:.2f}ms)"
                )
                
                # Add attributes if present
                if event.attributes:
                    self.logger.log(
                        self.event_log_level,
                        f"{event_prefix}  Event attributes: "
                        f"{self._format_metadata(event.attributes)}"
                    ) 