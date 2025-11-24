"""Add tier application system with 3-tier qualification structure

Revision ID: 010_add_tier_application_system
Revises: 009_add_admin_action_table
Create Date: 2025-11-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010_add_tier_application_system'
down_revision = '009_add_admin_action_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add tier application tables and update users table."""

    # ===========================
    # 1. Add new fields to users table
    # ===========================

    # Add first_name and last_name fields
    op.add_column('users', sa.Column('first_name', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=255), nullable=True))

    # Create user_tier_enum type
    op.execute("""
        CREATE TYPE user_tier_enum AS ENUM (
            'tier_1_researcher',
            'tier_2_reviewer',
            'tier_3_editor'
        )
    """)

    # Add tier field to users table
    op.add_column(
        'users',
        sa.Column(
            'tier',
            postgresql.ENUM('tier_1_researcher', 'tier_2_reviewer', 'tier_3_editor', name='user_tier_enum', create_type=False),
            nullable=False,
            server_default='tier_1_researcher'
        )
    )

    # Create index on tier field
    op.create_index('idx_users_tier', 'users', ['tier'])

    # ===========================
    # 2. Create tier application enums
    # ===========================

    # Application tier enum
    op.execute("""
        CREATE TYPE application_tier_enum AS ENUM (
            'tier_2_reviewer',
            'tier_3_editor'
        )
    """)

    # Application status enum
    op.execute("""
        CREATE TYPE application_status_enum AS ENUM (
            'submitted',
            'auto_verification_in_progress',
            'auto_verification_passed',
            'auto_verification_failed',
            'manual_review_pending',
            'manual_review_in_progress',
            'references_check_in_progress',
            'advisory_board_review',
            'more_info_requested',
            'approved',
            'denied',
            'appealed',
            'appeal_approved',
            'appeal_denied'
        )
    """)

    # Editorial experience type enum
    op.execute("""
        CREATE TYPE editorial_experience_type_enum AS ENUM (
            'board',
            'recommendations',
            'guest_editor'
        )
    """)

    # ===========================
    # 3. Create tier_applications table
    # ===========================

    op.create_table(
        'tier_applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),

        # Application type and status
        sa.Column('tier_applied_for', postgresql.ENUM(name='application_tier_enum', create_type=False), nullable=False, index=True),
        sa.Column('status', postgresql.ENUM(name='application_status_enum', create_type=False), nullable=False, server_default='submitted', index=True),

        # Academic credentials
        sa.Column('degree_type', sa.String(length=50), nullable=False),
        sa.Column('degree_institution', sa.String(length=255), nullable=False),
        sa.Column('degree_field', sa.String(length=255), nullable=False),
        sa.Column('degree_year', sa.Integer(), nullable=False),

        # Verification identifiers
        sa.Column('orcid_id', sa.String(length=19), nullable=False, index=True),
        sa.Column('google_scholar_url', sa.Text(), nullable=False),
        sa.Column('publication_dois', postgresql.ARRAY(sa.Text()), nullable=False),

        # Verification status
        sa.Column('orcid_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('google_scholar_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('auto_verification_passed', sa.Boolean(), nullable=True),

        # Verification results
        sa.Column('h_index', sa.Integer(), nullable=True),
        sa.Column('total_citations', sa.Integer(), nullable=True),
        sa.Column('total_publications', sa.Integer(), nullable=True),

        # Peer review experience
        sa.Column('total_reviews_completed', sa.Integer(), nullable=False),
        sa.Column('journals_reviewed_for', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('max_concurrent_reviews', sa.Integer(), nullable=False),
        sa.Column('preferred_review_timeframe_days', sa.Integer(), nullable=False),
        sa.Column('review_languages', postgresql.ARRAY(sa.String(length=50)), nullable=False),

        # Research expertise
        sa.Column('expertise_domains', postgresql.ARRAY(sa.String(length=255)), nullable=False),
        sa.Column('expertise_keywords', postgresql.ARRAY(sa.String(length=100)), nullable=False),
        sa.Column('research_methodologies', postgresql.ARRAY(sa.String(length=255)), nullable=False),

        # Ethics
        sa.Column('conflicts_of_interest_disclosed', sa.Boolean(), nullable=False),
        sa.Column('conflict_details', sa.Text(), nullable=True),
        sa.Column('research_misconduct_question', sa.Boolean(), nullable=False),
        sa.Column('misconduct_details', sa.Text(), nullable=True),
        sa.Column('cope_guidelines_accepted', sa.Boolean(), nullable=False),

        # Optional Publons
        sa.Column('publons_profile_url', sa.Text(), nullable=True),

        # Tier 3 specific fields
        sa.Column('editorial_experience_type', postgresql.ENUM(name='editorial_experience_type_enum', create_type=False), nullable=True),
        sa.Column('editorial_board_journal', sa.String(length=255), nullable=True),
        sa.Column('editorial_board_role', sa.String(length=255), nullable=True),
        sa.Column('editorial_board_years', sa.String(length=50), nullable=True),
        sa.Column('guest_editor_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('conflict_management_essay', sa.Text(), nullable=True),
        sa.Column('editorial_philosophy_essay', sa.Text(), nullable=True),
        sa.Column('professional_references', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('weekly_hours_available', sa.Integer(), nullable=True),

        # File uploads
        sa.Column('cv_file_path', sa.Text(), nullable=True),
        sa.Column('degree_certificate_path', sa.Text(), nullable=True),
        sa.Column('recommendation_letters_paths', postgresql.ARRAY(sa.Text()), nullable=True),

        # Decision information
        sa.Column('approved', sa.Boolean(), nullable=True),
        sa.Column('denial_reasons', postgresql.ARRAY(sa.String(length=100)), nullable=True),
        sa.Column('denial_explanation', sa.Text(), nullable=True),

        # More info requested
        sa.Column('requested_info', postgresql.ARRAY(sa.Text()), nullable=True),

        # Probationary approval
        sa.Column('probationary_approval', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('probation_end_date', sa.DateTime(), nullable=True),

        # Appeal
        sa.Column('appeal_submitted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('appeal_reason', sa.Text(), nullable=True),
        sa.Column('appeal_additional_evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('appeal_submitted_at', sa.DateTime(), nullable=True),
        sa.Column('appeal_decided_at', sa.DateTime(), nullable=True),
        sa.Column('appeal_denial_explanation', sa.Text(), nullable=True),

        # Admin review
        sa.Column('reviewed_by_admin_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('appeal_reviewed_by_admin_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),

        # Reference checks
        sa.Column('references_contacted_at', sa.DateTime(), nullable=True),
        sa.Column('references_responses', postgresql.JSONB(astext_type=sa.Text()), nullable=True),

        # Timestamps
        sa.Column('submitted_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, index=True),
        sa.Column('decision_made_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )

    # Create composite indexes for common query patterns
    op.create_index(
        'idx_tier_applications_user_status',
        'tier_applications',
        ['user_id', 'status']
    )

    op.create_index(
        'idx_tier_applications_tier_status',
        'tier_applications',
        ['tier_applied_for', 'status']
    )

    op.create_index(
        'idx_tier_applications_submitted',
        'tier_applications',
        ['submitted_at']
    )

    # ===========================
    # 4. Create qualification_verifications table
    # ===========================

    op.create_table(
        'qualification_verifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('application_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tier_applications.id'), nullable=False, unique=True, index=True),

        # Verification status
        sa.Column('verification_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verification_date', sa.DateTime(), nullable=True),
        sa.Column('verification_passed', sa.Boolean(), nullable=True),

        # Verification results (JSON)
        sa.Column('orcid_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('google_scholar_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('publications_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('background_check_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),

        # Verification notes
        sa.Column('verification_notes', sa.Text(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    """Remove tier application tables and user tier fields."""

    # Drop qualification_verifications table
    op.drop_table('qualification_verifications')

    # Drop tier_applications table and indexes
    op.drop_index('idx_tier_applications_submitted', table_name='tier_applications')
    op.drop_index('idx_tier_applications_tier_status', table_name='tier_applications')
    op.drop_index('idx_tier_applications_user_status', table_name='tier_applications')
    op.drop_table('tier_applications')

    # Drop enums
    op.execute('DROP TYPE editorial_experience_type_enum')
    op.execute('DROP TYPE application_status_enum')
    op.execute('DROP TYPE application_tier_enum')

    # Remove tier field and index from users table
    op.drop_index('idx_users_tier', table_name='users')
    op.drop_column('users', 'tier')
    op.execute('DROP TYPE user_tier_enum')

    # Remove first_name and last_name from users
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
