"""Researcher model - shared across Tools 2, 4."""

from typing import TYPE_CHECKING, Optional
from datetime import date

from sqlalchemy import Column, String, Text, Integer, Float, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.paper import Paper


class Researcher(Base, BaseModel):
    """Researcher/Expert model - used by Tools 2, 4."""

    __tablename__ = "researchers"

    # Basic information
    orcid = Column(String(50), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    institution = Column(String(255), nullable=True, index=True)
    department = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True, index=True)
    website = Column(Text, nullable=True)

    # Academic metrics
    h_index = Column(Integer, nullable=True)
    i10_index = Column(Integer, nullable=True)
    total_citations = Column(Integer, default=0, nullable=False)
    publication_count = Column(Integer, default=0, nullable=False)

    # Tool 4: Reviewer Matching fields
    expertise_keywords = Column(ARRAY(String), nullable=True)
    expertise_domains = Column(JSONB, nullable=True, default=dict)  # {domain: confidence_score}
    research_domains = Column(ARRAY(String), nullable=True)

    # Review activity tracking
    recent_review_count = Column(Integer, default=0, nullable=False)
    total_review_count = Column(Integer, default=0, nullable=False)
    average_review_time_days = Column(Float, nullable=True)
    last_review_date = Column(Date, nullable=True)

    # Availability and workload
    estimated_availability = Column(Float, nullable=True)  # 0.0 to 1.0 score
    current_workload = Column(Integer, default=0, nullable=False)
    response_rate = Column(Float, nullable=True)  # 0.0 to 1.0

    # Tool 2: Research Direction fields
    trending_areas = Column(ARRAY(String), nullable=True)
    emerging_expertise = Column(JSONB, nullable=True, default=dict)

    # Social/network information
    coauthor_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    institution_collaborators = Column(ARRAY(UUID(as_uuid=True)), nullable=True)

    # Activity tracking
    last_active = Column(Date, nullable=True)
    last_publication_date = Column(Date, nullable=True)

    # Additional metadata
    researcher_metadata = Column(JSONB, nullable=True, default=dict)

    # Profile data from external sources
    semantic_scholar_id = Column(String(100), nullable=True, index=True)
    google_scholar_id = Column(String(100), nullable=True, index=True)

    # Relationships
    projects = relationship("Project", secondary="project_researchers", back_populates="researchers", lazy="dynamic")
    papers = relationship("Paper", secondary="paper_authors", back_populates="authors_relationships", lazy="dynamic")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Researcher(id={self.id}, name={self.name}, h_index={self.h_index})>"
