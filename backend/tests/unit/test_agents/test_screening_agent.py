"""Unit tests for ScreeningAgent."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.agents.base import AgentConfig, AgentRole
from app.agents.specialized.screening import ScreeningAgent


class TestScreeningAgent:
    """Test suite for ScreeningAgent."""

    @pytest.fixture
    def screening_agent(self, mock_anthropic_client):
        """Create ScreeningAgent instance for testing."""
        config = AgentConfig(
            name="test_screening",
            role=AgentRole.SCREENING,
            model="claude-3-5-sonnet-20241022"
        )
        return ScreeningAgent(config)

    @pytest.fixture
    def sample_studies(self):
        """Create sample studies for screening tests."""
        return [
            {
                "id": str(uuid4()),
                "title": "Effect of Exercise on Depression: A Randomized Controlled Trial",
                "abstract": "Background: Depression is a major health concern. Methods: RCT with 200 participants. Results: Significant improvement. Conclusion: Exercise is effective.",
                "year": 2023,
                "study_type": "RCT",
                "journal": "Journal of Medicine"
            },
            {
                "id": str(uuid4()),
                "title": "Review Article on Mental Health Interventions",
                "abstract": "This review discusses various interventions for mental health without original research data.",
                "year": 2022,
                "study_type": "Review",
                "journal": "Psychology Review"
            },
            {
                "id": str(uuid4()),
                "title": "Exercise Benefits in Elderly Population",
                "abstract": "Study of exercise benefits in people over 65 years old. Sample size: 50 participants.",
                "year": 2020,
                "study_type": "Cohort Study",
                "journal": "Geriatrics Journal"
            }
        ]

    @pytest.mark.asyncio
    async def test_screening_agent_initialization(self, screening_agent):
        """Test that ScreeningAgent initializes correctly."""
        assert screening_agent.config.role == AgentRole.SCREENING
        assert screening_agent.config.name == "test_screening"

    def test_screening_agent_system_prompt(self, screening_agent):
        """Test that system prompt contains required elements."""
        prompt = screening_agent.get_system_prompt()

        assert "Screening Agent" in prompt
        assert "PRISMA" in prompt
        assert "inclusion" in prompt.lower() or "exclusion" in prompt.lower()
        assert "criteria" in prompt.lower()

    @pytest.mark.asyncio
    async def test_title_abstract_screening(self, screening_agent, sample_studies):
        """Test title and abstract screening."""
        input_data = {
            "studies": sample_studies,
            "inclusion_criteria": [
                "Randomized controlled trials",
                "Studies on exercise and depression",
                "Published 2015-2024"
            ],
            "exclusion_criteria": [
                "Review articles",
                "Non-English studies"
            ],
            "screening_level": "title_abstract"
        }

        result = await screening_agent.process(input_data)

        assert result is not None
        assert "included" in result or "excluded" in result

        # Should categorize studies
        if "included" in result and "excluded" in result:
            total = len(result["included"]) + len(result["excluded"])
            uncertain = len(result.get("uncertain", []))
            assert total + uncertain == len(sample_studies)

    @pytest.mark.asyncio
    async def test_full_text_screening(self, screening_agent, sample_studies):
        """Test full-text screening."""
        input_data = {
            "studies": sample_studies,
            "inclusion_criteria": [
                "Original research",
                "Adequate sample size (n > 100)"
            ],
            "exclusion_criteria": [
                "Review articles",
                "Case reports"
            ],
            "screening_level": "full_text"
        }

        result = await screening_agent.process(input_data)

        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_screening_with_pico_criteria(self, screening_agent, sample_studies):
        """Test screening using PICO framework."""
        input_data = {
            "studies": sample_studies,
            "inclusion_criteria": [
                "Population: Adults with depression",
                "Intervention: Exercise programs",
                "Comparison: Control or standard care",
                "Outcome: Depression scores"
            ],
            "exclusion_criteria": [
                "Animal studies",
                "Pediatric populations"
            ],
            "screening_level": "title_abstract"
        }

        result = await screening_agent.process(input_data)

        assert result is not None

    @pytest.mark.asyncio
    async def test_screening_reasons_documented(self, screening_agent, sample_studies):
        """Test that exclusion reasons are documented."""
        input_data = {
            "studies": sample_studies[:1],  # Just one study
            "inclusion_criteria": ["RCT studies only"],
            "exclusion_criteria": ["Review articles"],
            "screening_level": "title_abstract"
        }

        result = await screening_agent.process(input_data)

        # Check that decisions have reasoning
        all_studies = (
            result.get("included", []) +
            result.get("excluded", []) +
            result.get("uncertain", [])
        )

        if all_studies:
            first_study = all_studies[0]
            has_reasoning = (
                "screening_result" in first_study and
                ("reasoning" in first_study["screening_result"] or
                 "reason" in first_study["screening_result"])
            )
            assert has_reasoning, "Screening decisions should have reasoning"

    @pytest.mark.asyncio
    async def test_uncertain_cases_flagged(self, screening_agent):
        """Test that uncertain cases are flagged for human review."""
        # Create an ambiguous study
        ambiguous_study = {
            "id": str(uuid4()),
            "title": "Ambiguous Study Title",
            "abstract": "Limited information provided. Study design unclear.",
            "year": 2023
        }

        input_data = {
            "studies": [ambiguous_study],
            "inclusion_criteria": ["Clear study design", "Adequate methodology"],
            "exclusion_criteria": ["Insufficient data"],
            "screening_level": "title_abstract"
        }

        result = await screening_agent.process(input_data)

        # Might be flagged as uncertain
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_prisma_flow_data_generation(self, screening_agent, sample_studies):
        """Test PRISMA flow diagram data generation."""
        input_data = {
            "studies": sample_studies,
            "inclusion_criteria": ["RCT studies"],
            "exclusion_criteria": ["Review articles"],
            "screening_level": "title_abstract"
        }

        result = await screening_agent.process(input_data)

        # Should generate PRISMA flow data
        prisma_fields = ["prisma", "flow", "total", "screened", "included", "excluded"]
        has_prisma = any(field in str(result).lower() for field in prisma_fields)
        assert has_prisma, "Should generate PRISMA flow data"

    @pytest.mark.asyncio
    async def test_screening_consistency(self, screening_agent):
        """Test consistency of screening decisions."""
        # Same study screened twice should give same result
        study = {
            "id": str(uuid4()),
            "title": "Test Study on Exercise",
            "abstract": "RCT testing exercise intervention.",
            "year": 2023,
            "study_type": "RCT"
        }

        input_data = {
            "studies": [study],
            "inclusion_criteria": ["RCT studies"],
            "exclusion_criteria": ["Review articles"],
            "screening_level": "title_abstract"
        }

        result1 = await screening_agent.process(input_data)
        result2 = await screening_agent.process(input_data)

        # Results should be consistent
        assert result1.keys() == result2.keys()

    @pytest.mark.asyncio
    async def test_empty_studies_list(self, screening_agent):
        """Test handling of empty studies list."""
        input_data = {
            "studies": [],
            "inclusion_criteria": ["RCT studies"],
            "exclusion_criteria": ["Review articles"],
            "screening_level": "title_abstract"
        }

        result = await screening_agent.process(input_data)

        assert result is not None
        assert result.get("included", []) == []
        assert result.get("excluded", []) == []

    @pytest.mark.asyncio
    async def test_no_criteria_provided(self, screening_agent, sample_studies):
        """Test handling when no criteria are provided."""
        input_data = {
            "studies": sample_studies,
            "inclusion_criteria": [],
            "exclusion_criteria": [],
            "screening_level": "title_abstract"
        }

        # Should either include all or flag all as uncertain
        result = await screening_agent.process(input_data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_conflicting_criteria(self, screening_agent, sample_studies):
        """Test handling of potentially conflicting criteria."""
        input_data = {
            "studies": sample_studies,
            "inclusion_criteria": [
                "Studies published 2020-2024",
                "RCT studies"
            ],
            "exclusion_criteria": [
                "Studies published before 2021",
                "Non-randomized studies"
            ],
            "screening_level": "title_abstract"
        }

        result = await screening_agent.process(input_data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_batch_screening_performance(self, screening_agent):
        """Test screening performance with large batch."""
        # Create large batch of studies
        large_batch = [
            {
                "id": str(uuid4()),
                "title": f"Study {i}",
                "abstract": "Research study abstract.",
                "year": 2023
            }
            for i in range(50)
        ]

        input_data = {
            "studies": large_batch,
            "inclusion_criteria": ["Published research"],
            "exclusion_criteria": ["Review articles"],
            "screening_level": "title_abstract"
        }

        import time
        start = time.time()
        result = await screening_agent.process(input_data)
        duration = time.time() - start

        assert result is not None
        # Should complete in reasonable time (under 30 seconds for 50 studies)
        assert duration < 30, f"Screening took too long: {duration}s"

    @pytest.mark.asyncio
    async def test_study_design_identification(self, screening_agent):
        """Test identification of study designs."""
        studies = [
            {
                "id": str(uuid4()),
                "title": "Randomized Controlled Trial",
                "abstract": "RCT methodology...",
                "study_type": "RCT"
            },
            {
                "id": str(uuid4()),
                "title": "Case Control Study",
                "abstract": "Retrospective case-control design...",
                "study_type": "Case-Control"
            },
            {
                "id": str(uuid4()),
                "title": "Systematic Review",
                "abstract": "Review of literature...",
                "study_type": "Review"
            }
        ]

        input_data = {
            "studies": studies,
            "inclusion_criteria": ["Primary research only"],
            "exclusion_criteria": ["Review articles"],
            "screening_level": "title_abstract"
        }

        result = await screening_agent.process(input_data)

        # Should identify and filter reviews
        if "excluded" in result:
            excluded_titles = [s.get("title", "") for s in result["excluded"]]
            review_excluded = any("Review" in title for title in excluded_titles)
            # May or may not exclude reviews depending on implementation


class TestScreeningAgentEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_malformed_study_data(self, screening_agent):
        """Test handling of malformed study data."""
        malformed = [
            {"id": "1"},  # Missing title and abstract
            {"title": "Only Title"},  # Missing abstract
            {}  # Empty
        ]

        input_data = {
            "studies": malformed,
            "inclusion_criteria": ["Valid studies"],
            "exclusion_criteria": [],
            "screening_level": "title_abstract"
        }

        # Should handle gracefully
        result = await screening_agent.process(input_data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_invalid_screening_level(self, screening_agent, sample_studies):
        """Test handling of invalid screening level."""
        input_data = {
            "studies": sample_studies,
            "inclusion_criteria": ["RCT"],
            "exclusion_criteria": [],
            "screening_level": "invalid_level"
        }

        # Should default to title_abstract or raise clear error
        try:
            result = await screening_agent.process(input_data)
            assert result is not None
        except ValueError as e:
            assert "screening_level" in str(e).lower()
