"""Unit tests for PDF text extraction service."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from app.services.pdf_text_extractor import PDFTextExtractor
from app.models.pdf_metadata import (
    PDFMetadata,
    FullTextExtraction,
    SectionType,
    PDFDownloadStatus,
)


class TestPDFTextExtractor:
    """Test PDF text extraction service."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        db = Mock()
        db.add = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        db.query.return_value.filter.return_value.first.return_value = None
        return db

    @pytest.fixture
    def pdf_extractor(self, mock_db):
        """Create PDF text extractor."""
        return PDFTextExtractor(mock_db)

    @pytest.fixture
    def sample_pdf_metadata(self, tmp_path):
        """Create sample PDF metadata."""
        # Create fake PDF file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4 fake pdf content")

        metadata = Mock(spec=PDFMetadata)
        metadata.id = "test-metadata-id"
        metadata.paper_id = "test-paper-id"
        metadata.storage_path = str(pdf_file)
        metadata.download_status = PDFDownloadStatus.SUCCESS
        metadata.extraction_status = "pending"
        return metadata

    @pytest.fixture
    def sample_text(self):
        """Sample academic paper text."""
        return """
        Title: Effects of Intervention on Outcome

        ABSTRACT
        This study examines the effects of intervention X on outcome Y.
        We conducted a randomized controlled trial with n = 200 participants.
        Results showed significant improvement (p < 0.05).

        INTRODUCTION
        Previous research has shown...

        METHODS
        We recruited 200 participants (mean age = 45.2, SD = 10.1).
        This was a double-blind randomized controlled trial.
        Effect size was calculated using Cohen's d.

        RESULTS
        Primary outcome showed improvement (d = 0.65, 95% CI [0.42, 0.88], p = 0.001).
        Secondary outcomes were also significant (p < 0.05).

        DISCUSSION
        Our findings suggest that intervention X is effective...

        REFERENCES
        1. Smith et al. (2020). Previous study.
        2. Johnson et al. (2019). Related work.
        """

    def test_extractor_initialization(self, pdf_extractor):
        """Test extractor initializes correctly."""
        assert pdf_extractor.db is not None
        assert hasattr(pdf_extractor, "SECTION_PATTERNS")
        assert hasattr(pdf_extractor, "STATISTICS_PATTERNS")

    def test_detect_sections(self, pdf_extractor, sample_text):
        """Test section detection."""
        sections = pdf_extractor._detect_sections(sample_text)

        assert SectionType.ABSTRACT in sections
        assert SectionType.INTRODUCTION in sections
        assert SectionType.METHODS in sections
        assert SectionType.RESULTS in sections
        assert SectionType.DISCUSSION in sections
        assert SectionType.REFERENCES in sections

    def test_detect_sections_case_insensitive(self, pdf_extractor):
        """Test section detection is case insensitive."""
        text = """
        ABSTRACT
        This is the abstract.

        abstract
        This should also be detected.
        """
        sections = pdf_extractor._detect_sections(text)
        assert SectionType.ABSTRACT in sections

    def test_extract_statistics(self, pdf_extractor, sample_text):
        """Test statistics extraction."""
        statistics = pdf_extractor._extract_statistics(sample_text)

        assert len(statistics) > 0

        # Check for specific patterns
        p_values = [s for s in statistics if "p" in s["text"].lower()]
        assert len(p_values) > 0

        sample_sizes = [s for s in statistics if "n = " in s["text"].lower()]
        assert len(sample_sizes) > 0

    def test_extract_study_design_mentions(self, pdf_extractor, sample_text):
        """Test study design extraction."""
        mentions = pdf_extractor._extract_study_design_mentions(sample_text)

        assert len(mentions) > 0
        assert any("randomized controlled trial" in m.lower() for m in mentions)
        assert any("double" in m.lower() and "blind" in m.lower() for m in mentions)

    def test_extract_intervention_mentions(self, pdf_extractor):
        """Test intervention extraction."""
        text = """
        The intervention group received treatment X.
        The control group received placebo.
        """
        mentions = pdf_extractor._extract_intervention_mentions(text)

        assert len(mentions) > 0
        assert any("intervention group" in m.lower() for m in mentions)
        assert any("control group" in m.lower() for m in mentions)

    def test_extract_outcome_mentions(self, pdf_extractor):
        """Test outcome extraction."""
        text = """
        The primary outcome was symptom reduction.
        Secondary outcomes included quality of life.
        """
        mentions = pdf_extractor._extract_outcome_mentions(text)

        assert len(mentions) > 0
        assert any("primary outcome" in m.lower() for m in mentions)
        assert any("secondary outcome" in m.lower() for m in mentions)

    def test_extract_sample_size_mentions(self, pdf_extractor, sample_text):
        """Test sample size extraction."""
        mentions = pdf_extractor._extract_sample_size_mentions(sample_text)

        assert len(mentions) > 0
        assert any("n = 200" in m.lower() for m in mentions)

    def test_count_figures(self, pdf_extractor):
        """Test figure counting."""
        text = """
        As shown in Figure 1, the results were significant.
        Figure 2 shows the distribution.
        See Figure 1 again for comparison.
        """
        count = pdf_extractor._count_figures(text)

        assert count == 2  # Should count unique figures

    def test_count_references(self, pdf_extractor):
        """Test reference counting."""
        references_text = """
        1. Smith et al. (2020). First paper.
        2. Johnson et al. (2019). Second paper.
        3. Williams et al. (2018). Third paper.
        """
        count = pdf_extractor._count_references(references_text)

        assert count == 3

    def test_assess_extraction_quality_high(self, pdf_extractor, sample_text):
        """Test quality assessment for good extraction."""
        sections = pdf_extractor._detect_sections(sample_text)
        quality = pdf_extractor._assess_extraction_quality(sample_text, sections)

        assert quality > 0.5
        assert quality <= 1.0

    def test_assess_extraction_quality_low(self, pdf_extractor):
        """Test quality assessment for poor extraction."""
        text = "abc def ghi"  # Very short, no structure
        sections = {}
        quality = pdf_extractor._assess_extraction_quality(text, sections)

        assert quality < 0.5

    @patch("app.services.pdf_text_extractor.PDFPLUMBER_AVAILABLE", True)
    @patch("app.services.pdf_text_extractor.pdfplumber")
    def test_extract_with_pdfplumber(self, mock_pdfplumber, pdf_extractor, tmp_path):
        """Test extraction using pdfplumber."""
        # Mock PDF
        mock_page = Mock()
        mock_page.extract_text.return_value = "Page 1 text"
        mock_page.extract_tables.return_value = [["table", "data"]]

        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)

        mock_pdfplumber.open.return_value = mock_pdf

        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf")

        text, page_count, tables_count = pdf_extractor._extract_with_pdfplumber(test_file)

        assert text == "Page 1 text"
        assert page_count == 1
        assert tables_count == 1

    @patch("app.services.pdf_text_extractor.PYPDF2_AVAILABLE", True)
    @patch("app.services.pdf_text_extractor.PdfReader")
    def test_extract_with_pypdf2(self, mock_reader_class, pdf_extractor, tmp_path):
        """Test extraction using PyPDF2."""
        # Mock PDF
        mock_page = Mock()
        mock_page.extract_text.return_value = "Page 1 text"

        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_reader_class.return_value = mock_reader

        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf")

        text, page_count, tables_count = pdf_extractor._extract_with_pypdf2(test_file)

        assert text == "Page 1 text"
        assert page_count == 1
        assert tables_count == 0  # PyPDF2 doesn't detect tables

    @patch("app.services.pdf_text_extractor.PDFPLUMBER_AVAILABLE", True)
    @patch("app.services.pdf_text_extractor.pdfplumber")
    def test_extract_text_from_pdf_success(
        self, mock_pdfplumber, pdf_extractor, mock_db, sample_pdf_metadata, sample_text
    ):
        """Test successful text extraction."""
        # Mock PDF extraction
        mock_page = Mock()
        mock_page.extract_text.return_value = sample_text
        mock_page.extract_tables.return_value = []

        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)

        mock_pdfplumber.open.return_value = mock_pdf

        # Extract
        success, extraction = pdf_extractor.extract_text_from_pdf(sample_pdf_metadata)

        assert success
        assert extraction is not None
        assert extraction.word_count > 0
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()

    def test_extract_text_no_file(self, pdf_extractor, mock_db):
        """Test extraction when PDF file doesn't exist."""
        metadata = Mock(spec=PDFMetadata)
        metadata.storage_path = "/nonexistent/file.pdf"

        success, extraction = pdf_extractor.extract_text_from_pdf(metadata)

        assert not success
        assert extraction is None

    def test_extract_text_no_path(self, pdf_extractor, mock_db):
        """Test extraction when no storage path."""
        metadata = Mock(spec=PDFMetadata)
        metadata.storage_path = None

        success, extraction = pdf_extractor.extract_text_from_pdf(metadata)

        assert not success
        assert extraction is None

    @patch("app.services.pdf_text_extractor.PDFPLUMBER_AVAILABLE", True)
    @patch("app.services.pdf_text_extractor.pdfplumber")
    def test_extract_text_too_short(
        self, mock_pdfplumber, pdf_extractor, mock_db, sample_pdf_metadata
    ):
        """Test extraction with very short text (likely OCR needed)."""
        # Mock PDF with minimal text
        mock_page = Mock()
        mock_page.extract_text.return_value = "abc"  # Very short
        mock_page.extract_tables.return_value = []

        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)

        mock_pdfplumber.open.return_value = mock_pdf

        success, extraction = pdf_extractor.extract_text_from_pdf(sample_pdf_metadata)

        assert not success
        assert sample_pdf_metadata.is_scanned
        assert sample_pdf_metadata.is_ocr_required

    def test_batch_extract(self, pdf_extractor, mock_db):
        """Test batch extraction."""
        metadata_list = [Mock(spec=PDFMetadata) for _ in range(3)]

        with patch.object(pdf_extractor, "extract_text_from_pdf") as mock_extract:
            mock_extract.return_value = (True, Mock())

            stats = pdf_extractor.batch_extract(metadata_list)

            assert stats["total"] == 3
            assert stats["success"] == 3
            assert mock_extract.call_count == 3

    def test_get_extraction(self, pdf_extractor, mock_db):
        """Test getting extraction."""
        mock_extraction = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_extraction

        extraction = pdf_extractor.get_extraction("test-metadata-id")

        assert extraction == mock_extraction
        mock_db.query.assert_called_once()
