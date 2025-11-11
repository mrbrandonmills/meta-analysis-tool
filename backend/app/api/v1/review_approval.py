"""Review approval API endpoints for editor workflow."""

from typing import List, Optional
from datetime import datetime, date
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status, Query
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.models.peer_review import PeerReview, ReviewStatus
from app.models.review_completion import ReviewCompletion, PayoutStatus
from app.models.payout_pool import PayoutPool, PayoutPoolStatus
from app.models.manuscript import Manuscript
from app.models.researcher import Researcher
from app.core.security import get_current_user_token, TokenData, require_editor

router = APIRouter()


# Pydantic schemas
class ReviewApprovalRequest(BaseModel):
    """Schema for review approval request."""

    approved: bool = Field(..., description="True to approve, False to reject")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Quality score 0-1")
    completeness_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    constructiveness_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    approval_notes: Optional[str] = None
    eligible_for_payout: bool = Field(default=True, description="Whether review is eligible for payout")
    ineligibility_reason: Optional[str] = None


class ReviewApprovalResponse(BaseModel):
    """Schema for review approval response."""

    review_id: str
    editor_approved: bool
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    eligible_for_payout: bool
    added_to_pool: Optional[str]
    estimated_payout: Optional[float]


class PendingReviewResponse(BaseModel):
    """Schema for pending review response."""

    review_id: str
    manuscript_id: str
    manuscript_title: str
    reviewer_name: Optional[str]
    submitted_at: Optional[datetime]
    overall_score: Optional[float]
    recommendation: Optional[str]
    review_preview: dict


# Helper function
async def get_current_payout_pool(db: AsyncSession) -> PayoutPool:
    """Get or create the current month's payout pool."""
    current_month = date.today().replace(day=1)

    result = await db.execute(
        select(PayoutPool).where(
            PayoutPool.pool_month == current_month,
            PayoutPool.status == PayoutPoolStatus.OPEN
        )
    )
    pool = result.scalar_one_or_none()

    if not pool:
        pool = PayoutPool(
            pool_month=current_month,
            status=PayoutPoolStatus.OPEN
        )
        db.add(pool)
        await db.commit()
        await db.refresh(pool)
        logger.info(f"Created new payout pool for {current_month}")

    return pool


# API Endpoints
@router.post("/{review_id}/approve", response_model=ReviewApprovalResponse)
async def approve_review(
    review_id: UUID,
    approval_data: ReviewApprovalRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_editor)
):
    """
    Approve or reject a peer review for payout eligibility (Editor only).

    When approved:
    1. Updates peer_review record
    2. Creates review_completion record
    3. Links to current month's payout pool
    4. Increments pool's approved review count
    """
    try:
        # Get review
        result = await db.execute(
            select(PeerReview).where(PeerReview.id == review_id)
        )
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Verify review is submitted
        if review.status != ReviewStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Review must be submitted before approval. Current status: {review.status.value}"
            )

        # Check if already approved
        if review.editor_approved:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Review has already been approved"
            )

        # Update peer review
        review.editor_approved = approval_data.approved
        review.approved_by = UUID(current_user.user_id)
        review.approved_at = datetime.utcnow()
        review.approval_notes = approval_data.approval_notes
        review.eligible_for_payout = approval_data.eligible_for_payout if approval_data.approved else False

        pool = None
        estimated_payout = None

        if approval_data.approved:
            # Get current payout pool
            pool = await get_current_payout_pool(db)

            # Create review completion record
            completion = ReviewCompletion(
                pool_id=pool.id,
                peer_review_id=review.id,
                reviewer_id=review.reviewer_id,
                manuscript_id=review.manuscript_id,
                editor_id=UUID(current_user.user_id),
                approved_at=datetime.utcnow(),
                approval_notes=approval_data.approval_notes,
                quality_score=approval_data.quality_score,
                completeness_score=approval_data.completeness_score,
                constructiveness_score=approval_data.constructiveness_score,
                eligible_for_payout=approval_data.eligible_for_payout,
                ineligibility_reason=approval_data.ineligibility_reason,
                payout_status=PayoutStatus.PENDING
            )
            db.add(completion)

            # Increment pool counters
            pool.total_reviews_approved += 1

            # Estimate payout
            if pool.total_contributions_cents > 0 and pool.total_reviews_approved > 0:
                estimated_payout = pool.total_contributions_cents / pool.total_reviews_approved / 100

            logger.info(f"Approved review {review_id} for payout in pool {pool.pool_month}")
        else:
            logger.info(f"Rejected review {review_id}")

        await db.commit()
        await db.refresh(review)

        return ReviewApprovalResponse(
            review_id=str(review.id),
            editor_approved=review.editor_approved,
            approved_by=str(review.approved_by) if review.approved_by else None,
            approved_at=review.approved_at,
            eligible_for_payout=review.eligible_for_payout,
            added_to_pool=str(pool.pool_month) if pool else None,
            estimated_payout=estimated_payout
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving review: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{review_id}/reject", response_model=ReviewApprovalResponse)
async def reject_review(
    review_id: UUID,
    rejection_reason: str = Query(..., description="Reason for rejection"),
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_editor)
):
    """
    Reject a review (not eligible for payout).

    Shortcut endpoint for rejection without full approval data.
    """
    approval_data = ReviewApprovalRequest(
        approved=False,
        approval_notes=rejection_reason,
        eligible_for_payout=False,
        ineligibility_reason=rejection_reason
    )

    return await approve_review(review_id, approval_data, db, current_user)


@router.get("/pending", response_model=List[PendingReviewResponse])
async def get_pending_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_editor)
):
    """
    Get all reviews awaiting editor approval.

    Returns reviews that are submitted but not yet approved.
    """
    try:
        result = await db.execute(
            select(PeerReview).where(
                and_(
                    PeerReview.status == ReviewStatus.SUBMITTED,
                    PeerReview.editor_approved == False
                )
            ).offset(skip).limit(limit).order_by(PeerReview.submission_date.asc())
        )
        reviews = result.scalars().all()

        pending_reviews = []
        for review in reviews:
            # Get manuscript
            result = await db.execute(
                select(Manuscript).where(Manuscript.id == review.manuscript_id)
            )
            manuscript = result.scalar_one_or_none()

            # Get reviewer name
            reviewer_name = None
            if review.reviewer_id:
                result = await db.execute(
                    select(Researcher).where(Researcher.id == review.reviewer_id)
                )
                reviewer = result.scalar_one_or_none()
                if reviewer:
                    reviewer_name = reviewer.name

            pending_reviews.append(PendingReviewResponse(
                review_id=str(review.id),
                manuscript_id=str(review.manuscript_id),
                manuscript_title=manuscript.title if manuscript else "Unknown",
                reviewer_name=reviewer_name,
                submitted_at=review.submission_date,
                overall_score=review.overall_score,
                recommendation=review.recommendation.value if review.recommendation else None,
                review_preview={
                    'strengths_count': len(review.strengths.split('\n')) if review.strengths else 0,
                    'weaknesses_count': len(review.weaknesses.split('\n')) if review.weaknesses else 0,
                    'word_count': len(review.review_text.split()) if review.review_text else 0
                }
            ))

        return pending_reviews

    except Exception as e:
        logger.error(f"Error fetching pending reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{review_id}/details")
async def get_review_details(
    review_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_editor)
):
    """
    Get full details of a review for approval decision.

    Returns complete review content for editor evaluation.
    """
    try:
        result = await db.execute(
            select(PeerReview).where(PeerReview.id == review_id)
        )
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Get manuscript
        result = await db.execute(
            select(Manuscript).where(Manuscript.id == review.manuscript_id)
        )
        manuscript = result.scalar_one_or_none()

        # Get reviewer
        reviewer = None
        if review.reviewer_id:
            result = await db.execute(
                select(Researcher).where(Researcher.id == review.reviewer_id)
            )
            reviewer = result.scalar_one_or_none()

        return {
            'review': {
                'id': str(review.id),
                'status': review.status.value,
                'submission_date': review.submission_date.isoformat() if review.submission_date else None,
                'overall_score': review.overall_score,
                'recommendation': review.recommendation.value if review.recommendation else None,
                'review_text': review.review_text,
                'strengths': review.strengths,
                'weaknesses': review.weaknesses,
                'detailed_comments': review.detailed_comments,
                'confidence': review.confidence
            },
            'manuscript': {
                'id': str(manuscript.id),
                'title': manuscript.title,
                'abstract': manuscript.abstract[:500] + '...' if manuscript and len(manuscript.abstract) > 500 else manuscript.abstract
            } if manuscript else None,
            'reviewer': {
                'name': reviewer.name if reviewer else "Anonymous",
                'h_index': reviewer.h_index,
                'institution': reviewer.institution
            } if reviewer else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching review details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
