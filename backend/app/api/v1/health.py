"""Health check and system status endpoints."""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
from loguru import logger

from app.db.session import get_async_db
from app.core.config import get_settings
from app.core.security import require_admin, TokenData

settings = get_settings()
router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.

    Returns 200 if service is running.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "meta-analysis-platform",
        "version": "0.1.0",
    }


@router.get("/health/detailed", tags=["health"])
async def detailed_health_check(
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """
    Detailed health check with dependency status.

    Checks:
    - Database connectivity
    - Redis connectivity
    - Background worker status
    """
    checks = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": "meta-analysis-platform",
        "version": "0.1.0",
        "status": "healthy",
        "checks": {}
    }

    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        checks["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        checks["status"] = "unhealthy"
        checks["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        logger.error(f"Database health check failed: {e}")

    # Check Redis
    try:
        redis_client = await redis.from_url(settings.redis_url, decode_responses=True)
        await redis_client.ping()
        await redis_client.close()
        checks["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        checks["status"] = "unhealthy"
        checks["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
        logger.error(f"Redis health check failed: {e}")

    # Check Celery workers
    try:
        from app.workers.celery_app import celery_app

        inspect = celery_app.control.inspect()
        stats = inspect.stats()

        if stats:
            worker_count = len(stats)
            checks["checks"]["celery"] = {
                "status": "healthy",
                "message": f"{worker_count} worker(s) active",
                "workers": list(stats.keys())
            }
        else:
            checks["checks"]["celery"] = {
                "status": "degraded",
                "message": "No workers available"
            }
    except Exception as e:
        checks["checks"]["celery"] = {
            "status": "unknown",
            "message": f"Could not check workers: {str(e)}"
        }

    return checks


@router.get("/health/live", tags=["health"])
async def liveness_probe() -> Dict[str, str]:
    """
    Kubernetes liveness probe endpoint.

    Returns 200 if service should stay alive.
    """
    return {"status": "alive"}


@router.get("/health/ready", tags=["health"])
async def readiness_probe(
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """
    Kubernetes readiness probe endpoint.

    Returns 200 if service is ready to accept traffic.
    """
    try:
        # Check if database is accessible
        await db.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "reason": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health/metrics", tags=["health"])
async def metrics(
    token: TokenData = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """
    System metrics endpoint (admin only).

    Returns:
    - Database pool statistics
    - Redis info
    - Celery queue stats
    - API usage metrics
    """
    metrics_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "database": {},
        "redis": {},
        "celery": {},
    }

    # Database pool stats
    try:
        from app.db.session import async_engine

        pool = async_engine.pool
        metrics_data["database"] = {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow(),
        }
    except Exception as e:
        metrics_data["database"]["error"] = str(e)

    # Redis info
    try:
        redis_client = await redis.from_url(settings.redis_url, decode_responses=True)
        info = await redis_client.info()
        await redis_client.close()

        metrics_data["redis"] = {
            "used_memory_human": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_commands_processed": info.get("total_commands_processed"),
            "uptime_in_seconds": info.get("uptime_in_seconds"),
        }
    except Exception as e:
        metrics_data["redis"]["error"] = str(e)

    # Celery stats
    try:
        from app.workers.celery_app import get_queue_stats

        celery_stats = get_queue_stats()
        metrics_data["celery"] = celery_stats
    except Exception as e:
        metrics_data["celery"]["error"] = str(e)

    return metrics_data


@router.get("/health/version", tags=["health"])
async def version_info() -> Dict[str, Any]:
    """
    Service version information.

    Returns:
    - Service version
    - Python version
    - Dependencies
    """
    import sys
    import platform

    return {
        "service": "meta-analysis-platform",
        "version": "0.1.0",
        "python_version": sys.version,
        "platform": platform.platform(),
        "dependencies": {
            "fastapi": "0.104.1",
            "sqlalchemy": "2.0.23",
            "celery": "5.3.4",
        }
    }
