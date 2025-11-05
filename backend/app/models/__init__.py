"""Database models package."""

from app.models.base import BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin
from app.models.user import User, UserRole
from app.models.project import Project, ToolType, ProjectStatus
from app.models.workflow import Workflow, WorkflowStatus, AgentRole
from app.models.paper import Paper, CredibilityLevel, DatabaseSource
from app.models.researcher import Researcher
from app.models.manuscript import Manuscript, ManuscriptStatus, ManuscriptType
from app.models.peer_review import PeerReview, ReviewRecommendation, ReviewStatus
from app.models.reviewer_match import ReviewerMatch, MatchStatus, ConflictType
from app.models.research_gap import ResearchGap, GapType, GapPriority
from app.models.research_proposal import ResearchProposal, ProposalStatus, ProposalType
from app.models.associations import project_papers, project_researchers, paper_authors

__all__ = [
    # Base models and mixins
    "BaseModel",
    "UUIDMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    # Core models
    "User",
    "UserRole",
    "Project",
    "ToolType",
    "ProjectStatus",
    "Workflow",
    "WorkflowStatus",
    "AgentRole",
    # Shared models
    "Paper",
    "CredibilityLevel",
    "DatabaseSource",
    "Researcher",
    # Tool 3: Peer Review models
    "Manuscript",
    "ManuscriptStatus",
    "ManuscriptType",
    "PeerReview",
    "ReviewRecommendation",
    "ReviewStatus",
    # Tool 4: Reviewer Matcher models
    "ReviewerMatch",
    "MatchStatus",
    "ConflictType",
    # Tool 2: Research Direction models
    "ResearchGap",
    "GapType",
    "GapPriority",
    "ResearchProposal",
    "ProposalStatus",
    "ProposalType",
    # Association tables
    "project_papers",
    "project_researchers",
    "paper_authors",
]
