"""add research direction table

Revision ID: 007_add_research_direction
Revises: 006_add_payment_ecosystem
Create Date: 2025-11-11 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '007_add_research_direction'
down_revision: Union[str, None] = '006_add_payment_ecosystem'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create research_directions table."""

    op.create_table(
        'research_directions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),

        # Foreign keys
        sa.Column('meta_analysis_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),

        # Analysis configuration
        sa.Column('focus_areas', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('max_proposals', sa.String(length=50), nullable=True),
        sa.Column('include_literature_review', sa.String(length=50), nullable=True),

        # Analysis results (JSONB for flexibility)
        sa.Column('gaps_identified', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('research_questions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('research_proposals', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('priority_ranking', postgresql.JSONB(astext_type=sa.Text()), nullable=True),

        # Quality metrics
        sa.Column('completeness_score', sa.Float(), nullable=True),
        sa.Column('num_gaps', sa.String(length=50), nullable=True),
        sa.Column('num_questions', sa.String(length=50), nullable=True),
        sa.Column('num_proposals', sa.String(length=50), nullable=True),

        # Processing metadata
        sa.Column('processing_time_seconds', sa.Float(), nullable=True),
        sa.Column('model_version', sa.String(length=100), nullable=True),
        sa.Column('agent_version', sa.String(length=50), nullable=True),

        # Export tracking
        sa.Column('exported_formats', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('last_exported_at', sa.String(length=100), nullable=True),

        # Additional metadata
        sa.Column('analysis_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),

        # Primary key
        sa.PrimaryKeyConstraint('id'),

        # Foreign key constraints
        sa.ForeignKeyConstraint(
            ['meta_analysis_id'],
            ['meta_analyses.id'],
            name='fk_research_directions_meta_analysis_id',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            name='fk_research_directions_user_id',
            ondelete='CASCADE'
        ),
    )

    # Create indexes for performance
    op.create_index(
        'ix_research_directions_meta_analysis_id',
        'research_directions',
        ['meta_analysis_id'],
        unique=False
    )
    op.create_index(
        'ix_research_directions_user_id',
        'research_directions',
        ['user_id'],
        unique=False
    )
    op.create_index(
        'ix_research_directions_created_at',
        'research_directions',
        ['created_at'],
        unique=False
    )

    # Add comment to table
    op.execute(
        """
        COMMENT ON TABLE research_directions IS
        'Stores research direction analyses generated from meta-analysis results. Each record contains identified gaps, research questions, and detailed proposals for future research.'
        """
    )


def downgrade() -> None:
    """Drop research_directions table."""

    # Drop indexes
    op.drop_index('ix_research_directions_created_at', table_name='research_directions')
    op.drop_index('ix_research_directions_user_id', table_name='research_directions')
    op.drop_index('ix_research_directions_meta_analysis_id', table_name='research_directions')

    # Drop table
    op.drop_table('research_directions')
