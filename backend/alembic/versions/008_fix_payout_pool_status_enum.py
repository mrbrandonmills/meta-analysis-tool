"""Fix payout_pools status column to use proper ENUM type

Revision ID: 008_fix_payout_pool_status_enum
Revises: 007_add_research_direction
Create Date: 2025-11-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_fix_payout_pool_status_enum'
down_revision = '007_add_research_direction'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Convert payout_pools.status from VARCHAR to native PostgreSQL ENUM."""

    # Create the enum type if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payoutpoolstatus') THEN
                CREATE TYPE payoutpoolstatus AS ENUM ('open', 'calculating', 'distributed', 'closed', 'rolled_over');
            END IF;
        END$$;
    """)

    # Drop the default value first (can't cast default automatically)
    op.execute("ALTER TABLE payout_pools ALTER COLUMN status DROP DEFAULT")

    # Convert the column to use the enum type
    op.execute("""
        ALTER TABLE payout_pools
            ALTER COLUMN status TYPE payoutpoolstatus
            USING status::payoutpoolstatus
    """)

    # Re-add the default value using the enum type
    op.execute("ALTER TABLE payout_pools ALTER COLUMN status SET DEFAULT 'open'::payoutpoolstatus")


def downgrade() -> None:
    """Revert payout_pools.status from ENUM back to VARCHAR."""

    # Drop the default first
    op.execute("ALTER TABLE payout_pools ALTER COLUMN status DROP DEFAULT")

    # Convert back to VARCHAR
    op.execute("""
        ALTER TABLE payout_pools
            ALTER COLUMN status TYPE VARCHAR(50)
            USING status::text
    """)

    # Re-add the default value as a string
    op.execute("ALTER TABLE payout_pools ALTER COLUMN status SET DEFAULT 'open'")

    # Drop the enum type
    op.execute("DROP TYPE IF EXISTS payoutpoolstatus")
