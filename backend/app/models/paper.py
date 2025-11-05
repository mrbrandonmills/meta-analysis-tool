"""Paper model - shared across Tools 1, 2, 3."""

from typing import TYPE_CHECKING, Optional
import enum

from sqlalchemy import Column, String, Text, Integer, Float, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.researcher import Researcher


class CredibilityLevel(str, enum.Enum):
    """Credibility level enumeration."""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DatabaseSource(str, enum.Enum):
    """Database source enumeration."""

    PUBMED = "pubmed"
    ARXIV = "arxiv"
    EUROPE_PMC = "europe_pmc"
    CORE = "core"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    CROSSREF = "crossref"
    MANUAL = "manual"


class Paper(Base, BaseModel):
    """Paper/Study model - universal for all tools."""

    __tablename__ = "papers"

    # Basic metadata
    title = Column(Text, nullable=False, index=True)
    abstract = Column(Text, nullable=True)
    authors = Column(ARRAY(String), nullable=True)
    journal = Column(String(255), nullable=True, index=True)
    year = Column(Integer, nullable=True, index=True)
    publication_date = Column(JSONB, nullable=True)  # Full date if available

    # Identifiers
    doi = Column(String(255), unique=True, nullable=True, index=True)
    pmid = Column(String(50), unique=True, nullable=True, index=True)
    arxiv_id = Column(String(50), unique=True, nullable=True, index=True)
    pmc_id = Column(String(50), unique=True, nullable=True, index=True)

    # Content
    keywords = Column(ARRAY(String), nullable=True)
    mesh_terms = Column(ARRAY(String), nullable=True)
    database_source = Column(SQLEnum(DatabaseSource), nullable=True, index=True)

    # Tool 1: Meta-Analysis fields
    credibility_level = Column(SQLEnum(CredibilityLevel), nullable=True, index=True)
    credibility_score = Column(Float, nullable=True)
    credibility_reasoning = Column(Text, nullable=True)
    extracted_statistics = Column(JSONB, nullable=True, default=dict)
    effect_size = Column(Float, nullable=True)
    effect_size_ci_lower = Column(Float, nullable=True)
    effect_size_ci_upper = Column(Float, nullable=True)
    sample_size = Column(Integer, nullable=True)
    p_value = Column(Float, nullable=True)
    inclusion_status = Column(String(50), nullable=True, index=True)  # included, excluded, screening
    exclusion_reason = Column(Text, nullable=True)

    # Tool 2: Research Direction fields
    research_gaps = Column(ARRAY(String), nullable=True)
    trending_topics = Column(ARRAY(String), nullable=True)
    novelty_score = Column(Float, nullable=True)

    # Tool 3: Peer Review fields
    review_quality_score = Column(Float, nullable=True)
    methodology_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)

    # Shared fields
    citation_count = Column(Integer, default=0, nullable=False)
    full_text_url = Column(Text, nullable=True)
    pdf_path = Column(Text, nullable=True)
    pdf_hash = Column(String(64), nullable=True, index=True)  # SHA256 for deduplication

    # Full-text search
    full_text = Column(Text, nullable=True)

    # Additional metadata
    paper_metadata = Column(JSONB, nullable=True, default=dict)

    # Relationships
    projects = relationship("Project", secondary="project_papers", back_populates="papers", lazy="dynamic")
    authors_relationships = relationship(
        "Researcher",
        secondary="paper_authors",
        back_populates="papers",
        lazy="dynamic"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Paper(id={self.id}, title={self.title[:50]}...)>"
