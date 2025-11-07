"""Tests for Health API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check_basic(self, client):
        """Test basic health check endpoint."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_health_check_detailed(self, client):
        """Test detailed health check endpoint."""
        response = client.get("/api/v1/health/detailed")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "services" in data
        assert "database" in data["services"]
        assert "redis" in data["services"]
        assert "anthropic_api" in data["services"]

    @patch("app.db.session.AsyncSession")
    async def test_health_check_database_down(self, mock_session, client):
        """Test health check when database is down."""
        # Mock database connection failure
        mock_session.execute = AsyncMock(side_effect=Exception("Connection failed"))

        response = client.get("/api/v1/health/detailed")

        # Should still return 200 but with degraded/unhealthy status
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["degraded", "unhealthy"]
        assert data["services"]["database"]["status"] == "unhealthy"

    def test_health_check_with_startup_time(self, client):
        """Test health check includes startup time."""
        response = client.get("/api/v1/health/detailed")

        assert response.status_code == 200
        data = response.json()
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0

    def test_root_endpoint(self, client):
        """Test root endpoint returns platform info."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Meta-Analysis Research Platform"
        assert "version" in data
        assert "tools" in data
        assert "documentation" in data
