# Deployment Verification Quick Start

## Run Verification (1 Command)

```bash
./verify_production_deployment.sh
```

## What You'll See

### Success (All Green)
```
✓ Backend is reachable (HTTP 200)
✓ Service status: healthy
✓ Database connection: connected
✓ All 28 tests passed
```

### Warning (Yellow)
```
⚠ Backend response time: 2500ms (consider optimization)
⚠ CORS headers not found - may cause frontend issues
```

### Failure (Red)
```
✗ Backend unreachable (HTTP 500)
✗ Database connection: disconnected
✗ User login failed (HTTP 401)
```

## Quick Troubleshooting

### Problem: Backend Unreachable
```bash
# Check Railway deployment
railway status

# View logs
railway logs

# Restart service
railway up
```

### Problem: Database Issues
```bash
# Check database connection
railway run rails db:migrate:status

# Run migrations
railway run rails db:migrate
```

### Problem: Authentication Fails
```bash
# Verify JWT secret is set
railway variables

# Check auth service logs
railway logs --filter auth
```

## Read the Report

```bash
# View JSON report
cat production_deployment_report.json | jq .

# Check specific sections
jq .results production_deployment_report.json
jq .issues production_deployment_report.json
jq .recommendations production_deployment_report.json
```

## Manual Testing URLs

After script runs, test these manually:

**Backend:**
- Health: https://meta-analysis-tool-production.up.railway.app/api/v1/health
- Researchers: https://meta-analysis-tool-production.up.railway.app/api/v1/researchers
- Manuscripts: https://meta-analysis-tool-production.up.railway.app/api/v1/manuscripts

**Frontend:**
- Homepage: https://meta-analysis-tool.vercel.app
- Peer Review: https://meta-analysis-tool.vercel.app/tools/peer-review
- Reviewer Matcher: https://meta-analysis-tool.vercel.app/tools/reviewer-matcher

## Success Criteria

- [ ] All 28 tests pass
- [ ] Backend health: `healthy`
- [ ] Frontend status: `up`
- [ ] Response times < 2000ms
- [ ] No critical issues in report
- [ ] CORS headers present
- [ ] Authentication working

## When to Run

1. After every production deployment
2. Before announcing new features
3. After infrastructure changes
4. During incident investigation
5. Weekly health checks

## Get Help

Full documentation: `DEPLOYMENT_VERIFICATION.md`
