# Production Deployment Checklist
## Meta-Analysis Research Platform

**Version:** 1.0
**Last Updated:** November 4, 2025

---

## Pre-Deployment Checklist

### Code Quality

- [ ] All tests passing (`pytest`)
- [ ] Code linting clean (`flake8`, `black`, `mypy`)
- [ ] No security vulnerabilities (`bandit`, `safety`)
- [ ] No secrets in code (check with `trufflehog`)
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped

### Infrastructure Setup

- [ ] Railway account created
- [ ] Vercel account created
- [ ] GitHub repository created
- [ ] Sentry account created (optional)
- [ ] Domain name purchased (optional)

### Environment Configuration

- [ ] `.env` file created (DO NOT commit!)
- [ ] All required environment variables set
- [ ] API keys validated
- [ ] Secret key generated (32+ characters)
- [ ] CORS origins configured
- [ ] Database credentials secure

### Railway Services

- [ ] Backend API service created
- [ ] Worker service created (if using Celery)
- [ ] PostgreSQL database provisioned
- [ ] Redis cache provisioned
- [ ] Environment variables set in Railway
- [ ] Resource limits configured

### Database

- [ ] Database schema created
- [ ] Migrations prepared (`alembic`)
- [ ] Seed data ready (optional)
- [ ] Backup strategy in place
- [ ] Indexes created
- [ ] Connection pooling configured

### Monitoring & Observability

- [ ] Sentry DSN configured
- [ ] Logging configured (structured JSON)
- [ ] Metrics endpoint enabled (`/metrics`)
- [ ] Health check endpoint tested (`/health`)
- [ ] Uptime monitoring configured
- [ ] Alert rules configured

### Security

- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] Rate limiting enabled
- [ ] API authentication implemented
- [ ] Secrets in environment variables only
- [ ] Database encryption enabled
- [ ] Backup encryption enabled

### Performance

- [ ] Database queries optimized
- [ ] Caching strategy implemented
- [ ] CDN configured (Vercel)
- [ ] Connection pooling enabled
- [ ] Worker concurrency tuned
- [ ] Resource limits set

---

## Deployment Steps

### Phase 1: Railway Backend Setup

#### 1.1 Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway init

# Link to GitHub repository
railway link
```

#### 1.2 Provision Services

```bash
# Add PostgreSQL
railway add --service postgresql

# Add Redis
railway add --service redis

# Verify services
railway status
```

#### 1.3 Configure Environment Variables

```bash
# Set required variables
railway variables set ANTHROPIC_API_KEY="sk-ant-..."
railway variables set SECRET_KEY="$(openssl rand -hex 32)"
railway variables set DEBUG="false"
railway variables set LOG_LEVEL="INFO"

# Set optional variables
railway variables set SENTRY_DSN="https://...@sentry.io/..."
railway variables set ALLOWED_ORIGINS="https://your-app.vercel.app"

# Verify variables
railway variables list
```

#### 1.4 Deploy Backend

```bash
# Deploy from local
railway up --service backend

# Or deploy from GitHub (preferred)
# Push to main branch, Railway auto-deploys

# Check deployment status
railway status

# View logs
railway logs --service backend
```

#### 1.5 Run Database Migrations

```bash
# Run migrations
railway run --service backend alembic upgrade head

# Verify
railway run --service backend psql -c "\dt"
```

#### 1.6 Test Backend

```bash
# Get backend URL
railway domain --service backend

# Test health endpoint
curl https://your-backend.railway.app/health

# Expected response
# {"status": "healthy"}
```

### Phase 2: Vercel Frontend Setup

#### 2.1 Install Vercel CLI

```bash
npm install -g vercel
```

#### 2.2 Configure Frontend

```bash
cd frontend

# Create .env.production
cat > .env.production << EOF
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
EOF
```

#### 2.3 Deploy to Vercel

```bash
# Link project
vercel link

# Set environment variables
vercel env add NEXT_PUBLIC_API_URL production

# Deploy
vercel --prod

# Get deployment URL
vercel inspect
```

#### 2.4 Test Frontend

```bash
# Open in browser
open https://your-app.vercel.app

# Test API connectivity
# Should see data from backend
```

### Phase 3: CI/CD Setup

#### 3.1 Configure GitHub Secrets

Go to GitHub repo → Settings → Secrets → Actions:

```
ANTHROPIC_API_KEY=sk-ant-...
RAILWAY_TOKEN=<from railway.com/account/tokens>
VERCEL_TOKEN=<from vercel.com/account/tokens>
VERCEL_ORG_ID=<from vercel.json>
VERCEL_PROJECT_ID=<from vercel.json>
SENTRY_DSN=https://...@sentry.io/...
SLACK_WEBHOOK=https://hooks.slack.com/...
```

#### 3.2 Enable GitHub Actions

```bash
# Actions should auto-enable when you push .github/workflows/

# Verify workflows
# Go to GitHub → Actions tab
# Should see "Deploy to Production" workflow

# Trigger manual deployment
# Actions → Deploy to Production → Run workflow
```

#### 3.3 Test CI/CD Pipeline

```bash
# Create test branch
git checkout -b test-deployment

# Make small change
echo "# Test" >> README.md

# Commit and push
git add .
git commit -m "test: CI/CD pipeline"
git push origin test-deployment

# Create pull request
# Should see tests running in PR

# Merge to main
# Should trigger production deployment
```

### Phase 4: Monitoring Setup

#### 4.1 Configure Sentry

```bash
# Login to Sentry
open https://sentry.io

# Create project
# - Platform: Python / FastAPI
# - Copy DSN

# Add to Railway
railway variables set SENTRY_DSN="https://...@sentry.io/..."

# Test error reporting
railway run python -c "from app.monitoring import capture_exception; capture_exception(Exception('test'))"

# Check Sentry dashboard
# Should see test error
```

#### 4.2 Configure Uptime Monitoring

```bash
# Option 1: UptimeRobot (free)
# 1. Sign up at uptimerobot.com
# 2. Add monitor:
#    - Type: HTTP(s)
#    - URL: https://your-backend.railway.app/health
#    - Interval: 5 minutes
# 3. Add alert contacts (email, Slack)

# Option 2: Better Stack
# 1. Sign up at betterstack.com
# 2. Create monitor
# 3. Configure alerts
```

#### 4.3 Set Up Grafana (Optional)

```bash
# For local monitoring
docker-compose -f docker-compose.prod.yml up grafana prometheus

# Access Grafana
open http://localhost:3001

# Login: admin / (check .env for password)

# Import dashboards
# - Go to Dashboards → Import
# - Upload config/grafana/dashboards/*.json
```

### Phase 5: Backups

#### 5.1 Test Backup Script

```bash
# Run manual backup
./scripts/backup-db.sh production

# Verify backup created
ls -lh backups/

# Test backup integrity
gunzip -t backups/production_backup_*.sql.gz
```

#### 5.2 Schedule Automated Backups

```bash
# Option 1: Railway Cron (if available)
# Add to railway.toml
[build]
cronJobs = [
  {schedule = "0 2 * * *", command = "./scripts/backup-db.sh production"}
]

# Option 2: External Cron (GitHub Actions)
# .github/workflows/backup.yml
name: Daily Backup
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily
jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/backup-db.sh production

# Option 3: Railway built-in backups
# Railway → PostgreSQL → Backups → Enable
```

#### 5.3 Test Restore

```bash
# NEVER test on production!
# Test on staging or local

# Restore to local
./scripts/restore-db.sh backups/production_backup_*.sql.gz local

# Verify data
psql $DATABASE_URL -c "SELECT COUNT(*) FROM papers;"
```

### Phase 6: Performance Testing

#### 6.1 Load Testing

```bash
# Install load testing tool
pip install locust

# Run load test
locust -f tests/load/locustfile.py \
  --host=https://your-backend.railway.app \
  --users=100 \
  --spawn-rate=10

# Access web UI
open http://localhost:8089

# Run test for 5 minutes
# Monitor:
# - Response times
# - Error rate
# - Railway metrics
```

#### 6.2 Database Performance

```bash
# Check slow queries
railway run psql -c "
  SELECT query, calls, mean_exec_time
  FROM pg_stat_statements
  ORDER BY mean_exec_time DESC
  LIMIT 10;
"

# Add missing indexes if needed
railway run psql -c "
  CREATE INDEX idx_papers_created_at ON papers(created_at);
"
```

#### 6.3 API Performance

```bash
# Test endpoints
curl -w "@curl-format.txt" https://your-backend.railway.app/api/v1/health

# curl-format.txt:
#     time_namelookup:  %{time_namelookup}s\n
#        time_connect:  %{time_connect}s\n
#     time_appconnect:  %{time_appconnect}s\n
#    time_pretransfer:  %{time_pretransfer}s\n
#       time_redirect:  %{time_redirect}s\n
#  time_starttransfer:  %{time_starttransfer}s\n
#                     ----------\n
#          time_total:  %{time_total}s\n
```

---

## Post-Deployment Checklist

### Verification

- [ ] Backend health check responding
- [ ] Frontend loading correctly
- [ ] Database accessible
- [ ] Redis cache working
- [ ] API endpoints responding
- [ ] Authentication working
- [ ] Agent workflows executing
- [ ] Background tasks processing
- [ ] Logs being generated
- [ ] Metrics being collected
- [ ] Errors tracked in Sentry
- [ ] Backups running

### Performance

- [ ] API latency < 2 seconds (P95)
- [ ] Error rate < 1%
- [ ] Database query time < 100ms (P95)
- [ ] Cache hit rate > 80%
- [ ] Memory usage < 70%
- [ ] CPU usage < 60%

### Security

- [ ] HTTPS working
- [ ] HTTP redirects to HTTPS
- [ ] Security headers present
- [ ] CORS properly configured
- [ ] No secrets exposed in logs
- [ ] No secrets in error messages
- [ ] Rate limiting working

### Monitoring

- [ ] Uptime monitor active
- [ ] Alerts configured
- [ ] Sentry receiving errors
- [ ] Metrics endpoint accessible
- [ ] Dashboards showing data
- [ ] On-call rotation set up

### Documentation

- [ ] README updated
- [ ] Architecture diagram current
- [ ] API documentation current
- [ ] Deployment guide current
- [ ] Runbooks current
- [ ] Contact information current

---

## Rollback Procedures

### If Deployment Fails

#### Option 1: Railway Rollback

```bash
# List recent deployments
railway deployments --service backend

# Rollback to previous version
railway rollback --service backend --deployment-id <id>

# Verify
railway logs --service backend
```

#### Option 2: Git Revert

```bash
# Revert commit
git revert HEAD
git push origin main

# Railway auto-deploys the revert
```

#### Option 3: Redeploy Previous Tag

```bash
# Tag known good version
git tag v1.0.0 <good-commit-hash>
git push origin v1.0.0

# Deploy tag
railway up --service backend --tag v1.0.0
```

### If Database Migration Fails

```bash
# Rollback migration
railway run --service backend alembic downgrade -1

# Restore from backup (if needed)
./scripts/restore-db.sh backups/pre-deploy-backup.sql.gz production

# Fix migration, redeploy
```

---

## Maintenance Mode

### Enable Maintenance Mode

```bash
# Set maintenance flag
railway variables set MAINTENANCE_MODE=true

# Restart service
railway restart --service backend

# Users will see maintenance page
```

### Disable Maintenance Mode

```bash
# Unset maintenance flag
railway variables set MAINTENANCE_MODE=false

# Restart service
railway restart --service backend
```

---

## Cost Monitoring

### Phase 0-1 Budget: < $100/month

| Service | Expected Cost |
|---------|--------------|
| Railway API | $20 |
| Railway PostgreSQL | $5 |
| Railway Redis | $5 |
| Vercel | $0 |
| Claude API | $50-70 |
| **Total** | **$80-100** |

### Set Up Cost Alerts

```bash
# Railway billing alerts
railway billing alerts \
  --threshold 100 \
  --email team@example.com

# Check current usage
railway usage

# View billing
railway billing
```

### Monitor Claude API Costs

```bash
# Check Anthropic dashboard
open https://console.anthropic.com/

# Set up budget alerts in Anthropic console

# Monitor token usage in logs
railway logs | grep "tokens="
```

---

## Troubleshooting

### Deployment Fails

```bash
# Check build logs
railway logs --service backend --deployment <id>

# Common issues:
# - Missing environment variables
# - Failed dependency installation
# - Database connection failed
# - Docker build errors

# Debug locally
docker build -t test -f backend/Dockerfile backend/
docker run test
```

### Health Check Fails

```bash
# Check service status
railway status --service backend

# Check logs
railway logs --service backend --tail 100

# Test locally
curl https://your-backend.railway.app/health

# Common issues:
# - Service not started
# - Port binding error
# - Database connection failed
```

### Database Migration Fails

```bash
# Check migration status
railway run --service backend alembic current

# Check migration history
railway run --service backend alembic history

# Manually run migration
railway run --service backend alembic upgrade head

# If fails, check logs for SQL errors
```

---

## Success Criteria

Deployment is successful when:

1. ✅ All health checks passing
2. ✅ API responding < 2s
3. ✅ Error rate < 1%
4. ✅ Database migrations complete
5. ✅ Frontend loading correctly
6. ✅ Monitoring active
7. ✅ Backups configured
8. ✅ Documentation updated

---

## Next Steps After Deployment

1. **Monitor for 24 hours** - Watch for errors, performance issues
2. **Test with real users** - Beta testing with small group
3. **Optimize performance** - Based on real usage data
4. **Plan scaling** - Prepare for increased load
5. **Document learnings** - Update runbooks with issues encountered
6. **Schedule reviews** - Monthly infrastructure reviews

---

**Last Updated:** November 4, 2025
**Version:** 1.0
**Next Review:** December 4, 2025
