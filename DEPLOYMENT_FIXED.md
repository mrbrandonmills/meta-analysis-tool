# 🚀 Fixed Deployment Guide - Railway + Vercel

## Issues Fixed

### ✅ Issue 1: Vercel - Invalid vercel.json
**Error**: `should NOT have additional property rootDirectory`
**Fix**: Removed `vercel.json` - these settings belong in Vercel dashboard, not the config file.

### ✅ Issue 2: Railway - "cd command not found"
**Error**: `The executable 'cd' could not be found`
**Fix**: Removed all `cd` commands from build scripts. Railway needs root directory set in dashboard instead.

---

## Step-by-Step Deployment

### PART 1: Railway Backend (5 minutes)

#### Step 1: Configure Root Directory

**IMPORTANT**: Railway needs to know to use the `backend` folder.

1. Go to https://railway.app/dashboard
2. Click your **meta-analysis-tool** project
3. Click your backend service
4. Go to **Settings**
5. Scroll to **Root Directory**
6. Set to: `backend`
7. Click **Save**

#### Step 2: Verify Branch

Still in Settings:
- **Source** → **Branch**: Should be `main`
- Click **Save** if you changed it

#### Step 3: Set Environment Variables

Go to **Variables** tab and add:

```bash
# REQUIRED
ANTHROPIC_API_KEY=sk-ant-api03-...
SECRET_KEY=<generate-random-string>

# AUTO-PROVIDED (if you added PostgreSQL/Redis services)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# OPTIONAL
OPENAI_API_KEY=sk-proj-...
PUBMED_EMAIL=your-email@example.com

# APPLICATION SETTINGS
DEBUG=false
LOG_LEVEL=INFO

# CORS (add your Vercel URL once you have it)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

#### Step 4: Verify Build Settings (Auto-detected)

Go to **Settings** → scroll to **Build & Deploy**:
- **Build Command**: Should auto-detect from `nixpacks.toml`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

If not auto-detected, manually set:
- **Build Command**: `pip install --upgrade pip && pip install -r requirements.production.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Step 5: Deploy

Railway should auto-deploy when you push to `main`. Or manually:
1. Go to **Deployments** tab
2. Click **⋮** on latest deployment
3. Click **Redeploy**

#### Step 6: Get Backend URL

Once deployed:
1. Go to **Settings** → **Networking**
2. Click **Generate Domain** (if not already generated)
3. Copy your URL: `https://your-app-production.up.railway.app`
4. **Save this - you need it for Vercel**

---

### PART 2: Vercel Frontend (3 minutes)

#### Step 1: Import or Link Project

1. Go to https://vercel.com/dashboard
2. Click **Add New...** → **Project**
3. Select `mrbrandonmills/meta-analysis-tool`
4. Click **Import**

#### Step 2: Configure Project Settings

**IMPORTANT**: These settings are NOT in vercel.json anymore.

**Framework Preset**: Next.js (auto-detected)
**Root Directory**: `frontend`
**Build Command**: `npm run build` (default)
**Output Directory**: `.next` (default)

#### Step 3: Set Environment Variable

**Before deploying**, click **Environment Variables**:
- **Key**: `NEXT_PUBLIC_API_URL`
- **Value**: `https://your-railway-backend.up.railway.app` (from Railway Step 6)
- **Environment**: ✅ Production, ✅ Preview, ✅ Development

Click **Add**

#### Step 4: Set Production Branch

In project settings:
- **Git** → **Production Branch**: `main`
- Click **Save**

#### Step 5: Deploy

Click **Deploy**

Wait 1-2 minutes for build to complete.

#### Step 6: Get Frontend URL

Once deployed:
- Copy your Vercel URL: `https://meta-analysis-tool.vercel.app`
- Or custom domain if you set one up

---

### PART 3: Connect Frontend & Backend (2 minutes)

#### Update Railway CORS

Now that you have your Vercel URL:

1. Go back to Railway dashboard
2. Click your backend service
3. Go to **Variables** tab
4. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://meta-analysis-tool.vercel.app,http://localhost:3000,http://localhost:3001
   ```
   (Replace with your actual Vercel URL)
5. Railway will auto-redeploy (~1 minute)

---

## Verification Checklist

### ✅ Railway Backend

Test your backend URL:

```bash
# Health check
curl https://your-railway-backend.up.railway.app/health

# Should return: {"status":"healthy"}

# Main endpoint
curl https://your-railway-backend.up.railway.app/

# Should return app info with "status":"operational"
```

### ✅ Vercel Frontend

1. Visit your Vercel URL
2. Open DevTools (F12) → Console tab
3. Should see no CORS errors
4. Try creating a meta-analysis to test the connection

### ✅ Full Integration

Test the complete flow:
1. Go to your Vercel URL
2. Enter a research question: `"What is the effect of exercise on depression?"`
3. Enter topic: `"exercise and mental health"`
4. Click **Create Meta-Analysis**
5. Should see workflow created
6. Click **Execute Meta-Analysis**
7. Should see search results and screening

---

## Common Issues & Solutions

### ❌ Railway: "requirements.production.txt not found"
**Solution**: Make sure **Root Directory** is set to `backend` in Railway Settings

### ❌ Railway: Still using old build command
**Solution**:
1. Go to Settings → clear custom build command
2. Let Railway auto-detect from `nixpacks.toml`

### ❌ Vercel: "NEXT_PUBLIC_API_URL is undefined"
**Solution**:
1. Settings → Environment Variables
2. Add `NEXT_PUBLIC_API_URL` with your Railway URL
3. Redeploy

### ❌ CORS errors on frontend
**Solution**:
1. Check `ALLOWED_ORIGINS` in Railway includes your Vercel URL
2. Wait for Railway to redeploy
3. Hard refresh frontend (Cmd+Shift+R or Ctrl+Shift+R)

### ❌ Vercel: "vercel.json schema validation failed"
**Solution**: Already fixed - `vercel.json` has been removed

---

## Current Configuration

### Files Updated:
- ✅ Removed `vercel.json` (settings go in dashboard)
- ✅ Fixed `Procfile` (no `cd` command)
- ✅ Fixed `nixpacks.toml` (no `cd` command)
- ✅ Fixed `railway.json` (simplified)
- ✅ Fixed `railway.toml` (simplified)

### Dashboard Settings Required:

**Railway**:
- Root Directory: `backend`
- Branch: `main`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Vercel**:
- Root Directory: `frontend`
- Branch: `main`
- Environment: `NEXT_PUBLIC_API_URL=<railway-url>`

---

## Quick Reference

**Repository**: https://github.com/mrbrandonmills/meta-analysis-tool
**Branch**: `main`
**Railway Backend**: `backend` folder
**Vercel Frontend**: `frontend` folder

---

## Next Steps

1. ✅ Push these fixes (coming next)
2. ⏳ Configure Railway root directory → `backend`
3. ⏳ Configure Vercel root directory → `frontend`
4. ⏳ Set environment variables
5. ⏳ Deploy and test

**Let's get this deployed!** 🚀
