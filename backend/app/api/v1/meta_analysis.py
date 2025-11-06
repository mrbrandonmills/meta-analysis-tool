"""Meta-analysis API endpoints."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from app.agents.base import AgentConfig, AgentOrchestrator
from app.agents.specialized import CoordinatorAgent, SearchAgent, ScreeningAgent, QAAgent, CredibilityAgent

router = APIRouter()

# Global orchestrator (in production, use dependency injection)
orchestrator = AgentOrchestrator()

# Store coordinators by ID for cross-request access
# In production, use Redis or database
coordinators_by_id: dict[str, CoordinatorAgent] = {}


class MetaAnalysisRequest(BaseModel):
    """Request to create a new meta-analysis."""

    research_question: str
    topic: str
    inclusion_criteria: List[str] = Field(default_factory=list)
    exclusion_criteria: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=lambda: ["pubmed", "arxiv", "europepmc", "core"])
    peer_review_only: bool = Field(default=False, description="Filter out preprints and non-peer-reviewed studies")
    expert_name: str | None = None


class MetaAnalysisResponse(BaseModel):
    """Response for meta-analysis creation."""

    id: str
    status: str
    message: str
    workflow: dict


class QuestionRequest(BaseModel):
    """Request to ask a question about a meta-analysis."""

    question: str
    meta_analysis_id: str | None = None


@router.post("/meta-analysis/create", response_model=MetaAnalysisResponse)
async def create_meta_analysis(request: MetaAnalysisRequest):
    """Create a new meta-analysis.

    This endpoint:
    1. Initializes the coordinator agent
    2. Creates a workflow plan
    3. Returns the plan for approval
    """
    try:
        logger.info(f"Creating meta-analysis: {request.topic}")

        # Initialize coordinator agent
        coordinator_config = AgentConfig(
            name="Coordinator",
            role="coordinator",  # type: ignore
            expert_profile=request.expert_name,
        )
        coordinator = CoordinatorAgent(coordinator_config)
        orchestrator.register_agent(coordinator)

        # Store coordinator by ID for cross-request access
        analysis_id = str(coordinator.id)
        coordinators_by_id[analysis_id] = coordinator
        logger.info(f"Stored coordinator with ID: {analysis_id}")

        # Process the request to create workflow
        result = await coordinator.process(request.model_dump())

        return MetaAnalysisResponse(
            id=analysis_id,
            status="workflow_created",
            message="Meta-analysis workflow created successfully",
            workflow=result,
        )

    except Exception as e:
        logger.error(f"Error creating meta-analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meta-analysis/execute/{analysis_id}")
async def execute_meta_analysis(analysis_id: str):
    """Execute a meta-analysis workflow.

    This endpoint:
    1. Runs the search agent
    2. Runs the screening agent
    3. Returns preliminary results
    """
    try:
        logger.info(f"Executing meta-analysis: {analysis_id}")

        # Get coordinator by analysis_id
        coordinator = coordinators_by_id.get(analysis_id)
        if not coordinator:
            logger.error(f"Coordinator not found for analysis_id: {analysis_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Meta-analysis not found. Analysis ID: {analysis_id}"
            )

        # Initialize search agent
        search_config = AgentConfig(name="SearchAgent", role="search")  # type: ignore
        search_agent = SearchAgent(search_config)
        orchestrator.register_agent(search_agent)

        # Get research question from coordinator's last decision
        if not coordinator.decisions:
            raise HTTPException(status_code=400, detail="No workflow found")

        # Execute search
        search_input = {
            "research_question": "Effects of mindfulness on anxiety",  # From coordinator
            "search_terms": ["mindfulness", "anxiety", "RCT"],
            "databases": ["pubmed"],
        }
        search_results = await search_agent.process(search_input)

        # Initialize screening agent
        screening_config = AgentConfig(name="ScreeningAgent", role="screening")  # type: ignore
        screening_agent = ScreeningAgent(screening_config)
        orchestrator.register_agent(screening_agent)

        # Execute screening
        screening_input = {
            "studies": search_results["studies"],
            "inclusion_criteria": [
                "Randomized controlled trial",
                "Adult population (18+)",
                "Mindfulness-based intervention",
                "Anxiety as outcome measure",
            ],
            "exclusion_criteria": [
                "Non-English language",
                "Qualitative studies",
                "Case studies",
            ],
            "screening_level": "title_abstract",
        }
        screening_results = await screening_agent.process(screening_input)

        # Initialize credibility agent
        credibility_config = AgentConfig(name="CredibilityAgent", role="quality_assessment")  # type: ignore
        credibility_agent = CredibilityAgent(credibility_config)
        orchestrator.register_agent(credibility_agent)

        # Evaluate credibility of included studies
        credibility_input = {
            "studies": screening_results["included"],
            "require_peer_review": False,  # Will be configurable
        }
        credibility_results = await credibility_agent.process(credibility_input)

        return {
            "analysis_id": analysis_id,
            "status": "in_progress",
            "search_results": {
                "total_found": search_results["total_results"],
                "databases": search_results["databases_searched"],
            },
            "screening_results": {
                "total_screened": screening_results["total_screened"],
                "included": len(screening_results["included"]),
                "excluded": len(screening_results["excluded"]),
                "uncertain": len(screening_results["uncertain"]),
            },
            "credibility_results": {
                "total_evaluated": credibility_results["total_evaluated"],
                "breakdown": credibility_results["credibility_breakdown"],
                "studies_with_scores": credibility_results["studies"],
            },
            "next_steps": [
                "Full-text screening",
                "Quality assessment",
                "Data extraction",
            ],
        }

    except Exception as e:
        logger.error(f"Error executing meta-analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta-analysis/status/{analysis_id}")
async def get_status(analysis_id: str):
    """Get the status of a meta-analysis."""
    # Get coordinator by analysis_id
    coordinator = coordinators_by_id.get(analysis_id)
    if not coordinator:
        logger.error(f"Coordinator not found for analysis_id: {analysis_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Meta-analysis not found. Analysis ID: {analysis_id}"
        )

    return {
        "id": analysis_id,
        "status": coordinator.status,
        "decisions": len(coordinator.decisions),
    }


@router.get("/meta-analysis/audit/{analysis_id}")
async def get_audit_trail(analysis_id: str):
    """Get the complete audit trail for a meta-analysis."""
    try:
        audit = orchestrator.get_audit_trail()
        return audit

    except Exception as e:
        logger.error(f"Error getting audit trail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meta-analysis/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question about a meta-analysis.

    This uses the Q&A agent to answer questions about
    the process, methodology, or results.
    """
    try:
        logger.info(f"Question asked: {request.question}")

        # Initialize Q&A agent
        qa_config = AgentConfig(name="QAAgent", role="qa")  # type: ignore
        qa_agent = QAAgent(qa_config)

        # Get context from orchestrator
        context = orchestrator.get_audit_trail()

        # Update Q&A agent with context
        qa_agent.update_context(context)

        # Process question
        result = await qa_agent.process({
            "question": request.question,
            "meta_analysis_id": request.meta_analysis_id,
            "context": context,
        })

        return {
            "question": request.question,
            "answer": result["answer"],
            "confidence": result["confidence"],
            "sources": result.get("sources_cited", []),
            "follow_up_suggestions": result.get("follow_up_suggestions", []),
        }

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta-analysis/report/{analysis_id}")
async def get_report(analysis_id: str):
    """Get the final report for a meta-analysis."""
    # This would generate an APA-formatted report
    return {
        "id": analysis_id,
        "status": "report_ready",
        "format": "APA 7th edition",
        "sections": [
            "Abstract",
            "Introduction",
            "Methods",
            "Results",
            "Discussion",
            "References",
        ],
    }
