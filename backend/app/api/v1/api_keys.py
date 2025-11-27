"""
API Key Management Endpoints

Allows users to manage their own API keys for subscription databases.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_async_db
from app.models.api_keys import DatabaseProvider
from app.models.user import User
from app.services.api_key_service import api_key_service

router = APIRouter()


# Request/Response Models
class AddAPIKeyRequest(BaseModel):
    """Request to add a new API key."""

    provider: DatabaseProvider = Field(..., description="Database provider")
    api_key: str = Field(..., description="API key (will be encrypted)")
    key_name: str | None = Field(None, description="Optional name for the key")
    verify: bool = Field(True, description="Verify the key immediately")


class APIKeyResponse(BaseModel):
    """Response with API key metadata (never includes actual key)."""

    id: str
    provider: str
    key_name: str
    enabled: bool
    verified: bool
    last_verified_at: str | None
    last_used_at: str | None
    created_at: str
    total_requests: str
    failed_requests: str


class APIKeyListResponse(BaseModel):
    """List of user API keys."""

    keys: List[APIKeyResponse]
    total: int


class VerifyKeyResponse(BaseModel):
    """Response from key verification."""

    success: bool
    message: str


class DatabaseInfoResponse(BaseModel):
    """Information about a database provider."""

    provider: str
    name: str
    description: str
    requires_key: bool
    estimated_coverage: str
    cost: str
    setup_instructions: str


# Endpoints
@router.post("/api-keys/add", response_model=APIKeyResponse)
async def add_api_key(
    request: AddAPIKeyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Add a new API key for a subscription database.

    The API key will be encrypted and stored securely.
    Optionally verifies the key works before accepting it.
    """
    try:
        logger.info(f"User {current_user.id} adding API key for {request.provider.value}")

        key_record = await api_key_service.add_api_key(
            db=db,
            user_id=current_user.id,
            provider=request.provider,
            api_key=request.api_key,
            key_name=request.key_name,
            verify=request.verify,
        )

        return APIKeyResponse(
            id=str(key_record.id),
            provider=key_record.provider.value,
            key_name=key_record.key_name,
            enabled=key_record.enabled,
            verified=key_record.verified,
            last_verified_at=key_record.last_verified_at.isoformat() if key_record.last_verified_at else None,
            last_used_at=key_record.last_used_at.isoformat() if key_record.last_used_at else None,
            created_at=key_record.created_at.isoformat(),
            total_requests=key_record.total_requests,
            failed_requests=key_record.failed_requests,
        )

    except Exception as e:
        logger.error(f"Error adding API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api-keys/list", response_model=APIKeyListResponse)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """List all API keys for the current user.

    Returns metadata only - never exposes actual API keys.
    """
    try:
        keys = await api_key_service.list_user_keys(db, current_user.id)

        return APIKeyListResponse(
            keys=[APIKeyResponse(**key) for key in keys],
            total=len(keys),
        )

    except Exception as e:
        logger.error(f"Error listing API keys: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api-keys/delete/{key_id}")
async def delete_api_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Delete an API key.

    Only the owner of the key can delete it.
    """
    try:
        success = await api_key_service.delete_api_key(
            db=db,
            user_id=current_user.id,
            key_id=key_id,
        )

        if not success:
            raise HTTPException(status_code=404, detail="API key not found")

        return {"message": "API key deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api-keys/verify/{key_id}", response_model=VerifyKeyResponse)
async def verify_api_key(
    key_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Verify that an API key works.

    Tests the key against the actual database API.
    """
    try:
        success = await api_key_service.verify_api_key(db, key_id)

        if success:
            return VerifyKeyResponse(
                success=True,
                message="API key verified successfully",
            )
        else:
            return VerifyKeyResponse(
                success=False,
                message="API key verification failed - check your key is valid",
            )

    except Exception as e:
        logger.error(f"Error verifying API key: {e}")
        return VerifyKeyResponse(
            success=False,
            message=f"Verification error: {str(e)}",
        )


@router.get("/databases/info", response_model=List[DatabaseInfoResponse])
async def get_database_info():
    """Get information about all available databases.

    Shows which databases are free vs require API keys,
    and provides setup instructions.
    """
    databases = [
        {
            "provider": "pubmed",
            "name": "PubMed/MEDLINE",
            "description": "36M+ biomedical and life sciences papers from NIH",
            "requires_key": False,
            "estimated_coverage": "36 million",
            "cost": "FREE",
            "setup_instructions": "No setup required - included by default",
        },
        {
            "provider": "arxiv",
            "name": "arXiv",
            "description": "2M+ pre-prints in physics, math, CS, and quantitative biology",
            "requires_key": False,
            "estimated_coverage": "2 million",
            "cost": "FREE",
            "setup_instructions": "No setup required - included by default",
        },
        {
            "provider": "europepmc",
            "name": "Europe PMC",
            "description": "42M+ life sciences publications from European research",
            "requires_key": False,
            "estimated_coverage": "42 million",
            "cost": "FREE",
            "setup_instructions": "No setup required - included by default",
        },
        {
            "provider": "core",
            "name": "CORE",
            "description": "280M+ open access papers from global repositories",
            "requires_key": False,
            "estimated_coverage": "280 million",
            "cost": "FREE",
            "setup_instructions": "No setup required - included by default",
        },
        {
            "provider": "doaj",
            "name": "DOAJ",
            "description": "2M+ articles from 20,000+ open access journals",
            "requires_key": False,
            "estimated_coverage": "2 million",
            "cost": "FREE",
            "setup_instructions": "No setup required - included by default",
        },
        {
            "provider": "semantic_scholar",
            "name": "Semantic Scholar",
            "description": "200M+ papers with AI-powered citation analysis",
            "requires_key": False,
            "estimated_coverage": "200 million",
            "cost": "FREE",
            "setup_instructions": "No setup required - included by default",
        },
        {
            "provider": "crossref",
            "name": "Crossref",
            "description": "140M+ DOI records covering all academic disciplines",
            "requires_key": False,
            "estimated_coverage": "140 million",
            "cost": "FREE",
            "setup_instructions": "No setup required - included by default",
        },
        {
            "provider": "base",
            "name": "BASE",
            "description": "340M+ academic documents from Bielefeld Academic Search Engine",
            "requires_key": False,
            "estimated_coverage": "340 million",
            "cost": "FREE",
            "setup_instructions": "No setup required - included by default",
        },
        {
            "provider": "google_scholar",
            "name": "Google Scholar",
            "description": "389M+ papers - largest academic database",
            "requires_key": True,
            "estimated_coverage": "389 million",
            "cost": "$50/month (SerpApi)",
            "setup_instructions": "1. Sign up at serpapi.com\n2. Subscribe to Google Scholar API ($50/month)\n3. Copy your API key\n4. Add it here",
        },
        {
            "provider": "scopus",
            "name": "Scopus",
            "description": "84M+ records with excellent citation tracking",
            "requires_key": True,
            "estimated_coverage": "84 million",
            "cost": "Institutional subscription ($5000+/year)",
            "setup_instructions": "1. Get API key from your institution\n2. Visit dev.elsevier.com\n3. Generate API key with Scopus access\n4. Add it here",
        },
        {
            "provider": "web_of_science",
            "name": "Web of Science",
            "description": "90M+ records - gold standard for citation tracking",
            "requires_key": True,
            "estimated_coverage": "90 million",
            "cost": "Institutional subscription ($10,000+/year)",
            "setup_instructions": "1. Get access from your institution\n2. Visit developer.clarivate.com\n3. Generate API access token\n4. Add it here",
        },
        {
            "provider": "ieee_xplore",
            "name": "IEEE Xplore",
            "description": "5M+ computer science and engineering papers",
            "requires_key": True,
            "estimated_coverage": "5 million",
            "cost": "$99/year (personal) or institutional",
            "setup_instructions": "1. Get API key at developer.ieee.org\n2. Subscribe ($99/year personal)\n3. Copy your API key\n4. Add it here",
        },
        {
            "provider": "jstor",
            "name": "JSTOR",
            "description": "12M+ humanities and social sciences articles",
            "requires_key": True,
            "estimated_coverage": "12 million",
            "cost": "Institutional subscription",
            "setup_instructions": "1. Get access from your institution\n2. Contact JSTOR for API access\n3. Add your API key here",
        },
        {
            "provider": "sciencedirect",
            "name": "ScienceDirect",
            "description": "18M+ science and health papers from Elsevier",
            "requires_key": True,
            "estimated_coverage": "18 million",
            "cost": "Institutional subscription (can share with Scopus)",
            "setup_instructions": "1. Use your Scopus API key (same company)\n2. Or get dedicated key from dev.elsevier.com\n3. Add it here",
        },
    ]

    return [DatabaseInfoResponse(**db) for db in databases]


@router.get("/databases/available")
async def get_available_databases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Get list of databases available to the current user.

    Returns all free databases plus any subscription databases
    the user has added API keys for.
    """
    try:
        # Get user's API keys
        user_keys = await api_key_service.list_user_keys(db, current_user.id)

        # Free databases (always available)
        free_databases = [
            "pubmed",
            "arxiv",
            "europepmc",
            "core",
            "doaj",
            "semantic_scholar",
            "crossref",
            "base",
        ]

        # Subscription databases user has access to
        subscription_databases = [
            key["provider"]
            for key in user_keys
            if key["enabled"] and key["verified"]
        ]

        return {
            "free_databases": free_databases,
            "subscription_databases": subscription_databases,
            "total_available": len(free_databases) + len(subscription_databases),
            "estimated_total_papers": "1+ billion (free) + subscription coverage",
        }

    except Exception as e:
        logger.error(f"Error getting available databases: {e}")
        raise HTTPException(status_code=500, detail=str(e))
