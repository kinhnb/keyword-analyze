"""
Prometheus metrics exporter.

This exporter exposes metrics in Prometheus format for scraping.
"""

import logging
import threading
from typing import Dict, Any, Optional, List, Tuple
import time
from collections import defaultdict

# Import conditionally to make prometheus-client optional
try:
    import prometheus_client
    from prometheus_client import Counter, Gauge, Histogram, REGISTRY
    from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily, HistogramMetricFamily
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False
    logging.warning("prometheus-client package not installed. PrometheusExporter will be disabled.")

from ai_serp_keyword_research.metrics.exporters.base import MetricsExporter


class PrometheusExporter(MetricsExporter):
    """
    Exporter that exposes metrics in Prometheus format.
    
    This exporter can work in two modes:
    1. Push mode: Metrics are pushed to a Prometheus Pushgateway
    2. Pull mode: Metrics are exposed via an HTTP endpoint for scraping
    
    If prometheus-client is not installed, this exporter will be disabled.
    """
    
    def __init__(
        self,
        namespace: str = "serp_keyword_agent",
        push_gateway: Optional[str] = None,
        push_interval: int = 15,
        expose_port: Optional[int] = None,
        expose_path: str = "/metrics"
    ):
        """
        Initialize the Prometheus exporter.
        
        Args:
            namespace: Prefix for all metric names
            push_gateway: URL of the Prometheus Pushgateway (for push mode)
            push_interval: Interval in seconds between pushes (for push mode)
            expose_port: Port to expose metrics on (for pull mode)
            expose_path: URL path to expose metrics on (for pull mode)
            
        Note:
            If neither push_gateway nor expose_port is provided, the exporter
            will use the default prometheus_client registry but not expose
            or push metrics automatically.
        """
        if not HAS_PROMETHEUS:
            logging.error("Cannot initialize PrometheusExporter: prometheus-client package not installed.")
            return
        
        self.namespace = namespace
        self.push_gateway = push_gateway
        self.push_interval = push_interval
        self.expose_port = expose_port
        self.expose_path = expose_path
        
        # Create a custom collector
        self.collector = MetricsCollector(namespace)
        
        # Register the collector with Prometheus
        prometheus_client.REGISTRY.register(self.collector)
        
        # Set up HTTP server if requested
        if expose_port is not None:
            prometheus_client.start_http_server(expose_port)
            logging.info(f"Prometheus metrics exposed at :{expose_port}{expose_path}")
        
        # Set up push thread if requested
        self.stop_push_thread = False
        self.push_thread = None
        if push_gateway is not None:
            self.push_thread = threading.Thread(target=self._push_metrics_loop)
            self.push_thread.daemon = True
            self.push_thread.start()
            logging.info(f"Prometheus metrics will be pushed to {push_gateway} every {push_interval}s")
    
    def export(self, metrics: Dict[str, Any]) -> None:
        """
        Export metrics to Prometheus.
        
        Args:
            metrics: Dictionary containing all metrics to export
        """
        if not HAS_PROMETHEUS:
            return
        
        # Update the collector's metrics
        self.collector.update_metrics(metrics)
    
    def _push_metrics_loop(self) -> None:
        """Push metrics to the Pushgateway periodically."""
        while not self.stop_push_thread:
            try:
                prometheus_client.push_to_gateway(
                    self.push_gateway,
                    job=self.namespace,
                    registry=REGISTRY
                )
            except Exception as e:
                logging.error(f"Error pushing metrics to Prometheus Pushgateway: {str(e)}", exc_info=True)
            
            # Sleep until next push interval
            time.sleep(self.push_interval)
    
    def close(self) -> None:
        """Close the exporter and stop any background threads."""
        if not HAS_PROMETHEUS:
            return
        
        # Stop push thread if it's running
        if self.push_thread is not None:
            self.stop_push_thread = True
            self.push_thread.join(timeout=5.0)
        
        # Unregister our collector
        try:
            REGISTRY.unregister(self.collector)
        except:
            pass


class MetricsCollector:
    """
    Custom Prometheus collector that adapts our metrics format to Prometheus format.
    
    This is used internally by the PrometheusExporter.
    """
    
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.metrics = {}
        self.lock = threading.RLock()
    
    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update the collector's metrics from our internal format."""
        with self.lock:
            self.metrics = metrics
    
    def collect(self) -> List[Any]:
        """
        Collect all metrics in Prometheus format.
        
        This method is called by Prometheus to scrape metrics.
        """
        result = []
        
        with self.lock:
            # Convert counters
            if "counters" in self.metrics:
                for name, value in self.metrics["counters"].items():
                    # Parse tags from the name if present
                    base_name, labels, label_values = self._parse_name_and_tags(name)
                    
                    # Create counter
                    c = CounterMetricFamily(
                        f"{self.namespace}_{base_name}",
                        f"Counter for {base_name}",
                        labels=labels
                    )
                    c.add_metric(label_values, value)
                    result.append(c)
            
            # Convert gauges
            if "gauges" in self.metrics:
                for name, value in self.metrics["gauges"].items():
                    # Parse tags from the name if present
                    base_name, labels, label_values = self._parse_name_and_tags(name)
                    
                    # Create gauge
                    g = GaugeMetricFamily(
                        f"{self.namespace}_{base_name}",
                        f"Gauge for {base_name}",
                        labels=labels
                    )
                    g.add_metric(label_values, value)
                    result.append(g)
            
            # Convert histograms
            if "histograms" in self.metrics:
                for name, stats in self.metrics["histograms"].items():
                    # Parse tags from the name if present
                    base_name, labels, label_values = self._parse_name_and_tags(name)
                    
                    # Create simple summary (as we don't have full histogram buckets)
                    g = GaugeMetricFamily(
                        f"{self.namespace}_{base_name}_mean",
                        f"Mean value for {base_name}",
                        labels=labels
                    )
                    g.add_metric(label_values, stats.get("mean", 0))
                    result.append(g)
                    
                    # Add additional gauges for min, max, etc.
                    for stat_name in ["min", "max", "p50", "p95", "p99"]:
                        if stat_name in stats:
                            g = GaugeMetricFamily(
                                f"{self.namespace}_{base_name}_{stat_name}",
                                f"{stat_name.upper()} value for {base_name}",
                                labels=labels
                            )
                            g.add_metric(label_values, stats[stat_name])
                            result.append(g)
                    
                    # Add count gauge
                    g = GaugeMetricFamily(
                        f"{self.namespace}_{base_name}_count",
                        f"Count for {base_name}",
                        labels=labels
                    )
                    g.add_metric(label_values, stats.get("count", 0))
                    result.append(g)
        
        return result
    
    def _parse_name_and_tags(self, name: str) -> Tuple[str, List[str], List[str]]:
        """
        Parse the metric name and embedded tags.
        
        Returns:
            Tuple of (base_name, labels, label_values)
        """
        # Check if the name contains tags
        parts = name.split("_")
        if len(parts) <= 1:
            return name, [], []
        
        # Attempt to parse tags
        labels = []
        label_values = []
        
        # Start with the first part as the base name
        base_name = parts[0]
        
        # Look for key-value pairs in the remaining parts
        i = 1
        while i < len(parts) - 1:
            # Treat each odd-even pair as a key-value
            labels.append(parts[i])
            label_values.append(parts[i+1])
            i += 2
        
        # If there's an unpaired part at the end, append it to the base name
        if i < len(parts):
            base_name = f"{base_name}_{parts[i]}"
        
        return base_name, labels, label_values 