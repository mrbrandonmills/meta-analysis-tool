# Testing Guide for Meta-Analysis Tool

This document provides comprehensive guidance on testing the Meta-Analysis Tool, including unit tests, integration tests, E2E tests, and CI/CD pipelines.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [E2E Testing](#e2e-testing)
- [Running Tests](#running-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Writing Tests](#writing-tests)
- [Coverage Requirements](#coverage-requirements)
- [Best Practices](#best-practices)

## Overview

Our testing strategy follows the **testing pyramid** approach:

```
         /\
        /E2E\          <- Few, slow, expensive (10%)
       /------\
      /Integr.\       <- Medium number, medium speed (20%)
     /----------\
    /   Unit     \    <- Many, fast, cheap (70%)
   /--------------\
```

### Test Levels

1. **Unit Tests (70%)**: Test individual components, functions, and classes in isolation
2. **Integration Tests (20%)**: Test interactions between components and external services
3. **E2E Tests (10%)**: Test complete user workflows from end to end

## Test Structure

```
meta-analysis-tool/
├── backend/
│   ├── tests/
│   │   ├── conftest.py              # Pytest fixtures
│   │   ├── unit/
│   │   │   ├── test_agents/         # Agent unit tests
│   │   │   ├── test_services/       # Service unit tests
│   │   │   └── test_models/         # Model unit tests
│   │   ├── integration/
│   │   │   ├── test_api/            # API integration tests
│   │   │   ├── test_workflows/      # Workflow integration tests
│   │   │   └── test_database/       # Database integration tests
│   │   └── validation/
│   │       └── test_meta_analysis/  # Validation against gold standards
│   └── pytest.ini                   # Pytest configuration
├── frontend/
│   ├── tests/
│   │   ├── components/              # Component tests
│   │   ├── hooks/                   # Custom hook tests
│   │   ├── integration/             # API client tests
│   │   └── setup.ts                 # Test setup
│   └── vitest.config.ts             # Vitest configuration
└── tests/
    └── e2e/
        ├── playwright.config.ts     # Playwright configuration
        ├── auth.spec.ts             # Auth E2E tests
        └── meta-analysis-workflow.spec.ts  # Workflow E2E tests
```

## Backend Testing

### Setup

```bash
cd backend
pip install -r requirements-test.txt
```

### Running Backend Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit -v

# Run integration tests only
pytest tests/integration -v

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_agents/test_search_agent.py -v

# Run tests matching pattern
pytest -k "search" -v

# Run with markers
pytest -m "unit" -v
pytest -m "integration" -v
pytest -m "slow" -v
```

### Available Pytest Markers

- `@pytest.mark.unit`: Unit tests (fast, isolated)
- `@pytest.mark.integration`: Integration tests (external dependencies)
- `@pytest.mark.e2e`: End-to-end tests (full workflow)
- `@pytest.mark.validation`: Validation tests against gold standards
- `@pytest.mark.performance`: Performance and load tests
- `@pytest.mark.security`: Security tests
- `@pytest.mark.slow`: Slow running tests

### Example Backend Test

```python
import pytest
from app.agents.specialized.search import SearchAgent

class TestSearchAgent:
    @pytest.fixture
    def search_agent(self, mock_anthropic_client):
        config = AgentConfig(name="test", role=AgentRole.SEARCH)
        return SearchAgent(config)

    @pytest.mark.asyncio
    async def test_search_with_query(self, search_agent):
        input_data = {
            "research_question": "Effect of exercise on depression",
            "databases": ["pubmed"]
        }

        result = await search_agent.process(input_data)

        assert result is not None
        assert "studies" in result or "results" in result
```

## Frontend Testing

### Setup

```bash
cd frontend
npm install
```

### Running Frontend Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test

# Run with coverage
npm run test:coverage

# Run tests with UI
npm run test:ui

# Run specific test file
npm test -- src/components/MetaAnalysisForm.test.tsx
```

### Example Frontend Test

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MetaAnalysisForm from '@/components/MetaAnalysisForm';

describe('MetaAnalysisForm', () => {
  it('submits form with valid data', async () => {
    const user = userEvent.setup();
    const mockOnSubmit = vi.fn();

    render(<MetaAnalysisForm onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/research question/i), 'Test question');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    expect(mockOnSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        researchQuestion: 'Test question'
      })
    );
  });
});
```

## E2E Testing

### Setup

```bash
cd tests/e2e
npm install
npx playwright install --with-deps
```

### Running E2E Tests

```bash
# Run all E2E tests
npx playwright test

# Run in specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific test file
npx playwright test auth.spec.ts

# Run with UI mode
npx playwright test --ui

# Debug mode
npx playwright test --debug
```

### Example E2E Test

```typescript
import { test, expect } from '@playwright/test';

test('complete meta-analysis workflow', async ({ page }) => {
  // Login
  await page.goto('/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'password');
  await page.click('button[type="submit"]');

  // Create analysis
  await page.goto('/meta-analysis/create');
  await page.fill('textarea[name="researchQuestion"]', 'Test question');
  await page.click('button[type="submit"]');

  // Verify creation
  await expect(page).toHaveURL(/dashboard/);
  await expect(page.locator('text=/success/i')).toBeVisible();
});
```

## CI/CD Pipeline

### GitHub Actions Workflows

We have four main CI/CD workflows:

1. **Backend Tests** (`.github/workflows/backend-tests.yml`)
   - Runs on: Push to main/develop, PRs
   - Jobs: Unit tests, integration tests, code quality, security
   - Coverage requirement: 80%

2. **Frontend Tests** (`.github/workflows/frontend-tests.yml`)
   - Runs on: Push to main/develop, PRs
   - Jobs: Unit tests, linting, type checking, build
   - Coverage requirement: 60% (increasing to 80%)

3. **E2E Tests** (`.github/workflows/e2e-tests.yml`)
   - Runs on: Push to main/develop, PRs, daily schedule
   - Jobs: E2E tests across browsers, mobile tests, accessibility, performance

4. **Production Readiness** (`.github/workflows/production-readiness.yml`)
   - Runs on: PRs to main
   - Jobs: Full test suite, security scans, load tests

### Quality Gates

PRs must pass all of these to merge:

- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ Code coverage ≥ 80% (backend), ≥ 60% (frontend)
- ✅ No linting errors
- ✅ TypeScript/mypy type checking passes
- ✅ No high-severity security vulnerabilities
- ✅ Build succeeds

### Viewing Test Results

1. **GitHub Actions UI**: Go to Actions tab → Select workflow run
2. **Test Reports**: Download artifacts from workflow run
3. **Coverage Reports**: Check Codecov.io integration
4. **Playwright Reports**: Download HTML reports from E2E workflow

## Writing Tests

### Test Naming Conventions

```python
# Python (pytest)
def test_<what_is_being_tested>_<expected_behavior>():
    # Examples:
    def test_search_agent_returns_studies():
    def test_screening_agent_filters_by_criteria():
    def test_api_endpoint_requires_authentication():
```

```typescript
// TypeScript (Vitest/Playwright)
it('should <expected behavior>', async () => {
  // Examples:
  it('should submit form with valid data', async () => {});
  it('should show error for invalid email', async () => {});
  it('should redirect after successful login', async () => {});
});
```

### AAA Pattern

Follow the **Arrange-Act-Assert** pattern:

```python
def test_screening_agent():
    # Arrange - Set up test data
    agent = ScreeningAgent(config)
    input_data = {"studies": [...], "criteria": [...]}

    # Act - Perform the action
    result = await agent.process(input_data)

    # Assert - Verify the outcome
    assert result["included"] is not None
    assert len(result["excluded"]) > 0
```

### Mocking Best Practices

```python
# Use pytest fixtures for common mocks
@pytest.fixture
def mock_anthropic_client(monkeypatch):
    mock_client = MockAnthropicClient()
    monkeypatch.setattr("anthropic.Anthropic", lambda: mock_client)
    return mock_client

# Mock external APIs
@pytest.fixture
def mock_pubmed_api(requests_mock):
    requests_mock.get(
        "https://pubmed.ncbi.nlm.nih.gov/api",
        json={"results": [...]}
    )
```

## Coverage Requirements

### Backend

- **Overall**: 80% minimum
- **Critical paths**: 90%+
- **Agents**: 85%+
- **API endpoints**: 90%+
- **Services**: 85%+
- **Models**: 70%+

### Frontend

- **Overall**: 60% minimum (target: 80%)
- **Components**: 70%+
- **Hooks**: 80%+
- **API client**: 85%+
- **Utilities**: 90%+

### Viewing Coverage

```bash
# Backend
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html

# Frontend
cd frontend
npm run test:coverage
open coverage/index.html
```

## Best Practices

### DO ✅

1. **Write tests first** (TDD): Write failing test → Make it pass → Refactor
2. **Test behavior, not implementation**: Focus on what, not how
3. **Keep tests independent**: Tests should not depend on each other
4. **Use descriptive names**: `test_search_returns_empty_array_when_no_results()`
5. **Mock external dependencies**: Don't hit real APIs in tests
6. **Test edge cases**: Empty inputs, null values, errors
7. **Keep tests fast**: Unit tests should run in milliseconds
8. **Use fixtures**: Reuse common test setup
9. **Test error handling**: Verify errors are handled gracefully
10. **Document complex tests**: Add comments explaining why

### DON'T ❌

1. **Don't test implementation details**: Test public API only
2. **Don't rely on test order**: Tests should work in any order
3. **Don't use sleeps**: Use proper async/await or mocking
4. **Don't skip tests**: Fix or remove broken tests
5. **Don't test third-party code**: Trust libraries work
6. **Don't write huge tests**: Split into smaller, focused tests
7. **Don't hardcode values**: Use fixtures and factories
8. **Don't ignore flaky tests**: Fix or investigate immediately
9. **Don't test private methods directly**: Test through public API
10. **Don't commit commented-out tests**: Remove or fix

### Testing Checklist

Before submitting a PR, ensure:

- [ ] All new code has tests
- [ ] All tests pass locally
- [ ] Coverage meets requirements
- [ ] No skipped tests without reason
- [ ] Tests follow naming conventions
- [ ] Mocks are used appropriately
- [ ] Edge cases are covered
- [ ] Error cases are tested
- [ ] Tests are fast (unit tests < 1s)
- [ ] CI/CD pipeline passes

## Troubleshooting

### Common Issues

**Tests fail locally but pass in CI**
- Check Python/Node versions match
- Ensure all dependencies installed
- Check environment variables

**Tests are slow**
- Profile tests: `pytest --durations=10`
- Mock external services
- Use in-memory databases for tests

**Flaky tests**
- Add explicit waits in E2E tests
- Check for race conditions
- Use `pytest-randomly` to find order dependencies

**Coverage not updating**
- Delete `.coverage` file
- Run `coverage erase`
- Rebuild coverage report

### Getting Help

- **Slack**: #testing channel
- **GitHub Issues**: Tag with `testing` label
- **Documentation**: This file + inline code comments
- **CI/CD Logs**: Check GitHub Actions for detailed error messages

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library](https://testing-library.com/)
- [Martin Fowler - Testing](https://martinfowler.com/testing/)

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure coverage meets requirements
3. Update this documentation if needed
4. Add examples for complex tests
5. Review testing checklist before PR

---

**Last Updated**: 2025-11-06
**Version**: 1.0.0
**Maintainers**: Test Expert Team
