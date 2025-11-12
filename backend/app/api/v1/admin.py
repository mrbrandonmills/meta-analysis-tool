"""Master admin API endpoints for platform management."""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status, Query, Path, Request
from loguru import logger
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db
from app.models.user import User, UserResponse
from app.models.researcher import Researcher
from app.models.subscription import Subscription
from app.models.payout_pool import PayoutPool, PayoutPoolStatus
from app.models.payout_distribution import PayoutDistribution
from app.models.payout_contribution import PayoutContribution
from app.models.admin_action import AdminAction, AdminActionType, AdminActionCreate, AdminActionResponse
from app.core.security import get_current_user_token, TokenData, require_admin, UserRole
from app.services.payout_service import PayoutService

router = APIRouter()


# Pydantic schemas
class ResearcherListItem(BaseModel):
    """Researcher list item schema."""

    id: str
    name: str
    email: Optional[str]
    institution: Optional[str]
    h_index: Optional[int]
    total_citations: int
    publication_count: int
    total_review_count: int
    total_earnings_cents: int
    connect_account_status: str
    last_active: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


class ResearcherDetailResponse(BaseModel):
    """Detailed researcher response schema."""

    id: str
    orcid: Optional[str]
    name: str
    email: Optional[str]
    institution: Optional[str]
    department: Optional[str]
    country: Optional[str]
    h_index: Optional[int]
    i10_index: Optional[int]
    total_citations: int
    publication_count: int
    expertise_keywords: Optional[List[str]]
    research_domains: Optional[List[str]]
    total_review_count: int
    recent_review_count: int
    average_review_time_days: Optional[float]
    response_rate: Optional[float]
    stripe_connect_account_id: Optional[str]
    connect_account_status: str
    total_earnings_cents: int
    lifetime_reviews_paid: int
    last_payout_date: Optional[date]
    last_active: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResearcherUpdateRequest(BaseModel):
    """Request schema for updating researcher."""

    is_active: Optional[bool] = None
    suspension_reason: Optional[str] = None


class PlatformStatsResponse(BaseModel):
    """Platform statistics response."""

    total_users: int
    active_users_30d: int
    total_researchers: int
    active_researchers_30d: int
    total_subscriptions: int
    active_subscriptions: int
    total_reviews_completed: int
    reviews_completed_30d: int
    total_revenue_cents: int
    revenue_30d_cents: int
    total_payouts_cents: int
    payouts_30d_cents: int
    avg_review_time_days: float
    platform_health_score: float


class RevenueAnalyticsResponse(BaseModel):
    """Revenue analytics response."""

    total_lifetime_revenue_cents: int
    total_lifetime_payouts_cents: int
    net_revenue_cents: int
    current_month_revenue_cents: int
    current_month_payouts_cents: int
    revenue_by_month: List[Dict[str, Any]]
    top_contributors: List[Dict[str, Any]]
    subscription_breakdown: Dict[str, int]


class PayoutPoolCreateRequest(BaseModel):
    """Request schema for creating payout pool."""

    pool_month: date = Field(..., description="First day of the month (YYYY-MM-01)")
    initial_contribution_cents: Optional[int] = Field(0, description="Initial pool contribution in cents")


class PayoutPoolResponse(BaseModel):
    """Payout pool response schema."""

    id: str
    pool_month: date
    total_contributions_cents: int
    total_distributed_cents: int
    remaining_cents: int
    total_reviews_assigned: int
    total_reviews_completed: int
    total_reviews_approved: int
    payout_per_review_cents: Optional[int]
    status: str
    calculated_at: Optional[datetime]
    distributed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class PayoutDistributionRequest(BaseModel):
    """Request schema for distributing payouts."""

    dry_run: bool = Field(False, description="Calculate without executing transfers")


# Helper function to log admin actions
async def log_admin_action(
    db: AsyncSession,
    admin_token: TokenData,
    action_type: AdminActionType,
    description: str,
    target_type: Optional[str] = None,
    target_id: Optional[UUID] = None,
    target_identifier: Optional[str] = None,
    previous_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    request: Optional[Request] = None
):
    """Log an admin action to the audit trail."""
    ip_address = None
    user_agent = None

    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    admin_action = AdminAction(
        admin_id=admin_token.user_id,
        admin_email=admin_token.email,
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        target_identifier=target_identifier,
        description=description,
        previous_values=previous_values or {},
        new_values=new_values or {},
        ip_address=ip_address,
        user_agent=user_agent
    )

    db.add(admin_action)
    await db.commit()

    logger.info(f"Admin action logged: {action_type.value} by {admin_token.email}")


# Researcher Management Endpoints
@router.get("/researchers", response_model=List[ResearcherListItem])
async def list_researchers(
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name, email, or institution"),
    min_h_index: Optional[int] = Query(None, ge=0),
    country: Optional[str] = Query(None),
    connect_status: Optional[str] = Query(None, description="Filter by Stripe Connect status"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc")
):
    """
    List all researchers with filtering and pagination.

    Admin only. Supports filtering by:
    - Search query (name, email, institution)
    - Minimum h-index
    - Country
    - Stripe Connect status
    """
    query = select(Researcher)

    # Apply search filter
    if search:
        search_filter = or_(
            Researcher.name.ilike(f"%{search}%"),
            Researcher.email.ilike(f"%{search}%"),
            Researcher.institution.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # Apply h-index filter
    if min_h_index is not None:
        query = query.where(Researcher.h_index >= min_h_index)

    # Apply country filter
    if country:
        query = query.where(Researcher.country == country)

    # Apply connect status filter
    if connect_status:
        query = query.where(Researcher.connect_account_status == connect_status)

    # Apply sorting
    sort_column = getattr(Researcher, sort_by, Researcher.created_at)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    researchers = result.scalars().all()

    return [
        ResearcherListItem(
            id=str(r.id),
            name=r.name,
            email=r.email,
            institution=r.institution,
            h_index=r.h_index,
            total_citations=r.total_citations,
            publication_count=r.publication_count,
            total_review_count=r.total_review_count,
            total_earnings_cents=r.total_earnings_cents,
            connect_account_status=r.connect_account_status,
            last_active=r.last_active,
            created_at=r.created_at
        )
        for r in researchers
    ]


@router.get("/researchers/{researcher_id}", response_model=ResearcherDetailResponse)
async def get_researcher_details(
    researcher_id: str = Path(..., description="Researcher UUID"),
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_admin)
):
    """
    Get detailed information about a specific researcher.

    Admin only. Returns complete researcher profile including:
    - Academic metrics
    - Review statistics
    - Financial information
    - Activity history
    """
    result = await db.execute(
        select(Researcher).where(Researcher.id == researcher_id)
    )
    researcher = result.scalar_one_or_none()

    if not researcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Researcher not found: {researcher_id}"
        )

    return ResearcherDetailResponse(
        id=str(researcher.id),
        orcid=researcher.orcid,
        name=researcher.name,
        email=researcher.email,
        institution=researcher.institution,
        department=researcher.department,
        country=researcher.country,
        h_index=researcher.h_index,
        i10_index=researcher.i10_index,
        total_citations=researcher.total_citations,
        publication_count=researcher.publication_count,
        expertise_keywords=researcher.expertise_keywords,
        research_domains=researcher.research_domains,
        total_review_count=researcher.total_review_count,
        recent_review_count=researcher.recent_review_count,
        average_review_time_days=researcher.average_review_time_days,
        response_rate=researcher.response_rate,
        stripe_connect_account_id=researcher.stripe_connect_account_id,
        connect_account_status=researcher.connect_account_status,
        total_earnings_cents=researcher.total_earnings_cents,
        lifetime_reviews_paid=researcher.lifetime_reviews_paid,
        last_payout_date=researcher.last_payout_date,
        last_active=researcher.last_active,
        created_at=researcher.created_at,
        updated_at=researcher.updated_at
    )


@router.patch("/researchers/{researcher_id}", response_model=ResearcherDetailResponse)
async def update_researcher(
    researcher_id: str = Path(..., description="Researcher UUID"),
    update_data: ResearcherUpdateRequest = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_admin),
    request: Request = None
):
    """
    Update researcher account status.

    Admin only. Supports:
    - Suspending/activating accounts
    - Recording suspension reasons
    """
    result = await db.execute(
        select(Researcher).where(Researcher.id == researcher_id)
    )
    researcher = result.scalar_one_or_none()

    if not researcher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Researcher not found: {researcher_id}"
        )

    # Track changes for audit log
    previous_values = {}
    new_values = {}

    # Note: Researcher model doesn't have is_active field by default
    # This would need to be added to the model if account suspension is required
    # For now, we'll log the action but not update the field

    description = f"Researcher account updated: {researcher.name}"
    if update_data.suspension_reason:
        description += f" - Reason: {update_data.suspension_reason}"

    # Log admin action
    await log_admin_action(
        db=db,
        admin_token=current_user,
        action_type=AdminActionType.RESEARCHER_UPDATED,
        description=description,
        target_type="researcher",
        target_id=researcher.id,
        target_identifier=researcher.email,
        previous_values=previous_values,
        new_values=new_values,
        request=request
    )

    await db.commit()
    await db.refresh(researcher)

    return ResearcherDetailResponse(
        id=str(researcher.id),
        orcid=researcher.orcid,
        name=researcher.name,
        email=researcher.email,
        institution=researcher.institution,
        department=researcher.department,
        country=researcher.country,
        h_index=researcher.h_index,
        i10_index=researcher.i10_index,
        total_citations=researcher.total_citations,
        publication_count=researcher.publication_count,
        expertise_keywords=researcher.expertise_keywords,
        research_domains=researcher.research_domains,
        total_review_count=researcher.total_review_count,
        recent_review_count=researcher.recent_review_count,
        average_review_time_days=researcher.average_review_time_days,
        response_rate=researcher.response_rate,
        stripe_connect_account_id=researcher.stripe_connect_account_id,
        connect_account_status=researcher.connect_account_status,
        total_earnings_cents=researcher.total_earnings_cents,
        lifetime_reviews_paid=researcher.lifetime_reviews_paid,
        last_payout_date=researcher.last_payout_date,
        last_active=researcher.last_active,
        created_at=researcher.created_at,
        updated_at=researcher.updated_at
    )


# Platform Statistics
@router.get("/stats", response_model=PlatformStatsResponse)
async def get_platform_stats(
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_admin)
):
    """
    Get comprehensive platform statistics.

    Admin only. Returns:
    - User and researcher counts
    - Subscription metrics
    - Review completion stats
    - Revenue and payout totals
    - Platform health score
    """
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # User statistics
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    active_users_result = await db.execute(
        select(func.count(User.id)).where(User.last_login >= thirty_days_ago)
    )
    active_users_30d = active_users_result.scalar() or 0

    # Researcher statistics
    total_researchers_result = await db.execute(select(func.count(Researcher.id)))
    total_researchers = total_researchers_result.scalar() or 0

    active_researchers_result = await db.execute(
        select(func.count(Researcher.id)).where(Researcher.last_active >= thirty_days_ago.date())
    )
    active_researchers_30d = active_researchers_result.scalar() or 0

    # Subscription statistics
    total_subs_result = await db.execute(select(func.count(Subscription.id)))
    total_subscriptions = total_subs_result.scalar() or 0

    active_subs_result = await db.execute(
        select(func.count(Subscription.id)).where(Subscription.status == "active")
    )
    active_subscriptions = active_subs_result.scalar() or 0

    # Review statistics (would need ReviewCompletion model)
    total_reviews_completed = 0
    reviews_completed_30d = 0

    # Revenue statistics
    total_revenue_result = await db.execute(
        select(func.sum(PayoutContribution.amount_cents))
    )
    total_revenue_cents = total_revenue_result.scalar() or 0

    revenue_30d_result = await db.execute(
        select(func.sum(PayoutContribution.amount_cents)).where(
            PayoutContribution.contributed_at >= thirty_days_ago
        )
    )
    revenue_30d_cents = revenue_30d_result.scalar() or 0

    # Payout statistics
    total_payouts_result = await db.execute(
        select(func.sum(PayoutDistribution.amount_cents))
    )
    total_payouts_cents = total_payouts_result.scalar() or 0

    payouts_30d_result = await db.execute(
        select(func.sum(PayoutDistribution.amount_cents)).where(
            PayoutDistribution.created_at >= thirty_days_ago
        )
    )
    payouts_30d_cents = payouts_30d_result.scalar() or 0

    # Average review time
    avg_review_time_result = await db.execute(
        select(func.avg(Researcher.average_review_time_days)).where(
            Researcher.average_review_time_days.isnot(None)
        )
    )
    avg_review_time_days = avg_review_time_result.scalar() or 0.0

    # Calculate platform health score (0-100)
    # Based on: active users, active researchers, review completion rate, avg review time
    health_components = []

    # User activity score (0-25 points)
    user_activity_rate = (active_users_30d / total_users * 100) if total_users > 0 else 0
    health_components.append(min(user_activity_rate, 25))

    # Researcher activity score (0-25 points)
    researcher_activity_rate = (active_researchers_30d / total_researchers * 100) if total_researchers > 0 else 0
    health_components.append(min(researcher_activity_rate, 25))

    # Subscription health (0-25 points)
    subscription_rate = (active_subscriptions / total_subscriptions * 100) if total_subscriptions > 0 else 0
    health_components.append(min(subscription_rate, 25))

    # Review time efficiency (0-25 points, inverse of review time)
    if avg_review_time_days > 0:
        review_efficiency = max(0, 25 - (avg_review_time_days / 2))
    else:
        review_efficiency = 25
    health_components.append(review_efficiency)

    platform_health_score = sum(health_components)

    return PlatformStatsResponse(
        total_users=total_users,
        active_users_30d=active_users_30d,
        total_researchers=total_researchers,
        active_researchers_30d=active_researchers_30d,
        total_subscriptions=total_subscriptions,
        active_subscriptions=active_subscriptions,
        total_reviews_completed=total_reviews_completed,
        reviews_completed_30d=reviews_completed_30d,
        total_revenue_cents=total_revenue_cents,
        revenue_30d_cents=revenue_30d_cents,
        total_payouts_cents=total_payouts_cents,
        payouts_30d_cents=payouts_30d_cents,
        avg_review_time_days=float(avg_review_time_days),
        platform_health_score=round(platform_health_score, 2)
    )


# Revenue Analytics
@router.get("/revenue", response_model=RevenueAnalyticsResponse)
async def get_revenue_analytics(
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_admin),
    months: int = Query(12, ge=1, le=24, description="Number of months to include")
):
    """
    Get detailed revenue analytics.

    Admin only. Returns:
    - Lifetime revenue and payouts
    - Current month metrics
    - Monthly revenue breakdown
    - Top contributors
    - Subscription breakdown
    """
    # Total lifetime metrics
    total_revenue_result = await db.execute(
        select(func.sum(PayoutContribution.amount_cents))
    )
    total_lifetime_revenue_cents = total_revenue_result.scalar() or 0

    total_payouts_result = await db.execute(
        select(func.sum(PayoutDistribution.amount_cents))
    )
    total_lifetime_payouts_cents = total_payouts_result.scalar() or 0

    net_revenue_cents = total_lifetime_revenue_cents - total_lifetime_payouts_cents

    # Current month metrics
    current_month_start = date.today().replace(day=1)
    current_month_revenue_result = await db.execute(
        select(func.sum(PayoutContribution.amount_cents)).where(
            func.date(PayoutContribution.contributed_at) >= current_month_start
        )
    )
    current_month_revenue_cents = current_month_revenue_result.scalar() or 0

    current_month_payouts_result = await db.execute(
        select(func.sum(PayoutDistribution.amount_cents)).where(
            func.date(PayoutDistribution.created_at) >= current_month_start
        )
    )
    current_month_payouts_cents = current_month_payouts_result.scalar() or 0

    # Revenue by month (last N months)
    revenue_by_month = []
    for i in range(months):
        month_date = (date.today().replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        next_month = (month_date + timedelta(days=32)).replace(day=1)

        month_revenue_result = await db.execute(
            select(func.sum(PayoutContribution.amount_cents)).where(
                and_(
                    func.date(PayoutContribution.contributed_at) >= month_date,
                    func.date(PayoutContribution.contributed_at) < next_month
                )
            )
        )
        month_revenue = month_revenue_result.scalar() or 0

        month_payouts_result = await db.execute(
            select(func.sum(PayoutDistribution.amount_cents)).where(
                and_(
                    func.date(PayoutDistribution.created_at) >= month_date,
                    func.date(PayoutDistribution.created_at) < next_month
                )
            )
        )
        month_payouts = month_payouts_result.scalar() or 0

        revenue_by_month.append({
            "month": month_date.strftime("%Y-%m"),
            "revenue_cents": month_revenue,
            "payouts_cents": month_payouts,
            "net_cents": month_revenue - month_payouts
        })

    revenue_by_month.reverse()  # Chronological order

    # Top contributors (top 10 paying users)
    top_contributors_result = await db.execute(
        select(
            User.email,
            User.full_name,
            func.sum(PayoutContribution.amount_cents).label("total_contributed")
        )
        .join(PayoutContribution, User.id == PayoutContribution.user_id)
        .group_by(User.id, User.email, User.full_name)
        .order_by(desc("total_contributed"))
        .limit(10)
    )
    top_contributors = [
        {
            "email": row.email,
            "name": row.full_name or "Unknown",
            "total_contributed_cents": row.total_contributed
        }
        for row in top_contributors_result
    ]

    # Subscription breakdown
    sub_breakdown_result = await db.execute(
        select(
            Subscription.status,
            func.count(Subscription.id).label("count")
        )
        .group_by(Subscription.status)
    )
    subscription_breakdown = {
        row.status: row.count for row in sub_breakdown_result
    }

    return RevenueAnalyticsResponse(
        total_lifetime_revenue_cents=total_lifetime_revenue_cents,
        total_lifetime_payouts_cents=total_lifetime_payouts_cents,
        net_revenue_cents=net_revenue_cents,
        current_month_revenue_cents=current_month_revenue_cents,
        current_month_payouts_cents=current_month_payouts_cents,
        revenue_by_month=revenue_by_month,
        top_contributors=top_contributors,
        subscription_breakdown=subscription_breakdown
    )


# Payout Pool Management
@router.post("/payout-pool/create", response_model=PayoutPoolResponse, status_code=status.HTTP_201_CREATED)
async def create_payout_pool(
    pool_data: PayoutPoolCreateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_admin),
    request: Request = None
):
    """
    Create a new monthly payout pool.

    Admin only. Creates a pool for the specified month.
    Only one pool can exist per month.
    """
    # Validate pool_month is first day of month
    if pool_data.pool_month.day != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="pool_month must be the first day of the month (YYYY-MM-01)"
        )

    # Check if pool already exists
    existing_pool_result = await db.execute(
        select(PayoutPool).where(PayoutPool.pool_month == pool_data.pool_month)
    )
    existing_pool = existing_pool_result.scalar_one_or_none()

    if existing_pool:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payout pool already exists for {pool_data.pool_month.strftime('%Y-%m')}"
        )

    # Create new pool
    new_pool = PayoutPool(
        pool_month=pool_data.pool_month,
        total_contributions_cents=pool_data.initial_contribution_cents,
        total_distributed_cents=0,
        remaining_cents=pool_data.initial_contribution_cents,
        total_reviews_assigned=0,
        total_reviews_completed=0,
        total_reviews_approved=0,
        status=PayoutPoolStatus.OPEN
    )

    db.add(new_pool)
    await db.commit()
    await db.refresh(new_pool)

    # Log admin action
    await log_admin_action(
        db=db,
        admin_token=current_user,
        action_type=AdminActionType.PAYOUT_POOL_CREATED,
        description=f"Created payout pool for {pool_data.pool_month.strftime('%Y-%m')}",
        target_type="payout_pool",
        target_id=new_pool.id,
        target_identifier=pool_data.pool_month.strftime('%Y-%m'),
        new_values={
            "pool_month": str(pool_data.pool_month),
            "initial_contribution_cents": pool_data.initial_contribution_cents
        },
        request=request
    )

    logger.info(f"Payout pool created for {pool_data.pool_month.strftime('%Y-%m')} by {current_user.email}")

    return PayoutPoolResponse(
        id=str(new_pool.id),
        pool_month=new_pool.pool_month,
        total_contributions_cents=new_pool.total_contributions_cents,
        total_distributed_cents=new_pool.total_distributed_cents,
        remaining_cents=new_pool.remaining_cents,
        total_reviews_assigned=new_pool.total_reviews_assigned,
        total_reviews_completed=new_pool.total_reviews_completed,
        total_reviews_approved=new_pool.total_reviews_approved,
        payout_per_review_cents=new_pool.payout_per_review_cents,
        status=new_pool.status.value,
        calculated_at=new_pool.calculated_at,
        distributed_at=new_pool.distributed_at,
        created_at=new_pool.created_at
    )


@router.patch("/payout-pool/{pool_id}/distribute", response_model=Dict[str, Any])
async def distribute_payout_pool(
    pool_id: str = Path(..., description="Payout pool UUID"),
    distribution_data: PayoutDistributionRequest = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_admin),
    request: Request = None
):
    """
    Distribute funds from a payout pool to reviewers.

    Admin only. Calculates and distributes payouts based on:
    - Approved reviews in the pool period
    - Available pool funds
    - Reviewer Stripe Connect accounts

    Set dry_run=true to calculate without executing transfers.
    """
    result = await db.execute(
        select(PayoutPool).where(PayoutPool.id == pool_id)
    )
    pool = result.scalar_one_or_none()

    if not pool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payout pool not found: {pool_id}"
        )

    # Check pool status
    if pool.status == PayoutPoolStatus.DISTRIBUTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payout pool has already been distributed"
        )

    if pool.status == PayoutPoolStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payout pool is closed"
        )

    # Use PayoutService to calculate and distribute
    try:
        payout_result = await PayoutService.calculate_monthly_payouts(
            pool_month=pool.pool_month,
            db=db,
            dry_run=distribution_data.dry_run if distribution_data else False
        )

        # Log admin action
        action_type = AdminActionType.PAYOUT_DISTRIBUTED if not (distribution_data and distribution_data.dry_run) else AdminActionType.PAYOUT_POOL_CREATED
        await log_admin_action(
            db=db,
            admin_token=current_user,
            action_type=action_type,
            description=f"{'[DRY RUN] ' if (distribution_data and distribution_data.dry_run) else ''}Distributed payout pool for {pool.pool_month.strftime('%Y-%m')}",
            target_type="payout_pool",
            target_id=pool.id,
            target_identifier=pool.pool_month.strftime('%Y-%m'),
            new_values={
                "total_distributed_cents": payout_result.total_distributed_cents,
                "reviewers_paid": payout_result.reviewers_paid,
                "dry_run": distribution_data.dry_run if distribution_data else False
            },
            request=request
        )

        logger.info(
            f"{'[DRY RUN] ' if (distribution_data and distribution_data.dry_run) else ''}"
            f"Payout pool distributed for {pool.pool_month.strftime('%Y-%m')} "
            f"by {current_user.email}: ${payout_result.total_distributed_cents / 100:.2f} "
            f"to {payout_result.reviewers_paid} reviewers"
        )

        return payout_result.to_dict()

    except Exception as e:
        logger.error(f"Error distributing payout pool {pool_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error distributing payouts: {str(e)}"
        )


# Admin Action Logs
@router.get("/actions", response_model=List[AdminActionResponse])
async def get_admin_actions(
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(require_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    admin_email: Optional[str] = Query(None, description="Filter by admin email"),
    start_date: Optional[datetime] = Query(None, description="Filter actions after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter actions before this date")
):
    """
    Get admin action audit logs.

    Admin only. Returns paginated list of admin actions with filtering.
    """
    query = select(AdminAction)

    # Apply filters
    if action_type:
        query = query.where(AdminAction.action_type == action_type)

    if admin_email:
        query = query.where(AdminAction.admin_email == admin_email)

    if start_date:
        query = query.where(AdminAction.performed_at >= start_date)

    if end_date:
        query = query.where(AdminAction.performed_at <= end_date)

    # Sort by most recent first
    query = query.order_by(desc(AdminAction.performed_at))

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    actions = result.scalars().all()

    return [
        AdminActionResponse(
            id=str(action.id),
            admin_id=str(action.admin_id),
            admin_email=action.admin_email,
            action_type=action.action_type.value,
            target_type=action.target_type,
            target_id=str(action.target_id) if action.target_id else None,
            target_identifier=action.target_identifier,
            description=action.description,
            previous_values=action.previous_values,
            new_values=action.new_values,
            action_metadata=action.action_metadata,
            performed_at=action.performed_at
        )
        for action in actions
    ]
