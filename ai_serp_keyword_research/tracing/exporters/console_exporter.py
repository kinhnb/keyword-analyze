"""
Console trace exporter for the application.

This exporter outputs trace data to the console in a readable format.
"""

import json
import sys
from typing import Any, Dict, Optional

from agents import TraceProcessor, Trace, Span


class ConsoleTraceExporter(TraceProcessor):
    """
    Trace processor that exports trace data to the console.
    
    This exporter formats trace data in a readable format and prints it
    to the console, making it useful for development and debugging.
    """
    
    def __init__(
        self,
        indent: int = 2,
        include_metadata: bool = True,
        output_stream = sys.stdout,
        use_colors: bool = True,
    ):
        """
        Initialize the console trace exporter.
        
        Args:
            indent: Number of spaces to use for indentation
            include_metadata: Whether to include metadata in the output
            output_stream: The stream to write to (default: stdout)
            use_colors: Whether to use colors in the output
        """
        self.indent = indent
        self.include_metadata = include_metadata
        self.output_stream = output_stream
        self.use_colors = use_colors
        
        # ANSI color codes
        self.colors = {
            "reset": "\033[0m",
            "bold": "\033[1m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
        } if use_colors else {k: "" for k in ["reset", "bold", "green", "yellow", "blue", "magenta", "cyan", "white"]}
    
    def _format_metadata(self, metadata: Optional[Dict[str, Any]]) -> str:
        """Format metadata as a JSON string."""
        if not metadata:
            return "{}"
        
        try:
            return json.dumps(metadata, sort_keys=True, indent=self.indent, default=str)
        except (TypeError, ValueError):
            # Fall back to simple string representation if JSON serialization fails
            return str(metadata)
    
    def _write(self, text: str) -> None:
        """Write text to the output stream."""
        self.output_stream.write(text + "\n")
        self.output_stream.flush()
    
    def process_trace(self, trace: Trace) -> None:
        """
        Process a completed trace and export it to the console.
        
        Args:
            trace: The completed trace
        """
        c = self.colors
        
        # Write trace header
        self._write(
            f"{c['bold']}{c['green']}┌─ Trace: {trace.workflow_name} "
            f"(id: {trace.trace_id}){c['reset']}"
        )
        self._write(
            f"{c['green']}│  Duration: {trace.duration_ms:.2f}ms{c['reset']}"
        )
        
        # Write metadata if present and configured
        if self.include_metadata and trace.metadata:
            self._write(
                f"{c['green']}│  Metadata: {c['reset']}"
                f"{self._format_metadata(trace.metadata)}"
            )
        
        # Write spans
        if trace.spans:
            for i, span in enumerate(trace.spans):
                is_last = i == len(trace.spans) - 1
                self._write(
                    f"{c['green']}│{c['reset']}"
                )
                
                # Branch character depends on whether this is the last span
                branch = "└─" if is_last else "├─"
                
                self._write(
                    f"{c['green']}│  {branch} {c['cyan']}Span: {span.name} "
                    f"(duration: {span.duration_ms:.2f}ms){c['reset']}"
                )
                
                # Indentation for span content
                indent_prefix = "   " if is_last else "│  "
                
                # Write span metadata if present and configured
                if self.include_metadata and span.metadata:
                    self._write(
                        f"{c['green']}│  {indent_prefix}{c['cyan']}Metadata: {c['reset']}"
                        f"{self._format_metadata(span.metadata)}"
                    )
                
                # Write events
                if span.events:
                    for j, event in enumerate(span.events):
                        event_is_last = j == len(span.events) - 1
                        event_branch = "└─" if event_is_last else "├─"
                        event_indent = "   " if event_is_last else "│  "
                        
                        self._write(
                            f"{c['green']}│  {indent_prefix}{event_branch} "
                            f"{c['magenta']}Event: {event.name} "
                            f"(at {event.time_offset_ms:.2f}ms){c['reset']}"
                        )
                        
                        # Write event attributes if present and configured
                        if self.include_metadata and event.attributes:
                            self._write(
                                f"{c['green']}│  {indent_prefix}{event_indent} "
                                f"{c['magenta']}Attributes: {c['reset']}"
                                f"{self._format_metadata(event.attributes)}"
                            )
        
        # Write trace footer
        self._write(f"{c['green']}└──────────────────────────────────────{c['reset']}")
    
    def process_span(self, span: Span) -> None:
        """
        Process a span (not part of a complete trace).
        
        For the console exporter, we don't export individual spans,
        only complete traces with their contained spans.
        
        Args:
            span: The span
        """
        # Not implemented - we only export complete traces 