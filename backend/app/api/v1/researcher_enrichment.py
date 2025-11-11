"""Researcher Enrichment API endpoints.

Provides endpoints for enriching researcher profiles with data from:
- Google Scholar
- ORCID
- Semantic Scholar
- Claude AI analysis
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_token, TokenData, require_researcher
from app.db.session import get_async_db
from app.models.researcher import Researcher
from app.services.researcher_profile_enricher import create_enricher

router = APIRouter()


# Pydantic schemas
class EnrichmentRequest(BaseModel):
    """Request schema for enrichment."""

    force_refresh: bool = Field(
        default=False,
        description="Force re-enrichment even if recently enriched"
    )


class BatchEnrichmentRequest(BaseModel):
    """Request schema for batch enrichment."""

    researcher_ids: List[str] = Field(
        ...,
        min_items=1,
        max_items=50,
        description="List of researcher IDs to enrich (max 50)"
    )
    force_refresh: bool = Field(
        default=False,
        description="Force re-enrichment for all researchers"
    )


class EnrichmentResponse(BaseModel):
    """Response schema for enrichment results."""

    researcher_id: str
    researcher_name: str
    sources_checked: List[str]
    data_found: dict
    errors: List[str]
    completeness_score: float
    completeness_percentage: str
    status: str  # "success", "partial", "failed"


class BatchEnrichmentResponse(BaseModel):
    """Response schema for batch enrichment."""

    total_requested: int
    successful: int
    failed: int
    results: List[EnrichmentResponse]


class CompletenessResponse(BaseModel):
    """Response schema for profile completeness."""

    researcher_id: str
    researcher_name: str
    completeness_score: float
    completeness_percentage: str
    missing_fields: List[str]
    recommendations: List[str]


@router.post(
    "/researchers/{researcher_id}/enrich",
    response_model=EnrichmentResponse,
    summary="Enrich researcher profile",
    description="Trigger enrichment for a single researcher from academic data sources"
)
async def enrich_researcher(
    researcher_id: str,
    request: EnrichmentRequest = EnrichmentRequest(),
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(require_researcher),
):
    """
    Enrich a researcher profile with data from multiple academic sources.

    This endpoint will:
    1. Search Google Scholar for h-index, citations, publications
    2. Fetch ORCID profile if ORCID ID is available
    3. Search Semantic Scholar for additional metadata
    4. Use Claude AI to analyze publications and extract domains/keywords
    5. Calculate profile completeness score

    The process respects rate limits for each API and implements retry logic.

    Returns enrichment results including:
    - Sources checked
    - Data found from each source
    - Any errors encountered
    - Updated completeness score
    """
    try:
        # Validate UUID
        try:
            researcher_uuid = UUID(researcher_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid researcher ID format"
            )

        # Check researcher exists
        result = await db.execute(
            select(Researcher).where(Researcher.id == researcher_uuid)
        )
        researcher = result.scalar_one_or_none()

        if not researcher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Researcher not found: {researcher_id}"
            )

        # Check if recently enriched (skip if force_refresh=False)
        if not request.force_refresh and researcher.researcher_metadata:
            last_enrichment = researcher.researcher_metadata.get("last_enrichment")
            if last_enrichment:
                logger.info(f"Researcher recently enriched: {last_enrichment}")
                # Could add time-based check here

        # Create enricher and run enrichment
        enricher = create_enricher()
        try:
            enrichment_data = await enricher.enrich_researcher_profile(
                researcher_uuid,
                db
            )

            # Determine status
            if enrichment_data["errors"]:
                if enrichment_data["sources_checked"]:
                    status_value = "partial"
                else:
                    status_value = "failed"
            else:
                status_value = "success"

            return EnrichmentResponse(
                researcher_id=enrichment_data["researcher_id"],
                researcher_name=enrichment_data["researcher_name"],
                sources_checked=enrichment_data["sources_checked"],
                data_found=enrichment_data["data_found"],
                errors=enrichment_data["errors"],
                completeness_score=enrichment_data["completeness_score"],
                completeness_percentage=enrichment_data["completeness_percentage"],
                status=status_value
            )

        finally:
            await enricher.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enriching researcher {researcher_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enrichment failed: {str(e)}"
        )


async def _enrich_single_researcher(
    researcher_id: UUID,
    db: AsyncSession,
    force_refresh: bool = False
) -> EnrichmentResponse:
    """Helper function to enrich a single researcher.

    Args:
        researcher_id: UUID of researcher
        db: Database session
        force_refresh: Whether to force refresh

    Returns:
        EnrichmentResponse with results
    """
    enricher = create_enricher()
    try:
        enrichment_data = await enricher.enrich_researcher_profile(
            researcher_id,
            db
        )

        # Determine status
        if enrichment_data["errors"]:
            if enrichment_data["sources_checked"]:
                status_value = "partial"
            else:
                status_value = "failed"
        else:
            status_value = "success"

        return EnrichmentResponse(
            researcher_id=enrichment_data["researcher_id"],
            researcher_name=enrichment_data["researcher_name"],
            sources_checked=enrichment_data["sources_checked"],
            data_found=enrichment_data["data_found"],
            errors=enrichment_data["errors"],
            completeness_score=enrichment_data["completeness_score"],
            completeness_percentage=enrichment_data["completeness_percentage"],
            status=status_value
        )

    except Exception as e:
        logger.error(f"Error enriching researcher {researcher_id}: {e}")
        return EnrichmentResponse(
            researcher_id=str(researcher_id),
            researcher_name="Unknown",
            sources_checked=[],
            data_found={},
            errors=[str(e)],
            completeness_score=0.0,
            completeness_percentage="0.0%",
            status="failed"
        )
    finally:
        await enricher.close()


@router.post(
    "/researchers/batch-enrich",
    response_model=BatchEnrichmentResponse,
    summary="Batch enrich researchers",
    description="Enrich multiple researchers in a single request"
)
async def batch_enrich_researchers(
    request: BatchEnrichmentRequest,
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(require_researcher),
):
    """
    Enrich multiple researchers in batch.

    This is useful for:
    - Initial database population
    - Periodic refresh of researcher profiles
    - Post-import enrichment from journal data

    Maximum 50 researchers per request to prevent timeouts.
    Each researcher is enriched sequentially to respect API rate limits.

    Returns summary of results including success/failure counts.
    """
    try:
        results = []
        successful = 0
        failed = 0

        logger.info(f"Starting batch enrichment for {len(request.researcher_ids)} researchers")

        for researcher_id_str in request.researcher_ids:
            try:
                researcher_id = UUID(researcher_id_str)

                # Check researcher exists
                result = await db.execute(
                    select(Researcher).where(Researcher.id == researcher_id)
                )
                researcher = result.scalar_one_or_none()

                if not researcher:
                    logger.warning(f"Researcher not found: {researcher_id_str}")
                    results.append(EnrichmentResponse(
                        researcher_id=researcher_id_str,
                        researcher_name="Not Found",
                        sources_checked=[],
                        data_found={},
                        errors=["Researcher not found"],
                        completeness_score=0.0,
                        completeness_percentage="0.0%",
                        status="failed"
                    ))
                    failed += 1
                    continue

                # Enrich researcher
                enrichment_result = await _enrich_single_researcher(
                    researcher_id,
                    db,
                    request.force_refresh
                )

                results.append(enrichment_result)

                if enrichment_result.status == "success":
                    successful += 1
                elif enrichment_result.status == "partial":
                    successful += 1  # Count partial as success
                else:
                    failed += 1

            except ValueError:
                logger.error(f"Invalid UUID format: {researcher_id_str}")
                results.append(EnrichmentResponse(
                    researcher_id=researcher_id_str,
                    researcher_name="Invalid ID",
                    sources_checked=[],
                    data_found={},
                    errors=["Invalid UUID format"],
                    completeness_score=0.0,
                    completeness_percentage="0.0%",
                    status="failed"
                ))
                failed += 1
            except Exception as e:
                logger.error(f"Error enriching {researcher_id_str}: {e}")
                results.append(EnrichmentResponse(
                    researcher_id=researcher_id_str,
                    researcher_name="Error",
                    sources_checked=[],
                    data_found={},
                    errors=[str(e)],
                    completeness_score=0.0,
                    completeness_percentage="0.0%",
                    status="failed"
                ))
                failed += 1

        logger.info(
            f"Batch enrichment complete: {successful} successful, {failed} failed"
        )

        return BatchEnrichmentResponse(
            total_requested=len(request.researcher_ids),
            successful=successful,
            failed=failed,
            results=results
        )

    except Exception as e:
        logger.error(f"Batch enrichment error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch enrichment failed: {str(e)}"
        )


@router.get(
    "/researchers/{researcher_id}/completeness",
    response_model=CompletenessResponse,
    summary="Get profile completeness",
    description="Calculate and return profile completeness score with recommendations"
)
async def get_profile_completeness(
    researcher_id: str,
    db: AsyncSession = Depends(get_async_db),
    token: TokenData = Depends(get_current_user_token),
):
    """
    Get profile completeness score for a researcher.

    Returns:
    - Completeness score (0.0-1.0)
    - Percentage representation
    - List of missing fields
    - Recommendations for improving completeness

    This is useful for:
    - Showing users their profile completion status
    - Determining if a researcher is eligible for reviewer matching
    - Identifying gaps in researcher data
    """
    try:
        # Validate UUID
        try:
            researcher_uuid = UUID(researcher_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid researcher ID format"
            )

        # Get researcher
        result = await db.execute(
            select(Researcher).where(Researcher.id == researcher_uuid)
        )
        researcher = result.scalar_one_or_none()

        if not researcher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Researcher not found: {researcher_id}"
            )

        # Calculate completeness
        enricher = create_enricher()
        try:
            completeness_score = await enricher.calculate_profile_completeness(researcher)
        finally:
            await enricher.close()

        # Identify missing fields
        missing_fields = []
        recommendations = []

        if not researcher.name:
            missing_fields.append("name")
        if not researcher.email:
            missing_fields.append("email")
        if not researcher.institution:
            missing_fields.append("institution")
            recommendations.append("Add your institutional affiliation")

        if researcher.h_index is None or researcher.h_index == 0:
            missing_fields.append("h_index")
            recommendations.append("Run profile enrichment to fetch your h-index from Google Scholar")

        if not researcher.research_domains or len(researcher.research_domains) == 0:
            missing_fields.append("research_domains")
            recommendations.append("Add research domains to improve reviewer matching")

        if not researcher.expertise_keywords or len(researcher.expertise_keywords) == 0:
            missing_fields.append("expertise_keywords")
            recommendations.append("Add expertise keywords to your profile")

        publications = researcher.researcher_metadata.get("publications", []) if researcher.researcher_metadata else []
        if not publications:
            missing_fields.append("publications")
            recommendations.append("Run profile enrichment to import your publications")

        if not researcher.orcid:
            missing_fields.append("orcid")
            recommendations.append("Add your ORCID ID for better data integration")

        if researcher.total_citations == 0:
            missing_fields.append("total_citations")

        if not researcher.coauthor_ids or len(researcher.coauthor_ids) == 0:
            missing_fields.append("coauthor_network")

        # Add general recommendation if score is low
        if completeness_score < 0.8:
            recommendations.insert(
                0,
                "Run profile enrichment to automatically populate missing fields from academic databases"
            )

        return CompletenessResponse(
            researcher_id=str(researcher.id),
            researcher_name=researcher.name,
            completeness_score=completeness_score,
            completeness_percentage=f"{completeness_score * 100:.1f}%",
            missing_fields=missing_fields,
            recommendations=recommendations
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating completeness for {researcher_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate completeness: {str(e)}"
        )
