# COMPREHENSIVE TEST PLAN: Meta-Analysis Research Platform
**Date:** November 5, 2025
**Test Lead:** QA Engineering Agent
**Platform:** Academic Meta-Analysis Research Tool
**Objective:** Institution-Grade Quality Certification

---

## EXECUTIVE SUMMARY

This test plan provides 10 comprehensive test scenarios using REAL research questions to validate end-to-end functionality of the meta-analysis platform. Each test must use actual API calls, real LLM responses, and genuine data—no mocks, no simulations, no patches.

**Test Philosophy:** Academic software must be bulletproof. Every result will be mathematically correct, statistically valid, and scientifically accurate.

**Current Status:** ⚠️ BLOCKED - Critical bugs must be fixed before testing can proceed (see Forensic Analysis Report BUG-001 through BUG-010).

---

## TABLE OF CONTENTS

1. [Prerequisites and Blockers](#1-prerequisites-and-blockers)
2. [Test Environment Setup](#2-test-environment-setup)
3. [Test Data Requirements](#3-test-data-requirements)
4. [Test Scenario 1: Basic Meta-Analysis Flow](#test-scenario-1-basic-meta-analysis-flow)
5. [Test Scenario 2: Multi-Database Literature Search](#test-scenario-2-multi-database-literature-search)
6. [Test Scenario 3: Effect Size Calculations](#test-scenario-3-effect-size-calculations)
7. [Test Scenario 4: Complex Research Question with Moderators](#test-scenario-4-complex-research-question-with-moderators)
8. [Test Scenario 5: Study Quality Assessment](#test-scenario-5-study-quality-assessment)
9. [Test Scenario 6: Data Export and Download](#test-scenario-6-data-export-and-download)
10. [Test Scenario 7: User Authentication and Authorization](#test-scenario-7-user-authentication-and-authorization)
11. [Test Scenario 8: Concurrent Users and Load](#test-scenario-8-concurrent-users-and-load)
12. [Test Scenario 9: Error Handling and Recovery](#test-scenario-9-error-handling-and-recovery)
13. [Test Scenario 10: Background Job Processing](#test-scenario-10-background-job-processing)
14. [Success Criteria and Validation](#success-criteria-and-validation)
15. [Bug Tracking Matrix](#bug-tracking-matrix)

---

## 1. PREREQUISITES AND BLOCKERS

### Must Fix Before Testing

**CRITICAL BLOCKERS (prevent ALL testing):**

1. ❌ **BUG-001:** User Registration Crashes
   - Status: BLOCKS Test Scenario 7 and all auth-protected tests
   - Priority: P0
   - Fix: Debug SQL error in `/backend/app/api/v1/auth.py`

2. ❌ **BUG-002:** Redis Connection Failed
   - Status: BLOCKS rate limiting, caching, Celery
   - Priority: P0
   - Fix: Deploy Redis service to Railway

3. ❌ **BUG-003:** Celery Workers Not Running
   - Status: BLOCKS Test Scenario 10 and all background jobs
   - Priority: P0
   - Fix: Deploy Celery worker service to Railway

4. ❌ **BUG-004:** Missing Statistical Libraries
   - Status: BLOCKS Test Scenarios 1, 3, 4, 5 (all meta-analysis tests)
   - Priority: P0
   - Fix: Restore scipy, numpy, pandas, statsmodels to requirements.txt

5. ❌ **BUG-008:** StatisticalAgent Not Implemented
   - Status: BLOCKS all actual meta-analysis calculations
   - Priority: P0
   - Fix: Implement statistical agent (2-3 weeks estimated)

**HIGH-PRIORITY BLOCKERS (prevent specific tests):**

6. ⚠️ **BUG-005:** Frontend API URL Misconfigured
   - Status: BLOCKS all frontend-backend integration tests
   - Priority: P1
   - Fix: Update `.env.production` with Railway URL (5 minutes)

7. ⚠️ **BUG-009:** Search Agents Return Mock Data
   - Status: BLOCKS Test Scenario 2 (literature search validation)
   - Priority: P1
   - Fix: Implement actual PubMed/arXiv API calls (1 week)

### Test Environment Requirements

**Infrastructure:**
- ✅ PostgreSQL database (running in Railway)
- ❌ Redis server (MISSING)
- ❌ Celery worker (MISSING)
- ✅ FastAPI backend (deployed but degraded)
- ✅ Next.js frontend (deployed)

**Configuration:**
- ❌ Backend `.env` file for local testing
- ❌ Frontend `.env.local` file for local testing
- ⚠️ Anthropic API key (unknown if valid)
- ❌ PubMed API key (not configured)
- ❌ Test database separate from production

**Dependencies:**
- ❌ Python test environment (loguru, pytest-asyncio, httpx missing)
- ❌ Statistical libraries (scipy, numpy, pandas, statsmodels)
- ❌ Visualization libraries (matplotlib, seaborn)

### Prerequisites Checklist

Before running ANY tests, complete this checklist:

- [ ] Fix BUG-001: User registration working
- [ ] Fix BUG-002: Redis deployed and connected
- [ ] Fix BUG-003: Celery workers running
- [ ] Fix BUG-004: Statistical libraries installed
- [ ] Fix BUG-005: Frontend API URL corrected
- [ ] Create test user account successfully
- [ ] Obtain valid JWT access token
- [ ] Verify health check shows all services "healthy"
- [ ] Verify database migration applied
- [ ] Set up test environment variables
- [ ] Install all test dependencies
- [ ] Create separate test database
- [ ] Verify Anthropic API key valid
- [ ] Verify PubMed API access working

**Estimated Time to Prerequisites Complete:** 3-5 days

---

## 2. TEST ENVIRONMENT SETUP

### 2.1 Local Development Environment

**Step 1: Clone Repository**
```bash
cd /Users/brandon/meta-analysis-tool
git pull origin main
```

**Step 2: Backend Setup**
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Create environment file
cp .env.example .env

# Edit .env with test values:
# ANTHROPIC_API_KEY=sk-ant-xxx (get from Anthropic Console)
# SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/meta_analysis_test
# REDIS_URL=redis://localhost:6379/0
# PUBMED_API_KEY=xxx (get from NCBI)
# PUBMED_EMAIL=your-email@example.com

# Start services (requires Docker)
docker-compose up -d postgres redis

# Run database migrations
alembic upgrade head

# Verify setup
python -m pytest tests/unit/test_agents/test_credibility.py -v
```

**Step 3: Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

**Step 4: Start Backend Server**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Step 5: Start Celery Worker** (in separate terminal)
```bash
cd backend
source venv/bin/activate
celery -A app.workers.celery_app worker -l info
```

### 2.2 Production Test Environment (Railway + Vercel)

**URLs:**
- Frontend: https://meta-analysis-tool.vercel.app
- Backend: https://meta-analysis-tool-production.up.railway.app
- API Docs: https://meta-analysis-tool-production.up.railway.app/docs

**Test Account:**
```
Email: qa-test@meta-analysis-tool.com
Password: QATest123!SecurePwd
```
*(Create after BUG-001 is fixed)*

### 2.3 Test Data Preparation

**Required Test Datasets:**

1. **Known Meta-Analysis (Gold Standard):**
   - Source: Cochrane Database of Systematic Reviews
   - Example: "Cognitive behavioral therapy for depression" (Beck et al., 2015)
   - Includes: Raw data, published effect sizes, heterogeneity metrics
   - Purpose: Validate calculation accuracy

2. **Sample Papers (10-20):**
   - Mix of RCTs, cohort studies, case-control studies
   - Various sample sizes (50 to 5000)
   - Different journals (high and low impact)
   - Some with extractable effect sizes, some without

3. **Test Manuscripts (3-5):**
   - For peer review testing
   - Different quality levels
   - Various domains (medical, psychological, educational)

4. **Researcher Profiles (20-30):**
   - From ORCID or PubMed
   - Mix of expertise areas
   - Co-authorship networks available

**Load Test Data:**
```bash
cd backend
python scripts/load_test_data.py
```

---

## TEST SCENARIO 1: Basic Meta-Analysis Flow

### Research Question
**"What is the effectiveness of cognitive behavioral therapy (CBT) for treating depression in adults?"**

### Objective
Validate complete end-to-end meta-analysis workflow from research question to final report.

### Prerequisites
- ✅ User authenticated (JWT token obtained)
- ✅ StatisticalAgent implemented
- ✅ Celery workers running
- ✅ Scientific libraries installed

### Test Steps

**1. Create Meta-Analysis Project**

```bash
# API Request
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/create \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "What is the effectiveness of cognitive behavioral therapy for treating depression in adults?",
    "topic": "CBT for depression",
    "inclusion_criteria": [
      "Randomized controlled trials (RCTs)",
      "Adult participants (18+ years)",
      "Diagnosed with major depressive disorder",
      "CBT as primary intervention",
      "Depression measured with validated scale (BDI, HAM-D, etc.)"
    ],
    "exclusion_criteria": [
      "Adolescent or child populations",
      "Bipolar disorder or psychotic features",
      "Non-randomized studies",
      "No control group",
      "Unpublished dissertations"
    ],
    "databases": ["pubmed", "psychinfo"],
    "peer_review_only": true
  }'
```

**Expected Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "workflow_created",
  "message": "Meta-analysis workflow created successfully",
  "workflow": {
    "steps": [
      "literature_search",
      "title_abstract_screening",
      "full_text_screening",
      "quality_assessment",
      "data_extraction",
      "statistical_analysis",
      "report_generation"
    ],
    "estimated_time": "2-4 hours",
    "agent_assignments": {
      "search": "SearchAgent",
      "screening": "ScreeningAgent",
      "quality": "CredibilityAgent",
      "extraction": "DataExtractionAgent",
      "analysis": "StatisticalAgent",
      "report": "ReportAgent"
    }
  }
}
```

**Validation:**
- ✅ Response status 201 Created
- ✅ Valid UUID returned
- ✅ Workflow contains all required steps
- ✅ Estimated time reasonable
- ✅ All agents assigned

**2. Execute Literature Search**

```bash
# Start execution
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/execute/$ANALYSIS_ID \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Behavior:**
- Celery job created and queued
- SearchAgent begins database queries
- Real PubMed API calls made (verify in logs)
- Results stored in database

**Monitor Progress:**
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/status/$ANALYSIS_ID \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response (after 2-5 minutes):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "search_completed",
  "progress": 14,
  "current_step": "screening",
  "results_summary": {
    "total_found": 2847,
    "pubmed": 2234,
    "psychinfo": 613,
    "duplicates_removed": 521,
    "unique_studies": 2326
  },
  "next_step": "title_abstract_screening",
  "estimated_completion": "2025-11-05T18:30:00Z"
}
```

**Validation:**
- ✅ Status progresses through workflow
- ✅ Progress percentage increases
- ✅ Real study counts (not placeholder numbers)
- ✅ Multiple databases searched
- ✅ Deduplication performed
- ✅ Estimated completion time provided

**3. Screening Phase**

**Wait for automatic screening (10-15 minutes)** or monitor progress:

```bash
# Poll every 30 seconds
while true; do
  curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/status/$ANALYSIS_ID \
    -H "Authorization: Bearer $JWT_TOKEN" | jq '.status, .progress'
  sleep 30
done
```

**Expected Phases:**
1. `title_abstract_screening` (5-10 min)
2. `full_text_retrieval` (3-5 min)
3. `full_text_screening` (5-10 min)
4. `quality_assessment` (3-5 min)

**After Screening Complete:**
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/results/$ANALYSIS_ID/screening \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response:**
```json
{
  "screening_results": {
    "total_screened": 2326,
    "included_after_title_abstract": 187,
    "excluded_after_title_abstract": 2139,
    "full_text_retrieved": 187,
    "full_text_unavailable": 12,
    "included_after_full_text": 42,
    "excluded_after_full_text": 145,
    "final_included": 42
  },
  "exclusion_reasons": {
    "wrong_population": 892,
    "wrong_intervention": 645,
    "wrong_outcome": 423,
    "wrong_study_design": 179,
    "full_text_unavailable": 12,
    "other": 45
  },
  "prisma_flow_diagram_url": "https://.../_analysis_550e8400_prisma.png"
}
```

**Validation:**
- ✅ Numbers add up correctly (total = included + excluded)
- ✅ Exclusion reasons categorized
- ✅ PRISMA flow diagram generated
- ✅ Reasonable inclusion rate (1-5% typical)

**4. Data Extraction**

```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/results/$ANALYSIS_ID/extraction \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response:**
```json
{
  "extracted_data": {
    "studies_with_extractable_data": 38,
    "studies_missing_data": 4,
    "total_participants": 4523,
    "effect_sizes_extracted": 38,
    "studies": [
      {
        "study_id": "pmid:25678901",
        "first_author": "Beck",
        "year": 2015,
        "sample_size": 120,
        "intervention_n": 60,
        "control_n": 60,
        "outcome_measure": "BDI-II",
        "intervention_mean": 12.3,
        "intervention_sd": 8.4,
        "control_mean": 22.1,
        "control_sd": 9.2,
        "effect_size_d": 1.12,
        "confidence_interval": [0.76, 1.48],
        "quality_score": 8.5
      }
      // ... 37 more studies
    ]
  }
}
```

**Validation:**
- ✅ Effect sizes calculated correctly (Cohen's d)
- ✅ Confidence intervals provided
- ✅ Quality scores assigned
- ✅ All required statistics present
- ✅ Sample sizes sum correctly

**Manual Validation:** Compare 3-5 randomly selected studies against original papers (spot check)

**5. Statistical Analysis (Meta-Analysis)**

```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/results/$ANALYSIS_ID/statistics \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response:**
```json
{
  "meta_analysis_results": {
    "model": "random_effects",
    "pooled_effect_size": {
      "cohens_d": 0.89,
      "standard_error": 0.08,
      "confidence_interval_95": [0.73, 1.05],
      "z_value": 11.13,
      "p_value": 0.0001
    },
    "heterogeneity": {
      "Q_statistic": 87.42,
      "df": 37,
      "p_value": 0.0001,
      "I_squared": 67.3,
      "tau_squared": 0.142,
      "interpretation": "Substantial heterogeneity"
    },
    "publication_bias": {
      "eggers_test_p": 0.23,
      "interpretation": "No significant publication bias detected",
      "funnel_plot_url": "https://.../funnel_plot.png"
    },
    "sensitivity_analysis": {
      "leave_one_out_range": [0.85, 0.92],
      "influential_studies": []
    },
    "forest_plot_url": "https://.../forest_plot.png"
  }
}
```

**Validation (CRITICAL - Academic Accuracy):**

✅ **Effect Size Validation:**
- Pool 3-5 studies manually using formula: d = (M1 - M2) / SD_pooled
- Compare to platform's result (tolerance: ±0.05)

✅ **Confidence Interval Validation:**
- Calculate 95% CI manually: d ± 1.96 * SE
- Compare to platform's CI (tolerance: ±0.02)

✅ **Heterogeneity Validation:**
- Calculate Q = Σ w_i (d_i - d_pooled)² manually for subset
- Verify I² = ((Q - df) / Q) * 100 if Q > df
- Compare to platform's I² (tolerance: ±5%)

✅ **Statistical Significance:**
- Verify p-value calculation: Z = d / SE, p from Z-table
- Compare to platform's p-value (tolerance: ±0.01)

**Tools for Manual Validation:**
- Use R with `meta` package as gold standard
- Or use online calculator: https://www.meta-analysis.com/

**6. Download Results**

```bash
# Download forest plot
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/results/$ANALYSIS_ID/export/forest-plot \
  -H "Authorization: Bearer $JWT_TOKEN" \
  --output forest_plot.png

# Download data CSV
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/results/$ANALYSIS_ID/export/csv \
  -H "Authorization: Bearer $JWT_TOKEN" \
  --output meta_analysis_data.csv

# Download full report PDF
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/results/$ANALYSIS_ID/export/report \
  -H "Authorization: Bearer $JWT_TOKEN" \
  --output meta_analysis_report.pdf
```

**Validation:**
- ✅ Files download successfully
- ✅ Forest plot image is valid PNG
- ✅ CSV data matches API response
- ✅ PDF report is APA-formatted
- ✅ All statistics included in report
- ✅ References properly formatted
- ✅ PRISMA checklist included

**7. Verify Report Quality**

**Open PDF and check for:**
- ✅ Title and abstract
- ✅ Introduction with research question
- ✅ Methods section (search strategy, inclusion/exclusion criteria)
- ✅ Results section (PRISMA flow diagram, forest plot, statistics)
- ✅ Discussion section
- ✅ References (Vancouver or APA style)
- ✅ PRISMA 2020 checklist
- ✅ Author affiliations (AI-generated notice)

**Academic Review:** Have a domain expert (psychologist) review the report for:
- Clinical interpretation accuracy
- Statistical method appropriateness
- Conclusions supported by data
- APA 7th edition formatting

### Success Criteria

✅ **PASS Conditions:**
1. Complete workflow executes end-to-end
2. Real literature search (verified in PubMed logs)
3. Statistical calculations match manual validation (±5%)
4. Forest plot visually accurate
5. Report is publication-ready
6. Total execution time < 4 hours
7. No 500 errors or crashes
8. Academic reviewer rates quality ≥ 7/10

❌ **FAIL Conditions:**
- Any statistical calculation error > 5%
- Workflow hangs or times out
- Missing critical report sections
- Mock data used instead of real search
- Academic reviewer rates quality < 5/10

### Performance Metrics

**Target Metrics:**
- Literature search: < 5 minutes for 2000 results
- Screening: < 15 minutes for 2000 papers
- Data extraction: < 10 minutes for 50 papers
- Statistical analysis: < 30 seconds for 50 studies
- Report generation: < 2 minutes
- **Total time: < 30 minutes**

**Resource Usage:**
- API calls: < 100 Claude API calls total
- Token usage: < 200,000 tokens total
- Database queries: < 500 queries total
- Memory: < 2GB backend peak
- CPU: < 1.0 vCPU sustained

### Bug Report Template

**If test fails, document:**

```markdown
## BUG-XXX: [Title]
**Severity:** [CRITICAL/HIGH/MEDIUM/LOW]
**Component:** [Agent/API/Database/Frontend]
**Test:** Test Scenario 1 - Step X
**Expected:** [What should happen]
**Actual:** [What actually happened]
**Reproduction:**
[Exact curl command or steps]
**Logs:**
[Relevant log output]
**Screenshots:** [If applicable]
**Impact:** [Description of impact on users]
```

---

## TEST SCENARIO 2: Multi-Database Literature Search

### Research Question
**"What are the effects of intermittent fasting on metabolic health markers (blood glucose, insulin sensitivity, and lipid profiles)?"**

### Objective
Validate comprehensive literature search across multiple databases with proper deduplication and source tracking.

### Prerequisites
- ✅ PubMed API key configured
- ✅ SearchAgent with real API integration (BUG-009 fixed)
- ✅ Deduplication algorithm functional
- ✅ Rate limiting configured

### Test Steps

**1. Create Search with All Databases**

```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/create \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "What are the effects of intermittent fasting on metabolic health markers?",
    "topic": "Intermittent fasting and metabolic health",
    "inclusion_criteria": [
      "Human studies (adults 18+)",
      "Intermittent fasting intervention (16:8, 5:2, alternate day)",
      "Metabolic outcomes measured (glucose, insulin, lipids)",
      "At least 4 weeks duration"
    ],
    "exclusion_criteria": [
      "Animal studies",
      "Children or adolescents",
      "Non-fasting interventions",
      "Duration < 4 weeks"
    ],
    "databases": ["pubmed", "arxiv", "europepmc", "core"],
    "peer_review_only": false
  }'
```

**2. Monitor Search Progress by Database**

```bash
# Poll search status
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/$ANALYSIS_ID/search-progress \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response:**
```json
{
  "search_progress": {
    "status": "in_progress",
    "databases_searched": 2,
    "databases_remaining": 2,
    "current_database": "europepmc",
    "results_by_database": {
      "pubmed": {
        "status": "completed",
        "results_found": 347,
        "query_used": "(intermittent fasting[Title/Abstract]) AND (glucose[Title/Abstract] OR insulin[Title/Abstract] OR lipid[Title/Abstract])",
        "search_duration": "2.3s",
        "api_calls": 4
      },
      "arxiv": {
        "status": "completed",
        "results_found": 12,
        "query_used": "all:intermittent AND all:fasting AND (all:metabolic OR all:glucose)",
        "search_duration": "1.1s",
        "api_calls": 1
      },
      "europepmc": {
        "status": "in_progress",
        "results_found": 0,
        "query_used": "...",
        "search_duration": null,
        "api_calls": 0
      },
      "core": {
        "status": "pending",
        "results_found": 0
      }
    }
  }
}
```

**Validation:**
- ✅ Each database returns non-zero results
- ✅ Different query syntax per database
- ✅ API calls tracked per database
- ✅ Search duration reasonable (< 5s per database)
- ✅ Results found in expected ranges (PubMed > Europe PMC > arXiv > CORE)

**3. Verify Deduplication**

```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/$ANALYSIS_ID/deduplication-report \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response:**
```json
{
  "deduplication_summary": {
    "total_records": 478,
    "unique_records": 312,
    "duplicates_removed": 166,
    "duplicate_rate": "34.7%",
    "deduplication_method": "DOI + title + first_author + year",
    "duplicates_by_source": {
      "exact_doi_match": 89,
      "title_fuzzy_match": 54,
      "combined_match": 23
    },
    "cross_database_duplicates": [
      {
        "title": "Effects of alternate-day fasting on glucose metabolism",
        "found_in": ["pubmed", "europepmc"],
        "pubmed_id": "34567890",
        "pmc_id": "PMC8765432",
        "kept_record": "pubmed"
      }
      // ... more examples
    ]
  }
}
```

**Validation:**
- ✅ Duplicate rate reasonable (30-50% typical for multi-database searches)
- ✅ DOI matching prioritized (most accurate)
- ✅ Fuzzy title matching catches variations
- ✅ Cross-database duplicates identified correctly
- ✅ One version kept (preferably peer-reviewed over preprint)

**Manual Spot Check:**
- Select 5 duplicate pairs
- Verify they are truly the same study
- Verify correct version was kept

**4. Verify Database Coverage**

**Check specific databases returned expected results:**

**PubMed:**
```bash
# Search PubMed directly and compare
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=intermittent+fasting+glucose&retmax=20" \
  | grep "<Count>"
```

Compare count to platform's PubMed results (should be within 10%)

**arXiv:**
```bash
# Search arXiv directly
curl "http://export.arxiv.org/api/query?search_query=all:intermittent+AND+all:fasting&max_results=20" \
  | grep "<opensearch:totalResults>"
```

Compare to platform's arXiv results

**5. Export Search Results**

```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/$ANALYSIS_ID/export/search-results \
  -H "Authorization: Bearer $JWT_TOKEN" \
  --output search_results.csv
```

**Verify CSV contains:**
- ✅ All unique records (312 rows)
- ✅ Columns: title, authors, year, journal, DOI, PMID, abstract, source_database
- ✅ Source database tracked for each record
- ✅ Duplicate flag column (boolean)
- ✅ No missing critical fields

### Success Criteria

✅ **PASS Conditions:**
1. All 4 databases queried successfully
2. Results counts match direct API checks (±10%)
3. Deduplication removes 30-50% of records
4. No false positives in deduplication (verified by spot check)
5. CSV export complete and accurate
6. Search completes in < 5 minutes
7. No API rate limit errors

❌ **FAIL Conditions:**
- Any database returns 0 results (unless genuinely empty)
- Deduplication rate < 20% or > 60% (algorithm error)
- False positives found (unique studies marked as duplicates)
- CSV missing records or columns
- Search times out (> 10 minutes)

### Performance Metrics

**Target:**
- PubMed: < 5s for ~300 results
- arXiv: < 2s for ~20 results
- Europe PMC: < 5s for ~100 results
- CORE: < 10s for ~50 results
- Deduplication: < 5s for 500 records

---

## TEST SCENARIO 3: Effect Size Calculations

### Research Question
**"Does mindfulness meditation reduce anxiety symptoms in adults with generalized anxiety disorder?"**

### Objective
Validate accurate effect size extraction and calculation across different outcome measures and study designs.

### Prerequisites
- ✅ DataExtractionAgent implemented
- ✅ StatisticalAgent implemented
- ✅ Scientific libraries installed (scipy, numpy, statsmodels)
- ✅ Multiple effect size formulas supported

### Test Steps

**1. Create Meta-Analysis with Mixed Outcome Measures**

```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/create \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "Does mindfulness meditation reduce anxiety symptoms in adults with GAD?",
    "topic": "Mindfulness for anxiety",
    "inclusion_criteria": [
      "RCTs with control group",
      "Adults diagnosed with GAD (DSM-5 or ICD-10)",
      "Mindfulness-based intervention (MBSR, MBCT, or similar)",
      "Anxiety measured with validated scale (BAI, GAD-7, STAI, HAM-A)"
    ],
    "exclusion_criteria": [
      "Mixed anxiety disorders without separate GAD data",
      "Non-randomized studies",
      "Interventions < 4 weeks"
    ],
    "databases": ["pubmed", "psychinfo"],
    "peer_review_only": true
  }'
```

**2. Wait for Data Extraction Phase**

**Monitor until status = "data_extraction_completed"**

**3. Retrieve Extracted Data**

```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/$ANALYSIS_ID/extracted-data \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected Response with Mixed Data Types:**
```json
{
  "extracted_studies": [
    {
      "study_id": "study_001",
      "citation": "Hofmann et al. (2010). JAMA Psychiatry.",
      "outcome_measure": "BAI",
      "data_type": "means_sds",
      "intervention_group": {
        "n": 93,
        "mean_pre": 22.4,
        "mean_post": 12.1,
        "sd_pre": 8.3,
        "sd_post": 7.2
      },
      "control_group": {
        "n": 89,
        "mean_pre": 23.1,
        "mean_post": 19.8,
        "sd_pre": 8.7,
        "sd_post": 9.1
      },
      "effect_size_calculated": {
        "cohens_d": 0.94,
        "formula_used": "change_score_d",
        "standard_error": 0.16,
        "confidence_interval": [0.63, 1.25]
      }
    },
    {
      "study_id": "study_002",
      "citation": "Khoury et al. (2015). Clinical Psychology Review.",
      "outcome_measure": "GAD-7",
      "data_type": "means_sds",
      "intervention_group": {
        "n": 68,
        "mean_post": 8.2,
        "sd_post": 5.1
      },
      "control_group": {
        "n": 71,
        "mean_post": 13.4,
        "sd_post": 6.3
      },
      "effect_size_calculated": {
        "cohens_d": 0.91,
        "formula_used": "post_only_d",
        "standard_error": 0.18,
        "confidence_interval": [0.56, 1.26]
      }
    },
    {
      "study_id": "study_003",
      "citation": "Strauss et al. (2014). Behaviour Research and Therapy.",
      "outcome_measure": "STAI-State",
      "data_type": "t_statistic",
      "t_value": 3.42,
      "df": 118,
      "n_intervention": 60,
      "n_control": 60,
      "effect_size_calculated": {
        "cohens_d": 0.63,
        "formula_used": "t_to_d",
        "standard_error": 0.19,
        "confidence_interval": [0.26, 1.00]
      }
    }
  ]
}
```

**Validation Steps:**

**A. Verify Cohen's d Calculations**

**Study 001 (Change Scores):**
```python
# Manual calculation
intervention_change = 22.4 - 12.1  # 10.3
control_change = 23.1 - 19.8        # 3.3
difference = intervention_change - control_change  # 7.0

# Pooled SD of changes (approximation):
sd_pooled = sqrt((8.3^2 + 7.2^2 + 8.7^2 + 9.1^2) / 4)  # ~8.3

cohens_d = difference / sd_pooled  # 7.0 / 8.3 = 0.84

# Platform reported: 0.94
# Difference: 0.10 (acceptable if using more accurate formula)
```

✅ **Verify:** Platform's formula accounts for correlation between pre and post scores

**Study 002 (Post-Only Means):**
```python
# Manual calculation
difference = 13.4 - 8.2  # 5.2
sd_pooled = sqrt(((68-1)*5.1^2 + (71-1)*6.3^2) / (68+71-2))
# sd_pooled = 5.74

cohens_d = difference / sd_pooled  # 5.2 / 5.74 = 0.91
```

✅ **Verify:** Platform's calculation matches manual (tolerance: ±0.05)

**Study 003 (From t-statistic):**
```python
# Formula: d = t * sqrt((n1 + n2) / (n1 * n2))
d = 3.42 * sqrt((60 + 60) / (60 * 60))
d = 3.42 * sqrt(120 / 3600)
d = 3.42 * 0.183
d = 0.63
```

✅ **Verify:** Platform's conversion from t to d is correct

**B. Verify Standard Errors**

```python
# Formula: SE = sqrt((n1 + n2) / (n1 * n2) + (d^2 / (2 * (n1 + n2))))

# Study 001:
SE = sqrt((93 + 89) / (93 * 89) + (0.94^2 / (2 * (93 + 89))))
SE = sqrt(0.022 + 0.002)
SE = 0.15

# Platform reported: 0.16 (close enough, within rounding)
```

✅ **Verify:** Standard errors calculated correctly

**C. Verify Confidence Intervals**

```python
# Formula: CI = d ± (1.96 * SE)

# Study 001:
lower = 0.94 - (1.96 * 0.16) = 0.94 - 0.31 = 0.63
upper = 0.94 + (1.96 * 0.16) = 0.94 + 0.31 = 1.25

# Platform reported: [0.63, 1.25] ✅ Exact match
```

**4. Test Different Effect Size Types**

**Request specific effect size conversions:**

```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/$ANALYSIS_ID/convert-effect-size \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "study_id": "study_001",
    "convert_to": ["hedges_g", "odds_ratio", "correlation"]
  }'
```

**Expected Response:**
```json
{
  "original": {
    "cohens_d": 0.94
  },
  "conversions": {
    "hedges_g": 0.93,  // Small sample size correction
    "odds_ratio": 3.67,
    "correlation": 0.42,
    "nnt": 2.9  // Number needed to treat
  },
  "formulas_used": {
    "hedges_g": "d * (1 - (3 / (4 * (n1 + n2) - 9)))",
    "odds_ratio": "exp(d * π / sqrt(3))",
    "correlation": "d / sqrt(d^2 + 4)"
  }
}
```

**Validation:**
- ✅ Hedges' g slightly smaller than Cohen's d (bias correction)
- ✅ Odds ratio > 1 indicates intervention effect
- ✅ Correlation coefficient between 0 and 1
- ✅ NNT reasonable (lower is better)

**5. Test Handling of Missing Data**

**Upload study with incomplete data:**

```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/$ANALYSIS_ID/add-study-manual \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "citation": "Incomplete Study et al. (2020)",
    "intervention_n": 50,
    "control_n": 48,
    "intervention_mean": 15.2,
    "control_mean": 18.7,
    "sd_missing": true,
    "p_value": 0.03
  }'
```

**Expected Response:**
```json
{
  "status": "warning",
  "message": "Study added but effect size cannot be calculated precisely",
  "imputation_options": [
    "Use median SD from other studies in meta-analysis",
    "Estimate SD from p-value and sample sizes",
    "Contact authors for missing data",
    "Exclude study from analysis"
  ],
  "if_excluded": {
    "studies_remaining": 24,
    "impact_on_power": "Moderate - recommend retaining if possible"
  }
}
```

**Select imputation method:**

```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/$ANALYSIS_ID/impute-missing-data \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "study_id": "incomplete_study",
    "method": "median_sd",
    "sensitivity_analysis": true
  }'
```

**Validation:**
- ✅ Platform identifies missing data
- ✅ Offers appropriate imputation methods
- ✅ Warns about uncertainty
- ✅ Sensitivity analysis option provided

### Success Criteria

✅ **PASS Conditions:**
1. All effect size calculations match manual computation (±0.05)
2. Standard errors calculated correctly (±0.02)
3. Confidence intervals accurate (±0.02)
4. Different data types handled appropriately
5. Effect size conversions mathematically correct
6. Missing data flagged with warnings
7. Imputation methods offered and documented

❌ **FAIL Conditions:**
- Effect size error > 0.10 (10%)
- Incorrect formula used for data type
- Confidence intervals miscalculated
- Missing data silently ignored
- No sensitivity analysis for imputed values

### Performance Metrics

**Target:**
- Effect size calculation: < 0.1s per study
- Batch calculation (50 studies): < 5s
- Effect size conversion: < 0.5s

---

## TEST SCENARIO 4: Complex Research Question with Moderators

*(Due to length, I'll provide abbreviated version)*

### Research Question
**"How do age and gender moderate the relationship between exercise and cardiovascular health outcomes?"**

### Objective
Test subgroup analysis and meta-regression capabilities.

### Key Tests
1. Create analysis with moderator variables
2. Extract age and gender data from studies
3. Perform subgroup analyses
4. Run meta-regression
5. Validate interaction effects

### Success Criteria
- ✅ Subgroup analyses show different effect sizes by moderator
- ✅ Meta-regression coefficients calculated correctly
- ✅ Interaction plots generated
- ✅ Statistical tests for moderation (Q-between)

---

## TEST SCENARIO 5: Study Quality Assessment

### Research Question
**"What is the efficacy of vaccine interventions in preventing infectious disease?"**

### Objective
Test risk of bias assessment and quality scoring.

### Key Tests
1. Apply Cochrane Risk of Bias 2.0 tool
2. Calculate Newcastle-Ottawa scores
3. Perform sensitivity analysis excluding low-quality studies
4. Generate quality assessment summary table

### Success Criteria
- ✅ Risk of bias assessed across all domains
- ✅ Quality scores calculated appropriately
- ✅ Sensitivity analysis shows impact of quality
- ✅ Publication bias detected if present

---

## TEST SCENARIO 6: Data Export and Download

### Objective
Validate all export formats contain accurate, complete data.

### Test Steps

**1. Export Formats to Test:**
- CSV (raw data)
- Excel (formatted with sheets)
- PDF (publication-ready report)
- JSON (API format)
- RIS (reference manager)
- R script (reproducibility)

**2. Validation for Each Format:**
- ✅ File downloads without corruption
- ✅ Data integrity preserved
- ✅ All studies included
- ✅ Statistics match API response
- ✅ Formatting appropriate for format

### Success Criteria
- ✅ All 6 formats export successfully
- ✅ Data identical across formats
- ✅ PDF meets APA 7th edition standards
- ✅ R script reproduces analysis

---

## TEST SCENARIO 7: User Authentication and Authorization

### Objective
Validate complete auth flow and access control.

### Test Steps

**1. Registration**
```bash
# Create new user
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@test.com",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "institution": "Test University"
  }'
```

**Expected Response:**
```json
{
  "id": "user-uuid",
  "email": "newuser@test.com",
  "full_name": "Test User",
  "institution": "Test University",
  "role": "researcher",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-11-05T20:00:00Z"
}
```

**Validation:**
- ✅ User created successfully
- ✅ Password hashed (not stored in plain text)
- ✅ Default role assigned (researcher)
- ✅ Email verification required flag set

**2. Login**
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=newuser@test.com&password=SecurePass123!"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Validation:**
- ✅ JWT token returned
- ✅ Refresh token returned
- ✅ Token expiry set (30 minutes)
- ✅ Token contains user ID and role (verify by decoding)

**3. Access Protected Endpoint**
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/my-projects \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Validation:**
- ✅ Returns 200 with user's projects
- ✅ Does not return other users' projects
- ✅ Without token, returns 401 Unauthorized
- ✅ With expired token, returns 401 Unauthorized
- ✅ With invalid token, returns 401 Unauthorized

**4. Token Refresh**
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "$REFRESH_TOKEN"}'
```

**Expected Response:**
```json
{
  "access_token": "new_access_token...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**5. Role-Based Access Control**

**Try accessing admin endpoint as regular user:**
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/admin/users \
  -H "Authorization: Bearer $USER_TOKEN"
```

**Expected Response:**
```json
{
  "detail": "Insufficient permissions. Admin role required."
}
```

**Status Code:** 403 Forbidden

**6. Create Admin User and Test**

*(Only if admin seeding supported)*

**7. Logout**
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/logout \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Validation:**
- ✅ Token added to blocklist
- ✅ Subsequent requests with same token return 401

### Success Criteria

✅ **PASS Conditions:**
1. Registration creates user successfully
2. Login returns valid JWT tokens
3. Protected endpoints require authentication
4. Token refresh works correctly
5. Role-based access control enforced
6. Logout invalidates tokens

❌ **FAIL Conditions:**
- Registration crashes (BUG-001)
- Tokens missing or invalid
- Any user can access admin endpoints
- Token refresh fails
- Password stored in plain text

---

## TEST SCENARIO 8: Concurrent Users and Load

### Objective
Validate system handles multiple simultaneous meta-analyses.

### Test Setup

**Use load testing tool: Apache JMeter or Locust**

**Test Script (Locust):**
```python
from locust import HttpUser, task, between

class MetaAnalysisUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login and get token
        response = self.client.post("/api/v1/auth/login", data={
            "username": f"user{self.environment.runner.user_count}@test.com",
            "password": "TestPass123"
        })
        self.token = response.json()["access_token"]

    @task(3)
    def create_analysis(self):
        self.client.post("/api/v1/meta-analysis/create",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "research_question": "Test question",
                "topic": "Load test",
                # ... minimal config
            })

    @task(5)
    def check_status(self):
        self.client.get(f"/api/v1/meta-analysis/status/{self.analysis_id}",
            headers={"Authorization": f"Bearer {self.token}"})

    @task(1)
    def health_check(self):
        self.client.get("/api/v1/health")
```

**Load Test Scenarios:**

**Scenario A: Ramp-Up**
- Start: 1 user
- Ramp to: 50 users over 5 minutes
- Duration: 10 minutes
- Expected: System handles all requests

**Scenario B: Sustained Load**
- Users: 100 concurrent
- Duration: 30 minutes
- Expected: < 5% error rate, response time < 2s (p95)

**Scenario C: Spike Test**
- Normal: 20 users
- Spike to: 200 users for 1 minute
- Expected: System recovers, no crashes

### Success Criteria

✅ **PASS Conditions:**
1. Error rate < 5% at 50 concurrent users
2. P95 response time < 3s at 50 concurrent users
3. System recovers from spike within 2 minutes
4. No database deadlocks
5. No memory leaks (memory stable over 30 min)
6. Celery queue processes jobs without backlog

❌ **FAIL Conditions:**
- System crashes under load
- Error rate > 10%
- Response time > 10s
- Database connection pool exhausted
- Out of memory errors

---

## TEST SCENARIO 9: Error Handling and Recovery

### Objective
Test graceful degradation and error recovery.

### Test Cases

**1. Invalid Research Question**
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/create \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"research_question": ""}'
```

**Expected:** 400 Bad Request with validation error

**2. Database Connection Loss**
- Temporarily stop PostgreSQL
- Make API request
- Expected: 503 Service Unavailable, retry message

**3. Redis Connection Loss**
- Stop Redis
- Make API request
- Expected: Degraded functionality but no crash

**4. Claude API Rate Limit**
- Make rapid requests to exhaust rate limit
- Expected: Queue requests, retry with backoff

**5. PubMed API Failure**
- Mock PubMed returning 500 errors
- Expected: Fallback to other databases, warning logged

**6. Malformed Data Input**
- Upload study with negative sample size
- Expected: Validation error with helpful message

**7. Timeout Handling**
- Create meta-analysis with 10,000 papers
- Expected: Background job queued, status updates

### Success Criteria

✅ **PASS Conditions:**
- All errors return appropriate HTTP status codes
- Error messages are helpful and actionable
- System recovers automatically when service restored
- No unhandled exceptions
- Errors logged with context

---

## TEST SCENARIO 10: Background Job Processing

### Objective
Validate Celery workers process long-running tasks correctly.

### Test Steps

**1. Verify Celery Workers Running**
```bash
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected:**
```json
{
  "checks": {
    "celery": {
      "status": "healthy",
      "workers": 2,
      "active_tasks": 3,
      "queue_length": 12
    }
  }
}
```

**2. Submit Long-Running Analysis**

*(Analysis designed to take 15-30 minutes)*

```bash
ANALYSIS_ID=$(curl -X POST ... | jq -r '.id')

# Immediately check status
curl https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/status/$ANALYSIS_ID \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected:** Status "queued" or "in_progress"

**3. Monitor Progress Updates**

**Poll every 30 seconds:**
```bash
while true; do
  STATUS=$(curl -s https://.../$ANALYSIS_ID/status | jq -r '.status')
  PROGRESS=$(curl -s https://.../$ANALYSIS_ID/status | jq -r '.progress')
  echo "$(date): Status=$STATUS, Progress=$PROGRESS%"

  if [ "$STATUS" = "completed" ]; then
    break
  fi

  sleep 30
done
```

**Validation:**
- ✅ Progress increases monotonically
- ✅ Status transitions logically (queued → in_progress → completed)
- ✅ No status regressions
- ✅ ETA updates dynamically

**4. Test Job Cancellation**

```bash
curl -X DELETE https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/$ANALYSIS_ID \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Expected:**
- Job stops gracefully
- Partial results saved
- Status changes to "cancelled"

**5. Test Job Retry on Failure**

**Simulate transient failure:**
- Temporarily disconnect database during job
- Expected: Job retries 3 times before marking as failed
- Job enters "failed" state with error message

**6. Test Queue Prioritization**

- Submit 10 analyses
- Some marked as "priority: high"
- Validation: High priority jobs processed first

### Success Criteria

✅ **PASS Conditions:**
1. Jobs execute in background (API returns immediately)
2. Progress updates provided
3. Jobs complete successfully
4. Failed jobs retry appropriately
5. Job cancellation works
6. Queue stats accurate

❌ **FAIL Conditions:**
- Jobs block API requests
- Progress never updates
- Failed jobs not retried
- Cancelled jobs continue running
- Worker crashes

---

## SUCCESS CRITERIA AND VALIDATION

### Overall Test Suite Success

**Required to PASS:**
- ✅ 8 out of 10 scenarios PASS (80%)
- ✅ All CRITICAL scenarios PASS (1, 2, 3, 7)
- ✅ No P0 bugs remain unfixed
- ✅ Statistical calculations validated by expert
- ✅ Academic reviewer rates platform ≥ 7/10

**Scenarios by Priority:**

| Priority | Scenario | Criticality |
|----------|----------|-------------|
| P0 | 1. Basic Meta-Analysis Flow | CRITICAL |
| P0 | 3. Effect Size Calculations | CRITICAL |
| P0 | 7. User Authentication | CRITICAL |
| P1 | 2. Multi-Database Search | HIGH |
| P1 | 5. Study Quality Assessment | HIGH |
| P1 | 10. Background Jobs | HIGH |
| P2 | 4. Complex Moderators | MEDIUM |
| P2 | 6. Data Export | MEDIUM |
| P2 | 8. Concurrent Users | MEDIUM |
| P2 | 9. Error Handling | MEDIUM |

### Statistical Validation Thresholds

**Effect Sizes:**
- Tolerance: ±0.05 (5%)
- Reject if error > 0.10 (10%)

**Confidence Intervals:**
- Tolerance: ±0.02 at each bound
- Reject if any bound error > 0.05

**Heterogeneity (I²):**
- Tolerance: ±5 percentage points
- Reject if error > 10 percentage points

**P-values:**
- Tolerance: ±0.01
- Reject if crosses significance threshold (0.05)

### Academic Review Criteria

**Expert reviewer will assess:**
1. Statistical method appropriateness (weight: 30%)
2. Calculation accuracy (weight: 25%)
3. Interpretation correctness (weight: 20%)
4. Report completeness (weight: 15%)
5. Reproducibility (weight: 10%)

**Scoring:**
- 9-10: Excellent, publication-ready
- 7-8: Good, minor revisions needed
- 5-6: Acceptable, major revisions needed
- 3-4: Poor, significant issues
- 1-2: Unacceptable, not usable

**Minimum required score: 7/10**

---

## BUG TRACKING MATRIX

### Bug Tracking Template

| Bug ID | Severity | Component | Test | Status | Priority | Assigned | ETA |
|--------|----------|-----------|------|--------|----------|----------|-----|
| BUG-001 | CRITICAL | Auth API | T7-Step1 | OPEN | P0 | Backend | 1 day |
| BUG-002 | CRITICAL | Redis | T10-All | OPEN | P0 | DevOps | 0.5 day |
| BUG-003 | CRITICAL | Celery | T10-All | OPEN | P0 | DevOps | 1 day |
| BUG-004 | CRITICAL | Dependencies | T1,T3,T4 | OPEN | P0 | Backend | 0.5 day |
| BUG-005 | HIGH | Frontend | All | OPEN | P1 | Frontend | 0.1 day |
| BUG-008 | CRITICAL | StatisticalAgent | T1,T3 | OPEN | P0 | Backend | 15 days |
| BUG-009 | HIGH | SearchAgent | T2 | OPEN | P1 | Backend | 5 days |

### Bug Report Format

```markdown
## BUG-XXX: [Short Title]

**Severity:** [CRITICAL/HIGH/MEDIUM/LOW]
**Component:** [Auth/API/Agent/Database/Frontend/Infrastructure]
**Test Scenario:** [Test number and step]
**Discovered:** [Date]
**Status:** [OPEN/IN_PROGRESS/RESOLVED/CLOSED]

### Description
[Detailed description of the bug]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Reproduction Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Reproduction Rate
[X out of Y attempts]

### Environment
- Backend URL: [Production/Local]
- Frontend URL: [Production/Local]
- Database: [PostgreSQL version]
- Python: [Version]

### Logs
```
[Relevant log output]
```

### Screenshots
[If applicable]

### Impact
**Users Affected:** [All users / Authenticated users / Admin only / etc.]
**Functionality Blocked:** [What features are blocked]
**Workaround:** [Temporary workaround if available]

### Root Cause
[Analysis of why bug occurs]

### Proposed Fix
[How to fix the bug]

### Related Bugs
[Links to related issues]

### Test Coverage
[Tests to add to prevent regression]
```

---

## EXECUTION SCHEDULE

### Phase 1: Fix Blockers (3-5 days)
- Day 1: Fix BUG-001 (Auth), BUG-002 (Redis), BUG-003 (Celery)
- Day 2: Fix BUG-004 (Dependencies), BUG-005 (Frontend URL)
- Day 3-5: Setup test environment, verify all services healthy

### Phase 2: Implement Core Features (2-3 weeks)
- Week 1: Implement StatisticalAgent (BUG-008)
- Week 2: Implement real SearchAgent integration (BUG-009)
- Week 3: Implement DataExtractionAgent, buffer for delays

### Phase 3: Execute Test Scenarios (1 week)
- Day 1: T7 (Auth), T9 (Error Handling)
- Day 2: T2 (Search), T10 (Background Jobs)
- Day 3: T1 (Basic Flow) - end-to-end
- Day 4: T3 (Effect Sizes), T5 (Quality)
- Day 5: T4 (Moderators), T6 (Export), T8 (Load)

### Phase 4: Bug Fixing and Retesting (1 week)
- Fix bugs discovered in Phase 3
- Rerun failed tests
- Regression testing

### Phase 5: Academic Review (3-5 days)
- Submit results to domain expert
- Incorporate feedback
- Final validation

**Total Timeline: 6-8 weeks**

---

## APPENDIX: MANUAL VALIDATION FORMULAS

### Cohen's d (Mean Difference)
```
d = (M1 - M2) / SD_pooled

where:
SD_pooled = sqrt(((n1 - 1) * SD1^2 + (n2 - 1) * SD2^2) / (n1 + n2 - 2))
```

### Standard Error of d
```
SE_d = sqrt((n1 + n2) / (n1 * n2) + (d^2 / (2 * (n1 + n2))))
```

### 95% Confidence Interval
```
CI_lower = d - (1.96 * SE_d)
CI_upper = d + (1.96 * SE_d)
```

### Hedges' g (Small Sample Correction)
```
g = d * J

where:
J = 1 - (3 / (4 * (n1 + n2) - 9))
```

### Q Statistic (Heterogeneity)
```
Q = Σ w_i * (d_i - d_pooled)^2

where:
w_i = 1 / SE_i^2
```

### I² (Percentage of Heterogeneity)
```
I² = ((Q - df) / Q) * 100  if Q > df, else 0

where:
df = k - 1 (k = number of studies)
```

### τ² (Tau Squared, Between-Study Variance)
```
τ² = (Q - df) / C

where:
C = Σ w_i - (Σ w_i^2 / Σ w_i)
```

---

**Test Plan Prepared By:** QA Engineering Agent
**Document Version:** 1.0
**Date:** November 5, 2025
**Classification:** INTERNAL - Quality Assurance

**Next Steps:**
1. Prioritize and fix blocking bugs (BUG-001 through BUG-004)
2. Set up test environment
3. Begin test execution starting with Test Scenario 7 (Authentication)

---

END OF TEST PLAN
