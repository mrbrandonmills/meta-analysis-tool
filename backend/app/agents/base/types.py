"""Agent type definitions."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Agent role types."""

    COORDINATOR = "coordinator"
    SEARCH = "search"
    SCREENING = "screening"
    QUALITY_ASSESSMENT = "quality_assessment"
    DATA_EXTRACTION = "data_extraction"
    STATISTICAL = "statistical"
    REPORT = "report"
    QA = "qa"  # Question-Answering
    VERIFICATION = "verification"
    SECURITY = "security"
    INTEGRITY = "integrity"
    REVIEWER_MATCHING = "reviewer_matching"  # Expert reviewer matching


class AgentStatus(str, Enum):
    """Agent execution status."""

    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


class AgentMessage(BaseModel):
    """Message between agents."""

    id: UUID = Field(default_factory=uuid4)
    from_agent: str
    to_agent: str
    content: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    priority: int = Field(default=1, ge=1, le=10)


class AgentDecision(BaseModel):
    """Represents a decision made by an agent."""

    id: UUID = Field(default_factory=uuid4)
    agent_role: AgentRole
    agent_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    decision: str
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Provenance tracking
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None

    # Expert information
    expert_profile: Optional[str] = None  # Who programmed this agent
    version: str = "0.1.0"


class AgentTask(BaseModel):
    """Task assigned to an agent."""

    id: UUID = Field(default_factory=uuid4)
    role: AgentRole
    description: str
    input_data: Dict[str, Any]
    dependencies: List[UUID] = Field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AgentProfile(BaseModel):
    """Agent profile with expert information."""

    name: str
    role: AgentRole
    version: str
    description: str
    expert_name: Optional[str] = None
    expert_institution: Optional[str] = None
    expert_credentials: Optional[str] = None
    programming_date: datetime = Field(default_factory=datetime.utcnow)
    capabilities: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    prompt_template: Optional[str] = None
