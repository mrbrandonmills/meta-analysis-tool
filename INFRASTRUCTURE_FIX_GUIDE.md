# Infrastructure Bug Fixes - Deployment Guide
**Date:** November 5, 2025
**Status:** Critical Infrastructure Repairs
**Bugs Addressed:** BUG-002, BUG-003, BUG-004

---

## Executive Summary

This guide addresses three critical infrastructure bugs blocking production deployment:

- **BUG-004**: Statistical libraries removed from requirements.txt - **FIXED**
- **BUG-002**: Redis not deployed to Railway - **ACTION REQUIRED**
- **BUG-003**: Celery workers not running - **ACTION REQUIRED**

**Current Status:**
- ✅ BUG-004: RESOLVED (statistical libraries restored to requirements.txt)
- ⚠️ BUG-002: REQUIRES Railway configuration changes
- ⚠️ BUG-003: REQUIRES new Railway service deployment

---

## BUG-004: Statistical Libraries FIXED ✅

### What Was Wrong

The `backend/requirements.txt` file had all statistical computing libraries commented out with this note:

```python
# NOTE: Heavy dependencies removed for faster builds:
# - scipy, statsmodels, numpy, pandas (statistical analysis - future feature)
# - matplotlib, seaborn (visualization - future feature)
```

**Impact:** Platform could NOT perform ANY meta-analysis calculations without these libraries.

### What Was Fixed

Restored the following CRITICAL libraries to `backend/requirements.txt`:

```python
# Statistical & Scientific Computing (REQUIRED for meta-analysis)
numpy==1.26.2           # Numerical computations
scipy==1.11.4           # Statistical functions
pandas==2.1.4           # Data manipulation
statsmodels==0.14.1     # Meta-analysis statistics
scikit-learn==1.4.0     # Machine learning utilities

# Visualization (REQUIRED for forest plots and figures)
matplotlib==3.8.2       # Plotting library
seaborn==0.13.1         # Statistical visualizations
```

Also updated `backend/pyproject.toml` for Poetry dependency management.

### Library Purposes

| Library | Version | Purpose in Meta-Analysis |
|---------|---------|--------------------------|
| **numpy** | 1.26.2 | Array operations, numerical computations, effect size calculations |
| **scipy** | 1.11.4 | Statistical tests, probability distributions, confidence intervals |
| **pandas** | 2.1.4 | Data manipulation, study data organization, tabular results |
| **statsmodels** | 0.14.1 | Fixed/random effects models, heterogeneity analysis (I², τ²) |
| **scikit-learn** | 1.4.0 | Meta-regression, publication bias detection |
| **matplotlib** | 3.8.2 | Forest plots, funnel plots, visualizations |
| **seaborn** | 0.13.1 | Enhanced statistical visualizations |

### Verification Steps

After redeploying to Railway:

1. **Check deployment logs** for successful installation:
   ```
   Installing collected packages: numpy, scipy, pandas, statsmodels, scikit-learn, matplotlib, seaborn
   Successfully installed numpy-1.26.2 scipy-1.11.4 pandas-2.1.4 statsmodels-0.14.1 scikit-learn-1.4.0 matplotlib-3.8.2 seaborn-0.13.1
   ```

2. **Test import in Python**:
   ```bash
   # SSH into Railway container or use Railway console
   python -c "import numpy, scipy, pandas, statsmodels, sklearn, matplotlib, seaborn; print('All statistical libraries imported successfully')"
   ```

3. **Verify in application logs**:
   - No import errors related to statistical libraries
   - StatisticalAgent can initialize without errors

### Build Time Impact

**Before (without statistical libraries):**
- Build time: ~60-90 seconds
- Docker image size: ~400 MB

**After (with statistical libraries):**
- Build time: ~120-180 seconds (2-3 minutes)
- Docker image size: ~800 MB

**Conclusion:** The slower build time is NECESSARY and ACCEPTABLE for a functioning meta-analysis platform.

---

## BUG-002: Redis Deployment to Railway ⚠️

### Current State

**Problem:** Redis service is NOT deployed to Railway, but the application expects it.

**Evidence from health check:**
```json
{
  "status": "unhealthy",
  "checks": {
    "database": {"status": "healthy"},
    "redis": {
      "status": "unhealthy",
      "message": "Redis URL must specify one of the following schemes"
    }
  }
}
```

**Impact:**
- ❌ No caching layer (slower performance)
- ❌ No session storage
- ❌ No rate limiting (security risk)
- ❌ Celery message broker unavailable (blocks background jobs)

### Railway Redis Deployment Steps

#### Step 1: Add Redis Service to Railway Project

1. **Open your Railway project** at https://railway.app
2. **Click "+ New"** button in the project
3. **Select "Database"** → **"Add Redis"**
4. Railway will provision a Redis instance (usually takes 30-60 seconds)

#### Step 2: Verify Redis Environment Variable

Railway automatically creates the `REDIS_URL` environment variable when Redis is added.

**Verify it's set correctly:**

1. Go to your **backend web service** in Railway
2. Click **"Variables"** tab
3. Look for `REDIS_URL` - it should be automatically injected
4. Expected format: `redis://default:password@redis.railway.internal:6379`

**If `REDIS_URL` is NOT auto-set:**

1. Go to Redis service in Railway
2. Click **"Connect"** tab
3. Copy the **Private Network URL**: `redis://default:password@redis.railway.internal:6379`
4. Go to your backend web service
5. Click **"Variables"** tab
6. Add variable:
   ```
   REDIS_URL=redis://default:password@redis.railway.internal:6379
   ```

#### Step 3: Configure Redis Connection in Application

The application is already configured to use Redis via `REDIS_URL` environment variable.

**Configuration file:** `/Users/brandon/meta-analysis-tool/backend/app/core/config.py`

```python
class Settings(BaseSettings):
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
```

**Used by:**
- Rate limiting middleware
- Session storage
- Celery message broker
- Caching layer

#### Step 4: Redeploy Backend Service

After adding Redis:

1. Go to your backend web service in Railway
2. Click **"Deploy"** → **"Redeploy"**
3. Or push a new commit to trigger auto-deployment

#### Step 5: Verify Redis Connection

**Test via Railway health endpoint:**

```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed
```

**Expected response:**
```json
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"},
    "celery": {"status": "healthy"}
  }
}
```

**If Redis is still unhealthy:**

1. Check Railway logs for errors
2. Verify `REDIS_URL` format is correct
3. Ensure Redis service is running in Railway dashboard
4. Check network connectivity between services

### Redis Configuration Options

**For production optimization, configure these Railway Redis settings:**

1. **Persistence:** Ensure AOF (Append-Only File) is enabled for data durability
2. **Max Memory:** Set appropriate memory limit based on Railway plan
3. **Eviction Policy:** Set to `allkeys-lru` for caching use case

**Railway automatically handles:**
- ✅ Automatic backups
- ✅ High availability
- ✅ SSL/TLS encryption
- ✅ Private network routing

### Local Development with Redis

For local development, use Docker Compose:

```bash
# Start Redis locally
docker-compose up redis -d

# Or use Redis directly
docker run -d -p 6379:6379 redis:7-alpine
```

Update your local `.env` file:
```bash
REDIS_URL=redis://localhost:6379/0
```

---

## BUG-003: Celery Workers Deployment ⚠️

### Current State

**Problem:** Celery worker service is NOT deployed to Railway.

**Evidence from health check:**
```json
{
  "checks": {
    "celery": {
      "status": "unknown",
      "message": "[Errno 111] Connection refused"
    }
  }
}
```

**Impact:**
- ❌ Background jobs cannot execute
- ❌ Long-running meta-analysis tasks will timeout
- ❌ Literature search tasks cannot be queued
- ❌ Report generation fails
- ❌ Email notifications don't work

### Celery Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Railway Project                           │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Web Service │    │    Redis     │    │   PostgreSQL │  │
│  │   (FastAPI)  │───▶│ (Message     │◀───│  (Database)  │  │
│  │              │    │  Broker)     │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    ▲                              │
│         │ Send tasks         │ Fetch tasks                 │
│         ▼                    │                              │
│  ┌──────────────────────────────────────┐                  │
│  │      Celery Worker Service           │                  │
│  │  - Executes background tasks         │                  │
│  │  - Processes multiple queues         │                  │
│  │  - Handles long-running operations   │                  │
│  └──────────────────────────────────────┘                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Railway Celery Worker Deployment Steps

#### Step 1: Create New Worker Service

**Option A: Using Railway CLI (Recommended)**

1. **Install Railway CLI** (if not already):
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Link to your project:**
   ```bash
   railway link
   ```

4. **Create worker service:**
   ```bash
   railway service create celery-worker
   ```

**Option B: Using Railway Dashboard**

1. Go to your Railway project
2. Click **"+ New"** button
3. Select **"Empty Service"**
4. Name it: `celery-worker`

#### Step 2: Configure Worker Service

**In Railway dashboard, go to the worker service:**

1. **Click "Settings" tab**

2. **Set Build Configuration:**
   - **Builder:** Dockerfile
   - **Dockerfile Path:** `backend/Dockerfile`
   - **Build Watch Paths:** `backend/**`

3. **Set Start Command:**
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications
   ```

4. **Configure Health Check:**
   - **Type:** None (Celery workers don't have HTTP endpoints)
   - **Restart Policy:** ON_FAILURE
   - **Max Retries:** 10

5. **Set Resource Limits:**
   ```
   Memory: 1024 MB (1 GB)
   CPU: 1.0 vCPU
   ```

#### Step 3: Configure Environment Variables

**The worker service needs the SAME environment variables as the web service:**

1. Go to worker service → **"Variables"** tab
2. Click **"Reference Variables"** → Select your web service
3. Or manually copy these variables from web service:

```bash
# Database
DATABASE_URL=${{ PostgreSQL.DATABASE_URL }}

# Redis (Message Broker)
REDIS_URL=${{ Redis.REDIS_URL }}

# API Keys
ANTHROPIC_API_KEY=<same-as-web-service>
OPENAI_API_KEY=<same-as-web-service>

# Security
SECRET_KEY=<same-as-web-service>

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
```

**IMPORTANT:** Worker and web service MUST share the same:
- `REDIS_URL` (same message broker)
- `DATABASE_URL` (same database)
- `SECRET_KEY` (same JWT validation)
- `ANTHROPIC_API_KEY` (same API access)

#### Step 4: Configure Service Dependencies

Ensure worker service starts AFTER Redis:

1. Go to worker service settings
2. **Service Dependencies:** Add `redis` as dependency
3. This ensures Redis is healthy before worker starts

#### Step 5: Deploy Worker Service

1. **Connect to GitHub repository:**
   - Click **"Settings"** → **"Source"**
   - Select same GitHub repository as web service
   - Branch: `main` (or your production branch)

2. **Trigger deployment:**
   - Push to GitHub will auto-deploy
   - Or click **"Deploy"** → **"Redeploy"**

#### Step 6: Verify Worker Service

**Check Railway logs:**

1. Go to worker service → **"Logs"** tab
2. Look for Celery startup messages:
   ```
   [2025-11-05 10:00:00,000: INFO/MainProcess] Connected to redis://redis.railway.internal:6379/0
   [2025-11-05 10:00:00,100: INFO/MainProcess] mingle: searching for neighbors
   [2025-11-05 10:00:01,200: INFO/MainProcess] mingle: all alone
   [2025-11-05 10:00:01,300: INFO/MainProcess] celery@worker-1 ready.
   [2025-11-05 10:00:01,400: INFO/MainProcess] Registered tasks:
       app.workers.tasks.literature_search.search_pubmed
       app.workers.tasks.meta_analysis.execute_meta_analysis
       app.workers.tasks.reviewer_tasks.match_reviewers
       app.workers.tasks.notifications.send_email
   ```

**Test worker from web service:**

```bash
# SSH into web service or use Railway console
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/execute/test-id
```

Check worker logs for task execution:
```
[2025-11-05 10:05:00,000: INFO/MainProcess] Task app.workers.tasks.meta_analysis.execute_meta_analysis[abc-123] received
[2025-11-05 10:05:05,000: INFO/ForkPoolWorker-1] Task app.workers.tasks.meta_analysis.execute_meta_analysis[abc-123] succeeded in 5.0s
```

### Celery Worker Queues

The application uses multiple queues for task prioritization:

| Queue | Purpose | Priority |
|-------|---------|----------|
| `default` | General background tasks | Normal |
| `search` | Literature search operations (slow) | Low |
| `analysis` | Meta-analysis calculations (CPU-intensive) | High |
| `reviewer` | Reviewer matching (moderate) | Normal |
| `notifications` | Email/notifications (fast) | High |

**To scale specific queues:**

Create additional worker services with specific queue filters:

```bash
# Worker 1: High-priority tasks
celery -A app.workers.celery_app worker --queues=analysis,notifications

# Worker 2: Search tasks only
celery -A app.workers.celery_app worker --queues=search
```

### Optional: Celery Beat for Scheduled Tasks

**Celery Beat** runs periodic tasks (cron-like).

**Create Beat Service:**

1. Create new Railway service: `celery-beat`
2. Use same Dockerfile: `backend/Dockerfile`
3. Set start command:
   ```bash
   celery -A app.workers.celery_app beat --loglevel=info
   ```
4. Share same environment variables as worker
5. **IMPORTANT:** Only run ONE beat instance (multiple beats create duplicate tasks)

**Scheduled tasks defined in `celery_app.py`:**

```python
beat_schedule={
    "cleanup-expired-tasks": {
        "task": "app.workers.tasks.maintenance.cleanup_expired_tasks",
        "schedule": 3600.0,  # Every hour
    },
    "update-researcher-profiles": {
        "task": "app.workers.tasks.reviewer_tasks.update_researcher_profiles",
        "schedule": 86400.0,  # Every 24 hours
    },
}
```

### Optional: Flower for Celery Monitoring

**Flower** provides a web UI for monitoring Celery tasks.

**Create Flower Service:**

1. Create new Railway service: `celery-flower`
2. Use same Dockerfile: `backend/Dockerfile`
3. Set start command:
   ```bash
   celery -A app.workers.celery_app flower --port=$PORT
   ```
4. Environment variables:
   ```bash
   CELERY_BROKER_URL=${{ Redis.REDIS_URL }}
   CELERY_RESULT_BACKEND=${{ Redis.REDIS_URL }}
   ```
5. Enable public domain to access Flower UI
6. **Add authentication** (flower is publicly accessible):
   ```bash
   celery -A app.workers.celery_app flower --port=$PORT --basic-auth=admin:secure_password
   ```

**Access Flower:**
- URL: `https://celery-flower-production.up.railway.app`
- Monitor active tasks, worker status, queue lengths

### Local Development with Celery

**Using Docker Compose (Recommended):**

```bash
# Start all services including worker
docker-compose up

# Or start worker separately
docker-compose up celery_worker
```

**Manual Celery worker:**

```bash
cd backend
source venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=debug
```

---

## Complete Railway Architecture

After implementing all fixes, your Railway project should have:

```
Railway Project: meta-analysis-tool
│
├── Services:
│   ├── backend (FastAPI web service)
│   │   ├── Dockerfile: backend/Dockerfile
│   │   ├── Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
│   │   └── Health: /api/v1/health
│   │
│   ├── celery-worker (Background task processor)
│   │   ├── Dockerfile: backend/Dockerfile
│   │   ├── Start: celery -A app.workers.celery_app worker --loglevel=info
│   │   └── Depends on: redis
│   │
│   ├── celery-beat (Scheduled task scheduler) [OPTIONAL]
│   │   ├── Dockerfile: backend/Dockerfile
│   │   ├── Start: celery -A app.workers.celery_app beat --loglevel=info
│   │   └── Depends on: redis, celery-worker
│   │
│   └── celery-flower (Monitoring UI) [OPTIONAL]
│       ├── Dockerfile: backend/Dockerfile
│       ├── Start: celery -A app.workers.celery_app flower --port=$PORT
│       └── Public URL: https://flower.railway.app
│
└── Databases:
    ├── PostgreSQL (Primary database)
    │   └── Auto-injected: DATABASE_URL
    │
    └── Redis (Message broker + cache)
        └── Auto-injected: REDIS_URL
```

---

## Verification Checklist

After deploying all fixes:

### BUG-004: Statistical Libraries
- [ ] Deployment logs show successful installation of numpy, scipy, pandas, statsmodels, scikit-learn, matplotlib, seaborn
- [ ] No import errors in application logs
- [ ] Build time increased to 2-3 minutes (expected)
- [ ] Docker image size ~800 MB (expected)

### BUG-002: Redis
- [ ] Redis service visible in Railway dashboard
- [ ] `REDIS_URL` environment variable auto-injected to backend service
- [ ] Health endpoint shows `"redis": {"status": "healthy"}`
- [ ] No Redis connection errors in logs

### BUG-003: Celery Workers
- [ ] Worker service visible in Railway dashboard
- [ ] Worker logs show successful connection to Redis
- [ ] Worker logs show registered tasks
- [ ] Health endpoint shows `"celery": {"status": "healthy"}`
- [ ] Test task executes successfully

### End-to-End Testing
- [ ] Health check endpoint returns fully healthy status
- [ ] Can submit meta-analysis job via API
- [ ] Worker picks up and processes the job
- [ ] Job results stored in database
- [ ] Frontend can retrieve job status and results

---

## Cost Implications

**Railway Pricing (Hobby Plan: $5/month):**

- **Free tier:** $5 credit/month
- **Additional usage:** $0.000231/GB-hour RAM, $0.000463/vCPU-hour

**Service costs (estimated):**

| Service | RAM | CPU | Monthly Cost |
|---------|-----|-----|--------------|
| Backend (web) | 1 GB | 1 vCPU | ~$12/month |
| Celery Worker | 1 GB | 1 vCPU | ~$12/month |
| PostgreSQL | 256 MB | 0.25 vCPU | ~$3/month |
| Redis | 256 MB | 0.25 vCPU | ~$3/month |
| **Total** | **2.5 GB** | **2.5 vCPU** | **~$30/month** |

**Note:** Costs vary based on actual usage. Railway charges only for resources used.

**To reduce costs:**
- Use Railway's sleep feature for non-production services
- Scale down worker during low-traffic periods
- Monitor usage via Railway dashboard

---

## Rollback Plan

If issues occur after deployment:

### Rollback Dependencies
```bash
# Revert requirements.txt to previous version
git revert <commit-hash>
git push origin main
```

### Disable Worker Service
1. Go to Railway worker service
2. Click "Settings" → "Service"
3. Click "Stop Service" (keeps configuration, stops billing)

### Remove Redis
**WARNING:** Only if absolutely necessary (loses cache data)
1. Go to Railway Redis service
2. Click "Settings" → "Danger Zone"
3. Click "Remove Service"

---

## Support and Troubleshooting

### Railway Support
- Documentation: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### Application Logs
Access logs in Railway:
1. Go to service in Railway dashboard
2. Click "Logs" tab
3. Filter by time range or search terms

### Common Issues

**Issue: Worker can't connect to Redis**
- Verify `REDIS_URL` is set in worker service
- Check Redis service is running
- Ensure network connectivity between services

**Issue: Tasks not being picked up**
- Verify worker is running (check logs)
- Check task is sent to correct queue
- Inspect Redis queue: `redis-cli LLEN celery`

**Issue: Build timeout**
- Railway default timeout: 10 minutes
- Statistical libraries may take 2-3 minutes to install (normal)
- If timeout occurs, contact Railway support for limit increase

---

## Next Steps

1. **Deploy changes to Railway**
   ```bash
   git add backend/requirements.txt backend/pyproject.toml
   git commit -m "Fix BUG-004: Restore statistical libraries for meta-analysis"
   git push origin main
   ```

2. **Add Redis service** (see BUG-002 section)

3. **Deploy Celery worker** (see BUG-003 section)

4. **Verify all services healthy**

5. **Update frontend API URL** in Vercel:
   ```bash
   NEXT_PUBLIC_API_URL=https://meta-analysis-tool-production.up.railway.app
   ```

6. **Test end-to-end workflow**

---

**Document Version:** 1.0
**Last Updated:** November 5, 2025
**Author:** DevOps Engineering Agent
**Status:** Ready for Implementation
