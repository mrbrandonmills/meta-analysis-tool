# SMTP Configuration for Railway

**Status:** Pending - GitHub Actions deployment is failing, preventing automatic deployment

## Issue Identified

The GitHub Actions workflow (deploy.yml) is failing, which prevents automatic deployment to Railway. The workflow failed with:
```
X This run likely failed because of a workflow file issue.
Run ID: 19622263775
```

## Required Actions

### Option 1: Fix GitHub Actions and Let It Deploy (Recommended)
1. Check the GitHub Actions workflow logs at: https://github.com/mrbrandonmills/meta-analysis-tool/actions/runs/19622263775
2. Fix the workflow issue (likely missing secrets or configuration)
3. Re-run the workflow or push a fix
4. GitHub Actions will automatically deploy to Railway and run migrations

### Option 2: Manual Railway Deployment (Immediate)
Since GitHub Actions is failing, you can manually deploy using Railway dashboard:

1. **Go to Railway Dashboard:**
   - https://railway.com/project/b0e4e10d-b739-4b8e-88e9-ba3e9d99968c

2. **Manually Trigger Deployment:**
   - Click on the "backend" or "meta-analysis-tool" service
   - Go to "Deployments" tab
   - Click "Deploy" button (or it should auto-deploy from GitHub push)
   - Wait for build to complete (Docker build takes 5-10 minutes)

3. **Once Deployment Completes, Configure SMTP Variables:**

Navigate to your backend service → Variables tab and add:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=therealbrandonmills@gmail.com
SMTP_PASSWORD=izez hzpb rvaw tebd
SMTP_FROM_EMAIL=noreply@metaanalysistool.com
SMTP_FROM_NAME=Meta-Analysis Tool
SMTP_USE_TLS=true
```

**IMPORTANT:** After adding these variables, Railway will automatically redeploy the service.

4. **Run Database Migration:**

Once the deployment is complete, open Railway's service terminal or use CLI:

```bash
# Option A: Railway Dashboard Terminal
# Go to backend service → Terminal tab → Run:
alembic upgrade heads

# Option B: Local Railway CLI (if project is linked)
railway run alembic upgrade heads
```

## What This Enables

Once SMTP is configured and migration is run:
- **Email Notifications:** All tier application emails will be sent from therealbrandonmills@gmail.com
- **Database Tables:** tier_applications and qualification_verifications tables will be created
- **API Endpoints:** 19 new tier application endpoints will be available
- **Automatic Verification:** ORCID, Google Scholar, CrossRef verification will work
- **Admin Review System:** Admin can approve/deny applications

## Gmail App Password Details

**Email:** therealbrandonmills@gmail.com
**App Password:** `izez hzpb rvaw tebd`
**App Name:** Meta Analysis Tool

## Next Steps After Configuration

1. **Test Health Endpoint:**
   ```bash
   curl https://meta-analysis-tool-production.up.railway.app/api/v1/health
   ```

2. **Verify Tier Endpoints Exist:**
   ```bash
   curl https://meta-analysis-tool-production.up.railway.app/docs
   # Look for /api/v1/tier-applications endpoints
   ```

3. **Create Admin Account** (brandon@brandonmills.com)

4. **Create Test Accounts** for each tier

5. **Test Complete Workflow** from application to approval

## Troubleshooting GitHub Actions

If you want to fix the GitHub Actions workflow instead:

1. **Check Required Secrets:**
   - Go to: https://github.com/mrbrandonmills/meta-analysis-tool/settings/secrets/actions
   - Verify these secrets exist:
     - `RAILWAY_TOKEN` (required for Railway deployment)
     - `ANTHROPIC_API_KEY` (required for tests)
     - `VERCEL_TOKEN` (required for frontend deployment)
     - `VERCEL_ORG_ID`
     - `VERCEL_PROJECT_ID`

2. **Check Workflow Syntax:**
   - The workflow uses `--service meta-analysis-tool` but the service might have a different name
   - Check Railway dashboard for exact service name
   - Update line 198 in `.github/workflows/deploy.yml` if needed

3. **Re-run Workflow:**
   ```bash
   gh run rerun 19622263775
   ```

---

**Created:** 2025-11-24
**App Password Provided:** 2025-11-24
**Deployment Status:** Blocked by GitHub Actions failure
