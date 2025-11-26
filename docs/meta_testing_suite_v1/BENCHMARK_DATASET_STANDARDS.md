# Benchmark Dataset Standards

This document defines how to structure, store, and version the **real datasets** used for external validity testing.

---

## 1. Storage Layout

Recommended directory structure inside the repo:

```text
backend/
  tests/
    benchmarks/
      datasets/
        cardio_bp_reduction_v1.json
        oncology_survival_v1.json
        psych_cbt_depression_v1.json
        smoking_cessation_v1.json
        neuro_cognition_v1.json
      reports/
        REPORT_2025-11-26.json
      BENCHMARK_DATASET_STANDARDS.md
      BACKEND_EXTERNAL_VALIDITY_TESTS.md
```

---

## 2. Dataset Schema (JSON)

Every dataset file MUST include:

- **id** – unique string for the benchmark.
- **category** – domain (cardio, psych, etc.).
- **reference_paper** – citation + expected ranges.
- **studies** – list of per-study data points in a format compatible with your calculator.

Example schema (pseudo-JSON):

```jsonc
{
  "id": "psych_cbt_depression_v1",
  "category": "psychology",
  "reference_paper": {
    "title": "CBT vs Control for Major Depression: A Meta-analysis",
    "doi": "10.XXXX/XXXXX",
    "effect_type": "standardized_mean_difference",
    "expected_effect_model": "random",
    "expected_effect_point": -0.6,
    "expected_effect_ci": [-0.8, -0.4],
    "expected_i2_range": [40, 75]
  },
  "studies": [
    {
      "id": "smith_2010",
      "label": "Smith 2010",
      "n_treatment": 45,
      "n_control": 47,
      "mean_treatment": 15.2,
      "sd_treatment": 5.1,
      "mean_control": 20.8,
      "sd_control": 5.6
    }
  ]
}
```

---

## 3. Ground Truth & Annotation

For each dataset, include:

- **Ground truth file** (optional but recommended):  
  `cardio_bp_reduction_v1.truth.json` with:
  - The reference effect (from the paper).
  - Notes on any known simplifications (e.g., “we only used the primary endpoint”).
- **Assumptions**:
  - How multi-arm trials were handled.
  - How missing SDs were imputed (if at all).
  - Whether any outcomes were transformed (e.g., log-OR).

The Benchmark Runner Agent can use this to generate more detailed discrepancy reports.

---

## 4. Versioning

- Suffix datasets with `_v1`, `_v2`, etc.
- If you need to fix a data error, create a new version:
  - Old file: `psych_cbt_depression_v1.json` (kept for traceability).
  - New file: `psych_cbt_depression_v2.json` with a changelog section.

---

## 5. No Synthetic “Fake” Study Entries

- Each `study` in a benchmark dataset must correspond to a **real** trial from the reference paper or a clearly stated subset.
- If you must anonymize (e.g., for licensing reasons):
  - You may obfuscate author names or labels, **but not the numbers**.
  - Document that anonymization in the dataset metadata.

---

## 6. Quality Control Checklist

Before adding a dataset to `main`:

- [ ] All numeric values checked at least once against the reference paper.
- [ ] Reference effect & CI written down.
- [ ] I² or at least heterogeneity pattern documented.
- [ ] File validates against the expected JSON schema.
- [ ] CI benchmark tests for this dataset pass.
