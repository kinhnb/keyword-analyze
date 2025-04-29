"""
Performance metrics collection.

This module provides utilities for collecting system performance metrics.
"""

import os
import time
import threading
import logging
import psutil
from typing import Dict, Any, Optional

from ai_serp_keyword_research.metrics.collector import get_metrics_collector

logger = logging.getLogger(__name__)


class PerformanceMetricsMonitor:
    """
    Monitors and collects system performance metrics.
    
    This class collects metrics like:
    - CPU usage
    - Memory usage
    - Disk I/O
    - Network I/O
    - Process information
    
    It runs in a background thread and periodically reports metrics.
    """
    
    def __init__(self, interval: int = 60):
        """
        Initialize the performance metrics monitor.
        
        Args:
            interval: Collection interval in seconds
        """
        self.interval = interval
        self.metrics = get_metrics_collector()
        self.process = psutil.Process(os.getpid())
        self._stop_event = threading.Event()
        self._thread = None
    
    def start(self) -> None:
        """Start the metrics collection thread."""
        if self._thread is not None and self._thread.is_alive():
            logger.warning("Performance metrics monitor is already running")
            return
        
        logger.info("Starting performance metrics monitor with interval %d seconds", self.interval)
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._collect_metrics_loop)
        self._thread.daemon = True
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the metrics collection thread."""
        if self._thread is None or not self._thread.is_alive():
            logger.warning("Performance metrics monitor is not running")
            return
        
        logger.info("Stopping performance metrics monitor")
        self._stop_event.set()
        self._thread.join(timeout=5.0)
        self._thread = None
    
    def _collect_metrics_loop(self) -> None:
        """Main collection loop that runs in a background thread."""
        logger.info("Performance metrics monitor started")
        
        # Collect initial IO counters as baseline
        last_disk_io = psutil.disk_io_counters()
        last_net_io = psutil.net_io_counters()
        last_time = time.time()
        
        while not self._stop_event.is_set():
            try:
                # Collect metrics
                self._collect_cpu_metrics()
                self._collect_memory_metrics()
                self._collect_disk_metrics(last_disk_io, last_time)
                self._collect_network_metrics(last_net_io, last_time)
                self._collect_process_metrics()
                
                # Update baseline counters
                last_disk_io = psutil.disk_io_counters()
                last_net_io = psutil.net_io_counters()
                last_time = time.time()
                
            except Exception as e:
                logger.error(f"Error collecting performance metrics: {str(e)}", exc_info=True)
            
            # Sleep until next collection interval
            self._stop_event.wait(self.interval)
        
        logger.info("Performance metrics monitor stopped")
    
    def _collect_cpu_metrics(self) -> None:
        """Collect CPU usage metrics."""
        # System CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.5)
        self.metrics.set_gauge("system_cpu_percent", cpu_percent)
        
        # Per-CPU metrics
        per_cpu = psutil.cpu_percent(interval=0.5, percpu=True)
        for i, percent in enumerate(per_cpu):
            self.metrics.set_gauge(f"system_cpu_percent", percent, {"cpu": f"cpu{i}"})
        
        # CPU load averages (on Unix systems)
        try:
            load1, load5, load15 = psutil.getloadavg()
            self.metrics.set_gauge("system_load_avg_1min", load1)
            self.metrics.set_gauge("system_load_avg_5min", load5)
            self.metrics.set_gauge("system_load_avg_15min", load15)
        except (AttributeError, OSError):
            # Not available on Windows
            pass
    
    def _collect_memory_metrics(self) -> None:
        """Collect memory usage metrics."""
        # System memory metrics
        mem = psutil.virtual_memory()
        self.metrics.set_gauge("system_memory_total_bytes", mem.total)
        self.metrics.set_gauge("system_memory_available_bytes", mem.available)
        self.metrics.set_gauge("system_memory_used_bytes", mem.used)
        self.metrics.set_gauge("system_memory_percent", mem.percent)
        
        # Swap memory metrics
        swap = psutil.swap_memory()
        self.metrics.set_gauge("system_swap_total_bytes", swap.total)
        self.metrics.set_gauge("system_swap_used_bytes", swap.used)
        self.metrics.set_gauge("system_swap_percent", swap.percent)
    
    def _collect_disk_metrics(self, last_io: Optional[Any], last_time: float) -> None:
        """
        Collect disk usage and I/O metrics.
        
        Args:
            last_io: Previous disk I/O counters
            last_time: Timestamp of previous collection
        """
        # Disk usage metrics
        disk_usage = psutil.disk_usage('/')
        self.metrics.set_gauge("system_disk_total_bytes", disk_usage.total)
        self.metrics.set_gauge("system_disk_used_bytes", disk_usage.used)
        self.metrics.set_gauge("system_disk_percent", disk_usage.percent)
        
        # Disk I/O metrics
        if last_io:
            current_io = psutil.disk_io_counters()
            current_time = time.time()
            time_delta = current_time - last_time
            
            # Calculate rates
            read_bytes_rate = (current_io.read_bytes - last_io.read_bytes) / time_delta
            write_bytes_rate = (current_io.write_bytes - last_io.write_bytes) / time_delta
            
            self.metrics.set_gauge("system_disk_read_bytes_per_sec", read_bytes_rate)
            self.metrics.set_gauge("system_disk_write_bytes_per_sec", write_bytes_rate)
    
    def _collect_network_metrics(self, last_io: Optional[Any], last_time: float) -> None:
        """
        Collect network I/O metrics.
        
        Args:
            last_io: Previous network I/O counters
            last_time: Timestamp of previous collection
        """
        if last_io:
            current_io = psutil.net_io_counters()
            current_time = time.time()
            time_delta = current_time - last_time
            
            # Calculate rates
            sent_bytes_rate = (current_io.bytes_sent - last_io.bytes_sent) / time_delta
            recv_bytes_rate = (current_io.bytes_recv - last_io.bytes_recv) / time_delta
            
            self.metrics.set_gauge("system_net_sent_bytes_per_sec", sent_bytes_rate)
            self.metrics.set_gauge("system_net_recv_bytes_per_sec", recv_bytes_rate)
    
    def _collect_process_metrics(self) -> None:
        """Collect metrics for the current process."""
        # Process CPU usage
        try:
            process_cpu = self.process.cpu_percent(interval=0.1)
            self.metrics.set_gauge("process_cpu_percent", process_cpu)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # Process memory usage
        try:
            mem_info = self.process.memory_info()
            self.metrics.set_gauge("process_memory_rss_bytes", mem_info.rss)
            self.metrics.set_gauge("process_memory_vms_bytes", mem_info.vms)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # Process info
        try:
            # Number of threads
            self.metrics.set_gauge("process_threads", self.process.num_threads())
            
            # Number of open files
            try:
                open_files = len(self.process.open_files())
                self.metrics.set_gauge("process_open_files", open_files)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            # Number of open connections
            try:
                connections = len(self.process.connections())
                self.metrics.set_gauge("process_connections", connections)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


# Singleton instance
_performance_monitor_instance = None


def get_performance_monitor(interval: int = 60) -> PerformanceMetricsMonitor:
    """
    Get the singleton performance monitor instance.
    
    Args:
        interval: Collection interval in seconds
        
    Returns:
        The performance monitor instance
    """
    global _performance_monitor_instance
    if _performance_monitor_instance is None:
        _performance_monitor_instance = PerformanceMetricsMonitor(interval=interval)
    return _performance_monitor_instance 