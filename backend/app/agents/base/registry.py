"""Agent registry for managing available agents."""
from typing import Dict, List, Optional

from loguru import logger

from .agent import BaseAgent
from .types import AgentProfile, AgentRole


class AgentRegistry:
    """Registry of available agents and their capabilities.

    This allows for plugin-style agent management where new
    agents can be added dynamically.
    """

    def __init__(self):
        self._agents: Dict[str, type[BaseAgent]] = {}
        self._profiles: Dict[str, AgentProfile] = {}

    def register(self, agent_class: type[BaseAgent], profile: AgentProfile):
        """Register a new agent type.

        Args:
            agent_class: Agent class to register
            profile: Agent profile with metadata
        """
        name = profile.name
        self._agents[name] = agent_class
        self._profiles[name] = profile

        logger.info(
            f"Registered agent: {name} ({profile.role})"
            + (f" - Expert: {profile.expert_name}" if profile.expert_name else "")
        )

    def unregister(self, name: str):
        """Unregister an agent.

        Args:
            name: Agent name to unregister
        """
        if name in self._agents:
            del self._agents[name]
            del self._profiles[name]
            logger.info(f"Unregistered agent: {name}")

    def get_agent_class(self, name: str) -> Optional[type[BaseAgent]]:
        """Get agent class by name.

        Args:
            name: Agent name

        Returns:
            Agent class or None
        """
        return self._agents.get(name)

    def get_profile(self, name: str) -> Optional[AgentProfile]:
        """Get agent profile by name.

        Args:
            name: Agent name

        Returns:
            Agent profile or None
        """
        return self._profiles.get(name)

    def list_agents(self) -> List[str]:
        """List all registered agent names.

        Returns:
            List of agent names
        """
        return list(self._agents.keys())

    def list_by_role(self, role: AgentRole) -> List[AgentProfile]:
        """List all agents with a specific role.

        Args:
            role: Agent role to filter by

        Returns:
            List of agent profiles
        """
        return [profile for profile in self._profiles.values() if profile.role == role]

    def get_all_profiles(self) -> List[AgentProfile]:
        """Get all agent profiles.

        Returns:
            List of all agent profiles
        """
        return list(self._profiles.values())


# Global registry instance
_registry = AgentRegistry()


def get_registry() -> AgentRegistry:
    """Get the global agent registry.

    Returns:
        Global registry instance
    """
    return _registry
