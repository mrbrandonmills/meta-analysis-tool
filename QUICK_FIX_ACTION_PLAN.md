# QUICK FIX ACTION PLAN
## Unblock Meta-Analysis Platform in 4-6 Hours

**Goal:** Fix the 3 critical infrastructure bugs to unblock all testing and make the platform usable.

---

## 🚨 Critical Path: 3 Fixes Required

### Fix 1: Run Database Migrations (BUG-001)
**Time:** 2 hours
**Difficulty:** Easy
**Impact:** Unblocks authentication, enables all user operations

#### Problem
The `users` table doesn't exist in the PostgreSQL database. Alembic migrations have not been run.

#### Evidence
```
POST /api/v1/auth/register
Response: 500 Internal Server Error
Error: "InvalidRequestError"
```

#### Solution

**Option A: Via Railway CLI** (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to project
railway link

# Run migrations
railway run alembic upgrade head

# Verify
railway run python -c "from app.db.session import sync_engine; from sqlalchemy import inspect; print(inspect(sync_engine).get_table_names())"
```

**Option B: Update Start Command in Railway Dashboard**
```
Old: uvicorn app.main:app --host 0.0.0.0 --port $PORT
New: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Then redeploy.

**Option C: Manual Database Connection**
```bash
# Get database URL from Railway
railway variables

# Connect and run migration
DATABASE_URL="postgresql://..." alembic upgrade head
```

#### Verification
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User","institution":"Test Uni"}'

# Should return: 201 Created (or 400 if email exists)
# Should NOT return: 500 Internal Server Error
```

---

### Fix 2: Deploy Redis Service (BUG-002)
**Time:** 30 minutes
**Difficulty:** Easy
**Impact:** Enables rate limiting, session management, caching

#### Problem
Redis service not deployed. Health check shows "Redis URL must specify one of the following schemes".

#### Evidence
```
GET /api/v1/health/detailed
Response: {"checks": {"redis": {"status": "unhealthy"}}}
```

#### Solution

**Option A: Add Redis Plugin in Railway** (Recommended)
```bash
# Via Railway CLI
railway add

# Select: Redis
# This will create a Redis instance and set REDIS_URL automatically
```

**Option B: Via Railway Dashboard**
1. Go to your project
2. Click "+ New"
3. Select "Database"
4. Choose "Redis"
5. Railway will automatically set `${{REDIS.REDIS_URL}}` in your service

**Option C: Use External Redis (Upstash)**
```bash
# Sign up at upstash.com (free tier)
# Create Redis database
# Copy connection URL
# Add to Railway environment variables:
REDIS_URL=rediss://default:password@us1-example.upstash.io:6379
```

#### Verification
```bash
curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.redis'

# Should return:
# {
#   "status": "healthy",
#   "message": "Redis connection successful"
# }
```

---

### Fix 3: Deploy Celery Worker Service (BUG-003)
**Time:** 2 hours
**Difficulty:** Medium
**Impact:** Enables background job processing, required for meta-analyses

#### Problem
No Celery workers are running. Meta-analyses require async job processing.

#### Evidence
```
GET /api/v1/health/detailed
Response: {"checks": {"celery": {"status": "unknown", "message": "Connection refused"}}}
```

#### Solution

**Railway requires 2 separate services:**

**Step 1: Current "Web" Service**
```
Name: meta-analysis-tool-production
Start Command: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Step 2: Create New "Worker" Service**

**Via Railway Dashboard:**
1. Go to project
2. Click "+ New"
3. Select "Service"
4. Choose "GitHub Repo"
5. Select same repository
6. Configure:
   ```
   Name: meta-analysis-worker
   Root Directory: backend
   Start Command: celery -A app.workers.celery_app worker -l info
   ```
7. Add ALL environment variables (copy from web service):
   - `DATABASE_URL`
   - `REDIS_URL`
   - `ANTHROPIC_API_KEY`
   - `SECRET_KEY`
   - etc.
8. Deploy

**Via Railway CLI:**
```bash
# In Railway dashboard, manually create service
# Then configure via CLI:
railway service

# Select: meta-analysis-worker
# Set start command
railway env set START_COMMAND="celery -A app.workers.celery_app worker -l info"

# Copy environment variables from web service
railway env copy --from meta-analysis-tool-production --to meta-analysis-worker
```

#### Verification
```bash
curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.celery'

# Should return:
# {
#   "status": "healthy",
#   "workers": 1,
#   "active_tasks": 0
# }
```

---

## Execution Checklist

### Phase 1: Preparation (15 minutes)
- [ ] Install Railway CLI: `npm install -g @railway/cli`
- [ ] Login: `railway login`
- [ ] Link project: `railway link`
- [ ] Check current status: `railway status`
- [ ] List environment variables: `railway variables`

### Phase 2: Fix Database Migrations (1 hour)
- [ ] Run migrations: `railway run alembic upgrade head`
- [ ] Verify tables created: Check users table exists
- [ ] Test registration: Try creating a user
- [ ] Test login: Try logging in with created user
- [ ] Confirm 201/200 responses (not 500)

### Phase 3: Add Redis (30 minutes)
- [ ] Add Redis plugin: `railway add` → select Redis
- [ ] Verify REDIS_URL set: `railway variables | grep REDIS`
- [ ] Redeploy web service: `railway up`
- [ ] Wait for deployment (2-3 minutes)
- [ ] Check health: `/api/v1/health/detailed`
- [ ] Confirm Redis status: "healthy"

### Phase 4: Add Celery Worker (2 hours)
- [ ] Create new service in Railway dashboard
- [ ] Name: "meta-analysis-worker"
- [ ] Link to same repository
- [ ] Set root directory: `backend`
- [ ] Set start command: `celery -A app.workers.celery_app worker -l info`
- [ ] Copy all environment variables from web service
- [ ] Deploy worker service
- [ ] Wait for deployment (3-5 minutes)
- [ ] Check health: `/api/v1/health/detailed`
- [ ] Confirm Celery status: "healthy"

### Phase 5: Verification (30 minutes)
- [ ] Run comprehensive health check
- [ ] Test user registration (should succeed)
- [ ] Test user login (should succeed)
- [ ] Test creating meta-analysis project
- [ ] Check background job queued
- [ ] Monitor Celery logs for job processing
- [ ] Verify all health checks green

---

## Post-Fix Testing

Once all 3 fixes are deployed, run comprehensive tests:

```bash
# Clone or navigate to repo
cd /Users/brandon/meta-analysis-tool

# Run comprehensive test suite
python3 test_execution_comprehensive.py

# Expected results:
# - Test 7 (Authentication): PASS
# - Test 1 (Meta-Analysis): PARTIAL (may fail on StatisticalAgent)
# - Test 9 (Error Handling): PASS
# - Test 10 (Background Jobs): PASS
```

---

## Expected Results After Fixes

### Before Fixes
```
Total Tests: 10
Passed: 3 (30%)
Failed: 1 (10%)
Blocked: 6 (60%)
Production Ready: NO
```

### After Fixes
```
Total Tests: 10
Passed: 7+ (70%+)
Failed: 0-2 (0-20%) [may fail on unimplemented features]
Blocked: 1-3 (10-30%) [only StatisticalAgent, SearchAgent]
Production Ready: CONDITIONAL (alpha testing ready)
```

---

## Success Criteria

✅ **Fix is successful when:**
1. User registration returns 201 (not 500)
2. User login returns access token (not 500)
3. Redis health check shows "healthy"
4. Celery health check shows workers running
5. Can create meta-analysis project
6. Background job is queued
7. All infrastructure health checks green

---

## Rollback Plan

If something breaks:

```bash
# Revert to previous deployment
railway rollback

# Or revert specific service
railway service select meta-analysis-tool-production
railway rollback
```

---

## Common Issues

### Issue 1: Migration fails with "relation already exists"
**Solution:** The table already exists. Check if users table has data.
```bash
railway run python -c "from app.db.session import sync_engine; from sqlalchemy import text; print(sync_engine.execute(text('SELECT COUNT(*) FROM users')).scalar())"
```

### Issue 2: Redis still shows unhealthy after adding
**Solution:** Restart the web service
```bash
railway service select meta-analysis-tool-production
railway restart
```

### Issue 3: Celery worker crashes on startup
**Solution:** Check environment variables are copied correctly
```bash
railway service select meta-analysis-worker
railway variables
# Compare with web service variables
```

### Issue 4: Celery can't connect to Redis
**Solution:** Ensure both services can access Redis
- Check REDIS_URL is set in worker service
- Check Redis service is running
- Check network connectivity between services

---

## Timeline

| Task | Duration | Cumulative |
|------|----------|------------|
| Install Railway CLI | 5 min | 5 min |
| Login and link | 5 min | 10 min |
| Run migrations | 30 min | 40 min |
| Verify auth works | 15 min | 55 min |
| Add Redis plugin | 10 min | 1h 5min |
| Redeploy and verify | 10 min | 1h 15min |
| Create worker service | 30 min | 1h 45min |
| Configure worker | 20 min | 2h 5min |
| Deploy worker | 10 min | 2h 15min |
| Verify Celery | 15 min | 2h 30min |
| Run comprehensive tests | 30 min | 3h |
| Debug any issues | 1h buffer | 4h |

**Total Estimated Time:** 3-4 hours (with buffer: 4-6 hours)

---

## Next Steps After Fixes

Once infrastructure is fixed:

1. **Implement StatisticalAgent** (2-3 weeks)
   - Cohen's d calculation
   - Random-effects pooling
   - Heterogeneity tests
   - Forest plot generation

2. **Integrate Real Search APIs** (1 week)
   - PubMed E-utilities
   - arXiv API
   - Europe PMC
   - CORE API

3. **Academic Validation** (1 week)
   - Compare with published meta-analyses
   - Peer review
   - Quality assessment

4. **Production Deployment** (6-8 weeks total)

---

**Action:** Start with Fix 1 (database migrations). This will immediately unblock authentication and enable 70% of functionality.

**Report By:** Integration Test QA Agent
**Date:** November 5, 2025
**Priority:** URGENT - CRITICAL BLOCKERS
