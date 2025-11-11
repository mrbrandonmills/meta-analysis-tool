"""Background tasks for meta-analysis calculations."""

import asyncio
from typing import List, Dict, Any, Optional
from uuid import UUID
from celery import Task
from loguru import logger

from app.workers.celery_app import celery_app
from app.agents.specialized.statistical_agent import StatisticalAgent, EffectSizeCalculator
from app.agents.base import AgentConfig, AgentRole
from app.agents.base.orchestrator import AgentOrchestrator
from app.agents.specialized.coordinator import CoordinatorAgent
from app.agents.specialized.search import SearchAgent
from app.agents.specialized.screening import ScreeningAgent
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.meta_analysis import MetaAnalysis, MetaAnalysisStatus
from app.models.paper import Paper

settings = get_settings()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


@celery_app.task(
    name="app.workers.tasks.meta_analysis.calculate_effect_sizes",
    max_retries=2,
)
def calculate_effect_sizes(study_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate effect sizes for studies using the StatisticalAgent.

    This task processes study data and calculates standardized effect sizes
    (Cohen's d, Hedge's g, odds ratios, risk ratios) based on the type of data provided.

    Args:
        study_data: List of dicts with study statistics. Each dict should contain:
            - study_id: Unique identifier
            - study_name: Study name (optional)
            - effect_type: "continuous", "binary", or "correlation"

            For continuous outcomes:
                - mean_treatment, mean_control
                - sd_treatment, sd_control
                - n_treatment, n_control
                - es_method: "cohens_d" or "hedges_g" (default: hedges_g)

            For binary outcomes:
                - events_treatment, events_control
                - n_treatment, n_control
                - es_method: "odds_ratio" or "risk_ratio" (default: odds_ratio)

            For correlations:
                - correlation: Correlation coefficient
                - n: Sample size

    Returns:
        Dict with:
            - status: "completed" or "failed"
            - study_count: Number of studies processed
            - effect_sizes: List of effect size calculations
            - errors: List of any errors encountered
    """
    try:
        logger.info(f"Calculating effect sizes for {len(study_data)} studies")

        # Create StatisticalAgent configuration
        config = AgentConfig(
            name="effect_size_calculator",
            role=AgentRole.STATISTICAL,
            model=settings.openai_model,
            temperature=0.3
        )

        # Initialize effect size calculator
        calculator = EffectSizeCalculator()
        effect_sizes = []
        errors = []

        for i, study in enumerate(study_data):
            try:
                study_id = study.get("study_id", f"Study_{i+1}")
                study_name = study.get("study_name", f"Study {i+1}")
                effect_type = study.get("effect_type", "continuous")

                logger.info(f"Calculating effect size for {study_id} (type: {effect_type})")

                # Calculate based on effect type
                if effect_type == "continuous":
                    es_method = study.get("es_method", "hedges_g")

                    if es_method == "cohens_d":
                        result = calculator.cohens_d(
                            study["mean_treatment"],
                            study["mean_control"],
                            study["sd_treatment"],
                            study["sd_control"],
                            study["n_treatment"],
                            study["n_control"]
                        )
                    else:  # hedges_g (default, bias-corrected)
                        result = calculator.hedges_g(
                            study["mean_treatment"],
                            study["mean_control"],
                            study["sd_treatment"],
                            study["sd_control"],
                            study["n_treatment"],
                            study["n_control"]
                        )

                elif effect_type == "binary":
                    es_method = study.get("es_method", "odds_ratio")

                    if es_method == "risk_ratio":
                        result = calculator.risk_ratio(
                            study["events_treatment"],
                            study["n_treatment"],
                            study["events_control"],
                            study["n_control"]
                        )
                    else:  # odds_ratio (default)
                        result = calculator.odds_ratio(
                            study["events_treatment"],
                            study["n_treatment"],
                            study["events_control"],
                            study["n_control"]
                        )

                elif effect_type == "correlation":
                    result = calculator.fishers_z(
                        study["correlation"],
                        study["n"]
                    )
                else:
                    raise ValueError(f"Unknown effect_type: {effect_type}")

                # Add study metadata to result
                result["study_id"] = study_id
                result["study_name"] = study_name
                result["effect_type"] = effect_type

                effect_sizes.append(result)
                logger.info(f"Effect size calculated for {study_id}: {result['effect_size']:.4f}")

            except Exception as e:
                error_msg = f"Error calculating effect size for study {i}: {str(e)}"
                logger.error(error_msg)
                errors.append({
                    "study_index": i,
                    "study_id": study.get("study_id", f"Study_{i+1}"),
                    "error": str(e)
                })

        logger.info(f"Effect size calculation completed: {len(effect_sizes)} successful, {len(errors)} errors")

        return {
            "status": "completed" if len(effect_sizes) > 0 else "failed",
            "study_count": len(study_data),
            "successful_count": len(effect_sizes),
            "error_count": len(errors),
            "effect_sizes": effect_sizes,
            "errors": errors,
        }

    except Exception as exc:
        logger.exception(f"Effect size calculation task failed: {exc}")
        raise


@celery_app.task(
    name="app.workers.tasks.meta_analysis.run_meta_analysis",
    max_retries=2,
    soft_time_limit=1800,  # 30 minutes
)
def run_meta_analysis(
    effect_sizes: List[Dict],
    method: str = "random",
    tau_method: str = "DL"
) -> Dict[str, Any]:
    """
    Run meta-analysis calculations using StatisticalAgent.

    This task performs the complete meta-analysis including:
    - Fixed-effects or random-effects pooling
    - Heterogeneity assessment (Q, I², τ²)
    - Publication bias assessment (Egger's test)
    - Forest plot data generation
    - LLM-powered interpretation

    Args:
        effect_sizes: List of effect size dicts (output from calculate_effect_sizes)
        method: "fixed" or "random" (default: "random")
        tau_method: "DL" (DerSimonian-Laird) or "REML" (default: "DL")

    Returns:
        Dict with complete meta-analysis results:
            - meta_analysis: Pooled effect, CI, p-value, weights
            - heterogeneity: Q, I², τ², interpretation
            - publication_bias: Egger's test, funnel plot data
            - forest_plot: Data for visualization
            - interpretation: AI-generated interpretation
    """
    try:
        logger.info(f"Running meta-analysis with {len(effect_sizes)} effect sizes using {method} effects")

        # Create StatisticalAgent
        config = AgentConfig(
            name="meta_analysis_calculator",
            role=AgentRole.STATISTICAL,
            model=settings.openai_model,
            temperature=0.3
        )

        statistical_agent = StatisticalAgent(config)

        # Determine effect type from first study
        effect_type = effect_sizes[0].get("effect_type", "continuous") if effect_sizes else "continuous"

        # Prepare input for StatisticalAgent
        input_data = {
            "studies": effect_sizes,
            "effect_type": effect_type,
            "model": method,
            "tau_method": tau_method
        }

        # Run the meta-analysis asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(statistical_agent.process(input_data))
        finally:
            loop.close()

        logger.info(f"Meta-analysis completed successfully")
        logger.info(f"Pooled effect: {result['meta_analysis']['pooled_effect']:.4f}")
        logger.info(f"I² = {result['heterogeneity']['i_squared']:.1f}%")

        return {
            "status": "completed",
            "method": method,
            "tau_method": tau_method,
            **result
        }

    except Exception as exc:
        logger.exception(f"Meta-analysis task failed: {exc}")
        raise


@celery_app.task(
    name="app.workers.tasks.meta_analysis.extract_data_from_studies",
    max_retries=2,
)
def extract_data_from_studies(paper_ids: List[str]) -> Dict[str, Any]:
    """
    Extract statistical data from study papers for meta-analysis.

    This task reads papers from the database and extracts:
    - Sample sizes
    - Means and standard deviations
    - Event counts for binary outcomes
    - Correlations
    - Effect sizes (if pre-reported)
    - P-values and confidence intervals

    Args:
        paper_ids: List of paper UUIDs to extract data from

    Returns:
        Dict with:
            - status: "completed" or "partial"
            - extracted_count: Number of papers with extracted data
            - study_data: List of extracted statistics ready for effect size calculation
            - errors: List of extraction errors
    """
    try:
        logger.info(f"Extracting data from {len(paper_ids)} papers")

        db = get_db()
        extracted_data = []
        errors = []

        for paper_id in paper_ids:
            try:
                # Fetch paper from database
                paper = db.query(Paper).filter(Paper.id == paper_id).first()

                if not paper:
                    logger.warning(f"Paper {paper_id} not found in database")
                    errors.append({
                        "paper_id": paper_id,
                        "error": "Paper not found"
                    })
                    continue

                # Check if paper has extracted statistics
                if not paper.extracted_statistics:
                    logger.warning(f"Paper {paper_id} has no extracted statistics")
                    errors.append({
                        "paper_id": paper_id,
                        "title": paper.title,
                        "error": "No extracted statistics available"
                    })
                    continue

                # Parse extracted statistics
                stats = paper.extracted_statistics

                # Construct study data dict
                study_data = {
                    "study_id": str(paper.id),
                    "study_name": paper.title[:100] if paper.title else f"Paper {paper_id}",
                    "authors": paper.authors,
                    "year": paper.year,
                    "journal": paper.journal,
                }

                # Determine effect type and add relevant statistics
                if "mean_treatment" in stats and "mean_control" in stats:
                    # Continuous outcome
                    study_data.update({
                        "effect_type": "continuous",
                        "mean_treatment": float(stats["mean_treatment"]),
                        "mean_control": float(stats["mean_control"]),
                        "sd_treatment": float(stats.get("sd_treatment", stats.get("std_treatment", 0))),
                        "sd_control": float(stats.get("sd_control", stats.get("std_control", 0))),
                        "n_treatment": int(stats.get("n_treatment", stats.get("sample_size_treatment", 0))),
                        "n_control": int(stats.get("n_control", stats.get("sample_size_control", 0))),
                    })

                elif "events_treatment" in stats and "events_control" in stats:
                    # Binary outcome
                    study_data.update({
                        "effect_type": "binary",
                        "events_treatment": int(stats["events_treatment"]),
                        "events_control": int(stats["events_control"]),
                        "n_treatment": int(stats.get("n_treatment", 0)),
                        "n_control": int(stats.get("n_control", 0)),
                    })

                elif "correlation" in stats:
                    # Correlation
                    study_data.update({
                        "effect_type": "correlation",
                        "correlation": float(stats["correlation"]),
                        "n": int(stats.get("n", stats.get("sample_size", 0))),
                    })

                elif "effect_size" in stats:
                    # Pre-calculated effect size
                    study_data.update({
                        "effect_type": stats.get("effect_type", "continuous"),
                        "effect_size": float(stats["effect_size"]),
                        "standard_error": float(stats.get("standard_error", stats.get("se", 0))),
                        "variance": float(stats.get("variance", 0)),
                    })

                else:
                    logger.warning(f"Paper {paper_id} has unrecognized statistics format")
                    errors.append({
                        "paper_id": paper_id,
                        "title": paper.title,
                        "error": "Unrecognized statistics format",
                        "available_fields": list(stats.keys())
                    })
                    continue

                extracted_data.append(study_data)
                logger.info(f"Extracted data from paper {paper_id}: {study_data['effect_type']}")

            except Exception as e:
                error_msg = f"Error extracting data from paper {paper_id}: {str(e)}"
                logger.error(error_msg)
                errors.append({
                    "paper_id": paper_id,
                    "error": str(e)
                })

        logger.info(f"Data extraction completed: {len(extracted_data)} successful, {len(errors)} errors")

        return {
            "status": "completed" if len(extracted_data) > 0 else "failed",
            "total_papers": len(paper_ids),
            "extracted_count": len(extracted_data),
            "error_count": len(errors),
            "study_data": extracted_data,
            "errors": errors,
        }

    except Exception as exc:
        logger.exception(f"Data extraction task failed: {exc}")
        raise


@celery_app.task(
    name="app.workers.tasks.meta_analysis.run_complete_meta_analysis_workflow",
    max_retries=1,
    soft_time_limit=3600,  # 60 minutes
)
def run_complete_meta_analysis_workflow(meta_analysis_id: str) -> Dict[str, Any]:
    """
    Orchestrate the complete meta-analysis workflow from start to finish.

    This is the master task that coordinates all agents:
    1. CoordinatorAgent - Creates workflow plan
    2. SearchAgent - Literature search
    3. ScreeningAgent - Study screening
    4. StatisticalAgent - Data extraction and analysis
    5. ReportAgent - Final report generation

    Args:
        meta_analysis_id: UUID of the MetaAnalysis record

    Returns:
        Dict with complete workflow results and status
    """
    try:
        logger.info(f"Starting complete meta-analysis workflow for {meta_analysis_id}")

        # Get database session
        db = get_db()

        # Fetch meta-analysis record
        meta_analysis = db.query(MetaAnalysis).filter(
            MetaAnalysis.id == meta_analysis_id
        ).first()

        if not meta_analysis:
            raise ValueError(f"MetaAnalysis {meta_analysis_id} not found")

        # Update status
        meta_analysis.status = MetaAnalysisStatus.IN_PROGRESS
        db.commit()

        # Initialize AgentOrchestrator
        orchestrator = AgentOrchestrator()

        # Create and register agents
        coordinator_config = AgentConfig(
            name="coordinator",
            role=AgentRole.COORDINATOR,
            model=settings.openai_model,
            temperature=0.5
        )
        coordinator = CoordinatorAgent(coordinator_config)
        orchestrator.register_agent(coordinator)

        # Prepare input data for coordinator
        input_data = {
            "research_question": meta_analysis.research_question,
            "topic": meta_analysis.topic,
            "inclusion_criteria": meta_analysis.inclusion_criteria or [],
            "exclusion_criteria": meta_analysis.exclusion_criteria or [],
            "databases": meta_analysis.databases or ["pubmed", "arxiv"],
            "meta_analysis_id": str(meta_analysis.id)
        }

        # Run coordinator asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            workflow_result = loop.run_until_complete(coordinator.process(input_data))
        finally:
            loop.close()

        # Update meta-analysis with results
        meta_analysis.status = MetaAnalysisStatus.COMPLETED
        db.commit()

        logger.info(f"Complete meta-analysis workflow finished for {meta_analysis_id}")

        return {
            "status": "completed",
            "meta_analysis_id": str(meta_analysis.id),
            "workflow_result": workflow_result,
        }

    except Exception as exc:
        logger.exception(f"Complete meta-analysis workflow failed: {exc}")

        # Update status to failed
        try:
            db = get_db()
            meta_analysis = db.query(MetaAnalysis).filter(
                MetaAnalysis.id == meta_analysis_id
            ).first()
            if meta_analysis:
                meta_analysis.status = MetaAnalysisStatus.FAILED
                db.commit()
        except Exception:
            pass

        raise
