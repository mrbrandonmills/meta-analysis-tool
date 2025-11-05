# Infrastructure Documentation
## Meta-Analysis Research Platform - Production Infrastructure

**Version:** 1.0
**Last Updated:** November 4, 2025
**Maintainer:** DevOps Team

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Deployment Environments](#deployment-environments)
4. [Local Development](#local-development)
5. [Production Deployment](#production-deployment)
6. [Monitoring & Observability](#monitoring--observability)
7. [Backup & Recovery](#backup--recovery)
8. [Scaling Strategy](#scaling-strategy)
9. [Security](#security)
10. [Cost Management](#cost-management)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The Meta-Analysis Research Platform runs on a cloud-native architecture with the following components:

- **Backend API**: FastAPI application (Railway)
- **Worker Pool**: Celery workers for background jobs (Railway)
- **Frontend**: Next.js application (Vercel)
- **Database**: PostgreSQL 15 (Railway Managed)
- **Cache/Queue**: Redis 7 (Railway Managed)
- **CDN**: Vercel Edge Network
- **Error Tracking**: Sentry
- **Monitoring**: Prometheus + Grafana

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Runtime | Python | 3.11 | Backend API & Workers |
| Web Framework | FastAPI | 0.104+ | REST API |
| Task Queue | Celery | 5.3+ | Background jobs |
| Database | PostgreSQL | 15 | Data persistence |
| Cache | Redis | 7 | Caching & message broker |
| Frontend | Next.js | 14 | User interface |
| Containerization | Docker | 24+ | Container runtime |
| Orchestration | Docker Compose | 3.8+ | Local development |
| Deployment | Railway | - | Cloud hosting |
| CDN | Vercel | - | Frontend hosting |

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Users / Browsers                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌───────────────────┐     ┌──────────────────┐
        │  Vercel CDN       │     │  Railway API     │
        │  (Frontend)       │     │  (Backend)       │
        │                   │     │                  │
        │  Next.js App      │────▶│  FastAPI         │
        │  Static Assets    │     │  + Uvicorn       │
        └───────────────────┘     └──────────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
                    ▼                       ▼                       ▼
        ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
        │  PostgreSQL DB   │   │  Redis Cache     │   │  Celery Workers  │
        │  (Managed)       │   │  (Managed)       │   │  (Railway)       │
        │                  │   │                  │   │                  │
        │  Data Storage    │   │  Cache + Queue   │   │  Background Jobs │
        └──────────────────┘   └──────────────────┘   └──────────────────┘
                                                                  │
                                                                  ▼
                                                       ┌──────────────────┐
                                                       │  External APIs   │
                                                       │  - Claude AI     │
                                                       │  - PubMed        │
                                                       │  - arXiv         │
                                                       └──────────────────┘
```

### Component Responsibilities

#### Backend API (Railway)
- RESTful API endpoints
- Authentication & authorization
- Request validation
- Agent orchestration
- Real-time updates (SSE)
- Database queries

#### Celery Workers (Railway)
- Data extraction from PDFs
- Statistical analysis (R integration)
- Network analysis (reviewer matching)
- LLM API calls (Claude)
- Long-running workflows

#### PostgreSQL Database
- User accounts
- Projects & workflows
- Research papers metadata
- Researcher profiles
- Agent decisions (audit trail)

#### Redis Cache
- API response caching
- Session storage
- Celery message broker
- Celery result backend
- Rate limiting counters

#### Frontend (Vercel)
- User interface (React)
- Server-side rendering
- Static asset serving
- API client
- Real-time updates (SSE client)

---

## Deployment Environments

### Environment Matrix

| Environment | Purpose | URL | Database | Deployment |
|------------|---------|-----|----------|------------|
| **Local** | Development | localhost:8000 | Docker PostgreSQL | docker-compose up |
| **Staging** | Testing | staging.railway.app | Railway PostgreSQL | Auto-deploy from `develop` |
| **Production** | Live | meta-analysis-api.railway.app | Railway PostgreSQL | Auto-deploy from `main` |

### Environment Variables

#### Required (All Environments)
```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...
SECRET_KEY=<random-secret-key>

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/0
```

#### Optional
```bash
# AI APIs
OPENAI_API_KEY=sk-...

# Research APIs
PUBMED_API_KEY=...
PUBMED_EMAIL=...

# Monitoring
SENTRY_DSN=https://...
PROMETHEUS_ENABLED=true

# Feature Flags
ENABLE_CELERY=true
ENABLE_RATE_LIMITING=true
```

---

## Local Development

### Prerequisites

```bash
# Required
- Docker Desktop 24+
- Docker Compose 3.8+
- Git

# Optional (for native development)
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
```

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/meta-analysis-tool.git
cd meta-analysis-tool

# 2. Create .env file
cp .env.example .env
# Edit .env with your API keys

# 3. Start all services
docker-compose up

# Services will be available at:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - Flower (Celery): http://localhost:5555
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### Development Workflow

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f worker

# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d meta_analysis

# Access Redis CLI
docker-compose exec redis redis-cli

# Run tests
docker-compose exec backend pytest

# Stop services
docker-compose down

# Clean up (including volumes)
docker-compose down -v
```

### Production-Like Local Testing

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up

# This includes:
# - Production Docker images
# - Nginx reverse proxy
# - Prometheus metrics
# - Grafana dashboards
# - Production environment variables
```

---

## Production Deployment

### Railway Deployment

#### Initial Setup

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Create project
railway init

# 4. Add services
railway add --service postgresql
railway add --service redis

# 5. Set environment variables
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set SECRET_KEY=<random-key>
railway variables set SENTRY_DSN=https://...

# 6. Deploy
railway up
```

#### Continuous Deployment

The platform automatically deploys via GitHub Actions on push to `main` branch.

**Workflow:**
1. Push to `main` branch
2. GitHub Actions runs tests
3. Builds Docker images
4. Deploys to Railway
5. Runs database migrations
6. Deploys frontend to Vercel
7. Runs smoke tests
8. Sends Slack notification

**Manual Deployment:**
```bash
# Deploy backend
railway up --service backend

# Deploy worker
railway up --service worker

# Run migrations
railway run alembic upgrade head
```

### Vercel Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Link project
cd frontend
vercel link

# Deploy
vercel --prod
```

#### Environment Variables (Vercel)
```bash
NEXT_PUBLIC_API_URL=https://meta-analysis-api.railway.app
```

---

## Monitoring & Observability

### Logging

#### Structured JSON Logging

All logs are output in JSON format for easy parsing:

```json
{
  "timestamp": "2025-11-04T12:00:00.000Z",
  "level": "INFO",
  "logger": "app.agents.search",
  "function": "search_papers",
  "line": 42,
  "message": "Searching PubMed for query",
  "request_id": "abc123",
  "extra": {
    "query": "machine learning meta-analysis",
    "database": "pubmed"
  }
}
```

#### Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General informational messages
- **WARNING**: Warning messages (potential issues)
- **ERROR**: Error messages (recoverable errors)
- **CRITICAL**: Critical errors (system failures)

#### Log Locations

- **Local**: `logs/app.log`, `logs/error.log`
- **Production**: Railway logs (view with `railway logs`)
- **Centralized**: Sentry (errors only)

#### Viewing Logs

```bash
# Railway logs
railway logs --service backend

# Docker logs
docker-compose logs -f backend

# Tail error log
tail -f logs/error.log

# Parse JSON logs
cat logs/app.log | jq '.level, .message'
```

### Metrics

#### Prometheus Metrics Endpoint

Metrics are exposed at `/metrics` endpoint in Prometheus format:

```
# Application Metrics
http_requests_total{method="GET",path="/api/v1/meta-analysis",status="200"} 1523
http_request_duration_seconds_bucket{le="0.1"} 1420
agent_executions_total{agent="search",status="success"} 432
llm_api_calls_total{provider="anthropic",model="claude-3-sonnet"} 156
database_queries_total{type="select"} 8234

# System Metrics
active_workflows 12
queue_size{queue="celery"} 5
```

#### Grafana Dashboards

Access Grafana at http://localhost:3001 (local) or production URL.

**Pre-configured dashboards:**
1. **System Overview**: CPU, memory, request rate
2. **API Performance**: Latency, error rate, throughput
3. **Agent Activity**: Agent executions, LLM usage
4. **Database Health**: Connection pool, query latency
5. **Queue Status**: Celery tasks, queue depth

### Error Tracking (Sentry)

#### Setup

```bash
# Set Sentry DSN
export SENTRY_DSN=https://xxx@sentry.io/yyy

# Errors are automatically captured
```

#### What Gets Tracked

- Unhandled exceptions
- Agent failures
- API errors (4xx, 5xx)
- Database errors
- LLM API failures

#### Sentry Dashboard

- View errors at https://sentry.io
- Filter by environment (production, staging)
- See stack traces, context, breadcrumbs
- Track error frequency trends

### Health Checks

```bash
# API health check
curl https://meta-analysis-api.railway.app/health

# Expected response
{
  "status": "healthy"
}

# Detailed health (includes DB, Redis)
curl https://meta-analysis-api.railway.app/health/detailed
```

### Uptime Monitoring

**Recommended tools:**
- UptimeRobot (free tier)
- Pingdom
- Better Stack

**Monitor these endpoints:**
- `/health` - API health
- `https://meta-analysis-tool.vercel.app` - Frontend

**Alert on:**
- HTTP 5xx errors
- Response time > 5 seconds
- Downtime > 1 minute

---

## Backup & Recovery

### Automated Backups

#### Daily Database Backups

```bash
# Run backup script
./scripts/backup-db.sh production

# Backups stored in ./backups/
# Retention: 30 days
# Compression: gzip
```

#### Backup Schedule (Production)

```bash
# Add to crontab
0 2 * * * /path/to/meta-analysis-tool/scripts/backup-db.sh production

# Or use Railway cron (if available)
```

#### Backup Verification

```bash
# Verify backup integrity
gunzip -t backups/production_backup_20250104_120000.sql.gz

# Test restore to staging
./scripts/restore-db.sh backups/production_backup_20250104_120000.sql.gz staging
```

### Manual Backup

```bash
# Backup production database
railway run -s postgresql pg_dump > backup.sql

# Compress
gzip backup.sql
```

### Restore Procedures

#### Standard Restore

```bash
# Restore to local environment
./scripts/restore-db.sh backups/production_backup_20250104_120000.sql.gz local

# Restore to staging
./scripts/restore-db.sh backups/production_backup_20250104_120000.sql.gz staging
```

#### Emergency Production Restore

```bash
# ⚠️ WARNING: This will overwrite production data!

# 1. Create current backup first
./scripts/backup-db.sh production

# 2. Restore from backup
./scripts/restore-db.sh backups/production_backup_20250103_120000.sql.gz production

# 3. Verify data
railway run psql -c "SELECT COUNT(*) FROM papers;"

# 4. Run migrations (if needed)
railway run alembic upgrade head
```

### Point-in-Time Recovery

Railway PostgreSQL supports point-in-time recovery (PITR):

```bash
# Restore to specific timestamp
railway database restore --timestamp "2025-11-04 12:00:00"
```

### Disaster Recovery Plan

**RTO (Recovery Time Objective):** 4 hours
**RPO (Recovery Point Objective):** 24 hours

**Scenarios:**

1. **Database Corruption**
   - Restore from last backup (< 24 hours old)
   - Apply transaction logs if available
   - Verify data integrity
   - Resume operations

2. **Complete Service Failure**
   - Deploy to new Railway project
   - Restore database from backup
   - Update DNS/environment variables
   - Test all endpoints

3. **Data Loss (Partial)**
   - Identify lost data from audit logs
   - Restore specific tables/rows
   - Merge with current data
   - Verify consistency

---

## Scaling Strategy

### Horizontal Scaling

#### API Servers

```bash
# Railway automatically scales based on load
# Or manually set replicas in railway.toml

[deploy]
numReplicas = 3  # 3 API servers
```

#### Celery Workers

```bash
# Scale workers based on queue depth
# In docker-compose.prod.yml

worker:
  deploy:
    replicas: 5  # 5 worker instances
```

#### Auto-Scaling Rules

**Trigger Scale-Up When:**
- CPU > 70% for 5 minutes
- Memory > 80% for 5 minutes
- Queue depth > 100 tasks
- API latency > 2 seconds

**Trigger Scale-Down When:**
- CPU < 30% for 15 minutes
- Queue depth < 10 tasks

### Vertical Scaling

#### Resource Limits

**Current (Phase 0-1):**
- API: 1 GB RAM, 1 vCPU
- Worker: 2 GB RAM, 1 vCPU
- Database: Railway Starter (1 GB)
- Redis: Railway Starter (256 MB)

**Phase 2-3:**
- API: 2 GB RAM, 2 vCPU
- Worker: 4 GB RAM, 2 vCPU
- Database: Railway Pro (8 GB)
- Redis: Railway Pro (1 GB)

**Phase 4-5:**
- API: 4 GB RAM, 4 vCPU
- Worker: 8 GB RAM, 4 vCPU
- Database: Railway Pro (32 GB)
- Redis: Railway Pro (4 GB)

### Database Optimization

#### Connection Pooling

```python
# SQLAlchemy settings
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_POOL_PRE_PING = True
```

#### Indexing Strategy

```sql
-- Essential indexes
CREATE INDEX idx_papers_doi ON papers(doi);
CREATE INDEX idx_papers_title_trgm ON papers USING gin(title gin_trgm_ops);
CREATE INDEX idx_researchers_orcid ON researchers(orcid);
CREATE INDEX idx_workflows_status ON workflows(status);
```

#### Query Optimization

- Use `SELECT` with specific columns
- Add pagination (LIMIT/OFFSET)
- Use prepared statements
- Enable query caching in Redis

### Cache Strategy

#### Redis Caching Layers

**Layer 1: API Response Cache**
```python
# Cache API responses for 5 minutes
@cache(ttl=300)
def get_papers(query: str):
    ...
```

**Layer 2: Database Query Cache**
```python
# Cache expensive DB queries for 1 hour
@cache(ttl=3600)
def get_researcher_profile(orcid: str):
    ...
```

**Layer 3: LLM Response Cache**
```python
# Cache LLM responses for 24 hours
@cache(ttl=86400)
def generate_review(manuscript_id: str):
    ...
```

#### Cache Invalidation

```python
# Invalidate on update
def update_paper(paper_id: str, data: dict):
    update_database(paper_id, data)
    cache.delete(f"paper:{paper_id}")
```

---

## Security

### Security Headers

```python
# Configured in FastAPI middleware
- Content-Security-Policy
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Strict-Transport-Security
- X-XSS-Protection
```

### HTTPS Enforcement

- Railway: Automatic HTTPS with Let's Encrypt
- Vercel: Automatic HTTPS
- All HTTP requests redirect to HTTPS

### API Security

#### Authentication

```python
# JWT token-based authentication
Authorization: Bearer <jwt-token>

# Token expiration: 30 minutes
# Refresh token: 7 days
```

#### Rate Limiting

```python
# Per-user rate limits
- Free tier: 100 requests/hour
- Pro tier: 1000 requests/hour
- Enterprise: Unlimited

# Per-endpoint limits
- /api/v1/meta-analysis/execute: 10/hour
- /api/v1/search: 100/hour
```

### Secrets Management

**Never commit secrets to Git!**

```bash
# Use Railway secrets
railway variables set ANTHROPIC_API_KEY=sk-ant-...

# Use .env file locally (in .gitignore)
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### Vulnerability Scanning

```bash
# Scan dependencies
pip audit

# Scan Docker images
trivy image meta-analysis-backend:latest

# Scan code
bandit -r backend/app
```

### CORS Configuration

```python
# Allow specific origins only
ALLOWED_ORIGINS = [
    "https://meta-analysis-tool.vercel.app",
    "https://staging.meta-analysis.com"
]
```

---

## Cost Management

### Cost Breakdown (Monthly)

#### Phase 0-1 (MVP) - Target: < $100/month

| Service | Plan | Cost |
|---------|------|------|
| Railway API | Starter | $20 |
| Railway PostgreSQL | Shared | $5 |
| Railway Redis | Shared | $5 |
| Vercel Frontend | Hobby | $0 |
| Claude API | Usage | $50-200 |
| Sentry | Developer | $0 |
| **Total** | | **$80-230** |

#### Phase 2-3 (Growth) - Target: < $300/month

| Service | Plan | Cost |
|---------|------|------|
| Railway API | Pro | $50 |
| Railway Workers | Pro | $50 |
| Railway PostgreSQL | Pro 8GB | $50 |
| Railway Redis | Pro 1GB | $20 |
| Vercel Frontend | Pro | $20 |
| Claude API | Usage | $200-500 |
| Sentry | Team | $26 |
| **Total** | | **$416-716** |

#### Phase 4-5 (Scale) - Target: < $500/month

| Service | Plan | Cost |
|---------|------|------|
| Railway API | Pro (2x) | $100 |
| Railway Workers | Pro (4x) | $200 |
| Railway PostgreSQL | Pro 32GB | $150 |
| Railway Redis | Pro 4GB | $50 |
| Vercel Frontend | Pro | $20 |
| Claude API | Usage | $500-1000 |
| Sentry | Business | $80 |
| **Total** | | **$1,100-1,600** |

### Cost Optimization

#### 1. LLM API Cost Reduction

```python
# Use cheaper models for non-critical tasks
- Claude Haiku for simple queries
- Claude Sonnet for complex analysis
- Cache LLM responses aggressively
- Implement prompt compression
```

#### 2. Database Optimization

```python
# Reduce database costs
- Archive old data (> 1 year)
- Use connection pooling
- Optimize queries
- Enable query caching
```

#### 3. Compute Optimization

```bash
# Right-size instances
- Monitor CPU/memory usage
- Scale down during low traffic
- Use spot instances for workers (if available)
```

#### 4. Bandwidth Reduction

```bash
# CDN and caching
- Use Vercel Edge CDN
- Enable gzip compression
- Serve static assets from CDN
- Cache API responses
```

### Cost Monitoring

```bash
# Railway cost dashboard
railway dashboard

# Set up billing alerts
railway billing alerts --threshold 100 --email you@example.com

# Claude API usage
# Check Anthropic dashboard: console.anthropic.com
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Symptom:** `psycopg2.OperationalError: could not connect to server`

**Solution:**
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
pg_isready -d $DATABASE_URL

# Verify Railway database is running
railway status --service postgresql
```

#### 2. Redis Connection Errors

**Symptom:** `redis.exceptions.ConnectionError`

**Solution:**
```bash
# Check REDIS_URL
echo $REDIS_URL

# Test connection
redis-cli -u $REDIS_URL ping

# Verify Railway Redis is running
railway status --service redis
```

#### 3. High Memory Usage

**Symptom:** API crashes with OOM errors

**Solution:**
```bash
# Check memory usage
railway metrics --service backend

# Reduce worker concurrency
# In Dockerfile.worker
CMD celery worker --concurrency=1  # Reduce from 2

# Increase memory limit
# In railway.toml
[deploy.resources]
memoryLimit = 2048  # Increase to 2GB
```

#### 4. Slow API Responses

**Symptom:** API latency > 5 seconds

**Solution:**
```bash
# Check database queries
# Enable query logging in settings

# Add indexes
CREATE INDEX idx_papers_created_at ON papers(created_at);

# Enable Redis caching
# Add @cache decorator to slow endpoints

# Scale horizontally
# Add more API replicas
```

#### 5. Celery Tasks Stuck

**Symptom:** Tasks in queue but not processing

**Solution:**
```bash
# Check Celery workers
railway logs --service worker

# Restart workers
railway restart --service worker

# Purge queue
railway run celery -A app.tasks.celery_app purge

# Check Redis connection
railway run redis-cli -u $REDIS_URL ping
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with debug
railway run -s backend --debug
```

### Health Check Failures

```bash
# Test health endpoint
curl -v https://meta-analysis-api.railway.app/health

# Check Railway status
railway status

# View recent logs
railway logs --tail 100
```

---

## Support & Contact

- **Documentation:** https://github.com/yourusername/meta-analysis-tool
- **Issues:** https://github.com/yourusername/meta-analysis-tool/issues
- **Railway Support:** https://railway.app/support
- **Vercel Support:** https://vercel.com/support

---

**Last Updated:** November 4, 2025
**Version:** 1.0
**Next Review:** February 4, 2026
