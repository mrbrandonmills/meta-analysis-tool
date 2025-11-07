"""Integration tests for full-text PDF workflow.

Tests the complete workflow:
1. Download PDFs from sources
2. Extract text from PDFs
3. Perform full-text screening
4. Store results in database
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4

from app.services.pdf_download_service import PDFDownloadService
from app.services.pdf_text_extractor import PDFTextExtractor
from app.agents.specialized.full_text_screening import FullTextScreeningAgent
from app.agents.base import AgentConfig, AgentRole
from app.models.paper import Paper
from app.models.pdf_metadata import (
    PDFMetadata,
    PDFDownloadStatus,
    PDFSource,
    FullTextExtraction,
    FullTextScreening,
)


@pytest.mark.integration
class TestFullTextWorkflow:
    """Integration tests for full-text screening workflow."""

    @pytest.fixture
    def sample_papers(self, db_session):
        """Create sample papers in database."""
        papers = []
        for i in range(3):
            paper = Paper(
                id=uuid4(),
                title=f"Study {i+1}: Effects of Intervention on Outcome",
                abstract=f"This RCT examined intervention effects. N = {100 + i*50}. p < 0.05.",
                authors=["Smith J", "Johnson A"],
                journal="Test Journal",
                year=2023,
                doi=f"10.1234/test.{i+1}",
                pmid=f"1234567{i}",
                pmc_id=f"PMC12345{i}",
            )
            db_session.add(paper)
            papers.append(paper)

        db_session.commit()
        return papers

    @pytest.fixture
    def sample_pdf_text(self):
        """Sample academic paper text."""
        return """
        TITLE
        Effects of Mindfulness on Anxiety: A Randomized Controlled Trial

        ABSTRACT
        Background: Anxiety disorders are highly prevalent. This study examines
        the effects of mindfulness-based intervention on anxiety symptoms.
        Methods: We conducted a randomized controlled trial with N = 200 participants
        (mean age = 42.3, SD = 11.2). Participants were randomized to mindfulness
        intervention or waitlist control.
        Results: The intervention group showed significant reduction in anxiety
        (d = 0.68, 95% CI [0.45, 0.91], p < 0.001). Effect was maintained at
        3-month follow-up.
        Conclusions: Mindfulness-based intervention is effective for reducing anxiety.

        INTRODUCTION
        Anxiety disorders affect millions worldwide. Previous research has shown
        that mindfulness-based interventions may be helpful. However, rigorous
        RCTs are limited. This study addresses this gap.

        METHODS
        Study Design: This was a two-arm parallel randomized controlled trial.
        Registration: ClinicalTrials.gov NCT12345678.

        Participants: Adults aged 18-65 with diagnosed anxiety disorder.
        Recruitment occurred from January 2022 to June 2022.
        Sample size calculation indicated n = 180 needed for 80% power.

        Randomization: Computer-generated random sequence. Allocation concealment
        using sealed opaque envelopes. Blinding of outcome assessors.

        Intervention: 8-week mindfulness-based stress reduction program.
        Weekly 2-hour sessions plus daily home practice.

        Control: Waitlist control receiving intervention after study completion.

        Outcome Measures:
        Primary: Beck Anxiety Inventory (BAI) at 8 weeks.
        Secondary: Generalized Anxiety Disorder-7 (GAD-7), quality of life (SF-36).

        Statistical Analysis: Intention-to-treat analysis using mixed models.
        Effect sizes calculated using Cohen's d.

        RESULTS
        Participants: 200 randomized (100 intervention, 100 control).
        Attrition: 8% at post-treatment, 15% at follow-up.

        Primary Outcome: Significant group × time interaction (F = 45.2, p < 0.001).
        Intervention group showed greater reduction in BAI scores.
        Effect size: d = 0.68 (95% CI [0.45, 0.91]).

        Secondary Outcomes:
        - GAD-7: d = 0.55, p < 0.01
        - SF-36 mental component: d = 0.62, p < 0.001

        Subgroup Analysis: Effects consistent across age and gender.

        Adverse Events: No serious adverse events. 3 participants reported
        temporary increase in anxiety during initial sessions.

        DISCUSSION
        This RCT provides strong evidence for mindfulness-based intervention
        effectiveness in reducing anxiety. Effect sizes are medium to large
        and clinically meaningful.

        Comparison with Previous Research: Our findings align with meta-analytic
        evidence (Hofmann et al., 2010; Goyal et al., 2014).

        Strengths: Rigorous RCT design, adequate sample size, blinded assessment,
        intention-to-treat analysis, low attrition.

        Limitations: Single-site study, waitlist control (no active control),
        predominantly white sample limiting generalizability.

        Clinical Implications: Mindfulness-based interventions should be
        considered as evidence-based treatment for anxiety disorders.

        CONCLUSION
        Mindfulness-based stress reduction significantly reduces anxiety symptoms
        with medium to large effect sizes. Effects are maintained at follow-up.

        REFERENCES
        1. Hofmann SG, et al. (2010). Effect of mindfulness. J Consult Clin Psychol.
        2. Goyal M, et al. (2014). Meditation programs. JAMA Intern Med.
        """

    @patch("app.services.pdf_download_service.PDFDownloadService._download_from_url")
    def test_download_pdf_step(self, mock_download, db_session, sample_papers, tmp_path):
        """Test PDF download step of workflow."""
        # Setup mock download
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")
        mock_download.return_value = (True, test_pdf)

        # Initialize service
        download_service = PDFDownloadService(db_session, storage_dir=tmp_path)

        # Download PDFs
        success, metadata = download_service.download_pdf_for_paper(sample_papers[0])

        assert success
        assert metadata is not None
        assert metadata.download_status == PDFDownloadStatus.SUCCESS
        assert metadata.paper_id == sample_papers[0].id

        # Verify database
        saved_metadata = (
            db_session.query(PDFMetadata)
            .filter(PDFMetadata.paper_id == sample_papers[0].id)
            .first()
        )
        assert saved_metadata is not None
        assert saved_metadata.file_hash is not None

    @patch("app.services.pdf_text_extractor.PDFPLUMBER_AVAILABLE", True)
    @patch("app.services.pdf_text_extractor.pdfplumber")
    def test_extract_text_step(
        self, mock_pdfplumber, db_session, tmp_path, sample_pdf_text
    ):
        """Test text extraction step of workflow."""
        # Create PDF file
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")

        # Create PDF metadata
        pdf_metadata = PDFMetadata(
            id=uuid4(),
            paper_id=uuid4(),
            download_status=PDFDownloadStatus.SUCCESS,
            storage_path=str(test_pdf),
            extraction_status="pending",
        )
        db_session.add(pdf_metadata)
        db_session.commit()

        # Mock PDF extraction
        mock_page = Mock()
        mock_page.extract_text.return_value = sample_pdf_text
        mock_page.extract_tables.return_value = []

        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)

        mock_pdfplumber.open.return_value = mock_pdf

        # Extract text
        extractor = PDFTextExtractor(db_session)
        success, extraction = extractor.extract_text_from_pdf(pdf_metadata)

        assert success
        assert extraction is not None
        assert extraction.word_count > 100
        assert extraction.sections is not None
        assert len(extraction.statistics_found) > 0

        # Verify sections detected
        sections = extraction.sections
        assert "abstract" in str(sections).lower()
        assert "methods" in str(sections).lower()
        assert "results" in str(sections).lower()

        # Verify statistics extracted
        assert extraction.sample_size_mentions is not None
        assert len(extraction.sample_size_mentions) > 0

    @pytest.mark.asyncio
    async def test_full_text_screening_step(self, db_session, sample_pdf_text):
        """Test full-text screening step of workflow."""
        # Create extraction with sample text
        pdf_metadata = PDFMetadata(
            id=uuid4(),
            paper_id=uuid4(),
            download_status=PDFDownloadStatus.SUCCESS,
            extraction_status="completed",
        )
        db_session.add(pdf_metadata)
        db_session.commit()

        extraction = FullTextExtraction(
            id=uuid4(),
            pdf_metadata_id=pdf_metadata.id,
            full_text=sample_pdf_text,
            word_count=len(sample_pdf_text.split()),
            sections={
                "abstract": "Background: Anxiety disorders...",
                "methods": "Study Design: This was a two-arm...",
                "results": "Primary Outcome: Significant group...",
            },
            statistics_found=[
                {"text": "p < 0.001", "pattern": "p value"},
                {"text": "d = 0.68", "pattern": "effect size"},
                {"text": "n = 200", "pattern": "sample size"},
            ],
            study_design_mentions=["randomized controlled trial", "RCT"],
            sample_size_mentions=["n = 200", "n = 180"],
        )
        db_session.add(extraction)
        db_session.commit()

        # Initialize screening agent
        config = AgentConfig(
            name="FullTextScreeningAgent",
            role=AgentRole.SCREENING,
        )
        agent = FullTextScreeningAgent(config)

        # Perform screening
        inclusion_criteria = [
            "Randomized controlled trial",
            "Adult participants (18+)",
            "Anxiety as primary outcome",
        ]
        exclusion_criteria = [
            "Non-English language",
            "Qualitative study",
        ]

        results = await agent.process({
            "extractions": [extraction],
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "study_type": "RCT",
            "outcome_measures": ["anxiety"],
        })

        assert results is not None
        assert results["total_screened"] == 1
        assert len(results["included"]) + len(results["excluded"]) + len(results["uncertain"]) == 1

    @patch("app.services.pdf_download_service.PDFDownloadService._download_from_url")
    @patch("app.services.pdf_text_extractor.PDFPLUMBER_AVAILABLE", True)
    @patch("app.services.pdf_text_extractor.pdfplumber")
    @pytest.mark.asyncio
    async def test_complete_workflow(
        self,
        mock_pdfplumber,
        mock_download,
        db_session,
        sample_papers,
        sample_pdf_text,
        tmp_path,
    ):
        """Test complete end-to-end workflow."""
        # Step 1: Download PDF
        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")
        mock_download.return_value = (True, test_pdf)

        download_service = PDFDownloadService(db_session, storage_dir=tmp_path)
        success, pdf_metadata = download_service.download_pdf_for_paper(sample_papers[0])

        assert success
        assert pdf_metadata.download_status == PDFDownloadStatus.SUCCESS

        # Step 2: Extract text
        mock_page = Mock()
        mock_page.extract_text.return_value = sample_pdf_text
        mock_page.extract_tables.return_value = []

        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)

        mock_pdfplumber.open.return_value = mock_pdf

        extractor = PDFTextExtractor(db_session)
        success, extraction = extractor.extract_text_from_pdf(pdf_metadata)

        assert success
        assert extraction.word_count > 0
        assert pdf_metadata.extraction_status == "completed"

        # Step 3: Screen full text
        config = AgentConfig(
            name="FullTextScreeningAgent",
            role=AgentRole.SCREENING,
        )
        agent = FullTextScreeningAgent(config)

        results = await agent.process({
            "extractions": [extraction],
            "inclusion_criteria": ["RCT", "Anxiety outcome"],
            "exclusion_criteria": ["Qualitative"],
            "study_type": "RCT",
        })

        assert results["total_screened"] == 1

        # Step 4: Verify data persistence
        # Check PDF metadata
        saved_pdf = (
            db_session.query(PDFMetadata)
            .filter(PDFMetadata.paper_id == sample_papers[0].id)
            .first()
        )
        assert saved_pdf is not None
        assert saved_pdf.download_status == PDFDownloadStatus.SUCCESS

        # Check extraction
        saved_extraction = (
            db_session.query(FullTextExtraction)
            .filter(FullTextExtraction.pdf_metadata_id == pdf_metadata.id)
            .first()
        )
        assert saved_extraction is not None
        assert saved_extraction.word_count > 0

    def test_workflow_error_handling(self, db_session, sample_papers):
        """Test error handling in workflow."""
        # Test with missing file
        pdf_metadata = PDFMetadata(
            id=uuid4(),
            paper_id=sample_papers[0].id,
            download_status=PDFDownloadStatus.SUCCESS,
            storage_path="/nonexistent/file.pdf",
            extraction_status="pending",
        )
        db_session.add(pdf_metadata)
        db_session.commit()

        extractor = PDFTextExtractor(db_session)
        success, extraction = extractor.extract_text_from_pdf(pdf_metadata)

        assert not success
        assert extraction is None

    @patch("app.services.pdf_download_service.PDFDownloadService._download_from_url")
    def test_workflow_with_paywall(self, mock_download, db_session, sample_papers):
        """Test workflow when PDF is behind paywall."""
        # Mock 403 error (paywall)
        from httpx import HTTPStatusError, Response, Request

        mock_response = Response(status_code=403, request=Request("GET", "http://test.com"))
        mock_download.side_effect = HTTPStatusError(
            "Forbidden", request=mock_response.request, response=mock_response
        )

        download_service = PDFDownloadService(db_session)
        success, metadata = download_service.download_pdf_for_paper(sample_papers[0], max_retries=1)

        assert not success
        # Should mark as paywall or failed
        assert metadata.download_status in [
            PDFDownloadStatus.PAYWALL,
            PDFDownloadStatus.FAILED,
        ]

    @patch("app.services.pdf_text_extractor.PDFPLUMBER_AVAILABLE", True)
    @patch("app.services.pdf_text_extractor.pdfplumber")
    def test_workflow_with_scanned_pdf(self, mock_pdfplumber, db_session, tmp_path):
        """Test workflow with scanned PDF requiring OCR."""
        # Create PDF metadata
        test_pdf = tmp_path / "scanned.pdf"
        test_pdf.write_bytes(b"fake scanned pdf")

        pdf_metadata = PDFMetadata(
            id=uuid4(),
            paper_id=uuid4(),
            download_status=PDFDownloadStatus.SUCCESS,
            storage_path=str(test_pdf),
            extraction_status="pending",
        )
        db_session.add(pdf_metadata)
        db_session.commit()

        # Mock extraction with minimal text
        mock_page = Mock()
        mock_page.extract_text.return_value = "abc"  # Very short - likely scanned
        mock_page.extract_tables.return_value = []

        mock_pdf = Mock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=False)

        mock_pdfplumber.open.return_value = mock_pdf

        # Extract
        extractor = PDFTextExtractor(db_session)
        success, extraction = extractor.extract_text_from_pdf(pdf_metadata)

        assert not success
        assert pdf_metadata.is_scanned
        assert pdf_metadata.is_ocr_required
