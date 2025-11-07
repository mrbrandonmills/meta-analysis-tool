# ✅ WORKING PRODUCTION URLS

## Backend API (Railway) - OPERATIONAL ✅

### Base URL
```
https://meta-analysis-tool-production.up.railway.app
```

### Working Endpoints (Click to Test):

1. **Health Check** (GET):
   ```
   https://meta-analysis-tool-production.up.railway.app/api/v1/health
   ```

2. **API Documentation** (Interactive Swagger UI):
   ```
   https://meta-analysis-tool-production.up.railway.app/docs
   ```

3. **Root Endpoint** (GET):
   ```
   https://meta-analysis-tool-production.up.railway.app/
   ```

4. **Available Agents List** (GET):
   ```
   https://meta-analysis-tool-production.up.railway.app/api/v1/agents/available
   ```

### Test with curl:

```bash
# Health check
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health

# List agents
curl https://meta-analysis-tool-production.up.railway.app/api/v1/agents/available

# Register new user
curl -X POST "https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User","institution":"Test U"}'
```

---

## Frontend (Vercel) - NOT DEPLOYED ❌

**Status**: The frontend has not been deployed to Vercel yet.

**Vercel Project**: 
- Project ID: `prj_2HT5zddASRGmP2uzodxIfybKyPZy`
- Project Name: `meta-analysis-tool`

### To Deploy Frontend:

```bash
# Install Vercel CLI if needed
npm install -g vercel

# Deploy from frontend directory
cd /Users/brandon/meta-analysis-tool/frontend
vercel --prod
```

**Or use Vercel Dashboard**:
1. Go to: https://vercel.com/dashboard
2. Find project: `meta-analysis-tool`
3. Click "Deploy" → Import from Git
4. Connect to GitHub repo: `mrbrandonmills/meta-analysis-tool`
5. Set root directory to `frontend`
6. Deploy

---

## Summary

✅ **Backend is 100% operational** - All API endpoints working
❌ **Frontend needs deployment** - Run `vercel --prod` or deploy from dashboard

The audit confirmed the backend is production-ready. You just need to deploy the frontend!
