# Frontend Deployment - Live URLs and Configuration

## Live Production URLs

### Frontend (Vercel)
- **URL**: https://frontend-21t1abo91-brandons-projects-c4dfa14a.vercel.app
- **Status**: ✓ OPERATIONAL (HTTP 200)
- **Framework**: Next.js 14.0.0
- **Deployment**: November 7, 2025

### Backend (Railway)
- **URL**: https://meta-analysis-tool-production.up.railway.app
- **Status**: ✓ OPERATIONAL (HTTP 200)
- **Version**: 0.1.0
- **Agents**: 5/25 operational

## Environment Configuration

### Frontend Environment File
**Path**: `/Users/brandon/meta-analysis-tool/frontend/.env.production`

```
NEXT_PUBLIC_API_URL=https://meta-analysis-tool-production.up.railway.app
```

### Vercel Configuration
**Path**: `/Users/brandon/meta-analysis-tool/frontend/vercel.json`

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "outputDirectory": ".next",
  "cleanUrls": true,
  "trailingSlash": false,
  "regions": ["iad1"],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://meta-analysis-tool-production.up.railway.app"
  }
}
```

## Access Instructions

### For Users
Simply navigate to:
```
https://frontend-21t1abo91-brandons-projects-c4dfa14a.vercel.app
```

### For Developers
**Repository**: https://github.com/mrbrandonmills/meta-analysis-tool

**Quick Commands**:
```bash
# Clone the repository
git clone https://github.com/mrbrandonmills/meta-analysis-tool.git

# Navigate to frontend
cd meta-analysis-tool/frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Deploy to Vercel
npx vercel --prod
```

## Important Git Configuration

For deployments, use the correct git author:
```bash
git config user.email "therealbrandonmills@gmail.com"
git config user.name "Brandon Mills"
```

## Git Commit References

- **Latest Deployment**: c0a9668
- **Fix Commit**: c0a9668 - Fix: Correct AgentStatusCard component prop type for Vercel build
- **Deploy Commit**: c294412 - Deploy: Update environment and fix git author for Vercel deployment

## Verification Checks

All systems operational:

1. Frontend Accessibility: ✓ HTTP 200
2. Backend Accessibility: ✓ HTTP 200
3. Backend Health: ✓ Operational
4. Environment Configuration: ✓ Correct
5. Frontend-Backend Integration: ✓ Ready

## Support Documentation

- **Deployment Details**: `/Users/brandon/meta-analysis-tool/VERCEL_DEPLOYMENT_FIX.md`
- **Success Summary**: `/Users/brandon/meta-analysis-tool/DEPLOYMENT_SUCCESS.md`

---

**Last Updated**: November 7, 2025
**Status**: PRODUCTION OPERATIONAL
