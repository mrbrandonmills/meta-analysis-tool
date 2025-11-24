"""
Pydantic schemas for tier applications (Tier 2 Reviewer and Tier 3 Editor).
"""

from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID
from enum import Enum


# ===========================
# ENUMS
# ===========================

class ApplicationTierEnum(str, Enum):
    TIER_2_REVIEWER = "tier_2_reviewer"
    TIER_3_EDITOR = "tier_3_editor"


class ApplicationStatusEnum(str, Enum):
    SUBMITTED = "submitted"
    AUTO_VERIFICATION_IN_PROGRESS = "auto_verification_in_progress"
    AUTO_VERIFICATION_PASSED = "auto_verification_passed"
    AUTO_VERIFICATION_FAILED = "auto_verification_failed"
    MANUAL_REVIEW_PENDING = "manual_review_pending"
    MANUAL_REVIEW_IN_PROGRESS = "manual_review_in_progress"
    REFERENCES_CHECK_IN_PROGRESS = "references_check_in_progress"
    ADVISORY_BOARD_REVIEW = "advisory_board_review"
    MORE_INFO_REQUESTED = "more_info_requested"
    APPROVED = "approved"
    DENIED = "denied"
    APPEALED = "appealed"
    APPEAL_APPROVED = "appeal_approved"
    APPEAL_DENIED = "appeal_denied"


class DenialReasonEnum(str, Enum):
    INSUFFICIENT_PUBLICATIONS = "insufficient_publications"
    DEGREE_NOT_VERIFIED = "degree_not_verified"
    H_INDEX_TOO_LOW = "h_index_too_low"
    INSUFFICIENT_REVIEW_EXPERIENCE = "insufficient_review_experience"
    NO_EDITORIAL_EXPERIENCE = "no_editorial_experience"
    ETHICAL_CONCERNS = "ethical_concerns"
    RESEARCH_MISCONDUCT_FOUND = "research_misconduct_found"
    WEAK_REFERENCES = "weak_references"
    INCOMPLETE_APPLICATION = "incomplete_application"
    OTHER = "other"


class EditorialExperienceTypeEnum(str, Enum):
    EDITORIAL_BOARD = "board"
    RECOMMENDATION_LETTERS = "recommendations"
    GUEST_EDITOR = "guest_editor"


# ===========================
# NESTED SCHEMAS
# ===========================

class JournalReviewedFor(BaseModel):
    """Journal and review experience details"""
    journal_name: str = Field(..., min_length=2, max_length=255)
    years: str = Field(..., example="2022-2024", description="Years reviewed for this journal")
    review_count: int = Field(..., ge=1, description="Number of reviews completed")


class RecommendationLetter(BaseModel):
    """Letter of recommendation details"""
    recommender_name: str = Field(..., min_length=2)
    recommender_institution: str
    recommender_email: EmailStr
    recommender_role: str = Field(..., description="e.g., Editor-in-Chief, Associate Editor")
    received_date: Optional[datetime] = None
    file_path: Optional[str] = None


class ProfessionalReference(BaseModel):
    """Professional reference contact information"""
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    institution: str
    relationship: str = Field(..., description="How you know this person (e.g., colleague, supervisor)")
    duration_years: int = Field(..., ge=2, description="How many years you've known them")


class PublicationDOI(BaseModel):
    """Publication DOI for verification"""
    doi: str = Field(..., description="Digital Object Identifier")
    title: Optional[str] = None
    year: Optional[int] = None


class GuestEditorExperience(BaseModel):
    """Guest editor experience details"""
    journal_name: str
    special_issue_title: str
    year: int
    manuscripts_handled: int = Field(..., ge=5, description="Number of manuscripts you managed")
    issue_published: bool
    verification_url: Optional[HttpUrl] = None


# ===========================
# TIER 2 APPLICATION SCHEMAS
# ===========================

class Tier2ApplicationCreate(BaseModel):
    """Application for Tier 2 (Peer Reviewer) access"""

    # Academic Credentials
    degree_type: str = Field(..., example="PhD", description="Terminal degree type (PhD, MD, JD, etc.)")
    degree_institution: str = Field(..., min_length=2, max_length=255)
    degree_field: str = Field(..., description="Field of study")
    degree_year: int = Field(..., ge=1950, le=2025, description="Year degree was awarded")

    # ORCID
    orcid_id: str = Field(..., pattern=r'^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$', example="0000-0001-2345-6789")

    # Google Scholar
    google_scholar_url: HttpUrl = Field(..., description="Public Google Scholar profile URL")

    # Publications
    publication_dois: List[str] = Field(
        ...,
        min_items=3,
        description="DOIs for your 3 best peer-reviewed publications"
    )

    # Peer Review Experience
    total_reviews_completed: int = Field(..., ge=3, description="Total peer reviews completed in career")
    journals_reviewed_for: List[JournalReviewedFor] = Field(
        ...,
        min_items=2,
        description="Journals you have reviewed for"
    )
    max_concurrent_reviews: int = Field(..., ge=1, le=5, description="Max reviews you can handle at once")
    preferred_review_timeframe_days: int = Field(
        ...,
        description="Preferred days to complete a review",
        example=14
    )
    review_languages: List[str] = Field(..., min_items=1, description="Languages you can review in")

    # Research Expertise
    expertise_domains: List[str] = Field(..., min_items=1, max_items=5, description="Research domains")
    expertise_keywords: List[str] = Field(
        ...,
        min_items=10,
        max_items=30,
        description="Specific research keywords"
    )
    research_methodologies: List[str] = Field(..., min_items=3, description="Research methods")

    # Ethics
    conflicts_of_interest_disclosed: bool = Field(
        ...,
        description="Have you disclosed all potential conflicts of interest?"
    )
    conflict_details: Optional[str] = Field(None, max_length=2000)
    research_misconduct_question: bool = Field(
        ...,
        description="Have you EVER been found responsible for research misconduct? (True = Yes)"
    )
    misconduct_details: Optional[str] = Field(None, max_length=2000)
    cope_guidelines_accepted: bool = Field(..., description="Do you accept COPE guidelines?")

    # Optional: Publons profile for faster verification
    publons_profile_url: Optional[HttpUrl] = None

    @validator("research_misconduct_question")
    def validate_no_misconduct(cls, v):
        """Automatic rejection if research misconduct found"""
        if v is True:
            raise ValueError(
                "Applications cannot be accepted from individuals found responsible for research misconduct. "
                "If you believe this is an error, please contact support."
            )
        return v

    @validator("cope_guidelines_accepted")
    def validate_cope_acceptance(cls, v):
        """Must accept COPE guidelines"""
        if not v:
            raise ValueError("You must accept COPE (Committee on Publication Ethics) guidelines to proceed")
        return v


class Tier2ApplicationResponse(BaseModel):
    """Response after submitting Tier 2 application"""
    application_id: UUID
    user_id: UUID
    tier_applied_for: ApplicationTierEnum
    status: ApplicationStatusEnum
    submitted_at: datetime
    estimated_review_time_days: int = Field(default=5, description="Estimated days until decision")

    class Config:
        orm_mode = True


# ===========================
# TIER 3 APPLICATION SCHEMAS
# ===========================

class Tier3ApplicationCreate(BaseModel):
    """Application for Tier 3 (Editor) access"""

    # All Tier 2 fields are pre-filled from existing Tier 2 application
    # Only need to provide additional Tier 3-specific requirements

    # Enhanced qualifications (will be auto-verified)
    # h_index and publications are fetched from Google Scholar

    # Editorial Experience (CHOOSE ONE)
    editorial_experience_type: EditorialExperienceTypeEnum

    # Option 1: Editorial Board Membership
    editorial_board_journal: Optional[str] = None
    editorial_board_role: Optional[str] = None
    editorial_board_years: Optional[str] = None  # e.g., "2020-present"

    # Option 2: Recommendation Letters (uploaded separately via file upload endpoint)
    # recommendation_letters: List[RecommendationLetter] - handled via separate endpoint

    # Option 3: Guest Editor Experience
    guest_editor_details: Optional[GuestEditorExperience] = None

    # Essays (500-1000 words each)
    conflict_management_essay: str = Field(
        ...,
        min_length=500,
        max_length=1000,
        description="Describe your approach to managing conflicts of interest in peer review"
    )
    editorial_philosophy_essay: str = Field(
        ...,
        min_length=500,
        max_length=1000,
        description="What is your philosophy on peer review and editorial decision-making?"
    )

    # Professional References (3 required)
    professional_references: List[ProfessionalReference] = Field(
        ...,
        min_items=3,
        max_items=3,
        description="Three professional references who can attest to your qualifications"
    )

    # Time Commitment
    weekly_hours_available: int = Field(
        ...,
        ge=5,
        description="Hours per week you can commit to editorial duties"
    )

    @validator("editorial_board_journal")
    def validate_editorial_board(cls, v, values):
        """If choosing editorial board, must provide details"""
        if values.get("editorial_experience_type") == EditorialExperienceTypeEnum.EDITORIAL_BOARD:
            if not v:
                raise ValueError("Editorial board journal name is required when choosing this option")
        return v

    @validator("guest_editor_details")
    def validate_guest_editor(cls, v, values):
        """If choosing guest editor, must provide details"""
        if values.get("editorial_experience_type") == EditorialExperienceTypeEnum.GUEST_EDITOR:
            if not v:
                raise ValueError("Guest editor details are required when choosing this option")
        return v


class Tier3ApplicationResponse(BaseModel):
    """Response after submitting Tier 3 application"""
    application_id: UUID
    user_id: UUID
    tier_applied_for: ApplicationTierEnum
    status: ApplicationStatusEnum
    submitted_at: datetime
    estimated_review_time_days: int = Field(default=10, description="Estimated days until decision")

    class Config:
        orm_mode = True


# ===========================
# APPLICATION STATUS SCHEMAS
# ===========================

class ApplicationStatusResponse(BaseModel):
    """Current status of an application"""
    application_id: UUID
    status: ApplicationStatusEnum
    submitted_at: datetime
    estimated_decision_date: Optional[datetime] = None
    days_in_review: int
    current_step: str
    total_steps: int
    can_appeal: bool

    # If auto-verification completed
    auto_verification_completed: bool = False
    auto_verification_passed: Optional[bool] = None

    # If denied
    denial_reasons: Optional[List[str]] = None
    denial_explanation: Optional[str] = None


class ApplicationDetailResponse(BaseModel):
    """Detailed application information"""
    application_id: UUID
    user_id: UUID
    tier_applied_for: ApplicationTierEnum
    status: ApplicationStatusEnum

    # Academic credentials
    degree_type: Optional[str]
    degree_institution: Optional[str]
    degree_field: Optional[str]
    degree_year: Optional[int]

    # Verification results
    orcid_verified: bool = False
    google_scholar_verified: bool = False
    h_index: Optional[int] = None
    total_citations: Optional[int] = None
    total_publications: Optional[int] = None

    # Dates
    submitted_at: datetime
    decision_made_at: Optional[datetime] = None

    # Decision
    approved: Optional[bool] = None
    denial_reasons: Optional[List[str]] = None

    # Appeal
    appeal_submitted: bool = False
    appeal_decided_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ===========================
# APPEAL SCHEMAS
# ===========================

class AppealSubmission(BaseModel):
    """Submit an appeal for denied application"""
    reason: str = Field(..., min_length=100, max_length=2000, description="Reason for appeal")
    additional_evidence: Optional[Dict] = Field(
        None,
        description="Any additional evidence or documents to support your appeal"
    )


class AppealResponse(BaseModel):
    """Response after submitting appeal"""
    message: str
    application_id: UUID
    expected_response_time_days: int


# ===========================
# ADMIN REVIEW SCHEMAS
# ===========================

class AdminReviewDecision(BaseModel):
    """Admin decision on application"""
    action: str = Field(
        ...,
        pattern="^(APPROVE|DENY|REQUEST_MORE_INFO|PROBATIONARY_APPROVE)$",
        description="Decision action"
    )
    reasons: Optional[List[DenialReasonEnum]] = None
    explanation: Optional[str] = Field(None, max_length=2000, description="Detailed explanation")
    requested_info: Optional[List[str]] = Field(None, description="If requesting more info, what is needed?")
    admin_notes: Optional[str] = Field(None, max_length=5000, description="Internal admin notes")


class ReviewDecisionResponse(BaseModel):
    """Response after admin review"""
    application_id: UUID
    decision: str
    message: str


class TierApplicationSummary(BaseModel):
    """Summary for admin dashboard"""
    application_id: UUID
    applicant_name: str
    applicant_email: EmailStr
    tier_applied_for: ApplicationTierEnum
    status: ApplicationStatusEnum
    submitted_at: datetime
    days_pending: int
    auto_verification_passed: Optional[bool] = None
    h_index: Optional[int] = None
    total_publications: Optional[int] = None

    class Config:
        orm_mode = True


# ===========================
# FILE UPLOAD SCHEMAS
# ===========================

class UploadResponse(BaseModel):
    """Response after uploading a file"""
    file_path: str
    message: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class RecommendationLetterUpload(BaseModel):
    """Upload recommendation letter"""
    recommender_name: str
    recommender_email: EmailStr
    recommender_institution: str
    file_path: str  # Path to uploaded PDF


# ===========================
# VERIFICATION RESULT SCHEMAS
# ===========================

class ORCIDVerificationResult(BaseModel):
    """Result of ORCID verification"""
    verified: bool
    profile_exists: bool
    name: Optional[str] = None
    works_count: Optional[int] = None
    has_minimum_data: bool = False
    error: Optional[str] = None


class GoogleScholarVerificationResult(BaseModel):
    """Result of Google Scholar verification"""
    verified: bool
    profile_exists: bool
    name: Optional[str] = None
    h_index: Optional[int] = None
    total_citations: Optional[int] = None
    publications_count: Optional[int] = None
    has_minimum_data: bool = False
    error: Optional[str] = None


class ComprehensiveVerificationResult(BaseModel):
    """Complete verification result"""
    verification_passed: bool
    orcid_result: ORCIDVerificationResult
    google_scholar_result: GoogleScholarVerificationResult
    publications_verified: int
    background_checks_clear: bool
    verification_date: datetime
