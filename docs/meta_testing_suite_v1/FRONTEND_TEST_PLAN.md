# Frontend Test Plan – Integrity & UX

This document defines how to test the **React frontend** against all 4 phases of the integrity work.

## 1. Purpose

Ensure that for all user-visible workflows:

- The UI **never lies** about what the backend actually did.
- All integrity guardrails are **visible and understandable** to the user.
- Edge cases (zero studies, high heterogeneity, abstract-only, etc.) are surfaced with clear messaging.
- The user always sees:
  - What was analyzed
  - What was **not** analyzed (and why)
  - How certain the system is

---

## 2. System Prompt for a “Frontend QA Agent”

You can paste this into Claude as a system message for a QA/testing agent:

```text
You are FRONTEND-QA-AGENT for a meta-analysis research platform.

Your mission:
- Drive the web UI like a real researcher.
- Confirm that **all integrity guardrails implemented in the backend are accurately surfaced in the frontend**.
- You must NEVER assume the system did an analysis unless the UI explicitly shows it.

When you test:
1. For each scenario, document:
   - Steps you took in the UI
   - What the UI displayed
   - Whether messages were clear and non-misleading
2. Compare the UI behavior with the expected outcomes defined in the test plan.
3. If anything is ambiguous, misleading, or missing, flag it as **FAIL** and propose specific copy / UX fixes.
4. Do NOT invent data or assume results – your job is to verify visibility of real system behavior, not to fabricate outcomes.
```

---

## 3. Core Scenarios (All Must Pass)

Each scenario should be run **after** the backend integrity guardrails are confirmed to be active.

### Scenario F1 – Zero Studies Found

**Goal:** When no eligible studies are found, UI must clearly state this and avoid fake results.

- **Steps**
  1. Run a search with extremely narrow criteria so that the backend returns `NO_STUDIES_FOUND`.
  2. Wait for the workflow to complete.
- **Expected UI behavior**
  - No forest plot or summary effect is shown.
  - Prominent message:  
    “No studies were found matching your criteria. Try broadening your inclusion criteria or search terms.”
  - Suggestions / next steps visible.
- **Fail conditions**
  - Any “summary effect” or “meta-analysis results” are shown.
  - Vague messaging like “error” or “something went wrong” with no explanation.

### Scenario F2 – Single Study Only

**Goal:** Validate UI behavior when only 1 study is found and pooling is blocked.

- **Steps**
  1. Use criteria that return exactly 1 eligible study.
- **Expected UI behavior**
  - Clear banner: “Meta-analysis requires at least 2 studies for pooling. Only 1 study was found.”
  - The single study can be shown with its data, but **no pooled estimate**.
- **Fail conditions**
  - Any chart, number, or wording suggesting a pooled meta-analysis was performed.

### Scenario F3 – 2 Studies, Below Minimum

**Goal:** Verify that “minimum studies for reliable meta-analysis” is surfaced.

- **Steps**
  1. Use criteria that return 2 studies.
- **Expected UI behavior**
  - Message: “Only 2 studies were found. A minimum of 3 studies is recommended for reliable meta-analysis. Results with fewer studies are highly uncertain.”
  - Either:  
    - No pooled estimate, OR
    - If the backend is ever configured to allow pooling here, the UI must mark the result as **preliminary / low confidence**.
- **Fail conditions**
  - UI presents result as “strong” or “robust” without an uncertainty warning.

### Scenario F4 – High Heterogeneity (I² > 75%)

**Goal:** Ensure “apples vs oranges” blocking is fully visible.

- **Steps**
  1. Trigger a benchmark job with high heterogeneity (use one of the benchmark configs from `BACKEND_EXTERNAL_VALIDITY_TESTS.md` that is known to produce I² > 75%).
- **Expected UI behavior**
  - No pooled summary effect.
  - Clear explanation: “Studies are too heterogeneous to pool (I² > 75%). We refused to compute a pooled effect size.”
  - Recommendations section visible (subgroup analysis, narrative synthesis, etc.).
- **Fail conditions**
  - Any pooled effect value is shown.
  - UI silently shows “0” or “N/A” without explanation.

### Scenario F5 – Abstract-Only Credibility Assessment

**Goal:** Show the difference between full-text & abstract-only assessments.

- **Steps**
  1. Run a meta-analysis where at least one study lacks full text (abstract-only mode).
- **Expected UI behavior**
  - For that study, a badge like “Abstract-only assessment” or similar.
  - The credibility panel includes a warning: assessment is limited; maximum credibility level is capped.
- **Fail conditions**
  - Abstract-only studies appear indistinguishable from full-text assessed studies.

### Scenario F6 – QA Agent with Missing Context

**Goal:** Confirm that QA refuses to hallucinate answers.

- **Steps**
  1. Ask a QA question **before** the analysis finishes or for a failed run.
- **Expected UI behavior**
  - Message like:  
    “I don’t have enough information to answer this question yet. Please wait for the meta-analysis to complete.”
- **Fail conditions**
  - Any specific answer about effect sizes, p-values, or conclusions is generated.

---

## 4. Visual & UX Requirements

For every error / guardrail state:

- Message must be:
  - Specific (“high heterogeneity”) not vague (“error”).
  - Linked to next steps (“broaden your criteria”, “review outliers”, etc.).
- The UI should avoid:
  - Red error screens with no guidance.
  - Tiny, easy-to-miss banners.

You can add these as acceptance criteria in your design system or Storybook stories.

---

## 5. Regression Checklist

Before any release:

- [ ] Run F1–F6.
- [ ] Confirm copy hasn’t regressed.
- [ ] Confirm colors / states for warnings vs hard blocks are consistent.
- [ ] Confirm QA widget never answers while core context is missing.
