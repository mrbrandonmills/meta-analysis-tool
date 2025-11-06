# EXPECTED VS ACTUAL RESULTS TEMPLATE
## Meta-Analysis Research Platform - Test Results

**Test Session ID:** TEST-________
**Date:** ______________
**Tester:** ______________
**Environment:** ☐ Production ☐ Staging ☐ Local
**Build Version:** ______________

---

## Research Question 1: Exercise and Depression

### Test Configuration

```json
{
  "research_question": "What is the effect of exercise on depression?",
  "topic": "Exercise Interventions for Depression",
  "databases": ["pubmed", "europepmc"],
  "search_terms": ["exercise", "depression", "randomized controlled trial"],
  "date_range": {
    "start": "2015-01-01",
    "end": "2024-12-31"
  },
  "peer_review_only": true
}
```

### Literature Search Results

| Metric | Expected | Actual | ✓/✗ | Notes |
|--------|----------|--------|-----|-------|
| **PubMed Results** | | | | |
| - Total studies found | ≥20 | | ☐ | |
| - Studies with abstracts | 100% | | ☐ | |
| - Studies with authors | 100% | | ☐ | |
| - Studies within date range | 100% | | ☐ | |
| - Response time | <30s | | ☐ | |
| **Europe PMC Results** | | | | |
| - Total studies found | ≥10 | | ☐ | |
| - Open access papers | ≥50% | | ☐ | |
| - Response time | <30s | | ☐ | |
| **Combined Results** | | | | |
| - Total results (before dedup) | ≥30 | | ☐ | |
| - Unique results (after dedup) | ≥25 | | ☐ | |
| - Duplicates removed | 3-10 | | ☐ | |
| - Deduplication accuracy | 100% | | ☐ | |

**Sample Study Verification (Spot Check 5 Random Studies):**

| Study # | PMID/ID | Title Contains "Exercise" or "Depression" | Date in Range | Has Abstract | ✓/✗ |
|---------|---------|-------------------------------------------|---------------|--------------|-----|
| 1 | | ☐ | ☐ | ☐ | ☐ |
| 2 | | ☐ | ☐ | ☐ | ☐ |
| 3 | | ☐ | ☐ | ☐ | ☐ |
| 4 | | ☐ | ☐ | ☐ | ☐ |
| 5 | | ☐ | ☐ | ☐ | ☐ |

### Screening Results

| Metric | Expected | Actual | ✓/✗ | Notes |
|--------|----------|--------|-----|-------|
| **AI Agent Decisions** | | | | |
| - Studies screened | All found studies | | ☐ | |
| - Studies included | 10-15 (40-60%) | | ☐ | |
| - Studies excluded | 10-15 (40-60%) | | ☐ | |
| - Studies uncertain | 0-5 (0-20%) | | ☐ | |
| - Screening time | <5 min total | | ☐ | |
| **Exclusion Reasons** | | | | |
| - Wrong population | 2-5 studies | | ☐ | |
| - Wrong intervention | 2-5 studies | | ☐ | |
| - Wrong outcome | 1-3 studies | | ☐ | |
| - Not RCT | 1-3 studies | | ☐ | |
| **Agreement with Expert** | | | | |
| - Inclusion decisions match | ≥80% | | ☐ | |
| - Exclusion decisions match | ≥80% | | ☐ | |

**AI Decision Validation (Check 10 Random Decisions):**

| Study | AI Decision | Manual Review | Agreement? | Notes |
|-------|-------------|---------------|------------|-------|
| 1 | | | ☐ | |
| 2 | | | ☐ | |
| 3 | | | ☐ | |
| 4 | | | ☐ | |
| 5 | | | ☐ | |
| 6 | | | ☐ | |
| 7 | | | ☐ | |
| 8 | | | ☐ | |
| 9 | | | ☐ | |
| 10 | | | ☐ | |

**Agreement Rate:** ___/10 = ____%

### Quality Assessment Results

| Metric | Expected | Actual | ✓/✗ | Notes |
|--------|----------|--------|-----|-------|
| **Risk of Bias Assessment** | | | | |
| - Studies assessed | All included | | ☐ | |
| - Low risk studies | 50-70% | | ☐ | |
| - Some concerns | 20-40% | | ☐ | |
| - High risk | 5-15% | | ☐ | |
| **Bias Domains** | | | | |
| - Randomization assessed | 100% | | ☐ | |
| - Blinding assessed | 100% | | ☐ | |
| - Attrition assessed | 100% | | ☐ | |
| - Reporting assessed | 100% | | ☐ | |

### Data Extraction Results

| Metric | Expected | Actual | ✓/✗ | Notes |
|--------|----------|--------|-----|-------|
| **Extracted Data Completeness** | | | | |
| - Sample sizes extracted | 100% | | ☐ | |
| - Means extracted | 100% | | ☐ | |
| - Standard deviations extracted | 100% | | ☐ | |
| - Outcome measures documented | 100% | | ☐ | |
| - Intervention details recorded | 100% | | ☐ | |
| **Data Quality** | | | | |
| - No missing critical data | 100% | | ☐ | |
| - All values reasonable | 100% | | ☐ | |
| - Units consistent | 100% | | ☐ | |

### Statistical Analysis Results

| Metric | Expected | Actual | ✓/✗ | Variance | Notes |
|--------|----------|--------|-----|----------|-------|
| **Effect Sizes (Per Study)** | | | | | |
| - Cohen's d range | -1.5 to -0.3 | | ☐ | | |
| - Standard errors | 0.1 to 0.3 | | ☐ | | |
| - Confidence intervals | All cross zero or favor treatment | | ☐ | | |
| **Meta-Analysis Results** | | | | | |
| - Pooled effect (Cohen's d) | -0.4 to -0.8 | | ☐ | | |
| - 95% CI lower bound | -1.0 to -0.5 | | ☐ | | |
| - 95% CI upper bound | -0.2 to -0.6 | | ☐ | | |
| - Z-value | 5 to 10 | | ☐ | | |
| - P-value | <0.001 | | ☐ | | |
| - Model used | Random-effects (DL) | | ☐ | | |
| **Heterogeneity** | | | | | |
| - Q statistic | 10-30 | | ☐ | | |
| - Degrees of freedom | n_studies - 1 | | ☐ | | |
| - Q p-value | 0.05-0.5 | | ☐ | | |
| - I² | 0-50% (low to moderate) | | ☐ | | |
| - Tau² | 0-0.1 | | ☐ | | |
| - Interpretation | "Low to moderate heterogeneity" | | ☐ | | |
| **Publication Bias** | | | | | |
| - Egger's intercept | -2 to 2 | | ☐ | | |
| - Egger's p-value | >0.05 (not significant) | | ☐ | | |
| - Interpretation | "No significant asymmetry" | | ☐ | | |

**Statistical Validation Against R metafor:**

| Calculation | Platform Result | R metafor Result | Difference | Within Tolerance? | ✓/✗ |
|-------------|-----------------|------------------|------------|-------------------|-----|
| Pooled Effect | | | | ±1% | ☐ |
| Standard Error | | | | ±1% | ☐ |
| CI Lower | | | | ±1% | ☐ |
| CI Upper | | | | ±1% | ☐ |
| I² | | | | ±5 percentage points | ☐ |
| Tau² | | | | ±10% | ☐ |
| Q Statistic | | | | ±5% | ☐ |

**R Validation Code:**
```R
library(metafor)

# Input data from platform
yi <- c(___) # effect sizes
sei <- c(___) # standard errors

# Random-effects meta-analysis
res <- rma(yi, sei, method="DL")
summary(res)

# Expected output:
# [Paste R output here]
```

### Forest Plot Quality

| Element | Expected | Actual | ✓/✗ | Notes |
|---------|----------|--------|-----|-------|
| **Visual Elements** | | | | |
| - All studies displayed | Yes | | ☐ | |
| - Study names readable | Yes | | ☐ | |
| - Effect sizes with CIs shown | Yes | | ☐ | |
| - Pooled effect (diamond) | Yes | | ☐ | |
| - Weights displayed | Yes (as %) | | ☐ | |
| - Zero line visible | Yes | | ☐ | |
| **Statistical Information** | | | | |
| - I² displayed | Yes | | ☐ | |
| - Heterogeneity stats | Yes | | ☐ | |
| - P-value for pooled effect | Yes | | ☐ | |
| **Quality** | | | | |
| - Resolution | ≥300 DPI | | ☐ | |
| - Text readable | Yes | | ☐ | |
| - Color scheme professional | Yes | | ☐ | |
| - Publication ready | Yes | | ☐ | |

### Funnel Plot Quality

| Element | Expected | Actual | ✓/✗ | Notes |
|---------|----------|--------|-----|-------|
| - All studies plotted | Yes | | ☐ | |
| - X-axis: Effect size | Yes | | ☐ | |
| - Y-axis: Standard error (inverted) | Yes | | ☐ | |
| - Pooled effect line | Yes | | ☐ | |
| - 95% CI funnel | Yes | | ☐ | |
| - Symmetry visible | Visual inspection | | ☐ | |
| - Asymmetry if present | Matches Egger's test | | ☐ | |

### Report Generation

| Section | Expected | Actual | ✓/✗ | Notes |
|---------|----------|--------|-----|-------|
| **Report Structure** | | | | |
| - Title page | Present | | ☐ | |
| - Abstract | Present (structured) | | ☐ | |
| - Introduction | Present | | ☐ | |
| - Methods | Present (detailed) | | ☐ | |
| - Results | Present | | ☐ | |
| - Discussion | Present | | ☐ | |
| - References | Present (APA 7) | | ☐ | |
| - Appendices | Present | | ☐ | |
| **PRISMA Compliance** | | | | |
| - Flow diagram | Complete | | ☐ | |
| - All numbers consistent | Yes | | ☐ | |
| - Exclusion reasons documented | Yes | | ☐ | |
| - Search strategy documented | Yes | | ☐ | |
| **Formatting** | | | | |
| - APA 7th edition | Correct | | ☐ | |
| - Figures numbered | Correct | | ☐ | |
| - Tables formatted | Professional | | ☐ | |
| - Citations formatted | APA style | | ☐ | |
| - Page length | 15-25 pages | | ☐ | |

### Export Quality

| Format | Expected | Actual | ✓/✗ | Issues |
|--------|----------|--------|-----|--------|
| **CSV Export** | | | | |
| - File downloads | Yes | | ☐ | |
| - Opens in Excel | Yes | | ☐ | |
| - All data present | Yes | | ☐ | |
| - No missing values | Yes | | ☐ | |
| - UTF-8 encoding | Yes | | ☐ | |
| - File size | <500 KB | | ☐ | |
| **Excel Export** | | | | |
| - Multiple sheets | 5 sheets | | ☐ | |
| - Sheet 1: Summary | Present | | ☐ | |
| - Sheet 2: Studies | Present | | ☐ | |
| - Sheet 3: Statistics | Present | | ☐ | |
| - Sheet 4: Quality | Present | | ☐ | |
| - Sheet 5: PRISMA | Present | | ☐ | |
| - Formatting intact | Yes | | ☐ | |
| - Formulas work (if any) | Yes | | ☐ | |
| - File size | <2 MB | | ☐ | |
| **JSON Export** | | | | |
| - Valid JSON | Yes | | ☐ | |
| - Complete data | Yes | | ☐ | |
| - Can re-import | Yes | | ☐ | |
| **PDF Report** | | | | |
| - High quality | Yes | | ☐ | |
| - Searchable text | Yes | | ☐ | |
| - Images embedded | Yes | | ☐ | |
| - File size | <5 MB | | ☐ | |
| **Forest Plot PNG** | | | | |
| - Resolution | ≥300 DPI | | ☐ | |
| - Transparent background | Optional | | ☐ | |
| - File size | <1 MB | | ☐ | |

---

## Research Question 2: Mindfulness and Anxiety

### Test Configuration

```json
{
  "research_question": "Does mindfulness reduce anxiety?",
  "topic": "Mindfulness for Anxiety Reduction",
  "databases": ["pubmed", "arxiv", "core"],
  "search_terms": ["mindfulness", "anxiety", "intervention"],
  "peer_review_only": false
}
```

### Key Metrics

| Metric | Expected | Actual | ✓/✗ | Notes |
|--------|----------|--------|-----|-------|
| **Search Results** | | | | |
| - Total unique studies | ≥15 | | ☐ | |
| - PubMed results | ≥8 | | ☐ | |
| - arXiv preprints | ≥3 | | ☐ | |
| - CORE results | ≥5 | | ☐ | |
| - Preprints flagged | Yes | | ☐ | |
| - Search time | <60s | | ☐ | |
| **Screening** | | | | |
| - Studies included | 8-12 | | ☐ | |
| - Preprints included | ≥1 | | ☐ | |
| **Meta-Analysis** | | | | |
| - Pooled effect (Cohen's d) | -0.3 to -0.7 | | ☐ | |
| - 95% CI | Favors mindfulness | | ☐ | |
| - I² | 0-60% | | ☐ | |
| - P-value | <0.05 | | ☐ | |
| **Unique Features** | | | | |
| - Preprint handling correct | Yes | | ☐ | |
| - Different from RQ1 results | Yes | | ☐ | |
| - arXiv integration works | Yes | | ☐ | |

---

## Research Question 3: Diet and Cardiovascular Disease

### Test Configuration

```json
{
  "research_question": "Impact of diet on cardiovascular disease",
  "topic": "Dietary Interventions for CVD Prevention",
  "databases": ["pubmed", "europepmc", "core"],
  "search_terms": ["diet", "cardiovascular disease", "prevention"],
  "peer_review_only": true
}
```

### Key Metrics

| Metric | Expected | Actual | ✓/✗ | Notes |
|--------|----------|--------|-----|-------|
| **Search Results** | | | | |
| - Total unique studies | ≥30 | | ☐ | |
| - Large result set handled | Yes | | ☐ | |
| - Search time | <90s | | ☐ | |
| **Screening** | | | | |
| - Studies included | 15-25 | | ☐ | |
| - Performance (studies/sec) | ≥0.5 | | ☐ | |
| **Meta-Analysis** | | | | |
| - Effect type | Risk Ratio or OR | | ☐ | |
| - Pooled RR/OR | 0.6-0.9 | | ☐ | |
| - I² | Likely >50% | | ☐ | |
| - High heterogeneity flagged | Yes | | ☐ | |
| **Unique Features** | | | | |
| - Binary outcomes handled | Yes | | ☐ | |
| - Large dataset performance | Good | | ☐ | |
| - Subgroup analysis offered | Yes | | ☐ | |

---

## Performance Benchmarks

| Operation | Target | Actual | ✓/✗ | Notes |
|-----------|--------|--------|-----|-------|
| **Search Performance** | | | | |
| - PubMed search (50 results) | <30s | | ☐ | |
| - arXiv search (30 results) | <25s | | ☐ | |
| - Europe PMC search (50 results) | <35s | | ☐ | |
| - CORE search (40 results) | <40s | | ☐ | |
| - 4 databases parallel | <60s | | ☐ | |
| **Workflow Performance** | | | | |
| - Project creation | <2s | | ☐ | |
| - Screening 50 studies | <5min | | ☐ | |
| - Meta-analysis (15 studies) | <15s | | ☐ | |
| - Meta-analysis (50 studies) | <45s | | ☐ | |
| - Report generation | <120s | | ☐ | |
| **Export Performance** | | | | |
| - CSV export | <5s | | ☐ | |
| - Excel export | <10s | | ☐ | |
| - JSON export | <5s | | ☐ | |
| - PDF report | <30s | | ☐ | |
| - Forest plot PNG | <10s | | ☐ | |

---

## Security Test Results

| Test | Expected | Actual | ✓/✗ | Details |
|------|----------|--------|-----|---------|
| **SQL Injection** | | | | |
| - Payload 1: ' OR '1'='1 | Blocked/Escaped | | ☐ | |
| - Payload 2: '; DROP TABLE | Blocked/Escaped | | ☐ | |
| - Payload 3: admin'-- | Blocked/Escaped | | ☐ | |
| **XSS Prevention** | | | | |
| - Payload 1: <script>alert('XSS')</script> | Escaped | | ☐ | |
| - Payload 2: <img src=x onerror=alert()> | Escaped | | ☐ | |
| **Authentication** | | | | |
| - No token → 401 | Yes | | ☐ | |
| - Expired token → 401 | Yes | | ☐ | |
| - Invalid token → 401 | Yes | | ☐ | |
| - Modified JWT → 401 | Yes | | ☐ | |
| **Password Security** | | | | |
| - Passwords hashed (bcrypt) | Yes | | ☐ | |
| - Passwords not in logs | Yes | | ☐ | |
| - Min 8 characters enforced | Yes | | ☐ | |
| - Complexity requirements | Yes | | ☐ | |

---

## Bug Summary

### Critical Bugs (P1)
| Bug ID | Description | Impact | Status |
|--------|-------------|--------|--------|
| | | | |

### High Priority Bugs (P2)
| Bug ID | Description | Impact | Status |
|--------|-------------|--------|--------|
| | | | |

### Medium Priority Bugs (P3)
| Bug ID | Description | Impact | Status |
|--------|-------------|--------|--------|
| | | | |

### Low Priority Bugs (P4)
| Bug ID | Description | Impact | Status |
|--------|-------------|--------|--------|
| | | | |

---

## Overall Assessment

### Score Card

| Category | Tests | Passed | Failed | Pass Rate | Status |
|----------|-------|--------|--------|-----------|--------|
| Authentication | | | | % | ☐ |
| Literature Search | | | | % | ☐ |
| Screening | | | | % | ☐ |
| Statistical Analysis | | | | % | ☐ |
| Data Export | | | | % | ☐ |
| Performance | | | | % | ☐ |
| Security | | | | % | ☐ |
| **TOTAL** | | | | % | ☐ |

### Production Readiness Decision

**Overall Status:** ☐ GO | ☐ GO WITH CAUTIONS | ☐ NO-GO

**Rationale:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

**Critical Issues That Must Be Fixed:**
1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

**Recommended Next Steps:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

### Sign-Off

**QA Engineer:** _______________________ **Date:** _____________

**Tech Lead:** _______________________ **Date:** _____________

**Product Manager:** _______________________ **Date:** _____________

---

**END OF TEST RESULTS**

**Test Session:** TEST-________
**Completed:** ______________
**Total Duration:** ________ hours
