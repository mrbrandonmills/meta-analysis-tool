# Celery Worker - Quick Fix Guide

## Current Problem
```
✅ Database: healthy
✅ Redis: healthy
⚠️  Celery: degraded - "No workers available"
```

## 3-Step Fix (15 minutes)

### Step 1: Copy Environment Variables
1. Open: https://railway.app/dashboard
2. Go to: **Meta-Analysis-Tool** project
3. Open: **backend** service → **Variables** tab
4. Copy ALL variables (click "Copy All")
5. Open: **meta-analysis-worker** service → **Variables** tab
6. Paste all variables
7. **CRITICAL:** Ensure these two use Railway references:
   ```
   DATABASE_URL = ${{Postgres.DATABASE_URL}}
   REDIS_URL = ${{Redis.REDIS_URL}}
   ```

### Step 2: Verify Start Command
1. In **meta-analysis-worker** → **Settings** → **Deploy**
2. Start Command should be:
   ```
   celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4
   ```

### Step 3: Redeploy
1. In **meta-analysis-worker** → Click ⋯ menu
2. Click **Redeploy**
3. Wait 3-4 minutes
4. Check logs for: `celery@meta-analysis-worker ready.`

## Verify Success
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.celery'
```

Should return:
```json
{
  "status": "healthy",
  "message": "1 worker(s) active"
}
```

## Automated Fix
```bash
cd /Users/brandon/meta-analysis-tool
./deploy-celery-worker.sh
```

## Need Help?
- Run: `./diagnose-worker.sh`
- Read: `CELERY_WORKER_DEPLOYMENT.md`
- Read: `WORKER_DEPLOYMENT_SUMMARY.md`
