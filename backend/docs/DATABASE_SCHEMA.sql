-- ============================================================================
-- Meta-Analysis Tool - PostgreSQL Database Schema
-- ============================================================================
-- Version: 1.0
-- Date: 2025-11-06
-- Migration: 004_add_meta_analysis_tables
--
-- This schema provides production-grade persistence for the meta-analysis
-- system, replacing in-memory state with PostgreSQL-backed storage.
--
-- Features:
-- - Full state persistence for crash recovery
-- - Horizontal scaling support (multiple workers)
-- - Complete audit trail of agent executions
-- - JSONB for flexible schema evolution
-- - Comprehensive indexing for performance
-- ============================================================================

-- ============================================================================
-- ENUMS
-- ============================================================================

-- Meta-analysis workflow status
CREATE TYPE meta_analysis_status AS ENUM (
    'created',              -- Initial creation
    'workflow_created',     -- Coordinator created workflow plan
    'in_progress',         -- Execution started
    'searching',           -- Search agent active
    'screening',           -- Screening agent active
    'quality_assessment',  -- Quality assessment in progress
    'data_extraction',     -- Extracting data from studies
    'analysis',            -- Statistical analysis running
    'completed',           -- Successfully completed
    'failed',              -- Execution failed
    'cancelled'            -- User cancelled
);

-- ============================================================================
-- TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- meta_analyses: Core meta-analysis metadata and configuration
-- ----------------------------------------------------------------------------
-- Purpose: Store meta-analysis research parameters and track progress
-- Replaces: coordinators_by_id in-memory dict
-- Relationships:
--   - Belongs to users (user_id)
--   - Has one coordinator_state
--   - Has many agent_executions
-- ----------------------------------------------------------------------------

CREATE TABLE meta_analyses (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign keys
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Research parameters
    research_question TEXT NOT NULL,
    topic VARCHAR(500) NOT NULL,
    inclusion_criteria JSONB,        -- Array of inclusion criteria strings
    exclusion_criteria JSONB,        -- Array of exclusion criteria strings

    -- Configuration
    databases JSONB,                 -- Array of database names ["pubmed", "arxiv"]
    peer_review_only VARCHAR(50) DEFAULT 'false',
    expert_name VARCHAR(255),        -- Optional expert profile name

    -- Status tracking
    status meta_analysis_status NOT NULL DEFAULT 'created',

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX ix_meta_analyses_user_id ON meta_analyses(user_id);
CREATE INDEX ix_meta_analyses_topic ON meta_analyses(topic);
CREATE INDEX ix_meta_analyses_status ON meta_analyses(status);
CREATE INDEX ix_meta_analyses_created_at ON meta_analyses(created_at);

-- Comments
COMMENT ON TABLE meta_analyses IS 'Core meta-analysis metadata and configuration';
COMMENT ON COLUMN meta_analyses.research_question IS 'Primary research question being investigated';
COMMENT ON COLUMN meta_analyses.topic IS 'Brief topic description for searching and filtering';
COMMENT ON COLUMN meta_analyses.inclusion_criteria IS 'JSONB array of inclusion criteria for screening';
COMMENT ON COLUMN meta_analyses.exclusion_criteria IS 'JSONB array of exclusion criteria for screening';
COMMENT ON COLUMN meta_analyses.databases IS 'JSONB array of databases to search (pubmed, arxiv, etc)';
COMMENT ON COLUMN meta_analyses.status IS 'Current workflow status (created → completed)';

-- ----------------------------------------------------------------------------
-- coordinator_states: Coordinator agent state for recovery and scaling
-- ----------------------------------------------------------------------------
-- Purpose: Persist coordinator agent state to enable crash recovery and
--          allow any worker to load and resume processing
-- Enables:
--   - Horizontal scaling (multiple Uvicorn workers)
--   - Crash recovery (reload state after restart)
--   - State debugging (inspect agent decisions at any time)
-- ----------------------------------------------------------------------------

CREATE TABLE coordinator_states (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign keys (one-to-one with meta_analyses)
    analysis_id UUID NOT NULL UNIQUE REFERENCES meta_analyses(id) ON DELETE CASCADE,

    -- Serialized agent state
    agent_state JSONB NOT NULL,      -- Serialized CoordinatorAgent state
    decisions JSONB NOT NULL DEFAULT '[]',  -- Array of agent decisions
    workflow_plan JSONB,             -- Workflow plan created by coordinator

    -- Metadata
    coordinator_id UUID NOT NULL,    -- Original coordinator agent instance ID
    version VARCHAR(50) DEFAULT '1.0',  -- State schema version for migrations

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE UNIQUE INDEX ix_coordinator_states_analysis_id ON coordinator_states(analysis_id);

-- Comments
COMMENT ON TABLE coordinator_states IS 'Persistent storage of coordinator agent state for recovery and scaling';
COMMENT ON COLUMN coordinator_states.agent_state IS 'Serialized CoordinatorAgent internal state (JSON)';
COMMENT ON COLUMN coordinator_states.decisions IS 'Array of agent decisions made during execution';
COMMENT ON COLUMN coordinator_states.workflow_plan IS 'Complete workflow plan generated by coordinator';
COMMENT ON COLUMN coordinator_states.coordinator_id IS 'UUID of original coordinator agent instance';
COMMENT ON COLUMN coordinator_states.version IS 'State schema version for backward compatibility';

-- ----------------------------------------------------------------------------
-- agent_executions: Complete audit trail of all agent operations
-- ----------------------------------------------------------------------------
-- Purpose: Log every agent execution for debugging, analysis, and compliance
-- Benefits:
--   - Full execution history for debugging
--   - Performance monitoring (execution times, token usage)
--   - Result reproducibility
--   - Compliance and audit requirements
-- ----------------------------------------------------------------------------

CREATE TABLE agent_executions (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign keys
    analysis_id UUID NOT NULL REFERENCES meta_analyses(id) ON DELETE CASCADE,

    -- Agent identification
    agent_name VARCHAR(100) NOT NULL,  -- "SearchAgent", "ScreeningAgent", etc
    agent_role VARCHAR(50) NOT NULL,   -- "search", "screening", "qa", etc
    agent_id UUID NOT NULL,            -- Agent instance UUID

    -- Execution data
    input_data JSONB NOT NULL,         -- Input parameters provided to agent
    output_data JSONB NOT NULL,        -- Output results from agent
    error_message TEXT,                -- Error message if execution failed

    -- Performance metrics
    execution_time_ms VARCHAR(50),     -- Execution duration in milliseconds
    tokens_used VARCHAR(50),           -- LLM tokens consumed (if applicable)

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'success',  -- success, failed, partial

    -- Timestamp
    executed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for performance (this table will grow large)
CREATE INDEX ix_agent_executions_analysis_id ON agent_executions(analysis_id);
CREATE INDEX ix_agent_executions_agent_name ON agent_executions(agent_name);
CREATE INDEX ix_agent_executions_agent_role ON agent_executions(agent_role);
CREATE INDEX ix_agent_executions_status ON agent_executions(status);
CREATE INDEX ix_agent_executions_executed_at ON agent_executions(executed_at);

-- Composite index for time-based queries
CREATE INDEX ix_agent_executions_analysis_time ON agent_executions(analysis_id, executed_at);

-- Comments
COMMENT ON TABLE agent_executions IS 'Complete audit trail of all agent executions for debugging and analysis';
COMMENT ON COLUMN agent_executions.agent_name IS 'Human-readable agent name (SearchAgent, ScreeningAgent)';
COMMENT ON COLUMN agent_executions.agent_role IS 'Agent role/type (search, screening, qa, coordinator)';
COMMENT ON COLUMN agent_executions.input_data IS 'Complete input data provided to agent (JSONB)';
COMMENT ON COLUMN agent_executions.output_data IS 'Complete output data returned by agent (JSONB)';
COMMENT ON COLUMN agent_executions.execution_time_ms IS 'Total execution duration in milliseconds';
COMMENT ON COLUMN agent_executions.tokens_used IS 'Number of LLM tokens consumed during execution';

-- ============================================================================
-- SAMPLE DATA (for testing and development)
-- ============================================================================

-- Insert sample user (if users table exists)
-- INSERT INTO users (id, email, hashed_password, full_name, role, is_active, is_verified)
-- VALUES (
--     '550e8400-e29b-41d4-a716-446655440000',
--     'researcher@example.com',
--     '$argon2id$v=19$m=65536,t=3,p=4$...',  -- hashed password
--     'Dr. Jane Smith',
--     'RESEARCHER',
--     true,
--     true
-- );

-- Insert sample meta-analysis
-- INSERT INTO meta_analyses (
--     id,
--     user_id,
--     research_question,
--     topic,
--     inclusion_criteria,
--     exclusion_criteria,
--     databases,
--     status
-- ) VALUES (
--     '660e8400-e29b-41d4-a716-446655440001',
--     '550e8400-e29b-41d4-a716-446655440000',
--     'What are the effects of mindfulness-based interventions on anxiety in adults?',
--     'Mindfulness and Anxiety',
--     '["Randomized controlled trial", "Adult population (18+)", "Mindfulness-based intervention", "Anxiety as outcome measure"]',
--     '["Non-English language", "Qualitative studies", "Case studies"]',
--     '["pubmed", "arxiv", "europepmc", "core"]',
--     'created'
-- );

-- ============================================================================
-- UTILITY QUERIES
-- ============================================================================

-- Count meta-analyses by status
-- SELECT status, COUNT(*) as count
-- FROM meta_analyses
-- GROUP BY status
-- ORDER BY count DESC;

-- Get active meta-analyses (in progress)
-- SELECT id, topic, research_question, status, created_at
-- FROM meta_analyses
-- WHERE status IN ('in_progress', 'searching', 'screening', 'quality_assessment')
-- ORDER BY created_at DESC;

-- Get complete audit trail for a meta-analysis
-- SELECT
--     ae.agent_name,
--     ae.agent_role,
--     ae.status,
--     ae.execution_time_ms,
--     ae.tokens_used,
--     ae.executed_at
-- FROM agent_executions ae
-- WHERE ae.analysis_id = '660e8400-e29b-41d4-a716-446655440001'
-- ORDER BY ae.executed_at;

-- Get agent performance statistics
-- SELECT
--     agent_name,
--     agent_role,
--     COUNT(*) as total_executions,
--     AVG(CAST(execution_time_ms AS INTEGER)) as avg_execution_time_ms,
--     SUM(CAST(tokens_used AS INTEGER)) as total_tokens
-- FROM agent_executions
-- WHERE execution_time_ms IS NOT NULL
-- GROUP BY agent_name, agent_role
-- ORDER BY avg_execution_time_ms DESC;

-- Get failed executions
-- SELECT
--     ae.analysis_id,
--     ma.topic,
--     ae.agent_name,
--     ae.error_message,
--     ae.executed_at
-- FROM agent_executions ae
-- JOIN meta_analyses ma ON ae.analysis_id = ma.id
-- WHERE ae.status = 'failed'
-- ORDER BY ae.executed_at DESC;

-- ============================================================================
-- MAINTENANCE QUERIES
-- ============================================================================

-- Check table sizes
-- SELECT
--     schemaname,
--     tablename,
--     pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
--     pg_total_relation_size(schemaname||'.'||tablename) AS bytes
-- FROM pg_tables
-- WHERE schemaname = 'public' AND tablename IN ('meta_analyses', 'coordinator_states', 'agent_executions')
-- ORDER BY bytes DESC;

-- Check index usage
-- SELECT
--     schemaname,
--     tablename,
--     indexname,
--     idx_scan as index_scans,
--     idx_tup_read as tuples_read,
--     idx_tup_fetch as tuples_fetched
-- FROM pg_stat_user_indexes
-- WHERE schemaname = 'public' AND tablename IN ('meta_analyses', 'coordinator_states', 'agent_executions')
-- ORDER BY idx_scan DESC;

-- Vacuum and analyze (maintenance)
-- VACUUM ANALYZE meta_analyses;
-- VACUUM ANALYZE coordinator_states;
-- VACUUM ANALYZE agent_executions;

-- ============================================================================
-- MIGRATION ROLLBACK
-- ============================================================================

-- To rollback this migration:
-- DROP TABLE IF EXISTS agent_executions CASCADE;
-- DROP TABLE IF EXISTS coordinator_states CASCADE;
-- DROP TABLE IF EXISTS meta_analyses CASCADE;
-- DROP TYPE IF EXISTS meta_analysis_status;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
