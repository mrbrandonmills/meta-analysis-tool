"""Manuscript model - Tool 3: Peer Review."""

from typing import TYPE_CHECKING
from datetime import datetime
import enum

from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class ManuscriptStatus(str, enum.Enum):
    """Manuscript status enumeration."""

    SUBMITTED = "submitted"
    DESK_REVIEW = "desk_review"
    IN_REVIEW = "in_review"
    REVISION_REQUESTED = "revision_requested"
    REVISED = "revised"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ManuscriptType(str, enum.Enum):
    """Manuscript type enumeration."""

    RESEARCH_ARTICLE = "research_article"
    REVIEW = "review"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    CASE_STUDY = "case_study"
    SHORT_COMMUNICATION = "short_communication"
    LETTER = "letter"
    COMMENTARY = "commentary"


class Manuscript(Base, BaseModel):
    """Manuscript model for peer review system."""

    __tablename__ = "manuscripts"

    # Basic information
    title = Column(Text, nullable=False, index=True)
    abstract = Column(Text, nullable=True)
    keywords = Column(ARRAY(String), nullable=True)
    manuscript_type = Column(SQLEnum(ManuscriptType), nullable=False)

    # Submission details
    submission_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    journal_name = Column(String(255), nullable=True, index=True)
    journal_id = Column(UUID(as_uuid=True), nullable=True)  # For future journal integration

    # Authors
    corresponding_author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    author_names = Column(ARRAY(String), nullable=True)
    author_affiliations = Column(JSONB, nullable=True, default=dict)

    # Status tracking
    status = Column(SQLEnum(ManuscriptStatus), default=ManuscriptStatus.SUBMITTED, nullable=False, index=True)
    current_round = Column(JSONB, default=1, nullable=False)  # Review round number

    # Files
    pdf_path = Column(Text, nullable=True)
    supplementary_files = Column(ARRAY(String), nullable=True)

    # Screening results
    desk_review_decision = Column(String(50), nullable=True)
    desk_review_reasoning = Column(Text, nullable=True)
    quality_score = Column(JSONB, nullable=True)
    methodology_score = Column(JSONB, nullable=True)
    novelty_score = Column(JSONB, nullable=True)

    # Editorial decision
    editorial_decision = Column(String(50), nullable=True)
    editorial_decision_date = Column(DateTime, nullable=True)
    decision_letter = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSONB, nullable=True, default=dict)

    # Relationships
    corresponding_author = relationship("User", foreign_keys=[corresponding_author_id])
    reviews = relationship("PeerReview", back_populates="manuscript", cascade="all, delete-orphan")
    reviewer_matches = relationship("ReviewerMatch", back_populates="manuscript", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Manuscript(id={self.id}, title={self.title[:50]}..., status={self.status})>"
