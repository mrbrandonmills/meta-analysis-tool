"""Research Gap model - Tool 2: Research Direction Generator."""

from typing import TYPE_CHECKING
import enum

from sqlalchemy import Column, String, Text, Float, Integer, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.project import Project


class GapType(str, enum.Enum):
    """Research gap type enumeration."""

    POPULATION = "population"
    INTERVENTION = "intervention"
    OUTCOME = "outcome"
    METHODOLOGY = "methodology"
    THEORETICAL = "theoretical"
    GEOGRAPHIC = "geographic"
    TEMPORAL = "temporal"
    INTERDISCIPLINARY = "interdisciplinary"


class GapPriority(str, enum.Enum):
    """Gap priority level."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ResearchGap(Base, BaseModel):
    """Research gap identified by gap analysis."""

    __tablename__ = "research_gaps"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)

    # Gap description
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    gap_type = Column(SQLEnum(GapType), nullable=False, index=True)
    domain = Column(String(255), nullable=True, index=True)

    # Supporting evidence
    evidence = Column(ARRAY(String), nullable=True)
    supporting_papers = Column(ARRAY(UUID(as_uuid=True)), nullable=True)  # References to paper IDs
    citation_count = Column(Integer, default=0, nullable=False)

    # Impact and priority
    impact_potential = Column(Float, nullable=True)  # 0.0 to 1.0
    feasibility_score = Column(Float, nullable=True)  # 0.0 to 1.0
    novelty_score = Column(Float, nullable=True)  # 0.0 to 1.0
    priority = Column(SQLEnum(GapPriority), nullable=True, index=True)

    # Trends and patterns
    temporal_trend = Column(String(100), nullable=True)  # increasing, decreasing, stable
    geographic_coverage = Column(ARRAY(String), nullable=True)
    understudied_populations = Column(ARRAY(String), nullable=True)

    # AI reasoning
    reasoning = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)

    # Metadata
    metadata = Column(JSONB, nullable=True, default=dict)

    # Relationships
    project = relationship("Project", foreign_keys=[project_id])

    def __repr__(self) -> str:
        """String representation."""
        return f"<ResearchGap(id={self.id}, type={self.gap_type}, priority={self.priority})>"
