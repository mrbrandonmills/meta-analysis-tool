"""
Comprehensive integration tests for Tier Application System.

Tests cover:
- Tier 2 (Reviewer) applications
- Tier 3 (Editor) applications
- Admin review workflow
- File uploads
- Authorization and security
- Error handling and edge cases
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.main import app
from app.models.user import User, UserRole
from app.models.tier_application import TierApplication, QualificationVerification
from app.schemas.tier_applications import ApplicationStatusEnum, ApplicationTierEnum


class TestTier2ApplicationFlow:
    """Test complete Tier 2 application workflow."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def tier1_user(self, db_session):
        """Create Tier 1 user for testing."""
        user = User(
            id=uuid4(),
            email=f"tier1_{uuid4()}@example.com",
            first_name="Test",
            last_name="User",
            role=UserRole.USER,
            tier="tier_1_researcher",
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def tier2_application_data(self):
        """Valid Tier 2 application data."""
        return {
            "degree_type": "PhD",
            "degree_institution": "Stanford University",
            "degree_field": "Computer Science",
            "degree_year": 2020,
            "orcid_id": "0000-0001-2345-6789",
            "google_scholar_url": "https://scholar.google.com/citations?user=ABC123",
            "publication_dois": [
                "10.1234/test.001",
                "10.1234/test.002",
                "10.1234/test.003"
            ],
            "total_reviews_completed": 5,
            "journals_reviewed_for": [
                {
                    "journal_name": "Nature",
                    "years": "2021-2024",
                    "review_count": 3
                },
                {
                    "journal_name": "Science",
                    "years": "2022-2024",
                    "review_count": 2
                }
            ],
            "max_concurrent_reviews": 3,
            "preferred_review_timeframe_days": 14,
            "review_languages": ["English", "Spanish"],
            "expertise_domains": ["Machine Learning", "Computer Vision"],
            "expertise_keywords": [
                "deep learning", "neural networks", "image recognition",
                "convolutional networks", "transfer learning", "computer vision",
                "object detection", "semantic segmentation", "image classification",
                "feature extraction"
            ],
            "research_methodologies": [
                "Experimental design",
                "Statistical analysis",
                "Computational modeling"
            ],
            "conflicts_of_interest_disclosed": True,
            "conflict_details": "None",
            "research_misconduct_question": False,
            "misconduct_details": None,
            "cope_guidelines_accepted": True,
            "publons_profile_url": None
        }

    @pytest.mark.integration
    def test_submit_tier_2_application_success(
        self, client, tier1_user, tier2_application_data, auth_token
    ):
        """Test successful Tier 2 application submission."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        with patch('app.api.v1.tier_applications.run_automatic_verification'):
            response = client.post(
                "/api/v1/tier-applications/tier-2/apply",
                json=tier2_application_data
            )

        assert response.status_code == 201
        data = response.json()
        assert "application_id" in data
        assert data["tier_applied_for"] == "tier_2_reviewer"
        assert data["status"] == "submitted"
        assert data["estimated_review_time_days"] == 5

    @pytest.mark.integration
    def test_submit_tier_2_with_misconduct_fails(
        self, client, tier1_user, tier2_application_data, auth_token
    ):
        """Test application rejected if research misconduct disclosed."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        # Set misconduct to True
        tier2_application_data["research_misconduct_question"] = True

        response = client.post(
            "/api/v1/tier-applications/tier-2/apply",
            json=tier2_application_data
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    def test_submit_tier_2_without_cope_acceptance_fails(
        self, client, tier1_user, tier2_application_data, auth_token
    ):
        """Test application rejected if COPE guidelines not accepted."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        tier2_application_data["cope_guidelines_accepted"] = False

        response = client.post(
            "/api/v1/tier-applications/tier-2/apply",
            json=tier2_application_data
        )

        assert response.status_code == 422

    @pytest.mark.integration
    def test_submit_tier_2_with_insufficient_publications(
        self, client, tier1_user, tier2_application_data, auth_token
    ):
        """Test validation fails with less than 3 publications."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        tier2_application_data["publication_dois"] = [
            "10.1234/test.001",
            "10.1234/test.002"
        ]

        response = client.post(
            "/api/v1/tier-applications/tier-2/apply",
            json=tier2_application_data
        )

        assert response.status_code == 422

    @pytest.mark.integration
    def test_submit_tier_2_with_invalid_orcid(
        self, client, tier1_user, tier2_application_data, auth_token
    ):
        """Test validation fails with invalid ORCID format."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        tier2_application_data["orcid_id"] = "invalid-orcid"

        response = client.post(
            "/api/v1/tier-applications/tier-2/apply",
            json=tier2_application_data
        )

        assert response.status_code == 422

    @pytest.mark.integration
    def test_cannot_submit_multiple_pending_applications(
        self, client, tier1_user, tier2_application_data, auth_token, db_session
    ):
        """Test user cannot submit multiple pending Tier 2 applications."""
        # Create existing pending application
        existing_app = TierApplication(
            id=uuid4(),
            user_id=tier1_user.id,
            tier_applied_for=ApplicationTierEnum.TIER_2_REVIEWER,
            status=ApplicationStatusEnum.SUBMITTED,
            **tier2_application_data
        )
        db_session.add(existing_app)
        tier1_user.has_pending_tier_2_application = True
        db_session.commit()

        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        response = client.post(
            "/api/v1/tier-applications/tier-2/apply",
            json=tier2_application_data
        )

        assert response.status_code == 400
        assert "pending" in response.json()["detail"].lower()


class TestTier3ApplicationFlow:
    """Test complete Tier 3 application workflow."""

    @pytest.fixture
    def tier2_user(self, db_session):
        """Create approved Tier 2 user."""
        user = User(
            id=uuid4(),
            email=f"tier2_{uuid4()}@example.com",
            first_name="Senior",
            last_name="Reviewer",
            role=UserRole.USER,
            tier="tier_2_reviewer",
            tier_2_approval_date=datetime.utcnow() - timedelta(days=100),
            total_reviews_completed=10,
            average_review_quality_score=4.5,
            created_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def tier2_application(self, db_session, tier2_user):
        """Create approved Tier 2 application."""
        app = TierApplication(
            id=uuid4(),
            user_id=tier2_user.id,
            tier_applied_for=ApplicationTierEnum.TIER_2_REVIEWER,
            status=ApplicationStatusEnum.APPROVED,
            approved=True,
            degree_type="PhD",
            degree_institution="MIT",
            degree_field="Biology",
            degree_year=2018,
            orcid_id="0000-0002-3456-7890",
            google_scholar_url="https://scholar.google.com/citations?user=XYZ789",
            publication_dois=["10.1234/test.001", "10.1234/test.002", "10.1234/test.003"],
            total_reviews_completed=10,
            journals_reviewed_for=[],
            max_concurrent_reviews=3,
            preferred_review_timeframe_days=14,
            review_languages=["English"],
            expertise_domains=["Biology"],
            expertise_keywords=["cell biology"] * 10,
            research_methodologies=["Experimental", "Statistical", "Computational"],
            conflicts_of_interest_disclosed=True,
            research_misconduct_question=False,
            cope_guidelines_accepted=True,
            created_at=datetime.utcnow()
        )
        db_session.add(app)
        db_session.commit()
        return app

    @pytest.fixture
    def tier3_application_data(self):
        """Valid Tier 3 application data."""
        return {
            "editorial_experience_type": "board",
            "editorial_board_journal": "Nature Reviews",
            "editorial_board_role": "Associate Editor",
            "editorial_board_years": "2020-present",
            "guest_editor_details": None,
            "conflict_management_essay": "A" * 600,  # 600 chars
            "editorial_philosophy_essay": "B" * 700,  # 700 chars
            "professional_references": [
                {
                    "name": "Dr. John Doe",
                    "email": "john.doe@university.edu",
                    "phone": "+1234567890",
                    "institution": "Harvard University",
                    "relationship": "Colleague",
                    "duration_years": 5
                },
                {
                    "name": "Dr. Jane Smith",
                    "email": "jane.smith@university.edu",
                    "phone": "+1234567891",
                    "institution": "Stanford University",
                    "relationship": "Supervisor",
                    "duration_years": 8
                },
                {
                    "name": "Dr. Bob Johnson",
                    "email": "bob.johnson@university.edu",
                    "phone": "+1234567892",
                    "institution": "MIT",
                    "relationship": "Collaborator",
                    "duration_years": 3
                }
            ],
            "weekly_hours_available": 10
        }

    @pytest.mark.integration
    def test_submit_tier_3_application_success(
        self, client, tier2_user, tier2_application, tier3_application_data, auth_token
    ):
        """Test successful Tier 3 application submission."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier2_user)}"

        with patch('app.api.v1.tier_applications.run_enhanced_verification'):
            response = client.post(
                "/api/v1/tier-applications/tier-3/apply",
                json=tier3_application_data
            )

        assert response.status_code == 201
        data = response.json()
        assert data["tier_applied_for"] == "tier_3_editor"
        assert data["estimated_review_time_days"] == 10

    @pytest.mark.integration
    def test_tier_3_requires_tier_2_tenure(
        self, client, tier2_user, tier2_application, tier3_application_data, auth_token, db_session
    ):
        """Test Tier 3 requires 90 days as Tier 2."""
        # Set approval date to less than 90 days ago
        tier2_user.tier_2_approval_date = datetime.utcnow() - timedelta(days=60)
        db_session.commit()

        client.headers["Authorization"] = f"Bearer {auth_token(tier2_user)}"

        response = client.post(
            "/api/v1/tier-applications/tier-3/apply",
            json=tier3_application_data
        )

        assert response.status_code == 400
        assert "90 days" in response.json()["detail"]

    @pytest.mark.integration
    def test_tier_3_requires_minimum_reviews(
        self, client, tier2_user, tier3_application_data, auth_token, db_session
    ):
        """Test Tier 3 requires at least 5 completed reviews."""
        tier2_user.total_reviews_completed = 3
        db_session.commit()

        client.headers["Authorization"] = f"Bearer {auth_token(tier2_user)}"

        response = client.post(
            "/api/v1/tier-applications/tier-3/apply",
            json=tier3_application_data
        )

        assert response.status_code == 400
        assert "5 peer reviews" in response.json()["detail"]

    @pytest.mark.integration
    def test_tier_3_requires_quality_score(
        self, client, tier2_user, tier2_application, tier3_application_data, auth_token, db_session
    ):
        """Test Tier 3 requires review quality >= 4.0."""
        tier2_user.average_review_quality_score = 3.5
        db_session.commit()

        client.headers["Authorization"] = f"Bearer {auth_token(tier2_user)}"

        response = client.post(
            "/api/v1/tier-applications/tier-3/apply",
            json=tier3_application_data
        )

        assert response.status_code == 400
        assert "4.0" in response.json()["detail"]


class TestFileUploadEndpoints:
    """Test file upload functionality."""

    @pytest.fixture
    def application(self, db_session, tier1_user):
        """Create test application."""
        app = TierApplication(
            id=uuid4(),
            user_id=tier1_user.id,
            tier_applied_for=ApplicationTierEnum.TIER_2_REVIEWER,
            status=ApplicationStatusEnum.SUBMITTED,
            # ... minimal required fields
        )
        db_session.add(app)
        db_session.commit()
        return app

    @pytest.mark.integration
    @pytest.mark.security
    def test_upload_cv_validates_file_type(
        self, client, tier1_user, application, auth_token
    ):
        """Test CV upload only accepts PDF."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        # Try uploading non-PDF file
        files = {"file": ("resume.docx", b"fake content", "application/msword")}

        response = client.post(
            f"/api/v1/tier-applications/{application.id}/upload-cv",
            files=files
        )

        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.security
    def test_upload_cv_validates_file_size(
        self, client, tier1_user, application, auth_token
    ):
        """Test CV upload rejects files > 10 MB."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        # Create file > 10 MB
        large_content = b"A" * (11 * 1024 * 1024)
        files = {"file": ("resume.pdf", large_content, "application/pdf")}

        response = client.post(
            f"/api/v1/tier-applications/{application.id}/upload-cv",
            files=files
        )

        assert response.status_code == 400
        assert "10 MB" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.security
    def test_user_cannot_upload_to_others_application(
        self, client, tier1_user, application, auth_token, db_session
    ):
        """Test authorization check on file upload."""
        # Create another user
        other_user = User(
            id=uuid4(),
            email="other@example.com",
            first_name="Other",
            last_name="User",
            role=UserRole.USER,
            tier="tier_1_researcher"
        )
        db_session.add(other_user)
        db_session.commit()

        client.headers["Authorization"] = f"Bearer {auth_token(other_user)}"

        files = {"file": ("resume.pdf", b"content", "application/pdf")}

        response = client.post(
            f"/api/v1/tier-applications/{application.id}/upload-cv",
            files=files
        )

        assert response.status_code == 404


class TestAdminReviewEndpoints:
    """Test admin review workflow."""

    @pytest.fixture
    def admin_user(self, db_session):
        """Create admin user."""
        admin = User(
            id=uuid4(),
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            tier="tier_1_researcher"
        )
        db_session.add(admin)
        db_session.commit()
        return admin

    @pytest.fixture
    def pending_application(self, db_session, tier1_user):
        """Create pending application."""
        app = TierApplication(
            id=uuid4(),
            user_id=tier1_user.id,
            tier_applied_for=ApplicationTierEnum.TIER_2_REVIEWER,
            status=ApplicationStatusEnum.MANUAL_REVIEW_PENDING,
            auto_verification_passed=True,
            h_index=15,
            total_citations=500,
            # ... other required fields
        )
        db_session.add(app)
        db_session.commit()
        return app

    @pytest.mark.integration
    def test_admin_can_view_pending_applications(
        self, client, admin_user, pending_application, auth_token
    ):
        """Test admin can list pending applications."""
        client.headers["Authorization"] = f"Bearer {auth_token(admin_user)}"

        response = client.get("/api/v1/admin/tier-applications/pending")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.integration
    @pytest.mark.security
    def test_non_admin_cannot_access_admin_endpoints(
        self, client, tier1_user, auth_token
    ):
        """Test regular users cannot access admin endpoints."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        response = client.get("/api/v1/admin/tier-applications/pending")

        assert response.status_code == 403

    @pytest.mark.integration
    def test_admin_approve_application(
        self, client, admin_user, pending_application, auth_token, db_session
    ):
        """Test admin can approve application."""
        client.headers["Authorization"] = f"Bearer {auth_token(admin_user)}"

        decision = {
            "action": "APPROVE",
            "admin_notes": "Excellent qualifications"
        }

        with patch('app.api.v1.admin_tier_applications.EmailService'):
            response = client.post(
                f"/api/v1/admin/tier-applications/{pending_application.id}/review",
                json=decision
            )

        assert response.status_code == 200
        data = response.json()
        assert data["decision"] == "APPROVE"

        # Verify application status updated
        db_session.refresh(pending_application)
        assert pending_application.status == ApplicationStatusEnum.APPROVED
        assert pending_application.approved == True

    @pytest.mark.integration
    def test_admin_deny_application_requires_reason(
        self, client, admin_user, pending_application, auth_token
    ):
        """Test denial requires reasons and explanation."""
        client.headers["Authorization"] = f"Bearer {auth_token(admin_user)}"

        decision = {
            "action": "DENY"
            # Missing reasons and explanation
        }

        response = client.post(
            f"/api/v1/admin/tier-applications/{pending_application.id}/review",
            json=decision
        )

        assert response.status_code == 400
        assert "reasons" in response.json()["detail"].lower()

    @pytest.mark.integration
    def test_admin_deny_application_success(
        self, client, admin_user, pending_application, auth_token, db_session
    ):
        """Test admin can deny application with proper reasons."""
        client.headers["Authorization"] = f"Bearer {auth_token(admin_user)}"

        decision = {
            "action": "DENY",
            "reasons": ["insufficient_publications", "h_index_too_low"],
            "explanation": "While the applicant shows promise, they need more publications and higher h-index to qualify for Tier 2."
        }

        with patch('app.api.v1.admin_tier_applications.EmailService'):
            response = client.post(
                f"/api/v1/admin/tier-applications/{pending_application.id}/review",
                json=decision
            )

        assert response.status_code == 200

        # Verify denial recorded
        db_session.refresh(pending_application)
        assert pending_application.status == ApplicationStatusEnum.DENIED
        assert pending_application.approved == False
        assert len(pending_application.denial_reasons) == 2

    @pytest.mark.integration
    def test_admin_request_more_info(
        self, client, admin_user, pending_application, auth_token, db_session
    ):
        """Test admin can request additional information."""
        client.headers["Authorization"] = f"Bearer {auth_token(admin_user)}"

        decision = {
            "action": "REQUEST_MORE_INFO",
            "requested_info": [
                "Please provide verification of editorial board membership",
                "Clarify publication authorship for DOI 10.1234/test.001"
            ]
        }

        with patch('app.api.v1.admin_tier_applications.EmailService'):
            response = client.post(
                f"/api/v1/admin/tier-applications/{pending_application.id}/review",
                json=decision
            )

        assert response.status_code == 200

        db_session.refresh(pending_application)
        assert pending_application.status == ApplicationStatusEnum.MORE_INFO_REQUESTED
        assert len(pending_application.requested_info) == 2


class TestApplicationStatusEndpoints:
    """Test application status checking."""

    @pytest.mark.integration
    def test_user_can_view_own_applications(
        self, client, tier1_user, auth_token, db_session
    ):
        """Test user can list their applications."""
        # Create applications for user
        for i in range(3):
            app = TierApplication(
                id=uuid4(),
                user_id=tier1_user.id,
                tier_applied_for=ApplicationTierEnum.TIER_2_REVIEWER,
                status=ApplicationStatusEnum.SUBMITTED,
                # ... minimal fields
            )
            db_session.add(app)
        db_session.commit()

        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        response = client.get("/api/v1/tier-applications/my-applications")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @pytest.mark.integration
    @pytest.mark.security
    def test_user_cannot_view_others_applications(
        self, client, tier1_user, auth_token, db_session
    ):
        """Test user cannot access another user's application."""
        # Create other user and their application
        other_user = User(
            id=uuid4(),
            email="other@example.com",
            first_name="Other",
            last_name="User",
            role=UserRole.USER
        )
        db_session.add(other_user)

        other_app = TierApplication(
            id=uuid4(),
            user_id=other_user.id,
            tier_applied_for=ApplicationTierEnum.TIER_2_REVIEWER,
            status=ApplicationStatusEnum.SUBMITTED,
            # ... minimal fields
        )
        db_session.add(other_app)
        db_session.commit()

        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        response = client.get(f"/api/v1/tier-applications/{other_app.id}")

        assert response.status_code == 403


class TestAppealWorkflow:
    """Test application appeal process."""

    @pytest.fixture
    def denied_application(self, db_session, tier1_user):
        """Create denied application."""
        app = TierApplication(
            id=uuid4(),
            user_id=tier1_user.id,
            tier_applied_for=ApplicationTierEnum.TIER_2_REVIEWER,
            status=ApplicationStatusEnum.DENIED,
            approved=False,
            denial_reasons=["insufficient_publications"],
            denial_explanation="Need more peer-reviewed publications",
            # ... other required fields
        )
        db_session.add(app)
        db_session.commit()
        return app

    @pytest.mark.integration
    def test_submit_appeal_for_denied_application(
        self, client, tier1_user, denied_application, auth_token, db_session
    ):
        """Test user can submit appeal for denied application."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        appeal_data = {
            "reason": "Since the original application, I have published 3 additional peer-reviewed papers in high-impact journals. I believe these new publications address the denial reason and demonstrate my qualifications for Tier 2 status.",
            "additional_evidence": {
                "new_publications": [
                    "10.1234/new.001",
                    "10.1234/new.002",
                    "10.1234/new.003"
                ]
            }
        }

        with patch('app.api.v1.tier_applications.send_email'):
            response = client.post(
                f"/api/v1/tier-applications/{denied_application.id}/appeal",
                json=appeal_data
            )

        assert response.status_code == 200
        data = response.json()
        assert "appeal" in data["message"].lower()

        db_session.refresh(denied_application)
        assert denied_application.status == ApplicationStatusEnum.APPEALED
        assert denied_application.appeal_submitted == True

    @pytest.mark.integration
    def test_cannot_appeal_approved_application(
        self, client, tier1_user, auth_token, db_session
    ):
        """Test cannot submit appeal for approved application."""
        approved_app = TierApplication(
            id=uuid4(),
            user_id=tier1_user.id,
            tier_applied_for=ApplicationTierEnum.TIER_2_REVIEWER,
            status=ApplicationStatusEnum.APPROVED,
            approved=True,
            # ... fields
        )
        db_session.add(approved_app)
        db_session.commit()

        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        appeal_data = {
            "reason": "This shouldn't work" * 10
        }

        response = client.post(
            f"/api/v1/tier-applications/{approved_app.id}/appeal",
            json=appeal_data
        )

        assert response.status_code == 400
        assert "denied" in response.json()["detail"].lower()

    @pytest.mark.integration
    def test_cannot_submit_duplicate_appeal(
        self, client, tier1_user, denied_application, auth_token, db_session
    ):
        """Test cannot submit multiple appeals for same application."""
        # Mark appeal as already submitted
        denied_application.appeal_submitted = True
        db_session.commit()

        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        appeal_data = {
            "reason": "Second appeal attempt" * 10
        }

        response = client.post(
            f"/api/v1/tier-applications/{denied_application.id}/appeal",
            json=appeal_data
        )

        assert response.status_code == 400
        assert "already submitted" in response.json()["detail"].lower()


class TestSecurityAndAuthorization:
    """Test security controls and authorization."""

    @pytest.mark.integration
    @pytest.mark.security
    def test_unauthenticated_requests_rejected(self, client):
        """Test all endpoints require authentication."""
        endpoints = [
            ("/api/v1/tier-applications/tier-2/apply", "POST"),
            ("/api/v1/tier-applications/my-applications", "GET"),
            ("/api/v1/admin/tier-applications/pending", "GET"),
        ]

        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})

            assert response.status_code in [401, 403], \
                f"Endpoint {endpoint} should require authentication"

    @pytest.mark.integration
    @pytest.mark.security
    def test_sql_injection_protection(self, client, tier1_user, auth_token):
        """Test SQL injection attempts are blocked."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        # Try SQL injection in application ID
        malicious_id = "1'; DROP TABLE tier_applications; --"

        response = client.get(f"/api/v1/tier-applications/{malicious_id}")

        # Should fail with 422 (invalid UUID) not 500 (SQL error)
        assert response.status_code == 422

    @pytest.mark.integration
    @pytest.mark.security
    def test_path_traversal_protection_in_file_upload(
        self, client, tier1_user, auth_token, db_session
    ):
        """Test file upload prevents path traversal attacks."""
        # This is a placeholder - actual implementation would test
        # the save_upload_to_storage function with malicious paths
        pass


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.integration
    def test_application_with_maximum_keywords(
        self, client, tier1_user, tier2_application_data, auth_token
    ):
        """Test application with maximum allowed keywords (30)."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        tier2_application_data["expertise_keywords"] = [f"keyword_{i}" for i in range(30)]

        with patch('app.api.v1.tier_applications.run_automatic_verification'):
            response = client.post(
                "/api/v1/tier-applications/tier-2/apply",
                json=tier2_application_data
            )

        assert response.status_code == 201

    @pytest.mark.integration
    def test_application_with_too_many_keywords_rejected(
        self, client, tier1_user, tier2_application_data, auth_token
    ):
        """Test application with > 30 keywords is rejected."""
        client.headers["Authorization"] = f"Bearer {auth_token(tier1_user)}"

        tier2_application_data["expertise_keywords"] = [f"keyword_{i}" for i in range(31)]

        response = client.post(
            "/api/v1/tier-applications/tier-2/apply",
            json=tier2_application_data
        )

        assert response.status_code == 422

    @pytest.mark.integration
    def test_concurrent_application_submissions(
        self, client, tier1_user, tier2_application_data, auth_token
    ):
        """Test race condition handling for concurrent submissions."""
        # This would require actual concurrent requests
        # Placeholder for now
        pass
