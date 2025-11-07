"""Unit tests for APA report generation."""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
import tempfile
import os

from app.services.apa_report_generator import (
    APAReportGenerator,
    APACitationFormatter,
    APAFormatConfig,
)


class TestAPACitationFormatter:
    """Test cases for APA citation formatting."""

    def test_format_journal_article_basic(self):
        """Test basic journal article citation formatting."""
        formatter = APACitationFormatter()

        citation = formatter.format_journal_article(
            authors=["Smith, J. D.", "Jones, A. B."],
            year=2020,
            title="Effects of mindfulness on anxiety",
            journal="Journal of Clinical Psychology",
            volume=76,
            issue=5,
            pages="123-145",
            doi="10.1234/jcp.2020.12345",
        )

        assert "Smith, J. D., & Jones, A. B." in citation
        assert "(2020)" in citation
        assert "Effects of mindfulness on anxiety" in citation
        assert "Journal of Clinical Psychology" in citation
        assert "76(5)" in citation
        assert "123-145" in citation
        assert "https://doi.org/10.1234/jcp.2020.12345" in citation

    def test_format_journal_article_single_author(self):
        """Test citation with single author."""
        formatter = APACitationFormatter()

        citation = formatter.format_journal_article(
            authors=["Smith, J. D."],
            year=2020,
            title="Test article",
            journal="Test Journal",
        )

        assert "Smith, J. D." in citation
        assert " & " not in citation

    def test_format_journal_article_no_doi(self):
        """Test citation without DOI."""
        formatter = APACitationFormatter()

        citation = formatter.format_journal_article(
            authors=["Smith, J. D."],
            year=2020,
            title="Test article",
            journal="Test Journal",
            volume=1,
        )

        assert "doi" not in citation.lower()
        assert "Test Journal, 1." in citation

    def test_format_author_list_two_authors(self):
        """Test author list formatting with two authors."""
        formatter = APACitationFormatter()

        formatted = formatter._format_author_list(["Smith, J.", "Jones, A."])

        assert formatted == "Smith, J., & Jones, A."

    def test_format_author_list_three_authors(self):
        """Test author list formatting with three authors."""
        formatter = APACitationFormatter()

        formatted = formatter._format_author_list(["Smith, J.", "Jones, A.", "Brown, K."])

        assert formatted == "Smith, J., Jones, A., & Brown, K."

    def test_format_author_list_many_authors(self):
        """Test author list formatting with 21+ authors."""
        formatter = APACitationFormatter()

        authors = [f"Author{i}, X." for i in range(25)]
        formatted = formatter._format_author_list(authors)

        assert "..." in formatted
        assert formatted.count(",") == 19  # First 19 authors + final author

    def test_format_in_text_citation_single_author(self):
        """Test in-text citation with single author."""
        formatter = APACitationFormatter()

        citation = formatter.format_in_text_citation(["Smith"], 2020)

        assert citation == "(Smith, 2020)"

    def test_format_in_text_citation_two_authors(self):
        """Test in-text citation with two authors."""
        formatter = APACitationFormatter()

        citation = formatter.format_in_text_citation(["Smith", "Jones"], 2020)

        assert citation == "(Smith & Jones, 2020)"

    def test_format_in_text_citation_three_or_more_authors(self):
        """Test in-text citation with three or more authors."""
        formatter = APACitationFormatter()

        citation = formatter.format_in_text_citation(["Smith", "Jones", "Brown"], 2020)

        assert citation == "(Smith et al., 2020)"

    def test_format_in_text_citation_no_authors(self):
        """Test in-text citation with no authors."""
        formatter = APACitationFormatter()

        citation = formatter.format_in_text_citation([], 2020)

        assert citation == "(Unknown, 2020)"


class TestAPAReportGenerator:
    """Test cases for APA report generation."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def generator(self, temp_output_dir):
        """Create report generator instance."""
        return APAReportGenerator(output_dir=temp_output_dir)

    @pytest.fixture
    def sample_analysis_data(self):
        """Sample analysis data for testing."""
        return {
            "id": "test-analysis-123",
            "title": "Effects of Mindfulness on Anxiety: A Meta-Analysis",
            "topic": "mindfulness and anxiety",
            "research_question": "What is the effect of mindfulness-based interventions on anxiety?",
            "num_studies": 10,
            "num_participants": 500,
            "num_identified": 200,
            "num_screened": 50,
            "pooled_effect_size": 0.63,
            "ci_lower": 0.48,
            "ci_upper": 0.78,
            "p_value": 0.001,
            "i_squared": 42.3,
            "year_range": "2010-2024",
            "search_date": "January 15, 2024",
            "databases": ["PubMed", "PsycINFO"],
            "search_terms": ["mindfulness", "anxiety"],
            "inclusion_criteria": ["RCT", "Adult participants"],
            "exclusion_criteria": ["Non-English"],
            "analysis_method": "random-effects model",
            "keywords": ["meta-analysis", "mindfulness", "anxiety"],
            "authors": ["Smith, J. D.", "Jones, A. B."],
            "institution": "University of Testing",
            "studies": [
                {
                    "authors": ["Hofmann, S. G."],
                    "year": 2010,
                    "title": "Test study",
                    "journal": "Test Journal",
                    "volume": 1,
                    "issue": 1,
                    "pages": "1-10",
                    "doi": "10.1234/test",
                    "sample_size": 100,
                    "design": "RCT",
                    "effect_size": 0.5,
                    "ci_lower": 0.3,
                    "ci_upper": 0.7,
                    "standard_error": 0.1,
                    "quality_rating": "High",
                }
            ],
        }

    def test_generator_initialization(self, temp_output_dir):
        """Test generator initialization."""
        generator = APAReportGenerator(output_dir=temp_output_dir)

        assert generator.output_dir == temp_output_dir
        assert temp_output_dir.exists()
        assert isinstance(generator.citation_formatter, APACitationFormatter)

    def test_generate_abstract(self, generator, sample_analysis_data):
        """Test abstract generation."""
        abstract = generator._generate_abstract(sample_analysis_data)

        assert isinstance(abstract, str)
        assert len(abstract) > 0
        assert "meta-analysis" in abstract.lower()
        assert str(sample_analysis_data["num_studies"]) in abstract
        assert str(sample_analysis_data["pooled_effect_size"]) in abstract

    def test_generate_introduction(self, generator, sample_analysis_data):
        """Test introduction generation."""
        intro = generator._generate_introduction(sample_analysis_data)

        assert isinstance(intro, str)
        assert len(intro) > 0
        assert sample_analysis_data["topic"] in intro.lower()

    def test_generate_discussion(self, generator, sample_analysis_data):
        """Test discussion generation."""
        discussion = generator._generate_discussion(sample_analysis_data)

        assert isinstance(discussion, str)
        assert len(discussion) > 0
        assert str(sample_analysis_data["pooled_effect_size"]) in discussion

    def test_generate_word_document(self, generator, sample_analysis_data):
        """Test Word document generation."""
        output_path = generator._generate_word_document(
            analysis_data=sample_analysis_data,
            custom_sections=None,
        )

        assert output_path.exists()
        assert output_path.suffix == ".docx"
        assert output_path.stat().st_size > 0

    def test_generate_word_document_with_custom_sections(self, generator, sample_analysis_data):
        """Test Word document generation with custom sections."""
        custom_sections = {
            "abstract": "This is a custom abstract.",
            "introduction": "This is a custom introduction.",
        }

        output_path = generator._generate_word_document(
            analysis_data=sample_analysis_data,
            custom_sections=custom_sections,
        )

        assert output_path.exists()
        assert output_path.suffix == ".docx"

    def test_generate_pdf_document(self, generator, sample_analysis_data):
        """Test PDF document generation."""
        output_path = generator._generate_pdf_document(
            analysis_data=sample_analysis_data,
            custom_sections=None,
        )

        assert output_path.exists()
        assert output_path.suffix == ".pdf"
        assert output_path.stat().st_size > 0

    def test_generate_report_docx_only(self, generator, sample_analysis_data):
        """Test report generation with DOCX format only."""
        result = generator.generate_report(
            analysis_data=sample_analysis_data,
            format="docx",
        )

        assert "docx_path" in result
        assert "pdf_path" not in result
        assert "generated_at" in result
        assert Path(result["docx_path"]).exists()

    def test_generate_report_pdf_only(self, generator, sample_analysis_data):
        """Test report generation with PDF format only."""
        result = generator.generate_report(
            analysis_data=sample_analysis_data,
            format="pdf",
        )

        assert "pdf_path" in result
        assert "docx_path" not in result
        assert "generated_at" in result
        assert Path(result["pdf_path"]).exists()

    def test_generate_report_both_formats(self, generator, sample_analysis_data):
        """Test report generation with both formats."""
        result = generator.generate_report(
            analysis_data=sample_analysis_data,
            format="both",
        )

        assert "docx_path" in result
        assert "pdf_path" in result
        assert "generated_at" in result
        assert Path(result["docx_path"]).exists()
        assert Path(result["pdf_path"]).exists()

    def test_generate_forest_plot(self, generator, sample_analysis_data):
        """Test forest plot generation."""
        studies = sample_analysis_data["studies"]

        output_path = generator.generate_forest_plot(studies)

        assert output_path.exists()
        assert output_path.suffix == ".png"
        assert output_path.stat().st_size > 0

    def test_generate_funnel_plot(self, generator, sample_analysis_data):
        """Test funnel plot generation."""
        studies = sample_analysis_data["studies"]

        output_path = generator.generate_funnel_plot(studies)

        assert output_path.exists()
        assert output_path.suffix == ".png"
        assert output_path.stat().st_size > 0

    def test_generate_forest_plot_with_custom_path(self, generator, sample_analysis_data, temp_output_dir):
        """Test forest plot generation with custom output path."""
        studies = sample_analysis_data["studies"]
        custom_path = temp_output_dir / "custom_forest_plot.png"

        output_path = generator.generate_forest_plot(studies, output_path=custom_path)

        assert output_path == custom_path
        assert output_path.exists()

    def test_generate_funnel_plot_with_custom_path(self, generator, sample_analysis_data, temp_output_dir):
        """Test funnel plot generation with custom output path."""
        studies = sample_analysis_data["studies"]
        custom_path = temp_output_dir / "custom_funnel_plot.png"

        output_path = generator.generate_funnel_plot(studies, output_path=custom_path)

        assert output_path == custom_path
        assert output_path.exists()

    def test_apa_format_config(self):
        """Test APA format configuration values."""
        assert APAFormatConfig.FONT_NAME == "Times New Roman"
        assert APAFormatConfig.FONT_SIZE == 12
        assert APAFormatConfig.LINE_SPACING == 2.0
        assert APAFormatConfig.MARGIN_INCHES == 1.0
        assert APAFormatConfig.ABSTRACT_MAX_WORDS == 250

    def test_heading_sizes_configuration(self):
        """Test heading size configuration."""
        assert len(APAFormatConfig.HEADING_SIZES) == 5
        assert APAFormatConfig.HEADING_SIZES[1] == 14
        assert APAFormatConfig.HEADING_SIZES[5] == 12


class TestAPAReportGeneratorEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def generator(self, temp_output_dir):
        """Create report generator instance."""
        return APAReportGenerator(output_dir=temp_output_dir)

    def test_generate_report_with_minimal_data(self, generator):
        """Test report generation with minimal required data."""
        minimal_data = {
            "id": "minimal-test",
            "title": "Minimal Test Report",
            "studies": [],
        }

        result = generator.generate_report(
            analysis_data=minimal_data,
            format="docx",
        )

        assert "docx_path" in result
        assert Path(result["docx_path"]).exists()

    def test_generate_report_with_empty_studies(self, generator):
        """Test report generation with empty studies list."""
        data = {
            "id": "empty-studies",
            "title": "Report with No Studies",
            "studies": [],
            "num_studies": 0,
        }

        result = generator.generate_report(
            analysis_data=data,
            format="docx",
        )

        assert "docx_path" in result

    def test_generate_forest_plot_with_empty_studies(self, generator):
        """Test forest plot generation with empty studies list."""
        # Should not crash, should handle gracefully
        output_path = generator.generate_forest_plot([])

        assert output_path.exists()

    def test_citation_formatter_with_missing_fields(self):
        """Test citation formatting with missing optional fields."""
        formatter = APACitationFormatter()

        citation = formatter.format_journal_article(
            authors=["Test, A."],
            year=2020,
            title="Test",
            journal="Journal",
        )

        assert "Test, A." in citation
        assert "(2020)" in citation
        assert "Journal." in citation


class TestAPAReportGeneratorIntegration:
    """Integration tests for complete report generation workflow."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def generator(self, temp_output_dir):
        """Create report generator instance."""
        return APAReportGenerator(output_dir=temp_output_dir)

    def test_full_report_generation_workflow(self, generator):
        """Test complete workflow from data to reports."""
        # Complete analysis data
        analysis_data = {
            "id": "integration-test",
            "title": "Complete Integration Test Report",
            "topic": "test topic",
            "research_question": "What is the test question?",
            "num_studies": 5,
            "num_participants": 250,
            "pooled_effect_size": 0.5,
            "ci_lower": 0.3,
            "ci_upper": 0.7,
            "p_value": 0.01,
            "i_squared": 30.0,
            "authors": ["Test, A.", "Researcher, B."],
            "institution": "Test University",
            "keywords": ["test", "meta-analysis"],
            "databases": ["TestDB"],
            "studies": [
                {
                    "authors": ["Author, X."],
                    "year": 2020,
                    "title": "Test Study",
                    "journal": "Test Journal",
                    "volume": 1,
                    "effect_size": 0.5,
                    "ci_lower": 0.2,
                    "ci_upper": 0.8,
                    "standard_error": 0.15,
                    "sample_size": 50,
                    "design": "RCT",
                    "quality_rating": "High",
                }
            ],
        }

        # Generate both formats
        result = generator.generate_report(
            analysis_data=analysis_data,
            format="both",
            custom_sections={
                "abstract": "This is a custom abstract for integration testing.",
            },
        )

        # Verify both files were created
        assert "docx_path" in result
        assert "pdf_path" in result
        assert Path(result["docx_path"]).exists()
        assert Path(result["pdf_path"]).exists()

        # Verify file sizes are reasonable
        assert Path(result["docx_path"]).stat().st_size > 1000
        assert Path(result["pdf_path"]).stat().st_size > 1000

        # Generate visualizations
        forest_plot = generator.generate_forest_plot(analysis_data["studies"])
        funnel_plot = generator.generate_funnel_plot(analysis_data["studies"])

        assert forest_plot.exists()
        assert funnel_plot.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
