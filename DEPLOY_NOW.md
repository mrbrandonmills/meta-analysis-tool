# 🚀 COMPLETE DEPLOYMENT GUIDE - ALL IN ONE

## STEP-BY-STEP DEPLOYMENT

### Part 1: Deploy Backend to Railway (5 minutes)

**1. Go to Railway**
- Visit: https://railway.app
- Click "Login with GitHub"
- Authorize Railway

**2. Create New Project**
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose: `mrbrandonmills/meta-analysis-tool`
- Branch: `claude/ai-research-meta-analysis-tool-011CUoVRJHcpFgeW1MBBRiQ2`

**3. Add Services**
Click "+ New" for each:
- PostgreSQL (Add PostgreSQL plugin)
- Redis (Add Redis plugin)

**4. Configure Backend Service**
- Click on your main service (meta-analysis-tool)
- Go to "Settings"
- Set "Root Directory": `backend`
- Set "Start Command": `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- or use custom Start Command: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**5. Add Environment Variables**
In Railway dashboard, go to "Variables" tab and add:

```
ANTHROPIC_API_KEY=<your-anthropic-key-from-env-file>

OPENAI_API_KEY=<your-openai-key-from-env-file>

DATABASE_URL=${{Postgres.DATABASE_URL}}

REDIS_URL=${{Redis.REDIS_URL}}

SECRET_KEY=<generate-a-random-secret>

DEBUG=false

LOG_LEVEL=INFO
```

**IMPORTANT:** Get your actual API keys from the `.env` file on your local machine!

**6. Generate Public URL**
- Go to "Settings" → "Networking"
- Click "Generate Domain"
- Copy your URL (e.g., `https://your-app.up.railway.app`)

**7. Wait for Deploy**
- Watch the "Deployments" tab
- Should take 3-5 minutes
- Look for "SUCCESS" status

---

### Part 2: Deploy Frontend to Vercel (3 minutes)

**1. Go to Vercel**
- Visit: https://vercel.com
- Click "Login with GitHub"
- Authorize Vercel

**2. Import Project**
- Click "Add New..." → "Project"
- Select `mrbrandonmills/meta-analysis-tool`
- Choose branch: `claude/ai-research-meta-analysis-tool-011CUoVRJHcpFgeW1MBBRiQ2`

**3. Configure Build Settings**
Vercel will auto-detect Next.js, but configure:
- Framework Preset: **Next.js**
- Root Directory: **frontend**
- Build Command: `npm run build` (or leave default)
- Output Directory: `.next` (or leave default)
- Install Command: `npm install` (or leave default)

**4. Add Environment Variable**
Click "Environment Variables" and add:

```
Key: NEXT_PUBLIC_API_URL
Value: https://your-app.up.railway.app
```
(Use your Railway URL from Part 1, Step 6)

**5. Deploy**
- Click "Deploy"
- Wait 2-3 minutes
- Vercel will give you a URL like: `https://meta-analysis-tool.vercel.app`

---

## TESTING YOUR DEPLOYMENT

### Test Backend
```bash
curl https://your-app.up.railway.app/health
```
Should return: `{"status":"healthy"}`

### Test Frontend
1. Visit your Vercel URL
2. Try creating a meta-analysis
3. If you get errors, check:
   - Backend is running (check Railway logs)
   - Environment variables are set correctly
   - CORS is enabled (already configured in code)

---

## TROUBLESHOOTING

### Backend Won't Start on Railway
1. Check "Deployments" → "View Logs"
2. Common issues:
   - Missing environment variables
   - Wrong start command
   - Database not connected

**Fix:**
- Make sure `DATABASE_URL` shows: `${{Postgres.DATABASE_URL}}`
- Make sure `REDIS_URL` shows: `${{Redis.REDIS_URL}}`
- Redeploy after fixing

### Frontend Can't Reach Backend
1. Check `NEXT_PUBLIC_API_URL` in Vercel
2. Make sure it's your Railway URL (with https://)
3. Redeploy frontend after fixing

### API Key Errors
Your keys are exposed in this chat! After testing:
1. Go to https://console.anthropic.com/
2. Delete old key
3. Create new key
4. Update in Railway

---

## QUICK START COMMANDS (If you want CLI)

### Railway CLI (Optional)
```bash
# Install
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Vercel CLI (Optional)
```bash
# Install
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

---

## YOUR URLS AFTER DEPLOYMENT

Backend (Railway): `https://[your-project].up.railway.app`
Frontend (Vercel): `https://[your-project].vercel.app`

---

## NEXT STEPS AFTER DEPLOYMENT

1. ✅ Visit your Vercel URL
2. ✅ Create a test meta-analysis
3. ✅ Show your professor!
4. ⚠️  **ROTATE YOUR API KEYS** (they're exposed in chat)
5. 📊 Monitor usage in Railway/Vercel dashboards

---

## COST

- Railway: $5/month (includes PostgreSQL + Redis)
- Vercel: Free tier is enough
- **Total: ~$5/month**

---

## SUPPORT

- Railway Issues: https://railway.app/discord
- Vercel Issues: https://vercel.com/support
- Code Issues: GitHub Issues on your repo

---

## THAT'S IT! 🎉

Just follow Part 1 (Railway) then Part 2 (Vercel) and you're live!

The UI will have beautiful step-by-step workflow, animations, and guide users through the entire process.
