"""Metrics API endpoints for Prometheus monitoring."""
from fastapi import APIRouter, Response
from loguru import logger

from app.monitoring.metrics import metrics

router = APIRouter()


@router.get(
    "/metrics",
    response_class=Response,
    summary="Prometheus Metrics",
    description="Export metrics in Prometheus text format for scraping",
    tags=["monitoring"],
)
async def get_metrics():
    """Export metrics in Prometheus format.

    Returns:
        Response: Prometheus-formatted metrics
    """
    try:
        metrics_text = metrics.export()
        return Response(
            content=metrics_text,
            media_type="text/plain; version=0.0.4"
        )
    except Exception as e:
        logger.error(f"Failed to export metrics: {e}")
        return Response(
            content="# Error exporting metrics\n",
            media_type="text/plain; version=0.0.4",
            status_code=500
        )


@router.get(
    "/health/detailed",
    summary="Detailed Health Check",
    description="Comprehensive health check including database and Redis",
    tags=["monitoring"],
)
async def detailed_health_check():
    """Detailed health check with component status.

    Returns:
        dict: Health status of all components
    """
    from app.core.config import get_settings
    import asyncpg
    import redis.asyncio as aioredis

    settings = get_settings()
    health_status = {
        "status": "healthy",
        "components": {}
    }

    # Check database
    try:
        conn = await asyncpg.connect(settings.database_url)
        await conn.execute("SELECT 1")
        await conn.close()
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")

    # Check Redis
    try:
        redis_client = aioredis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.close()
        health_status["components"]["redis"] = "healthy"
    except Exception as e:
        health_status["components"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"Redis health check failed: {e}")

    # Check API
    health_status["components"]["api"] = "healthy"

    return health_status
