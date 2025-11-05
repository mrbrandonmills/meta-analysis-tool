# Database Architecture - Quick Start Guide

## Overview

This document provides quick setup instructions for the multi-tool database architecture. For complete schema documentation, see [DATABASE_SCHEMA.md](/DATABASE_SCHEMA.md).

---

## Prerequisites

- PostgreSQL 14+ (or SQLite for development)
- Python 3.12+
- All dependencies from `requirements.txt`

```bash
pip install sqlalchemy alembic psycopg2-binary asyncpg aiosqlite pydantic-settings passlib
```

---

## Quick Start

### 1. Configure Database Connection

Edit `/Users/brandon/meta-analysis-tool/backend/.env`:

```env
# For PostgreSQL (Production/Staging)
DATABASE_URL=postgresql://user:password@localhost:5432/meta_analysis_db

# For SQLite (Development)
DATABASE_URL=sqlite:///./meta_analysis.db

# Required for migrations
ANTHROPIC_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

### 2. Initialize Database

```bash
cd /Users/brandon/meta-analysis-tool/backend

# Create/upgrade database schema
alembic upgrade head

# Verify migration
alembic current
```

### 3. Seed Sample Data (Optional)

```bash
# Add sample data for development/testing
python -m app.db.seeds

# Clear all data (DANGER!)
python -m app.db.seeds --clear
```

---

## Database Structure

### Core Tables
- **users** - Authentication and user profiles
- **projects** - Universal container for all tool workflows
- **workflows** - Agent execution tracking

### Shared Tables (Multi-Tool)
- **papers** - Academic papers (Tools 1, 2, 3)
- **researchers** - Researcher profiles (Tools 2, 4)

### Tool 1: Meta-Analysis
- Uses: `papers`, `projects`, `workflows`
- Special fields in `papers` for meta-analysis data

### Tool 2: Research Direction
- **research_gaps** - Identified research gaps
- **research_proposals** - AI-generated proposals

### Tool 3: Peer Review
- **manuscripts** - Submitted manuscripts
- **peer_reviews** - Review records

### Tool 4: Reviewer Matcher
- **reviewer_matches** - Reviewer recommendations

### Association Tables
- **project_papers** - Many-to-many: projects ↔ papers
- **project_researchers** - Many-to-many: projects ↔ researchers
- **paper_authors** - Many-to-many: papers ↔ researchers

---

## Common Operations

### Create a Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Review the generated migration file in alembic/versions/
# Edit if needed, then apply:
alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# Rollback all
alembic downgrade base
```

### View Migration History

```bash
# Show current version
alembic current

# Show all migrations
alembic history

# Show verbose history
alembic history --verbose
```

---

## Using Models in Code

### Basic Query Examples

```python
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models import User, Project, Paper

# Create session
db = SessionLocal()

# Query users
users = db.query(User).filter(User.is_active == True).all()

# Get project with relationships
project = db.query(Project).filter(Project.id == project_id).first()
papers = project.papers.all()  # Lazy-loaded relationship

# Create new record
new_user = User(
    email="test@example.com",
    hashed_password=hash_password("password123"),
    name="Test User",
    role="researcher"
)
db.add(new_user)
db.commit()
db.refresh(new_user)

# Update record
user = db.query(User).filter(User.email == "test@example.com").first()
user.name = "Updated Name"
db.commit()

# Soft delete
user.deleted_at = datetime.utcnow()
db.commit()

# Always close session
db.close()
```

### Async Query Examples

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session
from app.models import User, Project

# Async context manager
async with async_session() as db:
    # Query users
    result = await db.execute(select(User).where(User.is_active == True))
    users = result.scalars().all()

    # Get specific user
    result = await db.execute(select(User).where(User.email == "test@example.com"))
    user = result.scalar_one_or_none()

    # Create new record
    new_project = Project(
        user_id=user.id,
        tool_type="meta_analysis",
        title="New Project",
        status="draft"
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
```

### FastAPI Integration

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models import User

router = APIRouter()

@router.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## Performance Optimization

### Indexes

All critical indexes are created by the migration. Key indexes:

- **UUID Primary Keys** - Automatic B-tree indexes
- **Foreign Keys** - Indexed for join performance
- **Full-Text Search** - GIN trigram indexes on text fields
- **JSONB** - GIN indexes for fast JSON queries
- **Status Fields** - Indexed for filtering

### Query Optimization Tips

1. **Use `select_in_load` for relationships**:
```python
from sqlalchemy.orm import selectinload

# Eager load to avoid N+1 queries
projects = db.query(Project).options(
    selectinload(Project.workflows),
    selectinload(Project.papers)
).all()
```

2. **Use database connection pooling**:
Already configured in `app/db/base.py` and `app/db/session.py`

3. **Profile slow queries**:
```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

4. **Batch operations**:
```python
# Instead of multiple commits
users = [User(...) for _ in range(100)]
db.bulk_save_objects(users)
db.commit()
```

---

## Schema Validation

### Check Schema Matches Migration

```bash
# Generate migration to see if models changed
alembic revision --autogenerate -m "check_schema"

# If no changes detected, schema is in sync
# If changes found, review and decide whether to apply
```

### Validate Constraints

```sql
-- Check foreign key constraints
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'public'
  AND tc.constraint_type = 'FOREIGN KEY';

-- Check indexes
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

---

## Backup and Restore

### PostgreSQL

```bash
# Backup
pg_dump -U postgres meta_analysis_db > backup.sql

# Restore
psql -U postgres meta_analysis_db < backup.sql
```

### SQLite

```bash
# Backup
cp meta_analysis.db meta_analysis_backup.db

# Restore
cp meta_analysis_backup.db meta_analysis.db
```

---

## Troubleshooting

### Migration Fails

```bash
# Check current state
alembic current

# Check migration history
alembic history

# Manually mark as current (CAREFUL!)
alembic stamp head
```

### Connection Issues

```python
# Test database connection
from app.db.base import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(result.fetchone())
```

### Model Import Errors

Ensure all models are imported in `app/models/__init__.py` and `alembic/env.py`

---

## File Structure

```
backend/
├── alembic/
│   ├── versions/
│   │   └── 001_multi_tool_schema.py    # Initial migration
│   ├── env.py                           # Alembic environment config
│   └── script.py.mako                   # Migration template
├── alembic.ini                          # Alembic configuration
├── app/
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                      # Sync database session
│   │   ├── session.py                   # Async database session
│   │   └── seeds.py                     # Seed data script
│   └── models/
│       ├── __init__.py                  # Export all models
│       ├── base.py                      # Base model mixins
│       ├── user.py                      # User model
│       ├── project.py                   # Project model
│       ├── workflow.py                  # Workflow model
│       ├── paper.py                     # Paper model
│       ├── researcher.py                # Researcher model
│       ├── manuscript.py                # Manuscript model
│       ├── peer_review.py               # PeerReview model
│       ├── reviewer_match.py            # ReviewerMatch model
│       ├── research_gap.py              # ResearchGap model
│       ├── research_proposal.py         # ResearchProposal model
│       └── associations.py              # Junction tables
└── DATABASE_README.md                   # This file
```

---

## Sample Data

After running `python -m app.db.seeds`, you can log in with:

**Admin:**
- Email: `admin@academic-platform.com`
- Password: `Admin123!`

**Researcher:**
- Email: `researcher@stanford.edu`
- Password: `Research123!`

**Editor:**
- Email: `editor@nature.com`
- Password: `Editor123!`

**Reviewer:**
- Email: `reviewer@mit.edu`
- Password: `Review123!`

---

## Next Steps

1. ✅ Database schema designed and migrated
2. ✅ Sample data loaded
3. 🔄 Integrate with existing agents (Tools 1-4)
4. 🔄 Build API endpoints using these models
5. 🔄 Create frontend components for data visualization

---

## Resources

- **Full Schema Documentation**: [DATABASE_SCHEMA.md](/DATABASE_SCHEMA.md)
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Alembic Docs**: https://alembic.sqlalchemy.org/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

**Last Updated**: November 4, 2025
**Maintained By**: Database Architecture Team
