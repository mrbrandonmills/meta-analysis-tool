"""PDF download service for academic papers.

Supports multiple sources:
- PubMed Central (PMC)
- Europe PMC
- arXiv
- bioRxiv/medRxiv
- Unpaywall API
- Direct DOI resolution
"""

import hashlib
import httpx
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy.orm import Session

from app.models.paper import Paper
from app.models.pdf_metadata import (
    PDFMetadata,
    PDFDownloadStatus,
    PDFSource,
)
from app.core.config import get_settings


class RateLimiter:
    """Simple rate limiter for API requests."""

    def __init__(self, requests_per_second: float = 3):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time: Dict[str, float] = {}

    def wait_if_needed(self, source: str):
        """Wait if necessary to respect rate limits."""
        now = time.time()
        last_time = self.last_request_time.get(source, 0)
        time_since_last = now - last_time

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            logger.debug(f"Rate limiting {source}: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time[source] = time.time()


class PDFDownloadService:
    """Service for downloading PDFs from academic sources.

    Features:
    - Multi-source fallback strategy
    - Rate limiting and retry logic
    - Duplicate detection via hashing
    - Error tracking and reporting
    - Storage abstraction (local/S3/GCS)
    """

    def __init__(self, db: Session, storage_dir: Optional[Path] = None):
        """Initialize PDF download service.

        Args:
            db: Database session
            storage_dir: Directory for storing PDFs (defaults to config)
        """
        self.db = db
        self.settings = get_settings()
        self.storage_dir = storage_dir or Path(self.settings.downloads_dir) / "pdfs"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Rate limiter (3 requests/second by default)
        self.rate_limiter = RateLimiter(requests_per_second=3)

        # HTTP client with timeout and retries
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Meta-Analysis-Tool/1.0 (Educational Research Tool; mailto:research@example.com)"
            }
        )

        # Source priority order (most reliable first)
        self.source_priority = [
            PDFSource.PUBMED_CENTRAL,
            PDFSource.EUROPE_PMC,
            PDFSource.ARXIV,
            PDFSource.BIORXIV,
            PDFSource.UNPAYWALL,
            PDFSource.DOI_DIRECT,
        ]

    def download_pdf_for_paper(
        self, paper: Paper, max_retries: int = 3
    ) -> Tuple[bool, Optional[PDFMetadata]]:
        """Download PDF for a paper from available sources.

        Args:
            paper: Paper to download PDF for
            max_retries: Maximum retry attempts per source

        Returns:
            Tuple of (success, pdf_metadata)
        """
        logger.info(f"Starting PDF download for paper: {paper.title[:50]}...")

        # Check if PDF already downloaded
        existing_metadata = (
            self.db.query(PDFMetadata)
            .filter(PDFMetadata.paper_id == paper.id)
            .first()
        )

        if existing_metadata and existing_metadata.download_status == PDFDownloadStatus.SUCCESS:
            logger.info(f"PDF already downloaded for paper {paper.id}")
            return True, existing_metadata

        # Create or update metadata record
        pdf_metadata = existing_metadata or PDFMetadata(
            paper_id=paper.id,
            download_status=PDFDownloadStatus.PENDING,
        )

        # Try each source in priority order
        for source in self.source_priority:
            try:
                logger.debug(f"Trying source: {source}")

                # Get download URL for this source
                download_url = self._get_download_url(paper, source)
                if not download_url:
                    logger.debug(f"No URL available for source: {source}")
                    continue

                # Attempt download with retries
                for attempt in range(max_retries):
                    try:
                        success, file_path = self._download_from_url(
                            download_url, paper.id, source
                        )

                        if success and file_path:
                            # Calculate file hash for deduplication
                            file_hash = self._calculate_file_hash(file_path)

                            # Update metadata
                            pdf_metadata.download_status = PDFDownloadStatus.SUCCESS
                            pdf_metadata.pdf_source = source
                            pdf_metadata.download_url = download_url
                            pdf_metadata.storage_path = str(file_path)
                            pdf_metadata.storage_type = "local"
                            pdf_metadata.file_hash = file_hash
                            pdf_metadata.file_size_bytes = file_path.stat().st_size
                            pdf_metadata.download_attempts = attempt + 1

                            # Save metadata
                            if not existing_metadata:
                                self.db.add(pdf_metadata)
                            self.db.commit()
                            self.db.refresh(pdf_metadata)

                            logger.info(
                                f"Successfully downloaded PDF from {source} for paper {paper.id}"
                            )
                            return True, pdf_metadata

                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 429:  # Rate limited
                            wait_time = int(e.response.headers.get("Retry-After", 60))
                            logger.warning(
                                f"Rate limited by {source}, waiting {wait_time}s"
                            )
                            time.sleep(wait_time)
                        elif e.response.status_code == 403:  # Paywall
                            logger.info(f"PDF behind paywall at {source}")
                            pdf_metadata.download_status = PDFDownloadStatus.PAYWALL
                            break
                        else:
                            logger.warning(
                                f"HTTP error {e.response.status_code} from {source}"
                            )
                            if attempt == max_retries - 1:
                                raise

                    except Exception as e:
                        logger.warning(
                            f"Download attempt {attempt + 1} failed: {str(e)}"
                        )
                        if attempt == max_retries - 1:
                            raise

            except Exception as e:
                logger.error(f"Error downloading from {source}: {str(e)}")
                continue

        # All sources failed
        pdf_metadata.download_status = PDFDownloadStatus.FAILED
        pdf_metadata.error_message = "All download sources failed"
        pdf_metadata.download_attempts = max_retries * len(self.source_priority)

        if not existing_metadata:
            self.db.add(pdf_metadata)
        self.db.commit()
        self.db.refresh(pdf_metadata)

        logger.warning(f"Failed to download PDF for paper {paper.id}")
        return False, pdf_metadata

    def _get_download_url(self, paper: Paper, source: PDFSource) -> Optional[str]:
        """Get download URL for a specific source.

        Args:
            paper: Paper to get URL for
            source: PDF source to use

        Returns:
            Download URL or None if not available
        """
        if source == PDFSource.PUBMED_CENTRAL:
            if paper.pmc_id:
                # PMC OA subset download URL
                return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{paper.pmc_id}/pdf/"

        elif source == PDFSource.EUROPE_PMC:
            if paper.pmid:
                # Europe PMC API
                return f"https://www.ebi.ac.uk/europepmc/webservices/rest/{paper.pmid}/fullTextXML"

        elif source == PDFSource.ARXIV:
            if paper.arxiv_id:
                # arXiv PDF URL
                arxiv_id = paper.arxiv_id.replace("arXiv:", "")
                return f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        elif source == PDFSource.BIORXIV:
            # Check if DOI is from bioRxiv or medRxiv
            if paper.doi:
                if "biorxiv" in paper.doi.lower():
                    return f"https://www.biorxiv.org/content/{paper.doi}v1.full.pdf"
                elif "medrxiv" in paper.doi.lower():
                    return f"https://www.medrxiv.org/content/{paper.doi}v1.full.pdf"

        elif source == PDFSource.UNPAYWALL:
            if paper.doi:
                # Query Unpaywall API for OA location
                try:
                    self.rate_limiter.wait_if_needed("unpaywall")
                    email = self.settings.pubmed_email or "research@example.com"
                    response = self.client.get(
                        f"https://api.unpaywall.org/v2/{paper.doi}",
                        params={"email": email}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("is_oa") and data.get("best_oa_location"):
                            return data["best_oa_location"].get("url_for_pdf")
                except Exception as e:
                    logger.warning(f"Unpaywall API error: {str(e)}")

        elif source == PDFSource.DOI_DIRECT:
            if paper.doi:
                # Try direct DOI resolution (may hit paywall)
                return f"https://doi.org/{paper.doi}"

        return None

    def _download_from_url(
        self, url: str, paper_id, source: PDFSource
    ) -> Tuple[bool, Optional[Path]]:
        """Download PDF from URL.

        Args:
            url: URL to download from
            paper_id: Paper ID for filename
            source: Source being downloaded from

        Returns:
            Tuple of (success, file_path)
        """
        self.rate_limiter.wait_if_needed(str(source))

        logger.debug(f"Downloading from: {url}")
        response = self.client.get(url)
        response.raise_for_status()

        # Check if response is actually a PDF
        content_type = response.headers.get("content-type", "").lower()
        if "pdf" not in content_type and not url.endswith(".pdf"):
            # Might be HTML or XML
            if "html" in content_type or "xml" in content_type:
                logger.warning(f"Received {content_type} instead of PDF")
                return False, None

        # Save to file
        filename = f"{paper_id}_{source.value}.pdf"
        file_path = self.storage_dir / filename

        file_path.write_bytes(response.content)
        logger.debug(f"Saved PDF to: {file_path}")

        return True, file_path

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file for deduplication.

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def batch_download(
        self, papers: List[Paper], max_concurrent: int = 5
    ) -> Dict[str, int]:
        """Download PDFs for multiple papers.

        Args:
            papers: List of papers to download PDFs for
            max_concurrent: Maximum concurrent downloads (not implemented yet)

        Returns:
            Statistics dictionary
        """
        stats = {
            "total": len(papers),
            "success": 0,
            "failed": 0,
            "paywall": 0,
            "already_downloaded": 0,
        }

        for paper in papers:
            try:
                success, metadata = self.download_pdf_for_paper(paper)

                if success:
                    if metadata.download_attempts == 0:
                        stats["already_downloaded"] += 1
                    else:
                        stats["success"] += 1
                elif metadata.download_status == PDFDownloadStatus.PAYWALL:
                    stats["paywall"] += 1
                else:
                    stats["failed"] += 1

            except Exception as e:
                logger.error(f"Error downloading PDF for paper {paper.id}: {str(e)}")
                stats["failed"] += 1

        logger.info(f"Batch download complete: {stats}")
        return stats

    def get_download_status(self, paper_id) -> Optional[PDFMetadata]:
        """Get download status for a paper.

        Args:
            paper_id: Paper ID

        Returns:
            PDF metadata or None
        """
        return (
            self.db.query(PDFMetadata)
            .filter(PDFMetadata.paper_id == paper_id)
            .first()
        )

    def cleanup_old_pdfs(self, days: int = 30):
        """Clean up PDFs older than specified days.

        Args:
            days: Number of days to keep PDFs
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        old_metadata = (
            self.db.query(PDFMetadata)
            .filter(PDFMetadata.created_at < cutoff_date)
            .all()
        )

        deleted_count = 0
        for metadata in old_metadata:
            if metadata.storage_path:
                file_path = Path(metadata.storage_path)
                if file_path.exists():
                    file_path.unlink()
                    deleted_count += 1

            self.db.delete(metadata)

        self.db.commit()
        logger.info(f"Cleaned up {deleted_count} old PDFs")

    def __del__(self):
        """Clean up HTTP client."""
        if hasattr(self, "client"):
            self.client.close()
