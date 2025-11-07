"""Meta-analysis models for production-grade persistence."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class MetaAnalysisStatus(str, Enum):
    """Meta-analysis workflow status."""

    CREATED = "created"
    WORKFLOW_CREATED = "workflow_created"
    IN_PROGRESS = "in_progress"
    SEARCHING = "searching"
    SCREENING = "screening"
    QUALITY_ASSESSMENT = "quality_assessment"
    DATA_EXTRACTION = "data_extraction"
    ANALYSIS = "analysis"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MetaAnalysis(Base):
    """
    Meta-analysis database model for persistent storage.

    This model stores the core metadata and configuration for each meta-analysis,
    replacing the in-memory coordinators_by_id dict.
    """

    __tablename__ = "meta_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Research parameters
    research_question = Column(Text, nullable=False)
    topic = Column(String(500), nullable=False, index=True)
    inclusion_criteria = Column(JSONB, nullable=True)  # List of inclusion criteria
    exclusion_criteria = Column(JSONB, nullable=True)  # List of exclusion criteria

    # Configuration
    databases = Column(JSONB, nullable=True)  # List of databases to search
    peer_review_only = Column(String(50), nullable=True, default="false")
    expert_name = Column(String(255), nullable=True)

    # Status tracking
    status = Column(
        SQLEnum(MetaAnalysisStatus, name="meta_analysis_status", native_enum=False),
        nullable=False,
        default=MetaAnalysisStatus.CREATED,
        index=True,
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="meta_analyses")
    coordinator_state = relationship(
        "CoordinatorState",
        back_populates="meta_analysis",
        uselist=False,
        cascade="all, delete-orphan",
    )
    agent_executions = relationship(
        "AgentExecution",
        back_populates="meta_analysis",
        cascade="all, delete-orphan",
        order_by="AgentExecution.executed_at",
    )

    def __repr__(self):
        """String representation."""
        return f"<MetaAnalysis {self.id} - {self.topic} ({self.status})>"


class CoordinatorState(Base):
    """
    Coordinator agent state for recovery and horizontal scaling.

    This model stores the complete state of the coordinator agent,
    allowing it to be recovered after crashes or loaded by any worker.
    """

    __tablename__ = "coordinator_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("meta_analyses.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Coordinator state serialization
    agent_state = Column(JSONB, nullable=False)  # Serialized agent internal state
    decisions = Column(JSONB, nullable=False, default=list)  # List of agent decisions
    workflow_plan = Column(JSONB, nullable=True)  # Workflow plan created by coordinator

    # Metadata
    coordinator_id = Column(UUID(as_uuid=True), nullable=False)  # Original coordinator agent ID
    version = Column(String(50), nullable=True, default="1.0")  # State schema version

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    meta_analysis = relationship("MetaAnalysis", back_populates="coordinator_state")

    def __repr__(self):
        """String representation."""
        return f"<CoordinatorState {self.id} for Analysis {self.analysis_id}>"


class AgentExecution(Base):
    """
    Agent execution audit trail for debugging and analysis.

    This model provides a complete audit trail of all agent executions,
    enabling debugging, performance analysis, and result reproducibility.
    """

    __tablename__ = "agent_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("meta_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Agent information
    agent_name = Column(String(100), nullable=False, index=True)
    agent_role = Column(String(50), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), nullable=False)

    # Execution data
    input_data = Column(JSONB, nullable=False)  # Input provided to the agent
    output_data = Column(JSONB, nullable=False)  # Output generated by the agent
    error_message = Column(Text, nullable=True)  # Error message if execution failed

    # Performance metrics
    execution_time_ms = Column(String(50), nullable=True)  # Execution time in milliseconds
    tokens_used = Column(String(50), nullable=True)  # LLM tokens consumed (if applicable)

    # Status
    status = Column(
        String(50),
        nullable=False,
        default="success",
        index=True,
    )  # success, failed, partial

    # Timestamp
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    meta_analysis = relationship("MetaAnalysis", back_populates="agent_executions")

    def __repr__(self):
        """String representation."""
        return f"<AgentExecution {self.agent_name} at {self.executed_at}>"
