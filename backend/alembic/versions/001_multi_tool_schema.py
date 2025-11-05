"""Multi-tool schema initial migration

Revision ID: 001
Revises:
Create Date: 2025-11-04

Creates complete database schema for 4-tool platform:
- Tool 1: Meta-Analysis Assistant
- Tool 2: Research Direction Generator
- Tool 3: Peer Review Assistant
- Tool 4: Expert Reviewer Matcher
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables for multi-tool platform."""

    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('institution', sa.String(255), nullable=True, index=True),
        sa.Column('role', sa.String(50), default='researcher', nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('is_verified', sa.Boolean, default=False, nullable=False),
        sa.Column('is_superuser', sa.Boolean, default=False, nullable=False),
        sa.Column('orcid', sa.String(50), unique=True, nullable=True, index=True),
        sa.Column('verification_token', sa.String(255), nullable=True),
        sa.Column('verification_token_expires', sa.DateTime, nullable=True),
        sa.Column('reset_token', sa.String(255), nullable=True),
        sa.Column('reset_token_expires', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('last_login', sa.DateTime, nullable=True),
        sa.Column('deleted_at', sa.DateTime, nullable=True, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    # API Keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('key_hash', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('key_prefix', sa.String(20), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('scopes', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=True),
        sa.Column('last_used_at', sa.DateTime, nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Projects table (universal container for all tools)
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('tool_type', sa.String(50), nullable=False, index=True),  # meta_analysis, research_direction, peer_review, reviewer_matcher
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('status', sa.String(50), default='draft', nullable=False, index=True),  # draft, in_progress, completed, failed, archived
        sa.Column('config', postgresql.JSONB, nullable=True),
        sa.Column('findings', postgresql.JSONB, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("tool_type IN ('meta_analysis', 'research_direction', 'peer_review', 'reviewer_matcher')", name='valid_tool_type'),
        sa.CheckConstraint("status IN ('draft', 'in_progress', 'completed', 'failed', 'archived')", name='valid_project_status'),
    )

    # Workflows table (agent execution tracking)
    op.create_table(
        'workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('agent_name', sa.String(255), nullable=False, index=True),
        sa.Column('agent_role', sa.String(50), nullable=False, index=True),
        sa.Column('input_data', postgresql.JSONB, nullable=True),
        sa.Column('output_data', postgresql.JSONB, nullable=True),
        sa.Column('decisions', postgresql.JSONB, nullable=True),
        sa.Column('status', sa.String(50), default='created', nullable=False, index=True),  # created, queued, in_progress, paused, completed, failed, cancelled
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('retry_count', sa.Integer, default=0, nullable=False),
        sa.Column('started_at', postgresql.JSONB, nullable=True),
        sa.Column('completed_at', postgresql.JSONB, nullable=True),
        sa.Column('duration_seconds', sa.Float, nullable=True),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('quality_score', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )

    # Papers table (shared across Tools 1, 2, 3)
    op.create_table(
        'papers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.Text, nullable=False, index=True),
        sa.Column('abstract', sa.Text, nullable=True),
        sa.Column('authors', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('journal', sa.String(255), nullable=True, index=True),
        sa.Column('year', sa.Integer, nullable=True, index=True),
        sa.Column('publication_date', postgresql.JSONB, nullable=True),
        # Identifiers
        sa.Column('doi', sa.String(255), unique=True, nullable=True, index=True),
        sa.Column('pmid', sa.String(50), unique=True, nullable=True, index=True),
        sa.Column('arxiv_id', sa.String(50), unique=True, nullable=True, index=True),
        sa.Column('pmc_id', sa.String(50), unique=True, nullable=True, index=True),
        # Content
        sa.Column('keywords', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('mesh_terms', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('database_source', sa.String(50), nullable=True, index=True),
        # Tool 1: Meta-Analysis
        sa.Column('credibility_level', sa.String(50), nullable=True, index=True),
        sa.Column('credibility_score', sa.Float, nullable=True),
        sa.Column('credibility_reasoning', sa.Text, nullable=True),
        sa.Column('extracted_statistics', postgresql.JSONB, nullable=True),
        sa.Column('effect_size', sa.Float, nullable=True),
        sa.Column('effect_size_ci_lower', sa.Float, nullable=True),
        sa.Column('effect_size_ci_upper', sa.Float, nullable=True),
        sa.Column('sample_size', sa.Integer, nullable=True),
        sa.Column('p_value', sa.Float, nullable=True),
        sa.Column('inclusion_status', sa.String(50), nullable=True, index=True),
        sa.Column('exclusion_reason', sa.Text, nullable=True),
        # Tool 2: Research Direction
        sa.Column('research_gaps', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('trending_topics', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('novelty_score', sa.Float, nullable=True),
        # Tool 3: Peer Review
        sa.Column('review_quality_score', sa.Float, nullable=True),
        sa.Column('methodology_score', sa.Float, nullable=True),
        sa.Column('clarity_score', sa.Float, nullable=True),
        # Shared
        sa.Column('citation_count', sa.Integer, default=0, nullable=False),
        sa.Column('full_text_url', sa.Text, nullable=True),
        sa.Column('pdf_path', sa.Text, nullable=True),
        sa.Column('pdf_hash', sa.String(64), nullable=True, index=True),
        sa.Column('full_text', sa.Text, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Researchers table (shared across Tools 2, 4)
    op.create_table(
        'researchers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('orcid', sa.String(50), unique=True, nullable=True, index=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('email', sa.String(255), nullable=True, index=True),
        sa.Column('institution', sa.String(255), nullable=True, index=True),
        sa.Column('department', sa.String(255), nullable=True),
        sa.Column('country', sa.String(100), nullable=True, index=True),
        sa.Column('website', sa.Text, nullable=True),
        # Academic metrics
        sa.Column('h_index', sa.Integer, nullable=True),
        sa.Column('i10_index', sa.Integer, nullable=True),
        sa.Column('total_citations', sa.Integer, default=0, nullable=False),
        sa.Column('publication_count', sa.Integer, default=0, nullable=False),
        # Tool 4: Reviewer Matching
        sa.Column('expertise_keywords', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('expertise_domains', postgresql.JSONB, nullable=True),
        sa.Column('research_domains', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('recent_review_count', sa.Integer, default=0, nullable=False),
        sa.Column('total_review_count', sa.Integer, default=0, nullable=False),
        sa.Column('average_review_time_days', sa.Float, nullable=True),
        sa.Column('last_review_date', sa.Date, nullable=True),
        sa.Column('estimated_availability', sa.Float, nullable=True),
        sa.Column('current_workload', sa.Integer, default=0, nullable=False),
        sa.Column('response_rate', sa.Float, nullable=True),
        # Tool 2: Research Direction
        sa.Column('trending_areas', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('emerging_expertise', postgresql.JSONB, nullable=True),
        # Network info
        sa.Column('coauthor_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('institution_collaborators', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('last_active', sa.Date, nullable=True),
        sa.Column('last_publication_date', sa.Date, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('semantic_scholar_id', sa.String(100), nullable=True, index=True),
        sa.Column('google_scholar_id', sa.String(100), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Manuscripts table (Tool 3: Peer Review)
    op.create_table(
        'manuscripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.Text, nullable=False, index=True),
        sa.Column('abstract', sa.Text, nullable=True),
        sa.Column('keywords', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('manuscript_type', sa.String(50), nullable=False),
        sa.Column('submission_date', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('journal_name', sa.String(255), nullable=True, index=True),
        sa.Column('journal_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('corresponding_author_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('author_names', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('author_affiliations', postgresql.JSONB, nullable=True),
        sa.Column('status', sa.String(50), default='submitted', nullable=False, index=True),
        sa.Column('current_round', sa.Integer, default=1, nullable=False),
        sa.Column('pdf_path', sa.Text, nullable=True),
        sa.Column('supplementary_files', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('desk_review_decision', sa.String(50), nullable=True),
        sa.Column('desk_review_reasoning', sa.Text, nullable=True),
        sa.Column('quality_score', sa.Float, nullable=True),
        sa.Column('methodology_score', sa.Float, nullable=True),
        sa.Column('novelty_score', sa.Float, nullable=True),
        sa.Column('editorial_decision', sa.String(50), nullable=True),
        sa.Column('editorial_decision_date', sa.DateTime, nullable=True),
        sa.Column('decision_letter', sa.Text, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['corresponding_author_id'], ['users.id']),
    )

    # Peer Reviews table (Tool 3: Peer Review Assistant)
    op.create_table(
        'peer_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('manuscript_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('review_round', sa.Integer, default=1, nullable=False),
        sa.Column('invitation_date', sa.DateTime, nullable=True),
        sa.Column('acceptance_date', sa.DateTime, nullable=True),
        sa.Column('submission_date', sa.DateTime, nullable=True),
        sa.Column('due_date', sa.DateTime, nullable=True),
        sa.Column('status', sa.String(50), default='invited', nullable=False, index=True),
        sa.Column('review_text', sa.Text, nullable=True),
        sa.Column('strengths', sa.Text, nullable=True),
        sa.Column('weaknesses', sa.Text, nullable=True),
        sa.Column('detailed_comments', sa.Text, nullable=True),
        sa.Column('confidential_comments', sa.Text, nullable=True),
        sa.Column('overall_score', sa.Float, nullable=True),
        sa.Column('originality_score', sa.Float, nullable=True),
        sa.Column('methodology_score', sa.Float, nullable=True),
        sa.Column('clarity_score', sa.Float, nullable=True),
        sa.Column('significance_score', sa.Float, nullable=True),
        sa.Column('recommendation', sa.String(50), nullable=True, index=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('ai_assisted', sa.Boolean, default=False, nullable=False),
        sa.Column('ai_draft_used', sa.Boolean, default=False, nullable=False),
        sa.Column('ai_generated_sections', postgresql.JSONB, nullable=True),
        sa.Column('review_quality_score', sa.Float, nullable=True),
        sa.Column('constructiveness_score', sa.Float, nullable=True),
        sa.Column('bias_score', sa.Float, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['manuscript_id'], ['manuscripts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['researchers.id']),
    )

    # Reviewer Matches table (Tool 4: Expert Reviewer Matcher)
    op.create_table(
        'reviewer_matches',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('manuscript_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('expertise_score', sa.Float, nullable=False),
        sa.Column('availability_score', sa.Float, nullable=False),
        sa.Column('diversity_score', sa.Float, nullable=True),
        sa.Column('overall_score', sa.Float, nullable=False, index=True),
        sa.Column('rank', sa.Integer, nullable=True),
        sa.Column('conflict_risk', sa.Float, nullable=False),
        sa.Column('conflict_types', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('conflict_details', postgresql.JSONB, nullable=True),
        sa.Column('has_conflict', sa.Boolean, default=False, nullable=False, index=True),
        sa.Column('matching_keywords', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('matching_domains', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('expertise_overlap', postgresql.JSONB, nullable=True),
        sa.Column('estimated_workload', sa.Integer, nullable=True),
        sa.Column('recent_reviews', postgresql.JSONB, nullable=True),
        sa.Column('response_likelihood', sa.Float, nullable=True),
        sa.Column('geographic_region', sa.String(100), nullable=True),
        sa.Column('institution_type', sa.String(100), nullable=True),
        sa.Column('career_stage', sa.String(50), nullable=True),
        sa.Column('reasoning', sa.Text, nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('status', sa.String(50), default='pending', nullable=False, index=True),
        sa.Column('invitation_sent_at', sa.DateTime, nullable=True),
        sa.Column('response_received_at', sa.DateTime, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['manuscript_id'], ['manuscripts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['researcher_id'], ['researchers.id']),
    )

    # Research Gaps table (Tool 2: Research Direction Generator)
    op.create_table(
        'research_gaps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('gap_type', sa.String(50), nullable=False, index=True),
        sa.Column('domain', sa.String(255), nullable=True, index=True),
        sa.Column('evidence', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('supporting_papers', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('citation_count', sa.Integer, default=0, nullable=False),
        sa.Column('impact_potential', sa.Float, nullable=True),
        sa.Column('feasibility_score', sa.Float, nullable=True),
        sa.Column('novelty_score', sa.Float, nullable=True),
        sa.Column('priority', sa.String(50), nullable=True, index=True),
        sa.Column('temporal_trend', sa.String(100), nullable=True),
        sa.Column('geographic_coverage', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('understudied_populations', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('reasoning', sa.Text, nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    )

    # Research Proposals table (Tool 2: Research Direction Generator)
    op.create_table(
        'research_proposals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('gap_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('title', sa.Text, nullable=False),
        sa.Column('proposal_type', sa.String(50), default='research_plan', nullable=False),
        sa.Column('status', sa.String(50), default='draft', nullable=False, index=True),
        sa.Column('research_question', sa.Text, nullable=False),
        sa.Column('background', sa.Text, nullable=True),
        sa.Column('significance', sa.Text, nullable=True),
        sa.Column('innovation', sa.Text, nullable=True),
        sa.Column('methodology', sa.Text, nullable=True),
        sa.Column('expected_outcomes', sa.Text, nullable=True),
        sa.Column('expected_impact', sa.Text, nullable=True),
        sa.Column('timeline', sa.Text, nullable=True),
        sa.Column('budget_overview', sa.Text, nullable=True),
        sa.Column('study_population', sa.String(500), nullable=True),
        sa.Column('intervention', sa.String(500), nullable=True),
        sa.Column('comparator', sa.String(500), nullable=True),
        sa.Column('outcomes', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('study_design', sa.String(255), nullable=True),
        sa.Column('key_references', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('literature_gaps_addressed', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('novelty_score', sa.Float, nullable=True),
        sa.Column('feasibility_score', sa.Float, nullable=True),
        sa.Column('impact_score', sa.Float, nullable=True),
        sa.Column('predicted_citation_count', sa.Float, nullable=True),
        sa.Column('funding_likelihood', sa.Float, nullable=True),
        sa.Column('nih_format', postgresql.JSONB, nullable=True),
        sa.Column('nsf_format', postgresql.JSONB, nullable=True),
        sa.Column('custom_sections', postgresql.JSONB, nullable=True),
        sa.Column('ai_generated', sa.Boolean, default=True, nullable=False),
        sa.Column('generation_prompt', sa.Text, nullable=True),
        sa.Column('refinement_history', postgresql.JSONB, nullable=True),
        sa.Column('submitted_to', sa.String(255), nullable=True),
        sa.Column('submission_date', sa.DateTime, nullable=True),
        sa.Column('decision_date', sa.DateTime, nullable=True),
        sa.Column('decision', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['gap_id'], ['research_gaps.id']),
    )

    # Association Tables (Many-to-Many)

    # Project <-> Paper
    op.create_table(
        'project_papers',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('paper_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('role', sa.String(50), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
    )

    # Project <-> Researcher
    op.create_table(
        'project_researchers',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('role', sa.String(50), nullable=True),
        sa.Column('relevance_score', sa.Float, nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['researcher_id'], ['researchers.id'], ondelete='CASCADE'),
    )

    # Paper <-> Researcher (authorship)
    op.create_table(
        'paper_authors',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('paper_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('researcher_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('author_position', sa.Integer, nullable=True),
        sa.Column('is_corresponding', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['researcher_id'], ['researchers.id'], ondelete='CASCADE'),
    )

    # Create indexes for performance
    op.create_index('idx_papers_full_text', 'papers', ['full_text'], postgresql_using='gin', postgresql_ops={'full_text': 'gin_trgm_ops'}, if_not_exists=True)
    op.create_index('idx_papers_title', 'papers', ['title'], postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'}, if_not_exists=True)
    op.create_index('idx_researchers_name', 'researchers', ['name'], postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'}, if_not_exists=True)
    op.create_index('idx_projects_title', 'projects', ['title'], postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'}, if_not_exists=True)

    # Create GIN indexes for JSONB fields (fast JSON queries)
    op.create_index('idx_papers_metadata', 'papers', ['metadata'], postgresql_using='gin', if_not_exists=True)
    op.create_index('idx_projects_config', 'projects', ['config'], postgresql_using='gin', if_not_exists=True)
    op.create_index('idx_workflows_decisions', 'workflows', ['decisions'], postgresql_using='gin', if_not_exists=True)


def downgrade() -> None:
    """Drop all tables."""

    # Drop association tables first
    op.drop_table('paper_authors')
    op.drop_table('project_researchers')
    op.drop_table('project_papers')

    # Drop main tables
    op.drop_table('research_proposals')
    op.drop_table('research_gaps')
    op.drop_table('reviewer_matches')
    op.drop_table('peer_reviews')
    op.drop_table('manuscripts')
    op.drop_table('researchers')
    op.drop_table('papers')
    op.drop_table('workflows')
    op.drop_table('projects')
    op.drop_table('api_keys')
    op.drop_table('users')
