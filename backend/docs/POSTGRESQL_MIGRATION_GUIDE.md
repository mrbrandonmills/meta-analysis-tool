# PostgreSQL Migration Guide: From In-Memory to Production-Grade Persistence

## Overview

This guide documents the migration from in-memory state management (`coordinators_by_id` dict) to PostgreSQL-backed persistence for the meta-analysis system.

## Problem Statement

### Before Migration (In-Memory State)

**Limitations:**
- State stored in `coordinators_by_id: dict[str, CoordinatorAgent]` at module level
- State lost on server restart or crash
- Cannot scale horizontally (stuck at 1 Uvicorn worker)
- No persistence of meta-analysis progress
- No way to recover from failures
- Memory leaks with long-running processes

**Code Location:** `backend/app/api/v1/meta_analysis.py:19`

```python
# Old implementation (DO NOT USE)
coordinators_by_id: dict[str, CoordinatorAgent] = {}

# Stored in memory - lost on restart
coordinators_by_id[analysis_id] = coordinator
```

### After Migration (PostgreSQL Persistence)

**Benefits:**
- State persisted to PostgreSQL database
- Survives server restarts and crashes
- Horizontal scaling with 4+ Uvicorn workers
- Complete audit trail of all agent executions
- State recovery and debugging capabilities
- Production-grade reliability

**New Implementation:** `backend/app/api/v1/meta_analysis_db.py`

## Architecture Changes

### Database Schema

Three new tables added for meta-analysis persistence:

#### 1. `meta_analyses` - Core Metadata
```sql
CREATE TABLE meta_analyses (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    research_question TEXT NOT NULL,
    topic VARCHAR(500) NOT NULL,
    inclusion_criteria JSONB,
    exclusion_criteria JSONB,
    databases JSONB,
    peer_review_only VARCHAR(50) DEFAULT 'false',
    expert_name VARCHAR(255),
    status meta_analysis_status NOT NULL DEFAULT 'created',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    completed_at TIMESTAMP,
    INDEX ix_meta_analyses_user_id (user_id),
    INDEX ix_meta_analyses_topic (topic),
    INDEX ix_meta_analyses_status (status),
    INDEX ix_meta_analyses_created_at (created_at)
);
```

**Purpose:** Store meta-analysis configuration and metadata

#### 2. `coordinator_states` - Agent State Persistence
```sql
CREATE TABLE coordinator_states (
    id UUID PRIMARY KEY,
    analysis_id UUID UNIQUE REFERENCES meta_analyses(id) ON DELETE CASCADE,
    agent_state JSONB NOT NULL,
    decisions JSONB NOT NULL DEFAULT '[]',
    workflow_plan JSONB,
    coordinator_id UUID NOT NULL,
    version VARCHAR(50) DEFAULT '1.0',
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    INDEX ix_coordinator_states_analysis_id (analysis_id)
);
```

**Purpose:** Store serialized coordinator agent state for recovery

#### 3. `agent_executions` - Complete Audit Trail
```sql
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES meta_analyses(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    agent_role VARCHAR(50) NOT NULL,
    agent_id UUID NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB NOT NULL,
    error_message TEXT,
    execution_time_ms VARCHAR(50),
    tokens_used VARCHAR(50),
    status VARCHAR(50) NOT NULL DEFAULT 'success',
    executed_at TIMESTAMP NOT NULL DEFAULT now(),
    INDEX ix_agent_executions_analysis_id (analysis_id),
    INDEX ix_agent_executions_agent_name (agent_name),
    INDEX ix_agent_executions_agent_role (agent_role),
    INDEX ix_agent_executions_status (status),
    INDEX ix_agent_executions_executed_at (executed_at),
    INDEX ix_agent_executions_analysis_time (analysis_id, executed_at)
);
```

**Purpose:** Complete audit trail for debugging and analysis

### SQLAlchemy Models

**Location:** `backend/app/models/meta_analysis.py`

```python
from app.models.meta_analysis import (
    MetaAnalysis,           # Core meta-analysis model
    CoordinatorState,       # Coordinator state persistence
    AgentExecution,         # Agent execution audit trail
    MetaAnalysisStatus,     # Status enum
)
```

## Migration Steps

### Step 1: Add PostgreSQL to Railway

1. **Login to Railway Dashboard**
   ```bash
   railway login
   ```

2. **Add PostgreSQL Database**
   ```bash
   # In Railway dashboard:
   # Project → New → Database → PostgreSQL

   # Railway will automatically provision:
   # - PostgreSQL 15+ instance
   # - DATABASE_URL environment variable
   # - Automatic backups
   ```

3. **Verify Database Connection**
   ```bash
   # Railway automatically injects DATABASE_URL
   # Format: postgresql://user:pass@host:port/dbname

   # Test connection
   railway run alembic current
   ```

### Step 2: Run Database Migrations

1. **Run Migration Locally (Development)**
   ```bash
   cd backend

   # Set database URL
   export DATABASE_URL="postgresql://localhost/meta_analysis_dev"

   # Run migration
   alembic upgrade head

   # Verify tables created
   psql $DATABASE_URL -c "\dt"
   ```

2. **Run Migration on Railway (Production)**
   ```bash
   # Railway will run migrations automatically via start.sh
   # Or run manually:
   railway run alembic upgrade head

   # Verify
   railway run alembic current
   ```

### Step 3: Update API Router

Update `backend/app/main.py` or router configuration:

```python
# OLD: In-memory implementation
from app.api.v1 import meta_analysis

# NEW: PostgreSQL implementation
from app.api.v1 import meta_analysis_db

# Register new router
app.include_router(
    meta_analysis_db.router,
    prefix="/api/v1",
    tags=["meta-analysis"],
)
```

### Step 4: Update Dockerfile

Already updated to support 4 workers:

```dockerfile
# backend/Dockerfile:83
CMD /opt/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4 --app-dir /app
```

### Step 5: Deploy to Railway

```bash
# Commit changes
git add .
git commit -m "Migrate to PostgreSQL for production-grade persistence"

# Push to Railway
git push railway main

# Monitor deployment
railway logs
```

## API Changes

### Endpoint Compatibility

All endpoints remain the same, but now use database persistence:

| Endpoint | Method | Changes |
|----------|--------|---------|
| `/meta-analysis/create` | POST | Now saves to DB |
| `/meta-analysis/execute/{id}` | POST | Loads from DB |
| `/meta-analysis/status/{id}` | GET | Reads from DB |
| `/meta-analysis/audit/{id}` | GET | Reads from DB |
| `/meta-analysis/ask` | POST | Saves to audit trail |
| `/meta-analysis/report/{id}` | GET | Reads from DB |

### Request/Response Format

**No changes to API contract!** Same request/response formats.

**Example - Create Meta-Analysis:**
```bash
curl -X POST http://localhost:8000/api/v1/meta-analysis/create \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "Effects of mindfulness on anxiety",
    "topic": "Mindfulness and Anxiety",
    "inclusion_criteria": ["RCT", "Adult population"],
    "exclusion_criteria": ["Non-English"],
    "databases": ["pubmed", "arxiv"]
  }'

# Response (same format, but now persisted to DB):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "workflow_created",
  "message": "Meta-analysis workflow created successfully",
  "workflow": { ... }
}
```

## State Management

### Coordinator State Serialization

**Serialization Function:** `serialize_coordinator_state()`

Converts `CoordinatorAgent` instance to JSON-compatible dict:

```python
{
    "id": "uuid",
    "name": "Coordinator",
    "role": "coordinator",
    "status": "idle",
    "expert_profile": "Dr. Smith",
    "context": { ... },
    "decisions": [ ... ]
}
```

### State Recovery

**Deserialization Function:** `deserialize_coordinator_state()`

Reconstructs `CoordinatorAgent` from database state:

```python
# Load from database
coordinator = await deserialize_coordinator_state(
    state_data=coordinator_state.agent_state,
    decisions=coordinator_state.decisions,
    workflow_plan=coordinator_state.workflow_plan,
)

# Agent is fully restored and can continue processing
result = await coordinator.process(input_data)
```

## Scaling Configuration

### Uvicorn Workers

**Before (1 worker):**
```dockerfile
CMD uvicorn app.main:app --workers 1
```

**After (4 workers):**
```dockerfile
CMD uvicorn app.main:app --workers 4
```

### Worker Process Model

```
┌─────────────────────────────────────┐
│         Load Balancer (Railway)     │
└─────────────┬───────────────────────┘
              │
    ┌─────────┼─────────┬─────────┐
    │         │         │         │
┌───▼───┐ ┌──▼────┐ ┌──▼────┐ ┌──▼────┐
│Worker1│ │Worker2│ │Worker3│ │Worker4│
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘
    │         │         │         │
    └─────────┴─────────┴─────────┘
              │
    ┌─────────▼─────────────────┐
    │   PostgreSQL Database     │
    │  (Shared State Storage)   │
    └───────────────────────────┘
```

Each worker:
- Handles independent requests
- Reads/writes to shared PostgreSQL database
- No shared memory between workers
- Fully stateless application layer

## Database Indexes

Performance optimizations via strategic indexing:

```sql
-- Meta-analyses
CREATE INDEX ix_meta_analyses_user_id ON meta_analyses(user_id);
CREATE INDEX ix_meta_analyses_status ON meta_analyses(status);
CREATE INDEX ix_meta_analyses_created_at ON meta_analyses(created_at);

-- Coordinator states
CREATE UNIQUE INDEX ix_coordinator_states_analysis_id ON coordinator_states(analysis_id);

-- Agent executions (most queried table)
CREATE INDEX ix_agent_executions_analysis_id ON agent_executions(analysis_id);
CREATE INDEX ix_agent_executions_agent_role ON agent_executions(agent_role);
CREATE INDEX ix_agent_executions_executed_at ON agent_executions(executed_at);
CREATE INDEX ix_agent_executions_analysis_time ON agent_executions(analysis_id, executed_at);
```

## Audit Trail

### Complete Execution History

Every agent execution is logged to `agent_executions` table:

```python
await save_agent_execution(
    db=db,
    analysis_id=meta_analysis.id,
    agent_name="SearchAgent",
    agent_role="search",
    agent_id=search_agent.id,
    input_data={"research_question": "..."},
    output_data={"studies": [...]},
    status="success",
    execution_time_ms=1250,
    tokens_used=2500,
)
```

### Query Audit Trail

```bash
# Get all executions for an analysis
curl http://localhost:8000/api/v1/meta-analysis/audit/{analysis_id}

# Response:
{
  "analysis_id": "...",
  "total_executions": 5,
  "executions": [
    {
      "id": "...",
      "agent_name": "Coordinator",
      "agent_role": "coordinator",
      "status": "success",
      "executed_at": "2025-11-06T12:00:00",
      "execution_time_ms": "850",
      "tokens_used": "1200"
    },
    ...
  ]
}
```

## Error Recovery

### Crash Recovery

If server crashes mid-execution:

1. **State Preserved:** Last committed state in database
2. **Resume Execution:** Load coordinator state and continue
3. **Audit Trail:** View exactly where execution stopped

```python
# After crash, load and resume
result = await db.execute(
    select(MetaAnalysis).where(MetaAnalysis.status == MetaAnalysisStatus.IN_PROGRESS)
)
in_progress_analyses = result.scalars().all()

for analysis in in_progress_analyses:
    # Load coordinator state and resume
    coordinator = await load_coordinator(analysis.id)
    await coordinator.resume()
```

### Transaction Safety

All database operations use async transactions:

```python
try:
    # Create records
    db.add(meta_analysis)
    db.add(coordinator_state)

    # Commit atomically
    await db.commit()

except Exception as e:
    # Rollback on error
    await db.rollback()
    raise
```

## Testing

### Local Testing

```bash
# Start local PostgreSQL
docker run -d \
  --name meta-analysis-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=meta_analysis_dev \
  -p 5432:5432 \
  postgres:15

# Set database URL
export DATABASE_URL="postgresql://postgres:password@localhost:5432/meta_analysis_dev"

# Run migrations
cd backend
alembic upgrade head

# Start server with 4 workers
uvicorn app.main:app --reload --workers 4

# Test API
curl -X POST http://localhost:8000/api/v1/meta-analysis/create \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### Verify Multi-Worker Operation

```bash
# Check worker processes
ps aux | grep uvicorn

# Should see 4 worker processes:
# uvicorn app.main:app --workers 4  (master)
# uvicorn app.main:app              (worker 1)
# uvicorn app.main:app              (worker 2)
# uvicorn app.main:app              (worker 3)
# uvicorn app.main:app              (worker 4)
```

## Performance Considerations

### Connection Pooling

SQLAlchemy manages connection pooling automatically:

```python
# backend/app/db/base.py
engine = create_engine(
    database_url,
    pool_size=10,           # 10 persistent connections
    max_overflow=20,        # 20 additional connections on demand
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True,     # Verify connections before use
)
```

### Query Optimization

- Use indexes for all common queries
- JSONB columns for flexible schema
- Composite indexes for multi-column queries
- Async queries to avoid blocking

### Monitoring

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check query performance
SELECT * FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

## Rollback Plan

If issues arise, rollback to in-memory implementation:

```bash
# 1. Revert router changes
git revert HEAD

# 2. Rollback database migration
alembic downgrade -1

# 3. Update Dockerfile to 1 worker
# Change: --workers 4  →  --workers 1

# 4. Redeploy
git push railway main
```

## Security Considerations

### Database Access

- Use strong passwords
- Enable SSL connections in production
- Restrict database access to Railway internal network
- Rotate credentials regularly

### Data Privacy

- JSONB columns may contain sensitive data
- Consider encryption at rest for production
- Implement proper access controls
- Audit database access logs

## Maintenance

### Database Backups

Railway provides automatic backups:
- Daily snapshots
- Point-in-time recovery
- Manual backup triggers

### Schema Evolution

Use Alembic for schema changes:

```bash
# Create new migration
alembic revision --autogenerate -m "add_new_field"

# Review generated migration
cat alembic/versions/005_add_new_field.py

# Apply migration
alembic upgrade head
```

### Monitoring

Monitor these metrics:
- Database connection pool utilization
- Query execution times
- Table sizes and growth rates
- Agent execution success rates

## Troubleshooting

### Common Issues

**Issue 1: Connection Pool Exhausted**
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 10 overflow 20 reached
```

**Solution:**
```python
# Increase pool size in db/base.py
pool_size=20,
max_overflow=40,
```

**Issue 2: State Deserialization Fails**
```
KeyError: 'decisions'
```

**Solution:**
```python
# Add default values in deserialization
decisions = state_data.get("decisions", [])
```

**Issue 3: Migration Conflicts**
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution:**
```bash
# Check current revision
alembic current

# Stamp database with current revision
alembic stamp head

# Retry migration
alembic upgrade head
```

## Success Metrics

After migration, you should observe:

✅ **Reliability**
- Zero state loss on restart
- Automatic crash recovery
- 99.9%+ uptime

✅ **Scalability**
- 4x request throughput (4 workers)
- Linear scaling with additional workers
- No memory leaks

✅ **Observability**
- Complete audit trail
- Query execution history
- Performance metrics

✅ **Maintainability**
- Easy debugging via database queries
- State inspection at any point
- Reproducible issues

## Next Steps

1. **Add Railway PostgreSQL database**
2. **Run database migrations**
3. **Deploy updated Dockerfile**
4. **Monitor performance metrics**
5. **Tune connection pool settings**
6. **Set up database monitoring**

## Resources

- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
- [Alembic Migration Guide](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [PostgreSQL JSONB Performance](https://www.postgresql.org/docs/current/datatype-json.html)
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)
- [Railway PostgreSQL](https://docs.railway.app/databases/postgresql)
