"""Workflow model."""

from typing import TYPE_CHECKING, Optional
from datetime import datetime
import enum

from sqlalchemy import Column, String, Text, ForeignKey, Float, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.project import Project


class WorkflowStatus(str, enum.Enum):
    """Workflow status enumeration."""

    CREATED = "created"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentRole(str, enum.Enum):
    """Agent role enumeration."""

    COORDINATOR = "coordinator"
    SEARCH = "search"
    SCREENING = "screening"
    CREDIBILITY = "credibility"
    QA = "qa"
    DATA_EXTRACTION = "data_extraction"
    STATISTICAL = "statistical"
    GAP_ANALYSIS = "gap_analysis"
    TREND_ANALYSIS = "trend_analysis"
    METHOD_INNOVATION = "method_innovation"
    IMPACT_PREDICTION = "impact_prediction"
    PROPOSAL_GENERATOR = "proposal_generator"
    REVIEW_DRAFTER = "review_drafter"
    EDITOR_ASSISTANT = "editor_assistant"
    EXPERTISE_ANALYZER = "expertise_analyzer"
    CONFLICT_DETECTOR = "conflict_detector"
    AVAILABILITY_PREDICTOR = "availability_predictor"
    MATCHER = "matcher"


class Workflow(Base, BaseModel):
    """Workflow execution tracking model."""

    __tablename__ = "workflows"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(255), nullable=False, index=True)
    agent_role = Column(SQLEnum(AgentRole), nullable=False, index=True)

    # Input/Output data
    input_data = Column(JSONB, nullable=True, default=dict)
    output_data = Column(JSONB, nullable=True, default=dict)

    # Agent decisions (array of decision objects)
    decisions = Column(JSONB, nullable=True, default=list)

    # Execution tracking
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.CREATED, nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)

    # Performance metrics
    started_at = Column(JSONB, nullable=True)  # datetime
    completed_at = Column(JSONB, nullable=True)  # datetime
    duration_seconds = Column(Float, nullable=True)

    # Confidence and quality scores
    confidence_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="workflows")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Workflow(id={self.id}, agent={self.agent_role}, status={self.status})>"
