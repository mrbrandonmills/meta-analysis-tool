"""Reviewer Match model - Tool 4: Expert Reviewer Matcher."""

from typing import TYPE_CHECKING
import enum

from sqlalchemy import Column, String, Text, ForeignKey, Float, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.researcher import Researcher


class MatchStatus(str, enum.Enum):
    """Match status enumeration."""

    PENDING = "pending"
    INVITED = "invited"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    NO_RESPONSE = "no_response"
    WITHDRAWN = "withdrawn"


class ConflictType(str, enum.Enum):
    """Conflict of interest type."""

    NONE = "none"
    COAUTHOR = "coauthor"
    INSTITUTION = "institution"
    RECENT_COLLABORATION = "recent_collaboration"
    ADVISOR_ADVISEE = "advisor_advisee"
    COMPETITOR = "competitor"
    PERSONAL = "personal"
    OTHER = "other"


class ReviewerMatch(Base, BaseModel):
    """Reviewer match/recommendation model."""

    __tablename__ = "reviewer_matches"

    manuscript_id = Column(UUID(as_uuid=True), ForeignKey("manuscripts.id", ondelete="CASCADE"), nullable=False, index=True)
    researcher_id = Column(UUID(as_uuid=True), ForeignKey("researchers.id"), nullable=False, index=True)

    # Match scores (0.0 to 1.0)
    expertise_score = Column(Float, nullable=False)
    availability_score = Column(Float, nullable=False)
    diversity_score = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=False, index=True)

    # Ranking
    rank = Column(JSONB, nullable=True)  # Position in recommendation list

    # Conflict detection
    conflict_risk = Column(Float, nullable=False)  # 0.0 to 1.0
    conflict_types = Column(ARRAY(String), nullable=True)
    conflict_details = Column(JSONB, nullable=True, default=dict)
    has_conflict = Column(Boolean, default=False, nullable=False, index=True)

    # Expertise matching details
    matching_keywords = Column(ARRAY(String), nullable=True)
    matching_domains = Column(ARRAY(String), nullable=True)
    expertise_overlap = Column(JSONB, nullable=True, default=dict)

    # Availability details
    estimated_workload = Column(JSONB, nullable=True)
    recent_reviews = Column(JSONB, nullable=True)
    response_likelihood = Column(Float, nullable=True)

    # Geographic/demographic diversity
    geographic_region = Column(String(100), nullable=True)
    institution_type = Column(String(100), nullable=True)
    career_stage = Column(String(50), nullable=True)

    # AI reasoning
    reasoning = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)

    # Invitation tracking
    status = Column(SQLEnum(MatchStatus), default=MatchStatus.PENDING, nullable=False, index=True)
    invitation_sent_at = Column(JSONB, nullable=True)
    response_received_at = Column(JSONB, nullable=True)

    # Additional metadata
    match_metadata = Column(JSONB, nullable=True, default=dict)

    # Relationships
    manuscript = relationship("Manuscript", back_populates="reviewer_matches")
    researcher = relationship("Researcher", foreign_keys=[researcher_id])

    def __repr__(self) -> str:
        """String representation."""
        return f"<ReviewerMatch(id={self.id}, researcher_id={self.researcher_id}, overall_score={self.overall_score:.2f})>"
