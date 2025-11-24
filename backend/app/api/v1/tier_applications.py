"""
Tier Application API Endpoints
Handles Tier 2 (Reviewer) and Tier 3 (Editor) applications.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.db.session import get_async_db
from app.core.security import get_current_user, require_admin
from app.models.user import User, UserRole
from app.models.tier_applications import (
    TierApplication,
    ApplicationTier,
    ApplicationStatus,
    SubscriptionTier
)
from app.models.subscription import Subscription
from app.schemas.tier_applications import *
from app.services.credential_verification import auto_verify_application
from app.services.email_service import send_email
from app.core.logging_config import logger
import os
import shutil
from pathlib import Path

router = APIRouter(prefix="/tier-applications", tags=["tier-applications"])


# ===========================
# HELPER FUNCTIONS
# ===========================

async def save_upload_to_storage(file: UploadFile, subdirectory: str) -> str:
    """
    Save uploaded file to storage and return path.

    Args:
        file: The uploaded file
        subdirectory: Subdirectory within uploads (e.g., "cv", "degree_certificates")

    Returns:
        Relative path to saved file
    """
    # Create uploads directory if it doesn't exist
    upload_dir = Path(f"uploads/{subdirectory}")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = upload_dir / filename

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return str(file_path)


async def run_automatic_verification(application_id: UUID, db: AsyncSession):
    """
    Background task to run automatic verification for Tier 2 application.
    """
    try:
        application = await db.get(TierApplication, application_id)
        if not application:
            logger.error(f"Application {application_id} not found for verification")
            return

        # Update status
        application.status = ApplicationStatus.AUTO_VERIFICATION_IN_PROGRESS
        await db.commit()

        # Run verification
        verification_passed, results = await auto_verify_application(
            orcid_id=application.orcid_id,
            google_scholar_url=application.google_scholar_url,
            publication_dois=application.publication_dois or [],
            researcher_name=application.user.full_name
        )

        # Store results
        application.orcid_verified = results.get("results", {}).get("orcid", {}).get("verified", False)
        application.orcid_verification_date = datetime.utcnow()
        application.orcid_data = results.get("results", {}).get("orcid")

        application.google_scholar_verified = results.get("results", {}).get("google_scholar", {}).get("verified", False)
        application.google_scholar_verification_date = datetime.utcnow()
        application.google_scholar_data = results.get("results", {}).get("google_scholar")

        # Extract h-index and citations
        gs_data = results.get("results", {}).get("google_scholar", {}).get("data", {})
        application.h_index = gs_data.get("h_index", 0)
        application.total_citations = gs_data.get("total_citations", 0)

        # Background checks
        application.ori_check_performed = True
        application.ori_check_date = datetime.utcnow()
        application.ori_findings = results.get("results", {}).get("ori", {}).get("findings")

        application.retraction_watch_check_performed = True
        application.retraction_watch_findings = results.get("results", {}).get("retraction_watch")

        application.pubpeer_check_performed = True
        application.pubpeer_findings = results.get("results", {}).get("pubpeer")

        # Update status based on results
        application.auto_verification_completed_at = datetime.utcnow()

        if verification_passed:
            application.status = ApplicationStatus.AUTO_VERIFICATION_PASSED
            application.manual_review_pending = True  # Flag for admin review queue

            # Send success email
            user = await db.get(User, application.user_id)
            await send_email(
                to=user.email,
                subject="Application Verification Complete - Under Review",
                template="auto_verification_passed.html",
                context={
                    "user": user,
                    "application": application,
                    "h_index": application.h_index,
                    "citations": application.total_citations
                }
            )
        else:
            application.status = ApplicationStatus.AUTO_VERIFICATION_FAILED

            # Determine which check failed
            failed_checks = []
            if not results.get("results", {}).get("orcid", {}).get("verified"):
                failed_checks.append("ORCID profile could not be verified")
            if not results.get("results", {}).get("google_scholar", {}).get("verified"):
                failed_checks.append("Google Scholar profile could not be verified")
            if not results.get("results", {}).get("orcid", {}).get("has_minimum_data"):
                failed_checks.append("ORCID profile does not have minimum required data (3+ publications)")
            if not results.get("results", {}).get("google_scholar", {}).get("has_minimum_data"):
                failed_checks.append("Google Scholar profile does not meet minimum requirements")

            # Auto-deny if automatic verification failed
            application.approved = False
            application.status = ApplicationStatus.DENIED
            application.denial_reasons = ["INSUFFICIENT_PUBLICATIONS", "DEGREE_NOT_VERIFIED"]
            application.denial_explanation = f"Automatic verification failed: {', '.join(failed_checks)}"
            application.decision_made_at = datetime.utcnow()

            # Send denial email
            user = await db.get(User, application.user_id)
            await send_email(
                to=user.email,
                subject="Application Decision - Verification Failed",
                template="auto_verification_failed.html",
                context={
                    "user": user,
                    "application": application,
                    "failed_checks": failed_checks
                }
            )

        await db.commit()
        logger.info(f"Automatic verification complete for application {application_id}: {'PASSED' if verification_passed else 'FAILED'}")

    except Exception as e:
        logger.error(f"Error in automatic verification for {application_id}: {e}")


async def run_enhanced_verification(application_id: UUID, db: AsyncSession):
    """
    Background task for enhanced verification for Tier 3 application.
    """
    # Similar to run_automatic_verification but with additional checks
    await run_automatic_verification(application_id, db)

    # TODO: Add additional Tier 3 specific checks
    # - Verify h-index meets minimum (10+)
    # - Verify editorial board membership if applicable
    # - Validate recommendation letters


def get_status_timeline(application: TierApplication) -> Dict:
    """Calculate current step and estimated completion date."""
    status_steps = {
        ApplicationStatus.SUBMITTED: (1, 8),
        ApplicationStatus.AUTO_VERIFICATION_IN_PROGRESS: (2, 8),
        ApplicationStatus.AUTO_VERIFICATION_PASSED: (3, 8),
        ApplicationStatus.MANUAL_REVIEW_PENDING: (4, 8),
        ApplicationStatus.MANUAL_REVIEW_IN_PROGRESS: (5, 8),
        ApplicationStatus.REFERENCES_CHECK_IN_PROGRESS: (6, 8),  # Tier 3 only
        ApplicationStatus.ADVISORY_BOARD_REVIEW: (7, 8),  # Tier 3 only
        ApplicationStatus.APPROVED: (8, 8),
        ApplicationStatus.DENIED: (8, 8),
    }

    current_step, total_steps = status_steps.get(application.status, (1, 8))

    # Estimate decision date
    days_pending = (datetime.utcnow() - application.submitted_at).days
    if application.tier_applied_for == ApplicationTier.TIER_2_REVIEWER:
        total_expected_days = 5
    else:
        total_expected_days = 10

    days_remaining = max(0, total_expected_days - days_pending)
    estimated_decision_date = datetime.utcnow() + timedelta(days=days_remaining)

    return {
        "current_step": current_step,
        "total_steps": total_steps,
        "estimated_decision_date": estimated_decision_date
    }


# ===========================
# TIER 2 APPLICATION ENDPOINTS
# ===========================

@router.post("/tier-2/apply", response_model=Tier2ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_tier_2(
    application_data: Tier2ApplicationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Submit Tier 2 (Peer Reviewer) application.

    **Requirements:**
    - User must be at least Tier 1 (Researcher)
    - No pending applications
    - Complete all required fields
    - Must have uploaded CV and degree certificate (separate endpoints)

    **Automatic Verification:**
    - ORCID profile verification
    - Google Scholar profile verification
    - Publication DOI validation
    - Background checks (ORI, Retraction Watch, PubPeer)

    **Review Process:**
    - Auto-verification: 1-24 hours
    - Manual admin review: 2-5 business days
    - Total estimated time: 3-7 days
    """
    # Check eligibility
    if current_user.has_pending_tier_2_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending Tier 2 application"
        )

    if current_user.current_tier == SubscriptionTier.TIER_2_REVIEWER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a Tier 2 reviewer"
        )

    # Create application
    application = TierApplication(
        user_id=current_user.id,
        tier_applied_for=ApplicationTier.TIER_2_REVIEWER,
        status=ApplicationStatus.SUBMITTED,
        **application_data.dict()
    )
    db.add(application)

    # Mark user as having pending application
    current_user.has_pending_tier_2_application = True

    await db.commit()
    await db.refresh(application)

    logger.info(f"Tier 2 application submitted by {current_user.email} (ID: {application.id})")

    # Trigger automatic verification (background task)
    background_tasks.add_task(run_automatic_verification, application.id, db)

    # Send confirmation email
    background_tasks.add_task(
        send_email,
        to=current_user.email,
        subject="Tier 2 Application Received - Verification in Progress",
        template="tier_2_application_submitted.html",
        context={"user": current_user, "application": application}
    )

    return Tier2ApplicationResponse(
        application_id=application.id,
        user_id=application.user_id,
        tier_applied_for=application.tier_applied_for,
        status=application.status,
        submitted_at=application.submitted_at,
        estimated_review_time_days=5
    )


@router.post("/tier-3/apply", response_model=Tier3ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_tier_3(
    application_data: Tier3ApplicationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Submit Tier 3 (Editor) application.

    **Requirements:**
    - User must be approved Tier 2 reviewer
    - Active Tier 2 subscription for at least 3 months
    - Completed at least 5 reviews with avg quality ≥ 4.0
    - No pending Tier 3 applications
    - H-index ≥ 10 (verified via Google Scholar)
    - Editorial experience OR 2 letters of recommendation

    **Review Process:**
    - Enhanced auto-verification: 1-24 hours
    - Senior admin review: 5-7 business days
    - Reference checks: 2-3 days
    - Academic advisory board (if needed): 3-5 days
    - Total estimated time: 7-14 days
    """
    # Check eligibility
    if current_user.current_tier != SubscriptionTier.TIER_2_REVIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be an approved Tier 2 reviewer to apply for Tier 3"
        )

    if current_user.has_pending_tier_3_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending Tier 3 application"
        )

    # Check subscription duration
    if not current_user.tier_2_approval_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tier 2 approval date not found"
        )

    tier_2_duration = (datetime.utcnow() - current_user.tier_2_approval_date).days
    if tier_2_duration < 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Must be Tier 2 for at least 90 days. Current: {tier_2_duration} days"
        )

    # Check review performance
    if current_user.total_reviews_completed < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Must have completed at least 5 peer reviews. Current: {current_user.total_reviews_completed}"
        )

    if current_user.average_review_quality_score and current_user.average_review_quality_score < 4.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Average review quality must be ≥ 4.0. Current: {current_user.average_review_quality_score:.2f}"
        )

    # Get existing Tier 2 application to pull data
    result = await db.execute(
        select(TierApplication)
        .where(TierApplication.user_id == current_user.id)
        .where(TierApplication.tier_applied_for == ApplicationTier.TIER_2_REVIEWER)
        .where(TierApplication.approved == True)
    )
    tier_2_app = result.scalar_one_or_none()

    if not tier_2_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not find your approved Tier 2 application"
        )

    # Create Tier 3 application (inherits Tier 2 data)
    application = TierApplication(
        user_id=current_user.id,
        tier_applied_for=ApplicationTier.TIER_3_EDITOR,
        status=ApplicationStatus.SUBMITTED,

        # Inherit from Tier 2
        degree_type=tier_2_app.degree_type,
        degree_institution=tier_2_app.degree_institution,
        degree_field=tier_2_app.degree_field,
        degree_year=tier_2_app.degree_year,
        orcid_id=tier_2_app.orcid_id,
        google_scholar_url=tier_2_app.google_scholar_url,
        publication_dois=tier_2_app.publication_dois,
        total_reviews_completed=tier_2_app.total_reviews_completed,
        journals_reviewed_for=tier_2_app.journals_reviewed_for,
        expertise_domains=tier_2_app.expertise_domains,
        expertise_keywords=tier_2_app.expertise_keywords,
        research_methodologies=tier_2_app.research_methodologies,

        # Add Tier 3 specific data
        **application_data.dict()
    )
    db.add(application)

    # Mark user as having pending application
    current_user.has_pending_tier_3_application = True

    await db.commit()
    await db.refresh(application)

    logger.info(f"Tier 3 application submitted by {current_user.email} (ID: {application.id})")

    # Trigger enhanced verification (background task)
    background_tasks.add_task(run_enhanced_verification, application.id, db)

    # Send confirmation email
    background_tasks.add_task(
        send_email,
        to=current_user.email,
        subject="Tier 3 Application Received - Enhanced Verification in Progress",
        template="tier_3_application_submitted.html",
        context={"user": current_user, "application": application}
    )

    return Tier3ApplicationResponse(
        application_id=application.id,
        user_id=application.user_id,
        tier_applied_for=application.tier_applied_for,
        status=application.status,
        submitted_at=application.submitted_at,
        estimated_review_time_days=10
    )


# ===========================
# FILE UPLOAD ENDPOINTS
# ===========================

@router.post("/{application_id}/upload-cv", response_model=UploadResponse)
async def upload_cv(
    application_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Upload CV/Resume for application.

    **Requirements:**
    - PDF format only
    - Maximum file size: 10 MB
    - Must include education, employment, publications
    """
    application = await db.get(TierApplication, application_id)

    if not application or application.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")

    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > 10 * 1024 * 1024:  # 10 MB
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size must be less than 10 MB")

    # Save file
    file_path = await save_upload_to_storage(file, f"cv/{application_id}")

    # Update application
    application.cv_resume_path = file_path
    await db.commit()

    logger.info(f"CV uploaded for application {application_id}: {file_path}")

    return UploadResponse(
        file_path=file_path,
        message="CV uploaded successfully"
    )


@router.post("/{application_id}/upload-degree", response_model=UploadResponse)
async def upload_degree_certificate(
    application_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Upload degree certificate/diploma for application.

    **Requirements:**
    - PDF, JPG, or PNG format
    - Maximum file size: 5 MB
    - Must be legible scan or photo
    """
    application = await db.get(TierApplication, application_id)

    if not application or application.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    # Validate file
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, JPG, or PNG files are allowed"
        )

    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > 5 * 1024 * 1024:  # 5 MB
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size must be less than 5 MB")

    # Save file
    file_path = await save_upload_to_storage(file, f"degree_certificates/{application_id}")

    # Update application
    application.degree_certificate_path = file_path
    await db.commit()

    logger.info(f"Degree certificate uploaded for application {application_id}: {file_path}")

    return UploadResponse(
        file_path=file_path,
        message="Degree certificate uploaded successfully"
    )


@router.post("/{application_id}/upload-recommendation-letter", response_model=UploadResponse)
async def upload_recommendation_letter(
    application_id: UUID,
    recommender_name: str,
    recommender_email: EmailStr,
    recommender_institution: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Upload letter of recommendation for Tier 3 application.

    **Requirements:**
    - Tier 3 applications only
    - PDF format on official letterhead
    - Signed and dated within last 6 months
    - 2 letters required
    """
    application = await db.get(TierApplication, application_id)

    if not application or application.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if application.tier_applied_for != ApplicationTier.TIER_3_EDITOR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation letters only required for Tier 3 applications"
        )

    # Validate file
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")

    # Save file
    file_path = await save_upload_to_storage(file, f"recommendation_letters/{application_id}")

    # Add to application's recommendation_letters JSON field
    if not application.recommendation_letters:
        application.recommendation_letters = []

    application.recommendation_letters.append({
        "recommender_name": recommender_name,
        "recommender_email": recommender_email,
        "recommender_institution": recommender_institution,
        "file_path": file_path,
        "uploaded_at": datetime.utcnow().isoformat()
    })

    await db.commit()

    logger.info(f"Recommendation letter uploaded for application {application_id} from {recommender_name}")

    return UploadResponse(
        file_path=file_path,
        message=f"Recommendation letter from {recommender_name} uploaded successfully"
    )


# ===========================
# APPLICATION STATUS ENDPOINTS
# ===========================

@router.get("/my-applications", response_model=List[ApplicationDetailResponse])
async def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all applications for current user."""
    result = await db.execute(
        select(TierApplication)
        .where(TierApplication.user_id == current_user.id)
        .order_by(TierApplication.created_at.desc())
    )
    applications = result.scalars().all()
    return applications


@router.get("/{application_id}", response_model=ApplicationDetailResponse)
async def get_application_details(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get detailed information about a specific application.

    Users can only view their own applications (unless admin).
    """
    application = await db.get(TierApplication, application_id)

    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    # Users can only view their own applications (unless admin)
    if application.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this application")

    return application


@router.get("/status/{application_id}", response_model=ApplicationStatusResponse)
async def check_application_status(
    application_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Check the current status of an application with estimated completion time.
    """
    application = await db.get(TierApplication, application_id)

    if not application or application.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    # Calculate timeline
    timeline = get_status_timeline(application)

    return ApplicationStatusResponse(
        application_id=application_id,
        status=application.status,
        submitted_at=application.submitted_at,
        estimated_decision_date=timeline["estimated_decision_date"],
        days_in_review=(datetime.utcnow() - application.submitted_at).days,
        current_step=timeline["current_step"],
        total_steps=timeline["total_steps"],
        can_appeal=(application.status == ApplicationStatus.DENIED and not application.appeal_submitted),
        auto_verification_completed=bool(application.auto_verification_completed_at),
        auto_verification_passed=(
            application.status == ApplicationStatus.AUTO_VERIFICATION_PASSED
            if application.auto_verification_completed_at else None
        ),
        denial_reasons=application.denial_reasons,
        denial_explanation=application.denial_explanation
    )


# ===========================
# APPEAL ENDPOINTS
# ===========================

@router.post("/{application_id}/appeal", response_model=AppealResponse)
async def submit_appeal(
    application_id: UUID,
    appeal_data: AppealSubmission,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Submit an appeal for a denied application.

    **Requirements:**
    - Application must be denied
    - Cannot already have pending appeal
    - Must provide detailed reason and any additional evidence

    **Appeal Process:**
    - Tier 2: Reviewed by senior admin (7 days)
    - Tier 3: Reviewed by Academic Advisory Board (10 days)
    """
    application = await db.get(TierApplication, application_id)

    if not application or application.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if application.status != ApplicationStatus.DENIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only appeal denied applications"
        )

    if application.appeal_submitted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appeal already submitted for this application"
        )

    # Update application with appeal
    application.appeal_submitted = True
    application.appeal_submitted_at = datetime.utcnow()
    application.appeal_reason = appeal_data.reason
    application.appeal_additional_evidence = appeal_data.additional_evidence
    application.status = ApplicationStatus.APPEALED

    await db.commit()

    logger.info(f"Appeal submitted for application {application_id} by {current_user.email}")

    # Notify admin team
    background_tasks.add_task(
        send_email,
        to="appeals@meta-analysis-platform.com",
        subject=f"New Appeal: {current_user.full_name}",
        template="admin_appeal_notification.html",
        context={"user": current_user, "application": application}
    )

    # Send confirmation to user
    background_tasks.add_task(
        send_email,
        to=current_user.email,
        subject="Appeal Submitted - Under Review",
        template="appeal_submitted.html",
        context={"user": current_user, "application": application}
    )

    expected_days = 7 if application.tier_applied_for == ApplicationTier.TIER_2_REVIEWER else 10

    return AppealResponse(
        message="Appeal submitted successfully. You will receive a response within the estimated timeframe.",
        application_id=application_id,
        expected_response_time_days=expected_days
    )
