"""Background tasks for literature search operations."""

from typing import List, Dict, Any
from celery import Task
from loguru import logger

from app.workers.celery_app import celery_app


class CallbackTask(Task):
    """Base task class with callbacks for progress tracking."""

    def on_success(self, retval, task_id, args, kwargs):
        """Called on successful task completion."""
        logger.info(f"Task {task_id} completed successfully")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure."""
        logger.error(f"Task {task_id} failed: {exc}")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried."""
        logger.warning(f"Task {task_id} is being retried: {exc}")


@celery_app.task(
    bind=True,
    base=CallbackTask,
    name="app.workers.tasks.literature_search.search_databases",
    max_retries=3,
    default_retry_delay=60,
)
def search_databases(
    self,
    query: str,
    databases: List[str],
    max_results: int = 1000,
    user_id: str = None
) -> Dict[str, Any]:
    """
    Search multiple literature databases.

    Args:
        query: Search query
        databases: List of database names (e.g., ['pubmed', 'arxiv'])
        max_results: Maximum results per database
        user_id: User requesting the search

    Returns:
        Dict with search results and metadata
    """
    try:
        logger.info(f"Starting literature search: {query} across {databases}")

        # Update task state to track progress
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": len(databases), "status": "Starting search..."}
        )

        results = {}
        total_found = 0

        for idx, database in enumerate(databases):
            logger.info(f"Searching {database}...")

            # Update progress
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": idx + 1,
                    "total": len(databases),
                    "status": f"Searching {database}...",
                    "database": database,
                }
            )

            # TODO: Implement actual database search using existing agents
            # For now, this is a placeholder
            # In production, this would call:
            # from app.agents.specialized.search import SearchAgent
            # agent = SearchAgent()
            # db_results = await agent.search(query, database, max_results)

            # Placeholder results
            db_results = {
                "count": 0,
                "papers": [],
                "database": database,
            }

            results[database] = db_results
            total_found += db_results["count"]

        logger.info(f"Literature search completed. Total papers found: {total_found}")

        return {
            "status": "completed",
            "query": query,
            "databases": databases,
            "results": results,
            "total_papers": total_found,
            "user_id": user_id,
        }

    except Exception as exc:
        logger.exception(f"Literature search failed: {exc}")
        # Retry on failure
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.workers.tasks.literature_search.deduplicate_papers",
    max_retries=2,
)
def deduplicate_papers(paper_ids: List[str]) -> Dict[str, Any]:
    """
    Deduplicate papers from multiple sources.

    Args:
        paper_ids: List of paper IDs to deduplicate

    Returns:
        Dict with deduplicated paper IDs and duplicates removed
    """
    try:
        logger.info(f"Starting deduplication of {len(paper_ids)} papers")

        # TODO: Implement deduplication logic
        # This should check for:
        # - Identical DOIs
        # - Similar titles (fuzzy matching)
        # - Same authors + year

        # Placeholder
        unique_papers = list(set(paper_ids))
        duplicates_removed = len(paper_ids) - len(unique_papers)

        logger.info(f"Deduplication complete. Removed {duplicates_removed} duplicates")

        return {
            "status": "completed",
            "total_input": len(paper_ids),
            "unique_papers": len(unique_papers),
            "duplicates_removed": duplicates_removed,
            "paper_ids": unique_papers,
        }

    except Exception as exc:
        logger.exception(f"Deduplication failed: {exc}")
        raise


@celery_app.task(
    name="app.workers.tasks.literature_search.fetch_full_text",
    max_retries=3,
    default_retry_delay=120,
)
def fetch_full_text(paper_id: str, source_url: str = None) -> Dict[str, Any]:
    """
    Fetch full text of a paper.

    Args:
        paper_id: Paper identifier
        source_url: Optional direct URL to PDF

    Returns:
        Dict with full text and metadata
    """
    try:
        logger.info(f"Fetching full text for paper: {paper_id}")

        # TODO: Implement PDF fetching and parsing
        # This should:
        # - Download PDF from source
        # - Parse PDF to extract text
        # - Store in file system or database
        # - Extract structured data (tables, figures)

        # Placeholder
        result = {
            "status": "completed",
            "paper_id": paper_id,
            "full_text": None,
            "pdf_path": None,
            "error": "Not implemented yet",
        }

        return result

    except Exception as exc:
        logger.exception(f"Full text fetch failed for {paper_id}: {exc}")
        raise
