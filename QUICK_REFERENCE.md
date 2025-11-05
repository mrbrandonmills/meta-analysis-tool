# Quick Reference Guide
## Meta-Analysis Research Platform - DevOps

**Version:** 1.0 | **Last Updated:** November 4, 2025

---

## 🚀 Quick Start

### Local Development
```bash
# 1. Clone and setup
git clone <repo-url>
cd meta-analysis-tool
cp .env.example .env
# Edit .env with your API keys

# 2. Start services
docker-compose up

# 3. Access
# API: http://localhost:8000
# Frontend: http://localhost:3000
# Flower: http://localhost:5555
```

### Production Deployment
```bash
# Railway
railway login
railway up

# Vercel
cd frontend && vercel --prod
```

---

## 📊 Essential Commands

### Railway

```bash
# View logs
railway logs --service backend

# Check status
railway status

# Restart service
railway restart --service backend

# Deploy
railway up

# Rollback
railway rollback --service backend

# Environment variables
railway variables list
railway variables set KEY=value
railway variables get KEY

# Run command
railway run <command>

# Database
railway run psql
railway run psql -c "SELECT COUNT(*) FROM papers;"
```

### Docker Compose

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs --tail=100

# Restart service
docker-compose restart backend

# Stop all
docker-compose down

# Clean up volumes
docker-compose down -v

# Rebuild
docker-compose up --build
```

### Database

```bash
# Backup
./scripts/backup-db.sh production

# Restore
./scripts/restore-db.sh backup.sql.gz local

# Connect
railway run psql
# or locally:
psql postgresql://postgres:postgres@localhost:5432/meta_analysis

# Migrations
railway run alembic upgrade head
railway run alembic downgrade -1
railway run alembic current
```

---

## 🔍 Monitoring

### Health Checks

```bash
# API health
curl https://your-api.railway.app/health
# Returns: {"status": "healthy"}

# Detailed health
curl https://your-api.railway.app/health/detailed
# Returns component status

# Metrics
curl https://your-api.railway.app/metrics
# Prometheus format
```

### Logs

```bash
# Railway logs
railway logs --service backend
railway logs --service backend --tail 100
railway logs --service backend --follow

# Docker logs
docker-compose logs -f backend
docker-compose logs --tail=100 backend

# Search logs
railway logs | grep ERROR
cat logs/app.log | jq 'select(.level == "ERROR")'
```

### Metrics & Dashboards

```bash
# Grafana (local)
open http://localhost:3001
# Login: admin / (from .env)

# Flower (Celery monitoring)
open http://localhost:5555

# Prometheus (local)
open http://localhost:9090

# Sentry (errors)
open https://sentry.io
```

---

## 🚨 Troubleshooting

### API Not Responding

```bash
# 1. Check status
railway status --service backend

# 2. Check logs
railway logs --service backend --tail 100

# 3. Restart
railway restart --service backend

# 4. Check health
curl https://your-api.railway.app/health
```

### Database Issues

```bash
# Check connection
railway run psql -c "SELECT 1;"

# Check connections
railway run psql -c "SELECT count(*) FROM pg_stat_activity;"

# Kill long queries
railway run psql -c "SELECT pg_terminate_backend(PID);"

# Vacuum
railway run psql -c "VACUUM ANALYZE;"
```

### Worker Not Processing

```bash
# Check logs
railway logs --service worker

# Restart workers
railway restart --service worker

# Purge queue
railway run celery -A app.tasks.celery_app purge

# Check queue
railway run redis-cli -u $REDIS_URL llen celery
```

### High Memory/CPU

```bash
# Check metrics
railway metrics --service backend

# Scale up
# Edit railway.toml
[deploy.resources]
memoryLimit = 2048
cpuLimit = 2.0

# Redeploy
railway up
```

---

## 🔐 Security

### Environment Variables

```bash
# Set in Railway
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# View (local)
cat .env | grep -v "^#"

# Generate secret
openssl rand -hex 32
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Security Checks

```bash
# Check for secrets in code
grep -r "sk-ant-" . --exclude-dir=node_modules --exclude-dir=.git

# Vulnerability scan
pip audit
npm audit

# Docker scan
trivy image meta-analysis-backend:latest
```

---

## 📈 Performance

### Database Optimization

```bash
# Slow queries
railway run psql -c "
  SELECT query, calls, mean_exec_time
  FROM pg_stat_statements
  ORDER BY mean_exec_time DESC
  LIMIT 10;
"

# Add index
railway run psql -c "CREATE INDEX idx_name ON table(column);"

# Analyze
railway run psql -c "ANALYZE;"
```

### Cache Operations

```bash
# Check Redis
railway run redis-cli -u $REDIS_URL INFO stats

# Clear cache
railway run redis-cli -u $REDIS_URL FLUSHDB

# Check key
railway run redis-cli -u $REDIS_URL GET key

# Check TTL
railway run redis-cli -u $REDIS_URL TTL key
```

---

## 🔄 Deployment

### Standard Deployment

```bash
# 1. Run tests
pytest

# 2. Commit and push
git add .
git commit -m "feat: new feature"
git push origin main

# 3. GitHub Actions deploys automatically

# 4. Verify
curl https://your-api.railway.app/health
```

### Manual Deployment

```bash
# Railway
railway up --service backend

# Vercel
cd frontend
vercel --prod

# Run migrations
railway run alembic upgrade head
```

### Rollback

```bash
# Railway
railway rollback --service backend

# Git revert
git revert HEAD
git push origin main

# Emergency: restore DB
./scripts/restore-db.sh backup.sql.gz production
```

---

## 💰 Cost Monitoring

### Check Costs

```bash
# Railway usage
railway usage
railway billing

# Set alerts
railway billing alerts --threshold 100 --email team@example.com

# Claude API usage
# Check: https://console.anthropic.com/
```

### Cost Optimization

```bash
# Scale down in off-hours
railway up --service worker --replicas 1

# Check resource usage
railway metrics --service backend

# Optimize queries (reduce DB costs)
railway run psql -c "SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;"
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/test_agents.py

# Integration tests
pytest tests/integration/

# Load testing
locust -f tests/load/locustfile.py --host=https://your-api.railway.app
```

---

## 📦 Backups

### Create Backup

```bash
# Production
./scripts/backup-db.sh production

# Staging
./scripts/backup-db.sh staging

# Local
./scripts/backup-db.sh local

# List backups
ls -lh backups/
```

### Restore Backup

```bash
# To local
./scripts/restore-db.sh backups/production_backup_20250104.sql.gz local

# To staging
./scripts/restore-db.sh backups/production_backup_20250104.sql.gz staging

# To production (CAREFUL!)
./scripts/restore-db.sh backups/production_backup_20250104.sql.gz production
```

---

## 🔗 Useful URLs

### Production
- API: https://your-backend.railway.app
- Frontend: https://your-app.vercel.app
- Docs: https://your-backend.railway.app/docs
- Health: https://your-backend.railway.app/health
- Metrics: https://your-backend.railway.app/metrics

### Dashboards
- Railway: https://railway.app/dashboard
- Vercel: https://vercel.com/dashboard
- Sentry: https://sentry.io
- Grafana (local): http://localhost:3001
- Flower (local): http://localhost:5555

### Documentation
- Anthropic: https://docs.anthropic.com
- Railway: https://docs.railway.app
- Vercel: https://vercel.com/docs
- FastAPI: https://fastapi.tiangolo.com

---

## 📚 Documentation

| Topic | Document |
|-------|----------|
| Complete guide | [INFRASTRUCTURE.md](./INFRASTRUCTURE.md) |
| Monitoring | [MONITORING.md](./MONITORING.md) |
| Incidents | [INCIDENT_RESPONSE.md](./INCIDENT_RESPONSE.md) |
| Deployment | [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) |
| Overview | [INFRASTRUCTURE_README.md](./INFRASTRUCTURE_README.md) |
| Summary | [DEVOPS_SUMMARY.md](./DEVOPS_SUMMARY.md) |

---

## 🆘 Emergency Contacts

### On-Call
- Check rotation in [INCIDENT_RESPONSE.md](./INCIDENT_RESPONSE.md)

### Support
- Railway: support@railway.app
- Vercel: support@vercel.com
- Anthropic: support@anthropic.com
- Sentry: support@sentry.io

---

## ⚡ Hot Keys (Common Operations)

```bash
# Start local dev
dc up

# View API logs
rw logs

# Deploy
rw up

# Backup DB
./scripts/backup-db.sh production

# Check health
curl $(rw domain)/health

# Restart API
rw restart --service backend

# SSH to container
rw run bash

# Check DB
rw run psql

# View metrics
curl $(rw domain)/metrics
```

**Aliases (add to ~/.bashrc):**
```bash
alias dc='docker-compose'
alias rw='railway'
alias dclogs='docker-compose logs -f'
alias rwlogs='railway logs --follow'
```

---

**Need more help?** See full documentation in respective files above.

**Last Updated:** November 4, 2025
