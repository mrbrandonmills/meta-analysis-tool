"""Logging configuration for the application.

HIGH PRIORITY FIX: This module configures proper logging levels and formatting
to ensure INFO logs are not incorrectly tagged as error level.
"""
import sys
from loguru import logger

from app.core.config import get_settings


def configure_logging():
    """Configure logging with proper levels and formatting.

    This function should be called at application startup to ensure
    logs are properly categorized by level (DEBUG, INFO, WARNING, ERROR).
    """
    settings = get_settings()

    # Remove default logger
    logger.remove()

    # Add console handler with proper formatting
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        level=settings.log_level.upper(),
        colorize=True,
    )

    # Add file handler for persistent logs (optional, can be configured via settings)
    # This writes all logs to a file for debugging and audit purposes
    logger.add(
        "logs/app.log",
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="10 days",  # Keep logs for 10 days
        compression="zip",  # Compress rotated logs
        level="DEBUG",  # Log all levels to file
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
    )

    logger.info(f"Logging configured with level: {settings.log_level}")
    logger.debug("Debug logging is enabled")


def get_logger(name: str):
    """Get a logger instance with the given name.

    Args:
        name: Name for the logger (typically __name__)

    Returns:
        Configured logger instance
    """
    return logger.bind(name=name)
