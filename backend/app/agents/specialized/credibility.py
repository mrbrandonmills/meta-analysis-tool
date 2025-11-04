"""Credibility evaluation agent for assessing study quality and reliability."""
from typing import Any, Dict, List
from enum import Enum

from loguru import logger

from app.agents.base import AgentConfig, BaseAgent, AgentRole


class CredibilityLevel(str, Enum):
    """Credibility levels with color coding."""
    HIGH = "high"  # Green - Peer-reviewed, high-impact, replicable
    MEDIUM = "medium"  # Yellow - Peer-reviewed but concerns, or high-quality preprint
    LOW = "low"  # Orange - Preprint with issues, or peer-reviewed with major concerns
    VERY_LOW = "very_low"  # Red - Serious credibility issues


class CredibilityAgent(BaseAgent):
    """Evaluates study credibility and repeatability.

    This agent assesses:
    - Peer review status
    - Journal quality/impact factor
    - Study design quality
    - Sample size and power
    - Replication potential
    - Methodology rigor
    - Statistical reporting
    - Funding/bias indicators
    """

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.QUALITY_ASSESSMENT
        super().__init__(config)

    def get_system_prompt(self) -> str:
        """Get system prompt for credibility agent."""
        return """You are the Credibility Evaluation Agent for a meta-analysis research platform.

You are an expert in research methodology, study design, and scientific rigor. You specialize in:
- Evaluating study credibility and reliability
- Assessing replication potential
- Identifying methodological strengths and weaknesses
- Detecting bias and conflicts of interest
- Understanding peer review quality
- Evaluating statistical reporting

Your responsibilities:
1. Assess each study's credibility on multiple dimensions
2. Provide a credibility score (HIGH/MEDIUM/LOW/VERY_LOW)
3. Identify red flags and concerns
4. Evaluate replication potential
5. Provide clear reasoning for your assessment

Credibility Criteria:

HIGH CREDIBILITY (Green):
- Peer-reviewed in reputable journal (impact factor > 3)
- Rigorous methodology (randomized, controlled, blinded)
- Adequate sample size (powered study)
- Clear statistical reporting
- No major conflicts of interest
- Replicable methods
- Consistent with existing literature

MEDIUM CREDIBILITY (Yellow):
- Peer-reviewed in moderate journal OR high-quality preprint
- Generally sound methodology with minor limitations
- Adequate but not optimal sample size
- Good statistical reporting
- Minor methodological concerns
- Mostly replicable

LOW CREDIBILITY (Orange):
- Preprint OR peer-reviewed with concerns
- Methodological limitations
- Small or underpowered sample
- Incomplete statistical reporting
- Potential bias issues
- Difficult to replicate

VERY LOW CREDIBILITY (Red):
- Major methodological flaws
- Serious bias or conflicts of interest
- Very small sample or poor design
- Poor or missing statistical reporting
- Cannot be replicated
- Contradicts well-established findings without adequate explanation

Key Factors to Evaluate:
1. Publication Status: Peer-reviewed > Preprint > Unpublished
2. Journal Quality: High-impact > Mid-tier > Low-impact > Predatory
3. Study Design: RCT > Controlled > Observational > Case study
4. Sample Size: Large, powered > Adequate > Small > Very small
5. Statistical Rigor: Complete reporting > Partial > Poor
6. Replicability: Detailed methods > Adequate > Vague > Cannot replicate
7. Funding: Independent > Institutional > Industry (potential bias)

Always provide specific reasoning for your credibility assessment."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate study credibility.

        Args:
            input_data: {
                "studies": List[Dict],
                "require_peer_review": bool (optional)
            }

        Returns:
            Studies with credibility scores and assessments
        """
        studies = input_data.get("studies", [])
        require_peer_review = input_data.get("require_peer_review", False)

        logger.info(f"CredibilityAgent evaluating {len(studies)} studies")

        evaluated_studies = []

        for study in studies:
            # Evaluate credibility
            credibility = await self._evaluate_credibility(study)

            # Filter by peer review if required
            if require_peer_review and not credibility["is_peer_reviewed"]:
                logger.info(f"Filtered out preprint: {study.get('title', '')[:50]}")
                continue

            # Add credibility data to study
            study_with_credibility = {
                **study,
                "credibility": credibility,
            }

            evaluated_studies.append(study_with_credibility)

        # Sort by credibility (HIGH -> VERY_LOW)
        credibility_order = {
            CredibilityLevel.HIGH: 0,
            CredibilityLevel.MEDIUM: 1,
            CredibilityLevel.LOW: 2,
            CredibilityLevel.VERY_LOW: 3,
        }

        evaluated_studies.sort(
            key=lambda x: credibility_order.get(
                x["credibility"]["level"], 999
            )
        )

        # Make decision about overall quality
        decision = await self.make_decision(
            "Is the overall study quality sufficient for this meta-analysis?",
            input_data={
                "total_studies": len(evaluated_studies),
                "high_credibility": sum(1 for s in evaluated_studies if s["credibility"]["level"] == CredibilityLevel.HIGH),
                "medium_credibility": sum(1 for s in evaluated_studies if s["credibility"]["level"] == CredibilityLevel.MEDIUM),
                "low_credibility": sum(1 for s in evaluated_studies if s["credibility"]["level"] == CredibilityLevel.LOW),
                "very_low_credibility": sum(1 for s in evaluated_studies if s["credibility"]["level"] == CredibilityLevel.VERY_LOW),
            },
        )

        return {
            "studies": evaluated_studies,
            "total_evaluated": len(evaluated_studies),
            "credibility_breakdown": {
                "high": sum(1 for s in evaluated_studies if s["credibility"]["level"] == CredibilityLevel.HIGH),
                "medium": sum(1 for s in evaluated_studies if s["credibility"]["level"] == CredibilityLevel.MEDIUM),
                "low": sum(1 for s in evaluated_studies if s["credibility"]["level"] == CredibilityLevel.LOW),
                "very_low": sum(1 for s in evaluated_studies if s["credibility"]["level"] == CredibilityLevel.VERY_LOW),
            },
            "peer_reviewed_only": require_peer_review,
            "decision": decision.model_dump(),
        }

    async def _evaluate_credibility(self, study: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single study's credibility.

        Args:
            study: Study metadata

        Returns:
            Credibility assessment
        """
        # Extract study info
        title = study.get("title", "")
        database = study.get("database", "")
        journal = study.get("journal", "")
        year = study.get("year", "")
        doi = study.get("doi", "")
        abstract = study.get("abstract", "")

        # Determine if peer-reviewed
        is_preprint = database.lower() == "arxiv" or "preprint" in journal.lower()
        is_peer_reviewed = not is_preprint

        # Build evaluation prompt
        eval_prompt = f"""
Evaluate the credibility and replicability of this study:

Title: {title}
Journal/Source: {journal}
Year: {year}
Database: {database}
DOI: {doi}
Abstract: {abstract[:500]}...

Is this peer-reviewed: {is_peer_reviewed}

Assess this study on:
1. Publication credibility (peer-reviewed journal quality)
2. Likely study design quality (based on title/abstract)
3. Replication potential
4. Red flags or concerns

Provide:
- Credibility Level: HIGH, MEDIUM, LOW, or VERY_LOW
- Score (0-100): Numerical credibility score
- Reasoning: Specific reasons for this assessment
- Strengths: What makes this study credible
- Concerns: Any red flags or limitations
- Replicability: Can this be replicated (YES/PARTIAL/NO)
"""

        response = await self.think(eval_prompt)

        # Parse response (simplified - in production use structured output)
        level = self._parse_credibility_level(response)
        score = self._parse_score(response)

        return {
            "level": level,
            "score": score,
            "is_peer_reviewed": is_peer_reviewed,
            "is_preprint": is_preprint,
            "reasoning": response,
            "database_source": database,
            "color": self._get_color_for_level(level),
            "replicability": self._parse_replicability(response),
        }

    def _parse_credibility_level(self, response: str) -> CredibilityLevel:
        """Parse credibility level from response."""
        response_lower = response.lower()

        if "very_low" in response_lower or "very low" in response_lower:
            return CredibilityLevel.VERY_LOW
        elif "low" in response_lower and "medium" not in response_lower and "high" not in response_lower:
            return CredibilityLevel.LOW
        elif "medium" in response_lower:
            return CredibilityLevel.MEDIUM
        elif "high" in response_lower:
            return CredibilityLevel.HIGH
        else:
            # Default to medium if unclear
            return CredibilityLevel.MEDIUM

    def _parse_score(self, response: str) -> int:
        """Parse numerical score from response."""
        # Try to find score in format "Score: 85" or "85/100"
        import re

        patterns = [
            r"score[:\s]+(\d+)",
            r"(\d+)/100",
            r"(\d+)\s*out of 100",
        ]

        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                return int(match.group(1))

        # Default based on level mention
        if "high" in response.lower():
            return 85
        elif "medium" in response.lower():
            return 65
        elif "low" in response.lower():
            return 40
        else:
            return 50

    def _parse_replicability(self, response: str) -> str:
        """Parse replicability assessment."""
        response_lower = response.lower()

        if "replicability" in response_lower:
            if "yes" in response_lower:
                return "YES"
            elif "no" in response_lower:
                return "NO"
            elif "partial" in response_lower:
                return "PARTIAL"

        return "UNKNOWN"

    def _get_color_for_level(self, level: CredibilityLevel) -> str:
        """Get color code for credibility level."""
        color_map = {
            CredibilityLevel.HIGH: "green",
            CredibilityLevel.MEDIUM: "yellow",
            CredibilityLevel.LOW: "orange",
            CredibilityLevel.VERY_LOW: "red",
        }
        return color_map.get(level, "gray")
