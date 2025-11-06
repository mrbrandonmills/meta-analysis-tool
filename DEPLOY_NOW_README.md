# EMERGENCY DEPLOYMENT - START HERE

**URGENCY:** Board meeting tomorrow - Platform must be 100% operational
**TIME REQUIRED:** 35-40 minutes
**DIFFICULTY:** Easy - All via Railway web dashboard

---

## WHAT YOU NEED TO DO

Your platform is **75% deployed** but **3 critical services are missing**:
1. ❌ **Redis** - Blocks sessions, caching, and background jobs
2. ❌ **Database Migrations** - Blocks user authentication (causes 500 errors)
3. ❌ **Celery Workers** - Blocks literature search and analysis

**After these 3 fixes → Platform 100% operational for board meeting**

---

## QUICK START (CHOOSE YOUR PATH)

### Path 1: Step-by-Step Checklist (Recommended)
**Best for:** Following along step-by-step with checkboxes
```bash
open /Users/brandon/meta-analysis-tool/QUICK_DEPLOY_CHECKLIST.md
```

### Path 2: Detailed Guide (If You Need Context)
**Best for:** Understanding what each step does and why
```bash
open /Users/brandon/meta-analysis-tool/RAILWAY_DEPLOYMENT_GUIDE.md
```

### Path 3: Quick Reference Card (Keep Open During Deployment)
**Best for:** Quick lookup during deployment
```bash
cat /Users/brandon/meta-analysis-tool/DEPLOYMENT_QUICK_REFERENCE.txt
```

### Path 4: Executive Summary (For Management)
**Best for:** Understanding business impact and readiness
```bash
open /Users/brandon/meta-analysis-tool/DEPLOYMENT_SUMMARY.md
```

---

## FASTEST WAY TO DEPLOY (35 MINUTES)

### Pre-Deployment Check (2 min)
```bash
# Run verification to see current status
cd /Users/brandon/meta-analysis-tool
./verify-deployment.sh
```

**Expected Output:**
```
✅ Database: healthy
❌ Redis: unhealthy - DEPLOY REDIS NOW
❌ Celery: unknown - DEPLOY WORKER SERVICE
✗ Registration failed (HTTP 500) - DATABASE MIGRATIONS NOT RUN
```

---

### Fix 1: Deploy Redis (10 min)

**Railway Dashboard:** https://railway.app/dashboard

1. Open project: "meta-analysis-tool"
2. Click **"+ New"** → **"Database"** → **"Add Redis"**
3. Wait 2-3 minutes (until status shows "Active")
4. Go to backend service → Verify `REDIS_URL` in Variables tab
5. Click **"Deployments"** → **"Redeploy"**

**Verify:**
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | grep redis
# Should show: "redis": {"status": "healthy"}
```

---

### Fix 2: Run Database Migrations (5 min)

**Railway Dashboard:** Backend Service → Settings

1. Find **"Start Command"** field
2. Change to:
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 2 --app-dir /app
   ```
3. Click **"Save"** then **"Deploy"**
4. Check logs for: `"Running upgrade -> 002_add_user_tables"`

**Verify:**
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!","full_name":"Test User"}'
# Should return: HTTP 201 (not 500)
```

---

### Fix 3: Deploy Celery Workers (20 min)

**Railway Dashboard:** Add New Service

#### Create Service (2 min)
1. Click **"+ New"** → **"Empty Service"**
2. Name it: `meta-analysis-worker`

#### Connect Repository (3 min)
3. Go to **"Settings"** → **"Source"** → **"Connect Repo"**
4. Select same repository as backend
5. Branch: `main`

#### Configure Build (2 min)
6. **"Settings"** → **"Build"**:
   - Builder: `DOCKERFILE`
   - Dockerfile Path: `backend/Dockerfile`
   - Watch Paths: `backend/**`

#### Set Start Command (1 min)
7. **"Settings"** → **"Deploy"** → **"Start Command"**:
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4
   ```

#### Add Environment Variables (10 min)
8. Go to **"Variables"** tab

**Plain Text Variables:**
```
PYTHONUNBUFFERED = 1
WORKER_TYPE = celery
DEBUG = false
LOG_LEVEL = INFO
```

**Reference Variables** (link to services):
- `DATABASE_URL` → Reference → PostgreSQL → DATABASE_URL
- `REDIS_URL` → Reference → Redis → REDIS_URL

**Copy from Backend** (go to backend service → Variables → copy):
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `SECRET_KEY`
- `SENTRY_DSN` (optional)
- `PUBMED_API_KEY` (optional)
- `PUBMED_EMAIL` (optional)

#### Deploy (2 min)
9. Click **"Deploy"** → **"Deploy Latest"**
10. Wait 3-4 minutes, check logs for `"celery@<hostname> ready"`

**Verify:**
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | grep celery
# Should show: "celery": {"status": "healthy", "workers": 1}
```

---

## FINAL VERIFICATION

### Run Automated Tests
```bash
cd /Users/brandon/meta-analysis-tool
./verify-deployment.sh
```

### Expected Success Output
```
========================================
DEPLOYMENT VERIFICATION SUMMARY
========================================

Database:     healthy
Redis:        healthy
Celery:       healthy

=========================================
🎉 ALL SYSTEMS OPERATIONAL
=========================================
Platform ready for board meeting!
```

---

## MANUAL VERIFICATION (Optional)

### Test 1: Health Check
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed
```
**Expected:** All services show "healthy"

### Test 2: User Registration
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "board@example.com",
    "password": "SecurePass123!",
    "full_name": "Board Member"
  }'
```
**Expected:** HTTP 201 with user_id and access_token

### Test 3: User Login
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "board@example.com",
    "password": "SecurePass123!"
  }'
```
**Expected:** HTTP 200 with JWT tokens

---

## TROUBLESHOOTING

### Redis Not Healthy?
- Verify Redis service status is "Active" in Railway
- Check backend service has `REDIS_URL` variable
- Redeploy backend service

### Registration Still Returns 500?
- Check backend deployment logs
- Look for "Running upgrade -> 002" message
- Verify start command includes `alembic upgrade head`

### Celery Shows "Unknown"?
- Check worker service logs for connection errors
- Verify worker has `REDIS_URL` variable
- Ensure Redis is healthy first

### Worker Won't Deploy?
- Check Dockerfile path is exactly `backend/Dockerfile`
- Verify start command has no typos
- Ensure all environment variables are set

---

## FILES IN THIS DEPLOYMENT PACKAGE

| File | Purpose |
|------|---------|
| `DEPLOY_NOW_README.md` | **This file** - Start here |
| `RAILWAY_DEPLOYMENT_GUIDE.md` | Detailed step-by-step guide with context |
| `QUICK_DEPLOY_CHECKLIST.md` | Checkbox-based deployment checklist |
| `DEPLOYMENT_QUICK_REFERENCE.txt` | One-page quick reference card |
| `DEPLOYMENT_SUMMARY.md` | Executive summary for management |
| `verify-deployment.sh` | Automated verification script |
| `railway.worker.json` | Celery worker Railway configuration |

---

## TIMELINE

| Time | Task | Status |
|------|------|--------|
| 0:00 | Start deployment | → |
| 0:02 | Redis deployed | → |
| 0:12 | Migrations run | → |
| 0:17 | Celery deployed | → |
| 0:37 | Verification complete | → |
| 0:40 | **BOARD MEETING READY** | ✅ |

---

## SUPPORT

**Stuck?** Check the detailed guide:
```bash
open /Users/brandon/meta-analysis-tool/RAILWAY_DEPLOYMENT_GUIDE.md
```

**Railway Issues?**
- Support: https://discord.gg/railway
- Docs: https://docs.railway.app
- Status: https://railway.statuspage.io

**DevOps Engineer:** Available for deployment support

---

## CONFIDENCE LEVEL: HIGH

- ✅ All fixes are Railway dashboard operations (no CLI needed)
- ✅ Each fix has clear verification step
- ✅ Rollback available via "Redeploy" previous version
- ✅ Backend already proven stable
- ✅ Standard Railway services (no custom config)

---

## NEXT STEPS AFTER BOARD MEETING

1. Add Celery Beat for scheduled tasks
2. Configure monitoring and alerting
3. Set up automated backups
4. Implement auto-scaling policies
5. Add load testing

---

## RECOMMENDATION

**DEPLOY NOW** - Total time: 40 minutes with buffer

Platform will be **100% operational** for board meeting tomorrow.

---

**START DEPLOYMENT:**
```bash
# 1. Check current status
./verify-deployment.sh

# 2. Open Railway dashboard
open https://railway.app/dashboard

# 3. Follow checklist
open QUICK_DEPLOY_CHECKLIST.md

# 4. Verify when done
./verify-deployment.sh
```

**GO! ✅**
