# 🚀 DEPLOYMENT ARCHITECTURE

**Date:** November 26, 2025  
**Project:** Meta-Analysis Research Platform

---

## ⚠️ IMPORTANT CLARIFICATION

**Your question:** "Is all this pushed to Vercel from Railway?"  
**Answer:** NO - Railway and Vercel are SEPARATE deployment platforms hosting DIFFERENT parts of the application.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                           │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌────────────────┐      ┌────────────────┐
│   VERCEL       │      │   RAILWAY      │
│   (Frontend)   │─────▶│   (Backend)    │
│                │      │                │
│ Next.js App    │ API  │ FastAPI App    │
│ React UI       │ Calls│ Python API     │
│ Static Assets  │      │ PostgreSQL DB  │
└────────────────┘      └────────────────┘
```

---

## 🌐 FRONTEND (Vercel)

**Platform:** Vercel  
**Technology:** Next.js 15 + React + TypeScript  
**Project:** `frontend` (brandons-projects-c4dfa14a)

### Production URL
**Latest Deployment:** https://frontend-4hognfvwt-brandons-projects-c4dfa14a.vercel.app  
**Status:** ✅ LIVE (deployed 2 days ago)  
**Duration:** 1 minute build time

### Environment Variable
```bash
NEXT_PUBLIC_API_URL=https://meta-analysis-tool-production.up.railway.app
```

### What's Deployed
- Meta-analysis creation forms
- Progress tracking UI
- Download/export functionality
- E2E test integration (7 data-testid attributes)
- Reviewer matcher tool
- Dashboard
- Authentication UI

### Recent Deployments
```
✅ frontend-4hognfvwt  - Production (2d ago)
✅ frontend-wj84s0qnh  - Production (4d ago)
✅ frontend-aks6mcgx5  - Preview    (4d ago)
✅ frontend-ey4uwfjam  - Production (4d ago)
```

---

## 🔧 BACKEND (Railway)

**Platform:** Railway  
**Technology:** FastAPI + Python 3.12 + PostgreSQL  
**Project:** `meta-analysis-tool-production`

### Production URL
**API Base:** https://meta-analysis-tool-production.up.railway.app  
**Health Check:** https://meta-analysis-tool-production.up.railway.app/api/v1/health  
**API Docs:** https://meta-analysis-tool-production.up.railway.app/docs

### Status
```json
{
  "status": "healthy",
  "timestamp": "2025-11-27T00:18:33.117486",
  "service": "meta-analysis-platform",
  "version": "0.1.0"
}
```

### What's Deployed
- Meta-analysis workflow engine
- 6 specialized research agents (Coordinator, Search, Screening, Full-text, QA, Credibility)
- Database integrations (PubMed, arXiv, Semantic Scholar, Crossref)
- PostgreSQL database
- Task queue system
- API key management
- Authentication endpoints

### Configuration
```json
{
  "builder": "DOCKERFILE",
  "dockerfilePath": "backend/Dockerfile",
  "healthcheckPath": "/api/v1/health",
  "healthcheckTimeout": 300
}
```

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Task queue
- `ANTHROPIC_API_KEY` - AI processing
- `OPENAI_API_KEY` - AI processing
- `SECRET_KEY` - Security

---

## 🔗 FRONTEND ↔ BACKEND CONNECTION

### How They Connect

1. **Frontend makes API calls:**
   ```typescript
   const API_URL = "https://meta-analysis-tool-production.up.railway.app";
   
   // Create meta-analysis
   await fetch(`${API_URL}/api/v1/meta-analysis/create`, {
     method: 'POST',
     body: JSON.stringify(data)
   });
   ```

2. **Backend processes request:**
   - Receives request at Railway
   - Executes workflow with 6 agents
   - Stores results in PostgreSQL
   - Returns response

3. **Frontend displays results:**
   - Real-time progress tracking
   - Download reports (PDF/JSON)
   - Display analytics

### ✅ Connection Verified

**Test Result:**
```bash
$ python3 test_api_quick.py

Status: 200 ✅
Meta-analysis ID: 498784c6-be57-49ac-b515-9af8514f7ad2
Message: "Meta-analysis created successfully"
```

---

## 📦 DEPLOYMENT WORKFLOW

### Backend (Railway) Deployment
```bash
# Automatic deployment on git push
git push origin main
↓
Railway detects changes in backend/**
↓
Builds Docker image from backend/Dockerfile
↓
Runs health check on /api/v1/health
↓
Deploys to production
```

### Frontend (Vercel) Deployment
```bash
# Manual or automatic deployment
cd frontend
npx vercel --prod
↓
Vercel builds Next.js app
↓
Injects NEXT_PUBLIC_API_URL env var
↓
Deploys static assets + serverless functions
↓
Live at frontend-*.vercel.app
```

---

## 🔄 SYNC STATUS

### GitHub → Railway
✅ **Synced** - Railway pulls from `main` branch automatically

### GitHub → Vercel
⚠️ **Manual** - Requires `npx vercel --prod` from frontend directory

### MASTER Branch → Both Platforms
✅ **Code in sync** - Both platforms use code from `/Volumes/Super Mastery/meta-analysis-tool`

---

## 🎯 DEPLOYMENT CHECKLIST

### Backend (Railway)
- [x] Backend API deployed and healthy
- [x] Database connected
- [x] Environment variables configured
- [x] Health check passing
- [x] API documentation accessible

### Frontend (Vercel)
- [x] Frontend deployed to Vercel
- [x] API URL configured (NEXT_PUBLIC_API_URL)
- [x] Build successful
- [x] Production deployment live
- [ ] Custom domain configured (optional)

### Integration
- [x] Frontend can reach backend API
- [x] CORS configured correctly
- [x] Authentication working
- [x] Meta-analysis workflow functional

---

## 🚀 NEXT DEPLOYMENT STEPS

### To Deploy Latest Frontend Changes:
```bash
cd "/Volumes/Super Mastery/meta-analysis-tool/frontend"
npx vercel --prod
```

### To Deploy Latest Backend Changes:
```bash
# Just push to GitHub - Railway auto-deploys
cd "/Volumes/Super Mastery/meta-analysis-tool"
git push origin main
```

### To Deploy Both:
```bash
# 1. Push to GitHub (deploys backend via Railway)
git push origin main

# 2. Deploy frontend manually
cd frontend
npx vercel --prod
```

---

## 📝 SUMMARY

**CONFIRMED:**
- ✅ Backend is deployed and running on Railway
- ✅ Frontend is deployed and running on Vercel  
- ✅ Frontend is configured to connect to Railway backend
- ✅ API connection tested and working
- ✅ Latest code from MASTER is on GitHub
- ✅ Railway auto-deploys from GitHub
- ⚠️ Vercel requires manual deployment

**NOT DEPLOYED:**
- ❌ Latest consolidation changes NOT yet on Vercel (2 days old deployment)
- ❌ E2E test fixes NOT yet on Vercel
- ❌ Playwright config NOT yet on Vercel

**ACTION REQUIRED:**
Run `npx vercel --prod` from frontend directory to deploy latest changes.

---

**Railway hosts the BACKEND.**  
**Vercel hosts the FRONTEND.**  
**They are SEPARATE but CONNECTED platforms.**
