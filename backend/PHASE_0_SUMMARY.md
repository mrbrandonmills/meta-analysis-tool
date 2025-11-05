# Phase 0 Backend Infrastructure - Quick Reference

## What Was Built

Phase 0 (2-week sprint) delivered production-ready infrastructure:

### ✅ 1. Database Layer (`/app/db/`)
- **session.py** - Async database sessions with connection pooling
- **base.py** - Sync database sessions
- Features: Auto-commit/rollback, transaction management, connection lifecycle

### ✅ 2. Authentication System (`/app/core/security.py`, `/app/api/v1/auth.py`)
- JWT tokens (access + refresh)
- Password hashing (bcrypt)
- Role-based access control (admin, researcher, reviewer, viewer)
- API key management
- OAuth2 password flow

### ✅ 3. User Models (`/app/models/user.py`)
- User table with roles
- API key table for programmatic access
- Pydantic schemas for validation

### ✅ 4. Background Jobs (`/app/workers/`)
- Celery + Redis setup
- Task queues (search, analysis, reviewer, notifications)
- Sample tasks for literature search and meta-analysis
- Progress tracking and error handling

### ✅ 5. Middleware (`/app/core/middleware.py`)
- Rate limiting (Redis-backed, 100 req/min authenticated, 20 req/min unauthenticated)
- RFC 7807 Problem Details error responses
- Pagination helpers
- Request ID tracking
- Performance monitoring

### ✅ 6. Health Checks (`/app/api/v1/health.py`)
- `/health` - Basic check
- `/health/detailed` - Database, Redis, Celery status
- `/health/live` - Kubernetes liveness probe
- `/health/ready` - Kubernetes readiness probe
- `/health/metrics` - System metrics (admin only)

### ✅ 7. Infrastructure
- **docker-compose.yml** - PostgreSQL, Redis, Backend, Celery, Flower
- **.env.example** - Environment template
- **Updated main.py** - Integrated all components

## Quick Start

```bash
# 1. Create .env file
cp backend/.env.example backend/.env
# Edit .env and add your ANTHROPIC_API_KEY and SECRET_KEY

# 2. Start all services
docker-compose up -d

# 3. Check health
curl http://localhost:8000/api/v1/health

# 4. View API docs
open http://localhost:8000/docs

# 5. Monitor Celery
open http://localhost:5555
```

## Key Files Created

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── auth.py          # Authentication endpoints
│   │   └── health.py        # Health check endpoints
│   ├── core/
│   │   ├── middleware.py    # Rate limiting, pagination, errors
│   │   └── security.py      # JWT, password hashing, RBAC
│   ├── db/
│   │   ├── base.py          # Sync database sessions
│   │   └── session.py       # Async database sessions
│   ├── models/
│   │   └── user.py          # User and API key models
│   └── workers/
│       ├── celery_app.py    # Celery configuration
│       └── tasks/
│           ├── literature_search.py
│           ├── meta_analysis.py
│           ├── reviewer_tasks.py
│           └── notifications.py
├── .env.example             # Environment template
├── requirements.txt         # Updated dependencies
└── requirements.production.txt  # Updated prod dependencies

docker-compose.yml           # Local development setup
PHASE_0_SETUP.md            # Comprehensive documentation
```

## API Endpoints Added

### Authentication
```
POST   /api/v1/auth/register       # Register new user
POST   /api/v1/auth/login          # Login (OAuth2 password flow)
POST   /api/v1/auth/refresh        # Refresh access token
GET    /api/v1/auth/me             # Get current user
POST   /api/v1/auth/api-keys       # Create API key
GET    /api/v1/auth/api-keys       # List API keys
DELETE /api/v1/auth/api-keys/{id}  # Delete API key
POST   /api/v1/auth/logout         # Logout
```

### Health Checks
```
GET /api/v1/health                  # Basic health
GET /api/v1/health/detailed         # Detailed with dependencies
GET /api/v1/health/live            # Liveness probe
GET /api/v1/health/ready           # Readiness probe
GET /api/v1/health/metrics         # System metrics (admin)
GET /api/v1/health/version         # Version info
```

## Usage Examples

### 1. Register and Login

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "researcher@example.com", "password": "SecurePass123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=researcher@example.com&password=SecurePass123"

# Returns:
# {
#   "access_token": "eyJhbGci...",
#   "refresh_token": "eyJhbGci...",
#   "token_type": "bearer",
#   "expires_in": 1800
# }
```

### 2. Use Protected Endpoint

```bash
# Get current user
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### 3. Submit Background Task

```python
from app.workers.tasks.literature_search import search_databases

# Submit task
task = search_databases.delay(
    query="COVID-19 vaccines",
    databases=["pubmed", "arxiv"],
    max_results=1000
)

# Check status
from app.workers.celery_app import get_task_status
status = get_task_status(task.id)
```

### 4. Role-Based Access

```python
from app.core.security import require_admin, require_researcher
from fastapi import Depends

# Admin only
@router.post("/admin-endpoint")
async def admin_only(token = Depends(require_admin)):
    return {"message": "Admin access granted"}

# Researcher or admin
@router.post("/researcher-endpoint")
async def researcher_only(token = Depends(require_researcher)):
    return {"message": "Researcher access granted"}
```

## Dependencies Added

- **python-jose** - JWT token handling
- **passlib** - Password hashing
- **asyncpg** - Async PostgreSQL driver
- **aiosqlite** - Async SQLite driver
- **celery** - Background task queue
- **flower** - Celery monitoring
- **alembic** - Database migrations

## Next Steps

1. **Database Architect**: Complete schema for Projects, Workflows, Papers, Researchers
2. **Add Alembic migrations**: Initialize and create first migration
3. **Add tests**: Unit tests for security, integration tests for auth flow
4. **Complete Tool 1**: DataExtractionAgent and StatisticalAgent
5. **Begin Tool 4**: Expert Reviewer Matcher

## Monitoring

- **Backend logs**: `docker-compose logs -f backend`
- **Celery logs**: `docker-compose logs -f celery_worker`
- **Database logs**: `docker-compose logs -f postgres`
- **Celery monitoring**: http://localhost:5555 (Flower)
- **API docs**: http://localhost:8000/docs

## Troubleshooting

See PHASE_0_SETUP.md for detailed troubleshooting guide.

Quick fixes:
```bash
# Restart all services
docker-compose restart

# Rebuild backend
docker-compose up -d --build backend

# View logs
docker-compose logs -f

# Check service health
curl http://localhost:8000/api/v1/health/detailed
```

---

**Phase 0 Status: COMPLETE ✅**

All foundational infrastructure is in place. Ready to build Tools 2-4!
