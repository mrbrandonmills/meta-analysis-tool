"""Integration tests for complete meta-analysis workflow."""
import pytest
import asyncio
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


class TestCompleteMetaAnalysisWorkflow:
    """Test complete meta-analysis workflow end-to-end."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def authenticated_client(self, client):
        """Create authenticated test client."""
        # Register and login
        email = f"workflow_{uuid4()}@example.com"
        password = "WorkflowTest123!"

        client.post("/api/v1/auth/register", json={
            "email": email,
            "password": password,
            "name": "Workflow Test",
            "institution": "Test University"
        })

        login_response = client.post("/api/v1/auth/login", json={
            "email": email,
            "password": password
        })

        token_data = login_response.json()
        token = token_data.get("access_token") or token_data.get("token")

        # Add token to client headers
        client.headers["Authorization"] = f"Bearer {token}"
        return client

    @pytest.mark.integration
    @pytest.mark.slow
    def test_create_meta_analysis(self, authenticated_client):
        """Test creating a meta-analysis project."""
        request_data = {
            "research_question": "What is the effect of exercise on depression in adults?",
            "topic": "Exercise and Depression",
            "inclusion_criteria": [
                "Randomized controlled trials",
                "Adult participants (18-65 years)",
                "Exercise intervention"
            ],
            "exclusion_criteria": [
                "Animal studies",
                "Pediatric populations"
            ],
            "databases": ["pubmed"]
        }

        response = authenticated_client.post(
            "/api/v1/meta-analysis/create",
            json=request_data
        )

        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert "status" in data or "workflow" in data

        return data["id"]

    @pytest.mark.integration
    @pytest.mark.slow
    def test_execute_meta_analysis(self, authenticated_client):
        """Test executing a meta-analysis workflow."""
        # First create
        create_data = {
            "research_question": "Effect of meditation on anxiety",
            "topic": "Meditation and Anxiety",
            "inclusion_criteria": ["RCT studies"],
            "exclusion_criteria": ["Animal studies"],
            "databases": ["pubmed"]
        }

        create_response = authenticated_client.post(
            "/api/v1/meta-analysis/create",
            json=create_data
        )

        assert create_response.status_code in [200, 201]
        analysis_id = create_response.json()["id"]

        # Then execute
        execute_response = authenticated_client.post(
            f"/api/v1/meta-analysis/execute/{analysis_id}"
        )

        # Execution might take time, so accept 202 (Accepted) or 200
        assert execute_response.status_code in [200, 202]

    @pytest.mark.integration
    @pytest.mark.slow
    def test_ask_question_about_analysis(self, authenticated_client):
        """Test asking questions about a meta-analysis."""
        # Create and execute first
        create_data = {
            "research_question": "Clinical trial outcomes",
            "topic": "Test Topic",
            "databases": ["pubmed"]
        }

        create_response = authenticated_client.post(
            "/api/v1/meta-analysis/create",
            json=create_data
        )

        analysis_id = create_response.json()["id"]

        # Ask question
        question_data = {
            "question": "What is the effect size?",
            "meta_analysis_id": analysis_id
        }

        response = authenticated_client.post(
            "/api/v1/meta-analysis/ask",
            json=question_data
        )

        # Should accept the question even if analysis not complete
        assert response.status_code in [200, 404]

    @pytest.mark.integration
    def test_list_user_analyses(self, authenticated_client):
        """Test listing user's meta-analyses."""
        # Create a couple analyses
        for i in range(2):
            authenticated_client.post(
                "/api/v1/meta-analysis/create",
                json={
                    "research_question": f"Question {i}",
                    "topic": f"Topic {i}",
                    "databases": ["pubmed"]
                }
            )

        # List analyses
        response = authenticated_client.get("/api/v1/meta-analysis/list")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "items" in data

    @pytest.mark.integration
    def test_get_analysis_details(self, authenticated_client):
        """Test retrieving specific analysis details."""
        # Create analysis
        create_response = authenticated_client.post(
            "/api/v1/meta-analysis/create",
            json={
                "research_question": "Test question",
                "topic": "Test topic",
                "databases": ["pubmed"]
            }
        )

        analysis_id = create_response.json()["id"]

        # Get details
        response = authenticated_client.get(
            f"/api/v1/meta-analysis/{analysis_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == analysis_id

    @pytest.mark.integration
    def test_delete_analysis(self, authenticated_client):
        """Test deleting a meta-analysis."""
        # Create analysis
        create_response = authenticated_client.post(
            "/api/v1/meta-analysis/create",
            json={
                "research_question": "To be deleted",
                "topic": "Delete test",
                "databases": ["pubmed"]
            }
        )

        analysis_id = create_response.json()["id"]

        # Delete
        delete_response = authenticated_client.delete(
            f"/api/v1/meta-analysis/{analysis_id}"
        )

        assert delete_response.status_code in [200, 204]

        # Verify deleted
        get_response = authenticated_client.get(
            f"/api/v1/meta-analysis/{analysis_id}"
        )
        assert get_response.status_code == 404

    @pytest.mark.integration
    @pytest.mark.slow
    def test_workflow_with_multiple_databases(self, authenticated_client):
        """Test workflow with multiple database searches."""
        request_data = {
            "research_question": "Multi-database search test",
            "topic": "Test",
            "databases": ["pubmed", "arxiv", "core"],
            "inclusion_criteria": ["Recent studies"],
            "exclusion_criteria": []
        }

        response = authenticated_client.post(
            "/api/v1/meta-analysis/create",
            json=request_data
        )

        assert response.status_code in [200, 201]

    @pytest.mark.integration
    def test_workflow_with_peer_review_filter(self, authenticated_client):
        """Test workflow with peer review filter."""
        request_data = {
            "research_question": "Peer-reviewed only",
            "topic": "Test",
            "databases": ["pubmed"],
            "peer_review_only": True
        }

        response = authenticated_client.post(
            "/api/v1/meta-analysis/create",
            json=request_data
        )

        assert response.status_code in [200, 201]

    @pytest.mark.integration
    def test_concurrent_analysis_creation(self, authenticated_client):
        """Test creating multiple analyses concurrently."""
        import concurrent.futures

        def create_analysis(i):
            return authenticated_client.post(
                "/api/v1/meta-analysis/create",
                json={
                    "research_question": f"Concurrent test {i}",
                    "topic": f"Topic {i}",
                    "databases": ["pubmed"]
                }
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(create_analysis, i) for i in range(3)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(r.status_code in [200, 201] for r in results)


class TestWorkflowErrorHandling:
    """Test error handling in workflows."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.mark.integration
    def test_create_with_invalid_data(self, client):
        """Test creating analysis with invalid data."""
        invalid_data = {
            "research_question": "",  # Empty
            "topic": ""
        }

        response = client.post(
            "/api/v1/meta-analysis/create",
            json=invalid_data
        )

        assert response.status_code in [400, 422]

    @pytest.mark.integration
    def test_execute_nonexistent_analysis(self, client):
        """Test executing non-existent analysis."""
        fake_id = str(uuid4())

        response = client.post(
            f"/api/v1/meta-analysis/execute/{fake_id}"
        )

        assert response.status_code == 404

    @pytest.mark.integration
    def test_access_other_user_analysis(self, client):
        """Test that users can't access other users' analyses."""
        # Create two users
        user1_email = f"user1_{uuid4()}@example.com"
        user2_email = f"user2_{uuid4()}@example.com"

        # Register both
        for email in [user1_email, user2_email]:
            client.post("/api/v1/auth/register", json={
                "email": email,
                "password": "Password123!",
                "name": "Test User",
                "institution": "Test"
            })

        # User 1 creates analysis
        login1 = client.post("/api/v1/auth/login", json={
            "email": user1_email,
            "password": "Password123!"
        })
        token1 = login1.json().get("access_token")

        client.headers["Authorization"] = f"Bearer {token1}"
        create_response = client.post(
            "/api/v1/meta-analysis/create",
            json={
                "research_question": "User 1 analysis",
                "topic": "Private",
                "databases": ["pubmed"]
            }
        )
        analysis_id = create_response.json()["id"]

        # User 2 tries to access
        login2 = client.post("/api/v1/auth/login", json={
            "email": user2_email,
            "password": "Password123!"
        })
        token2 = login2.json().get("access_token")

        client.headers["Authorization"] = f"Bearer {token2}"
        access_response = client.get(
            f"/api/v1/meta-analysis/{analysis_id}"
        )

        # Should be forbidden
        assert access_response.status_code in [403, 404]


class TestWorkflowPerformance:
    """Test workflow performance characteristics."""

    @pytest.mark.integration
    @pytest.mark.performance
    def test_analysis_creation_time(self, authenticated_client):
        """Test that analysis creation completes in reasonable time."""
        import time

        start = time.time()

        response = authenticated_client.post(
            "/api/v1/meta-analysis/create",
            json={
                "research_question": "Performance test",
                "topic": "Test",
                "databases": ["pubmed"]
            }
        )

        duration = time.time() - start

        assert response.status_code in [200, 201]
        # Should create within 5 seconds
        assert duration < 5.0

    @pytest.mark.integration
    @pytest.mark.performance
    def test_list_analyses_performance(self, authenticated_client):
        """Test listing analyses performance with many items."""
        import time

        # Create multiple analyses
        for i in range(10):
            authenticated_client.post(
                "/api/v1/meta-analysis/create",
                json={
                    "research_question": f"Item {i}",
                    "topic": f"Topic {i}",
                    "databases": ["pubmed"]
                }
            )

        # Time the list operation
        start = time.time()
        response = authenticated_client.get("/api/v1/meta-analysis/list")
        duration = time.time() - start

        assert response.status_code == 200
        # Should list within 2 seconds even with many items
        assert duration < 2.0
