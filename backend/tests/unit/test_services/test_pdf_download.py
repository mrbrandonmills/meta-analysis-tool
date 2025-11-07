"""Unit tests for PDF download service."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import httpx

from app.services.pdf_download_service import PDFDownloadService, RateLimiter
from app.models.paper import Paper
from app.models.pdf_metadata import PDFMetadata, PDFDownloadStatus, PDFSource


class TestRateLimiter:
    """Test rate limiter functionality."""

    def test_rate_limiter_initialization(self):
        """Test rate limiter initializes correctly."""
        limiter = RateLimiter(requests_per_second=5)
        assert limiter.requests_per_second == 5
        assert limiter.min_interval == 0.2

    def test_rate_limiter_waits(self):
        """Test rate limiter enforces delays."""
        limiter = RateLimiter(requests_per_second=10)

        import time
        start = time.time()
        limiter.wait_if_needed("test_source")
        limiter.wait_if_needed("test_source")
        elapsed = time.time() - start

        # Should wait at least the min_interval
        assert elapsed >= limiter.min_interval


class TestPDFDownloadService:
    """Test PDF download service."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        db = Mock()
        db.query.return_value.filter.return_value.first.return_value = None
        db.add = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        return db

    @pytest.fixture
    def sample_paper(self):
        """Create sample paper."""
        paper = Mock(spec=Paper)
        paper.id = "test-paper-id"
        paper.title = "Test Paper"
        paper.doi = "10.1234/test"
        paper.pmid = "12345678"
        paper.pmc_id = "PMC123456"
        paper.arxiv_id = "2301.12345"
        return paper

    @pytest.fixture
    def pdf_service(self, mock_db, tmp_path):
        """Create PDF download service."""
        service = PDFDownloadService(mock_db, storage_dir=tmp_path)
        return service

    def test_service_initialization(self, pdf_service, tmp_path):
        """Test service initializes correctly."""
        assert pdf_service.storage_dir == tmp_path
        assert pdf_service.storage_dir.exists()
        assert hasattr(pdf_service, "client")
        assert hasattr(pdf_service, "rate_limiter")

    def test_get_download_url_pmc(self, pdf_service, sample_paper):
        """Test getting download URL for PMC."""
        url = pdf_service._get_download_url(sample_paper, PDFSource.PUBMED_CENTRAL)
        assert url is not None
        assert "pmc" in url.lower()
        assert sample_paper.pmc_id in url

    def test_get_download_url_arxiv(self, pdf_service, sample_paper):
        """Test getting download URL for arXiv."""
        url = pdf_service._get_download_url(sample_paper, PDFSource.ARXIV)
        assert url is not None
        assert "arxiv.org" in url
        assert "2301.12345" in url

    def test_get_download_url_no_identifier(self, pdf_service, sample_paper):
        """Test getting download URL when paper lacks identifiers."""
        sample_paper.pmc_id = None
        sample_paper.arxiv_id = None
        sample_paper.doi = None

        url = pdf_service._get_download_url(sample_paper, PDFSource.PUBMED_CENTRAL)
        assert url is None

    @patch("app.services.pdf_download_service.PDFDownloadService._download_from_url")
    def test_download_pdf_success(self, mock_download, pdf_service, mock_db, sample_paper, tmp_path):
        """Test successful PDF download."""
        # Setup mock
        test_pdf_path = tmp_path / "test.pdf"
        test_pdf_path.write_bytes(b"fake pdf content")
        mock_download.return_value = (True, test_pdf_path)

        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # Download
        success, metadata = pdf_service.download_pdf_for_paper(sample_paper)

        assert success
        assert metadata is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()

    @patch("app.services.pdf_download_service.PDFDownloadService._get_download_url")
    def test_download_pdf_no_url(self, mock_get_url, pdf_service, mock_db, sample_paper):
        """Test download when no URL is available."""
        mock_get_url.return_value = None
        mock_db.query.return_value.filter.return_value.first.return_value = None

        success, metadata = pdf_service.download_pdf_for_paper(sample_paper, max_retries=1)

        assert not success
        assert metadata.download_status == PDFDownloadStatus.FAILED

    def test_download_from_url_success(self, pdf_service, tmp_path):
        """Test downloading from URL."""
        # Mock HTTP response
        with patch.object(pdf_service.client, "get") as mock_get:
            mock_response = Mock()
            mock_response.content = b"fake pdf content"
            mock_response.headers = {"content-type": "application/pdf"}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            success, file_path = pdf_service._download_from_url(
                "http://example.com/test.pdf",
                "test-id",
                PDFSource.PUBMED_CENTRAL
            )

            assert success
            assert file_path is not None
            assert file_path.exists()
            assert file_path.read_bytes() == b"fake pdf content"

    def test_download_from_url_not_pdf(self, pdf_service):
        """Test downloading non-PDF content."""
        with patch.object(pdf_service.client, "get") as mock_get:
            mock_response = Mock()
            mock_response.content = b"<html>not a pdf</html>"
            mock_response.headers = {"content-type": "text/html"}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            success, file_path = pdf_service._download_from_url(
                "http://example.com/test.html",
                "test-id",
                PDFSource.DOI_DIRECT
            )

            assert not success
            assert file_path is None

    def test_calculate_file_hash(self, pdf_service, tmp_path):
        """Test file hash calculation."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"test content")

        hash1 = pdf_service._calculate_file_hash(test_file)
        hash2 = pdf_service._calculate_file_hash(test_file)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length

    def test_batch_download(self, pdf_service, mock_db, sample_paper):
        """Test batch download."""
        papers = [sample_paper]

        with patch.object(pdf_service, "download_pdf_for_paper") as mock_download:
            mock_metadata = Mock()
            mock_metadata.download_attempts = 1
            mock_metadata.download_status = PDFDownloadStatus.SUCCESS
            mock_download.return_value = (True, mock_metadata)

            stats = pdf_service.batch_download(papers)

            assert stats["total"] == 1
            assert stats["success"] == 1
            assert stats["failed"] == 0

    def test_get_download_status(self, pdf_service, mock_db):
        """Test getting download status."""
        mock_metadata = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_metadata

        status = pdf_service.get_download_status("test-paper-id")

        assert status == mock_metadata
        mock_db.query.assert_called_once()

    def test_cleanup_old_pdfs(self, pdf_service, mock_db, tmp_path):
        """Test cleaning up old PDFs."""
        # Create test file
        test_file = tmp_path / "old.pdf"
        test_file.write_bytes(b"old pdf")

        # Mock old metadata
        old_metadata = Mock()
        old_metadata.storage_path = str(test_file)
        old_metadata.created_at = "2020-01-01"

        mock_db.query.return_value.filter.return_value.all.return_value = [old_metadata]

        pdf_service.cleanup_old_pdfs(days=30)

        mock_db.delete.assert_called_once_with(old_metadata)
        mock_db.commit.assert_called_once()
        assert not test_file.exists()
