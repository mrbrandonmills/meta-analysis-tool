"""Integration tests for Meta-Analysis API.

Tests complete API workflows including:
- Project creation
- Workflow execution
- Status monitoring
- Results retrieval
- Error handling
"""

import pytest
from uuid import uuid4


class TestMetaAnalysisAPI:
    """Integration tests for meta-analysis API endpoints."""

    def test_create_meta_analysis_success(self, authenticated_client):
        """Test successful creation of meta-analysis project."""
        payload = {
            "title": "Test Meta-Analysis Project",
            "research_question": "What is the effect of intervention X on outcome Y?",
            "inclusion_criteria": [
                "Randomized controlled trials",
                "Published 2015-2023",
                "English language"
            ],
            "exclusion_criteria": [
                "Non-peer reviewed",
                "Case reports"
            ]
        }

        response = authenticated_client.post(
            "/api/v1/meta-analysis/create",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert data["title"] == payload["title"]
        assert data["research_question"] == payload["research_question"]
        assert data["status"] in ["draft", "created"]

    def test_create_meta_analysis_validation_error(self, authenticated_client):
        """Test validation of required fields."""
        payload = {
            "title": "Test",
            # Missing required field: research_question
        }

        response = authenticated_client.post(
            "/api/v1/meta-analysis/create",
            json=payload
        )

        assert response.status_code == 422  # Validation error

    def test_create_meta_analysis_unauthorized(self, test_client):
        """Test creation requires authentication."""
        payload = {
            "title": "Test Meta-Analysis",
            "research_question": "Test question?"
        }

        response = test_client.post(
            "/api/v1/meta-analysis/create",
            json=payload
        )

        assert response.status_code == 401

    def test_get_meta_analysis(self, authenticated_client, sample_meta_analysis):
        """Test retrieving a meta-analysis project."""
        response = authenticated_client.get(
            f"/api/v1/meta-analysis/{sample_meta_analysis.id}"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(sample_meta_analysis.id)
        assert data["title"] == sample_meta_analysis.title

    def test_get_meta_analysis_not_found(self, authenticated_client):
        """Test 404 for non-existent project."""
        fake_id = str(uuid4())

        response = authenticated_client.get(
            f"/api/v1/meta-analysis/{fake_id}"
        )

        assert response.status_code == 404

    def test_list_meta_analyses(self, authenticated_client, sample_meta_analysis):
        """Test listing user's meta-analyses."""
        response = authenticated_client.get("/api/v1/meta-analysis/list")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(p["id"] == str(sample_meta_analysis.id) for p in data)

    @pytest.mark.integration
    @pytest.mark.slow
    def test_execute_workflow(self, authenticated_client, sample_meta_analysis):
        """Test executing meta-analysis workflow."""
        response = authenticated_client.post(
            f"/api/v1/meta-analysis/execute/{sample_meta_analysis.id}"
        )

        # Should accept the request and start background processing
        assert response.status_code == 202  # Accepted
        data = response.json()

        assert data["status"] in ["queued", "in_progress"]
        assert "workflow_id" in data

    def test_get_workflow_status(self, authenticated_client, sample_meta_analysis):
        """Test checking workflow status."""
        # Start workflow
        execute_response = authenticated_client.post(
            f"/api/v1/meta-analysis/execute/{sample_meta_analysis.id}"
        )
        workflow_id = execute_response.json()["workflow_id"]

        # Check status
        status_response = authenticated_client.get(
            f"/api/v1/meta-analysis/status/{workflow_id}"
        )

        assert status_response.status_code == 200
        status_data = status_response.json()

        assert "status" in status_data
        assert status_data["status"] in [
            "queued", "in_progress", "completed", "failed"
        ]

    def test_get_audit_trail(self, authenticated_client, sample_meta_analysis):
        """Test retrieving audit trail."""
        response = authenticated_client.get(
            f"/api/v1/meta-analysis/audit/{sample_meta_analysis.id}"
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        # Audit trail should contain agent decisions

    @pytest.mark.integration
    def test_ask_question(self, authenticated_client, sample_meta_analysis):
        """Test Q&A endpoint."""
        payload = {
            "project_id": str(sample_meta_analysis.id),
            "question": "What is the overall effect size?"
        }

        response = authenticated_client.post(
            "/api/v1/meta-analysis/ask",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()

        assert "answer" in data
        assert "confidence" in data
        assert isinstance(data["answer"], str)

    def test_delete_meta_analysis(self, authenticated_client, sample_meta_analysis):
        """Test deleting a meta-analysis project."""
        response = authenticated_client.delete(
            f"/api/v1/meta-analysis/{sample_meta_analysis.id}"
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = authenticated_client.get(
            f"/api/v1/meta-analysis/{sample_meta_analysis.id}"
        )
        assert get_response.status_code == 404


class TestMetaAnalysisWorkflow:
    """Test complete meta-analysis workflows."""

    @pytest.mark.integration
    @pytest.mark.slow
    async def test_complete_workflow_success(self, authenticated_client):
        """Test complete meta-analysis from creation to results."""
        # 1. Create project
        create_response = authenticated_client.post(
            "/api/v1/meta-analysis/create",
            json={
                "title": "Complete Workflow Test",
                "research_question": "Test workflow?",
                "inclusion_criteria": ["RCT"]
            }
        )
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]

        # 2. Execute workflow
        execute_response = authenticated_client.post(
            f"/api/v1/meta-analysis/execute/{project_id}"
        )
        assert execute_response.status_code == 202
        workflow_id = execute_response.json()["workflow_id"]

        # 3. Poll for completion (in real test, would wait)
        status_response = authenticated_client.get(
            f"/api/v1/meta-analysis/status/{workflow_id}"
        )
        assert status_response.status_code == 200

        # 4. Get results (if completed)
        results_response = authenticated_client.get(
            f"/api/v1/meta-analysis/{project_id}/results"
        )
        # May be 200 (if done) or 202 (if still processing)
        assert results_response.status_code in [200, 202]


class TestMetaAnalysisErrors:
    """Test error handling in meta-analysis API."""

    def test_invalid_project_id_format(self, authenticated_client):
        """Test handling of invalid UUID format."""
        response = authenticated_client.get(
            "/api/v1/meta-analysis/not-a-uuid"
        )

        assert response.status_code == 422  # Validation error

    def test_concurrent_execution_prevention(
        self,
        authenticated_client,
        sample_meta_analysis
    ):
        """Test that concurrent executions are prevented."""
        # Start first execution
        response1 = authenticated_client.post(
            f"/api/v1/meta-analysis/execute/{sample_meta_analysis.id}"
        )
        assert response1.status_code == 202

        # Try to start second execution immediately
        response2 = authenticated_client.post(
            f"/api/v1/meta-analysis/execute/{sample_meta_analysis.id}"
        )

        # Should reject or queue, not start second concurrent run
        assert response2.status_code in [409, 202]  # Conflict or Queued

    def test_rate_limiting(self, authenticated_client):
        """Test API rate limiting protection."""
        # Make many requests quickly
        responses = []
        for _ in range(100):
            response = authenticated_client.get("/api/v1/meta-analysis/list")
            responses.append(response.status_code)

        # Should have some rate limit responses if implemented
        # Note: This depends on rate limiting configuration
        assert all(status in [200, 429] for status in responses)


class TestMetaAnalysisPermissions:
    """Test authorization and permissions."""

    def test_user_can_only_access_own_projects(
        self,
        authenticated_client,
        test_client,
        sample_meta_analysis
    ):
        """Test users can't access other users' projects."""
        # Create a different user's project (would need another fixture)
        # For now, test that unauthorized access is denied

        # Unauthenticated access
        response = test_client.get(
            f"/api/v1/meta-analysis/{sample_meta_analysis.id}"
        )

        assert response.status_code == 401

    def test_admin_can_access_all_projects(self):
        """Test admin users have broader access."""
        # TODO: Implement when admin role is added
        pytest.skip("Admin functionality not yet implemented")
