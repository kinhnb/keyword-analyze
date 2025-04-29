"""
File trace exporter for the application.

This exporter saves trace data to a file in JSON format for later analysis.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional, List, TextIO, Union

from agents import TraceProcessor, Trace, Span


class FileTraceExporter(TraceProcessor):
    """
    Trace processor that exports trace data to a file.
    
    This exporter saves trace data to a JSON file, either as individual
    files per trace or in a combined log file format, for later analysis.
    """
    
    def __init__(
        self,
        export_dir: str = "./traces",
        file_prefix: str = "trace",
        mode: str = "combined",  # "combined" or "individual"
        max_file_size_mb: int = 100,
        max_files: int = 5,
        include_spans: bool = True,
        include_events: bool = True,
    ):
        """
        Initialize the file trace exporter.
        
        Args:
            export_dir: Directory to save trace files to
            file_prefix: Prefix for trace files
            mode: Export mode ("combined" or "individual")
            max_file_size_mb: Maximum size of the log file before rotation (for combined mode)
            max_files: Maximum number of rotated log files to keep (for combined mode)
            include_spans: Whether to include spans in the exported traces
            include_events: Whether to include events in the exported spans
        """
        self.export_dir = export_dir
        self.file_prefix = file_prefix
        self.mode = mode
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.max_files = max_files
        self.include_spans = include_spans
        self.include_events = include_events
        
        # Create trace directory if it doesn't exist
        os.makedirs(self.export_dir, exist_ok=True)
        
        # Combined log file handle (only used in combined mode)
        self.log_file: Optional[TextIO] = None
        self.log_file_path: Optional[str] = None
        self.current_file_size: int = 0
        
        # Set up logger
        self.logger = logging.getLogger("trace_file_exporter")
        
        # Initialize log file if in combined mode
        if self.mode == "combined":
            self._initialize_log_file()
    
    def _initialize_log_file(self) -> None:
        """Initialize the combined log file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_path = os.path.join(
            self.export_dir, f"{self.file_prefix}_{timestamp}.jsonl"
        )
        
        try:
            self.log_file = open(self.log_file_path, "a", encoding="utf-8")
            self.current_file_size = os.path.getsize(self.log_file_path) if os.path.exists(self.log_file_path) else 0
            self.logger.info(f"Initialized trace log file: {self.log_file_path}")
        except Exception as e:
            self.logger.error(f"Error initializing trace log file: {str(e)}")
            self.log_file = None
    
    def _check_log_file_rotation(self) -> None:
        """Check if the log file needs to be rotated based on size."""
        if (
            self.log_file is not None
            and self.log_file_path is not None
            and self.current_file_size >= self.max_file_size_bytes
        ):
            # Close the current file
            self.log_file.close()
            
            # Rotate existing files if needed
            self._rotate_log_files()
            
            # Create a new file
            self._initialize_log_file()
    
    def _rotate_log_files(self) -> None:
        """Rotate log files, keeping only the most recent max_files."""
        try:
            # Get all log files in the export directory with the specified prefix
            files = [
                os.path.join(self.export_dir, f)
                for f in os.listdir(self.export_dir)
                if f.startswith(self.file_prefix) and f.endswith(".jsonl")
            ]
            
            # Sort by modification time (oldest first)
            files.sort(key=lambda f: os.path.getmtime(f))
            
            # Delete old files if we have more than max_files
            files_to_delete = files[:-self.max_files] if len(files) > self.max_files else []
            for file_path in files_to_delete:
                os.remove(file_path)
                self.logger.info(f"Rotated and removed old trace log file: {file_path}")
        
        except Exception as e:
            self.logger.error(f"Error rotating trace log files: {str(e)}")
    
    def _trace_to_dict(self, trace: Trace) -> Dict[str, Any]:
        """
        Convert a trace to a dictionary for JSON serialization.
        
        Args:
            trace: The trace to convert
            
        Returns:
            Dictionary representation of the trace
        """
        trace_dict = {
            "trace_id": trace.trace_id,
            "workflow_name": trace.workflow_name,
            "duration_ms": trace.duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": trace.metadata or {}
        }
        
        # Add spans if configured
        if self.include_spans and trace.spans:
            trace_dict["spans"] = [self._span_to_dict(span) for span in trace.spans]
        
        return trace_dict
    
    def _span_to_dict(self, span: Span) -> Dict[str, Any]:
        """
        Convert a span to a dictionary for JSON serialization.
        
        Args:
            span: The span to convert
            
        Returns:
            Dictionary representation of the span
        """
        span_dict = {
            "name": span.name,
            "duration_ms": span.duration_ms,
            "metadata": span.metadata or {}
        }
        
        # Add events if configured
        if self.include_events and span.events:
            span_dict["events"] = [
                {
                    "name": event.name,
                    "time_offset_ms": event.time_offset_ms,
                    "attributes": event.attributes or {}
                }
                for event in span.events
            ]
        
        return span_dict
    
    def process_trace(self, trace: Trace) -> None:
        """
        Process a completed trace and export it to a file.
        
        Args:
            trace: The completed trace
        """
        trace_dict = self._trace_to_dict(trace)
        
        try:
            if self.mode == "individual":
                # Save as individual file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                trace_id_short = trace.trace_id.split("-")[0] if trace.trace_id else "unknown"
                file_path = os.path.join(
                    self.export_dir,
                    f"{self.file_prefix}_{timestamp}_{trace_id_short}.json"
                )
                
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(trace_dict, f, indent=2, default=str)
                
                self.logger.debug(f"Exported trace to file: {file_path}")
            
            elif self.mode == "combined":
                # Check if we need to rotate the log file
                self._check_log_file_rotation()
                
                # Ensure log file is initialized
                if self.log_file is None:
                    self._initialize_log_file()
                
                if self.log_file is not None:
                    # Write the trace as a single line JSON
                    line = json.dumps(trace_dict, default=str) + "\n"
                    self.log_file.write(line)
                    self.log_file.flush()
                    
                    # Update current file size
                    self.current_file_size += len(line.encode("utf-8"))
                    
                    self.logger.debug(
                        f"Exported trace {trace.trace_id} to combined log file: {self.log_file_path}"
                    )
        
        except Exception as e:
            self.logger.error(f"Error exporting trace to file: {str(e)}")
    
    def process_span(self, span: Span) -> None:
        """
        Process a span (not part of a complete trace).
        
        For the file exporter, we don't export individual spans,
        only complete traces with their contained spans.
        
        Args:
            span: The span
        """
        # Not implemented - we only export complete traces
    
    def __del__(self) -> None:
        """Clean up resources when the exporter is destroyed."""
        if self.log_file is not None:
            try:
                self.log_file.close()
            except:
                pass 