# Testing Guide for Meta-Analysis Tool Backend

## Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest tests/unit                    # Fast unit tests
pytest tests/integration             # Integration tests
pytest tests/validation -m validation # Validation tests (slow)
```

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── pytest.ini                  # Pytest settings
│
├── unit/                       # Unit tests (fast, isolated)
│   ├── test_agents/           # Agent tests
│   ├── test_utils/            # Utility function tests
│   └── test_services/         # Service layer tests
│
├── integration/               # Integration tests
│   ├── test_api/             # API endpoint tests
│   ├── test_database/        # Database integration
│   └── test_workflows/       # Multi-agent workflows
│
├── validation/               # Validation against gold standards
│   ├── test_meta_analysis/  # Meta-analysis accuracy
│   ├── test_reviewer_matcher/
│   ├── test_peer_review/
│   └── test_research_direction/
│
├── performance/              # Performance benchmarks
├── security/                 # Security tests
│
└── fixtures/                 # Test data
    ├── papers/
    ├── researchers/
    ├── manuscripts/
    └── mocks/
```

## Running Tests

### Basic Usage

```bash
# All tests
pytest

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run specific file
pytest tests/unit/test_agents/test_credibility.py

# Run specific test
pytest tests/unit/test_agents/test_credibility.py::test_assess_credibility_high_quality
```

### Test Selection

```bash
# By marker
pytest -m unit              # Only unit tests
pytest -m integration       # Only integration tests
pytest -m validation        # Only validation tests
pytest -m "not slow"        # Skip slow tests

# By keyword
pytest -k "credibility"     # Tests matching "credibility"
pytest -k "agent and not slow"
```

### Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Open report in browser
open htmlcov/index.html

# Coverage with missing lines
pytest --cov=app --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80
```

### Performance

```bash
# Show slowest tests
pytest --durations=10

# Performance benchmarks
pytest tests/performance -m performance
```

## Writing Tests

### Unit Test Example

```python
# tests/unit/test_agents/test_my_agent.py

import pytest
from app.agents.specialized.my_agent import MyAgent

class TestMyAgent:
    """Test suite for MyAgent."""

    @pytest.mark.asyncio
    async def test_process_success(self, my_agent):
        \"\"\"Test successful processing.\"\"\"
        result = await my_agent.process({"input": "test"})

        assert result["status"] == "success"
        assert "output" in result

    @pytest.mark.asyncio
    async def test_handles_error(self, my_agent):
        \"\"\"Test error handling.\"\"\"
        with pytest.raises(ValueError):
            await my_agent.process({"invalid": True})
```

### Integration Test Example

```python
# tests/integration/test_api/test_my_endpoint.py

def test_create_resource(authenticated_client):
    \"\"\"Test creating a resource via API.\"\"\"
    response = authenticated_client.post(
        "/api/v1/resources",
        json={"name": "Test Resource"}
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
```

### Validation Test Example

```python
# tests/validation/test_accuracy.py

@pytest.mark.validation
@pytest.mark.slow
async def test_replicate_published_study():
    \"\"\"Validate against published research.\"\"\"
    result = await run_meta_analysis(known_dataset)

    # Must match within 5%
    assert abs(result.effect_size - 0.45) < 0.05
```

## Fixtures

### Available Fixtures

```python
# Database
db_session              # Clean database session
test_user              # Test user
sample_meta_analysis   # Sample project

# API
test_client            # FastAPI test client
authenticated_client   # Authenticated client

# Agents
search_agent          # SearchAgent instance
screening_agent       # ScreeningAgent instance
credibility_agent     # CredibilityAgent instance
qa_agent             # QAAgent instance
coordinator_agent    # CoordinatorAgent instance

# Test Data
sample_paper         # Single paper
sample_papers        # List of papers
sample_researcher    # Researcher profile
sample_manuscript    # Test manuscript

# Mocks
mock_anthropic_client  # Mock Claude API
```

### Creating Custom Fixtures

```python
# In your test file or conftest.py

@pytest.fixture
def my_custom_fixture():
    \"\"\"Create custom test data.\"\"\"
    data = setup_test_data()
    yield data
    cleanup_test_data(data)
```

## Test Data

### Using Sample Data

```python
def test_with_sample_papers(sample_papers):
    \"\"\"Test uses pre-defined sample papers.\"\"\"
    assert len(sample_papers) == 10
    assert all("title" in p for p in sample_papers)
```

### Loading Fixture Files

```python
def test_with_fixture_file(load_test_file):
    \"\"\"Load data from fixture file.\"\"\"
    data = load_test_file("papers/sample_papers.json")
    assert len(data) > 0
```

## Mocking

### Mocking Anthropic API

```python
# Automatic mocking via fixture
def test_with_mock(mock_anthropic_client, search_agent):
    \"\"\"Test with mocked API.\"\"\"
    result = await search_agent.search("test query")

    # Mock returns predefined response
    assert "search results" in result
```

### Custom Mocking

```python
def test_with_custom_mock(monkeypatch):
    \"\"\"Test with custom mock.\"\"\"
    def mock_function(*args, **kwargs):
        return "mocked result"

    monkeypatch.setattr("app.services.some_function", mock_function)
```

## Common Issues

### Issue: Tests fail with "Database locked"

```bash
# Solution: Use in-memory database
# Already configured in conftest.py
pytest  # Should work
```

### Issue: Anthropic API key error

```bash
# Solution: Mock is automatic, but if needed:
export ANTHROPIC_API_KEY="test_key"
pytest
```

### Issue: Tests are slow

```bash
# Skip slow tests
pytest -m "not slow"

# Run in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

### Issue: Flaky tests

```bash
# Run test multiple times
pytest --count=10 tests/unit/test_flaky.py

# Identify flaky tests
pytest --lf  # Run last failed
```

## CI/CD

Tests run automatically on:
- Every push to `develop` or `main`
- Every pull request
- See `.github/workflows/test.yml`

### Required Checks

Before merge, must pass:
- ✅ All unit tests
- ✅ All integration tests
- ✅ Coverage ≥ 80%
- ✅ No security vulnerabilities
- ✅ Linting and formatting

## Best Practices

### DO ✅

- Write tests before fixing bugs (TDD)
- Use descriptive test names
- Test one thing per test
- Use fixtures for common setup
- Mock external dependencies
- Document expected behavior
- Test edge cases
- Keep tests fast (<1s each)

### DON'T ❌

- Test implementation details
- Write flaky tests
- Skip cleanup
- Use sleep() for timing
- Commit commented-out tests
- Leave print() statements
- Ignore test failures

## Performance Tips

1. **Use pytest-xdist for parallel execution**
   ```bash
   pip install pytest-xdist
   pytest -n auto
   ```

2. **Skip slow tests during development**
   ```bash
   pytest -m "not slow and not validation"
   ```

3. **Use pytest-benchmark for profiling**
   ```bash
   pytest --benchmark-only
   ```

## Debugging Tests

```bash
# Print output
pytest -s

# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb

# Show local variables on failure
pytest -l

# Verbose output
pytest -vv
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Strategy](../../TESTING_STRATEGY.md)
- [Test Results Baseline](../../TEST_RESULTS_BASELINE.md)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Questions?

See the main [TESTING_STRATEGY.md](../../TESTING_STRATEGY.md) or ask the team.
