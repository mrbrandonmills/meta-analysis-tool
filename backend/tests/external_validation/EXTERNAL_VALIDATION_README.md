# External Validation System - Implementation Summary

## Overview

This directory contains a complete external validation system for the Meta-Analysis Platform, designed to verify:
1. **Numeric consistency** of meta-analysis outputs
2. **LLM-based validation** of methodology and reporting quality
3. **End-to-end integration** via frontend E2E tests

## Current Status

### ✅ Implemented

1. **Validation Scripts** (Python)
   - `numeric_validator.py` - Validates numeric consistency of reports
   - `llm_validation.py` - Generates prompts for external LLM review
   - `full_validation_summary.py` - Rolls up all validation results
   - `convert_benchmark_reports.py` - Converts benchmark outputs to expected format

2. **Frontend E2E Test Scaffold** (TypeScript/Playwright)
   - `frontend/tests/e2e/meta_frontend_e2e.spec.ts` - 10 test scenarios
   - Designed to run full UI flows and capture JSON + MD reports

3. **Benchmark Testing Infrastructure**
   - 5 benchmark datasets covering:
     - Psychology (Omega-3 depression)
     - Cardiovascular (BP reduction)
     - Oncology (adjuvant therapy)
     - Public Health (smoking cessation)
     - Neurology (cognitive training)
   - Benchmark runner with pass/fail validation
   - Automated report generation

### ⏳ Requires Frontend Integration

The E2E test suite requires the following UI elements with `data-testid` attributes:

```typescript
// Required UI elements:
- data-testid="research-question"      // Text input for research question
- data-testid="database-select"         // Multi-select for databases
- data-testid="min-studies"             // Number input for minimum studies
- data-testid="run-meta-analysis"       // Button to start analysis
- data-testid="results-summary"         // Container showing results
- data-testid="download-json"           // Button to download JSON report
- data-testid="download-markdown"       // Button to download MD report
```

## Directory Structure

```
meta-analysis-tool/
  backend/
    tests/
      benchmarks/
        datasets/                       # 5 benchmark datasets
        reports/                        # Generated reports (JSON + MD)
          cardio_bp_reduction_v1.json
          neuro_cognition_v1.json
          omega3_depression_v1.json
          oncology_adjuvant_v1.json
          smoking_cessation_v1.json
          REPORT_*.json                 # Benchmark rollup reports
        run_benchmarks.py               # Benchmark runner
      external_validation/
        numeric_validator.py            # ✅ Numeric consistency checks
        llm_validation.py               # ✅ LLM prompt generator
        full_validation_summary.py      # ✅ Rollup summary
        convert_benchmark_reports.py    # ✅ Format converter
        NUMERIC_VALIDATION_SUMMARY.json # Generated validation results
        LLM_VALIDATION_SUMMARY.json     # Generated LLM prompts
        FULL_VALIDATION_ROLLUP.json     # Final rollup
  frontend/
    tests/
      e2e/
        meta_frontend_e2e.spec.ts       # ✅ E2E test scaffold (needs UI)
```

## Usage

### 1. Run Backend Benchmark Tests

```bash
cd backend
python3 tests/benchmarks/run_benchmarks.py
```

This generates benchmark reports in `tests/benchmarks/reports/`.

### 2. Convert Benchmark Reports

```bash
cd backend
python3 tests/external_validation/convert_benchmark_reports.py
```

This converts rollup reports to individual scenario reports with the expected format.

### 3. Run Numeric Validation

```bash
cd backend
python3 tests/external_validation/numeric_validator.py
```

Output: `tests/external_validation/NUMERIC_VALIDATION_SUMMARY.json`

**Current Results:**
- Total reports: 8 (5 benchmark + 3 rollup)
- Passed: 5 (all benchmark reports)
- Failed: 3 (rollup reports - expected, different format)

### 4. Generate LLM Validation Prompts

```bash
cd backend
python3 tests/external_validation/llm_validation.py
```

Output: `tests/external_validation/LLM_VALIDATION_SUMMARY.json`

**Note:** Requires Markdown reports. Currently no `.md` files exist (requires frontend E2E tests).

### 5. Create Full Validation Rollup

```bash
cd backend
python3 tests/external_validation/full_validation_summary.py
```

Output: `tests/external_validation/FULL_VALIDATION_ROLLUP.json`

### 6. Run Frontend E2E Tests (Requires UI Integration)

```bash
cd frontend
npm install
npx playwright install
npx playwright test tests/e2e/meta_frontend_e2e.spec.ts
```

**Prerequisites:**
- Backend API running on `http://localhost:8000`
- Frontend dev server on `http://localhost:3000`
- UI elements with required `data-testid` attributes
- Download functionality for JSON and MD reports

## Validation Checks

### Numeric Validator

Checks each report for:

1. **Status Consistency**
   - If `status` indicates insufficient evidence → no pooled effect size
   - If `status` indicates pooling → effect size, CI, p-value must be present

2. **Effect Size Reporting**
   - `meta_analysis.effect_size` present
   - `meta_analysis.ci_lower` and `ci_upper` present
   - `meta_analysis.p_value` present

3. **Heterogeneity Consistency**
   - `heterogeneity.i_squared` within [0, 100]
   - `heterogeneity.interpretation` aligned with numeric value:
     - "low" → I² < 50%
     - "moderate" → I² 50-75%
     - "high/very high" → I² > 50%

### LLM Validator

Generates prompts for external review by:
- **Claude**: Focus on methodological coherence, PRISMA compliance, credibility score
- **Gemini**: Focus on statistical soundness, clarity, transparency

## Report Format

### Expected Format for Individual Reports

```json
{
  "benchmark_id": "omega3_depression_v1",
  "timestamp": "2025-11-25T21:37:35.853813",
  "status": "success",
  "meta_analysis": {
    "effect_size": -0.288,
    "ci_lower": -0.386,
    "ci_upper": -0.178,
    "p_value": 0.002,
    "model": "random"
  },
  "heterogeneity": {
    "i_squared": 47.8,
    "interpretation": "low"
  },
  "n_studies": 11,
  "reference": { ... }
}
```

## Integration Steps for Full E2E Testing

### Step 1: Frontend UI Elements

Add `data-testid` attributes to the following components:

```tsx
// Research question input
<input data-testid="research-question" ... />

// Database multi-select
<select data-testid="database-select" multiple ... />

// Min studies input
<input data-testid="min-studies" type="number" ... />

// Run button
<button data-testid="run-meta-analysis" ... />

// Results container
<div data-testid="results-summary" ... />

// Download buttons
<button data-testid="download-json" ... />
<button data-testid="download-markdown" ... />
```

### Step 2: Implement Download Functionality

Both JSON and Markdown reports should be downloadable via UI buttons. The downloads should save to `backend/tests/benchmarks/reports/` or be captured by Playwright.

### Step 3: Start Services

```bash
# Terminal 1: Backend
cd backend
source .venv/bin/activate  # or create venv if needed
uvicorn app.main:app --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev -- --port 3000

# Terminal 3: Run E2E tests
cd frontend
npx playwright test tests/e2e/meta_frontend_e2e.spec.ts
```

### Step 4: Run Full Validation Pipeline

After E2E tests complete:

```bash
cd backend
python3 tests/external_validation/numeric_validator.py
python3 tests/external_validation/llm_validation.py
python3 tests/external_validation/full_validation_summary.py
```

## Expected Outcomes

### Successful Validation

When all components are integrated:

1. **10 E2E test scenarios complete**
   - 10 JSON reports in `benchmarks/reports/`
   - 10 MD reports in `benchmarks/reports/`

2. **Numeric Validation passes**
   - All reports have consistent status, effect sizes, CIs, p-values
   - I² values aligned with interpretations

3. **LLM prompts generated**
   - Claude prompts for all 10 MD reports
   - Gemini prompts for all 10 MD reports

4. **Rollup status: `READY_FOR_EXTERNAL_LLM_REVIEW`**

## Current Validation Results

```json
{
  "overall_status": "NUMERIC_ISSUES_DETECTED",
  "total_reports_numeric": 8,
  "total_reports_llm": 0,
  "numeric_all_ok": false,
  "details": {
    "numeric": {
      "num_ok": 5,
      "num_failed": 3
    }
  }
}
```

**Interpretation:**
- 5 benchmark reports passed all numeric checks ✅
- 3 rollup reports failed (expected - different format)
- 0 LLM prompts generated (no MD files yet)

## Next Steps

1. **Add `data-testid` attributes to frontend UI** components
2. **Implement JSON/MD download functionality** in frontend
3. **Configure Playwright** with proper browser installation
4. **Run full E2E test suite** (10 scenarios)
5. **Execute validation pipeline** on generated reports
6. **Manual LLM review** using generated prompts

## Troubleshooting

### E2E Tests Fail with "Element not found"

**Cause:** Missing `data-testid` attributes in UI components.

**Fix:** Add attributes as specified in "Integration Steps" above.

### No Markdown Reports Generated

**Cause:** Download functionality not implemented or MD export not available.

**Fix:** Implement MD report generation and download in frontend.

### Numeric Validation Failures

**Cause:** Report format doesn't match expected schema.

**Fix:** Run `convert_benchmark_reports.py` or ensure frontend reports match expected format.

### LLM Validation Shows 0 Reports

**Cause:** No `.md` files in `benchmarks/reports/` directory.

**Fix:** Run E2E tests to generate MD reports, or manually create MD files.

## References

- BACKEND_EXTERNAL_VALIDITY_TESTS.md - External validity testing specification
- BENCHMARK_DATASET_STANDARDS.md - Benchmark dataset format and requirements
- TESTING_OVERVIEW.md - Four-pillar testing framework

## Contact

For questions or issues with the external validation system, refer to the Testing Architect documentation or the project's Testing Architect agent.
