"""Studies API endpoints."""
from typing import List

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

router = APIRouter()


class SearchRequest(BaseModel):
    """Request to search for studies."""

    query: str
    databases: List[str] = ["pubmed"]
    filters: dict = {}


@router.post("/studies/search")
async def search_studies(request: SearchRequest):
    """Search for studies in academic databases."""
    try:
        logger.info(f"Searching for: {request.query}")

        # This would call the search agent
        return {
            "query": request.query,
            "databases": request.databases,
            "results": [
                {
                    "id": "PMID:12345",
                    "title": "Example Study on Mindfulness and Anxiety",
                    "authors": ["Smith, J.", "Doe, A."],
                    "year": 2023,
                    "journal": "Journal of Psychology",
                    "abstract": "This study investigated...",
                }
            ],
            "total": 1,
        }

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/studies/{study_id}")
async def get_study(study_id: str):
    """Get detailed information about a specific study."""
    return {
        "id": study_id,
        "title": "Example Study",
        "metadata": {},
        "full_text": "Not available",
    }


@router.post("/studies/screen")
async def screen_studies(studies: List[dict], criteria: dict):
    """Screen studies based on inclusion/exclusion criteria."""
    # This would call the screening agent
    return {
        "total": len(studies),
        "included": len(studies) // 2,
        "excluded": len(studies) // 2,
    }
