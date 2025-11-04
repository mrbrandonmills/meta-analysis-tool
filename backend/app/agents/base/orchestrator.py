"""Agent orchestrator for coordinating multiple agents."""
import asyncio
from typing import Any, Dict, List, Optional
from uuid import UUID

from loguru import logger

from .agent import BaseAgent
from .types import AgentMessage, AgentRole, AgentStatus, AgentTask


class AgentOrchestrator:
    """Orchestrates collaboration between multiple agents."""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[UUID, AgentTask] = {}
        self.message_queue: List[AgentMessage] = []

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator.

        Args:
            agent: Agent to register
        """
        self.agents[agent.config.name] = agent
        logger.info(f"Registered agent: {agent.config.name} ({agent.config.role})")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name.

        Args:
            name: Agent name

        Returns:
            Agent instance or None
        """
        return self.agents.get(name)

    def get_agents_by_role(self, role: AgentRole) -> List[BaseAgent]:
        """Get all agents with a specific role.

        Args:
            role: Agent role to filter by

        Returns:
            List of agents with that role
        """
        return [agent for agent in self.agents.values() if agent.config.role == role]

    async def create_task(
        self, role: AgentRole, description: str, input_data: Dict[str, Any]
    ) -> AgentTask:
        """Create a new task for an agent.

        Args:
            role: Role of agent to handle this task
            description: Task description
            input_data: Input data for the task

        Returns:
            Created task
        """
        task = AgentTask(role=role, description=description, input_data=input_data)

        self.tasks[task.id] = task
        logger.info(f"Created task {task.id} for role {role}: {description}")

        return task

    async def execute_task(self, task_id: UUID) -> Dict[str, Any]:
        """Execute a task.

        Args:
            task_id: ID of task to execute

        Returns:
            Task result
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Find agent for this task
        agents = self.get_agents_by_role(task.role)
        if not agents:
            raise ValueError(f"No agent available for role {task.role}")

        agent = agents[0]  # Use first available agent

        logger.info(f"Executing task {task_id} with agent {agent.config.name}")

        task.status = AgentStatus.WORKING
        task.started_at = asyncio.get_event_loop().time()

        try:
            result = await agent.process(task.input_data)
            task.result = result
            task.status = AgentStatus.COMPLETED
            logger.info(f"Task {task_id} completed successfully")

        except Exception as e:
            task.error = str(e)
            task.status = AgentStatus.ERROR
            logger.error(f"Task {task_id} failed: {e}")
            raise

        finally:
            task.completed_at = asyncio.get_event_loop().time()

        return result

    async def execute_workflow(self, workflow: List[AgentTask]) -> Dict[str, Any]:
        """Execute a workflow of multiple tasks.

        Args:
            workflow: List of tasks to execute

        Returns:
            Workflow results
        """
        logger.info(f"Executing workflow with {len(workflow)} tasks")

        results = {}
        for task in workflow:
            # Wait for dependencies
            if task.dependencies:
                logger.debug(f"Waiting for dependencies: {task.dependencies}")
                # In a real implementation, check if dependencies are completed

            result = await self.execute_task(task.id)
            results[str(task.id)] = result

        logger.info("Workflow completed")
        return results

    async def route_message(self, message: AgentMessage):
        """Route a message to its destination agent.

        Args:
            message: Message to route
        """
        to_agent = self.get_agent(message.to_agent)
        if not to_agent:
            logger.warning(f"Agent {message.to_agent} not found for message routing")
            return

        await to_agent.receive_message(message)

    def get_all_decisions(self) -> List[Dict[str, Any]]:
        """Get all decisions made by all agents.

        Returns:
            List of all decisions
        """
        all_decisions = []
        for agent in self.agents.values():
            decisions = agent.get_decision_trail()
            all_decisions.extend([d.model_dump() for d in decisions])

        return sorted(all_decisions, key=lambda x: x["timestamp"])

    def get_audit_trail(self) -> Dict[str, Any]:
        """Get complete audit trail for all agents.

        Returns:
            Complete audit trail
        """
        return {
            "agents": {name: agent.get_audit_log() for name, agent in self.agents.items()},
            "tasks": {str(task_id): task.model_dump() for task_id, task in self.tasks.items()},
            "total_decisions": sum(len(agent.decisions) for agent in self.agents.values()),
        }
