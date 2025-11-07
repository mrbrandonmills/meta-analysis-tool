# Railway Deployment Guide - PostgreSQL Persistence

## Quick Start

This guide walks you through deploying the meta-analysis backend with PostgreSQL persistence on Railway.

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository connected to Railway
- Environment variables configured

## Step-by-Step Deployment

### Step 1: Add PostgreSQL Database

1. Open your Railway project dashboard
2. Click **"New"** → **"Database"** → **"PostgreSQL"**
3. Railway will automatically:
   - Provision a PostgreSQL instance
   - Set the `DATABASE_URL` environment variable
   - Link it to your backend service

### Step 2: Verify Environment Variables

In your Railway backend service, ensure these variables are set:

```bash
# Automatically set by Railway
DATABASE_URL=postgresql://...

# Required API keys
ANTHROPIC_API_KEY=sk-ant-api-...
OPENAI_API_KEY=sk-...

# Optional configuration
DEBUG=false
LOG_LEVEL=INFO
```

### Step 3: Deploy Application

Railway will automatically deploy when you push to your connected branch:

```bash
git add .
git commit -m "Add PostgreSQL persistence for horizontal scaling"
git push origin main
```

Or trigger manual deployment:
1. Go to Railway dashboard
2. Click your backend service
3. Click **"Deploy"** → **"Deploy Now"**

### Step 4: Monitor Deployment

Watch the deployment logs in Railway:

```
Building Docker image...
✓ Stage 1: Builder completed
✓ Stage 2: Runtime completed
Running database migrations...
✓ Alembic migration 004_add_meta_analysis_tables applied
Starting uvicorn with 4 workers...
✓ Worker 1 started
✓ Worker 2 started
✓ Worker 3 started
✓ Worker 4 started
Application ready on port 8000
```

### Step 5: Verify Deployment

#### Check Health Endpoint

```bash
curl https://your-app.railway.app/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "workers": 4
}
```

#### Test Meta-Analysis Creation

```bash
curl -X POST https://your-app.railway.app/api/v1/meta-analysis/create \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "What are the effects of mindfulness meditation on anxiety in adults?",
    "topic": "Mindfulness and Anxiety Meta-Analysis",
    "inclusion_criteria": [
      "Randomized controlled trial",
      "Adult population (18+)",
      "Mindfulness-based intervention",
      "Anxiety as outcome measure"
    ],
    "exclusion_criteria": [
      "Non-English language",
      "Qualitative studies",
      "Case studies"
    ],
    "databases": ["pubmed", "arxiv"],
    "peer_review_only": false
  }'
```

Expected response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "workflow_created",
  "message": "Meta-analysis workflow created successfully",
  "workflow": {
    "steps": [...]
  }
}
```

#### Check Status

```bash
# Use the ID from the create response
curl https://your-app.railway.app/api/v1/meta-analysis/status/550e8400-e29b-41d4-a716-446655440000
```

Expected response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "workflow_created",
  "decisions": 2,
  "created_at": "2025-11-06T20:00:00Z",
  "updated_at": "2025-11-06T20:00:00Z"
}
```

#### Execute Meta-Analysis

```bash
curl -X POST https://your-app.railway.app/api/v1/meta-analysis/execute/550e8400-e29b-41d4-a716-446655440000
```

Expected response:
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in_progress",
  "search_results": {
    "total_found": 150,
    "databases": ["pubmed"]
  },
  "screening_results": {
    "total_screened": 150,
    "included": 75,
    "excluded": 70,
    "uncertain": 5
  },
  "credibility_results": {
    "total_evaluated": 75,
    "breakdown": {...}
  }
}
```

## Database Verification

### View Tables in Railway PostgreSQL

1. Go to Railway dashboard
2. Click your PostgreSQL service
3. Click **"Data"** tab
4. View tables:
   - `meta_analyses`
   - `coordinator_states`
   - `agent_executions`
   - `users`

### Query Database Directly

Use Railway's built-in query tool or connect with psql:

```bash
# Get DATABASE_URL from Railway
railway run psql $DATABASE_URL

# View meta-analyses
SELECT id, topic, status, created_at FROM meta_analyses;

# View coordinator states
SELECT analysis_id, coordinator_id, created_at FROM coordinator_states;

# View agent execution audit trail
SELECT agent_name, agent_role, status, executed_at
FROM agent_executions
WHERE analysis_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY executed_at;
```

## Troubleshooting

### Issue: Migration Not Running

**Symptom:** Tables not created in database

**Solution:**
```bash
# Connect to Railway environment
railway run alembic upgrade head

# Or check migration status
railway run alembic current
```

### Issue: Workers Not Starting

**Symptom:** Logs show "failed to start workers"

**Solution:**
- Check DATABASE_URL is set correctly
- Verify PostgreSQL service is running
- Check for port conflicts in logs

### Issue: State Not Persisting

**Symptom:** Meta-analysis not found after creation

**Solution:**
- Check database connection in logs
- Verify transactions are committing
- Look for rollback errors in logs

### Issue: Slow Performance

**Symptom:** API requests taking >5 seconds

**Solution:**
- Check PostgreSQL query performance in Railway
- Verify connection pool isn't exhausted
- Consider adding Redis caching layer

## Monitoring

### Application Logs

View logs in Railway dashboard:
- Deployment logs
- Runtime logs
- Error logs

Filter by worker:
```bash
# In Railway logs filter
worker 1
worker 2
worker 3
worker 4
```

### Database Metrics

Monitor in Railway PostgreSQL dashboard:
- Connection count
- Query performance
- Storage usage
- Cache hit ratio

### Health Checks

Railway automatically monitors:
- HTTP health endpoint (every 30s)
- Container restart on failure
- Automatic scaling if needed

## Scaling

### Horizontal Scaling (More Workers)

Edit Dockerfile line 83:
```dockerfile
# From 4 to 8 workers
CMD ... --workers 8
```

Recommended worker count:
- Development: 1-2 workers
- Staging: 2-4 workers
- Production: 4-8 workers

### Vertical Scaling (Bigger Database)

In Railway PostgreSQL settings:
- Increase memory allocation
- Upgrade to dedicated PostgreSQL instance
- Enable read replicas for heavy read loads

### Caching Layer

Add Redis for hot data:
```bash
# In Railway dashboard
New → Database → Redis

# Update backend to cache coordinator states
# (Future enhancement)
```

## Backup and Recovery

### Automated Backups

Railway PostgreSQL includes:
- Automatic daily backups (retained 7 days)
- Point-in-time recovery
- One-click restore

### Manual Backup

```bash
# Backup database
railway run pg_dump $DATABASE_URL > backup.sql

# Restore from backup
railway run psql $DATABASE_URL < backup.sql
```

### State Recovery

If application crashes:
1. Railway restarts container automatically
2. Application loads state from database
3. Execution continues from last saved checkpoint
4. Audit trail shows exactly where it stopped

## Security

### Database Security

Railway PostgreSQL includes:
- Encrypted connections (SSL)
- Isolated network per project
- Automatic security patches
- No public internet access

### Application Security

Implemented safeguards:
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic models)
- Transaction management (commit/rollback)
- Error handling without data leaks

### API Security

Add authentication (recommended for production):
```python
# In meta_analysis.py endpoints
async def create_meta_analysis(
    request: MetaAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Add this
):
    # Use current_user.id instead of dummy user
```

## Cost Optimization

### Railway Pricing

Estimated monthly costs:
- **Starter Plan**: $5/month
  - PostgreSQL: $5/month (500MB)
  - Backend: Included in Hobby plan

- **Pro Plan**: $20/month
  - PostgreSQL: $10/month (5GB)
  - Backend: Included in Pro plan
  - Priority support

### Optimization Tips

1. **Connection Pooling**: Already configured (10 connections)
2. **Index Optimization**: Indexes on all query columns
3. **JSONB Compression**: PostgreSQL auto-compresses
4. **Archive Old Data**: Delete analyses older than 30 days

## Production Checklist

Before going live:

- [ ] PostgreSQL provisioned and connected
- [ ] Environment variables configured
- [ ] DATABASE_URL verified
- [ ] ANTHROPIC_API_KEY set
- [ ] OPENAI_API_KEY set
- [ ] DEBUG=false
- [ ] Database migrations run successfully
- [ ] Health check endpoint responding
- [ ] Test meta-analysis created successfully
- [ ] Status endpoint working
- [ ] Execute endpoint working
- [ ] Audit trail logging properly
- [ ] Workers (4) all started
- [ ] Logs show no errors
- [ ] Database tables created
- [ ] Indexes created
- [ ] Connection pooling working
- [ ] Backups configured
- [ ] Monitoring enabled

## Support

### Railway Support
- Documentation: https://docs.railway.app
- Discord: https://discord.gg/railway
- GitHub: https://github.com/railwayapp/railway

### Application Issues
- Check logs in Railway dashboard
- Review error messages
- Verify environment variables
- Test database connection
- Check migration status

## Next Steps

After successful deployment:

1. **Add Authentication**: Implement user authentication
2. **Add Redis Caching**: Cache coordinator states
3. **Enable Monitoring**: Set up error tracking (Sentry)
4. **Add Analytics**: Track usage and performance
5. **Implement Rate Limiting**: Prevent API abuse
6. **Add WebSockets**: Real-time status updates
7. **Background Jobs**: Move long tasks to Celery

## Summary

You now have:
- ✅ PostgreSQL database for persistence
- ✅ 4 Uvicorn workers for horizontal scaling
- ✅ Complete audit trail of agent executions
- ✅ Automatic state recovery on crashes
- ✅ Production-ready connection pooling
- ✅ Comprehensive error handling
- ✅ Railway-optimized deployment

**Your meta-analysis API is production-ready with database persistence!**
