# Scientific Compliance Checklist

This document ensures that the platform’s outputs conform to **scientific and editorial standards**, not just “code that runs”.

Think: PRISMA, Cochrane-style clarity, honesty about uncertainty.

---

## 1. Reporting Structure

Every completed meta-analysis report should include:

- Research question (PICO-style where applicable).
- Search strategy summary (databases, date ranges, key terms).
- Study selection:
  - Number of records identified, screened, included, excluded.
  - Reasons for exclusion (high-level categories).
- Effect size and model:
  - Effect measure (e.g., SMD, RR, OR).
  - Model used (fixed vs random, with justification).
- Heterogeneity:
  - I², Q statistic, p-value.
  - Interpretation (low / moderate / high).
- Risk of Bias / credibility:
  - Per-study assessment.
  - Aggregated summary.
- Limitations:
  - Data limitations.
  - Methodological limitations.
  - Generalizability caveats.

---

## 2. Compliance Checklist

For each report, check:

- [ ] Research question clearly stated.
- [ ] PICO elements identifiable (if applicable).
- [ ] Databases and date ranges clearly listed.
- [ ] Total N of studies at each stage is consistent (matches PRISMA-like flow).
- [ ] Effect measure is appropriate for the outcome type.
- [ ] Model choice (fixed/random) is justified.
- [ ] I² reported and qualitatively interpreted.
- [ ] High heterogeneity → either:
  - [ ] Pooling refused with explanation, **or**
  - [ ] Pooling allowed only with **explicit** caution flags.
- [ ] Risk of Bias summary present, with clear limitations.
- [ ] Any abstract-only assessments are clearly labeled as such.
- [ ] Limitations section present and non-trivial (not just boilerplate).

---

## 3. System Prompt for a “Scientific Compliance Agent”

```text
You are SCIENTIFIC-COMPLIANCE-AGENT for a meta-analysis platform.

Your job:
- Review completed reports and check them against the Scientific Compliance Checklist.
- You must not re-run the analysis, but you should verify whether the report:
  - Honestly represents what was done.
  - Appropriately acknowledges limitations and uncertainty.
  - Follows good scientific reporting norms.

Output format:
- COMPLIANT or NON-COMPLIANT
- A list of failed checklist items, if any.
- Concrete suggestions for how to improve the report.

You must be strict but fair: never ask for perfection, but do not allow misleading or incomplete scientific reporting.
```

---

## 4. Minimum Bar for “Publication-Grade”

Mark a report “publication-grade” only if:

- All critical checklist items are met:
  - Clear research question.
  - Transparent inclusion/exclusion.
  - Correct effect measure + model + heterogeneity reporting.
  - Risk of bias considerations.
  - Limitations acknowledged.
- The integrity guardrails (min studies, heterogeneity, QA context) were respected.
- No hallucinated data or claims are detected.

This checklist can be integrated into both automated QA and human editorial review.
