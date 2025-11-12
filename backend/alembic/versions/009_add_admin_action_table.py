"""Add AdminAction table for audit trail

Revision ID: 009_add_admin_action_table
Revises: 008_fix_payout_pool_status_enum
Create Date: 2025-11-12 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_add_admin_action_table'
down_revision = '008_fix_payout_pool_status_enum'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add admin_actions table for comprehensive audit logging."""

    # Create the admin_action_type enum
    op.execute("""
        CREATE TYPE admin_action_type AS ENUM (
            'user_created', 'user_updated', 'user_suspended', 'user_activated', 'user_deleted',
            'researcher_updated', 'researcher_suspended', 'researcher_activated',
            'payout_pool_created', 'payout_distributed', 'payout_pool_closed',
            'subscription_cancelled', 'subscription_refunded',
            'content_moderated', 'review_approved', 'review_rejected',
            'system_config_changed', 'permissions_changed'
        )
    """)

    # Create the admin_actions table
    op.create_table(
        'admin_actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),

        # Who performed the action
        sa.Column('admin_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('admin_email', sa.String(length=255), nullable=False),

        # What action was performed
        sa.Column('action_type', postgresql.ENUM(name='admin_action_type', create_type=False), nullable=False, index=True),

        # What entity was affected
        sa.Column('target_type', sa.String(length=50), nullable=True, index=True),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('target_identifier', sa.String(length=255), nullable=True),

        # Action details
        sa.Column('description', sa.Text(), nullable=False),

        # Previous and new values (for updates)
        sa.Column('previous_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),

        # Additional metadata
        sa.Column('action_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),

        # Request context
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),

        # Timestamp
        sa.Column('performed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), index=True),
    )

    # Create composite indexes for common query patterns
    op.create_index(
        'idx_admin_actions_admin_performed',
        'admin_actions',
        ['admin_id', 'performed_at']
    )

    op.create_index(
        'idx_admin_actions_target_type_id',
        'admin_actions',
        ['target_type', 'target_id']
    )

    op.create_index(
        'idx_admin_actions_action_performed',
        'admin_actions',
        ['action_type', 'performed_at']
    )


def downgrade() -> None:
    """Remove admin_actions table and enum type."""

    # Drop indexes first
    op.drop_index('idx_admin_actions_action_performed', table_name='admin_actions')
    op.drop_index('idx_admin_actions_target_type_id', table_name='admin_actions')
    op.drop_index('idx_admin_actions_admin_performed', table_name='admin_actions')

    # Drop the table
    op.drop_table('admin_actions')

    # Drop the enum type
    op.execute('DROP TYPE admin_action_type')
