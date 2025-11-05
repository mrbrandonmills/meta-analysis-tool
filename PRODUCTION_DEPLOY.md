# 🚀 Production Deployment - Complete Guide

## Current Status
✅ Code merged to `main` branch
✅ Railway deployment files configured
✅ CORS settings updated for production
⏳ Vercel needs to deploy from `main` branch
⏳ Backend URL needs to be configured

---

## Step 1: Get Your Railway Backend URL

### Option A: From Railway Dashboard
1. Go to https://railway.app/dashboard
2. Click on your **meta-analysis-tool** project
3. Click on your **backend service**
4. Go to **Settings** → **Networking**
5. Look for your **Public URL** (e.g., `https://meta-analysis-tool-production.up.railway.app`)
6. **Copy this URL** - you'll need it in Step 2

### Option B: Using Railway CLI
```bash
# Link to your Railway project
railway link

# Get the domain
railway domain
```

---

## Step 2: Configure Vercel to Deploy from Main Branch

### In Vercel Dashboard:

1. **Go to Vercel**: https://vercel.com/dashboard
2. **Find your project**: Look for `meta-analysis-tool`
3. **Go to Settings** → **Git**
4. **Production Branch**: Change to `main` (if it's not already)
5. **Save changes**

### Update Environment Variables:

1. In Vercel, go to **Settings** → **Environment Variables**
2. Add or update:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app
   ```
   ⚠️ **Replace with your actual Railway URL from Step 1**

3. **Important**: Make sure to set this for:
   - ✅ Production
   - ✅ Preview (optional)
   - ✅ Development (optional)

4. Click **Save**

---

## Step 3: Update Railway CORS Settings

Your Railway backend needs to allow requests from your Vercel frontend.

### In Railway Dashboard:

1. Go to your **backend service**
2. Click **Variables** tab
3. Add or update:
   ```
   ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3000,http://localhost:3001
   ```
   ⚠️ **Replace with your actual Vercel URL**

4. Railway will automatically redeploy

---

## Step 4: Trigger Vercel Redeployment

### Option A: From Dashboard (Easiest)
1. Go to Vercel dashboard
2. Click on your project
3. Go to **Deployments** tab
4. Find the latest deployment
5. Click the **⋯** (three dots) → **Redeploy**
6. Select **Use existing Build Cache** → No
7. Click **Redeploy**

### Option B: Push a Change
```bash
# Make a small change to trigger deployment
git commit --allow-empty -m "Trigger Vercel redeployment"
git push origin main
```

### Option C: Using Vercel CLI
```bash
# Install if you haven't
npm i -g vercel

# Login
vercel login

# Deploy to production
cd /Users/brandon/meta-analysis-tool
vercel --prod --cwd frontend
```

---

## Step 5: Verify Deployment

### Check Backend (Railway):
```bash
# Should return: {"status": "healthy"}
curl https://your-railway-backend.up.railway.app/health

# Should return agent and app info
curl https://your-railway-backend.up.railway.app/
```

### Check Frontend (Vercel):
1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Open browser DevTools (F12) → Console
3. Check for any CORS errors
4. Try creating a meta-analysis to test the connection

---

## Common Issues & Fixes

### ❌ "Failed to fetch" errors on Vercel
**Fix**:
1. Check `NEXT_PUBLIC_API_URL` is set correctly in Vercel
2. Verify Railway backend is running (check Railway logs)
3. Make sure Railway CORS includes your Vercel URL

### ❌ CORS errors
**Fix**:
1. In Railway, update `ALLOWED_ORIGINS` to include your Vercel URL
2. Wait for Railway to redeploy (30-60 seconds)
3. Hard refresh your Vercel app (Ctrl+Shift+R or Cmd+Shift+R)

### ❌ Vercel showing "404: NOT_FOUND"
**Fix**:
1. Make sure Vercel is deploying from `main` branch
2. Check that `rootDirectory` is set to `frontend` in Project Settings
3. Redeploy from Vercel dashboard

### ❌ Railway "Module not found" errors
**Fix**:
1. Check that `requirements.txt` is in the `backend/` directory
2. Verify Railway is using the correct root directory (`backend`)
3. Check Railway build logs for specific errors

---

## Quick Reference

### Your URLs (Update these):
```
Railway Backend:  https://[YOUR-APP].up.railway.app
Vercel Frontend:  https://[YOUR-APP].vercel.app
GitHub Repo:      https://github.com/mrbrandonmills/meta-analysis-tool
```

### Environment Variables Needed:

**Railway Backend:**
- ✅ `ANTHROPIC_API_KEY` (required)
- ✅ `SECRET_KEY` (required)
- ✅ `DATABASE_URL` (auto-provided)
- ✅ `REDIS_URL` (auto-provided)
- ✅ `ALLOWED_ORIGINS` (your Vercel URL)
- ⚙️ `DEBUG=false`
- ⚙️ `LOG_LEVEL=INFO`

**Vercel Frontend:**
- ✅ `NEXT_PUBLIC_API_URL` (your Railway URL)

---

## Testing Checklist

After deployment, verify:

- [ ] Backend health endpoint responds: `/health`
- [ ] Frontend loads without errors
- [ ] Can create a new meta-analysis
- [ ] Search agent finds studies
- [ ] Screening agent categorizes studies
- [ ] Credibility assessment shows color codes
- [ ] QA agent answers questions
- [ ] No CORS errors in browser console

---

## Security Reminder

🔐 **After deployment, you should:**
1. Rotate your API keys (they were shared in chat)
2. Generate new Anthropic key: https://console.anthropic.com/
3. Generate new OpenAI key: https://platform.openai.com/api-keys
4. Update Railway environment variables
5. Delete old keys from providers

---

## Need Help?

Check these logs:
- **Railway**: Dashboard → Your Service → Deployments → Click deployment → View Logs
- **Vercel**: Dashboard → Your Project → Deployments → Click deployment → View Function Logs
- **Browser**: F12 → Console tab (for frontend errors)

---

**Branch Status:**
- ✅ `main` - Production ready
- ✅ Code merged and pushed
- ✅ Ready to deploy

**Next Action:** Follow Step 1 above to get your Railway URL! 🚀
