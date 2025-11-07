"""Report model for storing generated meta-analysis reports."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class ReportFormat(str, enum.Enum):
    """Report format types."""
    DOCX = "docx"
    PDF = "pdf"
    BOTH = "both"


class ReportStatus(str, enum.Enum):
    """Report generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base):
    """Model for storing meta-analysis reports.

    Tracks generated reports with their metadata, custom sections,
    and file locations.
    """

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, nullable=False, index=True)  # Links to meta-analysis
    title = Column(String(500), nullable=False)

    # Report metadata
    format = Column(SQLEnum(ReportFormat), nullable=False, default=ReportFormat.DOCX)
    status = Column(SQLEnum(ReportStatus), nullable=False, default=ReportStatus.PENDING)

    # Authors and institution
    authors = Column(JSON, nullable=True)  # List of author names
    institution = Column(String(500), nullable=True)
    author_note = Column(Text, nullable=True)

    # Custom sections (optional overrides)
    custom_sections = Column(JSON, nullable=True)  # Dict of section_name: content

    # Keywords
    keywords = Column(JSON, nullable=True)  # List of keywords

    # File paths
    docx_path = Column(String(1000), nullable=True)
    pdf_path = Column(String(1000), nullable=True)

    # Report content metadata
    num_studies = Column(Integer, nullable=True)
    pooled_effect_size = Column(String(50), nullable=True)

    # Generation metadata
    generated_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # User who requested the report
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="reports")

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "title": self.title,
            "format": self.format.value if self.format else None,
            "status": self.status.value if self.status else None,
            "authors": self.authors,
            "institution": self.institution,
            "author_note": self.author_note,
            "custom_sections": self.custom_sections,
            "keywords": self.keywords,
            "docx_path": self.docx_path,
            "pdf_path": self.pdf_path,
            "num_studies": self.num_studies,
            "pooled_effect_size": self.pooled_effect_size,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
        }

    def __repr__(self) -> str:
        return f"<Report(id={self.id}, analysis_id={self.analysis_id}, status={self.status})>"


class ReportTemplate(Base):
    """Model for storing report templates.

    Templates allow users to customize report structure and content.
    """

    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Template configuration
    sections = Column(JSON, nullable=False)  # Dict of section configurations
    style_config = Column(JSON, nullable=True)  # Custom styling options

    # Template metadata
    is_public = Column(Integer, default=0)  # 0 = private, 1 = public
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User", back_populates="report_templates")

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "sections": self.sections,
            "style_config": self.style_config,
            "is_public": bool(self.is_public),
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<ReportTemplate(id={self.id}, name={self.name})>"
