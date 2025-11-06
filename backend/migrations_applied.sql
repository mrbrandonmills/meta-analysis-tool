-- This shows what migrations need to be applied
-- Generated from backend/alembic/versions/

-- Migration 1: Initial multi-tool schema
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    institution VARCHAR(255),
    role VARCHAR(50) DEFAULT 'researcher',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ... (simplified - full schema in alembic/versions/*.py)

SELECT 'Run: railway run alembic upgrade head' as instruction;
