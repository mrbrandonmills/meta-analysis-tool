# Quick Deployment Commands - Meta-Analysis Tool

Quick reference for deploying the fixed backend to Railway.

---

## Pre-Deployment: Commit Changes

```bash
cd /Users/brandon/meta-analysis-tool

# Check status
git status

# Add all changes
git add .

# Commit with descriptive message
git commit -m "Fix critical production bugs

- Add Anthropic API key validation at startup
- Improve error handling with specific Anthropic exceptions
- Fix debug mode to default to false in production
- Add /agents/list endpoint alias
- Configure proper logging levels
- Update .env.example with Railway instructions
- Add comprehensive RAILWAY_SETUP.md guide"

# Push to GitHub (Railway will auto-deploy)
git push origin main
```

---

## Railway Setup Commands

### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Set Environment Variables (via Railway Dashboard)
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...
SECRET_KEY=<output-from-command-above>

# Recommended
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://meta-analysis-tool.vercel.app,https://your-custom-domain.com
```

---

## Verification Commands

### Test Health Endpoint
```bash
curl https://your-service.railway.app/health
# Expected: {"status": "healthy"}
```

### Test Root Endpoint
```bash
curl https://your-service.railway.app/
# Expected: {"name": "Meta-Analysis Research Platform", ...}
```

### Test Agents List (Original)
```bash
curl https://your-service.railway.app/api/v1/agents/available
```

### Test Agents List (New Alias)
```bash
curl https://your-service.railway.app/api/v1/agents/list
```

### Test with Pretty Print
```bash
curl -s https://your-service.railway.app/health | python -m json.tool
```

---

## Railway CLI Commands (Optional)

### Install Railway CLI
```bash
npm i -g @railway/cli
```

### Login
```bash
railway login
```

### Link to Project
```bash
cd /Users/brandon/meta-analysis-tool
railway link
```

### View Logs
```bash
railway logs
```

### Check Variables
```bash
railway variables
```

### Deploy Manually
```bash
railway up
```

---

## Local Testing Commands

### Run Backend Locally
```bash
cd /Users/brandon/meta-analysis-tool/backend

# Create .env file first (copy from .env.example)
cp ../.env.example .env
# Edit .env with your actual keys

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Test Locally
```bash
# Health check
curl http://localhost:8000/health

# Agents list
curl http://localhost:8000/api/v1/agents/list
```

---

## Troubleshooting Commands

### View Railway Service Logs
```bash
# In Railway dashboard, go to your service > Logs tab
# Or use CLI:
railway logs --tail
```

### Check Environment Variables
```bash
railway variables
```

### Restart Service
```bash
# In Railway dashboard: Deployments > Latest > Restart
# Or redeploy
railway up
```

### Test API Key Validation Locally
```bash
# This should fail if API key is invalid
export ANTHROPIC_API_KEY="invalid-key"
cd /Users/brandon/meta-analysis-tool/backend
uvicorn app.main:app --reload
# Expected: ValueError with clear error message
```

---

## Frontend Update Commands

### Update Vercel Environment Variable
```bash
# In Vercel dashboard:
# Project Settings > Environment Variables
# Update: NEXT_PUBLIC_API_URL=https://your-service.railway.app
```

### Redeploy Frontend
```bash
# Vercel will auto-deploy on git push
cd /path/to/frontend
git add .
git commit -m "Update API URL to Railway backend"
git push origin main
```

---

## Monitoring Commands

### Check Service Status
```bash
curl -w "\n%{http_code}\n" https://your-service.railway.app/health
# Should return 200
```

### Monitor Logs in Real-Time
```bash
railway logs --tail
```

### Check Application Startup
```bash
# Look for these messages in logs:
# ✓ Anthropic API key validated successfully
# Debug mode: False
# Logging configured with level: INFO
```

---

## Rollback Commands

### Rollback to Previous Deployment
```bash
# In Railway dashboard:
# Deployments > Select previous successful deployment > Redeploy
```

### Force Fresh Deploy
```bash
railway up --detach
```

---

## Files to Review

- `RAILWAY_SETUP.md` - Full deployment guide
- `BUGFIX_SUMMARY.md` - Summary of all fixes
- `.env.example` - Environment variable reference
- `backend/app/main.py` - API key validation
- `backend/app/core/config.py` - Debug mode fix
- `backend/app/core/logging_config.py` - Logging configuration
- `backend/app/api/v1/agents.py` - Endpoint alias
- `backend/app/agents/base/agent.py` - Error handling

---

## Quick Test Script

Save this as `test_deployment.sh` and run it:

```bash
#!/bin/bash
SERVICE_URL="https://your-service.railway.app"

echo "Testing Meta-Analysis Tool Backend..."
echo "======================================"

echo -e "\n1. Health Check:"
curl -s "$SERVICE_URL/health" | python -m json.tool

echo -e "\n2. Root Endpoint:"
curl -s "$SERVICE_URL/" | python -m json.tool

echo -e "\n3. Agents List (available):"
curl -s "$SERVICE_URL/api/v1/agents/available" | python -m json.tool | head -20

echo -e "\n4. Agents List (list alias):"
curl -s "$SERVICE_URL/api/v1/agents/list" | python -m json.tool | head -20

echo -e "\n5. HTTP Status Codes:"
echo -n "Health: "
curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health"
echo -n " | Root: "
curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/"
echo -n " | Agents: "
curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/api/v1/agents/list"
echo ""

echo -e "\nAll tests completed!"
```

Make executable and run:
```bash
chmod +x test_deployment.sh
./test_deployment.sh
```

---

## Success Criteria

Your deployment is successful if:

- ✅ Health endpoint returns `{"status": "healthy"}`
- ✅ Root endpoint returns service info
- ✅ Both `/agents/available` and `/agents/list` work
- ✅ Logs show: "✓ Anthropic API key validated successfully"
- ✅ Logs show: "Debug mode: False"
- ✅ No error messages in Railway logs
- ✅ Frontend can connect (no CORS errors)

---

## Need Help?

1. Check `RAILWAY_SETUP.md` for detailed troubleshooting
2. Review `BUGFIX_SUMMARY.md` for what was changed
3. Check Railway logs for specific errors
4. Verify all environment variables are set correctly

---

**Last Updated**: 2025-11-04
