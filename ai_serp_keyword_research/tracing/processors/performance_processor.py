"""
Performance trace processor for the application.

This processor analyzes performance bottlenecks in traces and provides insights.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple

from agents import TraceProcessor, Trace, Span


class PerformanceTraceProcessor(TraceProcessor):
    """
    Trace processor that analyzes performance metrics and identifies bottlenecks.
    
    This processor:
    - Identifies slow traces and spans
    - Detects performance patterns
    - Provides optimization recommendations
    - Tracks performance trends over time
    """
    
    def __init__(
        self,
        slow_trace_threshold_ms: float = 5000.0,
        slow_span_threshold_ms: float = 1000.0,
        logger_name: str = "serp_keyword_performance",
        alert_threshold_ms: float = 10000.0,
    ):
        """
        Initialize the performance trace processor.
        
        Args:
            slow_trace_threshold_ms: Threshold in ms to consider a trace slow
            slow_span_threshold_ms: Threshold in ms to consider a span slow
            logger_name: Name of the logger to use
            alert_threshold_ms: Threshold in ms to trigger a performance alert
        """
        self.slow_trace_threshold_ms = slow_trace_threshold_ms
        self.slow_span_threshold_ms = slow_span_threshold_ms
        self.alert_threshold_ms = alert_threshold_ms
        self.logger = logging.getLogger(logger_name)
        
        # Performance tracking
        self.trace_performance_history: Dict[str, List[float]] = {}
        self.span_performance_history: Dict[str, List[float]] = {}
        self.bottleneck_counts: Dict[str, int] = {}
        
        # Timestamp of the last performance report
        self.last_performance_report = time.time()
        self.performance_report_interval = 3600  # 1 hour
    
    def process_trace(self, trace: Trace) -> None:
        """
        Process a trace for performance analysis.
        
        Args:
            trace: The completed trace
        """
        # Check if the trace is slow
        workflow_name = trace.workflow_name
        duration_ms = trace.duration_ms
        
        # Add to performance history
        if workflow_name not in self.trace_performance_history:
            self.trace_performance_history[workflow_name] = []
        self.trace_performance_history[workflow_name].append(duration_ms)
        
        # Keep only the last 100 records for each workflow
        if len(self.trace_performance_history[workflow_name]) > 100:
            self.trace_performance_history[workflow_name] = self.trace_performance_history[workflow_name][-100:]
        
        # Check for slow trace
        if duration_ms > self.slow_trace_threshold_ms:
            self.logger.warning(
                f"Slow trace detected: {workflow_name} took {duration_ms:.2f}ms "
                f"(threshold: {self.slow_trace_threshold_ms:.2f}ms)"
            )
            
            # Find bottlenecks within the trace
            bottlenecks = self._identify_bottlenecks(trace)
            if bottlenecks:
                bottleneck_details = ", ".join([
                    f"{name} ({duration:.2f}ms, {percentage:.1f}%)" 
                    for name, duration, percentage in bottlenecks
                ])
                self.logger.warning(f"Bottlenecks in {workflow_name}: {bottleneck_details}")
                
                # Update bottleneck counts
                for name, _, _ in bottlenecks:
                    if name not in self.bottleneck_counts:
                        self.bottleneck_counts[name] = 0
                    self.bottleneck_counts[name] += 1
            
            # Alert on extremely slow traces
            if duration_ms > self.alert_threshold_ms:
                self.logger.error(
                    f"PERFORMANCE ALERT: {workflow_name} took {duration_ms:.2f}ms "
                    f"(alert threshold: {self.alert_threshold_ms:.2f}ms)"
                )
        
        # Process spans for additional performance data
        if trace.spans:
            for span in trace.spans:
                self.process_span(span)
        
        # Check if it's time for a performance report
        current_time = time.time()
        if current_time - self.last_performance_report >= self.performance_report_interval:
            self._generate_performance_report()
            self.last_performance_report = current_time
    
    def process_span(self, span: Span) -> None:
        """
        Process a span for performance analysis.
        
        Args:
            span: The span
        """
        span_name = span.name
        duration_ms = span.duration_ms
        
        # Add to performance history
        if span_name not in self.span_performance_history:
            self.span_performance_history[span_name] = []
        self.span_performance_history[span_name].append(duration_ms)
        
        # Keep only the last 100 records for each span type
        if len(self.span_performance_history[span_name]) > 100:
            self.span_performance_history[span_name] = self.span_performance_history[span_name][-100:]
        
        # Check for slow span
        if duration_ms > self.slow_span_threshold_ms:
            self.logger.warning(
                f"Slow span detected: {span_name} took {duration_ms:.2f}ms "
                f"(threshold: {self.slow_span_threshold_ms:.2f}ms)"
            )
    
    def _identify_bottlenecks(self, trace: Trace) -> List[Tuple[str, float, float]]:
        """
        Identify performance bottlenecks in a trace.
        
        Args:
            trace: The trace to analyze
            
        Returns:
            List of (span_name, duration_ms, percentage) tuples representing bottlenecks
        """
        if not trace.spans:
            return []
        
        bottlenecks = []
        total_duration = trace.duration_ms
        
        # Find spans taking more than 20% of the total time
        for span in trace.spans:
            percentage = (span.duration_ms / total_duration) * 100
            if percentage > 20.0:
                bottlenecks.append((span.name, span.duration_ms, percentage))
        
        # Sort by duration (descending)
        return sorted(bottlenecks, key=lambda x: x[1], reverse=True)
    
    def _generate_performance_report(self) -> None:
        """Generate and log a performance report with trends and recommendations."""
        self.logger.info("=== Performance Analysis Report ===")
        
        # Trace performance analysis
        self.logger.info("Trace Performance:")
        for workflow, durations in self.trace_performance_history.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)
                min_duration = min(durations)
                p95_duration = sorted(durations)[int(0.95 * len(durations))]
                
                # Calculate trend (comparing first and last 5 durations if available)
                trend = "unknown"
                if len(durations) >= 10:
                    first_5_avg = sum(durations[:5]) / 5
                    last_5_avg = sum(durations[-5:]) / 5
                    diff_percent = ((last_5_avg - first_5_avg) / first_5_avg) * 100
                    
                    if diff_percent < -10:
                        trend = "improving"
                    elif diff_percent > 10:
                        trend = "degrading"
                    else:
                        trend = "stable"
                
                self.logger.info(
                    f"  {workflow}: avg={avg_duration:.2f}ms, "
                    f"min={min_duration:.2f}ms, max={max_duration:.2f}ms, "
                    f"p95={p95_duration:.2f}ms, samples={len(durations)}, "
                    f"trend={trend}"
                )
        
        # Top bottlenecks
        if self.bottleneck_counts:
            self.logger.info("Top Bottlenecks:")
            top_bottlenecks = sorted(
                self.bottleneck_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            for name, count in top_bottlenecks:
                durations = self.span_performance_history.get(name, [])
                avg_duration = sum(durations) / len(durations) if durations else 0
                
                self.logger.info(
                    f"  {name}: occurred {count} times, "
                    f"avg duration={avg_duration:.2f}ms"
                )
                
                # Add recommendations based on bottleneck type
                if "agent_run" in name:
                    self.logger.info(
                        f"    Recommendation: Consider optimizing agent instructions "
                        f"or breaking down complex agent tasks"
                    )
                elif "fetch_serp_data" in name:
                    self.logger.info(
                        f"    Recommendation: Improve caching strategy for SERP data "
                        f"or optimize API calls"
                    )
                elif "database" in name:
                    self.logger.info(
                        f"    Recommendation: Review database queries, check indexes, "
                        f"or improve connection pooling"
                    )
        
        # Overall recommendations
        self.logger.info("General Recommendations:")
        self.logger.info(
            "  1. Review any traces consistently exceeding the slow threshold"
        )
        self.logger.info(
            "  2. Consider caching results for frequent queries"
        )
        self.logger.info(
            "  3. Monitor agent token usage for cost optimization"
        )
        
        # Reset bottleneck counts for the next interval
        self.bottleneck_counts = {} 