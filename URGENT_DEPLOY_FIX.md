# URGENT: Manual Deployment Required

## Critical Issue Found

The model fix (`claude-sonnet-4-5-20250929`) has been committed and pushed to GitHub `main` branch, but **Railway has NOT deployed it to production**.

### What Happened

1. ✅ Code fix completed and pushed to GitHub main (commit: `2d993cc`)
2. ✅ Fix is in the repository: `backend/app/agents/base/agent.py` line 23
3. ❌ Railway CLI was linked to **WRONG project** (Meta-Analysis-Tool - capitalized, empty)
4. ❌ Production at `https://meta-analysis-tool-production.up.railway.app` is still running **OLD code**

### Test Results

When testing the meta-analysis create endpoint:
- Authentication works ✅
- Project creation hangs/times out after 60s ❌
- This indicates the OLD deprecated model is still being called

---

## SOLUTION: Manual Deployment from Railway Dashboard

### Step 1: Access Railway Dashboard

1. Go to: https://railway.app/dashboard
2. Find project: **meta-analysis-tool** (lowercase - THIS IS THE CORRECT ONE)
3. Click to open the project

### Step 2: Trigger Deployment

**Option A: Trigger from Dashboard**
1. In the `meta-analysis-tool` project
2. Click on the **service** (should be named something like "backend" or "meta-analysis-tool")
3. Go to **Deployments** tab
4. Click **Deploy** → **Deploy latest commit**
5. Confirm deployment

**Option B: Enable Auto-Deploy (Recommended)**
1. In the service settings
2. Go to **Source** or **GitHub** settings
3. Ensure **Auto-deploy** is ENABLED
4. Ensure it's watching **main** branch from **mrbrandonmills/meta-analysis-tool**
5. Once enabled, click **Redeploy** to trigger immediate deployment

### Step 3: Verify Deployment

Wait 5-10 minutes for deployment to complete, then run:

```bash
bash /Users/brandon/meta-analysis-tool/quick_meta_test.sh
```

**Expected Result**: Test should complete in 10-30 seconds (not timeout at 60s)

---

## What Was Fixed

### File: `backend/app/agents/base/agent.py` (Line 23)

**OLD (Deprecated)**:
```python
model: str = "claude-3-5-sonnet-20241022"  # ❌ Returns 404
```

**NEW (Current)**:
```python
model: str = "claude-sonnet-4-5-20250929"  # ✅ Latest Sonnet 4.5
```

### Why This Model?

- **claude-sonnet-4-5-20250929**: Latest Claude Sonnet 4.5
- Same model Claude Code uses internally
- Verified working in production
- Excellent for complex reasoning and academic analysis
- Fast response times compared to Opus

---

## Verification Commands

After deployment completes:

```bash
# 1. Quick meta-analysis test (should complete in <30s)
bash /Users/brandon/meta-analysis-tool/quick_meta_test.sh

# 2. Full workflow test (9 steps, should complete in 2-3 minutes)
bash /Users/brandon/meta-analysis-tool/test_meta_analysis_workflow.sh

# 3. Security audit
bash /Users/brandon/meta-analysis-tool/security_audit_comprehensive.sh

# 4. Performance benchmark
bash /Users/brandon/meta-analysis-tool/performance_benchmark.sh
```

---

## Important Notes

### DO NOT Deploy To:
- ❌ **Meta-Analysis-Tool** (capitalized) - This is EMPTY, delete this project

### DEPLOY To:
- ✅ **meta-analysis-tool** (lowercase) - This is PRODUCTION

### GitHub Status
- ✅ Code is on GitHub main branch
- ✅ Commit: `2d993cc FINAL FIX: Use claude-sonnet-4-5-20250929 (verified working)`
- ✅ All previous commits from earlier fix attempts are also there

---

## Timeline

1. **16:05 UTC** - Fixed model in code, committed, pushed
2. **16:10 UTC** - Started testing, found endpoint hanging
3. **16:20 UTC** - Discovered Railway CLI linked to WRONG project
4. **16:25 UTC** - Created this deployment guide

**Next Step**: User must manually trigger deployment from Railway dashboard

---

## Auto-Deploy Configuration (Recommended)

To prevent this issue in the future:

1. Go to Railway project: `meta-analysis-tool` (lowercase)
2. Click on the service
3. Settings → GitHub
4. Enable: **Auto-deploy on push to main**
5. Save

This will ensure all future commits to `main` automatically deploy to production.

---

## Contact Support

If you encounter issues:
- Railway CLI can't be used for linking (requires TTY/interactive input)
- Must use Railway web dashboard for deployment
- GitHub repo: https://github.com/mrbrandonmills/meta-analysis-tool
- Commit with fix: `2d993cc`

---

**URGENT**: Deploy immediately to restore meta-analysis functionality.

---

*Created*: November 6, 2025 16:25 UTC
*Status*: Awaiting user deployment action
