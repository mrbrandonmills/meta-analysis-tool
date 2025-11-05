# 🚀 Railway Fresh Setup - Step-by-Step Guide

## STEP 1: Delete Old Service (1 minute)

1. **Go to Railway Dashboard:**
   ```
   https://railway.app/dashboard
   ```

2. **Click on your current service** (meta-analysis-tool)

3. **Click "Settings" tab** (left sidebar)

4. **Scroll to the bottom** → Find "Delete Service"

5. **Click "Delete Service"** → Confirm deletion

---

## STEP 2: Create New Service (3 minutes)

### **2.1: Start Fresh**

1. **Click "New Project"** (top right)

2. **Select "Deploy from GitHub repo"**

3. **Choose: `mrbrandonmills/meta-analysis-tool`**

4. **Railway will detect the repo** → Click "Deploy Now"

---

### **2.2: Configure Service**

1. **Click on the new service** (will be deploying)

2. **Click "Settings" tab**

3. **Set Root Directory:**
   - Find "Root Directory" field
   - Leave it BLANK (we'll use Dockerfile path instead)
   - Click "Update"

4. **Verify Dockerfile Path:**
   - Should show: `backend/Dockerfile`
   - This is set by railway.toml (already in your repo)

5. **IMPORTANT - Custom Start Command:**
   - Find "Custom Start Command"
   - Make sure it's **EMPTY/BLANK**
   - If there's anything there, DELETE IT
   - Click "Update"

6. **Set Healthcheck:**
   - Find "Healthcheck Path"
   - Should already be: `/health` (from railway.toml)
   - If not, set it to: `/api/v1/health`
   - Click "Update"

---

## STEP 3: Add Database Services (2 minutes)

### **3.1: Add PostgreSQL**

1. **Click "New" button** (top right)

2. **Select "Database" → "Add PostgreSQL"**

3. **PostgreSQL will provision** (takes 30 seconds)

4. **Note:** Railway auto-creates DATABASE_URL variable

### **3.2: Add Redis**

1. **Click "New" button** again

2. **Select "Database" → "Add Redis"**

3. **Redis will provision** (takes 30 seconds)

4. **Note:** Railway auto-creates REDIS_URL variable

---

## STEP 4: Add Environment Variables (3 minutes)

1. **Click on your service** (the main app, not databases)

2. **Click "Variables" tab**

3. **Click "New Variable"** and add these ONE BY ONE:

### **Required Variables:**

```bash
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE
```
⚠️ Replace with your REAL Anthropic API key

```bash
SECRET_KEY=your-super-secret-key-min-32-characters-long-random-string
```
⚠️ Generate a random 32+ character string

```bash
ENVIRONMENT=production
```

```bash
DEBUG=false
```

```bash
PORT=${{PORT}}
```
✅ Railway auto-provides this

```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
```
✅ Links to PostgreSQL database

```bash
REDIS_URL=${{Redis.REDIS_URL}}
```
✅ Links to Redis database

### **Optional Variables (for later):**

```bash
ALLOWED_ORIGINS=https://meta-analysis-tool.vercel.app,https://meta-analysis-tool-brandons-projects-c4dfa14a.vercel.app
```

```bash
LOG_LEVEL=INFO
```

4. **Click "Add" for each variable**

---

## STEP 5: Deploy and Verify (5 minutes)

### **5.1: Trigger Deployment**

1. **Go to "Deployments" tab**

2. **Click "Deploy"** (or wait for auto-deploy)

3. **Watch the build logs:**
   - Should see Dockerfile building
   - Should see pip installing dependencies
   - Build time: ~60 seconds (first time)

### **5.2: Check Deploy Logs**

**Look for these SUCCESS indicators:**

```
✅ Build time: XX seconds
✅ Deploy › Create container
✅ Starting Meta Analysis Tool Backend API...
✅ INFO: Started server process [1]
✅ INFO: Application startup complete.
✅ INFO: Uvicorn running on http://0.0.0.0:8000
```

**Status should change to:** ✅ **Running**

### **5.3: Get Your Railway URL**

1. **Click "Settings" tab**

2. **Under "Networking" → "Public Networking"**

3. **Copy the URL:**
   ```
   https://meta-analysis-tool-production.up.railway.app
   ```

### **5.4: Test the Backend**

Open terminal and test:

```bash
# Replace with your actual Railway URL
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health
```

**Expected response:**
```json
{"status":"healthy","timestamp":"2025-11-05T...","version":"1.0.0"}
```

✅ **If you see this, backend is WORKING!**

---

## STEP 6: Connect to Vercel (3 minutes)

### **6.1: Update Vercel Environment Variable**

1. **Go to Vercel Dashboard:**
   ```
   https://vercel.com/brandons-projects-c4dfa14a/meta-analysis-tool
   ```

2. **Click "Settings" tab**

3. **Click "Environment Variables"** (left sidebar)

4. **Find `NEXT_PUBLIC_API_URL`** or click "Add New"

5. **Set the value to your Railway URL:**
   ```
   https://meta-analysis-tool-production.up.railway.app
   ```

6. **Select environments:** Production, Preview, Development

7. **Click "Save"**

### **6.2: Redeploy Vercel**

1. **Go to "Deployments" tab**

2. **Click the latest deployment**

3. **Click the three dots (...) → "Redeploy"**

4. **Wait 2-3 minutes for build**

5. **Status should be:** ✅ **Ready**

---

## STEP 7: Test Full Integration (2 minutes)

### **7.1: Test Frontend**

**Visit your Vercel site:**
```
https://meta-analysis-tool.vercel.app
```

**You should see:**
- ✨ Animated landing page
- 🎨 Floating orbs
- 🌊 Smooth scrolling
- 💫 All animations working

### **7.2: Test API Connection**

**Open browser console** (F12) and check:
- No CORS errors
- No API connection errors
- Frontend can talk to Railway backend

**Or test directly:**

```bash
# Your Vercel frontend should call your Railway backend
# Check Network tab in browser DevTools when visiting the site
```

---

## 🎉 SUCCESS CHECKLIST

Check all these boxes:

- [ ] Old Railway service deleted
- [ ] New Railway service created
- [ ] PostgreSQL database added
- [ ] Redis database added
- [ ] All environment variables set
- [ ] Railway deployment shows "Running"
- [ ] Backend health check returns `{"status":"healthy"}`
- [ ] Vercel environment variable updated with Railway URL
- [ ] Vercel redeployed successfully
- [ ] Frontend loads with animations
- [ ] No CORS errors in console

---

## 🐛 Troubleshooting

### **If Railway Build Fails:**

1. Check build logs for specific error
2. Verify `backend/Dockerfile` exists in repo
3. Verify `railway.toml` has correct dockerfilePath

### **If Railway Deploy Fails:**

1. Check deploy logs
2. Verify ANTHROPIC_API_KEY is set correctly
3. Verify DATABASE_URL and REDIS_URL are linked
4. Check that Custom Start Command is EMPTY

### **If Vercel Can't Connect to Railway:**

1. Verify Railway URL is correct in Vercel env vars
2. Check Railway logs for CORS errors
3. Verify ALLOWED_ORIGINS includes your Vercel URLs
4. Check Railway service is "Running"

### **If You See "cd" Error Again:**

1. Railway Settings → Custom Start Command
2. Make ABSOLUTELY SURE it's empty/blank
3. If anything is there, DELETE IT
4. Save and redeploy

---

## 📞 Your URLs After Setup

**Backend (Railway):**
```
https://meta-analysis-tool-production.up.railway.app
```

**Frontend (Vercel):**
```
https://meta-analysis-tool.vercel.app
```

**Health Check:**
```
https://meta-analysis-tool-production.up.railway.app/api/v1/health
```

**API Docs:**
```
https://meta-analysis-tool-production.up.railway.app/docs
```

---

## 💪 You're Done!

Total time: ~20 minutes

You now have:
- ✅ Fresh Railway backend (no cached configs)
- ✅ PostgreSQL + Redis databases
- ✅ Proper environment variables
- ✅ Connected to Vercel frontend
- ✅ Jaw-dropping UI live
- ✅ Full integration working

**Your academic research platform is LIVE and WORKING!** 🎉🚀✨
