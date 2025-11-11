"""
Helper functions for reporting task progress
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Import progress tracking functions
try:
    from app.api.v1.progress import set_task_progress, estimate_task_time
    PROGRESS_AVAILABLE = True
except ImportError:
    logger.warning("Progress tracking not available")
    PROGRESS_AVAILABLE = False

    # Stub functions if import fails
    def set_task_progress(*args, **kwargs):
        pass

    def estimate_task_time(*args, **kwargs):
        return 60


class ProgressReporter:
    """
    Helper class for reporting task progress
    """

    def __init__(
        self,
        task_id: str,
        task_type: str,
        total_steps: int,
        step_names: List[str],
        input_size: dict = None
    ):
        """
        Initialize progress reporter

        Args:
            task_id: Unique task identifier
            task_type: Type of task (meta-analysis, peer-review, reviewer-matcher)
            total_steps: Total number of steps in the task
            step_names: Names of all steps
            input_size: Dictionary with size metrics for time estimation
        """
        self.task_id = task_id
        self.task_type = task_type
        self.total_steps = total_steps
        self.step_names = step_names
        self.current_step_index = 0

        # Estimate total time
        self.estimated_total_time = estimate_task_time(
            task_type,
            input_size or {}
        )

        # Track start time for more accurate estimates
        import time
        self.start_time = time.time()

        logger.info(
            f"Progress reporter initialized for {task_type} task {task_id}. "
            f"Total steps: {total_steps}, Estimated time: {self.estimated_total_time}s"
        )

    def start(self):
        """Mark task as started"""
        set_task_progress(
            task_id=self.task_id,
            task_type=self.task_type,
            progress=0,
            status='running',
            current_step=self.step_names[0] if self.step_names else 'Starting...',
            steps_completed=[],
            steps_remaining=self.step_names,
            estimated_time_remaining=self.estimated_total_time
        )
        logger.info(f"Task {self.task_id} started")

    def update_step(self, step_index: int, message: Optional[str] = None):
        """
        Update current step

        Args:
            step_index: Index of current step (0-based)
            message: Optional custom message for the step
        """
        if step_index >= self.total_steps:
            return

        self.current_step_index = step_index

        # Calculate progress percentage
        progress = int((step_index / self.total_steps) * 100)

        # Get step names
        steps_completed = self.step_names[:step_index]
        steps_remaining = self.step_names[step_index + 1:]
        current_step = message or self.step_names[step_index]

        # Estimate time remaining based on elapsed time
        import time
        elapsed = time.time() - self.start_time
        if step_index > 0:
            avg_time_per_step = elapsed / step_index
            remaining_steps = self.total_steps - step_index
            estimated_remaining = int(avg_time_per_step * remaining_steps)
        else:
            estimated_remaining = self.estimated_total_time

        set_task_progress(
            task_id=self.task_id,
            task_type=self.task_type,
            progress=progress,
            status='running',
            current_step=current_step,
            steps_completed=steps_completed,
            steps_remaining=steps_remaining,
            estimated_time_remaining=estimated_remaining
        )

        logger.info(
            f"Task {self.task_id} progress: {progress}% - {current_step} "
            f"(~{estimated_remaining}s remaining)"
        )

    def complete(self):
        """Mark task as completed"""
        set_task_progress(
            task_id=self.task_id,
            task_type=self.task_type,
            progress=100,
            status='completed',
            current_step='Complete',
            steps_completed=self.step_names,
            steps_remaining=[],
            estimated_time_remaining=0
        )

        import time
        elapsed = time.time() - self.start_time
        logger.info(
            f"Task {self.task_id} completed in {elapsed:.1f}s "
            f"(estimated: {self.estimated_total_time}s)"
        )

    def error(self, error_message: str):
        """Mark task as failed"""
        set_task_progress(
            task_id=self.task_id,
            task_type=self.task_type,
            progress=int((self.current_step_index / self.total_steps) * 100),
            status='error',
            current_step=f'Failed: {error_message}',
            steps_completed=self.step_names[:self.current_step_index],
            steps_remaining=self.step_names[self.current_step_index:],
            estimated_time_remaining=0,
            message=error_message
        )
        logger.error(f"Task {self.task_id} failed: {error_message}")


# Convenience functions for common task types

def create_meta_analysis_reporter(task_id: str, num_studies: int = 100) -> ProgressReporter:
    """Create progress reporter for meta-analysis task"""
    steps = [
        "Literature Search",
        "Study Screening",
        "Quality Assessment",
        "Data Extraction",
        "Statistical Analysis",
        "Report Generation"
    ]

    return ProgressReporter(
        task_id=task_id,
        task_type='meta-analysis',
        total_steps=len(steps),
        step_names=steps,
        input_size={'num_studies': num_studies, 'num_agents': 6}
    )


def create_peer_review_reporter(task_id: str, num_pages: int = 10) -> ProgressReporter:
    """Create progress reporter for peer review task"""
    steps = [
        "Manuscript Analysis",
        "Quality Screening",
        "Methodology Review",
        "Results Evaluation",
        "Review Generation"
    ]

    return ProgressReporter(
        task_id=task_id,
        task_type='peer-review',
        total_steps=len(steps),
        step_names=steps,
        input_size={'num_pages': num_pages}
    )


def create_reviewer_matcher_reporter(task_id: str, pool_size: int = 100) -> ProgressReporter:
    """Create progress reporter for reviewer matcher task"""
    steps = [
        "Manuscript Analysis",
        "Expert Pool Search",
        "Expertise Matching",
        "Conflict Detection",
        "Ranking & Selection"
    ]

    return ProgressReporter(
        task_id=task_id,
        task_type='reviewer-matcher',
        total_steps=len(steps),
        step_names=steps,
        input_size={'pool_size': pool_size}
    )
