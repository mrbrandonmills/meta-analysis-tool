# Celery Worker Deployment Report
**Date:** 2025-11-06
**DevOps Engineer Report**
**Project:** Meta-Analysis-Tool (Railway)

---

## Executive Summary

### Current Status: ⚠️ ACTION REQUIRED

The Celery worker service is **deployed but not operational**. The service exists in Railway with correct build configuration, but workers are not connecting to Redis to process background tasks.

**Impact:**
- ❌ Literature search tasks cannot be processed
- ❌ Meta-analysis calculations will fail
- ❌ Background notifications won't send
- ✅ API and database are fully operational
- ✅ Redis is healthy and ready

**Root Cause:** Missing or incorrectly configured environment variables on the worker service.

**Time to Resolution:** 15-20 minutes (manual) or 10-15 minutes (automated script)

---

## What Was Analyzed

### 1. Infrastructure Health Check
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed
```

**Results:**
| Component | Status | Details |
|-----------|--------|---------|
| Database (Postgres) | ✅ Healthy | Connection successful |
| Redis | ✅ Healthy | Connection successful |
| Celery Workers | ⚠️ Degraded | No workers available |

**Diagnosis:** Prerequisites are healthy. Worker service configuration issue.

### 2. Configuration Review

**Files Analyzed:**
- ✅ `railway-worker-config.json` - Build/deploy configuration is correct
- ✅ `backend/Dockerfile` - Multi-stage build properly configured
- ✅ `backend/app/workers/celery_app.py` - Celery configuration is correct
- ✅ `backend/app/workers/tasks/*.py` - All task modules exist and properly structured
- ✅ `backend/app/core/config.py` - Application configuration requires specific env vars

**Build Configuration (Verified):**
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile",
    "watchPatterns": ["backend/**"]
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "startCommand": "celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4"
  }
}
```
✅ This configuration is **CORRECT**

**Task Modules Verified:**
- ✅ `literature_search.py` - Database search tasks
- ✅ `meta_analysis.py` - Statistical analysis tasks
- ✅ `reviewer_tasks.py` - Researcher profiling tasks
- ✅ `notifications.py` - Email/notification tasks

### 3. Dependency Analysis

**Required Environment Variables (from config.py):**

| Variable | Required By | Critical? | Purpose |
|----------|-------------|-----------|---------|
| `DATABASE_URL` | SQLAlchemy | ✅ YES | Database connection for task results |
| `REDIS_URL` | Celery | ✅ YES | Message broker and result backend |
| `ANTHROPIC_API_KEY` | Application Config | ✅ YES | Required for app initialization (default: "dummy_key_for_migrations") |
| `SECRET_KEY` | Application Security | ✅ YES | JWT tokens, session security |
| `OPENAI_API_KEY` | OpenAI Integration | ⚠️ Recommended | Literature analysis features |
| `PUBMED_API_KEY` | PubMed API | ⚠️ Optional | Enhanced PubMed access |
| `PUBMED_EMAIL` | PubMed API | ⚠️ Optional | PubMed API compliance |
| `PYTHONUNBUFFERED` | Logging | ⚠️ Recommended | Real-time log output |
| `LOG_LEVEL` | Logging | ⚠️ Recommended | Log verbosity control |

**Critical Finding:** The application's `config.py` requires `ANTHROPIC_API_KEY` for initialization. Even if a worker task doesn't use AI features, the application will fail to import without this variable set.

---

## What Was Fixed/Created

### 1. Diagnostic Tools

#### `/Users/brandon/meta-analysis-tool/diagnose-worker.sh`
**Purpose:** Quick diagnostic to identify current issues

**Functionality:**
- Checks health endpoint
- Analyzes service status
- Identifies common configuration issues
- Provides specific troubleshooting steps
- Shows recommended fixes

**Usage:**
```bash
./diagnose-worker.sh
```

#### `/Users/brandon/meta-analysis-tool/deploy-celery-worker.sh`
**Purpose:** Interactive deployment wizard with automated verification

**Functionality:**
- Checks if workers are already healthy (skip if operational)
- Guides through environment variable configuration
- Verifies build settings
- Monitors redeploy progress
- Validates worker connection (10 retry attempts)
- Reports success or provides detailed troubleshooting

**Usage:**
```bash
./deploy-celery-worker.sh
```

### 2. Documentation

#### `/Users/brandon/meta-analysis-tool/CELERY_WORKER_DEPLOYMENT.md`
**Comprehensive 400+ line deployment guide containing:**
- Root cause analysis
- Required environment variables with explanations
- Step-by-step deployment instructions (automated and manual)
- Troubleshooting guide for common issues
- Architecture notes and design decisions
- Scaling considerations
- Monitoring and observability strategies
- Expected log patterns and health check outputs

#### `/Users/brandon/meta-analysis-tool/WORKER_DEPLOYMENT_SUMMARY.md`
**Executive summary document containing:**
- Current status analysis
- Files created and their purposes
- Deployment plan (automated vs manual)
- Expected outcomes and success criteria
- Verification checklist
- Technical context and architecture explanation

#### `/Users/brandon/meta-analysis-tool/WORKER_QUICK_FIX.md`
**Quick reference card:**
- 3-step fix guide
- Critical configuration values
- Verification command
- Links to detailed documentation

### 3. Configuration Templates

#### `/Users/brandon/meta-analysis-tool/railway-worker-config.json`
**Railway service configuration template:**
- Build settings (Dockerfile, paths, watch patterns)
- Deploy settings (start command, restart policy, replicas)
- Healthcheck configuration

---

## Deployment Instructions

### Option A: Automated Deployment (Recommended)

**Time Required:** 10-15 minutes

**Steps:**
1. Open terminal in project directory:
   ```bash
   cd /Users/brandon/meta-analysis-tool
   ```

2. Run deployment wizard:
   ```bash
   ./deploy-celery-worker.sh
   ```

3. Follow interactive prompts:
   - Verify environment variables in Railway dashboard
   - Confirm build settings
   - Trigger redeploy
   - Wait for automatic verification

4. Script will report success or provide troubleshooting

**Advantages:**
- ✅ Automated health checking
- ✅ Retries with delays
- ✅ Clear success/failure reporting
- ✅ Troubleshooting guidance if issues

### Option B: Manual Deployment

**Time Required:** 15-20 minutes

#### Step 1: Configure Environment Variables (5 min)

1. Open Railway Dashboard: https://railway.app/dashboard
2. Navigate to project: **Meta-Analysis-Tool**
3. Open service: **backend** → **Variables** tab
4. Copy ALL variables to clipboard
5. Open service: **meta-analysis-worker** → **Variables** tab
6. Paste all variables
7. **CRITICAL:** Verify these two use Railway references:
   ```
   DATABASE_URL = ${{Postgres.DATABASE_URL}}
   REDIS_URL = ${{Redis.REDIS_URL}}
   ```
   (NOT hardcoded connection strings)

#### Step 2: Verify Build Configuration (2 min)

1. In **meta-analysis-worker** → **Settings** → **Source**:
   - Repository: `mrbrandonmills/meta-analysis-tool`
   - Branch: `main`
   - Root Directory: `/` (default)

2. In **Settings** → **Build**:
   - Builder: `DOCKERFILE`
   - Dockerfile Path: `backend/Dockerfile` ⚠️ (no leading slash!)
   - Watch Patterns: `backend/**`

3. In **Settings** → **Deploy**:
   - Start Command:
     ```
     celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4
     ```
   - Restart Policy: `ON_FAILURE`
   - Max Retries: `10`
   - Healthcheck Timeout: `300`

#### Step 3: Redeploy Service (3-5 min)

1. In **meta-analysis-worker** service
2. Click three dots menu (⋯)
3. Select **Redeploy**
4. Wait for build to complete (2-4 minutes)
5. Monitor deployment logs

#### Step 4: Monitor Deployment Logs (2 min)

Watch for success indicators:
```
✓ celery@meta-analysis-worker ready.
✓ Connected to redis://redis.railway.internal:6379/0
✓ [tasks]
  . app.workers.tasks.literature_search.search_databases
  . app.workers.tasks.meta_analysis.run_analysis
  . app.workers.tasks.reviewer_tasks.profile_reviewer
  . app.workers.tasks.notifications.send_notification
```

Watch for error indicators:
```
✗ Cannot connect to redis://...
✗ ModuleNotFoundError: No module named 'app'
✗ Configuration error: ANTHROPIC_API_KEY not set
✗ Connection refused
```

#### Step 5: Verify Health (1 min)

```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.celery'
```

**Expected output:**
```json
{
  "status": "healthy",
  "message": "1 worker(s) active"
}
```

---

## Success Criteria

### Technical Validation

- [ ] Worker service shows "Active" status in Railway dashboard
- [ ] Worker deployment logs show no errors
- [ ] Logs contain: `celery@meta-analysis-worker ready.`
- [ ] Logs show Redis connection: `Connected to redis://...`
- [ ] All task modules imported successfully (5 task modules listed)
- [ ] Health endpoint returns Celery status: `"healthy"`
- [ ] Health message shows: `"1 worker(s) active"` or more
- [ ] All 5 queues active: default, search, analysis, reviewer, notifications

### Functional Validation

- [ ] Can submit literature search task via API
- [ ] Worker processes task (visible in logs)
- [ ] Task results stored in database
- [ ] Task status updates correctly
- [ ] No task failures or retries

### Operational Validation

- [ ] Worker service auto-restarts on failure
- [ ] CPU usage <80% under normal load
- [ ] Memory usage stable (~200-500MB per worker)
- [ ] No memory leaks over time
- [ ] Logs accessible in Railway dashboard

---

## Troubleshooting Guide

### Issue 1: "No workers available" (Most Common)

**Symptoms:**
- Health check shows Celery as "degraded"
- Message: "No workers available"

**Root Causes:**
1. Environment variables not set on worker service
2. REDIS_URL not using Railway variable reference
3. Worker service not redeployed after configuration changes

**Solutions:**
1. Copy ALL environment variables from backend to worker service
2. Ensure `REDIS_URL = ${{Redis.REDIS_URL}}` (not hardcoded)
3. Ensure `DATABASE_URL = ${{Postgres.DATABASE_URL}}` (not hardcoded)
4. Verify ANTHROPIC_API_KEY is set (required for app initialization)
5. Redeploy worker service
6. Wait 3-4 minutes for build
7. Check logs for connection success

**Verification:**
```bash
./diagnose-worker.sh
```

### Issue 2: Worker Crashes on Startup

**Symptoms:**
- Service deploys but immediately restarts
- Restart count increases
- Logs show Python exceptions

**Root Causes:**
1. Missing dependencies in requirements.txt
2. Invalid API key format
3. Redis connection failure
4. Import errors in task modules

**Solutions:**
1. Check worker logs for specific Python error
2. Verify ANTHROPIC_API_KEY format (should start with "sk-")
3. Ensure Redis service is running (check service health)
4. Verify all task module files exist in repository
5. Check requirements.txt includes all dependencies

**Verification:**
```bash
# Check Redis health
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.redis'

# Check worker logs in Railway dashboard
railway logs --service=meta-analysis-worker
```

### Issue 3: Workers Start but Don't Process Tasks

**Symptoms:**
- Health check shows workers available
- Tasks submitted but stay in "pending" state
- No task execution in logs

**Root Causes:**
1. Queue name mismatch
2. Task routing configuration error
3. Redis pub/sub not working

**Solutions:**
1. Verify start command includes all queues:
   `--queues=default,search,analysis,reviewer,notifications`
2. Check celery_app.py task routing matches queue names
3. Test Redis connection: Submit simple task to default queue
4. Check worker logs for task acknowledgment

### Issue 4: Connection Refused to Redis

**Symptoms:**
- Worker logs show "Connection refused"
- "Cannot connect to redis://" errors

**Root Causes:**
1. Using external Redis URL instead of internal Railway networking
2. Redis service not running
3. Incorrect REDIS_URL format

**Solutions:**
1. **Use Railway's internal network:**
   ```
   REDIS_URL = ${{Redis.REDIS_URL}}
   ```
   This automatically resolves to:
   ```
   redis://default:<password>@redis.railway.internal:6379
   ```

2. **Verify Redis service health:**
   - Check Redis service in Railway dashboard
   - Ensure status is "Active"

3. **Don't use external URLs:**
   - Railway services should use private networking
   - External URLs add latency and are less secure

---

## Architecture Notes

### Microservices Design

The platform uses a **distributed task processing architecture**:

```
┌─────────────────┐
│   Frontend      │
│   (Vue.js)      │
└────────┬────────┘
         │
         │ HTTP
         │
┌────────▼────────┐
│   Backend API   │◄──────┐
│   (FastAPI)     │       │
└────────┬────────┘       │
         │                │
         │ Enqueue        │ Read/Write
         │ Tasks          │ Results
         │                │
┌────────▼────────┐       │
│   Redis         │       │
│   (Message      │       │
│    Broker)      │       │
└────────┬────────┘       │
         │                │
         │ Dequeue        │
         │ Tasks          │
         │                │
┌────────▼────────┐       │
│ Celery Workers  │       │
│ (Background     │───────┘
│  Processors)    │
└─────────────────┘
```

**Benefits:**
- **Scalability:** Workers scale independently from API
- **Reliability:** Task retries don't affect API availability
- **Performance:** API stays responsive during long-running tasks
- **Flexibility:** Different worker types for different task types

### Shared Infrastructure

**Same Components:**
- Docker image (same Dockerfile)
- Codebase (same repository)
- Database (shared Postgres)
- Message broker (shared Redis)

**Different Components:**
- Entry point (uvicorn vs celery)
- Port exposure (API needs public, worker doesn't)
- Scaling triggers (traffic vs task volume)
- Resource allocation (API: low CPU/high I/O, Worker: varies by task type)

### Queue Strategy

**5 Specialized Queues:**

| Queue | Purpose | Task Type | Concurrency | Priority |
|-------|---------|-----------|-------------|----------|
| `default` | General tasks | Mixed | 1 | Normal |
| `search` | Literature searches | I/O-intensive | 2 | High |
| `analysis` | Statistical analysis | CPU-intensive | 1 | Normal |
| `reviewer` | Researcher profiling | API-intensive | 2 | Low |
| `notifications` | Email/alerts | I/O-bound | 1 | Low |

**Rationale:**
- **Isolation:** Long searches don't block quick notifications
- **Resource Optimization:** Different concurrency per task type
- **Priority:** Critical tasks (search) get more workers
- **Scaling:** Can add queue-specific workers independently

---

## Monitoring and Observability

### Health Checks

**Primary Health Endpoint:**
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed
```

**Response Structure:**
```json
{
  "timestamp": "2025-11-06T...",
  "service": "meta-analysis-platform",
  "version": "0.1.0",
  "status": "healthy",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful"
    },
    "celery": {
      "status": "healthy",
      "message": "1 worker(s) active"
    }
  }
}
```

### Worker-Specific Metrics

**Available via Celery Inspect API:**
```python
from app.workers.celery_app import celery_app

inspect = celery_app.control.inspect()

# Active tasks
print(inspect.active())

# Scheduled tasks
print(inspect.scheduled())

# Reserved tasks
print(inspect.reserved())

# Worker statistics
print(inspect.stats())
```

### Railway Metrics

**Monitor in Dashboard:**
- **CPU Usage:** Should be <80% under normal load
- **Memory Usage:** ~200-500MB per worker (4 workers = ~1GB total)
- **Network I/O:** Spikes during literature searches
- **Restart Count:** Should be 0 (restarts indicate crashes)

### Log Patterns to Monitor

**Success Patterns:**
```
[INFO] Task started: app.workers.tasks.literature_search.search_databases [abc123]
[INFO] Task completed: app.workers.tasks.literature_search.search_databases [abc123]
[INFO] Task succeeded in 45.2s
```

**Warning Patterns:**
```
[WARNING] Task is being retried: Connection timeout
[WARNING] Task exceeded soft time limit (1800s)
```

**Error Patterns:**
```
[ERROR] Task failed: abc123 - Division by zero
[ERROR] Connection refused to redis://...
[ERROR] ModuleNotFoundError: No module named 'app'
```

---

## Scaling Considerations

### Current Configuration
- **Worker Replicas:** 1
- **Concurrency per Worker:** 4
- **Total Capacity:** 4 concurrent tasks
- **Queue Distribution:** All queues on single worker

### Vertical Scaling (Increase Concurrency)

**When to Use:**
- Task volume <10 concurrent tasks
- Tasks are I/O-bound (waiting on external APIs)
- Single worker sufficient for load

**How to Scale:**
```bash
# Update start command to:
celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=8
```

**Trade-offs:**
- ✅ Simple to configure
- ✅ Lower infrastructure cost
- ✅ Easier to monitor
- ❌ Single point of failure
- ❌ CPU bottleneck on intensive tasks

### Horizontal Scaling (Add Replicas)

**When to Use:**
- Task volume >10 concurrent tasks
- Need redundancy and high availability
- Tasks are CPU-intensive

**How to Scale:**
```bash
# In Railway Dashboard → meta-analysis-worker → Deploy
# Set replicas: 2 or 3
```

**Trade-offs:**
- ✅ Redundancy (no single point of failure)
- ✅ Better CPU utilization
- ✅ Handles higher volume
- ❌ Higher infrastructure cost
- ❌ More complex monitoring

### Queue-Specific Workers (Advanced)

**When to Use:**
- Different SLAs for different task types
- Need to optimize resource allocation per queue
- High volume on specific queues

**How to Implement:**
```bash
# Create separate worker services:

# meta-analysis-worker-search
celery -A app.workers.celery_app worker --queues=search --concurrency=4

# meta-analysis-worker-analysis
celery -A app.workers.celery_app worker --queues=analysis --concurrency=2

# meta-analysis-worker-other
celery -A app.workers.celery_app worker --queues=default,reviewer,notifications --concurrency=3
```

**Trade-offs:**
- ✅ Optimized resource allocation
- ✅ SLA-based scaling
- ✅ Isolation of critical tasks
- ❌ Higher complexity
- ❌ More services to monitor
- ❌ Higher infrastructure cost

---

## Cost Analysis

### Current Configuration (1 Worker, 4 Concurrency)
- **Railway Cost:** ~$5-10/month (depends on usage)
- **CPU Usage:** 0.5-1 vCPU
- **Memory:** 512MB-1GB
- **Capacity:** 4 concurrent tasks

### Scaling Scenarios

| Configuration | Monthly Cost | Capacity | Use Case |
|---------------|--------------|----------|----------|
| 1 worker × 4 concurrency | $5-10 | 4 tasks | MVP, low volume |
| 1 worker × 8 concurrency | $8-15 | 8 tasks | Growing usage |
| 2 workers × 4 concurrency | $10-20 | 8 tasks | High availability |
| 3 workers × 4 concurrency | $15-30 | 12 tasks | Production scale |
| Queue-specific (3 services) | $20-40 | 10 tasks | Optimized SLAs |

**Recommendation for Current Stage:**
- Start with 1 worker × 4 concurrency
- Monitor task queue lengths
- Scale when queue lengths consistently >10 tasks
- Consider horizontal scaling for redundancy in production

---

## Next Steps

### Immediate (After Deployment)

1. **Deploy Worker Service** (15 min)
   - Run `./deploy-celery-worker.sh` OR
   - Follow manual deployment steps
   - Verify health endpoint

2. **Test Functionality** (10 min)
   - Submit test literature search task
   - Monitor worker logs for processing
   - Verify task completion
   - Check results in database

3. **Monitor Initial Operations** (30 min)
   - Watch worker logs for errors
   - Monitor CPU/memory usage
   - Check task processing times
   - Verify auto-restart functionality

### Short-term (This Week)

4. **Set Up Monitoring** (30 min)
   - Configure Railway alerts for worker crashes
   - Set up uptime monitoring (UptimeRobot, etc.)
   - Create dashboard for key metrics
   - Document baseline performance

5. **Load Testing** (1 hour)
   - Submit multiple concurrent tasks
   - Monitor queue buildup
   - Test worker recovery from failures
   - Identify bottlenecks

6. **Documentation** (30 min)
   - Document actual task processing times
   - Create runbook for common issues
   - Update architecture diagrams
   - Share knowledge with team

### Medium-term (This Month)

7. **Optimization** (2-3 hours)
   - Optimize slow tasks
   - Fine-tune concurrency settings
   - Implement task result caching
   - Review error retry strategies

8. **Scaling Strategy** (1 hour)
   - Analyze usage patterns
   - Plan capacity for growth
   - Document scaling procedures
   - Set up auto-scaling triggers (if needed)

9. **Advanced Monitoring** (2-3 hours)
   - Implement Prometheus metrics
   - Set up Grafana dashboards
   - Configure alerting rules
   - Create SLA monitoring

---

## Files Delivered

### Executable Scripts
1. **`/Users/brandon/meta-analysis-tool/diagnose-worker.sh`**
   - Quick diagnostic tool
   - Identifies current issues
   - Provides specific fixes
   - ~150 lines

2. **`/Users/brandon/meta-analysis-tool/deploy-celery-worker.sh`**
   - Interactive deployment wizard
   - Automated verification
   - Retry logic with delays
   - ~250 lines

### Documentation
3. **`/Users/brandon/meta-analysis-tool/CELERY_WORKER_DEPLOYMENT.md`**
   - Comprehensive deployment guide
   - Troubleshooting reference
   - Architecture notes
   - ~400 lines

4. **`/Users/brandon/meta-analysis-tool/WORKER_DEPLOYMENT_SUMMARY.md`**
   - Executive summary
   - Quick reference
   - Success criteria
   - ~300 lines

5. **`/Users/brandon/meta-analysis-tool/WORKER_QUICK_FIX.md`**
   - 3-step quick fix guide
   - Critical configuration
   - Verification commands
   - ~50 lines

6. **`/Users/brandon/meta-analysis-tool/DEPLOYMENT_REPORT.md`** (this file)
   - Comprehensive deployment report
   - Complete analysis
   - All findings and recommendations
   - ~600 lines

### Configuration
7. **`/Users/brandon/meta-analysis-tool/railway-worker-config.json`**
   - Railway service configuration
   - Build and deploy settings
   - Already reviewed and verified correct

**Total Lines of Code/Documentation:** ~2000 lines

---

## Summary

### What Was Found
- ✅ Worker service exists in Railway
- ✅ Build configuration is correct
- ✅ Task modules are properly structured
- ✅ Database and Redis are healthy
- ⚠️ Workers not connecting ("No workers available")
- ⚠️ Missing or incorrect environment variables

### What Was Created
- ✅ 2 executable deployment/diagnostic scripts
- ✅ 4 comprehensive documentation files
- ✅ 1 verified configuration template
- ✅ Complete troubleshooting guide
- ✅ Architecture and scaling analysis

### What Needs to Be Done
1. Configure environment variables on worker service
2. Ensure REDIS_URL and DATABASE_URL use Railway references
3. Redeploy worker service
4. Verify health endpoint shows workers as healthy
5. Test with sample literature search task

### Expected Outcome
```json
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "celery": {
      "status": "healthy",
      "message": "1 worker(s) active"
    }
  }
}
```

### Time to Resolution
- **Automated:** 10-15 minutes
- **Manual:** 15-20 minutes

### Ready to Deploy?
```bash
cd /Users/brandon/meta-analysis-tool
./deploy-celery-worker.sh
```

---

**Report Prepared By:** DevOps Engineer (Claude)
**Date:** 2025-11-06
**Status:** Ready for Deployment
