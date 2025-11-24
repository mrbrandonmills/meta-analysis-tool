"""Meta-analysis API endpoints."""
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentConfig, AgentOrchestrator
from app.agents.specialized import (
    CoordinatorAgent,
    SearchAgent,
    ScreeningAgent,
    FullTextScreeningAgent,
    QAAgent,
    CredibilityAgent,
)
from app.db.session import get_async_db
from app.models.paper import Paper
from app.models.pdf_metadata import PDFMetadata, PDFDownloadStatus, FullTextExtraction, FullTextScreening
from app.models.meta_analysis import MetaAnalysisStatus
from app.services.pdf_download_service import PDFDownloadService
from app.services.pdf_text_extractor import PDFTextExtractor
from app.services.meta_analysis_service import MetaAnalysisService

router = APIRouter()

# Global orchestrator (in production, use dependency injection)
orchestrator = AgentOrchestrator()


class MetaAnalysisRequest(BaseModel):
    """Request to create a new meta-analysis."""

    research_question: str
    topic: str
    inclusion_criteria: List[str] = Field(default_factory=list)
    exclusion_criteria: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=lambda: ["pubmed", "arxiv", "europepmc", "core"])
    peer_review_only: bool = Field(default=False, description="Filter out preprints and non-peer-reviewed studies")
    expert_name: str | None = None


class MetaAnalysisResponse(BaseModel):
    """Response for meta-analysis creation."""

    id: str
    status: str
    message: str
    workflow: Optional[dict] = None


class QuestionRequest(BaseModel):
    """Request to ask a question about a meta-analysis."""

    question: str
    meta_analysis_id: str | None = None


@router.post("/meta-analysis/create", response_model=MetaAnalysisResponse)
async def create_meta_analysis(
    request: MetaAnalysisRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new meta-analysis.

    This endpoint:
    1. Creates database record for meta-analysis
    2. Returns the analysis ID

    Note: Workflow planning happens in the /execute endpoint.
    """
    try:
        logger.info(f"Creating meta-analysis: {request.topic}")

        # Initialize service
        service = MetaAnalysisService(db)

        # TODO: Get user_id from authentication
        # For now, use first user if no authentication (development only)
        from app.models.user import User
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            # Create a default user for development
            user = User(
                email="default@example.com",
                hashed_password="dummy",
                full_name="Default User",
            )
            db.add(user)
            await db.flush()
            logger.info("Created default user for development")

        # Create meta-analysis database record
        meta_analysis = await service.create_meta_analysis(
            user_id=user.id,
            research_question=request.research_question,
            topic=request.topic,
            inclusion_criteria=request.inclusion_criteria,
            exclusion_criteria=request.exclusion_criteria,
            databases=request.databases,
            peer_review_only=request.peer_review_only,
            expert_name=request.expert_name,
        )

        # Commit the meta-analysis record
        await db.commit()

        logger.info(f"Created meta-analysis {meta_analysis.id}")

        return MetaAnalysisResponse(
            id=str(meta_analysis.id),
            status="created",
            message="Meta-analysis created successfully. Use /execute endpoint to run the workflow.",
            workflow=None,
        )

    except Exception as e:
        logger.error(f"Error creating meta-analysis: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meta-analysis/execute/{analysis_id}")
async def execute_meta_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_async_db),
):
    """Execute a meta-analysis workflow.

    This endpoint:
    1. Retrieves coordinator state from database
    2. Runs the search agent
    3. Runs the screening agent
    4. Persists all agent executions
    5. Returns preliminary results
    """
    try:
        logger.info(f"Executing meta-analysis: {analysis_id}")

        # Initialize service
        service = MetaAnalysisService(db)

        # Get meta-analysis from database
        analysis_uuid = UUID(analysis_id)
        meta_analysis = await service.get_meta_analysis(analysis_uuid)
        if not meta_analysis:
            logger.error(f"Meta-analysis not found: {analysis_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Meta-analysis not found. Analysis ID: {analysis_id}"
            )

        # Restore coordinator from database
        coordinator_config = AgentConfig(
            name="Coordinator",
            role="coordinator",  # type: ignore
            expert_profile=meta_analysis.expert_name,
        )
        coordinator = await service.restore_coordinator(analysis_uuid, coordinator_config)
        if not coordinator:
            logger.error(f"Coordinator state not found for analysis_id: {analysis_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Coordinator state not found. Analysis ID: {analysis_id}"
            )

        # Update status to in_progress
        await service.update_meta_analysis_status(analysis_uuid, MetaAnalysisStatus.IN_PROGRESS)

        # Initialize search agent
        search_config = AgentConfig(name="SearchAgent", role="search")  # type: ignore
        search_agent = SearchAgent(search_config)
        orchestrator.register_agent(search_agent)

        # Get research question from coordinator's last decision
        if not coordinator.decisions:
            raise HTTPException(status_code=400, detail="No workflow found")

        # Execute search
        search_input = {
            "research_question": meta_analysis.research_question,
            "search_terms": ["mindfulness", "anxiety", "RCT"],  # TODO: Extract from workflow
            "databases": meta_analysis.databases or ["pubmed"],
        }
        search_results = await search_agent.process(search_input)

        # Log search agent execution
        await service.log_agent_execution(
            analysis_id=analysis_uuid,
            agent_name=search_agent.config.name,
            agent_role="search",
            agent_id=search_agent.id,
            input_data=search_input,
            output_data=search_results,
            status="success",
        )

        # Initialize screening agent
        screening_config = AgentConfig(name="ScreeningAgent", role="screening")  # type: ignore
        screening_agent = ScreeningAgent(screening_config)
        orchestrator.register_agent(screening_agent)

        # Execute screening
        screening_input = {
            "studies": search_results["studies"],
            "inclusion_criteria": meta_analysis.inclusion_criteria or [
                "Randomized controlled trial",
                "Adult population (18+)",
                "Mindfulness-based intervention",
                "Anxiety as outcome measure",
            ],
            "exclusion_criteria": meta_analysis.exclusion_criteria or [
                "Non-English language",
                "Qualitative studies",
                "Case studies",
            ],
            "screening_level": "title_abstract",
        }
        screening_results = await screening_agent.process(screening_input)

        # Log screening agent execution
        await service.log_agent_execution(
            analysis_id=analysis_uuid,
            agent_name=screening_agent.config.name,
            agent_role="screening",
            agent_id=screening_agent.id,
            input_data=screening_input,
            output_data=screening_results,
            status="success",
        )

        # Initialize credibility agent
        credibility_config = AgentConfig(name="CredibilityAgent", role="quality_assessment")  # type: ignore
        credibility_agent = CredibilityAgent(credibility_config)
        orchestrator.register_agent(credibility_agent)

        # Evaluate credibility of included studies
        credibility_input = {
            "studies": screening_results["included"],
            "require_peer_review": meta_analysis.peer_review_only == "true",
        }
        credibility_results = await credibility_agent.process(credibility_input)

        # Log credibility agent execution
        await service.log_agent_execution(
            analysis_id=analysis_uuid,
            agent_name=credibility_agent.config.name,
            agent_role="quality_assessment",
            agent_id=credibility_agent.id,
            input_data=credibility_input,
            output_data=credibility_results,
            status="success",
        )

        # Update coordinator state with progress
        await service.save_coordinator_state(
            analysis_id=analysis_uuid,
            coordinator=coordinator,
        )

        # Commit all changes
        await db.commit()

        return {
            "analysis_id": analysis_id,
            "status": "in_progress",
            "search_results": {
                "total_found": search_results["total_results"],
                "databases": search_results["databases_searched"],
            },
            "screening_results": {
                "total_screened": screening_results["total_screened"],
                "included": len(screening_results["included"]),
                "excluded": len(screening_results["excluded"]),
                "uncertain": len(screening_results["uncertain"]),
            },
            "credibility_results": {
                "total_evaluated": credibility_results["total_evaluated"],
                "breakdown": credibility_results["credibility_breakdown"],
                "studies_with_scores": credibility_results["studies"],
            },
            "next_steps": [
                "Full-text screening",
                "Quality assessment",
                "Data extraction",
            ],
        }

    except Exception as e:
        logger.error(f"Error executing meta-analysis: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta-analysis/status/{analysis_id}")
async def get_status(analysis_id: str, db: AsyncSession = Depends(get_async_db)):
    """Get the status of a meta-analysis from database."""
    try:
        service = MetaAnalysisService(db)

        # Get meta-analysis from database
        analysis_uuid = UUID(analysis_id)
        meta_analysis = await service.get_meta_analysis(analysis_uuid)
        if not meta_analysis:
            logger.error(f"Meta-analysis not found: {analysis_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Meta-analysis not found. Analysis ID: {analysis_id}"
            )

        # Get coordinator state
        coordinator_state = await service.get_coordinator_state(analysis_uuid)

        return {
            "id": analysis_id,
            "status": meta_analysis.status.value,
            "decisions": len(coordinator_state.decisions) if coordinator_state else 0,
            "created_at": meta_analysis.created_at.isoformat(),
            "updated_at": meta_analysis.updated_at.isoformat(),
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid analysis ID format")
    except Exception as e:
        logger.error(f"Error getting meta-analysis status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta-analysis/audit/{analysis_id}")
async def get_audit_trail(analysis_id: str):
    """Get the complete audit trail for a meta-analysis."""
    try:
        audit = orchestrator.get_audit_trail()
        return audit

    except Exception as e:
        logger.error(f"Error getting audit trail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meta-analysis/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question about a meta-analysis.

    This uses the Q&A agent to answer questions about
    the process, methodology, or results.
    """
    try:
        logger.info(f"Question asked: {request.question}")

        # Initialize Q&A agent
        qa_config = AgentConfig(name="QAAgent", role="qa")  # type: ignore
        qa_agent = QAAgent(qa_config)

        # Get context from orchestrator
        context = orchestrator.get_audit_trail()

        # Update Q&A agent with context
        qa_agent.update_context(context)

        # Process question
        result = await qa_agent.process({
            "question": request.question,
            "meta_analysis_id": request.meta_analysis_id,
            "context": context,
        })

        return {
            "question": request.question,
            "answer": result["answer"],
            "confidence": result["confidence"],
            "sources": result.get("sources_cited", []),
            "follow_up_suggestions": result.get("follow_up_suggestions", []),
        }

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta-analysis/report/{analysis_id}")
async def get_report(analysis_id: str):
    """Get the final report for a meta-analysis."""
    # This would generate an APA-formatted report
    return {
        "id": analysis_id,
        "status": "report_ready",
        "format": "APA 7th edition",
        "sections": [
            "Abstract",
            "Introduction",
            "Methods",
            "Results",
            "Discussion",
            "References",
        ],
    }


# ============================================================================
# PDF DOWNLOAD AND FULL-TEXT ANALYSIS ENDPOINTS
# ============================================================================


class PDFDownloadRequest(BaseModel):
    """Request to download PDFs for studies."""

    paper_ids: Optional[List[str]] = Field(None, description="Specific paper IDs to download. If not provided, downloads all included studies.")
    max_concurrent: int = Field(default=5, ge=1, le=10, description="Maximum concurrent downloads")


class PDFDownloadResponse(BaseModel):
    """Response for PDF download request."""

    analysis_id: str
    status: str
    total: int
    success: int
    failed: int
    paywall: int
    already_downloaded: int
    message: str


class PDFStatusResponse(BaseModel):
    """Response for PDF status check."""

    analysis_id: str
    total_papers: int
    downloaded: int
    pending: int
    failed: int
    paywall: int
    extraction_completed: int
    extraction_pending: int
    download_stats: List[Dict]


class FullTextScreeningRequest(BaseModel):
    """Request for full-text screening."""

    inclusion_criteria: List[str] = Field(..., description="Inclusion criteria")
    exclusion_criteria: List[str] = Field(..., description="Exclusion criteria")
    study_type: Optional[str] = Field(None, description="Expected study type (e.g., 'RCT')")
    outcome_measures: List[str] = Field(default_factory=list, description="Expected outcome measures")


class FullTextScreeningResponse(BaseModel):
    """Response for full-text screening."""

    analysis_id: str
    total_screened: int
    included: int
    excluded: int
    uncertain: int
    quality_summary: Dict
    message: str


@router.post("/meta-analysis/download-pdfs/{analysis_id}", response_model=PDFDownloadResponse)
async def download_pdfs(
    analysis_id: str,
    request: PDFDownloadRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Download PDFs for studies in a meta-analysis.

    This endpoint:
    1. Retrieves included studies from the analysis
    2. Downloads PDFs from multiple sources (PMC, arXiv, etc.)
    3. Tracks download status and errors
    4. Returns statistics

    Note: For large batches, consider using the background task endpoint.
    """
    try:
        logger.info(f"Starting PDF download for analysis {analysis_id}")

        # Get papers to download
        if request.paper_ids:
            result = await db.execute(select(Paper).where(Paper.id.in_(request.paper_ids)))
            papers = result.scalars().all()
        else:
            # Get all papers for this analysis (simplified - in production, link to Project)
            # For now, get papers that don't have PDFs yet
            result = await db.execute(
                select(Paper)
                .outerjoin(PDFMetadata, Paper.id == PDFMetadata.paper_id)
                .where(
                    (PDFMetadata.id == None) |
                    (PDFMetadata.download_status != PDFDownloadStatus.SUCCESS)
                )
                .limit(100)  # Safety limit
            )
            papers = result.scalars().all()

        if not papers:
            return PDFDownloadResponse(
                analysis_id=analysis_id,
                status="no_papers",
                total=0,
                success=0,
                failed=0,
                paywall=0,
                already_downloaded=0,
                message="No papers found to download"
            )

        # Initialize download service
        download_service = PDFDownloadService(db)

        # Download PDFs
        stats = download_service.batch_download(papers, max_concurrent=request.max_concurrent)

        return PDFDownloadResponse(
            analysis_id=analysis_id,
            status="completed",
            total=stats["total"],
            success=stats["success"],
            failed=stats["failed"],
            paywall=stats["paywall"],
            already_downloaded=stats["already_downloaded"],
            message=f"Downloaded {stats['success']} of {stats['total']} PDFs"
        )

    except Exception as e:
        logger.error(f"Error downloading PDFs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta-analysis/pdf-status/{analysis_id}", response_model=PDFStatusResponse)
async def get_pdf_status(analysis_id: str, db: AsyncSession = Depends(get_async_db)):
    """Get PDF download and extraction status for an analysis.

    Returns statistics about:
    - Total papers in analysis
    - Download success/failure/pending
    - Text extraction status
    - Individual paper statuses
    """
    try:
        logger.info(f"Checking PDF status for analysis {analysis_id}")

        # Get all PDF metadata (simplified - should filter by analysis)
        result = await db.execute(select(PDFMetadata))
        pdf_metadata_list = result.scalars().all()

        # Calculate statistics
        total = len(pdf_metadata_list)
        downloaded = sum(
            1 for m in pdf_metadata_list
            if m.download_status == PDFDownloadStatus.SUCCESS
        )
        pending = sum(
            1 for m in pdf_metadata_list
            if m.download_status == PDFDownloadStatus.PENDING
        )
        failed = sum(
            1 for m in pdf_metadata_list
            if m.download_status == PDFDownloadStatus.FAILED
        )
        paywall = sum(
            1 for m in pdf_metadata_list
            if m.download_status == PDFDownloadStatus.PAYWALL
        )
        extraction_completed = sum(
            1 for m in pdf_metadata_list
            if m.extraction_status == "completed"
        )
        extraction_pending = sum(
            1 for m in pdf_metadata_list
            if m.extraction_status == "pending"
        )

        # Get detailed stats per paper
        download_stats = []
        for metadata in pdf_metadata_list[:50]:  # Limit to first 50
            download_stats.append({
                "paper_id": str(metadata.paper_id),
                "download_status": metadata.download_status.value,
                "extraction_status": metadata.extraction_status,
                "pdf_source": metadata.pdf_source.value if metadata.pdf_source else None,
                "file_size_bytes": metadata.file_size_bytes,
                "page_count": metadata.page_count,
            })

        return PDFStatusResponse(
            analysis_id=analysis_id,
            total_papers=total,
            downloaded=downloaded,
            pending=pending,
            failed=failed,
            paywall=paywall,
            extraction_completed=extraction_completed,
            extraction_pending=extraction_pending,
            download_stats=download_stats,
        )

    except Exception as e:
        logger.error(f"Error getting PDF status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meta-analysis/extract-text/{analysis_id}")
async def extract_text(analysis_id: str, db: AsyncSession = Depends(get_async_db)):
    """Extract text from downloaded PDFs.

    This endpoint:
    1. Finds all successfully downloaded PDFs
    2. Extracts text and detects sections
    3. Stores structured text in database
    4. Returns extraction statistics
    """
    try:
        logger.info(f"Starting text extraction for analysis {analysis_id}")

        # Get PDFs ready for extraction
        result = await db.execute(
            select(PDFMetadata)
            .where(
                PDFMetadata.download_status == PDFDownloadStatus.SUCCESS,
                PDFMetadata.extraction_status.in_(["pending", "failed"])
            )
        )
        pdf_metadata_list = result.scalars().all()

        if not pdf_metadata_list:
            return {
                "analysis_id": analysis_id,
                "status": "no_pdfs",
                "message": "No PDFs available for extraction"
            }

        # Initialize extraction service
        extractor = PDFTextExtractor(db)

        # Extract text from PDFs
        stats = extractor.batch_extract(pdf_metadata_list)

        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "total": stats["total"],
            "success": stats["success"],
            "failed": stats["failed"],
            "requires_ocr": stats["requires_ocr"],
            "message": f"Extracted text from {stats['success']} of {stats['total']} PDFs"
        }

    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meta-analysis/full-text-screen/{analysis_id}", response_model=FullTextScreeningResponse)
async def full_text_screen(
    analysis_id: str,
    request: FullTextScreeningRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Perform full-text screening using extracted text.

    This endpoint:
    1. Retrieves extracted full texts
    2. Applies FullTextScreeningAgent for detailed analysis
    3. Extracts PICO components and study quality indicators
    4. Stores screening results
    5. Returns comprehensive screening statistics
    """
    try:
        logger.info(f"Starting full-text screening for analysis {analysis_id}")

        # Get all full-text extractions
        result = await db.execute(
            select(FullTextExtraction)
            .join(PDFMetadata)
            .where(PDFMetadata.extraction_status == "completed")
        )
        extractions = result.scalars().all()

        if not extractions:
            raise HTTPException(
                status_code=400,
                detail="No full-text extractions available. Please extract text first."
            )

        # Initialize full-text screening agent
        agent_config = AgentConfig(
            name="FullTextScreeningAgent",
            role="screening"  # type: ignore
        )
        screening_agent = FullTextScreeningAgent(agent_config)
        orchestrator.register_agent(screening_agent)

        # Perform screening
        screening_input = {
            "extractions": extractions,
            "inclusion_criteria": request.inclusion_criteria,
            "exclusion_criteria": request.exclusion_criteria,
            "study_type": request.study_type,
            "outcome_measures": request.outcome_measures,
        }

        results = await screening_agent.process(screening_input)

        # Store screening results in database
        for study in results["included"] + results["excluded"] + results["uncertain"]:
            extraction = study  # Assuming study is the extraction object
            result = study.get("screening_result", {})

            screening_record = FullTextScreening(
                full_text_extraction_id=extraction.id,
                paper_id=extraction.pdf_metadata.paper_id,
                decision=result["decision"],
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                pico_extraction=result.get("pico_extraction", {}),
                study_quality_indicators=result.get("study_quality_indicators", {}),
                data_extraction_preview=result.get("data_extraction_preview", {}),
                inclusion_criteria_met=result.get("inclusion_criteria_met", []),
                exclusion_criteria_violated=result.get("exclusion_criteria_violated", []),
                needs_human_review=result["needs_human_review"],
                has_concerns=len(result.get("concerns", [])) > 0,
                concern_details=result.get("concerns", []),
                screening_agent_id=str(screening_agent.id),
            )
            db.add(screening_record)

        await db.commit()

        return FullTextScreeningResponse(
            analysis_id=analysis_id,
            total_screened=results["total_screened"],
            included=len(results["included"]),
            excluded=len(results["excluded"]),
            uncertain=len(results["uncertain"]),
            quality_summary=results["quality_summary"],
            message=f"Screened {results['total_screened']} full-text studies"
        )

    except Exception as e:
        logger.error(f"Error in full-text screening: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta-analysis/study/{study_id}/full-text")
async def get_study_full_text(study_id: str, db: AsyncSession = Depends(get_async_db)):
    """Get full-text extraction and screening results for a study.

    Returns:
    - Extracted text with sections
    - Statistics and study characteristics
    - Screening decision and reasoning
    - PICO components
    - Quality indicators
    """
    try:
        # Get paper
        result = await db.execute(select(Paper).where(Paper.id == study_id))
        paper = result.scalar_one_or_none()
        if not paper:
            raise HTTPException(status_code=404, detail="Study not found")

        # Get PDF metadata
        result = await db.execute(
            select(PDFMetadata)
            .where(PDFMetadata.paper_id == study_id)
        )
        pdf_metadata = result.scalar_one_or_none()

        if not pdf_metadata:
            return {
                "study_id": study_id,
                "status": "no_pdf",
                "message": "No PDF downloaded for this study"
            }

        # Get extraction
        result = await db.execute(
            select(FullTextExtraction)
            .where(FullTextExtraction.pdf_metadata_id == pdf_metadata.id)
        )
        extraction = result.scalar_one_or_none()

        if not extraction:
            return {
                "study_id": study_id,
                "status": "not_extracted",
                "pdf_status": pdf_metadata.download_status.value,
                "message": "Text not yet extracted from PDF"
            }

        # Get screening results
        result = await db.execute(
            select(FullTextScreening)
            .where(FullTextScreening.full_text_extraction_id == extraction.id)
        )
        screening = result.scalar_one_or_none()

        return {
            "study_id": study_id,
            "paper": {
                "title": paper.title,
                "authors": paper.authors,
                "year": paper.year,
                "journal": paper.journal,
                "doi": paper.doi,
            },
            "pdf_metadata": {
                "download_status": pdf_metadata.download_status.value,
                "pdf_source": pdf_metadata.pdf_source.value if pdf_metadata.pdf_source else None,
                "page_count": pdf_metadata.page_count,
                "file_size_bytes": pdf_metadata.file_size_bytes,
            },
            "extraction": {
                "word_count": extraction.word_count,
                "sections": extraction.sections,
                "tables_detected": extraction.tables_detected,
                "figures_detected": extraction.figures_detected,
                "references_count": extraction.references_count,
                "extraction_quality": extraction.extraction_quality,
                "statistics_found": extraction.statistics_found,
                "study_design_mentions": extraction.study_design_mentions,
                "intervention_mentions": extraction.intervention_mentions,
                "outcome_measures": extraction.outcome_measures,
            },
            "screening": {
                "decision": screening.decision if screening else None,
                "confidence": screening.confidence if screening else None,
                "reasoning": screening.reasoning if screening else None,
                "pico_extraction": screening.pico_extraction if screening else None,
                "study_quality_indicators": screening.study_quality_indicators if screening else None,
                "data_extraction_preview": screening.data_extraction_preview if screening else None,
                "needs_human_review": screening.needs_human_review if screening else None,
                "concerns": screening.concern_details if screening else None,
            } if screening else None,
        }

    except Exception as e:
        logger.error(f"Error getting full text: {e}")
        raise HTTPException(status_code=500, detail=str(e))
