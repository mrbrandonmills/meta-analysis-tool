# Railway Celery Worker Fix - Step-by-Step Guide

## Current Issue
- Backend API: ✅ Healthy
- Database: ✅ Healthy
- Redis: ✅ Healthy
- Celery Workers: ❌ Degraded ("No workers available")

## Root Cause
The worker service exists but is missing required environment variables, preventing workers from connecting to Redis and starting properly.

## Solution: Configure Environment Variables

### Step 1: Access Railway Dashboard
1. Open: https://railway.app/dashboard
2. Click on: **Meta-Analysis-Tool** project
3. You should see these services:
   - backend (API service)
   - Postgres (database)
   - Redis (cache/broker)
   - meta-analysis-worker (Celery worker service)

### Step 2: View Backend Service Variables
1. Click on the **backend** service
2. Click the **Variables** tab
3. **Keep this tab/window open** - you'll copy values from here

You should see variables like:
- `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`
- `REDIS_URL` = `${{Redis.REDIS_URL}}`
- `ANTHROPIC_API_KEY` = `sk-ant-...`
- `SECRET_KEY` = `<some-secret-value>`
- `OPENAI_API_KEY` = `sk-...`
- And possibly others

### Step 3: Configure Worker Service Variables
1. Open a **new tab/window** (keep backend variables visible for reference)
2. Navigate to: Railway Dashboard → **Meta-Analysis-Tool** → **meta-analysis-worker**
3. Click the **Variables** tab

### Step 4: Add Required Variables
Click **+ New Variable** and add each of these:

#### Critical Variables (REQUIRED):

**DATABASE_URL**
- Value: `${{Postgres.DATABASE_URL}}`
- ⚠️ Use the Railway variable reference, NOT the actual URL
- This ensures the worker always uses the correct database

**REDIS_URL**
- Value: `${{Redis.REDIS_URL}}`
- ⚠️ Use the Railway variable reference, NOT the actual URL
- This is crucial for Celery broker connection

**ANTHROPIC_API_KEY**
- Value: Copy from backend service
- Example: `sk-ant-api03-...`
- Required for AI-powered analysis tasks

**SECRET_KEY**
- Value: Copy from backend service
- Example: `dev-secret-key-change-in-production` or similar
- Required for Flask application initialization

#### Recommended Variables:

**OPENAI_API_KEY**
- Value: Copy from backend service (if present)
- Example: `sk-proj-...`
- Optional but enables OpenAI integration

**PUBMED_API_KEY**
- Value: Copy from backend service (if present)
- Optional but improves PubMed API rate limits

**PUBMED_EMAIL**
- Value: Copy from backend service (if present)
- Optional but required for PubMed API

**PYTHONUNBUFFERED**
- Value: `1`
- Ensures logs are immediately visible

**LOG_LEVEL**
- Value: `INFO`
- Controls logging verbosity

### Step 5: Verify Configuration
After adding all variables, your worker service should have AT MINIMUM:
- ✅ DATABASE_URL
- ✅ REDIS_URL
- ✅ ANTHROPIC_API_KEY
- ✅ SECRET_KEY

### Step 6: Verify Build Settings
1. In **meta-analysis-worker** service, click **Settings**
2. Scroll to **Build** section
3. Verify:
   - **Builder**: DOCKERFILE
   - **Dockerfile Path**: `backend/Dockerfile` (no leading slash!)

### Step 7: Verify Deploy Settings
1. Still in **Settings**, scroll to **Deploy** section
2. Verify **Start Command**:
   ```
   celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4
   ```
3. Verify **Restart Policy**: ON_FAILURE

### Step 8: Redeploy Worker Service
1. In **meta-analysis-worker** service, click the **three dots menu (⋯)** in the top right
2. Click **Redeploy**
3. A new deployment will start - watch the progress
4. This will take 2-4 minutes

### Step 9: Monitor Deployment
1. Click on the **Deployments** tab in the worker service
2. Click on the latest deployment to view logs
3. Look for these success indicators:
   - ✅ `celery@meta-analysis-worker ready.`
   - ✅ `Connected to redis://...`
   - ✅ Task modules listed (e.g., `app.workers.tasks.literature_search`)

Watch for these errors:
- ❌ `Connection refused` → Check REDIS_URL
- ❌ `ModuleNotFoundError` → Dockerfile issue
- ❌ `Missing environment variable` → Add missing variable
- ❌ `Invalid API key` → Check ANTHROPIC_API_KEY

### Step 10: Verify Worker Health
After deployment completes, run this command in your terminal:

```bash
curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.celery'
```

Expected output:
```json
{
  "status": "healthy",
  "message": "1 worker(s) active"
}
```

Or use the provided script:
```bash
./verify-worker-health.sh
```

## Troubleshooting

### If workers still show "degraded" after 5 minutes:

1. **Check worker logs**:
   - Railway Dashboard → meta-analysis-worker → Deployments → Latest deployment
   - Look for error messages

2. **Verify REDIS_URL format**:
   - Should be: `${{Redis.REDIS_URL}}`
   - NOT a hardcoded URL

3. **Verify all required variables are set**:
   - Run through Step 4 again
   - Ensure no typos in variable names

4. **Check if Redis service is running**:
   - Railway Dashboard → Redis service → Should show "Active"

5. **Verify backend service has the API keys**:
   - If backend doesn't have ANTHROPIC_API_KEY, add it there first
   - Then copy to worker service

### Common Mistakes:

❌ **Using hardcoded DATABASE_URL instead of variable reference**
- Wrong: `postgresql://user:pass@host:5432/db`
- Right: `${{Postgres.DATABASE_URL}}`

❌ **Using hardcoded REDIS_URL instead of variable reference**
- Wrong: `redis://default:pass@redis.railway.internal:6379`
- Right: `${{Redis.REDIS_URL}}`

❌ **Forgetting to redeploy after adding variables**
- Variables don't apply until you redeploy!

❌ **Wrong Dockerfile path**
- Wrong: `/backend/Dockerfile` (leading slash)
- Wrong: `Dockerfile` (missing directory)
- Right: `backend/Dockerfile`

## Quick Verification Checklist

- [ ] Opened Railway Dashboard
- [ ] Viewed backend service variables
- [ ] Added DATABASE_URL = `${{Postgres.DATABASE_URL}}` to worker
- [ ] Added REDIS_URL = `${{Redis.REDIS_URL}}` to worker
- [ ] Added ANTHROPIC_API_KEY (copied from backend) to worker
- [ ] Added SECRET_KEY (copied from backend) to worker
- [ ] Added PYTHONUNBUFFERED = 1 to worker
- [ ] Added LOG_LEVEL = INFO to worker
- [ ] Verified Dockerfile path is `backend/Dockerfile`
- [ ] Verified start command is correct
- [ ] Redeployed worker service
- [ ] Waited 2-4 minutes for deployment
- [ ] Checked deployment logs for "celery@meta-analysis-worker ready."
- [ ] Verified health endpoint shows "healthy" status

## Need More Help?

Run the diagnostic script:
```bash
./diagnose-worker.sh
```

Or the full deployment script:
```bash
./deploy-celery-worker.sh
```

## Expected Timeline
- Configuration: 5-10 minutes
- Deployment: 2-4 minutes
- Total: 7-14 minutes
