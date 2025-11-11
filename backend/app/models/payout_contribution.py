"""Payout Contribution model for tracking individual $20 contributions."""

from datetime import datetime
from typing import TYPE_CHECKING
import enum

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.payout_pool import PayoutPool
    from app.models.user import User
    from app.models.subscription import Subscription


class ContributionStatus(str, enum.Enum):
    """Contribution status enumeration."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PayoutContribution(Base, BaseModel):
    """Individual subscription contributions to payout pool."""

    __tablename__ = "payout_contributions"

    # Foreign Keys
    pool_id = Column(UUID(as_uuid=True), ForeignKey("payout_pools.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Contribution Details
    contribution_amount_cents = Column(Integer, nullable=False, default=2000)  # $20.00
    billing_date = Column(DateTime, nullable=False)

    # Stripe Details
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_invoice_id = Column(String(255), nullable=True)

    # Status
    status = Column(SQLEnum(ContributionStatus), nullable=False, default=ContributionStatus.PENDING, index=True)

    # Relationships
    pool = relationship("PayoutPool", back_populates="contributions")
    user = relationship("User", back_populates="contributions")
    subscription = relationship("Subscription", back_populates="contributions")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PayoutContribution(id={self.id}, user_id={self.user_id}, amount=${self.contribution_amount_cents/100:.2f})>"
