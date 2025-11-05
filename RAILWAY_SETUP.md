# Railway Deployment Guide - Meta-Analysis Research Platform

This guide provides step-by-step instructions for deploying the Meta-Analysis Research Platform backend on Railway.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Environment Variables Configuration](#environment-variables-configuration)
4. [Database Setup](#database-setup)
5. [Deployment](#deployment)
6. [Verification](#verification)
7. [Common Issues](#common-issues)
8. [Production Checklist](#production-checklist)

---

## Prerequisites

Before deploying to Railway, ensure you have:

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Anthropic API Key**: Get from [console.anthropic.com](https://console.anthropic.com/)
3. **GitHub Repository**: Your code should be in a GitHub repository
4. **Vercel Frontend** (optional): If you have a frontend deployed on Vercel

---

## Initial Setup

### 1. Create a New Railway Project

1. Go to [railway.app](https://railway.app) and log in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `meta-analysis-tool`
5. Railway will automatically detect the Python application

### 2. Configure Build Settings

Railway should automatically detect your Python application. If needed, configure:

- **Root Directory**: `/backend` (if your backend is in a subdirectory)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## Environment Variables Configuration

### Required Variables (CRITICAL)

Add these environment variables in Railway's **Variables** tab:

#### 1. Anthropic API Key (REQUIRED)
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...
```
- **Where to get**: [console.anthropic.com](https://console.anthropic.com/)
- **Format**: Must start with `sk-ant-`
- **Critical**: The app will not start without this

#### 2. Secret Key (REQUIRED)
```
SECRET_KEY=your-secure-random-key-here
```
- **Generate with**:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- **Purpose**: Used for JWT token signing and security
- **Important**: Keep this secret and never commit to version control

### Recommended Variables

#### 3. Debug Mode (RECOMMENDED)
```
DEBUG=false
```
- **Default**: `false` (if omitted)
- **Production**: Always set to `false` or omit
- **Development**: Can set to `true` for testing

#### 4. Log Level (RECOMMENDED)
```
LOG_LEVEL=INFO
```
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Production**: Use `INFO` or `WARNING`
- **Development**: Use `DEBUG` for detailed logs

#### 5. CORS Origins (RECOMMENDED)
```
ALLOWED_ORIGINS=https://meta-analysis-tool.vercel.app,https://your-custom-domain.com
```
- **Purpose**: Allow your frontend to make API requests
- **Format**: Comma-separated list of URLs (no spaces)
- **Example**: `https://your-app.vercel.app,https://www.your-domain.com`

### Optional Variables

#### 6. OpenAI API Key (OPTIONAL)
```
OPENAI_API_KEY=sk-xxxxx...
```
- Only needed if using OpenAI models
- Get from: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

#### 7. PubMed API (OPTIONAL)
```
PUBMED_API_KEY=your_pubmed_key
PUBMED_EMAIL=your_email@example.com
```
- Required for PubMed search functionality
- Get from: [NCBI Account Settings](https://www.ncbi.nlm.nih.gov/account/)

#### 8. Feature Flags (OPTIONAL)
```
ENABLE_VOICE=false
ENABLE_LEARNING=true
ENABLE_VERIFICATION=true
```

---

## Database Setup

### Option 1: Railway PostgreSQL (Recommended)

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway automatically creates `DATABASE_URL` environment variable
4. **No manual configuration needed!**

### Option 2: Railway Redis (Optional)

For caching and session storage:

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add Redis"**
3. Railway automatically creates `REDIS_URL` environment variable

### Option 3: External Database

If using an external database:

```
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://user:password@host:port/0
```

---

## Deployment

### Automatic Deployment

Railway automatically deploys on every push to your main branch:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Configure for Railway deployment"
   git push origin main
   ```

2. **Monitor Deployment**:
   - Go to your Railway project dashboard
   - Click on the **"Deployments"** tab
   - Watch the build logs for any errors

### Manual Deployment

To manually trigger a deployment:

1. Go to your service in Railway
2. Click **"Deploy"** → **"Redeploy"**

---

## Verification

### 1. Check Service Health

Once deployed, verify your service is running:

1. **Get Service URL**:
   - Railway provides a public URL like `https://your-service.railway.app`
   - Find it in the **"Settings"** → **"Domains"** section

2. **Test Health Endpoint**:
   ```bash
   curl https://your-service.railway.app/health
   ```

   Expected response:
   ```json
   {"status": "healthy"}
   ```

3. **Test Root Endpoint**:
   ```bash
   curl https://your-service.railway.app/
   ```

   Expected response:
   ```json
   {
     "name": "Meta-Analysis Research Platform",
     "version": "0.1.0",
     "status": "operational",
     "agents": "ready"
   }
   ```

### 2. Check Agent Endpoints

Test the agents endpoint:

```bash
curl https://your-service.railway.app/api/v1/agents/list
```

Expected: List of available agents

### 3. Check Logs

Monitor application logs in Railway:

1. Go to your service
2. Click **"Logs"** tab
3. Look for:
   - ✅ `Starting Meta-Analysis Research Platform`
   - ✅ `✓ Anthropic API key validated successfully`
   - ✅ `Debug mode: False`
   - ❌ No error messages about missing API keys

---

## Common Issues

### Issue 1: "Anthropic API key is missing"

**Error Message**:
```
CRITICAL ERROR: Anthropic API key is missing or not configured
```

**Solution**:
1. Go to Railway Variables tab
2. Add `ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...`
3. Redeploy the service

### Issue 2: "API key appears to be invalid"

**Error Message**:
```
CRITICAL ERROR: Anthropic API key appears to be invalid (should start with 'sk-ant-')
```

**Solution**:
1. Verify your API key format
2. Ensure it starts with `sk-ant-`
3. Get a new key from [console.anthropic.com](https://console.anthropic.com/) if needed

### Issue 3: CORS Errors from Frontend

**Error Message** (in browser console):
```
Access to fetch at 'https://api.railway.app/...' from origin 'https://your-app.vercel.app' has been blocked by CORS policy
```

**Solution**:
1. Add your frontend URL to `ALLOWED_ORIGINS` in Railway Variables:
   ```
   ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
   ```
2. Redeploy the service

### Issue 4: Debug Mode Enabled in Production

**Error Message** (in logs):
```
Debug mode: True
```

**Solution**:
1. Set `DEBUG=false` in Railway Variables (or remove it entirely)
2. Redeploy the service
3. Verify in logs: `Debug mode: False`

### Issue 5: Database Connection Errors

**Error Message**:
```
Could not connect to database
```

**Solution**:
1. Ensure PostgreSQL plugin is added to your Railway project
2. Verify `DATABASE_URL` is automatically set
3. Check database service is running in Railway dashboard

### Issue 6: Application Won't Start

**Check the logs for specific errors**:

1. **Port Binding**: Railway automatically sets `$PORT`, no configuration needed
2. **Missing Dependencies**: Check `requirements.txt` is complete
3. **Import Errors**: Verify all Python packages are installed

---

## Production Checklist

Before going live, verify:

### Security
- [ ] `ANTHROPIC_API_KEY` is set and valid
- [ ] `SECRET_KEY` is set to a secure random value
- [ ] `DEBUG=false` (or omitted)
- [ ] `ALLOWED_ORIGINS` includes only your trusted domains
- [ ] No secrets are committed to version control

### Configuration
- [ ] `LOG_LEVEL=INFO` (or `WARNING` for production)
- [ ] Database (PostgreSQL) is provisioned and connected
- [ ] Redis is provisioned (if using caching)
- [ ] All required environment variables are set

### Testing
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Root endpoint returns service information
- [ ] Agents list endpoint works: `/api/v1/agents/list`
- [ ] Frontend can connect to backend (no CORS errors)
- [ ] API key validation works (check startup logs)

### Monitoring
- [ ] Set up Railway monitoring and alerts
- [ ] Configure log retention and rotation
- [ ] Set up uptime monitoring (e.g., UptimeRobot)
- [ ] Monitor Anthropic API usage and limits

### Documentation
- [ ] Update frontend `NEXT_PUBLIC_API_URL` to Railway URL
- [ ] Document any custom environment variables
- [ ] Create runbook for common operations
- [ ] Document rollback procedure

---

## Next Steps

After successful deployment:

1. **Configure Custom Domain** (Optional):
   - Go to Railway **Settings** → **Domains**
   - Add your custom domain
   - Update DNS records as instructed

2. **Set Up Monitoring**:
   - Use Railway's built-in monitoring
   - Consider external monitoring (UptimeRobot, Pingdom)
   - Set up alerts for downtime

3. **Configure Frontend**:
   - Update frontend environment variables:
     ```
     NEXT_PUBLIC_API_URL=https://your-service.railway.app
     ```
   - Redeploy frontend on Vercel

4. **Test End-to-End**:
   - Create a test meta-analysis
   - Verify all agent interactions work
   - Test all API endpoints

---

## Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **Anthropic Docs**: [docs.anthropic.com](https://docs.anthropic.com)
- **Project Issues**: [GitHub Issues](https://github.com/yourusername/meta-analysis-tool/issues)

---

## Quick Reference: Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | - | Anthropic API key (format: `sk-ant-...`) |
| `SECRET_KEY` | ✅ Yes | - | JWT signing key (generate random) |
| `DEBUG` | ❌ No | `false` | Debug mode (set to `false` in production) |
| `LOG_LEVEL` | ❌ No | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `ALLOWED_ORIGINS` | ⚠️ Recommended | localhost | Comma-separated CORS origins |
| `DATABASE_URL` | ⚠️ Auto-set | - | PostgreSQL URL (auto-set by Railway) |
| `REDIS_URL` | ❌ No | - | Redis URL (auto-set if using Railway Redis) |
| `OPENAI_API_KEY` | ❌ No | - | OpenAI API key (if using OpenAI models) |
| `PUBMED_API_KEY` | ❌ No | - | PubMed API key (for literature search) |
| `PUBMED_EMAIL` | ❌ No | - | Email for PubMed API |

---

**Last Updated**: 2025-11-04
**Version**: 1.0.0
**Author**: Meta-Analysis Research Platform Team
