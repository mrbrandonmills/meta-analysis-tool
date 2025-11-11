"""
Progress tracking API endpoints
Provides real-time progress updates for long-running tasks
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
import redis
import json
import logging

from app.db.session import get_async_db
from app.core.security import get_current_user_from_bearer
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

# Redis client for progress tracking
try:
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )
except Exception as e:
    logger.warning(f"Redis not available for progress tracking: {e}")
    redis_client = None


class ProgressResponse:
    """Progress response model"""
    def __init__(
        self,
        progress: int = 0,
        status: str = "pending",
        estimated_time_remaining: int = 0,
        current_step: str = "",
        steps_completed: list = None,
        steps_remaining: list = None,
        started_at: Optional[str] = None,
        estimated_completion: Optional[str] = None,
        message: Optional[str] = None
    ):
        self.progress = progress
        self.status = status
        self.estimated_time_remaining = estimated_time_remaining
        self.current_step = current_step
        self.steps_completed = steps_completed or []
        self.steps_remaining = steps_remaining or []
        self.started_at = started_at
        self.estimated_completion = estimated_completion
        self.message = message

    def dict(self):
        return {
            "progress": self.progress,
            "status": self.status,
            "estimated_time_remaining": self.estimated_time_remaining,
            "current_step": self.current_step,
            "steps_completed": self.steps_completed,
            "steps_remaining": self.steps_remaining,
            "started_at": self.started_at,
            "estimated_completion": self.estimated_completion,
            "message": self.message
        }


def get_progress_key(task_id: str, task_type: str) -> str:
    """Generate Redis key for task progress"""
    return f"progress:{task_type}:{task_id}"


def set_task_progress(
    task_id: str,
    task_type: str,
    progress: int,
    status: str,
    current_step: str = "",
    steps_completed: list = None,
    steps_remaining: list = None,
    estimated_time_remaining: int = 0,
    message: Optional[str] = None
) -> None:
    """
    Store task progress in Redis

    Args:
        task_id: Task identifier
        task_type: Type of task (meta-analysis, peer-review, reviewer-matcher)
        progress: Progress percentage (0-100)
        status: Task status (pending, running, completed, error)
        current_step: Current step description
        steps_completed: List of completed steps
        steps_remaining: List of remaining steps
        estimated_time_remaining: Estimated seconds remaining
        message: Optional message (e.g., error message)
    """
    if not redis_client:
        return

    try:
        key = get_progress_key(task_id, task_type)

        # Get existing data to preserve started_at
        existing = redis_client.get(key)
        started_at = None
        if existing:
            try:
                existing_data = json.loads(existing)
                started_at = existing_data.get('started_at')
            except:
                pass

        # Set started_at if status is running and not set
        if status == 'running' and not started_at:
            started_at = datetime.utcnow().isoformat()

        # Calculate estimated completion
        estimated_completion = None
        if status == 'running' and estimated_time_remaining > 0:
            completion_time = datetime.utcnow() + timedelta(seconds=estimated_time_remaining)
            estimated_completion = completion_time.isoformat()

        progress_data = ProgressResponse(
            progress=progress,
            status=status,
            estimated_time_remaining=estimated_time_remaining,
            current_step=current_step,
            steps_completed=steps_completed or [],
            steps_remaining=steps_remaining or [],
            started_at=started_at,
            estimated_completion=estimated_completion,
            message=message
        )

        # Store in Redis with 24-hour expiration
        redis_client.setex(
            key,
            86400,  # 24 hours
            json.dumps(progress_data.dict())
        )

        logger.info(f"Progress updated for {task_type} task {task_id}: {progress}% - {current_step}")

    except Exception as e:
        logger.error(f"Failed to set task progress: {e}")


def get_task_progress(task_id: str, task_type: str) -> ProgressResponse:
    """
    Get task progress from Redis

    Args:
        task_id: Task identifier
        task_type: Type of task

    Returns:
        ProgressResponse object
    """
    if not redis_client:
        # Return default progress if Redis not available
        return ProgressResponse(
            progress=0,
            status="running",
            current_step="Processing...",
            message="Progress tracking unavailable"
        )

    try:
        key = get_progress_key(task_id, task_type)
        data = redis_client.get(key)

        if data:
            progress_dict = json.loads(data)
            return ProgressResponse(**progress_dict)
        else:
            # No progress data found, return pending
            return ProgressResponse(
                progress=0,
                status="pending",
                current_step="Initializing...",
                steps_remaining=["Initialization", "Processing", "Completion"]
            )

    except Exception as e:
        logger.error(f"Failed to get task progress: {e}")
        return ProgressResponse(
            progress=0,
            status="error",
            message=f"Failed to retrieve progress: {str(e)}"
        )


@router.get("/tasks/{task_id}/progress")
async def get_progress(
    task_id: str,
    task_type: str = Query(..., description="Type of task (meta-analysis, peer-review, reviewer-matcher)"),
    current_user: User = Depends(get_current_user_from_bearer),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get real-time progress for a task

    **Parameters:**
    - `task_id`: Task identifier
    - `task_type`: Type of task (meta-analysis, peer-review, reviewer-matcher)

    **Returns:**
    - Progress data including percentage, status, time estimates, and step information
    """
    try:
        progress = get_task_progress(task_id, task_type)
        return progress.dict()

    except Exception as e:
        logger.error(f"Error getting progress for task {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve task progress: {str(e)}"
        )


@router.delete("/tasks/{task_id}/progress")
async def clear_progress(
    task_id: str,
    task_type: str = Query(..., description="Type of task"),
    current_user: User = Depends(get_current_user_from_bearer)
):
    """
    Clear progress data for a task

    **Parameters:**
    - `task_id`: Task identifier
    - `task_type`: Type of task

    **Returns:**
    - Success message
    """
    if not redis_client:
        raise HTTPException(
            status_code=503,
            detail="Progress tracking service unavailable"
        )

    try:
        key = get_progress_key(task_id, task_type)
        redis_client.delete(key)

        return {"message": "Progress data cleared successfully"}

    except Exception as e:
        logger.error(f"Error clearing progress for task {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear progress: {str(e)}"
        )


# Helper function to estimate time based on task type and input
def estimate_task_time(
    task_type: str,
    input_size: dict
) -> int:
    """
    Estimate task completion time in seconds

    Args:
        task_type: Type of task
        input_size: Dictionary with task-specific size metrics

    Returns:
        Estimated time in seconds
    """
    base_times = {
        'meta-analysis': 60,  # 1 minute base
        'peer-review': 45,    # 45 seconds base
        'reviewer-matcher': 30  # 30 seconds base
    }

    base_time = base_times.get(task_type, 60)

    if task_type == 'meta-analysis':
        # Time = base + (studies * 0.5s) + (agents * 10s)
        num_studies = input_size.get('num_studies', 100)
        num_agents = input_size.get('num_agents', 6)
        return int(base_time + (num_studies * 0.5) + (num_agents * 10))

    elif task_type == 'peer-review':
        # Time = base + (pages * 2s)
        num_pages = input_size.get('num_pages', 10)
        return int(base_time + (num_pages * 2))

    elif task_type == 'reviewer-matcher':
        # Time = base + (pool_size * 0.1s)
        pool_size = input_size.get('pool_size', 100)
        return int(base_time + (pool_size * 0.1))

    return base_time


# Export functions for use in tasks
__all__ = [
    'router',
    'set_task_progress',
    'get_task_progress',
    'estimate_task_time',
    'ProgressResponse'
]
