"""Meta-analysis API endpoints with PostgreSQL persistence."""
import json
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.base import AgentConfig, AgentOrchestrator
from app.agents.specialized import CoordinatorAgent, SearchAgent, ScreeningAgent, QAAgent, CredibilityAgent
from app.db.session import get_async_db
from app.models.meta_analysis import MetaAnalysis, CoordinatorState, AgentExecution, MetaAnalysisStatus
from app.models.user import User

router = APIRouter()

# Global orchestrator (can be moved to dependency injection)
orchestrator = AgentOrchestrator()


class MetaAnalysisRequest(BaseModel):
    """Request to create a new meta-analysis."""

    research_question: str
    topic: str
    inclusion_criteria: List[str] = Field(default_factory=list)
    exclusion_criteria: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=lambda: ["pubmed", "arxiv", "europepmc", "core"])
    peer_review_only: bool = Field(default=False, description="Filter out preprints and non-peer-reviewed studies")
    expert_name: str | None = None
    user_id: Optional[str] = None  # In production, get from JWT token


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


async def serialize_coordinator_state(coordinator: CoordinatorAgent) -> dict:
    """
    Serialize coordinator agent state to JSON-compatible dict.

    Args:
        coordinator: CoordinatorAgent instance

    Returns:
        Dict with serialized state
    """
    return {
        "id": str(coordinator.id),
        "name": coordinator.name,
        "role": coordinator.role,
        "status": coordinator.status,
        "expert_profile": coordinator.expert_profile,
        "context": coordinator.context,
        # Add other relevant state fields
    }


async def deserialize_coordinator_state(
    state_data: dict,
    decisions: List[dict],
    workflow_plan: Optional[dict]
) -> CoordinatorAgent:
    """
    Deserialize coordinator agent from database state.

    Args:
        state_data: Serialized agent state
        decisions: List of agent decisions
        workflow_plan: Workflow plan (if any)

    Returns:
        Reconstructed CoordinatorAgent instance
    """
    # Recreate coordinator config
    config = AgentConfig(
        name=state_data.get("name", "Coordinator"),
        role=state_data.get("role", "coordinator"),
        expert_profile=state_data.get("expert_profile"),
    )

    # Create coordinator agent
    coordinator = CoordinatorAgent(config)

    # Restore state
    coordinator.status = state_data.get("status", "idle")
    coordinator.context = state_data.get("context", {})
    coordinator.decisions = decisions

    return coordinator


async def save_agent_execution(
    db: AsyncSession,
    analysis_id: UUID,
    agent_name: str,
    agent_role: str,
    agent_id: UUID,
    input_data: dict,
    output_data: dict,
    status: str = "success",
    error_message: Optional[str] = None,
    execution_time_ms: Optional[int] = None,
    tokens_used: Optional[int] = None,
) -> AgentExecution:
    """
    Save agent execution to audit trail.

    Args:
        db: Database session
        analysis_id: Meta-analysis ID
        agent_name: Name of the agent
        agent_role: Role of the agent
        agent_id: Agent instance ID
        input_data: Input data provided to agent
        output_data: Output data from agent
        status: Execution status (success, failed, partial)
        error_message: Error message if failed
        execution_time_ms: Execution time in milliseconds
        tokens_used: Number of LLM tokens used

    Returns:
        Created AgentExecution record
    """
    execution = AgentExecution(
        id=uuid4(),
        analysis_id=analysis_id,
        agent_name=agent_name,
        agent_role=agent_role,
        agent_id=agent_id,
        input_data=input_data,
        output_data=output_data,
        status=status,
        error_message=error_message,
        execution_time_ms=str(execution_time_ms) if execution_time_ms else None,
        tokens_used=str(tokens_used) if tokens_used else None,
        executed_at=datetime.utcnow(),
    )

    db.add(execution)
    await db.commit()
    await db.refresh(execution)

    return execution


@router.post("/meta-analysis/create", response_model=MetaAnalysisResponse)
async def create_meta_analysis(
    request: MetaAnalysisRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Create a new meta-analysis with PostgreSQL persistence.

    This endpoint:
    1. Creates a MetaAnalysis record in the database
    2. Initializes the coordinator agent
    3. Creates a workflow plan
    4. Saves coordinator state to database
    5. Returns the plan for approval

    Args:
        request: Meta-analysis creation request
        db: Database session

    Returns:
        MetaAnalysisResponse with workflow plan
    """
    try:
        logger.info(f"Creating meta-analysis: {request.topic}")

        # TODO: In production, get user_id from JWT token
        # For now, use first user or create a default one
        user_id = UUID(request.user_id) if request.user_id else None

        if not user_id:
            # Get first user from database
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=400, detail="No user found. Please create a user first.")
            user_id = user.id

        # Create MetaAnalysis record
        meta_analysis = MetaAnalysis(
            id=uuid4(),
            user_id=user_id,
            research_question=request.research_question,
            topic=request.topic,
            inclusion_criteria=request.inclusion_criteria,
            exclusion_criteria=request.exclusion_criteria,
            databases=request.databases,
            peer_review_only=str(request.peer_review_only).lower(),
            expert_name=request.expert_name,
            status=MetaAnalysisStatus.CREATED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(meta_analysis)
        await db.flush()  # Flush to get the ID without committing

        # Initialize coordinator agent
        coordinator_config = AgentConfig(
            name="Coordinator",
            role="coordinator",  # type: ignore
            expert_profile=request.expert_name,
        )
        coordinator = CoordinatorAgent(coordinator_config)
        orchestrator.register_agent(coordinator)

        logger.info(f"Created coordinator with ID: {coordinator.id}")

        # Process the request to create workflow
        result = await coordinator.process(request.model_dump())

        # Serialize coordinator state
        agent_state = await serialize_coordinator_state(coordinator)

        # Create CoordinatorState record
        coordinator_state = CoordinatorState(
            id=uuid4(),
            analysis_id=meta_analysis.id,
            coordinator_id=coordinator.id,
            agent_state=agent_state,
            decisions=coordinator.decisions,
            workflow_plan=result,
            version="1.0",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db.add(coordinator_state)

        # Update meta-analysis status
        meta_analysis.status = MetaAnalysisStatus.WORKFLOW_CREATED
        meta_analysis.updated_at = datetime.utcnow()

        # Save agent execution to audit trail
        await save_agent_execution(
            db=db,
            analysis_id=meta_analysis.id,
            agent_name=coordinator.name,
            agent_role="coordinator",
            agent_id=coordinator.id,
            input_data=request.model_dump(),
            output_data=result,
            status="success",
        )

        await db.commit()

        logger.info(f"Saved meta-analysis to database: {meta_analysis.id}")

        return MetaAnalysisResponse(
            id=str(meta_analysis.id),
            status=meta_analysis.status.value,
            message="Meta-analysis workflow created successfully",
            workflow=result,
        )

    except Exception as e:
        logger.error(f"Error creating meta-analysis: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meta-analysis/execute/{analysis_id}")
async def execute_meta_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Execute a meta-analysis workflow with database persistence.

    This endpoint:
    1. Loads the meta-analysis from database
    2. Restores coordinator state
    3. Runs the search agent
    4. Runs the screening agent
    5. Saves all results and state to database
    6. Returns preliminary results

    Args:
        analysis_id: Meta-analysis ID
        db: Database session

    Returns:
        Execution results
    """
    try:
        logger.info(f"Executing meta-analysis: {analysis_id}")

        # Load meta-analysis from database
        result = await db.execute(
            select(MetaAnalysis).where(MetaAnalysis.id == UUID(analysis_id))
        )
        meta_analysis = result.scalar_one_or_none()

        if not meta_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Meta-analysis not found. Analysis ID: {analysis_id}"
            )

        # Load coordinator state
        result = await db.execute(
            select(CoordinatorState).where(CoordinatorState.analysis_id == UUID(analysis_id))
        )
        coordinator_state_record = result.scalar_one_or_none()

        if not coordinator_state_record:
            raise HTTPException(
                status_code=400,
                detail="Coordinator state not found. Please create the workflow first."
            )

        # Restore coordinator from database state
        coordinator = await deserialize_coordinator_state(
            coordinator_state_record.agent_state,
            coordinator_state_record.decisions,
            coordinator_state_record.workflow_plan,
        )

        # Update meta-analysis status
        meta_analysis.status = MetaAnalysisStatus.IN_PROGRESS
        meta_analysis.updated_at = datetime.utcnow()

        # Initialize search agent
        search_config = AgentConfig(name="SearchAgent", role="search")  # type: ignore
        search_agent = SearchAgent(search_config)
        orchestrator.register_agent(search_agent)

        # Execute search
        search_input = {
            "research_question": meta_analysis.research_question,
            "search_terms": ["mindfulness", "anxiety", "RCT"],  # TODO: Extract from workflow
            "databases": meta_analysis.databases or ["pubmed"],
        }
        search_results = await search_agent.process(search_input)

        # Save search execution to audit trail
        await save_agent_execution(
            db=db,
            analysis_id=meta_analysis.id,
            agent_name=search_agent.name,
            agent_role="search",
            agent_id=search_agent.id,
            input_data=search_input,
            output_data=search_results,
            status="success",
        )

        # Initialize screening agent
        screening_config = AgentConfig(name="ScreeningAgent", role="screening")  # type: ignore
        screening_agent = ScreeningAgent(screening_config)
        orchestrator.register_agent(screening_agent)

        # Execute screening
        screening_input = {
            "studies": search_results["studies"],
            "inclusion_criteria": meta_analysis.inclusion_criteria or [],
            "exclusion_criteria": meta_analysis.exclusion_criteria or [],
            "screening_level": "title_abstract",
        }
        screening_results = await screening_agent.process(screening_input)

        # Save screening execution to audit trail
        await save_agent_execution(
            db=db,
            analysis_id=meta_analysis.id,
            agent_name=screening_agent.name,
            agent_role="screening",
            agent_id=screening_agent.id,
            input_data=screening_input,
            output_data=screening_results,
            status="success",
        )

        # Initialize credibility agent
        credibility_config = AgentConfig(name="CredibilityAgent", role="quality_assessment")  # type: ignore
        credibility_agent = CredibilityAgent(credibility_config)
        orchestrator.register_agent(credibility_agent)

        # Evaluate credibility of included studies
        credibility_input = {
            "studies": screening_results["included"],
            "require_peer_review": meta_analysis.peer_review_only == "true",
        }
        credibility_results = await credibility_agent.process(credibility_input)

        # Save credibility execution to audit trail
        await save_agent_execution(
            db=db,
            analysis_id=meta_analysis.id,
            agent_name=credibility_agent.name,
            agent_role="quality_assessment",
            agent_id=credibility_agent.id,
            input_data=credibility_input,
            output_data=credibility_results,
            status="success",
        )

        # Update coordinator state in database
        coordinator_state_record.decisions = coordinator.decisions
        coordinator_state_record.updated_at = datetime.utcnow()

        # Update meta-analysis status
        meta_analysis.status = MetaAnalysisStatus.SCREENING
        meta_analysis.updated_at = datetime.utcnow()

        await db.commit()

        logger.info(f"Execution completed for meta-analysis: {analysis_id}")

        return {
            "analysis_id": analysis_id,
            "status": meta_analysis.status.value,
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
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta-analysis/status/{analysis_id}")
async def get_status(
    analysis_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get the status of a meta-analysis from database.

    Args:
        analysis_id: Meta-analysis ID
        db: Database session

    Returns:
        Status information
    """
    try:
        # Load meta-analysis from database
        result = await db.execute(
            select(MetaAnalysis).where(MetaAnalysis.id == UUID(analysis_id))
        )
        meta_analysis = result.scalar_one_or_none()

        if not meta_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Meta-analysis not found. Analysis ID: {analysis_id}"
            )

        # Load coordinator state
        result = await db.execute(
            select(CoordinatorState).where(CoordinatorState.analysis_id == UUID(analysis_id))
        )
        coordinator_state = result.scalar_one_or_none()

        return {
            "id": str(meta_analysis.id),
            "topic": meta_analysis.topic,
            "status": meta_analysis.status.value,
            "research_question": meta_analysis.research_question,
            "created_at": meta_analysis.created_at.isoformat(),
            "updated_at": meta_analysis.updated_at.isoformat(),
            "decisions": len(coordinator_state.decisions) if coordinator_state else 0,
        }

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta-analysis/audit/{analysis_id}")
async def get_audit_trail(
    analysis_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get the complete audit trail for a meta-analysis from database.

    Args:
        analysis_id: Meta-analysis ID
        db: Database session

    Returns:
        Complete audit trail
    """
    try:
        # Load all agent executions for this analysis
        result = await db.execute(
            select(AgentExecution)
            .where(AgentExecution.analysis_id == UUID(analysis_id))
            .order_by(AgentExecution.executed_at)
        )
        executions = result.scalars().all()

        audit_trail = []
        for execution in executions:
            audit_trail.append({
                "id": str(execution.id),
                "agent_name": execution.agent_name,
                "agent_role": execution.agent_role,
                "status": execution.status,
                "executed_at": execution.executed_at.isoformat(),
                "execution_time_ms": execution.execution_time_ms,
                "tokens_used": execution.tokens_used,
                "input_summary": {
                    "keys": list(execution.input_data.keys()) if execution.input_data else [],
                },
                "output_summary": {
                    "keys": list(execution.output_data.keys()) if execution.output_data else [],
                },
                "error_message": execution.error_message,
            })

        return {
            "analysis_id": analysis_id,
            "total_executions": len(audit_trail),
            "executions": audit_trail,
        }

    except Exception as e:
        logger.error(f"Error getting audit trail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meta-analysis/ask")
async def ask_question(
    request: QuestionRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Ask a question about a meta-analysis.

    This uses the Q&A agent to answer questions about
    the process, methodology, or results.

    Args:
        request: Question request
        db: Database session

    Returns:
        Answer with confidence and sources
    """
    try:
        logger.info(f"Question asked: {request.question}")

        # Initialize Q&A agent
        qa_config = AgentConfig(name="QAAgent", role="qa")  # type: ignore
        qa_agent = QAAgent(qa_config)

        # Get context from database if meta_analysis_id provided
        context = {}
        if request.meta_analysis_id:
            result = await db.execute(
                select(AgentExecution)
                .where(AgentExecution.analysis_id == UUID(request.meta_analysis_id))
                .order_by(AgentExecution.executed_at)
            )
            executions = result.scalars().all()

            context = {
                "executions": [
                    {
                        "agent": exec.agent_name,
                        "role": exec.agent_role,
                        "timestamp": exec.executed_at.isoformat(),
                        "status": exec.status,
                    }
                    for exec in executions
                ]
            }

        # Update Q&A agent with context
        qa_agent.update_context(context)

        # Process question
        result = await qa_agent.process({
            "question": request.question,
            "meta_analysis_id": request.meta_analysis_id,
            "context": context,
        })

        # Save Q&A execution to audit trail if meta_analysis_id provided
        if request.meta_analysis_id:
            await save_agent_execution(
                db=db,
                analysis_id=UUID(request.meta_analysis_id),
                agent_name=qa_agent.name,
                agent_role="qa",
                agent_id=qa_agent.id,
                input_data={"question": request.question},
                output_data=result,
                status="success",
            )
            await db.commit()

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
async def get_report(
    analysis_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get the final report for a meta-analysis.

    Args:
        analysis_id: Meta-analysis ID
        db: Database session

    Returns:
        Report metadata
    """
    try:
        # Load meta-analysis from database
        result = await db.execute(
            select(MetaAnalysis).where(MetaAnalysis.id == UUID(analysis_id))
        )
        meta_analysis = result.scalar_one_or_none()

        if not meta_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Meta-analysis not found. Analysis ID: {analysis_id}"
            )

        # This would generate an APA-formatted report
        return {
            "id": analysis_id,
            "topic": meta_analysis.topic,
            "status": "report_ready" if meta_analysis.status == MetaAnalysisStatus.COMPLETED else "in_progress",
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

    except Exception as e:
        logger.error(f"Error getting report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
