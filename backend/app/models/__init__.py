"""Database models package."""

from app.models.base import BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin
from app.models.user import User, UserRole
from app.models.project import Project, ToolType, ProjectStatus
from app.models.workflow import Workflow, WorkflowStatus, AgentRole
from app.models.paper import Paper, CredibilityLevel, DatabaseSource
from app.models.pdf_metadata import (
    PDFMetadata,
    PDFDownloadStatus,
    PDFSource,
    FullTextExtraction,
    SectionType,
    FullTextScreening
)
from app.models.researcher import Researcher
from app.models.manuscript import Manuscript, ManuscriptStatus, ManuscriptType
from app.models.peer_review import PeerReview, ReviewRecommendation, ReviewStatus
from app.models.reviewer_match import ReviewerMatch, MatchStatus, ConflictType
from app.models.research_gap import ResearchGap, GapType, GapPriority
from app.models.research_proposal import ResearchProposal, ProposalStatus, ProposalType
from app.models.research_direction import ResearchDirection
from app.models.meta_analysis import MetaAnalysis, CoordinatorState, AgentExecution, MetaAnalysisStatus
from app.models.report import Report, ReportTemplate, ReportFormat, ReportStatus
from app.models.associations import project_papers, project_researchers, paper_authors
# Payment ecosystem models
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionPlanType
from app.models.payout_pool import PayoutPool, PayoutPoolStatus
from app.models.payout_contribution import PayoutContribution, ContributionStatus
from app.models.review_completion import ReviewCompletion, PayoutStatus
from app.models.payout_distribution import PayoutDistribution, TransferStatus

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
    # PDF and full-text models
    "PDFMetadata",
    "PDFDownloadStatus",
    "PDFSource",
    "FullTextExtraction",
    "SectionType",
    "FullTextScreening",
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
    "ResearchDirection",
    # Report models
    "Report",
    "ReportTemplate",
    "ReportFormat",
    "ReportStatus",
    # Tool 1: Meta-analysis models
    "MetaAnalysis",
    "CoordinatorState",
    "AgentExecution",
    "MetaAnalysisStatus",
    # Association tables
    "project_papers",
    "project_researchers",
    "paper_authors",
    # Payment ecosystem models
    "Subscription",
    "SubscriptionStatus",
    "SubscriptionPlanType",
    "PayoutPool",
    "PayoutPoolStatus",
    "PayoutContribution",
    "ContributionStatus",
    "ReviewCompletion",
    "PayoutStatus",
    "PayoutDistribution",
    "TransferStatus",
]
