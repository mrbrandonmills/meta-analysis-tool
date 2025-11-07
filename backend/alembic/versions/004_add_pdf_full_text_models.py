"""Add PDF and full-text analysis models

Revision ID: 004_add_pdf_full_text_models
Revises: 003_align_schema_with_models
Create Date: 2025-01-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_pdf_full_text_models'
down_revision = '003_align_schema_with_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add PDF metadata and full-text extraction tables."""

    # Create enum types
    op.execute("""
        CREATE TYPE pdfdownloadstatus AS ENUM (
            'pending', 'downloading', 'success', 'failed', 'not_available', 'paywall'
        )
    """)

    op.execute("""
        CREATE TYPE pdfsource AS ENUM (
            'pubmed_central', 'europe_pmc', 'arxiv', 'biorxiv', 'medrxiv',
            'unpaywall', 'doi_direct', 'manual_upload'
        )
    """)

    op.execute("""
        CREATE TYPE sectiontype AS ENUM (
            'title', 'abstract', 'introduction', 'background', 'methods',
            'results', 'discussion', 'conclusion', 'references',
            'acknowledgments', 'appendix', 'supplementary', 'unknown'
        )
    """)

    # Create pdf_metadata table
    op.create_table(
        'pdf_metadata',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('paper_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('download_status', postgresql.ENUM(name='pdfdownloadstatus'), nullable=False),
        sa.Column('pdf_source', postgresql.ENUM(name='pdfsource'), nullable=True),
        sa.Column('download_url', sa.Text(), nullable=True),
        sa.Column('download_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_download_attempt', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('storage_path', sa.Text(), nullable=True),
        sa.Column('storage_type', sa.String(length=50), nullable=False, server_default='local'),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('file_hash', sa.String(length=64), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('is_scanned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_ocr_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('extraction_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('extraction_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_extraction_attempt', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('retry_after', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('pdf_metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for pdf_metadata
    op.create_index('ix_pdf_metadata_paper_id', 'pdf_metadata', ['paper_id'])
    op.create_index('ix_pdf_metadata_download_status', 'pdf_metadata', ['download_status'])
    op.create_index('ix_pdf_metadata_pdf_source', 'pdf_metadata', ['pdf_source'])
    op.create_index('ix_pdf_metadata_file_hash', 'pdf_metadata', ['file_hash'])
    op.create_index('ix_pdf_metadata_extraction_status', 'pdf_metadata', ['extraction_status'])

    # Create full_text_extractions table
    op.create_table(
        'full_text_extractions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('pdf_metadata_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('full_text', sa.Text(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('sections', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('section_headings', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('tables_detected', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('figures_detected', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('references_count', sa.Integer(), nullable=True),
        sa.Column('extraction_quality', sa.Float(), nullable=True),
        sa.Column('has_extraction_errors', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('extraction_warnings', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('ocr_performed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('ocr_confidence', sa.Float(), nullable=True),
        sa.Column('statistics_found', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('outcome_measures', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('sample_size_mentions', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('study_design_mentions', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('intervention_mentions', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('population_mentions', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('extraction_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['pdf_metadata_id'], ['pdf_metadata.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('pdf_metadata_id')
    )

    # Create indexes for full_text_extractions
    op.create_index('ix_full_text_extractions_pdf_metadata_id', 'full_text_extractions', ['pdf_metadata_id'], unique=True)

    # Create full_text_screenings table
    op.create_table(
        'full_text_screenings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('full_text_extraction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('paper_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('decision', sa.String(length=50), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('inclusion_criteria_met', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('exclusion_criteria_violated', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('pico_extraction', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('study_quality_indicators', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('data_extraction_preview', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('needs_human_review', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('has_concerns', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('concern_details', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('screening_agent_id', sa.String(length=100), nullable=True),
        sa.Column('agent_version', sa.String(length=50), nullable=True),
        sa.Column('screening_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['full_text_extraction_id'], ['full_text_extractions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for full_text_screenings
    op.create_index('ix_full_text_screenings_full_text_extraction_id', 'full_text_screenings', ['full_text_extraction_id'])
    op.create_index('ix_full_text_screenings_paper_id', 'full_text_screenings', ['paper_id'])
    op.create_index('ix_full_text_screenings_decision', 'full_text_screenings', ['decision'])


def downgrade() -> None:
    """Remove PDF and full-text analysis tables."""

    # Drop tables
    op.drop_table('full_text_screenings')
    op.drop_table('full_text_extractions')
    op.drop_table('pdf_metadata')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS sectiontype')
    op.execute('DROP TYPE IF EXISTS pdfsource')
    op.execute('DROP TYPE IF EXISTS pdfdownloadstatus')
