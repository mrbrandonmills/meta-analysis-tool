"""Structured logging infrastructure with JSON format for production."""
import sys
import json
from typing import Any, Dict, Optional
from datetime import datetime
from loguru import logger
from contextvars import ContextVar

# Context variable for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class JSONFormatter:
    """Custom JSON formatter for structured logging."""

    def __init__(self):
        self.format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    def __call__(self, record: Dict[str, Any]) -> str:
        """Format log record as JSON in production, pretty format in development."""
        # Get extra fields
        extra = record.get("extra", {})

        # Build structured log entry
        log_entry = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
        }

        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_entry["request_id"] = request_id

        # Add extra fields
        if extra:
            log_entry["extra"] = extra

        # Add exception info if present
        if record.get("exception"):
            log_entry["exception"] = {
                "type": record["exception"].type.__name__ if record["exception"].type else None,
                "value": str(record["exception"].value) if record["exception"].value else None,
                "traceback": record["exception"].traceback if record["exception"].traceback else None,
            }

        # Return JSON string
        return json.dumps(log_entry, default=str)


def configure_structured_logging(json_logs: bool = False):
    """Configure loguru for structured logging.

    Args:
        json_logs: If True, output JSON format (for production)
    """
    # Remove default logger
    logger.remove()

    # Add console handler
    if json_logs:
        # JSON format for production
        logger.add(
            sys.stdout,
            format=JSONFormatter(),
            level="INFO",
            serialize=True,
        )
    else:
        # Pretty format for development
        logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level> | "
                "{extra}"
            ),
            level="DEBUG",
            colorize=True,
        )

    # Add file handler for errors
    logger.add(
        "logs/error.log",
        format=JSONFormatter(),
        level="ERROR",
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        serialize=True,
    )

    # Add file handler for all logs
    logger.add(
        "logs/app.log",
        format=JSONFormatter(),
        level="INFO",
        rotation="500 MB",
        retention="7 days",
        compression="gz",
        serialize=True,
    )


def get_structured_logger(name: str):
    """Get a logger instance with the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Loguru logger instance
    """
    return logger.bind(logger_name=name)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **extra_fields
):
    """Log HTTP request with structured data.

    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        **extra_fields: Additional fields to log
    """
    logger.bind(
        request_method=method,
        request_path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        **extra_fields
    ).info(f"{method} {path} - {status_code} ({duration_ms:.2f}ms)")


def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    **extra_fields
):
    """Log error with structured context.

    Args:
        error: Exception instance
        context: Additional context about the error
        **extra_fields: Additional fields to log
    """
    logger.bind(
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {},
        **extra_fields
    ).error(f"Error: {type(error).__name__}: {str(error)}")


def log_metric(
    metric_name: str,
    value: float,
    unit: str = "",
    tags: Optional[Dict[str, str]] = None,
    **extra_fields
):
    """Log application metric.

    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
        tags: Metric tags/labels
        **extra_fields: Additional fields to log
    """
    logger.bind(
        metric_name=metric_name,
        metric_value=value,
        metric_unit=unit,
        tags=tags or {},
        **extra_fields
    ).info(f"Metric: {metric_name}={value}{unit}")


def log_agent_decision(
    agent_name: str,
    decision: str,
    confidence: float,
    reasoning: str,
    **extra_fields
):
    """Log agent decision for audit trail.

    Args:
        agent_name: Name of the agent
        decision: Decision made
        confidence: Confidence score (0-1)
        reasoning: Reasoning for decision
        **extra_fields: Additional fields to log
    """
    logger.bind(
        agent_name=agent_name,
        decision=decision,
        confidence=confidence,
        reasoning=reasoning,
        timestamp=datetime.utcnow().isoformat(),
        **extra_fields
    ).info(f"Agent Decision: {agent_name} - {decision} (confidence: {confidence:.2f})")


def log_workflow_event(
    workflow_id: str,
    event_type: str,
    agent_name: Optional[str] = None,
    status: Optional[str] = None,
    **extra_fields
):
    """Log workflow event.

    Args:
        workflow_id: Workflow identifier
        event_type: Type of event (started, completed, failed, etc.)
        agent_name: Name of the agent (if applicable)
        status: Current status
        **extra_fields: Additional fields to log
    """
    logger.bind(
        workflow_id=workflow_id,
        event_type=event_type,
        agent_name=agent_name,
        status=status,
        timestamp=datetime.utcnow().isoformat(),
        **extra_fields
    ).info(f"Workflow Event: {workflow_id} - {event_type}")
