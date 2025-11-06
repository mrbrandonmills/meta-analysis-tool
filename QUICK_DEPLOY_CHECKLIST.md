# RAILWAY DEPLOYMENT CHECKLIST
**⏱️ 35-Minute Emergency Deployment**

---

## 📋 PRE-DEPLOYMENT (2 min)

- [ ] Railway account logged in: https://railway.app/dashboard
- [ ] Project "meta-analysis-tool" open
- [ ] Backend service running (green status)
- [ ] PostgreSQL database healthy

---

## 🔴 FIX 1: REDIS (10 min)

- [ ] Click "+ New" → "Database" → "Add Redis"
- [ ] Wait for Redis status: "Active" (2-3 min)
- [ ] Verify `REDIS_URL` in backend service variables
- [ ] Redeploy backend service
- [ ] **VERIFY:** `curl https://meta-analysis-tool-production.up.railway.app/api/v1/health`
- [ ] **CHECK:** `"redis": {"status": "healthy"}`

---

## 🔴 FIX 2: DATABASE MIGRATIONS (5 min)

- [ ] Go to backend service → "Settings"
- [ ] Find "Start Command" field
- [ ] Update to: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 2 --app-dir /app`
- [ ] Click "Save" and "Deploy"
- [ ] Check deployment logs for migration success
- [ ] **VERIFY:** `curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register ...`
- [ ] **CHECK:** HTTP 201 (not 500)

---

## 🔴 FIX 3: CELERY WORKER (20 min)

### Add Service
- [ ] Click "+ New" → "Empty Service"
- [ ] Name: `meta-analysis-worker`

### Configure Source
- [ ] "Settings" → "Source" → "Connect Repo"
- [ ] Select repository (same as backend)
- [ ] Branch: `main`

### Configure Build
- [ ] "Builder": `DOCKERFILE`
- [ ] "Dockerfile Path": `backend/Dockerfile`
- [ ] "Watch Paths": `backend/**`

### Configure Deployment
- [ ] "Start Command": `celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4`

### Add Variables
- [ ] `PYTHONUNBUFFERED` = `1`
- [ ] `WORKER_TYPE` = `celery`
- [ ] `DEBUG` = `false`
- [ ] `LOG_LEVEL` = `INFO`
- [ ] `DATABASE_URL` → Reference PostgreSQL
- [ ] `REDIS_URL` → Reference Redis
- [ ] `ANTHROPIC_API_KEY` → Copy from backend
- [ ] `OPENAI_API_KEY` → Copy from backend
- [ ] `SECRET_KEY` → Copy from backend
- [ ] `SENTRY_DSN` → Copy from backend (optional)
- [ ] `PUBMED_API_KEY` → Copy from backend (optional)
- [ ] `PUBMED_EMAIL` → Copy from backend (optional)

### Deploy
- [ ] Click "Deploy" → "Deploy Latest"
- [ ] Wait 3-4 minutes for build
- [ ] Check logs for "celery@<hostname> ready"
- [ ] **VERIFY:** `curl https://meta-analysis-tool-production.up.railway.app/api/v1/health`
- [ ] **CHECK:** `"celery": {"status": "healthy", "workers": 1}`

---

## ✅ FINAL VERIFICATION (3 min)

Run the verification script:
```bash
cd /Users/brandon/meta-analysis-tool
./verify-deployment.sh
```

**Expected Output:**
```
Database:     healthy
Redis:        healthy
Celery:       healthy

🎉 ALL SYSTEMS OPERATIONAL
Platform ready for board meeting!
```

---

## 🎯 SUCCESS CRITERIA

### All Green
- ✅ Database: healthy
- ✅ Redis: healthy
- ✅ Celery: healthy (workers: 1)

### Auth Working
- ✅ User registration: HTTP 201
- ✅ User login: HTTP 200 + JWT token

### Tasks Processing
- ✅ Background tasks accepted
- ✅ Worker logs show task execution

---

## ⚠️ TROUBLESHOOTING QUICK FIXES

| Problem | Quick Fix |
|---------|-----------|
| Redis unhealthy | Redeploy backend after Redis is "Active" |
| Registration 500 | Check migration ran in logs: "Running upgrade -> 002" |
| Celery unknown | Verify REDIS_URL variable exists in worker service |
| Worker won't start | Check start command has no typos |
| Missing env vars | Copy from backend service variables tab |

---

## 📞 HELP

**Stuck?** Check: `/Users/brandon/meta-analysis-tool/RAILWAY_DEPLOYMENT_GUIDE.md`

**Railway Issues?** https://discord.gg/railway

---

**TOTAL TIME:** 40 minutes (with 20-min buffer)
**COMPLETION:** ___/___  (Fill in time when done)
