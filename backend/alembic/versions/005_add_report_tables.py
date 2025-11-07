"""Add report and report_template tables

Revision ID: 005_add_report_tables
Revises: 004_add_meta_analysis_tables
Create Date: 2024-11-06 14:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_report_tables'
down_revision = '004_add_meta_analysis_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create reports and report_templates tables."""

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('format', sa.String(length=10), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('authors', sa.JSON(), nullable=True),
        sa.Column('institution', sa.String(length=500), nullable=True),
        sa.Column('author_note', sa.Text(), nullable=True),
        sa.Column('custom_sections', sa.JSON(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('docx_path', sa.String(length=1000), nullable=True),
        sa.Column('pdf_path', sa.String(length=1000), nullable=True),
        sa.Column('num_studies', sa.Integer(), nullable=True),
        sa.Column('pooled_effect_size', sa.String(length=50), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_reports_analysis_id', 'reports', ['analysis_id'])
    op.create_index('ix_reports_status', 'reports', ['status'])
    op.create_index('ix_reports_user_id', 'reports', ['user_id'])

    # Create report_templates table
    op.create_table(
        'report_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sections', sa.JSON(), nullable=False),
        sa.Column('style_config', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create indexes
    op.create_index('ix_report_templates_name', 'report_templates', ['name'])
    op.create_index('ix_report_templates_is_public', 'report_templates', ['is_public'])
    op.create_index('ix_report_templates_created_by', 'report_templates', ['created_by'])


def downgrade() -> None:
    """Drop reports and report_templates tables."""

    # Drop indexes first
    op.drop_index('ix_report_templates_created_by', table_name='report_templates')
    op.drop_index('ix_report_templates_is_public', table_name='report_templates')
    op.drop_index('ix_report_templates_name', table_name='report_templates')
    op.drop_index('ix_reports_user_id', table_name='reports')
    op.drop_index('ix_reports_status', table_name='reports')
    op.drop_index('ix_reports_analysis_id', table_name='reports')

    # Drop tables
    op.drop_table('report_templates')
    op.drop_table('reports')
