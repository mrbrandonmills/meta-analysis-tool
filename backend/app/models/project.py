"""Project model."""

from typing import TYPE_CHECKING, Optional
import enum

from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workflow import Workflow
    from app.models.paper import Paper
    from app.models.researcher import Researcher


class ToolType(str, enum.Enum):
    """Tool type enumeration."""

    META_ANALYSIS = "meta_analysis"
    RESEARCH_DIRECTION = "research_direction"
    PEER_REVIEW = "peer_review"
    REVIEWER_MATCHER = "reviewer_matcher"


class ProjectStatus(str, enum.Enum):
    """Project status enumeration."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Project(Base, BaseModel):
    """Project model - universal container for all tools."""

    __tablename__ = "projects"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_type = Column(SQLEnum(ToolType), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False, index=True)

    # Flexible storage for tool-specific configuration
    config = Column(JSONB, nullable=True, default=dict)

    # Shared results across all tools
    findings = Column(JSONB, nullable=True, default=dict)
    metadata = Column(JSONB, nullable=True, default=dict)

    # Relationships
    user = relationship("User", back_populates="projects")
    workflows = relationship("Workflow", back_populates="project", cascade="all, delete-orphan", lazy="dynamic")

    # Many-to-many relationships
    papers = relationship("Paper", secondary="project_papers", back_populates="projects", lazy="dynamic")
    researchers = relationship("Researcher", secondary="project_researchers", back_populates="projects", lazy="dynamic")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Project(id={self.id}, tool={self.tool_type}, status={self.status})>"
