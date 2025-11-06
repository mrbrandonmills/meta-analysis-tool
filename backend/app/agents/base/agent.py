"""Base agent class."""
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from anthropic import Anthropic, APIError, AuthenticationError, RateLimitError, APIConnectionError
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import get_settings
from .types import AgentDecision, AgentMessage, AgentRole, AgentStatus

settings = get_settings()


class AgentConfig(BaseModel):
    """Agent configuration."""

    name: str
    role: AgentRole
    model: str = "claude-3-opus-20240229"  # Most capable Claude 3 model
    temperature: float = 0.3
    max_tokens: int = 4096
    expert_profile: Optional[str] = None
    version: str = "0.1.0"


class BaseAgent(ABC):
    """Base class for all specialized agents.

    Each agent represents expert knowledge in a specific domain
    and can make decisions, communicate with other agents, and
    learn from feedback.
    """

    def __init__(self, config: AgentConfig):
        self.id = uuid4()
        self.config = config
        self.status = AgentStatus.IDLE
        self.decisions: List[AgentDecision] = []
        self.messages: List[AgentMessage] = []
        self.client = Anthropic(api_key=settings.anthropic_api_key)

        logger.info(f"Initialized {self.config.role} agent: {self.config.name}")

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return output.

        Args:
            input_data: Input data for the agent to process

        Returns:
            Processing result
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent.

        This prompt encodes the expert knowledge and instructions
        for how the agent should behave.

        Returns:
            System prompt string
        """
        pass

    async def think(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Use LLM to think through a problem.

        Args:
            prompt: The prompt/question to think about
            context: Additional context for the prompt

        Returns:
            LLM response
        """
        self.status = AgentStatus.THINKING

        system_prompt = self.get_system_prompt()
        if context:
            prompt = f"Context: {context}\n\n{prompt}"

        try:
            message = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            response = message.content[0].text
            logger.debug(f"{self.config.name} thought process: {response[:200]}...")

            return response

        # CRITICAL FIX: Add specific Anthropic exception handling
        except AuthenticationError as e:
            error_msg = (
                f"Anthropic API authentication failed for {self.config.name}. "
                f"Please verify your ANTHROPIC_API_KEY is correct. Error: {e}"
            )
            logger.error(error_msg)
            self.status = AgentStatus.ERROR
            raise ValueError(error_msg) from e

        except RateLimitError as e:
            error_msg = (
                f"Anthropic API rate limit exceeded for {self.config.name}. "
                f"Please wait before retrying. Error: {e}"
            )
            logger.error(error_msg)
            self.status = AgentStatus.ERROR
            raise ValueError(error_msg) from e

        except APIConnectionError as e:
            error_msg = (
                f"Failed to connect to Anthropic API for {self.config.name}. "
                f"Please check your network connection. Error: {e}"
            )
            logger.error(error_msg)
            self.status = AgentStatus.ERROR
            raise ValueError(error_msg) from e

        except APIError as e:
            error_msg = (
                f"Anthropic API error in {self.config.name}: {e}. "
                f"Status code: {getattr(e, 'status_code', 'unknown')}"
            )
            logger.error(error_msg)
            self.status = AgentStatus.ERROR
            raise ValueError(error_msg) from e

        except Exception as e:
            logger.error(f"Unexpected error in {self.config.name} think: {e}")
            self.status = AgentStatus.ERROR
            raise

    async def make_decision(
        self,
        decision_prompt: str,
        input_data: Dict[str, Any],
        confidence_threshold: float = 0.7,
    ) -> AgentDecision:
        """Make a decision and log it.

        Args:
            decision_prompt: What decision needs to be made
            input_data: Input data for the decision
            confidence_threshold: Minimum confidence required

        Returns:
            AgentDecision object with reasoning and confidence
        """
        self.status = AgentStatus.WORKING

        # Ask LLM to make decision with reasoning and confidence
        prompt = f"""
{decision_prompt}

Input data: {input_data}

Please provide your decision in the following format:
Decision: [your decision]
Reasoning: [detailed reasoning for your decision]
Confidence: [0.0-1.0, how confident you are]
Sources: [any sources or references you used]
"""

        response = await self.think(prompt, context=input_data)

        # Parse response (in production, use structured output)
        # For now, simple parsing
        lines = response.strip().split("\n")
        decision_text = ""
        reasoning = ""
        confidence = 0.8
        sources = []

        for line in lines:
            if line.startswith("Decision:"):
                decision_text = line.replace("Decision:", "").strip()
            elif line.startswith("Reasoning:"):
                reasoning = line.replace("Reasoning:", "").strip()
            elif line.startswith("Confidence:"):
                try:
                    confidence = float(line.replace("Confidence:", "").strip())
                except ValueError:
                    confidence = 0.8
            elif line.startswith("Sources:"):
                sources_str = line.replace("Sources:", "").strip()
                sources = [s.strip() for s in sources_str.split(",") if s.strip()]

        decision = AgentDecision(
            agent_role=self.config.role,
            agent_name=self.config.name,
            decision=decision_text,
            reasoning=reasoning,
            confidence=confidence,
            sources=sources,
            input_data=input_data,
            output_data={"decision": decision_text},
            expert_profile=self.config.expert_profile,
            version=self.config.version,
        )

        self.decisions.append(decision)
        logger.info(
            f"{self.config.name} made decision: {decision_text} "
            f"(confidence: {confidence:.2f})"
        )

        if confidence < confidence_threshold:
            logger.warning(
                f"Low confidence decision: {confidence:.2f} < {confidence_threshold}"
            )

        return decision

    async def send_message(self, to_agent: str, content: Dict[str, Any], priority: int = 1):
        """Send a message to another agent.

        Args:
            to_agent: Name of the recipient agent
            content: Message content
            priority: Message priority (1-10)
        """
        message = AgentMessage(
            from_agent=self.config.name, to_agent=to_agent, content=content, priority=priority
        )

        self.messages.append(message)
        logger.debug(f"{self.config.name} -> {to_agent}: {content}")

        return message

    async def receive_message(self, message: AgentMessage) -> Dict[str, Any]:
        """Receive and process a message from another agent.

        Args:
            message: Incoming message

        Returns:
            Response to the message
        """
        logger.debug(f"{self.config.name} received message from {message.from_agent}")
        self.messages.append(message)

        # Process message based on content
        # This can be overridden by subclasses
        return {"status": "acknowledged"}

    def get_decision_trail(self) -> List[AgentDecision]:
        """Get all decisions made by this agent.

        Returns:
            List of decisions
        """
        return self.decisions

    def get_audit_log(self) -> Dict[str, Any]:
        """Get complete audit log for this agent.

        Returns:
            Audit log with all decisions and messages
        """
        return {
            "agent_id": str(self.id),
            "agent_name": self.config.name,
            "agent_role": self.config.role,
            "expert_profile": self.config.expert_profile,
            "version": self.config.version,
            "decisions": [d.model_dump() for d in self.decisions],
            "messages_sent": len([m for m in self.messages if m.from_agent == self.config.name]),
            "messages_received": len([m for m in self.messages if m.to_agent == self.config.name]),
        }
