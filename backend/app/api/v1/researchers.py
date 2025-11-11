"""Researcher management API endpoints - Tool 4: Reviewer Matcher."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, status
from loguru import logger
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.models.researcher import Researcher
from app.core.security import get_current_user_token, TokenData, require_researcher

router = APIRouter()


# Pydantic schemas for request/response
class ResearcherCreate(BaseModel):
    """Schema for creating a new researcher."""

    orcid: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    institution: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    h_index: Optional[int] = Field(None, ge=0)
    i10_index: Optional[int] = Field(None, ge=0)
    total_citations: int = Field(default=0, ge=0)
    publication_count: int = Field(default=0, ge=0)
    expertise_keywords: Optional[List[str]] = Field(default_factory=list)
    research_domains: Optional[List[str]] = Field(default_factory=list)
    expertise_domains: Optional[dict] = Field(default_factory=dict)
    semantic_scholar_id: Optional[str] = None
    google_scholar_id: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Validate email format."""
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v

    @field_validator("orcid")
    @classmethod
    def validate_orcid(cls, v):
        """Validate ORCID format."""
        if v and not v.replace("-", "").isdigit():
            raise ValueError("ORCID must contain only digits and hyphens")
        return v


class ResearcherUpdate(BaseModel):
    """Schema for updating a researcher."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    institution: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = None
    country: Optional[str] = None
    website: Optional[str] = None
    h_index: Optional[int] = Field(None, ge=0)
    i10_index: Optional[int] = Field(None, ge=0)
    total_citations: Optional[int] = Field(None, ge=0)
    publication_count: Optional[int] = Field(None, ge=0)
    expertise_keywords: Optional[List[str]] = None
    research_domains: Optional[List[str]] = None
    expertise_domains: Optional[dict] = None
    recent_review_count: Optional[int] = Field(None, ge=0)
    total_review_count: Optional[int] = Field(None, ge=0)
    average_review_time_days: Optional[float] = Field(None, ge=0)
    estimated_availability: Optional[float] = Field(None, ge=0.0, le=1.0)
    current_workload: Optional[int] = Field(None, ge=0)
    response_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    semantic_scholar_id: Optional[str] = None
    google_scholar_id: Optional[str] = None


class ResearcherResponse(BaseModel):
    """Schema for researcher response."""

    id: str
    orcid: Optional[str]
    name: str
    email: Optional[str]
    institution: Optional[str]
    department: Optional[str]
    country: Optional[str]
    website: Optional[str]
    h_index: Optional[int]
    i10_index: Optional[int]
    total_citations: int
    publication_count: int
    expertise_keywords: Optional[List[str]]
    research_domains: Optional[List[str]]
    expertise_domains: Optional[dict]
    recent_review_count: int
    total_review_count: int
    average_review_time_days: Optional[float]
    estimated_availability: Optional[float]
    current_workload: int
    response_rate: Optional[float]
    semantic_scholar_id: Optional[str]
    google_scholar_id: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ResearcherListResponse(BaseModel):
    """Schema for paginated researcher list."""

    total: int
    page: int
    page_size: int
    researchers: List[ResearcherResponse]


@router.get("/researchers", response_model=ResearcherListResponse)
async def search_researchers(
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(get_current_user_token),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    keyword: Optional[str] = Query(None, description="Search by expertise keyword"),
    domain: Optional[str] = Query(None, description="Filter by research domain"),
    institution: Optional[str] = Query(None, description="Filter by institution"),
    country: Optional[str] = Query(None, description="Filter by country"),
    min_h_index: Optional[int] = Query(None, ge=0, description="Minimum h-index"),
    min_citations: Optional[int] = Query(None, ge=0, description="Minimum total citations"),
    sort_by: str = Query("h_index", description="Sort field: h_index, citations, name, recent_reviews"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
):
    """
    Search and filter researchers with pagination.

    Features:
    - Keyword search in expertise
    - Filter by domain, institution, country
    - Filter by academic metrics (h-index, citations)
    - Sort by various fields
    - Pagination support
    """
    try:
        # Build base query
        query = select(Researcher)
        conditions = []

        # Apply filters
        if keyword:
            # Search in expertise keywords (case-insensitive)
            conditions.append(
                or_(
                    func.lower(Researcher.name).contains(keyword.lower()),
                    Researcher.expertise_keywords.contains([keyword]),
                    Researcher.research_domains.contains([keyword]),
                )
            )

        if domain:
            conditions.append(Researcher.research_domains.contains([domain]))

        if institution:
            conditions.append(func.lower(Researcher.institution).contains(institution.lower()))

        if country:
            conditions.append(func.lower(Researcher.country) == country.lower())

        if min_h_index is not None:
            conditions.append(Researcher.h_index >= min_h_index)

        if min_citations is not None:
            conditions.append(Researcher.total_citations >= min_citations)

        # Apply conditions
        if conditions:
            query = query.where(and_(*conditions))

        # Count total matching records
        count_query = select(func.count()).select_from(Researcher)
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply sorting
        sort_field_map = {
            "h_index": Researcher.h_index,
            "citations": Researcher.total_citations,
            "name": Researcher.name,
            "recent_reviews": Researcher.recent_review_count,
            "publications": Researcher.publication_count,
            "response_rate": Researcher.response_rate,
        }

        sort_field = sort_field_map.get(sort_by, Researcher.h_index)

        if sort_order.lower() == "asc":
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)

        # Execute query
        result = await db.execute(query)
        researchers = result.scalars().all()

        # Format response
        researcher_responses = [
            ResearcherResponse(
                id=str(r.id),
                orcid=r.orcid,
                name=r.name,
                email=r.email,
                institution=r.institution,
                department=r.department,
                country=r.country,
                website=r.website,
                h_index=r.h_index,
                i10_index=r.i10_index,
                total_citations=r.total_citations,
                publication_count=r.publication_count,
                expertise_keywords=r.expertise_keywords,
                research_domains=r.research_domains,
                expertise_domains=r.expertise_domains,
                recent_review_count=r.recent_review_count,
                total_review_count=r.total_review_count,
                average_review_time_days=r.average_review_time_days,
                estimated_availability=r.estimated_availability,
                current_workload=r.current_workload,
                response_rate=r.response_rate,
                semantic_scholar_id=r.semantic_scholar_id,
                google_scholar_id=r.google_scholar_id,
                created_at=r.created_at.isoformat() if r.created_at else "",
                updated_at=r.updated_at.isoformat() if r.updated_at else "",
            )
            for r in researchers
        ]

        logger.info(f"Found {total} researchers, returning page {page} ({len(researcher_responses)} items)")

        return ResearcherListResponse(
            total=total,
            page=page,
            page_size=page_size,
            researchers=researcher_responses,
        )

    except Exception as e:
        logger.error(f"Error searching researchers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/researchers/{researcher_id}", response_model=ResearcherResponse)
async def get_researcher(
    researcher_id: str,
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(get_current_user_token),
):
    """
    Get detailed researcher profile by ID.

    Returns complete researcher information including:
    - Basic information
    - Academic metrics
    - Expertise and domains
    - Review activity
    - Availability metrics
    """
    try:
        researcher_uuid = UUID(researcher_id)

        result = await db.execute(
            select(Researcher).where(Researcher.id == researcher_uuid)
        )
        researcher = result.scalar_one_or_none()

        if not researcher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Researcher not found: {researcher_id}"
            )

        return ResearcherResponse(
            id=str(researcher.id),
            orcid=researcher.orcid,
            name=researcher.name,
            email=researcher.email,
            institution=researcher.institution,
            department=researcher.department,
            country=researcher.country,
            website=researcher.website,
            h_index=researcher.h_index,
            i10_index=researcher.i10_index,
            total_citations=researcher.total_citations,
            publication_count=researcher.publication_count,
            expertise_keywords=researcher.expertise_keywords,
            research_domains=researcher.research_domains,
            expertise_domains=researcher.expertise_domains,
            recent_review_count=researcher.recent_review_count,
            total_review_count=researcher.total_review_count,
            average_review_time_days=researcher.average_review_time_days,
            estimated_availability=researcher.estimated_availability,
            current_workload=researcher.current_workload,
            response_rate=researcher.response_rate,
            semantic_scholar_id=researcher.semantic_scholar_id,
            google_scholar_id=researcher.google_scholar_id,
            created_at=researcher.created_at.isoformat() if researcher.created_at else "",
            updated_at=researcher.updated_at.isoformat() if researcher.updated_at else "",
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid researcher ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting researcher {researcher_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/researchers", response_model=ResearcherResponse, status_code=status.HTTP_201_CREATED)
async def create_researcher(
    researcher_data: ResearcherCreate,
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(require_researcher),
):
    """
    Add a new researcher to the database.

    Requires researcher or admin role.

    Accepts:
    - Basic information (name, email, institution)
    - Academic metrics (h-index, citations)
    - Expertise keywords and domains
    - External IDs (ORCID, Semantic Scholar, Google Scholar)
    """
    try:
        # Check for duplicate ORCID
        if researcher_data.orcid:
            result = await db.execute(
                select(Researcher).where(Researcher.orcid == researcher_data.orcid)
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Researcher with ORCID {researcher_data.orcid} already exists"
                )

        # Create new researcher
        new_researcher = Researcher(
            orcid=researcher_data.orcid,
            name=researcher_data.name,
            email=researcher_data.email,
            institution=researcher_data.institution,
            department=researcher_data.department,
            country=researcher_data.country,
            website=researcher_data.website,
            h_index=researcher_data.h_index,
            i10_index=researcher_data.i10_index,
            total_citations=researcher_data.total_citations,
            publication_count=researcher_data.publication_count,
            expertise_keywords=researcher_data.expertise_keywords,
            research_domains=researcher_data.research_domains,
            expertise_domains=researcher_data.expertise_domains,
            semantic_scholar_id=researcher_data.semantic_scholar_id,
            google_scholar_id=researcher_data.google_scholar_id,
        )

        db.add(new_researcher)
        await db.commit()
        await db.refresh(new_researcher)

        logger.info(f"Created researcher: {new_researcher.name} (ID: {new_researcher.id})")

        return ResearcherResponse(
            id=str(new_researcher.id),
            orcid=new_researcher.orcid,
            name=new_researcher.name,
            email=new_researcher.email,
            institution=new_researcher.institution,
            department=new_researcher.department,
            country=new_researcher.country,
            website=new_researcher.website,
            h_index=new_researcher.h_index,
            i10_index=new_researcher.i10_index,
            total_citations=new_researcher.total_citations,
            publication_count=new_researcher.publication_count,
            expertise_keywords=new_researcher.expertise_keywords,
            research_domains=new_researcher.research_domains,
            expertise_domains=new_researcher.expertise_domains,
            recent_review_count=new_researcher.recent_review_count,
            total_review_count=new_researcher.total_review_count,
            average_review_time_days=new_researcher.average_review_time_days,
            estimated_availability=new_researcher.estimated_availability,
            current_workload=new_researcher.current_workload,
            response_rate=new_researcher.response_rate,
            semantic_scholar_id=new_researcher.semantic_scholar_id,
            google_scholar_id=new_researcher.google_scholar_id,
            created_at=new_researcher.created_at.isoformat() if new_researcher.created_at else "",
            updated_at=new_researcher.updated_at.isoformat() if new_researcher.updated_at else "",
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating researcher: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/researchers/{researcher_id}", response_model=ResearcherResponse)
async def update_researcher(
    researcher_id: str,
    researcher_data: ResearcherUpdate,
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(require_researcher),
):
    """
    Update an existing researcher's information.

    Requires researcher or admin role.

    All fields are optional - only provided fields will be updated.
    """
    try:
        researcher_uuid = UUID(researcher_id)

        result = await db.execute(
            select(Researcher).where(Researcher.id == researcher_uuid)
        )
        researcher = result.scalar_one_or_none()

        if not researcher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Researcher not found: {researcher_id}"
            )

        # Update fields
        update_data = researcher_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(researcher, field, value)

        await db.commit()
        await db.refresh(researcher)

        logger.info(f"Updated researcher: {researcher.name} (ID: {researcher_id})")

        return ResearcherResponse(
            id=str(researcher.id),
            orcid=researcher.orcid,
            name=researcher.name,
            email=researcher.email,
            institution=researcher.institution,
            department=researcher.department,
            country=researcher.country,
            website=researcher.website,
            h_index=researcher.h_index,
            i10_index=researcher.i10_index,
            total_citations=researcher.total_citations,
            publication_count=researcher.publication_count,
            expertise_keywords=researcher.expertise_keywords,
            research_domains=researcher.research_domains,
            expertise_domains=researcher.expertise_domains,
            recent_review_count=researcher.recent_review_count,
            total_review_count=researcher.total_review_count,
            average_review_time_days=researcher.average_review_time_days,
            estimated_availability=researcher.estimated_availability,
            current_workload=researcher.current_workload,
            response_rate=researcher.response_rate,
            semantic_scholar_id=researcher.semantic_scholar_id,
            google_scholar_id=researcher.google_scholar_id,
            created_at=researcher.created_at.isoformat() if researcher.created_at else "",
            updated_at=researcher.updated_at.isoformat() if researcher.updated_at else "",
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid researcher ID format"
        )
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating researcher {researcher_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/researchers/{researcher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_researcher(
    researcher_id: str,
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(require_researcher),
):
    """
    Delete a researcher from the database.

    Requires researcher or admin role.

    Note: This will also delete associated reviewer matches.
    """
    try:
        researcher_uuid = UUID(researcher_id)

        result = await db.execute(
            select(Researcher).where(Researcher.id == researcher_uuid)
        )
        researcher = result.scalar_one_or_none()

        if not researcher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Researcher not found: {researcher_id}"
            )

        await db.delete(researcher)
        await db.commit()

        logger.info(f"Deleted researcher: {researcher.name} (ID: {researcher_id})")

        return None

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid researcher ID format"
        )
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting researcher {researcher_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
