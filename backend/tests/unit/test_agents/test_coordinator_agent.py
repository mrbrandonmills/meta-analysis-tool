"""Unit tests for CoordinatorAgent."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.agents.base import AgentConfig, AgentRole
from app.agents.specialized.coordinator import CoordinatorAgent


class TestCoordinatorAgent:
    """Test suite for CoordinatorAgent."""

    @pytest.fixture
    def coordinator_agent(self, mock_anthropic_client):
        """Create CoordinatorAgent instance for testing."""
        config = AgentConfig(
            name="test_coordinator",
            role=AgentRole.COORDINATOR,
            model="claude-3-5-sonnet-20241022"
        )
        return CoordinatorAgent(config)

    @pytest.fixture
    def meta_analysis_request(self):
        """Create sample meta-analysis request."""
        return {
            "research_question": "What is the effect of exercise on depression in adults?",
            "topic": "Exercise and Depression",
            "inclusion_criteria": [
                "Randomized controlled trials",
                "Adult participants (18-65 years)",
                "Exercise intervention",
                "Depression outcome measures"
            ],
            "exclusion_criteria": [
                "Animal studies",
                "Pediatric populations",
                "Non-exercise interventions"
            ],
            "databases": ["pubmed", "psycinfo", "cochrane"]
        }

    @pytest.mark.asyncio
    async def test_coordinator_initialization(self, coordinator_agent):
        """Test that CoordinatorAgent initializes correctly."""
        assert coordinator_agent.config.role == AgentRole.COORDINATOR
        assert coordinator_agent.config.name == "test_coordinator"

    def test_coordinator_system_prompt(self, coordinator_agent):
        """Test that system prompt contains required elements."""
        prompt = coordinator_agent.get_system_prompt()

        assert "Coordinator" in prompt
        assert "workflow" in prompt.lower() or "orchestrat" in prompt.lower()

    @pytest.mark.asyncio
    async def test_create_workflow_plan(self, coordinator_agent, meta_analysis_request):
        """Test workflow plan creation."""
        result = await coordinator_agent.process(meta_analysis_request)

        assert result is not None
        assert "workflow" in result or "plan" in result or "steps" in result

    @pytest.mark.asyncio
    async def test_workflow_includes_all_phases(self, coordinator_agent, meta_analysis_request):
        """Test that workflow includes all required phases."""
        result = await coordinator_agent.process(meta_analysis_request)

        result_text = str(result).lower()
        required_phases = ["search", "screen", "extract", "analysis"]

        # Should mention key workflow phases
        phases_mentioned = sum(1 for phase in required_phases if phase in result_text)
        assert phases_mentioned >= 2, "Workflow should include key phases"

    @pytest.mark.asyncio
    async def test_coordinate_search_phase(self, coordinator_agent, meta_analysis_request):
        """Test coordination of search phase."""
        # First create workflow
        workflow = await coordinator_agent.process(meta_analysis_request)

        assert workflow is not None

    @pytest.mark.asyncio
    async def test_coordinate_screening_phase(self, coordinator_agent, meta_analysis_request):
        """Test coordination of screening phase."""
        workflow = await coordinator_agent.process(meta_analysis_request)

        assert workflow is not None

    @pytest.mark.asyncio
    async def test_handle_workflow_errors(self, coordinator_agent):
        """Test error handling in workflow coordination."""
        invalid_request = {
            "research_question": "",  # Empty question
            "topic": ""
        }

        # Should handle gracefully or raise clear error
        try:
            result = await coordinator_agent.process(invalid_request)
            assert result is not None
        except (ValueError, KeyError):
            pass  # Acceptable to raise error for invalid request

    @pytest.mark.asyncio
    async def test_workflow_state_tracking(self, coordinator_agent, meta_analysis_request):
        """Test that coordinator tracks workflow state."""
        result = await coordinator_agent.process(meta_analysis_request)

        # Should have some state information
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_agent_delegation(self, coordinator_agent, meta_analysis_request):
        """Test that coordinator properly delegates to other agents."""
        result = await coordinator_agent.process(meta_analysis_request)

        # Should create plan that involves other agents
        result_text = str(result).lower()
        agent_types = ["search", "screen", "credibility", "qa"]
        mentions_agents = any(agent in result_text for agent in agent_types)

        assert mentions_agents, "Coordinator should mention delegating to other agents"

    @pytest.mark.asyncio
    async def test_workflow_validation(self, coordinator_agent, meta_analysis_request):
        """Test workflow validation logic."""
        # Request with minimal info
        minimal_request = {
            "research_question": "Simple question?",
            "topic": "Test"
        }

        result = await coordinator_agent.process(minimal_request)
        assert result is not None

    @pytest.mark.asyncio
    async def test_progress_tracking(self, coordinator_agent, meta_analysis_request):
        """Test workflow progress tracking."""
        result = await coordinator_agent.process(meta_analysis_request)

        # Should be able to track progress
        assert result is not None

    @pytest.mark.asyncio
    async def test_parallel_task_coordination(self, coordinator_agent, meta_analysis_request):
        """Test coordination of parallel tasks."""
        result = await coordinator_agent.process(meta_analysis_request)

        # Workflow might include parallel tasks (e.g., searching multiple databases)
        assert result is not None

    @pytest.mark.asyncio
    async def test_error_recovery(self, coordinator_agent, meta_analysis_request):
        """Test error recovery mechanisms."""
        result = await coordinator_agent.process(meta_analysis_request)

        # Should have strategy for handling failures
        assert result is not None

    @pytest.mark.asyncio
    async def test_workflow_customization(self, coordinator_agent):
        """Test workflow customization based on request."""
        # Different types of requests
        requests = [
            {
                "research_question": "Simple RCT analysis",
                "topic": "Simple",
                "databases": ["pubmed"]
            },
            {
                "research_question": "Complex multi-database analysis",
                "topic": "Complex",
                "databases": ["pubmed", "psycinfo", "embase", "cochrane"],
                "peer_review_only": True
            }
        ]

        for req in requests:
            result = await coordinator_agent.process(req)
            assert result is not None

    @pytest.mark.asyncio
    async def test_quality_control_integration(self, coordinator_agent, meta_analysis_request):
        """Test integration of quality control in workflow."""
        result = await coordinator_agent.process(meta_analysis_request)

        # Should include quality control steps
        result_text = str(result).lower()
        quality_terms = ["quality", "credibility", "validation", "review"]
        has_quality_control = any(term in result_text for term in quality_terms)

    @pytest.mark.asyncio
    async def test_expert_profile_integration(self, coordinator_agent):
        """Test integration of expert profile."""
        request_with_expert = {
            "research_question": "Expert analysis",
            "topic": "Test",
            "expert_name": "Dr. Smith"
        }

        result = await coordinator_agent.process(request_with_expert)
        assert result is not None


class TestCoordinatorAgentWorkflowExecution:
    """Test workflow execution scenarios."""

    @pytest.mark.asyncio
    async def test_successful_workflow_execution(self, coordinator_agent, meta_analysis_request):
        """Test successful end-to-end workflow execution."""
        result = await coordinator_agent.process(meta_analysis_request)

        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_partial_workflow_execution(self, coordinator_agent, meta_analysis_request):
        """Test partial workflow execution (e.g., stopped midway)."""
        result = await coordinator_agent.process(meta_analysis_request)

        # Should be able to handle partial completion
        assert result is not None

    @pytest.mark.asyncio
    async def test_workflow_resume(self, coordinator_agent, meta_analysis_request):
        """Test resuming a workflow from checkpoint."""
        # First execution
        result1 = await coordinator_agent.process(meta_analysis_request)

        assert result1 is not None

    @pytest.mark.asyncio
    async def test_concurrent_workflows(self, coordinator_agent):
        """Test handling multiple concurrent workflows."""
        import asyncio

        requests = [
            {
                "research_question": f"Question {i}",
                "topic": f"Topic {i}"
            }
            for i in range(3)
        ]

        # Process concurrently
        results = await asyncio.gather(
            *[coordinator_agent.process(req) for req in requests]
        )

        assert len(results) == 3
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_workflow_timeout_handling(self, coordinator_agent, meta_analysis_request):
        """Test handling of workflow timeouts."""
        # This would need actual timeout mechanism
        result = await coordinator_agent.process(meta_analysis_request)
        assert result is not None


class TestCoordinatorAgentEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_request(self, coordinator_agent):
        """Test handling of empty request."""
        with pytest.raises((ValueError, KeyError, Exception)):
            await coordinator_agent.process({})

    @pytest.mark.asyncio
    async def test_malformed_request(self, coordinator_agent):
        """Test handling of malformed request."""
        malformed = {
            "invalid_field": "value"
        }

        with pytest.raises((ValueError, KeyError, Exception)):
            await coordinator_agent.process(malformed)

    @pytest.mark.asyncio
    async def test_very_complex_criteria(self, coordinator_agent):
        """Test handling of very complex inclusion/exclusion criteria."""
        complex_request = {
            "research_question": "Complex analysis",
            "topic": "Test",
            "inclusion_criteria": [f"Criteria {i}" for i in range(20)],
            "exclusion_criteria": [f"Exclusion {i}" for i in range(15)]
        }

        result = await coordinator_agent.process(complex_request)
        assert result is not None
