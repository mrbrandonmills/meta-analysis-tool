"""PDF metadata and full-text extraction models."""

import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.paper import Paper


class PDFDownloadStatus(str, enum.Enum):
    """PDF download status enumeration."""

    PENDING = "pending"
    DOWNLOADING = "downloading"
    SUCCESS = "success"
    FAILED = "failed"
    NOT_AVAILABLE = "not_available"
    PAYWALL = "paywall"


class PDFSource(str, enum.Enum):
    """PDF source enumeration."""

    PUBMED_CENTRAL = "pubmed_central"
    EUROPE_PMC = "europe_pmc"
    ARXIV = "arxiv"
    BIORXIV = "biorxiv"
    MEDRXIV = "medrxiv"
    UNPAYWALL = "unpaywall"
    DOI_DIRECT = "doi_direct"
    MANUAL_UPLOAD = "manual_upload"


class PDFMetadata(Base, BaseModel):
    """PDF download and storage metadata.

    Tracks PDF download attempts, storage locations, and processing status.
    Enables deduplication and caching of downloaded PDFs.
    """

    __tablename__ = "pdf_metadata"

    # Foreign key to paper
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)

    # Download information
    download_status = Column(SQLEnum(PDFDownloadStatus), nullable=False, default=PDFDownloadStatus.PENDING, index=True)
    pdf_source = Column(SQLEnum(PDFSource), nullable=True, index=True)
    download_url = Column(Text, nullable=True)
    download_attempts = Column(Integer, default=0, nullable=False)
    last_download_attempt = Column(JSONB, nullable=True)  # Timestamp

    # Storage information
    storage_path = Column(Text, nullable=True)  # Local path or S3 key
    storage_type = Column(String(50), default="local", nullable=False)  # 'local', 's3', 'gcs'
    file_size_bytes = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True, index=True)  # SHA256 for deduplication

    # PDF properties
    page_count = Column(Integer, nullable=True)
    is_scanned = Column(Boolean, default=False, nullable=False)
    is_ocr_required = Column(Boolean, default=False, nullable=False)

    # Processing status
    extraction_status = Column(String(50), default="pending", nullable=False, index=True)  # pending, processing, completed, failed
    extraction_attempts = Column(Integer, default=0, nullable=False)
    last_extraction_attempt = Column(JSONB, nullable=True)

    # Error tracking
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)

    # Rate limiting
    retry_after = Column(JSONB, nullable=True)  # Timestamp when retry is allowed

    # Additional metadata
    pdf_metadata_json = Column(JSONB, nullable=True, default=dict)  # PDF document metadata

    # Relationships
    paper = relationship("Paper", back_populates="pdf_metadata", uselist=False)
    full_text_extraction = relationship("FullTextExtraction", back_populates="pdf_metadata", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PDFMetadata(id={self.id}, paper_id={self.paper_id}, status={self.download_status})>"


class SectionType(str, enum.Enum):
    """Document section type enumeration."""

    TITLE = "title"
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    BACKGROUND = "background"
    METHODS = "methods"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"
    ACKNOWLEDGMENTS = "acknowledgments"
    APPENDIX = "appendix"
    SUPPLEMENTARY = "supplementary"
    UNKNOWN = "unknown"


class FullTextExtraction(Base, BaseModel):
    """Extracted full-text content from PDF.

    Stores structured text extracted from PDF with section detection.
    Enables full-text search and detailed content analysis.
    """

    __tablename__ = "full_text_extractions"

    # Foreign key to PDF metadata
    pdf_metadata_id = Column(UUID(as_uuid=True), ForeignKey("pdf_metadata.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Extracted content
    full_text = Column(Text, nullable=False)  # Complete extracted text
    word_count = Column(Integer, nullable=True)

    # Structured sections
    sections = Column(JSONB, nullable=False, default=dict)  # {section_type: content}
    section_headings = Column(ARRAY(String), nullable=True)  # Detected headings

    # Extracted elements
    tables_detected = Column(Integer, default=0, nullable=False)
    figures_detected = Column(Integer, default=0, nullable=False)
    references_count = Column(Integer, nullable=True)

    # Text quality
    extraction_quality = Column(Float, nullable=True)  # 0.0-1.0 score
    has_extraction_errors = Column(Boolean, default=False, nullable=False)
    extraction_warnings = Column(ARRAY(String), nullable=True)

    # OCR information (if applicable)
    ocr_performed = Column(Boolean, default=False, nullable=False)
    ocr_confidence = Column(Float, nullable=True)  # Average OCR confidence

    # Statistics extraction (for meta-analysis)
    statistics_found = Column(JSONB, nullable=True, default=list)  # List of detected statistics
    outcome_measures = Column(ARRAY(String), nullable=True)
    sample_size_mentions = Column(ARRAY(String), nullable=True)

    # Study characteristics extraction
    study_design_mentions = Column(ARRAY(String), nullable=True)
    intervention_mentions = Column(ARRAY(String), nullable=True)
    population_mentions = Column(ARRAY(String), nullable=True)

    # Additional metadata
    extraction_metadata = Column(JSONB, nullable=True, default=dict)

    # Relationships
    pdf_metadata = relationship("PDFMetadata", back_populates="full_text_extraction")
    screening_results = relationship("FullTextScreening", back_populates="full_text_extraction", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation."""
        return f"<FullTextExtraction(id={self.id}, pdf_id={self.pdf_metadata_id}, words={self.word_count})>"


class FullTextScreening(Base, BaseModel):
    """Full-text screening results.

    Stores detailed screening decisions based on full-text analysis.
    Links to FullTextExtraction for audit trail.
    """

    __tablename__ = "full_text_screenings"

    # Foreign key to full-text extraction
    full_text_extraction_id = Column(UUID(as_uuid=True), ForeignKey("full_text_extractions.id", ondelete="CASCADE"), nullable=False, index=True)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)

    # Screening decision
    decision = Column(String(50), nullable=False, index=True)  # include, exclude, uncertain
    confidence = Column(Float, nullable=False)  # 0.0-1.0
    reasoning = Column(Text, nullable=False)

    # Criteria evaluation
    inclusion_criteria_met = Column(ARRAY(String), nullable=True)
    exclusion_criteria_violated = Column(ARRAY(String), nullable=True)

    # Detailed findings
    pico_extraction = Column(JSONB, nullable=True, default=dict)  # Population, Intervention, Comparison, Outcome
    study_quality_indicators = Column(JSONB, nullable=True, default=dict)
    data_extraction_preview = Column(JSONB, nullable=True, default=dict)

    # Flags
    needs_human_review = Column(Boolean, default=False, nullable=False)
    has_concerns = Column(Boolean, default=False, nullable=False)
    concern_details = Column(ARRAY(String), nullable=True)

    # Agent information
    screening_agent_id = Column(String(100), nullable=True)
    agent_version = Column(String(50), nullable=True)

    # Additional metadata
    screening_metadata = Column(JSONB, nullable=True, default=dict)

    # Relationships
    full_text_extraction = relationship("FullTextExtraction", back_populates="screening_results")
    paper = relationship("Paper", foreign_keys=[paper_id])

    def __repr__(self) -> str:
        """String representation."""
        return f"<FullTextScreening(id={self.id}, paper_id={self.paper_id}, decision={self.decision})>"
