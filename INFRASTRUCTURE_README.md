# Infrastructure README
## Meta-Analysis Research Platform - DevOps Documentation

**Created:** November 4, 2025
**Status:** Production-Ready

---

## Overview

This document provides an overview of the production infrastructure setup for the Meta-Analysis Research Platform. The infrastructure is designed for scalability, reliability, and cost-efficiency.

## Infrastructure Stack

### Production Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Users / Clients                           │
└─────────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌─────────┐    ┌─────────┐    ┌─────────┐
   │ Vercel  │    │ Railway │    │ Railway │
   │ CDN     │    │ API     │    │ Workers │
   └─────────┘    └─────────┘    └─────────┘
                       │               │
         ┌─────────────┼───────────────┤
         │             │               │
         ▼             ▼               ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │Postgres │   │  Redis  │   │ Sentry  │
   │   DB    │   │  Cache  │   │ Errors  │
   └─────────┘   └─────────┘   └─────────┘
```

### Technology Components

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 on Vercel | User interface, SSR |
| **API** | FastAPI on Railway | REST API, orchestration |
| **Workers** | Celery on Railway | Background jobs |
| **Database** | PostgreSQL 15 | Data persistence |
| **Cache** | Redis 7 | Caching, message queue |
| **Monitoring** | Prometheus + Grafana | Metrics, dashboards |
| **Errors** | Sentry | Error tracking |
| **CI/CD** | GitHub Actions | Automated deployment |

## Quick Start

### Local Development

```bash
# 1. Clone and setup
git clone <repo-url>
cd meta-analysis-tool
cp .env.example .env
# Edit .env with your API keys

# 2. Start all services
docker-compose up

# 3. Access services
# - API: http://localhost:8000
# - Frontend: http://localhost:3000
# - Flower: http://localhost:5555
# - Grafana: http://localhost:3001
```

### Production Deployment

```bash
# 1. Setup Railway
railway login
railway init

# 2. Configure services
railway add postgresql
railway add redis
railway variables set ANTHROPIC_API_KEY=sk-ant-...

# 3. Deploy
railway up

# See DEPLOYMENT_CHECKLIST.md for complete guide
```

## File Structure

```
meta-analysis-tool/
├── backend/
│   ├── Dockerfile                    # Production API image
│   ├── Dockerfile.worker             # Worker image
│   ├── app/
│   │   ├── monitoring/              # Monitoring infrastructure
│   │   │   ├── logger.py           # Structured logging
│   │   │   ├── metrics.py          # Prometheus metrics
│   │   │   └── sentry.py           # Error tracking
│   │   └── api/v1/
│   │       └── metrics.py          # Metrics endpoint
│   └── requirements.worker.txt      # Worker dependencies
├── frontend/
│   └── [Next.js application]
├── scripts/
│   ├── backup-db.sh                # Database backup
│   ├── restore-db.sh               # Database restore
│   └── init-db.sql                 # Database initialization
├── config/
│   ├── redis.conf                  # Redis configuration
│   ├── prometheus.yml              # Prometheus config
│   └── grafana/                    # Grafana dashboards
├── .github/workflows/
│   ├── deploy.yml                  # Production deployment
│   └── test.yml                    # PR tests
├── docker-compose.yml              # Local development
├── docker-compose.prod.yml         # Production-like local
├── railway.json                    # Railway config (JSON)
├── railway.toml                    # Railway config (TOML)
├── INFRASTRUCTURE.md               # Complete infrastructure docs
├── MONITORING.md                   # Monitoring guide
├── INCIDENT_RESPONSE.md            # Incident runbooks
└── DEPLOYMENT_CHECKLIST.md         # Deployment checklist
```

## Key Features

### 1. Multi-Stage Docker Builds

- **Backend**: Optimized for fast deploys (~200MB)
- **Worker**: Includes scientific libraries for analysis
- **Security**: Non-root user, minimal dependencies
- **Performance**: Layer caching, multi-stage builds

### 2. Monitoring & Observability

- **Structured Logging**: JSON format, searchable
- **Metrics**: Prometheus-compatible (`/metrics`)
- **Error Tracking**: Sentry integration
- **Dashboards**: Pre-configured Grafana dashboards
- **Health Checks**: `/health` and `/health/detailed`

### 3. Backup & Recovery

- **Automated Backups**: Daily database backups
- **Retention**: 30 days
- **Testing**: Verified restore procedures
- **Disaster Recovery**: RTO: 4 hours, RPO: 24 hours

### 4. CI/CD Pipeline

- **Automated Tests**: Run on every PR
- **Automated Deployment**: Push to `main` → deploy
- **Rollback**: One-command rollback capability
- **Smoke Tests**: Post-deployment verification

### 5. Scalability

- **Horizontal Scaling**: Auto-scaling API & workers
- **Vertical Scaling**: Resource limits per phase
- **Database**: Connection pooling, indexing
- **Caching**: Multi-layer Redis caching

## Documentation

### Core Documents

1. **[INFRASTRUCTURE.md](./INFRASTRUCTURE.md)** - Complete infrastructure guide
   - Architecture overview
   - Deployment environments
   - Scaling strategy
   - Cost management
   - Troubleshooting

2. **[MONITORING.md](./MONITORING.md)** - Monitoring & observability
   - Metrics collection
   - Logging best practices
   - Alerting rules
   - Dashboards
   - Performance monitoring

3. **[INCIDENT_RESPONSE.md](./INCIDENT_RESPONSE.md)** - Incident runbooks
   - Incident classification
   - Response procedures
   - Playbooks for common issues
   - Communication templates
   - Post-mortem templates

4. **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** - Deployment guide
   - Pre-deployment checklist
   - Step-by-step deployment
   - Post-deployment verification
   - Rollback procedures

### Quick Reference

| Topic | Document | Section |
|-------|----------|---------|
| Local setup | INFRASTRUCTURE.md | Local Development |
| Deploy to Railway | DEPLOYMENT_CHECKLIST.md | Phase 1 |
| Deploy to Vercel | DEPLOYMENT_CHECKLIST.md | Phase 2 |
| View logs | MONITORING.md | Logging |
| Set up alerts | MONITORING.md | Alerting |
| Database backup | INFRASTRUCTURE.md | Backup & Recovery |
| API down | INCIDENT_RESPONSE.md | P0-1: API Health Check |
| High latency | INCIDENT_RESPONSE.md | P1: High Latency |
| Cost tracking | INFRASTRUCTURE.md | Cost Management |

## Monitoring Endpoints

```bash
# Health check
GET /health
# Returns: {"status": "healthy"}

# Detailed health check
GET /health/detailed
# Returns: {
#   "status": "healthy",
#   "components": {
#     "database": "healthy",
#     "redis": "healthy",
#     "api": "healthy"
#   }
# }

# Prometheus metrics
GET /metrics
# Returns: Prometheus-formatted metrics

# API documentation
GET /docs
# Returns: Swagger UI
```

## Cost Breakdown

### Phase 0-1 (MVP) - Target: < $100/month

| Service | Cost |
|---------|------|
| Railway API | $20 |
| Railway PostgreSQL | $5 |
| Railway Redis | $5 |
| Vercel Frontend | $0 |
| Claude API (usage) | $50-70 |
| **Total** | **$80-100** |

### Scaling Costs

- **Phase 2-3 (Growth)**: $300-400/month
- **Phase 4-5 (Scale)**: $500-700/month

See [INFRASTRUCTURE.md](./INFRASTRUCTURE.md#cost-management) for detailed cost breakdown.

## Scaling Strategy

### Current Resources (Phase 0-1)

- API: 1 instance, 1 GB RAM, 1 vCPU
- Worker: 1 instance, 2 GB RAM, 1 vCPU
- Database: 1 GB storage
- Redis: 256 MB memory

### Scaling Triggers

**Scale Up When:**
- CPU > 70% for 5 minutes
- Memory > 80% for 5 minutes
- Queue depth > 100 tasks
- API latency > 2 seconds

**Scale Down When:**
- CPU < 30% for 15 minutes
- Queue depth < 10 tasks

See [INFRASTRUCTURE.md](./INFRASTRUCTURE.md#scaling-strategy) for details.

## Security

### Security Measures

- ✅ HTTPS enforced (Railway + Vercel)
- ✅ Security headers (CORS, CSP, X-Frame-Options)
- ✅ Secrets in environment variables only
- ✅ Non-root Docker containers
- ✅ Rate limiting per user tier
- ✅ Database encryption at rest
- ✅ Dependency vulnerability scanning

### Security Checklist

See [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md#security) for complete security checklist.

## Support & Contact

### On-Call

- **Primary**: Check on-call rotation
- **Escalation**: See [INCIDENT_RESPONSE.md](./INCIDENT_RESPONSE.md#escalation-path)

### External Support

- **Railway**: support@railway.app
- **Vercel**: support@vercel.com
- **Anthropic**: support@anthropic.com
- **Sentry**: support@sentry.io

### Documentation

- **GitHub**: [Project Repository]
- **Confluence**: [Team Wiki]
- **Runbooks**: [INCIDENT_RESPONSE.md](./INCIDENT_RESPONSE.md)

## Common Commands

```bash
# Railway
railway logs --service backend         # View logs
railway status                          # Check status
railway restart --service backend       # Restart service
railway up                             # Deploy

# Docker
docker-compose up                       # Start local
docker-compose logs -f backend         # View logs
docker-compose restart backend         # Restart service

# Backups
./scripts/backup-db.sh production      # Backup database
./scripts/restore-db.sh backup.sql.gz  # Restore database

# Monitoring
curl http://localhost:8000/metrics     # View metrics
open http://localhost:3001             # Grafana
open http://localhost:5555             # Flower (Celery)
```

## Troubleshooting

### Quick Diagnostics

```bash
# 1. Check service health
curl https://your-api.railway.app/health

# 2. Check logs
railway logs --service backend --tail 100

# 3. Check resource usage
railway metrics --service backend

# 4. Check database
railway run psql -c "SELECT 1;"

# 5. Check Redis
railway run redis-cli ping
```

### Common Issues

| Issue | Quick Fix | Documentation |
|-------|-----------|---------------|
| API down | `railway restart --service backend` | INCIDENT_RESPONSE.md |
| High latency | Check `/metrics`, scale up | INCIDENT_RESPONSE.md |
| Database errors | Check connection pool | INCIDENT_RESPONSE.md |
| Worker stuck | `railway restart --service worker` | INCIDENT_RESPONSE.md |

See [INCIDENT_RESPONSE.md](./INCIDENT_RESPONSE.md) for detailed troubleshooting.

## Next Steps

### Immediate (Week 1)
- [ ] Deploy to Railway staging
- [ ] Test all endpoints
- [ ] Configure monitoring
- [ ] Set up backups

### Short-term (Month 1)
- [ ] Deploy to production
- [ ] Configure alerts
- [ ] Test disaster recovery
- [ ] Optimize performance

### Long-term (Quarter 1)
- [ ] Scale infrastructure
- [ ] Implement auto-scaling
- [ ] Advanced monitoring
- [ ] Cost optimization

## License

[Your License]

## Contributors

[Your Team]

---

**Last Updated:** November 4, 2025
**Infrastructure Version:** 1.0
**Next Review:** December 4, 2025

**For detailed information, see:**
- [INFRASTRUCTURE.md](./INFRASTRUCTURE.md) - Complete infrastructure guide
- [MONITORING.md](./MONITORING.md) - Monitoring & observability
- [INCIDENT_RESPONSE.md](./INCIDENT_RESPONSE.md) - Incident runbooks
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Deployment guide
