# Database Architecture - Visual Guide

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    4-TOOL ACADEMIC RESEARCH PLATFORM                     │
│                         Database Architecture                            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           CORE INFRASTRUCTURE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐         ┌──────────┐         ┌──────────┐                │
│  │  USERS   │─────────│ PROJECTS │─────────│ WORKFLOWS│                │
│  │          │         │          │         │          │                │
│  │ •Email   │         │•Tool Type│         │•Agent    │                │
│  │ •Role    │ owns    │•Title    │contains │•Status   │                │
│  │ •ORCID   │         │•Status   │         │•Decisions│                │
│  └──────────┘         └──────────┘         └──────────┘                │
│                              │                                           │
│                              │ uses                                      │
│                              ↓                                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         SHARED ENTITIES (Multi-Tool)                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐                        ┌──────────────┐              │
│  │   PAPERS     │◄──────authors──────────│ RESEARCHERS  │              │
│  │              │                         │              │              │
│  │ •Title       │                         │ •Name        │              │
│  │ •DOI/PMID    │                         │ •ORCID       │              │
│  │ •Credibility │                         │ •H-index     │              │
│  │ •Effect Size │                         │ •Expertise   │              │
│  │ •JSONB Data  │                         │ •Availability│              │
│  └──────────────┘                         └──────────────┘              │
│         ▲                                         ▲                      │
│         │                                         │                      │
│         └────────┬──────────────────────┬────────┘                      │
│                  │                      │                                │
│         ┌────────┴────────┐    ┌───────┴────────┐                      │
│         │ project_papers  │    │project_researchers│                    │
│         │  (association)  │    │   (association)   │                    │
│         └─────────────────┘    └──────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    TOOL 1: META-ANALYSIS ASSISTANT                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Uses: PROJECTS + PAPERS + WORKFLOWS                                    │
│                                                                          │
│  Special fields in PAPERS:                                              │
│  • credibility_level (very_low → high)                                  │
│  • extracted_statistics (JSONB)                                         │
│  • effect_size, sample_size, p_value                                    │
│  • inclusion_status (included, excluded, screening)                     │
│                                                                          │
│  Agents: Search, Screening, Credibility, Data Extraction, Statistical   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                  TOOL 2: RESEARCH DIRECTION GENERATOR                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐                  ┌─────────────────────┐          │
│  │ RESEARCH_GAPS   │                  │ RESEARCH_PROPOSALS  │          │
│  │                 │                  │                     │          │
│  │ •Gap Type       │──────addresses───│ •Research Question  │          │
│  │ •Impact Score   │                  │ •Methodology        │          │
│  │ •Feasibility    │                  │ •Novelty Score      │          │
│  │ •Priority       │                  │ •Funding Likelihood │          │
│  │ •Evidence       │                  │ •AI Generated       │          │
│  └─────────────────┘                  └─────────────────────┘          │
│         ▲                                                                │
│         │ identified_in                                                 │
│         │                                                                │
│   ┌─────┴──────┐                                                        │
│   │  PROJECTS  │                                                        │
│   └────────────┘                                                        │
│                                                                          │
│  Uses: PAPERS (for gap analysis), RESEARCHERS (for expertise)           │
│  Agents: Gap Analysis, Trend Analysis, Proposal Generator               │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                   TOOL 3: PEER REVIEW ASSISTANT                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐                      ┌─────────────────┐             │
│  │ MANUSCRIPTS  │                      │  PEER_REVIEWS   │             │
│  │              │                      │                 │             │
│  │ •Title       │──────receives────────│ •Review Text    │             │
│  │ •Status      │                      │ •Scores         │             │
│  │ •Round       │                      │ •Recommendation │             │
│  │ •Quality     │                      │ •AI Assisted    │             │
│  └──────────────┘                      └─────────────────┘             │
│         │                                       │                       │
│         │ submitted_by                          │ written_by            │
│         ↓                                       ↓                       │
│   ┌─────────┐                          ┌──────────────┐                │
│   │  USERS  │                          │ RESEARCHERS  │                │
│   └─────────┘                          └──────────────┘                │
│                                                                          │
│  Agents: Screening, Review Drafter, Editor Assistant                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                  TOOL 4: EXPERT REVIEWER MATCHER                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐                    ┌─────────────────────┐           │
│  │ MANUSCRIPTS  │                    │ REVIEWER_MATCHES    │           │
│  │              │                    │                     │           │
│  │ •Keywords    │────matches─────────│ •Expertise Score    │           │
│  │ •Abstract    │                    │ •Availability Score │           │
│  │ •Authors     │                    │ •Conflict Risk      │           │
│  └──────────────┘                    │ •Overall Score      │           │
│                                      │ •Reasoning (AI)     │           │
│                                      └─────────────────────┘           │
│                                              │                          │
│                                              │ recommends               │
│                                              ↓                          │
│                                      ┌──────────────┐                   │
│                                      │ RESEARCHERS  │                   │
│                                      │              │                   │
│                                      │ •Expertise   │                   │
│                                      │ •Availability│                   │
│                                      │ •Review Count│                   │
│                                      │ •Co-authors  │                   │
│                                      └──────────────┘                   │
│                                                                          │
│  Agents: Expertise Analyzer, Conflict Detector, Matcher                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Tool 1: Meta-Analysis Workflow

```
User Creates Project
       ↓
[SearchAgent] → Queries 4 databases → Stores in PAPERS
       ↓
[ScreeningAgent] → Applies criteria → Updates PAPERS.inclusion_status
       ↓
[CredibilityAgent] → Assesses quality → Updates PAPERS.credibility_level
       ↓
[DataExtractionAgent] → Extracts stats → Updates PAPERS.extracted_statistics
       ↓
[StatisticalAgent] → Calculates → Updates PROJECT.findings
       ↓
Results: Forest plot, heterogeneity, effect sizes
```

### Tool 4: Reviewer Matching Workflow

```
Editor Submits Manuscript
       ↓
[MANUSCRIPTS] record created
       ↓
[ExpertiseAnalyzerAgent]
   ↓
   Analyzes MANUSCRIPTS.keywords + abstract
   Searches RESEARCHERS by expertise_keywords
   ↓
Creates multiple REVIEWER_MATCHES with scores
       ↓
[ConflictDetectorAgent]
   ↓
   Checks RESEARCHERS.coauthor_ids
   Checks institutional affiliations
   Updates REVIEWER_MATCHES.conflict_risk
       ↓
[AvailabilityPredictorAgent]
   ↓
   Checks RESEARCHERS.current_workload
   Checks recent_review_count
   Updates REVIEWER_MATCHES.availability_score
       ↓
[MatcherAgent]
   ↓
   Calculates weighted overall_score
   Ranks matches
   ↓
Top 10 Reviewers Recommended
```

---

## Database Relationships

### One-to-Many Relationships

```
USER ──┬──> PROJECT (1 user owns many projects)
       │
       └──> MANUSCRIPT (1 user submits many manuscripts)

PROJECT ──┬──> WORKFLOW (1 project has many workflows)
          │
          ├──> RESEARCH_GAP (1 project identifies many gaps)
          │
          └──> RESEARCH_PROPOSAL (1 project generates many proposals)

MANUSCRIPT ──┬──> PEER_REVIEW (1 manuscript receives many reviews)
             │
             └──> REVIEWER_MATCH (1 manuscript has many match candidates)

RESEARCHER ───┬──> PEER_REVIEW (1 researcher writes many reviews)
              │
              └──> REVIEWER_MATCH (1 researcher matched to many manuscripts)

RESEARCH_GAP ───> RESEARCH_PROPOSAL (1 gap addressed by many proposals)
```

### Many-to-Many Relationships

```
PROJECT ◄──┬──► PAPER (projects can include many papers;
            │           papers can be in many projects)
            │
            └──► RESEARCHER (projects can involve many researchers;
                            researchers can work on many projects)

PAPER ◄────────► RESEARCHER (papers have many authors;
                             researchers author many papers)
```

---

## Index Strategy Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                     INDEX HIERARCHY                          │
└─────────────────────────────────────────────────────────────┘

LEVEL 1: Primary Keys (UUID) - B-tree
  ├─ All tables have UUID primary key index
  └─ Automatically created

LEVEL 2: Foreign Keys - B-tree
  ├─ project_id (in workflows, research_gaps, etc.)
  ├─ user_id (in projects, manuscripts)
  ├─ manuscript_id (in peer_reviews, reviewer_matches)
  └─ researcher_id (in peer_reviews, reviewer_matches)

LEVEL 3: Status/Filter Fields - B-tree
  ├─ status columns (projects, workflows, manuscripts, etc.)
  ├─ deleted_at (for soft delete queries)
  └─ created_at (for temporal queries)

LEVEL 4: Unique Identifiers - B-tree + UNIQUE
  ├─ email (users)
  ├─ orcid (users, researchers)
  ├─ doi, pmid, arxiv_id (papers)
  └─ Partial indexes WHERE value IS NOT NULL

LEVEL 5: Full-Text Search - GIN + Trigram
  ├─ papers.title
  ├─ papers.full_text
  ├─ researchers.name
  └─ manuscripts.title

LEVEL 6: JSONB Fields - GIN
  ├─ papers.metadata
  ├─ projects.config
  ├─ workflows.decisions
  └─ Fast JSON queries: @>, ?, ?&, ?|

LEVEL 7: Composite Indexes
  ├─ (manuscript_id, overall_score DESC) - reviewer ranking
  ├─ (project_id, status) - workflow filtering
  └─ (journal, year DESC) - paper queries
```

---

## Query Performance Map

```
┌────────────────────────────────────────────────────────────────┐
│               QUERY PERFORMANCE GUIDE                          │
└────────────────────────────────────────────────────────────────┘

ULTRA-FAST (<1ms) - Primary Key Lookups
├─ SELECT * FROM users WHERE id = :uuid
├─ SELECT * FROM projects WHERE id = :uuid
└─ Uses primary key index

FAST (<10ms) - Indexed Foreign Key Queries
├─ SELECT * FROM workflows WHERE project_id = :uuid
├─ SELECT * FROM peer_reviews WHERE manuscript_id = :uuid
└─ Uses foreign key indexes

MEDIUM (10-100ms) - Filtered Status Queries
├─ SELECT * FROM projects WHERE user_id = :uuid AND status = 'in_progress'
├─ SELECT * FROM manuscripts WHERE status = 'in_review'
└─ Uses composite indexes

SLOWER (100-500ms) - Full-Text Search
├─ SELECT * FROM papers WHERE title ILIKE '%transformer%'
├─ SELECT * FROM researchers WHERE name ILIKE '%turing%'
└─ Uses GIN trigram indexes

SLOW (500ms-2s) - Complex Aggregations
├─ Reviewer conflict detection (network analysis)
├─ Meta-analysis statistics calculation
└─ Use caching or materialized views

VERY SLOW (>2s) - Unindexed Queries
├─ Queries without WHERE clause on indexed columns
├─ Complex JOINs without proper indexes
└─ Needs optimization!
```

---

## Scaling Roadmap

```
┌────────────────────────────────────────────────────────────────┐
│                     SCALING TRAJECTORY                         │
└────────────────────────────────────────────────────────────────┘

Phase 1: MVP (Current)
├─ Single PostgreSQL instance
├─ 10GB storage
├─ 1-10 concurrent users
└─ <1,000 projects

Phase 2: Growth (Month 3-6)
├─ Vertical scaling (more RAM/CPU)
├─ Connection pooling (pgBouncer)
├─ 50GB storage
├─ 10-100 concurrent users
└─ <10,000 projects

Phase 3: Scaling (Month 6-12)
├─ Read replicas (2-3 instances)
├─ Redis caching layer
├─ 200GB storage
├─ 100-500 concurrent users
└─ <100,000 projects

Phase 4: Enterprise (Year 2)
├─ Multi-region deployment
├─ Table partitioning (papers by year)
├─ Materialized views for dashboards
├─ 1TB+ storage
├─ 500-2,000 concurrent users
└─ 1M+ projects

Phase 5: Massive Scale (Year 3+)
├─ Database sharding
├─ Microservices architecture
├─ Event sourcing for audit trail
├─ 10TB+ storage
├─ 2,000+ concurrent users
└─ 10M+ projects
```

---

## Data Security Layers

```
┌────────────────────────────────────────────────────────────────┐
│                    SECURITY ARCHITECTURE                       │
└────────────────────────────────────────────────────────────────┘

LAYER 1: Network Security
  ├─ VPC/Private subnet for database
  ├─ Firewall rules (allow only app server)
  └─ SSL/TLS for connections

LAYER 2: Authentication
  ├─ Bcrypt password hashing (cost factor 12)
  ├─ JWT tokens for API access
  ├─ API keys for programmatic access
  └─ Email verification

LAYER 3: Authorization
  ├─ Role-based access control (RBAC)
  │   ├─ admin: Full access
  │   ├─ researcher: Own projects only
  │   ├─ editor: Manuscript access
  │   └─ reviewer: Assigned manuscripts only
  └─ Future: Row-level security (RLS)

LAYER 4: Data Protection
  ├─ Soft deletes (recovery possible)
  ├─ Audit trails (who, what, when)
  ├─ No PII in logs
  └─ Encrypted backups

LAYER 5: SQL Injection Prevention
  ├─ Parameterized queries (SQLAlchemy ORM)
  ├─ Input validation (Pydantic)
  └─ Prepared statements

LAYER 6: Privacy Compliance
  ├─ GDPR-ready (user data export/delete)
  ├─ Optional fields for PII
  ├─ Confidential review comments separated
  └─ Data retention policies
```

---

## Monitoring & Observability

```
┌────────────────────────────────────────────────────────────────┐
│                 OBSERVABILITY STRATEGY                         │
└────────────────────────────────────────────────────────────────┘

DATABASE METRICS
  ├─ Connection pool utilization
  ├─ Query execution time (p50, p95, p99)
  ├─ Slow query log (>500ms)
  ├─ Table sizes and growth rate
  └─ Index usage statistics

APPLICATION METRICS
  ├─ API endpoint latency
  ├─ Request rate (req/sec)
  ├─ Error rate
  └─ Agent execution time

BUSINESS METRICS
  ├─ Projects created per day
  ├─ Papers processed per day
  ├─ Reviews generated per day
  ├─ Reviewer matches per day
  └─ Active users (DAU/MAU)

ALERTS
  ├─ Database connection pool exhausted
  ├─ Slow queries (>2 seconds)
  ├─ High error rate (>5%)
  ├─ Disk space >80% full
  └─ Replication lag >1 minute

TOOLS
  ├─ PostgreSQL built-in stats (pg_stat_*)
  ├─ Prometheus + Grafana (time-series)
  ├─ CloudWatch/DataDog (APM)
  └─ Sentry (error tracking)
```

---

## Backup & Disaster Recovery

```
┌────────────────────────────────────────────────────────────────┐
│                  BACKUP STRATEGY                               │
└────────────────────────────────────────────────────────────────┘

BACKUP FREQUENCY
  ├─ Continuous: WAL archiving (point-in-time recovery)
  ├─ Hourly: Incremental backups
  ├─ Daily: Full backups
  └─ Weekly: Full backup + verification

RETENTION POLICY
  ├─ Hourly backups: 7 days
  ├─ Daily backups: 30 days
  ├─ Weekly backups: 1 year
  └─ Monthly backups: 7 years (compliance)

RECOVERY OBJECTIVES
  ├─ RPO (Recovery Point Objective): 1 hour
  ├─ RTO (Recovery Time Objective): 4 hours
  └─ Test recovery: Monthly

STORAGE
  ├─ Primary: Cloud storage (S3/GCS)
  ├─ Secondary: Different region
  └─ Tertiary: Offline/cold storage

DISASTER SCENARIOS
  ├─ Single table corruption → Point-in-time restore
  ├─ Database failure → Failover to replica
  ├─ Region outage → Cross-region failover
  └─ Ransomware → Restore from offline backup
```

---

## Future Enhancements

```
┌────────────────────────────────────────────────────────────────┐
│                  FUTURE ROADMAP                                │
└────────────────────────────────────────────────────────────────┘

QUARTER 1 (Month 1-3)
  ✓ Core schema design
  ✓ Migration system
  ✓ Basic indexes
  ○ Tool 4 integration
  ○ Tool 1 completion

QUARTER 2 (Month 4-6)
  ○ Read replicas
  ○ Connection pooling
  ○ Materialized views for dashboards
  ○ Full-text search optimization
  ○ Tool 2 and 3 integration

QUARTER 3 (Month 7-9)
  ○ Table partitioning (papers by year)
  ○ Row-level security (RLS)
  ○ Automated backup verification
  ○ Performance monitoring dashboard
  ○ Advanced caching strategy

QUARTER 4 (Month 10-12)
  ○ Cross-region replication
  ○ Event sourcing for audit trail
  ○ GraphQL API layer
  ○ Real-time subscriptions
  ○ Advanced analytics views

YEAR 2
  ○ Database sharding
  ○ Microservices migration
  ○ Machine learning pipelines
  ○ Data warehouse for analytics
  ○ Multi-tenancy architecture
```

---

**Visualization Guide Version**: 1.0
**Last Updated**: November 4, 2025
**Maintained By**: Database Architecture Team

