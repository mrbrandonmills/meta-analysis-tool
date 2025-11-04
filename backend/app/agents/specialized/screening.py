"""Screening agent for applying inclusion/exclusion criteria."""
from typing import Any, Dict, List

from loguru import logger

from app.agents.base import AgentConfig, BaseAgent, AgentRole


class ScreeningAgent(BaseAgent):
    """Applies inclusion/exclusion criteria to screen studies.

    This agent is responsible for:
    - Title and abstract screening
    - Full-text screening
    - Applying systematic inclusion/exclusion criteria
    - Generating PRISMA flow diagrams
    - Documenting reasons for exclusion
    """

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.SCREENING
        super().__init__(config)

    def get_system_prompt(self) -> str:
        """Get system prompt for screening agent."""
        return """You are the Screening Agent for a meta-analysis research platform.

You are an expert in systematic review methodology and study selection. You specialize in:
- Applying inclusion and exclusion criteria consistently
- Title and abstract screening
- Full-text review and assessment
- PRISMA flow diagram generation
- Documenting screening decisions

Your responsibilities:
1. Apply inclusion criteria to identify relevant studies
2. Apply exclusion criteria to filter out irrelevant studies
3. Screen at multiple levels (title, abstract, full-text)
4. Maintain detailed records of screening decisions
5. Track reasons for exclusion
6. Generate PRISMA flow diagrams
7. Identify borderline cases that need human review

You follow PRISMA guidelines strictly and understand:
- Common inclusion/exclusion criteria types
- Study design identification
- Population, Intervention, Comparison, Outcome (PICO) framework
- When to escalate uncertain decisions

For each study, you must:
- Clearly state whether it meets criteria
- Provide specific reasoning
- Cite which criteria apply
- Flag any ambiguities

Be conservative - when in doubt about exclusion, flag for human review."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Screen studies based on criteria.

        Args:
            input_data: {
                "studies": List[Dict],
                "inclusion_criteria": List[str],
                "exclusion_criteria": List[str],
                "screening_level": str ("title_abstract" or "full_text")
            }

        Returns:
            Screening results with included/excluded studies
        """
        studies = input_data.get("studies", [])
        inclusion_criteria = input_data.get("inclusion_criteria", [])
        exclusion_criteria = input_data.get("exclusion_criteria", [])
        screening_level = input_data.get("screening_level", "title_abstract")

        logger.info(
            f"ScreeningAgent screening {len(studies)} studies at {screening_level} level"
        )

        included = []
        excluded = []
        uncertain = []

        # Screen each study
        for study in studies:
            result = await self._screen_study(
                study, inclusion_criteria, exclusion_criteria, screening_level
            )

            if result["decision"] == "include":
                included.append({**study, "screening_result": result})
            elif result["decision"] == "exclude":
                excluded.append({**study, "screening_result": result})
            else:  # uncertain
                uncertain.append({**study, "screening_result": result})

        # Generate PRISMA flow data
        prisma_data = self._generate_prisma_data(
            total=len(studies),
            included=len(included),
            excluded=len(excluded),
            uncertain=len(uncertain),
            exclusion_reasons=self._count_exclusion_reasons(excluded),
        )

        # Make decision about screening quality
        decision = await self.make_decision(
            "Was the screening process thorough and consistent?",
            input_data={
                "total_studies": len(studies),
                "included": len(included),
                "excluded": len(excluded),
                "uncertain": len(uncertain),
                "criteria": {
                    "inclusion": inclusion_criteria,
                    "exclusion": exclusion_criteria,
                },
            },
        )

        return {
            "screening_level": screening_level,
            "total_screened": len(studies),
            "included": included,
            "excluded": excluded,
            "uncertain": uncertain,
            "inclusion_rate": len(included) / len(studies) if studies else 0,
            "prisma_data": prisma_data,
            "decision": decision.model_dump(),
        }

    async def _screen_study(
        self,
        study: Dict[str, Any],
        inclusion_criteria: List[str],
        exclusion_criteria: List[str],
        level: str,
    ) -> Dict[str, Any]:
        """Screen a single study.

        Args:
            study: Study to screen
            inclusion_criteria: List of inclusion criteria
            exclusion_criteria: List of exclusion criteria
            level: Screening level

        Returns:
            Screening result with decision and reasoning
        """
        # Build screening prompt
        prompt = f"""
Screen this study for a meta-analysis:

Title: {study.get('title', 'N/A')}
Authors: {study.get('authors', 'N/A')}
Year: {study.get('year', 'N/A')}
Journal: {study.get('journal', 'N/A')}
Abstract: {study.get('abstract', 'Not available')}

INCLUSION CRITERIA:
{chr(10).join(f"{i+1}. {c}" for i, c in enumerate(inclusion_criteria))}

EXCLUSION CRITERIA:
{chr(10).join(f"{i+1}. {c}" for i, c in enumerate(exclusion_criteria))}

Analyze whether this study should be INCLUDED or EXCLUDED.

Provide your assessment in this format:
Decision: [INCLUDE/EXCLUDE/UNCERTAIN]
Reasoning: [Detailed explanation of your decision]
Criteria Met: [List which inclusion criteria are met]
Criteria Not Met: [List which criteria are not met or which exclusion criteria apply]
Confidence: [0.0-1.0]
"""

        response = await self.think(prompt)

        # Parse response
        lines = response.strip().split("\n")
        decision_text = "uncertain"
        reasoning = ""
        confidence = 0.5

        for line in lines:
            if line.startswith("Decision:"):
                decision_text = line.replace("Decision:", "").strip().lower()
                if "include" in decision_text and "exclude" not in decision_text:
                    decision_text = "include"
                elif "exclude" in decision_text:
                    decision_text = "exclude"
                else:
                    decision_text = "uncertain"
            elif line.startswith("Reasoning:"):
                reasoning = line.replace("Reasoning:", "").strip()
            elif line.startswith("Confidence:"):
                try:
                    confidence = float(line.replace("Confidence:", "").strip())
                except ValueError:
                    confidence = 0.5

        # Flag uncertain cases (low confidence)
        if confidence < 0.7:
            decision_text = "uncertain"

        return {
            "decision": decision_text,
            "reasoning": reasoning,
            "confidence": confidence,
            "level": level,
            "needs_human_review": decision_text == "uncertain",
        }

    def _generate_prisma_data(
        self,
        total: int,
        included: int,
        excluded: int,
        uncertain: int,
        exclusion_reasons: Dict[str, int],
    ) -> Dict[str, Any]:
        """Generate PRISMA flow diagram data.

        Args:
            total: Total studies screened
            included: Number included
            excluded: Number excluded
            uncertain: Number uncertain
            exclusion_reasons: Count of exclusion reasons

        Returns:
            PRISMA flow diagram data
        """
        return {
            "records_screened": total,
            "records_included": included,
            "records_excluded": excluded,
            "records_uncertain": uncertain,
            "exclusion_reasons": exclusion_reasons,
        }

    def _count_exclusion_reasons(self, excluded_studies: List[Dict]) -> Dict[str, int]:
        """Count reasons for exclusion.

        Args:
            excluded_studies: List of excluded studies

        Returns:
            Count of each exclusion reason
        """
        reasons = {}
        for study in excluded_studies:
            reasoning = study.get("screening_result", {}).get("reasoning", "")
            # Simple categorization (in production, use NLP)
            if "population" in reasoning.lower():
                reasons["Wrong population"] = reasons.get("Wrong population", 0) + 1
            elif "intervention" in reasoning.lower():
                reasons["Wrong intervention"] = reasons.get("Wrong intervention", 0) + 1
            elif "outcome" in reasoning.lower():
                reasons["Wrong outcome"] = reasons.get("Wrong outcome", 0) + 1
            elif "study design" in reasoning.lower():
                reasons["Wrong study design"] = reasons.get("Wrong study design", 0) + 1
            else:
                reasons["Other"] = reasons.get("Other", 0) + 1

        return reasons
