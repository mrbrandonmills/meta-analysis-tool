-- Initial Database Setup for Meta-Analysis Platform
-- This file is run automatically when PostgreSQL container starts

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For better indexing

-- Create custom types
DO $$ BEGIN
    CREATE TYPE credibility_level AS ENUM ('VERY_LOW', 'LOW', 'MEDIUM', 'HIGH');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE agent_role AS ENUM (
        'COORDINATOR',
        'SEARCH',
        'SCREENING',
        'CREDIBILITY',
        'QA',
        'DATA_EXTRACTION',
        'STATISTICAL',
        'EXPERTISE_ANALYZER',
        'CONFLICT_DETECTOR',
        'AVAILABILITY_PREDICTOR',
        'MATCHER',
        'REVIEW_DRAFTER',
        'EDITOR_ASSISTANT',
        'GAP_ANALYSIS',
        'TREND_ANALYSIS',
        'METHOD_INNOVATION',
        'IMPACT_PREDICTION',
        'PROPOSAL_GENERATOR'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE workflow_status AS ENUM (
        'CREATED',
        'QUEUED',
        'IN_PROGRESS',
        'PAUSED',
        'COMPLETED',
        'FAILED',
        'CANCELLED'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully';
    RAISE NOTICE 'Extensions enabled: uuid-ossp, pg_trgm, btree_gin';
    RAISE NOTICE 'Custom types created: credibility_level, agent_role, workflow_status';
END $$;
