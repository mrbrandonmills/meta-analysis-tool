"""Unit tests for SearchAgent."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.agents.base import AgentConfig, AgentRole
from app.agents.specialized.search import SearchAgent


class TestSearchAgent:
    """Test suite for SearchAgent."""

    @pytest.fixture
    def search_agent(self, mock_anthropic_client):
        """Create SearchAgent instance for testing."""
        config = AgentConfig(
            name="test_search",
            role=AgentRole.SEARCH,
            model="claude-3-5-sonnet-20241022"
        )
        return SearchAgent(config)

    @pytest.mark.asyncio
    async def test_search_agent_initialization(self, search_agent):
        """Test that SearchAgent initializes correctly."""
        assert search_agent.config.role == AgentRole.SEARCH
        assert search_agent.config.name == "test_search"
        assert "claude" in search_agent.config.model.lower()

    def test_search_agent_system_prompt(self, search_agent):
        """Test that system prompt contains required elements."""
        prompt = search_agent.get_system_prompt()

        assert "Search Agent" in prompt
        assert "PubMed" in prompt or "MEDLINE" in prompt
        assert "PRISMA" in prompt
        assert "Boolean" in prompt or "search" in prompt.lower()

    @pytest.mark.asyncio
    async def test_search_with_research_question(self, search_agent):
        """Test searching with a research question."""
        input_data = {
            "research_question": "What is the effect of exercise on depression?",
            "search_terms": ["exercise", "depression"],
            "databases": ["pubmed"]
        }

        result = await search_agent.process(input_data)

        assert result is not None
        assert "studies" in result or "search_strategy" in result or "results" in result

    @pytest.mark.asyncio
    async def test_search_with_multiple_databases(self, search_agent):
        """Test searching across multiple databases."""
        input_data = {
            "research_question": "Effect of meditation on anxiety",
            "search_terms": ["meditation", "anxiety"],
            "databases": ["pubmed", "arxiv", "core"]
        }

        result = await search_agent.process(input_data)

        assert result is not None
        # Should have results from multiple databases
        if "studies" in result:
            assert isinstance(result["studies"], list)

    @pytest.mark.asyncio
    async def test_search_with_date_range_filter(self, search_agent):
        """Test searching with date range filters."""
        input_data = {
            "research_question": "Recent studies on COVID-19 treatment",
            "search_terms": ["COVID-19", "treatment"],
            "databases": ["pubmed"],
            "date_range": {
                "start": "2020-01-01",
                "end": "2024-12-31"
            }
        }

        result = await search_agent.process(input_data)

        assert result is not None

    @pytest.mark.asyncio
    async def test_search_with_filters(self, search_agent):
        """Test searching with additional filters."""
        input_data = {
            "research_question": "RCTs on hypertension treatment",
            "search_terms": ["hypertension", "treatment"],
            "databases": ["pubmed"],
            "filters": {
                "study_type": "RCT",
                "language": "eng",
                "has_abstract": True
            }
        }

        result = await search_agent.process(input_data)

        assert result is not None

    @pytest.mark.asyncio
    async def test_search_empty_results(self, search_agent):
        """Test handling of searches with no results."""
        input_data = {
            "research_question": "Very specific niche topic with no results xyz123",
            "search_terms": ["nonexistent_term_xyz123"],
            "databases": ["pubmed"]
        }

        result = await search_agent.process(input_data)

        # Should still return a valid structure even with no results
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_search_error_handling(self, search_agent):
        """Test error handling in search process."""
        # Invalid input data
        with pytest.raises((ValueError, KeyError, Exception)):
            await search_agent.process({})

    @pytest.mark.asyncio
    async def test_search_deduplication(self, search_agent):
        """Test that duplicate studies are removed."""
        input_data = {
            "research_question": "Duplicate study detection",
            "search_terms": ["test"],
            "databases": ["pubmed", "europepmc"]  # Might have overlapping results
        }

        result = await search_agent.process(input_data)

        # If we have studies, they should be deduplicated
        if "studies" in result and result["studies"]:
            study_ids = [s.get("id") or s.get("pmid") or s.get("doi")
                        for s in result["studies"]]
            # Remove None values
            study_ids = [sid for sid in study_ids if sid]
            # Check for duplicates
            if study_ids:
                assert len(study_ids) == len(set(study_ids)), "Found duplicate studies"

    @pytest.mark.asyncio
    async def test_search_metadata_extraction(self, search_agent):
        """Test that study metadata is properly extracted."""
        input_data = {
            "research_question": "Meta-analysis studies",
            "search_terms": ["meta-analysis"],
            "databases": ["pubmed"]
        }

        result = await search_agent.process(input_data)

        # Check that studies have proper metadata
        if "studies" in result and result["studies"]:
            first_study = result["studies"][0]
            # Should have at least some metadata fields
            expected_fields = ["title", "abstract", "authors", "year"]
            has_metadata = any(field in first_study for field in expected_fields)
            assert has_metadata, "Studies missing metadata"

    @pytest.mark.asyncio
    async def test_search_strategy_documentation(self, search_agent):
        """Test that search strategy is documented."""
        input_data = {
            "research_question": "Clinical trials on diabetes",
            "search_terms": ["diabetes", "clinical trial"],
            "databases": ["pubmed"]
        }

        result = await search_agent.process(input_data)

        # Should document search strategy
        strategy_fields = ["search_strategy", "strategy", "methodology", "search_terms"]
        has_strategy = any(field in result for field in strategy_fields)
        assert has_strategy, "Search strategy not documented"

    @pytest.mark.asyncio
    async def test_search_prisma_compliance(self, search_agent):
        """Test that search follows PRISMA guidelines."""
        input_data = {
            "research_question": "Systematic review on interventions",
            "search_terms": ["intervention", "systematic review"],
            "databases": ["pubmed"]
        }

        result = await search_agent.process(input_data)

        # PRISMA requires documentation of:
        # - Databases searched
        # - Date of search
        # - Number of results
        prisma_elements = ["databases", "date", "count", "total", "n_results"]
        has_prisma_elements = any(elem in str(result).lower() for elem in prisma_elements)
        assert has_prisma_elements, "PRISMA elements not documented"

    @pytest.mark.asyncio
    async def test_concurrent_searches(self, search_agent):
        """Test handling multiple concurrent searches."""
        import asyncio

        searches = [
            {
                "research_question": f"Research question {i}",
                "search_terms": [f"term{i}"],
                "databases": ["pubmed"]
            }
            for i in range(3)
        ]

        # Run searches concurrently
        results = await asyncio.gather(
            *[search_agent.process(search) for search in searches]
        )

        assert len(results) == 3
        assert all(result is not None for result in results)

    def test_search_agent_config_validation(self):
        """Test that invalid configurations are rejected."""
        # Missing required fields should raise error
        with pytest.raises((ValueError, Exception)):
            config = AgentConfig(name="", role=AgentRole.SEARCH)
            SearchAgent(config)


class TestSearchAgentIntegration:
    """Integration tests for SearchAgent with external APIs."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_pubmed_search_integration(self, search_agent):
        """Test actual PubMed API integration."""
        pytest.skip("Requires PubMed API access - run in integration tests")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_arxiv_search_integration(self, search_agent):
        """Test actual arXiv API integration."""
        pytest.skip("Requires arXiv API access - run in integration tests")
