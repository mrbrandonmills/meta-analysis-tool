# Testing Quick Start Guide

**For developers who want to start testing immediately**

---

## 🚀 Fast Start (2 minutes)

```bash
# 1. Install test dependencies
cd backend
pip install -r requirements-test.txt

# 2. Run the example tests
pytest tests/unit/test_agents/test_credibility.py -v

# 3. Check coverage
pytest --cov=app --cov-report=term-missing

# 4. View results
# Tests should pass (or skip if dependencies missing)
# Coverage report shows what's tested
```

---

## 📋 What's Already Built

### ✅ Complete Testing Framework
- Pytest configuration with fixtures
- Mock Anthropic API (no real API calls needed)
- Test database (in-memory SQLite)
- Example tests you can copy
- CI/CD pipeline ready

### ✅ Test Categories Ready
1. **Unit Tests** - Test individual functions/classes
2. **Integration Tests** - Test API endpoints
3. **Validation Tests** - Compare with published research
4. **Performance Tests** - Measure speed
5. **Security Tests** - Check for vulnerabilities

### ✅ Example Tests Created
- `test_credibility.py` - 15+ test cases (copy this pattern!)
- `test_meta_analysis_api.py` - API integration examples
- `test_statistical_accuracy.py` - Validation test structure

---

## ✍️ Write Your First Test

### 1. Copy the Template

```bash
# Copy the example test
cp backend/tests/unit/test_agents/test_credibility.py \
   backend/tests/unit/test_agents/test_search.py

# Edit it for SearchAgent
```

### 2. Simple Test Pattern

```python
# tests/unit/test_agents/test_search.py

import pytest
from app.agents.specialized.search import SearchAgent

class TestSearchAgent:
    """Test suite for SearchAgent."""

    @pytest.mark.asyncio
    async def test_search_pubmed(self, search_agent):
        """Test PubMed search works."""
        result = await search_agent.search_pubmed("cancer therapy")

        # Check it returns results
        assert "results" in result
        assert len(result["results"]) > 0

    @pytest.mark.asyncio
    async def test_handles_invalid_query(self, search_agent):
        """Test error handling for invalid query."""
        result = await search_agent.search_pubmed("")

        # Should handle gracefully
        assert result is not None
```

### 3. Run Your Test

```bash
pytest tests/unit/test_agents/test_search.py -v
```

---

## 🎯 Common Test Patterns

### Pattern 1: Test Agent Processing

```python
@pytest.mark.asyncio
async def test_agent_process(self, my_agent):
    """Test agent processes input correctly."""
    input_data = {"test": "data"}

    result = await my_agent.process(input_data)

    assert result["status"] == "success"
    assert "output" in result
```

### Pattern 2: Test API Endpoint

```python
def test_api_endpoint(self, authenticated_client):
    """Test API endpoint returns correct data."""
    response = authenticated_client.get("/api/v1/endpoint")

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
```

### Pattern 3: Test Error Handling

```python
@pytest.mark.asyncio
async def test_handles_error(self, my_agent):
    """Test agent handles errors gracefully."""
    with pytest.raises(ValueError):
        await my_agent.process({"invalid": True})
```

### Pattern 4: Test With Mock Data

```python
def test_with_sample_data(self, sample_papers):
    """Test using pre-made sample data."""
    assert len(sample_papers) == 10
    result = process_papers(sample_papers)
    assert result is not None
```

---

## 🛠️ Available Fixtures (Use These!)

### Agent Fixtures
```python
search_agent          # SearchAgent instance
screening_agent       # ScreeningAgent instance
credibility_agent     # CredibilityAgent instance
qa_agent             # QAAgent instance
coordinator_agent    # CoordinatorAgent instance
```

### Data Fixtures
```python
sample_paper         # Single test paper
sample_papers        # 10 test papers
sample_researcher    # Researcher profile
sample_manuscript    # Test manuscript
```

### API Fixtures
```python
test_client            # Basic API client
authenticated_client   # Logged-in API client
```

### Database Fixtures
```python
db_session           # Clean database
test_user           # Test user account
sample_meta_analysis # Sample project
```

---

## 🏃 Running Tests

### Quick Commands

```bash
# Fast tests only (for development)
./scripts/quick_test.sh

# Full test suite
./scripts/run_all_tests.sh

# Specific tests
pytest tests/unit                     # Unit tests
pytest tests/integration              # Integration tests
pytest -k "credibility"              # Tests matching name
pytest tests/unit/test_agents/test_credibility.py::test_assess_credibility_high_quality
```

### With Coverage

```bash
# Run with coverage
pytest --cov=app --cov-report=html

# Open in browser (macOS)
open htmlcov/index.html

# See missing lines
pytest --cov=app --cov-report=term-missing
```

### Useful Flags

```bash
-v          # Verbose output
-s          # Show print statements
-x          # Stop on first failure
--pdb       # Drop into debugger on failure
-k "name"   # Run tests matching name
-m "marker" # Run tests with marker
```

---

## 📊 Check Your Progress

### 1. Run Coverage Report

```bash
pytest --cov=app --cov-report=term-missing
```

**Look for:**
- Overall coverage percentage (goal: >80%)
- Which files are tested
- Which lines are missing tests

### 2. Count Your Tests

```bash
pytest --collect-only | grep "test session starts"
```

**Target:** 450+ tests total

### 3. Check Test Speed

```bash
pytest --durations=10
```

**Goal:** Most tests <1 second

---

## 🎓 Learning Resources

### Read These First
1. [Backend Test README](backend/tests/README.md) - How to use the test framework
2. [TESTING_STRATEGY.md](TESTING_STRATEGY.md) - Overall strategy (skim sections 1-3)
3. Example test files - Copy these patterns

### When You Need It
- [TEST_RESULTS_BASELINE.md](TEST_RESULTS_BASELINE.md) - Track your progress
- [TESTING_FRAMEWORK_SUMMARY.md](TESTING_FRAMEWORK_SUMMARY.md) - What's been built
- [Pytest Docs](https://docs.pytest.org/) - Official documentation

---

## 🐛 Common Issues

### "Module not found"
```bash
# Install test dependencies
pip install -r backend/requirements-test.txt
```

### "Anthropic API key error"
```bash
# Tests use mocks - no real API key needed
# If you see this error, the mock isn't working
# Check conftest.py is being loaded
```

### "Database locked"
```bash
# Tests use in-memory SQLite - should never lock
# If you see this, check you're using db_session fixture
```

### Tests are slow
```bash
# Skip slow tests during development
pytest -m "not slow"
```

---

## ✅ Next Steps

### This Week
1. ✅ Install dependencies: `pip install -r requirements-test.txt`
2. ✅ Run example tests: `pytest tests/unit/test_agents/test_credibility.py`
3. ✅ Write tests for SearchAgent (copy credibility test pattern)
4. ✅ Write tests for ScreeningAgent
5. ✅ Write tests for QAAgent
6. ✅ Run coverage report
7. ✅ Update TEST_RESULTS_BASELINE.md with your actual numbers

### This Month
1. Achieve 80% overall coverage
2. Write integration tests for all API endpoints
3. Create validation datasets
4. Run first validation test

### This Quarter
1. 100% critical path coverage
2. Complete validation suite
3. Publish validation results

---

## 💡 Pro Tips

1. **Copy Working Tests** - Start by copying test_credibility.py and modifying it

2. **Use Fixtures** - Don't create test data manually, use the fixtures

3. **Test One Thing** - Each test should check one specific behavior

4. **Write Tests First** - TDD: Write test → Run (fails) → Implement → Run (passes)

5. **Run Tests Often** - Use `./scripts/quick_test.sh` during development

6. **Check Coverage** - After writing tests, check coverage increased

7. **Read Error Messages** - Pytest errors are usually clear about what failed

8. **Use -v Flag** - Verbose mode helps see what's being tested

---

## 🎯 Your Goal

**By end of this week:**
- [ ] 50+ tests written
- [ ] All 5 operational agents have unit tests
- [ ] Coverage >60%
- [ ] All tests passing

**By end of this month:**
- [ ] 200+ tests written
- [ ] Coverage >80%
- [ ] Integration tests for API
- [ ] First validation test passing

---

## 🆘 Get Help

1. **Check the docs:** [backend/tests/README.md](backend/tests/README.md)
2. **Look at examples:** All test files in `tests/unit/test_agents/`
3. **Read the strategy:** [TESTING_STRATEGY.md](TESTING_STRATEGY.md)
4. **Review pytest docs:** https://docs.pytest.org/

---

## 📝 Quick Reference Card

```bash
# INSTALL
pip install -r backend/requirements-test.txt

# RUN TESTS
pytest                                    # All tests
pytest tests/unit                        # Unit tests only
pytest -v                                # Verbose
pytest -k "credibility"                  # Specific tests
pytest --cov=app --cov-report=html      # With coverage

# WRITE TESTS
# 1. Copy tests/unit/test_agents/test_credibility.py
# 2. Rename for your agent
# 3. Update test methods
# 4. Run: pytest tests/unit/test_agents/test_your_agent.py

# CHECK PROGRESS
pytest --cov=app --cov-report=term-missing
open htmlcov/index.html

# USEFUL FLAGS
-v      Verbose
-s      Show prints
-x      Stop on fail
-k      Filter by name
-m      Filter by marker
--pdb   Debug on fail
```

---

**Ready? Start with:** `pytest tests/unit/test_agents/test_credibility.py -v`

**Good luck! 🚀**
