"""
Metrics trace processor for the application.

This processor collects metrics from traces and reports them for monitoring.
"""

import time
from collections import defaultdict
from typing import Dict, List, Optional, Any, DefaultDict

from agents import TraceProcessor, Trace, Span


class MetricsTraceProcessor(TraceProcessor):
    """
    Trace processor that collects and reports metrics from traces.
    
    This processor tracks various metrics like:
    - Trace counts by workflow name
    - Average duration by workflow name
    - Success/failure rates
    - Agent token usage
    """
    
    def __init__(self, reporting_interval: int = 60):
        """
        Initialize the metrics trace processor.
        
        Args:
            reporting_interval: Interval in seconds between metrics reporting
        """
        self.reporting_interval = reporting_interval
        self.last_report_time = time.time()
        
        # Metrics storage
        self.trace_counts: DefaultDict[str, int] = defaultdict(int)
        self.trace_durations: DefaultDict[str, List[float]] = defaultdict(list)
        self.error_counts: DefaultDict[str, int] = defaultdict(int)
        self.span_counts: DefaultDict[str, int] = defaultdict(int)
        self.span_durations: DefaultDict[str, List[float]] = defaultdict(list)
        self.agent_token_usage: DefaultDict[str, List[int]] = defaultdict(list)
        
        # Aggregated metrics for the current interval
        self.current_metrics: Dict[str, Any] = {}
    
    def process_trace(self, trace: Trace) -> None:
        """
        Process a completed trace and collect metrics.
        
        Args:
            trace: The completed trace
        """
        # Collect basic trace metrics
        workflow_name = trace.workflow_name
        self.trace_counts[workflow_name] += 1
        self.trace_durations[workflow_name].append(trace.duration_ms)
        
        # Check for errors
        has_error = False
        if trace.metadata and "error" in trace.metadata:
            has_error = True
            self.error_counts[workflow_name] += 1
        
        # Process spans for additional metrics
        if trace.spans:
            for span in trace.spans:
                self.process_span(span)
                
                # Check for token usage in agent runs
                if span.name.startswith("agent_run:") and span.metadata:
                    if "input_tokens" in span.metadata and "output_tokens" in span.metadata:
                        agent_name = span.metadata.get("agent_name", "unknown")
                        total_tokens = (
                            span.metadata.get("input_tokens", 0) + 
                            span.metadata.get("output_tokens", 0)
                        )
                        self.agent_token_usage[agent_name].append(total_tokens)
        
        # Check if it's time to report metrics
        current_time = time.time()
        if current_time - self.last_report_time >= self.reporting_interval:
            self._report_metrics()
            self.last_report_time = current_time
    
    def process_span(self, span: Span) -> None:
        """
        Process a span and collect metrics.
        
        Args:
            span: The span
        """
        span_name = span.name
        self.span_counts[span_name] += 1
        self.span_durations[span_name].append(span.duration_ms)
    
    def _report_metrics(self) -> None:
        """
        Aggregate and report the current metrics.
        
        This method calculates averages, rates, and other derived metrics
        and would typically send them to a metrics monitoring system.
        For now, it simply calculates the metrics and prints them.
        """
        # Aggregate trace metrics
        trace_metrics = {}
        for name, counts in self.trace_counts.items():
            durations = self.trace_durations[name]
            errors = self.error_counts[name]
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            error_rate = errors / counts if counts > 0 else 0
            
            trace_metrics[name] = {
                "count": counts,
                "avg_duration_ms": avg_duration,
                "error_rate": error_rate,
                "success_rate": 1.0 - error_rate
            }
        
        # Aggregate span metrics
        span_metrics = {}
        for name, counts in self.span_counts.items():
            durations = self.span_durations[name]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            span_metrics[name] = {
                "count": counts,
                "avg_duration_ms": avg_duration
            }
        
        # Aggregate token usage metrics
        token_metrics = {}
        for agent, tokens in self.agent_token_usage.items():
            avg_tokens = sum(tokens) / len(tokens) if tokens else 0
            token_metrics[agent] = {
                "calls": len(tokens),
                "avg_tokens": avg_tokens,
                "total_tokens": sum(tokens)
            }
        
        # Combine all metrics
        self.current_metrics = {
            "traces": trace_metrics,
            "spans": span_metrics,
            "tokens": token_metrics,
            "timestamp": time.time()
        }
        
        # In a real implementation, we would send these metrics to a monitoring system
        # For now, we'll just print them
        print(f"Metrics collected at {time.time()}:")
        for category, metrics in self.current_metrics.items():
            if category != "timestamp":
                print(f"  {category.capitalize()}:")
                for name, values in metrics.items():
                    print(f"    {name}: {values}")
        
        # Reset counters for the next interval
        self._reset_counters()
    
    def _reset_counters(self) -> None:
        """Reset all metric counters for the next reporting interval."""
        self.trace_counts = defaultdict(int)
        self.trace_durations = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.span_counts = defaultdict(int)
        self.span_durations = defaultdict(list)
        self.agent_token_usage = defaultdict(list)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get the current metrics.
        
        Returns:
            The current aggregated metrics
        """
        return self.current_metrics.copy() 