"""
Celery application configuration for background task processing.

Handles:
- Long-running literature searches
- Meta-analysis calculations
- Reviewer profiling
- Report generation
- Email notifications
"""

from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
from kombu import Exchange, Queue
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "meta_analysis_workers",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.workers.tasks.literature_search",
        "app.workers.tasks.meta_analysis",
        "app.workers.tasks.reviewer_tasks",
        "app.workers.tasks.notifications",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.workers.tasks.literature_search.*": {"queue": "search"},
        "app.workers.tasks.meta_analysis.*": {"queue": "analysis"},
        "app.workers.tasks.reviewer_tasks.*": {"queue": "reviewer"},
        "app.workers.tasks.notifications.*": {"queue": "notifications"},
    },

    # Task queues
    task_queues=(
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("search", Exchange("search"), routing_key="search"),
        Queue("analysis", Exchange("analysis"), routing_key="analysis"),
        Queue("reviewer", Exchange("reviewer"), routing_key="reviewer"),
        Queue("notifications", Exchange("notifications"), routing_key="notifications"),
    ),

    # Default queue
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",

    # Task execution
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task result settings
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,  # Store additional metadata

    # Task retry settings
    task_acks_late=True,  # Acknowledge tasks after completion
    task_reject_on_worker_lost=True,  # Requeue tasks if worker dies
    task_max_retries=3,  # Default max retries
    task_default_retry_delay=60,  # 1 minute between retries

    # Worker settings
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks
    worker_disable_rate_limits=False,

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,

    # Task time limits
    task_soft_time_limit=1800,  # 30 minutes soft limit
    task_time_limit=2400,  # 40 minutes hard limit

    # Beat schedule (periodic tasks)
    beat_schedule={
        "cleanup-expired-tasks": {
            "task": "app.workers.tasks.maintenance.cleanup_expired_tasks",
            "schedule": 3600.0,  # Every hour
        },
        "update-researcher-profiles": {
            "task": "app.workers.tasks.reviewer_tasks.update_researcher_profiles",
            "schedule": 86400.0,  # Every 24 hours
        },
    },
)


# Task lifecycle hooks
@task_prerun.connect
def task_prerun_handler(task_id, task, *args, **kwargs):
    """Log when task starts."""
    logger.info(f"Task started: {task.name} [{task_id}]")


@task_postrun.connect
def task_postrun_handler(task_id, task, *args, **kwargs):
    """Log when task completes."""
    logger.info(f"Task completed: {task.name} [{task_id}]")


@task_failure.connect
def task_failure_handler(task_id, exception, *args, **kwargs):
    """Log when task fails."""
    logger.error(f"Task failed: {task_id} - {exception}")


# Utility functions for task management
def get_task_status(task_id: str) -> dict:
    """
    Get status of a celery task.

    Args:
        task_id: Task ID

    Returns:
        Dict with task status and result
    """
    from celery.result import AsyncResult

    result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "traceback": result.traceback if result.failed() else None,
    }


def revoke_task(task_id: str, terminate: bool = False) -> bool:
    """
    Revoke a running task.

    Args:
        task_id: Task ID to revoke
        terminate: If True, terminate immediately. If False, wait for current step.

    Returns:
        True if task was revoked
    """
    celery_app.control.revoke(task_id, terminate=terminate)
    logger.info(f"Task revoked: {task_id} (terminate={terminate})")
    return True


def get_active_tasks() -> list[dict]:
    """
    Get list of active tasks.

    Returns:
        List of active task info
    """
    inspect = celery_app.control.inspect()
    active = inspect.active()

    if not active:
        return []

    tasks = []
    for worker, task_list in active.items():
        for task in task_list:
            tasks.append({
                "worker": worker,
                "task_id": task["id"],
                "task_name": task["name"],
                "args": task["args"],
                "kwargs": task["kwargs"],
            })

    return tasks


def get_queue_stats() -> dict:
    """
    Get statistics about task queues.

    Returns:
        Dict with queue statistics
    """
    inspect = celery_app.control.inspect()

    return {
        "active": inspect.active(),
        "scheduled": inspect.scheduled(),
        "reserved": inspect.reserved(),
        "stats": inspect.stats(),
    }
