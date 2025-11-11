"""Reviewer Matcher API endpoints - Tool 4: Expert Reviewer Matching."""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, status
from loguru import logger
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.models.researcher import Researcher
from app.models.reviewer_match import ReviewerMatch, MatchStatus, ConflictType
from app.models.manuscript import Manuscript
from app.core.security import get_current_user_token, TokenData, require_researcher

router = APIRouter()


# Pydantic schemas
class MatchSearchRequest(BaseModel):
    """Request to search for matching reviewers."""

    manuscript_id: str
    required_expertise: List[str] = Field(..., min_items=1, description="Required expertise keywords")
    research_domains: Optional[List[str]] = Field(default_factory=list, description="Research domains")
    exclude_institutions: Optional[List[str]] = Field(default_factory=list, description="Institutions to exclude")
    exclude_countries: Optional[List[str]] = Field(default_factory=list, description="Countries to exclude")
    exclude_researcher_ids: Optional[List[str]] = Field(default_factory=list, description="Specific researchers to exclude")
    min_h_index: int = Field(default=5, ge=0, description="Minimum h-index")
    min_citations: int = Field(default=100, ge=0, description="Minimum citations")
    max_current_workload: int = Field(default=5, ge=0, description="Maximum current workload")
    min_response_rate: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum response rate")
    diversity_preference: float = Field(default=0.3, ge=0.0, le=1.0, description="Weight for diversity (0-1)")
    max_results: int = Field(default=20, ge=1, le=100, description="Maximum results to return")

    @field_validator("manuscript_id")
    @classmethod
    def validate_uuid(cls, v):
        """Validate UUID format."""
        try:
            UUID(v)
        except ValueError:
            raise ValueError("Invalid manuscript ID format")
        return v


class ReviewerMatchResponse(BaseModel):
    """Response schema for reviewer match."""

    id: str
    manuscript_id: str
    researcher_id: str
    researcher_name: str
    researcher_institution: Optional[str]
    researcher_country: Optional[str]
    researcher_h_index: Optional[int]
    researcher_email: Optional[str]
    expertise_score: float
    availability_score: float
    diversity_score: Optional[float]
    overall_score: float
    rank: Optional[int]
    has_conflict: bool
    conflict_types: Optional[List[str]]
    conflict_details: Optional[Dict]
    matching_keywords: Optional[List[str]]
    matching_domains: Optional[List[str]]
    expertise_overlap: Optional[Dict]
    reasoning: Optional[str]
    confidence: Optional[float]
    status: str
    created_at: str

    class Config:
        from_attributes = True


class MatchSearchResponse(BaseModel):
    """Response for match search."""

    manuscript_id: str
    total_candidates: int
    matches: List[ReviewerMatchResponse]  # No quotes needed now
    search_criteria: Dict[str, Any]
    timestamp: str


class InvitationRequest(BaseModel):
    """Request to send reviewer invitation."""

    match_id: str
    custom_message: Optional[str] = None
    deadline_days: int = Field(default=14, ge=1, le=90, description="Days until review deadline")


class InvitationResponse(BaseModel):
    """Response for invitation."""

    match_id: str
    researcher_id: str
    status: str
    invitation_sent_at: str
    message: str


class MatchStatusUpdate(BaseModel):
    """Request to update match status."""

    status: MatchStatus
    notes: Optional[str] = None


class ManuscriptMatchesResponse(BaseModel):
    """Response for all matches for a manuscript."""

    manuscript_id: str
    total_matches: int
    pending: int
    invited: int
    accepted: int
    declined: int
    matches: List[ReviewerMatchResponse]


def calculate_expertise_score(
    researcher: Researcher,
    required_keywords: List[str],
    research_domains: List[str],
) -> tuple[float, List[str], Dict[str, Any]]:
    """
    Calculate expertise match score based on keywords and domains.

    Returns: (score, matching_keywords, overlap_details)
    """
    if not researcher.expertise_keywords and not researcher.research_domains:
        return 0.0, [], {}

    # Keyword matching
    researcher_keywords = set(k.lower() for k in (researcher.expertise_keywords or []))
    required_keywords_lower = set(k.lower() for k in required_keywords)
    matching_keywords = list(researcher_keywords.intersection(required_keywords_lower))

    keyword_score = len(matching_keywords) / len(required_keywords) if required_keywords else 0.0

    # Domain matching
    researcher_domains = set(d.lower() for d in (researcher.research_domains or []))
    required_domains = set(d.lower() for d in research_domains)
    matching_domains = list(researcher_domains.intersection(required_domains))

    domain_score = len(matching_domains) / len(research_domains) if research_domains else 0.0

    # Weighted average (keywords 70%, domains 30%)
    overall_score = (keyword_score * 0.7) + (domain_score * 0.3)

    overlap_details = {
        "keyword_matches": len(matching_keywords),
        "total_keywords": len(required_keywords),
        "domain_matches": len(matching_domains),
        "total_domains": len(research_domains),
    }

    return overall_score, matching_keywords, overlap_details


def calculate_availability_score(researcher: Researcher) -> float:
    """
    Calculate availability score based on workload and review history.

    Factors:
    - Current workload (lower is better)
    - Response rate (higher is better)
    - Recent review count (moderate is best)
    - Estimated availability
    """
    score = 0.0
    factors = []

    # Workload score (inverse)
    workload = researcher.current_workload or 0
    if workload == 0:
        workload_score = 1.0
    elif workload <= 2:
        workload_score = 0.8
    elif workload <= 5:
        workload_score = 0.5
    else:
        workload_score = 0.2
    factors.append(workload_score * 0.4)  # 40% weight

    # Response rate score
    response_rate = researcher.response_rate or 0.5
    factors.append(response_rate * 0.3)  # 30% weight

    # Recent review activity (not too busy, not inactive)
    recent_reviews = researcher.recent_review_count or 0
    if 1 <= recent_reviews <= 5:
        activity_score = 1.0
    elif recent_reviews == 0:
        activity_score = 0.6  # Inactive
    else:
        activity_score = 0.4  # Too busy
    factors.append(activity_score * 0.2)  # 20% weight

    # Estimated availability
    availability = researcher.estimated_availability or 0.5
    factors.append(availability * 0.1)  # 10% weight

    score = sum(factors)
    return min(1.0, max(0.0, score))


def calculate_diversity_score(
    researcher: Researcher,
    existing_matches: List[ReviewerMatch],
) -> float:
    """
    Calculate diversity score to promote reviewer diversity.

    Factors:
    - Geographic diversity (different countries)
    - Institutional diversity (different institutions)
    - Career stage diversity
    """
    if not existing_matches:
        return 1.0  # First match always has perfect diversity

    # Count unique countries and institutions
    countries = set()
    institutions = set()

    for match in existing_matches:
        if match.geographic_region:
            countries.add(match.geographic_region)
        if match.researcher and match.researcher.institution:
            institutions.add(match.researcher.institution)

    # Score based on difference
    diversity_score = 1.0

    # Penalize if same country
    if researcher.country and researcher.country in countries:
        diversity_score -= 0.3

    # Penalize if same institution
    if researcher.institution and researcher.institution in institutions:
        diversity_score -= 0.5

    return max(0.0, diversity_score)


def detect_conflicts(
    researcher: Researcher,
    manuscript: Manuscript,
) -> tuple[bool, float, List[str], Dict[str, Any]]:
    """
    Detect potential conflicts of interest.

    Returns: (has_conflict, conflict_risk, conflict_types, details)
    """
    has_conflict = False
    conflict_risk = 0.0
    conflict_types = []
    details = {}

    # Check institutional conflict
    if researcher.institution and manuscript.author_affiliations:
        for affiliation in manuscript.author_affiliations.values():
            if researcher.institution.lower() in str(affiliation).lower():
                has_conflict = True
                conflict_risk += 0.5
                conflict_types.append(ConflictType.INSTITUTION.value)
                details["institution_match"] = researcher.institution

    # Check co-author conflict (would need manuscript author IDs)
    # This is a simplified check - in production, check against coauthor_ids
    if researcher.coauthor_ids and len(researcher.coauthor_ids) > 0:
        # Placeholder for actual coauthor checking logic
        pass

    # Check if researcher is corresponding author
    if manuscript.corresponding_author_id and researcher.id == manuscript.corresponding_author_id:
        has_conflict = True
        conflict_risk = 1.0
        conflict_types.append(ConflictType.COAUTHOR.value)

    return has_conflict, conflict_risk, conflict_types, details


@router.post("/reviewer-matches/search", response_model=MatchSearchResponse)
async def search_matching_reviewers(
    request: MatchSearchRequest,
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(get_current_user_token),
):
    """
    Search for matching reviewers for a manuscript.

    Algorithm:
    1. Filter candidates by expertise keywords and domains
    2. Apply minimum criteria (h-index, citations, workload)
    3. Calculate multi-factor scores (expertise, availability, diversity)
    4. Detect conflicts of interest
    5. Rank candidates by overall score
    6. Store matches in database

    Returns ranked list of potential reviewers with detailed scores.
    """
    try:
        manuscript_uuid = UUID(request.manuscript_id)

        # Get manuscript
        manuscript_result = await db.execute(
            select(Manuscript).where(Manuscript.id == manuscript_uuid)
        )
        manuscript = manuscript_result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Manuscript not found: {request.manuscript_id}"
            )

        # Build candidate query with filters
        query = select(Researcher)
        conditions = []

        # Expertise matching (required)
        for keyword in request.required_expertise:
            conditions.append(
                or_(
                    Researcher.expertise_keywords.contains([keyword]),
                    Researcher.research_domains.contains([keyword]),
                )
            )

        # Minimum academic metrics
        if request.min_h_index > 0:
            conditions.append(Researcher.h_index >= request.min_h_index)

        if request.min_citations > 0:
            conditions.append(Researcher.total_citations >= request.min_citations)

        # Workload constraint
        conditions.append(Researcher.current_workload <= request.max_current_workload)

        # Response rate filter
        if request.min_response_rate > 0:
            conditions.append(
                or_(
                    Researcher.response_rate >= request.min_response_rate,
                    Researcher.response_rate.is_(None),  # Include researchers without history
                )
            )

        # Exclusion filters
        if request.exclude_institutions:
            for institution in request.exclude_institutions:
                conditions.append(
                    func.lower(Researcher.institution) != institution.lower()
                )

        if request.exclude_countries:
            conditions.append(
                ~Researcher.country.in_(request.exclude_countries)
            )

        if request.exclude_researcher_ids:
            exclude_uuids = [UUID(rid) for rid in request.exclude_researcher_ids]
            conditions.append(~Researcher.id.in_(exclude_uuids))

        # Apply all conditions
        if conditions:
            query = query.where(and_(*conditions))

        # Execute query
        result = await db.execute(query)
        candidates = result.scalars().all()

        logger.info(f"Found {len(candidates)} candidate reviewers for manuscript {request.manuscript_id}")

        # Get existing matches for diversity calculation
        existing_matches_result = await db.execute(
            select(ReviewerMatch).where(ReviewerMatch.manuscript_id == manuscript_uuid)
        )
        existing_matches = existing_matches_result.scalars().all()

        # Score each candidate
        scored_matches = []
        for candidate in candidates:
            # Calculate expertise score
            expertise_score, matching_keywords, overlap = calculate_expertise_score(
                candidate,
                request.required_expertise,
                request.research_domains,
            )

            # Calculate availability score
            availability_score = calculate_availability_score(candidate)

            # Calculate diversity score
            diversity_score = calculate_diversity_score(candidate, existing_matches)

            # Detect conflicts
            has_conflict, conflict_risk, conflict_types, conflict_details = detect_conflicts(
                candidate, manuscript
            )

            # Calculate overall score (weighted average)
            # Expertise: 50%, Availability: 30%, Diversity: 20%
            diversity_weight = request.diversity_preference
            overall_score = (
                expertise_score * 0.5 +
                availability_score * (0.5 - diversity_weight) +
                diversity_score * diversity_weight
            )

            # Penalize for conflicts
            if has_conflict:
                overall_score *= (1.0 - conflict_risk * 0.5)

            # Generate reasoning
            reasoning = f"Expertise match: {expertise_score:.2f}, Availability: {availability_score:.2f}, "
            reasoning += f"Diversity: {diversity_score:.2f}. "
            if has_conflict:
                reasoning += f"Conflict detected: {', '.join(conflict_types)}. "

            scored_matches.append({
                "candidate": candidate,
                "expertise_score": expertise_score,
                "availability_score": availability_score,
                "diversity_score": diversity_score,
                "overall_score": overall_score,
                "has_conflict": has_conflict,
                "conflict_risk": conflict_risk,
                "conflict_types": conflict_types,
                "conflict_details": conflict_details,
                "matching_keywords": matching_keywords,
                "overlap": overlap,
                "reasoning": reasoning,
            })

        # Sort by overall score (descending)
        scored_matches.sort(key=lambda x: x["overall_score"], reverse=True)

        # Limit results
        top_matches = scored_matches[:request.max_results]

        # Save matches to database
        saved_matches = []
        for rank, match_data in enumerate(top_matches, start=1):
            candidate = match_data["candidate"]

            # Create match record
            new_match = ReviewerMatch(
                manuscript_id=manuscript_uuid,
                researcher_id=candidate.id,
                expertise_score=match_data["expertise_score"],
                availability_score=match_data["availability_score"],
                diversity_score=match_data["diversity_score"],
                overall_score=match_data["overall_score"],
                rank=rank,
                conflict_risk=match_data["conflict_risk"],
                has_conflict=match_data["has_conflict"],
                conflict_types=match_data["conflict_types"],
                conflict_details=match_data["conflict_details"],
                matching_keywords=match_data["matching_keywords"],
                matching_domains=request.research_domains if match_data["overlap"]["domain_matches"] > 0 else [],
                expertise_overlap=match_data["overlap"],
                reasoning=match_data["reasoning"],
                confidence=match_data["overall_score"],
                status=MatchStatus.PENDING,
                geographic_region=candidate.country,
                institution_type=candidate.institution,
            )

            db.add(new_match)
            saved_matches.append((new_match, candidate))

        await db.commit()

        # Refresh to get IDs
        for match, _ in saved_matches:
            await db.refresh(match)

        logger.info(f"Saved {len(saved_matches)} reviewer matches for manuscript {request.manuscript_id}")

        # Format response
        match_responses = [
            ReviewerMatchResponse(
                id=str(match.id),
                manuscript_id=str(match.manuscript_id),
                researcher_id=str(match.researcher_id),
                researcher_name=candidate.name,
                researcher_institution=candidate.institution,
                researcher_country=candidate.country,
                researcher_h_index=candidate.h_index,
                researcher_email=candidate.email,
                expertise_score=match.expertise_score,
                availability_score=match.availability_score,
                diversity_score=match.diversity_score,
                overall_score=match.overall_score,
                rank=match.rank,
                has_conflict=match.has_conflict,
                conflict_types=match.conflict_types,
                conflict_details=match.conflict_details,
                matching_keywords=match.matching_keywords,
                matching_domains=match.matching_domains,
                expertise_overlap=match.expertise_overlap,
                reasoning=match.reasoning,
                confidence=match.confidence,
                status=match.status.value,
                created_at=match.created_at.isoformat() if match.created_at else "",
            )
            for match, candidate in saved_matches
        ]

        return MatchSearchResponse(
            manuscript_id=request.manuscript_id,
            total_candidates=len(candidates),
            matches=match_responses,
            search_criteria=request.model_dump(),
            timestamp=datetime.utcnow().isoformat(),
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error searching reviewers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reviewer-matches/{match_id}", response_model=ReviewerMatchResponse)
async def get_match_details(
    match_id: str,
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(get_current_user_token),
):
    """
    Get detailed information about a specific reviewer match.

    Returns complete match details including scores, conflicts, and reasoning.
    """
    try:
        match_uuid = UUID(match_id)

        result = await db.execute(
            select(ReviewerMatch).where(ReviewerMatch.id == match_uuid)
        )
        match = result.scalar_one_or_none()

        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match not found: {match_id}"
            )

        # Get researcher details
        researcher_result = await db.execute(
            select(Researcher).where(Researcher.id == match.researcher_id)
        )
        researcher = researcher_result.scalar_one_or_none()

        if not researcher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Researcher not found for match"
            )

        return ReviewerMatchResponse(
            id=str(match.id),
            manuscript_id=str(match.manuscript_id),
            researcher_id=str(match.researcher_id),
            researcher_name=researcher.name,
            researcher_institution=researcher.institution,
            researcher_country=researcher.country,
            researcher_h_index=researcher.h_index,
            researcher_email=researcher.email,
            expertise_score=match.expertise_score,
            availability_score=match.availability_score,
            diversity_score=match.diversity_score,
            overall_score=match.overall_score,
            rank=match.rank,
            has_conflict=match.has_conflict,
            conflict_types=match.conflict_types,
            conflict_details=match.conflict_details,
            matching_keywords=match.matching_keywords,
            matching_domains=match.matching_domains,
            expertise_overlap=match.expertise_overlap,
            reasoning=match.reasoning,
            confidence=match.confidence,
            status=match.status.value,
            created_at=match.created_at.isoformat() if match.created_at else "",
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid match ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting match details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviewer-matches/invite", response_model=InvitationResponse)
async def send_invitation(
    request: InvitationRequest,
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(require_researcher),
):
    """
    Send a review invitation to a matched reviewer.

    Updates match status to INVITED and records invitation timestamp.

    In production, this would:
    - Send email notification
    - Create notification in system
    - Track invitation in external system
    """
    try:
        match_uuid = UUID(request.match_id)

        result = await db.execute(
            select(ReviewerMatch).where(ReviewerMatch.id == match_uuid)
        )
        match = result.scalar_one_or_none()

        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match not found: {request.match_id}"
            )

        if match.status != MatchStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot invite - match status is {match.status.value}"
            )

        # Update status
        match.status = MatchStatus.INVITED
        match.invitation_sent_at = {"timestamp": datetime.utcnow().isoformat(), "deadline_days": request.deadline_days}

        await db.commit()
        await db.refresh(match)

        logger.info(f"Invitation sent for match {request.match_id} to researcher {match.researcher_id}")

        return InvitationResponse(
            match_id=str(match.id),
            researcher_id=str(match.researcher_id),
            status=match.status.value,
            invitation_sent_at=datetime.utcnow().isoformat(),
            message="Invitation sent successfully",
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid match ID format"
        )
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error sending invitation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/reviewer-matches/{match_id}/status", response_model=ReviewerMatchResponse)
async def update_match_status(
    match_id: str,
    status_update: MatchStatusUpdate,
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(require_researcher),
):
    """
    Update the status of a reviewer match.

    Valid status transitions:
    - PENDING -> INVITED
    - INVITED -> ACCEPTED
    - INVITED -> DECLINED
    - INVITED -> NO_RESPONSE
    - Any -> WITHDRAWN
    """
    try:
        match_uuid = UUID(match_id)

        result = await db.execute(
            select(ReviewerMatch).where(ReviewerMatch.id == match_uuid)
        )
        match = result.scalar_one_or_none()

        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Match not found: {match_id}"
            )

        # Update status
        old_status = match.status
        match.status = status_update.status

        # Update response timestamp if accepted/declined
        if status_update.status in [MatchStatus.ACCEPTED, MatchStatus.DECLINED]:
            match.response_received_at = {"timestamp": datetime.utcnow().isoformat(), "notes": status_update.notes}

        await db.commit()
        await db.refresh(match)

        # Get researcher for response
        researcher_result = await db.execute(
            select(Researcher).where(Researcher.id == match.researcher_id)
        )
        researcher = researcher_result.scalar_one_or_none()

        logger.info(f"Updated match {match_id} status: {old_status.value} -> {status_update.status.value}")

        return ReviewerMatchResponse(
            id=str(match.id),
            manuscript_id=str(match.manuscript_id),
            researcher_id=str(match.researcher_id),
            researcher_name=researcher.name if researcher else "Unknown",
            researcher_institution=researcher.institution if researcher else None,
            researcher_country=researcher.country if researcher else None,
            researcher_h_index=researcher.h_index if researcher else None,
            researcher_email=researcher.email if researcher else None,
            expertise_score=match.expertise_score,
            availability_score=match.availability_score,
            diversity_score=match.diversity_score,
            overall_score=match.overall_score,
            rank=match.rank,
            has_conflict=match.has_conflict,
            conflict_types=match.conflict_types,
            conflict_details=match.conflict_details,
            matching_keywords=match.matching_keywords,
            matching_domains=match.matching_domains,
            expertise_overlap=match.expertise_overlap,
            reasoning=match.reasoning,
            confidence=match.confidence,
            status=match.status.value,
            created_at=match.created_at.isoformat() if match.created_at else "",
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid match ID format"
        )
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating match status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/manuscripts/{manuscript_id}/matches", response_model=ManuscriptMatchesResponse)
async def get_manuscript_matches(
    manuscript_id: str,
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(get_current_user_token),
    status_filter: Optional[MatchStatus] = Query(None, description="Filter by match status"),
):
    """
    Get all reviewer matches for a manuscript.

    Returns:
    - Summary statistics (pending, invited, accepted, declined counts)
    - List of all matches with details
    - Can filter by status
    """
    try:
        manuscript_uuid = UUID(manuscript_id)

        # Build query
        query = select(ReviewerMatch).where(ReviewerMatch.manuscript_id == manuscript_uuid)

        if status_filter:
            query = query.where(ReviewerMatch.status == status_filter)

        query = query.order_by(ReviewerMatch.overall_score.desc())

        result = await db.execute(query)
        matches = result.scalars().all()

        # Calculate statistics
        total = len(matches)
        pending = sum(1 for m in matches if m.status == MatchStatus.PENDING)
        invited = sum(1 for m in matches if m.status == MatchStatus.INVITED)
        accepted = sum(1 for m in matches if m.status == MatchStatus.ACCEPTED)
        declined = sum(1 for m in matches if m.status == MatchStatus.DECLINED)

        # Format matches with researcher details
        match_responses = []
        for match in matches:
            researcher_result = await db.execute(
                select(Researcher).where(Researcher.id == match.researcher_id)
            )
            researcher = researcher_result.scalar_one_or_none()

            if researcher:
                match_responses.append(
                    ReviewerMatchResponse(
                        id=str(match.id),
                        manuscript_id=str(match.manuscript_id),
                        researcher_id=str(match.researcher_id),
                        researcher_name=researcher.name,
                        researcher_institution=researcher.institution,
                        researcher_country=researcher.country,
                        researcher_h_index=researcher.h_index,
                        researcher_email=researcher.email,
                        expertise_score=match.expertise_score,
                        availability_score=match.availability_score,
                        diversity_score=match.diversity_score,
                        overall_score=match.overall_score,
                        rank=match.rank,
                        has_conflict=match.has_conflict,
                        conflict_types=match.conflict_types,
                        conflict_details=match.conflict_details,
                        matching_keywords=match.matching_keywords,
                        matching_domains=match.matching_domains,
                        expertise_overlap=match.expertise_overlap,
                        reasoning=match.reasoning,
                        confidence=match.confidence,
                        status=match.status.value,
                        created_at=match.created_at.isoformat() if match.created_at else "",
                    )
                )

        return ManuscriptMatchesResponse(
            manuscript_id=manuscript_id,
            total_matches=total,
            pending=pending,
            invited=invited,
            accepted=accepted,
            declined=declined,
            matches=match_responses,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid manuscript ID format"
        )
    except Exception as e:
        logger.error(f"Error getting manuscript matches: {e}")
        raise HTTPException(status_code=500, detail=str(e))
