# Celery Worker Deployment Guide

## Current Status

**Service Name:** meta-analysis-worker
**Platform:** Railway
**Status:** ⚠️ Service exists but workers not connecting ("No workers available")

---

## Root Cause Analysis

The Celery worker service is deployed but not successfully connecting to Redis and starting workers. This is typically caused by:

1. **Missing Environment Variables** - Worker needs same config as backend API
2. **Incorrect Redis URL** - Must use Railway's internal network
3. **Build/Deploy Configuration Issues** - Start command or Dockerfile path errors
4. **Application Dependencies** - Missing API keys preventing task module imports

---

## Required Environment Variables

The worker service **MUST** have these environment variables configured:

### Critical (Required)
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
ANTHROPIC_API_KEY=<your-anthropic-api-key>
SECRET_KEY=<your-secret-key>
```

### Recommended
```bash
OPENAI_API_KEY=<your-openai-key>
PUBMED_API_KEY=<your-pubmed-key>
PUBMED_EMAIL=<your-email>
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

### Why These Are Required

- **DATABASE_URL**: Worker tasks need database access for storing results
- **REDIS_URL**: Celery uses Redis as message broker and result backend
- **ANTHROPIC_API_KEY**: Required for AI-powered analysis tasks (app imports fail without it)
- **SECRET_KEY**: Application configuration requires this for security
- **OPENAI_API_KEY**: Optional, but needed for OpenAI-powered features
- **PYTHONUNBUFFERED**: Ensures logs are visible in real-time

---

## Deployment Configuration

### Source Settings
```
Repository: mrbrandonmills/meta-analysis-tool
Branch: main
Root Directory: / (leave default)
```

### Build Settings
```
Builder: DOCKERFILE
Dockerfile Path: backend/Dockerfile
Watch Patterns: backend/**
```

### Deploy Settings
```bash
# Start Command
celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4

# Restart Policy
ON_FAILURE

# Max Retries
10

# Healthcheck Timeout
300 (5 minutes)
```

---

## Deployment Steps

### Option 1: Use Automated Script

```bash
cd /Users/brandon/meta-analysis-tool
./deploy-celery-worker.sh
```

This script will:
1. Check current health status
2. Guide you through environment variable setup
3. Verify build configuration
4. Trigger redeploy
5. Monitor worker connection

### Option 2: Manual Deployment

#### Step 1: Configure Environment Variables

1. Open Railway Dashboard: https://railway.app/dashboard
2. Select: **Meta-Analysis-Tool** project
3. Select: **meta-analysis-worker** service
4. Go to: **Variables** tab
5. Copy ALL variables from **backend** service
6. Add/verify these critical variables:
   - `DATABASE_URL = ${{Postgres.DATABASE_URL}}`
   - `REDIS_URL = ${{Redis.REDIS_URL}}`
   - `ANTHROPIC_API_KEY = <your-key>`
   - `SECRET_KEY = <your-secret>`

#### Step 2: Verify Build Configuration

1. In worker service, go to: **Settings** → **Source**
   - Verify GitHub repo is connected
   - Verify branch is `main`

2. Go to: **Settings** → **Build**
   - Builder: `DOCKERFILE`
   - Dockerfile Path: `backend/Dockerfile` ⚠️ (no leading slash!)

3. Go to: **Settings** → **Deploy**
   - Start Command:
     ```
     celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4
     ```

#### Step 3: Redeploy

1. Click three dots menu (⋯) in worker service
2. Select **Redeploy**
3. Wait 2-4 minutes for build

#### Step 4: Monitor Logs

Watch deployment logs for:

**Success indicators:**
```
✓ celery@meta-analysis-worker ready.
✓ Connected to redis://...
✓ [tasks]
  . app.workers.tasks.literature_search.search_databases
  . app.workers.tasks.meta_analysis.run_analysis
  . app.workers.tasks.reviewer_tasks.profile_reviewer
  . app.workers.tasks.notifications.send_notification
```

**Error indicators:**
```
✗ Cannot connect to redis://...
✗ ModuleNotFoundError: No module named 'app'
✗ Configuration error: ANTHROPIC_API_KEY not set
✗ Connection refused
```

#### Step 5: Verify Health

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

## Troubleshooting

### Issue: "No workers available"

**Symptoms:**
- Health check shows Celery as "degraded"
- Message: "No workers available"

**Diagnosis:**
1. Check worker service logs in Railway Dashboard
2. Look for startup errors
3. Verify environment variables are set

**Solutions:**
1. **Missing environment variables** → Copy all vars from backend service
2. **Wrong Redis URL** → Use `${{Redis.REDIS_URL}}` not a hardcoded URL
3. **Import errors** → Ensure ANTHROPIC_API_KEY is set (required for app config)
4. **Build errors** → Check Dockerfile path is correct

### Issue: Worker crashes on startup

**Symptoms:**
- Service deploys but immediately restarts
- Logs show Python errors

**Common causes:**
1. **Missing dependencies** → Check requirements.txt is complete
2. **Invalid API keys** → Verify ANTHROPIC_API_KEY format
3. **Redis connection failure** → Check Redis service is running
4. **Database migration issues** → Backend should run migrations first

**Solutions:**
1. Check worker logs for specific error message
2. Verify all services (Postgres, Redis) are healthy
3. Ensure backend service deployed successfully first
4. Test Redis connection: `${{Redis.REDIS_URL}}` format

### Issue: Workers start but don't process tasks

**Symptoms:**
- Health check shows workers available
- Tasks queued but not executed

**Diagnosis:**
1. Check if workers are listening to correct queues
2. Verify task routing configuration
3. Check Redis connection

**Solutions:**
1. Verify start command includes all queues: `--queues=default,search,analysis,reviewer,notifications`
2. Check task routing in `celery_app.py` matches queue names
3. Test Redis pub/sub functionality

### Issue: "Connection refused" to Redis

**Symptoms:**
- Worker logs show Redis connection errors
- "Connection refused" or "Cannot connect to redis"

**Solutions:**
1. **Use Railway's internal network:**
   ```
   REDIS_URL=${{Redis.REDIS_URL}}
   ```
   This resolves to: `redis://default:<password>@redis.railway.internal:6379`

2. **Don't use external Redis URL** - Railway services should use internal networking

3. **Verify Redis service is running** - Check Redis service health in dashboard

---

## Verification Checklist

Before marking deployment as complete, verify:

- [ ] Worker service shows "Active" status in Railway
- [ ] No errors in worker deployment logs
- [ ] Health endpoint shows Celery as "healthy"
- [ ] Worker logs show "celery@... ready"
- [ ] All task modules imported successfully
- [ ] Redis connection established
- [ ] Database connection works
- [ ] Can submit test task and see it process

### Quick Verification

```bash
# Check overall health
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed

# Test task submission (requires authentication)
# 1. Register/login to get token
# 2. Submit literature search task
# 3. Check task status
# 4. Verify worker processes it
```

---

## Expected Worker Logs

### Healthy Startup Sequence

```
[2025-11-06 00:45:00,123: INFO/MainProcess] Connected to redis://redis.railway.internal:6379/0
[2025-11-06 00:45:00,234: INFO/MainProcess] mingle: searching for neighbors
[2025-11-06 00:45:01,345: INFO/MainProcess] mingle: all alone
[2025-11-06 00:45:01,456: INFO/MainProcess] celery@meta-analysis-worker ready.

-------------- celery@meta-analysis-worker v5.3.4 --------------
--- ***** -----
-- ******* ---- Linux-x86_64-with-glibc2.35
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         meta_analysis_workers:0x7f8b9c123456
- ** ---------- .> transport:   redis://redis.railway.internal:6379/0
- ** ---------- .> results:     redis://redis.railway.internal:6379/0
- *** --- * --- .> concurrency: 4 (prefork)
-- ******* ---- .> task events: ON
--- ***** -----
 -------------- [queues]
                .> analysis         exchange=analysis(direct) key=analysis
                .> default          exchange=default(direct) key=default
                .> notifications    exchange=notifications(direct) key=notifications
                .> reviewer         exchange=reviewer(direct) key=reviewer
                .> search           exchange=search(direct) key=search

[tasks]
  . app.workers.tasks.literature_search.search_databases
  . app.workers.tasks.meta_analysis.run_analysis
  . app.workers.tasks.reviewer_tasks.profile_reviewer
  . app.workers.tasks.notifications.send_notification
  . app.workers.tasks.maintenance.cleanup_expired_tasks
  . app.workers.tasks.reviewer_tasks.update_researcher_profiles
```

---

## Architecture Notes

### Worker vs API Service

Both services use the **same Dockerfile** (`backend/Dockerfile`) but different start commands:

**Backend API:**
```bash
CMD /opt/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**Celery Worker:**
```bash
celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4
```

The Dockerfile's CMD is overridden by Railway's "Start Command" setting.

### Queue Architecture

The worker processes tasks from 5 specialized queues:

1. **default** - General background tasks
2. **search** - Literature database searches (long-running)
3. **analysis** - Meta-analysis calculations (CPU-intensive)
4. **reviewer** - Researcher profiling (API-intensive)
5. **notifications** - Email/notification delivery (I/O-bound)

Each queue can be scaled independently by adjusting `--concurrency` or adding more worker replicas.

---

## Scaling Considerations

### Current Configuration
- **Replicas:** 1
- **Concurrency:** 4 workers
- **Total Capacity:** 4 concurrent tasks

### Scaling Options

**Vertical Scaling (increase concurrency):**
```bash
--concurrency=8  # More workers per replica
```
Good for: CPU-intensive tasks, maximizing single instance

**Horizontal Scaling (add replicas):**
```
Deploy → Replicas: 2
```
Good for: High task volume, redundancy, avoiding single point of failure

**Queue-Specific Workers:**
Deploy separate worker services for specific queues:
- `meta-analysis-worker-search` → only `--queues=search`
- `meta-analysis-worker-analysis` → only `--queues=analysis`

---

## Monitoring

### Health Checks

**API Health Endpoint:**
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed
```

**Worker-Specific Metrics:**
```python
# Via Celery inspect API (requires backend access)
from app.workers.celery_app import celery_app

inspect = celery_app.control.inspect()
print(inspect.active())      # Currently running tasks
print(inspect.scheduled())   # Scheduled tasks
print(inspect.reserved())    # Reserved tasks
print(inspect.stats())       # Worker statistics
```

### Railway Metrics

Monitor in Railway Dashboard:
- **CPU Usage** - Should be <80% under normal load
- **Memory Usage** - Workers typically use 200-500MB each
- **Restart Count** - Should be 0 (restarts indicate crashes)
- **Deploy Time** - Typically 2-4 minutes

### Logs to Monitor

**Key log patterns:**
```bash
# Task execution
"Task started: app.workers.tasks.literature_search.search_databases"
"Task completed: app.workers.tasks.literature_search.search_databases"

# Errors
"Task failed: <task_id> - <error>"
"Connection refused"
"ModuleNotFoundError"

# Performance
"Task <name> succeeded in <time>s"
```

---

## Next Steps After Deployment

1. ✅ Verify health endpoint shows Celery as "healthy"
2. ✅ Check worker logs show successful startup
3. ✅ Test literature search submission
4. ✅ Monitor task processing in real-time
5. ✅ Set up alerting for worker failures
6. ✅ Document task processing times
7. ✅ Plan scaling strategy based on usage

---

## Support Resources

**Railway Documentation:**
- [Services Guide](https://docs.railway.com/develop/services)
- [Environment Variables](https://docs.railway.com/develop/variables)
- [Private Networking](https://docs.railway.com/reference/private-networking)

**Celery Documentation:**
- [Worker Guide](https://docs.celeryq.dev/en/stable/userguide/workers.html)
- [Configuration](https://docs.celeryq.dev/en/stable/userguide/configuration.html)
- [Monitoring](https://docs.celeryq.dev/en/stable/userguide/monitoring.html)

**Common Commands:**
```bash
# Check health
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed

# Run deployment script
./deploy-celery-worker.sh

# View Railway logs (requires Railway CLI)
railway logs --service=meta-analysis-worker

# Redeploy service
railway up --service=meta-analysis-worker
```
