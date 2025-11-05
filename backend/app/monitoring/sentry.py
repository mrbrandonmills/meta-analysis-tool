"""Sentry error tracking integration."""
import os
from typing import Optional, Dict, Any
from loguru import logger

# Try to import sentry_sdk
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logger.warning("Sentry SDK not installed. Error tracking disabled.")


def init_sentry(
    dsn: Optional[str] = None,
    environment: str = "production",
    release: Optional[str] = None,
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
):
    """Initialize Sentry error tracking.

    Args:
        dsn: Sentry DSN (if None, read from SENTRY_DSN env var)
        environment: Environment name (production, staging, development)
        release: Release version
        traces_sample_rate: Sampling rate for performance traces (0.0 to 1.0)
        profiles_sample_rate: Sampling rate for profiling (0.0 to 1.0)
    """
    if not SENTRY_AVAILABLE:
        logger.warning("Sentry SDK not available")
        return

    # Get DSN from parameter or environment
    sentry_dsn = dsn or os.getenv("SENTRY_DSN")

    if not sentry_dsn:
        logger.info("Sentry DSN not configured. Error tracking disabled.")
        return

    try:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            release=release,
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            integrations=[
                FastApiIntegration(transaction_style="url"),
                RedisIntegration(),
                SqlalchemyIntegration(),
            ],
            # Send default PII (user IP, cookies, etc.)
            send_default_pii=False,
            # Attach stack traces to messages
            attach_stacktrace=True,
            # Maximum breadcrumbs
            max_breadcrumbs=50,
            # Debug mode
            debug=False,
        )

        logger.info(f"Sentry initialized for environment: {environment}")

    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def capture_exception(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    level: str = "error",
    tags: Optional[Dict[str, str]] = None,
):
    """Capture exception to Sentry with context.

    Args:
        error: Exception to capture
        context: Additional context
        level: Error level (fatal, error, warning, info, debug)
        tags: Custom tags
    """
    if not SENTRY_AVAILABLE:
        return

    try:
        # Set context
        if context:
            sentry_sdk.set_context("custom", context)

        # Set tags
        if tags:
            for key, value in tags.items():
                sentry_sdk.set_tag(key, value)

        # Set level
        with sentry_sdk.push_scope() as scope:
            scope.level = level
            sentry_sdk.capture_exception(error)

    except Exception as e:
        logger.error(f"Failed to capture exception to Sentry: {e}")


def capture_message(
    message: str,
    level: str = "info",
    context: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, str]] = None,
):
    """Capture message to Sentry.

    Args:
        message: Message to capture
        level: Message level (fatal, error, warning, info, debug)
        context: Additional context
        tags: Custom tags
    """
    if not SENTRY_AVAILABLE:
        return

    try:
        # Set context
        if context:
            sentry_sdk.set_context("custom", context)

        # Set tags
        if tags:
            for key, value in tags.items():
                sentry_sdk.set_tag(key, value)

        # Capture message
        sentry_sdk.capture_message(message, level=level)

    except Exception as e:
        logger.error(f"Failed to capture message to Sentry: {e}")


def set_user(user_id: str, email: Optional[str] = None, username: Optional[str] = None):
    """Set user context for Sentry.

    Args:
        user_id: User ID
        email: User email
        username: Username
    """
    if not SENTRY_AVAILABLE:
        return

    try:
        sentry_sdk.set_user({
            "id": user_id,
            "email": email,
            "username": username,
        })
    except Exception as e:
        logger.error(f"Failed to set Sentry user context: {e}")


def add_breadcrumb(
    message: str,
    category: str = "default",
    level: str = "info",
    data: Optional[Dict[str, Any]] = None,
):
    """Add breadcrumb to Sentry.

    Args:
        message: Breadcrumb message
        category: Category (navigation, http, auth, etc.)
        level: Level (fatal, error, warning, info, debug)
        data: Additional data
    """
    if not SENTRY_AVAILABLE:
        return

    try:
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {},
        )
    except Exception as e:
        logger.error(f"Failed to add Sentry breadcrumb: {e}")
