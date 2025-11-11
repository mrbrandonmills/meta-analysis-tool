"""Subscription model for payment ecosystem."""

from datetime import datetime
from typing import TYPE_CHECKING
import enum

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.payout_contribution import PayoutContribution


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enumeration."""

    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    TRIALING = "trialing"


class SubscriptionPlanType(str, enum.Enum):
    """Subscription plan type enumeration."""

    RESEARCHER_MONTHLY = "researcher_monthly"
    RESEARCHER_ANNUAL = "researcher_annual"


class Subscription(Base, BaseModel):
    """Subscription model for tracking researcher subscriptions."""

    __tablename__ = "subscriptions"

    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Stripe Integration
    stripe_subscription_id = Column(String(255), unique=True, nullable=False, index=True)
    stripe_customer_id = Column(String(255), nullable=False, index=True)
    stripe_payment_method_id = Column(String(255), nullable=True)

    # Subscription Details
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE, index=True)
    plan_type = Column(SQLEnum(SubscriptionPlanType), nullable=False, default=SubscriptionPlanType.RESEARCHER_MONTHLY)
    monthly_amount_cents = Column(Integer, nullable=False, default=10000)  # $100.00
    payout_contribution_cents = Column(Integer, nullable=False, default=2000)  # $20.00

    # Billing Cycle
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    trial_end = Column(DateTime, nullable=True)
    billing_cycle_anchor = Column(DateTime, nullable=True)

    # Cancellation
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    canceled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    contributions = relationship("PayoutContribution", back_populates="subscription", cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Subscription(id={self.id}, user_id={self.user_id}, status={self.status.value})>"
