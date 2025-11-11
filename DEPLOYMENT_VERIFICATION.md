# Production Deployment Verification Guide

## Overview
Comprehensive verification script that tests all production endpoints, authentication, and new features after deployment to Railway and Vercel.

## Quick Start

```bash
# Run the verification script
./verify_production_deployment.sh
```

## What Gets Tested

### 1. Backend Health & Infrastructure
- Backend availability check
- Database connection status
- API version verification
- Root endpoint accessibility

### 2. Authentication & Security
- User registration flow
- Login and JWT token generation
- Token validation
- Protected endpoint access

### 3. Core API Endpoints
- Researchers API (`GET /api/v1/researchers`)
- Manuscripts API (`GET /api/v1/manuscripts`)
- Studies API (`GET /api/v1/studies`)
- Meta-Analysis API (`GET /api/v1/meta-analyses`)

### 4. New Feature APIs
- Reviewer Matcher (`GET /api/v1/reviewer-matches`)
- Peer Review System (`GET /api/v1/peer-reviews`)
- Progress Tracking (`GET /api/v1/tasks/progress`)

### 5. Frontend Application (Vercel)
- Homepage (`/`)
- Peer Review Tool (`/tools/peer-review`)
- Reviewer Matcher Tool (`/tools/reviewer-matcher`)
- Meta-Analysis Tool (`/tools/meta-analysis`)
- Dashboard (`/dashboard`)
- Static asset loading

### 6. Security & CORS Configuration
- CORS headers validation
- Security headers check
- Cross-origin request handling

### 7. Performance Metrics
- Backend response time measurement
- Frontend response time measurement
- Performance recommendations

## Expected Output

### Successful Deployment
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   Production Deployment Verification                     ║
║   Meta-Analysis Tool Platform                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Backend URL:  https://meta-analysis-tool-production.up.railway.app
Frontend URL: https://meta-analysis-tool.vercel.app
Timestamp:    2025-11-10T12:00:00Z

======================================
1. Backend Health & Infrastructure
======================================
ℹ Testing backend availability...
✓ Backend is reachable (HTTP 200)
✓ Service status: healthy
✓ Database connection: connected
✓ API version: 1.0.0
✓ Root endpoint accessible (HTTP 200)

======================================
2. Authentication & Security
======================================
ℹ Testing user registration...
✓ User registration successful (HTTP 201)
✓ JWT token received on registration
ℹ Testing user login...
✓ User login successful (HTTP 200)
✓ JWT token received and stored
ℹ Testing token validation...
✓ Token validation successful (HTTP 200)

======================================
3. Core API Endpoints
======================================
ℹ Testing Researchers API...
✓ Researchers API accessible (HTTP 200)
ℹ Testing Manuscripts API...
✓ Manuscripts API accessible (HTTP 200)
ℹ Testing Studies API...
✓ Studies API accessible (HTTP 200)

======================================
4. New Feature APIs
======================================
ℹ Testing Reviewer Matcher API...
✓ Reviewer Matcher API accessible (HTTP 200)
ℹ Testing Peer Review API...
✓ Peer Review API accessible (HTTP 200)
ℹ Testing Progress Tracking API...
✓ Progress Tracking API accessible (HTTP 200)
ℹ Testing Meta-Analysis API...
✓ Meta-Analysis API accessible (HTTP 200)

======================================
5. Frontend Application (Vercel)
======================================
ℹ Testing frontend endpoints...
✓ Homepage (HTTP 200)
✓ Peer Review Tool (HTTP 200)
✓ Reviewer Matcher Tool (HTTP 200)
✓ Meta-Analysis Tool (HTTP 200)
✓ Dashboard (HTTP 200)
ℹ Testing static asset loading...
✓ Static assets loading (favicon.ico - HTTP 200)

======================================
6. Security & CORS Configuration
======================================
ℹ Testing CORS headers...
✓ CORS headers present
ℹ Testing security headers...
✓ Security headers configured

======================================
7. Performance Metrics
======================================
ℹ Testing backend response time...
✓ Backend response time: 234ms (excellent)
ℹ Testing frontend response time...
✓ Frontend response time: 456ms (excellent)

======================================
8. Generating Report
======================================
✓ Report generated: production_deployment_report.json

======================================
Deployment Verification Summary
======================================

Total Tests:    28
Passed:         28
Failed:         0
Success Rate:   100.00%

Backend Health:  healthy
Frontend Status: up

╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ✓ ALL TESTS PASSED - DEPLOYMENT VERIFIED               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

## Report Format

The script generates a JSON report (`production_deployment_report.json`):

```json
{
  "timestamp": "2025-11-10T12:00:00Z",
  "deployment": {
    "backend_url": "https://meta-analysis-tool-production.up.railway.app",
    "frontend_url": "https://meta-analysis-tool.vercel.app"
  },
  "results": {
    "backend_health": "healthy",
    "frontend_status": "up",
    "endpoints_tested": 28,
    "endpoints_passed": 28,
    "endpoints_failed": 0,
    "success_rate": 100.00
  },
  "issues": [],
  "recommendations": [],
  "test_coverage": {
    "health_check": true,
    "authentication": true,
    "core_apis": true,
    "new_features": true,
    "frontend": true,
    "security": true,
    "performance": true
  }
}
```

## Exit Codes

- `0` - All tests passed or minor warnings only
- `1` - Critical failures detected

## Health Status Definitions

### Backend Health
- **healthy** - All tests passing, no failures
- **degraded** - 1-3 failed tests, service partially operational
- **down** - More than 3 failed tests, critical issues

### Frontend Status
- **up** - Frontend accessible and serving pages
- **down** - Frontend unreachable or critical errors

## Troubleshooting

### Backend Unreachable
```
✗ Backend unreachable (HTTP 000)
Aborting tests - backend is not responding
```
**Solution**: Check Railway deployment status and logs

### Authentication Failures
```
✗ User login failed (HTTP 401)
✗ JWT token not found in login response
```
**Solution**: Verify authentication service is running and database is connected

### CORS Issues
```
⚠ CORS headers not found - may cause frontend issues
```
**Solution**: Check backend CORS configuration for frontend URL

### Performance Warnings
```
⚠ Backend response time: 2500ms (consider optimization)
```
**Solution**: Review database queries, add caching, or scale resources

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Verify Production Deployment

on:
  deployment_status:
    types: [success]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run verification
        run: ./verify_production_deployment.sh
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: deployment-report
          path: production_deployment_report.json
```

### Post-Deployment Checklist
- [ ] Run verification script
- [ ] Review JSON report
- [ ] Check all tests passed
- [ ] Verify performance metrics
- [ ] Review any warnings or recommendations
- [ ] Test critical user flows manually
- [ ] Monitor error tracking (Sentry, etc.)
- [ ] Check application logs

## Monitoring Integration

The report can be integrated with monitoring systems:

```bash
# Send report to monitoring service
curl -X POST https://monitoring.example.com/deployments \
  -H "Content-Type: application/json" \
  -d @production_deployment_report.json

# Alert on failures
if [ $? -ne 0 ]; then
  # Send Slack/Discord/Email notification
  ./notify_team.sh "Deployment verification failed"
fi
```

## Development vs Production

To test staging environment, modify the URLs:
```bash
# Edit the script or set environment variables
export BACKEND_URL="https://meta-analysis-tool-staging.up.railway.app"
export FRONTEND_URL="https://staging.meta-analysis-tool.vercel.app"
./verify_production_deployment.sh
```

## Requirements

- `curl` - HTTP client
- `jq` - JSON processor (for report generation)
- `bash` 4.0+ - Shell interpreter

Install dependencies:
```bash
# macOS
brew install jq

# Ubuntu/Debian
apt-get install jq curl

# Alpine Linux
apk add jq curl bash
```

## Advanced Usage

### Verbose Mode
Add `-x` flag for detailed execution:
```bash
bash -x ./verify_production_deployment.sh
```

### Custom Test User
Set environment variables:
```bash
export TEST_EMAIL="custom@example.com"
export TEST_PASSWORD="CustomPassword123!"
./verify_production_deployment.sh
```

### Save Output to Log
```bash
./verify_production_deployment.sh | tee deployment-$(date +%Y%m%d-%H%M%S).log
```

## Support

For issues or questions:
1. Check the JSON report for detailed error information
2. Review Railway and Vercel deployment logs
3. Verify environment variables are correctly set
4. Ensure database migrations have been applied
5. Check API endpoint availability manually with `curl`

## Version History

- **v1.0.0** - Initial release with comprehensive endpoint testing
- Tests: 28 endpoints across 7 categories
- Coverage: Health, Auth, Core APIs, New Features, Frontend, Security, Performance
