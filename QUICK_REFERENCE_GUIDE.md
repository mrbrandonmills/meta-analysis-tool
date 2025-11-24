# Meta-Analysis Platform - Quick Reference Guide

## System Overview at a Glance

**Platform:** 4-Tool AI Research Ecosystem
**Backend:** FastAPI + PostgreSQL + Celery
**Frontend:** Next.js + React + Tailwind
**Deployment:** Railway (backend) + Vercel (frontend)
**Status:** Production-Ready MVP

---

## Quick Facts

| Aspect | Details |
|--------|---------|
| **Python Files** | 140 in backend |
| **Database Models** | 23 core models |
| **API Routes** | 20+ route files, 100+ endpoints |
| **Migrations** | 10 Alembic migrations |
| **Test Coverage** | 80%+ enforced |
| **Auth Method** | JWT + Argon2 |
| **Main Database** | PostgreSQL 15+ |
| **Task Queue** | Celery + Redis |
| **Primary LLM** | Claude (Anthropic) |
| **Payment System** | Stripe subscriptions |

---

## The 4 Tools

### Tool 1: Meta-Analysis Assistant
- **Purpose:** Systematic reviews & meta-analysis
- **Key Agents:** Coordinator, Search, Screening, DataExtraction
- **Database:** MetaAnalysis, Paper, PDFMetadata, FullTextExtraction
- **API Route:** `/api/v1/meta-analysis`

### Tool 2: Research Direction Generator
- **Purpose:** Gap analysis & proposal generation
- **Key Models:** ResearchGap, ResearchProposal, ResearchDirection
- **API Route:** `/api/v1/research-direction`

### Tool 3: Peer Review Assistant
- **Purpose:** Manuscript review & quality assessment
- **Key Models:** Manuscript, PeerReview, ReviewCompletion
- **API Route:** `/api/v1/peer-reviews`

### Tool 4: Expert Reviewer Matcher
- **Purpose:** AI researcher matching
- **Key Models:** ReviewerMatch, Researcher profiles
- **API Route:** `/api/v1/reviewer-matcher`

---

## User Roles

| Role | Can Create Analysis | Can Review | Can Approve | Status |
|------|---------------------|-----------|------------|--------|
| ADMIN | ✅ | ✅ | ✅ | Full access |
| EDITOR | ❌ | ✅ | ✅ | Review management |
| RESEARCHER | ✅ | ❌ | ❌ | Default role |
| REVIEWER | ✅ | ✅ | ❌ | Via $100/mo subscription |
| VIEWER | ❌ | ❌ | ❌ | Read-only |

---

## Key Database Models

**User/Auth:**
- User (auth + profile)
- APIKey (programmatic access)
- Researcher (extended profile for Tools 2-4)

**Tool 1:**
- MetaAnalysis, CoordinatorState, AgentExecution
- Paper, PDFMetadata, FullTextExtraction, FullTextScreening
- Report, Project, Workflow

**Tool 2:**
- ResearchGap, ResearchProposal, ResearchDirection

**Tool 3:**
- Manuscript, PeerReview, ReviewCompletion

**Tool 4:**
- ReviewerMatch, ReviewerMatchFeedback

**Payment:**
- Subscription, PayoutPool, PayoutContribution, PayoutDistribution

---

## Critical API Endpoints

### Authentication
```
POST   /api/v1/auth/login              - Login (email + password)
POST   /api/v1/auth/register           - Register new user
POST   /api/v1/auth/refresh-token      - Refresh JWT
GET    /api/v1/auth/me                 - Current user profile
```

### Meta-Analysis (Tool 1)
```
POST   /api/v1/meta-analysis/create    - Start new analysis
GET    /api/v1/meta-analysis/{id}/status
POST   /api/v1/meta-analysis/ask       - Q&A with agents
GET    /api/v1/meta-analysis/{id}/report
```

### Reviewer Matcher (Tool 4)
```
POST   /api/v1/reviewer-matcher/match/search
GET    /api/v1/reviewer-matcher/match/{id}
POST   /api/v1/reviewer-matcher/match/{id}/invite
```

### Peer Review (Tool 3)
```
POST   /api/v1/peer-reviews/generate   - AI generate review
POST   /api/v1/peer-reviews/submit     - Submit review
POST   /api/v1/peer-reviews/{id}/approve
```

### Subscriptions/Payments
```
POST   /api/v1/subscriptions/create    - Create subscription
GET    /api/v1/payouts/earnings        - Get reviewer earnings
POST   /api/v1/payouts/connect         - Connect Stripe account
```

---

## Tech Stack Summary

**Backend Core:**
- FastAPI 0.104.1
- SQLAlchemy 2.0.23 (async ORM)
- Pydantic 2.5.0 (validation)
- PostgreSQL 15+

**AI/ML:**
- Anthropic Claude SDK (0.18.1)
- OpenAI (fallback)

**Processing:**
- Celery 5.3.4 (background jobs)
- Redis 7 (cache + broker)
- pdfplumber + PyMuPDF (PDF)
- NumPy, SciPy, Pandas (data)
- statsmodels (statistics)

**Frontend:**
- Next.js 15.5.6
- React 18.2.0
- TypeScript 5.3.2
- Tailwind CSS 3.3.0
- Zustand (state mgmt)
- React Query (data fetching)

**Infrastructure:**
- Docker + Docker Compose
- Alembic (migrations)
- GitHub Actions (CI/CD)
- Railway (backend)
- Vercel (frontend)

---

## Directory Structure

```
backend/
├── app/
│   ├── main.py              ← FastAPI app entry point
│   ├── core/
│   │   ├── config.py        ← Settings
│   │   ├── security.py      ← JWT, auth
│   │   └── middleware.py    ← CORS, rate limit, etc.
│   ├── api/v1/              ← 20+ route files
│   ├── models/              ← 23 database models
│   ├── services/            ← Business logic (6 services)
│   ├── agents/              ← AI agents
│   ├── db/                  ← Database setup
│   └── workers/             ← Celery tasks
├── alembic/
│   └── versions/            ← 10 migrations
├── tests/                   ← Pytest suite
└── requirements.txt         ← Dependencies

frontend/
├── src/
│   ├── pages/               ← Next.js routes
│   │   ├── tools/           ← Tool pages (4 tools)
│   │   ├── onboarding/      ← 5-step researcher signup
│   │   └── admin/           ← Admin dashboards
│   ├── components/          ← React components
│   ├── stores/              ← Zustand state
│   ├── types/               ← TypeScript defs
│   └── lib/                 ← Utilities
└── package.json             ← Dependencies
```

---

## Critical Code Paths

### 1. Creating a Meta-Analysis
```
POST /api/v1/meta-analysis/create
  → MetaAnalysisService.create_meta_analysis()
  → CoordinatorAgent initialized
  → Workflow plan persisted to CoordinatorState
  → SearchAgent executes (async)
  → Papers stored + PDFs downloaded
  → ScreeningAgent applies criteria
  → DataExtractionAgent extracts stats
  → Report generated (APA format)
  → Results returned
```

### 2. Matching Reviewers
```
POST /api/v1/reviewer-matcher/match/search
  → Query Researcher table with filters
  → Score expertise (keyword match + domain overlap)
  → Score availability (inverse workload)
  → Score diversity (geographic + institutional)
  → Calculate overall_score = 0.5*expertise + 0.3*avail + 0.2*diversity
  → Detect conflicts of interest
  → Return top N candidates ranked by score
```

### 3. Peer Review Workflow
```
Manuscript submitted
  → AI desk review (quality scores + recommendation)
  → Editor reviews scores
  → If approved: AI generates full review
  → Editor approves/rejects review
  → Final review sent to author
  → If approved: eligible_for_payout = true
```

### 4. Researcher Onboarding
```
GET /onboarding/researcher
  Step 1: Basic info (name, email, institution)
  Step 2: Academic profile (ORCID, Google Scholar)
  Step 3: Expertise (domains, keywords, methods)
  Step 4: Review experience (h-index, languages, capacity)
  Step 5: Payment (Stripe subscription $100/mo)
  → Researcher profile enriched via AI
  → Available for Tool 4 matching
```

---

## Environment Variables (Production)

```bash
# REQUIRED
ANTHROPIC_API_KEY=sk-ant-xxxxxx
SECRET_KEY=generated_secret_here

# DATABASE (auto-provided by Railway)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# APPLICATION
DEBUG=false
LOG_LEVEL=INFO

# STRIPE (for payments)
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# CORS
ALLOWED_ORIGINS=https://frontend.vercel.app,http://localhost:3000
```

---

## Common Tasks

### Run Local Development
```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main

# Terminal 2: Frontend
cd frontend
npm install
npm run dev

# Browser: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Run with Docker
```bash
docker-compose up -d

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs
# Flower: http://localhost:5555
```

### Run Tests
```bash
cd backend
pytest                          # All tests
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests
pytest --cov=app                # Coverage report
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Deploy to Railway
```bash
# Backend automatically deploys on git push to main
# Make sure to set environment variables:
# - ANTHROPIC_API_KEY
# - SECRET_KEY
# - DATABASE_URL (auto)
# - REDIS_URL (auto)
```

### Deploy to Vercel
```bash
# Frontend automatically deploys on git push to main
# Make sure to set:
# - NEXT_PUBLIC_API_URL=https://api-railway-url.railway.app
```

---

## Known Issues & Gaps

| Issue | Status | Impact | Fix |
|-------|--------|--------|-----|
| Init_async_db in production | FIXED | DB conflicts | Use Alembic migrations only |
| Anthropic API key missing | FIXED | App won't start | Validate at startup |
| Rate limiting in-memory | KNOWN | Won't scale | Use Redis |
| Migration naming (004) | KNOWN | Confusing | Rename second one |
| Vector embeddings | NOT DONE | No semantic search | Add ChromaDB/Pinecone |
| Full-text search | NOT DONE | Can't search papers | Add PostgreSQL FTS |
| Email notifications | NOT DONE | Users not notified | Add SendGrid |
| Voice features | FLAG ONLY | Not implemented | Add Deepgram |
| Multi-language | NOT DONE | English only | Add i18n |

---

## Performance Notes

### Scaling Limits
- Single PostgreSQL instance (add read replicas at 1k+ QPS)
- In-memory rate limiting (won't work distributed)
- Synchronous PDF downloads (move to Celery)

### Optimization Opportunities
- Add Redis caching for queries
- Implement pagination for large lists
- Add query result caching
- Move PDF processing to background jobs
- Use Celery job priorities

---

## Security Checklist

✅ **Implemented:**
- JWT authentication with refresh tokens
- Argon2 password hashing
- CORS configuration
- Rate limiting middleware
- SQL injection protection (ORM)
- XSS protection (React)

⚠️ **To Implement:**
- HTTPS enforcement in all configs
- API key rotation strategy
- Security headers (CSP, HSTS)
- Rate limiter in Redis (distributed)
- DDoS protection (reverse proxy)

❌ **Not Done:**
- OAuth2 (Google, GitHub)
- 2FA/MFA
- API key management UI
- IP whitelisting
- PII encryption at rest

---

## Useful Files to Know

| File | Purpose | Size |
|------|---------|------|
| `ARCHITECTURE.md` | System design | 10KB |
| `DATABASE_SCHEMA.md` | Schema docs | 37KB |
| `openapi_spec.json` | API specification | 22KB |
| `docker-compose.yml` | Local development | 2KB |
| `requirements.txt` | Python deps | 2KB |
| `ONBOARDING_COMPLETE.md` | Researcher signup | 14KB |
| `COMPREHENSIVE_CODEBASE_DEEP_DIVE.md` | THIS FILE | 50KB |

---

## Contact & Support

For detailed information, see:
- `COMPREHENSIVE_CODEBASE_DEEP_DIVE.md` - Full analysis (THIS FILE)
- `ARCHITECTURE.md` - System design details
- `DATABASE_SCHEMA.md` - Database documentation
- `README.md` - Getting started
- API Docs: `http://localhost:8000/docs` (Swagger UI)

---

**Last Updated:** November 22, 2025
**Version:** 1.0
**Status:** Production-Ready MVP

