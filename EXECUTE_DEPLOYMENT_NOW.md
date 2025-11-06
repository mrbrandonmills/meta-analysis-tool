# 🚀 EXECUTE DEPLOYMENT NOW - Complete Infrastructure Setup

**Status:** Ready to execute
**Time Required:** 30-45 minutes
**Goal:** All 3 infrastructure components deployed and verified

---

## ⚠️ IMPORTANT: Why Manual Steps Are Required

Railway CLI commands like `railway link` and `railway add` require interactive terminal input (TTY) that cannot be automated in scripts. Therefore, you'll need to execute these steps through Railway's web dashboard.

**What I've Prepared:**
- ✅ All code fixes deployed to GitHub
- ✅ Backend successfully deployed to Railway
- ✅ Complete configuration files ready
- ✅ Verification scripts created
- ✅ Comprehensive testing suite ready

**What You Need to Do:**
- 🔧 Deploy Redis (3-5 minutes, Railway dashboard)
- 🔧 Run migrations (5-10 minutes, Railway dashboard)
- 🔧 Deploy Celery workers (15-20 minutes, Railway dashboard)

---

## 🎯 DEPLOYMENT CHECKLIST

### Pre-Deployment Verification

```bash
cd /Users/brandon/meta-analysis-tool

# Check current status
curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.'

# Expected current state:
# ✅ database: healthy
# ❌ redis: unhealthy
# ❌ celery: unknown
```

---

## 📋 STEP 1: Deploy Redis Database (5 minutes)

### 1.1 Open Railway Dashboard
```bash
open https://railway.app/dashboard
```

### 1.2 Find Your Project
- Look for: **"meta-analysis-tool"** project
- Click to open it

### 1.3 Add Redis Service
1. Click **"+ New"** button (top right corner)
2. Select **"Database"**
3. Click **"Add Redis"**
4. Railway will automatically:
   - Provision Redis instance
   - Generate `REDIS_URL` environment variable
   - Inject `REDIS_URL` into your backend service
   - Trigger automatic backend redeployment

### 1.4 Wait for Deployment
- Watch the deployment logs (click on backend service → Deployments tab)
- Wait 2-3 minutes for backend to redeploy with Redis connection
- Look for: "Build successful" and "Deploy successful"

### 1.5 Verify Redis Connection
```bash
# Wait 3 minutes after deployment completes, then check:
curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.redis'

# Expected output:
# {
#   "status": "healthy",
#   "message": "Redis connection successful"
# }
```

**✅ CHECKPOINT 1:** Redis shows "healthy" status

---

## 📋 STEP 2: Run Database Migrations (10 minutes)

The migration files exist in your code but haven't been executed on the production database yet.

### 2.1 Option A: Update Start Command (Recommended)

This makes migrations run automatically on every deployment.

1. In Railway dashboard, click on **"backend"** service
2. Go to **"Settings"** tab
3. Scroll to **"Deploy"** section
4. Find **"Start Command"** (currently: `/app/start.sh`)
5. Click to edit
6. Change to:
   ```bash
   sh -c "alembic upgrade head && exec /app/start.sh"
   ```
7. Click **"Deploy"** button

### 2.2 Wait for Redeployment
- Backend will redeploy (2-3 minutes)
- Watch logs for migration messages:
  ```
  Running upgrade -> 001_multi_tool_schema
  Running upgrade 001 -> 002_remove_duplicate_name_column
  ✓ Database migrations completed successfully
  ```

### 2.3 Verify Migrations Applied
```bash
# Test user registration (should return 201, not 500)
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "test'$(date +%s)'@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }' | jq '.'

# Expected: HTTP 201 with user object (not 500 error)
```

### 2.4 Option B: Run Migration Manually (Alternative)

If you prefer to run migration as a one-time command:

1. Click on **"backend"** service
2. Click three dots menu (⋮) → **"Run Command"**
3. Enter command: `alembic upgrade head`
4. Click **"Run"**
5. Watch logs for migration completion

**✅ CHECKPOINT 2:** User registration returns HTTP 201 (success)

---

## 📋 STEP 3: Deploy Celery Worker Service (20 minutes)

This is the most involved step as it requires creating a new Railway service.

### 3.1 Create New Service

1. In Railway dashboard, click **"+ New"** button
2. Select **"Empty Service"**
3. Name it: `meta-analysis-worker`
4. Click **"Create"**

### 3.2 Connect to GitHub Repository

1. Click on **"meta-analysis-worker"** service
2. Go to **"Settings"** tab
3. Find **"Source"** section
4. Click **"Connect to GitHub"**
5. Select repository: **"mrbrandonmills/meta-analysis-tool"**
6. Branch: **"main"**
7. Click **"Connect"**

### 3.3 Configure Build Settings

1. Still in **"Settings"** tab
2. Find **"Build"** section
3. Set these values:
   - **Builder:** `DOCKERFILE`
   - **Dockerfile Path:** `backend/Dockerfile`
   - **Root Directory:** `/` (leave as root)

### 3.4 Configure Deployment Settings

1. In **"Settings"** tab, find **"Deploy"** section
2. Set **"Start Command":**
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4
   ```
3. Set **"Health Check Path":** (leave empty for workers)
4. Set **"Restart Policy":** `ON_FAILURE`

### 3.5 Configure Environment Variables

This is CRITICAL. The worker needs the same environment variables as the backend.

1. Click on **"Variables"** tab
2. Copy these variables from your **backend** service:

**How to copy from backend:**
- Open backend service in a new tab
- Go to Variables tab
- Copy each value

**Variables to set on worker:**

```bash
# Database connection
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis connection (Celery broker)
REDIS_URL=${{Redis.REDIS_URL}}

# API Keys
ANTHROPIC_API_KEY=<copy from backend>
OPENAI_API_KEY=<copy from backend>

# Security
SECRET_KEY=<copy from backend>

# Application settings
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
DEBUG=false

# Optional but recommended
PUBMED_EMAIL=<copy from backend if exists>
PUBMED_API_KEY=<copy from backend if exists>
SENTRY_DSN=<copy from backend if exists>
```

**IMPORTANT:** Make sure `REDIS_URL` is set! Workers cannot start without Redis.

### 3.6 Deploy Worker

1. After setting all environment variables, click **"Deploy"** button
2. Wait for build (5-10 minutes for first build)
3. Watch deployment logs:
   - Look for: `celery@meta-analysis-worker ready.`
   - Look for: Worker registering queues

### 3.7 Verify Celery Workers

```bash
# Check worker connection
curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.celery'

# Expected output:
# {
#   "status": "healthy",
#   "message": "1 worker(s) active"
# }
```

**✅ CHECKPOINT 3:** Celery shows "healthy" status with active workers

---

## ✅ FINAL VERIFICATION

### Run Complete Health Check

```bash
cd /Users/brandon/meta-analysis-tool
./verify-deployment.sh
```

**Expected Output:**
```
=========================================
Railway Deployment Verification
=========================================

TEST 1: Health Check - All Services
-------------------------------------------
✓ Health check endpoint accessible (HTTP 200)
✓ Database: healthy
✓ Redis: healthy
✓ Celery: healthy

TEST 2: User Registration (Database Migrations)
-------------------------------------------
✓ Registration successful (HTTP 201)

TEST 3: User Login (JWT Authentication)
-------------------------------------------
✓ Login successful (HTTP 200)
✓ JWT tokens received

=========================================
🎉 ALL SYSTEMS OPERATIONAL
=========================================

Platform ready for alpha testing!
```

---

## 📊 POST-DEPLOYMENT TESTING

### Test 1: Complete Authentication Flow

```bash
# 1. Register a new user
TIMESTAMP=$(date +%s)
REGISTER_RESPONSE=$(curl -s -X POST \
  https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d "{
    \"email\": \"alpha-test-${TIMESTAMP}@example.com\",
    \"password\": \"AlphaTest123!\",
    \"full_name\": \"Alpha Tester\"
  }")

echo "Registration: $REGISTER_RESPONSE"

# 2. Login with new user
LOGIN_RESPONSE=$(curl -s -X POST \
  https://meta-analysis-tool-production.up.railway.app/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d "{
    \"username\": \"alpha-test-${TIMESTAMP}@example.com\",
    \"password\": \"AlphaTest123!\"
  }")

echo "Login: $LOGIN_RESPONSE"

# 3. Extract access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "Access Token: $ACCESS_TOKEN"

# 4. Test protected endpoint
curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/users/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'
```

### Test 2: Background Job Submission

```bash
# Submit a background task
curl -s -X POST \
  https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/analyze \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "research_question": "What is the effectiveness of cognitive behavioral therapy for depression?",
    "study_design": "RCT",
    "outcome_measure": "depression scores"
  }' | jq '.'

# Should return task_id indicating background job was queued
```

### Test 3: Service Performance

```bash
# Check response times
time curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health > /dev/null
# Should be < 200ms

# Check database query performance
time curl -s "https://meta-analysis-tool-production.up.railway.app/docs" > /dev/null
# Should be < 1 second
```

---

## 🎯 SUCCESS CRITERIA

After completing all steps, you should have:

### Infrastructure (4 Railway Services)
- ✅ **backend** - FastAPI application (running)
- ✅ **Postgres** - Database (healthy)
- ✅ **Redis** - Cache + Broker (healthy)
- ✅ **meta-analysis-worker** - Celery workers (running)

### Health Checks (All Green)
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

### Authentication (Functional)
- ✅ User registration works (HTTP 201)
- ✅ User login works (HTTP 200)
- ✅ JWT tokens generated correctly
- ✅ Protected endpoints require authentication

### Background Jobs (Operational)
- ✅ Tasks can be submitted
- ✅ Workers pick up tasks
- ✅ Task status can be queried
- ✅ Results are returned

### API Documentation (Accessible)
- ✅ Swagger UI: https://meta-analysis-tool-production.up.railway.app/docs
- ✅ ReDoc: https://meta-analysis-tool-production.up.railway.app/redoc
- ✅ OpenAPI spec: https://meta-analysis-tool-production.up.railway.app/openapi.json

---

## 🔍 TROUBLESHOOTING

### Problem: Redis still shows "unhealthy" after deployment

**Solution:**
1. Verify Redis service is running in Railway dashboard
2. Check that REDIS_URL was auto-injected into backend
3. Backend may need manual redeploy to pick up new env var
4. Wait 2-3 minutes after Redis deployment

### Problem: Migrations fail with "relation already exists"

**Solution:**
1. This is OK if migrations ran before
2. Check migration history: `railway run -s backend alembic current`
3. If stuck, downgrade and re-upgrade:
   ```bash
   railway run -s backend alembic downgrade -1
   railway run -s backend alembic upgrade head
   ```

### Problem: Celery workers won't start

**Check:**
1. Redis is deployed and healthy (workers need Redis as broker)
2. REDIS_URL is set in worker environment variables
3. DATABASE_URL is set correctly
4. Check worker logs for specific error messages

**Common issues:**
- Missing REDIS_URL: Worker logs will show "Connection refused"
- Missing DATABASE_URL: Worker will crash on task execution
- Wrong start command: Worker won't start at all

### Problem: Worker builds but immediately exits

**Solution:**
1. Check that start command is exactly:
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4
   ```
2. Verify all environment variables are set
3. Check worker logs for Python import errors

---

## 💰 COST IMPLICATIONS

After deploying all 3 components:

```
Backend (FastAPI):         $5-10/month (Hobby plan)
PostgreSQL:                $0-5/month (shared)
Redis:                     $0-5/month (shared)
Celery Worker:             $5-10/month (Hobby plan)
─────────────────────────────────────────────
Total:                     $15-30/month

Variable costs:
- Anthropic API:           $0.10 per meta-analysis
- OpenAI API (optional):   $0.05 per query
─────────────────────────────────────────────
Estimated monthly total:   $50-100/month (with usage)
```

---

## 📈 NEXT STEPS (Week 1 Timeline)

### Today (Deployment Day)
- ✅ Deploy Redis (5 min)
- ✅ Run migrations (10 min)
- ✅ Deploy Celery workers (20 min)
- ✅ Verify all health checks (5 min)
- ✅ Run integration tests (10 min)

### Tomorrow (Testing Day)
- Test with real research question
- Verify meta-analysis calculations
- Test literature search across all 4 APIs
- Validate data exports
- Document any issues

### Days 3-5 (Alpha Testing Preparation)
- Performance testing
- Load testing (simulate multiple concurrent users)
- Fix any bugs discovered
- Optimize slow queries
- Enhance monitoring

### End of Week 1
- **Goal:** Alpha testing ready ✅
- Platform fully operational
- All features tested
- Performance acceptable
- Ready for first external users

---

## 📝 DEPLOYMENT CHECKLIST

Print this and check off as you complete each step:

```
REDIS DEPLOYMENT
[ ] Opened Railway dashboard
[ ] Found meta-analysis-tool project
[ ] Clicked "+ New" → "Database" → "Add Redis"
[ ] Waited for Redis provisioning (1-2 min)
[ ] Verified REDIS_URL injected into backend
[ ] Backend redeployed automatically (2-3 min)
[ ] Health check shows Redis healthy
[ ] Verified with: curl health endpoint

DATABASE MIGRATIONS
[ ] Opened backend service settings
[ ] Found "Start Command" section
[ ] Updated command to include migrations
[ ] Clicked "Deploy" button
[ ] Watched logs for migration messages
[ ] Saw "upgrade -> 001" and "upgrade 001 -> 002"
[ ] Saw "Database migrations completed successfully"
[ ] Tested registration endpoint (HTTP 201)
[ ] Registration works without 500 error

CELERY WORKER
[ ] Clicked "+ New" → "Empty Service"
[ ] Named service "meta-analysis-worker"
[ ] Connected to GitHub repository
[ ] Selected branch "main"
[ ] Set Dockerfile path: backend/Dockerfile
[ ] Set start command (full celery command)
[ ] Copied DATABASE_URL from backend
[ ] Copied REDIS_URL from backend
[ ] Copied ANTHROPIC_API_KEY from backend
[ ] Copied SECRET_KEY from backend
[ ] Set PYTHONUNBUFFERED=1
[ ] Set LOG_LEVEL=INFO
[ ] Clicked "Deploy"
[ ] Waited for build (5-10 min)
[ ] Saw "celery@meta-analysis-worker ready" in logs
[ ] Health check shows Celery healthy
[ ] Verified worker is processing tasks

FINAL VERIFICATION
[ ] Ran ./verify-deployment.sh
[ ] All 3 services show "healthy"
[ ] Registration works (HTTP 201)
[ ] Login works (HTTP 200)
[ ] Protected endpoints accessible
[ ] Background jobs can be submitted
[ ] API documentation accessible

ALPHA TESTING READY
[ ] Platform fully operational
[ ] All tests passing
[ ] Performance acceptable
[ ] Documentation updated
[ ] Ready for Week 1 completion
```

---

## 🚀 YOU'RE READY TO DEPLOY

**Time to complete:** 30-45 minutes
**Complexity:** Low (mostly point-and-click in Railway)
**Risk:** Very low (can rollback any service)
**Support:** Railway has excellent documentation and Discord

**Start now by opening:**
```bash
open https://railway.app/dashboard
```

Then follow this guide step-by-step. Check off each item in the checklist as you complete it.

**When done, run:**
```bash
./verify-deployment.sh
```

You'll see: **🎉 ALL SYSTEMS OPERATIONAL**

---

**Good luck! You've got this!** 🚀
