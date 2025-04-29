"""
Base metrics exporter interface.

All metrics exporters should implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class MetricsExporter(ABC):
    """
    Abstract base class for all metrics exporters.
    
    Metrics exporters are responsible for sending metrics to various
    monitoring systems like Prometheus, Datadog, CloudWatch, etc.
    """
    
    @abstractmethod
    def export(self, metrics: Dict[str, Any]) -> None:
        """
        Export the collected metrics to the target system.
        
        Args:
            metrics: Dictionary containing all metrics to export
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """
        Close the exporter and release any resources.
        
        This method should be called before application shutdown.
        """
        pass 