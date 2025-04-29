"""
Logging metrics exporter.

This exporter sends metrics to the Python logging system.
"""

import json
import logging
from typing import Dict, Any, Optional

from ai_serp_keyword_research.metrics.exporters.base import MetricsExporter


class LoggingExporter(MetricsExporter):
    """
    Exporter that sends metrics to the Python logging system.
    
    This is useful for integrating with existing logging infrastructure.
    """
    
    def __init__(self, logger_name: str = "metrics", level: int = logging.INFO):
        """
        Initialize the logging exporter.
        
        Args:
            logger_name: Name of the logger to use
            level: Logging level (default: INFO)
        """
        self.logger = logging.getLogger(logger_name)
        self.level = level
    
    def export(self, metrics: Dict[str, Any]) -> None:
        """
        Export metrics by sending them to the logger.
        
        Args:
            metrics: Dictionary containing all metrics to export
        """
        # Convert metrics to a json string for structured logging
        metrics_json = json.dumps(metrics)
        
        # Log metrics at the configured level
        self.logger.log(self.level, "Metrics report", extra={"metrics": metrics_json})
    
    def close(self) -> None:
        """Close the exporter (no-op for logging exporter)."""
        pass 