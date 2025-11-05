"""Pytest configuration and shared fixtures.

This module provides core testing infrastructure including:
- Database fixtures
- Agent fixtures
- API client fixtures
- Mock Anthropic API
- Test data factories
"""

import asyncio
import json
import pytest
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, List
from uuid import uuid4
from datetime import datetime, timedelta

# FastAPI testing
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Database
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Application imports
from app.main import app
from app.core.config import get_settings
from app.agents.base.agent import AgentConfig, BaseAgent
from app.agents.base.types import AgentRole, AgentStatus, AgentDecision

# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "validation: validation tests against gold standards (slow)"
    )
    config.addinivalue_line(
        "markers", "performance: performance and load tests"
    )
    config.addinivalue_line(
        "markers", "integration: integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: slow running tests"
    )
    config.addinivalue_line(
        "markers", "security: security and authentication tests"
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine.

    Uses in-memory SQLite for fast, isolated tests.
    Each test gets a clean database state.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Import all models to ensure tables are created
    from app.models import Base

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Session:
    """Create database session for a test.

    Provides clean database state for each test via transaction rollback.
    """
    connection = db_engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ============================================================================
# API CLIENT FIXTURES
# ============================================================================

@pytest.fixture
def test_client() -> TestClient:
    """Create FastAPI test client."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def authenticated_client(test_client, test_user, auth_token) -> TestClient:
    """Create authenticated test client."""
    test_client.headers["Authorization"] = f"Bearer {auth_token}"
    return test_client


# ============================================================================
# AUTH FIXTURES
# ============================================================================

@pytest.fixture
def test_user(db_session):
    """Create test user."""
    from app.models.user import User

    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        institution="Test University",
        role="researcher",
        created_at=datetime.utcnow()
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


@pytest.fixture
def auth_token(test_user):
    """Create JWT auth token for test user."""
    from app.services.auth_service import AuthService

    auth_service = AuthService()
    token = auth_service.create_access_token(
        user_id=str(test_user.id),
        expires_delta=timedelta(hours=1)
    )

    return token


# ============================================================================
# ANTHROPIC API MOCKING
# ============================================================================

@pytest.fixture
def anthropic_mock_responses() -> Dict[str, Any]:
    """Load mock responses for Anthropic API."""
    mock_file = Path(__file__).parent / "fixtures/mocks/anthropic_responses.json"

    if mock_file.exists():
        with open(mock_file) as f:
            return json.load(f)

    # Default mock responses if file doesn't exist
    return {
        "search_query": {
            "prompt_contains": "search query",
            "response": "((systematic review) OR (meta-analysis)) AND (intervention)"
        },
        "credibility": {
            "prompt_contains": "credibility",
            "response": "HIGH credibility. Randomized controlled trial with robust methodology."
        },
        "screening": {
            "prompt_contains": "screening",
            "response": "INCLUDE. Study meets inclusion criteria."
        },
        "qa": {
            "prompt_contains": "question",
            "response": "Based on the analysis, the effect size is 0.45 (95% CI: 0.32-0.58)."
        }
    }


class MockAnthropicMessage:
    """Mock Anthropic message response."""

    def __init__(self, text: str):
        self.content = [type('Content', (), {'text': text})]
        self.usage = type('Usage', (), {
            'input_tokens': 100,
            'output_tokens': 200
        })


class MockAnthropicClient:
    """Mock Anthropic API client."""

    def __init__(self, api_key: str, responses: Dict[str, Any]):
        self.api_key = api_key
        self.responses = responses
        self.calls = []

    def messages_create(self, **kwargs):
        """Mock messages.create() method."""
        # Log the call for inspection
        self.calls.append(kwargs)

        # Get the prompt
        messages = kwargs.get("messages", [])
        prompt = messages[0].get("content", "") if messages else ""

        # Find matching response
        for key, mock in self.responses.items():
            if mock["prompt_contains"].lower() in prompt.lower():
                return MockAnthropicMessage(mock["response"])

        # Default response
        return MockAnthropicMessage("Mock agent response for testing.")


@pytest.fixture
def mock_anthropic_client(monkeypatch, anthropic_mock_responses):
    """Mock Anthropic API client with smart response matching."""
    mock_clients = []

    def mock_anthropic_init(api_key: str):
        client = MockAnthropicClient(api_key, anthropic_mock_responses)
        mock_clients.append(client)
        return client

    monkeypatch.setattr("anthropic.Anthropic", mock_anthropic_init)

    # Return the list so tests can inspect calls
    return mock_clients


# ============================================================================
# AGENT FIXTURES
# ============================================================================

@pytest.fixture
def base_agent_config() -> AgentConfig:
    """Create base agent configuration."""
    return AgentConfig(
        name="test_agent",
        role=AgentRole.COORDINATOR,
        model="claude-3-5-sonnet-20241022",
        temperature=0.3,
        max_tokens=4096
    )


@pytest.fixture
def search_agent(mock_anthropic_client):
    """Create SearchAgent for testing."""
    from app.agents.specialized.search import SearchAgent

    config = AgentConfig(
        name="test_search",
        role=AgentRole.SEARCH
    )

    return SearchAgent(config)


@pytest.fixture
def screening_agent(mock_anthropic_client):
    """Create ScreeningAgent for testing."""
    from app.agents.specialized.screening import ScreeningAgent

    config = AgentConfig(
        name="test_screening",
        role=AgentRole.SCREENING
    )

    return ScreeningAgent(config)


@pytest.fixture
def credibility_agent(mock_anthropic_client):
    """Create CredibilityAgent for testing."""
    from app.agents.specialized.credibility import CredibilityAgent

    config = AgentConfig(
        name="test_credibility",
        role=AgentRole.CREDIBILITY
    )

    return CredibilityAgent(config)


@pytest.fixture
def qa_agent(mock_anthropic_client):
    """Create QAAgent for testing."""
    from app.agents.specialized.qa import QAAgent

    config = AgentConfig(
        name="test_qa",
        role=AgentRole.QA
    )

    return QAAgent(config)


@pytest.fixture
def coordinator_agent(mock_anthropic_client):
    """Create CoordinatorAgent for testing."""
    from app.agents.specialized.coordinator import CoordinatorAgent

    config = AgentConfig(
        name="test_coordinator",
        role=AgentRole.COORDINATOR
    )

    return CoordinatorAgent(config)


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_paper() -> Dict[str, Any]:
    """Create sample paper for testing."""
    return {
        "id": str(uuid4()),
        "title": "Effect of Intervention X on Outcome Y: A Randomized Controlled Trial",
        "abstract": "Background: This study investigates...\nMethods: Randomized controlled trial with 200 participants...\nResults: Significant improvement was observed...\nConclusion: Intervention X is effective for outcome Y.",
        "authors": ["Smith J", "Johnson A", "Williams B"],
        "journal": "Journal of Medical Research",
        "year": 2023,
        "doi": "10.1234/jmr.2023.001",
        "pmid": "12345678",
        "keywords": ["randomized controlled trial", "intervention", "outcome"],
        "study_type": "RCT",
        "sample_size": 200,
        "peer_reviewed": True
    }


@pytest.fixture
def sample_papers(sample_paper) -> List[Dict[str, Any]]:
    """Create list of sample papers for testing."""
    papers = []

    for i in range(10):
        paper = sample_paper.copy()
        paper["id"] = str(uuid4())
        paper["title"] = f"{paper['title']} - Study {i+1}"
        paper["pmid"] = str(12345678 + i)
        papers.append(paper)

    return papers


@pytest.fixture
def sample_meta_analysis(test_user, db_session):
    """Create sample meta-analysis project."""
    from app.models.project import Project

    project = Project(
        id=uuid4(),
        user_id=test_user.id,
        tool_type="meta_analysis",
        title="Test Meta-Analysis",
        description="Testing meta-analysis workflow",
        status="draft",
        created_at=datetime.utcnow()
    )

    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    return project


@pytest.fixture
def sample_researcher() -> Dict[str, Any]:
    """Create sample researcher profile."""
    return {
        "id": str(uuid4()),
        "orcid": "0000-0001-2345-6789",
        "name": "Dr. Jane Smith",
        "email": "jane.smith@university.edu",
        "institution": "University of Research",
        "department": "Department of Medicine",
        "h_index": 25,
        "i10_index": 40,
        "total_citations": 1500,
        "publication_count": 85,
        "expertise_keywords": ["meta-analysis", "clinical trials", "epidemiology"],
        "research_domains": ["Medicine", "Public Health"]
    }


@pytest.fixture
def sample_manuscript() -> Dict[str, Any]:
    """Create sample manuscript for reviewer matching."""
    return {
        "id": str(uuid4()),
        "title": "Novel Approach to Treatment of Condition X",
        "abstract": "We present a novel treatment approach...",
        "keywords": ["treatment", "clinical trial", "methodology"],
        "submission_date": datetime.utcnow(),
        "journal_id": str(uuid4())
    }


# ============================================================================
# VALIDATION DATA FIXTURES
# ============================================================================

@pytest.fixture
def cochrane_dataset():
    """Load Cochrane review dataset for validation."""
    dataset_file = Path(__file__).parent / "fixtures/papers/meta_analysis_datasets/cochrane_review_1.json"

    if dataset_file.exists():
        with open(dataset_file) as f:
            return json.load(f)

    # Return minimal mock dataset if file doesn't exist
    return {
        "title": "Cochrane Review Test Dataset",
        "inclusion_criteria": ["RCT", "Published 2015-2023"],
        "databases": ["pubmed", "cochrane"],
        "included_studies": [],
        "results": {
            "effect_size": 0.45,
            "ci_lower": 0.32,
            "ci_upper": 0.58,
            "i_squared": 45.2,
            "tau_squared": 0.05
        }
    }


# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def temp_directory(tmp_path):
    """Create temporary directory for test files."""
    return tmp_path


@pytest.fixture
def load_test_file():
    """Helper to load test data files."""
    def _load(filename: str) -> Dict[str, Any]:
        filepath = Path(__file__).parent / "fixtures" / filename
        with open(filepath) as f:
            return json.load(f)
    return _load


# ============================================================================
# PERFORMANCE TESTING FIXTURES
# ============================================================================

@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, *args):
            self.end_time = time.time()

        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

        @property
        def elapsed_ms(self):
            if self.elapsed:
                return self.elapsed * 1000
            return None

    return Timer


# ============================================================================
# CLEANUP
# ============================================================================

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    # Add any singleton reset logic here
    yield
    # Cleanup after test


# ============================================================================
# TEST HELPERS
# ============================================================================

class TestHelpers:
    """Helper methods for tests."""

    @staticmethod
    def assert_agent_decision_valid(decision: AgentDecision):
        """Assert agent decision has valid structure."""
        assert decision.id is not None
        assert decision.agent_id is not None
        assert decision.role is not None
        assert decision.action is not None
        assert 0 <= decision.confidence <= 1
        assert decision.reasoning is not None
        assert decision.timestamp is not None

    @staticmethod
    def assert_api_response_valid(response, expected_status: int = 200):
        """Assert API response is valid."""
        assert response.status_code == expected_status

        if expected_status == 200:
            data = response.json()
            assert data is not None
            return data


@pytest.fixture
def helpers():
    """Provide test helper methods."""
    return TestHelpers
