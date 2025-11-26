# CI Pipeline – Integrity & External Validity

This document describes how to wire your **tests + benchmarks** into a CI pipeline (e.g., GitHub Actions, GitLab CI, etc.).

Goal:  
Every commit should protect:
- Internal integrity guardrails.
- Frontend behavior (via component / e2e tests).
- External validity (via nightly benchmarks).

---

## 1. Stages

Recommended stages:

1. **lint_and_typecheck**
2. **unit_tests_backend**
3. **integration_tests_backend**
4. **unit_tests_frontend**
5. **end_to_end_frontend** (optional or nightly)
6. **benchmarks_external_validity** (nightly)

---

## 2. Minimal GitHub Actions Skeleton

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          pip install -r requirements.txt
      - name: Run unit + integration tests
        run: |
          python -m pytest tests/unit tests/integration -v

  frontend-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install deps
        run: |
          npm ci
      - name: Run unit tests
        run: |
          npm test -- --watch=false
```

---

## 3. Nightly External Validity Job

```yaml
name: Nightly Benchmarks

on:
  schedule:
    - cron: '0 8 * * *'  # every day at 08:00 UTC

jobs:
  run-benchmarks:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          pip install -r requirements.txt
      - name: Run benchmark suite
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python -m tests.benchmarks.run_all_benchmarks             --config-dir tests/benchmarks/datasets             --report-dir tests/benchmarks/reports

```

The `run_all_benchmarks` entrypoint would:

1. Discover all `*.json` configs.
2. Run the full pipeline for each.
3. Compare outputs with expected ranges.
4. Exit with non-zero status if any FAIL.

---

## 4. Guardrail Expectations

- A PR cannot be merged into `main` unless:
  - Backend unit + integration tests pass.
  - Frontend unit tests pass.
- Nightly benchmark failures should:
  - **Not** block normal development immediately, but
  - Trigger alerts and be treated as high-priority issues.

---

## 5. For Claude / Agent Integration

You can give an agent the job of **maintaining CI health** using this prompt:

```text
You are CI-MAINTAINER-AGENT for a meta-analysis platform.

Your job:
- Monitor test results from the CI system.
- When a test fails, read the logs and summarize:
  - What failed
  - Why it failed
  - What code files are most likely involved
- Propose precise patch plans that preserve the integrity guardrails and external validity.

You must treat any regression in integrity or benchmarks as CRITICAL.
```

This turns the CI + test suite into an ongoing feedback loop rather than a one-off check.
