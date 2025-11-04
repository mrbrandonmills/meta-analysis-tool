# 🎯 START HERE - Complete Deployment Instructions

## What You Have

A **complete AI-powered meta-analysis platform** with:
- ✅ Multi-agent backend (Python/FastAPI)
- ✅ Beautiful step-by-step UI (Next.js/React)
- ✅ Complete agent system (Coordinator, Search, Screening, Q&A agents)
- ✅ Real PubMed integration
- ✅ Docker setup
- ✅ Production-ready code

## Your API Keys (Local .env file)

Your keys are securely stored in `/home/user/meta-analysis-tool/.env`:
- Anthropic API Key: ✅ Configured
- OpenAI API Key: ✅ Configured

**⚠️ SECURITY NOTE:** These keys were shared in chat. After testing, rotate them!

## Quick Deploy (8 minutes total)

### STEP 1: Deploy Backend to Railway (5 min)

1. **Go to** https://railway.app
2. **Login** with GitHub
3. **New Project** → "Deploy from GitHub repo"
4. **Select** your repo: `mrbrandonmills/meta-analysis-tool`
5. **Add Services**:
   - Click "+ New" → Add PostgreSQL
   - Click "+ New" → Add Redis
6. **Configure Backend**:
   - Root Directory: `backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. **Add Variables** (copy from your `.env` file):
   ```
   ANTHROPIC_API_KEY=<from-your-env-file>
   OPENAI_API_KEY=<from-your-env-file>
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   SECRET_KEY=your-secret-here
   ```
8. **Generate Domain** → Copy your URL

### STEP 2: Deploy Frontend to Vercel (3 min)

1. **Go to** https://vercel.com
2. **Login** with GitHub
3. **Add New** → Project
4. **Select** your repo: `mrbrandonmills/meta-analysis-tool`
5. **Configure**:
   - Root Directory: `frontend`
   - Framework: Next.js (auto-detected)
6. **Add Environment Variable**:
   ```
   NEXT_PUBLIC_API_URL=<your-railway-url>
   ```
7. **Deploy!**

## Test Your Deployment

### Backend Health Check
```bash
curl https://your-app.up.railway.app/health
```
Should return: `{"status":"healthy"}`

### Frontend
Visit: `https://your-app.vercel.app`

## What the UI Does

Beautiful step-by-step wizard that:

### Step 1: Research Question
- Define research question & topic
- Add inclusion/exclusion criteria
- Creates AI workflow

### Step 2: Search & Screen
- Searches PubMed automatically
- Applies your criteria
- Shows results breakdown

### Step 3: Analysis & Q&A
- Interactive chat with Q&A agent
- Ask questions about decisions
- Get confidence scores
- Follow-up suggestions

### Step 4: Results
- Complete meta-analysis
- Download report
- View audit trail

## Local Testing (Optional)

### Backend
```bash
cd backend
source venv/bin/activate
python -m app.main
```
Visit: http://localhost:8000

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Visit: http://localhost:3000

## File Structure

```
meta-analysis-tool/
├── DEPLOY_NOW.md          ← Complete deployment guide
├── START_HERE.md          ← THIS FILE
├── ARCHITECTURE.md        ← System design
├── backend/
│   ├── app/
│   │   ├── agents/        ← AI agents (Coordinator, Search, Screening, Q&A)
│   │   ├── api/v1/        ← REST endpoints
│   │   └── main.py        ← FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/pages/
│   │   └── index.tsx      ← Beautiful UI
│   └── package.json
└── .env                   ← Your API keys (local only)
```

## URLs You'll Need

- **GitHub Repo**: https://github.com/mrbrandonmills/meta-analysis-tool
- **Railway Dashboard**: https://railway.app/dashboard
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Anthropic Console**: https://console.anthropic.com/
- **OpenAI Console**: https://platform.openai.com/

## Cost

- Railway: $5/month (backend + database + redis)
- Vercel: FREE
- **Total: $5/month**

## Next Steps After Deployment

1. ✅ Test the deployment
2. ✅ Create a sample meta-analysis
3. ✅ Show your psychology professor
4. ⚠️  **Rotate API keys** (they were shared in chat)
5. 📊 Monitor usage in dashboards

## Troubleshooting

### Backend won't start on Railway
- Check "Deployments" → "View Logs"
- Verify environment variables are set
- Ensure DATABASE_URL and REDIS_URL use `${{...}}` syntax

### Frontend can't reach backend
- Check NEXT_PUBLIC_API_URL in Vercel
- Must be your Railway URL (with https://)
- Redeploy after changing

### API Key errors
- Copy keys from `.env` file
- Don't use placeholder text
- Rotate keys after testing

## Security Checklist

- [ ] API keys added to Railway (not in git)
- [ ] Environment variables configured
- [ ] HTTPS enabled (automatic on Railway/Vercel)
- [ ] After testing, rotate both API keys
- [ ] Never commit .env file to git

## Demo Script for Your Professor

1. Open your Vercel URL
2. Show the beautiful step-by-step interface
3. Enter research question: "What is the effectiveness of mindfulness on anxiety?"
4. Add criteria (pre-filled examples)
5. Click "Create Workflow" → Show AI planning
6. Click "Start Analysis" → Show PubMed search results
7. Show screening results (included/excluded/uncertain)
8. Ask Q&A agent: "How did you decide which studies to include?"
9. Show confidence scores and explanations
10. Explain audit trail for peer review

## Support

- **This Project**: GitHub Issues on your repo
- **Railway**: https://railway.app/discord
- **Vercel**: https://vercel.com/support
- **Anthropic**: https://docs.anthropic.com/

---

## 🚀 Ready to Deploy?

1. Read `DEPLOY_NOW.md` for step-by-step guide
2. Deploy backend to Railway (5 min)
3. Deploy frontend to Vercel (3 min)
4. Test and share!

**That's it!** You have a production-ready meta-analysis platform powered by AI agents.
