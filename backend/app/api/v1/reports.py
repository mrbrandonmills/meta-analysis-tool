"""Report generation API endpoints for meta-analysis."""

from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from loguru import logger
from sqlalchemy.orm import Session

from app.services.apa_report_generator import APAReportGenerator
from app.models.report import Report, ReportTemplate, ReportFormat, ReportStatus
from app.db.base import get_db

router = APIRouter()


class ReportGenerationRequest(BaseModel):
    """Request model for generating a report."""

    format: str = Field(default="docx", description="Report format: 'docx', 'pdf', or 'both'")
    title: str = Field(..., description="Report title")
    authors: List[str] = Field(default_factory=list, description="List of author names")
    institution: Optional[str] = Field(None, description="Institution name")
    author_note: Optional[str] = Field(None, description="Author note or acknowledgments")
    keywords: List[str] = Field(default_factory=list, description="Keywords for the report")
    custom_sections: Optional[Dict[str, str]] = Field(None, description="Custom content for sections")


class ReportCustomizationRequest(BaseModel):
    """Request model for customizing a report."""

    title: Optional[str] = None
    authors: Optional[List[str]] = None
    institution: Optional[str] = None
    author_note: Optional[str] = None
    keywords: Optional[List[str]] = None
    custom_sections: Optional[Dict[str, str]] = None


class ReportResponse(BaseModel):
    """Response model for report operations."""

    id: int
    analysis_id: str
    title: str
    format: str
    status: str
    docx_path: Optional[str] = None
    pdf_path: Optional[str] = None
    generated_at: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str


class TemplateCreateRequest(BaseModel):
    """Request model for creating a report template."""

    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    sections: Dict[str, Any] = Field(..., description="Section configurations")
    style_config: Optional[Dict[str, Any]] = Field(None, description="Custom styling options")
    is_public: bool = Field(False, description="Whether template is public")


class TemplateResponse(BaseModel):
    """Response model for report templates."""

    id: int
    name: str
    description: Optional[str]
    sections: Dict[str, Any]
    style_config: Optional[Dict[str, Any]]
    is_public: bool
    created_at: str
    updated_at: str


# Initialize report generator (in production, use dependency injection)
report_generator = APAReportGenerator()


def get_analysis_data(analysis_id: str, db: Session) -> Dict[str, Any]:
    """Fetch analysis data from database or coordinator.

    Args:
        analysis_id: ID of the meta-analysis
        db: Database session

    Returns:
        Dictionary containing analysis data
    """
    # TODO: Fetch from actual database once meta-analysis models are integrated
    # For now, return mock data
    logger.info(f"Fetching analysis data for {analysis_id}")

    return {
        "id": analysis_id,
        "title": "Effects of Mindfulness-Based Interventions on Anxiety: A Meta-Analysis",
        "topic": "mindfulness and anxiety",
        "research_question": "What is the effect of mindfulness-based interventions on anxiety levels in adults?",
        "num_studies": 25,
        "num_participants": 1847,
        "num_identified": 458,
        "num_screened": 156,
        "pooled_effect_size": 0.63,
        "ci_lower": 0.48,
        "ci_upper": 0.78,
        "p_value": 0.001,
        "i_squared": 42.3,
        "year_range": "2010-2024",
        "search_date": "January 15, 2024",
        "databases": ["PubMed", "PsycINFO", "Web of Science", "Cochrane Library"],
        "search_terms": ["mindfulness", "mindfulness-based", "MBSR", "MBCT", "anxiety", "anxious"],
        "inclusion_criteria": [
            "Randomized controlled trials (RCTs)",
            "Adult participants (age 18+)",
            "Mindfulness-based intervention",
            "Validated anxiety outcome measure",
            "Published in peer-reviewed journals",
        ],
        "exclusion_criteria": [
            "Non-English language publications",
            "Qualitative studies",
            "Case studies or case series",
            "Insufficient statistical data",
        ],
        "analysis_method": "random-effects model",
        "keywords": ["meta-analysis", "mindfulness", "anxiety", "RCT", "systematic review"],
        "limitations": [
            "Limited to English-language publications",
            "Moderate heterogeneity across studies (I² = 42.3%)",
            "Potential publication bias cannot be ruled out",
            "Variability in intervention duration and format",
        ],
        "studies": [
            {
                "authors": ["Hofmann, S. G.", "Sawyer, A. T.", "Witt, A. A."],
                "year": 2010,
                "title": "The effect of mindfulness-based therapy on anxiety and depression",
                "journal": "Journal of Consulting and Clinical Psychology",
                "volume": 78,
                "issue": 2,
                "pages": "169-183",
                "doi": "10.1037/a0018555",
                "sample_size": 209,
                "design": "RCT",
                "effect_size": 0.59,
                "ci_lower": 0.23,
                "ci_upper": 0.95,
                "standard_error": 0.18,
                "quality_rating": "High",
            },
            {
                "authors": ["Khoury, B.", "Lecomte, T.", "Fortin, G."],
                "year": 2013,
                "title": "Mindfulness-based therapy: A comprehensive meta-analysis",
                "journal": "Clinical Psychology Review",
                "volume": 33,
                "issue": 6,
                "pages": "763-771",
                "doi": "10.1016/j.cpr.2013.05.005",
                "sample_size": 142,
                "design": "RCT",
                "effect_size": 0.71,
                "ci_lower": 0.42,
                "ci_upper": 1.00,
                "standard_error": 0.15,
                "quality_rating": "High",
            },
            {
                "authors": ["Goyal, M.", "Singh, S.", "Sibinga, E. M."],
                "year": 2014,
                "title": "Meditation programs for psychological stress and well-being",
                "journal": "JAMA Internal Medicine",
                "volume": 174,
                "issue": 3,
                "pages": "357-368",
                "doi": "10.1001/jamainternmed.2013.13018",
                "sample_size": 186,
                "design": "RCT",
                "effect_size": 0.38,
                "ci_lower": 0.12,
                "ci_upper": 0.64,
                "standard_error": 0.13,
                "quality_rating": "Moderate",
            },
            {
                "authors": ["Hoge, E. A.", "Bui, E.", "Marques, L."],
                "year": 2013,
                "title": "Randomized controlled trial of mindfulness meditation for anxiety disorder",
                "journal": "Journal of Clinical Psychiatry",
                "volume": 74,
                "issue": 8,
                "pages": "786-792",
                "doi": "10.4088/JCP.12m08083",
                "sample_size": 89,
                "design": "RCT",
                "effect_size": 0.89,
                "ci_lower": 0.48,
                "ci_upper": 1.30,
                "standard_error": 0.21,
                "quality_rating": "High",
            },
            {
                "authors": ["Kuyken, W.", "Hayes, R.", "Barrett, B."],
                "year": 2015,
                "title": "Effectiveness of mindfulness-based cognitive therapy in prevention of depressive relapse",
                "journal": "The Lancet",
                "volume": 386,
                "issue": 9988,
                "pages": "63-73",
                "doi": "10.1016/S0140-6736(14)62222-4",
                "sample_size": 424,
                "design": "RCT",
                "effect_size": 0.42,
                "ci_lower": 0.18,
                "ci_upper": 0.66,
                "standard_error": 0.12,
                "quality_rating": "High",
            },
        ],
    }


@router.post("/meta-analysis/generate-report/{analysis_id}", response_model=ReportResponse)
async def generate_report(
    analysis_id: str,
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Generate an APA-formatted report for a meta-analysis.

    This endpoint:
    1. Validates the analysis exists
    2. Creates a report record
    3. Generates Word and/or PDF documents
    4. Returns report metadata with download links
    """
    try:
        logger.info(f"Generating report for analysis {analysis_id}")

        # Validate format
        if request.format not in ["docx", "pdf", "both"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid format. Must be 'docx', 'pdf', or 'both'"
            )

        # Get analysis data
        analysis_data = get_analysis_data(analysis_id, db)

        # Override with custom data from request
        if request.title:
            analysis_data["title"] = request.title
        if request.authors:
            analysis_data["authors"] = request.authors
        if request.institution:
            analysis_data["institution"] = request.institution
        if request.author_note:
            analysis_data["author_note"] = request.author_note
        if request.keywords:
            analysis_data["keywords"] = request.keywords

        # Create report record in database
        report = Report(
            analysis_id=analysis_id,
            title=request.title,
            format=ReportFormat(request.format),
            status=ReportStatus.GENERATING,
            authors=request.authors,
            institution=request.institution,
            author_note=request.author_note,
            keywords=request.keywords,
            custom_sections=request.custom_sections,
            num_studies=analysis_data.get("num_studies"),
            pooled_effect_size=str(analysis_data.get("pooled_effect_size", "")),
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        # Generate report documents
        try:
            result = report_generator.generate_report(
                analysis_data=analysis_data,
                format=request.format,
                custom_sections=request.custom_sections,
            )

            # Update report record with file paths
            if "docx_path" in result:
                report.docx_path = result["docx_path"]
            if "pdf_path" in result:
                report.pdf_path = result["pdf_path"]

            report.status = ReportStatus.COMPLETED
            report.generated_at = result["generated_at"]

        except Exception as e:
            logger.error(f"Error generating report documents: {e}")
            report.status = ReportStatus.FAILED
            report.error_message = str(e)

        db.commit()
        db.refresh(report)

        # Generate visualizations in background
        background_tasks.add_task(
            generate_visualizations,
            analysis_id,
            analysis_data.get("studies", []),
        )

        return ReportResponse(**report.to_dict())

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def generate_visualizations(analysis_id: str, studies: List[Dict[str, Any]]):
    """Background task to generate forest and funnel plots.

    Args:
        analysis_id: ID of the meta-analysis
        studies: List of study data
    """
    try:
        logger.info(f"Generating visualizations for analysis {analysis_id}")

        # Generate forest plot
        report_generator.generate_forest_plot(studies)

        # Generate funnel plot
        report_generator.generate_funnel_plot(studies)

        logger.info(f"Visualizations generated for analysis {analysis_id}")

    except Exception as e:
        logger.error(f"Error generating visualizations: {e}")


@router.get("/meta-analysis/report/{report_id}", response_model=ReportResponse)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get report metadata by ID.

    Args:
        report_id: Report ID
        db: Database session

    Returns:
        Report metadata
    """
    try:
        report = db.query(Report).filter(Report.id == report_id).first()

        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        return ReportResponse(**report.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta-analysis/report/{report_id}/download")
async def download_report(
    report_id: int,
    format: str = "docx",
    db: Session = Depends(get_db),
):
    """Download a generated report file.

    Args:
        report_id: Report ID
        format: File format to download ('docx' or 'pdf')
        db: Database session

    Returns:
        File download response
    """
    try:
        # Get report from database
        report = db.query(Report).filter(Report.id == report_id).first()

        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        if report.status != ReportStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Report is not ready. Current status: {report.status.value}"
            )

        # Get file path based on format
        if format == "docx":
            file_path = report.docx_path
        elif format == "pdf":
            file_path = report.pdf_path
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Must be 'docx' or 'pdf'")

        if not file_path or not Path(file_path).exists():
            raise HTTPException(
                status_code=404,
                detail=f"Report file not found for format: {format}"
            )

        # Determine media type
        media_type = (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            if format == "docx"
            else "application/pdf"
        )

        # Return file
        filename = Path(file_path).name
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meta-analysis/report/{report_id}/customize", response_model=ReportResponse)
async def customize_report(
    report_id: int,
    request: ReportCustomizationRequest,
    db: Session = Depends(get_db),
):
    """Customize an existing report and regenerate.

    Args:
        report_id: Report ID
        request: Customization parameters
        db: Database session

    Returns:
        Updated report metadata
    """
    try:
        # Get report from database
        report = db.query(Report).filter(Report.id == report_id).first()

        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Update report metadata
        if request.title:
            report.title = request.title
        if request.authors:
            report.authors = request.authors
        if request.institution:
            report.institution = request.institution
        if request.author_note:
            report.author_note = request.author_note
        if request.keywords:
            report.keywords = request.keywords
        if request.custom_sections:
            report.custom_sections = request.custom_sections

        report.status = ReportStatus.GENERATING

        db.commit()
        db.refresh(report)

        # Get analysis data and regenerate
        analysis_data = get_analysis_data(report.analysis_id, db)

        # Override with custom data
        if report.title:
            analysis_data["title"] = report.title
        if report.authors:
            analysis_data["authors"] = report.authors
        if report.institution:
            analysis_data["institution"] = report.institution
        if report.author_note:
            analysis_data["author_note"] = report.author_note
        if report.keywords:
            analysis_data["keywords"] = report.keywords

        # Regenerate documents
        try:
            result = report_generator.generate_report(
                analysis_data=analysis_data,
                format=report.format.value,
                custom_sections=report.custom_sections,
            )

            # Update file paths
            if "docx_path" in result:
                report.docx_path = result["docx_path"]
            if "pdf_path" in result:
                report.pdf_path = result["pdf_path"]

            report.status = ReportStatus.COMPLETED
            report.generated_at = result["generated_at"]

        except Exception as e:
            logger.error(f"Error regenerating report: {e}")
            report.status = ReportStatus.FAILED
            report.error_message = str(e)

        db.commit()
        db.refresh(report)

        return ReportResponse(**report.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error customizing report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meta-analysis/reports/analysis/{analysis_id}", response_model=List[ReportResponse])
async def list_reports_by_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
):
    """List all reports for a specific analysis.

    Args:
        analysis_id: Meta-analysis ID
        db: Database session

    Returns:
        List of report metadata
    """
    try:
        reports = db.query(Report).filter(Report.analysis_id == analysis_id).all()

        return [ReportResponse(**report.to_dict()) for report in reports]

    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Template Management Endpoints

@router.post("/report-templates", response_model=TemplateResponse)
async def create_template(
    request: TemplateCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a new report template.

    Args:
        request: Template creation parameters
        db: Database session

    Returns:
        Created template metadata
    """
    try:
        # Check if template name already exists
        existing = db.query(ReportTemplate).filter(ReportTemplate.name == request.name).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Template with name '{request.name}' already exists"
            )

        # Create template
        template = ReportTemplate(
            name=request.name,
            description=request.description,
            sections=request.sections,
            style_config=request.style_config,
            is_public=1 if request.is_public else 0,
        )

        db.add(template)
        db.commit()
        db.refresh(template)

        return TemplateResponse(**template.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report-templates", response_model=List[TemplateResponse])
async def list_templates(
    public_only: bool = True,
    db: Session = Depends(get_db),
):
    """List available report templates.

    Args:
        public_only: Only show public templates
        db: Database session

    Returns:
        List of template metadata
    """
    try:
        query = db.query(ReportTemplate)

        if public_only:
            query = query.filter(ReportTemplate.is_public == 1)

        templates = query.all()

        return [TemplateResponse(**template.to_dict()) for template in templates]

    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report-templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific report template.

    Args:
        template_id: Template ID
        db: Database session

    Returns:
        Template metadata
    """
    try:
        template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        return TemplateResponse(**template.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/report-templates/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
):
    """Delete a report template.

    Args:
        template_id: Template ID
        db: Database session

    Returns:
        Success message
    """
    try:
        template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        db.delete(template)
        db.commit()

        return {"message": "Template deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {e}")
        raise HTTPException(status_code=500, detail=str(e))
