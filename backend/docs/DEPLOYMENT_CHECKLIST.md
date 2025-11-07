# PostgreSQL Migration - Deployment Checklist

## Pre-Deployment Checklist

### Code Quality
- [x] SQLAlchemy models created and tested
  - File: `app/models/meta_analysis.py`
  - Models: MetaAnalysis, CoordinatorState, AgentExecution
  - Syntax: ✅ Verified

- [x] Alembic migration script created
  - File: `alembic/versions/004_add_meta_analysis_tables.py`
  - Revision: 004 (follows 003)
  - Syntax: ✅ Verified

- [x] Database-backed API implemented
  - File: `app/api/v1/meta_analysis_db.py`
  - All endpoints migrated
  - Syntax: ✅ Verified

- [x] Dockerfile updated for multiple workers
  - File: `Dockerfile`
  - Workers: 4 (changed from 1)

- [x] Models exported in __init__.py
  - File: `app/models/__init__.py`
  - Exports: MetaAnalysis, CoordinatorState, AgentExecution, MetaAnalysisStatus

- [x] User model relationship added
  - File: `app/models/user.py`
  - Relationship: meta_analyses

### Documentation
- [x] Full migration guide created
  - File: `docs/POSTGRESQL_MIGRATION_GUIDE.md`
  - Length: ~700 lines

- [x] SQL schema reference created
  - File: `docs/DATABASE_SCHEMA.sql`
  - Length: ~400 lines

- [x] Quick start guide created
  - File: `docs/MIGRATION_QUICKSTART.md`
  - Length: Single page

- [x] Implementation summary created
  - File: `docs/IMPLEMENTATION_SUMMARY.md`
  - Length: Comprehensive

---

## Railway Setup Checklist

### Step 1: PostgreSQL Database
- [ ] Login to Railway dashboard
  ```bash
  railway login
  ```

- [ ] Add PostgreSQL database to project
  - Dashboard → Your Project → New → Database → PostgreSQL
  - Railway auto-provisions database
  - DATABASE_URL environment variable created

- [ ] Verify DATABASE_URL is set
  ```bash
  railway run env | grep DATABASE_URL
  ```

### Step 2: Database Migration
- [ ] Run migration on Railway
  ```bash
  cd backend
  railway run alembic upgrade head
  ```

- [ ] Verify tables created
  ```bash
  railway run psql $DATABASE_URL -c "\dt"
  ```

  Expected tables:
  - meta_analyses
  - coordinator_states
  - agent_executions

- [ ] Verify indexes created
  ```bash
  railway run psql $DATABASE_URL -c "\di"
  ```

### Step 3: Application Configuration
- [ ] Update router in `app/main.py` (if needed)
  ```python
  from app.api.v1 import meta_analysis_db

  app.include_router(
      meta_analysis_db.router,
      prefix="/api/v1",
      tags=["meta-analysis"],
  )
  ```

- [ ] Verify start.sh includes migration
  ```bash
  # Should run: alembic upgrade head
  cat backend/start.sh
  ```

---

## Deployment Checklist

### Step 1: Commit Changes
- [ ] Stage all changes
  ```bash
  git add .
  ```

- [ ] Review changes
  ```bash
  git status
  git diff --cached
  ```

- [ ] Commit with descriptive message
  ```bash
  git commit -m "Migrate to PostgreSQL for production-grade persistence

  - Add MetaAnalysis, CoordinatorState, AgentExecution models
  - Create Alembic migration 004 for meta-analysis tables
  - Implement database-backed API (meta_analysis_db.py)
  - Update Dockerfile to support 4 workers
  - Add comprehensive documentation

  This enables:
  - State persistence across restarts
  - Horizontal scaling with multiple workers
  - Complete audit trail of executions
  - Crash recovery capabilities"
  ```

### Step 2: Deploy to Railway
- [ ] Push to Railway
  ```bash
  git push railway main
  ```

- [ ] Monitor deployment logs
  ```bash
  railway logs
  ```

- [ ] Wait for successful deployment
  - Look for: "Application started successfully"
  - Look for: "Uvicorn running on 0.0.0.0:8000"

### Step 3: Verify Deployment
- [ ] Check application health
  ```bash
  curl https://your-app.railway.app/api/v1/health
  ```

- [ ] Check database connection
  ```bash
  railway run psql $DATABASE_URL -c "SELECT version()"
  ```

- [ ] Verify worker count
  ```bash
  railway logs | grep "Started parent process"
  # Should show 4 worker processes
  ```

---

## Testing Checklist

### API Endpoint Tests

#### 1. Create Meta-Analysis
- [ ] Test endpoint
  ```bash
  curl -X POST https://your-app.railway.app/api/v1/meta-analysis/create \
    -H "Content-Type: application/json" \
    -d '{
      "research_question": "Test question for deployment",
      "topic": "Deployment Test",
      "inclusion_criteria": ["RCT"],
      "exclusion_criteria": ["Non-English"],
      "databases": ["pubmed"]
    }'
  ```

- [ ] Verify response contains:
  - id (UUID)
  - status: "workflow_created"
  - workflow object

- [ ] Verify database record created
  ```bash
  railway run psql $DATABASE_URL -c \
    "SELECT id, topic, status FROM meta_analyses ORDER BY created_at DESC LIMIT 1"
  ```

#### 2. Get Status
- [ ] Test endpoint (use ID from step 1)
  ```bash
  curl https://your-app.railway.app/api/v1/meta-analysis/status/{analysis_id}
  ```

- [ ] Verify response contains:
  - id
  - topic
  - status
  - research_question
  - timestamps

#### 3. Execute Meta-Analysis
- [ ] Test endpoint (use ID from step 1)
  ```bash
  curl -X POST https://your-app.railway.app/api/v1/meta-analysis/execute/{analysis_id}
  ```

- [ ] Verify response contains:
  - analysis_id
  - status: "screening" or "in_progress"
  - search_results
  - screening_results
  - credibility_results

- [ ] Verify agent executions logged
  ```bash
  railway run psql $DATABASE_URL -c \
    "SELECT agent_name, agent_role, status FROM agent_executions WHERE analysis_id = '{analysis_id}'"
  ```

#### 4. Get Audit Trail
- [ ] Test endpoint
  ```bash
  curl https://your-app.railway.app/api/v1/meta-analysis/audit/{analysis_id}
  ```

- [ ] Verify response contains:
  - analysis_id
  - total_executions (should be > 0)
  - executions array with agent details

### Database Integrity Tests

#### 1. Foreign Key Constraints
- [ ] Test cascade deletion
  ```sql
  -- Verify foreign keys exist
  SELECT
      tc.constraint_name,
      tc.table_name,
      kcu.column_name,
      ccu.table_name AS foreign_table_name
  FROM information_schema.table_constraints AS tc
  JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
  JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
  WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name IN ('meta_analyses', 'coordinator_states', 'agent_executions');
  ```

#### 2. Index Usage
- [ ] Verify indexes are being used
  ```sql
  SELECT
      schemaname,
      tablename,
      indexname,
      idx_scan as scans
  FROM pg_stat_user_indexes
  WHERE schemaname = 'public'
    AND tablename IN ('meta_analyses', 'coordinator_states', 'agent_executions')
  ORDER BY idx_scan DESC;
  ```

#### 3. Table Sizes
- [ ] Check table sizes
  ```sql
  SELECT
      tablename,
      pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
  FROM pg_tables
  WHERE schemaname = 'public'
    AND tablename IN ('meta_analyses', 'coordinator_states', 'agent_executions');
  ```

### Performance Tests

#### 1. Connection Pool
- [ ] Monitor connection count
  ```sql
  SELECT count(*) FROM pg_stat_activity WHERE datname = current_database();
  ```

- [ ] Verify connections < pool limit
  - Should be < 40 (10 pool + 20 overflow × 1 worker)
  - With 4 workers: < 120 connections max

#### 2. Query Performance
- [ ] Check slow queries
  ```sql
  SELECT
      query,
      calls,
      mean_exec_time,
      max_exec_time
  FROM pg_stat_statements
  WHERE query LIKE '%meta_analyses%'
  ORDER BY mean_exec_time DESC
  LIMIT 10;
  ```

#### 3. Load Test (Optional)
- [ ] Run concurrent requests
  ```bash
  # Install apache bench
  # brew install httpd (macOS)
  # apt-get install apache2-utils (Linux)

  ab -n 100 -c 10 -H "Content-Type: application/json" \
    -p test_request.json \
    https://your-app.railway.app/api/v1/meta-analysis/create
  ```

---

## Post-Deployment Checklist

### Monitoring Setup
- [ ] Set up database monitoring
  - Railway provides built-in metrics
  - Monitor CPU, memory, disk usage

- [ ] Set up application logging
  - Configure log retention
  - Set up log aggregation (optional)

- [ ] Configure alerts
  - Database connection failures
  - High query execution times
  - Application errors

### Backup Verification
- [ ] Verify automatic backups enabled
  - Railway enables daily backups by default
  - Check backup retention policy

- [ ] Test backup restore (optional)
  ```bash
  # Create manual backup
  railway run pg_dump $DATABASE_URL > backup.sql

  # Test restore to local database
  psql local_test_db < backup.sql
  ```

### Documentation Updates
- [ ] Update README.md with new database requirements
- [ ] Add environment variable documentation
- [ ] Update deployment instructions
- [ ] Create runbook for common operations

---

## Rollback Checklist

If issues arise, follow this rollback procedure:

### Step 1: Assess Impact
- [ ] Check error logs
  ```bash
  railway logs --tail 100
  ```

- [ ] Check database status
  ```bash
  railway run psql $DATABASE_URL -c "SELECT 1"
  ```

- [ ] Identify root cause
  - Database connection issues?
  - Migration errors?
  - Application bugs?

### Step 2: Quick Fix (if possible)
- [ ] Hot fix for minor issues
  ```bash
  # Fix code
  git add .
  git commit -m "Hot fix for [issue]"
  git push railway main
  ```

### Step 3: Full Rollback (if needed)
- [ ] Revert code changes
  ```bash
  git revert HEAD
  git push railway main
  ```

- [ ] Rollback database migration
  ```bash
  railway run alembic downgrade -1
  ```

- [ ] Update Dockerfile to 1 worker
  ```dockerfile
  CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --app-dir /app
  ```

- [ ] Redeploy
  ```bash
  git commit -am "Rollback to in-memory state"
  git push railway main
  ```

### Step 4: Post-Rollback
- [ ] Verify application is working
- [ ] Document rollback reason
- [ ] Create issue for investigation
- [ ] Plan remediation

---

## Success Criteria

The deployment is successful if:

- ✅ All API endpoints respond correctly
- ✅ Database records are created and persisted
- ✅ State survives application restart
- ✅ Multiple workers are running (4)
- ✅ Audit trail logs all executions
- ✅ No database connection errors
- ✅ Response times are acceptable (< 500ms for simple queries)
- ✅ No memory leaks observed
- ✅ Backup system is functional

---

## Post-Deployment Actions

### Week 1
- [ ] Monitor error rates daily
- [ ] Check database growth rate
- [ ] Review audit trail for anomalies
- [ ] Optimize slow queries if identified

### Week 2
- [ ] Review performance metrics
- [ ] Tune connection pool if needed
- [ ] Archive old agent_executions if table is large
- [ ] Update documentation based on learnings

### Month 1
- [ ] Analyze usage patterns
- [ ] Consider implementing Redis caching
- [ ] Plan Celery integration for background tasks
- [ ] Evaluate need for read replicas

---

## Support & Resources

### Documentation
- Full guide: `docs/POSTGRESQL_MIGRATION_GUIDE.md`
- Quick start: `docs/MIGRATION_QUICKSTART.md`
- SQL schema: `docs/DATABASE_SCHEMA.sql`
- Implementation: `docs/IMPLEMENTATION_SUMMARY.md`

### Railway Resources
- [Railway PostgreSQL Documentation](https://docs.railway.app/databases/postgresql)
- [Railway Environment Variables](https://docs.railway.app/develop/variables)
- [Railway Deployments](https://docs.railway.app/deploy/deployments)

### SQLAlchemy Resources
- [Async SQLAlchemy](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
- [Alembic Migrations](https://alembic.sqlalchemy.org/en/latest/)

---

## Final Sign-Off

- [ ] All checklist items completed
- [ ] Testing successful
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Team notified of deployment

**Deployment Date:** _____________
**Deployed By:** _____________
**Sign-Off:** _____________

---

**Status:** Ready for Deployment ✅
