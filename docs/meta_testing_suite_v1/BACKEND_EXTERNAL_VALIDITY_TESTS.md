# Backend External Validity Test Suite

This document defines how to prove that the system performs correctly on **real-world data**, not just synthetic or self-generated examples.

The idea:  
1. Use **published meta-analyses** as benchmarks.  
2. Recreate them as closely as possible with our system.  
3. Compare our outputs (effect size, direction, significance, heterogeneity) to the published results.

---

## 1. Principles

- **No fake data.** All benchmark datasets must be derived from real published studies.
- **Transparent deviations.** If we simplify anything (e.g., only re-use main outcome), that simplification must be documented.
- **Separate internal vs external validity.**
  - Internal = “Does the code compute what we think it computes?” (unit tests, already covered).
  - External = “Do we get reasonable answers on real problems?” (this document).

---

## 2. Benchmark Meta-Analysis Categories

Define at least **5 benchmark sets**, each with:

- A real published meta-analysis (with DOI).
- A machine-readable dataset (CSV / JSON) in your repo.
- Expected ranges for:
  - Effect size (e.g., Cohen’s d, log OR, RR)
  - Confidence interval
  - Heterogeneity (I²)
  - Direction (positive/negative, favors treatment/control)

Example benchmark categories (you can customize DOIs later):

1. **Cardiovascular – Drug vs Placebo**  
   - Outcome: mortality, MI, or BP reduction.
2. **Oncology – Adjuvant Therapy**  
   - Outcome: survival or recurrence.
3. **Psychology – CBT vs Control**  
   - Outcome: depression/anxiety symptom scales.
4. **Public Health – Smoking Cessation**  
   - Outcome: quit rates at follow-up.
5. **Neurology / Cognitive – Intervention vs Control**  
   - Outcome: cognitive test scores or dementia incidence.

Each benchmark set gets a config file, e.g.:

```jsonc
// backend/tests/benchmarks/cardio_bp_reduction.json
{
  "id": "cardio_bp_reduction_v1",
  "category": "cardiovascular",
  "reference_paper": {
    "title": "Example BP Drug Meta-analysis",
    "doi": "10.XXXX/XXXXX",
    "expected_effect_model": "random",
    "expected_effect_type": "mean_difference",
    "expected_effect_point": -5.0,
    "expected_effect_ci": [-7.0, -3.0],
    "expected_i2_range": [20.0, 60.0]
  },
  "studies": [
    {
      "id": "study_1",
      "label": "Trial A 2009",
      "n_treatment": 120,
      "n_control": 118,
      "mean_treatment": 130.5,
      "sd_treatment": 15.2,
      "mean_control": 135.8,
      "sd_control": 14.9
    }
    // etc.
  ]
}
```

---

## 3. System Prompt for a “Benchmark Runner Agent”

This is a system prompt you can give to Claude to orchestrate external validity tests:

```text
You are BENCHMARK-RUNNER-AGENT for a meta-analysis platform.

Your mission:
- Load real-world benchmark datasets defined in JSON/CSV files.
- Run the platform's full pipeline on each benchmark:
  - Data ingestion
  - Effect size calculation
  - Heterogeneity estimation
  - Meta-analysis (fixed/random)
  - Outlier analysis
  - Credibility and GRADE-like assessments
- Compare outputs to the benchmark's reference values and assert whether they fall within the expected ranges.

For each benchmark:
1. Log the benchmark ID and reference paper.
2. Run the analysis through the REAL production endpoints (not a mocked system).
3. Capture system outputs:
   - Pooled effect size and CI
   - I² and heterogeneity statistics
   - Number of included studies
4. Compare to expectations:
   - Is the direction of effect the same?
   - Is the point estimate within a reasonable tolerance (e.g., ±0.1 for SMD, or ±10–15% of RR/OR)?
   - Is I² in the expected range?
5. Mark the benchmark as PASS or FAIL based on defined criteria.
6. Output a structured JSON report for each benchmark.
```

---

## 4. Pass / Fail Criteria

For each benchmark:

- **Direction match (REQUIRED)**
  - Our effect must favor the same side (treatment or control) as the reference.
- **Magnitude tolerance**
  - Let E_ref be reference effect; E_sys our effect.
  - PASS if:
    - |E_sys − E_ref| ≤ 0.1 for standardized effects (Cohen’s d, Hedges g), OR
    - E_sys within ±15% of E_ref for OR/RR/HR.
- **Confidence interval overlap**
  - Our 95% CI should overlap with the reference CI.
- **Heterogeneity**
  - Our I² ∈ [expected_min, expected_max] range OR at least qualitatively similar (low vs moderate vs high).

If ANY of the following happens, mark as **FAIL**:

- Direction of effect flips.
- Point estimate is far outside tolerance.
- Our system pools when the benchmark paper explicitly warns against pooling due to extreme heterogeneity.

---

## 5. Integration with CI

Once benchmarks are implemented:

- Add a **nightly job** (not every push, to avoid long runs) that:
  - Runs all benchmark configs with a “headless” backend mode.
  - Saves a JSON report to `backend/tests/benchmarks/reports/REPORT_YYYYMMDD.json`.
  - Fails the job if any benchmark fails.

This ensures that future refactors don’t quietly break external validity.

---

## 6. Extensibility

Future additions:

- Add **topic coverage stats** (how many domains: cardio, psych, oncology, etc.).
- Add **sensitivity benchmarks** – remove outliers and confirm system’s sensitivity analysis matches reference patterns.
- Add **subgroup benchmarks** – e.g., age, sex, dosage subgroups.

All of these can be orchestrated using the same Benchmark Runner Agent prompt.
