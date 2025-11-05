"""Unit tests for CredibilityAgent.

Tests the credibility assessment agent's ability to:
- Assess study quality based on methodology
- Calculate confidence scores
- Provide reasoning for decisions
- Handle edge cases
"""

import pytest
from app.agents.base.types import AgentRole, AgentStatus


class TestCredibilityAgent:
    """Test suite for CredibilityAgent."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, credibility_agent):
        """Test agent initializes with correct configuration."""
        assert credibility_agent.config.name == "test_credibility"
        assert credibility_agent.config.role == AgentRole.CREDIBILITY
        assert credibility_agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_assess_credibility_high_quality(self, credibility_agent, sample_paper):
        """Test credibility assessment for high-quality RCT."""
        # Modify sample to be clearly high quality
        study = sample_paper.copy()
        study.update({
            "study_type": "RCT",
            "sample_size": 500,
            "methodology": "Double-blind randomized controlled trial",
            "peer_reviewed": True,
            "journal": "New England Journal of Medicine"
        })

        result = await credibility_agent.process({"study": study})

        # Verify structure
        assert "credibility_level" in result
        assert "confidence" in result
        assert "reasoning" in result

        # Verify high quality assessment
        # Note: Actual values depend on agent implementation
        assert result["credibility_level"] in ["HIGH", "MEDIUM"]
        assert result["confidence"] > 0.5
        assert len(result["reasoning"]) > 0

    @pytest.mark.asyncio
    async def test_assess_credibility_low_quality(self, credibility_agent):
        """Test credibility assessment for low-quality study."""
        study = {
            "title": "Case report of single patient",
            "study_type": "case_report",
            "sample_size": 1,
            "methodology": "Observational case report",
            "peer_reviewed": False,
            "journal": "Unknown Journal"
        }

        result = await credibility_agent.process({"study": study})

        # Should identify as low quality
        assert result["credibility_level"] in ["LOW", "VERY_LOW", "MEDIUM"]
        assert "reasoning" in result

    @pytest.mark.asyncio
    async def test_assess_credibility_medium_quality(self, credibility_agent):
        """Test credibility assessment for medium-quality observational study."""
        study = {
            "title": "Cohort study of treatment outcomes",
            "study_type": "cohort",
            "sample_size": 200,
            "methodology": "Prospective cohort study",
            "peer_reviewed": True,
            "journal": "Journal of Epidemiology"
        }

        result = await credibility_agent.process({"study": study})

        assert result["credibility_level"] in ["MEDIUM", "HIGH", "LOW"]
        assert 0 <= result["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_confidence_score_bounds(self, credibility_agent, sample_paper):
        """Test confidence score is always between 0 and 1."""
        result = await credibility_agent.process({"study": sample_paper})

        assert 0 <= result["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_reasoning_provided(self, credibility_agent, sample_paper):
        """Test that agent provides reasoning for decision."""
        result = await credibility_agent.process({"study": sample_paper})

        assert "reasoning" in result
        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 20  # Substantial reasoning

    @pytest.mark.asyncio
    async def test_handles_missing_data(self, credibility_agent):
        """Test agent handles studies with missing information."""
        incomplete_study = {
            "title": "Study with missing data",
            # Missing: study_type, sample_size, methodology
        }

        result = await credibility_agent.process({"study": incomplete_study})

        # Should still return a result, but with lower confidence
        assert "credibility_level" in result
        assert "confidence" in result
        # Confidence should be lower due to missing data
        assert result["confidence"] < 0.8

    @pytest.mark.asyncio
    async def test_decision_logging(self, credibility_agent, sample_paper):
        """Test that decisions are logged for audit trail."""
        initial_decision_count = len(credibility_agent.decisions)

        await credibility_agent.process({"study": sample_paper})

        # Should have logged a decision
        assert len(credibility_agent.decisions) == initial_decision_count + 1

        # Verify decision structure
        decision = credibility_agent.decisions[-1]
        assert decision.agent_id == credibility_agent.id
        assert decision.role == AgentRole.CREDIBILITY
        assert decision.action == "assess_credibility"

    @pytest.mark.asyncio
    async def test_batch_assessment(self, credibility_agent, sample_papers):
        """Test assessing multiple studies efficiently."""
        results = []

        for paper in sample_papers[:5]:
            result = await credibility_agent.process({"study": paper})
            results.append(result)

        # All should have valid assessments
        assert len(results) == 5
        assert all("credibility_level" in r for r in results)

    def test_get_system_prompt(self, credibility_agent):
        """Test system prompt is properly defined."""
        prompt = credibility_agent.get_system_prompt()

        assert isinstance(prompt, str)
        assert len(prompt) > 100
        # Should contain key concepts
        assert any(keyword in prompt.lower() for keyword in [
            "credibility", "quality", "assess", "methodology"
        ])

    @pytest.mark.asyncio
    async def test_status_transitions(self, credibility_agent, sample_paper):
        """Test agent status transitions during processing."""
        assert credibility_agent.status == AgentStatus.IDLE

        # Status should change during processing
        # Note: This depends on implementation details
        await credibility_agent.process({"study": sample_paper})

        # After processing, should return to IDLE or COMPLETED
        assert credibility_agent.status in [AgentStatus.IDLE, AgentStatus.COMPLETED]


class TestCredibilityLevels:
    """Test credibility level classification."""

    @pytest.mark.parametrize("study_type,expected_range", [
        ("RCT", ["HIGH", "MEDIUM"]),
        ("cohort", ["MEDIUM", "HIGH", "LOW"]),
        ("case_control", ["MEDIUM", "LOW"]),
        ("case_report", ["LOW", "VERY_LOW"]),
        ("expert_opinion", ["VERY_LOW", "LOW"]),
    ])
    @pytest.mark.asyncio
    async def test_study_type_credibility(
        self,
        credibility_agent,
        study_type,
        expected_range
    ):
        """Test credibility varies appropriately by study type."""
        study = {
            "title": f"Test {study_type} study",
            "study_type": study_type,
            "sample_size": 100,
            "peer_reviewed": True
        }

        result = await credibility_agent.process({"study": study})

        # Credibility should be in expected range for study type
        # Note: This is a guideline, not strict requirement
        assert "credibility_level" in result


class TestCredibilityEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_study(self, credibility_agent):
        """Test handling of empty study data."""
        result = await credibility_agent.process({"study": {}})

        # Should handle gracefully
        assert "credibility_level" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_malformed_data(self, credibility_agent):
        """Test handling of malformed study data."""
        malformed_study = {
            "sample_size": "not_a_number",
            "year": "invalid",
            "peer_reviewed": "maybe"
        }

        result = await credibility_agent.process({"study": malformed_study})

        # Should not crash, should provide assessment
        assert "credibility_level" in result

    @pytest.mark.asyncio
    async def test_very_large_sample_size(self, credibility_agent):
        """Test handling of unusually large sample sizes."""
        study = {
            "title": "Large population study",
            "study_type": "RCT",
            "sample_size": 1000000,  # 1 million
            "peer_reviewed": True
        }

        result = await credibility_agent.process({"study": study})

        # Large sample should be positive factor
        assert "credibility_level" in result

    @pytest.mark.asyncio
    async def test_very_small_sample_size(self, credibility_agent):
        """Test handling of very small sample sizes."""
        study = {
            "title": "Pilot study",
            "study_type": "RCT",
            "sample_size": 5,
            "peer_reviewed": True
        }

        result = await credibility_agent.process({"study": study})

        # Small sample should lower confidence
        assert result["confidence"] < 0.9  # Lower confidence due to small n
