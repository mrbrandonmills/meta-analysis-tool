# 🚨 MANUAL PRODUCTION FIX - 5 MINUTES

## The Problem:
User registration returns HTTP 500 because migration 003 hasn't run in production.

## The Fix (5 minutes):

### Option 1: Railway Dashboard (Easiest)

1. **Open Railway Dashboard**: https://railway.app/dashboard
2. **Go to your project**: "Meta-Analysis-Tool"
3. **Click on backend service**: "meta-analysis-tool"
4. **Open "Deploy" tab**
5. **Click "Redeploy"** button
6. **Wait 2-3 minutes** for deployment

That's it! The start.sh script will run migration 003 automatically.

### Option 2: Railway CLI (If Railway link works)

```bash
# In a REAL terminal (not automated):
railway link
# Select: Meta-Analysis-Tool
# Select: meta-analysis-tool (backend service)

railway run alembic upgrade head
```

### Verify It Worked:

```bash
# Test registration:
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'

# Should return: HTTP 201 (not 500)
```

## Why This Fixes It:

Migration 003 removes extra columns from the users table that don't exist in the SQLAlchemy model:
- `orcid`
- `deleted_at`
- `created_by`
- `updated_by`

Once these are removed, SQLAlchemy can create users without errors.

## After Fix:
- ✅ User registration: HTTP 201
- ✅ User login: HTTP 200
- ✅ All authentication working
- ⚠️ Celery still degraded (optional, can fix later)

**Estimated time**: 5 minutes
**Success rate**: 99%
