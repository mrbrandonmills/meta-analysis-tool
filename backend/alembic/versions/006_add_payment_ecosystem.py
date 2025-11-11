"""Add payment ecosystem tables

Revision ID: 006_add_payment_ecosystem
Revises: 005_add_report_tables
Create Date: 2025-11-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_add_payment_ecosystem'
down_revision = '005_add_report_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create payment ecosystem tables and modify existing tables."""

    # Step 1: Modify existing tables - Add payment fields to users
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('is_paying_member', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('member_since', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('subscription_status', sa.String(length=50), nullable=True))
    op.create_index('ix_users_stripe_customer_id', 'users', ['stripe_customer_id'])
    op.create_unique_constraint('uq_users_stripe_customer_id', 'users', ['stripe_customer_id'])

    # Step 2: Modify existing tables - Add payout fields to researchers
    op.add_column('researchers', sa.Column('stripe_connect_account_id', sa.String(length=255), nullable=True))
    op.add_column('researchers', sa.Column('connect_account_status', sa.String(length=50), nullable=False, server_default='not_connected'))
    op.add_column('researchers', sa.Column('bank_account_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('researchers', sa.Column('total_earnings_cents', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('researchers', sa.Column('lifetime_reviews_paid', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('researchers', sa.Column('last_payout_date', sa.Date(), nullable=True))
    op.create_index('ix_researchers_stripe_connect_account_id', 'researchers', ['stripe_connect_account_id'])
    op.create_unique_constraint('uq_researchers_stripe_connect_account_id', 'researchers', ['stripe_connect_account_id'])
    op.create_index('ix_researchers_connect_account_status', 'researchers', ['connect_account_status'])

    # Step 3: Modify existing tables - Add approval fields to peer_reviews
    op.add_column('peer_reviews', sa.Column('editor_approved', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('peer_reviews', sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('peer_reviews', sa.Column('approved_at', sa.DateTime(), nullable=True))
    op.add_column('peer_reviews', sa.Column('approval_notes', sa.Text(), nullable=True))
    op.add_column('peer_reviews', sa.Column('eligible_for_payout', sa.Boolean(), nullable=False, server_default='true'))
    op.create_index('ix_peer_reviews_editor_approved', 'peer_reviews', ['editor_approved'])
    op.create_index('ix_peer_reviews_approved_at', 'peer_reviews', ['approved_at'])
    op.create_foreign_key('fk_peer_reviews_approved_by_users', 'peer_reviews', 'users', ['approved_by'], ['id'])

    # Step 4: Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=False),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=False),
        sa.Column('stripe_payment_method_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('plan_type', sa.String(length=50), nullable=False),
        sa.Column('monthly_amount_cents', sa.Integer(), nullable=False, server_default='10000'),
        sa.Column('payout_contribution_cents', sa.Integer(), nullable=False, server_default='2000'),
        sa.Column('current_period_start', sa.DateTime(), nullable=False),
        sa.Column('current_period_end', sa.DateTime(), nullable=False),
        sa.Column('trial_end', sa.DateTime(), nullable=True),
        sa.Column('billing_cycle_anchor', sa.DateTime(), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('canceled_at', sa.DateTime(), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_subscription_id')
    )
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'])
    op.create_index('ix_subscriptions_status', 'subscriptions', ['status'])
    op.create_index('ix_subscriptions_stripe_customer_id', 'subscriptions', ['stripe_customer_id'])
    op.create_index('ix_subscriptions_stripe_subscription_id', 'subscriptions', ['stripe_subscription_id'])
    op.create_index('ix_subscriptions_created_at', 'subscriptions', ['created_at'])
    op.create_index('ix_subscriptions_deleted_at', 'subscriptions', ['deleted_at'])

    # Step 5: Create payout_pools table
    op.create_table(
        'payout_pools',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pool_month', sa.Date(), nullable=False),
        sa.Column('total_contributions_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_distributed_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('remaining_cents', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_reviews_assigned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_reviews_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_reviews_approved', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('payout_per_review_cents', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='open'),
        sa.Column('calculated_at', sa.DateTime(), nullable=True),
        sa.Column('distributed_at', sa.DateTime(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('pool_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('pool_month')
    )
    op.create_index('ix_payout_pools_pool_month', 'payout_pools', ['pool_month'])
    op.create_index('ix_payout_pools_status', 'payout_pools', ['status'])
    op.create_index('ix_payout_pools_created_at', 'payout_pools', ['created_at'])
    op.create_index('ix_payout_pools_deleted_at', 'payout_pools', ['deleted_at'])

    # Step 6: Create payout_contributions table
    op.create_table(
        'payout_contributions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pool_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contribution_amount_cents', sa.Integer(), nullable=False, server_default='2000'),
        sa.Column('billing_date', sa.DateTime(), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_invoice_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['pool_id'], ['payout_pools.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payout_contributions_pool_id', 'payout_contributions', ['pool_id'])
    op.create_index('ix_payout_contributions_user_id', 'payout_contributions', ['user_id'])
    op.create_index('ix_payout_contributions_subscription_id', 'payout_contributions', ['subscription_id'])
    op.create_index('ix_payout_contributions_status', 'payout_contributions', ['status'])
    op.create_index('ix_payout_contributions_created_at', 'payout_contributions', ['created_at'])
    op.create_index('ix_payout_contributions_deleted_at', 'payout_contributions', ['deleted_at'])

    # Step 7: Create review_completions table
    op.create_table(
        'review_completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pool_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('peer_review_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('manuscript_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('editor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('completeness_score', sa.Float(), nullable=True),
        sa.Column('constructiveness_score', sa.Float(), nullable=True),
        sa.Column('eligible_for_payout', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('ineligibility_reason', sa.Text(), nullable=True),
        sa.Column('payout_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('payout_amount_cents', sa.Integer(), nullable=True),
        sa.Column('distributed_at', sa.DateTime(), nullable=True),
        sa.Column('completion_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['pool_id'], ['payout_pools.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['peer_review_id'], ['peer_reviews.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['researchers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['manuscript_id'], ['manuscripts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['editor_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('peer_review_id')
    )
    op.create_index('ix_review_completions_pool_id', 'review_completions', ['pool_id'])
    op.create_index('ix_review_completions_reviewer_id', 'review_completions', ['reviewer_id'])
    op.create_index('ix_review_completions_payout_status', 'review_completions', ['payout_status'])
    op.create_index('ix_review_completions_approved_at', 'review_completions', ['approved_at'])
    op.create_index('ix_review_completions_peer_review_id', 'review_completions', ['peer_review_id'])
    op.create_index('ix_review_completions_created_at', 'review_completions', ['created_at'])
    op.create_index('ix_review_completions_deleted_at', 'review_completions', ['deleted_at'])

    # Step 8: Create payout_distributions table
    op.create_table(
        'payout_distributions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pool_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approved_reviews_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('payout_per_review_cents', sa.Integer(), nullable=False),
        sa.Column('total_payout_cents', sa.Integer(), nullable=False),
        sa.Column('stripe_connect_account_id', sa.String(length=255), nullable=False),
        sa.Column('stripe_transfer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_payout_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('transfer_initiated_at', sa.DateTime(), nullable=True),
        sa.Column('transfer_completed_at', sa.DateTime(), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('destination_bank_last4', sa.String(length=4), nullable=True),
        sa.Column('destination_bank_name', sa.String(length=255), nullable=True),
        sa.Column('estimated_arrival_date', sa.Date(), nullable=True),
        sa.Column('notification_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notification_sent_at', sa.DateTime(), nullable=True),
        sa.Column('distribution_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['pool_id'], ['payout_pools.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['researchers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_transfer_id'),
        sa.CheckConstraint('total_payout_cents >= 0', name='positive_payout'),
        sa.CheckConstraint('approved_reviews_count >= 0', name='positive_reviews')
    )
    op.create_index('ix_payout_distributions_pool_id', 'payout_distributions', ['pool_id'])
    op.create_index('ix_payout_distributions_reviewer_id', 'payout_distributions', ['reviewer_id'])
    op.create_index('ix_payout_distributions_status', 'payout_distributions', ['status'])
    op.create_index('ix_payout_distributions_stripe_transfer_id', 'payout_distributions', ['stripe_transfer_id'])
    op.create_index('ix_payout_distributions_created_at', 'payout_distributions', ['created_at'])
    op.create_index('ix_payout_distributions_deleted_at', 'payout_distributions', ['deleted_at'])

    # Step 9: Seed initial payout pool for current month
    # Note: This will be done programmatically on first subscription creation


def downgrade() -> None:
    """Drop payment ecosystem tables and columns."""

    # Drop tables in reverse order
    op.drop_table('payout_distributions')
    op.drop_table('review_completions')
    op.drop_table('payout_contributions')
    op.drop_table('payout_pools')
    op.drop_table('subscriptions')

    # Drop peer_reviews columns
    op.drop_constraint('fk_peer_reviews_approved_by_users', 'peer_reviews', type_='foreignkey')
    op.drop_index('ix_peer_reviews_approved_at', table_name='peer_reviews')
    op.drop_index('ix_peer_reviews_editor_approved', table_name='peer_reviews')
    op.drop_column('peer_reviews', 'eligible_for_payout')
    op.drop_column('peer_reviews', 'approval_notes')
    op.drop_column('peer_reviews', 'approved_at')
    op.drop_column('peer_reviews', 'approved_by')
    op.drop_column('peer_reviews', 'editor_approved')

    # Drop researchers columns
    op.drop_index('ix_researchers_connect_account_status', table_name='researchers')
    op.drop_constraint('uq_researchers_stripe_connect_account_id', 'researchers', type_='unique')
    op.drop_index('ix_researchers_stripe_connect_account_id', table_name='researchers')
    op.drop_column('researchers', 'last_payout_date')
    op.drop_column('researchers', 'lifetime_reviews_paid')
    op.drop_column('researchers', 'total_earnings_cents')
    op.drop_column('researchers', 'bank_account_verified')
    op.drop_column('researchers', 'connect_account_status')
    op.drop_column('researchers', 'stripe_connect_account_id')

    # Drop users columns
    op.drop_constraint('uq_users_stripe_customer_id', 'users', type_='unique')
    op.drop_index('ix_users_stripe_customer_id', table_name='users')
    op.drop_column('users', 'subscription_status')
    op.drop_column('users', 'member_since')
    op.drop_column('users', 'is_paying_member')
    op.drop_column('users', 'stripe_customer_id')
