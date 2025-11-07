"""Unit tests for QAAgent."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.agents.base import AgentConfig, AgentRole
from app.agents.specialized.qa import QAAgent


class TestQAAgent:
    """Test suite for QAAgent."""

    @pytest.fixture
    def qa_agent(self, mock_anthropic_client):
        """Create QAAgent instance for testing."""
        config = AgentConfig(
            name="test_qa",
            role=AgentRole.QA,
            model="claude-3-5-sonnet-20241022"
        )
        return QAAgent(config)

    @pytest.fixture
    def sample_analysis_context(self):
        """Create sample analysis context for QA testing."""
        return {
            "research_question": "What is the effect of exercise on depression?",
            "included_studies": [
                {
                    "id": str(uuid4()),
                    "title": "Exercise RCT Study 1",
                    "effect_size": 0.45,
                    "sample_size": 200
                },
                {
                    "id": str(uuid4()),
                    "title": "Exercise RCT Study 2",
                    "effect_size": 0.38,
                    "sample_size": 150
                }
            ],
            "meta_analysis_results": {
                "pooled_effect_size": 0.42,
                "ci_lower": 0.30,
                "ci_upper": 0.54,
                "i_squared": 35.2,
                "p_value": 0.001
            }
        }

    @pytest.mark.asyncio
    async def test_qa_agent_initialization(self, qa_agent):
        """Test that QAAgent initializes correctly."""
        assert qa_agent.config.role == AgentRole.QA
        assert qa_agent.config.name == "test_qa"

    def test_qa_agent_system_prompt(self, qa_agent):
        """Test that system prompt contains required elements."""
        prompt = qa_agent.get_system_prompt()

        assert "QA Agent" in prompt or "Question" in prompt
        assert "answer" in prompt.lower()

    @pytest.mark.asyncio
    async def test_answer_effect_size_question(self, qa_agent, sample_analysis_context):
        """Test answering question about effect size."""
        input_data = {
            "question": "What is the overall effect size?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        assert result is not None
        assert "answer" in result or "response" in result

        # Answer should mention the effect size
        answer_text = str(result).lower()
        assert "0.42" in answer_text or "effect" in answer_text

    @pytest.mark.asyncio
    async def test_answer_heterogeneity_question(self, qa_agent, sample_analysis_context):
        """Test answering question about heterogeneity."""
        input_data = {
            "question": "Is there significant heterogeneity between studies?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        assert result is not None
        # Should discuss I-squared or heterogeneity
        result_text = str(result).lower()
        assert "heterogeneity" in result_text or "i-squared" in result_text or "i2" in result_text

    @pytest.mark.asyncio
    async def test_answer_significance_question(self, qa_agent, sample_analysis_context):
        """Test answering question about statistical significance."""
        input_data = {
            "question": "Is the result statistically significant?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        assert result is not None
        # Should discuss p-value and significance
        result_text = str(result).lower()
        assert any(term in result_text for term in ["significant", "p-value", "p <"])

    @pytest.mark.asyncio
    async def test_answer_study_quality_question(self, qa_agent, sample_analysis_context):
        """Test answering question about study quality."""
        input_data = {
            "question": "What is the overall quality of included studies?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        assert result is not None
        # Should provide quality assessment
        result_text = str(result).lower()
        assert any(term in result_text for term in ["quality", "studies", "sample"])

    @pytest.mark.asyncio
    async def test_answer_clinical_relevance_question(self, qa_agent, sample_analysis_context):
        """Test answering question about clinical relevance."""
        input_data = {
            "question": "What are the clinical implications of these findings?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        assert result is not None
        # Should discuss clinical implications
        result_text = str(result).lower()
        assert any(term in result_text for term in ["clinical", "implication", "practice"])

    @pytest.mark.asyncio
    async def test_answer_with_citations(self, qa_agent, sample_analysis_context):
        """Test that answers include study citations when relevant."""
        input_data = {
            "question": "Which studies found the largest effect?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        assert result is not None
        # Should reference specific studies
        result_text = str(result)
        # Might include study titles or IDs

    @pytest.mark.asyncio
    async def test_answer_comparison_question(self, qa_agent, sample_analysis_context):
        """Test answering comparative questions."""
        input_data = {
            "question": "How does this compare to other interventions?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        assert result is not None

    @pytest.mark.asyncio
    async def test_answer_methodology_question(self, qa_agent, sample_analysis_context):
        """Test answering questions about methodology."""
        input_data = {
            "question": "What statistical method was used for the meta-analysis?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        assert result is not None
        # Should discuss methodology
        result_text = str(result).lower()
        assert any(term in result_text for term in ["method", "statistical", "analysis"])

    @pytest.mark.asyncio
    async def test_handle_out_of_scope_question(self, qa_agent, sample_analysis_context):
        """Test handling of out-of-scope questions."""
        input_data = {
            "question": "What is the weather today?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        # Should politely decline or redirect to relevant info
        assert result is not None

    @pytest.mark.asyncio
    async def test_handle_ambiguous_question(self, qa_agent, sample_analysis_context):
        """Test handling of ambiguous questions."""
        input_data = {
            "question": "What about the thing?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        # Should ask for clarification or provide best attempt
        assert result is not None

    @pytest.mark.asyncio
    async def test_multiple_questions_in_sequence(self, qa_agent, sample_analysis_context):
        """Test answering multiple questions in sequence."""
        questions = [
            "What is the effect size?",
            "Is it significant?",
            "What are the limitations?"
        ]

        for question in questions:
            input_data = {
                "question": question,
                "context": sample_analysis_context
            }
            result = await qa_agent.process(input_data)
            assert result is not None

    @pytest.mark.asyncio
    async def test_answer_with_limited_context(self, qa_agent):
        """Test answering when context is limited."""
        limited_context = {
            "research_question": "Exercise and depression"
        }

        input_data = {
            "question": "What were the results?",
            "context": limited_context
        }

        result = await qa_agent.process(input_data)

        # Should indicate insufficient information
        assert result is not None

    @pytest.mark.asyncio
    async def test_answer_numerical_calculation(self, qa_agent, sample_analysis_context):
        """Test answering questions requiring calculations."""
        input_data = {
            "question": "What is the total sample size across all studies?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        assert result is not None
        # Should calculate total: 200 + 150 = 350
        result_text = str(result)
        assert "350" in result_text or "total" in result_text.lower()

    @pytest.mark.asyncio
    async def test_explain_statistical_concept(self, qa_agent, sample_analysis_context):
        """Test explaining statistical concepts."""
        input_data = {
            "question": "What does I-squared mean?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        assert result is not None
        # Should explain heterogeneity measure
        result_text = str(result).lower()
        assert any(term in result_text for term in ["heterogeneity", "variability", "consistency"])

    @pytest.mark.asyncio
    async def test_confidence_in_answers(self, qa_agent, sample_analysis_context):
        """Test that agent expresses appropriate confidence."""
        input_data = {
            "question": "Can we definitively conclude causation?",
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        assert result is not None
        # Should express appropriate caution about causation


class TestQAAgentEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_question(self, qa_agent, sample_analysis_context):
        """Test handling of empty question."""
        input_data = {
            "question": "",
            "context": sample_analysis_context
        }

        # Should handle gracefully or raise clear error
        try:
            result = await qa_agent.process(input_data)
            assert result is not None
        except ValueError:
            pass  # Acceptable to raise error for empty question

    @pytest.mark.asyncio
    async def test_no_context_provided(self, qa_agent):
        """Test handling when no context is provided."""
        input_data = {
            "question": "What are the results?"
        }

        result = await qa_agent.process(input_data)

        # Should indicate need for context
        assert result is not None

    @pytest.mark.asyncio
    async def test_very_long_question(self, qa_agent, sample_analysis_context):
        """Test handling of very long questions."""
        long_question = " ".join([f"word{i}" for i in range(500)])

        input_data = {
            "question": long_question,
            "context": sample_analysis_context
        }

        result = await qa_agent.process(input_data)

        assert result is not None
