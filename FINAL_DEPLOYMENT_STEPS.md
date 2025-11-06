# 🚀 FINAL DEPLOYMENT - 2 Manual Steps Required

## CURRENT STATUS:
✅ Database: healthy  
❌ Redis: NOT deployed  
❌ Celery: NOT deployed  

---

## STEP 1: ADD REDIS (5 minutes)

### Open Railway Dashboard:
```
https://railway.app/dashboard
```

### Find Your Project:
Look for: **"Meta-Analysis-Tool"** (the one with backend already deployed)

### Add Redis:
1. Click **"+ New"** button (top right)
2. Select **"Database"**
3. Click **"Add Redis"**
4. Wait 2-3 minutes (Railway auto-redeploys backend with Redis connection)

### Verify:
```bash
curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.redis.status'
```
Should show: `"healthy"`

---

## STEP 2: ADD CELERY WORKER (20 minutes)

### Create New Service:
1. Same Railway project
2. Click **"+ New"** → **"Empty Service"**
3. Name: **meta-analysis-worker**

### Configure Source:
- Settings → Source → Connect to GitHub
- Repository: **mrbrandonmills/meta-analysis-tool**
- Branch: **main**

### Configure Build:
- Settings → Build
- Builder: **DOCKERFILE**
- Dockerfile Path: **backend/Dockerfile**

### Configure Start Command:
- Settings → Deploy → Start Command:
```
celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4
```

### Configure Environment Variables:
- Settings → Variables
- **Copy these from your backend service:**

```
DATABASE_URL = (use reference: ${{Postgres.DATABASE_URL}})
REDIS_URL = (use reference: ${{Redis.REDIS_URL}})
ANTHROPIC_API_KEY = (copy value from backend)
SECRET_KEY = (copy value from backend)
OPENAI_API_KEY = (copy value from backend)
PYTHONUNBUFFERED = 1
LOG_LEVEL = INFO
DEBUG = false
```

### Deploy:
- Click **"Deploy"** button
- Wait 5-10 minutes for build
- Check logs for: `celery@meta-analysis-worker ready`

### Verify:
```bash
curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.celery.status'
```
Should show: `"healthy"`

---

## VERIFICATION (After Both Steps):

```bash
cd /Users/brandon/meta-analysis-tool
./verify-deployment.sh
```

Expected output:
```
✓ Database: healthy
✓ Redis: healthy
✓ Celery: healthy
✓ Registration: HTTP 201
✓ Login: HTTP 200

🎉 ALL SYSTEMS OPERATIONAL
```

---

## TIME ESTIMATE:
- Redis: 5 minutes
- Celery: 20 minutes
- **Total: 25 minutes**

---

## START NOW:
Open: https://railway.app/dashboard
