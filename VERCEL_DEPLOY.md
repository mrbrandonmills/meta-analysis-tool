# Deploy to Vercel - Step by Step

## Quick Deploy Guide 🚀

### Step 1: Deploy to Vercel (Frontend)

The easiest way is through the Vercel dashboard:

1. **Go to Vercel**: https://vercel.com
2. **Sign in with GitHub**
3. **Click "Add New... → Project"**
4. **Import your repository**: `mrbrandonmills/meta-analysis-tool`
5. **Configure**:
   - Framework Preset: **Next.js**
   - Root Directory: **frontend**
   - Build Command: `npm run build`
   - Output Directory: `.next`

6. **Add Environment Variable**:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-backend-url.railway.app` (we'll get this in Step 2)

7. **Click Deploy!**

### Step 2: Deploy Backend (Python/FastAPI)

The backend needs a Python-friendly platform. **Railway** is easiest:

1. **Go to Railway**: https://railway.app
2. **Sign in with GitHub**
3. **New Project → Deploy from GitHub repo**
4. **Select your repository**
5. **Add PostgreSQL** (click "+ New" → Database → PostgreSQL)
6. **Add Redis** (click "+ New" → Database → Redis)
7. **Configure the backend service**:
   - Root Directory: **backend**
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

8. **Add Environment Variables** in Railway:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-fT3kbE76mmf...
   OPENAI_API_KEY=sk-proj-DYP5Mn8fqq...
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   SECRET_KEY=your-secret-key-here
   ```

9. **Generate Domain**: Railway will give you a URL like `your-app.up.railway.app`

10. **Copy this URL** and go back to Vercel:
    - Settings → Environment Variables
    - Update `NEXT_PUBLIC_API_URL` with your Railway URL
    - Redeploy

### Step 3: Test It!

Visit your Vercel URL (e.g., `https://meta-analysis-tool.vercel.app`)

## Alternative: CLI Deployment

### Vercel CLI:

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd meta-analysis-tool
vercel --prod

# Follow prompts:
# - Link to existing project? No
# - Project name: meta-analysis-tool
# - Directory: ./frontend
```

### Railway CLI:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy
railway up
```

## Environment Variables

### Required for Backend (Railway):
- `ANTHROPIC_API_KEY` - Your Claude API key
- `OPENAI_API_KEY` - Your OpenAI API key (optional)
- `DATABASE_URL` - Auto-provided by Railway PostgreSQL
- `REDIS_URL` - Auto-provided by Railway Redis
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`

### Required for Frontend (Vercel):
- `NEXT_PUBLIC_API_URL` - Your Railway backend URL

## Quick Links

- **Your GitHub Repo**: https://github.com/mrbrandonmills/meta-analysis-tool
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Railway Dashboard**: https://railway.app/dashboard

## Troubleshooting

### "Module not found" errors:
```bash
# In frontend directory:
cd frontend
npm install
```

### Backend won't start:
- Check Railway logs
- Verify all environment variables are set
- Make sure DATABASE_URL and REDIS_URL are connected

### Frontend can't reach backend:
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS settings in `backend/app/main.py`
- Make sure backend is running (check Railway logs)

## What Gets Deployed

### Frontend (Vercel):
- Next.js web interface
- React components
- Tailwind CSS styling
- Automatic CDN distribution
- HTTPS included

### Backend (Railway):
- FastAPI Python server
- All AI agents
- PostgreSQL database
- Redis cache
- Background workers

## Cost

- **Vercel**: Free tier is enough for testing
- **Railway**: $5/month hobby plan includes:
  - Backend hosting
  - PostgreSQL database
  - Redis cache
  - 500 hours of execution

**Total**: ~$5/month

## After Deployment

1. **Test the API**: `curl https://your-backend.railway.app/health`
2. **Test the Frontend**: Visit your Vercel URL
3. **Create a meta-analysis**: Try the web interface
4. **Rotate API keys**: Since they were shared in chat, generate new ones:
   - Anthropic: https://console.anthropic.com/
   - OpenAI: https://platform.openai.com/api-keys

## Next Steps

- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Railway
- [ ] Update environment variables
- [ ] Test the deployment
- [ ] Rotate API keys (security!)
- [ ] Share with your professor

---

**Need help?** Check DEPLOYMENT.md for more detailed instructions.
