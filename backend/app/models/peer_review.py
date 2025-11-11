"""Peer Review model - Tool 3: Peer Review Assistant."""

from typing import TYPE_CHECKING
from datetime import datetime
import enum

from sqlalchemy import Column, String, Text, ForeignKey, Float, Enum as SQLEnum, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.researcher import Researcher


class ReviewRecommendation(str, enum.Enum):
    """Review recommendation enumeration."""

    ACCEPT = "accept"
    MINOR_REVISION = "minor_revision"
    MAJOR_REVISION = "major_revision"
    REJECT = "reject"
    REJECT_RESUBMIT = "reject_resubmit"


class ReviewStatus(str, enum.Enum):
    """Review status enumeration."""

    INVITED = "invited"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    DRAFT = "draft"
    SUBMITTED = "submitted"
    LATE = "late"


class PeerReview(Base, BaseModel):
    """Peer review model."""

    __tablename__ = "peer_reviews"

    manuscript_id = Column(UUID(as_uuid=True), ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("researchers.id"), nullable=True, index=True)

    # Review metadata
    review_round = Column(JSONB, default=1, nullable=False)
    invitation_date = Column(DateTime, nullable=True)
    acceptance_date = Column(DateTime, nullable=True)
    submission_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)

    # Review status
    status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.INVITED, nullable=False, index=True)

    # Review content
    review_text = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    detailed_comments = Column(Text, nullable=True)
    confidential_comments = Column(Text, nullable=True)  # Comments for editor only

    # Scores and ratings
    overall_score = Column(Float, nullable=True)  # 1-10 scale
    originality_score = Column(Float, nullable=True)
    methodology_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    significance_score = Column(Float, nullable=True)

    # Recommendation
    recommendation = Column(SQLEnum(ReviewRecommendation), nullable=True, index=True)
    confidence = Column(Float, nullable=True)  # 0.0 to 1.0

    # AI assistance tracking
    ai_assisted = Column(Boolean, default=False, nullable=False)
    ai_draft_used = Column(Boolean, default=False, nullable=False)
    ai_generated_sections = Column(JSONB, nullable=True, default=dict)

    # Quality metrics
    review_quality_score = Column(Float, nullable=True)
    constructiveness_score = Column(Float, nullable=True)
    bias_score = Column(Float, nullable=True)

    # Additional metadata
    review_metadata = Column(JSONB, nullable=True, default=dict)

    # Approval fields
    editor_approved = Column(Boolean, default=False, nullable=False, index=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True, index=True)
    approval_notes = Column(Text, nullable=True)
    eligible_for_payout = Column(Boolean, default=True, nullable=False)

    # Relationships
    manuscript = relationship("Manuscript", back_populates="reviews")
    reviewer = relationship("Researcher", foreign_keys=[reviewer_id])
    approver = relationship("User", foreign_keys=[approved_by])
    completion = relationship("ReviewCompletion", back_populates="peer_review", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PeerReview(id={self.id}, manuscript_id={self.manuscript_id}, recommendation={self.recommendation})>"
