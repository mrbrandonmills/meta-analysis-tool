# Contributing to Tests

Thank you for contributing to the Meta-Analysis Tool testing suite! This guide will help you write effective tests.

## Quick Start

### Setting Up Your Development Environment

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/meta-analysis-tool.git
cd meta-analysis-tool

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
pip install -r requirements-test.txt

# Frontend setup
cd ../frontend
npm install

# E2E tests setup
cd ../tests/e2e
npm install
npx playwright install --with-deps
```

### Before You Start

1. **Read TESTING.md**: Comprehensive testing guide
2. **Check existing tests**: Look for similar test patterns
3. **Create an issue**: Discuss major test additions
4. **Branch naming**: `test/feature-name` or `fix/test-name`

## Writing Tests

### Test-Driven Development (TDD)

We follow TDD practices:

1. **RED**: Write a failing test
2. **GREEN**: Write minimal code to make it pass
3. **REFACTOR**: Improve code while keeping tests green

### Backend Tests (Python/Pytest)

#### Unit Test Template

```python
"""Unit tests for [ComponentName]."""
import pytest
from app.module.component import Component

class TestComponent:
    """Test suite for Component."""

    @pytest.fixture
    def component(self):
        """Create component instance for testing."""
        return Component(config={"setting": "value"})

    def test_component_initialization(self, component):
        """Test that component initializes correctly."""
        assert component is not None
        assert component.setting == "value"

    @pytest.mark.asyncio
    async def test_component_process(self, component):
        """Test component processing logic."""
        # Arrange
        input_data = {"key": "value"}

        # Act
        result = await component.process(input_data)

        # Assert
        assert result is not None
        assert "expected_field" in result

    def test_component_error_handling(self, component):
        """Test component handles errors gracefully."""
        with pytest.raises(ValueError, match="expected error message"):
            component.process_invalid_input(None)
```

#### Integration Test Template

```python
"""Integration tests for [Feature] API."""
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
class TestFeatureAPI:
    """Integration tests for feature endpoints."""

    @pytest.fixture
    def authenticated_client(self, client, test_user, auth_token):
        """Create authenticated client."""
        client.headers["Authorization"] = f"Bearer {auth_token}"
        return client

    def test_create_feature(self, authenticated_client):
        """Test creating a new feature."""
        response = authenticated_client.post(
            "/api/v1/features",
            json={"name": "Test Feature", "data": {...}}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Feature"
        assert "id" in data

    def test_get_feature_requires_auth(self, client):
        """Test that endpoint requires authentication."""
        response = client.get("/api/v1/features/123")
        assert response.status_code == 401
```

### Frontend Tests (TypeScript/Vitest)

#### Component Test Template

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ComponentName } from '@/components/ComponentName';

describe('ComponentName', () => {
  const defaultProps = {
    onSubmit: vi.fn(),
    initialValue: 'test'
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<ComponentName {...defaultProps} />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('handles user interactions', async () => {
    const user = userEvent.setup();
    render(<ComponentName {...defaultProps} />);

    await user.type(screen.getByLabelText(/input/i), 'test input');
    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(defaultProps.onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({ value: 'test input' })
      );
    });
  });

  it('displays error messages', async () => {
    render(<ComponentName {...defaultProps} />);

    await userEvent.click(screen.getByRole('button', { name: /submit/i }));

    expect(screen.getByText(/error message/i)).toBeInTheDocument();
  });
});
```

#### Custom Hook Test Template

```typescript
import { describe, it, expect } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCustomHook } from '@/hooks/useCustomHook';

describe('useCustomHook', () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  it('fetches data successfully', async () => {
    const { result } = renderHook(() => useCustomHook(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toBeDefined();
  });

  it('handles errors', async () => {
    const { result } = renderHook(() => useCustomHook({ shouldFail: true }), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});
```

### E2E Tests (Playwright)

#### E2E Test Template

```typescript
import { test, expect, Page } from '@playwright/test';

test.describe('Feature Workflow', () => {
  let page: Page;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;
    // Login
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard/);
  });

  test('completes feature workflow', async () => {
    // Navigate
    await page.click('text=/create new/i');
    await expect(page).toHaveURL(/create/);

    // Fill form
    await page.fill('input[name="title"]', 'Test Title');
    await page.fill('textarea[name="description"]', 'Test Description');

    // Submit
    await page.click('button[type="submit"]');

    // Verify
    await expect(page.locator('text=/success/i')).toBeVisible({ timeout: 10000 });
    await expect(page).toHaveURL(/dashboard/);
  });

  test('handles errors gracefully', async () => {
    await page.click('text=/create new/i');

    // Submit without filling required fields
    await page.click('button[type="submit"]');

    // Should show validation errors
    await expect(page.locator('text=/required/i')).toBeVisible();
  });
});
```

## Testing Best Practices

### 1. Test Isolation

```python
# Good: Each test is independent
def test_feature_a(self):
    data = create_test_data()
    result = process(data)
    assert result is not None

def test_feature_b(self):
    data = create_test_data()
    result = process(data)
    assert result.status == "success"

# Bad: Tests depend on each other
def test_feature_a(self):
    self.data = create_test_data()
    self.result = process(self.data)

def test_feature_b(self):
    # Depends on test_feature_a running first
    assert self.result.status == "success"
```

### 2. Clear Test Names

```python
# Good: Descriptive names
def test_search_agent_returns_empty_list_when_no_results_found(self):
def test_api_returns_401_when_user_not_authenticated(self):
def test_form_shows_validation_error_for_invalid_email(self):

# Bad: Vague names
def test_search(self):
def test_api(self):
def test_form(self):
```

### 3. Arrange-Act-Assert

```python
def test_screening_agent_filters_studies(self):
    # Arrange - Set up test data
    agent = ScreeningAgent(config)
    studies = [study1, study2, study3]
    criteria = ["RCT studies only"]

    # Act - Execute the code being tested
    result = agent.screen(studies, criteria)

    # Assert - Verify expected outcomes
    assert len(result.included) == 2
    assert len(result.excluded) == 1
    assert result.included[0].study_type == "RCT"
```

### 4. Test One Thing

```python
# Good: One assertion per test
def test_user_email_is_stored_correctly(self):
    user = User(email="test@example.com")
    assert user.email == "test@example.com"

def test_user_name_is_stored_correctly(self):
    user = User(name="John Doe")
    assert user.name == "John Doe"

# Bad: Multiple unrelated assertions
def test_user_creation(self):
    user = User(email="test@example.com", name="John")
    assert user.email == "test@example.com"
    assert user.name == "John"
    assert user.is_active is True
    assert user.created_at is not None
```

### 5. Meaningful Assertions

```python
# Good: Clear, specific assertions
assert result["status"] == "success"
assert len(result["studies"]) == 10
assert result["effect_size"] == pytest.approx(0.45, abs=0.01)

# Bad: Vague assertions
assert result is not None
assert result
assert True
```

## Common Patterns

### Testing Async Code

```python
@pytest.mark.asyncio
async def test_async_operation(self):
    result = await async_function()
    assert result is not None
```

### Testing Exceptions

```python
# Using pytest.raises
def test_raises_value_error(self):
    with pytest.raises(ValueError, match="Invalid input"):
        function_that_raises(invalid_input)

# Using try/except
def test_exception_handling(self):
    try:
        function_that_might_fail()
        pytest.fail("Should have raised exception")
    except ValueError as e:
        assert "expected message" in str(e)
```

### Parameterized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("valid@email.com", True),
    ("invalid-email", False),
    ("another@valid.com", True),
])
def test_email_validation(input, expected):
    assert validate_email(input) == expected
```

### Mocking External Services

```python
def test_with_mocked_api(self, requests_mock):
    requests_mock.get(
        "https://api.example.com/data",
        json={"result": "success"}
    )

    result = fetch_data()
    assert result["result"] == "success"
```

## Code Review Checklist

When reviewing test PRs, check:

- [ ] Tests follow naming conventions
- [ ] Tests are in correct directory (unit/integration/e2e)
- [ ] Tests use appropriate markers (@pytest.mark.unit, etc.)
- [ ] Mocks are used for external dependencies
- [ ] Tests are independent and can run in any order
- [ ] Edge cases are covered
- [ ] Error cases are tested
- [ ] Tests are fast (unit tests < 1s)
- [ ] Coverage meets requirements (80% backend, 60% frontend)
- [ ] Tests pass locally and in CI
- [ ] Documentation is updated if needed

## Debugging Tests

### Backend (Pytest)

```bash
# Run with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_agents/test_search_agent.py::TestSearchAgent::test_search_with_query -v

# Print output
pytest -s

# Drop into debugger on failure
pytest --pdb

# Show local variables
pytest -l
```

### Frontend (Vitest)

```bash
# Run in watch mode
npm test

# Run specific test
npm test -- ComponentName.test.tsx

# Debug mode
npm test -- --inspect-brk
```

### E2E (Playwright)

```bash
# Debug mode (opens browser)
npx playwright test --debug

# Run in headed mode
npx playwright test --headed

# UI mode
npx playwright test --ui

# Generate tests
npx playwright codegen http://localhost:3000
```

## Performance Guidelines

### Test Speed Targets

- **Unit tests**: < 1 second each
- **Integration tests**: < 5 seconds each
- **E2E tests**: < 30 seconds each

### Making Tests Faster

1. Use in-memory databases
2. Mock external services
3. Parallelize test execution
4. Use fixtures efficiently
5. Avoid unnecessary waits

## Common Mistakes to Avoid

1. **Testing implementation details** instead of behavior
2. **Depending on test execution order**
3. **Not cleaning up after tests**
4. **Using real APIs in tests**
5. **Testing third-party libraries**
6. **Skipping tests without good reason**
7. **Not testing error cases**
8. **Making tests too complex**
9. **Hardcoding test data**
10. **Ignoring flaky tests**

## Getting Help

- Check **TESTING.md** for comprehensive guide
- Review existing tests for patterns
- Ask in **#testing** Slack channel
- Tag **@test-experts** in PR for review
- Create issue with **testing** label

## Resources

- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Testing Library Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Martin Fowler on Testing](https://martinfowler.com/testing/)

Thank you for contributing to our test suite! 🎉
