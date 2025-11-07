# Code Changes Summary - PostgreSQL Persistence

## Quick Reference for Reviewing Changes

### 1. Service Layer (NEW FILE)

**File:** `/backend/app/services/meta_analysis_service.py`

```python
class MetaAnalysisService:
    """Service for persisting and retrieving meta-analysis state."""

    def __init__(self, db: Session):
        self.db = db

    # Core methods:
    def create_meta_analysis(...)       # Create new meta-analysis
    def save_coordinator_state(...)     # Persist coordinator state
    def get_meta_analysis(...)          # Retrieve meta-analysis
    def get_coordinator_state(...)      # Retrieve coordinator state
    def restore_coordinator(...)        # Restore coordinator from DB
    def update_meta_analysis_status(...) # Update status
    def log_agent_execution(...)        # Log agent execution
```

### 2. API Endpoints Changes

**File:** `/backend/app/api/v1/meta_analysis.py`

#### Import Changes
```python
# ADDED
from app.models.meta_analysis import MetaAnalysisStatus
from app.services.meta_analysis_service import MetaAnalysisService

# REMOVED
coordinators_by_id: dict[str, CoordinatorAgent] = {}
```

#### Endpoint: POST /meta-analysis/create

**Before:**
```python
@router.post("/meta-analysis/create", response_model=MetaAnalysisResponse)
async def create_meta_analysis(request: MetaAnalysisRequest):
    # Create coordinator
    coordinator = CoordinatorAgent(coordinator_config)

    # Store in memory dict
    analysis_id = str(coordinator.id)
    coordinators_by_id[analysis_id] = coordinator

    # Process request
    result = await coordinator.process(request.model_dump())

    return MetaAnalysisResponse(...)
```

**After:**
```python
@router.post("/meta-analysis/create", response_model=MetaAnalysisResponse)
async def create_meta_analysis(
    request: MetaAnalysisRequest,
    db: Session = Depends(get_db),  # ADDED
):
    # Initialize service
    service = MetaAnalysisService(db)

    # Create meta-analysis in database
    meta_analysis = service.create_meta_analysis(
        user_id=user.id,
        research_question=request.research_question,
        topic=request.topic,
        # ... other fields
    )

    # Create coordinator
    coordinator = CoordinatorAgent(coordinator_config)

    # Process request
    result = await coordinator.process(request.model_dump())

    # Save coordinator state to database
    service.save_coordinator_state(
        analysis_id=meta_analysis.id,
        coordinator=coordinator,
        workflow_plan=result,
    )

    # Update status
    service.update_meta_analysis_status(
        analysis_id=meta_analysis.id,
        status=MetaAnalysisStatus.WORKFLOW_CREATED,
    )

    # Log execution
    service.log_agent_execution(
        analysis_id=meta_analysis.id,
        agent_name=coordinator.config.name,
        agent_role="coordinator",
        agent_id=coordinator.id,
        input_data=request.model_dump(),
        output_data=result,
        status="success",
    )

    db.commit()  # ADDED

    return MetaAnalysisResponse(
        id=str(meta_analysis.id),  # Use database ID
        # ...
    )
```

#### Endpoint: POST /meta-analysis/execute/{analysis_id}

**Before:**
```python
@router.post("/meta-analysis/execute/{analysis_id}")
async def execute_meta_analysis(analysis_id: str):
    # Get coordinator from in-memory dict
    coordinator = coordinators_by_id.get(analysis_id)
    if not coordinator:
        raise HTTPException(status_code=404, ...)

    # Execute agents
    search_results = await search_agent.process(search_input)
    screening_results = await screening_agent.process(screening_input)

    return {...}
```

**After:**
```python
@router.post("/meta-analysis/execute/{analysis_id}")
async def execute_meta_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),  # ADDED
):
    # Initialize service
    service = MetaAnalysisService(db)

    # Get meta-analysis from database
    analysis_uuid = UUID(analysis_id)
    meta_analysis = service.get_meta_analysis(analysis_uuid)
    if not meta_analysis:
        raise HTTPException(status_code=404, ...)

    # Restore coordinator from database
    coordinator = service.restore_coordinator(analysis_uuid, coordinator_config)
    if not coordinator:
        raise HTTPException(status_code=404, ...)

    # Update status
    service.update_meta_analysis_status(analysis_uuid, MetaAnalysisStatus.IN_PROGRESS)

    # Execute search agent
    search_results = await search_agent.process(search_input)
    service.log_agent_execution(...)  # Log execution

    # Execute screening agent
    screening_results = await screening_agent.process(screening_input)
    service.log_agent_execution(...)  # Log execution

    # Execute credibility agent
    credibility_results = await credibility_agent.process(credibility_input)
    service.log_agent_execution(...)  # Log execution

    # Update coordinator state
    service.save_coordinator_state(analysis_uuid, coordinator)

    db.commit()  # ADDED

    return {...}
```

#### Endpoint: GET /meta-analysis/status/{analysis_id}

**Before:**
```python
@router.get("/meta-analysis/status/{analysis_id}")
async def get_status(analysis_id: str):
    # Get coordinator from in-memory dict
    coordinator = coordinators_by_id.get(analysis_id)
    if not coordinator:
        raise HTTPException(status_code=404, ...)

    return {
        "id": analysis_id,
        "status": coordinator.status,
        "decisions": len(coordinator.decisions),
    }
```

**After:**
```python
@router.get("/meta-analysis/status/{analysis_id}")
async def get_status(analysis_id: str, db: Session = Depends(get_db)):
    service = MetaAnalysisService(db)

    # Get meta-analysis from database
    analysis_uuid = UUID(analysis_id)
    meta_analysis = service.get_meta_analysis(analysis_uuid)
    if not meta_analysis:
        raise HTTPException(status_code=404, ...)

    # Get coordinator state
    coordinator_state = service.get_coordinator_state(analysis_uuid)

    return {
        "id": analysis_id,
        "status": meta_analysis.status.value,  # From database
        "decisions": len(coordinator_state.decisions) if coordinator_state else 0,
        "created_at": meta_analysis.created_at.isoformat(),
        "updated_at": meta_analysis.updated_at.isoformat(),
    }
```

### 3. Alembic Configuration

**File:** `/backend/alembic/env.py`

```python
# ADDED imports
from app.models import (
    # ... existing imports ...
    MetaAnalysis,
    CoordinatorState,
    AgentExecution,
    PDFMetadata,
    FullTextExtraction,
    FullTextScreening,
    Report,
    ReportTemplate,
)
```

### 4. Key Patterns Used

#### Transaction Management
```python
try:
    service.create_meta_analysis(...)
    service.save_coordinator_state(...)
    service.log_agent_execution(...)
    db.commit()  # All or nothing
except Exception as e:
    db.rollback()  # Revert everything
    raise HTTPException(...)
```

#### State Serialization
```python
def _serialize_coordinator_state(self, coordinator: CoordinatorAgent) -> Dict:
    return {
        "status": coordinator.status,
        "context": coordinator.context,
        "config": {
            "name": coordinator.config.name,
            "role": coordinator.config.role.value,
            "expert_profile": coordinator.config.expert_profile,
        },
    }
```

#### State Restoration
```python
def restore_coordinator(self, analysis_id: UUID, config: AgentConfig):
    state = self.get_coordinator_state(analysis_id)

    coordinator = CoordinatorAgent(config)
    coordinator.id = state.coordinator_id
    coordinator.decisions = state.decisions

    if state.agent_state:
        coordinator.status = state.agent_state["status"]
        coordinator.context = state.agent_state["context"]

    return coordinator
```

### 5. Database Tables Used

#### meta_analyses
Stores core meta-analysis information
- Created by: `service.create_meta_analysis()`
- Updated by: `service.update_meta_analysis_status()`
- Retrieved by: `service.get_meta_analysis()`

#### coordinator_states
Stores coordinator agent state
- Created/Updated by: `service.save_coordinator_state()`
- Retrieved by: `service.get_coordinator_state()`
- Used by: `service.restore_coordinator()`

#### agent_executions
Stores audit trail of agent executions
- Created by: `service.log_agent_execution()`
- Queried via: `meta_analysis.agent_executions` relationship

### 6. Testing the Changes

#### Local Testing (with PostgreSQL)
```bash
# Start PostgreSQL
docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres

# Update .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/meta_analysis

# Run migrations
alembic upgrade head

# Test endpoints
curl -X POST http://localhost:8000/api/v1/meta-analysis/create -d '{...}'
curl -X POST http://localhost:8000/api/v1/meta-analysis/execute/{id}
curl http://localhost:8000/api/v1/meta-analysis/status/{id}
```

#### Railway Testing
```bash
# After deployment
curl https://your-app.railway.app/api/v1/health
curl -X POST https://your-app.railway.app/api/v1/meta-analysis/create -d '{...}'
```

### 7. Migration Flow

```
1. User creates meta-analysis
   ↓
2. MetaAnalysis record created in database
   ↓
3. Coordinator agent initialized
   ↓
4. Workflow created by coordinator
   ↓
5. CoordinatorState saved to database
   ↓
6. AgentExecution logged
   ↓
7. Status updated to workflow_created
   ↓
8. All changes committed to database
```

### 8. Error Handling Examples

```python
# Handle invalid UUID
try:
    analysis_uuid = UUID(analysis_id)
except ValueError:
    raise HTTPException(status_code=400, detail="Invalid analysis ID format")

# Handle not found
meta_analysis = service.get_meta_analysis(analysis_uuid)
if not meta_analysis:
    raise HTTPException(status_code=404, detail="Meta-analysis not found")

# Handle database errors
try:
    db.commit()
except Exception as e:
    db.rollback()
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database error")
```

### 9. Key Differences Summary

| Aspect | Before (In-Memory) | After (Database) |
|--------|-------------------|------------------|
| Storage | Python dict | PostgreSQL |
| Persistence | Lost on restart | Persists forever |
| Workers | 1 only | 4+ workers |
| Recovery | No recovery | Auto recovery |
| Audit Trail | None | Full history |
| Scalability | Not scalable | Horizontally scalable |
| State Access | `dict.get()` | `service.get_meta_analysis()` |
| State Save | `dict[id] = obj` | `service.save_coordinator_state()` |

### 10. Deployment Changes Needed

**Environment Variables (Railway):**
```bash
# Auto-set by Railway when you add PostgreSQL
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Required API keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Configuration
DEBUG=false
LOG_LEVEL=INFO
```

**No code changes needed for deployment!**
- Dockerfile already configured with 4 workers
- Migration will run automatically
- Application will connect to Railway PostgreSQL

---

## Review Checklist

When reviewing the code changes:

- [ ] Service layer properly handles database operations
- [ ] All endpoints use database session dependency
- [ ] Transactions are properly committed/rolled back
- [ ] Error handling includes database errors
- [ ] UUIDs are validated before database queries
- [ ] Coordinator state is serialized correctly
- [ ] Agent executions are logged with full context
- [ ] Status updates are persisted to database
- [ ] In-memory dict is completely removed
- [ ] No coordinator state stored in application memory

## Files to Review

1. `/backend/app/services/meta_analysis_service.py` (NEW)
2. `/backend/app/api/v1/meta_analysis.py` (MODIFIED)
3. `/backend/alembic/env.py` (MODIFIED)

Total lines changed: ~500 lines added, ~50 lines removed

---

**Status:** Ready for code review and deployment
