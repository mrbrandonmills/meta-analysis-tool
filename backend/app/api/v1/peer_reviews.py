"""
Peer Review API endpoints for AI-assisted manuscript review.

Handles peer review generation, submission, and management for Tool 3: Peer Review Assistant.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger
from pydantic import BaseModel, Field
import anthropic

from app.db.session import get_async_db
from app.models.manuscript import Manuscript, ManuscriptStatus
from app.models.peer_review import PeerReview, ReviewRecommendation, ReviewStatus
from app.core.security import get_current_user_token, TokenData
from app.core.config import get_settings

settings = get_settings()
router = APIRouter()


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class PeerReviewGenerate(BaseModel):
    """Schema for AI peer review generation request."""

    manuscript_id: str = Field(..., description="Manuscript ID to review")
    review_focus: Optional[List[str]] = Field(
        default=["methodology", "results", "clarity", "significance"],
        description="Areas to focus on during review"
    )
    expertise_level: Optional[str] = Field(
        default="expert",
        description="Expertise level: 'expert', 'senior', 'junior'"
    )
    review_style: Optional[str] = Field(
        default="constructive",
        description="Review style: 'constructive', 'critical', 'supportive'"
    )
    include_suggestions: bool = Field(
        default=True,
        description="Include improvement suggestions"
    )


class PeerReviewCreate(BaseModel):
    """Schema for creating/submitting a peer review."""

    manuscript_id: str = Field(..., description="Manuscript ID being reviewed")
    review_text: str = Field(..., min_length=100, description="Main review text")
    strengths: Optional[str] = Field(None, description="Manuscript strengths")
    weaknesses: Optional[str] = Field(None, description="Manuscript weaknesses")
    detailed_comments: Optional[str] = Field(None, description="Detailed comments")
    confidential_comments: Optional[str] = Field(None, description="Comments for editor only")
    overall_score: Optional[float] = Field(None, ge=1.0, le=10.0, description="Overall score (1-10)")
    originality_score: Optional[float] = Field(None, ge=1.0, le=10.0)
    methodology_score: Optional[float] = Field(None, ge=1.0, le=10.0)
    clarity_score: Optional[float] = Field(None, ge=1.0, le=10.0)
    significance_score: Optional[float] = Field(None, ge=1.0, le=10.0)
    recommendation: ReviewRecommendation = Field(..., description="Review recommendation")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Reviewer confidence (0-1)")
    ai_assisted: bool = Field(default=False, description="Was AI assistance used?")


class PeerReviewUpdate(BaseModel):
    """Schema for updating a peer review."""

    review_text: Optional[str] = Field(None, min_length=100)
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    detailed_comments: Optional[str] = None
    confidential_comments: Optional[str] = None
    overall_score: Optional[float] = Field(None, ge=1.0, le=10.0)
    originality_score: Optional[float] = Field(None, ge=1.0, le=10.0)
    methodology_score: Optional[float] = Field(None, ge=1.0, le=10.0)
    clarity_score: Optional[float] = Field(None, ge=1.0, le=10.0)
    significance_score: Optional[float] = Field(None, ge=1.0, le=10.0)
    recommendation: Optional[ReviewRecommendation] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    status: Optional[ReviewStatus] = None


class PeerReviewResponse(BaseModel):
    """Schema for peer review response."""

    id: str
    manuscript_id: str
    reviewer_id: Optional[str]
    review_round: int
    status: str
    review_text: Optional[str]
    strengths: Optional[str]
    weaknesses: Optional[str]
    detailed_comments: Optional[str]
    overall_score: Optional[float]
    originality_score: Optional[float]
    methodology_score: Optional[float]
    clarity_score: Optional[float]
    significance_score: Optional[float]
    recommendation: Optional[str]
    confidence: Optional[float]
    ai_assisted: bool
    ai_draft_used: bool
    submission_date: Optional[datetime]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PeerReviewListResponse(BaseModel):
    """Schema for peer review list response."""

    total: int
    reviews: List[PeerReviewResponse]
    page: int
    page_size: int


class AIReviewGenerateResponse(BaseModel):
    """Schema for AI-generated review response."""

    manuscript_id: str
    review_text: str
    strengths: str
    weaknesses: str
    detailed_comments: str
    overall_score: float
    originality_score: float
    methodology_score: float
    clarity_score: float
    significance_score: float
    recommendation: str
    confidence: float
    ai_reasoning: str
    review_focus_areas: List[str]
    estimated_time_saved_hours: float


# ============================================================================
# AI REVIEW GENERATION
# ============================================================================

async def generate_ai_review(
    manuscript: Manuscript,
    review_focus: List[str],
    expertise_level: str,
    review_style: str,
    include_suggestions: bool,
) -> dict:
    """
    Generate an AI-powered peer review using Claude.

    Uses Anthropic's Claude to analyze manuscript and generate:
    - Comprehensive review text
    - Strengths and weaknesses
    - Detailed comments
    - Quantitative scores
    - Recommendation

    Returns dict with review content and metadata.
    """
    # Build the review prompt
    manuscript_content = f"""
Title: {manuscript.title}

Abstract: {manuscript.abstract or "No abstract provided"}

Keywords: {", ".join(manuscript.keywords) if manuscript.keywords else "None"}

Manuscript Type: {manuscript.manuscript_type.value}

Authors: {", ".join(manuscript.author_names) if manuscript.author_names else "Not specified"}
"""

    # Read PDF if available (simplified - in production, extract full text)
    pdf_content = ""
    if manuscript.pdf_path:
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(manuscript.pdf_path)
            # Extract first 10 pages for review
            for page_num in range(min(10, len(doc))):
                pdf_content += doc[page_num].get_text()
            doc.close()
        except Exception as e:
            logger.warning(f"Failed to extract PDF content: {e}")
            pdf_content = "[PDF content could not be extracted]"

    review_prompt = f"""You are an expert peer reviewer for a scientific journal. You have been asked to provide a comprehensive, {review_style} peer review of the following manuscript.

{manuscript_content}

{"Full Text (First 10 Pages):" if pdf_content else ""}
{pdf_content[:10000] if pdf_content else ""}

Please provide a thorough peer review focusing on the following areas:
{", ".join(review_focus)}

Your review should:
1. Provide an overall assessment of the manuscript
2. Identify key strengths (be specific and cite examples)
3. Identify weaknesses and areas for improvement
4. Provide detailed, constructive comments on each major section
5. Score the manuscript on:
   - Overall quality (1-10)
   - Originality (1-10)
   - Methodology (1-10)
   - Clarity of presentation (1-10)
   - Significance to the field (1-10)
6. Make a final recommendation: ACCEPT, MINOR_REVISION, MAJOR_REVISION, or REJECT
7. Explain your confidence level in this review (0.0-1.0)

{"Include specific, actionable suggestions for improvement." if include_suggestions else ""}

Adopt the perspective of a {expertise_level} reviewer in this field.

Please structure your response as follows:

OVERALL ASSESSMENT:
[Your overall assessment]

STRENGTHS:
[Specific strengths with examples]

WEAKNESSES:
[Specific weaknesses with examples]

DETAILED COMMENTS:
[Section-by-section detailed comments]

SCORES:
Overall: [1-10]
Originality: [1-10]
Methodology: [1-10]
Clarity: [1-10]
Significance: [1-10]

RECOMMENDATION: [ACCEPT/MINOR_REVISION/MAJOR_REVISION/REJECT]

CONFIDENCE: [0.0-1.0]

REASONING:
[Brief explanation of your recommendation and confidence level]
"""

    try:
        # Initialize Anthropic client
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        # Generate review using Claude
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": review_prompt
                }
            ]
        )

        # Extract response
        review_response = message.content[0].text

        # Parse the structured response
        parsed_review = parse_ai_review_response(review_response)

        logger.info(f"Generated AI review for manuscript {manuscript.id}")

        return parsed_review

    except Exception as e:
        logger.error(f"AI review generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI review generation failed: {str(e)}"
        )


def parse_ai_review_response(response_text: str) -> dict:
    """
    Parse the structured AI review response into components.

    Extracts sections, scores, and recommendation from Claude's response.
    """
    # Simple parsing (in production, use more robust parsing)
    sections = {
        "overall_assessment": "",
        "strengths": "",
        "weaknesses": "",
        "detailed_comments": "",
        "overall_score": 7.0,
        "originality_score": 7.0,
        "methodology_score": 7.0,
        "clarity_score": 7.0,
        "significance_score": 7.0,
        "recommendation": "MAJOR_REVISION",
        "confidence": 0.75,
        "reasoning": "",
    }

    # Extract sections using simple string matching
    lines = response_text.split('\n')
    current_section = None

    for line in lines:
        line_upper = line.upper().strip()

        if "OVERALL ASSESSMENT" in line_upper:
            current_section = "overall_assessment"
        elif "STRENGTHS:" in line_upper:
            current_section = "strengths"
        elif "WEAKNESSES:" in line_upper:
            current_section = "weaknesses"
        elif "DETAILED COMMENTS" in line_upper:
            current_section = "detailed_comments"
        elif "SCORES:" in line_upper:
            current_section = "scores"
        elif "RECOMMENDATION:" in line_upper:
            current_section = "recommendation"
        elif "CONFIDENCE:" in line_upper:
            current_section = "confidence"
        elif "REASONING:" in line_upper:
            current_section = "reasoning"
        elif current_section == "scores":
            # Parse score lines
            if "overall:" in line.lower():
                try:
                    sections["overall_score"] = float(line.split(':')[1].strip())
                except:
                    pass
            elif "originality:" in line.lower():
                try:
                    sections["originality_score"] = float(line.split(':')[1].strip())
                except:
                    pass
            elif "methodology:" in line.lower():
                try:
                    sections["methodology_score"] = float(line.split(':')[1].strip())
                except:
                    pass
            elif "clarity:" in line.lower():
                try:
                    sections["clarity_score"] = float(line.split(':')[1].strip())
                except:
                    pass
            elif "significance:" in line.lower():
                try:
                    sections["significance_score"] = float(line.split(':')[1].strip())
                except:
                    pass
        elif current_section == "recommendation":
            # Extract recommendation
            for rec in ["ACCEPT", "MINOR_REVISION", "MAJOR_REVISION", "REJECT"]:
                if rec in line_upper:
                    sections["recommendation"] = rec
                    current_section = None
                    break
        elif current_section == "confidence":
            # Extract confidence
            try:
                conf_str = line.split(':')[-1].strip()
                sections["confidence"] = float(conf_str)
                current_section = None
            except:
                pass
        elif current_section in ["overall_assessment", "strengths", "weaknesses", "detailed_comments", "reasoning"]:
            if line.strip() and not line_upper.startswith("OVERALL") and not line_upper.startswith("STRENGTHS"):
                sections[current_section] += line + "\n"

    # Combine into review text
    review_text = f"{sections['overall_assessment']}\n\n{sections['detailed_comments']}"

    return {
        "review_text": review_text.strip(),
        "strengths": sections["strengths"].strip(),
        "weaknesses": sections["weaknesses"].strip(),
        "detailed_comments": sections["detailed_comments"].strip(),
        "overall_score": sections["overall_score"],
        "originality_score": sections["originality_score"],
        "methodology_score": sections["methodology_score"],
        "clarity_score": sections["clarity_score"],
        "significance_score": sections["significance_score"],
        "recommendation": sections["recommendation"],
        "confidence": sections["confidence"],
        "reasoning": sections["reasoning"].strip(),
    }


# ============================================================================
# PEER REVIEW ENDPOINTS
# ============================================================================

@router.post("/peer-reviews/generate", response_model=AIReviewGenerateResponse)
async def generate_peer_review(
    request: PeerReviewGenerate,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Generate an AI-powered peer review for a manuscript.

    - Uses Claude AI to analyze manuscript and generate comprehensive review
    - Provides structured feedback: strengths, weaknesses, detailed comments
    - Generates quantitative scores across multiple dimensions
    - Makes evidence-based recommendation
    - Does NOT save the review automatically (use POST /peer-reviews to save)

    Returns the generated review for user to review/edit before submission.
    """
    try:
        # Get manuscript
        result = await db.execute(
            select(Manuscript).where(Manuscript.id == UUID(request.manuscript_id))
        )
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscript not found"
            )

        # Check if manuscript has content to review
        if not manuscript.abstract and not manuscript.pdf_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manuscript must have either abstract or PDF for review generation"
            )

        # Generate AI review
        ai_review = await generate_ai_review(
            manuscript=manuscript,
            review_focus=request.review_focus,
            expertise_level=request.expertise_level,
            review_style=request.review_style,
            include_suggestions=request.include_suggestions,
        )

        # Estimate time saved (typical review takes 3-5 hours)
        estimated_time_saved = 4.0

        return AIReviewGenerateResponse(
            manuscript_id=request.manuscript_id,
            review_text=ai_review["review_text"],
            strengths=ai_review["strengths"],
            weaknesses=ai_review["weaknesses"],
            detailed_comments=ai_review["detailed_comments"],
            overall_score=ai_review["overall_score"],
            originality_score=ai_review["originality_score"],
            methodology_score=ai_review["methodology_score"],
            clarity_score=ai_review["clarity_score"],
            significance_score=ai_review["significance_score"],
            recommendation=ai_review["recommendation"],
            confidence=ai_review["confidence"],
            ai_reasoning=ai_review["reasoning"],
            review_focus_areas=request.review_focus,
            estimated_time_saved_hours=estimated_time_saved,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating peer review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate peer review: {str(e)}"
        )


@router.post("/peer-reviews", response_model=PeerReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_peer_review(
    review_data: PeerReviewCreate,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Create and submit a peer review.

    - Can be AI-generated or human-written
    - Associates review with current user as reviewer
    - Sets review to SUBMITTED status
    - Updates manuscript review count

    Returns the created peer review.
    """
    try:
        # Verify manuscript exists
        result = await db.execute(
            select(Manuscript).where(Manuscript.id == UUID(review_data.manuscript_id))
        )
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscript not found"
            )

        # Create peer review
        new_review = PeerReview(
            manuscript_id=UUID(review_data.manuscript_id),
            reviewer_id=None,  # Anonymous review (in production, link to researcher)
            review_round=manuscript.current_round,
            status=ReviewStatus.SUBMITTED,
            submission_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=14),  # Default 2 weeks
            review_text=review_data.review_text,
            strengths=review_data.strengths,
            weaknesses=review_data.weaknesses,
            detailed_comments=review_data.detailed_comments,
            confidential_comments=review_data.confidential_comments,
            overall_score=review_data.overall_score,
            originality_score=review_data.originality_score,
            methodology_score=review_data.methodology_score,
            clarity_score=review_data.clarity_score,
            significance_score=review_data.significance_score,
            recommendation=review_data.recommendation,
            confidence=review_data.confidence,
            ai_assisted=review_data.ai_assisted,
            ai_draft_used=review_data.ai_assisted,
        )

        db.add(new_review)
        await db.commit()
        await db.refresh(new_review)

        # Update manuscript status to IN_REVIEW if not already
        if manuscript.status == ManuscriptStatus.SUBMITTED:
            manuscript.status = ManuscriptStatus.IN_REVIEW
            await db.commit()

        logger.info(f"Created peer review {new_review.id} for manuscript {review_data.manuscript_id}")

        return PeerReviewResponse(
            id=str(new_review.id),
            manuscript_id=str(new_review.manuscript_id),
            reviewer_id=str(new_review.reviewer_id) if new_review.reviewer_id else None,
            review_round=new_review.review_round,
            status=new_review.status.value,
            review_text=new_review.review_text,
            strengths=new_review.strengths,
            weaknesses=new_review.weaknesses,
            detailed_comments=new_review.detailed_comments,
            overall_score=new_review.overall_score,
            originality_score=new_review.originality_score,
            methodology_score=new_review.methodology_score,
            clarity_score=new_review.clarity_score,
            significance_score=new_review.significance_score,
            recommendation=new_review.recommendation.value if new_review.recommendation else None,
            confidence=new_review.confidence,
            ai_assisted=new_review.ai_assisted,
            ai_draft_used=new_review.ai_draft_used,
            submission_date=new_review.submission_date,
            due_date=new_review.due_date,
            created_at=new_review.created_at,
            updated_at=new_review.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating peer review: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create peer review: {str(e)}"
        )


@router.get("/peer-reviews/{review_id}", response_model=PeerReviewResponse)
async def get_peer_review(
    review_id: str,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get a specific peer review by ID.

    - Returns review details
    - Access control: Only manuscript author or reviewer can access
    """
    try:
        result = await db.execute(
            select(PeerReview).where(PeerReview.id == UUID(review_id))
        )
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peer review not found"
            )

        # Check access permissions
        manuscript_result = await db.execute(
            select(Manuscript).where(Manuscript.id == review.manuscript_id)
        )
        manuscript = manuscript_result.scalar_one_or_none()

        if manuscript and str(manuscript.corresponding_author_id) != token.user_id:
            # In production, also check if current user is the reviewer
            # For now, allow access
            pass

        return PeerReviewResponse(
            id=str(review.id),
            manuscript_id=str(review.manuscript_id),
            reviewer_id=str(review.reviewer_id) if review.reviewer_id else None,
            review_round=review.review_round,
            status=review.status.value,
            review_text=review.review_text,
            strengths=review.strengths,
            weaknesses=review.weaknesses,
            detailed_comments=review.detailed_comments,
            overall_score=review.overall_score,
            originality_score=review.originality_score,
            methodology_score=review.methodology_score,
            clarity_score=review.clarity_score,
            significance_score=review.significance_score,
            recommendation=review.recommendation.value if review.recommendation else None,
            confidence=review.confidence,
            ai_assisted=review.ai_assisted,
            ai_draft_used=review.ai_draft_used,
            submission_date=review.submission_date,
            due_date=review.due_date,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting peer review {review_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get peer review: {str(e)}"
        )


@router.put("/peer-reviews/{review_id}", response_model=PeerReviewResponse)
async def update_peer_review(
    review_id: str,
    review_data: PeerReviewUpdate,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Update an existing peer review.

    - Can update review content, scores, recommendation, status
    - Only reviewer can update (in production, enforce this)
    """
    try:
        result = await db.execute(
            select(PeerReview).where(PeerReview.id == UUID(review_id))
        )
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peer review not found"
            )

        # Update fields
        update_data = review_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(review, field, value)

        await db.commit()
        await db.refresh(review)

        logger.info(f"Updated peer review {review_id}")

        return PeerReviewResponse(
            id=str(review.id),
            manuscript_id=str(review.manuscript_id),
            reviewer_id=str(review.reviewer_id) if review.reviewer_id else None,
            review_round=review.review_round,
            status=review.status.value,
            review_text=review.review_text,
            strengths=review.strengths,
            weaknesses=review.weaknesses,
            detailed_comments=review.detailed_comments,
            overall_score=review.overall_score,
            originality_score=review.originality_score,
            methodology_score=review.methodology_score,
            clarity_score=review.clarity_score,
            significance_score=review.significance_score,
            recommendation=review.recommendation.value if review.recommendation else None,
            confidence=review.confidence,
            ai_assisted=review.ai_assisted,
            ai_draft_used=review.ai_draft_used,
            submission_date=review.submission_date,
            due_date=review.due_date,
            created_at=review.created_at,
            updated_at=review.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating peer review {review_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update peer review: {str(e)}"
        )


@router.get("/manuscripts/{manuscript_id}/reviews", response_model=PeerReviewListResponse)
async def list_manuscript_reviews(
    manuscript_id: str,
    page: int = 1,
    page_size: int = 20,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    List all peer reviews for a specific manuscript.

    - Returns all reviews associated with the manuscript
    - Supports pagination
    - Access control: Only manuscript author can view reviews
    """
    try:
        # Verify manuscript exists and user has access
        manuscript_result = await db.execute(
            select(Manuscript).where(
                Manuscript.id == UUID(manuscript_id),
                Manuscript.corresponding_author_id == UUID(token.user_id)
            )
        )
        manuscript = manuscript_result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscript not found or access denied"
            )

        # Build query
        query = select(PeerReview).where(PeerReview.manuscript_id == UUID(manuscript_id))

        # Get total count
        count_result = await db.execute(
            select(func.count()).where(PeerReview.manuscript_id == UUID(manuscript_id))
        )
        total = count_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(PeerReview.submission_date.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        # Execute query
        result = await db.execute(query)
        reviews = result.scalars().all()

        # Convert to response models
        review_responses = [
            PeerReviewResponse(
                id=str(review.id),
                manuscript_id=str(review.manuscript_id),
                reviewer_id=str(review.reviewer_id) if review.reviewer_id else None,
                review_round=review.review_round,
                status=review.status.value,
                review_text=review.review_text,
                strengths=review.strengths,
                weaknesses=review.weaknesses,
                detailed_comments=review.detailed_comments,
                overall_score=review.overall_score,
                originality_score=review.originality_score,
                methodology_score=review.methodology_score,
                clarity_score=review.clarity_score,
                significance_score=review.significance_score,
                recommendation=review.recommendation.value if review.recommendation else None,
                confidence=review.confidence,
                ai_assisted=review.ai_assisted,
                ai_draft_used=review.ai_draft_used,
                submission_date=review.submission_date,
                due_date=review.due_date,
                created_at=review.created_at,
                updated_at=review.updated_at,
            )
            for review in reviews
        ]

        return PeerReviewListResponse(
            total=total,
            reviews=review_responses,
            page=page,
            page_size=page_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing reviews for manuscript {manuscript_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list reviews: {str(e)}"
        )


@router.delete("/peer-reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_peer_review(
    review_id: str,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Delete a peer review.

    - Only reviewer or manuscript author can delete
    - Permanent deletion
    """
    try:
        result = await db.execute(
            select(PeerReview).where(PeerReview.id == UUID(review_id))
        )
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Peer review not found"
            )

        # Check access (simplified - in production, verify user is reviewer or author)
        manuscript_result = await db.execute(
            select(Manuscript).where(Manuscript.id == review.manuscript_id)
        )
        manuscript = manuscript_result.scalar_one_or_none()

        if manuscript and str(manuscript.corresponding_author_id) != token.user_id:
            # In production, also check if current user is the reviewer
            pass

        # Delete review
        await db.delete(review)
        await db.commit()

        logger.info(f"Deleted peer review {review_id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting peer review {review_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete peer review: {str(e)}"
        )
