# Celery Worker Deployment Summary

## Current Status

**Date:** 2025-11-06
**Service:** meta-analysis-worker (Railway)
**Status:** ⚠️ **DEGRADED** - "No workers available"

### Health Check Results
```
✅ Database: healthy
✅ Redis: healthy
⚠️  Celery: degraded - No workers available
```

---

## What Was Found

### 1. Root Cause Identified

The Celery worker service is **deployed but not connecting to Redis**. This is the classic "service exists but workers not running" scenario.

**Symptoms:**
- Worker service shows in Railway dashboard
- Build configuration appears correct
- Start command is configured
- BUT: Health endpoint reports "No workers available"

**Diagnosis:**
The worker service likely has one or more of these issues:
1. **Missing environment variables** (most common)
2. **Incorrect REDIS_URL** (not using Railway's variable reference)
3. **Service needs redeploy** after configuration changes
4. **Import errors** due to missing API keys (ANTHROPIC_API_KEY)

### 2. Current Configuration Analysis

**Reviewed Files:**
- ✅ `railway-worker-config.json` - Correct build/deploy settings
- ✅ `backend/Dockerfile` - Multi-stage build is proper
- ✅ `backend/app/workers/celery_app.py` - Celery config is correct
- ✅ All task modules exist and properly structured

**Configuration Verified:**
- ✅ Dockerfile path: `backend/Dockerfile` ✓
- ✅ Start command: Correct Celery worker command ✓
- ✅ Queues configured: default, search, analysis, reviewer, notifications ✓
- ✅ Concurrency: 4 workers ✓

**Missing/Unverified:**
- ❓ Environment variables on worker service (cannot verify remotely)
- ❓ Whether worker service has been redeployed recently
- ❓ Worker logs (need Railway dashboard access to view)

---

## What Needs to Be Fixed

### Critical Actions Required

#### 1. Configure Environment Variables ⚠️ CRITICAL

The worker service **MUST** have these environment variables:

```bash
# Essential (Worker won't start without these)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
ANTHROPIC_API_KEY=<your-api-key>
SECRET_KEY=<your-secret-key>

# Recommended (For full functionality)
OPENAI_API_KEY=<your-openai-key>
PUBMED_API_KEY=<your-pubmed-key>
PUBMED_EMAIL=<your-email>

# Operational (For better logging/performance)
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
```

**Why Each is Required:**

| Variable | Why It's Required |
|----------|-------------------|
| `DATABASE_URL` | Worker tasks need database access to store results, update task status, and retrieve user data |
| `REDIS_URL` | Celery broker/backend - worker **cannot start** without valid Redis connection |
| `ANTHROPIC_API_KEY` | Application config imports fail without this (even if task doesn't use AI) |
| `SECRET_KEY` | Required for application security, JWT validation, and session management |
| `OPENAI_API_KEY` | Optional, but needed for OpenAI-powered features (literature analysis) |
| `PYTHONUNBUFFERED` | Ensures logs appear in real-time in Railway dashboard |

**How to Fix:**
1. Open Railway Dashboard: https://railway.app/dashboard
2. Navigate to: **Meta-Analysis-Tool** → **meta-analysis-worker**
3. Click: **Variables** tab
4. Copy **ALL** variables from **backend** service
5. Pay special attention to:
   - `REDIS_URL` must be `${{Redis.REDIS_URL}}` (Railway variable reference)
   - `DATABASE_URL` must be `${{Postgres.DATABASE_URL}}` (Railway variable reference)
   - API keys must be copied exactly (no extra spaces)

#### 2. Verify Build Settings

**Expected Configuration:**
```
Source:
  Repository: mrbrandonmills/meta-analysis-tool
  Branch: main
  Root Directory: / (default)

Build:
  Builder: DOCKERFILE
  Dockerfile Path: backend/Dockerfile
  Watch Patterns: backend/**

Deploy:
  Start Command: celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4
  Restart Policy: ON_FAILURE
  Max Retries: 10
  Healthcheck Timeout: 300
```

**How to Verify:**
1. Railway Dashboard → **meta-analysis-worker** → **Settings**
2. Check **Source** section
3. Check **Build** section
4. Check **Deploy** section

⚠️ **Common Mistake:** Dockerfile path with leading slash (`/backend/Dockerfile` instead of `backend/Dockerfile`)

#### 3. Redeploy Worker Service

After configuring environment variables:

1. Railway Dashboard → **meta-analysis-worker**
2. Click three dots menu (⋯)
3. Select **Redeploy**
4. Wait 2-4 minutes for build and deployment
5. Monitor logs for successful startup

**Expected Log Messages:**
```
✓ celery@meta-analysis-worker ready.
✓ Connected to redis://redis.railway.internal:6379/0
✓ [tasks]
  . app.workers.tasks.literature_search.search_databases
  . app.workers.tasks.meta_analysis.run_analysis
  . app.workers.tasks.reviewer_tasks.profile_reviewer
  . app.workers.tasks.notifications.send_notification
```

#### 4. Verify Worker Connection

After redeploy, check health:

```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.celery'
```

**Expected Output:**
```json
{
  "status": "healthy",
  "message": "1 worker(s) active"
}
```

---

## Files Created for You

### 1. `/Users/brandon/meta-analysis-tool/diagnose-worker.sh`
**Purpose:** Quick diagnostic script to check current status and identify issues

**Usage:**
```bash
cd /Users/brandon/meta-analysis-tool
./diagnose-worker.sh
```

**What It Does:**
- Checks health endpoint
- Analyzes current status
- Lists common issues
- Provides specific fixes
- Shows next steps

### 2. `/Users/brandon/meta-analysis-tool/deploy-celery-worker.sh`
**Purpose:** Interactive deployment wizard with verification

**Usage:**
```bash
cd /Users/brandon/meta-analysis-tool
./deploy-celery-worker.sh
```

**What It Does:**
- Checks if workers are already healthy (exits if yes)
- Guides through environment variable setup
- Verifies build configuration
- Triggers redeploy
- Monitors worker connection (10 attempts)
- Reports success or provides troubleshooting

### 3. `/Users/brandon/meta-analysis-tool/CELERY_WORKER_DEPLOYMENT.md`
**Purpose:** Comprehensive deployment guide and troubleshooting reference

**Contains:**
- Root cause analysis
- Step-by-step deployment instructions
- Environment variable requirements
- Troubleshooting guide
- Architecture notes
- Scaling considerations
- Monitoring strategies

---

## Deployment Plan

### Option A: Automated (Recommended)

```bash
cd /Users/brandon/meta-analysis-tool
./deploy-celery-worker.sh
```

This script will:
1. ✅ Check current health (skip if already healthy)
2. 📋 Show environment variable checklist
3. ⚙️ Guide through configuration verification
4. 🚀 Trigger redeploy
5. 📊 Monitor worker connection
6. ✅ Confirm success or show troubleshooting

### Option B: Manual

1. **Configure Variables** (5 minutes)
   - Railway Dashboard → meta-analysis-worker → Variables
   - Copy all variables from backend service
   - Ensure REDIS_URL and DATABASE_URL use Railway references

2. **Verify Settings** (2 minutes)
   - Check Build section: Dockerfile path
   - Check Deploy section: Start command

3. **Redeploy** (3-5 minutes)
   - Click ⋯ menu → Redeploy
   - Wait for build to complete

4. **Monitor** (2 minutes)
   - Watch deployment logs
   - Check for "celery@... ready"
   - Verify health endpoint

**Total Time:** ~15 minutes

---

## Expected Outcomes

### Success Scenario

**Health Check:**
```json
{
  "timestamp": "2025-11-06T...",
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

**Worker Logs:**
```
[INFO] celery@meta-analysis-worker ready.
[INFO] Connected to redis://redis.railway.internal:6379/0
[INFO] Task started: app.workers.tasks.literature_search.search_databases
[INFO] Task completed: app.workers.tasks.literature_search.search_databases
```

**System Ready For:**
- ✅ Literature search task submission
- ✅ Meta-analysis calculations
- ✅ Reviewer profiling
- ✅ Background notifications
- ✅ Production workloads

### Failure Scenarios

#### Scenario 1: Still "No workers available" after redeploy

**Likely Cause:** Missing or incorrect environment variables

**Fix:**
1. Check worker logs in Railway for specific error
2. Most common: "Configuration error: ANTHROPIC_API_KEY not set"
3. Verify all variables are copied from backend service
4. Ensure no typos in variable names
5. Redeploy again after fixing

#### Scenario 2: Worker crashes on startup

**Likely Cause:** Redis connection failure or import errors

**Fix:**
1. Check REDIS_URL uses `${{Redis.REDIS_URL}}` format
2. Verify Redis service is running (check service health)
3. Check worker logs for Python import errors
4. Ensure all dependencies in requirements.txt

#### Scenario 3: Workers start but don't process tasks

**Likely Cause:** Queue configuration mismatch

**Fix:**
1. Verify start command includes all queues
2. Check task routing in celery_app.py
3. Test with simple task submission

---

## Verification Checklist

Before marking deployment as complete:

- [ ] Worker service shows "Active" in Railway dashboard
- [ ] No errors in worker deployment logs
- [ ] Logs show "celery@meta-analysis-worker ready"
- [ ] Health endpoint returns Celery status: "healthy"
- [ ] Health message shows "1 worker(s) active" (or more)
- [ ] All 5 queues listed in worker logs
- [ ] All task modules imported successfully
- [ ] Redis connection established (check logs)
- [ ] Database connection works (check logs)
- [ ] Can submit test task and see it process

**Quick Verification Command:**
```bash
# Run diagnostic
./diagnose-worker.sh

# Or check health directly
curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.'
```

---

## Support Commands

```bash
# Check current status
./diagnose-worker.sh

# Run full deployment wizard
./deploy-celery-worker.sh

# Check health endpoint
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.celery'

# View Railway logs (requires Railway CLI linked to project)
railway logs --service=meta-analysis-worker

# Redeploy via CLI
railway up --service=meta-analysis-worker
```

---

## Next Steps After Success

1. **Test Functionality**
   - Submit a test literature search task
   - Monitor task execution in worker logs
   - Verify results are stored in database
   - Check task status via API

2. **Monitor Performance**
   - Watch CPU/memory usage in Railway
   - Monitor task processing times
   - Check for any errors in logs
   - Verify auto-restart on failures

3. **Scale if Needed**
   - If task queue grows, increase concurrency
   - Consider adding more worker replicas
   - Monitor Redis queue lengths

4. **Set Up Alerts**
   - Configure Railway alerts for worker crashes
   - Monitor health endpoint regularly
   - Set up uptime monitoring

---

## Technical Context

### Why Workers Are Separate from API

The platform uses a **microservices architecture**:

- **Backend API** (`backend` service)
  - Handles HTTP requests
  - User authentication
  - Submits tasks to queues
  - Returns task status

- **Celery Workers** (`meta-analysis-worker` service)
  - Processes long-running tasks
  - Literature searches (minutes)
  - Meta-analysis calculations (minutes to hours)
  - Researcher profiling (API-intensive)
  - Background notifications

**Benefits:**
- API stays responsive (doesn't block on long tasks)
- Workers can scale independently
- Task retries don't affect API
- Better resource utilization

### Shared Infrastructure

Both services use:
- **Same Dockerfile** (`backend/Dockerfile`)
- **Same codebase** (different entry points)
- **Same database** (Postgres)
- **Same message broker** (Redis)

**Different:**
- **Start command** (uvicorn vs celery)
- **Port exposure** (API needs public port, worker doesn't)
- **Scaling strategy** (API scales for traffic, worker for task volume)

---

## Troubleshooting Resources

**Created Files:**
- `diagnose-worker.sh` - Quick diagnostic
- `deploy-celery-worker.sh` - Deployment wizard
- `CELERY_WORKER_DEPLOYMENT.md` - Full reference guide
- `railway-worker-config.json` - Build/deploy config

**External Docs:**
- [Railway Services](https://docs.railway.com/develop/services)
- [Celery Workers](https://docs.celeryq.dev/en/stable/userguide/workers.html)
- [Private Networking](https://docs.railway.com/reference/private-networking)

**Common Commands:**
```bash
# Diagnostic
./diagnose-worker.sh

# Deployment
./deploy-celery-worker.sh

# Health check
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed

# Railway CLI
railway logs --service=meta-analysis-worker
```

---

## Summary

### What's Wrong
- ✅ **Identified:** Workers not connecting ("No workers available")
- ✅ **Cause:** Missing/incorrect environment variables or needs redeploy
- ✅ **Prerequisites:** Database and Redis are healthy

### What's Provided
- ✅ Diagnostic script (`diagnose-worker.sh`)
- ✅ Deployment wizard (`deploy-celery-worker.sh`)
- ✅ Comprehensive guide (`CELERY_WORKER_DEPLOYMENT.md`)
- ✅ Configuration template (`railway-worker-config.json`)

### What You Need to Do
1. Run `./deploy-celery-worker.sh` OR
2. Manually configure environment variables in Railway dashboard
3. Ensure REDIS_URL and DATABASE_URL use Railway variable references
4. Redeploy worker service
5. Verify health endpoint shows Celery as "healthy"

### Expected Time
- **Automated:** 10-15 minutes
- **Manual:** 15-20 minutes

### Success Criteria
```json
"celery": {
  "status": "healthy",
  "message": "1 worker(s) active"
}
```

---

**Ready to deploy? Run:**
```bash
cd /Users/brandon/meta-analysis-tool
./deploy-celery-worker.sh
```
