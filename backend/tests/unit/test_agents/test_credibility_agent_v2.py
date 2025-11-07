"""Tests for CredibilityAgentV2."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.base import AgentConfig, AgentRole
from app.agents.specialized.credibility_agent_v2 import (
    CredibilityAgentV2,
    CredibilityLevel,
    StudyDesignType,
    RiskOfBias,
    GRADELevel,
)


@pytest.fixture
def agent_config():
    """Create agent configuration for testing."""
    return AgentConfig(
        name="TestCredibilityAgent",
        role=AgentRole.QUALITY_ASSESSMENT,
        model="claude-sonnet-4-5-20250929",
    )


@pytest.fixture
def credibility_agent(agent_config):
    """Create CredibilityAgentV2 instance."""
    agent = CredibilityAgentV2(agent_config)
    # Mock the Claude API client
    agent.client = MagicMock()
    agent.client.messages.create = AsyncMock(
        return_value=MagicMock(
            content=[
                MagicMock(
                    text="""
Study Design: Randomized Controlled Trial (RCT)
Evidence Level: 2 - High quality RCT
Risk of Bias Overall: Low
Risk of Bias Details: Randomization: Low | Deviations: Low | Missing data: Low | Measurement: Low | Selection: Low
GRADE Quality: HIGH
GRADE Justification: Well-designed RCT with low risk of bias, no serious concerns for inconsistency, indirectness, or imprecision
Sample Size: Adequate
Power Analysis: Present, adequate (>80% power)
Methodological Strengths:
- Randomized allocation with concealment
- Double-blind design
- Intent-to-treat analysis
- Complete outcome data
Methodological Limitations:
- Single-center study
- Limited generalizability
Replicability: High
Overall Credibility: HIGH
Quality Score: 85
Inclusion Recommendation: Recommend include
Reasoning: This is a well-conducted RCT with low risk of bias and high methodological quality. Suitable for inclusion in meta-analysis.
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
            "id": "PMID:12345",
            "pmid": "12345",
            "title": "Effect of intervention on diabetes: A randomized controlled trial",
            "abstract": "This double-blind randomized controlled trial examined the effect of dietary intervention on glycemic control in 200 adults with type 2 diabetes. Participants were randomly allocated to intervention or control. Primary outcome was HbA1c at 6 months. Results showed significant improvement in the intervention group (p<0.001).",
            "authors": ["Smith J", "Doe J", "Johnson A"],
            "journal": "New England Journal of Medicine",
            "year": "2023",
            "doi": "10.1056/nejm.2023.12345",
            "database": "PubMed",
            "keywords": ["diabetes", "RCT", "dietary intervention"],
            "mesh_terms": ["Diabetes Mellitus, Type 2", "Randomized Controlled Trial"],
            "publication_types": ["Randomized Controlled Trial", "Journal Article"],
        },
        {
            "id": "arXiv:2301.12345",
            "arxiv_id": "2301.12345",
            "title": "Machine learning for diabetes prediction: A preprint",
            "abstract": "We developed a machine learning model to predict diabetes risk. Preliminary results on 100 patients show promise.",
            "authors": ["Preprint Author"],
            "journal": "arXiv Preprint",
            "year": "2023",
            "doi": "",
            "database": "arXiv",
            "is_preprint": True,
        },
    ]


class TestCredibilityLevel:
    """Tests for CredibilityLevel enum."""

    def test_credibility_levels(self):
        """Test all credibility levels."""
        assert CredibilityLevel.HIGH == "high"
        assert CredibilityLevel.MEDIUM == "medium"
        assert CredibilityLevel.LOW == "low"
        assert CredibilityLevel.VERY_LOW == "very_low"


class TestCredibilityAgentV2:
    """Tests for CredibilityAgentV2 class."""

    @pytest.mark.asyncio
    async def test_initialization(self, credibility_agent):
        """Test agent initialization."""
        assert credibility_agent.config.role == AgentRole.QUALITY_ASSESSMENT
        assert credibility_agent._retraction_cache == {}

    @pytest.mark.asyncio
    async def test_process_basic_evaluation(
        self, credibility_agent, sample_studies
    ):
        """Test basic credibility evaluation."""
        input_data = {
            "studies": sample_studies[:1],  # Evaluate one study
            "require_peer_review": False,
            "check_retractions": False,  # Disable for simpler test
            "fetch_citations": False,
        }

        # Mock decision making
        credibility_agent.make_decision = AsyncMock(
            return_value=MagicMock(
                model_dump=lambda: {
                    "decision": "Quality is sufficient",
                    "confidence": 0.9,
                }
            )
        )

        result = await credibility_agent.process(input_data)

        assert "studies" in result
        assert "credibility_breakdown" in result
        assert "design_breakdown" in result
        assert "grade_breakdown" in result
        assert result["total_evaluated"] >= 1

        # Check that credibility data is attached to studies
        if result["studies"]:
            first_study = result["studies"][0]
            assert "credibility" in first_study
            assert "level" in first_study["credibility"]
            assert "quality_score" in first_study["credibility"]

    @pytest.mark.asyncio
    async def test_filter_by_peer_review(
        self, credibility_agent, sample_studies
    ):
        """Test filtering by peer review requirement."""
        # Mock evaluation to return preprint status correctly
        async def mock_evaluate(study, **kwargs):
            is_preprint = "arxiv" in study.get("database", "").lower()
            return {
                "level": CredibilityLevel.MEDIUM,
                "quality_score": 60,
                "is_peer_reviewed": not is_preprint,
                "is_preprint": is_preprint,
                "is_retracted": False,
                "study_design": "Unknown",
                "grade_quality": "MODERATE",
            }

        credibility_agent._evaluate_credibility_comprehensive = mock_evaluate
        credibility_agent.make_decision = AsyncMock(
            return_value=MagicMock(model_dump=lambda: {"decision": "OK"})
        )

        input_data = {
            "studies": sample_studies,  # Includes preprint
            "require_peer_review": True,
        }

        result = await credibility_agent.process(input_data)

        # Should filter out preprints
        for study in result["studies"]:
            assert study["credibility"]["is_peer_reviewed"]
            assert not study["credibility"]["is_preprint"]

    @pytest.mark.asyncio
    async def test_filter_by_minimum_credibility(
        self, credibility_agent, sample_studies
    ):
        """Test filtering by minimum credibility threshold."""
        # Mock evaluation to return different credibility levels
        call_count = [0]

        async def mock_evaluate(study, **kwargs):
            call_count[0] += 1
            level = CredibilityLevel.HIGH if call_count[0] == 1 else CredibilityLevel.LOW
            return {
                "level": level,
                "quality_score": 80 if level == CredibilityLevel.HIGH else 30,
                "is_peer_reviewed": True,
                "is_preprint": False,
                "is_retracted": False,
                "study_design": "RCT",
                "grade_quality": "HIGH",
            }

        credibility_agent._evaluate_credibility_comprehensive = mock_evaluate
        credibility_agent.make_decision = AsyncMock(
            return_value=MagicMock(model_dump=lambda: {"decision": "OK"})
        )

        input_data = {
            "studies": sample_studies,
            "minimum_credibility": "medium",
        }

        result = await credibility_agent.process(input_data)

        # Should filter out LOW and VERY_LOW credibility studies
        for study in result["studies"]:
            level = study["credibility"]["level"]
            assert level in [CredibilityLevel.HIGH, CredibilityLevel.MEDIUM]

    def test_is_preprint_detection(self, credibility_agent):
        """Test preprint detection logic."""
        # arXiv database
        assert credibility_agent._is_preprint("arXiv", "Some Journal", "")

        # bioRxiv in journal name
        assert credibility_agent._is_preprint("PubMed", "bioRxiv preprint", "")

        # Preprint in DOI
        assert credibility_agent._is_preprint("", "", "10.1101/2023.01.01")

        # Peer-reviewed journal
        assert not credibility_agent._is_preprint("PubMed", "Nature", "10.1038/s41586")

    @pytest.mark.asyncio
    async def test_check_retraction_status_cached(self, credibility_agent):
        """Test retraction checking with cache."""
        # Add to cache
        credibility_agent._retraction_cache["10.1234/test"] = True

        is_retracted, info = await credibility_agent._check_retraction_status(
            "10.1234/test", ""
        )

        assert is_retracted is True

    @pytest.mark.asyncio
    async def test_fetch_citation_count(self, credibility_agent):
        """Test citation count fetching."""
        # Mock httpx client
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"count": 42}]

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            citation_count = await credibility_agent._fetch_citation_count(
                "10.1234/test"
            )

            # Should return count from mock
            assert citation_count is not None

    def test_meets_minimum_credibility(self, credibility_agent):
        """Test minimum credibility threshold checking."""
        # HIGH meets all thresholds
        assert credibility_agent._meets_minimum_credibility(
            CredibilityLevel.HIGH, "high"
        )
        assert credibility_agent._meets_minimum_credibility(
            CredibilityLevel.HIGH, "medium"
        )
        assert credibility_agent._meets_minimum_credibility(
            CredibilityLevel.HIGH, "low"
        )

        # MEDIUM meets medium and low
        assert not credibility_agent._meets_minimum_credibility(
            CredibilityLevel.MEDIUM, "high"
        )
        assert credibility_agent._meets_minimum_credibility(
            CredibilityLevel.MEDIUM, "medium"
        )
        assert credibility_agent._meets_minimum_credibility(
            CredibilityLevel.MEDIUM, "low"
        )

        # LOW only meets low
        assert not credibility_agent._meets_minimum_credibility(
            CredibilityLevel.LOW, "high"
        )
        assert not credibility_agent._meets_minimum_credibility(
            CredibilityLevel.LOW, "medium"
        )
        assert credibility_agent._meets_minimum_credibility(
            CredibilityLevel.LOW, "low"
        )

    def test_credibility_sort_key(self, credibility_agent):
        """Test credibility sorting."""
        high_key = credibility_agent._credibility_sort_key(CredibilityLevel.HIGH)
        medium_key = credibility_agent._credibility_sort_key(CredibilityLevel.MEDIUM)
        low_key = credibility_agent._credibility_sort_key(CredibilityLevel.LOW)
        very_low_key = credibility_agent._credibility_sort_key(CredibilityLevel.VERY_LOW)

        # HIGH should sort first (lowest key)
        assert high_key < medium_key < low_key < very_low_key

    def test_get_color_for_level(self, credibility_agent):
        """Test color assignment for credibility levels."""
        assert credibility_agent._get_color_for_level(CredibilityLevel.HIGH) == "green"
        assert credibility_agent._get_color_for_level(CredibilityLevel.MEDIUM) == "yellow"
        assert credibility_agent._get_color_for_level(CredibilityLevel.LOW) == "orange"
        assert credibility_agent._get_color_for_level(CredibilityLevel.VERY_LOW) == "red"

    def test_calculate_credibility_breakdown(self, credibility_agent):
        """Test credibility breakdown calculation."""
        studies = [
            {"credibility": {"level": CredibilityLevel.HIGH}},
            {"credibility": {"level": CredibilityLevel.HIGH}},
            {"credibility": {"level": CredibilityLevel.MEDIUM}},
            {"credibility": {"level": CredibilityLevel.LOW}},
        ]

        breakdown = credibility_agent._calculate_credibility_breakdown(studies)

        assert breakdown["high"] == 2
        assert breakdown["medium"] == 1
        assert breakdown["low"] == 1
        assert breakdown["very_low"] == 0

    def test_calculate_design_breakdown(self, credibility_agent):
        """Test study design breakdown calculation."""
        studies = [
            {"credibility": {"study_design": "Randomized Controlled Trial (RCT)"}},
            {"credibility": {"study_design": "Randomized Controlled Trial (RCT)"}},
            {"credibility": {"study_design": "Cohort Study"}},
            {"credibility": {"study_design": "Case-Control Study"}},
        ]

        breakdown = credibility_agent._calculate_design_breakdown(studies)

        assert breakdown["Randomized Controlled Trial (RCT)"] == 2
        assert breakdown["Cohort Study"] == 1
        assert breakdown["Case-Control Study"] == 1

    def test_calculate_grade_breakdown(self, credibility_agent):
        """Test GRADE quality breakdown calculation."""
        studies = [
            {"credibility": {"grade_quality": "HIGH"}},
            {"credibility": {"grade_quality": "HIGH"}},
            {"credibility": {"grade_quality": "MODERATE"}},
            {"credibility": {"grade_quality": "LOW"}},
        ]

        breakdown = credibility_agent._calculate_grade_breakdown(studies)

        assert breakdown["HIGH"] == 2
        assert breakdown["MODERATE"] == 1
        assert breakdown["LOW"] == 1
        assert breakdown["VERY LOW"] == 0

    def test_parse_comprehensive_assessment(self, credibility_agent):
        """Test parsing of comprehensive assessment response."""
        response = """
Study Design: Randomized Controlled Trial (RCT)
Evidence Level: 2 - High quality RCT
Risk of Bias Overall: Low
Risk of Bias Details: All domains low risk
GRADE Quality: HIGH
GRADE Justification: Well-conducted RCT with no serious concerns
Sample Size: Adequate
Power Analysis: Present and adequate
Methodological Strengths:
- Randomization with concealment
- Double-blind design
- Complete follow-up
Methodological Limitations:
- Single-center study
- Short follow-up period
Replicability: High
Overall Credibility: HIGH
Quality Score: 90
Inclusion Recommendation: Recommend include
Reasoning: Excellent quality RCT suitable for meta-analysis
"""

        parsed = credibility_agent._parse_comprehensive_assessment(response)

        assert parsed["study_design"] == "Randomized Controlled Trial (RCT)"
        assert parsed["evidence_level"] == 2
        assert parsed["risk_of_bias_overall"] == "Low"
        assert parsed["grade_quality"] == "HIGH"
        assert parsed["sample_size"] == "Adequate"
        assert parsed["replicability"] == "High"
        assert parsed["level"] == CredibilityLevel.HIGH
        assert parsed["quality_score"] == 90
        assert len(parsed["methodological_strengths"]) == 3
        assert len(parsed["methodological_limitations"]) == 2

    def test_parse_assessment_medium_credibility(self, credibility_agent):
        """Test parsing medium credibility assessment."""
        response = """
Study Design: Cohort Study
Evidence Level: 3 - Observational study
Risk of Bias Overall: Some concerns
GRADE Quality: MODERATE
Sample Size: Borderline
Overall Credibility: MEDIUM
Quality Score: 65
"""

        parsed = credibility_agent._parse_comprehensive_assessment(response)

        assert parsed["level"] == CredibilityLevel.MEDIUM
        assert parsed["grade_quality"] == "MODERATE"
        assert parsed["quality_score"] == 65

    def test_parse_assessment_low_credibility(self, credibility_agent):
        """Test parsing low credibility assessment."""
        response = """
Study Design: Case Series
Evidence Level: 6 - Weak evidence
Risk of Bias Overall: High
GRADE Quality: LOW
Sample Size: Inadequate
Overall Credibility: LOW
Quality Score: 35
"""

        parsed = credibility_agent._parse_comprehensive_assessment(response)

        assert parsed["level"] == CredibilityLevel.LOW
        assert parsed["grade_quality"] == "LOW"
        assert parsed["quality_score"] == 35

    def test_parse_assessment_very_low_credibility(self, credibility_agent):
        """Test parsing very low credibility assessment."""
        response = """
Study Design: Expert Opinion
Evidence Level: 8 - Lowest evidence level
Risk of Bias Overall: High
GRADE Quality: VERY LOW
Sample Size: Not applicable
Overall Credibility: VERY LOW
Quality Score: 15
"""

        parsed = credibility_agent._parse_comprehensive_assessment(response)

        assert parsed["level"] == CredibilityLevel.VERY_LOW
        assert parsed["grade_quality"] == "VERY LOW"
        assert parsed["quality_score"] == 15

    @pytest.mark.asyncio
    async def test_study_sorting_by_credibility(self, credibility_agent):
        """Test that studies are sorted by credibility and quality score."""
        # Mock studies with different credibility levels
        async def mock_evaluate(study, **kwargs):
            # Return different credibility based on study ID
            study_id = study.get("id", "")
            if "1" in study_id:
                return {
                    "level": CredibilityLevel.HIGH,
                    "quality_score": 90,
                    "is_peer_reviewed": True,
                    "is_preprint": False,
                    "is_retracted": False,
                    "study_design": "RCT",
                    "grade_quality": "HIGH",
                }
            elif "2" in study_id:
                return {
                    "level": CredibilityLevel.MEDIUM,
                    "quality_score": 70,
                    "is_peer_reviewed": True,
                    "is_preprint": False,
                    "is_retracted": False,
                    "study_design": "Cohort",
                    "grade_quality": "MODERATE",
                }
            else:
                return {
                    "level": CredibilityLevel.LOW,
                    "quality_score": 40,
                    "is_peer_reviewed": True,
                    "is_preprint": False,
                    "is_retracted": False,
                    "study_design": "Case-Control",
                    "grade_quality": "LOW",
                }

        credibility_agent._evaluate_credibility_comprehensive = mock_evaluate
        credibility_agent.make_decision = AsyncMock(
            return_value=MagicMock(model_dump=lambda: {"decision": "OK"})
        )

        studies = [
            {"id": "3", "title": "Low quality"},
            {"id": "1", "title": "High quality"},
            {"id": "2", "title": "Medium quality"},
        ]

        result = await credibility_agent.process({"studies": studies})

        # Should be sorted: HIGH, MEDIUM, LOW
        assert result["studies"][0]["credibility"]["level"] == CredibilityLevel.HIGH
        assert result["studies"][1]["credibility"]["level"] == CredibilityLevel.MEDIUM
        assert result["studies"][2]["credibility"]["level"] == CredibilityLevel.LOW
