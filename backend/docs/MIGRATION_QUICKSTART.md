# PostgreSQL Migration - Quick Start Guide

## TL;DR

**Problem:** In-memory state (`coordinators_by_id` dict) doesn't scale and loses data on restart.

**Solution:** PostgreSQL persistence with 4 Uvicorn workers.

## Quick Steps

### 1. Add PostgreSQL to Railway

```bash
# Railway Dashboard → Your Project → New → Database → PostgreSQL
# Railway auto-generates DATABASE_URL environment variable
```

### 2. Run Database Migration

```bash
cd backend
railway run alembic upgrade head
```

### 3. Deploy

```bash
git add .
git commit -m "Migrate to PostgreSQL persistence"
git push railway main
```

### 4. Verify

```bash
# Check tables created
railway run psql $DATABASE_URL -c "\dt"

# Should show:
# - meta_analyses
# - coordinator_states
# - agent_executions

# Test API
curl -X POST https://your-app.railway.app/api/v1/meta-analysis/create \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "Test question",
    "topic": "Test topic",
    "inclusion_criteria": ["RCT"]
  }'
```

## What Changed

### Before (In-Memory)
```python
# Lost on restart
coordinators_by_id: dict[str, CoordinatorAgent] = {}
coordinators_by_id[id] = coordinator
```

### After (PostgreSQL)
```python
# Persisted to database
meta_analysis = MetaAnalysis(...)
db.add(meta_analysis)
await db.commit()
```

### Workers
- **Before:** 1 worker (shared memory required)
- **After:** 4 workers (shared database)

## Key Files

| File | Purpose |
|------|---------|
| `app/models/meta_analysis.py` | SQLAlchemy models |
| `app/api/v1/meta_analysis_db.py` | Database-backed API |
| `alembic/versions/004_add_meta_analysis_tables.py` | Migration script |
| `Dockerfile` | Updated to 4 workers |

## Database Tables

```
meta_analyses
├── id (UUID, PK)
├── user_id (UUID, FK → users)
├── research_question (TEXT)
├── topic (VARCHAR)
├── status (ENUM)
└── timestamps

coordinator_states
├── id (UUID, PK)
├── analysis_id (UUID, FK → meta_analyses)
├── agent_state (JSONB)
├── decisions (JSONB)
└── workflow_plan (JSONB)

agent_executions
├── id (UUID, PK)
├── analysis_id (UUID, FK → meta_analyses)
├── agent_name (VARCHAR)
├── input_data (JSONB)
├── output_data (JSONB)
└── executed_at (TIMESTAMP)
```

## Benefits

✅ **State persistence** - Survives restarts
✅ **Horizontal scaling** - 4+ workers
✅ **Crash recovery** - Resume from last state
✅ **Audit trail** - Complete execution history
✅ **Production-ready** - No memory leaks

## Troubleshooting

### Migration fails
```bash
# Check current revision
alembic current

# Stamp if needed
alembic stamp head

# Retry
alembic upgrade head
```

### Connection issues
```bash
# Verify DATABASE_URL
railway run env | grep DATABASE_URL

# Test connection
railway run psql $DATABASE_URL -c "SELECT 1"
```

### API returns 404
```bash
# Make sure router is registered in app/main.py:
from app.api.v1 import meta_analysis_db

app.include_router(
    meta_analysis_db.router,
    prefix="/api/v1",
    tags=["meta-analysis"],
)
```

## Next Steps

1. **Monitor performance:** Check Railway metrics
2. **Tune connection pool:** Adjust if needed (db/base.py)
3. **Set up backups:** Railway auto-backs up daily
4. **Add monitoring:** Track execution times in agent_executions

## Full Documentation

See `POSTGRESQL_MIGRATION_GUIDE.md` for complete details.
