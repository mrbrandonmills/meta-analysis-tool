"""Celery tasks for PDF download and text extraction.

Background tasks for:
- Batch PDF downloading
- Text extraction from PDFs
- Full-text screening
"""

from typing import List
from loguru import logger
from celery import group

from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.paper import Paper
from app.models.pdf_metadata import PDFMetadata, PDFDownloadStatus, FullTextExtraction
from app.services.pdf_download_service import PDFDownloadService
from app.services.pdf_text_extractor import PDFTextExtractor


@celery_app.task(name="pdf.download_single", bind=True, max_retries=3)
def download_pdf_task(self, paper_id: str):
    """Download PDF for a single paper.

    Args:
        paper_id: Paper ID to download PDF for

    Returns:
        Status dictionary
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting PDF download task for paper {paper_id}")

        # Get paper
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            logger.error(f"Paper {paper_id} not found")
            return {"status": "error", "message": "Paper not found"}

        # Initialize download service
        download_service = PDFDownloadService(db)

        # Download PDF
        success, metadata = download_service.download_pdf_for_paper(paper)

        if success:
            logger.info(f"Successfully downloaded PDF for paper {paper_id}")
            return {
                "status": "success",
                "paper_id": paper_id,
                "pdf_metadata_id": str(metadata.id),
                "source": metadata.pdf_source.value if metadata.pdf_source else None,
            }
        else:
            logger.warning(f"Failed to download PDF for paper {paper_id}")
            return {
                "status": "failed",
                "paper_id": paper_id,
                "download_status": metadata.download_status.value,
                "error": metadata.error_message,
            }

    except Exception as e:
        logger.error(f"Error in PDF download task: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    finally:
        db.close()


@celery_app.task(name="pdf.download_batch", bind=True)
def download_pdfs_batch_task(self, paper_ids: List[str], analysis_id: str):
    """Download PDFs for multiple papers in parallel.

    Args:
        paper_ids: List of paper IDs
        analysis_id: Meta-analysis ID

    Returns:
        Statistics dictionary
    """
    logger.info(f"Starting batch PDF download for {len(paper_ids)} papers")

    # Create parallel tasks
    job = group(download_pdf_task.s(paper_id) for paper_id in paper_ids)
    result = job.apply_async()

    # Wait for all tasks to complete
    results = result.get()

    # Aggregate statistics
    stats = {
        "total": len(results),
        "success": sum(1 for r in results if r.get("status") == "success"),
        "failed": sum(1 for r in results if r.get("status") == "failed"),
        "analysis_id": analysis_id,
    }

    logger.info(f"Batch PDF download complete: {stats}")
    return stats


@celery_app.task(name="pdf.extract_text_single", bind=True, max_retries=3)
def extract_text_task(self, pdf_metadata_id: str):
    """Extract text from a single PDF.

    Args:
        pdf_metadata_id: PDF metadata ID

    Returns:
        Status dictionary
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting text extraction task for PDF {pdf_metadata_id}")

        # Get PDF metadata
        pdf_metadata = (
            db.query(PDFMetadata)
            .filter(PDFMetadata.id == pdf_metadata_id)
            .first()
        )

        if not pdf_metadata:
            logger.error(f"PDF metadata {pdf_metadata_id} not found")
            return {"status": "error", "message": "PDF metadata not found"}

        # Initialize extractor
        extractor = PDFTextExtractor(db)

        # Extract text
        success, extraction = extractor.extract_text_from_pdf(pdf_metadata)

        if success:
            logger.info(f"Successfully extracted text from PDF {pdf_metadata_id}")
            return {
                "status": "success",
                "pdf_metadata_id": pdf_metadata_id,
                "extraction_id": str(extraction.id),
                "word_count": extraction.word_count,
            }
        else:
            logger.warning(f"Failed to extract text from PDF {pdf_metadata_id}")
            return {
                "status": "failed",
                "pdf_metadata_id": pdf_metadata_id,
                "requires_ocr": pdf_metadata.is_ocr_required,
            }

    except Exception as e:
        logger.error(f"Error in text extraction task: {str(e)}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

    finally:
        db.close()


@celery_app.task(name="pdf.extract_text_batch", bind=True)
def extract_text_batch_task(self, pdf_metadata_ids: List[str], analysis_id: str):
    """Extract text from multiple PDFs in parallel.

    Args:
        pdf_metadata_ids: List of PDF metadata IDs
        analysis_id: Meta-analysis ID

    Returns:
        Statistics dictionary
    """
    logger.info(f"Starting batch text extraction for {len(pdf_metadata_ids)} PDFs")

    # Create parallel tasks
    job = group(extract_text_task.s(pdf_id) for pdf_id in pdf_metadata_ids)
    result = job.apply_async()

    # Wait for all tasks to complete
    results = result.get()

    # Aggregate statistics
    stats = {
        "total": len(results),
        "success": sum(1 for r in results if r.get("status") == "success"),
        "failed": sum(1 for r in results if r.get("status") == "failed"),
        "requires_ocr": sum(1 for r in results if r.get("requires_ocr", False)),
        "analysis_id": analysis_id,
    }

    logger.info(f"Batch text extraction complete: {stats}")
    return stats


@celery_app.task(name="pdf.full_workflow", bind=True)
def full_pdf_workflow_task(self, paper_ids: List[str], analysis_id: str):
    """Complete PDF workflow: download -> extract -> ready for screening.

    Args:
        paper_ids: List of paper IDs
        analysis_id: Meta-analysis ID

    Returns:
        Workflow statistics
    """
    logger.info(f"Starting full PDF workflow for analysis {analysis_id}")

    # Step 1: Download PDFs
    download_result = download_pdfs_batch_task(paper_ids, analysis_id)
    logger.info(f"Download phase: {download_result}")

    # Step 2: Extract text from successful downloads
    db = SessionLocal()
    try:
        pdf_metadata_ids = (
            db.query(PDFMetadata.id)
            .join(Paper)
            .filter(
                Paper.id.in_(paper_ids),
                PDFMetadata.download_status == PDFDownloadStatus.SUCCESS,
            )
            .all()
        )
        pdf_metadata_ids = [str(id[0]) for id in pdf_metadata_ids]

        if pdf_metadata_ids:
            extraction_result = extract_text_batch_task(pdf_metadata_ids, analysis_id)
            logger.info(f"Extraction phase: {extraction_result}")
        else:
            extraction_result = {"total": 0, "success": 0, "failed": 0}

    finally:
        db.close()

    # Return combined statistics
    return {
        "analysis_id": analysis_id,
        "download": download_result,
        "extraction": extraction_result,
        "status": "completed",
    }


@celery_app.task(name="pdf.cleanup_old")
def cleanup_old_pdfs_task(days: int = 30):
    """Clean up old PDFs and metadata.

    Args:
        days: Number of days to keep PDFs

    Returns:
        Cleanup statistics
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting PDF cleanup task (older than {days} days)")

        download_service = PDFDownloadService(db)
        download_service.cleanup_old_pdfs(days=days)

        logger.info("PDF cleanup completed")
        return {"status": "success", "days": days}

    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        return {"status": "error", "message": str(e)}

    finally:
        db.close()


@celery_app.task(name="pdf.monitor_queue")
def monitor_pdf_queue_task():
    """Monitor PDF processing queue and report statistics.

    Returns:
        Queue statistics
    """
    db = SessionLocal()
    try:
        # Get queue statistics
        pending_downloads = (
            db.query(PDFMetadata)
            .filter(PDFMetadata.download_status == PDFDownloadStatus.PENDING)
            .count()
        )

        pending_extractions = (
            db.query(PDFMetadata)
            .filter(
                PDFMetadata.download_status == PDFDownloadStatus.SUCCESS,
                PDFMetadata.extraction_status == "pending",
            )
            .count()
        )

        completed = (
            db.query(PDFMetadata)
            .filter(PDFMetadata.extraction_status == "completed")
            .count()
        )

        stats = {
            "pending_downloads": pending_downloads,
            "pending_extractions": pending_extractions,
            "completed": completed,
            "timestamp": "now",
        }

        logger.info(f"PDF queue stats: {stats}")
        return stats

    finally:
        db.close()
