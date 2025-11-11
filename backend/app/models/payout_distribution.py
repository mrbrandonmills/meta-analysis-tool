"""Payout Distribution model for individual reviewer payouts."""

from datetime import datetime, date
from typing import TYPE_CHECKING
import enum

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey, Text, Enum as SQLEnum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.payout_pool import PayoutPool
    from app.models.researcher import Researcher


class TransferStatus(str, enum.Enum):
    """Transfer status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERSED = "reversed"


class PayoutDistribution(Base, BaseModel):
    """Individual reviewer payouts."""

    __tablename__ = "payout_distributions"

    # Foreign Keys
    pool_id = Column(UUID(as_uuid=True), ForeignKey("payout_pools.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False, index=True)

    # Payout Calculation
    approved_reviews_count = Column(Integer, nullable=False, default=0)
    payout_per_review_cents = Column(Integer, nullable=False)
    total_payout_cents = Column(Integer, nullable=False)

    # Stripe Connect Details
    stripe_connect_account_id = Column(String(255), nullable=False)
    stripe_transfer_id = Column(String(255), unique=True, nullable=True)
    stripe_payout_id = Column(String(255), nullable=True)

    # Transfer Status
    status = Column(SQLEnum(TransferStatus), nullable=False, default=TransferStatus.PENDING, index=True)
    transfer_initiated_at = Column(DateTime, nullable=True)
    transfer_completed_at = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)

    # Banking Details
    destination_bank_last4 = Column(String(4), nullable=True)
    destination_bank_name = Column(String(255), nullable=True)
    estimated_arrival_date = Column(Date, nullable=True)

    # Notifications
    notification_sent = Column(Boolean, default=False, nullable=False)
    notification_sent_at = Column(DateTime, nullable=True)

    # Metadata
    distribution_metadata = Column(JSONB, nullable=True, default=dict)

    # Relationships
    pool = relationship("PayoutPool", back_populates="distributions")
    reviewer = relationship("Researcher", back_populates="payout_distributions")

    # Constraints
    __table_args__ = (
        CheckConstraint("total_payout_cents >= 0", name="positive_payout"),
        CheckConstraint("approved_reviews_count >= 0", name="positive_reviews"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<PayoutDistribution(id={self.id}, reviewer_id={self.reviewer_id}, amount=${self.total_payout_cents/100:.2f})>"
