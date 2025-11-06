"""Align database schema with SQLAlchemy models

Revision ID: 003
Revises: 002
Create Date: 2025-11-05

Fixes BUG-001 Part 2: Schema mismatch between migrations and models
Root cause: Migration 001 created extra columns (orcid, deleted_at, created_by, updated_by)
that don't exist in the User model, causing potential issues with SQLAlchemy ORM operations.

This migration removes those extra columns to align the database schema exactly with
the User model definition.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove extra columns from users table to match User model."""

    # Check if the columns exist before attempting to drop them
    # This prevents errors if the migration runs on a database created after the fix
    from sqlalchemy import inspect

    # Get the connection from the operation context
    conn = op.get_bind()
    inspector = inspect(conn)

    # Check if 'users' table exists
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]

        # Remove orcid column (not in User model)
        if 'orcid' in columns:
            op.drop_column('users', 'orcid')

        # Remove deleted_at column (soft delete not implemented in User model)
        if 'deleted_at' in columns:
            op.drop_column('users', 'deleted_at')

        # Remove created_by column (audit trail not in User model)
        if 'created_by' in columns:
            op.drop_column('users', 'created_by')

        # Remove updated_by column (audit trail not in User model)
        if 'updated_by' in columns:
            op.drop_column('users', 'updated_by')


def downgrade() -> None:
    """Add the columns back (for rollback purposes)."""

    # Add columns back in reverse order
    op.add_column('users', sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('users', sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime, nullable=True))
    op.add_column('users', sa.Column('orcid', sa.String(50), unique=True, nullable=True))

    # Re-create indexes if needed
    op.create_index('ix_users_deleted_at', 'users', ['deleted_at'])
    op.create_index('ix_users_orcid', 'users', ['orcid'])
    op.create_index('ix_users_created_by', 'users', ['created_by'])
