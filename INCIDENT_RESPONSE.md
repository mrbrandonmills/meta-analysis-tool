# Incident Response Runbook
## Meta-Analysis Research Platform

**Version:** 1.0
**Last Updated:** November 4, 2025

---

## Table of Contents

1. [Incident Classification](#incident-classification)
2. [Response Procedures](#response-procedures)
3. [Incident Playbooks](#incident-playbooks)
4. [Communication](#communication)
5. [Post-Incident](#post-incident)
6. [Contact Information](#contact-information)

---

## Incident Classification

### Severity Levels

| Level | Impact | Response Time | Examples |
|-------|--------|---------------|----------|
| **P0 - Critical** | Complete service outage | 15 minutes | API down, database corruption |
| **P1 - High** | Major functionality impaired | 1 hour | Slow responses, agent failures |
| **P2 - Medium** | Minor functionality impaired | 4 hours | Single feature broken |
| **P3 - Low** | Minimal impact | 1 business day | UI glitch, documentation error |

### Incident Examples

**P0 - Critical:**
- API health check failing
- Database unavailable
- 100% error rate
- Security breach
- Data loss

**P1 - High:**
- Error rate > 10%
- P95 latency > 10 seconds
- Workers not processing tasks
- External API (Claude) down
- Memory leak causing crashes

**P2 - Medium:**
- Single agent failing
- Slow database queries
- Cache misses
- Non-critical feature broken

**P3 - Low:**
- UI rendering issue
- Documentation out of date
- Non-critical bug
- Performance optimization needed

---

## Response Procedures

### General Incident Response Flow

```
1. DETECT
   └─> Automated alert OR Manual report
        │
2. ASSESS
   └─> Determine severity (P0-P3)
        │
3. RESPOND
   └─> Follow appropriate playbook
        │
4. MITIGATE
   └─> Restore service
        │
5. COMMUNICATE
   └─> Update stakeholders
        │
6. RESOLVE
   └─> Implement permanent fix
        │
7. DOCUMENT
   └─> Write post-mortem
```

### On-Call Responsibilities

**When you receive an alert:**

1. **Acknowledge** within 5 minutes
2. **Assess** severity within 10 minutes
3. **Update** status page
4. **Escalate** if needed
5. **Resolve** or hand off
6. **Document** actions taken

### Escalation Path

```
On-call Engineer
    └─> If unresolved in 30 min
        │
Senior Engineer
    └─> If unresolved in 1 hour
        │
Engineering Manager
    └─> If unresolved in 2 hours
        │
CTO / CEO
```

---

## Incident Playbooks

### P0-1: API Health Check Failing

**Symptoms:**
- `/health` endpoint returns 500 or times out
- Railway shows service as down
- Users cannot access the application

**Diagnosis:**

```bash
# 1. Check Railway status
railway status --service backend

# 2. Check recent logs
railway logs --service backend --tail 100

# 3. Check resource usage
railway metrics --service backend

# 4. Test database connection
railway run psql -c "SELECT 1;"

# 5. Test Redis connection
railway run redis-cli -u $REDIS_URL ping
```

**Resolution:**

```bash
# Option A: Restart service
railway restart --service backend

# Option B: Redeploy
railway up --service backend

# Option C: Rollback to previous version
railway rollback --service backend

# Option D: Scale up if resource exhaustion
railway up --service backend --replicas 2
```

**Communication Template:**
```
🚨 INCIDENT REPORT - P0
Service: API
Status: INVESTIGATING
Impact: Complete service outage
Started: 2025-11-04 12:00 UTC
Next update: 15 minutes
```

---

### P0-1: Database Connection Errors

**Symptoms:**
- `psycopg2.OperationalError`
- "could not connect to server"
- Database queries timing out

**Diagnosis:**

```bash
# 1. Check database status
railway status --service postgresql

# 2. Check connection pool
railway run psql -c "SELECT count(*) FROM pg_stat_activity;"

# 3. Check active connections
railway run psql -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

# 4. Check for long-running queries
railway run psql -c "
  SELECT pid, now() - query_start as duration, query
  FROM pg_stat_activity
  WHERE state = 'active'
  ORDER BY duration DESC;
"

# 5. Check database size
railway run psql -c "SELECT pg_size_pretty(pg_database_size('meta_analysis'));"
```

**Resolution:**

```bash
# Option A: Kill long-running queries
railway run psql -c "SELECT pg_terminate_backend(PID);"

# Option B: Increase connection pool
# Edit app/core/config.py
SQLALCHEMY_POOL_SIZE = 30  # Increase from 20

# Option C: Restart database (CAUTION!)
railway restart --service postgresql

# Option D: Restore from backup (if corrupted)
./scripts/backup-db.sh production  # Backup first!
./scripts/restore-db.sh backups/latest.sql.gz production
```

**Prevention:**
- Set connection pool limits
- Add query timeout settings
- Monitor slow queries
- Set up connection pool monitoring

---

### P0-1: High Error Rate (>10%)

**Symptoms:**
- Spike in 500 errors
- Sentry showing high error volume
- Users reporting failures

**Diagnosis:**

```bash
# 1. Check error logs
railway logs --service backend | grep ERROR

# 2. Check error rate
curl http://localhost:8000/metrics | grep http_requests_total

# 3. Check Sentry dashboard
open https://sentry.io

# 4. Identify pattern
# - Specific endpoint?
# - Specific error type?
# - Started at specific time?

# 5. Check recent deployments
railway deployments --service backend
```

**Resolution:**

```bash
# Option A: Rollback deployment
railway rollback --service backend

# Option B: Apply hotfix
# Fix code, commit, push
git commit -m "hotfix: fix critical error"
git push origin main

# Option C: Scale horizontally (if overloaded)
railway up --service backend --replicas 3

# Option D: Enable maintenance mode
# Set MAINTENANCE_MODE=true
railway variables set MAINTENANCE_MODE=true
```

**Root Cause Analysis:**
1. What changed? (code, config, dependencies)
2. When did it start? (check deployment times)
3. What's the error pattern? (specific endpoints, users)
4. What's the fix? (code change, config change, rollback)

---

### P0-1: Out of Memory (OOM)

**Symptoms:**
- Service crashes with OOM error
- Logs show memory warnings
- Railway shows 100% memory usage

**Diagnosis:**

```bash
# 1. Check current memory usage
railway metrics --service backend

# 2. Check memory limit
cat railway.toml | grep memoryLimit

# 3. Identify memory leak
railway logs --service backend | grep -i memory

# 4. Check Python memory profiling
# If enabled in code
```

**Resolution:**

```bash
# IMMEDIATE: Restart service
railway restart --service backend

# SHORT-TERM: Increase memory limit
# Edit railway.toml
[deploy.resources]
memoryLimit = 2048  # Increase to 2GB

railway up --service backend

# LONG-TERM: Fix memory leak
# 1. Add memory profiling
# 2. Identify leak
# 3. Fix code
# 4. Deploy fix

# Temporary workaround: Restart on schedule
# Add cron job to restart every 6 hours
```

**Prevention:**
- Set memory limits
- Add memory monitoring
- Implement memory leak detection
- Use memory profiling in staging

---

### P1: Celery Workers Not Processing

**Symptoms:**
- Queue depth increasing
- Tasks stuck in PENDING state
- No worker activity in Flower

**Diagnosis:**

```bash
# 1. Check worker status
railway logs --service worker

# 2. Check Flower dashboard
open http://localhost:5555

# 3. Check queue depth
railway run redis-cli -u $REDIS_URL llen celery

# 4. Check for stuck tasks
railway run celery -A app.tasks.celery_app inspect active

# 5. Check for errors
railway run celery -A app.tasks.celery_app inspect stats
```

**Resolution:**

```bash
# Option A: Restart workers
railway restart --service worker

# Option B: Purge queue (if tasks are old)
railway run celery -A app.tasks.celery_app purge
# WARNING: This deletes all pending tasks!

# Option C: Scale workers
railway up --service worker --replicas 3

# Option D: Revoke stuck tasks
railway run celery -A app.tasks.celery_app revoke <task-id>

# Option E: Reset Redis queue
railway run redis-cli -u $REDIS_URL flushdb
# WARNING: This clears all Redis data!
```

---

### P1: High Latency (P95 > 5s)

**Symptoms:**
- API responses slow
- Users complaining about performance
- Timeout errors

**Diagnosis:**

```bash
# 1. Check metrics
curl http://localhost:8000/metrics | grep duration

# 2. Identify slow endpoints
railway logs --service backend | grep "duration="

# 3. Check database queries
railway run psql -c "
  SELECT query, calls, mean_exec_time
  FROM pg_stat_statements
  ORDER BY mean_exec_time DESC
  LIMIT 10;
"

# 4. Check for N+1 queries
# Enable SQL logging
export DEBUG=true

# 5. Check external API latency
railway logs | grep "claude_api_duration"
```

**Resolution:**

```bash
# SHORT-TERM: Scale horizontally
railway up --service backend --replicas 2

# MEDIUM-TERM: Add caching
# Add Redis caching to slow endpoints
@cache(ttl=300)
def slow_endpoint():
    ...

# LONG-TERM: Optimize queries
# Add database indexes
CREATE INDEX idx_papers_created_at ON papers(created_at);

# Fix N+1 queries
# Use SELECT_IN loading or JOIN
query = query.options(selectinload(Paper.authors))
```

---

### P1: External API Failures (Claude API)

**Symptoms:**
- LLM API calls failing
- "API key invalid" errors
- Rate limit errors

**Diagnosis:**

```bash
# 1. Check API status
curl https://status.anthropic.com

# 2. Check API key
railway variables get ANTHROPIC_API_KEY

# 3. Check rate limits
railway logs | grep "rate_limit"

# 4. Check error pattern
railway logs | grep "anthropic" | grep ERROR

# 5. Test API directly
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

**Resolution:**

```bash
# Option A: Retry with backoff
# Implemented in code - check if working

# Option B: Use fallback model
# Switch to Haiku temporarily
export FALLBACK_MODEL=claude-3-haiku-20240307

# Option C: Queue tasks for later
# If rate limited, queue tasks and retry

# Option D: Use alternative API key
railway variables set ANTHROPIC_API_KEY=<backup-key>
```

---

### P2: Database Slow Queries

**Symptoms:**
- Queries taking > 1 second
- Database CPU high
- Slow page loads

**Diagnosis:**

```bash
# 1. Identify slow queries
railway run psql -c "
  SELECT query, calls, mean_exec_time, max_exec_time
  FROM pg_stat_statements
  WHERE mean_exec_time > 1000
  ORDER BY mean_exec_time DESC
  LIMIT 20;
"

# 2. Check for missing indexes
railway run psql -c "
  SELECT schemaname, tablename, attname, n_distinct
  FROM pg_stats
  WHERE schemaname = 'public'
  AND n_distinct < 100;
"

# 3. Check table sizes
railway run psql -c "
  SELECT tablename, pg_size_pretty(pg_total_relation_size(tablename::regclass))
  FROM pg_tables
  WHERE schemaname = 'public'
  ORDER BY pg_total_relation_size(tablename::regclass) DESC;
"

# 4. Analyze query plan
railway run psql -c "EXPLAIN ANALYZE <slow-query>;"
```

**Resolution:**

```bash
# Add indexes
railway run psql -c "
  CREATE INDEX idx_papers_title ON papers(title);
  CREATE INDEX idx_papers_created_at ON papers(created_at);
"

# Vacuum database
railway run psql -c "VACUUM ANALYZE;"

# Update statistics
railway run psql -c "ANALYZE;"

# Rewrite query
# Optimize in code, redeploy
```

---

### P2: Cache Misses

**Symptoms:**
- High database load
- Redis cache not being used
- Slow response times

**Diagnosis:**

```bash
# 1. Check Redis stats
railway run redis-cli -u $REDIS_URL INFO stats

# 2. Check cache hit rate
# Hits / (Hits + Misses)

# 3. Check cache keys
railway run redis-cli -u $REDIS_URL KEYS "*"

# 4. Check TTL
railway run redis-cli -u $REDIS_URL TTL <key>
```

**Resolution:**

```bash
# Increase cache TTL
@cache(ttl=3600)  # 1 hour instead of 5 minutes

# Warm cache
# Run cache warming script

# Increase Redis memory
# Edit railway.toml for Redis service
```

---

### P3: UI Rendering Issues

**Symptoms:**
- Frontend not loading correctly
- JavaScript errors
- CSS not applying

**Diagnosis:**

```bash
# 1. Check Vercel deployment
vercel inspect <deployment-url>

# 2. Check browser console
# Open DevTools > Console

# 3. Check API connectivity
curl https://meta-analysis-api.railway.app/health

# 4. Check environment variables
vercel env ls
```

**Resolution:**

```bash
# Redeploy frontend
cd frontend
vercel --prod

# Clear CDN cache
vercel redeploy --no-build

# Rollback deployment
vercel rollback
```

---

## Communication

### Status Page Updates

**Template:**

```markdown
🚨 **INVESTIGATING** - API Performance Degradation
- **Started:** 2025-11-04 12:00 UTC
- **Impact:** Some requests experiencing delays
- **Status:** Engineering team investigating
- **Next Update:** 12:15 UTC
```

```markdown
⚠️ **IDENTIFIED** - Database Connection Pool Exhaustion
- **Started:** 2025-11-04 12:00 UTC
- **Impact:** Some requests experiencing delays
- **Cause:** Connection pool exhausted
- **Fix:** Restarting database connections
- **Next Update:** 12:30 UTC
```

```markdown
✅ **RESOLVED** - API Performance Restored
- **Started:** 2025-11-04 12:00 UTC
- **Resolved:** 2025-11-04 12:45 UTC
- **Duration:** 45 minutes
- **Impact:** Some requests experienced 3-5s delays
- **Cause:** Database connection pool exhaustion
- **Fix:** Restarted connections, increased pool size
- **Prevention:** Added connection pool monitoring
```

### Stakeholder Communication

**Internal (Slack):**
```
#incidents channel:
🚨 P0 INCIDENT - API Down
- Impact: Complete outage
- Started: 12:00 UTC
- Owner: @engineer
- War room: #incident-2025-11-04
```

**External (Email/Twitter):**
```
Subject: Service Disruption - Meta-Analysis Platform

We're experiencing a service disruption affecting API availability.
Our team is actively working on a resolution.

Started: 12:00 UTC
Impact: API requests may fail
Status: https://status.example.com
Updates: Every 15 minutes

We apologize for the inconvenience.
```

---

## Post-Incident

### Post-Mortem Template

```markdown
# Incident Post-Mortem

**Incident ID:** INC-2025-11-04-001
**Date:** 2025-11-04
**Severity:** P0
**Duration:** 45 minutes
**Author:** Engineer Name

## Summary
Brief description of what happened.

## Timeline
- 12:00 UTC: Alert triggered
- 12:05 UTC: Engineer acknowledged
- 12:15 UTC: Root cause identified
- 12:30 UTC: Fix deployed
- 12:45 UTC: Incident resolved

## Root Cause
What caused the incident?

## Impact
- Users affected: ~1,000
- Requests failed: ~5,000
- Revenue impact: $0
- SLA impact: 99.9% → 99.5%

## Resolution
How was it fixed?

## Prevention
What will we do to prevent this?

## Action Items
- [ ] Add monitoring for X (@engineer, due: 2025-11-11)
- [ ] Update runbook (@engineer, due: 2025-11-05)
- [ ] Improve alerting (@engineer, due: 2025-11-08)

## Lessons Learned
What did we learn?
```

### Blameless Post-Mortem

Focus on:
- What happened (facts)
- Why it happened (root cause)
- How to prevent it (action items)

**NOT:**
- Who caused it
- Who to blame
- Who made mistakes

---

## Contact Information

### On-Call Rotation

| Week | Primary | Backup |
|------|---------|--------|
| Week 1 | Engineer A | Engineer B |
| Week 2 | Engineer B | Engineer C |
| Week 3 | Engineer C | Engineer A |

### Escalation Contacts

| Role | Name | Contact |
|------|------|---------|
| On-Call Engineer | Rotating | PagerDuty |
| Senior Engineer | Name | phone/slack |
| Engineering Manager | Name | phone/slack |
| CTO | Name | phone/slack |

### External Contacts

| Service | Support | URL |
|---------|---------|-----|
| Railway | support@railway.app | https://railway.app/support |
| Vercel | support@vercel.com | https://vercel.com/support |
| Anthropic | support@anthropic.com | https://support.anthropic.com |
| Sentry | support@sentry.io | https://sentry.io/support |

### Useful Links

- **Status Page:** https://status.example.com
- **Grafana:** https://grafana.example.com
- **Sentry:** https://sentry.io/meta-analysis
- **Railway:** https://railway.app/dashboard
- **Documentation:** https://github.com/example/meta-analysis-tool
- **Runbooks:** This document

---

## Appendix: Common Commands

### Railway

```bash
# View logs
railway logs --service backend

# Restart service
railway restart --service backend

# Check status
railway status

# Deploy
railway up

# Rollback
railway rollback --service backend

# Run command
railway run <command>

# Get variables
railway variables get <name>

# Set variables
railway variables set KEY=value
```

### Docker

```bash
# View logs
docker-compose logs -f backend

# Restart
docker-compose restart backend

# Rebuild
docker-compose up --build backend

# Execute command
docker-compose exec backend <command>

# View running containers
docker-compose ps
```

### Database

```bash
# Connect
psql $DATABASE_URL

# Backup
./scripts/backup-db.sh production

# Restore
./scripts/restore-db.sh backup.sql.gz local

# Run migrations
alembic upgrade head

# Check status
psql -c "SELECT version();"
```

---

**Last Updated:** November 4, 2025
**Version:** 1.0
**Next Review:** February 4, 2026
