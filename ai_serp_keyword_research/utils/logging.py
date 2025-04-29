"""
Structured logging module for the AI SERP Keyword Research Agent.

This module provides structured logging capabilities with JSON formatting,
correlation IDs, and configurable log levels.
"""

import json
import logging
import sys
import time
import uuid
from typing import Any, Dict, Optional, Union

import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class CorrelationIDFilter(logging.Filter):
    """
    Filter that adds correlation ID to log records.
    
    This filter ensures that each log record contains a correlation ID for
    request tracing across components and services.
    """
    
    _correlation_id = None
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add correlation ID to log record.
        
        Args:
            record: LogRecord to process
            
        Returns:
            True to include the record in the log output
        """
        record.correlation_id = CorrelationIDFilter.get_correlation_id()
        return True
    
    @staticmethod
    def set_correlation_id(correlation_id: Optional[str] = None) -> str:
        """
        Set the current correlation ID.
        
        Args:
            correlation_id: ID to use, or None to generate a new one
            
        Returns:
            The correlation ID that was set
        """
        CorrelationIDFilter._correlation_id = correlation_id or str(uuid.uuid4())
        return CorrelationIDFilter._correlation_id
    
    @staticmethod
    def get_correlation_id() -> str:
        """
        Get the current correlation ID.
        
        Returns:
            Current correlation ID, or a new one if none is set
        """
        if CorrelationIDFilter._correlation_id is None:
            CorrelationIDFilter._correlation_id = str(uuid.uuid4())
        return CorrelationIDFilter._correlation_id
    
    @staticmethod
    def clear_correlation_id() -> None:
        """Clear the current correlation ID."""
        CorrelationIDFilter._correlation_id = None


class JSONFormatter(logging.Formatter):
    """
    Formatter for JSON-structured logs.
    
    This formatter outputs log records as JSON objects with consistent fields,
    making them easier to parse and analyze with log management tools.
    """
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = '%',
        include_stack_info: bool = False
    ):
        """
        Initialize the JSON formatter.
        
        Args:
            fmt: Format string (unused for JSON formatter)
            datefmt: Date format string
            style: Style of format string (unused for JSON formatter)
            include_stack_info: Whether to include stack info in logs
        """
        super().__init__(fmt, datefmt, style)
        self.include_stack_info = include_stack_info
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.
        
        Args:
            record: LogRecord to format
            
        Returns:
            JSON string representation of the log record
        """
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "correlation_id": getattr(record, "correlation_id", "unknown"),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "process": record.process,
            "thread": record.thread
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Add stack info if configured and present
        if self.include_stack_info and record.stack_info:
            log_data["stack_info"] = self.formatStack(record.stack_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in [
                "args", "asctime", "created", "exc_info", "exc_text", "filename",
                "funcName", "id", "levelname", "levelno", "lineno", "module",
                "msecs", "message", "msg", "name", "pathname", "process",
                "processName", "relativeCreated", "stack_info", "thread",
                "threadName", "correlation_id"
            ]:
                log_data[key] = value
        
        return json.dumps(log_data, default=str)


def get_logger(
    name: str,
    log_level: Union[str, int] = logging.INFO,
    json_format: bool = True,
    include_correlation_id: bool = True,
    log_to_console: bool = True,
    log_to_file: bool = False,
    log_file_path: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Get a configured logger with the specified settings.
    
    Args:
        name: Name of the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to format logs as JSON
        include_correlation_id: Whether to include correlation ID
        log_to_console: Whether to log to console
        log_to_file: Whether to log to file
        log_file_path: Path to log file (if log_to_file is True)
        max_bytes: Maximum size of log file before rotating
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger
    """
    # Convert string log level to numeric
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper())
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Remove existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    if json_format:
        formatter = JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(correlation_id)s] [%(module)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S.%fZ"
        )
    
    # Add correlation ID filter if requested
    if include_correlation_id:
        logger.addFilter(CorrelationIDFilter())
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if requested
    if log_to_file and log_file_path:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


class LogContext:
    """
    Context manager for setting correlation ID and other log context.
    
    This context manager ensures that correlation ID and other context values
    are properly set for the duration of a logical operation and then cleaned up.
    """
    
    def __init__(
        self,
        correlation_id: Optional[str] = None,
        context_values: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the log context.
        
        Args:
            correlation_id: Correlation ID to use, or None to generate a new one
            context_values: Additional context values to add to log records
        """
        self.correlation_id = correlation_id
        self.context_values = context_values or {}
        self.previous_correlation_id = None
    
    def __enter__(self) -> "LogContext":
        """Set up the log context."""
        # Save current correlation ID
        self.previous_correlation_id = CorrelationIDFilter.get_correlation_id()
        
        # Set new correlation ID
        if self.correlation_id:
            CorrelationIDFilter.set_correlation_id(self.correlation_id)
        else:
            CorrelationIDFilter.set_correlation_id()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Clean up the log context."""
        # Restore previous correlation ID
        if self.previous_correlation_id:
            CorrelationIDFilter.set_correlation_id(self.previous_correlation_id)
        else:
            CorrelationIDFilter.clear_correlation_id()
    
    @property
    def correlation_id(self) -> str:
        """Get the current correlation ID."""
        return CorrelationIDFilter.get_correlation_id()


# Configure default logger
app_logger = get_logger(
    name="serp_keyword_research",
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    json_format=os.getenv("LOG_JSON", "true").lower() == "true",
    include_correlation_id=True,
    log_to_console=True,
    log_to_file=os.getenv("LOG_TO_FILE", "false").lower() == "true",
    log_file_path=os.getenv("LOG_FILE_PATH", "logs/app.log")
) 