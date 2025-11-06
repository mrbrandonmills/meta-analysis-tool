# Meta-Analysis Tool - Complete Infrastructure Analysis
## Prepared by Infrastructure Development Team
**Analysis Date:** 2025-11-05
**Project:** Meta-Analysis Research Platform
**Status:** Production-Ready with Active Deployment

---

## Executive Summary

This comprehensive infrastructure analysis documents the complete deployment architecture, operational procedures, and infrastructure management strategy for the Meta-Analysis Research Platform. The system is deployed across Railway (backend/database/workers) and Vercel (frontend) with a sophisticated multi-tier architecture supporting asynchronous task processing, real-time updates, and AI-powered research workflows.

**Current Deployment Status:**
- Backend API: Deployed on Railway at `meta-analysis-tool-production.up.railway.app`
- Frontend: Deployed on Vercel
- Database: PostgreSQL 15 (Railway Managed)
- Redis: Deployed for caching and message brokering
- Celery Workers: Background task processing (recently configured)
- CI/CD: GitHub Actions automated pipeline

---

## 1. Architecture Overview

### 1.1 High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Internet Traffic                              │
└─────────────────────────────────────────────────────────────────────┘
                    │                              │
                    │                              │
          ┌─────────▼────────┐          ┌──────────▼──────────┐
          │   Vercel CDN     │          │   Railway Network   │
          │   (Frontend)     │          │   (Backend)         │
          │                  │          │                     │
          │ • Next.js 14    │          │ • FastAPI API       │
          │ • React UI      │──────────│ • Uvicorn Server    │
          │ • SSR/SSG       │   HTTP   │ • Health Checks     │
          │ • Edge Network  │          │ • Metrics Endpoint  │
          └──────────────────┘          └─────────┬───────────┘
                                                   │
                    ┌──────────────────────────────┼───────────────────────────┐
                    │                              │                           │
         ┌──────────▼─────────┐        ┌──────────▼────────┐      ┌──────────▼──────────┐
         │   PostgreSQL 15    │        │   Redis 7         │      │  Celery Workers     │
         │   (Database)       │        │   (Cache/Queue)   │      │  (Background Jobs)  │
         │                    │        │                   │      │                     │
         │ • User accounts    │        │ • Session store   │      │ • Literature search │
         │ • Research data    │        │ • API cache       │      │ • Meta-analysis     │
         │ • Workflows        │        │ • Task queue      │      │ • PDF processing    │
         │ • Agent decisions  │        │ • Result backend  │      │ • Reviewer matching │
         │ • Audit logs       │        │ • Rate limiting   │      │ • Notifications     │
         └────────────────────┘        └───────────────────┘      └─────────────────────┘
                                                                            │
                                                                            │
                                                                   ┌────────▼────────────┐
                                                                   │  External APIs      │
                                                                   │                     │
                                                                   │ • Claude (Anthropic)│
                                                                   │ • OpenAI (Optional) │
                                                                   │ • PubMed            │
                                                                   │ • arXiv             │
                                                                   │ • Crossref          │
                                                                   └─────────────────────┘
```

### 1.2 Component Breakdown

#### Backend API (Railway)
- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn with uvloop (high-performance async)
- **Workers:** 2 Uvicorn workers per instance
- **Port:** Dynamic (Railway assigns via `$PORT` env var)
- **Features:**
  - RESTful API endpoints
  - JWT-based authentication
  - Real-time updates via Server-Sent Events (SSE)
  - Prometheus metrics endpoint
  - Comprehensive health checks
  - Request validation with Pydantic
  - CORS middleware
  - Rate limiting

#### Celery Worker Infrastructure (Railway)
- **Framework:** Celery 5.3.4
- **Broker:** Redis (message queue)
- **Result Backend:** Redis (task results storage)
- **Concurrency:** 4 workers per instance
- **Queues:**
  - `default`: General background tasks
  - `search`: Literature search operations
  - `analysis`: Statistical analysis and meta-analysis
  - `reviewer`: Reviewer profiling and matching
  - `notifications`: Email and notification tasks

#### Database Layer (PostgreSQL 15)
- **Hosting:** Railway Managed PostgreSQL
- **Version:** PostgreSQL 15-alpine
- **Connection Pooling:** SQLAlchemy async pool (20 connections, 40 max overflow)
- **Migrations:** Alembic (3 migrations deployed)
- **Features:**
  - Async query execution
  - Full-text search with pg_trgm
  - JSONB columns for flexible data
  - Foreign key constraints
  - Automated backups

#### Cache & Message Broker (Redis 7)
- **Hosting:** Railway Managed Redis
- **Version:** Redis 7-alpine
- **Persistence:** AOF (Append-Only File)
- **Use Cases:**
  - API response caching
  - Session storage
  - Celery message broker
  - Celery result backend
  - Rate limiting counters
  - Real-time data synchronization

#### Frontend (Vercel)
- **Framework:** Next.js 14
- **Deployment:** Vercel Edge Network
- **Build:** Static Site Generation (SSG) + Server-Side Rendering (SSR)
- **Features:**
  - React UI components
  - Real-time updates (SSE client)
  - Responsive design
  - Global CDN distribution
  - Automatic HTTPS

---

## 2. Docker Infrastructure

### 2.1 Development Environment (docker-compose.yml)

**Services:**
```yaml
1. PostgreSQL (postgres)
   - Image: postgres:15-alpine
   - Port: 5432
   - Volume: postgres_data (persistent)
   - Health Check: pg_isready every 10s

2. Redis (redis)
   - Image: redis:7-alpine
   - Port: 6379
   - Volume: redis_data (persistent with AOF)
   - Health Check: redis-cli ping every 10s

3. Backend API (backend)
   - Build: ./backend/Dockerfile
   - Port: 8000
   - Command: uvicorn with --reload
   - Volumes: Live code mounting for hot reload
   - Depends on: postgres, redis (with health checks)

4. Celery Worker (celery_worker)
   - Build: ./backend/Dockerfile
   - Command: celery worker with all queues
   - Depends on: postgres, redis, backend

5. Celery Beat (celery_beat)
   - Build: ./backend/Dockerfile
   - Command: celery beat for scheduled tasks
   - Depends on: redis, celery_worker

6. Flower (flower)
   - Build: ./backend/Dockerfile
   - Port: 5555
   - Purpose: Celery monitoring UI
   - Depends on: redis, celery_worker
```

**Quick Start:**
```bash
docker-compose up
# Services available at:
# - Backend API: http://localhost:8000
# - Flower UI: http://localhost:5555
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

### 2.2 Production-Like Environment (docker-compose.prod.yml)

**Additional Services:**
```yaml
7. Nginx (nginx)
   - Image: nginx:alpine
   - Ports: 80, 443
   - Purpose: Reverse proxy, SSL termination
   - Volumes: Config and SSL certificates

8. Prometheus (prometheus)
   - Image: prom/prometheus:latest
   - Port: 9090
   - Config: ./config/prometheus.yml
   - Retention: 30 days

9. Grafana (grafana)
   - Image: grafana/grafana:latest
   - Port: 3001
   - Features: Pre-configured dashboards
   - Data source: Prometheus
```

**Resource Limits:**
```yaml
Backend:
  CPU: 1.0 vCPU
  Memory: 1 GB (limit), 512 MB (reservation)

Worker:
  CPU: 1.0 vCPU
  Memory: 2 GB (limit), 1 GB (reservation)
  Replicas: 2 (scalable)
```

### 2.3 Dockerfiles

#### Backend Dockerfile (Multi-stage)

**Stage 1: Builder**
```dockerfile
FROM python:3.11-slim AS builder
# Install build dependencies: gcc, g++, libpq-dev
# Create virtual environment at /opt/venv
# Install Python dependencies (requirements.txt)
```

**Stage 2: Runtime**
```dockerfile
FROM python:3.11-slim
# Copy virtual environment from builder
# Install only runtime dependencies: libpq5, curl
# Copy application code
# Create non-root user (appuser, UID 1000)
# Set up health check (curl to /api/v1/health)
# Expose port (default 8000, overridden by Railway)
# Command: uvicorn with 2 workers
```

**Image Size:** ~300 MB (optimized)

#### Worker Dockerfile (Specialized)

**Key Differences:**
- **Additional build dependencies:** gfortran, libopenblas-dev, liblapack-dev
- **Runtime dependencies:** R base, libgomp1 (for parallel processing)
- **R packages:** metafor, meta, ggplot2 (for statistical analysis)
- **Heavy Python packages:** scipy, numpy, pandas, statsmodels, scikit-learn
- **Concurrency:** 2 workers with max 100 tasks per child
- **User:** Non-root worker user

**Image Size:** ~1.2 GB (includes R and scientific libraries)

---

## 3. Railway Deployment Configuration

### 3.1 Backend Service Configuration

**railway.toml:**
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "backend/Dockerfile"
watchPaths = ["backend/**"]

[deploy]
numReplicas = 1
sleepApplication = false
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 300  # 5 minutes

[deploy.resources]
memoryLimit = 1024  # 1 GB
cpuLimit = 1.0      # 1 vCPU
```

**railway.json (Advanced Configuration):**
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile",
    "watchPatterns": ["backend/**"]
  },
  "deploy": {
    "startCommand": "/app/start.sh",
    "healthcheckPath": "/api/v1/health",
    "healthcheckTimeout": 300
  },
  "environments": {
    "production": {
      "name": "Production",
      "variables": {
        "PYTHONUNBUFFERED": "1",
        "DEBUG": "false",
        "LOG_LEVEL": "INFO",
        "ALLOWED_ORIGINS": "https://meta-analysis-tool.vercel.app"
      }
    }
  }
}
```

### 3.2 Celery Worker Configuration

**railway.worker.json:**
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4",
    "restartPolicyType": "ON_FAILURE"
  },
  "environments": {
    "production": {
      "name": "Production Worker",
      "variables": {
        "WORKER_TYPE": "celery",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Worker Service Setup Steps:**
1. Create new Railway service: "meta-analysis-worker"
2. Connect to same GitHub repository
3. Use backend/Dockerfile
4. Configure environment variables (copy from backend)
5. Set custom start command for Celery
6. Deploy and monitor logs

### 3.3 Environment Variables

#### Required Variables (All Services)
```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-api03-...  # Required for AI features
SECRET_KEY=<random-64-char-string>  # Generate with: openssl rand -hex 32

# Database (Auto-provided by Railway)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# Application
PYTHONUNBUFFERED=1
PORT=${{PORT}}  # Railway auto-assigns
```

#### Optional Variables
```bash
# Additional AI APIs
OPENAI_API_KEY=sk-...

# Research APIs
PUBMED_API_KEY=...
PUBMED_EMAIL=user@example.com

# Monitoring
SENTRY_DSN=https://...@sentry.io/...

# Feature Flags
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://meta-analysis-tool.vercel.app

# Worker-specific
WORKER_TYPE=celery
```

---

## 4. Database Management

### 4.1 Alembic Migrations

**Current Migrations:**
```
001_multi_tool_schema.py (29,942 bytes)
├── Creates initial database schema
├── Users, projects, workflows tables
├── Papers, researchers, reviews tables
├── Agent decisions, audit logs

002_remove_duplicate_name_column.py (1,421 bytes)
├── Schema cleanup
├── Removes duplicate column

003_align_schema_with_models.py (2,532 bytes)
├── Synchronizes DB schema with SQLAlchemy models
├── Adds missing constraints
└── Updates indexes
```

**Migration Workflow:**
```bash
# Development
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head

# Production (Railway)
# Automated via start.sh script:
alembic upgrade head && uvicorn app.main:app ...
```

**Alembic Configuration (alembic.ini):**
- Migration file template: `%%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s`
- Location: `alembic/versions/`
- Environment: Configured in `alembic/env.py`
- Async support: Uses SQLAlchemy 2.0 async engine

### 4.2 Backup Strategy

**Automated Daily Backups (backup-db.sh):**
```bash
./scripts/backup-db.sh production
```

**Features:**
- Connects to Railway PostgreSQL via DATABASE_URL
- Dumps database in plain SQL format
- Compresses with gzip
- Verifies backup integrity
- Cleans up backups older than 30 days
- Optional S3 upload
- Generates backup report

**Backup Format:**
```
backups/
├── production_backup_20250105_120000.sql.gz
├── backup_report_20250105_120000.txt
└── ...
```

**Restore Procedures (restore-db.sh):**
```bash
# Restore to local
./scripts/restore-db.sh backups/production_backup_20250105.sql.gz local

# Restore to staging (with safety prompts)
./scripts/restore-db.sh backups/production_backup_20250105.sql.gz staging

# Emergency production restore (requires confirmation)
./scripts/restore-db.sh backups/production_backup_20250105.sql.gz production
```

**Safety Features:**
- Pre-restore backup creation
- Connection validation
- Backup integrity verification
- Automatic migration application
- Restore verification

### 4.3 Database Schema Overview

**Core Tables:**
- `users`: User accounts, authentication
- `projects`: Research projects
- `workflows`: Analysis workflows and state
- `papers`: Literature papers and metadata
- `researchers`: Researcher profiles (ORCID)
- `reviews`: Peer reviews and feedback
- `agent_decisions`: AI agent decision audit trail

**Key Indexes:**
- `idx_papers_doi`: Fast DOI lookup
- `idx_papers_title_trgm`: Full-text search on titles
- `idx_researchers_orcid`: ORCID-based researcher lookup
- `idx_workflows_status`: Workflow state filtering

---

## 5. Celery Worker Infrastructure

### 5.1 Celery Application Configuration

**File:** `backend/app/workers/celery_app.py`

**Broker & Backend:**
- Broker: Redis (task queue)
- Backend: Redis (result storage)

**Task Modules:**
```python
include=[
    "app.workers.tasks.literature_search",
    "app.workers.tasks.meta_analysis",
    "app.workers.tasks.reviewer_tasks",
    "app.workers.tasks.notifications",
]
```

**Queue Configuration:**
```python
task_queues=(
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("search", Exchange("search"), routing_key="search"),
    Queue("analysis", Exchange("analysis"), routing_key="analysis"),
    Queue("reviewer", Exchange("reviewer"), routing_key="reviewer"),
    Queue("notifications", Exchange("notifications"), routing_key="notifications"),
)
```

**Task Routing:**
```python
task_routes={
    "app.workers.tasks.literature_search.*": {"queue": "search"},
    "app.workers.tasks.meta_analysis.*": {"queue": "analysis"},
    "app.workers.tasks.reviewer_tasks.*": {"queue": "reviewer"},
    "app.workers.tasks.notifications.*": {"queue": "notifications"},
}
```

**Worker Settings:**
- Serializer: JSON (security and portability)
- Timezone: UTC
- Acknowledgment: Late (after task completion)
- Prefetch: 1 (process one task at a time)
- Max tasks per child: 100 (prevent memory leaks)
- Task time limits: 30 min soft, 40 min hard

**Periodic Tasks (Celery Beat):**
```python
beat_schedule={
    "cleanup-expired-tasks": {
        "task": "app.workers.tasks.maintenance.cleanup_expired_tasks",
        "schedule": 3600.0,  # Every hour
    },
    "update-researcher-profiles": {
        "task": "app.workers.tasks.reviewer_tasks.update_researcher_profiles",
        "schedule": 86400.0,  # Every 24 hours
    },
}
```

### 5.2 Worker Deployment Architecture

**Worker Types:**
1. **General Workers:** Process all queues
2. **Specialized Workers:** (Future) Dedicated to specific queues
3. **High-Priority Workers:** (Future) For urgent tasks

**Current Configuration:**
- 1 worker instance on Railway
- Processes all 5 queues
- 4 concurrent tasks
- Auto-restart on failure

**Scaling Strategy:**
```bash
# Horizontal scaling (add more workers)
railway scale worker --replicas=3

# Vertical scaling (more resources per worker)
# Update railway.toml:
[deploy.resources]
memoryLimit = 4096  # 4 GB
cpuLimit = 2.0      # 2 vCPU
```

### 5.3 Task Monitoring

**Health Check Integration:**
```python
# Endpoint: /api/v1/health/detailed
inspect = celery_app.control.inspect()
stats = inspect.stats()

if stats:
    worker_count = len(stats)
    checks["celery"] = {
        "status": "healthy",
        "message": f"{worker_count} worker(s) active",
        "workers": list(stats.keys())
    }
```

**Utility Functions:**
- `get_task_status(task_id)`: Check task progress
- `revoke_task(task_id)`: Cancel running task
- `get_active_tasks()`: List currently processing tasks
- `get_queue_stats()`: Queue depth and statistics

**Flower Monitoring (Development):**
```bash
docker-compose up flower
# Access at: http://localhost:5555
# Shows: Task history, worker status, queue statistics
```

---

## 6. CI/CD Pipeline

### 6.1 GitHub Actions Workflows

#### Test Workflow (.github/workflows/test.yml)

**Triggers:**
- Pull requests to `main` or `develop`
- Pushes to `develop` branch

**Jobs:**
```yaml
1. backend-tests
   - Python 3.11 on Ubuntu
   - PostgreSQL 15 service container
   - Redis 7 service container
   - Runs: Unit tests, integration tests
   - Coverage: pytest-cov with XML reports

2. frontend-tests
   - Node.js 18 on Ubuntu
   - npm ci (clean install)
   - Runs: Jest tests
   - Build check: npm run build

3. code-quality
   - flake8: Linting (max line length 120)
   - black: Code formatting check
   - isort: Import sorting check
   - mypy: Type checking

4. security-scan
   - Trivy: Vulnerability scanning
   - TruffleHog: Secret detection
   - SARIF upload to GitHub Security
```

#### Deployment Workflow (.github/workflows/deploy.yml)

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Pipeline Stages:**

**Stage 1: Testing**
```yaml
test-backend:
  - Full test suite with coverage
  - Linting (flake8, black, mypy)
  - Codecov upload

test-frontend:
  - Frontend tests
  - Linting (eslint)
  - Production build
```

**Stage 2: Docker Build**
```yaml
build-docker:
  - Set up Docker Buildx
  - Login to GitHub Container Registry
  - Build backend image (multi-arch)
  - Build worker image (multi-arch)
  - Push to ghcr.io with tags:
    - main (branch name)
    - main-<sha> (commit hash)
    - latest (if main branch)
  - Layer caching via GitHub Actions cache
```

**Stage 3: Deployment**
```yaml
deploy-railway:
  - Install Railway CLI
  - Deploy backend service
  - Run database migrations
  - Health check verification

deploy-vercel:
  - Deploy frontend to Vercel
  - Production domain assignment
```

**Stage 4: Smoke Tests**
```yaml
smoke-tests:
  - Test API health endpoint
  - Test frontend availability
  - Verify response codes (200)
```

**Stage 5: Notification**
```yaml
notify:
  - Send Slack notification
  - Include: Deployment status, commit info, author
```

### 6.2 Deployment Scripts

#### Railway Deployment (railway-deploy.sh)

**Features:**
- Interactive project selection
- Current deployment health check
- Step-by-step Redis deployment
- Database migration verification
- Celery worker service setup
- Final verification with detailed status
- Automated backup before production changes

**Execution Flow:**
```bash
1. Check Railway CLI availability
2. List available projects
3. Verify current deployment health
4. Add Redis (if missing)
5. Verify database migrations
6. Deploy Celery worker service
7. Run final verification tests
8. Display success metrics
```

#### Worker Deployment (deploy-celery-worker.sh)

**Diagnostic Steps:**
1. Check deployment health
2. Verify environment variables
3. Check build configuration
4. Trigger redeploy if needed
5. Monitor worker connection (10 attempts)
6. Provide troubleshooting guidance

**Monitoring (monitor-worker-deployment.sh):**
- Continuous health monitoring (every 15 seconds)
- Up to 5 minutes of polling
- Real-time status display
- Success notification when workers connect
- Troubleshooting guidance on failure

#### Verification Scripts

**verify-deployment.sh:**
```bash
Tests:
1. Health check - All services
2. User registration - Database migrations
3. User login - JWT authentication
4. Protected endpoint - Redis sessions

Success Criteria:
- Database: healthy
- Redis: healthy
- Celery: healthy
- All HTTP tests pass (201, 200)
```

**verify-worker-health.sh:**
```bash
Quick check:
- Fetch /api/v1/health/detailed
- Parse Celery status
- Exit 0 if healthy, 1 if not
```

---

## 7. Monitoring and Observability

### 7.1 Health Check System

**Endpoint Structure:**

**Basic Health (`/api/v1/health`):**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-05T12:00:00.000Z",
  "service": "meta-analysis-platform",
  "version": "0.1.0"
}
```

**Detailed Health (`/api/v1/health/detailed`):**
```json
{
  "timestamp": "2025-11-05T12:00:00.000Z",
  "service": "meta-analysis-platform",
  "version": "0.1.0",
  "status": "healthy",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful"
    },
    "celery": {
      "status": "healthy",
      "message": "1 worker(s) active",
      "workers": ["celery@worker-hostname"]
    }
  }
}
```

**Kubernetes Probes:**
- **Liveness:** `/api/v1/health/live` - Service should stay alive
- **Readiness:** `/api/v1/health/ready` - Service ready for traffic

### 7.2 Prometheus Metrics

**Metrics Endpoint:** `/metrics`

**Custom Metrics:**
```prometheus
# HTTP Request Metrics
http_requests_total{method="GET",path="/api/v1/search",status="200"}
http_request_duration_seconds{method="POST",path="/api/v1/meta-analysis"}

# Agent Execution Metrics
agent_executions_total{agent="search",status="success"}
agent_execution_duration_seconds{agent="meta_analysis"}

# LLM API Metrics
llm_api_calls_total{provider="anthropic",model="claude-3-sonnet"}
llm_tokens_total{provider="anthropic",model="claude-3-sonnet"}
llm_api_duration_seconds{provider="anthropic"}

# Database Metrics
database_queries_total{type="select"}
database_query_duration_seconds{type="insert"}

# Workflow Metrics
workflow_events_total{event="started",workflow="meta_analysis"}
active_workflows
queue_size{queue="celery"}
```

**Prometheus Configuration (config/prometheus.yml):**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['backend:8000']

  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 7.3 Logging Infrastructure

**Structured Logging with Loguru:**

**Production Format (JSON):**
```json
{
  "timestamp": "2025-11-05T12:00:00.000Z",
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

**Development Format (Pretty):**
```
2025-11-05 12:00:00.000 | INFO     | app.agents.search:search_papers:42 | Searching PubMed for query
```

**Log Levels:**
- `DEBUG`: Detailed debugging (development only)
- `INFO`: General informational messages
- `WARNING`: Potential issues
- `ERROR`: Recoverable errors
- `CRITICAL`: System failures

**Context Tracking:**
- Request ID propagation
- User ID tracking
- Workflow ID correlation
- Exception tracing

### 7.4 Sentry Integration

**Error Tracking Configuration:**
```python
# File: backend/app/monitoring/sentry.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    environment=settings.environment,
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
        CeleryIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% of transactions
    profiles_sample_rate=0.1,  # 10% profiling
)
```

**What Gets Tracked:**
- Unhandled exceptions
- Agent failures
- API errors (4xx, 5xx)
- Database errors
- LLM API failures
- Background task failures

---

## 8. Operational Procedures

### 8.1 Deployment Checklist

**Pre-Deployment:**
- [ ] All tests passing in CI
- [ ] Database migrations reviewed
- [ ] Environment variables verified
- [ ] Dependencies updated
- [ ] Security scan passed
- [ ] Code review approved

**Deployment:**
- [ ] Create database backup
- [ ] Deploy to staging first
- [ ] Run smoke tests on staging
- [ ] Deploy to production
- [ ] Run database migrations
- [ ] Verify health checks
- [ ] Test critical user flows

**Post-Deployment:**
- [ ] Monitor error rates (Sentry)
- [ ] Check application logs
- [ ] Verify worker processing
- [ ] Test user registration/login
- [ ] Monitor resource usage
- [ ] Document deployment

### 8.2 Scaling Procedures

**Horizontal Scaling (Add Instances):**
```bash
# Scale backend API
# Update railway.toml:
[deploy]
numReplicas = 3

# Scale workers
# Add more worker services in Railway dashboard
# Or increase replicas in docker-compose.prod.yml:
worker:
  deploy:
    replicas: 5
```

**Vertical Scaling (More Resources):**
```bash
# Update resource limits in railway.toml:
[deploy.resources]
memoryLimit = 2048  # 2 GB
cpuLimit = 2.0      # 2 vCPU
```

**Database Scaling:**
- Railway: Upgrade to Pro plan (8 GB, 32 GB, etc.)
- Add read replicas for query distribution
- Implement connection pooling optimizations

**Cache Scaling:**
- Railway: Upgrade Redis plan (1 GB, 4 GB)
- Implement Redis Cluster for high availability
- Add cache warming for frequently accessed data

### 8.3 Incident Response

**Severity Levels:**
1. **P1 (Critical):** Service down, data loss
2. **P2 (High):** Major feature broken, performance degraded
3. **P3 (Medium):** Minor feature broken, workaround available
4. **P4 (Low):** Cosmetic issue, enhancement request

**Response Procedure:**

**1. Detection:**
- Health check failures
- Sentry error spike
- User reports
- Monitoring alerts

**2. Investigation:**
```bash
# Check service status
railway status

# View logs
railway logs --tail 100 --service backend

# Check health endpoint
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed

# Check database
railway run psql -c "SELECT 1"

# Check Redis
railway run redis-cli ping
```

**3. Mitigation:**
- Rollback deployment if recent change
- Scale resources if capacity issue
- Restart services if hung
- Disable feature flags if feature-specific

**4. Recovery:**
- Restore from backup if data corruption
- Run migrations if schema issues
- Clear cache if stale data

**5. Post-Mortem:**
- Document incident timeline
- Identify root cause
- Create action items
- Update runbooks

### 8.4 Troubleshooting Guide

#### Database Connection Errors
**Symptom:** `psycopg2.OperationalError`

**Solutions:**
```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
pg_isready -d $DATABASE_URL

# Check Railway PostgreSQL status
railway status --service postgresql

# Verify connection pool settings
# Check: SQLALCHEMY_POOL_SIZE, SQLALCHEMY_MAX_OVERFLOW
```

#### Redis Connection Errors
**Symptom:** `redis.exceptions.ConnectionError`

**Solutions:**
```bash
# Verify REDIS_URL
echo $REDIS_URL

# Test connection
redis-cli -u $REDIS_URL ping

# Check Railway Redis status
railway status --service redis

# Check Redis memory usage
redis-cli -u $REDIS_URL INFO memory
```

#### Celery Workers Not Processing
**Symptom:** Tasks stuck in queue

**Solutions:**
```bash
# Check worker logs
railway logs --service worker

# Verify worker is running
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed

# Purge stuck tasks
railway run celery -A app.workers.celery_app purge

# Restart workers
railway restart --service worker
```

#### High Memory Usage
**Symptom:** OOM errors, API crashes

**Solutions:**
```bash
# Check metrics
railway metrics --service backend

# Reduce worker concurrency
# Update start command:
celery worker --concurrency=1

# Increase memory limit
# Update railway.toml:
[deploy.resources]
memoryLimit = 2048
```

#### Slow API Responses
**Symptom:** Latency > 5 seconds

**Solutions:**
```bash
# Enable query logging
# Check slow queries

# Add database indexes
CREATE INDEX idx_papers_created_at ON papers(created_at);

# Enable Redis caching
# Add @cache decorator to slow endpoints

# Scale horizontally
railway scale backend --replicas=2
```

---

## 9. Security Infrastructure

### 9.1 Authentication & Authorization

**JWT Token System:**
- Algorithm: HS256
- Access token expiration: 30 minutes
- Refresh token expiration: 7 days
- Secret key: Stored in environment variable

**Password Security:**
- Hashing: bcrypt (passlib)
- Salt rounds: 12 (default)
- Minimum password strength enforced

**API Security:**
- Rate limiting (per-user and per-endpoint)
- CORS configuration (whitelist origins)
- Security headers (CSP, X-Frame-Options, etc.)
- HTTPS enforcement (Railway automatic)

### 9.2 Secrets Management

**Railway Variables:**
```bash
# Sensitive values stored in Railway
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set SECRET_KEY=<random-key>
railway variables set SENTRY_DSN=https://...

# Reference variables for service linking
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

**Local Development:**
```bash
# .env file (in .gitignore)
cp .env.example .env
# Edit .env with development secrets
```

### 9.3 Network Security

**Railway Private Networking:**
- Internal service-to-service communication
- Database accessible only from Railway network
- Redis accessible only from Railway network

**Vercel Security:**
- Automatic HTTPS/TLS
- DDoS protection
- Edge network security

---

## 10. Cost Analysis and Optimization

### 10.1 Current Cost Structure (Phase 0-1)

**Monthly Costs:**
| Service | Plan | Cost |
|---------|------|------|
| Railway Backend | Starter | $20 |
| Railway PostgreSQL | Shared | $5 |
| Railway Redis | Shared | $5 |
| Railway Worker | Starter | $20 |
| Vercel Frontend | Hobby | $0 |
| Claude API | Usage-based | $50-200 |
| **Total** | | **$100-250/month** |

### 10.2 Cost Optimization Strategies

**1. LLM API Cost Reduction:**
- Use Claude Haiku for simple queries (cheaper)
- Use Claude Sonnet for complex analysis
- Implement aggressive response caching (24-hour TTL)
- Prompt compression and optimization
- Batch API calls where possible

**2. Database Optimization:**
- Archive old data (> 1 year)
- Optimize queries (add indexes)
- Use connection pooling efficiently
- Enable query result caching

**3. Compute Optimization:**
- Right-size worker instances (monitor CPU/memory)
- Auto-scale workers based on queue depth
- Use spot instances when available
- Reduce Celery worker concurrency if underutilized

**4. Bandwidth Reduction:**
- Serve static assets from Vercel CDN
- Enable gzip compression
- Implement API response caching
- Minimize payload sizes

### 10.3 Scaling Cost Projections

**Phase 2-3 (Growth): $300-500/month**
- 2 API replicas
- 2 worker instances
- PostgreSQL Pro (8 GB)
- Redis Pro (1 GB)
- Increased Claude API usage

**Phase 4-5 (Scale): $500-1000/month**
- 4 API replicas
- 4-6 worker instances
- PostgreSQL Pro (32 GB)
- Redis Pro (4 GB)
- High-volume Claude API usage
- Sentry Business plan

---

## 11. Disaster Recovery

### 11.1 Recovery Objectives

- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 24 hours

### 11.2 Backup Strategy

**Automated Daily Backups:**
```bash
# Cron schedule
0 2 * * * /app/scripts/backup-db.sh production

# Retention: 30 days
# Compression: gzip
# Verification: Automated integrity check
# Storage: Local + S3 (optional)
```

**Backup Components:**
- PostgreSQL database (full dump)
- Redis data (RDB snapshots)
- Application configuration
- Environment variables (encrypted)

### 11.3 Disaster Scenarios

**Scenario 1: Database Corruption**
```bash
# 1. Restore from last backup
./scripts/restore-db.sh backups/production_backup_20250105.sql.gz production

# 2. Verify data integrity
railway run psql -c "SELECT COUNT(*) FROM papers;"

# 3. Run migrations
railway run alembic upgrade head

# 4. Resume operations
```

**Scenario 2: Complete Service Failure**
```bash
# 1. Deploy to new Railway project
railway init --name meta-analysis-recovery

# 2. Add services
railway add --service postgresql
railway add --service redis

# 3. Restore database
./scripts/restore-db.sh backups/production_backup_20250105.sql.gz production

# 4. Update environment variables
railway variables set ANTHROPIC_API_KEY=...

# 5. Deploy services
railway up

# 6. Update DNS/frontend configuration
```

**Scenario 3: Data Loss (Partial)**
```bash
# 1. Identify lost data from audit logs
railway run psql -c "SELECT * FROM audit_logs WHERE timestamp > '2025-11-05 12:00:00';"

# 2. Restore specific tables
pg_restore -t papers backups/production_backup_20250105.sql.gz

# 3. Verify consistency
# Check foreign key constraints
# Validate data relationships
```

---

## 12. Infrastructure Improvements Needed

### 12.1 High Priority

**1. Implement Celery Beat Service**
- Scheduled task execution (cleanup, profile updates)
- Separate Railway service or deployment
- Monitoring for scheduled task failures

**2. Add Automated Monitoring Alerts**
- Sentry error rate thresholds
- Health check failure notifications
- Resource usage alerts (CPU > 80%, Memory > 80%)
- Queue depth alerts (> 100 tasks)

**3. Implement API Rate Limiting**
- Per-user rate limits (100/hour free, 1000/hour pro)
- Per-endpoint limits
- Redis-based counter storage
- Graceful degradation

**4. Database Read Replicas**
- Separate read/write workloads
- Reduce primary database load
- Improve query performance

### 12.2 Medium Priority

**5. Enhanced Caching Strategy**
- Multi-layer caching (L1: memory, L2: Redis)
- Cache warming for hot data
- Intelligent cache invalidation
- CDN integration for static content

**6. Comprehensive Logging Pipeline**
- Centralized log aggregation (e.g., LogDNA, Datadog)
- Log retention policies
- Log search and analysis tools
- Automated log alerts

**7. Blue-Green Deployment**
- Zero-downtime deployments
- Quick rollback capability
- A/B testing infrastructure

**8. Performance Optimization**
- Database query optimization
- N+1 query elimination
- Lazy loading strategies
- Background task optimization

### 12.3 Low Priority

**9. Infrastructure as Code (IaC)**
- Terraform for Railway resources
- Version-controlled infrastructure
- Automated infrastructure provisioning

**10. Advanced Security Hardening**
- Web Application Firewall (WAF)
- DDoS protection
- Intrusion detection system
- Security audit logging

**11. Multi-Region Deployment**
- Geographic distribution
- Latency optimization
- Disaster recovery across regions

**12. Kubernetes Migration (Future)**
- For advanced orchestration needs
- Auto-scaling capabilities
- Self-healing infrastructure

---

## 13. Quick Reference Commands

### Development
```bash
# Start local environment
docker-compose up

# Run migrations
docker-compose exec backend alembic upgrade head

# View logs
docker-compose logs -f backend

# Access database
docker-compose exec postgres psql -U meta_analysis

# Access Redis
docker-compose exec redis redis-cli

# Run tests
docker-compose exec backend pytest
```

### Production (Railway)
```bash
# Deploy backend
railway up --service backend

# View logs
railway logs --tail 100 --service backend

# Run migrations
railway run alembic upgrade head

# Access database
railway run psql

# Restart service
railway restart --service backend

# Set environment variable
railway variables set KEY=value
```

### Database Operations
```bash
# Create backup
./scripts/backup-db.sh production

# Restore backup
./scripts/restore-db.sh backups/backup.sql.gz local

# Check migration status
cd backend && alembic current

# Create new migration
cd backend && alembic revision --autogenerate -m "description"
```

### Verification
```bash
# Health check
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed

# Run deployment verification
./verify-deployment.sh

# Check worker health
./verify-worker-health.sh

# Monitor worker deployment
./monitor-worker-deployment.sh
```

---

## 14. Documentation Index

**Infrastructure Documentation:**
- `INFRASTRUCTURE.md`: Comprehensive infrastructure guide
- `INFRASTRUCTURE_README.md`: Quick start guide
- `INFRASTRUCTURE_FIX_GUIDE.md`: Troubleshooting guide
- `INFRASTRUCTURE_BUG_FIX_REPORT.md`: Bug fix history

**Deployment Documentation:**
- `DEPLOYMENT.md`: General deployment guide
- `RAILWAY_DEPLOYMENT_GUIDE.md`: Railway-specific guide
- `RAILWAY_SETUP.md`: Initial Railway setup
- `VERCEL_DEPLOY.md`: Vercel deployment
- `DEPLOYMENT_CHECKLIST.md`: Pre-deployment checklist

**Worker Documentation:**
- `CELERY_WORKER_DEPLOYMENT.md`: Celery worker setup
- `RAILWAY_WORKER_FIX.md`: Worker troubleshooting
- `WORKER_DEPLOYMENT_STATUS.md`: Worker deployment status

**Scripts:**
- `railway-deploy.sh`: Automated Railway deployment
- `deploy-celery-worker.sh`: Worker deployment script
- `verify-deployment.sh`: Deployment verification
- `verify-worker-health.sh`: Worker health check
- `monitor-worker-deployment.sh`: Worker monitoring
- `backup-db.sh`: Database backup
- `restore-db.sh`: Database restore

---

## 15. Conclusion

The Meta-Analysis Research Platform infrastructure is production-ready with a robust, scalable architecture deployed across Railway and Vercel. The system demonstrates:

**Strengths:**
- Multi-tier architecture with clear separation of concerns
- Comprehensive CI/CD pipeline with automated testing
- Health monitoring and observability infrastructure
- Disaster recovery procedures with automated backups
- Security best practices implemented
- Cost-optimized deployment strategy

**Current State:**
- Backend API: Operational on Railway
- Database: PostgreSQL with 3 migrations applied
- Redis: Deployed for caching and message brokering
- Celery Workers: Deployed and processing background tasks
- Frontend: Deployed on Vercel with global CDN
- CI/CD: Automated deployment pipeline active

**Readiness:**
The infrastructure is ready for:
- Production user traffic
- Board meeting demonstrations
- Alpha/beta testing
- Real research workloads
- Incremental scaling as user base grows

**Next Steps:**
Priority should be given to implementing the high-priority improvements (Celery Beat, monitoring alerts, rate limiting) to enhance reliability and operational excellence.

---

**Prepared By:** Infrastructure Development Team
**Review Date:** 2025-11-05
**Next Review:** 2026-02-05
**Status:** Production-Ready
