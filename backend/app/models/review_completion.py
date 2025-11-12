"""Review Completion model for tracking approved reviews eligible for payout."""

from datetime import datetime
from typing import TYPE_CHECKING
import enum

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.payout_pool import PayoutPool
    from app.models.peer_review import PeerReview
    from app.models.researcher import Researcher
    from app.models.manuscript import Manuscript
    from app.models.user import User


class PayoutStatus(str, enum.Enum):
    """Payout status enumeration."""

    PENDING = "pending"
    CALCULATED = "calculated"
    DISTRIBUTED = "distributed"
    FAILED = "failed"


class ReviewCompletion(Base, BaseModel):
    """Approved reviews eligible for payout."""

    __tablename__ = "review_completions"

    # Foreign Keys
    pool_id = Column(UUID(as_uuid=True), ForeignKey("payout_pools.id", ondelete="CASCADE"), nullable=False, index=True)
    peer_review_id = Column(UUID(as_uuid=True), ForeignKey("peer_reviews.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False, index=True)
    manuscript_id = Column(UUID(as_uuid=True), ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)

    # Approval Details
    editor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Who approved the review
    approved_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    approval_notes = Column(Text, nullable=True)

    # Review Quality Metrics
    quality_score = Column(Float, nullable=True)  # 0.0 to 1.0
    completeness_score = Column(Float, nullable=True)
    constructiveness_score = Column(Float, nullable=True)

    # Payout Eligibility
    eligible_for_payout = Column(Boolean, nullable=False, default=True)
    ineligibility_reason = Column(Text, nullable=True)

    # Payout Status
    payout_status = Column(
        SQLEnum(PayoutStatus, values_callable=lambda x: [e.value for e in x], name='payoutstatus', native_enum=True),
        nullable=False,
        default=PayoutStatus.PENDING,
        index=True
    )
    payout_amount_cents = Column(Integer, nullable=True)
    distributed_at = Column(DateTime, nullable=True)

    # Metadata
    completion_metadata = Column(JSONB, nullable=True, default=dict)

    # Relationships
    pool = relationship("PayoutPool", back_populates="review_completions")
    peer_review = relationship("PeerReview", back_populates="completion")
    reviewer = relationship("Researcher", foreign_keys=[reviewer_id])
    manuscript = relationship("Manuscript")
    editor = relationship("User", foreign_keys=[editor_id])

    def __repr__(self) -> str:
        """String representation."""
        return f"<ReviewCompletion(id={self.id}, reviewer_id={self.reviewer_id}, payout_status={self.payout_status.value})>"
