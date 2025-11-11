"""Subscription management API endpoints."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, status, Request, Header
from loguru import logger
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import stripe

from app.db.session import get_async_db
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.payout_pool import PayoutPool, PayoutPoolStatus
from app.models.payout_contribution import PayoutContribution, ContributionStatus
from app.core.security import get_current_user_token, TokenData
from app.core.stripe_client import StripeService
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


# Pydantic schemas
class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription."""

    payment_method_id: str = Field(..., description="Stripe payment method ID")
    billing_email: Optional[EmailStr] = None


class SubscriptionResponse(BaseModel):
    """Schema for subscription response."""

    id: str
    user_id: str
    stripe_subscription_id: str
    stripe_customer_id: str
    status: str
    plan_type: str
    monthly_amount: float
    payout_contribution: float
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionCancelRequest(BaseModel):
    """Schema for canceling a subscription."""

    cancellation_reason: Optional[str] = None
    immediate: bool = Field(default=False, description="Cancel immediately instead of at period end")


class BillingHistoryItem(BaseModel):
    """Schema for billing history item."""

    date: datetime
    amount: float
    status: str
    invoice_url: Optional[str] = None


class SubscriptionDetailsResponse(BaseModel):
    """Schema for detailed subscription info."""

    subscription: SubscriptionResponse
    billing_history: List[BillingHistoryItem]
    contribution_summary: Dict[str, Any]


# Helper functions
async def get_or_create_current_payout_pool(db: AsyncSession) -> PayoutPool:
    """Get or create the current month's payout pool."""
    from datetime import date
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
@router.post("/create", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """
    Create a new subscription for the current user.

    Creates a Stripe subscription, saves it to the database, and adds
    the $20 contribution to the current month's payout pool.
    """
    try:
        # Get user
        result = await db.execute(select(User).where(User.id == UUID(current_user.user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if user already has active subscription
        result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == user.id,
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
        existing_subscription = result.scalar_one_or_none()

        if existing_subscription:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already has an active subscription"
            )

        # Create or retrieve Stripe customer
        if not user.stripe_customer_id:
            stripe_customer = StripeService.create_customer(
                email=subscription_data.billing_email or user.email,
                name=user.full_name or user.email,
                metadata={'user_id': str(user.id)}
            )
            user.stripe_customer_id = stripe_customer.id
        else:
            stripe_customer = stripe.Customer.retrieve(user.stripe_customer_id)

        # Create Stripe subscription
        stripe_subscription = StripeService.create_subscription(
            customer_id=user.stripe_customer_id,
            payment_method_id=subscription_data.payment_method_id,
            price_amount_cents=10000,  # $100
            metadata={
                'user_id': str(user.id),
                'payout_contribution_cents': 2000
            }
        )

        # Create subscription record
        new_subscription = Subscription(
            user_id=user.id,
            stripe_subscription_id=stripe_subscription.id,
            stripe_customer_id=user.stripe_customer_id,
            stripe_payment_method_id=subscription_data.payment_method_id,
            status=SubscriptionStatus(stripe_subscription.status),
            monthly_amount_cents=10000,
            payout_contribution_cents=2000,
            current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end),
            billing_cycle_anchor=datetime.fromtimestamp(stripe_subscription.billing_cycle_anchor) if stripe_subscription.billing_cycle_anchor else None
        )
        db.add(new_subscription)

        # Add contribution to current payout pool
        current_pool = await get_or_create_current_payout_pool(db)
        current_pool.total_contributions_cents += 2000

        contribution = PayoutContribution(
            pool_id=current_pool.id,
            user_id=user.id,
            subscription_id=new_subscription.id,
            contribution_amount_cents=2000,
            billing_date=datetime.utcnow(),
            status=ContributionStatus.COMPLETED
        )
        db.add(contribution)

        # Update user
        user.is_paying_member = True
        user.member_since = datetime.utcnow()
        user.subscription_status = 'active'

        await db.commit()
        await db.refresh(new_subscription)

        logger.info(f"Created subscription for user {user.id}")

        return SubscriptionResponse(
            id=str(new_subscription.id),
            user_id=str(new_subscription.user_id),
            stripe_subscription_id=new_subscription.stripe_subscription_id,
            stripe_customer_id=new_subscription.stripe_customer_id,
            status=new_subscription.status.value,
            plan_type=new_subscription.plan_type.value,
            monthly_amount=new_subscription.monthly_amount_cents / 100,
            payout_contribution=new_subscription.payout_contribution_cents / 100,
            current_period_start=new_subscription.current_period_start,
            current_period_end=new_subscription.current_period_end,
            cancel_at_period_end=new_subscription.cancel_at_period_end,
            created_at=new_subscription.created_at
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating subscription: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{subscription_id}/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    subscription_id: UUID,
    cancel_data: SubscriptionCancelRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """
    Cancel a subscription.

    By default, cancels at the end of the billing period.
    Can optionally cancel immediately.
    """
    try:
        # Get subscription
        result = await db.execute(
            select(Subscription).where(
                Subscription.id == subscription_id,
                Subscription.user_id == UUID(current_user.user_id)
            )
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Cancel in Stripe
        stripe_subscription = StripeService.cancel_subscription(
            subscription.stripe_subscription_id,
            at_period_end=not cancel_data.immediate
        )

        # Update database
        if cancel_data.immediate:
            subscription.status = SubscriptionStatus.CANCELED
            subscription.canceled_at = datetime.utcnow()
        else:
            subscription.cancel_at_period_end = True

        subscription.cancellation_reason = cancel_data.cancellation_reason

        await db.commit()
        await db.refresh(subscription)

        logger.info(f"Canceled subscription {subscription_id}")

        return SubscriptionResponse(
            id=str(subscription.id),
            user_id=str(subscription.user_id),
            stripe_subscription_id=subscription.stripe_subscription_id,
            stripe_customer_id=subscription.stripe_customer_id,
            status=subscription.status.value,
            plan_type=subscription.plan_type.value,
            monthly_amount=subscription.monthly_amount_cents / 100,
            payout_contribution=subscription.payout_contribution_cents / 100,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            cancel_at_period_end=subscription.cancel_at_period_end,
            created_at=subscription.created_at
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error canceling subscription: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/me", response_model=Optional[SubscriptionDetailsResponse])
async def get_my_subscription(
    db: AsyncSession = Depends(get_async_db),
    current_user: TokenData = Depends(get_current_user_token)
):
    """
    Get the current user's subscription details including billing history.
    """
    try:
        # Get active subscription
        result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == UUID(current_user.user_id),
                Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.PAST_DUE])
            ).order_by(Subscription.created_at.desc())
        )
        subscription = result.scalar_one_or_none()

        if not subscription:
            return None

        # Get billing history from Stripe
        billing_history = []
        try:
            invoices = StripeService.list_invoices(subscription.stripe_customer_id, limit=12)
            for invoice in invoices.data:
                billing_history.append(BillingHistoryItem(
                    date=datetime.fromtimestamp(invoice.created),
                    amount=invoice.amount_paid / 100,
                    status=invoice.status,
                    invoice_url=invoice.invoice_pdf if hasattr(invoice, 'invoice_pdf') else None
                ))
        except Exception as e:
            logger.warning(f"Failed to fetch billing history: {e}")

        # Get contribution summary
        result = await db.execute(
            select(PayoutContribution).where(
                PayoutContribution.user_id == UUID(current_user.user_id),
                PayoutContribution.status == ContributionStatus.COMPLETED
            )
        )
        contributions = result.scalars().all()

        contribution_summary = {
            'total_contributed': sum(c.contribution_amount_cents for c in contributions) / 100,
            'months_active': len(contributions),
            'next_contribution_date': subscription.current_period_end.isoformat() if subscription else None
        }

        return SubscriptionDetailsResponse(
            subscription=SubscriptionResponse(
                id=str(subscription.id),
                user_id=str(subscription.user_id),
                stripe_subscription_id=subscription.stripe_subscription_id,
                stripe_customer_id=subscription.stripe_customer_id,
                status=subscription.status.value,
                plan_type=subscription.plan_type.value,
                monthly_amount=subscription.monthly_amount_cents / 100,
                payout_contribution=subscription.payout_contribution_cents / 100,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                cancel_at_period_end=subscription.cancel_at_period_end,
                created_at=subscription.created_at
            ),
            billing_history=billing_history,
            contribution_summary=contribution_summary
        )

    except Exception as e:
        logger.error(f"Error fetching subscription: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Handle Stripe webhook events.

    Processes events like subscription updates, payment failures, etc.
    """
    try:
        payload = await request.body()

        # Construct and verify event
        event = StripeService.construct_webhook_event(
            payload,
            stripe_signature,
            settings.stripe_webhook_secret
        )

        logger.info(f"Received webhook event: {event.type}")

        # Handle different event types
        if event.type == 'customer.subscription.updated':
            subscription_data = event.data.object
            await handle_subscription_updated(subscription_data, db)

        elif event.type == 'customer.subscription.deleted':
            subscription_data = event.data.object
            await handle_subscription_deleted(subscription_data, db)

        elif event.type == 'invoice.payment_succeeded':
            invoice = event.data.object
            await handle_payment_succeeded(invoice, db)

        elif event.type == 'invoice.payment_failed':
            invoice = event.data.object
            await handle_payment_failed(invoice, db)

        return {"status": "success"}

    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Webhook handlers
async def handle_subscription_updated(subscription_data: Dict[str, Any], db: AsyncSession):
    """Handle subscription.updated webhook."""
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == subscription_data['id']
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = SubscriptionStatus(subscription_data['status'])
        subscription.current_period_start = datetime.fromtimestamp(subscription_data['current_period_start'])
        subscription.current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])
        subscription.cancel_at_period_end = subscription_data.get('cancel_at_period_end', False)
        await db.commit()
        logger.info(f"Updated subscription {subscription.id}")


async def handle_subscription_deleted(subscription_data: Dict[str, Any], db: AsyncSession):
    """Handle subscription.deleted webhook."""
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == subscription_data['id']
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = SubscriptionStatus.CANCELED
        subscription.canceled_at = datetime.utcnow()

        # Update user
        result = await db.execute(select(User).where(User.id == subscription.user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_paying_member = False
            user.subscription_status = 'canceled'

        await db.commit()
        logger.info(f"Deleted subscription {subscription.id}")


async def handle_payment_succeeded(invoice: Dict[str, Any], db: AsyncSession):
    """Handle invoice.payment_succeeded webhook."""
    subscription_id = invoice.get('subscription')
    if not subscription_id:
        return

    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == subscription_id
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        # Add contribution to current pool
        current_pool = await get_or_create_current_payout_pool(db)
        current_pool.total_contributions_cents += 2000

        contribution = PayoutContribution(
            pool_id=current_pool.id,
            user_id=subscription.user_id,
            subscription_id=subscription.id,
            contribution_amount_cents=2000,
            billing_date=datetime.utcnow(),
            stripe_payment_intent_id=invoice.get('payment_intent'),
            stripe_invoice_id=invoice['id'],
            status=ContributionStatus.COMPLETED
        )
        db.add(contribution)
        await db.commit()
        logger.info(f"Added contribution for subscription {subscription.id}")


async def handle_payment_failed(invoice: Dict[str, Any], db: AsyncSession):
    """Handle invoice.payment_failed webhook."""
    subscription_id = invoice.get('subscription')
    if not subscription_id:
        return

    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == subscription_id
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = SubscriptionStatus.PAST_DUE
        await db.commit()
        logger.warning(f"Payment failed for subscription {subscription.id}")
