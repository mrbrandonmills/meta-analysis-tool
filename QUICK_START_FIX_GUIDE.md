# Quick Start: Infrastructure Bug Fixes
**Date:** November 5, 2025
**Time to Complete:** 45-60 minutes
**Bugs Fixed:** BUG-002, BUG-003, BUG-004

---

## 🎯 What's Been Fixed

✅ **BUG-004: Statistical Libraries Restored**
- Added numpy, scipy, pandas, statsmodels, scikit-learn, matplotlib, seaborn
- Platform can now perform actual meta-analysis calculations
- Ready to deploy

---

## 🚀 Quick Deployment Steps

### Step 1: Deploy Code Changes (5 minutes)

```bash
# 1. Commit the fixes
git add backend/requirements.txt backend/pyproject.toml
git commit -m "Fix BUG-004: Restore statistical libraries for meta-analysis"

# 2. Push to trigger Railway deployment
git push origin main

# 3. Monitor Railway build (takes 2-3 minutes)
# Watch for: "Successfully installed numpy-1.26.2 scipy-1.11.4 pandas-2.1.4 ..."
```

**Expected:** Build time increases to 2-3 minutes (acceptable).

---

### Step 2: Add Redis to Railway (5 minutes)

**Fix BUG-002: Redis not deployed**

1. Go to https://railway.app → Your Project
2. Click **"+ New"**
3. Select **"Database"** → **"Add Redis"**
4. Railway auto-provisions (takes 30-60 seconds)
5. Verify `REDIS_URL` injected to backend service
6. Wait for backend to auto-redeploy

**Test:**
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed
# Should show: "redis": {"status": "healthy"}
```

---

### Step 3: Deploy Celery Worker (20 minutes)

**Fix BUG-003: Celery workers not running**

#### 3a. Create Worker Service

1. Go to Railway Project
2. Click **"+ New"** → **"Empty Service"**
3. Name: `celery-worker`

#### 3b. Configure Build

1. Click **"Settings"** tab
2. Under **"Build"**:
   - Builder: **Dockerfile**
   - Dockerfile Path: `backend/Dockerfile`
   - Watch Paths: `backend/**`

#### 3c. Set Start Command

1. Under **"Deploy"** → **"Start Command"**:
```bash
celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications
```

#### 3d. Configure Environment Variables

1. Click **"Variables"** tab
2. Click **"Reference Variables"** → Select **backend** service
3. Or manually add:

```bash
DATABASE_URL=${{ PostgreSQL.DATABASE_URL }}
REDIS_URL=${{ Redis.REDIS_URL }}
ANTHROPIC_API_KEY=<copy-from-backend>
SECRET_KEY=<copy-from-backend>
DEBUG=false
LOG_LEVEL=INFO
```

#### 3e. Connect to GitHub

1. Click **"Settings"** → **"Source"**
2. Connect to same GitHub repo as backend
3. Branch: `main`

#### 3f. Deploy

1. Railway auto-deploys
2. Check logs for: `celery@worker-1 ready.`

**Test:**
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed
# Should show: "celery": {"status": "healthy"}
```

---

## ✅ Verification Checklist

After completing all steps:

- [ ] Railway build shows statistical libraries installed
- [ ] No import errors in backend logs
- [ ] Redis service running in Railway
- [ ] Health endpoint shows Redis healthy
- [ ] Worker service running in Railway
- [ ] Worker logs show "celery@worker-1 ready"
- [ ] Health endpoint shows Celery healthy

**Full health check:**
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

---

## 📊 What Changed

### Files Modified
- ✏️ `backend/requirements.txt` - Added 7 statistical libraries
- ✏️ `backend/pyproject.toml` - Added same libraries for Poetry

### Railway Services
- 📦 **Backend** - Will redeploy with new libraries (2-3 min build)
- 🆕 **Redis** - New service (auto-provisioned)
- 🆕 **Celery Worker** - New service (manually configured)

### Build Impact
- Build time: 60-90s → 120-180s (acceptable)
- Image size: ~400 MB → ~800 MB (acceptable)
- Monthly cost: ~$15 → ~$30 (necessary)

---

## 🆘 Troubleshooting

### Issue: Build fails with library errors
**Solution:** Libraries are large, build may take 3-4 minutes. Wait for completion.

### Issue: Redis shows unhealthy
**Solution:** Verify `REDIS_URL` is injected to backend service. Check Redis service is running.

### Issue: Worker won't start
**Solution:**
1. Verify Redis is healthy first
2. Check worker has all environment variables
3. Look for errors in worker logs

### Issue: Worker can't connect to Redis
**Solution:** Ensure worker service has `REDIS_URL` variable referencing Redis service.

---

## 📚 Detailed Documentation

For comprehensive details, see:

- **INFRASTRUCTURE_FIX_GUIDE.md** - Complete step-by-step guide with explanations
- **INFRASTRUCTURE_BUG_FIX_REPORT.md** - Full analysis and technical details
- **railway-celery-worker.toml** - Worker configuration reference

---

## 💰 Cost Estimate

**New monthly costs:**

| Service | Cost/month |
|---------|------------|
| Backend (FastAPI) | ~$12 |
| PostgreSQL | ~$3 |
| Redis | ~$3 |
| Celery Worker | ~$12 |
| **Total** | **~$30** |

**Previous:** ~$15/month
**Increase:** +100% (but platform now actually works)

---

## 🎉 Success!

Once all three steps are complete:

✅ Platform can perform meta-analysis calculations
✅ Background jobs execute properly
✅ Caching and rate limiting work
✅ Long-running tasks don't timeout
✅ System is production-ready

---

**Questions?** See full documentation or contact DevOps team.

**Last Updated:** November 5, 2025
