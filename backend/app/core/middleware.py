"""
Middleware for rate limiting, error handling, and request tracking.

Includes:
- Rate limiting using Redis
- RFC 7807 Problem Details error responses
- Request ID tracking
- Performance monitoring
"""

import time
import uuid
from typing import Callable, Optional
from datetime import datetime, timedelta

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from loguru import logger
import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()


# RFC 7807 Problem Details for HTTP APIs
class ProblemDetail(JSONResponse):
    """
    RFC 7807 Problem Details response.

    Provides standardized error responses with:
    - type: URI reference for error type
    - title: Short human-readable summary
    - status: HTTP status code
    - detail: Human-readable explanation
    - instance: URI reference for specific occurrence
    """

    def __init__(
        self,
        status_code: int,
        title: str,
        detail: Optional[str] = None,
        type_uri: Optional[str] = None,
        instance: Optional[str] = None,
        **kwargs
    ):
        content = {
            "type": type_uri or f"https://httpstatuses.com/{status_code}",
            "title": title,
            "status": status_code,
        }

        if detail:
            content["detail"] = detail

        if instance:
            content["instance"] = instance

        # Add any additional fields
        content.update(kwargs)

        super().__init__(
            status_code=status_code,
            content=content,
            headers={"Content-Type": "application/problem+json"}
        )


# Rate limiting using Redis
class RateLimiter:
    """
    Token bucket rate limiter using Redis.

    Implements sliding window rate limiting with Redis for distributed rate limiting.
    """

    def __init__(self, redis_url: str = settings.redis_url):
        """Initialize rate limiter with Redis connection."""
        self.redis_client = None
        self.redis_url = redis_url

    async def init(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Rate limiter Redis connection established")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis for rate limiting: {e}")
            self.redis_client = None

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Rate limiter Redis connection closed")

    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check if request is allowed under rate limit.

        Args:
            key: Unique identifier for rate limit (e.g., user_id or IP)
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, metadata)
            metadata contains: remaining, reset_at, total
        """
        if not self.redis_client:
            # If Redis is not available, allow all requests
            logger.warning("Redis not available, rate limiting disabled")
            return True, {
                "remaining": max_requests,
                "reset_at": datetime.utcnow() + timedelta(seconds=window_seconds),
                "total": max_requests,
            }

        now = time.time()
        window_key = f"rate_limit:{key}"

        try:
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()

            # Remove expired timestamps
            pipe.zremrangebyscore(window_key, 0, now - window_seconds)

            # Count requests in current window
            pipe.zcard(window_key)

            # Add current request
            pipe.zadd(window_key, {str(uuid.uuid4()): now})

            # Set expiration
            pipe.expire(window_key, window_seconds)

            results = await pipe.execute()

            current_requests = results[1] + 1  # Count before adding new request

            remaining = max(0, max_requests - current_requests)
            reset_at = datetime.utcnow() + timedelta(seconds=window_seconds)

            is_allowed = current_requests <= max_requests

            return is_allowed, {
                "remaining": remaining,
                "reset_at": reset_at.isoformat(),
                "total": max_requests,
                "current": current_requests,
            }

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # On error, allow request but log the issue
            return True, {
                "remaining": max_requests,
                "reset_at": datetime.utcnow() + timedelta(seconds=window_seconds),
                "total": max_requests,
            }


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests.

    Applies different rate limits based on authentication:
    - Authenticated users: Higher limits
    - Unauthenticated users: Lower limits
    - API key users: Custom limits
    """

    def __init__(
        self,
        app: ASGIApp,
        authenticated_limit: int = 100,  # requests per minute
        unauthenticated_limit: int = 20,  # requests per minute
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.authenticated_limit = authenticated_limit
        self.unauthenticated_limit = unauthenticated_limit
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        # Determine rate limit key
        # Try to get user from token first, fall back to IP
        user_id = None
        try:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                from app.core.security import decode_token

                token = auth_header.replace("Bearer ", "")
                token_data = decode_token(token)
                user_id = token_data.user_id
        except Exception:
            pass

        if user_id:
            rate_limit_key = f"user:{user_id}"
            max_requests = self.authenticated_limit
        else:
            # Use IP address for unauthenticated requests
            client_ip = request.client.host if request.client else "unknown"
            rate_limit_key = f"ip:{client_ip}"
            max_requests = self.unauthenticated_limit

        # Check rate limit
        is_allowed, metadata = await rate_limiter.is_allowed(
            rate_limit_key,
            max_requests,
            self.window_seconds
        )

        if not is_allowed:
            return ProblemDetail(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                title="Rate limit exceeded",
                detail=f"Too many requests. Limit: {max_requests} per {self.window_seconds}s",
                type_uri="https://tools.ietf.org/html/rfc6585#section-4",
                retry_after=metadata.get("reset_at"),
            )

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(metadata.get("remaining", 0))
        response.headers["X-RateLimit-Reset"] = str(metadata.get("reset_at", ""))

        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to each request.

    Useful for distributed tracing and logging.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to request and response."""
        # Generate or use existing request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in request state for access in route handlers
        request.state.request_id = request_id

        # Add to logger context
        with logger.contextualize(request_id=request_id):
            response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track request performance.

    Logs slow requests and adds performance headers.
    """

    def __init__(self, app: ASGIApp, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track request performance."""
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        # Add performance header
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        # Log slow requests
        if process_time > self.slow_request_threshold:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.2f}s"
            )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware.

    Catches unhandled exceptions and returns RFC 7807 Problem Details.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle errors with RFC 7807 Problem Details."""
        try:
            response = await call_next(request)
            return response

        except HTTPException as exc:
            # Convert HTTPException to ProblemDetail
            return ProblemDetail(
                status_code=exc.status_code,
                title=exc.detail,
                detail=exc.detail,
                instance=str(request.url),
            )

        except Exception as exc:
            # Log unexpected errors
            logger.exception(f"Unhandled exception: {exc}")

            # Return 500 error
            return ProblemDetail(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                title="Internal Server Error",
                detail="An unexpected error occurred. Please try again later.",
                instance=str(request.url),
                error_type=type(exc).__name__,
            )


# Pagination helper
class PaginationParams:
    """
    Pagination parameters for list endpoints.

    Usage:
        @router.get("/items")
        async def list_items(pagination: PaginationParams = Depends()):
            items = await get_items(
                skip=pagination.skip,
                limit=pagination.limit
            )
            return pagination.paginate(items, total_count)
    """

    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100,
    ):
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        if page_size > max_page_size:
            page_size = max_page_size

        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size
        self.limit = page_size

    def paginate(self, items: list, total_count: int) -> dict:
        """
        Create paginated response.

        Args:
            items: List of items for current page
            total_count: Total number of items

        Returns:
            Dict with pagination metadata
        """
        total_pages = (total_count + self.page_size - 1) // self.page_size

        return {
            "items": items,
            "pagination": {
                "page": self.page,
                "page_size": self.page_size,
                "total_items": total_count,
                "total_pages": total_pages,
                "has_next": self.page < total_pages,
                "has_prev": self.page > 1,
            }
        }
