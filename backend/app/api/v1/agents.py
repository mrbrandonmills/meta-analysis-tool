"""Agents API endpoints."""
from fastapi import APIRouter
from loguru import logger

from app.agents.base import AgentRole

router = APIRouter()


@router.get("/agents/available")
async def list_available_agents():
    """List all available agent types."""
    return {
        "agents": [
            {
                "role": AgentRole.COORDINATOR,
                "name": "Coordinator Agent",
                "description": "Orchestrates the entire meta-analysis workflow",
                "capabilities": [
                    "Workflow planning",
                    "Task delegation",
                    "Result synthesis",
                ],
            },
            {
                "role": AgentRole.SEARCH,
                "name": "Search Agent",
                "description": "Searches academic databases for relevant studies",
                "capabilities": [
                    "PubMed search",
                    "Query construction",
                    "Deduplication",
                ],
            },
            {
                "role": AgentRole.SCREENING,
                "name": "Screening Agent",
                "description": "Applies inclusion/exclusion criteria",
                "capabilities": [
                    "Title/abstract screening",
                    "Full-text screening",
                    "PRISMA flow generation",
                ],
            },
            {
                "role": AgentRole.QUALITY_ASSESSMENT,
                "name": "Quality Assessment Agent",
                "description": "Evaluates study quality and risk of bias",
                "capabilities": [
                    "Cochrane risk of bias",
                    "Newcastle-Ottawa scale",
                    "Quality scoring",
                ],
            },
            {
                "role": AgentRole.DATA_EXTRACTION,
                "name": "Data Extraction Agent",
                "description": "Extracts data from studies",
                "capabilities": [
                    "Effect size extraction",
                    "Sample size extraction",
                    "Statistical data extraction",
                ],
            },
            {
                "role": AgentRole.STATISTICAL,
                "name": "Statistical Agent",
                "description": "Performs meta-analysis calculations",
                "capabilities": [
                    "Random/fixed effects models",
                    "Heterogeneity assessment",
                    "Forest plot generation",
                ],
            },
            {
                "role": AgentRole.REPORT,
                "name": "Report Agent",
                "description": "Generates publication-ready reports",
                "capabilities": [
                    "APA formatting",
                    "Citation management",
                    "Figure generation",
                ],
            },
            {
                "role": AgentRole.QA,
                "name": "Q&A Agent",
                "description": "Answers questions about the analysis",
                "capabilities": [
                    "Natural language Q&A",
                    "Explainability",
                    "Provenance tracking",
                ],
            },
            {
                "role": AgentRole.VERIFICATION,
                "name": "Verification Agent",
                "description": "Validates results against known meta-analyses",
                "capabilities": [
                    "Result validation",
                    "Confidence scoring",
                    "Discrepancy detection",
                ],
            },
        ]
    }


@router.get("/agents/profile/{agent_name}")
async def get_agent_profile(agent_name: str):
    """Get detailed profile for a specific agent."""
    # This would return expert information, version, etc.
    return {
        "name": agent_name,
        "version": "0.1.0",
        "expert_profile": {
            "name": "Dr. Jane Smith",
            "institution": "University Research Lab",
            "credentials": "PhD in Psychology, 15 years meta-analysis experience",
            "specialty": "Systematic reviews and meta-analysis methodology",
        },
        "programming_date": "2025-11-04",
        "capabilities": ["Task-specific capabilities..."],
        "limitations": ["Known limitations..."],
    }
