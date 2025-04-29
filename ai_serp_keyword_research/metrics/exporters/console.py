"""
Console metrics exporter.

This exporter prints metrics to the console for debugging purposes.
"""

import json
import time
from typing import Dict, Any

from ai_serp_keyword_research.metrics.exporters.base import MetricsExporter


class ConsoleExporter(MetricsExporter):
    """
    Exporter that prints metrics to the console.
    
    This is primarily used for development and debugging.
    """
    
    def __init__(self, pretty_print: bool = True):
        """
        Initialize the console exporter.
        
        Args:
            pretty_print: Whether to format the output with indentation
        """
        self.pretty_print = pretty_print
    
    def export(self, metrics: Dict[str, Any]) -> None:
        """
        Export metrics by printing them to the console.
        
        Args:
            metrics: Dictionary containing all metrics to export
        """
        print(f"\n=== Metrics Report at {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        
        # Format the metrics for display
        if self.pretty_print:
            print(json.dumps(metrics, indent=2))
        else:
            print(metrics)
        
        print("=" * 50)
    
    def close(self) -> None:
        """Close the exporter (no-op for console exporter)."""
        pass 