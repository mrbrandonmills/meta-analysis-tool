# COMPREHENSIVE END-TO-END TEST PLAN
## Meta-Analysis Research Platform - Production Readiness Testing

**Version:** 1.0
**Date:** 2025-11-05
**QA Engineer:** Quality Assurance Team
**Objective:** Achieve 100% confidence in platform production-readiness

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Test Environment Setup](#test-environment-setup)
3. [Authentication & User Management Tests](#1-authentication--user-management-tests)
4. [Literature Search Tests](#2-literature-search-tests)
5. [Meta-Analysis Workflow Tests](#3-meta-analysis-workflow-tests)
6. [Statistical Calculations Tests](#4-statistical-calculations-tests)
7. [Data Export Tests](#5-data-export-tests)
8. [Performance Tests](#6-performance-tests)
9. [Edge Cases & Error Handling](#7-edge-cases--error-handling)
10. [Integration Tests](#8-integration-tests)
11. [Security Tests](#9-security-tests)
12. [Acceptance Criteria](#acceptance-criteria)

---

## Executive Summary

This test plan provides comprehensive coverage of all platform features with:
- **3 Real Research Questions** tested end-to-end
- **4 Academic Databases** tested individually and combined
- **Statistical Accuracy Validation** against R metafor package
- **Performance Benchmarks** for production workloads
- **Security Validation** for user data protection

**Test Coverage:**
- Authentication: 8 tests
- Literature Search: 12 tests
- Meta-Analysis Workflow: 15 tests
- Statistical Calculations: 10 tests
- Data Export: 6 tests
- Performance: 8 tests
- Edge Cases: 12 tests
- Integration: 6 tests
- Security: 5 tests

**Total: 82 test scenarios**

---

## Test Environment Setup

### Prerequisites
1. **Backend URL:** https://meta-analysis-tool-production.up.railway.app
2. **Frontend URL:** https://meta-analysis-tool.vercel.app
3. **Test Accounts:**
   - Test User 1: `qa-researcher-1@example.com` / `SecurePass123!`
   - Test User 2: `qa-researcher-2@example.com` / `SecurePass123!`
   - Admin User: `qa-admin@example.com` / `AdminPass123!`

4. **Required Tools:**
   - Python 3.11+ with requests, pytest, numpy, scipy
   - R with metafor package (for validation)
   - Postman or curl for API testing
   - Browser for frontend testing

5. **API Keys Required:**
   - Anthropic API Key (for AI agents)
   - PubMed API Key (optional, for higher rate limits)

### Environment Variables
```bash
export API_BASE_URL="https://meta-analysis-tool-production.up.railway.app"
export FRONTEND_URL="https://meta-analysis-tool.vercel.app"
export TEST_USER_EMAIL="qa-researcher-1@example.com"
export TEST_USER_PASSWORD="SecurePass123!"
```

---

## 1. Authentication & User Management Tests

### Test 1.1: User Registration - Valid Email Formats
**Priority:** HIGH
**Type:** Functional

**Test Cases:**
| Test Case | Input Email | Expected Result | Pass Criteria |
|-----------|-------------|-----------------|---------------|
| 1.1.1 | researcher@university.edu | 201 Created | User created, returns user_id |
| 1.1.2 | john.doe+research@gmail.com | 201 Created | Plus addressing supported |
| 1.1.3 | researcher_123@lab.co.uk | 201 Created | Underscores and numbers work |
| 1.1.4 | invalidemail | 400 Bad Request | Validation error message |
| 1.1.5 | @nodomain.com | 400 Bad Request | Validation error message |
| 1.1.6 | duplicate@test.com (2nd attempt) | 400 Bad Request | "Email already registered" |

**Automated Test:**
```python
def test_user_registration_valid_formats():
    """Test registration with various email formats."""
    valid_emails = [
        "researcher@university.edu",
        "john.doe+research@gmail.com",
        "researcher_123@lab.co.uk"
    ]

    for email in valid_emails:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/register",
            json={
                "email": email,
                "password": "SecurePass123!",
                "full_name": "Test Researcher"
            }
        )
        assert response.status_code == 201
        assert "id" in response.json()
        assert response.json()["email"] == email
```

### Test 1.2: Password Requirements Validation
**Priority:** HIGH
**Type:** Security

**Test Cases:**
| Test Case | Password | Expected Result | Pass Criteria |
|-----------|----------|-----------------|---------------|
| 1.2.1 | SecurePass123! | Accepted | Meets all requirements |
| 1.2.2 | short | 400 Bad Request | "Password too short (min 8 chars)" |
| 1.2.3 | alllowercase123 | 400 Bad Request | "Must contain uppercase" |
| 1.2.4 | ALLUPPERCASE123 | 400 Bad Request | "Must contain lowercase" |
| 1.2.5 | NoNumbers! | 400 Bad Request | "Must contain digit" |

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (optional but recommended)

### Test 1.3: User Login Flow
**Priority:** CRITICAL
**Type:** Functional

**Test Steps:**
1. Register new user: `test-login@example.com`
2. Login with correct credentials
3. Verify access token received
4. Verify refresh token received
5. Verify token type is "Bearer"
6. Login with incorrect password
7. Verify 401 Unauthorized returned

**Expected Results:**
```json
// Successful login
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### Test 1.4: Token Refresh Mechanism
**Priority:** HIGH
**Type:** Functional

**Test Steps:**
1. Login to get initial tokens
2. Wait 5 seconds
3. Use refresh token to get new access token
4. Verify new access token works
5. Verify old access token is still valid (until expiry)
6. Try to use expired refresh token (simulate expiry)
7. Verify 401 Unauthorized

### Test 1.5: Token Expiration Handling
**Priority:** HIGH
**Type:** Functional

**Test Steps:**
1. Login to get access token
2. Wait for access token to expire (default: 60 minutes)
   - For testing, set expiry to 5 seconds via environment variable
3. Make authenticated request with expired token
4. Verify 401 Unauthorized with "Token expired" message
5. Use refresh token to get new access token
6. Verify new token works

### Test 1.6: Protected Endpoint Access
**Priority:** HIGH
**Type:** Security

**Test Cases:**
| Test Case | Token | Endpoint | Expected Result |
|-----------|-------|----------|-----------------|
| 1.6.1 | Valid token | GET /api/v1/auth/me | 200 OK, user data |
| 1.6.2 | No token | GET /api/v1/auth/me | 401 Unauthorized |
| 1.6.3 | Invalid token | GET /api/v1/auth/me | 401 Unauthorized |
| 1.6.4 | Expired token | GET /api/v1/auth/me | 401 Unauthorized |
| 1.6.5 | Malformed token | GET /api/v1/auth/me | 401 Unauthorized |

### Test 1.7: API Key Management
**Priority:** MEDIUM
**Type:** Functional

**Test Steps:**
1. Login as authenticated user
2. Create API key with name "Test API Key"
3. Verify API key returned (only shown once)
4. List API keys - verify new key appears (without secret)
5. Use API key to authenticate request
6. Delete API key
7. Verify deleted key no longer works

### Test 1.8: Concurrent Login Sessions
**Priority:** MEDIUM
**Type:** Functional

**Test Steps:**
1. Login from Browser 1
2. Login from Browser 2 (same user)
3. Verify both sessions work independently
4. Logout from Browser 1
5. Verify Browser 2 session still works

---

## 2. Literature Search Tests

### Real Research Question Setup

For all literature search tests, we'll use these real research questions:

**RQ1:** "What is the effect of exercise on depression?"
**RQ2:** "Does mindfulness reduce anxiety?"
**RQ3:** "Impact of diet on cardiovascular disease"

### Test 2.1: PubMed Search - Individual Database
**Priority:** CRITICAL
**Type:** Functional

**Research Question:** RQ1 - Exercise and Depression

**Test Configuration:**
```json
{
  "research_question": "What is the effect of exercise on depression?",
  "search_terms": ["exercise", "depression", "randomized controlled trial"],
  "databases": ["pubmed"],
  "max_results": 50,
  "filters": {
    "publication_types": ["Clinical Trial", "Randomized Controlled Trial"],
    "publication_date_start": "2015-01-01",
    "publication_date_end": "2024-12-31"
  }
}
```

**Expected Results:**
- Response time: < 30 seconds
- Status: 200 OK
- Minimum 20 studies returned
- Each study contains:
  - PMID
  - Title
  - Abstract (full text)
  - Authors list
  - Journal name
  - Publication year
  - DOI (if available)
  - Keywords
  - MeSH terms

**Validation Checks:**
1. All returned studies contain "exercise" OR "depression" in title/abstract
2. All studies are within date range (2015-2024)
3. No duplicate PMIDs
4. Abstract text is present (not empty)
5. At least one author listed per study

**Manual Verification:**
- Spot-check 5 random studies
- Verify studies are actually about exercise and depression
- Verify publication dates match filter
- Cross-reference 3 studies with PubMed directly

### Test 2.2: arXiv Search - Individual Database
**Priority:** HIGH
**Type:** Functional

**Research Question:** RQ2 - Mindfulness and Anxiety

**Test Configuration:**
```json
{
  "research_question": "Does mindfulness reduce anxiety?",
  "search_terms": ["mindfulness", "anxiety", "intervention"],
  "databases": ["arxiv"],
  "max_results": 30,
  "filters": {
    "categories": ["q-bio", "stat"],
    "publication_date_start": "2018-01-01"
  }
}
```

**Expected Results:**
- Response time: < 30 seconds
- Status: 200 OK
- Minimum 10 preprints returned
- Each preprint contains:
  - arXiv ID
  - Title
  - Abstract
  - Authors list
  - Categories
  - Publication date
  - URL to PDF

**Validation Checks:**
1. All arXiv IDs are valid format (YYMM.NNNNN)
2. All preprints within specified date range
3. Categories match filter (q-bio or stat)
4. PDFs are accessible via URL

### Test 2.3: Europe PMC Search - Individual Database
**Priority:** HIGH
**Type:** Functional

**Research Question:** RQ3 - Diet and Cardiovascular Disease

**Test Configuration:**
```json
{
  "research_question": "Impact of diet on cardiovascular disease",
  "search_terms": ["diet", "cardiovascular disease", "prevention"],
  "databases": ["europepmc"],
  "max_results": 50
}
```

**Expected Results:**
- Response time: < 30 seconds
- Status: 200 OK
- Minimum 20 studies returned
- Each study contains:
  - PMC ID or PMID
  - Title
  - Abstract
  - Authors
  - Journal
  - Publication year
  - DOI
  - Source (e.g., "PMC", "PubMed", "Agricola")

**Validation Checks:**
1. Mix of open access and subscription articles
2. No duplicate PMCIDs
3. DOIs are valid format (10.XXXX/...)
4. European sources properly identified

### Test 2.4: CORE Search - Individual Database
**Priority:** MEDIUM
**Type:** Functional

**Research Question:** RQ1 - Exercise and Depression

**Test Configuration:**
```json
{
  "research_question": "What is the effect of exercise on depression?",
  "search_terms": ["exercise", "depression"],
  "databases": ["core"],
  "max_results": 40
}
```

**Expected Results:**
- Response time: < 30 seconds
- Status: 200 OK
- Minimum 15 papers returned
- Each paper contains:
  - CORE ID
  - Title
  - Abstract
  - Authors
  - Publisher/Repository
  - Publication year
  - Download URL (if available)

**Validation Checks:**
1. Open access papers only
2. Download URLs functional
3. Mix of repository sources (institutional repos, preprint servers)

### Test 2.5: Combined Multi-Database Search
**Priority:** CRITICAL
**Type:** Integration

**Research Question:** RQ2 - Mindfulness and Anxiety

**Test Configuration:**
```json
{
  "research_question": "Does mindfulness reduce anxiety?",
  "search_terms": ["mindfulness", "anxiety"],
  "databases": ["pubmed", "arxiv", "europepmc", "core"],
  "max_results_per_database": 30,
  "filters": {
    "publication_date_start": "2015-01-01"
  }
}
```

**Expected Results:**
- Response time: < 60 seconds (parallel searches)
- Status: 200 OK
- Minimum 60 unique studies across all databases
- Results grouped by database
- Deduplication applied

**Deduplication Validation:**
1. Same paper in PubMed and Europe PMC counted once
2. Deduplication uses DOI as primary key
3. If no DOI, use title similarity (case-insensitive, normalized)
4. Log all duplicates removed with reason

**Example Expected Output:**
```json
{
  "total_results": 85,
  "unique_results": 72,
  "duplicates_removed": 13,
  "databases_searched": ["pubmed", "arxiv", "europepmc", "core"],
  "results_by_database": {
    "pubmed": 28,
    "arxiv": 15,
    "europepmc": 25,
    "core": 17
  },
  "search_duration_seconds": 45.3,
  "studies": [...]
}
```

### Test 2.6: Narrow Query (Few Results)
**Priority:** HIGH
**Type:** Edge Case

**Test Configuration:**
```json
{
  "research_question": "Effect of underwater basket weaving on quantum physics understanding",
  "search_terms": ["underwater basket weaving", "quantum physics"],
  "databases": ["pubmed", "arxiv"],
  "max_results": 100
}
```

**Expected Results:**
- Response time: < 20 seconds
- Status: 200 OK
- 0-5 results returned
- No errors or crashes
- Helpful message: "Limited results found. Consider broadening search terms."

### Test 2.7: Broad Query (Many Results)
**Priority:** HIGH
**Type:** Performance

**Test Configuration:**
```json
{
  "research_question": "Cancer treatment outcomes",
  "search_terms": ["cancer", "treatment"],
  "databases": ["pubmed"],
  "max_results": 1000
}
```

**Expected Results:**
- Response time: < 120 seconds for 1000 results
- Status: 200 OK
- Exactly 1000 results returned (max limit enforced)
- Pagination metadata provided:
  ```json
  {
    "total_available": 125000,
    "returned": 1000,
    "page": 1,
    "pages": 125,
    "next_page_url": "/api/v1/search?page=2"
  }
  ```

### Test 2.8: Search with Peer-Review Filter
**Priority:** HIGH
**Type:** Functional

**Research Question:** RQ3 - Diet and CVD

**Test Configuration:**
```json
{
  "research_question": "Impact of diet on cardiovascular disease",
  "search_terms": ["diet", "cardiovascular disease"],
  "databases": ["pubmed", "europepmc"],
  "peer_review_only": true,
  "max_results": 50
}
```

**Expected Results:**
- Only peer-reviewed articles returned
- No preprints, conference abstracts, or editorial content
- Each result flagged with: `"peer_reviewed": true`

**Validation:**
- Manually check 10 random results
- Verify publication types exclude: "Preprint", "Conference Abstract", "Editorial"

### Test 2.9: Search with Date Range Filter
**Priority:** HIGH
**Type:** Functional

**Test Configuration:**
```json
{
  "search_terms": ["exercise", "depression"],
  "databases": ["pubmed"],
  "filters": {
    "publication_date_start": "2020-01-01",
    "publication_date_end": "2022-12-31"
  }
}
```

**Expected Results:**
- All results published between Jan 1, 2020 and Dec 31, 2022
- Date validation applied server-side
- Invalid dates return 400 Bad Request

### Test 2.10: API Rate Limiting Handling
**Priority:** CRITICAL
**Type:** Resilience

**Test Scenario:**
Simulate hitting PubMed rate limit (3 requests/second)

**Test Steps:**
1. Make 10 rapid search requests to PubMed
2. Verify rate limiting implemented (max 3/sec)
3. Verify requests queued, not rejected
4. Verify all 10 requests complete successfully
5. Verify total time: ~3-4 seconds (not instant)

**Expected Behavior:**
- No 429 Too Many Requests errors from PubMed
- Automatic exponential backoff on rate limit errors
- Requests succeed after retry

### Test 2.11: Search Result Caching
**Priority:** MEDIUM
**Type:** Performance

**Test Steps:**
1. Execute search: "exercise AND depression" on PubMed
2. Record response time (should be ~15 seconds)
3. Execute identical search within 60 minutes
4. Record response time (should be < 1 second from cache)
5. Wait 61 minutes
6. Execute identical search
7. Record response time (should be ~15 seconds, cache expired)

**Cache Headers Validation:**
- Response includes: `X-Cache: HIT` or `X-Cache: MISS`
- Cache-Control headers present

### Test 2.12: Search Error Handling
**Priority:** HIGH
**Type:** Error Handling

**Test Cases:**
| Test Case | Scenario | Expected Response |
|-----------|----------|-------------------|
| 2.12.1 | PubMed API down | Graceful degradation, error message |
| 2.12.2 | Malformed search query | 400 Bad Request with details |
| 2.12.3 | Empty search terms | 400 "Search terms required" |
| 2.12.4 | Unsupported database | 400 "Database 'xyz' not supported" |
| 2.12.5 | Network timeout | 504 Gateway Timeout, retry message |

---

## 3. Meta-Analysis Workflow Tests

### Test 3.1: Complete Workflow - Research Question 1
**Priority:** CRITICAL
**Type:** End-to-End

**Research Question:** "What is the effect of exercise on depression?"

**Full Workflow Steps:**

#### Step 1: Create Project
```json
POST /api/v1/meta-analysis/create
{
  "research_question": "What is the effect of exercise on depression?",
  "topic": "Exercise Interventions for Depression",
  "inclusion_criteria": [
    "Randomized controlled trials",
    "Adult participants (18+ years)",
    "Depression diagnosis (DSM or ICD)",
    "Exercise intervention (any type)",
    "Depression outcome measure"
  ],
  "exclusion_criteria": [
    "Non-English studies",
    "Adolescent-only populations",
    "Animal studies",
    "No control group"
  ],
  "databases": ["pubmed", "europepmc"],
  "peer_review_only": true,
  "date_range": {
    "start": "2015-01-01",
    "end": "2024-12-31"
  }
}
```

**Expected Response:**
```json
{
  "project_id": "proj_123abc",
  "status": "created",
  "workflow_stages": [
    "literature_search",
    "title_abstract_screening",
    "full_text_screening",
    "quality_assessment",
    "data_extraction",
    "statistical_analysis",
    "report_generation"
  ],
  "current_stage": "literature_search",
  "created_at": "2024-11-05T10:30:00Z"
}
```

#### Step 2: Execute Literature Search
```json
POST /api/v1/meta-analysis/{project_id}/search
```

**Expected Results:**
- Search completes within 60 seconds
- Minimum 30 studies found
- Studies stored in database with project_id
- PRISMA flow diagram data generated:
  - Records identified: 45
  - Records after deduplication: 38
  - Ready for screening: 38

#### Step 3: Title/Abstract Screening
**Manual Test:** Review screening interface
**Automated Test:** Use screening API

```json
POST /api/v1/meta-analysis/{project_id}/screen
{
  "screening_level": "title_abstract",
  "studies": [study_ids],
  "criteria": {
    "inclusion": [...],
    "exclusion": [...]
  }
}
```

**Expected AI Agent Decisions:**
```json
{
  "screened": 38,
  "included": 22,
  "excluded": 14,
  "uncertain": 2,
  "exclusion_reasons": {
    "wrong_population": 5,
    "wrong_intervention": 4,
    "wrong_outcome": 3,
    "not_rct": 2
  },
  "uncertain_studies": [
    {
      "study_id": "PMID:12345678",
      "reason": "Unclear if depression was primary outcome",
      "recommendation": "Full-text review recommended"
    }
  ]
}
```

**Human Verification:**
- QA reviews 5 randomly selected "included" studies - should agree
- QA reviews 5 randomly selected "excluded" studies - should agree
- QA reviews all "uncertain" studies - provides final decision

#### Step 4: Full-Text Screening
**Note:** Simulated for MVP (full-text PDFs not auto-downloaded yet)

```json
POST /api/v1/meta-analysis/{project_id}/screen-fulltext
{
  "studies": [included_study_ids]
}
```

**Expected Results:**
- 22 studies → 15 studies after full-text review
- 7 excluded with reasons:
  - Insufficient data for meta-analysis: 4
  - Wrong intervention type: 2
  - Duplicate data: 1

#### Step 5: Quality Assessment
```json
POST /api/v1/meta-analysis/{project_id}/quality-assessment
{
  "studies": [final_included_ids],
  "assessment_tool": "Cochrane Risk of Bias 2.0"
}
```

**Expected Results:**
```json
{
  "assessed": 15,
  "risk_of_bias": {
    "low": 8,
    "some_concerns": 5,
    "high": 2
  },
  "domains": {
    "randomization": {"low": 12, "some_concerns": 2, "high": 1},
    "deviations": {"low": 10, "some_concerns": 4, "high": 1},
    "missing_data": {"low": 9, "some_concerns": 4, "high": 2},
    "outcome_measurement": {"low": 13, "some_concerns": 2, "high": 0},
    "selective_reporting": {"low": 11, "some_concerns": 3, "high": 1}
  },
  "studies": [
    {
      "study_id": "PMID:123",
      "overall_bias": "low",
      "domains": {...},
      "notes": "Well-designed RCT with low attrition"
    }
  ]
}
```

#### Step 6: Data Extraction
```json
POST /api/v1/meta-analysis/{project_id}/extract-data
{
  "studies": [final_included_ids],
  "outcomes": ["depression_severity", "remission_rate"]
}
```

**Expected Extracted Data (per study):**
```json
{
  "study_id": "PMID:123",
  "sample_size": {
    "intervention": 50,
    "control": 48
  },
  "intervention_details": {
    "type": "Aerobic exercise",
    "duration_weeks": 12,
    "frequency_per_week": 3,
    "session_duration_minutes": 45
  },
  "outcomes": {
    "depression_severity": {
      "measure": "BDI-II",
      "intervention_mean": 12.3,
      "intervention_sd": 5.2,
      "control_mean": 18.7,
      "control_sd": 6.1,
      "time_point": "post-intervention"
    }
  },
  "quality_score": "low_risk"
}
```

#### Step 7: Statistical Analysis
```json
POST /api/v1/meta-analysis/{project_id}/analyze
{
  "outcome": "depression_severity",
  "effect_type": "continuous",
  "model": "random",
  "effect_measure": "hedges_g"
}
```

**Expected Results:**
```json
{
  "meta_analysis": {
    "pooled_effect": -0.62,
    "standard_error": 0.08,
    "ci_lower": -0.78,
    "ci_upper": -0.46,
    "z_value": 7.75,
    "p_value": 0.0001,
    "model": "random-effects (DL)",
    "interpretation": "Large effect favoring exercise intervention"
  },
  "heterogeneity": {
    "q_statistic": 18.5,
    "df": 14,
    "q_p_value": 0.18,
    "i_squared": 24.3,
    "tau_squared": 0.02,
    "interpretation": "low heterogeneity"
  },
  "publication_bias": {
    "eggers_test": {
      "intercept": 0.45,
      "p_value": 0.34,
      "interpretation": "No significant asymmetry detected"
    },
    "funnel_plot": {...}
  },
  "forest_plot": {...},
  "n_studies": 15,
  "total_participants": 847
}
```

**Statistical Validation:**
1. Verify calculations against R metafor:
   ```R
   library(metafor)

   # Input data from our 15 studies
   yi <- c(-0.65, -0.58, -0.70, ...) # Effect sizes
   sei <- c(0.15, 0.18, 0.12, ...) # Standard errors

   # Random-effects model
   res <- rma(yi, sei, method="DL")
   summary(res)

   # Should match our results within 1% tolerance
   ```

2. Manual verification:
   - Spot-check 3 studies' effect size calculations
   - Verify pooled effect is weighted average
   - Verify confidence intervals use correct z-value (1.96 for 95%)

#### Step 8: Generate Report
```json
POST /api/v1/meta-analysis/{project_id}/generate-report
{
  "format": "APA7",
  "sections": ["all"]
}
```

**Expected Report Sections:**
1. Title page
2. Abstract (structured)
3. Introduction
4. Methods
   - Search strategy
   - Inclusion/exclusion criteria
   - Quality assessment
   - Statistical methods
5. Results
   - PRISMA flow diagram
   - Study characteristics table
   - Forest plot
   - Funnel plot
   - Meta-analysis results
6. Discussion
7. References (auto-generated from included studies)

#### Step 9: Export Results
**Test all export formats:**
- CSV export of study data
- Excel export with multiple sheets
- JSON export with complete data
- PDF report
- Forest plot PNG
- Funnel plot PNG

**Validation:**
- Open each file and verify contents
- Check data integrity (no missing values)
- Verify formatting is professional

### Test 3.2: Complete Workflow - Research Question 2
**Priority:** CRITICAL
**Type:** End-to-End

**Research Question:** "Does mindfulness reduce anxiety?"

**Configuration Differences:**
- Different databases: ["pubmed", "arxiv", "core"]
- Different outcome type: anxiety scales
- Different inclusion criteria

**Test Focus:**
- Verify workflow adapts to different research topics
- Test with mix of peer-reviewed and preprints
- Validate filtering logic works correctly

**Expected Results:**
- Similar workflow stages completed
- Different effect size magnitude
- Potentially different heterogeneity
- Proper handling of preprint vs. peer-reviewed distinction

### Test 3.3: Complete Workflow - Research Question 3
**Priority:** CRITICAL
**Type:** End-to-End

**Research Question:** "Impact of diet on cardiovascular disease"

**Configuration:**
```json
{
  "research_question": "Impact of diet on cardiovascular disease",
  "effect_type": "binary",
  "effect_measure": "risk_ratio",
  "databases": ["pubmed", "europepmc", "core"],
  "peer_review_only": true
}
```

**Test Focus:**
- Binary outcomes (event/no event)
- Risk Ratio or Odds Ratio calculation
- Large result set handling (expect 100+ initial results)

**Expected Challenges:**
- More heterogeneity (diet is broad topic)
- Multiple sub-analyses needed (Mediterranean vs. Low-fat vs. DASH)
- Publication bias more likely with large literature

### Test 3.4: Workflow State Persistence
**Priority:** HIGH
**Type:** Functional

**Test Steps:**
1. Start RQ1 workflow
2. Complete up to screening stage
3. Close browser / logout
4. Login again
5. Navigate to project
6. Verify state restored:
   - Search results preserved
   - Screening decisions preserved
   - Can resume from screening stage

### Test 3.5: Multiple Concurrent Projects
**Priority:** MEDIUM
**Type:** Functional

**Test Steps:**
1. User creates Project A (RQ1)
2. User creates Project B (RQ2)
3. Work on Project A (complete search)
4. Switch to Project B (complete search)
5. Return to Project A (complete screening)
6. Verify no data mixing between projects

### Test 3.6: Workflow Validation - Missing Steps
**Priority:** HIGH
**Type:** Error Handling

**Test Cases:**
| Scenario | Action | Expected Behavior |
|----------|--------|-------------------|
| Skip search | Try to screen without search | 400 "Must complete search first" |
| Skip screening | Try to extract data without screening | 400 "Must complete screening first" |
| No studies included | Try to analyze with 0 studies | 400 "Need at least 2 studies" |
| Incomplete extraction | Try to analyze with missing data | 400 "Data extraction incomplete" |

### Test 3.7: Undo/Redo Screening Decisions
**Priority:** MEDIUM
**Type:** Usability

**Test Steps:**
1. Screen 10 studies
2. Realize mistake on Study #5
3. Use "Undo" to revert decision
4. Change decision from "Exclude" to "Include"
5. Verify count updates
6. Use "Redo" if needed

### Test 3.8: Conflict Resolution - Multiple Screeners
**Priority:** MEDIUM
**Type:** Collaboration

**Test Scenario:**
- Two researchers screening same project
- Measure inter-rater reliability
- Resolve conflicts via discussion notes

**Test Steps:**
1. Researcher A screens studies 1-20
2. Researcher B screens studies 1-20 (blind to A's decisions)
3. System identifies conflicts
4. Calculate Cohen's Kappa agreement
5. Present conflicts for resolution
6. Track final decisions and rationale

**Expected:**
- Kappa > 0.70 (substantial agreement)
- Conflict resolution interface works
- Audit trail of all decisions

---

## 4. Statistical Calculations Tests

### Test 4.1: Cohen's d Calculation
**Priority:** CRITICAL
**Type:** Accuracy

**Test Data (Known Result):**
```json
{
  "mean_treatment": 15.2,
  "mean_control": 20.8,
  "sd_treatment": 5.4,
  "sd_control": 6.1,
  "n_treatment": 50,
  "n_control": 48
}
```

**Expected Result (calculated in R):**
```R
library(effsize)
cohen.d(treatment, control, pooled=TRUE)

# Expected: d = -0.99, 95% CI [-1.40, -0.58]
```

**Our Calculation Must Match Within:**
- Effect size: ±0.01
- Standard error: ±0.005
- Confidence intervals: ±0.01

### Test 4.2: Hedge's g Calculation
**Priority:** CRITICAL
**Type:** Accuracy

**Test Data:**
Same as Cohen's d above

**Expected Result:**
- Hedge's g = -0.98 (slightly smaller than Cohen's d due to bias correction)
- Correction factor J = 0.99 for n=98

**Validation:**
- g < d (bias correction applied)
- Difference increases with smaller samples

### Test 4.3: Odds Ratio Calculation
**Priority:** CRITICAL
**Type:** Accuracy

**Test Data:**
```json
{
  "events_treatment": 15,
  "n_treatment": 100,
  "events_control": 30,
  "n_control": 100
}
```

**Expected Result:**
```R
# Odds treatment = 15/85 = 0.176
# Odds control = 30/70 = 0.429
# OR = 0.176/0.429 = 0.41

# 95% CI using exact method
library(epitools)
oddsratio(matrix(c(15,85,30,70), nrow=2))

# Expected: OR = 0.41, 95% CI [0.20, 0.81]
```

**Our Result Must Match Within:**
- OR: ±0.02
- CI bounds: ±0.03

### Test 4.4: Risk Ratio Calculation
**Priority:** CRITICAL
**Type:** Accuracy

**Test Data:**
Same as OR test above

**Expected Result:**
```R
# Risk treatment = 15/100 = 0.15
# Risk control = 30/100 = 0.30
# RR = 0.15/0.30 = 0.50

# Expected: RR = 0.50, 95% CI [0.28, 0.89]
```

### Test 4.5: Fixed-Effects Meta-Analysis
**Priority:** CRITICAL
**Type:** Accuracy

**Test Data (5 Studies):**
| Study | Effect Size | SE | Weight |
|-------|-------------|-----|--------|
| A | 0.50 | 0.10 | 100 |
| B | 0.60 | 0.15 | 44.4 |
| C | 0.45 | 0.12 | 69.4 |
| D | 0.55 | 0.11 | 82.6 |
| E | 0.48 | 0.13 | 59.2 |

**R Validation:**
```R
library(metafor)

yi <- c(0.50, 0.60, 0.45, 0.55, 0.48)
sei <- c(0.10, 0.15, 0.12, 0.11, 0.13)

res <- rma(yi, sei, method="FE")
summary(res)

# Expected:
# Pooled effect = 0.512
# SE = 0.0534
# 95% CI [0.407, 0.617]
# Z = 9.59, p < 0.0001
```

**Accuracy Requirements:**
- Pooled effect: within 0.005
- SE: within 0.001
- CI: within 0.01
- Z-value: within 0.1
- P-value: within 0.001

### Test 4.6: Random-Effects Meta-Analysis (DerSimonian-Laird)
**Priority:** CRITICAL
**Type:** Accuracy

**Test Data:**
Same 5 studies as above

**R Validation:**
```R
res <- rma(yi, sei, method="DL")
summary(res)

# Expected:
# Tau² = 0.0023
# Pooled effect = 0.513
# SE = 0.056
# 95% CI [0.403, 0.623]
# Z = 9.16, p < 0.0001
```

**Validation:**
- Tau²: within 0.001
- Pooled effect: within 0.01
- SE larger than fixed-effects (incorporating between-study variance)

### Test 4.7: Random-Effects Meta-Analysis (REML)
**Priority:** HIGH
**Type:** Accuracy

**Same Test Data**

**R Validation:**
```R
res <- rma(yi, sei, method="REML")
summary(res)

# Expected:
# Tau² = 0.0026 (slightly different from DL)
# Pooled effect = 0.513
# SE = 0.057
```

**Note:**
- REML preferred for small number of studies
- Should give similar but not identical results to DL

### Test 4.8: Heterogeneity Statistics (Q, I², τ²)
**Priority:** CRITICAL
**Type:** Accuracy

**Test Data:**
Same 5 studies

**Expected Results:**
```R
# Q statistic
Q <- sum(weights * (effects - pooled)^2)
# Expected: Q = 4.82

# Degrees of freedom
df <- 5 - 1 = 4

# Q p-value (chi-square distribution)
pchisq(Q, df, lower.tail=FALSE)
# Expected: p = 0.31 (not significant)

# I² statistic
I2 <- max(0, ((Q - df) / Q) * 100)
# Expected: I² = 17% (low heterogeneity)

# Tau² (from DL method)
# Expected: τ² = 0.0023
```

**Interpretation Validation:**
- I² < 25%: "low heterogeneity" ✓
- Q p > 0.05: Not significant ✓
- Random effects CI wider than fixed effects ✓

### Test 4.9: Publication Bias - Egger's Test
**Priority:** HIGH
**Type:** Accuracy

**Test Data:**
10 studies with asymmetric funnel plot

**R Validation:**
```R
library(metafor)

yi <- c(0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7, 0.85)
sei <- c(0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25, 0.30, 0.40)

res <- rma(yi, sei, method="FE")
regtest(res, model="lm")

# Expected:
# Intercept = 2.15
# SE = 0.68
# t = 3.16, p = 0.013
# Interpretation: Significant asymmetry (possible publication bias)
```

**Our Result Validation:**
- Intercept: within 0.1
- P-value: within 0.01
- Correct interpretation provided

### Test 4.10: Funnel Plot Data Generation
**Priority:** MEDIUM
**Type:** Functional

**Test Data:**
Generate funnel plot data for 10 studies

**Expected Output:**
```json
{
  "studies": [
    {
      "effect_size": 0.50,
      "standard_error": 0.10,
      "precision": 10.0,
      "study_name": "Study A"
    },
    ...
  ],
  "pooled_effect": 0.512,
  "reference_lines": {
    "se_range": [0, 0.05, 0.10, ..., 0.40],
    "ci_lower": [...],
    "ci_upper": [...]
  }
}
```

**Validation:**
- Plot can be rendered correctly
- Asymmetry visually detectable if present
- Reference lines (95% CI funnel) correct

---

## 5. Data Export Tests

### Test 5.1: Export to CSV
**Priority:** HIGH
**Type:** Functional

**Test Steps:**
1. Complete RQ1 meta-analysis
2. Click "Export Results → CSV"
3. Download file: `exercise_depression_meta_analysis.csv`

**Expected CSV Structure:**
```csv
study_id,authors,year,journal,title,sample_size_treatment,sample_size_control,mean_treatment,sd_treatment,mean_control,sd_control,effect_size,standard_error,ci_lower,ci_upper,weight,quality_assessment
PMID:123,"Smith et al.",2020,"J Psych",Exercise for Depression,50,48,15.2,5.4,20.8,6.1,-0.99,0.21,-1.40,-0.58,22.5,low_risk
...
```

**Validation:**
- All studies included
- No missing values
- Proper CSV escaping (commas in titles)
- UTF-8 encoding
- Opens correctly in Excel and Google Sheets

### Test 5.2: Export to Excel
**Priority:** HIGH
**Type:** Functional

**Expected Excel File:**
- **Sheet 1 - Summary:** Overview of meta-analysis results
- **Sheet 2 - Studies:** Detailed study data
- **Sheet 3 - Statistics:** Statistical results
- **Sheet 4 - Quality Assessment:** Risk of bias data
- **Sheet 5 - PRISMA:** Flow diagram data

**Validation:**
- Multiple sheets present
- Proper formatting (headers bold, numbers formatted)
- Formulas work (if any)
- Charts embedded (forest plot, funnel plot)
- File size reasonable (< 5 MB for 50 studies)

### Test 5.3: Export to JSON
**Priority:** MEDIUM
**Type:** Functional

**Expected JSON Structure:**
```json
{
  "meta_analysis": {
    "project_id": "proj_123",
    "research_question": "What is the effect of exercise on depression?",
    "created_at": "2024-11-05T10:30:00Z",
    "completed_at": "2024-11-05T11:45:00Z"
  },
  "search_results": {
    "databases_searched": ["pubmed", "europepmc"],
    "total_found": 45,
    "duplicates_removed": 7,
    "screened": 38
  },
  "screening": {
    "included": 15,
    "excluded": 23,
    "exclusion_reasons": {...}
  },
  "studies": [...],
  "statistical_results": {...},
  "heterogeneity": {...},
  "publication_bias": {...}
}
```

**Validation:**
- Valid JSON (passes JSON validator)
- Complete data included
- Can be re-imported to system
- Suitable for programmatic access

### Test 5.4: Export Forest Plot (PNG)
**Priority:** HIGH
**Type:** Functional

**Expected Image:**
- High resolution (300 DPI minimum)
- Professional appearance
- Elements included:
  - Study names (left)
  - Effect sizes with confidence intervals (squares & lines)
  - Numerical effect sizes (right)
  - Weights (right)
  - Overall pooled effect (diamond)
  - Heterogeneity statistics (bottom)
  - Legend
  - Scale labeled correctly

**Validation:**
- Image renders correctly
- Text readable at print size
- Colors distinguishable (color-blind friendly)
- Can be inserted into Word document

**Acceptance Criteria:**
- Publication quality
- Meets journal submission standards

### Test 5.5: Export Funnel Plot (PNG)
**Priority:** MEDIUM
**Type:** Functional

**Expected Image:**
- X-axis: Effect size
- Y-axis: Standard error (inverted) or Precision
- Individual studies plotted as dots
- Pooled effect vertical line
- 95% confidence region (funnel lines)
- Pseudo-confidence region lines

**Validation:**
- Asymmetry visible if present
- Labels clear
- Reference lines correctly positioned

### Test 5.6: Export Full PDF Report
**Priority:** HIGH
**Type:** Functional

**Expected PDF:**
- 15-25 pages
- Professional formatting
- Sections:
  1. Cover page with title, authors, date
  2. Table of contents
  3. Abstract (structured)
  4. Introduction
  5. Methods
  6. Results
  7. Discussion
  8. References
  9. Appendices (PRISMA checklist, search strategies)

**Validation:**
- All sections present
- Figures embedded correctly
- Tables formatted properly
- References numbered correctly
- Page numbers
- Headers/footers
- PDF searchable (not scanned image)

---

## 6. Performance Tests

### Test 6.1: Search Response Time
**Priority:** HIGH
**Type:** Performance

**Test Scenarios:**
| Database | Query Complexity | Expected Time | Max Acceptable |
|----------|------------------|---------------|----------------|
| PubMed | Simple (2 terms) | < 10s | 30s |
| PubMed | Complex (5 terms + filters) | < 20s | 45s |
| arXiv | Simple | < 8s | 25s |
| Europe PMC | Simple | < 12s | 35s |
| CORE | Simple | < 15s | 40s |
| All 4 databases | Parallel search | < 30s | 60s |

**Test Method:**
```python
import time

start = time.time()
response = requests.post(f"{API_BASE_URL}/api/v1/search", json={
    "search_terms": ["exercise", "depression"],
    "databases": ["pubmed", "arxiv", "europepmc", "core"]
})
duration = time.time() - start

assert duration < 60, f"Search took {duration}s, exceeds 60s limit"
assert response.status_code == 200
```

### Test 6.2: Meta-Analysis Calculation Time
**Priority:** HIGH
**Type:** Performance

**Test Scenarios:**
| # Studies | Effect Type | Model | Expected Time | Max Acceptable |
|-----------|-------------|-------|---------------|----------------|
| 5 | Continuous | Random | < 2s | 5s |
| 15 | Continuous | Random | < 5s | 15s |
| 50 | Continuous | Random | < 15s | 45s |
| 100 | Continuous | Random | < 30s | 90s |
| 15 | Binary | Random | < 5s | 15s |

**Includes:**
- Effect size calculations
- Heterogeneity assessment
- Publication bias tests
- Forest plot generation
- Funnel plot generation

### Test 6.3: Concurrent Users - 10 Simultaneous Meta-Analyses
**Priority:** HIGH
**Type:** Load Testing

**Test Setup:**
- 10 test users
- Each starts a meta-analysis simultaneously
- Monitor system resources

**Test Script:**
```python
import concurrent.futures

def run_meta_analysis(user_id):
    # Login
    token = login(f"user{user_id}@test.com", "password")

    # Create project
    start = time.time()
    project = create_project(token, research_question="Exercise and depression")

    # Run search
    search_results = run_search(token, project['id'])

    # Run analysis
    analysis_results = run_analysis(token, project['id'])

    duration = time.time() - start
    return user_id, duration, "success"

# Run 10 concurrent meta-analyses
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(run_meta_analysis, i) for i in range(10)]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

# All should complete successfully
assert all(r[2] == "success" for r in results)

# Average time should be < 90 seconds
avg_time = sum(r[1] for r in results) / len(results)
assert avg_time < 90, f"Average time {avg_time}s exceeds 90s"
```

**Resource Monitoring:**
- CPU usage stays < 80%
- Memory usage stays < 4 GB
- Database connections < 100
- No connection pool exhaustion

### Test 6.4: Large File Export Performance
**Priority:** MEDIUM
**Type:** Performance

**Test Scenario:**
Meta-analysis with 100 studies

**Export Tests:**
| Format | Expected Time | Max Acceptable | File Size |
|--------|---------------|----------------|-----------|
| CSV | < 2s | 10s | < 500 KB |
| Excel | < 5s | 20s | < 2 MB |
| JSON | < 3s | 15s | < 1 MB |
| PDF Report | < 15s | 45s | < 5 MB |

**Validation:**
- No timeout errors
- Files download successfully
- File size within expected range

### Test 6.5: Database Query Performance
**Priority:** HIGH
**Type:** Performance

**Test Queries:**
```sql
-- Query 1: List user's projects
SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC LIMIT 20;
-- Expected: < 50ms

-- Query 2: Get project with all studies
SELECT p.*, s.* FROM projects p
JOIN studies s ON p.id = s.project_id
WHERE p.id = ?;
-- Expected: < 200ms for 50 studies

-- Query 3: Search studies by keyword
SELECT * FROM studies WHERE title ILIKE ? OR abstract ILIKE ?;
-- Expected: < 500ms with index
```

**Performance Requirements:**
- 95th percentile < expected time
- 99th percentile < 2x expected time
- No queries > 5 seconds

### Test 6.6: API Rate Limiting - Authenticated Users
**Priority:** MEDIUM
**Type:** Performance

**Test Scenario:**
Authenticated user makes 150 requests in 60 seconds

**Expected Behavior:**
- Rate limit: 100 requests per minute for authenticated users
- Requests 1-100: All succeed (200 OK)
- Requests 101-150: Rate limited (429 Too Many Requests)
- Response includes headers:
  ```
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1699200000
  ```

**Test Code:**
```python
for i in range(150):
    response = requests.get(
        f"{API_BASE_URL}/api/v1/meta-analysis/list",
        headers={"Authorization": f"Bearer {token}"}
    )

    if i < 100:
        assert response.status_code == 200
    else:
        assert response.status_code == 429
        assert "Retry-After" in response.headers
```

### Test 6.7: API Rate Limiting - Unauthenticated Users
**Priority:** MEDIUM
**Type:** Performance

**Expected:**
- Rate limit: 20 requests per minute for unauthenticated
- Applies to public endpoints (health, docs)
- Same 429 response on limit exceeded

### Test 6.8: Cache Hit Rate Monitoring
**Priority:** LOW
**Type:** Performance

**Test Scenario:**
- Execute same search 10 times
- Monitor cache hit rate

**Expected:**
- First request: Cache MISS (hits database)
- Requests 2-10: Cache HIT (returns cached data)
- Cache hit rate: 90%
- Response time for cached: < 100ms

---

## 7. Edge Cases & Error Handling

### Test 7.1: Empty Search Results
**Priority:** HIGH
**Type:** Edge Case

**Test Query:**
"Effect of purple unicorns on quantum entanglement in humans"

**Expected Response:**
```json
{
  "status": 200,
  "total_results": 0,
  "studies": [],
  "message": "No studies found matching your search criteria. Consider broadening your search terms or trying different databases.",
  "suggestions": [
    "Remove highly specific terms",
    "Try synonyms",
    "Expand date range",
    "Search additional databases"
  ]
}
```

**Validation:**
- No errors or crashes
- Helpful message provided
- User can modify search and try again

### Test 7.2: Single Study Meta-Analysis
**Priority:** HIGH
**Type:** Edge Case

**Test Scenario:**
User tries to run meta-analysis with only 1 study included

**Expected Behavior:**
```json
{
  "status": 400,
  "error": "Insufficient studies for meta-analysis",
  "message": "Meta-analysis requires at least 2 studies. You have 1 study included.",
  "recommendation": "Broaden inclusion criteria or conduct a narrative review instead.",
  "studies_needed": 2,
  "studies_current": 1
}
```

**Special Handling:**
- Offer to generate single-study report
- Suggest narrative synthesis
- Don't allow statistical pooling

### Test 7.3: Studies with Missing Data
**Priority:** HIGH
**Type:** Edge Case

**Test Scenarios:**
1. **Missing standard deviations:**
   - Can't calculate effect size
   - Exclude from meta-analysis
   - Flag in report: "3 studies excluded due to missing SD"

2. **Missing sample sizes:**
   - Can't calculate weights
   - Exclude from analysis
   - Document in PRISMA flow

3. **Partial data:**
   - Include if possible with available data
   - Note limitations
   - Sensitivity analysis without these studies

**Expected Behavior:**
- Graceful handling (no crash)
- Clear error messages
- Detailed logs for researcher
- Suggestions for obtaining missing data

### Test 7.4: Very Large Datasets (1000+ Studies)
**Priority:** MEDIUM
**Type:** Edge Case

**Test Scenario:**
Search for "cancer treatment" returns 2000+ studies

**Expected Behavior:**
1. **Search Phase:**
   - Return maximum 1000 results (configurable limit)
   - Provide pagination for more
   - Warn user: "Large result set. Consider refining search."

2. **Screening Phase:**
   - Batch processing (100 studies at a time)
   - Progress bar showing completion
   - Allow saving and resuming

3. **Analysis Phase:**
   - Process in chunks if memory constrained
   - Estimated time displayed
   - Background job with status updates

**Performance Requirements:**
- Search: < 2 minutes for 1000 studies
- Screening: ~1 study per second (AI agent)
- Analysis: < 5 minutes for 1000 studies

### Test 7.5: Concurrent Users - Same Project
**Priority:** MEDIUM
**Type:** Edge Case

**Test Scenario:**
Two users editing same project simultaneously

**Expected Behavior:**
- Optimistic locking (last write wins with warning)
- Conflict detection
- Auto-save every 30 seconds
- Version history maintained

**Test Steps:**
1. User A and User B open same project
2. User A excludes Study #5
3. User B includes Study #5 (before refresh)
4. User B saves → Conflict detected
5. System shows:
   ```
   Conflict: Another user modified this project.
   User A excluded Study #5 at 10:30 AM.
   You included Study #5 at 10:32 AM.

   [Use My Version] [Use Their Version] [Merge]
   ```

### Test 7.6: Session Timeout Handling
**Priority:** HIGH
**Type:** Resilience

**Test Scenario:**
User leaves browser open for 2 hours (idle)

**Expected Behavior:**
1. After 60 minutes: Warning toast appears
   ```
   "Your session will expire in 5 minutes due to inactivity.
   Click here to extend session."
   ```

2. After 65 minutes: Session expires
   - Access token invalid
   - Next API call returns 401
   - User redirected to login
   - After login, return to same page
   - Unsaved work preserved in local storage

**Test Code:**
```python
# Simulate session timeout
time.sleep(3700)  # 61 minutes

response = requests.get(
    f"{API_BASE_URL}/api/v1/auth/me",
    headers={"Authorization": f"Bearer {old_token}"}
)

assert response.status_code == 401
assert "expired" in response.json()["error"].lower()
```

### Test 7.7: Invalid API Credentials
**Priority:** HIGH
**Type:** Error Handling

**Test Scenarios:**
| Scenario | Expected Response |
|----------|-------------------|
| Missing Anthropic API key | 500 "AI service unavailable" |
| Invalid Anthropic API key | 500 "AI service authentication failed" |
| PubMed API down | Partial results from other databases, warning message |
| All external APIs down | 503 "Service temporarily unavailable. Please try again later." |

**Graceful Degradation:**
- If PubMed fails: Continue with other databases
- If AI agent fails: Offer manual screening mode
- If database fails: Queue request for later processing

### Test 7.8: Database Connection Loss
**Priority:** CRITICAL
**Type:** Resilience

**Test Scenario:**
Simulate database connection loss during meta-analysis

**Expected Behavior:**
1. Connection pool detects failure
2. Automatic retry (3 attempts with exponential backoff)
3. If all retries fail:
   ```json
   {
     "status": 503,
     "error": "Database temporarily unavailable",
     "message": "We're experiencing technical difficulties. Your work has been saved and will resume automatically.",
     "retry_after": 60
   }
   ```
4. Background job retries every 60 seconds
5. When database recovers, processing resumes
6. User notified: "Your analysis is now complete!"

### Test 7.9: Redis Connection Loss
**Priority:** HIGH
**Type:** Resilience

**Impact:**
- Session storage unavailable
- Cache unavailable
- Rate limiting unavailable

**Expected Behavior:**
- Fallback to in-memory sessions (for current requests)
- Disable caching (slight performance degradation)
- Disable rate limiting (security risk acceptable temporarily)
- Log error and alert administrators
- No user-facing errors

### Test 7.10: Malformed Input Data
**Priority:** HIGH
**Type:** Security

**Test Cases:**
| Input | Expected Response |
|-------|-------------------|
| SQL injection in search | Sanitized, no SQL executed |
| XSS in study title | HTML escaped |
| Buffer overflow attempt | Request rejected |
| Invalid JSON | 400 "Invalid JSON format" |
| Missing required fields | 400 "Missing required field: research_question" |
| Invalid data types | 400 "Field 'year' must be integer" |

### Test 7.11: API Timeout Scenarios
**Priority:** HIGH
**Type:** Resilience

**Test Scenarios:**
1. **PubMed search timeout:**
   - Timeout after 30 seconds
   - Return partial results from other databases
   - Message: "PubMed search timed out. Results from other databases only."

2. **AI agent timeout:**
   - Screening takes > 5 minutes
   - Move to background job
   - Send email when complete

3. **Export generation timeout:**
   - PDF generation takes > 60 seconds
   - Generate asynchronously
   - Provide download link when ready

### Test 7.12: High Heterogeneity Handling
**Priority:** MEDIUM
**Type:** Statistical

**Test Scenario:**
Meta-analysis with I² > 75% (high heterogeneity)

**Expected Behavior:**
1. Warning displayed:
   ```
   "High heterogeneity detected (I² = 82%).
   Random-effects model used.
   Consider subgroup analysis or meta-regression."
   ```

2. Recommendations provided:
   - Subgroup by intervention type
   - Subgroup by population
   - Sensitivity analysis
   - Investigate sources of heterogeneity

3. Forest plot shows wider confidence intervals

4. Discussion section notes heterogeneity

---

## 8. Integration Tests

### Test 8.1: Full Platform Integration
**Priority:** CRITICAL
**Type:** End-to-End

**Test Scenario:**
Complete meta-analysis from registration to publication-ready report

**Steps:**
1. Register new user account
2. Verify email (if email verification enabled)
3. Login to platform
4. Create new meta-analysis project
5. Configure search (4 databases)
6. Execute search
7. Review and screen studies
8. Conduct quality assessment
9. Extract data
10. Run statistical analysis
11. Review results
12. Generate report
13. Export in multiple formats
14. Download all files
15. Logout

**Duration:** ~2 hours (with manual steps)

**Pass Criteria:**
- All steps complete without errors
- Data persists across sessions
- Exported files are complete and correct
- Report is publication-ready

### Test 8.2: Frontend-Backend Integration
**Priority:** HIGH
**Type:** Integration

**Test Areas:**
1. **Authentication:**
   - Login form submits to backend
   - Token stored correctly
   - Token sent with each request

2. **Search Interface:**
   - Database checkboxes map to API request
   - Results display correctly
   - Pagination works

3. **Screening Interface:**
   - Include/Exclude buttons call API
   - Counts update in real-time
   - Undo/Redo works

4. **Visualization:**
   - Forest plot renders from API data
   - Funnel plot renders correctly
   - Interactive features work

### Test 8.3: Database Schema Validation
**Priority:** HIGH
**Type:** Integration

**Test Queries:**
```sql
-- Check all tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- Expected tables:
-- users, projects, studies, screening_decisions,
-- quality_assessments, statistical_results, audit_logs

-- Check foreign key constraints
SELECT constraint_name, table_name, column_name
FROM information_schema.key_column_usage
WHERE constraint_schema = 'public';

-- Check indexes exist
SELECT indexname, tablename FROM pg_indexes
WHERE schemaname = 'public';
```

**Validation:**
- All expected tables present
- Foreign keys enforce referential integrity
- Indexes on frequently queried columns
- No orphaned records

### Test 8.4: Agent Communication
**Priority:** HIGH
**Type:** Integration

**Test Scenario:**
Verify agent orchestration works correctly

**Agents:**
1. Coordinator Agent
2. Search Agent
3. Screening Agent
4. Quality Assessment Agent
5. Data Extraction Agent
6. Statistical Agent
7. QA Agent (question answering)

**Test:**
1. Coordinator receives meta-analysis request
2. Coordinator delegates to Search Agent
3. Search Agent returns results to Coordinator
4. Coordinator passes to Screening Agent
5. Continue through pipeline
6. All agents log decisions to audit trail
7. QA Agent can answer questions about process

**Validation:**
- Messages passed correctly between agents
- No data loss in handoffs
- Audit trail complete
- QA agent has full context

### Test 8.5: API Versioning
**Priority:** MEDIUM
**Type:** Integration

**Test:**
1. Call v1 endpoint: `/api/v1/meta-analysis/create`
2. Verify response format matches v1 spec
3. If v2 exists: Call `/api/v2/meta-analysis/create`
4. Verify v1 still works (backward compatibility)

**Version Policy:**
- v1 supported for at least 12 months after v2 release
- Deprecation warnings in response headers
- Migration guide provided

### Test 8.6: External API Integration
**Priority:** CRITICAL
**Type:** Integration

**APIs:**
1. **PubMed E-utilities:**
   - esearch (search)
   - efetch (retrieve)
   - esummary (summary)

2. **arXiv API:**
   - Query API
   - Metadata API

3. **Europe PMC API:**
   - Search API
   - FullText API

4. **CORE API v3:**
   - Search endpoint
   - Download endpoint

5. **Anthropic Claude API:**
   - Messages API
   - Streaming API

**Test Each API:**
- Authentication works
- Rate limiting respected
- Error handling robust
- Data parsing correct

---

## 9. Security Tests

### Test 9.1: SQL Injection Prevention
**Priority:** CRITICAL
**Type:** Security

**Test Payloads:**
```sql
' OR '1'='1
'; DROP TABLE users; --
' UNION SELECT * FROM users--
admin'--
```

**Test Inputs:**
- Email field during registration
- Search query field
- Project name field
- Any user input field

**Expected:**
- All inputs sanitized
- Parameterized queries used
- No SQL executed from user input

**Validation Method:**
```python
# Attempt SQL injection
response = requests.post(
    f"{API_BASE_URL}/api/v1/auth/register",
    json={
        "email": "admin'--@test.com",
        "password": "test123"
    }
)

# Should fail validation or be safely escaped
assert response.status_code in [400, 422]
# OR email stored as literal string "admin'--@test.com"
```

### Test 9.2: Cross-Site Scripting (XSS) Prevention
**Priority:** CRITICAL
**Type:** Security

**Test Payloads:**
```html
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
javascript:alert('XSS')
```

**Test Inputs:**
- User full name
- Project title
- Study title
- Notes fields

**Expected:**
- All HTML escaped in output
- JavaScript not executed
- Rendered as plain text

**Frontend Validation:**
```javascript
// React should escape by default
<div>{userInput}</div>  // Safe

// Dangerous (should never be used):
<div dangerouslySetInnerHTML={{__html: userInput}} />  // Avoid
```

### Test 9.3: Authentication Bypass Attempts
**Priority:** CRITICAL
**Type:** Security

**Test Scenarios:**
1. **Access protected endpoint without token:**
   ```bash
   curl https://api.example.com/api/v1/meta-analysis/list
   # Expected: 401 Unauthorized
   ```

2. **Use expired token:**
   ```bash
   curl -H "Authorization: Bearer <expired_token>" \
     https://api.example.com/api/v1/auth/me
   # Expected: 401 Token expired
   ```

3. **Modify JWT payload:**
   - Take valid JWT
   - Decode payload
   - Change user_id
   - Re-encode (without signing)
   - Attempt to use
   - Expected: 401 Invalid signature

4. **Reuse revoked token:**
   - Login
   - Logout (revoke token)
   - Try to use same token
   - Expected: 401 Token revoked

### Test 9.4: Password Security
**Priority:** CRITICAL
**Type:** Security

**Validation:**
1. **Passwords hashed:**
   ```sql
   SELECT hashed_password FROM users LIMIT 1;
   -- Should be bcrypt hash: $2b$12$...
   -- Should NOT be plain text
   ```

2. **Salt used:**
   - Each password has unique salt
   - Salt stored with hash

3. **Bcrypt cost factor:**
   - Minimum 12 rounds
   - Check: `$2b$12$...` (12 is cost factor)

4. **Password not logged:**
   - Check application logs
   - Verify no passwords in logs or errors

### Test 9.5: API Key Security
**Priority:** HIGH
**Type:** Security

**Validation:**
1. **API keys cryptographically strong:**
   - Length: 64 characters minimum
   - Entropy: 256+ bits
   - Format: Base64 or hex

2. **API keys hashed in database:**
   ```sql
   SELECT key_hash, key_prefix FROM api_keys LIMIT 1;
   -- key_hash: hashed value (not plain text)
   -- key_prefix: First 8 chars (for identification)
   ```

3. **API key shown only once:**
   - At creation, full key returned
   - Subsequent API calls: show prefix only
   - Cannot retrieve full key again

4. **API key rotation:**
   - User can create new key
   - User can delete old key
   - Old key immediately invalid

---

## Acceptance Criteria

### Overall Pass Criteria

**Critical Tests (Must Pass 100%):**
- All authentication tests
- All security tests
- Statistical accuracy tests (within tolerance)
- Full workflow for all 3 research questions

**High Priority Tests (Must Pass 95%):**
- Literature search tests
- Data export tests
- Performance tests (within acceptable limits)

**Medium Priority Tests (Must Pass 90%):**
- Edge case handling
- Integration tests

**Low Priority Tests (Must Pass 80%):**
- UI/UX tests
- Nice-to-have features

### Production Readiness Decision Matrix

| Category | Pass Rate | Status | Decision |
|----------|-----------|--------|----------|
| Critical | 100% | GREEN | GO |
| Critical | 95-99% | YELLOW | GO with cautions |
| Critical | <95% | RED | NO-GO |
| High Priority | 95% | GREEN | GO |
| High Priority | 85-94% | YELLOW | GO with monitoring |
| High Priority | <85% | RED | NO-GO |

### Statistical Accuracy Requirements

**Effect Size Calculations:**
- Cohen's d: within 1% of R calculation
- Hedge's g: within 1% of R calculation
- Odds Ratio: within 2% of R calculation
- Risk Ratio: within 2% of R calculation

**Meta-Analysis Pooling:**
- Pooled effect: within 0.5% of R metafor
- Standard error: within 1% of R
- Confidence intervals: within 1% of R
- Heterogeneity (I²): within 5 percentage points

**Replication Studies:**
- Match published meta-analysis results within 5%
- Study inclusion agreement > 90% with original

### Performance Requirements

**Response Times:**
- Health check: < 1 second
- Search (single DB): < 30 seconds
- Search (4 DBs): < 60 seconds
- Meta-analysis calculation: < 60 seconds for 50 studies
- Report generation: < 120 seconds

**Scalability:**
- Support 10 concurrent users
- Handle 1000 studies in single meta-analysis
- Database queries < 500ms (95th percentile)

### Security Requirements

**Must Pass All:**
- No SQL injection vulnerabilities
- No XSS vulnerabilities
- Passwords properly hashed (bcrypt)
- HTTPS enforced
- CORS properly configured
- Rate limiting implemented
- Authentication required for protected endpoints

---

## Test Execution Schedule

### Phase 1: Core Functionality (Week 1)
- Day 1: Authentication tests
- Day 2: Literature search tests (individual databases)
- Day 3: Literature search tests (combined)
- Day 4: Workflow tests RQ1
- Day 5: Workflow tests RQ2 & RQ3

### Phase 2: Statistical Validation (Week 2)
- Day 1-2: Effect size calculation tests
- Day 3-4: Meta-analysis calculation tests
- Day 5: Statistical accuracy validation vs R

### Phase 3: Exports & Performance (Week 2)
- Day 1: Data export tests (all formats)
- Day 2-3: Performance and load tests
- Day 4: Edge case testing
- Day 5: Integration testing

### Phase 4: Security & Final Validation (Week 3)
- Day 1-2: Security testing (all vulnerabilities)
- Day 3: End-to-end integration tests
- Day 4: Regression testing
- Day 5: Final sign-off and documentation

---

## Bug Reporting Template

```markdown
**Bug ID:** BUG-001
**Priority:** Critical / High / Medium / Low
**Category:** Authentication / Search / Statistical / Performance / Security / UI
**Status:** Open / In Progress / Fixed / Verified / Closed

**Summary:**
Brief description of the bug

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- Browser/Client: Chrome 120
- Backend Version: v0.1.0
- Database: PostgreSQL 15
- Test Account: qa-researcher-1@example.com

**Screenshots/Logs:**
Attach relevant files

**Additional Context:**
Any other relevant information
```

---

## Test Result Summary Template

```markdown
# Test Execution Summary
**Date:** 2024-11-05
**Tester:** QA Engineer Name
**Build Version:** v0.1.0

## Overall Results
- Total Tests: 82
- Passed: XX
- Failed: XX
- Skipped: XX
- Pass Rate: XX%

## Category Breakdown
| Category | Total | Passed | Failed | Pass Rate |
|----------|-------|--------|--------|-----------|
| Authentication | 8 | X | X | XX% |
| Literature Search | 12 | X | X | XX% |
| Workflow | 15 | X | X | XX% |
| Statistical | 10 | X | X | XX% |
| Export | 6 | X | X | XX% |
| Performance | 8 | X | X | XX% |
| Edge Cases | 12 | X | X | XX% |
| Integration | 6 | X | X | XX% |
| Security | 5 | X | X | XX% |

## Critical Issues
1. [BUG-001] Description
2. [BUG-002] Description

## Recommendation
[ ] GO - Production Ready
[ ] GO WITH CAUTIONS - Minor issues, monitor closely
[ ] NO-GO - Critical issues must be fixed

**Sign-off:**
QA Engineer: __________
Date: __________
```

---

## Appendix A: Test Data Fixtures

### Sample Research Questions
1. "What is the effect of exercise on depression?"
2. "Does mindfulness reduce anxiety?"
3. "Impact of diet on cardiovascular disease?"
4. "Effectiveness of cognitive behavioral therapy for insomnia"
5. "Does vitamin D supplementation prevent fractures in elderly?"

### Sample Studies for Testing

**Study 1: Exercise for Depression**
```json
{
  "pmid": "12345678",
  "title": "Aerobic Exercise for Major Depressive Disorder: A Randomized Trial",
  "authors": ["Smith J", "Jones A", "Williams B"],
  "journal": "Journal of Affective Disorders",
  "year": 2020,
  "doi": "10.1016/j.jad.2020.01.001",
  "sample_size_intervention": 50,
  "sample_size_control": 48,
  "mean_intervention": 15.2,
  "sd_intervention": 5.4,
  "mean_control": 20.8,
  "sd_control": 6.1,
  "outcome_measure": "BDI-II",
  "intervention_type": "Aerobic exercise",
  "duration_weeks": 12,
  "frequency_per_week": 3
}
```

### R Validation Scripts

**Effect Size Calculation:**
```R
library(metafor)

# Cohen's d
mean1 <- 15.2
mean2 <- 20.8
sd1 <- 5.4
sd2 <- 6.1
n1 <- 50
n2 <- 48

# Pooled SD
pooled_sd <- sqrt(((n1-1)*sd1^2 + (n2-1)*sd2^2) / (n1+n2-2))

# Cohen's d
d <- (mean1 - mean2) / pooled_sd
print(paste("Cohen's d:", round(d, 3)))

# SE of d
se_d <- sqrt((n1+n2)/(n1*n2) + d^2/(2*(n1+n2)))
print(paste("SE:", round(se_d, 3)))

# 95% CI
ci_lower <- d - 1.96*se_d
ci_upper <- d + 1.96*se_d
print(paste("95% CI: [", round(ci_lower, 3), ",", round(ci_upper, 3), "]"))
```

**Meta-Analysis:**
```R
# Sample data (5 studies)
yi <- c(0.50, 0.60, 0.45, 0.55, 0.48)
sei <- c(0.10, 0.15, 0.12, 0.11, 0.13)

# Fixed-effects
res_fe <- rma(yi, sei, method="FE")
print(res_fe)

# Random-effects (DL)
res_re <- rma(yi, sei, method="DL")
print(res_re)

# Heterogeneity
print(paste("Q statistic:", round(res_re$QE, 2)))
print(paste("I-squared:", round(res_re$I2, 1), "%"))
print(paste("Tau-squared:", round(res_re$tau2, 4)))

# Egger's test
regtest(res_re)
```

---

## Appendix B: Environment Setup Script

```bash
#!/bin/bash
# setup_test_environment.sh

# Install dependencies
pip install pytest requests numpy scipy pandas

# Set environment variables
export API_BASE_URL="https://meta-analysis-tool-production.up.railway.app"
export FRONTEND_URL="https://meta-analysis-tool.vercel.app"
export TEST_USER_EMAIL="qa-researcher-1@example.com"
export TEST_USER_PASSWORD="SecurePass123!"

# Create test data directory
mkdir -p test_results
mkdir -p test_fixtures

# Download R validation scripts
wget https://example.com/validation_scripts.R -O test_fixtures/validation.R

echo "Test environment setup complete!"
echo "Run tests with: pytest -v"
```

---

## Appendix C: Continuous Integration Configuration

```yaml
# .github/workflows/qa-tests.yml
name: QA Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  qa-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements-test.txt

    - name: Run authentication tests
      run: pytest tests/test_auth.py -v

    - name: Run search tests
      run: pytest tests/test_search.py -v

    - name: Run statistical tests
      run: pytest tests/test_statistics.py -v

    - name: Run security tests
      run: pytest tests/test_security.py -v

    - name: Generate test report
      run: pytest --html=report.html --self-contained-html

    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: report.html
```

---

**END OF COMPREHENSIVE TEST PLAN**

**Version:** 1.0
**Total Pages:** 35
**Last Updated:** 2025-11-05
**Next Review:** Before production deployment
