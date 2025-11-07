# Testing Guide

Comprehensive testing guide for the Meta-Analysis Research Platform, covering unit tests, integration tests, E2E tests, and CI/CD pipelines.

## Table of Contents

- [Overview](#overview)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [E2E Testing](#e2e-testing)
- [CI/CD Pipelines](#cicd-pipelines)
- [Coverage Requirements](#coverage-requirements)
- [Running Tests Locally](#running-tests-locally)
- [Writing New Tests](#writing-new-tests)
- [Troubleshooting](#troubleshooting)

## Overview

This project uses a comprehensive testing strategy to ensure code quality, reliability, and maintainability:

- **Backend**: pytest with asyncio support, 80%+ coverage required
- **Frontend**: Vitest with React Testing Library, 80%+ coverage target
- **E2E**: Playwright for cross-browser testing
- **CI/CD**: GitHub Actions with automatic deployment

### Test Pyramid

```
        /\
       /  \      E2E Tests (Playwright)
      /____\     - Cross-browser
     /      \    - Mobile
    /        \   - Accessibility
   /___________\
  /            \ Integration Tests
 /              \ - API endpoints
/                \ - Database operations
/__________________\ Unit Tests
                    - Agents
                    - Components
                    - Models
                    - Utils
```

## Backend Testing

### Directory Structure

```
backend/tests/
├── conftest.py                 # Pytest fixtures and configuration
├── pytest.ini                  # Pytest settings
├── unit/                       # Unit tests (fast, isolated)
│   ├── test_agents/           # Agent tests
│   ├── test_api/              # API unit tests
│   ├── test_models/           # Database model tests
│   └── test_utils/            # Utility function tests
├── integration/                # Integration tests (external services)
│   ├── test_api/              # Full API integration tests
│   └── test_workflows/        # End-to-end workflow tests
├── validation/                 # Validation tests (gold standards)
│   └── test_meta_analysis/
└── fixtures/                   # Test data and fixtures
```

### Running Backend Tests

```bash
# All tests
cd backend
pytest

# Unit tests only
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# Validation tests (slow, may fail)
pytest tests/validation -v -m validation

# With coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Specific test file
pytest tests/unit/test_agents/test_search_agent_v2.py -v

# Specific test function
pytest tests/unit/test_agents/test_search_agent_v2.py::TestQueryBuilder::test_build_pubmed_query_basic -v

# Run in parallel (faster)
pytest -n auto

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run only failed tests from last run
pytest --lf
```

### Backend Test Categories

#### Unit Tests

Test individual components in isolation:

```python
# Example: Testing an agent
@pytest.mark.asyncio
async def test_search_agent_query_building(search_agent):
    """Test that search agent builds valid PubMed queries."""
    result = await search_agent.execute({
        "research_question": "Effect of exercise on diabetes",
        "databases": ["pubmed"]
    })

    assert result["status"] == "success"
    assert "query" in result
    assert "diabetes" in result["query"].lower()
```

#### Integration Tests

Test multiple components working together:

```python
# Example: Testing API endpoint with database
@pytest.mark.asyncio
async def test_create_meta_analysis_integration(client, async_session):
    """Test creating meta-analysis through API."""
    response = await client.post(
        "/api/v1/meta-analysis/create",
        json={
            "research_question": "Test question",
            "topic": "Test topic"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None

    # Verify database record was created
    from app.models.meta_analysis import MetaAnalysis
    analysis = await async_session.get(MetaAnalysis, data["id"])
    assert analysis is not None
```

#### Validation Tests

Compare against gold standards:

```python
@pytest.mark.validation
@pytest.mark.slow
async def test_statistical_accuracy_against_gold_standard():
    """Validate statistical calculations against known meta-analysis."""
    # Load gold standard data
    gold_standard = load_gold_standard("diabetes_exercise.json")

    # Run our analysis
    our_result = await run_meta_analysis(gold_standard["inputs"])

    # Compare results (allow small tolerance)
    assert abs(our_result["effect_size"] - gold_standard["effect_size"]) < 0.01
```

### Backend Test Fixtures

Common fixtures available in `conftest.py`:

- `async_session` - Async database session
- `client` - FastAPI test client
- `agent_config` - Agent configuration
- `mock_anthropic_api` - Mocked Claude API
- `sample_papers` - Test paper data

### Code Quality Checks

```bash
# Format code with Black
black app tests

# Check formatting
black --check app tests

# Sort imports
isort app tests

# Lint with flake8
flake8 app tests --max-line-length=120

# Type check with mypy
mypy app --ignore-missing-imports

# Security scan
bandit -r app -ll
```

## Frontend Testing

### Directory Structure

```
frontend/tests/
├── setup.ts                    # Test setup and global mocks
├── components/                 # Component tests
│   ├── Button.test.tsx
│   ├── Card.test.tsx
│   └── visualizations/
├── integration/                # Integration tests
│   └── meta-analysis-workflow.test.tsx
├── unit/                       # Unit tests
│   └── api-client.test.ts
└── e2e/                        # E2E tests (Playwright)
```

### Running Frontend Tests

```bash
# All tests
cd frontend
npm test

# With UI
npm run test:ui

# With coverage
npm run test:coverage

# Watch mode
npm test -- --watch

# Specific file
npm test -- Button.test.tsx

# Update snapshots
npm test -- -u
```

### Frontend Test Examples

#### Component Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/shared/Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    await userEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByText('Click me')).toBeDisabled();
  });
});
```

#### API Client Tests

```typescript
import MockAdapter from 'axios-mock-adapter';
import { authApi } from '@/lib/api';

describe('Auth API', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(axios);
  });

  it('should login successfully', async () => {
    mock.onPost('/api/v1/auth/login').reply(200, {
      access_token: 'token',
      user: { id: '1', email: 'test@example.com' }
    });

    const result = await authApi.login({
      username: 'test@example.com',
      password: 'password'
    });

    expect(result.access_token).toBe('token');
  });
});
```

### Frontend Code Quality

```bash
# Lint
npm run lint

# Type check
npx tsc --noEmit

# Format with Prettier
npx prettier --write "src/**/*.{ts,tsx}"

# Check formatting
npx prettier --check "src/**/*.{ts,tsx}"
```

## E2E Testing

### Playwright Configuration

E2E tests are located in `tests/e2e/` and run with Playwright.

### Running E2E Tests

```bash
cd tests/e2e

# Install Playwright
npm install

# Install browsers
npx playwright install

# Run all E2E tests
npx playwright test

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific browser
npx playwright test --project=chromium

# Debug mode
npx playwright test --debug

# Show test report
npx playwright show-report
```

### E2E Test Example

```typescript
import { test, expect } from '@playwright/test';

test.describe('Meta-Analysis Workflow', () => {
  test('should create and execute meta-analysis', async ({ page }) => {
    // Navigate to app
    await page.goto('http://localhost:3000');

    // Login
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'password');
    await page.click('[data-testid="login-button"]');

    // Wait for dashboard
    await expect(page).toHaveURL(/.*dashboard/);

    // Create meta-analysis
    await page.click('[data-testid="create-analysis-button"]');
    await page.fill('[data-testid="research-question"]', 'Test question');
    await page.click('[data-testid="submit-button"]');

    // Verify creation
    await expect(page.locator('[data-testid="analysis-status"]')).toContainText('created');
  });
});
```

## CI/CD Pipelines

### GitHub Actions Workflows

#### Backend CI/CD (`.github/workflows/backend-ci-cd.yml`)

**Triggers**: Push to main/develop, PRs
**Jobs**:
1. **Test** - Unit and integration tests with 80% coverage requirement
2. **Security Scan** - Bandit and Safety checks
3. **Deploy** - Automatic deployment to Railway on main branch
4. **Notify** - Send deployment status

**Secrets Required**:
- `ANTHROPIC_API_KEY`
- `RAILWAY_TOKEN`
- `RAILWAY_API_URL`
- `CODECOV_TOKEN`

#### Frontend CI/CD (`.github/workflows/frontend-ci-cd.yml`)

**Triggers**: Push to main/develop, PRs
**Jobs**:
1. **Test** - Unit tests, linting, type checking, build
2. **Code Quality** - Prettier, console check, bundle size
3. **Security** - npm audit
4. **Deploy Preview** - Vercel preview on PRs
5. **Deploy Production** - Vercel production on main branch

**Secrets Required**:
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `NEXT_PUBLIC_API_URL`
- `CODECOV_TOKEN`

#### E2E Tests (`.github/workflows/e2e-tests.yml`)

**Triggers**: Push, PRs, daily schedule, manual
**Jobs**:
1. **E2E Tests** - Cross-browser testing (Chromium, Firefox, WebKit)
2. **Mobile Tests** - Mobile Chrome and Safari
3. **Accessibility** - axe-core accessibility checks
4. **Performance** - Lighthouse CI
5. **Report** - Merge and publish reports

**Secrets Required**:
- `STAGING_FRONTEND_URL`
- `STAGING_API_URL`
- `PRODUCTION_FRONTEND_URL`
- `PRODUCTION_API_URL`
- `E2E_TEST_USER_EMAIL`
- `E2E_TEST_USER_PASSWORD`

### Setting Up CI/CD

1. **Fork the repository**

2. **Add secrets to GitHub**:
   - Go to Settings > Secrets and variables > Actions
   - Add all required secrets listed above

3. **Configure Railway**:
   - Link your Railway project
   - Get Railway token: `railway login` then `railway whoami --token`

4. **Configure Vercel**:
   - Link your Vercel project
   - Get Vercel token from account settings
   - Get org ID and project ID: `vercel link`

5. **Enable workflows**:
   - Workflows run automatically on push/PR
   - Check Actions tab to see results

### CI/CD Best Practices

- **PRs must pass all checks** before merging
- **Coverage must meet thresholds** (80% backend, 80% frontend)
- **Security scans must pass** (no high/critical vulnerabilities)
- **E2E tests run nightly** to catch regressions
- **Deployments are automatic** on main branch

## Coverage Requirements

### Backend Coverage

- **Minimum**: 80% overall coverage
- **Critical paths**: 90%+ coverage
- **Agents**: 85%+ coverage
- **API endpoints**: 80%+ coverage
- **Models**: 75%+ coverage

### Frontend Coverage

- **Target**: 80% overall coverage
- **Components**: 80%+ coverage
- **API client**: 90%+ coverage
- **Integration**: 70%+ coverage

### Checking Coverage

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

## Running Tests Locally

### Quick Pre-Commit Check

```bash
# Run this before committing
./scripts/pre-commit-tests.sh
```

### Full Test Suite

```bash
# Run all tests (backend + frontend + E2E)
./scripts/run-all-tests.sh

# Backend only
./scripts/run-all-tests.sh --backend-only

# Frontend only
./scripts/run-all-tests.sh --frontend-only

# With validation tests
./scripts/run-all-tests.sh --with-validation
```

### Coverage Check

```bash
# Check coverage and generate reports
./scripts/check-coverage.sh

# Open reports in browser
./scripts/check-coverage.sh --open
```

## Writing New Tests

### Backend Test Template

```python
"""Tests for [Feature Name]."""
import pytest
from unittest.mock import AsyncMock, patch

from app.[module] import [Class]


@pytest.fixture
def sample_data():
    """Create sample test data."""
    return {"key": "value"}


class Test[ClassName]:
    """Tests for [ClassName]."""

    @pytest.mark.asyncio
    async def test_[feature_name](self, sample_data):
        """Test that [feature] works correctly."""
        # Arrange
        instance = [Class]()

        # Act
        result = await instance.method(sample_data)

        # Assert
        assert result["status"] == "success"
        assert "data" in result
```

### Frontend Test Template

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Component } from '@/components/Component';

describe('Component', () => {
  beforeEach(() => {
    // Setup
  });

  it('should render correctly', () => {
    render(<Component />);
    expect(screen.getByText('Expected text')).toBeInTheDocument();
  });

  it('should handle user interaction', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<Component onClick={handleClick} />);

    await user.click(screen.getByRole('button'));

    expect(handleClick).toHaveBeenCalled();
  });
});
```

## Troubleshooting

### Backend Tests Failing

**Issue**: `ImportError: No module named 'app'`
```bash
# Solution: Install in development mode
cd backend
pip install -e .
```

**Issue**: Database connection errors
```bash
# Solution: Ensure test database is running
docker-compose up -d postgres redis
```

**Issue**: Anthropic API key errors
```bash
# Solution: Set test API key
export ANTHROPIC_API_KEY=test-key-for-testing
```

### Frontend Tests Failing

**Issue**: `Cannot find module '@/components/...'`
```bash
# Solution: Check vitest.config.ts has correct path aliases
```

**Issue**: `localStorage is not defined`
```bash
# Solution: Mock localStorage in setup.ts
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  // ...
};
```

### E2E Tests Failing

**Issue**: Timeout errors
```bash
# Solution: Increase timeout in playwright.config.ts
timeout: 60000
```

**Issue**: Browser not installed
```bash
# Solution: Install browsers
npx playwright install --with-deps
```

### CI/CD Issues

**Issue**: Tests pass locally but fail in CI
- Check environment variables are set in GitHub Secrets
- Ensure all dependencies are in requirements.txt / package.json
- Review CI logs for specific errors

**Issue**: Deployment fails
- Verify Railway/Vercel tokens are valid
- Check deployment logs in Railway/Vercel dashboard
- Ensure environment variables are configured

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library Documentation](https://testing-library.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Questions?** Open an issue or contact the development team.
