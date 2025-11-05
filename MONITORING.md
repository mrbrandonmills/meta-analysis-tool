# Monitoring & Observability Guide
## Meta-Analysis Research Platform

**Version:** 1.0
**Last Updated:** November 4, 2025

---

## Table of Contents

1. [Monitoring Stack](#monitoring-stack)
2. [Metrics Collection](#metrics-collection)
3. [Logging](#logging)
4. [Alerting](#alerting)
5. [Dashboards](#dashboards)
6. [Performance Monitoring](#performance-monitoring)
7. [Cost Tracking](#cost-tracking)

---

## Monitoring Stack

### Components

| Component | Purpose | URL |
|-----------|---------|-----|
| **Prometheus** | Metrics collection | http://localhost:9090 |
| **Grafana** | Visualization | http://localhost:3001 |
| **Sentry** | Error tracking | https://sentry.io |
| **Railway Logs** | Application logs | railway logs |
| **Flower** | Celery monitoring | http://localhost:5555 |

### Quick Start

```bash
# Start monitoring stack locally
docker-compose -f docker-compose.prod.yml up prometheus grafana flower

# Access dashboards
open http://localhost:3001  # Grafana (admin/admin)
open http://localhost:5555  # Flower (Celery)
open http://localhost:9090  # Prometheus
```

---

## Metrics Collection

### Application Metrics

#### HTTP Request Metrics

```python
# Automatically collected by MetricsMiddleware

# Counter: Total requests
http_requests_total{method="GET",path="/api/v1/meta-analysis",status="200"}

# Histogram: Request duration
http_request_duration_seconds{method="GET",path="/api/v1/meta-analysis"}
```

#### Agent Execution Metrics

```python
# Counter: Agent executions
agent_executions_total{agent="search",status="success"}

# Histogram: Execution duration
agent_execution_duration_seconds{agent="search"}
```

#### LLM API Metrics

```python
# Counter: API calls
llm_api_calls_total{provider="anthropic",model="claude-3-sonnet"}

# Counter: Token usage
llm_tokens_total{provider="anthropic",model="claude-3-sonnet"}

# Histogram: API latency
llm_api_duration_seconds{provider="anthropic",model="claude-3-sonnet"}
```

#### Database Metrics

```python
# Counter: Query count
database_queries_total{type="select"}

# Histogram: Query duration
database_query_duration_seconds{type="select"}
```

#### Workflow Metrics

```python
# Counter: Workflow events
workflow_events_total{event="started",workflow="meta_analysis"}

# Gauge: Active workflows
active_workflows

# Gauge: Queue size
queue_size{queue="celery"}
```

### System Metrics

Automatically collected by Railway:

- CPU usage (%)
- Memory usage (MB)
- Disk I/O (MB/s)
- Network I/O (MB/s)
- Request rate (req/s)
- Error rate (%)

### Custom Metrics

```python
from app.monitoring.metrics import metrics

# Track custom event
metrics.counter_inc("custom_event", event_type="user_signup")

# Track custom value
metrics.gauge_set("custom_value", 42.0, category="analytics")

# Track custom duration
with metrics.timer("custom_operation"):
    # Your code here
    pass
```

### Metrics Endpoint

```bash
# View metrics in Prometheus format
curl http://localhost:8000/metrics

# Example output:
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/api/v1/health",status="200"} 1523
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 1420
http_request_duration_seconds_sum 142.5
http_request_duration_seconds_count 1523
```

---

## Logging

### Log Structure

All logs are in JSON format for structured querying:

```json
{
  "timestamp": "2025-11-04T12:00:00.123Z",
  "level": "INFO",
  "logger": "app.agents.search",
  "function": "search_papers",
  "line": 42,
  "message": "Searching PubMed for query",
  "request_id": "abc-123-def",
  "extra": {
    "query": "machine learning meta-analysis",
    "database": "pubmed",
    "results": 156
  }
}
```

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| **DEBUG** | Detailed debugging | Variable values, flow control |
| **INFO** | General information | Request received, task completed |
| **WARNING** | Potential issues | API rate limit approaching, slow query |
| **ERROR** | Recoverable errors | API call failed, validation error |
| **CRITICAL** | System failures | Database down, out of memory |

### Logging Best Practices

```python
from app.monitoring import get_structured_logger

logger = get_structured_logger(__name__)

# Good: Structured logging with context
logger.bind(
    user_id=user.id,
    workflow_id=workflow.id,
    agent="search"
).info(f"Starting search for {len(databases)} databases")

# Bad: Unstructured logging
logger.info("Starting search")

# Good: Log errors with context
try:
    result = await search_pubmed(query)
except Exception as e:
    logger.bind(
        query=query,
        error_type=type(e).__name__
    ).error(f"PubMed search failed: {e}")
    raise
```

### Viewing Logs

#### Local Development

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100 backend

# Filter by level
cat logs/app.log | jq 'select(.level == "ERROR")'

# Search for errors
cat logs/app.log | jq 'select(.message | contains("failed"))'
```

#### Production (Railway)

```bash
# View live logs
railway logs --service backend

# Filter by level
railway logs --service backend | grep ERROR

# Follow logs
railway logs --service backend --follow

# Export logs
railway logs --service backend --since 24h > logs.txt
```

### Log Retention

| Environment | Retention | Location |
|------------|-----------|----------|
| Local | 7 days | `logs/` directory |
| Production | 30 days | Railway logs |
| Error logs | 90 days | Sentry |

### Log Rotation

```python
# Configured in logger.py
logger.add(
    "logs/app.log",
    rotation="500 MB",      # Rotate when file reaches 500MB
    retention="7 days",     # Keep logs for 7 days
    compression="gz",       # Compress old logs
)
```

---

## Alerting

### Alert Rules

#### Critical Alerts (Page immediately)

| Alert | Condition | Action |
|-------|-----------|--------|
| **Service Down** | Health check fails for 2 minutes | Page on-call engineer |
| **Database Down** | Cannot connect to PostgreSQL | Page on-call engineer |
| **High Error Rate** | Error rate > 5% for 5 minutes | Page on-call engineer |
| **Out of Memory** | Memory usage > 95% | Auto-restart + page |

#### Warning Alerts (Email notification)

| Alert | Condition | Action |
|-------|-----------|--------|
| **High Latency** | P95 latency > 3s for 10 minutes | Email team |
| **Queue Buildup** | Celery queue > 100 tasks | Email team |
| **API Rate Limit** | Approaching Claude API limit | Email team |
| **High CPU** | CPU > 80% for 15 minutes | Email team |
| **Low Disk Space** | Disk < 20% free | Email team |

### Alert Channels

```yaml
# Configure in Grafana
channels:
  - name: "Critical Alerts"
    type: pagerduty
    url: ${PAGERDUTY_WEBHOOK}

  - name: "Team Notifications"
    type: slack
    url: ${SLACK_WEBHOOK}
    channel: "#alerts"

  - name: "Email Alerts"
    type: email
    addresses: ["team@example.com"]
```

### Alert Rules Configuration

```yaml
# Prometheus alert rules (config/prometheus.yml)

groups:
  - name: api_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}%"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 3
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High API latency"
          description: "P95 latency is {{ $value }}s"

      - alert: QueueBacklog
        expr: queue_size{queue="celery"} > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Celery queue backlog"
          description: "Queue has {{ $value }} pending tasks"
```

### On-Call Rotation

```
Week 1: Engineer A (primary), Engineer B (backup)
Week 2: Engineer B (primary), Engineer C (backup)
Week 3: Engineer C (primary), Engineer A (backup)
```

**On-call responsibilities:**
- Respond to critical alerts within 15 minutes
- Escalate if needed
- Document incidents
- Update runbooks

---

## Dashboards

### Grafana Dashboards

#### 1. System Overview Dashboard

**Metrics displayed:**
- Request rate (requests/second)
- Error rate (%)
- P50/P95/P99 latency
- CPU usage (%)
- Memory usage (MB)
- Active connections

**Refresh:** 10 seconds

#### 2. API Performance Dashboard

**Metrics displayed:**
- Requests by endpoint
- Error rate by endpoint
- Latency by endpoint
- Status code distribution
- Geographic distribution

**Refresh:** 30 seconds

#### 3. Agent Activity Dashboard

**Metrics displayed:**
- Agent executions by type
- Agent success/failure rate
- Agent execution duration
- LLM API calls
- Token usage
- Cost estimate

**Refresh:** 1 minute

#### 4. Database Health Dashboard

**Metrics displayed:**
- Connection pool usage
- Active queries
- Query duration (P95)
- Slow queries (> 1s)
- Cache hit rate
- Table sizes

**Refresh:** 1 minute

#### 5. Queue & Workers Dashboard

**Metrics displayed:**
- Queue depth
- Active workers
- Tasks processed/second
- Task success rate
- Task duration distribution
- Failed tasks

**Refresh:** 30 seconds

### Railway Dashboard

Access at https://railway.app/dashboard

**Metrics displayed:**
- Deployments
- Resource usage
- Database metrics
- Redis metrics
- Billing

### Custom Dashboards

Create custom dashboards in Grafana:

```bash
# 1. Log into Grafana
open http://localhost:3001

# 2. Create new dashboard
Dashboard > New Dashboard

# 3. Add panel
Add Panel > Select metric > Configure

# 4. Save dashboard
Save > Export JSON
```

---

## Performance Monitoring

### Application Performance Monitoring (APM)

#### Sentry Performance

```python
# Initialize Sentry with performance monitoring
init_sentry(
    dsn=settings.sentry_dsn,
    traces_sample_rate=0.1,  # Sample 10% of transactions
    profiles_sample_rate=0.1  # Sample 10% for profiling
)
```

**What gets tracked:**
- HTTP request traces
- Database query traces
- LLM API call traces
- Agent execution traces

#### Performance Tracing

```python
from app.monitoring import sentry

# Manual transaction
with sentry.start_transaction(op="task", name="process_workflow"):
    with sentry.start_span(op="db", description="fetch_papers"):
        papers = fetch_papers()

    with sentry.start_span(op="llm", description="analyze_papers"):
        results = analyze_papers(papers)
```

### Slow Query Detection

```python
# Log slow database queries
from app.monitoring import log_metric

def track_query(query: str, duration: float):
    if duration > 1.0:  # Slow if > 1 second
        log_metric(
            "slow_query",
            duration,
            tags={"query": query[:100]}
        )
```

### Memory Profiling

```python
# Profile memory usage
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Function code
    pass
```

### Load Testing

```bash
# Install locust
pip install locust

# Create load test
# tests/load/locustfile.py

# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Access UI
open http://localhost:8089
```

---

## Cost Tracking

### Infrastructure Costs

#### Railway Cost Dashboard

```bash
# View current usage
railway usage --service backend

# View billing
railway billing

# Set billing alerts
railway billing alerts \
  --threshold 100 \
  --email team@example.com
```

#### Cost Breakdown Dashboard

Create Grafana dashboard to track:

**Compute Costs:**
- API server hours
- Worker hours
- Database hours
- Redis hours

**API Costs:**
- Claude API usage ($)
- PubMed API calls
- Other external APIs

**Storage Costs:**
- Database storage (GB)
- Backup storage (GB)
- Log storage (GB)

**Bandwidth Costs:**
- Ingress (GB)
- Egress (GB)

### LLM API Cost Tracking

```python
from app.monitoring import log_metric

def track_llm_cost(provider: str, model: str, tokens: int):
    # Calculate cost
    cost = calculate_cost(provider, model, tokens)

    # Log metric
    log_metric(
        "llm_api_cost",
        cost,
        unit="USD",
        tags={
            "provider": provider,
            "model": model
        }
    )
```

**Cost per 1M tokens (as of 2025):**
- Claude 3.5 Sonnet: $15 (output) / $3 (input)
- Claude 3 Haiku: $1.25 (output) / $0.25 (input)

### Cost Optimization Alerts

```yaml
# Alert when costs exceed budget
- alert: HighDailyCost
  expr: sum(increase(llm_api_cost[24h])) > 50
  labels:
    severity: warning
  annotations:
    summary: "Daily LLM API costs exceed $50"

- alert: BudgetExceeded
  expr: sum(increase(llm_api_cost[30d])) > 1000
  labels:
    severity: critical
  annotations:
    summary: "Monthly budget exceeded"
```

### Cost Reports

```bash
# Generate monthly cost report
./scripts/generate-cost-report.sh 2025-11

# Output:
# Cost Report: November 2025
# ==========================
# Railway API: $50
# Railway Workers: $100
# Railway PostgreSQL: $50
# Railway Redis: $20
# Claude API: $456
# Vercel: $20
# Sentry: $26
# --------------------------
# Total: $722
```

---

## Best Practices

### 1. Monitoring Checklist

- [ ] All critical endpoints have health checks
- [ ] Alerts configured for critical failures
- [ ] Dashboards created for key metrics
- [ ] Logs are structured and searchable
- [ ] Error tracking enabled (Sentry)
- [ ] Performance monitoring enabled
- [ ] Cost tracking enabled
- [ ] On-call rotation established
- [ ] Incident runbooks created

### 2. Logging Checklist

- [ ] Use structured logging (JSON)
- [ ] Include request ID in all logs
- [ ] Log at appropriate levels
- [ ] Add context to error logs
- [ ] Use consistent field names
- [ ] Sanitize sensitive data
- [ ] Set up log retention
- [ ] Configure log rotation

### 3. Alerting Checklist

- [ ] Critical alerts page immediately
- [ ] Warning alerts email team
- [ ] Alert fatigue avoided (proper thresholds)
- [ ] Runbooks linked to alerts
- [ ] Alert escalation configured
- [ ] Test alerts regularly
- [ ] Document on-call procedures

### 4. Performance Checklist

- [ ] Slow queries identified and optimized
- [ ] API endpoints have SLOs (Service Level Objectives)
- [ ] Database queries use indexes
- [ ] Caching implemented
- [ ] Load testing performed
- [ ] Resource limits set
- [ ] Auto-scaling configured

---

## Tools & Resources

### Recommended Tools

| Category | Tool | Purpose |
|----------|------|---------|
| **Metrics** | Prometheus | Metrics collection |
| **Visualization** | Grafana | Dashboards |
| **Error Tracking** | Sentry | Error monitoring |
| **APM** | Sentry Performance | Application traces |
| **Uptime** | UptimeRobot | Uptime monitoring |
| **Logs** | Railway Logs | Log aggregation |
| **Load Testing** | Locust | Performance testing |
| **Alerting** | PagerDuty | Incident management |

### Useful Queries

**Prometheus:**
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Active workflows
active_workflows

# Queue depth
queue_size{queue="celery"}
```

**Grafana:**
```sql
-- Slow queries
SELECT * FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Database size
SELECT pg_size_pretty(pg_database_size('meta_analysis'));

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

**Last Updated:** November 4, 2025
**Version:** 1.0
**Next Review:** February 4, 2026
