# BUG-001 QUICK FIX SUMMARY

## Problem
User registration crashes with HTTP 500 error.

## Root Cause
Database migration created both `name` AND `full_name` columns in users table, but User model only defines `full_name`. SQLAlchemy couldn't insert users.

## Files Changed
1. `backend/alembic/versions/001_multi_tool_schema.py` - Removed duplicate `name` column (line 35)
2. `backend/alembic/versions/002_remove_duplicate_name_column.py` - NEW migration to fix production DB
3. `backend/Dockerfile` - Added alembic files to image
4. `backend/start.sh` - Added automatic migration execution

## Deploy Instructions
```bash
# 1. Commit changes
git add backend/alembic/versions/*.py backend/Dockerfile backend/start.sh
git commit -m "Fix BUG-001: Remove duplicate name column from users table"
git push

# 2. Deploy to Railway (automatic)
# Watch logs for: "✓ Database migrations completed successfully"

# 3. Test registration
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"TestPass123","full_name":"Test User"}'

# Expected: HTTP 201 with user data
```

## What Gets Fixed
✅ User registration endpoint
✅ User login (depends on registration)
✅ All protected endpoints (can now get auth tokens)
✅ Entire platform functionality (auth was blocking everything)

## Full Details
See: `backend/BUG-001_FIX_REPORT.md`
