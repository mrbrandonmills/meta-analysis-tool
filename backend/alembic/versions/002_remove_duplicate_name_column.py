"""Remove duplicate name column from users table

Revision ID: 002
Revises: 001
Create Date: 2025-11-05

Fixes BUG-001: User registration 500 error
Root cause: Migration 001 created both 'name' and 'full_name' columns in users table,
but the User model only defines 'full_name'. This mismatch caused SQLAlchemy to fail
when inserting new users.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Remove the duplicate 'name' column from users table."""

    # Check if the column exists before attempting to drop it
    # This prevents errors if the migration runs on a database created after the fix
    from sqlalchemy import inspect
    from sqlalchemy.engine import reflection

    # Get the connection from the operation context
    conn = op.get_bind()
    inspector = inspect(conn)

    # Check if 'users' table exists and has 'name' column
    if 'users' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('users')]
        if 'name' in columns:
            op.drop_column('users', 'name')
        # If column doesn't exist, this migration is a no-op (already fixed)


def downgrade() -> None:
    """Add the 'name' column back (for rollback purposes)."""

    op.add_column('users', sa.Column('name', sa.String(255), nullable=True))
