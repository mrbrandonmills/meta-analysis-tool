# Testing Quick Reference

Quick reference for running tests in the Meta-Analysis Research Platform.

## Quick Commands

### Backend Tests

```bash
# Run all tests
cd backend && pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Unit tests only
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# Fast parallel execution
pytest -n auto

# Stop on first failure
pytest -x

# Run specific test
pytest tests/unit/test_api/test_health_api.py::TestHealthEndpoints::test_health_check_basic -v

# Rerun failed tests
pytest --lf

# Show test durations
pytest --durations=10

# Generate HTML coverage report
pytest --cov=app --cov-report=html && open htmlcov/index.html
```

### Frontend Tests

```bash
# Run all tests
cd frontend && npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm test -- --watch

# UI mode (interactive)
npm run test:ui

# Run specific test file
npm test -- api-client.test.ts

# Update snapshots
npm test -- -u

# Open coverage report
npm run test:coverage && open coverage/index.html
```

### E2E Tests

```bash
cd tests/e2e

# Run all E2E tests
npx playwright test

# Run specific browser
npx playwright test --project=chromium

# Run in headed mode (see browser)
npx playwright test --headed

# Debug mode
npx playwright test --debug

# Run specific test
npx playwright test auth.spec.ts

# Show test report
npx playwright show-report
```

### Code Quality

```bash
# Backend
cd backend
black app tests                    # Format code
black --check app tests            # Check formatting
isort app tests                    # Sort imports
flake8 app tests                   # Lint code
mypy app                           # Type check
bandit -r app -ll                  # Security scan

# Frontend
cd frontend
npm run lint                       # ESLint
npx tsc --noEmit                  # Type check
npx prettier --write "src/**/*.{ts,tsx}"  # Format
```

## Test Structure

### Backend Test Locations

```
backend/tests/
├── unit/                    # Fast, isolated tests
│   ├── test_agents/        # Agent tests
│   ├── test_api/           # API unit tests
│   └── test_models/        # Model tests
├── integration/             # Tests with dependencies
│   ├── test_api/           # API integration
│   └── test_workflows/     # Workflow tests
└── validation/              # Gold standard tests
```

### Frontend Test Locations

```
frontend/tests/
├── components/              # Component tests
├── unit/                    # Unit tests
├── integration/             # Integration tests
└── e2e/                     # E2E tests (Playwright)
```

## Writing Tests

### Backend Test Template

```python
import pytest

class TestFeature:
    @pytest.mark.asyncio
    async def test_feature_works(self):
        # Arrange
        data = {"key": "value"}

        # Act
        result = await function_to_test(data)

        # Assert
        assert result["status"] == "success"
```

### Frontend Test Template

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

describe('Component', () => {
  it('renders correctly', () => {
    render(<Component />);
    expect(screen.getByText('Expected')).toBeInTheDocument();
  });
});
```

## CI/CD Workflows

### Workflow Status

Check status at: `https://github.com/YOUR_USERNAME/meta-analysis-tool/actions`

### Workflows

1. **Backend CI/CD** - Tests + Deploy to Railway
2. **Frontend CI/CD** - Tests + Deploy to Vercel
3. **E2E Tests** - Cross-browser testing
4. **Security** - Security scans

### Triggering Workflows

```bash
# Automatic triggers:
git push origin main          # Deploy to production
git push origin develop       # Deploy to staging
git push origin feature/*     # Run tests only

# Manual trigger:
# Go to Actions tab > Select workflow > Run workflow
```

## Coverage Requirements

- **Backend**: 80% minimum (enforced)
- **Frontend**: 80% target
- **Critical paths**: 90%+

## Common Issues

### Backend

**Import errors**
```bash
cd backend
pip install -e .
```

**Database errors**
```bash
docker-compose up -d postgres redis
```

### Frontend

**Module not found**
```bash
cd frontend
npm install
```

**TypeScript errors**
```bash
npx tsc --noEmit
```

### E2E

**Browser not installed**
```bash
npx playwright install --with-deps
```

## Pre-Commit Checklist

- [ ] Tests pass locally
- [ ] Coverage meets threshold
- [ ] Code formatted
- [ ] Linting passes
- [ ] Type checking passes
- [ ] No console.log statements

## Debugging Tests

### Backend

```bash
# Run with verbose output
pytest -vv

# Show local variables
pytest -l

# Drop into debugger on failure
pytest --pdb

# Print output
pytest -s
```

### Frontend

```bash
# Debug specific test
npm test -- --run api-client.test.ts

# UI mode for debugging
npm run test:ui
```

## Performance

### Backend

```bash
# Show slowest tests
pytest --durations=10

# Profile tests
pytest --profile

# Run in parallel
pytest -n auto
```

### Frontend

```bash
# Run specific test fast
npm test -- --run specific.test.ts

# No coverage for speed
npm test -- --no-coverage
```

## Resources

- Full guide: [TESTING_GUIDE.md](./TESTING_GUIDE.md)
- Summary: [TEST_IMPLEMENTATION_SUMMARY.md](./TEST_IMPLEMENTATION_SUMMARY.md)
- Contributing: [CONTRIBUTING_TESTS.md](./CONTRIBUTING_TESTS.md)

## Getting Help

1. Check documentation
2. Run tests with `-vv` flag
3. Check CI logs
4. Open GitHub issue

---

**Quick Start**: `cd backend && pytest` or `cd frontend && npm test`
