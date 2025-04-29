"""
Trace exporters for the application.

This module provides trace exporters for sending trace data to external systems.
"""

from typing import List, Type

from agents import TraceProcessor
from ai_serp_keyword_research.tracing.exporters.console_exporter import ConsoleTraceExporter
from ai_serp_keyword_research.tracing.exporters.file_exporter import FileTraceExporter


def get_exporters(export_to_console: bool = True, export_to_file: bool = False) -> List[TraceProcessor]:
    """
    Get the configured trace exporters.
    
    Args:
        export_to_console: Whether to export traces to the console
        export_to_file: Whether to export traces to a file
        
    Returns:
        List of configured trace exporters
    """
    exporters = []
    
    if export_to_console:
        exporters.append(ConsoleTraceExporter())
    
    if export_to_file:
        exporters.append(FileTraceExporter())
    
    return exporters
