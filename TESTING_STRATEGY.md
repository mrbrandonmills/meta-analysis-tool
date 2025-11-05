# Testing Strategy for Academic Research Platform
## Comprehensive Quality Assurance Framework

**Document Version:** 1.0
**Date:** November 4, 2025
**Status:** Living Document
**Critical Application:** Academic research depends on accuracy

---

## Executive Summary

This document outlines the comprehensive testing strategy for the 4-tool academic research platform. Given the critical nature of academic research, our testing approach prioritizes **accuracy**, **reproducibility**, and **statistical correctness** above all else.

**Key Principles:**
- Minimum 80% code coverage overall
- 100% coverage for critical paths (authentication, agent decisions, statistical calculations)
- All tests must be deterministic and reproducible
- Fast test suite execution (< 5 minutes for full run)
- Human expert validation for AI outputs
- Continuous validation against published research

---

## Table of Contents

1. [Testing Pyramid](#1-testing-pyramid)
2. [Testing Scope by Tool](#2-testing-scope-by-tool)
3. [Backend Testing Strategy](#3-backend-testing-strategy)
4. [Frontend Testing Strategy](#4-frontend-testing-strategy)
5. [Agent Validation Testing](#5-agent-validation-testing)
6. [Performance Testing](#6-performance-testing)
7. [Security Testing](#7-security-testing)
8. [CI/CD Integration](#8-cicd-integration)
9. [Test Data Management](#9-test-data-management)
10. [Quality Metrics](#10-quality-metrics)

---

## 1. Testing Pyramid

Our testing strategy follows the test pyramid model with emphasis on academic validation:

```
                    ┌─────────────────┐
                    │  E2E Tests (5%) │  <- User workflows
                    │   Playwright     │
                    └─────────────────┘
                  ┌───────────────────────┐
                  │ Integration (15%)     │  <- API + Database
                  │  pytest + httpx       │
                  └───────────────────────┘
              ┌────────────────────────────────┐
              │   Component Tests (25%)        │  <- React components
              │  React Testing Library         │
              └────────────────────────────────┘
          ┌──────────────────────────────────────────┐
          │        Unit Tests (40%)                  │  <- Functions, utils
          │     pytest + vitest                      │
          └──────────────────────────────────────────┘
    ┌──────────────────────────────────────────────────────┐
    │    Agent Validation Tests (15%)                      │  <- Academic accuracy
    │  Gold standard comparison, human expert validation   │
    └──────────────────────────────────────────────────────┘
```

### Coverage Goals

| Layer | Coverage Target | Priority | Speed |
|-------|----------------|----------|-------|
| Unit Tests | 85% | HIGH | < 30s |
| Component Tests | 80% | MEDIUM | < 45s |
| Integration Tests | 70% | HIGH | < 2m |
| E2E Tests | Critical paths only | MEDIUM | < 3m |
| Agent Validation | 100% of agents | CRITICAL | Variable |

### Critical Paths (100% Coverage Required)

1. **Authentication & Authorization**
   - User registration and login
   - JWT token generation and validation
   - Permission checks

2. **Agent Decision Making**
   - All agent.think() calls
   - Decision logging and audit trail
   - Confidence score calculation

3. **Statistical Calculations (Tool 1)**
   - Effect size calculations
   - Meta-analysis computations
   - Heterogeneity metrics (I², τ²)
   - Confidence intervals

4. **Data Integrity**
   - Database transactions
   - Data validation
   - Error handling

---

## 2. Testing Scope by Tool

### Tool 1: Meta-Analysis/Systematic Review Assistant

**Critical Areas:**
1. **Search Accuracy**
   - Query construction validation
   - Database API integration
   - Deduplication algorithm
   - Test: Compare with manual searches (>95% recall)

2. **Screening Reliability**
   - Inclusion/exclusion criteria application
   - Inter-rater reliability simulation
   - Test: Compare with human screeners (>90% agreement)

3. **Statistical Correctness**
   - Effect size extraction accuracy
   - Meta-analysis calculation validation
   - Forest plot generation
   - Test: Replicate 10 published meta-analyses (>95% match)

4. **PRISMA Compliance**
   - Flow diagram generation
   - Required section completeness
   - Test: PRISMA checklist validation (100% compliance)

**Validation Datasets:**
- 10 published meta-analyses with open data
- Cochrane systematic reviews
- JAMA/BMJ meta-analyses with replication data

### Tool 4: Expert Reviewer Matcher

**Critical Areas:**
1. **Expertise Matching**
   - Keyword extraction accuracy
   - Domain classification correctness
   - Test: Compare with editor selections (>80% overlap)

2. **Conflict of Interest Detection**
   - Co-authorship network accuracy
   - Institutional affiliation matching
   - Test: Known COI cases (100% detection)

3. **Match Ranking Algorithm**
   - Expertise score calculation
   - Availability prediction
   - Diversity optimization
   - Test: Editor satisfaction survey (>4.0/5)

**Validation Datasets:**
- 100 manuscript-reviewer pairs (editor verified)
- Known COI cases from retractions
- ORCID researcher profiles

### Tool 3: Peer Review Quality Assistant

**Critical Areas:**
1. **Review Quality**
   - Constructiveness of feedback
   - Technical accuracy
   - Completeness of coverage
   - Test: Expert comparison (top 50% quality)

2. **Bias Detection**
   - Biased language identification
   - Tone appropriateness
   - Test: Flagging rate on biased examples (>90%)

3. **Editor Synthesis**
   - Multi-review integration
   - Decision recommendation accuracy
   - Test: Agreement with actual decisions (>75%)

**Validation Datasets:**
- Anonymized peer reviews (with permission)
- Known biased review examples
- Editorial decision datasets

### Tool 2: Research Direction Generator

**Critical Areas:**
1. **Gap Identification**
   - Understudied area detection
   - Novel combination discovery
   - Test: Expert evaluation (>4.0/5 novelty)

2. **Impact Prediction**
   - Citation prediction accuracy
   - Feasibility assessment
   - Test: Track actual outcomes (≥ field average)

3. **Proposal Quality**
   - Completeness of sections
   - Methodological soundness
   - Test: Grant reviewer scores (>3.5/5)

**Validation Datasets:**
- Meta-analysis findings with known gaps
- Historical research trends
- Funded grant proposals

---

## 3. Backend Testing Strategy

### 3.1 Test Framework

**Primary Tools:**
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `httpx` - API client testing
- `faker` - Test data generation
- `factory-boy` - Model factories

### 3.2 Test Structure

```
backend/tests/
├── conftest.py                    # Pytest configuration & fixtures
├── pytest.ini                     # Pytest settings
├── .coveragerc                    # Coverage configuration
│
├── unit/                          # Unit tests (40% of tests)
│   ├── test_agents/
│   │   ├── test_base_agent.py
│   │   ├── test_coordinator.py
│   │   ├── test_search.py
│   │   ├── test_screening.py
│   │   ├── test_credibility.py
│   │   └── test_qa.py
│   ├── test_utils/
│   │   ├── test_pdf_parser.py
│   │   ├── test_stats_utils.py
│   │   └── test_network_utils.py
│   └── test_services/
│       ├── test_auth_service.py
│       └── test_search_service.py
│
├── integration/                   # Integration tests (15% of tests)
│   ├── test_api/
│   │   ├── test_meta_analysis_api.py
│   │   ├── test_reviewer_matcher_api.py
│   │   ├── test_peer_review_api.py
│   │   └── test_research_direction_api.py
│   ├── test_database/
│   │   ├── test_models.py
│   │   ├── test_relationships.py
│   │   └── test_transactions.py
│   └── test_workflows/
│       ├── test_orchestrator.py
│       └── test_multi_agent.py
│
├── validation/                    # Agent validation tests (15%)
│   ├── test_meta_analysis/
│   │   ├── test_statistical_accuracy.py
│   │   ├── test_prisma_compliance.py
│   │   └── test_replication_studies.py
│   ├── test_reviewer_matcher/
│   │   ├── test_match_quality.py
│   │   ├── test_coi_detection.py
│   │   └── test_diversity_optimization.py
│   ├── test_peer_review/
│   │   ├── test_review_quality.py
│   │   └── test_bias_detection.py
│   └── test_research_direction/
│       ├── test_gap_identification.py
│       └── test_novelty_scoring.py
│
├── performance/                   # Performance benchmarks
│   ├── test_api_performance.py
│   ├── test_agent_performance.py
│   └── test_database_performance.py
│
├── security/                      # Security tests
│   ├── test_authentication.py
│   ├── test_authorization.py
│   └── test_input_validation.py
│
└── fixtures/                      # Test data
    ├── papers/
    │   ├── sample_papers.json
    │   └── meta_analysis_datasets/
    ├── researchers/
    │   └── researcher_profiles.json
    ├── manuscripts/
    │   └── test_manuscripts.json
    └── mocks/
        ├── anthropic_responses.json
        └── database_responses.json
```

### 3.3 Key Test Fixtures

**Database Fixtures:**
```python
# conftest.py

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    engine = create_engine("postgresql://localhost/test_db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(db_engine):
    """Create clean database session for each test."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def test_user(db_session):
    """Create test user."""
    user = User(
        email="test@example.com",
        name="Test User",
        institution="Test University"
    )
    db_session.add(user)
    db_session.commit()
    return user
```

**Agent Fixtures:**
```python
@pytest.fixture
def mock_anthropic_client(monkeypatch):
    """Mock Anthropic API client."""
    class MockMessage:
        def __init__(self, text):
            self.content = [type('obj', (object,), {'text': text})]

    class MockClient:
        def __init__(self, api_key):
            pass

        def messages_create(self, **kwargs):
            # Return pre-defined responses based on prompt
            return MockMessage("Mock agent response")

    monkeypatch.setattr("anthropic.Anthropic", MockClient)

@pytest.fixture
def search_agent(mock_anthropic_client):
    """Create SearchAgent for testing."""
    from app.agents.specialized.search import SearchAgent
    config = AgentConfig(
        name="test_search",
        role=AgentRole.SEARCH
    )
    return SearchAgent(config)
```

**API Test Fixtures:**
```python
@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)

@pytest.fixture
def authenticated_client(test_client, test_user):
    """Create authenticated test client."""
    token = create_access_token(test_user.id)
    test_client.headers["Authorization"] = f"Bearer {token}"
    return test_client
```

### 3.4 Test Categories

#### Unit Tests Example

```python
# tests/unit/test_agents/test_credibility.py

import pytest
from app.agents.specialized.credibility import CredibilityAgent

class TestCredibilityAgent:
    """Test suite for CredibilityAgent."""

    @pytest.mark.asyncio
    async def test_assess_credibility_high_quality(self, credibility_agent):
        """Test credibility assessment for high-quality study."""
        study = {
            "title": "Randomized controlled trial...",
            "sample_size": 500,
            "methodology": "Double-blind RCT",
            "peer_reviewed": True
        }

        result = await credibility_agent.assess_credibility(study)

        assert result["credibility_level"] == "HIGH"
        assert result["confidence"] > 0.8
        assert "reasoning" in result

    @pytest.mark.asyncio
    async def test_assess_credibility_low_quality(self, credibility_agent):
        """Test credibility assessment for low-quality study."""
        study = {
            "title": "Observational study...",
            "sample_size": 10,
            "methodology": "Case report",
            "peer_reviewed": False
        }

        result = await credibility_agent.assess_credibility(study)

        assert result["credibility_level"] in ["LOW", "VERY_LOW"]
        assert result["confidence"] > 0.7

    def test_confidence_score_calculation(self, credibility_agent):
        """Test confidence score is always between 0 and 1."""
        scores = credibility_agent._calculate_confidence([0.5, 0.8, 0.9])
        assert 0 <= scores <= 1
```

#### Integration Tests Example

```python
# tests/integration/test_api/test_meta_analysis_api.py

import pytest

class TestMetaAnalysisAPI:
    """Integration tests for meta-analysis API."""

    def test_create_meta_analysis(self, authenticated_client):
        """Test creating a new meta-analysis project."""
        payload = {
            "title": "Test Meta-Analysis",
            "research_question": "What is the effect of X on Y?",
            "inclusion_criteria": ["RCTs", "Published after 2020"]
        }

        response = authenticated_client.post(
            "/api/v1/meta-analysis/create",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == payload["title"]

    def test_execute_workflow(self, authenticated_client, test_meta_analysis):
        """Test executing meta-analysis workflow."""
        response = authenticated_client.post(
            f"/api/v1/meta-analysis/execute/{test_meta_analysis.id}"
        )

        assert response.status_code == 202  # Accepted
        data = response.json()
        assert data["status"] == "in_progress"

    def test_invalid_authentication(self, test_client):
        """Test API rejects unauthenticated requests."""
        response = test_client.post("/api/v1/meta-analysis/create")
        assert response.status_code == 401
```

### 3.5 Mocking External APIs

**Anthropic API Mock:**
```python
# tests/fixtures/mocks/anthropic_responses.json

{
  "search_query_generation": {
    "prompt_contains": "generate search query",
    "response": "((meta-analysis) OR (systematic review)) AND (effect size)"
  },
  "credibility_assessment": {
    "prompt_contains": "assess credibility",
    "response": "HIGH credibility. Randomized controlled trial with large sample."
  },
  "screening_decision": {
    "prompt_contains": "screening criteria",
    "response": "INCLUDE. Study meets all inclusion criteria."
  }
}
```

**Mock Implementation:**
```python
# tests/conftest.py

import json
from pathlib import Path

@pytest.fixture
def anthropic_mock_responses():
    """Load mock responses for Anthropic API."""
    mock_file = Path(__file__).parent / "fixtures/mocks/anthropic_responses.json"
    with open(mock_file) as f:
        return json.load(f)

@pytest.fixture
def mock_anthropic_smart(monkeypatch, anthropic_mock_responses):
    """Smart Anthropic mock that returns context-appropriate responses."""
    class MockClient:
        def messages_create(self, **kwargs):
            prompt = kwargs.get("messages", [{}])[0].get("content", "")

            # Find matching response
            for key, mock in anthropic_mock_responses.items():
                if mock["prompt_contains"] in prompt.lower():
                    return MockMessage(mock["response"])

            return MockMessage("Generic mock response")

    monkeypatch.setattr("anthropic.Anthropic", lambda *args, **kwargs: MockClient())
```

### 3.6 Performance Benchmarks

```python
# tests/performance/test_agent_performance.py

import pytest
import time

class TestAgentPerformance:
    """Performance benchmarks for agents."""

    @pytest.mark.benchmark
    def test_search_agent_speed(self, search_agent, benchmark):
        """Search agent should process queries in < 2 seconds."""
        def run_search():
            return search_agent.search_pubmed("cancer AND therapy")

        result = benchmark(run_search)
        assert benchmark.stats.mean < 2.0  # < 2 seconds average

    @pytest.mark.benchmark
    def test_screening_agent_throughput(self, screening_agent, sample_papers):
        """Screening agent should process 100 papers in < 30 seconds."""
        start = time.time()

        for paper in sample_papers[:100]:
            screening_agent.screen_paper(paper)

        duration = time.time() - start
        assert duration < 30.0
        assert duration / 100 < 0.3  # < 300ms per paper
```

---

## 4. Frontend Testing Strategy

### 4.1 Test Framework

**Primary Tools:**
- `vitest` - Fast unit testing
- `@testing-library/react` - Component testing
- `@testing-library/user-event` - User interaction simulation
- `playwright` - E2E testing
- `axe-core` - Accessibility testing
- `@lighthouse/ci` - Performance testing

### 4.2 Test Structure

```
frontend/tests/
├── setup.ts                       # Test setup & configuration
├── vitest.config.ts              # Vitest configuration
│
├── unit/                          # Unit tests
│   ├── hooks/
│   │   ├── useAuth.test.ts
│   │   └── useMetaAnalysis.test.ts
│   └── utils/
│       ├── formatters.test.ts
│       └── validators.test.ts
│
├── components/                    # Component tests (25%)
│   ├── MetaAnalysisForm.test.tsx
│   ├── StudyList.test.tsx
│   ├── CredibilityBadge.test.tsx
│   └── ReviewerMatchCard.test.tsx
│
├── integration/                   # Integration tests
│   ├── MetaAnalysisWorkflow.test.tsx
│   └── ReviewerMatchFlow.test.tsx
│
├── e2e/                          # End-to-end tests (5%)
│   ├── meta-analysis.spec.ts
│   ├── reviewer-matcher.spec.ts
│   └── authentication.spec.ts
│
├── accessibility/                 # A11y tests
│   └── axe.test.tsx
│
└── fixtures/
    ├── mockData.ts
    └── testUtils.tsx
```

### 4.3 Component Testing Example

```typescript
// tests/components/CredibilityBadge.test.tsx

import { render, screen } from '@testing-library/react';
import { CredibilityBadge } from '@/components/CredibilityBadge';

describe('CredibilityBadge', () => {
  it('renders HIGH credibility with correct styling', () => {
    render(<CredibilityBadge level="HIGH" confidence={0.95} />);

    const badge = screen.getByText(/high/i);
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass('bg-green-500');
  });

  it('shows confidence score on hover', async () => {
    const { user } = setup(<CredibilityBadge level="MEDIUM" confidence={0.75} />);

    await user.hover(screen.getByText(/medium/i));

    expect(screen.getByText(/75% confidence/i)).toBeVisible();
  });

  it('renders low confidence warning', () => {
    render(<CredibilityBadge level="HIGH" confidence={0.45} />);

    expect(screen.getByRole('alert')).toHaveTextContent(/low confidence/i);
  });
});
```

### 4.4 E2E Testing Example

```typescript
// tests/e2e/meta-analysis.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Meta-Analysis Workflow', () => {
  test('complete meta-analysis from start to finish', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Create new meta-analysis
    await page.click('text=New Meta-Analysis');
    await page.fill('[name="title"]', 'Test Meta-Analysis');
    await page.fill('[name="research_question"]', 'What is the effect?');
    await page.click('text=Create');

    // Wait for creation
    await expect(page.locator('text=Meta-Analysis Created')).toBeVisible();

    // Execute workflow
    await page.click('text=Start Analysis');

    // Wait for completion (with timeout)
    await expect(page.locator('text=Analysis Complete')).toBeVisible({
      timeout: 60000
    });

    // Verify results
    await expect(page.locator('[data-testid="forest-plot"]')).toBeVisible();
    await expect(page.locator('[data-testid="effect-size"]')).toContainText(/\d+\.\d+/);
  });

  test('handles errors gracefully', async ({ page }) => {
    await page.goto('/meta-analysis/invalid-id');
    await expect(page.locator('text=Not Found')).toBeVisible();
  });
});
```

### 4.5 Accessibility Testing

```typescript
// tests/accessibility/axe.test.tsx

import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { MetaAnalysisPage } from '@/pages/meta-analysis';

expect.extend(toHaveNoViolations);

describe('Accessibility', () => {
  it('meta-analysis page has no accessibility violations', async () => {
    const { container } = render(<MetaAnalysisPage />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('keyboard navigation works', async () => {
    const { user } = setup(<MetaAnalysisForm />);

    await user.tab();
    expect(screen.getByLabelText(/title/i)).toHaveFocus();

    await user.tab();
    expect(screen.getByLabelText(/research question/i)).toHaveFocus();
  });
});
```

---

## 5. Agent Validation Testing

This is the most critical layer for academic credibility. Each tool has specific validation requirements.

### 5.1 Tool 1: Meta-Analysis Validation

**Goal:** Replicate published meta-analyses with >95% accuracy

```python
# tests/validation/test_meta_analysis/test_replication_studies.py

import pytest
from pathlib import Path
import json

class TestMetaAnalysisReplication:
    """Validate meta-analysis accuracy against published studies."""

    @pytest.fixture
    def cochrane_dataset_1(self):
        """Load Cochrane review replication dataset."""
        data_file = Path(__file__).parent / "datasets/cochrane_review_1.json"
        with open(data_file) as f:
            return json.load(f)

    @pytest.mark.validation
    @pytest.mark.slow
    async def test_replicate_cochrane_review_1(
        self,
        meta_analysis_workflow,
        cochrane_dataset_1
    ):
        """Replicate Cochrane review with known results."""
        # Run our meta-analysis
        result = await meta_analysis_workflow.execute(
            inclusion_criteria=cochrane_dataset_1["inclusion_criteria"],
            search_databases=cochrane_dataset_1["databases"],
            statistical_model="random_effects"
        )

        # Compare effect size
        published_effect_size = cochrane_dataset_1["results"]["effect_size"]
        published_ci_lower = cochrane_dataset_1["results"]["ci_lower"]
        published_ci_upper = cochrane_dataset_1["results"]["ci_upper"]

        # Allow 5% tolerance for computational differences
        assert abs(result.effect_size - published_effect_size) < 0.05
        assert abs(result.ci_lower - published_ci_lower) < 0.05
        assert abs(result.ci_upper - published_ci_upper) < 0.05

        # Compare heterogeneity
        published_i_squared = cochrane_dataset_1["results"]["i_squared"]
        assert abs(result.i_squared - published_i_squared) < 10  # Within 10%

        # Compare study inclusion
        published_included_studies = set(cochrane_dataset_1["included_studies"])
        our_included_studies = set([s.id for s in result.included_studies])

        agreement = len(published_included_studies & our_included_studies)
        total = len(published_included_studies | our_included_studies)
        overlap_percentage = (agreement / total) * 100

        assert overlap_percentage > 90  # >90% agreement on study inclusion

    @pytest.mark.validation
    def test_statistical_accuracy_validation(self, statistical_agent):
        """Validate statistical calculations against known values."""
        # Test data from published meta-analysis
        studies = [
            {"effect_size": 0.5, "se": 0.1, "n": 100},
            {"effect_size": 0.6, "se": 0.15, "n": 80},
            {"effect_size": 0.45, "se": 0.12, "n": 120}
        ]

        result = statistical_agent.calculate_meta_analysis(
            studies,
            model="fixed_effects"
        )

        # Known result from R metafor package
        expected_pooled_effect = 0.512
        expected_se = 0.067

        assert abs(result.pooled_effect - expected_pooled_effect) < 0.01
        assert abs(result.se - expected_se) < 0.01
```

### 5.2 Tool 4: Reviewer Matcher Validation

**Goal:** Match quality >80% agreement with expert editors

```python
# tests/validation/test_reviewer_matcher/test_match_quality.py

class TestReviewerMatchValidation:
    """Validate reviewer matching against editor selections."""

    @pytest.fixture
    def editor_validation_dataset(self):
        """100 manuscript-reviewer pairs validated by editors."""
        return load_validation_dataset("editor_matches_2024.json")

    @pytest.mark.validation
    async def test_match_quality_against_editors(
        self,
        reviewer_matcher,
        editor_validation_dataset
    ):
        """Compare AI matches with actual editor selections."""
        results = {
            "total": 0,
            "top_3_match": 0,
            "top_5_match": 0,
            "expertise_scores": []
        }

        for case in editor_validation_dataset:
            manuscript = case["manuscript"]
            editor_selected = set(case["selected_reviewers"])

            # Get AI recommendations
            matches = await reviewer_matcher.find_reviewers(
                manuscript=manuscript,
                n_recommendations=10
            )

            ai_top_3 = set([m.reviewer_id for m in matches[:3]])
            ai_top_5 = set([m.reviewer_id for m in matches[:5]])

            # Check if editor's choice appears in top-N
            if editor_selected & ai_top_3:
                results["top_3_match"] += 1
            if editor_selected & ai_top_5:
                results["top_5_match"] += 1

            results["total"] += 1

            # Collect expertise scores for selected reviewers
            for selected_id in editor_selected:
                match = next((m for m in matches if m.reviewer_id == selected_id), None)
                if match:
                    results["expertise_scores"].append(match.expertise_score)

        # Validation criteria
        top_3_rate = results["top_3_match"] / results["total"]
        top_5_rate = results["top_5_match"] / results["total"]
        avg_expertise = sum(results["expertise_scores"]) / len(results["expertise_scores"])

        assert top_3_rate > 0.60  # 60% of editor picks in top-3
        assert top_5_rate > 0.80  # 80% of editor picks in top-5
        assert avg_expertise > 0.75  # High expertise scores for selected reviewers

    @pytest.mark.validation
    async def test_coi_detection_accuracy(self, conflict_detector):
        """Test conflict detection on known cases."""
        known_conflicts = load_known_conflicts("coi_test_cases.json")

        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0

        for case in known_conflicts:
            result = await conflict_detector.check_conflict(
                author_id=case["author_id"],
                reviewer_id=case["reviewer_id"]
            )

            has_conflict = result.conflict_risk > 0.5

            if case["has_conflict"] and has_conflict:
                true_positives += 1
            elif case["has_conflict"] and not has_conflict:
                false_negatives += 1
            elif not case["has_conflict"] and has_conflict:
                false_positives += 1
            else:
                true_negatives += 1

        # Calculate metrics
        precision = true_positives / (true_positives + false_positives)
        recall = true_positives / (true_positives + false_negatives)
        f1_score = 2 * (precision * recall) / (precision + recall)

        # Validation criteria
        assert precision > 0.90  # Low false positive rate
        assert recall > 0.95  # Catch nearly all conflicts
        assert f1_score > 0.92  # Overall accuracy
```

### 5.3 Tool 3: Peer Review Quality Validation

**Goal:** Review quality in top 50% of human reviews

```python
# tests/validation/test_peer_review/test_review_quality.py

class TestPeerReviewValidation:
    """Validate peer review quality against human reviews."""

    @pytest.mark.validation
    async def test_review_quality_scoring(self, review_drafter, expert_raters):
        """Expert raters score AI-generated reviews."""
        manuscripts = load_test_manuscripts(n=20)
        ratings = []

        for manuscript in manuscripts:
            # Generate AI review
            ai_review = await review_drafter.generate_review(manuscript)

            # Get expert ratings (1-5 scale)
            expert_scores = []
            for rater in expert_raters:
                score = rater.rate_review(
                    review=ai_review,
                    criteria=[
                        "technical_accuracy",
                        "constructiveness",
                        "completeness",
                        "clarity"
                    ]
                )
                expert_scores.append(score)

            avg_score = sum(expert_scores) / len(expert_scores)
            ratings.append(avg_score)

        # Validation criteria
        overall_avg = sum(ratings) / len(ratings)
        assert overall_avg > 3.5  # Average rating > 3.5/5
        assert min(ratings) > 2.5  # No terrible reviews
        assert sum(1 for r in ratings if r >= 4.0) / len(ratings) > 0.30  # 30% excellent

    @pytest.mark.validation
    async def test_bias_detection_accuracy(self, bias_detector):
        """Test bias detection on known biased examples."""
        biased_examples = load_biased_review_examples()

        detected = 0
        for example in biased_examples:
            result = bias_detector.check_bias(example["text"])

            if result.bias_score > 0.3:  # Threshold for flagging
                detected += 1

        detection_rate = detected / len(biased_examples)
        assert detection_rate > 0.90  # Detect >90% of biased language
```

### 5.4 Tool 2: Research Direction Validation

**Goal:** Novelty scoring >4.0/5 by expert researchers

```python
# tests/validation/test_research_direction/test_gap_identification.py

class TestResearchDirectionValidation:
    """Validate research direction suggestions."""

    @pytest.mark.validation
    async def test_gap_identification_novelty(self, gap_analyzer, expert_panel):
        """Expert panel rates novelty of identified gaps."""
        meta_analyses = load_completed_meta_analyses(n=10)
        novelty_scores = []

        for ma in meta_analyses:
            # Identify gaps
            gaps = await gap_analyzer.identify_gaps(ma.findings)

            # Expert panel rates novelty
            for gap in gaps[:5]:  # Top 5 gaps
                panel_scores = []
                for expert in expert_panel:
                    score = expert.rate_novelty(
                        gap=gap,
                        domain=ma.domain
                    )
                    panel_scores.append(score)

                avg_novelty = sum(panel_scores) / len(panel_scores)
                novelty_scores.append(avg_novelty)

        # Validation criteria
        overall_avg = sum(novelty_scores) / len(novelty_scores)
        assert overall_avg > 4.0  # Average novelty > 4.0/5
        assert sum(1 for s in novelty_scores if s >= 4.5) / len(novelty_scores) > 0.20
```

---

## 6. Performance Testing

### 6.1 Performance Benchmarks

```python
# tests/performance/test_api_performance.py

class TestAPIPerformance:
    """Performance benchmarks for API endpoints."""

    @pytest.mark.performance
    def test_api_response_time(self, authenticated_client):
        """API endpoints respond within acceptable time."""
        endpoints = [
            ("GET", "/api/v1/meta-analysis/list", 500),  # < 500ms
            ("POST", "/api/v1/meta-analysis/create", 1000),  # < 1s
            ("GET", "/api/v1/studies/search", 2000),  # < 2s
        ]

        for method, endpoint, max_time_ms in endpoints:
            start = time.time()

            if method == "GET":
                response = authenticated_client.get(endpoint)
            else:
                response = authenticated_client.post(endpoint, json={})

            duration_ms = (time.time() - start) * 1000

            assert response.status_code < 500  # No server errors
            assert duration_ms < max_time_ms, f"{endpoint} took {duration_ms}ms"

    @pytest.mark.performance
    def test_concurrent_requests(self, authenticated_client):
        """API handles concurrent requests without degradation."""
        import concurrent.futures

        def make_request():
            return authenticated_client.get("/api/v1/meta-analysis/list")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [f.result() for f in futures]

        success_rate = sum(1 for r in results if r.status_code == 200) / len(results)
        assert success_rate > 0.95  # >95% success rate
```

### 6.2 Load Testing

```python
# tests/performance/load_test.py

from locust import HttpUser, task, between

class MetaAnalysisUser(HttpUser):
    """Simulated user for load testing."""
    wait_time = between(1, 3)

    def on_start(self):
        """Login before starting tasks."""
        self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })

    @task(3)
    def list_projects(self):
        """List meta-analysis projects."""
        self.client.get("/api/v1/meta-analysis/list")

    @task(1)
    def create_project(self):
        """Create new meta-analysis."""
        self.client.post("/api/v1/meta-analysis/create", json={
            "title": "Load Test Analysis",
            "research_question": "Test question?"
        })

    @task(2)
    def search_studies(self):
        """Search for studies."""
        self.client.post("/api/v1/studies/search", json={
            "query": "cancer therapy",
            "databases": ["pubmed"]
        })
```

---

## 7. Security Testing

### 7.1 Authentication Tests

```python
# tests/security/test_authentication.py

class TestAuthentication:
    """Security tests for authentication system."""

    def test_password_hashing(self, auth_service):
        """Passwords are properly hashed."""
        password = "SecurePassword123!"
        hashed = auth_service.hash_password(password)

        assert hashed != password
        assert len(hashed) > 50  # Bcrypt hash length
        assert auth_service.verify_password(password, hashed)

    def test_jwt_token_expiration(self, auth_service):
        """JWT tokens expire after configured time."""
        token = auth_service.create_token(user_id="test", expires_in=1)

        # Token valid immediately
        assert auth_service.verify_token(token) is not None

        # Token expired after 2 seconds
        time.sleep(2)
        with pytest.raises(ExpiredTokenError):
            auth_service.verify_token(token)

    def test_sql_injection_protection(self, test_client):
        """API protects against SQL injection."""
        malicious_input = "'; DROP TABLE users; --"

        response = test_client.post("/api/v1/auth/login", json={
            "email": malicious_input,
            "password": "test"
        })

        # Should fail authentication, not execute SQL
        assert response.status_code == 401

        # Verify users table still exists
        response = test_client.get("/api/v1/users")
        assert response.status_code in [200, 401]  # Not 500
```

---

## 8. CI/CD Integration

### 8.1 GitHub Actions Workflow

See `.github/workflows/test.yml` for complete CI/CD pipeline.

**Key Features:**
- Run on every PR and push to main
- Parallel test execution
- Coverage reporting to Codecov
- Performance regression detection
- Deployment gates (tests must pass)

### 8.2 Test Stages

```yaml
stages:
  1. Lint & Format Check (30s)
  2. Unit Tests (1-2 min)
  3. Integration Tests (2-3 min)
  4. E2E Tests (3-5 min)
  5. Security Scan (1 min)
  6. Coverage Report (30s)
  7. Performance Benchmarks (2 min)
```

---

## 9. Test Data Management

### 9.1 Test Data Sources

**Synthetic Data:**
- Factory-generated papers, researchers, manuscripts
- Controlled for edge cases
- Fast generation

**Anonymized Real Data:**
- Published meta-analyses with open data
- Public researcher profiles (ORCID)
- Sanitized manuscripts (with permission)

**Gold Standard Datasets:**
- Cochrane reviews with replication data
- JAMA/BMJ meta-analyses
- Known COI cases from retractions

### 9.2 Data Fixtures Location

```
backend/tests/fixtures/
├── papers/
│   ├── sample_papers.json          # 100 synthetic papers
│   ├── meta_analysis_datasets/
│   │   ├── cochrane_review_1.json
│   │   ├── cochrane_review_2.json
│   │   └── jama_meta_analysis_1.json
│   └── edge_cases/
│       ├── missing_data.json
│       └── conflicting_results.json
├── researchers/
│   ├── researcher_profiles.json    # 200 researcher profiles
│   └── coauthor_networks.json     # Network data
├── manuscripts/
│   ├── test_manuscripts.json       # 50 test manuscripts
│   └── biased_reviews.json        # Known biased examples
└── mocks/
    ├── anthropic_responses.json
    └── database_responses.json
```

---

## 10. Quality Metrics

### 10.1 Coverage Targets

| Component | Target | Current | Status |
|-----------|--------|---------|--------|
| Overall | 80% | TBD | 🔴 |
| Critical Paths | 100% | TBD | 🔴 |
| Agents | 85% | TBD | 🔴 |
| API Endpoints | 90% | TBD | 🔴 |
| Utils | 80% | TBD | 🔴 |
| UI Components | 75% | TBD | 🔴 |

### 10.2 Test Execution Metrics

**Target Metrics:**
- Full test suite: < 5 minutes
- Unit tests: < 30 seconds
- Integration tests: < 2 minutes
- E2E tests: < 3 minutes
- CI pipeline: < 10 minutes total

### 10.3 Quality Gates

**Pre-Commit:**
- Code formatted (black, prettier)
- Linting passes (flake8, eslint)
- Type checking passes (mypy, tsc)

**Pre-Push:**
- Unit tests pass
- Coverage maintained or increased

**Pre-Merge (PR):**
- All tests pass
- Coverage ≥ 80%
- No security vulnerabilities
- Performance benchmarks acceptable
- Code review approved

**Pre-Deploy:**
- E2E tests pass
- Integration tests pass
- Validation tests pass (for affected tools)
- Performance regression check

---

## 11. Running Tests

### 11.1 Backend Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit

# Integration tests
pytest tests/integration

# Validation tests (slow)
pytest tests/validation -m validation

# With coverage
pytest --cov=app --cov-report=html

# Performance benchmarks
pytest tests/performance -m performance

# Watch mode (auto-rerun on changes)
pytest-watch

# Specific test file
pytest tests/unit/test_agents/test_credibility.py

# Specific test function
pytest tests/unit/test_agents/test_credibility.py::test_assess_credibility_high_quality
```

### 11.2 Frontend Tests

```bash
# All tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage

# E2E tests
npm run test:e2e

# Accessibility tests
npm run test:a11y

# Performance tests
npm run test:performance
```

### 11.3 Full Test Suite

```bash
# Run everything
./scripts/run_all_tests.sh
```

---

## 12. Continuous Improvement

### 12.1 Test Maintenance

- **Weekly:** Review failing tests, update mocks
- **Monthly:** Review coverage, add missing tests
- **Quarterly:** Update validation datasets, re-run gold standard comparisons
- **Annually:** Review testing strategy, update benchmarks

### 12.2 Feedback Loops

1. **Academic Validation**
   - Continuously collect feedback from researchers
   - Update validation criteria based on published comparisons
   - Track accuracy metrics over time

2. **User Feedback**
   - Bug reports → Regression tests
   - Feature requests → Test coverage
   - Performance complaints → New benchmarks

3. **CI Metrics**
   - Track test execution time trends
   - Monitor flaky tests
   - Coverage trends over time

---

## Appendix A: Test Command Reference

See individual test files for detailed command options.

## Appendix B: Mock Data Specifications

See `tests/fixtures/` for mock data schemas.

## Appendix C: Validation Dataset Descriptions

See `tests/validation/datasets/README.md` for dataset details.

---

**Document Status:** ✅ Complete
**Last Updated:** November 4, 2025
**Next Review:** December 1, 2025
**Owner:** QA Lead Engineer

---

*This is a living document. All team members should contribute to keeping testing standards high.*
