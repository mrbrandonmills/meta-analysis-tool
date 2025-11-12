"""Payout Pool model for monthly payout tracking."""

from datetime import datetime, date
from typing import TYPE_CHECKING, Optional
import enum

from sqlalchemy import Column, Integer, Date, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.payout_contribution import PayoutContribution
    from app.models.review_completion import ReviewCompletion
    from app.models.payout_distribution import PayoutDistribution


class PayoutPoolStatus(str, enum.Enum):
    """Payout pool status enumeration."""

    OPEN = "open"
    CALCULATING = "calculating"
    DISTRIBUTED = "distributed"
    CLOSED = "closed"
    ROLLED_OVER = "rolled_over"


class PayoutPool(Base, BaseModel):
    """Monthly payout pool tracking."""

    __tablename__ = "payout_pools"

    # Time Period - First day of month (e.g., 2025-11-01)
    pool_month = Column(Date, nullable=False, unique=True, index=True)

    # Pool Amounts (in cents)
    total_contributions_cents = Column(Integer, nullable=False, default=0)
    total_distributed_cents = Column(Integer, nullable=False, default=0)
    remaining_cents = Column(Integer, nullable=False, default=0)

    # Review Counts
    total_reviews_assigned = Column(Integer, nullable=False, default=0)
    total_reviews_completed = Column(Integer, nullable=False, default=0)
    total_reviews_approved = Column(Integer, nullable=False, default=0)

    # Payout Calculation
    payout_per_review_cents = Column(Integer, nullable=True)  # Calculated on pool close

    # Status
    status = Column(
        SQLEnum(PayoutPoolStatus, values_callable=lambda x: [e.value for e in x], name='payoutpoolstatus', native_enum=True),
        nullable=False,
        default=PayoutPoolStatus.OPEN,
        index=True
    )
    calculated_at = Column(DateTime, nullable=True)
    distributed_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # Metadata
    pool_metadata = Column(JSONB, nullable=True, default=dict)

    # Relationships
    contributions = relationship("PayoutContribution", back_populates="pool", cascade="all, delete-orphan", lazy="dynamic")
    review_completions = relationship("ReviewCompletion", back_populates="pool", cascade="all, delete-orphan", lazy="dynamic")
    distributions = relationship("PayoutDistribution", back_populates="pool", cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PayoutPool(id={self.id}, month={self.pool_month}, status={self.status.value})>"
