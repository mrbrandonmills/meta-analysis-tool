"""Prometheus-compatible metrics for application monitoring."""
import time
from typing import Callable
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from dataclasses import dataclass, field


@dataclass
class MetricValue:
    """Container for metric values."""
    count: int = 0
    sum: float = 0.0
    min: float = float('inf')
    max: float = float('-inf')
    labels: dict = field(default_factory=dict)


class PrometheusMetrics:
    """Simple Prometheus-compatible metrics collector."""

    def __init__(self):
        """Initialize metrics storage."""
        self.counters: dict[str, int] = defaultdict(int)
        self.gauges: dict[str, float] = defaultdict(float)
        self.histograms: dict[str, list[float]] = defaultdict(list)
        self.summaries: dict[str, MetricValue] = defaultdict(MetricValue)

    def counter_inc(self, name: str, value: int = 1, **labels):
        """Increment a counter metric.

        Args:
            name: Metric name
            value: Increment value
            **labels: Metric labels
        """
        label_str = self._format_labels(labels)
        key = f"{name}{label_str}"
        self.counters[key] += value

    def gauge_set(self, name: str, value: float, **labels):
        """Set a gauge metric value.

        Args:
            name: Metric name
            value: Gauge value
            **labels: Metric labels
        """
        label_str = self._format_labels(labels)
        key = f"{name}{label_str}"
        self.gauges[key] = value

    def histogram_observe(self, name: str, value: float, **labels):
        """Observe a value in a histogram.

        Args:
            name: Metric name
            value: Observed value
            **labels: Metric labels
        """
        label_str = self._format_labels(labels)
        key = f"{name}{label_str}"
        self.histograms[key].append(value)

    def summary_observe(self, name: str, value: float, **labels):
        """Observe a value in a summary.

        Args:
            name: Metric name
            value: Observed value
            **labels: Metric labels
        """
        label_str = self._format_labels(labels)
        key = f"{name}{label_str}"

        if key not in self.summaries:
            self.summaries[key] = MetricValue(labels=labels)

        summary = self.summaries[key]
        summary.count += 1
        summary.sum += value
        summary.min = min(summary.min, value)
        summary.max = max(summary.max, value)

    def _format_labels(self, labels: dict) -> str:
        """Format labels as Prometheus string.

        Args:
            labels: Label dictionary

        Returns:
            Formatted label string
        """
        if not labels:
            return ""
        label_pairs = [f'{k}="{v}"' for k, v in sorted(labels.items())]
        return "{" + ",".join(label_pairs) + "}"

    def export(self) -> str:
        """Export metrics in Prometheus text format.

        Returns:
            Prometheus-formatted metrics string
        """
        lines = []

        # Export counters
        for name, value in self.counters.items():
            lines.append(f"# TYPE {name.split('{')[0]} counter")
            lines.append(f"{name} {value}")

        # Export gauges
        for name, value in self.gauges.items():
            lines.append(f"# TYPE {name.split('{')[0]} gauge")
            lines.append(f"{name} {value}")

        # Export histograms
        for name, values in self.histograms.items():
            base_name = name.split('{')[0]
            lines.append(f"# TYPE {base_name} histogram")

            # Calculate buckets
            buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
            for bucket in buckets:
                count = sum(1 for v in values if v <= bucket)
                lines.append(f'{base_name}_bucket{{le="{bucket}"}} {count}')

            lines.append(f'{base_name}_bucket{{le="+Inf"}} {len(values)}')
            lines.append(f'{base_name}_sum {sum(values)}')
            lines.append(f'{base_name}_count {len(values)}')

        # Export summaries
        for name, summary in self.summaries.items():
            base_name = name.split('{')[0]
            lines.append(f"# TYPE {base_name} summary")
            lines.append(f'{base_name}_sum {summary.sum}')
            lines.append(f'{base_name}_count {summary.count}')
            lines.append(f'{base_name}_min {summary.min}')
            lines.append(f'{base_name}_max {summary.max}')

        return "\n".join(lines) + "\n"


# Global metrics instance
metrics = PrometheusMetrics()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics.

        Args:
            request: Incoming request
            call_next: Next middleware in chain

        Returns:
            Response
        """
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Record metrics
        metrics.counter_inc(
            "http_requests_total",
            method=request.method,
            path=request.url.path,
            status=response.status_code
        )

        metrics.histogram_observe(
            "http_request_duration_seconds",
            duration,
            method=request.method,
            path=request.url.path
        )

        return response


def metrics_middleware():
    """Factory function for metrics middleware.

    Returns:
        MetricsMiddleware instance
    """
    return MetricsMiddleware


# Application-specific metrics helpers
def track_agent_execution(agent_name: str, duration: float, success: bool):
    """Track agent execution metrics.

    Args:
        agent_name: Name of the agent
        duration: Execution duration in seconds
        success: Whether execution succeeded
    """
    metrics.counter_inc(
        "agent_executions_total",
        agent=agent_name,
        status="success" if success else "failure"
    )

    metrics.histogram_observe(
        "agent_execution_duration_seconds",
        duration,
        agent=agent_name
    )


def track_llm_api_call(provider: str, model: str, tokens: int, duration: float):
    """Track LLM API call metrics.

    Args:
        provider: API provider (anthropic, openai)
        model: Model name
        tokens: Token count
        duration: API call duration in seconds
    """
    metrics.counter_inc(
        "llm_api_calls_total",
        provider=provider,
        model=model
    )

    metrics.counter_inc(
        "llm_tokens_total",
        tokens,
        provider=provider,
        model=model
    )

    metrics.histogram_observe(
        "llm_api_duration_seconds",
        duration,
        provider=provider,
        model=model
    )


def track_database_query(query_type: str, duration: float):
    """Track database query metrics.

    Args:
        query_type: Type of query (select, insert, update, delete)
        duration: Query duration in seconds
    """
    metrics.counter_inc(
        "database_queries_total",
        type=query_type
    )

    metrics.histogram_observe(
        "database_query_duration_seconds",
        duration,
        type=query_type
    )


def track_workflow_event(event_type: str, workflow_type: str):
    """Track workflow events.

    Args:
        event_type: Type of event (started, completed, failed)
        workflow_type: Type of workflow (meta_analysis, reviewer_match, etc.)
    """
    metrics.counter_inc(
        "workflow_events_total",
        event=event_type,
        workflow=workflow_type
    )


def set_active_workflows(count: int):
    """Set gauge for active workflows.

    Args:
        count: Number of active workflows
    """
    metrics.gauge_set("active_workflows", count)


def set_queue_size(queue_name: str, size: int):
    """Set gauge for queue size.

    Args:
        queue_name: Name of the queue
        size: Current queue size
    """
    metrics.gauge_set("queue_size", size, queue=queue_name)
