"""Tests for ScreeningAgentV2."""
import pytest
from unittest.mock import AsyncMock, MagicMock

import numpy as np

from app.agents.base import AgentConfig, AgentRole
from app.agents.specialized.screening_agent_v2 import (
    ScreeningAgentV2,
    ScreeningClassifier,
)


@pytest.fixture
def agent_config():
    """Create agent configuration for testing."""
    return AgentConfig(
        name="TestScreeningAgent",
        role=AgentRole.SCREENING,
        model="claude-sonnet-4-5-20250929",
    )


@pytest.fixture
def screening_agent(agent_config):
    """Create ScreeningAgentV2 instance."""
    agent = ScreeningAgentV2(agent_config)
    # Mock the Claude API client
    agent.client = MagicMock()
    agent.client.messages.create = AsyncMock(
        return_value=MagicMock(
            content=[
                MagicMock(
                    text="""
Decision: INCLUDE
Reasoning: This study meets all inclusion criteria. It is an RCT examining the target population with the specified intervention and measuring relevant outcomes.
Criteria Met: RCT design | Adult population | Intervention present | Primary outcome measured
Criteria Not Met: None
Exclusion Criteria Applied: None
Exclusion Reason Category: None
Confidence: 0.85
Next Step: Proceed to full-text review
Flags: None
"""
                )
            ]
        )
    )
    return agent


@pytest.fixture
def sample_studies():
    """Create sample studies for testing."""
    return [
        {
            "id": "PMID:1",
            "title": "Effect of intervention on diabetes outcomes in adults",
            "abstract": "This randomized controlled trial examined the effect of a dietary intervention on glycemic control in adults with type 2 diabetes. Results showed significant improvement in HbA1c levels.",
            "authors": ["Smith J", "Doe J"],
            "journal": "Diabetes Care",
            "year": "2023",
        },
        {
            "id": "PMID:2",
            "title": "Case report of unusual diabetes presentation",
            "abstract": "We report a case of an unusual presentation of diabetes in a single patient.",
            "authors": ["Johnson A"],
            "journal": "Case Reports",
            "year": "2022",
        },
        {
            "id": "PMID:3",
            "title": "Editorial on diabetes management",
            "abstract": "This editorial discusses current trends in diabetes management.",
            "authors": ["Expert X"],
            "journal": "Medical Opinion",
            "year": "2023",
        },
    ]


@pytest.fixture
def inclusion_criteria():
    """Sample inclusion criteria."""
    return [
        "Randomized controlled trials (RCTs)",
        "Adults aged 18+ with type 2 diabetes",
        "Dietary or lifestyle intervention",
        "Glycemic control outcomes (HbA1c)",
    ]


@pytest.fixture
def exclusion_criteria():
    """Sample exclusion criteria."""
    return [
        "Case reports or case series",
        "Pediatric populations",
        "Editorial or opinion pieces",
        "Animal studies",
    ]


class TestScreeningClassifier:
    """Tests for ScreeningClassifier class."""

    def test_initialization(self):
        """Test classifier initialization."""
        classifier = ScreeningClassifier()
        assert classifier.vectorizer is not None
        assert not classifier.is_fitted

    def test_fit_criteria(self):
        """Test fitting classifier on criteria."""
        classifier = ScreeningClassifier()
        inclusion = ["RCT studies", "Adult population"]
        exclusion = ["Animal studies", "Case reports"]

        classifier.fit_criteria(inclusion, exclusion)
        assert classifier.is_fitted

    def test_compute_relevance_score_basic(self):
        """Test basic relevance score computation."""
        classifier = ScreeningClassifier()
        inclusion = ["randomized controlled trial", "diabetes", "adults"]
        exclusion = ["animal study", "pediatric", "case report"]

        classifier.fit_criteria(inclusion, exclusion)

        study_text = "This randomized controlled trial studied diabetes in adults"
        inclusion_score, exclusion_score, details = classifier.compute_relevance_score(
            study_text, inclusion, exclusion
        )

        # Should have high inclusion score, low exclusion score
        assert inclusion_score > 0.1
        assert exclusion_score >= 0
        assert inclusion_score > exclusion_score

    def test_compute_relevance_score_exclusion(self):
        """Test relevance score for study that should be excluded."""
        classifier = ScreeningClassifier()
        inclusion = ["human study", "adult", "RCT"]
        exclusion = ["animal study", "rat", "mouse"]

        classifier.fit_criteria(inclusion, exclusion)

        study_text = "This study examined the effect of treatment in rats and mice"
        inclusion_score, exclusion_score, details = classifier.compute_relevance_score(
            study_text, inclusion, exclusion
        )

        # Should have high exclusion score
        assert exclusion_score > 0.1

    def test_relevance_score_empty_text(self):
        """Test relevance score with empty text."""
        classifier = ScreeningClassifier()
        classifier.fit_criteria(["test"], ["test"])

        inclusion_score, exclusion_score, details = classifier.compute_relevance_score(
            "", ["test"], ["test"]
        )

        assert inclusion_score == 0.0
        assert exclusion_score == 0.0


class TestScreeningAgentV2:
    """Tests for ScreeningAgentV2 class."""

    @pytest.mark.asyncio
    async def test_initialization(self, screening_agent):
        """Test agent initialization."""
        assert screening_agent.config.role == AgentRole.SCREENING
        assert screening_agent.classifier is not None

    @pytest.mark.asyncio
    async def test_process_basic_screening(
        self, screening_agent, sample_studies, inclusion_criteria, exclusion_criteria
    ):
        """Test basic screening process."""
        input_data = {
            "studies": sample_studies[:1],  # Use one study
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "screening_level": "abstract",
            "use_ml_scoring": True,
        }

        # Mock decision making
        screening_agent.make_decision = AsyncMock(
            return_value=MagicMock(
                model_dump=lambda: {
                    "decision": "Screening was thorough",
                    "confidence": 0.9,
                }
            )
        )

        result = await screening_agent.process(input_data)

        assert "included" in result
        assert "excluded" in result
        assert "uncertain" in result
        assert "prisma_data" in result
        assert "screening_stats" in result
        assert result["total_screened"] == 1

    @pytest.mark.asyncio
    async def test_title_level_screening(
        self, screening_agent, sample_studies, inclusion_criteria, exclusion_criteria
    ):
        """Test title-level screening."""
        input_data = {
            "studies": sample_studies[:1],
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "screening_level": "title",
        }

        screening_agent.make_decision = AsyncMock(
            return_value=MagicMock(model_dump=lambda: {"decision": "OK"})
        )

        result = await screening_agent.process(input_data)

        assert result["screening_level"] == "title"
        # Title screening should process studies
        assert len(result["included"]) + len(result["excluded"]) + len(result["uncertain"]) == 1

    @pytest.mark.asyncio
    async def test_abstract_level_screening(
        self, screening_agent, sample_studies, inclusion_criteria, exclusion_criteria
    ):
        """Test abstract-level screening."""
        input_data = {
            "studies": sample_studies[:1],
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "screening_level": "abstract",
        }

        screening_agent.make_decision = AsyncMock(
            return_value=MagicMock(model_dump=lambda: {"decision": "OK"})
        )

        result = await screening_agent.process(input_data)

        assert result["screening_level"] == "abstract"

    @pytest.mark.asyncio
    async def test_ml_scoring_enabled(
        self, screening_agent, sample_studies, inclusion_criteria, exclusion_criteria
    ):
        """Test screening with ML scoring enabled."""
        input_data = {
            "studies": sample_studies[:1],
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "screening_level": "abstract",
            "use_ml_scoring": True,
        }

        screening_agent.make_decision = AsyncMock(
            return_value=MagicMock(model_dump=lambda: {"decision": "OK"})
        )

        result = await screening_agent.process(input_data)

        assert result["ml_scoring_used"] is True

        # Check that at least one study has ML scores
        all_studies = result["included"] + result["excluded"] + result["uncertain"]
        if all_studies:
            first_study = all_studies[0]
            assert "screening_result" in first_study
            assert "ml_scores" in first_study["screening_result"]

    @pytest.mark.asyncio
    async def test_ml_scoring_disabled(
        self, screening_agent, sample_studies, inclusion_criteria, exclusion_criteria
    ):
        """Test screening with ML scoring disabled."""
        input_data = {
            "studies": sample_studies[:1],
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "screening_level": "abstract",
            "use_ml_scoring": False,
        }

        screening_agent.make_decision = AsyncMock(
            return_value=MagicMock(model_dump=lambda: {"decision": "OK"})
        )

        result = await screening_agent.process(input_data)

        assert result["ml_scoring_used"] is False

    @pytest.mark.asyncio
    async def test_batch_processing(
        self, screening_agent, sample_studies, inclusion_criteria, exclusion_criteria
    ):
        """Test batch processing of studies."""
        input_data = {
            "studies": sample_studies,  # All 3 studies
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "screening_level": "abstract",
            "batch_size": 2,  # Process in batches of 2
        }

        screening_agent.make_decision = AsyncMock(
            return_value=MagicMock(model_dump=lambda: {"decision": "OK"})
        )

        result = await screening_agent.process(input_data)

        assert result["total_screened"] == 3
        # All studies should be processed
        assert (
            len(result["included"]) + len(result["excluded"]) + len(result["uncertain"])
            == 3
        )

    @pytest.mark.asyncio
    async def test_confidence_threshold(
        self, screening_agent, sample_studies, inclusion_criteria, exclusion_criteria
    ):
        """Test confidence threshold for uncertain classification."""
        # Mock low confidence response
        screening_agent.client.messages.create = AsyncMock(
            return_value=MagicMock(
                content=[
                    MagicMock(
                        text="""
Decision: INCLUDE
Reasoning: Borderline case
Criteria Met: Some criteria met
Criteria Not Met: Some unclear
Exclusion Criteria Applied: None
Exclusion Reason Category: None
Confidence: 0.5
Next Step: Human review needed
Flags: Unclear eligibility
"""
                    )
                ]
            )
        )

        input_data = {
            "studies": sample_studies[:1],
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "screening_level": "abstract",
            "confidence_threshold": 0.7,  # High threshold
        }

        screening_agent.make_decision = AsyncMock(
            return_value=MagicMock(model_dump=lambda: {"decision": "OK"})
        )

        result = await screening_agent.process(input_data)

        # Low confidence should result in uncertain classification
        assert len(result["uncertain"]) > 0

    def test_categorize_exclusion_reasons(self, screening_agent):
        """Test exclusion reason categorization."""
        excluded_studies = [
            {
                "screening_result": {
                    "exclusion_reason_category": "Wrong population"
                }
            },
            {
                "screening_result": {
                    "exclusion_reason_category": "Wrong study design"
                }
            },
            {
                "screening_result": {
                    "exclusion_reason_category": "Wrong population"
                }
            },
        ]

        reasons = screening_agent._categorize_exclusion_reasons(excluded_studies)

        assert reasons["Wrong population"] == 2
        assert reasons["Wrong study design"] == 1

    def test_generate_prisma_data(self, screening_agent):
        """Test PRISMA flow data generation."""
        prisma_data = screening_agent._generate_prisma_data(
            screening_level="abstract",
            total=100,
            included=30,
            excluded=60,
            uncertain=10,
            exclusion_reasons={
                "Wrong population": 20,
                "Wrong intervention": 15,
                "Wrong outcomes": 25,
            },
        )

        assert prisma_data["screening_stage"] == "abstract"
        assert prisma_data["records_screened"] == 100
        assert prisma_data["records_included"] == 30
        assert prisma_data["records_excluded"] == 60
        assert prisma_data["records_uncertain"] == 10
        assert "exclusion_reasons" in prisma_data

    def test_calculate_screening_stats(self, screening_agent):
        """Test screening statistics calculation."""
        included = [
            {"screening_result": {"confidence": 0.9, "ml_scores": {}}}
        ]
        excluded = [
            {"screening_result": {"confidence": 0.85, "ml_scores": {}}}
        ]
        uncertain = [
            {"screening_result": {"confidence": 0.6, "ml_scores": {}}}
        ]

        stats = screening_agent._calculate_screening_stats(included, excluded, uncertain)

        assert "mean_confidence" in stats
        assert "std_confidence" in stats
        assert "high_confidence_count" in stats
        assert "low_confidence_count" in stats
        assert stats["total_screened"] == 3

    @pytest.mark.asyncio
    async def test_inter_rater_agreement(self, screening_agent):
        """Test Cohen's kappa calculation for inter-rater agreement."""
        # Create two sets of screening results
        results_1 = [
            {"screening_result": {"decision": "include"}},
            {"screening_result": {"decision": "include"}},
            {"screening_result": {"decision": "exclude"}},
            {"screening_result": {"decision": "exclude"}},
        ]

        results_2 = [
            {"screening_result": {"decision": "include"}},
            {"screening_result": {"decision": "exclude"}},  # Disagreement
            {"screening_result": {"decision": "exclude"}},
            {"screening_result": {"decision": "exclude"}},
        ]

        agreement = await screening_agent.calculate_inter_rater_agreement(
            results_1, results_2
        )

        assert "cohens_kappa" in agreement
        assert "percent_agreement" in agreement
        assert "disagreements" in agreement
        assert "interpretation" in agreement
        assert agreement["total_compared"] == 4
        assert agreement["disagreements"] == 1

    def test_interpret_kappa(self, screening_agent):
        """Test kappa interpretation."""
        assert "Poor" in screening_agent._interpret_kappa(-0.1)
        assert "Slight" in screening_agent._interpret_kappa(0.1)
        assert "Fair" in screening_agent._interpret_kappa(0.3)
        assert "Moderate" in screening_agent._interpret_kappa(0.5)
        assert "Substantial" in screening_agent._interpret_kappa(0.7)
        assert "Almost perfect" in screening_agent._interpret_kappa(0.9)

    def test_format_criteria_list(self, screening_agent, inclusion_criteria):
        """Test criteria list formatting."""
        formatted = screening_agent._format_criteria_list(inclusion_criteria)

        assert "1." in formatted
        assert inclusion_criteria[0] in formatted

    def test_format_ml_scores(self, screening_agent):
        """Test ML scores formatting."""
        ml_scores = {
            "inclusion_score": 0.75,
            "exclusion_score": 0.25,
            "net_score": 0.50,
        }

        formatted = screening_agent._format_ml_scores(ml_scores)

        assert "0.750" in formatted
        assert "0.250" in formatted
        assert "0.500" in formatted

    def test_parse_screening_response(self, screening_agent):
        """Test parsing of AI screening response."""
        response = """
Decision: EXCLUDE
Reasoning: This study does not meet inclusion criteria for study design.
Criteria Met: Adult population
Criteria Not Met: RCT design | Primary outcome measured
Exclusion Criteria Applied: Case report exclusion
Exclusion Reason Category: Wrong study design
Confidence: 0.92
Next Step: Exclude from meta-analysis
Flags: None
"""

        parsed = screening_agent._parse_screening_response(response)

        assert parsed["decision"] == "exclude"
        assert "study design" in parsed["reasoning"].lower()
        assert "Adult population" in parsed["criteria_met"]
        assert len(parsed["criteria_not_met"]) == 2
        assert parsed["exclusion_reason_category"] == "Wrong study design"
        assert parsed["confidence"] == 0.92
