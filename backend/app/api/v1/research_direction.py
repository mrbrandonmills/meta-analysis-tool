"""Research Direction API endpoints - Tool 2 of the 4-tool platform.

This module provides REST API endpoints for generating research directions
from completed meta-analyses.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.agents.specialized.research_direction_agent import ResearchDirectionAgent
from app.models.user import User
from app.models.meta_analysis import MetaAnalysis, MetaAnalysisStatus
from app.models.research_gap import ResearchGap, GapType, GapPriority
from app.models.research_proposal import ResearchProposal, ProposalStatus, ProposalType
from app.models.project import Project, ToolType

router = APIRouter()


# Request/Response Models

class GenerateDirectionRequest(BaseModel):
    """Request to generate research directions."""

    meta_analysis_id: UUID = Field(..., description="ID of completed meta-analysis")
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Specific areas to focus on (e.g., methodology, populations)"
    )
    max_proposals: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of research proposals to generate"
    )
    include_literature_review: bool = Field(
        default=True,
        description="Include detailed literature review in gaps"
    )


class GapIdentified(BaseModel):
    """Identified research gap."""

    gap_type: str
    title: str
    description: str
    evidence: str
    severity: str
    impact_potential: Optional[float] = None
    feasibility_score: Optional[float] = None
    novelty_score: Optional[float] = None
    reasoning: Optional[str] = None
    confidence: Optional[float] = None


class ResearchQuestionItem(BaseModel):
    """Generated research question."""

    question: str
    rationale: str
    gap_addressed: str
    expected_contribution: str
    feasibility: float
    novelty_score: Optional[float] = None
    priority: str


class MethodologyDetail(BaseModel):
    """Research methodology details."""

    design: str
    population: Optional[str] = None
    intervention: Optional[str] = None
    comparator: Optional[str] = None
    outcomes: List[str]
    measures: List[str]
    analysis_plan: str
    data_collection: Optional[str] = None


class ResearchProposalItem(BaseModel):
    """Generated research proposal."""

    title: str
    research_question: str
    background: Optional[str] = None
    significance: Optional[str] = None
    innovation: Optional[str] = None
    methodology: MethodologyDetail
    expected_outcomes: Optional[str] = None
    expected_impact: str
    timeline: Optional[str] = None
    feasibility_score: float
    impact_score: Optional[float] = None
    novelty_score: Optional[float] = None
    budget_estimate: Optional[str] = None
    key_challenges: Optional[List[str]] = None
    mitigation_strategies: Optional[List[str]] = None


class ResearchDirectionResponse(BaseModel):
    """Response containing generated research directions."""

    id: UUID
    project_id: UUID
    meta_analysis_id: UUID
    gaps_identified: List[GapIdentified]
    research_questions: List[ResearchQuestionItem]
    research_proposals: List[ResearchProposalItem]
    priority_ranking: List[str]
    completeness_score: float
    generated_at: datetime

    class Config:
        from_attributes = True


class ResearchDirectionSummary(BaseModel):
    """Summary of generated research direction."""

    id: UUID
    project_id: UUID
    meta_analysis_id: UUID
    num_gaps: int
    num_questions: int
    num_proposals: int
    completeness_score: float
    generated_at: datetime


class ExportRequest(BaseModel):
    """Request to export research direction."""

    format: str = Field(..., description="Export format: pdf, word, markdown")
    include_sections: Optional[List[str]] = Field(
        default=None,
        description="Sections to include: gaps, questions, proposals"
    )


# API Endpoints

@router.post(
    "/research-direction/generate",
    response_model=ResearchDirectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate research directions from meta-analysis",
    description="Analyzes completed meta-analysis to identify gaps and generate research proposals"
)
async def generate_research_direction(
    request: GenerateDirectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate research directions from a completed meta-analysis.

    This endpoint:
    1. Validates the meta-analysis exists and is completed
    2. Analyzes results to identify research gaps
    3. Generates novel research questions
    4. Creates detailed research proposals
    5. Saves all results to the database
    """
    logger.info(f"User {current_user.id} generating research directions for meta-analysis {request.meta_analysis_id}")

    try:
        # 1. Fetch and validate meta-analysis
        result = await db.execute(
            select(MetaAnalysis).where(
                and_(
                    MetaAnalysis.id == request.meta_analysis_id,
                    MetaAnalysis.user_id == current_user.id
                )
            )
        )
        meta_analysis = result.scalar_one_or_none()

        if not meta_analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meta-analysis {request.meta_analysis_id} not found or access denied"
            )

        # Check if meta-analysis is completed
        if meta_analysis.status != MetaAnalysisStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Meta-analysis must be completed. Current status: {meta_analysis.status}"
            )

        # 2. Create or get project for Tool 2
        project = await _get_or_create_project(db, current_user.id, meta_analysis)

        # 3. Initialize Research Direction Agent
        agent = ResearchDirectionAgent()

        # 4. Generate research directions
        logger.info("Generating research directions...")
        directions = await agent.analyze_meta_analysis(
            db=db,
            meta_analysis_id=request.meta_analysis_id,
            focus_areas=request.focus_areas,
            max_proposals=request.max_proposals
        )

        # 5. Save gaps to database
        gap_models = []
        for gap_data in directions.get("gaps_identified", []):
            gap = ResearchGap(
                project_id=project.id,
                title=gap_data.get("title", ""),
                description=gap_data.get("description", ""),
                gap_type=GapType(gap_data.get("gap_type", "methodology")),
                evidence=[gap_data.get("evidence", "")],
                impact_potential=gap_data.get("impact_potential"),
                feasibility_score=gap_data.get("feasibility_score"),
                novelty_score=gap_data.get("novelty_score"),
                priority=_map_severity_to_priority(gap_data.get("severity", "medium")),
                reasoning=gap_data.get("reasoning"),
                confidence=gap_data.get("confidence"),
                gap_metadata=gap_data
            )
            db.add(gap)
            gap_models.append(gap)

        # 6. Save proposals to database
        proposal_models = []
        for proposal_data in directions.get("research_proposals", []):
            methodology = proposal_data.get("methodology", {})

            proposal = ResearchProposal(
                project_id=project.id,
                title=proposal_data.get("title", ""),
                research_question=proposal_data.get("research_question", ""),
                background=proposal_data.get("background"),
                significance=proposal_data.get("significance"),
                innovation=proposal_data.get("innovation"),
                methodology=proposal_data.get("methodology_text", str(methodology)),
                expected_outcomes=proposal_data.get("expected_outcomes"),
                expected_impact=proposal_data.get("expected_impact", ""),
                timeline=proposal_data.get("timeline"),
                budget_overview=proposal_data.get("budget_estimate"),
                study_design=methodology.get("design") if isinstance(methodology, dict) else None,
                study_population=methodology.get("population") if isinstance(methodology, dict) else None,
                intervention=methodology.get("intervention") if isinstance(methodology, dict) else None,
                comparator=methodology.get("comparator") if isinstance(methodology, dict) else None,
                outcomes=methodology.get("outcomes", []) if isinstance(methodology, dict) else [],
                novelty_score=proposal_data.get("novelty_score"),
                feasibility_score=proposal_data.get("feasibility_score"),
                impact_score=proposal_data.get("impact_score"),
                status=ProposalStatus.DRAFT,
                proposal_type=ProposalType.RESEARCH_PLAN,
                ai_generated=True,
                proposal_metadata=proposal_data
            )
            db.add(proposal)
            proposal_models.append(proposal)

        # 7. Commit to database
        await db.commit()

        # 8. Refresh models to get IDs
        for gap in gap_models:
            await db.refresh(gap)
        for proposal in proposal_models:
            await db.refresh(proposal)

        logger.info(f"Successfully generated and saved research directions: "
                   f"{len(gap_models)} gaps, {len(proposal_models)} proposals")

        # 9. Build response
        response = ResearchDirectionResponse(
            id=project.id,  # Using project ID as research direction ID
            project_id=project.id,
            meta_analysis_id=request.meta_analysis_id,
            gaps_identified=[GapIdentified(**gap) for gap in directions.get("gaps_identified", [])],
            research_questions=[
                ResearchQuestionItem(**q) for q in directions.get("research_questions", [])
            ],
            research_proposals=[
                ResearchProposalItem(
                    **{k: v for k, v in p.items() if k != "methodology"},
                    methodology=MethodologyDetail(**p.get("methodology", {}))
                )
                for p in directions.get("research_proposals", [])
            ],
            priority_ranking=directions.get("priority_ranking", []),
            completeness_score=directions.get("completeness_score", 0.0),
            generated_at=datetime.utcnow()
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating research directions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate research directions: {str(e)}"
        )


@router.get(
    "/research-direction/by-meta-analysis/{meta_analysis_id}",
    response_model=ResearchDirectionResponse,
    summary="Get research directions for a meta-analysis",
    description="Retrieves previously generated research directions for a meta-analysis"
)
async def get_research_direction_by_meta_analysis(
    meta_analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get research directions generated for a specific meta-analysis."""
    logger.info(f"Fetching research directions for meta-analysis {meta_analysis_id}")

    try:
        # Find project associated with meta-analysis
        result = await db.execute(
            select(Project).where(
                and_(
                    Project.tool_type == ToolType.RESEARCH_DIRECTION,
                    Project.created_by == current_user.id
                )
            )
        )
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No research directions found for this meta-analysis"
            )

        # Fetch gaps
        gaps_result = await db.execute(
            select(ResearchGap).where(ResearchGap.project_id == project.id)
        )
        gaps = gaps_result.scalars().all()

        # Fetch proposals
        proposals_result = await db.execute(
            select(ResearchProposal).where(ResearchProposal.project_id == project.id)
        )
        proposals = proposals_result.scalars().all()

        # Build response
        response = ResearchDirectionResponse(
            id=project.id,
            project_id=project.id,
            meta_analysis_id=meta_analysis_id,
            gaps_identified=[
                GapIdentified(
                    gap_type=gap.gap_type.value,
                    title=gap.title,
                    description=gap.description,
                    evidence=gap.evidence[0] if gap.evidence else "",
                    severity=gap.priority.value if gap.priority else "medium",
                    impact_potential=gap.impact_potential,
                    feasibility_score=gap.feasibility_score,
                    novelty_score=gap.novelty_score,
                    reasoning=gap.reasoning,
                    confidence=gap.confidence
                )
                for gap in gaps
            ],
            research_questions=[],  # Questions not stored separately
            research_proposals=[
                ResearchProposalItem(
                    title=proposal.title,
                    research_question=proposal.research_question,
                    background=proposal.background,
                    significance=proposal.significance,
                    innovation=proposal.innovation,
                    methodology=MethodologyDetail(
                        design=proposal.study_design or "Not specified",
                        population=proposal.study_population,
                        intervention=proposal.intervention,
                        comparator=proposal.comparator,
                        outcomes=proposal.outcomes or [],
                        measures=[],
                        analysis_plan=proposal.methodology or "",
                        data_collection=None
                    ),
                    expected_outcomes=proposal.expected_outcomes,
                    expected_impact=proposal.expected_impact or "",
                    timeline=proposal.timeline,
                    feasibility_score=proposal.feasibility_score or 0.5,
                    impact_score=proposal.impact_score,
                    novelty_score=proposal.novelty_score,
                    budget_estimate=proposal.budget_overview,
                    key_challenges=None,
                    mitigation_strategies=None
                )
                for proposal in proposals
            ],
            priority_ranking=[p.title for p in sorted(
                proposals,
                key=lambda x: (x.impact_score or 0) * 0.4 + (x.feasibility_score or 0) * 0.35 + (x.novelty_score or 0) * 0.25,
                reverse=True
            )],
            completeness_score=_calculate_completeness_from_db(gaps, proposals),
            generated_at=project.created_at
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching research directions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch research directions: {str(e)}"
        )


@router.get(
    "/research-direction/history",
    response_model=List[ResearchDirectionSummary],
    summary="List user's research direction history",
    description="Returns all research directions generated by the current user"
)
async def get_research_direction_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all research directions generated by the user."""
    logger.info(f"Fetching research direction history for user {current_user.id}")

    try:
        # Fetch projects
        result = await db.execute(
            select(Project)
            .where(
                and_(
                    Project.tool_type == ToolType.RESEARCH_DIRECTION,
                    Project.created_by == current_user.id
                )
            )
            .order_by(Project.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        projects = result.scalars().all()

        summaries = []
        for project in projects:
            # Count gaps and proposals
            gaps_count = await db.scalar(
                select(ResearchGap).where(ResearchGap.project_id == project.id)
            )
            proposals_count = await db.scalar(
                select(ResearchProposal).where(ResearchProposal.project_id == project.id)
            )

            # Note: meta_analysis_id would need to be stored in project metadata
            summaries.append(
                ResearchDirectionSummary(
                    id=project.id,
                    project_id=project.id,
                    meta_analysis_id=project.id,  # Placeholder
                    num_gaps=gaps_count or 0,
                    num_questions=0,  # Not stored separately
                    num_proposals=proposals_count or 0,
                    completeness_score=0.8,  # Would need to be calculated
                    generated_at=project.created_at
                )
            )

        return summaries

    except Exception as e:
        logger.error(f"Error fetching history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}"
        )


@router.delete(
    "/research-direction/{direction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete research direction",
    description="Deletes a research direction and all associated gaps/proposals"
)
async def delete_research_direction(
    direction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a research direction (soft delete)."""
    logger.info(f"Deleting research direction {direction_id}")

    try:
        # Fetch project (research direction)
        result = await db.execute(
            select(Project).where(
                and_(
                    Project.id == direction_id,
                    Project.created_by == current_user.id,
                    Project.tool_type == ToolType.RESEARCH_DIRECTION
                )
            )
        )
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Research direction not found"
            )

        # Soft delete (if using soft delete mixin)
        await db.delete(project)
        await db.commit()

        logger.info(f"Successfully deleted research direction {direction_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting research direction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete research direction: {str(e)}"
        )


# Helper Functions

async def _get_or_create_project(
    db: AsyncSession,
    user_id: UUID,
    meta_analysis: MetaAnalysis
) -> Project:
    """Get or create a project for research direction generation."""
    # Try to find existing project
    result = await db.execute(
        select(Project).where(
            and_(
                Project.tool_type == ToolType.RESEARCH_DIRECTION,
                Project.created_by == user_id,
                Project.name.contains(meta_analysis.topic)
            )
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        # Create new project
        project = Project(
            name=f"Research Direction: {meta_analysis.topic}",
            description=f"Research directions generated from meta-analysis on: {meta_analysis.research_question}",
            tool_type=ToolType.RESEARCH_DIRECTION,
            created_by=user_id
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)

    return project


def _map_severity_to_priority(severity: str) -> GapPriority:
    """Map severity to GapPriority enum."""
    severity_map = {
        "critical": GapPriority.CRITICAL,
        "high": GapPriority.HIGH,
        "medium": GapPriority.MEDIUM,
        "low": GapPriority.LOW
    }
    return severity_map.get(severity.lower(), GapPriority.MEDIUM)


def _calculate_completeness_from_db(
    gaps: List[ResearchGap],
    proposals: List[ResearchProposal]
) -> float:
    """Calculate completeness score from database models."""
    gap_score = min(len(gaps) / 5.0, 1.0)
    proposal_score = min(len(proposals) / 3.0, 1.0)

    # Quality score
    all_scores = []
    all_scores.extend([g.feasibility_score for g in gaps if g.feasibility_score])
    all_scores.extend([p.feasibility_score for p in proposals if p.feasibility_score])

    quality_score = sum(all_scores) / len(all_scores) if all_scores else 0.5

    return round((gap_score * 0.4 + proposal_score * 0.4 + quality_score * 0.2), 3)
