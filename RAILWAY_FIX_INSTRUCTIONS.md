# Railway Deployment Fix - IMMEDIATE ACTION REQUIRED

## THE PROBLEM

Railway is NOT resolving your service reference variables:
- `${{Postgres.DATABASE_URL}}` is being passed as a literal string
- This causes SQLAlchemy to fail because it's not a valid database URL

## WHY THIS HAPPENS

Railway's service reference syntax `${{ServiceName.VARIABLE}}` requires:
1. The **EXACT** service name (case-sensitive)
2. The service must be in the SAME environment
3. The variable must exist on that service

## IMMEDIATE FIX OPTIONS

### Option 1: Fix the Service Reference (RECOMMENDED)

In Railway dashboard, go to your backend service environment variables and check:

1. **PostgreSQL Service Name**: Your Postgres service might be named differently:
   - Could be: `Postgres`, `PostgreSQL`, `postgres`, `database`, etc.
   - **ACTION**: Check the exact name in Railway dashboard under Services

2. **Update the variable reference**:
   - If service is named `Postgres`: use `${{Postgres.DATABASE_URL}}`
   - If service is named `postgres`: use `${{postgres.DATABASE_URL}}`
   - If service is named `PostgreSQL`: use `${{PostgreSQL.DATABASE_URL}}`

3. **Redis Service Name**: Same issue - check exact name

### Option 2: Use Direct Connection Strings (FASTEST - DO THIS NOW)

Since the reference syntax isn't working, use the actual connection strings:

#### Step 1: Get PostgreSQL Connection URL

In Railway dashboard:
1. Go to your PostgreSQL service
2. Click on "Variables" or "Connect" tab
3. Copy the `DATABASE_URL` value (should look like: `postgresql://user:pass@host:port/dbname`)

#### Step 2: Get Redis Connection URL

In Railway dashboard:
1. Go to your Redis service
2. Click on "Variables" or "Connect" tab
3. Copy the `REDIS_URL` value (should look like: `redis://default:pass@host:port`)

#### Step 3: Update Backend Service Variables

In your backend service's environment variables, set:

```
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://default:pass@host:port
```

**Replace the placeholder values with the ACTUAL connection strings from steps 1 and 2.**

### Option 3: Use Railway's Automatic Variables (IF AVAILABLE)

If your PostgreSQL and Redis are Railway-provisioned services:

1. PostgreSQL automatically exposes: `DATABASE_URL` (on the Postgres service)
2. Redis automatically exposes: `REDIS_URL` (on the Redis service)

In your backend service, these variables should be automatically available if the services are linked.

**ACTION**: Check if your backend service has these variables automatically set by Railway.

## QUICKEST PATH TO SUCCESS

**DO THIS RIGHT NOW:**

1. Open Railway dashboard in browser
2. Navigate to your `Meta-Analysis-Tool` project
3. Click on PostgreSQL service → Variables tab
4. Copy the `DATABASE_URL` value
5. Click on Redis service → Variables tab
6. Copy the `REDIS_URL` value
7. Click on your backend service → Variables tab
8. **DELETE** these variables:
   - `DATABASE_URL` (if it has `${{Postgres.DATABASE_URL}}`)
   - `REDIS_URL` (if it has `${{Redis.REDIS_URL}}`)
9. **ADD** these variables with the ACTUAL values you copied:
   - `DATABASE_URL` = (paste PostgreSQL connection string)
   - `REDIS_URL` = (paste Redis connection string)
10. Railway will automatically redeploy
11. Check logs - deployment should succeed

## VERIFICATION

After deploying, check the logs for:
- ✅ "Sync database connection established"
- ✅ "INFO:     Application startup complete"
- ❌ No more "Could not parse SQLAlchemy URL" errors

## ALTERNATIVE: Use Railway CLI

If you prefer CLI (requires linking project first):

```bash
# Link project (interactive - you may need to do this in Railway dashboard)
railway link

# Set variables directly
railway variables --set DATABASE_URL="postgresql://user:pass@host:port/dbname"
railway variables --set REDIS_URL="redis://default:pass@host:port"

# Trigger redeploy
railway up
```

## ROOT CAUSE

The `${{ServiceName.VARIABLE}}` syntax only works when:
1. Service name matches EXACTLY
2. Both services are in same environment
3. Railway can resolve the reference at build time

If it's not working, it means one of these conditions isn't met.

## NEXT STEPS

After fixing the database connection:
1. Verify deployment succeeds
2. Test the health endpoint: `https://your-app.railway.app/api/v1/health`
3. Check that database connections work
4. Test API endpoints

---

**URGENT**: Use Option 2 (direct connection strings) to get this working NOW. You can always switch back to service references later once you confirm the exact service names.
