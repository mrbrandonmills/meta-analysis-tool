# Celery Worker Deployment - Action Plan

## Executive Summary
**Issue**: Celery workers showing "degraded" status with "No workers available" message
**Root Cause**: Worker service missing required environment variables
**Solution**: Configure environment variables and redeploy worker service
**Estimated Time**: 10-15 minutes
**Success Criteria**: Health endpoint shows `"celery": {"status": "healthy", "message": "1 worker(s) active"}`

---

## Prerequisites Verified ✅
- [x] Backend API is healthy
- [x] PostgreSQL database is healthy
- [x] Redis service is healthy
- [x] Worker service exists on Railway
- [x] Correct start command configured
- [x] Correct Dockerfile path configured

## What's Missing ❌
The **meta-analysis-worker** service is missing these environment variables:
- ANTHROPIC_API_KEY
- SECRET_KEY
- Possibly OPENAI_API_KEY
- Possibly LOG_LEVEL and PYTHONUNBUFFERED

The worker service likely has DATABASE_URL and REDIS_URL, but they need to be verified to use Railway variable references.

---

## Action Steps (Do This Now)

### Phase 1: Configure Environment Variables (5 minutes)

1. **Open Railway Dashboard**
   - Navigate to: https://railway.app/dashboard
   - Click: **Meta-Analysis-Tool** project

2. **Open Backend Service Variables (Reference Tab)**
   - Click: **backend** service
   - Click: **Variables** tab
   - **Keep this tab open** - you'll copy values from here

3. **Open Worker Service Variables (Configuration Tab)**
   - In a new tab/window, go back to Meta-Analysis-Tool project
   - Click: **meta-analysis-worker** service
   - Click: **Variables** tab

4. **Configure Worker Variables**

   Add or verify these variables in the worker service:

   | Variable Name | Value | Source |
   |--------------|-------|--------|
   | `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | ⚠️ Use variable reference |
   | `REDIS_URL` | `${{Redis.REDIS_URL}}` | ⚠️ Use variable reference |
   | `ANTHROPIC_API_KEY` | Copy from backend | Critical |
   | `SECRET_KEY` | Copy from backend | Critical |
   | `OPENAI_API_KEY` | Copy from backend | Recommended |
   | `PUBMED_API_KEY` | Copy from backend (if exists) | Optional |
   | `PUBMED_EMAIL` | Copy from backend (if exists) | Optional |
   | `PYTHONUNBUFFERED` | `1` | Recommended |
   | `LOG_LEVEL` | `INFO` | Recommended |

5. **Verify Variable References**
   - **Critical**: DATABASE_URL and REDIS_URL MUST use `${{...}}` syntax
   - **Do NOT** use hardcoded URLs like `postgresql://...` or `redis://...`
   - The variable references ensure workers always connect to the correct services

### Phase 2: Redeploy Worker Service (2 minutes)

1. **Trigger Redeployment**
   - In **meta-analysis-worker** service
   - Click: **⋯** (three dots menu) in top right
   - Select: **Redeploy**

2. **Monitor Deployment**
   - Click: **Deployments** tab
   - Click: Latest deployment
   - Watch logs for success indicators

### Phase 3: Verify Deployment (2-5 minutes)

1. **Watch Deployment Logs**

   Look for these **success indicators**:
   ```
   ✅ celery@meta-analysis-worker ready.
   ✅ Connected to redis://...
   ✅ Tasks loaded: app.workers.tasks.literature_search
   ```

   Watch for these **error indicators**:
   ```
   ❌ Connection refused → Check REDIS_URL
   ❌ ModuleNotFoundError → Check Dockerfile path
   ❌ Missing environment variable → Add the variable
   ❌ Invalid API key → Check ANTHROPIC_API_KEY
   ```

2. **Check Health Endpoint**

   After deployment completes (2-4 minutes), verify worker health:

   ```bash
   # Option 1: Use provided script
   ./verify-worker-health.sh

   # Option 2: Manual check
   curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.celery'
   ```

   **Expected response**:
   ```json
   {
     "status": "healthy",
     "message": "1 worker(s) active"
   }
   ```

3. **Continuous Monitoring (Optional)**

   Run the monitoring script to automatically track deployment:
   ```bash
   ./monitor-worker-deployment.sh
   ```

---

## Automated Assistance Scripts

### Quick Health Check
```bash
./verify-worker-health.sh
```
- Checks current worker status
- Shows success/failure clearly
- Takes 2 seconds

### Diagnostic Analysis
```bash
./diagnose-worker.sh
```
- Analyzes current deployment state
- Identifies specific issues
- Provides targeted fix recommendations
- Takes 5 seconds

### Deployment Monitoring
```bash
./monitor-worker-deployment.sh
```
- Continuously monitors worker health
- Checks every 15 seconds for 5 minutes
- Alerts on success or provides troubleshooting

### Interactive Configuration
```bash
./deploy-celery-worker.sh
```
- Step-by-step guided configuration
- Waits for user confirmation at each step
- Verifies deployment success
- Requires manual Railway Dashboard actions

---

## Common Issues & Solutions

### Issue 1: "No workers available" persists after 5 minutes
**Cause**: Environment variables not configured correctly
**Solution**:
1. Double-check all variables in worker service
2. Ensure REDIS_URL uses `${{Redis.REDIS_URL}}`
3. Verify ANTHROPIC_API_KEY is valid
4. Redeploy worker service again

### Issue 2: Worker logs show "Connection refused"
**Cause**: REDIS_URL is hardcoded instead of using variable reference
**Solution**:
1. Change REDIS_URL to: `${{Redis.REDIS_URL}}`
2. Redeploy worker service

### Issue 3: Worker logs show "Missing environment variable"
**Cause**: Required variable not set in worker service
**Solution**:
1. Identify the missing variable from error message
2. Copy value from backend service
3. Add to worker service
4. Redeploy worker service

### Issue 4: Worker logs show "ModuleNotFoundError"
**Cause**: Incorrect Dockerfile path or Python import issue
**Solution**:
1. Verify Dockerfile path is `backend/Dockerfile` (no leading slash)
2. Check build logs for errors
3. Ensure all dependencies are in requirements.txt

---

## Success Verification Checklist

After completing the action steps, verify:

- [ ] Worker service has all required environment variables
- [ ] DATABASE_URL = `${{Postgres.DATABASE_URL}}`
- [ ] REDIS_URL = `${{Redis.REDIS_URL}}`
- [ ] ANTHROPIC_API_KEY is set and valid
- [ ] SECRET_KEY is set
- [ ] Worker service has been redeployed
- [ ] Deployment completed without errors
- [ ] Deployment logs show "celery@meta-analysis-worker ready."
- [ ] Health endpoint returns `"status": "healthy"`
- [ ] Health endpoint shows "1 worker(s) active"

---

## Timeline Expectations

| Phase | Duration | Activity |
|-------|----------|----------|
| Configuration | 5 min | Add environment variables in Railway Dashboard |
| Deployment | 2-4 min | Railway builds and deploys worker service |
| Verification | 1-2 min | Check logs and health endpoint |
| **Total** | **8-11 min** | End-to-end deployment |

---

## What Happens Next

Once workers are healthy:

1. **Literature Search Tasks**
   - Users can initiate PubMed searches
   - Tasks will process in background
   - Results appear when complete

2. **Meta-Analysis Tasks**
   - AI-powered analysis of studies
   - Statistical computations
   - Report generation

3. **Reviewer Assignment Tasks**
   - Automatic reviewer selection
   - Email notifications
   - Deadline tracking

4. **Monitoring**
   - Workers process tasks continuously
   - Logs available in Railway Dashboard
   - Health endpoint shows active workers

---

## Support & Documentation

| Resource | Purpose | Command |
|----------|---------|---------|
| `RAILWAY_WORKER_FIX.md` | Detailed step-by-step guide | `cat RAILWAY_WORKER_FIX.md` |
| `WORKER_QUICK_FIX.md` | 3-step quick reference | `cat WORKER_QUICK_FIX.md` |
| `CELERY_WORKER_DEPLOYMENT.md` | Comprehensive documentation | `cat CELERY_WORKER_DEPLOYMENT.md` |
| `diagnose-worker.sh` | Diagnostic script | `./diagnose-worker.sh` |
| `verify-worker-health.sh` | Quick health check | `./verify-worker-health.sh` |
| `monitor-worker-deployment.sh` | Continuous monitoring | `./monitor-worker-deployment.sh` |

---

## Emergency Rollback

If something goes wrong:

1. **Restore Previous Configuration**
   - Railway Dashboard → meta-analysis-worker → Variables
   - Click "..." on any variable → View history
   - Restore previous values

2. **Redeploy to Previous Version**
   - Railway Dashboard → meta-analysis-worker → Deployments
   - Find last successful deployment
   - Click "..." → Redeploy

3. **Check Backend Service**
   - Ensure backend service is still healthy
   - Workers won't affect backend operation

---

## Contact & Support

If issues persist after following this guide:

1. Check Railway service status: https://railway.app/status
2. Review Railway documentation: https://docs.railway.app
3. Check worker logs for specific error messages
4. Verify all prerequisites are met
5. Ensure API keys are valid and not expired

---

**Last Updated**: 2025-11-06
**Status**: Ready for deployment
**Risk Level**: Low (only affects background task processing, not API)
