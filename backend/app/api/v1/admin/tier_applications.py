"""
Admin endpoints for reviewing and managing tier applications.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user, require_admin
from app.models.user import User
from app.models.tier_application import TierApplication, QualificationVerification
from app.schemas.tier_applications import (
    TierApplicationSummary,
    ApplicationDetailResponse,
    AdminReviewDecision,
    ReviewDecisionResponse,
    ApplicationStatusEnum,
    ApplicationTierEnum,
    DenialReasonEnum
)
from app.services.email_service import EmailService
from app.services.credential_verification import ComprehensiveVerificationService

router = APIRouter(prefix="/admin/tier-applications", tags=["Admin - Tier Applications"])


# ===========================
# ADMIN DASHBOARD ENDPOINTS
# ===========================

@router.get("/pending", response_model=List[TierApplicationSummary])
async def get_pending_applications(
    tier: Optional[ApplicationTierEnum] = None,
    status: Optional[ApplicationStatusEnum] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get all pending applications for admin review.

    Filters:
    - tier: Filter by tier (tier_2_reviewer or tier_3_editor)
    - status: Filter by specific status
    - Default: Shows applications in MANUAL_REVIEW_PENDING or REFERENCES_CHECK_IN_PROGRESS
    """
    query = select(TierApplication).join(User, TierApplication.user_id == User.id)

    # Default to showing applications that need manual review
    if not status:
        query = query.where(
            TierApplication.status.in_([
                ApplicationStatusEnum.MANUAL_REVIEW_PENDING,
                ApplicationStatusEnum.MANUAL_REVIEW_IN_PROGRESS,
                ApplicationStatusEnum.REFERENCES_CHECK_IN_PROGRESS,
                ApplicationStatusEnum.ADVISORY_BOARD_REVIEW,
                ApplicationStatusEnum.MORE_INFO_REQUESTED
            ])
        )
    else:
        query = query.where(TierApplication.status == status)

    if tier:
        query = query.where(TierApplication.tier_applied_for == tier)

    # Order by submission date (oldest first for fairness)
    query = query.order_by(TierApplication.submitted_at.asc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    applications = result.scalars().all()

    # Build summary response
    summaries = []
    for app in applications:
        # Get user info
        user_result = await db.execute(select(User).where(User.id == app.user_id))
        user = user_result.scalar_one()

        # Calculate days pending
        days_pending = (datetime.utcnow() - app.submitted_at).days

        summaries.append(TierApplicationSummary(
            application_id=app.id,
            applicant_name=f"{user.first_name} {user.last_name}",
            applicant_email=user.email,
            tier_applied_for=app.tier_applied_for,
            status=app.status,
            submitted_at=app.submitted_at,
            days_pending=days_pending,
            auto_verification_passed=app.auto_verification_passed,
            h_index=app.h_index,
            total_publications=app.total_publications
        ))

    return summaries


@router.get("/statistics")
async def get_application_statistics(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get statistics on tier applications for admin dashboard.
    """
    # Total applications
    total_query = select(func.count(TierApplication.id))
    total_result = await db.execute(total_query)
    total_applications = total_result.scalar()

    # Pending review
    pending_query = select(func.count(TierApplication.id)).where(
        TierApplication.status.in_([
            ApplicationStatusEnum.MANUAL_REVIEW_PENDING,
            ApplicationStatusEnum.MANUAL_REVIEW_IN_PROGRESS,
            ApplicationStatusEnum.REFERENCES_CHECK_IN_PROGRESS,
            ApplicationStatusEnum.ADVISORY_BOARD_REVIEW
        ])
    )
    pending_result = await db.execute(pending_query)
    pending_review = pending_result.scalar()

    # Approved
    approved_query = select(func.count(TierApplication.id)).where(
        TierApplication.status == ApplicationStatusEnum.APPROVED
    )
    approved_result = await db.execute(approved_query)
    approved_count = approved_result.scalar()

    # Denied
    denied_query = select(func.count(TierApplication.id)).where(
        TierApplication.status == ApplicationStatusEnum.DENIED
    )
    denied_result = await db.execute(denied_query)
    denied_count = denied_result.scalar()

    # Auto-verification failure rate
    auto_failed_query = select(func.count(TierApplication.id)).where(
        TierApplication.status == ApplicationStatusEnum.AUTO_VERIFICATION_FAILED
    )
    auto_failed_result = await db.execute(auto_failed_query)
    auto_failed_count = auto_failed_result.scalar()

    # Appeals
    appeals_query = select(func.count(TierApplication.id)).where(
        TierApplication.status.in_([
            ApplicationStatusEnum.APPEALED,
            ApplicationStatusEnum.APPEAL_APPROVED,
            ApplicationStatusEnum.APPEAL_DENIED
        ])
    )
    appeals_result = await db.execute(appeals_query)
    appeals_count = appeals_result.scalar()

    # Applications needing urgent attention (>7 days pending)
    urgent_date = datetime.utcnow() - timedelta(days=7)
    urgent_query = select(func.count(TierApplication.id)).where(
        and_(
            TierApplication.status.in_([
                ApplicationStatusEnum.MANUAL_REVIEW_PENDING,
                ApplicationStatusEnum.REFERENCES_CHECK_IN_PROGRESS
            ]),
            TierApplication.submitted_at < urgent_date
        )
    )
    urgent_result = await db.execute(urgent_query)
    urgent_count = urgent_result.scalar()

    return {
        "total_applications": total_applications,
        "pending_review": pending_review,
        "approved": approved_count,
        "denied": denied_count,
        "auto_verification_failed": auto_failed_count,
        "appeals": appeals_count,
        "urgent_attention_needed": urgent_count,
        "average_approval_rate": round((approved_count / total_applications * 100), 2) if total_applications > 0 else 0
    }


@router.get("/{application_id}/details", response_model=ApplicationDetailResponse)
async def get_application_details(
    application_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get complete details of a specific application for admin review.
    """
    query = select(TierApplication).where(TierApplication.id == application_id)
    result = await db.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return ApplicationDetailResponse(
        application_id=application.id,
        user_id=application.user_id,
        tier_applied_for=application.tier_applied_for,
        status=application.status,
        degree_type=application.degree_type,
        degree_institution=application.degree_institution,
        degree_field=application.degree_field,
        degree_year=application.degree_year,
        orcid_verified=application.orcid_verified,
        google_scholar_verified=application.google_scholar_verified,
        h_index=application.h_index,
        total_citations=application.total_citations,
        total_publications=application.total_publications,
        submitted_at=application.submitted_at,
        decision_made_at=application.decision_made_at,
        approved=application.approved,
        denial_reasons=application.denial_reasons,
        appeal_submitted=application.appeal_submitted,
        appeal_decided_at=application.appeal_decided_at
    )


@router.get("/{application_id}/verification-report")
async def get_verification_report(
    application_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get detailed verification report including all credential checks.
    """
    query = select(QualificationVerification).where(
        QualificationVerification.application_id == application_id
    )
    result = await db.execute(query)
    verification = result.scalar_one_or_none()

    if not verification:
        raise HTTPException(status_code=404, detail="Verification report not found")

    return {
        "application_id": application_id,
        "verification_completed": verification.verification_completed,
        "verification_date": verification.verification_date,
        "orcid_data": verification.orcid_data,
        "google_scholar_data": verification.google_scholar_data,
        "publications_data": verification.publications_data,
        "background_check_data": verification.background_check_data,
        "verification_passed": verification.verification_passed,
        "verification_notes": verification.verification_notes
    }


# ===========================
# REVIEW DECISION ENDPOINTS
# ===========================

@router.post("/{application_id}/review", response_model=ReviewDecisionResponse)
async def review_application(
    application_id: UUID,
    decision: AdminReviewDecision,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Admin review decision on an application.

    Actions:
    - APPROVE: Approve application and grant tier access
    - DENY: Deny application with reasons
    - REQUEST_MORE_INFO: Request additional information from applicant
    - PROBATIONARY_APPROVE: Approve with probationary period (90 days)
    """
    # Get application
    query = select(TierApplication).where(TierApplication.id == application_id)
    result = await db.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Validate state transitions
    valid_states = [
        ApplicationStatusEnum.MANUAL_REVIEW_PENDING,
        ApplicationStatusEnum.MANUAL_REVIEW_IN_PROGRESS,
        ApplicationStatusEnum.REFERENCES_CHECK_IN_PROGRESS,
        ApplicationStatusEnum.ADVISORY_BOARD_REVIEW,
        ApplicationStatusEnum.MORE_INFO_REQUESTED,
        ApplicationStatusEnum.APPEALED
    ]

    if application.status not in valid_states:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot review application in status: {application.status}"
        )

    # Process decision
    if decision.action == "APPROVE":
        application.status = ApplicationStatusEnum.APPROVED
        application.approved = True
        application.decision_made_at = datetime.utcnow()
        application.admin_notes = decision.admin_notes
        application.reviewed_by_admin_id = current_user.id

        # Grant tier access to user
        user_query = select(User).where(User.id == application.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one()

        if application.tier_applied_for == ApplicationTierEnum.TIER_2_REVIEWER:
            user.tier = "tier_2_reviewer"
        elif application.tier_applied_for == ApplicationTierEnum.TIER_3_EDITOR:
            user.tier = "tier_3_editor"

        # TODO: Update Stripe subscription to appropriate tier

        message = "Application approved. User has been granted tier access."

        # Send approval email
        background_tasks.add_task(
            EmailService.send_application_approved_email,
            user.email,
            application.tier_applied_for
        )

    elif decision.action == "DENY":
        if not decision.reasons or not decision.explanation:
            raise HTTPException(
                status_code=400,
                detail="Denial requires reasons and explanation"
            )

        application.status = ApplicationStatusEnum.DENIED
        application.approved = False
        application.decision_made_at = datetime.utcnow()
        application.denial_reasons = [str(r) for r in decision.reasons]
        application.denial_explanation = decision.explanation
        application.admin_notes = decision.admin_notes
        application.reviewed_by_admin_id = current_user.id

        message = "Application denied. Applicant can appeal this decision."

        # Send denial email with appeal instructions
        user_query = select(User).where(User.id == application.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one()

        background_tasks.add_task(
            EmailService.send_application_denied_email,
            user.email,
            application.denial_reasons,
            decision.explanation
        )

    elif decision.action == "REQUEST_MORE_INFO":
        if not decision.requested_info:
            raise HTTPException(
                status_code=400,
                detail="Must specify what information is requested"
            )

        application.status = ApplicationStatusEnum.MORE_INFO_REQUESTED
        application.requested_info = decision.requested_info
        application.admin_notes = decision.admin_notes
        application.reviewed_by_admin_id = current_user.id

        message = "More information requested from applicant."

        # Send email requesting more info
        user_query = select(User).where(User.id == application.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one()

        background_tasks.add_task(
            EmailService.send_more_info_requested_email,
            user.email,
            decision.requested_info
        )

    elif decision.action == "PROBATIONARY_APPROVE":
        application.status = ApplicationStatusEnum.APPROVED
        application.approved = True
        application.probationary_approval = True
        application.probation_end_date = datetime.utcnow() + timedelta(days=90)
        application.decision_made_at = datetime.utcnow()
        application.admin_notes = decision.admin_notes
        application.reviewed_by_admin_id = current_user.id

        # Grant tier access
        user_query = select(User).where(User.id == application.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one()

        if application.tier_applied_for == ApplicationTierEnum.TIER_2_REVIEWER:
            user.tier = "tier_2_reviewer"
        elif application.tier_applied_for == ApplicationTierEnum.TIER_3_EDITOR:
            user.tier = "tier_3_editor"

        message = "Application approved with 90-day probationary period."

        background_tasks.add_task(
            EmailService.send_probationary_approval_email,
            user.email,
            application.tier_applied_for,
            application.probation_end_date
        )

    else:
        raise HTTPException(status_code=400, detail=f"Invalid action: {decision.action}")

    await db.commit()

    return ReviewDecisionResponse(
        application_id=application.id,
        decision=decision.action,
        message=message
    )


@router.post("/{application_id}/assign-to-advisory-board")
async def assign_to_advisory_board(
    application_id: UUID,
    notes: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Escalate application to advisory board for review.
    Use this for edge cases or applications requiring senior judgment.
    """
    query = select(TierApplication).where(TierApplication.id == application_id)
    result = await db.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = ApplicationStatusEnum.ADVISORY_BOARD_REVIEW
    application.admin_notes = f"Escalated to advisory board by {current_user.email}. Notes: {notes}"

    await db.commit()

    # TODO: Send notification to advisory board members

    return {
        "message": "Application escalated to advisory board",
        "application_id": application_id,
        "status": ApplicationStatusEnum.ADVISORY_BOARD_REVIEW
    }


@router.post("/{application_id}/contact-references")
async def contact_professional_references(
    application_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Initiate contact with professional references for Tier 3 applications.
    """
    query = select(TierApplication).where(TierApplication.id == application_id)
    result = await db.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.tier_applied_for != ApplicationTierEnum.TIER_3_EDITOR:
        raise HTTPException(
            status_code=400,
            detail="Reference checks only applicable to Tier 3 applications"
        )

    # Update status
    application.status = ApplicationStatusEnum.REFERENCES_CHECK_IN_PROGRESS
    application.references_contacted_at = datetime.utcnow()

    await db.commit()

    # Get professional references from application data
    references = application.professional_references or []

    if not references:
        raise HTTPException(
            status_code=400,
            detail="No professional references found in application"
        )

    # Send emails to references
    for ref in references:
        background_tasks.add_task(
            EmailService.send_reference_check_email,
            ref["email"],
            ref["name"],
            application.id,
            application.user_id
        )

    return {
        "message": f"Reference check emails sent to {len(references)} references",
        "application_id": application_id,
        "references_contacted": len(references)
    }


@router.post("/{application_id}/re-verify")
async def re_run_verification(
    application_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Re-run automatic verification (useful if initial verification had errors or needs refresh).
    """
    query = select(TierApplication).where(TierApplication.id == application_id)
    result = await db.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Update status
    application.status = ApplicationStatusEnum.AUTO_VERIFICATION_IN_PROGRESS
    application.auto_verification_passed = None

    await db.commit()

    # Re-run verification in background
    background_tasks.add_task(
        run_re_verification,
        application_id,
        db
    )

    return {
        "message": "Verification re-started",
        "application_id": application_id
    }


async def run_re_verification(application_id: UUID, db: AsyncSession):
    """
    Background task to re-run verification.
    """
    query = select(TierApplication).where(TierApplication.id == application_id)
    result = await db.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        return

    # Run comprehensive verification
    verification_result = await ComprehensiveVerificationService.verify_all_credentials(
        orcid_id=application.orcid_id,
        google_scholar_url=application.google_scholar_url,
        publication_dois=application.publication_dois,
        researcher_name=f"{application.degree_field} Researcher"
    )

    # Update application with results
    application.orcid_verified = verification_result["orcid_result"]["verified"]
    application.google_scholar_verified = verification_result["google_scholar_result"]["verified"]
    application.h_index = verification_result["google_scholar_result"].get("h_index")
    application.total_citations = verification_result["google_scholar_result"].get("total_citations")
    application.total_publications = verification_result["google_scholar_result"].get("publications_count")
    application.auto_verification_passed = verification_result["verification_passed"]

    if verification_result["verification_passed"]:
        application.status = ApplicationStatusEnum.MANUAL_REVIEW_PENDING
    else:
        application.status = ApplicationStatusEnum.AUTO_VERIFICATION_FAILED

    # Update verification record
    verification_query = select(QualificationVerification).where(
        QualificationVerification.application_id == application_id
    )
    verification_result_db = await db.execute(verification_query)
    verification_record = verification_result_db.scalar_one_or_none()

    if verification_record:
        verification_record.orcid_data = verification_result["orcid_result"]
        verification_record.google_scholar_data = verification_result["google_scholar_result"]
        verification_record.verification_completed = True
        verification_record.verification_date = datetime.utcnow()
        verification_record.verification_passed = verification_result["verification_passed"]

    await db.commit()


# ===========================
# APPEAL REVIEW ENDPOINTS
# ===========================

@router.get("/appeals/pending")
async def get_pending_appeals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get all pending appeals for admin review.
    """
    query = select(TierApplication).where(
        TierApplication.status == ApplicationStatusEnum.APPEALED
    ).order_by(TierApplication.appeal_submitted_at.asc())

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    applications = result.scalars().all()

    appeals = []
    for app in applications:
        user_query = select(User).where(User.id == app.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one()

        appeals.append({
            "application_id": app.id,
            "applicant_name": f"{user.first_name} {user.last_name}",
            "applicant_email": user.email,
            "tier_applied_for": app.tier_applied_for,
            "original_denial_reasons": app.denial_reasons,
            "appeal_reason": app.appeal_reason,
            "appeal_submitted_at": app.appeal_submitted_at,
            "days_since_appeal": (datetime.utcnow() - app.appeal_submitted_at).days
        })

    return appeals


@router.post("/{application_id}/appeal-decision")
async def review_appeal(
    application_id: UUID,
    approved: bool,
    explanation: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Make a decision on an appeal.
    """
    query = select(TierApplication).where(TierApplication.id == application_id)
    result = await db.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.status != ApplicationStatusEnum.APPEALED:
        raise HTTPException(
            status_code=400,
            detail="Application is not in appeal status"
        )

    if approved:
        application.status = ApplicationStatusEnum.APPEAL_APPROVED
        application.approved = True

        # Grant tier access
        user_query = select(User).where(User.id == application.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one()

        if application.tier_applied_for == ApplicationTierEnum.TIER_2_REVIEWER:
            user.tier = "tier_2_reviewer"
        elif application.tier_applied_for == ApplicationTierEnum.TIER_3_EDITOR:
            user.tier = "tier_3_editor"

        message = "Appeal approved. User granted tier access."

        background_tasks.add_task(
            EmailService.send_appeal_approved_email,
            user.email,
            application.tier_applied_for
        )
    else:
        application.status = ApplicationStatusEnum.APPEAL_DENIED
        application.appeal_denial_explanation = explanation

        message = "Appeal denied."

        user_query = select(User).where(User.id == application.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one()

        background_tasks.add_task(
            EmailService.send_appeal_denied_email,
            user.email,
            explanation
        )

    application.appeal_decided_at = datetime.utcnow()
    application.appeal_reviewed_by_admin_id = current_user.id

    await db.commit()

    return {
        "application_id": application_id,
        "appeal_decision": "approved" if approved else "denied",
        "message": message
    }
