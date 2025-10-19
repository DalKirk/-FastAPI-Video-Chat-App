"""
Metrics collection and monitoring utilities
"""
import time
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class Metrics:
    """System metrics container"""
    
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # WebSocket metrics
    active_connections: int = 0
    total_connections: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    
    # Video metrics
    live_streams_created: int = 0
    videos_uploaded: int = 0
    videos_processed: int = 0
    
    # Performance metrics
    request_durations: list = field(default_factory=list)
    error_count: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # Timestamp
    last_reset: datetime = field(default_factory=datetime.utcnow)
    
    def average_request_duration(self) -> float:
        """Calculate average request duration"""
        if not self.request_durations:
            return 0.0
        return sum(self.request_durations) / len(self.request_durations)
    
    def success_rate(self) -> float:
        """Calculate request success rate"""
        total = self.total_requests
        if total == 0:
            return 100.0
        return (self.successful_requests / total) * 100
    
    def to_dict(self) -> dict:
        """Convert metrics to dictionary"""
        return {
            "requests": {
                "total": self.total_requests,
                "successful": self.successful_requests,
                "failed": self.failed_requests,
                "success_rate": f"{self.success_rate():.2f}%",
                "average_duration_ms": f"{self.average_request_duration():.2f}"
            },
            "websocket": {
                "active_connections": self.active_connections,
                "total_connections": self.total_connections,
                "messages_sent": self.messages_sent,
                "messages_received": self.messages_received
            },
            "video": {
                "live_streams_created": self.live_streams_created,
                "videos_uploaded": self.videos_uploaded,
                "videos_processed": self.videos_processed
            },
            "errors": dict(self.error_count),
            "last_reset": self.last_reset.isoformat()
        }
    
    def reset(self):
        """Reset metrics"""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.request_durations.clear()
        self.error_count.clear()
        self.last_reset = datetime.utcnow()


class MetricsCollector:
    """Singleton metrics collector"""
    
    _instance: Optional['MetricsCollector'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.metrics = Metrics()
        return cls._instance
    
    def record_request(self, duration: float, success: bool = True):
        """Record API request"""
        self.metrics.total_requests += 1
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
        
        # Keep only last 1000 durations to prevent memory growth
        if len(self.metrics.request_durations) > 1000:
            self.metrics.request_durations.pop(0)
        self.metrics.request_durations.append(duration)
    
    def record_websocket_connection(self, connected: bool = True):
        """Record WebSocket connection"""
        if connected:
            self.metrics.active_connections += 1
            self.metrics.total_connections += 1
        else:
            self.metrics.active_connections = max(0, self.metrics.active_connections - 1)
    
    def record_message(self, sent: bool = True):
        """Record WebSocket message"""
        if sent:
            self.metrics.messages_sent += 1
        else:
            self.metrics.messages_received += 1
    
    def record_video_event(self, event_type: str):
        """Record video-related event"""
        if event_type == "live_stream":
            self.metrics.live_streams_created += 1
        elif event_type == "upload":
            self.metrics.videos_uploaded += 1
        elif event_type == "processed":
            self.metrics.videos_processed += 1
    
    def record_error(self, error_type: str):
        """Record error occurrence"""
        self.metrics.error_count[error_type] += 1
    
    def get_metrics(self) -> dict:
        """Get current metrics"""
        return self.metrics.to_dict()
    
    def reset(self):
        """Reset all metrics"""
        self.metrics.reset()


# Global metrics instance
metrics_collector = MetricsCollector()


# Decorator for automatic request timing
def timed_endpoint(func):
    """Decorator to automatically time endpoint execution"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000  # Convert to ms
            metrics_collector.record_request(duration, success=True)
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            metrics_collector.record_request(duration, success=False)
            metrics_collector.record_error(type(e).__name__)
            raise
    
    return wrapper
