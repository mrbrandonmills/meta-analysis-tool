# Deployment Guide

This guide shows you how to deploy the Meta-Analysis Research Platform to production.

## Architecture

- **Frontend**: Next.js deployed to Vercel
- **Backend**: Python/FastAPI deployed to Railway (or similar)
- **Database**: PostgreSQL on Railway/Neon
- **Cache**: Redis on Railway/Upstash

## Option 1: Quick Deploy (Recommended)

### Deploy Backend to Railway

1. **Sign up for Railway**:
   - Go to https://railway.app
   - Sign in with GitHub

2. **Deploy Backend**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login
   railway login

   # Create new project
   railway init

   # Add Dockerfile for backend
   railway up
   ```

3. **Add Environment Variables** in Railway dashboard:
   ```
   ANTHROPIC_API_KEY=your_key
   OPENAI_API_KEY=your_key
   DATABASE_URL=[automatically provided by Railway PostgreSQL]
   REDIS_URL=[automatically provided by Railway Redis]
   ```

4. **Note your backend URL**: Something like `https://your-app.railway.app`

### Deploy Frontend to Vercel

1. **Push to GitHub**:
   ```bash
   git add -A
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Deploy to Vercel**:
   - Go to https://vercel.com
   - Click "Import Project"
   - Select your GitHub repository
   - Vercel will auto-detect Next.js

3. **Configure Environment Variables** in Vercel:
   ```
   NEXT_PUBLIC_API_URL=https://your-app.railway.app
   ```

4. **Deploy**: Click Deploy!

## Option 2: All-in-One with Docker

Deploy both frontend and backend together:

### Using Railway:

1. Use the `docker-compose.yml` file
2. Railway will detect and deploy

### Using Fly.io:

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

## Option 3: Serverless (Advanced)

Convert the backend to Vercel serverless functions.

This requires restructuring the FastAPI app into individual serverless functions.
See `docs/SERVERLESS.md` for details.

## Environment Variables Required

### Backend:
```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
DATABASE_URL=
REDIS_URL=
SECRET_KEY=
```

### Frontend:
```
NEXT_PUBLIC_API_URL=
```

## Post-Deployment

### 1. Test the API
```bash
curl https://your-backend.railway.app/health
```

### 2. Test the Frontend
Visit: https://your-app.vercel.app

### 3. Test Integration
Create a meta-analysis through the web interface

## Monitoring

### Railway:
- View logs in Railway dashboard
- Monitor metrics and usage

### Vercel:
- View analytics in Vercel dashboard
- Monitor function execution times

## Scaling

### Backend (Railway):
- Automatically scales based on usage
- Can manually adjust resources in dashboard

### Frontend (Vercel):
- Automatically scales globally
- CDN distribution included

## Cost Estimates

### Railway:
- Hobby plan: $5/month
- Pro plan: $20/month + usage
- Includes PostgreSQL and Redis

### Vercel:
- Free tier: Great for testing
- Pro: $20/month for production

### Total estimate: $0-40/month depending on usage

## Security Checklist

- [ ] API keys secured in environment variables
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] HTTPS enforced
- [ ] Database backups configured
- [ ] Error tracking set up (Sentry)

## Troubleshooting

### Backend won't start:
- Check logs in Railway dashboard
- Verify environment variables are set
- Check database connection

### Frontend can't reach backend:
- Verify NEXT_PUBLIC_API_URL is correct
- Check CORS settings in backend
- Verify API is running

### Database connection errors:
- Check DATABASE_URL format
- Verify database is provisioned
- Check firewall settings

## Rolling Back

### Railway:
```bash
railway rollback
```

### Vercel:
- Go to Deployments
- Click "..." on previous deployment
- Click "Promote to Production"

## Support

- Railway: https://railway.app/discord
- Vercel: https://vercel.com/support
- Project issues: GitHub Issues

---

**Quick Commands**:

```bash
# Deploy backend to Railway
railway up

# Deploy frontend to Vercel (via GitHub)
git push

# View backend logs
railway logs

# View frontend logs
vercel logs
```
