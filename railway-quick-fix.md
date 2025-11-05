# RAILWAY DEPLOYMENT - IMMEDIATE FIX

## What Went Wrong

Railway is NOT resolving your service reference variables. Instead of getting the actual database URLs, your app is receiving the literal strings `${{Postgres.DATABASE_URL}}` and `${{Redis.REDIS_URL}}`.

## Root Cause

The `${{ServiceName.VARIABLE}}` syntax in Railway **requires**:
1. Exact service name match (case-sensitive)
2. Both services in the same environment
3. Proper service linking

Your error: `sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from string '${{Postgres.DATABASE_URL}'`

This proves Railway is passing the literal string, not resolving the reference.

## FASTEST FIX (Do This NOW - 5 Minutes)

### Step 1: Open Railway Dashboard
Visit: https://railway.app/dashboard

### Step 2: Navigate to Your Project
Click on **"Meta-Analysis-Tool"**

### Step 3: Get PostgreSQL Connection String

1. Click on your **PostgreSQL service** (might be named: Postgres, PostgreSQL, or database)
2. Click on the **"Variables"** tab or **"Connect"** tab
3. Look for **`DATABASE_URL`**
4. Click the **copy icon** 📋 to copy the full URL
5. It should look like: `postgresql://postgres:PASSWORD@hostname:5432/railway`

### Step 4: Get Redis Connection String

1. Click on your **Redis service**
2. Click on the **"Variables"** tab or **"Connect"** tab
3. Look for **`REDIS_URL`** or **`REDIS_PRIVATE_URL`**
4. Click the **copy icon** 📋 to copy the full URL
5. It should look like: `redis://default:PASSWORD@hostname:6379`

### Step 5: Update Your Backend Service Variables

1. Click on your **backend/main service** (the one that's failing to deploy)
2. Click on the **"Variables"** tab
3. Find and **DELETE** these variables (if they exist with `${{...}}` values):
   - `DATABASE_URL`
   - `REDIS_URL`
4. **ADD NEW** variables with the ACTUAL connection strings you copied:
   - Variable name: `DATABASE_URL`
   - Variable value: (paste the PostgreSQL URL from Step 3)
   - Click "Add"

   - Variable name: `REDIS_URL`
   - Variable value: (paste the Redis URL from Step 4)
   - Click "Add"

### Step 6: Save and Redeploy

Railway will automatically trigger a new deployment. Watch the logs for:
- ✅ "Application startup complete"
- ✅ No SQLAlchemy URL parsing errors

---

## Alternative: Fix Service Reference Names

If you want to keep using `${{...}}` syntax, you need the EXACT service names:

### Check Your Service Names

1. In Railway dashboard, look at the services list in your project
2. Look for the **exact name** shown (case-sensitive):
   - PostgreSQL service might be: `Postgres`, `PostgreSQL`, `postgres`, `database`, etc.
   - Redis service might be: `Redis`, `redis`, `cache`, etc.

### Update Variables with Correct Names

If your PostgreSQL service is named **exactly** `PostgreSQL` (not `Postgres`):
```
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}
```

If your Redis service is named **exactly** `redis` (not `Redis`):
```
REDIS_URL=${{redis.REDIS_URL}}
```

**Important:** Service references are case-sensitive and must match EXACTLY!

---

## Using Railway CLI (Alternative Method)

If you have Railway CLI installed and linked:

```bash
# First, link your project
cd /Users/brandon/meta-analysis-tool
railway link

# Then set variables (replace with actual URLs)
railway variables --set DATABASE_URL="postgresql://postgres:password@host:5432/railway"
railway variables --set REDIS_URL="redis://default:password@host:6379"

# Force redeploy
railway up --service backend
```

---

## Verification Steps

After deploying:

1. **Check Logs:**
   - Go to your backend service in Railway
   - Click on "Deployments"
   - Open the latest deployment logs
   - Look for: `INFO:     Application startup complete`
   - Should NOT see: `Could not parse SQLAlchemy URL`

2. **Test Health Endpoint:**
   - Find your deployment URL (e.g., `https://your-app.railway.app`)
   - Visit: `https://your-app.railway.app/api/v1/health`
   - Should return: `{"status": "healthy"}`

3. **Check Database Connection:**
   - Look in logs for: `Sync database connection established`
   - This confirms the database URL is working

---

## Why This Happened

Railway's `${{ServiceName.VARIABLE}}` syntax is powerful but strict:

- ✅ Works: `${{PostgreSQL.DATABASE_URL}}` (if service is named "PostgreSQL")
- ❌ Fails: `${{Postgres.DATABASE_URL}}` (if service is named "PostgreSQL")
- ❌ Fails: `${{postgres.DATABASE_URL}}` (if service is named "Postgres")

**The service name MUST match exactly, including capitalization.**

If the reference can't be resolved, Railway passes it as a literal string, causing your error.

---

## Recommended Approach

**For Production:** Use direct connection strings (Step 5) because:
1. No ambiguity
2. Easier to debug
3. More explicit
4. Works immediately

**For Dynamic References:** Only use `${{...}}` syntax if:
1. You know the exact service names
2. Services are in the same environment
3. You want automatic updates when services change

---

## Need More Help?

If this still doesn't work:

1. **Screenshot your Railway services list** - Show the exact names
2. **Screenshot your backend service variables** - Show what's currently set
3. **Share the latest deployment logs** - Show the current error

Then we can provide more specific guidance.

---

## Expected Timeline

⏱️ **5 minutes** - Get connection strings and update variables
⏱️ **2-3 minutes** - Railway redeploys automatically
⏱️ **1 minute** - Verify deployment succeeded

**Total: ~10 minutes to working deployment**

---

## Success Indicators

You'll know it's working when you see in the logs:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
Sync database connection established
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

And NO errors about "Could not parse SQLAlchemy URL"!
