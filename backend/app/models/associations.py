"""Association/junction tables for many-to-many relationships."""

from sqlalchemy import Table, Column, ForeignKey, Integer, Float, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.db.base import Base

# Project <-> Paper association
project_papers = Table(
    "project_papers",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("project_id", UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("paper_id", UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
    Column("role", String(50), nullable=True),  # e.g., "included", "excluded", "reference"
    Column("metadata", UUID, nullable=True),  # JSONB for additional data
)

# Project <-> Researcher association
project_researchers = Table(
    "project_researchers",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("project_id", UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("researcher_id", UUID(as_uuid=True), ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
    Column("role", String(50), nullable=True),  # e.g., "reviewer", "expert", "collaborator"
    Column("relevance_score", Float, nullable=True),
)

# Paper <-> Researcher (authorship) association
paper_authors = Table(
    "paper_authors",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("paper_id", UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("researcher_id", UUID(as_uuid=True), ForeignKey("researchers.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("author_position", Integer, nullable=True),  # 1 = first author, -1 = last author, etc.
    Column("is_corresponding", UUID, default=False, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)
