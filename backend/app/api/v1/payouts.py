"""Payout management API endpoints."""

from typing import Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.models.payout_pool import PayoutPool, PayoutPoolStatus
from app.models.payout_distribution import PayoutDistribution
from app.models.researcher import Researcher
from app.core.security import get_current_user_token, TokenData, require_admin
from app.services.payout_service import PayoutService

router = APIRouter()


# Pydantic schemas
class PayoutCalculationRequest(BaseModel):
    """Schema for payout calculation request."""

    pool_month: date = Field(..., description="First day of month to process (YYYY-MM-01)")
    dry_run: bool = Field(default=False, description="Calculate without executing transfers")


class PayoutPoolResponse(BaseModel):
    """Schema for payout pool response."""

    id: str
    pool_month: date
    total_contributions: float
    total_distributed: float
    remaining: float
    total_reviews_assigned: int
    total_reviews_completed: int
    total_reviews_approved: int
    payout_per_review: Optional[float]
    status: str
    calculated_at: Optional[datetime]
    distributed_at: Optional[datetime]

    class Config:
        from_attributes = True


class EarningsResponse(BaseModel):
    """Schema for earnings response."""

    lifetime_earnings: float
    lifetime_reviews_paid: int
    last_payout_date: Optional[str]
    current_month_pending: int
    estimated_current_month_payout: float
    earnings_history: list


# API Endpoints
@router.post("/calculate-monthly")
async def calculate_monthly_payouts(
    calculation_request: PayoutCalculationRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_admin)
):
    """
    Calculate and distribute monthly payouts (Admin/Cron only).

    This endpoint:
    1. Retrieves the payout pool for the specified month
    2. Calculates payout per review
    3. Creates Stripe Connect transfers
    4. Updates database records
    5. Closes the pool and creates next month's pool
    """
    try:
        result = await PayoutService.calculate_monthly_payouts(
            pool_month=calculation_request.pool_month,
            db=db,
            dry_run=calculation_request.dry_run
        )

        return result.to_dict()

    except Exception as e:
        logger.error(f"Error calculating payouts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/earnings", response_model=EarningsResponse)
async def get_my_earnings(
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """
    Get current user's earnings summary.

    Returns lifetime earnings, current month pending, and earnings history.
    """
    try:
        # Find researcher associated with user
        # Note: This assumes user_id maps to researcher somehow
        # You may need to adjust based on your user-researcher relationship
        result = await db.execute(
            select(Researcher).where(Researcher.email == current_user.email)
        )
        researcher = result.scalar_one_or_none()

        if not researcher:
            # Return empty earnings for non-researchers
            return EarningsResponse(
                lifetime_earnings=0,
                lifetime_reviews_paid=0,
                last_payout_date=None,
                current_month_pending=0,
                estimated_current_month_payout=0,
                earnings_history=[]
            )

        earnings = await PayoutService.get_reviewer_earnings(
            reviewer_id=researcher.id,
            db=db
        )

        return EarningsResponse(**earnings)

    except Exception as e:
        logger.error(f"Error fetching earnings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/pool/{year}/{month}", response_model=PayoutPoolResponse)
async def get_payout_pool(
    year: int = Path(..., ge=2020, le=2100),
    month: int = Path(..., ge=1, le=12),
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """
    Get payout pool details for a specific month.

    Returns pool statistics, contribution totals, and distribution status.
    """
    try:
        pool_date = date(year, month, 1)

        result = await db.execute(
            select(PayoutPool).where(PayoutPool.pool_month == pool_date)
        )
        pool = result.scalar_one_or_none()

        if not pool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No payout pool found for {year}-{month:02d}"
            )

        return PayoutPoolResponse(
            id=str(pool.id),
            pool_month=pool.pool_month,
            total_contributions=pool.total_contributions_cents / 100,
            total_distributed=pool.total_distributed_cents / 100,
            remaining=pool.remaining_cents / 100,
            total_reviews_assigned=pool.total_reviews_assigned,
            total_reviews_completed=pool.total_reviews_completed,
            total_reviews_approved=pool.total_reviews_approved,
            payout_per_review=pool.payout_per_review_cents / 100 if pool.payout_per_review_cents else None,
            status=pool.status.value,
            calculated_at=pool.calculated_at,
            distributed_at=pool.distributed_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payout pool: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/distribute")
async def distribute_payouts(
    pool_month: date,
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_admin)
):
    """
    Manually trigger payout distribution for a specific month (Admin only).

    Alias for calculate-monthly with dry_run=False.
    """
    try:
        result = await PayoutService.calculate_monthly_payouts(
            pool_month=pool_month,
            db=db,
            dry_run=False
        )

        return result.to_dict()

    except Exception as e:
        logger.error(f"Error distributing payouts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/current-pool", response_model=PayoutPoolResponse)
async def get_current_pool(
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """
    Get the current month's payout pool.
    """
    try:
        current_month = date.today().replace(day=1)

        result = await db.execute(
            select(PayoutPool).where(
                PayoutPool.pool_month == current_month
            )
        )
        pool = result.scalar_one_or_none()

        if not pool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No payout pool found for current month"
            )

        return PayoutPoolResponse(
            id=str(pool.id),
            pool_month=pool.pool_month,
            total_contributions=pool.total_contributions_cents / 100,
            total_distributed=pool.total_distributed_cents / 100,
            remaining=pool.remaining_cents / 100,
            total_reviews_assigned=pool.total_reviews_assigned,
            total_reviews_completed=pool.total_reviews_completed,
            total_reviews_approved=pool.total_reviews_approved,
            payout_per_review=pool.payout_per_review_cents / 100 if pool.payout_per_review_cents else None,
            status=pool.status.value,
            calculated_at=pool.calculated_at,
            distributed_at=pool.distributed_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching current pool: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
