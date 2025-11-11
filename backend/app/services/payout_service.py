"""Payout calculation and distribution service."""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from collections import defaultdict
from uuid import UUID

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import stripe

from app.models.payout_pool import PayoutPool, PayoutPoolStatus
from app.models.payout_contribution import PayoutContribution
from app.models.review_completion import ReviewCompletion, PayoutStatus
from app.models.payout_distribution import PayoutDistribution, TransferStatus
from app.models.researcher import Researcher
from app.core.stripe_client import StripeService


class PayoutCalculationResult:
    """Result of payout calculation."""

    def __init__(
        self,
        pool_month: date,
        status: str,
        total_pool_cents: int = 0,
        total_distributed_cents: int = 0,
        payout_per_review_cents: int = 0,
        approved_reviews_count: int = 0,
        unique_reviewers_count: int = 0,
        distributions: List[PayoutDistribution] = None,
        failed_distributions: List[Dict[str, Any]] = None,
        reason: Optional[str] = None
    ):
        self.pool_month = pool_month
        self.status = status
        self.total_pool_cents = total_pool_cents
        self.total_distributed_cents = total_distributed_cents
        self.payout_per_review_cents = payout_per_review_cents
        self.approved_reviews_count = approved_reviews_count
        self.unique_reviewers_count = unique_reviewers_count
        self.distributions = distributions or []
        self.failed_distributions = failed_distributions or []
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'pool_month': self.pool_month.isoformat(),
            'calculation_status': self.status,
            'summary': {
                'total_pool_amount': self.total_pool_cents / 100,
                'approved_reviews_count': self.approved_reviews_count,
                'payout_per_review': self.payout_per_review_cents / 100,
                'unique_reviewers': self.unique_reviewers_count,
                'total_distributed': self.total_distributed_cents / 100
            },
            'distributions': [
                {
                    'reviewer_id': str(d.reviewer_id),
                    'approved_reviews': d.approved_reviews_count,
                    'payout_amount': d.total_payout_cents / 100,
                    'stripe_transfer_id': d.stripe_transfer_id,
                    'status': d.status.value
                }
                for d in self.distributions
            ],
            'failed_distributions': self.failed_distributions,
            'reason': self.reason
        }


class PayoutService:
    """Service for payout calculation and distribution."""

    @staticmethod
    async def calculate_monthly_payouts(
        pool_month: date,
        db: AsyncSession,
        dry_run: bool = False
    ) -> PayoutCalculationResult:
        """
        Calculate and distribute monthly payouts.

        Args:
            pool_month: First day of the month to process
            db: Database session
            dry_run: If True, calculate but don't execute transfers

        Returns:
            PayoutCalculationResult with summary and distributions
        """
        logger.info(f"Starting payout calculation for {pool_month} (dry_run={dry_run})")

        # Step 1: Retrieve the payout pool
        result = await db.execute(
            select(PayoutPool).where(
                PayoutPool.pool_month == pool_month,
                PayoutPool.status == PayoutPoolStatus.OPEN
            )
        )
        pool = result.scalar_one_or_none()

        if not pool:
            logger.error(f"No open pool found for {pool_month}")
            return PayoutCalculationResult(
                pool_month=pool_month,
                status='error',
                reason='no_open_pool'
            )

        # Step 2: Validate pool has contributions
        if pool.total_contributions_cents == 0:
            logger.warning(f"Pool {pool_month} has zero contributions")
            pool.status = PayoutPoolStatus.CLOSED
            pool.closed_at = datetime.utcnow()
            if not dry_run:
                await db.commit()

            return PayoutCalculationResult(
                pool_month=pool_month,
                status='skipped',
                reason='no_contributions'
            )

        # Step 3: Query all approved reviews for this month
        result = await db.execute(
            select(ReviewCompletion).where(
                ReviewCompletion.pool_id == pool.id,
                ReviewCompletion.eligible_for_payout == True,
                ReviewCompletion.payout_status == PayoutStatus.PENDING
            )
        )
        approved_reviews = result.scalars().all()
        total_approved_reviews = len(approved_reviews)

        # Step 4: Handle edge case - no approved reviews
        if total_approved_reviews == 0:
            logger.warning(f"Pool {pool_month} has no approved reviews")
            pool.status = PayoutPoolStatus.ROLLED_OVER
            pool.remaining_cents = pool.total_contributions_cents
            pool.closed_at = datetime.utcnow()

            if not dry_run:
                await db.commit()
                await PayoutService._rollover_to_next_month(pool, db)

            return PayoutCalculationResult(
                pool_month=pool_month,
                status='rolled_over',
                reason='no_approved_reviews',
                total_pool_cents=pool.total_contributions_cents
            )

        # Step 5: Calculate payout per review
        payout_per_review_cents = pool.total_contributions_cents // total_approved_reviews
        pool.payout_per_review_cents = payout_per_review_cents
        pool.status = PayoutPoolStatus.CALCULATING
        pool.calculated_at = datetime.utcnow()

        if not dry_run:
            await db.commit()

        logger.info(
            f"Pool {pool_month}: ${pool.total_contributions_cents/100:.2f} / "
            f"{total_approved_reviews} reviews = ${payout_per_review_cents/100:.2f} per review"
        )

        # Step 6: Group reviews by reviewer
        reviews_by_reviewer = defaultdict(list)
        for review_completion in approved_reviews:
            reviews_by_reviewer[review_completion.reviewer_id].append(review_completion)

        # Step 7: Calculate individual payouts
        distributions = []
        failed_distributions = []

        for reviewer_id, reviews in reviews_by_reviewer.items():
            result = await db.execute(
                select(Researcher).where(Researcher.id == reviewer_id)
            )
            reviewer = result.scalar_one_or_none()

            if not reviewer:
                logger.error(f"Reviewer {reviewer_id} not found")
                failed_distributions.append({
                    'reviewer_id': str(reviewer_id),
                    'reason': 'reviewer_not_found',
                    'review_count': len(reviews)
                })
                continue

            # Calculate total payout for this reviewer
            review_count = len(reviews)
            total_payout_cents = payout_per_review_cents * review_count

            # Validate Stripe Connect account
            if not reviewer.stripe_connect_account_id:
                logger.error(f"Reviewer {reviewer.name} has no Connect account")
                failed_distributions.append({
                    'reviewer_id': str(reviewer_id),
                    'reviewer_name': reviewer.name,
                    'reason': 'no_connect_account',
                    'amount': total_payout_cents / 100,
                    'review_count': review_count
                })
                continue

            # Create distribution record
            distribution = PayoutDistribution(
                pool_id=pool.id,
                reviewer_id=reviewer_id,
                approved_reviews_count=review_count,
                payout_per_review_cents=payout_per_review_cents,
                total_payout_cents=total_payout_cents,
                stripe_connect_account_id=reviewer.stripe_connect_account_id,
                status=TransferStatus.PENDING
            )

            if not dry_run:
                # Step 8: Execute Stripe Connect transfer
                try:
                    transfer = StripeService.create_transfer(
                        connect_account_id=reviewer.stripe_connect_account_id,
                        amount_cents=total_payout_cents,
                        description=f"Peer review payouts for {pool_month.strftime('%B %Y')}",
                        metadata={
                            'pool_month': str(pool_month),
                            'review_count': review_count,
                            'payout_per_review': payout_per_review_cents / 100
                        }
                    )

                    distribution.stripe_transfer_id = transfer.id
                    distribution.status = TransferStatus.PROCESSING
                    distribution.transfer_initiated_at = datetime.utcnow()

                    # Update review completions
                    for review_completion in reviews:
                        review_completion.payout_status = PayoutStatus.DISTRIBUTED
                        review_completion.payout_amount_cents = payout_per_review_cents
                        review_completion.distributed_at = datetime.utcnow()

                    # Update researcher lifetime earnings
                    reviewer.total_earnings_cents += total_payout_cents
                    reviewer.lifetime_reviews_paid += review_count
                    reviewer.last_payout_date = date.today()

                    logger.info(
                        f"Transferred ${total_payout_cents/100:.2f} to {reviewer.name} "
                        f"for {review_count} reviews"
                    )

                except stripe.error.StripeError as e:
                    logger.error(f"Stripe transfer failed for reviewer {reviewer_id}: {e}")
                    distribution.status = TransferStatus.FAILED
                    distribution.failure_reason = str(e)
                    failed_distributions.append({
                        'reviewer_id': str(reviewer_id),
                        'reviewer_name': reviewer.name,
                        'reason': str(e),
                        'amount': total_payout_cents / 100,
                        'review_count': review_count
                    })

            db.add(distribution)
            distributions.append(distribution)

        # Step 9: Update pool status
        pool.total_distributed_cents = sum(d.total_payout_cents for d in distributions if d.status != TransferStatus.FAILED)
        pool.remaining_cents = pool.total_contributions_cents - pool.total_distributed_cents

        if not dry_run:
            pool.status = PayoutPoolStatus.DISTRIBUTED
            pool.distributed_at = datetime.utcnow()
            await db.commit()

            # Step 10: Close current pool and create next month's pool
            await PayoutService._close_pool(pool, db)
            await PayoutService._create_next_month_pool(pool_month, db)

        logger.info(
            f"Payout calculation completed for {pool_month}: "
            f"{len(distributions)} distributions, {len(failed_distributions)} failures"
        )

        return PayoutCalculationResult(
            pool_month=pool_month,
            status='completed' if not dry_run else 'dry_run',
            total_pool_cents=pool.total_contributions_cents,
            total_distributed_cents=pool.total_distributed_cents,
            payout_per_review_cents=payout_per_review_cents,
            approved_reviews_count=total_approved_reviews,
            unique_reviewers_count=len(reviews_by_reviewer),
            distributions=distributions,
            failed_distributions=failed_distributions
        )

    @staticmethod
    async def _rollover_to_next_month(pool: PayoutPool, db: AsyncSession):
        """Roll over contributions to next month if no reviews completed."""
        from dateutil.relativedelta import relativedelta

        next_month = pool.pool_month + relativedelta(months=1)

        # Get or create next month's pool
        result = await db.execute(
            select(PayoutPool).where(PayoutPool.pool_month == next_month)
        )
        next_pool = result.scalar_one_or_none()

        if not next_pool:
            next_pool = PayoutPool(
                pool_month=next_month,
                status=PayoutPoolStatus.OPEN
            )
            db.add(next_pool)

        # Add remaining to next month
        next_pool.total_contributions_cents += pool.remaining_cents
        await db.commit()

        logger.info(f"Rolled over ${pool.remaining_cents/100:.2f} to {next_month}")

    @staticmethod
    async def _close_pool(pool: PayoutPool, db: AsyncSession):
        """Close a payout pool."""
        pool.status = PayoutPoolStatus.CLOSED
        pool.closed_at = datetime.utcnow()
        await db.commit()
        logger.info(f"Closed pool {pool.pool_month}")

    @staticmethod
    async def _create_next_month_pool(current_month: date, db: AsyncSession):
        """Create next month's payout pool."""
        from dateutil.relativedelta import relativedelta

        next_month = current_month + relativedelta(months=1)

        result = await db.execute(
            select(PayoutPool).where(PayoutPool.pool_month == next_month)
        )
        existing = result.scalar_one_or_none()

        if not existing:
            new_pool = PayoutPool(
                pool_month=next_month,
                status=PayoutPoolStatus.OPEN
            )
            db.add(new_pool)
            await db.commit()
            logger.info(f"Created new pool for {next_month}")

    @staticmethod
    async def get_reviewer_earnings(
        reviewer_id: UUID,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get earnings summary for a reviewer.

        Args:
            reviewer_id: Reviewer ID
            db: Database session

        Returns:
            Dictionary with earnings summary
        """
        result = await db.execute(
            select(Researcher).where(Researcher.id == reviewer_id)
        )
        reviewer = result.scalar_one_or_none()

        if not reviewer:
            return {}

        # Get all distributions
        result = await db.execute(
            select(PayoutDistribution).where(
                PayoutDistribution.reviewer_id == reviewer_id
            ).order_by(PayoutDistribution.created_at.desc())
        )
        distributions = result.scalars().all()

        # Get current month pending reviews
        current_month = date.today().replace(day=1)
        result = await db.execute(
            select(func.count(ReviewCompletion.id)).where(
                ReviewCompletion.reviewer_id == reviewer_id,
                ReviewCompletion.eligible_for_payout == True,
                ReviewCompletion.payout_status == PayoutStatus.PENDING
            ).join(PayoutPool).where(
                PayoutPool.pool_month == current_month
            )
        )
        pending_count = result.scalar()

        # Estimate current month earnings
        result = await db.execute(
            select(PayoutPool).where(
                PayoutPool.pool_month == current_month,
                PayoutPool.status == PayoutPoolStatus.OPEN
            )
        )
        current_pool = result.scalar_one_or_none()

        estimated_payout = 0
        if current_pool and current_pool.total_reviews_approved > 0:
            estimated_per_review = current_pool.total_contributions_cents / current_pool.total_reviews_approved
            estimated_payout = estimated_per_review * pending_count

        return {
            'lifetime_earnings': reviewer.total_earnings_cents / 100,
            'lifetime_reviews_paid': reviewer.lifetime_reviews_paid,
            'last_payout_date': reviewer.last_payout_date.isoformat() if reviewer.last_payout_date else None,
            'current_month_pending': pending_count,
            'estimated_current_month_payout': estimated_payout / 100,
            'earnings_history': [
                {
                    'month': d.created_at.strftime('%Y-%m'),
                    'reviews_completed': d.approved_reviews_count,
                    'payout_amount': d.total_payout_cents / 100,
                    'payout_date': d.transfer_completed_at.isoformat() if d.transfer_completed_at else None,
                    'status': d.status.value
                }
                for d in distributions
            ]
        }
