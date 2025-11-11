"""Research Direction model - Consolidated model for Tool 2.

This model stores the complete output from the Research Direction Agent,
including gaps, questions, and proposals in a single record.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.meta_analysis import MetaAnalysis


class ResearchDirection(Base, BaseModel):
    """Research direction analysis results.

    This model stores the complete output from analyzing a meta-analysis,
    including identified gaps, generated research questions, and detailed proposals.
    """

    __tablename__ = "research_directions"

    # Foreign keys
    meta_analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("meta_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Analysis configuration
    focus_areas = Column(
        ARRAY(String),
        nullable=True,
        comment="Specific areas focused on during analysis (e.g., methodology, populations)"
    )
    max_proposals = Column(
        String(50),
        nullable=True,
        default="5",
        comment="Maximum number of proposals requested"
    )
    include_literature_review = Column(
        String(50),
        nullable=True,
        default="true",
        comment="Whether detailed literature review was included"
    )

    # Analysis results (stored as JSONB for flexibility)
    gaps_identified = Column(
        JSONB,
        nullable=False,
        default=list,
        comment="Array of identified research gaps with metadata"
    )
    research_questions = Column(
        JSONB,
        nullable=False,
        default=list,
        comment="Array of generated research questions with rationale"
    )
    research_proposals = Column(
        JSONB,
        nullable=False,
        default=list,
        comment="Array of detailed research proposals"
    )
    priority_ranking = Column(
        JSONB,
        nullable=True,
        default=list,
        comment="Ranked list of proposal titles by priority"
    )

    # Quality metrics
    completeness_score = Column(
        Float,
        nullable=True,
        comment="Score 0.0-1.0 indicating completeness of the analysis"
    )
    num_gaps = Column(
        String(50),
        nullable=True,
        comment="Number of gaps identified"
    )
    num_questions = Column(
        String(50),
        nullable=True,
        comment="Number of research questions generated"
    )
    num_proposals = Column(
        String(50),
        nullable=True,
        comment="Number of proposals created"
    )

    # Processing metadata
    processing_time_seconds = Column(
        Float,
        nullable=True,
        comment="Time taken to generate research directions"
    )
    model_version = Column(
        String(100),
        nullable=True,
        default="claude-sonnet-4-5-20250929",
        comment="AI model version used"
    )
    agent_version = Column(
        String(50),
        nullable=True,
        default="0.1.0",
        comment="Research Direction Agent version"
    )

    # Export tracking
    exported_formats = Column(
        ARRAY(String),
        nullable=True,
        comment="Formats this was exported to (pdf, word, markdown)"
    )
    last_exported_at = Column(
        String(100),
        nullable=True,
        comment="ISO timestamp of last export"
    )

    # Additional metadata
    analysis_metadata = Column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional metadata about the analysis"
    )

    # Relationships
    meta_analysis = relationship(
        "MetaAnalysis",
        foreign_keys=[meta_analysis_id],
        backref="research_directions"
    )
    user = relationship(
        "User",
        foreign_keys=[user_id]
    )

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<ResearchDirection(id={self.id}, "
            f"meta_analysis_id={self.meta_analysis_id}, "
            f"gaps={self.num_gaps}, "
            f"proposals={self.num_proposals})>"
        )

    @property
    def summary(self) -> str:
        """Get a brief summary of the research direction."""
        return (
            f"Identified {self.num_gaps or 0} gaps, "
            f"generated {self.num_questions or 0} questions, "
            f"created {self.num_proposals or 0} proposals "
            f"(completeness: {self.completeness_score or 0:.1%})"
        )

    def get_top_priority_proposals(self, limit: int = 3) -> list:
        """Get top priority proposals based on ranking.

        Args:
            limit: Maximum number of proposals to return

        Returns:
            List of top priority proposals
        """
        if not self.priority_ranking or not self.research_proposals:
            return []

        # Map ranking to full proposals
        top_proposals = []
        for title in self.priority_ranking[:limit]:
            for proposal in self.research_proposals:
                if proposal.get("title") == title:
                    top_proposals.append(proposal)
                    break

        return top_proposals

    def get_critical_gaps(self) -> list:
        """Get gaps marked as critical severity.

        Returns:
            List of critical gaps
        """
        if not self.gaps_identified:
            return []

        return [
            gap for gap in self.gaps_identified
            if gap.get("severity") == "critical"
        ]

    def get_gaps_by_type(self, gap_type: str) -> list:
        """Get all gaps of a specific type.

        Args:
            gap_type: Type of gap (methodology, population, etc.)

        Returns:
            List of gaps matching the type
        """
        if not self.gaps_identified:
            return []

        return [
            gap for gap in self.gaps_identified
            if gap.get("gap_type") == gap_type
        ]

    def get_feasible_proposals(self, min_feasibility: float = 0.7) -> list:
        """Get proposals with high feasibility scores.

        Args:
            min_feasibility: Minimum feasibility score (0.0-1.0)

        Returns:
            List of feasible proposals
        """
        if not self.research_proposals:
            return []

        return [
            proposal for proposal in self.research_proposals
            if proposal.get("feasibility_score", 0) >= min_feasibility
        ]

    def get_high_impact_proposals(self, min_impact: float = 0.7) -> list:
        """Get proposals with high impact scores.

        Args:
            min_impact: Minimum impact score (0.0-1.0)

        Returns:
            List of high-impact proposals
        """
        if not self.research_proposals:
            return []

        return [
            proposal for proposal in self.research_proposals
            if proposal.get("impact_score", 0) >= min_impact
        ]

    def to_export_dict(self, include_sections: list = None) -> dict:
        """Convert to dictionary suitable for export.

        Args:
            include_sections: List of sections to include (gaps, questions, proposals)

        Returns:
            Export-ready dictionary
        """
        if include_sections is None:
            include_sections = ["gaps", "questions", "proposals"]

        export_data = {
            "id": str(self.id),
            "generated_at": self.created_at.isoformat() if self.created_at else None,
            "completeness_score": self.completeness_score,
            "meta_analysis_id": str(self.meta_analysis_id)
        }

        if "gaps" in include_sections:
            export_data["gaps_identified"] = self.gaps_identified

        if "questions" in include_sections:
            export_data["research_questions"] = self.research_questions

        if "proposals" in include_sections:
            export_data["research_proposals"] = self.research_proposals
            export_data["priority_ranking"] = self.priority_ranking

        return export_data
