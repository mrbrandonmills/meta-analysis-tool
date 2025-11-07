"""add_meta_analysis_tables

Revision ID: 004
Revises: 003
Create Date: 2025-11-06 12:00:00.000000

This migration adds tables for persistent meta-analysis state management:
- meta_analyses: Core meta-analysis metadata and configuration
- coordinator_states: Coordinator agent state for recovery and scaling
- agent_executions: Audit trail of all agent executions

This enables:
1. State persistence across server restarts
2. Horizontal scaling with multiple Uvicorn workers
3. Full audit trail and debugging capability
4. Crash recovery and state reconstruction
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create meta-analysis persistence tables."""

    # Create meta_analysis_status enum
    op.execute("""
        CREATE TYPE meta_analysis_status AS ENUM (
            'created',
            'workflow_created',
            'in_progress',
            'searching',
            'screening',
            'quality_assessment',
            'data_extraction',
            'analysis',
            'completed',
            'failed',
            'cancelled'
        )
    """)

    # Create meta_analyses table
    op.create_table(
        'meta_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('research_question', sa.Text(), nullable=False),
        sa.Column('topic', sa.String(length=500), nullable=False),
        sa.Column('inclusion_criteria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('exclusion_criteria', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('databases', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('peer_review_only', sa.String(length=50), nullable=True, server_default='false'),
        sa.Column('expert_name', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Enum(
            'created', 'workflow_created', 'in_progress', 'searching', 'screening',
            'quality_assessment', 'data_extraction', 'analysis', 'completed', 'failed', 'cancelled',
            name='meta_analysis_status', native_enum=False
        ), nullable=False, server_default='created'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for meta_analyses
    op.create_index('ix_meta_analyses_user_id', 'meta_analyses', ['user_id'])
    op.create_index('ix_meta_analyses_topic', 'meta_analyses', ['topic'])
    op.create_index('ix_meta_analyses_status', 'meta_analyses', ['status'])
    op.create_index('ix_meta_analyses_created_at', 'meta_analyses', ['created_at'])

    # Create coordinator_states table
    op.create_table(
        'coordinator_states',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_state', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('decisions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('workflow_plan', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('coordinator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=True, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['analysis_id'], ['meta_analyses.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('analysis_id'),
    )

    # Create indexes for coordinator_states
    op.create_index('ix_coordinator_states_analysis_id', 'coordinator_states', ['analysis_id'], unique=True)

    # Create agent_executions table
    op.create_table(
        'agent_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_name', sa.String(length=100), nullable=False),
        sa.Column('agent_role', sa.String(length=50), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('execution_time_ms', sa.String(length=50), nullable=True),
        sa.Column('tokens_used', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='success'),
        sa.Column('executed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['analysis_id'], ['meta_analyses.id'], ondelete='CASCADE'),
    )

    # Create indexes for agent_executions
    op.create_index('ix_agent_executions_analysis_id', 'agent_executions', ['analysis_id'])
    op.create_index('ix_agent_executions_agent_name', 'agent_executions', ['agent_name'])
    op.create_index('ix_agent_executions_agent_role', 'agent_executions', ['agent_role'])
    op.create_index('ix_agent_executions_status', 'agent_executions', ['status'])
    op.create_index('ix_agent_executions_executed_at', 'agent_executions', ['executed_at'])

    # Create composite index for querying executions by analysis and time
    op.create_index(
        'ix_agent_executions_analysis_time',
        'agent_executions',
        ['analysis_id', 'executed_at']
    )


def downgrade() -> None:
    """Drop meta-analysis persistence tables."""

    # Drop indexes
    op.drop_index('ix_agent_executions_analysis_time', table_name='agent_executions')
    op.drop_index('ix_agent_executions_executed_at', table_name='agent_executions')
    op.drop_index('ix_agent_executions_status', table_name='agent_executions')
    op.drop_index('ix_agent_executions_agent_role', table_name='agent_executions')
    op.drop_index('ix_agent_executions_agent_name', table_name='agent_executions')
    op.drop_index('ix_agent_executions_analysis_id', table_name='agent_executions')

    op.drop_index('ix_coordinator_states_analysis_id', table_name='coordinator_states')

    op.drop_index('ix_meta_analyses_created_at', table_name='meta_analyses')
    op.drop_index('ix_meta_analyses_status', table_name='meta_analyses')
    op.drop_index('ix_meta_analyses_topic', table_name='meta_analyses')
    op.drop_index('ix_meta_analyses_user_id', table_name='meta_analyses')

    # Drop tables
    op.drop_table('agent_executions')
    op.drop_table('coordinator_states')
    op.drop_table('meta_analyses')

    # Drop enum type
    op.execute('DROP TYPE meta_analysis_status')
