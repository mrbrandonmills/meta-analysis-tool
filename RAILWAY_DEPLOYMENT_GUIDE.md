# EMERGENCY RAILWAY DEPLOYMENT GUIDE
**BOARD MEETING READINESS - EXECUTE IN 35 MINUTES**

---

## 🚨 CRITICAL PATH - DO THESE IN ORDER

### ✅ PREREQUISITE CHECK (2 minutes)

**Current Status:**
- ✅ Backend deployed: `https://meta-analysis-tool-production.up.railway.app`
- ✅ PostgreSQL database: Healthy
- ❌ Redis: **MISSING - DEPLOY NOW**
- ❌ Celery workers: **MISSING - DEPLOY NOW**
- ❌ Database migrations: **NOT RUN - BLOCKS AUTH**

**Railway Project:** meta-analysis-tool

---

## 🔴 FIX 1: DEPLOY REDIS (10 minutes)

### Step-by-Step Instructions:

1. **Open Railway Dashboard**
   ```
   URL: https://railway.app/dashboard
   → Find project: "meta-analysis-tool"
   → Click to open
   ```

2. **Add Redis Database**
   - Click **"+ New"** button (top right of canvas)
   - Select **"Database"**
   - Choose **"Add Redis"**
   - Railway auto-configures:
     - Name: `redis`
     - Plan: Shared (free)
     - Memory: 512MB
     - Region: Matched to backend

3. **Wait for Deployment (2-3 minutes)**
   - Redis status indicator will change from "Deploying" → "Active"
   - Railway automatically creates `REDIS_URL` variable

4. **Verify Environment Variables**
   - Click on **backend service**
   - Go to **"Variables"** tab
   - Confirm `REDIS_URL` exists (format: `redis://default:xxxxx@host:port`)
   - If missing, add manually:
     - Click **"+ New Variable"**
     - Select **"Reference Variable"**
     - Choose **"redis"** service
     - Select **"REDIS_URL"**

5. **Redeploy Backend to Pick Up Redis**
   - In backend service, click **"Deployments"** tab
   - Click **"Redeploy"** button (three dots menu → Redeploy)
   - Wait ~2 minutes for deployment

### Verification:
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health

# Expected Output:
{
  "database": {"status": "healthy"},
  "redis": {"status": "healthy"},  ← Should show healthy
  "celery": {"status": "unknown"}
}
```

**🎯 SUCCESS CRITERIA:** Redis status = "healthy"

---

## 🔴 FIX 2: RUN DATABASE MIGRATIONS (5 minutes)

### OPTION A: Modify Start Command (RECOMMENDED - Permanent Fix)

1. **Update Backend Service Start Command**
   - Go to backend service
   - Click **"Settings"** tab
   - Scroll to **"Deploy"** section
   - Find **"Start Command"** field
   - Change from:
     ```bash
     /app/start.sh
     ```
   - To:
     ```bash
     alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 2 --app-dir /app
     ```
   - Click **"Save"**

2. **Deploy Changes**
   - Click **"Deploy"** → **"Deploy Latest"**
   - Wait ~2 minutes

3. **Check Deployment Logs**
   - Click **"Deployments"** tab → Latest deployment
   - Click **"View Logs"**
   - Look for:
     ```
     INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial_schema
     INFO  [alembic.runtime.migration] Running upgrade 001 -> 002_add_user_tables
     ```

### OPTION B: One-Time Command (If Railway Provides Shell)

1. **Access Service Shell**
   - In backend service, look for **"Shell"** or **"Run Command"** option
   - If available, run:
     ```bash
     alembic upgrade head
     ```

2. **Verify Migration**
   ```bash
   alembic current
   # Should show: 002_add_user_tables (head)
   ```

### Verification:
```bash
# Test user registration (should return 201, not 500)
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'

# Expected: HTTP 201 Created
# Response includes: user_id, email, access_token
```

**🎯 SUCCESS CRITERIA:** User registration returns 201 (not 500)

---

## 🔴 FIX 3: DEPLOY CELERY WORKER SERVICE (20 minutes)

### Step-by-Step Instructions:

1. **Add New Service**
   - In Railway project dashboard
   - Click **"+ New"** button
   - Select **"Empty Service"**
   - Name it: `meta-analysis-worker`

2. **Configure GitHub Repository**
   - Click on the new service
   - Click **"Settings"** tab
   - Under **"Source"** section, click **"Connect Repo"**
   - Select your repository (same as backend)
   - Choose branch: `main` (or your production branch)

3. **Configure Build Settings**
   - In **"Settings"** tab, scroll to **"Build"** section
   - Set **"Builder"**: `DOCKERFILE`
   - Set **"Dockerfile Path"**: `backend/Dockerfile`
   - Set **"Watch Paths"**: `backend/**`

4. **Configure Start Command**
   - Still in **"Settings"** → **"Deploy"** section
   - Set **"Start Command"**:
     ```bash
     celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4
     ```

5. **Add Environment Variables** (CRITICAL - Copy from Backend Service)

   Click **"Variables"** tab, add these:

   **Required Variables:**
   ```
   PYTHONUNBUFFERED = 1
   WORKER_TYPE = celery
   DEBUG = false
   LOG_LEVEL = INFO
   ```

   **Reference Variables** (link to existing services):
   - `DATABASE_URL` → Reference → PostgreSQL service → DATABASE_URL
   - `REDIS_URL` → Reference → Redis service → REDIS_URL

   **Shared Secrets** (copy from backend service):
   - `ANTHROPIC_API_KEY` → Copy value from backend
   - `OPENAI_API_KEY` → Copy value from backend
   - `SECRET_KEY` → Copy value from backend
   - `SENTRY_DSN` → Copy value from backend (optional)
   - `PUBMED_API_KEY` → Copy value from backend (optional)
   - `PUBMED_EMAIL` → Copy value from backend (optional)

6. **Configure Deployment Settings**
   - **Number of Replicas**: `1`
   - **Restart Policy**: `ON_FAILURE`
   - **Max Retries**: `10`
   - **Health Check**: Leave disabled (workers don't expose HTTP)

7. **Deploy the Worker**
   - Click **"Deploy"** → **"Deploy Latest"**
   - Wait ~3-4 minutes for build and deployment

### Verification:

**Method 1: Check Worker Logs**
```
1. Go to worker service → "Deployments" tab
2. Click latest deployment → "View Logs"
3. Look for:
   - "[INFO/MainProcess] Connected to redis://..."
   - "[INFO/MainProcess] celery@<hostname> ready."
   - "celery@<hostname> v5.x.x"
```

**Method 2: Test Celery Health Check**
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health

# Expected:
{
  "database": {"status": "healthy"},
  "redis": {"status": "healthy"},
  "celery": {"status": "healthy", "workers": 1}  ← Should show healthy
}
```

**Method 3: Submit a Test Task**
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/search/pubmed \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "query": "cancer treatment",
    "max_results": 10
  }'

# Expected: Returns task_id
# Check worker logs for task processing
```

**🎯 SUCCESS CRITERIA:** Celery status = "healthy" with workers > 0

---

## 🎯 FINAL VERIFICATION CHECKLIST (3 minutes)

Run these commands to verify everything works:

### 1. Health Check - All Services Green
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health

# EXPECTED:
{
  "status": "healthy",
  "version": "1.0.0",
  "database": {"status": "healthy"},
  "redis": {"status": "healthy"},
  "celery": {"status": "healthy", "workers": 1}
}
```

### 2. User Registration - Auth Works
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "board@example.com",
    "password": "SecurePass123!",
    "full_name": "Board Member"
  }'

# EXPECTED: HTTP 201
# Response includes: user_id, email, access_token
```

### 3. User Login - JWT Tokens Work
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "board@example.com",
    "password": "SecurePass123!"
  }'

# EXPECTED: HTTP 200
# Response includes: access_token, refresh_token, token_type
```

### 4. Background Tasks - Celery Processing
```bash
# First, login to get token
TOKEN=$(curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"board@example.com","password":"SecurePass123!"}' \
  | jq -r '.access_token')

# Then submit a search task
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/search/pubmed \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"cancer treatment","max_results":5}'

# EXPECTED: Returns task_id
# Check worker logs in Railway for task execution
```

---

## 📊 SERVICE ARCHITECTURE (After Deployment)

```
┌─────────────────────────────────────────────────────────────┐
│                    Railway Project                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Backend    │──────│  PostgreSQL  │      │   Redis   │ │
│  │  (FastAPI)   │      │  (Database)  │      │ (Cache +  │ │
│  │              │      │              │      │  Broker)  │ │
│  └──────┬───────┘      └──────────────┘      └─────┬─────┘ │
│         │                                            │       │
│         │                                            │       │
│  ┌──────┴──────────────────────────────────────────┴─────┐ │
│  │              Celery Worker Service                     │ │
│  │  (Background task processing)                          │ │
│  │  - Literature search                                   │ │
│  │  - Meta-analysis                                       │ │
│  │  - Reviewer profiling                                  │ │
│  │  - Notifications                                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚠️ TROUBLESHOOTING

### Problem: Redis shows "unhealthy"
**Solution:**
1. Check Redis service status in Railway (should be "Active")
2. Verify `REDIS_URL` exists in backend service variables
3. Redeploy backend service to pick up Redis connection

### Problem: Celery shows "unknown" or "unhealthy"
**Solution:**
1. Check worker service logs for connection errors
2. Verify worker has `REDIS_URL` environment variable
3. Ensure start command is exactly: `celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4`
4. Check Redis is healthy first (Celery depends on Redis)

### Problem: User registration returns 500 error
**Solution:**
1. Check backend logs for migration errors
2. Verify start command includes: `alembic upgrade head`
3. Manually run migration if needed (see FIX 2, Option B)
4. Check PostgreSQL service is healthy

### Problem: Worker service won't deploy
**Solution:**
1. Verify Dockerfile path is `backend/Dockerfile`
2. Check build logs for Python dependency errors
3. Ensure all environment variables are set
4. Verify worker has access to DATABASE_URL and REDIS_URL

### Problem: "No such file or directory: alembic"
**Solution:**
1. Check backend/alembic directory exists in repository
2. Verify Dockerfile copies alembic folder: `COPY backend/alembic ./alembic`
3. Redeploy with clean build cache

---

## ⏱️ EXECUTION TIMELINE

| Step | Task | Duration | Cumulative |
|------|------|----------|------------|
| 0 | Prerequisite check | 2 min | 2 min |
| 1 | Deploy Redis | 10 min | 12 min |
| 2 | Run migrations | 5 min | 17 min |
| 3 | Deploy Celery worker | 20 min | 37 min |
| 4 | Final verification | 3 min | **40 min** |

**BUFFER:** 20 minutes for troubleshooting
**TOTAL TIME:** ~1 hour (with buffer)

---

## 🎯 SUCCESS METRICS FOR BOARD MEETING

**Service Availability:**
- ✅ Backend API: 99.9% uptime
- ✅ Database: Healthy, no connection errors
- ✅ Redis: Healthy, sub-ms latency
- ✅ Celery: Workers active, processing tasks

**Functional Tests Passing:**
- ✅ User registration (HTTP 201)
- ✅ User login (HTTP 200, JWT tokens)
- ✅ Background tasks (task_id returned, worker processes)
- ✅ Health checks (all services green)

**Performance:**
- ✅ API response time: <200ms (p95)
- ✅ Database queries: <50ms (p95)
- ✅ Task queue: <5 seconds to worker pickup

---

## 📞 EMERGENCY CONTACTS

**If Deployment Fails:**
1. Check Railway status: https://railway.statuspage.io
2. Review deployment logs in Railway dashboard
3. Rollback to last working deployment (if needed)

**Railway Support:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app

---

## 🚀 POST-DEPLOYMENT NEXT STEPS

**After Board Meeting:**
1. **Add Celery Beat** (scheduled tasks)
   - Create third service: `meta-analysis-scheduler`
   - Start command: `celery -A app.workers.celery_app beat --loglevel=info`

2. **Enable Monitoring**
   - Add Sentry for error tracking
   - Set up Prometheus/Grafana for metrics
   - Configure CloudWatch alarms

3. **Optimize Scaling**
   - Configure auto-scaling for backend (2-4 replicas)
   - Add more Celery workers for high load
   - Implement Redis clustering for reliability

4. **Security Hardening**
   - Enable Railway private networking
   - Add rate limiting middleware
   - Implement API key rotation
   - Set up WAF rules

---

**DEPLOYMENT OWNER:** DevOps Engineer
**LAST UPDATED:** 2025-11-05
**STATUS:** READY FOR EXECUTION
