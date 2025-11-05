# Phase 0 Foundation Setup Guide

**Meta-Analysis Research Platform - Production-Ready Infrastructure**

**Date:** November 4, 2025
**Version:** 1.0
**Status:** Complete

---

## Overview

Phase 0 establishes the critical infrastructure needed before building new tools for the academic research platform. This 2-week sprint delivers:

-  **Database Persistence Layer** - SQLAlchemy with connection pooling
-  **User Authentication System** - JWT-based auth with RBAC
-  **Background Job Queue** - Celery + Redis for long-running tasks
-  **API Improvements** - Rate limiting, pagination, error handling
-  **Production Infrastructure** - Docker Compose, health checks, monitoring

---

## Table of Contents

1. [Components Implemented](#components-implemented)
2. [Local Development Setup](#local-development-setup)
3. [Database Setup](#database-setup)
4. [Authentication](#authentication)
5. [Background Jobs](#background-jobs)
6. [API Documentation](#api-documentation)
7. [Testing](#testing)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)

---

## Components Implemented

### 1. Database Persistence Layer

**Files:**
- `/backend/app/db/base.py` - Sync database session management
- `/backend/app/db/session.py` - Async database session management
- `/backend/app/models/user.py` - User and API key models

**Features:**
-  SQLAlchemy ORM with Pydantic V2 schemas
-  Connection pooling (configurable pool size)
-  Async/sync dual support
-  Transaction management with context managers
-  Auto-commit/rollback on success/error
-  Database initialization and migrations ready

**Usage Example:**
```python
# Async database session
from app.db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

@router.get("/items")
async def get_items(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Item))
    return result.scalars().all()

# Transaction management
from app.db.session import async_transaction

async with async_transaction(db):
    user = User(email="test@example.com")
    db.add(user)
    # Automatically commits on success, rolls back on error
```

### 2. User Authentication System

**Files:**
- `/backend/app/core/security.py` - JWT utilities, password hashing, RBAC
- `/backend/app/api/v1/auth.py` - Registration, login, token endpoints
- `/backend/app/models/user.py` - User model with role system

**Features:**
-  JWT tokens (access + refresh)
-  Password hashing with bcrypt
-  Role-based access control (admin, researcher, reviewer, viewer)
-  API key management for programmatic access
-  OAuth2 password flow
-  Token refresh mechanism
-  Password strength validation

**User Roles:**
- **Admin** - Full system access
- **Researcher** - Create and manage own projects
- **Reviewer** - Review and comment on projects
- **Viewer** - Read-only access

**API Endpoints:**
```
POST   /api/v1/auth/register       - Register new user
POST   /api/v1/auth/login          - Login (returns access + refresh tokens)
POST   /api/v1/auth/refresh        - Refresh access token
GET    /api/v1/auth/me             - Get current user info
POST   /api/v1/auth/api-keys       - Create API key
GET    /api/v1/auth/api-keys       - List user's API keys
DELETE /api/v1/auth/api-keys/{id}  - Delete API key
POST   /api/v1/auth/logout         - Logout (client-side cleanup)
```

**Usage Example:**
```python
# Protect an endpoint
from app.core.security import get_current_user_token, TokenData
from fastapi import Depends

@router.get("/protected")
async def protected_route(token: TokenData = Depends(get_current_user_token)):
    return {"user_id": token.user_id, "role": token.role}

# Require specific role
from app.core.security import require_admin

@router.post("/admin-only")
async def admin_endpoint(token: TokenData = Depends(require_admin)):
    return {"message": "Admin access granted"}
```

### 3. Background Job Queue

**Files:**
- `/backend/app/workers/celery_app.py` - Celery configuration
- `/backend/app/workers/tasks/literature_search.py` - Literature search tasks
- `/backend/app/workers/tasks/meta_analysis.py` - Meta-analysis tasks

**Features:**
-  Celery with Redis backend
-  Multiple task queues (search, analysis, reviewer, notifications)
-  Task retry logic with exponential backoff
-  Task status tracking
-  Progress updates
-  Error handling and logging
-  Periodic tasks (Celery Beat)

**Task Queues:**
- **default** - General tasks
- **search** - Literature search tasks
- **analysis** - Meta-analysis calculations
- **reviewer** - Reviewer profiling tasks
- **notifications** - Email/notification tasks

**Usage Example:**
```python
# Enqueue a task
from app.workers.tasks.literature_search import search_databases

task = search_databases.delay(
    query="COVID-19 vaccines",
    databases=["pubmed", "arxiv"],
    max_results=1000,
    user_id="user_123"
)

# Check task status
from app.workers.celery_app import get_task_status

status = get_task_status(task.id)
# Returns: {"task_id": "...", "status": "PENDING|SUCCESS|FAILURE", "result": ...}
```

### 4. API Improvements

**Files:**
- `/backend/app/core/middleware.py` - Rate limiting, error handling, pagination
- `/backend/app/api/v1/health.py` - Health check endpoints

**Features:**
-  Rate limiting (Redis-backed, distributed)
-  Pagination helpers
-  RFC 7807 Problem Details error responses
-  Request ID tracking
-  Performance monitoring
-  Global error handling

**Rate Limiting:**
- Authenticated users: 100 requests/minute
- Unauthenticated users: 20 requests/minute
- Per-user tracking (not per-IP)
- Automatic retry-after headers

**Pagination Example:**
```python
from app.core.middleware import PaginationParams
from fastapi import Depends

@router.get("/items")
async def list_items(pagination: PaginationParams = Depends()):
    items = await get_items(skip=pagination.skip, limit=pagination.limit)
    total = await get_total_items()
    return pagination.paginate(items, total)

# Returns:
# {
#   "items": [...],
#   "pagination": {
#     "page": 1,
#     "page_size": 20,
#     "total_items": 150,
#     "total_pages": 8,
#     "has_next": true,
#     "has_prev": false
#   }
# }
```

**Health Checks:**
```
GET /api/v1/health                - Basic health check
GET /api/v1/health/detailed       - Detailed health with dependencies
GET /api/v1/health/live          - Kubernetes liveness probe
GET /api/v1/health/ready         - Kubernetes readiness probe
GET /api/v1/health/metrics       - System metrics (admin only)
GET /api/v1/health/version       - Version information
```

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+ (or use Docker)
- Redis 7+ (or use Docker)

### Quick Start with Docker Compose

1. **Clone and navigate to project:**
```bash
cd /Users/brandon/meta-analysis-tool
```

2. **Create `.env` file:**
```bash
cat > .env << 'EOF'
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Database (Docker Compose will use these)
DATABASE_URL=postgresql://meta_analysis:dev_password_change_in_production@postgres:5432/meta_analysis_db
REDIS_URL=redis://redis:6379/0

# Optional
OPENAI_API_KEY=your-openai-key-here
DEBUG=true
EOF
```

3. **Start all services:**
```bash
docker-compose up -d
```

This starts:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- FastAPI backend (port 8000)
- Celery worker (background jobs)
- Celery beat (periodic tasks)
- Flower (Celery monitoring at port 5555)

4. **Verify services:**
```bash
# Check all containers are running
docker-compose ps

# Check backend health
curl http://localhost:8000/api/v1/health

# Check API documentation
open http://localhost:8000/docs

# Check Celery monitoring
open http://localhost:5555
```

5. **View logs:**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### Manual Setup (Without Docker)

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Start PostgreSQL:**
```bash
# macOS with Homebrew
brew services start postgresql@15

# Create database
createdb meta_analysis_db
```

3. **Start Redis:**
```bash
# macOS with Homebrew
brew services start redis
```

4. **Set environment variables:**
```bash
export DATABASE_URL="postgresql://localhost:5432/meta_analysis_db"
export REDIS_URL="redis://localhost:6379/0"
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
export SECRET_KEY=$(openssl rand -hex 32)
```

5. **Run database migrations:**
```bash
cd backend
# TODO: Add Alembic migrations
# alembic upgrade head
```

6. **Start the backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. **Start Celery worker (in another terminal):**
```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

8. **Start Celery beat (in another terminal):**
```bash
cd backend
celery -A app.workers.celery_app beat --loglevel=info
```

---

## Database Setup

### Schema Management

The database uses SQLAlchemy ORM with async support. Models are defined in `/backend/app/models/`.

**Current Models:**
- `User` - User accounts with authentication
- `APIKey` - API keys for programmatic access

**Future Models (Database Architect will add):**
- `Project` - Research projects
- `Workflow` - Agent workflow execution
- `Paper` - Academic papers/studies
- `Researcher` - Researcher profiles
- And more...

### Database Initialization

The database is automatically initialized on startup:

```python
# In app/main.py lifespan function
await init_async_db()  # Creates all tables
```

### Manual Migration (Future)

Once Alembic is fully configured:

```bash
# Create a migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Authentication

### User Registration

**Endpoint:** `POST /api/v1/auth/register`

**Request:**
```json
{
  "email": "researcher@university.edu",
  "password": "SecurePass123",
  "full_name": "Dr. Jane Smith",
  "institution": "Stanford University"
}
```

**Response:**
```json
{
  "id": "uuid-here",
  "email": "researcher@university.edu",
  "full_name": "Dr. Jane Smith",
  "institution": "Stanford University",
  "role": "researcher",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-11-04T10:00:00Z",
  "last_login": null
}
```

### User Login

**Endpoint:** `POST /api/v1/auth/login`

**Request (form data):**
```
username=researcher@university.edu
password=SecurePass123
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using Authentication

**In API Requests:**
```bash
# Include access token in Authorization header
curl -H "Authorization: Bearer eyJhbGci..." \
     http://localhost:8000/api/v1/auth/me
```

**Token Refresh:**
```bash
# When access token expires, use refresh token
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"refresh_token": "eyJhbGci..."}' \
     http://localhost:8000/api/v1/auth/refresh
```

### API Keys

For programmatic access (scripts, CI/CD):

1. **Create API key:**
```bash
curl -X POST \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "My Script", "expires_in_days": 365}' \
     http://localhost:8000/api/v1/auth/api-keys
```

2. **Use API key:**
```bash
curl -H "X-API-Key: sk_your_api_key_here" \
     http://localhost:8000/api/v1/protected-endpoint
```

---

## Background Jobs

### Task Execution

**Submit a task:**
```python
from app.workers.tasks.literature_search import search_databases

task = search_databases.delay(
    query="machine learning",
    databases=["arxiv", "pubmed"],
    max_results=500
)

print(f"Task ID: {task.id}")
```

**Check task status:**
```python
from app.workers.celery_app import get_task_status

status = get_task_status(task_id)
print(status)
# {
#   "task_id": "abc-123",
#   "status": "SUCCESS",
#   "result": {...}
# }
```

**Cancel a running task:**
```python
from app.workers.celery_app import revoke_task

revoke_task(task_id, terminate=True)
```

### Monitoring with Flower

Flower provides a web-based dashboard for Celery monitoring:

```bash
# Access Flower dashboard
open http://localhost:5555
```

Features:
- Real-time task monitoring
- Worker status and statistics
- Task history and results
- Task rate graphs
- Broker monitoring

---

## API Documentation

### Interactive Documentation

FastAPI provides auto-generated API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Testing Endpoints

Use the interactive docs to test endpoints:

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Login to get access token
4. Paste token in authorization dialog
5. Try protected endpoints

### cURL Examples

**Register user:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test User"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPass123"
```

**Get current user:**
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

## Testing

### Unit Tests

**Run unit tests:**
```bash
cd backend
pytest tests/unit/ -v
```

**Test coverage:**
```bash
pytest tests/unit/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Integration Tests

**Run integration tests:**
```bash
pytest tests/integration/ -v
```

**Test auth flow:**
```bash
pytest tests/integration/test_auth.py -v
```

### Test Database

Tests use a separate test database:

```bash
# Set test database URL
export TEST_DATABASE_URL="postgresql://localhost:5432/meta_analysis_test"

# Run tests
pytest
```

---

## Production Deployment

### Environment Variables

**Required:**
```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...
SECRET_KEY=<64-char-random-hex>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/0

# Security
ALLOWED_ORIGINS=https://yourdomain.com
```

**Optional:**
```bash
# Application
DEBUG=false
LOG_LEVEL=INFO

# External APIs
OPENAI_API_KEY=sk-...
PUBMED_API_KEY=...
```

### Railway Deployment

The app is already configured for Railway:

1. **Push to GitHub**
2. **Connect Railway to repo**
3. **Set environment variables in Railway dashboard**
4. **Deploy**

Railway will:
- Provision PostgreSQL database
- Provision Redis cache
- Build and deploy backend
- Set up Celery workers

### Docker Production

**Build production image:**
```bash
docker build -t meta-analysis-backend -f backend/Dockerfile backend/
```

**Run in production:**
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="..." \
  -e REDIS_URL="..." \
  -e ANTHROPIC_API_KEY="..." \
  -e SECRET_KEY="..." \
  meta-analysis-backend
```

### Health Checks

Configure your load balancer/orchestrator to use:

- **Liveness:** `GET /api/v1/health/live`
- **Readiness:** `GET /api/v1/health/ready`

---

## Troubleshooting

### Database Connection Issues

**Problem:** `FATAL: database "meta_analysis_db" does not exist`

**Solution:**
```bash
# Create database
createdb meta_analysis_db

# Or with Docker
docker-compose exec postgres createdb -U meta_analysis meta_analysis_db
```

### Redis Connection Failed

**Problem:** `Error connecting to Redis`

**Solution:**
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Or with Docker
docker-compose logs redis
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Ensure you're in the backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run from correct directory
uvicorn app.main:app
```

### Celery Worker Not Processing Tasks

**Problem:** Tasks stuck in PENDING state

**Solution:**
```bash
# Check worker is running
celery -A app.workers.celery_app inspect active

# Restart worker
docker-compose restart celery_worker

# Check logs
docker-compose logs celery_worker
```

### Rate Limiting Not Working

**Problem:** Rate limiting not enforced

**Solution:**
```bash
# Check Redis connection
redis-cli ping

# Check rate limiter initialization logs
docker-compose logs backend | grep "rate limiter"

# Redis must be running for rate limiting to work
```

---

## Next Steps

Phase 0 foundation is complete! Next priorities:

1. **Database Architect:** Complete database schema for all 4 tools
2. **Complete Tool 1:** Add DataExtractionAgent and StatisticalAgent
3. **Begin Tool 4:** Expert Reviewer Matcher (highest ROI)
4. **Add Tests:** Unit and integration tests for all components
5. **Documentation:** API client libraries, tutorials

---

## Support

For questions or issues:

1. Check the troubleshooting section above
2. Review API documentation at `/docs`
3. Check logs: `docker-compose logs -f`
4. Review code comments in implementation files

---

**Phase 0 Complete!** <‰

The platform now has production-ready infrastructure for:
- User authentication and authorization
- Database persistence with connection pooling
- Background job processing
- Rate limiting and error handling
- Health monitoring
- Local development environment

Ready to build the next generation of academic research tools!
