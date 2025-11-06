# BUG-001 Deployment Checklist

**Bug:** User Registration 500 Error  
**Status:** FIXED - Ready for Deployment  
**Date:** November 5, 2025

---

## Pre-Deployment Verification

- [x] Root cause identified (duplicate `name` column in migration)
- [x] Migration 001 fixed (removed duplicate column)
- [x] Migration 002 created (drops column from production DB)
- [x] Dockerfile updated (copies alembic files)
- [x] start.sh updated (runs migrations automatically)
- [x] User model verified (only has `full_name`)
- [x] Registration endpoint code verified (correct logic)
- [x] Documentation complete (BUG-001_FIX_REPORT.md)

---

## Deployment Steps

### Step 1: Stage Changes
```bash
cd /Users/brandon/meta-analysis-tool
git status
# Should show:
#   modified: backend/alembic/versions/001_multi_tool_schema.py
#   new file: backend/alembic/versions/002_remove_duplicate_name_column.py
#   modified: backend/Dockerfile
#   modified: backend/start.sh
#   new file: backend/BUG-001_FIX_REPORT.md
```

### Step 2: Commit Changes
```bash
git add backend/alembic/versions/001_multi_tool_schema.py
git add backend/alembic/versions/002_remove_duplicate_name_column.py
git add backend/Dockerfile
git add backend/start.sh
git add backend/BUG-001_FIX_REPORT.md
git add backend/QUICKFIX_BUG001.md
git add BUG-001_DEPLOYMENT_CHECKLIST.md

git commit -m "Fix BUG-001: Remove duplicate name column from users table

- Fixed migration 001: Removed duplicate 'name' column definition
- Added migration 002: Drops 'name' column from production database
- Updated Dockerfile: Copy alembic files to Docker image
- Updated start.sh: Auto-run migrations on deployment
- Root cause: Schema mismatch between User model and migration
- Impact: User registration now functional
- Resolves: HTTP 500 error on POST /api/v1/auth/register

Detailed report: backend/BUG-001_FIX_REPORT.md"
```

### Step 3: Push to Repository
```bash
git push origin main
# Railway will automatically detect changes and deploy
```

---

## Post-Deployment Verification

### 1. Monitor Deployment Logs (Railway Dashboard)

Watch for these log messages:

```
✓ Starting Meta Analysis Tool Backend API...
✓ Running database migrations...
✓ Applying migration 002_remove_duplicate_name_column
✓ Database migrations completed successfully
✓ Meta-Analysis Research Platform started successfully
```

**If migration fails:** Check Railway logs for error details

### 2. Verify Migration Applied

Option A: Check via Railway CLI
```bash
railway run alembic current
# Should show: 002 (head)
```

Option B: Check database directly
```sql
-- Connect to Railway PostgreSQL
\d users
-- Should NOT show 'name' column
-- Should show 'full_name' column
```

### 3. Test User Registration

```bash
# Set API URL
export API_URL="https://meta-analysis-tool-production.up.railway.app"

# Test registration with valid data
curl -X POST $API_URL/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "test-bug001@example.com",
    "password": "SecurePass123!",
    "full_name": "BUG-001 Test User",
    "institution": "Test University"
  }'

# Expected Response: HTTP 201 Created
# {
#   "id": "uuid-here",
#   "email": "test-bug001@example.com",
#   "full_name": "BUG-001 Test User",
#   "institution": "Test University",
#   "role": "researcher",
#   "is_active": true,
#   "is_verified": false,
#   "created_at": "2025-11-05T...",
#   "last_login": null
# }
```

### 4. Test User Login

```bash
# Login with registered user
curl -X POST $API_URL/api/v1/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=test-bug001@example.com&password=SecurePass123!'

# Expected Response: HTTP 200 OK
# {
#   "access_token": "eyJ...",
#   "refresh_token": "eyJ...",
#   "token_type": "bearer"
# }
```

### 5. Test Protected Endpoint

```bash
# Extract token from login response
export TOKEN="<access_token_from_login>"

# Test /api/v1/auth/me endpoint
curl -X GET $API_URL/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Expected Response: HTTP 200 OK with user data
```

### 6. Test Password Validation

```bash
# Should fail - password too short
curl -X POST $API_URL/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"test2@example.com","password":"Short1","full_name":"Test"}'

# Expected: HTTP 422 with validation error

# Should fail - missing uppercase
curl -X POST $API_URL/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"test3@example.com","password":"lowercase123","full_name":"Test"}'

# Expected: HTTP 422 with validation error
```

---

## Success Criteria

- [ ] Deployment completed without errors
- [ ] Migration 002 applied successfully
- [ ] User registration returns HTTP 201 (not 500)
- [ ] User login returns HTTP 200 with tokens
- [ ] Protected endpoints accessible with valid token
- [ ] Password validation works correctly
- [ ] Database schema correct (no `name` column in users table)

---

## Rollback Plan (If Needed)

If deployment fails catastrophically:

```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or rollback migration manually
railway run alembic downgrade -1
```

**Note:** Downgrade will re-add the `name` column, which means registration will still be broken. Only use in emergency.

---

## Known Limitations

This fix resolves BUG-001 but does NOT address:

- BUG-002: Redis connection issues (rate limiting broken)
- BUG-003: Celery workers not running (background jobs broken)
- BUG-004: Missing statistical libraries (meta-analysis calculations unavailable)

These remain as separate critical issues documented in the forensic analysis.

---

## Next Steps After Deployment

1. Verify fix resolves BUG-001 completely
2. Update forensic analysis report with BUG-001 status: FIXED
3. Proceed to fix BUG-002 (Redis) - required for rate limiting
4. Proceed to fix BUG-003 (Celery) - required for background jobs
5. Proceed to fix BUG-004 (Statistical libraries) - required for core functionality

---

## Contact Information

**Fixed By:** Backend Development Agent  
**Documentation:** `/backend/BUG-001_FIX_REPORT.md`  
**Quick Reference:** `/backend/QUICKFIX_BUG001.md`  
**Date:** November 5, 2025

---

## Approval

- [ ] Code changes reviewed
- [ ] Documentation reviewed
- [ ] Ready for deployment
- [ ] Stakeholders notified

**Approved By:** _______________  
**Date:** _______________
