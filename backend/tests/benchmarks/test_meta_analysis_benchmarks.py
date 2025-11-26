"""
Meta-Analysis Benchmark Tests

External validity tests for meta-analysis statistical accuracy.

CRITICAL: All data comes from quality/benchmarks/, never invented.
"""

import pytest
import json
from pathlib import Path


class TestMetaAnalysisBenchmarks:
    """
    Benchmark tests for meta-analysis workflows.

    These tests verify the platform produces scientifically accurate results
    using real benchmark datasets.
    """

    @pytest.fixture
    def omega3_benchmark(self):
        """Load omega-3 depression benchmark dataset."""
        # Get project root (backend/tests/benchmarks -> backend -> project_root)
        project_root = Path(__file__).parent.parent.parent.parent
        benchmark_dir = project_root / "quality/benchmarks/meta_analysis/omega3_depression"

        # Verify benchmark exists
        assert benchmark_dir.exists(), f"Benchmark directory not found: {benchmark_dir}"

        # Load studies
        studies_file = benchmark_dir / "studies.json"
        assert studies_file.exists(), f"Studies file not found: {studies_file}"

        with open(studies_file) as f:
            studies_data = json.load(f)

        # Load ground truth
        ground_truth_file = benchmark_dir / "ground_truth.json"
        assert ground_truth_file.exists(), f"Ground truth file not found: {ground_truth_file}"

        with open(ground_truth_file) as f:
            ground_truth = json.load(f)

        return {
            "studies": studies_data["studies"],
            "expected": ground_truth["expected_outcomes"]["meta_analysis"],
            "ground_truth": ground_truth
        }

    def test_benchmark_data_loads(self, omega3_benchmark):
        """
        Verify benchmark dataset loads correctly.

        This is a smoke test ensuring benchmark data structure is valid.
        """
        # Verify studies loaded
        assert len(omega3_benchmark["studies"]) == 11, \
            "Expected 11 studies in omega-3 benchmark"

        # Verify expected outcomes present
        expected = omega3_benchmark["expected"]
        assert "pooled_effect" in expected
        assert "i_squared" in expected
        assert "should_pool" in expected

    def test_benchmark_studies_have_required_fields(self, omega3_benchmark):
        """
        Verify all benchmark studies have required fields.

        Required: pmid, title, authors, year, effect_size, sample_size, variance
        """
        required_fields = [
            "pmid", "title", "authors", "year",
            "effect_size", "sample_size", "variance"
        ]

        for i, study in enumerate(omega3_benchmark["studies"]):
            for field in required_fields:
                assert field in study, \
                    f"Study {i} missing required field: {field}"

            # Verify PMIDs are realistic (8 digits)
            assert len(study["pmid"]) == 8, \
                f"Study {i} PMID should be 8 digits, got: {study['pmid']}"

            # Verify effect sizes are reasonable (-2 to +2 for SMD)
            assert -2.0 <= study["effect_size"] <= 2.0, \
                f"Study {i} effect size unrealistic: {study['effect_size']}"

    def test_ground_truth_expectations(self, omega3_benchmark):
        """
        Verify ground truth contains valid expected outcomes.

        This ensures benchmark datasets follow standards.
        """
        expected = omega3_benchmark["expected"]

        # Verify pooled effect expectations
        assert expected["pooled_effect"] == -0.28, \
            "Ground truth pooled effect should match documented value"

        # Verify heterogeneity expectations
        assert expected["i_squared"] == 46.2, \
            "Ground truth I² should match documented value"

        # Verify interpretation
        assert expected["heterogeneity_interpretation"] == "moderate", \
            "I² of 46.2% should be interpreted as moderate"

        # Verify pooling decision
        assert expected["should_pool"] is True, \
            "Moderate heterogeneity should allow pooling"

    def test_heterogeneity_threshold_logic(self, omega3_benchmark):
        """
        Verify pooling decision matches I² threshold rule.

        Rule: I² ≤ 75% → should_pool = True
        """
        expected = omega3_benchmark["expected"]

        i_squared = expected["i_squared"]
        should_pool = expected["should_pool"]

        # Apply threshold logic
        expected_should_pool = i_squared <= 75.0

        assert should_pool == expected_should_pool, \
            f"Pooling decision inconsistent: I²={i_squared}%, should_pool={should_pool}"

    def test_tolerance_values_are_reasonable(self, omega3_benchmark):
        """
        Verify tolerances are strict (not loosened to pass tests).

        Max acceptable:
        - pooled_effect_tolerance: 0.10
        - i_squared_tolerance: 10.0
        """
        expected = omega3_benchmark["expected"]

        # Check pooled effect tolerance
        pe_tolerance = expected.get("pooled_effect_tolerance", 0.05)
        assert pe_tolerance <= 0.10, \
            f"Pooled effect tolerance too loose: {pe_tolerance} (max 0.10)"

        # Check I² tolerance
        i_sq_tolerance = expected.get("i_squared_tolerance", 5.0)
        assert i_sq_tolerance <= 10.0, \
            f"I² tolerance too loose: {i_sq_tolerance} (max 10.0)"

    def test_credibility_expectations(self, omega3_benchmark):
        """
        Verify credibility expectations match study quality distribution.
        """
        ground_truth = omega3_benchmark["ground_truth"]
        credibility_expected = ground_truth["expected_outcomes"]["credibility"]

        # Verify counts
        assert credibility_expected["high_quality_studies"] == 6
        assert credibility_expected["medium_quality_studies"] == 5
        assert credibility_expected["low_quality_studies"] == 0

        # Verify full-text availability
        assert credibility_expected["full_text_available"] == 6
        assert credibility_expected["abstract_only"] == 5

    # NOTE: Actual statistical tests would go here
    # These would call the real StatisticalAgent and verify results
    # For now, these tests validate the benchmark data structure

    def test_benchmark_readme_exists(self):
        """
        Verify benchmark has documentation.

        All benchmarks must have README with source information.
        """
        project_root = Path(__file__).parent.parent.parent.parent
        readme = project_root / "quality/benchmarks/meta_analysis/omega3_depression/README.md"

        assert readme.exists(), "Benchmark must have README.md with source documentation"

        # Verify README contains required sections
        content = readme.read_text()
        assert "## Source" in content
        assert "## Validation" in content
        assert "## Expected Use" in content


# Future tests when StatisticalAgent is fully implemented:
# - test_pooled_effect_calculation
# - test_heterogeneity_calculation
# - test_confidence_intervals
# - test_p_value_calculation
# - test_insufficient_studies_blocking
# - test_high_heterogeneity_blocking
