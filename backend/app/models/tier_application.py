"""
Tier Application models for Tier 2 (Reviewer) and Tier 3 (Editor) applications.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON, ARRAY, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class TierApplication(Base):
    """
    Tier application model for Tier 2 (Reviewer) and Tier 3 (Editor) applications.

    Stores all application data including academic credentials, review experience,
    and verification status.
    """

    __tablename__ = "tier_applications"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Application Type
    tier_applied_for = Column(
        SQLEnum(
            "tier_2_reviewer",
            "tier_3_editor",
            name="application_tier_enum"
        ),
        nullable=False,
        index=True
    )

    # Application Status
    status = Column(
        SQLEnum(
            "submitted",
            "auto_verification_in_progress",
            "auto_verification_passed",
            "auto_verification_failed",
            "manual_review_pending",
            "manual_review_in_progress",
            "references_check_in_progress",
            "advisory_board_review",
            "more_info_requested",
            "approved",
            "denied",
            "appealed",
            "appeal_approved",
            "appeal_denied",
            name="application_status_enum"
        ),
        nullable=False,
        default="submitted",
        index=True
    )

    # Academic Credentials (Required for both Tier 2 and Tier 3)
    degree_type = Column(String(50), nullable=False)  # PhD, MD, JD, etc.
    degree_institution = Column(String(255), nullable=False)
    degree_field = Column(String(255), nullable=False)
    degree_year = Column(Integer, nullable=False)

    # ORCID and Google Scholar
    orcid_id = Column(String(19), nullable=False, index=True)  # Format: 0000-0001-2345-6789
    google_scholar_url = Column(Text, nullable=False)

    # Publications (DOIs stored as JSON array)
    publication_dois = Column(ARRAY(Text), nullable=False)

    # Verification Status
    orcid_verified = Column(Boolean, default=False, nullable=False)
    google_scholar_verified = Column(Boolean, default=False, nullable=False)
    auto_verification_passed = Column(Boolean, nullable=True)

    # Verification Results (populated during auto-verification)
    h_index = Column(Integer, nullable=True)
    total_citations = Column(Integer, nullable=True)
    total_publications = Column(Integer, nullable=True)

    # Peer Review Experience (Tier 2 and Tier 3)
    total_reviews_completed = Column(Integer, nullable=False)
    journals_reviewed_for = Column(JSON, nullable=False)  # Array of {journal_name, years, review_count}
    max_concurrent_reviews = Column(Integer, nullable=False)
    preferred_review_timeframe_days = Column(Integer, nullable=False)
    review_languages = Column(ARRAY(String(50)), nullable=False)

    # Research Expertise
    expertise_domains = Column(ARRAY(String(255)), nullable=False)
    expertise_keywords = Column(ARRAY(String(100)), nullable=False)
    research_methodologies = Column(ARRAY(String(255)), nullable=False)

    # Ethics
    conflicts_of_interest_disclosed = Column(Boolean, nullable=False)
    conflict_details = Column(Text, nullable=True)
    research_misconduct_question = Column(Boolean, nullable=False)  # Must be False
    misconduct_details = Column(Text, nullable=True)
    cope_guidelines_accepted = Column(Boolean, nullable=False)  # Must be True

    # Optional - Publons
    publons_profile_url = Column(Text, nullable=True)

    # Tier 3 Specific Fields
    editorial_experience_type = Column(
        SQLEnum(
            "board",
            "recommendations",
            "guest_editor",
            name="editorial_experience_type_enum"
        ),
        nullable=True  # Only required for Tier 3
    )

    # Editorial Board Option
    editorial_board_journal = Column(String(255), nullable=True)
    editorial_board_role = Column(String(255), nullable=True)
    editorial_board_years = Column(String(50), nullable=True)

    # Guest Editor Option
    guest_editor_details = Column(JSON, nullable=True)  # {journal_name, special_issue_title, year, etc.}

    # Tier 3 Essays
    conflict_management_essay = Column(Text, nullable=True)
    editorial_philosophy_essay = Column(Text, nullable=True)

    # Professional References (Tier 3 only)
    professional_references = Column(JSON, nullable=True)  # Array of reference objects

    # Time Commitment (Tier 3 only)
    weekly_hours_available = Column(Integer, nullable=True)

    # File Uploads
    cv_file_path = Column(Text, nullable=True)
    degree_certificate_path = Column(Text, nullable=True)
    recommendation_letters_paths = Column(ARRAY(Text), nullable=True)

    # Decision Information
    approved = Column(Boolean, nullable=True)
    denial_reasons = Column(ARRAY(String(100)), nullable=True)  # Array of DenialReasonEnum values
    denial_explanation = Column(Text, nullable=True)

    # More Info Requested
    requested_info = Column(ARRAY(Text), nullable=True)

    # Probationary Approval
    probationary_approval = Column(Boolean, default=False, nullable=False)
    probation_end_date = Column(DateTime, nullable=True)

    # Appeal
    appeal_submitted = Column(Boolean, default=False, nullable=False)
    appeal_reason = Column(Text, nullable=True)
    appeal_additional_evidence = Column(JSON, nullable=True)
    appeal_submitted_at = Column(DateTime, nullable=True)
    appeal_decided_at = Column(DateTime, nullable=True)
    appeal_denial_explanation = Column(Text, nullable=True)

    # Admin Review
    reviewed_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    appeal_reviewed_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    admin_notes = Column(Text, nullable=True)

    # Reference Checks
    references_contacted_at = Column(DateTime, nullable=True)
    references_responses = Column(JSON, nullable=True)

    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    decision_made_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="tier_applications")
    reviewed_by_admin = relationship("User", foreign_keys=[reviewed_by_admin_id])
    appeal_reviewed_by_admin = relationship("User", foreign_keys=[appeal_reviewed_by_admin_id])
    verification = relationship("QualificationVerification", back_populates="application", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        """String representation."""
        return f"<TierApplication {self.id} - {self.tier_applied_for} - {self.status}>"


class QualificationVerification(Base):
    """
    Stores comprehensive verification results from automatic credential checks.

    Includes ORCID verification, Google Scholar scraping, publication verification,
    and background checks.
    """

    __tablename__ = "qualification_verifications"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key
    application_id = Column(UUID(as_uuid=True), ForeignKey("tier_applications.id"), nullable=False, unique=True, index=True)

    # Verification Status
    verification_completed = Column(Boolean, default=False, nullable=False)
    verification_date = Column(DateTime, nullable=True)
    verification_passed = Column(Boolean, nullable=True)

    # ORCID Verification Results (JSON)
    orcid_data = Column(JSON, nullable=True)
    # Expected structure:
    # {
    #   "verified": bool,
    #   "profile_exists": bool,
    #   "name": str,
    #   "works_count": int,
    #   "has_minimum_data": bool,
    #   "error": str (optional)
    # }

    # Google Scholar Verification Results (JSON)
    google_scholar_data = Column(JSON, nullable=True)
    # Expected structure:
    # {
    #   "verified": bool,
    #   "profile_exists": bool,
    #   "name": str,
    #   "h_index": int,
    #   "i10_index": int,
    #   "total_citations": int,
    #   "publications_count": int,
    #   "has_minimum_data": bool,
    #   "top_publications": [list],
    #   "error": str (optional)
    # }

    # Publication Verification Results (JSON)
    publications_data = Column(JSON, nullable=True)
    # Expected structure:
    # {
    #   "verified_count": int,
    #   "total_count": int,
    #   "publications": [
    #     {
    #       "doi": str,
    #       "verified": bool,
    #       "title": str,
    #       "authors": [list],
    #       "journal": str,
    #       "year": int,
    #       "citations": int,
    #       "is_peer_reviewed": bool,
    #       "error": str (optional)
    #     }
    #   ]
    # }

    # Background Check Results (JSON)
    background_check_data = Column(JSON, nullable=True)
    # Expected structure:
    # {
    #   "ori_check": {"clear": bool, "findings": []},
    #   "retraction_watch_check": {"clear": bool, "retractions": []},
    #   "pubpeer_check": {"clear": bool, "concerns": []},
    #   "overall_clear": bool
    # }

    # Verification Notes
    verification_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    application = relationship("TierApplication", back_populates="verification")

    def __repr__(self):
        """String representation."""
        return f"<QualificationVerification {self.id} - Application {self.application_id} - Passed: {self.verification_passed}>"
