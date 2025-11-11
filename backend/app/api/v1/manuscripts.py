"""
Manuscript API endpoints for peer review system.

Handles manuscript submission, upload, and management for Tool 3: Peer Review Assistant.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
import os
import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger
from pydantic import BaseModel, Field

from app.db.session import get_async_db
from app.models.manuscript import Manuscript, ManuscriptStatus, ManuscriptType
from app.models.user import User
from app.core.security import get_current_user_token, TokenData
from app.core.config import get_settings

settings = get_settings()
router = APIRouter()


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class ManuscriptCreate(BaseModel):
    """Schema for creating a new manuscript."""

    title: str = Field(..., min_length=10, max_length=500, description="Manuscript title")
    abstract: Optional[str] = Field(None, max_length=5000, description="Manuscript abstract")
    keywords: Optional[List[str]] = Field(default=[], description="Keywords")
    manuscript_type: ManuscriptType = Field(..., description="Type of manuscript")
    journal_name: Optional[str] = Field(None, max_length=255, description="Target journal name")
    author_names: Optional[List[str]] = Field(default=[], description="List of author names")
    author_affiliations: Optional[dict] = Field(default={}, description="Author affiliations mapping")


class ManuscriptUpdate(BaseModel):
    """Schema for updating a manuscript."""

    title: Optional[str] = Field(None, min_length=10, max_length=500)
    abstract: Optional[str] = Field(None, max_length=5000)
    keywords: Optional[List[str]] = None
    manuscript_type: Optional[ManuscriptType] = None
    journal_name: Optional[str] = Field(None, max_length=255)
    author_names: Optional[List[str]] = None
    author_affiliations: Optional[dict] = None


class ManuscriptStatusUpdate(BaseModel):
    """Schema for updating manuscript status."""

    status: ManuscriptStatus = Field(..., description="New manuscript status")
    decision_letter: Optional[str] = Field(None, description="Editorial decision letter")


class ManuscriptResponse(BaseModel):
    """Schema for manuscript response."""

    id: str
    title: str
    abstract: Optional[str]
    keywords: Optional[List[str]]
    manuscript_type: str
    status: str
    submission_date: datetime
    journal_name: Optional[str]
    author_names: Optional[List[str]]
    author_affiliations: Optional[dict]
    current_round: int
    pdf_path: Optional[str]
    has_pdf: bool
    desk_review_decision: Optional[str]
    desk_review_reasoning: Optional[str]
    quality_score: Optional[dict]
    methodology_score: Optional[dict]
    novelty_score: Optional[dict]
    editorial_decision: Optional[str]
    editorial_decision_date: Optional[datetime]
    review_count: int
    corresponding_author_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ManuscriptListResponse(BaseModel):
    """Schema for manuscript list response."""

    total: int
    manuscripts: List[ManuscriptResponse]
    page: int
    page_size: int


class PDFUploadResponse(BaseModel):
    """Schema for PDF upload response."""

    manuscript_id: str
    pdf_path: str
    file_size_bytes: int
    extracted_title: Optional[str]
    extracted_abstract: Optional[str]
    message: str


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_upload_directory() -> Path:
    """Get or create the upload directory for manuscript PDFs."""
    upload_dir = Path(settings.data_dir) / "manuscripts"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


async def extract_pdf_metadata(pdf_path: Path) -> dict:
    """
    Extract title and abstract from PDF using PyMuPDF.

    Returns dict with 'title', 'abstract', and 'text_preview'.
    Falls back gracefully if extraction fails.
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)

        # Extract first page text for title/abstract detection
        first_page = doc[0].get_text()
        lines = [line.strip() for line in first_page.split('\n') if line.strip()]

        # Simple heuristic: first substantial line is likely the title
        title = None
        for line in lines:
            if len(line) > 20 and not line.isupper():  # Skip headers
                title = line
                break

        # Look for abstract section
        full_text = ""
        for page in doc[:3]:  # Check first 3 pages
            full_text += page.get_text()

        abstract = None
        abstract_keywords = ["abstract", "summary"]
        for keyword in abstract_keywords:
            if keyword.lower() in full_text.lower():
                # Extract text after "Abstract" keyword
                idx = full_text.lower().find(keyword.lower())
                abstract_text = full_text[idx:idx+1500]
                # Clean up
                abstract = " ".join(abstract_text.split())[:1000]
                break

        doc.close()

        return {
            "title": title,
            "abstract": abstract,
            "text_preview": full_text[:500],
            "page_count": len(doc),
        }

    except Exception as e:
        logger.warning(f"PDF metadata extraction failed: {e}")
        return {
            "title": None,
            "abstract": None,
            "text_preview": None,
            "page_count": None,
        }


# ============================================================================
# MANUSCRIPT CRUD ENDPOINTS
# ============================================================================

@router.post("/manuscripts/upload", response_model=PDFUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_manuscript_pdf(
    file: UploadFile = File(..., description="PDF file to upload"),
    manuscript_id: Optional[str] = Form(None, description="Existing manuscript ID to attach PDF to"),
    auto_extract: bool = Form(True, description="Automatically extract title/abstract from PDF"),
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Upload a manuscript PDF file.

    - If manuscript_id is provided, attaches PDF to existing manuscript
    - If manuscript_id is null, creates a new manuscript with extracted metadata
    - Validates file type (PDF only)
    - Stores file with unique name to prevent collisions
    - Optionally extracts title/abstract from PDF

    Returns upload status and extracted metadata.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    # Validate file size (50MB limit)
    max_size = 50 * 1024 * 1024  # 50MB
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is 50MB, got {file_size / (1024*1024):.2f}MB"
        )

    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    upload_dir = get_upload_directory()
    file_path = upload_dir / safe_filename

    # Save file
    try:
        with open(file_path, 'wb') as f:
            f.write(file_content)
        logger.info(f"Saved PDF to {file_path} ({file_size} bytes)")
    except Exception as e:
        logger.error(f"Failed to save PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Extract metadata if requested
    extracted_data = {"title": None, "abstract": None}
    if auto_extract:
        extracted_data = await extract_pdf_metadata(file_path)

    # Handle manuscript creation or update
    if manuscript_id:
        # Update existing manuscript
        result = await db.execute(
            select(Manuscript).where(
                Manuscript.id == UUID(manuscript_id),
                Manuscript.corresponding_author_id == UUID(token.user_id)
            )
        )
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            # Cleanup uploaded file
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscript not found or access denied"
            )

        # Update manuscript with PDF path
        manuscript.pdf_path = str(file_path)

        # Update title/abstract if extracted and not already set
        if auto_extract and extracted_data["title"] and not manuscript.title:
            manuscript.title = extracted_data["title"]
        if auto_extract and extracted_data["abstract"] and not manuscript.abstract:
            manuscript.abstract = extracted_data["abstract"]

        await db.commit()
        await db.refresh(manuscript)

        return PDFUploadResponse(
            manuscript_id=str(manuscript.id),
            pdf_path=str(file_path),
            file_size_bytes=file_size,
            extracted_title=extracted_data.get("title"),
            extracted_abstract=extracted_data.get("abstract"),
            message="PDF uploaded and attached to manuscript successfully"
        )
    else:
        # Create new manuscript with extracted metadata
        new_manuscript = Manuscript(
            title=extracted_data.get("title") or "Untitled Manuscript",
            abstract=extracted_data.get("abstract"),
            manuscript_type=ManuscriptType.RESEARCH_ARTICLE,  # Default
            corresponding_author_id=UUID(token.user_id),
            pdf_path=str(file_path),
            status=ManuscriptStatus.SUBMITTED,
            current_round=1,
        )

        db.add(new_manuscript)
        await db.commit()
        await db.refresh(new_manuscript)

        logger.info(f"Created new manuscript {new_manuscript.id} from PDF upload")

        return PDFUploadResponse(
            manuscript_id=str(new_manuscript.id),
            pdf_path=str(file_path),
            file_size_bytes=file_size,
            extracted_title=extracted_data.get("title"),
            extracted_abstract=extracted_data.get("abstract"),
            message="PDF uploaded and new manuscript created successfully"
        )


@router.post("/manuscripts", response_model=ManuscriptResponse, status_code=status.HTTP_201_CREATED)
async def create_manuscript(
    manuscript_data: ManuscriptCreate,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Create a new manuscript submission.

    - Requires authentication
    - Sets the current user as corresponding author
    - Initializes manuscript in SUBMITTED status
    - Can be created with or without PDF (PDF can be uploaded separately)

    Returns the created manuscript.
    """
    try:
        # Create new manuscript
        new_manuscript = Manuscript(
            title=manuscript_data.title,
            abstract=manuscript_data.abstract,
            keywords=manuscript_data.keywords,
            manuscript_type=manuscript_data.manuscript_type,
            journal_name=manuscript_data.journal_name,
            author_names=manuscript_data.author_names,
            author_affiliations=manuscript_data.author_affiliations,
            corresponding_author_id=UUID(token.user_id),
            status=ManuscriptStatus.SUBMITTED,
            current_round=1,
            submission_date=datetime.utcnow(),
        )

        db.add(new_manuscript)
        await db.commit()
        await db.refresh(new_manuscript)

        # Count reviews (will be 0 for new manuscript)
        review_count_result = await db.execute(
            select(func.count()).select_from(
                select(1).where(
                    # Will need to import PeerReview model
                    # For now, just return 0
                ).subquery()
            )
        )
        review_count = 0

        logger.info(f"Created manuscript {new_manuscript.id}: {new_manuscript.title[:50]}")

        return ManuscriptResponse(
            id=str(new_manuscript.id),
            title=new_manuscript.title,
            abstract=new_manuscript.abstract,
            keywords=new_manuscript.keywords,
            manuscript_type=new_manuscript.manuscript_type.value,
            status=new_manuscript.status.value,
            submission_date=new_manuscript.submission_date,
            journal_name=new_manuscript.journal_name,
            author_names=new_manuscript.author_names,
            author_affiliations=new_manuscript.author_affiliations,
            current_round=new_manuscript.current_round,
            pdf_path=new_manuscript.pdf_path,
            has_pdf=bool(new_manuscript.pdf_path),
            desk_review_decision=new_manuscript.desk_review_decision,
            desk_review_reasoning=new_manuscript.desk_review_reasoning,
            quality_score=new_manuscript.quality_score,
            methodology_score=new_manuscript.methodology_score,
            novelty_score=new_manuscript.novelty_score,
            editorial_decision=new_manuscript.editorial_decision,
            editorial_decision_date=new_manuscript.editorial_decision_date,
            review_count=review_count,
            corresponding_author_id=str(new_manuscript.corresponding_author_id),
            created_at=new_manuscript.created_at,
            updated_at=new_manuscript.updated_at,
        )

    except Exception as e:
        logger.error(f"Error creating manuscript: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create manuscript: {str(e)}"
        )


@router.get("/manuscripts", response_model=ManuscriptListResponse)
async def list_manuscripts(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[ManuscriptStatus] = None,
    manuscript_type: Optional[ManuscriptType] = None,
    journal_name: Optional[str] = None,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    List manuscripts for the current user.

    - Shows only manuscripts where user is corresponding author
    - Supports pagination
    - Supports filtering by status, type, and journal
    - Returns manuscripts ordered by submission date (newest first)
    """
    try:
        # Build query
        query = select(Manuscript).where(
            Manuscript.corresponding_author_id == UUID(token.user_id)
        )

        # Apply filters
        if status_filter:
            query = query.where(Manuscript.status == status_filter)
        if manuscript_type:
            query = query.where(Manuscript.manuscript_type == manuscript_type)
        if journal_name:
            query = query.where(Manuscript.journal_name.ilike(f"%{journal_name}%"))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(Manuscript.submission_date.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        # Execute query
        result = await db.execute(query)
        manuscripts = result.scalars().all()

        # Convert to response models
        manuscript_responses = []
        for manuscript in manuscripts:
            # Count reviews for each manuscript
            from app.models.peer_review import PeerReview
            review_count_result = await db.execute(
                select(func.count()).where(PeerReview.manuscript_id == manuscript.id)
            )
            review_count = review_count_result.scalar() or 0

            manuscript_responses.append(
                ManuscriptResponse(
                    id=str(manuscript.id),
                    title=manuscript.title,
                    abstract=manuscript.abstract,
                    keywords=manuscript.keywords,
                    manuscript_type=manuscript.manuscript_type.value,
                    status=manuscript.status.value,
                    submission_date=manuscript.submission_date,
                    journal_name=manuscript.journal_name,
                    author_names=manuscript.author_names,
                    author_affiliations=manuscript.author_affiliations,
                    current_round=manuscript.current_round,
                    pdf_path=manuscript.pdf_path,
                    has_pdf=bool(manuscript.pdf_path),
                    desk_review_decision=manuscript.desk_review_decision,
                    desk_review_reasoning=manuscript.desk_review_reasoning,
                    quality_score=manuscript.quality_score,
                    methodology_score=manuscript.methodology_score,
                    novelty_score=manuscript.novelty_score,
                    editorial_decision=manuscript.editorial_decision,
                    editorial_decision_date=manuscript.editorial_decision_date,
                    review_count=review_count,
                    corresponding_author_id=str(manuscript.corresponding_author_id),
                    created_at=manuscript.created_at,
                    updated_at=manuscript.updated_at,
                )
            )

        return ManuscriptListResponse(
            total=total,
            manuscripts=manuscript_responses,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        logger.error(f"Error listing manuscripts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list manuscripts: {str(e)}"
        )


@router.get("/manuscripts/{manuscript_id}", response_model=ManuscriptResponse)
async def get_manuscript(
    manuscript_id: str,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get a specific manuscript by ID.

    - Requires authentication
    - Returns 404 if manuscript not found or access denied
    """
    try:
        result = await db.execute(
            select(Manuscript).where(
                Manuscript.id == UUID(manuscript_id),
                Manuscript.corresponding_author_id == UUID(token.user_id)
            )
        )
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscript not found or access denied"
            )

        # Count reviews
        from app.models.peer_review import PeerReview
        review_count_result = await db.execute(
            select(func.count()).where(PeerReview.manuscript_id == manuscript.id)
        )
        review_count = review_count_result.scalar() or 0

        return ManuscriptResponse(
            id=str(manuscript.id),
            title=manuscript.title,
            abstract=manuscript.abstract,
            keywords=manuscript.keywords,
            manuscript_type=manuscript.manuscript_type.value,
            status=manuscript.status.value,
            submission_date=manuscript.submission_date,
            journal_name=manuscript.journal_name,
            author_names=manuscript.author_names,
            author_affiliations=manuscript.author_affiliations,
            current_round=manuscript.current_round,
            pdf_path=manuscript.pdf_path,
            has_pdf=bool(manuscript.pdf_path),
            desk_review_decision=manuscript.desk_review_decision,
            desk_review_reasoning=manuscript.desk_review_reasoning,
            quality_score=manuscript.quality_score,
            methodology_score=manuscript.methodology_score,
            novelty_score=manuscript.novelty_score,
            editorial_decision=manuscript.editorial_decision,
            editorial_decision_date=manuscript.editorial_decision_date,
            review_count=review_count,
            corresponding_author_id=str(manuscript.corresponding_author_id),
            created_at=manuscript.created_at,
            updated_at=manuscript.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting manuscript {manuscript_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get manuscript: {str(e)}"
        )


@router.put("/manuscripts/{manuscript_id}", response_model=ManuscriptResponse)
async def update_manuscript(
    manuscript_id: str,
    manuscript_data: ManuscriptUpdate,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Update a manuscript.

    - Only corresponding author can update
    - Can update title, abstract, keywords, type, journal, authors
    - Cannot update status through this endpoint (use /status endpoint)
    """
    try:
        result = await db.execute(
            select(Manuscript).where(
                Manuscript.id == UUID(manuscript_id),
                Manuscript.corresponding_author_id == UUID(token.user_id)
            )
        )
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscript not found or access denied"
            )

        # Update fields
        update_data = manuscript_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(manuscript, field, value)

        await db.commit()
        await db.refresh(manuscript)

        # Count reviews
        from app.models.peer_review import PeerReview
        review_count_result = await db.execute(
            select(func.count()).where(PeerReview.manuscript_id == manuscript.id)
        )
        review_count = review_count_result.scalar() or 0

        logger.info(f"Updated manuscript {manuscript_id}")

        return ManuscriptResponse(
            id=str(manuscript.id),
            title=manuscript.title,
            abstract=manuscript.abstract,
            keywords=manuscript.keywords,
            manuscript_type=manuscript.manuscript_type.value,
            status=manuscript.status.value,
            submission_date=manuscript.submission_date,
            journal_name=manuscript.journal_name,
            author_names=manuscript.author_names,
            author_affiliations=manuscript.author_affiliations,
            current_round=manuscript.current_round,
            pdf_path=manuscript.pdf_path,
            has_pdf=bool(manuscript.pdf_path),
            desk_review_decision=manuscript.desk_review_decision,
            desk_review_reasoning=manuscript.desk_review_reasoning,
            quality_score=manuscript.quality_score,
            methodology_score=manuscript.methodology_score,
            novelty_score=manuscript.novelty_score,
            editorial_decision=manuscript.editorial_decision,
            editorial_decision_date=manuscript.editorial_decision_date,
            review_count=review_count,
            corresponding_author_id=str(manuscript.corresponding_author_id),
            created_at=manuscript.created_at,
            updated_at=manuscript.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating manuscript {manuscript_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update manuscript: {str(e)}"
        )


@router.put("/manuscripts/{manuscript_id}/status", response_model=ManuscriptResponse)
async def update_manuscript_status(
    manuscript_id: str,
    status_data: ManuscriptStatusUpdate,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Update manuscript status and editorial decision.

    - Tracks editorial decision changes
    - Records decision timestamps
    - Optionally includes decision letter
    """
    try:
        result = await db.execute(
            select(Manuscript).where(
                Manuscript.id == UUID(manuscript_id),
                Manuscript.corresponding_author_id == UUID(token.user_id)
            )
        )
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscript not found or access denied"
            )

        # Update status
        old_status = manuscript.status
        manuscript.status = status_data.status

        # Update editorial decision if status is terminal (accepted/rejected)
        if status_data.status in [ManuscriptStatus.ACCEPTED, ManuscriptStatus.REJECTED]:
            manuscript.editorial_decision = status_data.status.value
            manuscript.editorial_decision_date = datetime.utcnow()
            if status_data.decision_letter:
                manuscript.decision_letter = status_data.decision_letter

        await db.commit()
        await db.refresh(manuscript)

        # Count reviews
        from app.models.peer_review import PeerReview
        review_count_result = await db.execute(
            select(func.count()).where(PeerReview.manuscript_id == manuscript.id)
        )
        review_count = review_count_result.scalar() or 0

        logger.info(f"Updated manuscript {manuscript_id} status: {old_status} -> {status_data.status}")

        return ManuscriptResponse(
            id=str(manuscript.id),
            title=manuscript.title,
            abstract=manuscript.abstract,
            keywords=manuscript.keywords,
            manuscript_type=manuscript.manuscript_type.value,
            status=manuscript.status.value,
            submission_date=manuscript.submission_date,
            journal_name=manuscript.journal_name,
            author_names=manuscript.author_names,
            author_affiliations=manuscript.author_affiliations,
            current_round=manuscript.current_round,
            pdf_path=manuscript.pdf_path,
            has_pdf=bool(manuscript.pdf_path),
            desk_review_decision=manuscript.desk_review_decision,
            desk_review_reasoning=manuscript.desk_review_reasoning,
            quality_score=manuscript.quality_score,
            methodology_score=manuscript.methodology_score,
            novelty_score=manuscript.novelty_score,
            editorial_decision=manuscript.editorial_decision,
            editorial_decision_date=manuscript.editorial_decision_date,
            review_count=review_count,
            corresponding_author_id=str(manuscript.corresponding_author_id),
            created_at=manuscript.created_at,
            updated_at=manuscript.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating manuscript status {manuscript_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update manuscript status: {str(e)}"
        )


@router.delete("/manuscripts/{manuscript_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_manuscript(
    manuscript_id: str,
    token: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Delete a manuscript.

    - Only corresponding author can delete
    - Deletes associated PDF file if exists
    - Cascade deletes all related peer reviews
    """
    try:
        result = await db.execute(
            select(Manuscript).where(
                Manuscript.id == UUID(manuscript_id),
                Manuscript.corresponding_author_id == UUID(token.user_id)
            )
        )
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscript not found or access denied"
            )

        # Delete PDF file if exists
        if manuscript.pdf_path and os.path.exists(manuscript.pdf_path):
            try:
                os.remove(manuscript.pdf_path)
                logger.info(f"Deleted PDF file: {manuscript.pdf_path}")
            except Exception as e:
                logger.warning(f"Failed to delete PDF file {manuscript.pdf_path}: {e}")

        # Delete manuscript (cascade deletes reviews)
        await db.delete(manuscript)
        await db.commit()

        logger.info(f"Deleted manuscript {manuscript_id}")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting manuscript {manuscript_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete manuscript: {str(e)}"
        )
