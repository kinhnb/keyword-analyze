"""
Metrics collector for the application.

This module provides the main metrics collection functionality.
"""

import time
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import threading
import os
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Singleton instance
_metrics_collector_instance = None

class MetricsCollector:
    """
    Central metrics collector for the application.
    
    This class collects various metrics like:
    - Agent metrics (token usage, success rates)
    - API metrics (request counts, latencies, status codes)
    - Performance metrics (memory usage, CPU usage)
    
    It provides methods to record metrics and retrieve current values.
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self._lock = threading.RLock()
        self._exporters = []
        self._counters = defaultdict(int)  # Simple counters
        self._gauges = {}  # Current value metrics
        self._histograms = defaultdict(list)  # Distribution metrics
        self._last_export_time = time.time()
        self._reporting_interval = int(os.getenv("METRICS_REPORTING_INTERVAL", "60"))
        self._is_collecting = True
    
    def add_exporter(self, exporter) -> None:
        """
        Add a metrics exporter.
        
        Args:
            exporter: The exporter to add
        """
        with self._lock:
            self._exporters.append(exporter)
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Increment a counter metric.
        
        Args:
            name: The name of the counter
            value: The amount to increment by (default: 1)
            tags: Optional tags to associate with this metric
        """
        with self._lock:
            if tags:
                tag_str = "_".join(f"{k}_{v}" for k, v in sorted(tags.items()))
                name = f"{name}_{tag_str}"
            self._counters[name] += value
            self._maybe_export()
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Set a gauge metric to a specific value.
        
        Args:
            name: The name of the gauge
            value: The value to set
            tags: Optional tags to associate with this metric
        """
        with self._lock:
            if tags:
                tag_str = "_".join(f"{k}_{v}" for k, v in sorted(tags.items()))
                name = f"{name}_{tag_str}"
            self._gauges[name] = value
            self._maybe_export()
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a histogram value.
        
        Args:
            name: The name of the histogram
            value: The value to record
            tags: Optional tags to associate with this metric
        """
        with self._lock:
            if tags:
                tag_str = "_".join(f"{k}_{v}" for k, v in sorted(tags.items()))
                name = f"{name}_{tag_str}"
            self._histograms[name].append(value)
            self._maybe_export()
    
    @contextmanager
    def measure_latency(self, name: str, tags: Optional[Dict[str, str]] = None):
        """
        Context manager to measure the latency of an operation.
        
        Args:
            name: The name of the latency metric
            tags: Optional tags to associate with this metric
            
        Example:
            with metrics_collector.measure_latency("api_request", {"endpoint": "/analyze"}):
                # Do something that takes time
                process_request()
        """
        start_time = time.time()
        try:
            yield
        finally:
            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
            self.record_histogram(f"{name}_latency_ms", elapsed_time, tags)
    
    def _maybe_export(self) -> None:
        """Check if it's time to export metrics and do so if needed."""
        current_time = time.time()
        if current_time - self._last_export_time >= self._reporting_interval:
            self.export_metrics()
            self._last_export_time = current_time
    
    def export_metrics(self) -> None:
        """Export metrics to all registered exporters."""
        metrics = self.get_all_metrics()
        for exporter in self._exporters:
            try:
                exporter.export(metrics)
            except Exception as e:
                logger.error(f"Error exporting metrics: {str(e)}", exc_info=True)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all currently collected metrics.
        
        Returns:
            Dictionary of all metrics organized by type
        """
        with self._lock:
            # Process histograms to calculate statistics
            histogram_stats = {}
            for name, values in self._histograms.items():
                if not values:
                    continue
                
                # Calculate basic statistics
                count = len(values)
                mean = sum(values) / count
                
                # Simple percentile calculation
                sorted_values = sorted(values)
                p50 = sorted_values[int(count * 0.5)] if count > 0 else 0
                p95 = sorted_values[int(count * 0.95)] if count > 1 else mean
                p99 = sorted_values[int(count * 0.99)] if count > 1 else mean
                
                histogram_stats[name] = {
                    "count": count,
                    "mean": mean,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "p50": p50,
                    "p95": p95,
                    "p99": p99
                }
            
            # Reset histograms after exporting
            self._histograms = defaultdict(list)
            
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": histogram_stats,
                "timestamp": time.time()
            }
    
    def stop(self) -> None:
        """Stop the metrics collector."""
        with self._lock:
            self._is_collecting = False
    
    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters = defaultdict(int)
            self._gauges = {}
            self._histograms = defaultdict(list)


def get_metrics_collector() -> MetricsCollector:
    """
    Get the singleton metrics collector instance.
    
    Returns:
        The metrics collector instance
    """
    global _metrics_collector_instance
    if _metrics_collector_instance is None:
        _metrics_collector_instance = MetricsCollector()
    return _metrics_collector_instance


def configure_metrics(exporters: Optional[List[Any]] = None) -> None:
    """
    Configure metrics collection with the specified exporters.
    
    Args:
        exporters: List of metrics exporters to use
    """
    collector = get_metrics_collector()
    
    # Add default console exporter if none specified
    if not exporters:
        from ai_serp_keyword_research.metrics.exporters import ConsoleExporter
        exporters = [ConsoleExporter()]
    
    # Register all exporters
    for exporter in exporters:
        collector.add_exporter(exporter) 