# RUN THIS NOW - Deployment Verification

## Step 1: Run the Script

```bash
cd /Users/brandon/meta-analysis-tool
./verify_production_deployment.sh
```

## What Happens Next

The script will:

1. Test backend health at Railway
2. Verify database connection
3. Test authentication (creates a test user)
4. Test all 28 API endpoints
5. Test frontend at Vercel
6. Check CORS and security
7. Measure performance
8. Generate JSON report

**Expected Duration:** 30-60 seconds

## Expected Output

You should see:

```
╔═══════════════════════════════════════════════════════════╗
║   Production Deployment Verification                     ║
╚═══════════════════════════════════════════════════════════╝

Backend URL:  https://meta-analysis-tool-production.up.railway.app
Frontend URL: https://meta-analysis-tool.vercel.app

======================================
1. Backend Health & Infrastructure
======================================
✓ Backend is reachable (HTTP 200)
✓ Service status: healthy
✓ Database connection: connected
...

======================================
Deployment Verification Summary
======================================
Total Tests:    28
Passed:         28
Failed:         0
Success Rate:   100.00%

╔═══════════════════════════════════════════════════════════╗
║   ✓ ALL TESTS PASSED - DEPLOYMENT VERIFIED               ║
╚═══════════════════════════════════════════════════════════╝
```

## Step 2: Check the Report

```bash
cat production_deployment_report.json | jq .
```

You'll see:

```json
{
  "timestamp": "2025-11-10T...",
  "results": {
    "backend_health": "healthy",
    "frontend_status": "up",
    "endpoints_tested": 28,
    "endpoints_passed": 28,
    "endpoints_failed": 0,
    "success_rate": 100.00
  },
  "issues": [],
  "recommendations": []
}
```

## Step 3: Share the Results

If all tests pass, you can confidently announce:

**Deployment Successful**
- 23,829 lines of code deployed to production
- Backend: Railway (healthy)
- Frontend: Vercel (up)
- All 28 endpoints verified
- New features live:
  - Reviewer Matcher
  - Peer Review System
  - Progress Tracking

## If Issues Occur

### Backend Unreachable
```bash
# Check Railway status
railway status

# View logs
railway logs

# Restart if needed
railway up
```

### Authentication Fails
```bash
# Check environment variables
railway variables

# Verify JWT_SECRET is set
railway variables | grep JWT
```

### Frontend Issues
```bash
# Check Vercel deployment
vercel inspect https://meta-analysis-tool.vercel.app

# View logs
vercel logs
```

## Quick Commands Reference

```bash
# Run verification
./verify_production_deployment.sh

# View report
cat production_deployment_report.json | jq .

# Check specific sections
jq '.results' production_deployment_report.json
jq '.issues' production_deployment_report.json
jq '.recommendations' production_deployment_report.json

# Save output to file
./verify_production_deployment.sh | tee verification_$(date +%Y%m%d_%H%M%S).log
```

## Success Checklist

- [ ] Script completed without errors
- [ ] Exit code = 0
- [ ] All 28 tests passed
- [ ] Backend health = "healthy"
- [ ] Frontend status = "up"
- [ ] No issues in report
- [ ] Response times < 2000ms

## Manual Verification

Open these URLs in your browser:

1. Backend Health: https://meta-analysis-tool-production.up.railway.app/api/v1/health
2. Frontend Home: https://meta-analysis-tool.vercel.app
3. Peer Review: https://meta-analysis-tool.vercel.app/tools/peer-review
4. Reviewer Matcher: https://meta-analysis-tool.vercel.app/tools/reviewer-matcher
5. Meta-Analysis: https://meta-analysis-tool.vercel.app/tools/meta-analysis

All should load without errors.

## Need Help?

1. Read `VERIFICATION_QUICK_START.md` for troubleshooting
2. Check `DEPLOYMENT_VERIFICATION.md` for full docs
3. Review `sample_verification_output.txt` for expected output
4. Compare your report to `sample_deployment_report.json`

## Run It Now!

```bash
./verify_production_deployment.sh
```

That's it! Your production deployment will be fully verified in under 60 seconds.
