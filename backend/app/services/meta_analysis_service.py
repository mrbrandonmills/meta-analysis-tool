"""Meta-analysis persistence service for database operations."""

import json
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.specialized import CoordinatorAgent
from app.models.meta_analysis import MetaAnalysis, CoordinatorState, AgentExecution, MetaAnalysisStatus


def json_serializable(obj: Any) -> Any:
    """Convert objects to JSON-serializable types.

    Handles:
    - UUID -> str
    - Enum -> value
    - datetime -> ISO format str
    - dict -> recursively convert values
    - list -> recursively convert items
    - other -> attempt str() conversion
    """
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [json_serializable(item) for item in obj]
    elif hasattr(obj, "__dict__"):
        return json_serializable(obj.__dict__)
    else:
        return obj


class MetaAnalysisService:
    """Service for persisting and retrieving meta-analysis state."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db

    def create_meta_analysis(
        self,
        user_id: UUID,
        research_question: str,
        topic: str,
        inclusion_criteria: list[str],
        exclusion_criteria: list[str],
        databases: list[str],
        peer_review_only: bool,
        expert_name: Optional[str] = None,
    ) -> MetaAnalysis:
        """Create a new meta-analysis record.

        Args:
            user_id: ID of the user creating the analysis
            research_question: Research question to investigate
            topic: Topic/title of the meta-analysis
            inclusion_criteria: List of inclusion criteria
            exclusion_criteria: List of exclusion criteria
            databases: List of databases to search
            peer_review_only: Whether to filter for peer-reviewed studies only
            expert_name: Optional expert profile name

        Returns:
            Created MetaAnalysis instance
        """
        meta_analysis = MetaAnalysis(
            user_id=user_id,
            research_question=research_question,
            topic=topic,
            inclusion_criteria=inclusion_criteria,
            exclusion_criteria=exclusion_criteria,
            databases=databases,
            peer_review_only=str(peer_review_only).lower(),
            expert_name=expert_name,
            status=MetaAnalysisStatus.CREATED,
        )

        self.db.add(meta_analysis)
        self.db.flush()  # Get ID without committing
        logger.info(f"Created meta-analysis {meta_analysis.id} for user {user_id}")

        return meta_analysis

    async def save_coordinator_state(
        self,
        analysis_id: UUID,
        coordinator: CoordinatorAgent,
        workflow_plan: Optional[Dict[str, Any]] = None,
    ) -> CoordinatorState:
        """Save or update coordinator agent state.

        Args:
            analysis_id: ID of the meta-analysis
            coordinator: Coordinator agent instance
            workflow_plan: Optional workflow plan data

        Returns:
            Created or updated CoordinatorState instance
        """
        # Check if state already exists
        result = await self.db.execute(
            select(CoordinatorState)
            .where(CoordinatorState.analysis_id == analysis_id)
        )
        existing_state = result.scalar_one_or_none()

        # Serialize coordinator state
        agent_state = self._serialize_coordinator_state(coordinator)
        decisions = [self._serialize_decision(d) for d in coordinator.decisions]

        # Serialize workflow_plan to ensure all nested objects are JSON-compatible
        serialized_workflow_plan = json_serializable(workflow_plan) if workflow_plan else None

        if existing_state:
            # Update existing state
            existing_state.agent_state = agent_state
            existing_state.decisions = decisions
            if serialized_workflow_plan:
                existing_state.workflow_plan = serialized_workflow_plan
            coordinator_state = existing_state
            logger.info(f"Updated coordinator state for analysis {analysis_id}")
        else:
            # Create new state
            coordinator_state = CoordinatorState(
                analysis_id=analysis_id,
                coordinator_id=coordinator.id,
                agent_state=agent_state,
                decisions=decisions,
                workflow_plan=serialized_workflow_plan,
            )
            self.db.add(coordinator_state)
            logger.info(f"Created coordinator state for analysis {analysis_id}")

        await self.db.flush()
        return coordinator_state

    async def get_meta_analysis(self, analysis_id: UUID) -> Optional[MetaAnalysis]:
        """Retrieve a meta-analysis by ID.

        Args:
            analysis_id: ID of the meta-analysis

        Returns:
            MetaAnalysis instance or None if not found
        """
        result = await self.db.execute(
            select(MetaAnalysis)
            .where(MetaAnalysis.id == analysis_id)
        )
        return result.scalar_one_or_none()

    async def get_coordinator_state(self, analysis_id: UUID) -> Optional[CoordinatorState]:
        """Retrieve coordinator state for a meta-analysis.

        Args:
            analysis_id: ID of the meta-analysis

        Returns:
            CoordinatorState instance or None if not found
        """
        result = await self.db.execute(
            select(CoordinatorState)
            .where(CoordinatorState.analysis_id == analysis_id)
        )
        return result.scalar_one_or_none()

    async def restore_coordinator(
        self,
        analysis_id: UUID,
        coordinator_config: Any,
    ) -> Optional[CoordinatorAgent]:
        """Restore a coordinator agent from database state.

        Args:
            analysis_id: ID of the meta-analysis
            coordinator_config: AgentConfig for coordinator

        Returns:
            Restored CoordinatorAgent instance or None if state not found
        """
        state = await self.get_coordinator_state(analysis_id)
        if not state:
            logger.warning(f"No coordinator state found for analysis {analysis_id}")
            return None

        # Create new coordinator instance
        coordinator = CoordinatorAgent(coordinator_config)

        # Restore coordinator ID and state
        coordinator.id = state.coordinator_id

        # Restore decisions
        if state.decisions:
            coordinator.decisions = state.decisions

        # Restore agent state (status, context, etc.)
        if state.agent_state:
            if "status" in state.agent_state:
                coordinator.status = state.agent_state["status"]
            if "context" in state.agent_state:
                coordinator.context = state.agent_state["context"]

        logger.info(f"Restored coordinator {coordinator.id} for analysis {analysis_id}")
        return coordinator

    async def update_meta_analysis_status(
        self,
        analysis_id: UUID,
        status: MetaAnalysisStatus,
    ) -> Optional[MetaAnalysis]:
        """Update meta-analysis status.

        Args:
            analysis_id: ID of the meta-analysis
            status: New status

        Returns:
            Updated MetaAnalysis instance or None if not found
        """
        meta_analysis = await self.get_meta_analysis(analysis_id)
        if meta_analysis:
            meta_analysis.status = status
            await self.db.flush()
            logger.info(f"Updated meta-analysis {analysis_id} status to {status}")
        return meta_analysis

    def log_agent_execution(
        self,
        analysis_id: UUID,
        agent_name: str,
        agent_role: str,
        agent_id: UUID,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        status: str = "success",
        error_message: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
    ) -> AgentExecution:
        """Log an agent execution for audit trail.

        Args:
            analysis_id: ID of the meta-analysis
            agent_name: Name of the agent
            agent_role: Role of the agent
            agent_id: ID of the agent instance
            input_data: Input provided to the agent
            output_data: Output generated by the agent
            status: Execution status (success, failed, partial)
            error_message: Optional error message if execution failed
            execution_time_ms: Execution time in milliseconds
            tokens_used: LLM tokens consumed

        Returns:
            Created AgentExecution instance
        """
        execution = AgentExecution(
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
        )

        self.db.add(execution)
        self.db.flush()
        logger.debug(f"Logged {agent_name} execution for analysis {analysis_id}")

        return execution

    def _serialize_coordinator_state(self, coordinator: CoordinatorAgent) -> Dict[str, Any]:
        """Serialize coordinator agent state to JSON-compatible dict.

        Args:
            coordinator: CoordinatorAgent instance

        Returns:
            Serialized state dictionary
        """
        return {
            "status": coordinator.status,
            "context": coordinator.context if hasattr(coordinator, "context") else {},
            "config": {
                "name": coordinator.config.name,
                "role": coordinator.config.role.value if hasattr(coordinator.config.role, "value") else str(coordinator.config.role),
                "expert_profile": coordinator.config.expert_profile,
            },
        }

    def _serialize_decision(self, decision: Any) -> Dict[str, Any]:
        """Serialize a decision to JSON-compatible dict.

        Args:
            decision: Decision object (can be dict or custom type)

        Returns:
            Serialized decision dictionary
        """
        return json_serializable(decision)
