"""Full-text screening agent for comprehensive study assessment.

Performs detailed screening based on full PDF text, extracting:
- Detailed PICO components
- Study quality indicators
- Sample size and statistical power
- Outcome measures and effect sizes
- Methodological details
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from app.agents.base import AgentConfig, BaseAgent, AgentRole
from app.models.pdf_metadata import FullTextExtraction, FullTextScreening, SectionType


class FullTextScreeningAgent(BaseAgent):
    """Agent for comprehensive full-text screening.

    This agent performs detailed analysis of full-text PDFs to:
    - Apply inclusion/exclusion criteria with full context
    - Extract PICO (Population, Intervention, Comparison, Outcome) components
    - Assess study quality and risk of bias
    - Extract detailed methodological information
    - Identify data for extraction
    - Flag concerns and uncertainties
    """

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.SCREENING
        super().__init__(config)

    def get_system_prompt(self) -> str:
        """Get system prompt for full-text screening agent."""
        return """You are the Full-Text Screening Agent for meta-analysis research.

You are an expert in systematic review methodology with deep knowledge of:
- PICO framework (Population, Intervention, Comparison, Outcome)
- Study design assessment and risk of bias
- Cochrane and PRISMA guidelines
- Research methodology across disciplines
- Statistical methods and reporting
- Data extraction from primary studies

Your responsibilities:
1. Perform comprehensive full-text screening against inclusion/exclusion criteria
2. Extract detailed PICO components from full text
3. Assess study quality and methodological rigor
4. Identify outcome measures and statistical results
5. Extract sample size, power analysis, and design details
6. Flag concerns about bias, methodology, or reporting
7. Determine if study should be included in meta-analysis

For each study, you must:
- Read the complete full text, paying special attention to Methods and Results
- Make evidence-based decisions with specific citations from the text
- Extract quantitative data when available (effect sizes, CIs, p-values)
- Assess risk of bias using appropriate tools
- Flag any concerns for human review
- Provide detailed reasoning for all decisions

Be thorough and conservative - when critical information is missing or unclear,
flag the study for human review rather than making assumptions."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Screen studies using full-text analysis.

        Args:
            input_data: {
                "extractions": List[FullTextExtraction],
                "inclusion_criteria": List[str],
                "exclusion_criteria": List[str],
                "study_type": str (optional),
                "outcome_measures": List[str] (optional),
            }

        Returns:
            Full-text screening results with detailed analysis
        """
        extractions = input_data.get("extractions", [])
        inclusion_criteria = input_data.get("inclusion_criteria", [])
        exclusion_criteria = input_data.get("exclusion_criteria", [])
        study_type = input_data.get("study_type")
        outcome_measures = input_data.get("outcome_measures", [])

        logger.info(f"Full-text screening {len(extractions)} studies")

        included = []
        excluded = []
        uncertain = []

        for extraction in extractions:
            result = await self._screen_full_text(
                extraction,
                inclusion_criteria,
                exclusion_criteria,
                study_type,
                outcome_measures,
            )

            if result["decision"] == "include":
                included.append({**extraction, "screening_result": result})
            elif result["decision"] == "exclude":
                excluded.append({**extraction, "screening_result": result})
            else:
                uncertain.append({**extraction, "screening_result": result})

        # Generate quality summary
        quality_summary = self._generate_quality_summary(included)

        return {
            "total_screened": len(extractions),
            "included": included,
            "excluded": excluded,
            "uncertain": uncertain,
            "inclusion_rate": len(included) / len(extractions) if extractions else 0,
            "quality_summary": quality_summary,
        }

    async def _screen_full_text(
        self,
        extraction: FullTextExtraction,
        inclusion_criteria: List[str],
        exclusion_criteria: List[str],
        study_type: Optional[str],
        outcome_measures: List[str],
    ) -> Dict[str, Any]:
        """Screen a single study using full text.

        Args:
            extraction: Full text extraction
            inclusion_criteria: Inclusion criteria
            exclusion_criteria: Exclusion criteria
            study_type: Expected study type
            outcome_measures: Expected outcome measures

        Returns:
            Screening result with detailed analysis
        """
        # Build comprehensive prompt with full text sections
        sections = extraction.sections or {}

        prompt = f"""
Perform comprehensive full-text screening of this study:

=== ABSTRACT ===
{sections.get(SectionType.ABSTRACT.value, "Not available")}

=== METHODS ===
{sections.get(SectionType.METHODS.value, "Not available")}

=== RESULTS ===
{sections.get(SectionType.RESULTS.value, "Not available")}

=== DISCUSSION ===
{sections.get(SectionType.DISCUSSION.value, "Not available")}

INCLUSION CRITERIA:
{chr(10).join(f"{i+1}. {c}" for i, c in enumerate(inclusion_criteria))}

EXCLUSION CRITERIA:
{chr(10).join(f"{i+1}. {c}" for i, c in enumerate(exclusion_criteria))}

EXPECTED STUDY TYPE: {study_type or "Any appropriate design"}

EXPECTED OUTCOMES: {", ".join(outcome_measures) if outcome_measures else "Any relevant outcomes"}

DETECTED STATISTICS:
{chr(10).join(f"- {stat['text']}" for stat in (extraction.statistics_found or [])[:10])}

STUDY DESIGN MENTIONS:
{", ".join(extraction.study_design_mentions or [])}

SAMPLE SIZE MENTIONS:
{", ".join(extraction.sample_size_mentions or [])}

Please provide a comprehensive assessment in this format:

DECISION: [INCLUDE/EXCLUDE/UNCERTAIN]

REASONING: [Detailed explanation with specific references to the text]

CRITERIA ASSESSMENT:
- List each inclusion criterion and whether it's met (with evidence)
- List any exclusion criteria that apply (with evidence)

PICO EXTRACTION:
- Population: [Description with sample size if available]
- Intervention: [Description of intervention/exposure]
- Comparison: [Description of control/comparison group]
- Outcome: [Primary and secondary outcomes]

STUDY QUALITY INDICATORS:
- Study Design: [Type and appropriateness]
- Sample Size: [Adequate/Inadequate, with justification]
- Randomization: [Yes/No/NA, with details]
- Blinding: [Type and quality]
- Attrition: [Dropout rate and handling]
- Statistical Analysis: [Appropriate methods]

DATA EXTRACTION PREVIEW:
- Effect Size: [Value and type if reported]
- Confidence Interval: [If reported]
- P-value: [If reported]
- Sample Size: [Total N]

CONCERNS:
- List any methodological concerns
- List any reporting issues
- List missing critical information

NEEDS HUMAN REVIEW: [YES/NO]

CONFIDENCE: [0.0-1.0]
"""

        response = await self.think(prompt)

        # Parse response
        result = self._parse_screening_response(response)

        return result

    def _parse_screening_response(self, response: str) -> Dict[str, Any]:
        """Parse the screening response from the agent.

        Args:
            response: Raw response text

        Returns:
            Structured screening result
        """
        result = {
            "decision": "uncertain",
            "reasoning": "",
            "confidence": 0.5,
            "pico_extraction": {},
            "study_quality_indicators": {},
            "data_extraction_preview": {},
            "inclusion_criteria_met": [],
            "exclusion_criteria_violated": [],
            "concerns": [],
            "needs_human_review": True,
        }

        # Parse sections
        current_section = None
        current_content = []

        lines = response.strip().split("\n")
        for line in lines:
            line_stripped = line.strip()

            # Check for section headers
            if line_stripped.startswith("DECISION:"):
                decision_text = line_stripped.replace("DECISION:", "").strip().lower()
                if "include" in decision_text and "exclude" not in decision_text:
                    result["decision"] = "include"
                elif "exclude" in decision_text:
                    result["decision"] = "exclude"
                else:
                    result["decision"] = "uncertain"

            elif line_stripped.startswith("REASONING:"):
                result["reasoning"] = line_stripped.replace("REASONING:", "").strip()

            elif line_stripped.startswith("CONFIDENCE:"):
                try:
                    conf_text = line_stripped.replace("CONFIDENCE:", "").strip()
                    result["confidence"] = float(conf_text)
                except ValueError:
                    result["confidence"] = 0.5

            elif line_stripped.startswith("NEEDS HUMAN REVIEW:"):
                review_text = line_stripped.replace("NEEDS HUMAN REVIEW:", "").strip().lower()
                result["needs_human_review"] = "yes" in review_text

            elif line_stripped.startswith("PICO EXTRACTION:"):
                current_section = "pico"
                current_content = []

            elif line_stripped.startswith("STUDY QUALITY INDICATORS:"):
                current_section = "quality"
                current_content = []

            elif line_stripped.startswith("DATA EXTRACTION PREVIEW:"):
                current_section = "data"
                current_content = []

            elif line_stripped.startswith("CONCERNS:"):
                current_section = "concerns"
                current_content = []

            elif current_section and line_stripped.startswith("-"):
                current_content.append(line_stripped[1:].strip())

                # Parse PICO components
                if current_section == "pico":
                    if ":" in line_stripped:
                        key, value = line_stripped[1:].split(":", 1)
                        result["pico_extraction"][key.strip()] = value.strip()

                # Parse quality indicators
                elif current_section == "quality":
                    if ":" in line_stripped:
                        key, value = line_stripped[1:].split(":", 1)
                        result["study_quality_indicators"][key.strip()] = value.strip()

                # Parse data extraction
                elif current_section == "data":
                    if ":" in line_stripped:
                        key, value = line_stripped[1:].split(":", 1)
                        result["data_extraction_preview"][key.strip()] = value.strip()

                # Parse concerns
                elif current_section == "concerns":
                    result["concerns"].append(line_stripped[1:].strip())

        # Flag low confidence as needing review
        if result["confidence"] < 0.7:
            result["needs_human_review"] = True

        return result

    def _generate_quality_summary(self, included_studies: List[Dict]) -> Dict[str, Any]:
        """Generate summary of study quality across included studies.

        Args:
            included_studies: List of included studies with screening results

        Returns:
            Quality summary statistics
        """
        if not included_studies:
            return {}

        total = len(included_studies)

        # Count studies with specific quality indicators
        has_randomization = 0
        has_blinding = 0
        has_adequate_sample = 0
        has_effect_size = 0

        for study in included_studies:
            result = study.get("screening_result", {})
            quality = result.get("study_quality_indicators", {})
            data = result.get("data_extraction_preview", {})

            if "Randomization" in quality and "yes" in quality["Randomization"].lower():
                has_randomization += 1

            if "Blinding" in quality and quality["Blinding"].lower() != "none":
                has_blinding += 1

            if "Sample Size" in quality and "adequate" in quality["Sample Size"].lower():
                has_adequate_sample += 1

            if "Effect Size" in data and data["Effect Size"].lower() != "not reported":
                has_effect_size += 1

        return {
            "total_included": total,
            "with_randomization": has_randomization,
            "with_blinding": has_blinding,
            "with_adequate_sample": has_adequate_sample,
            "with_effect_size": has_effect_size,
            "randomization_rate": has_randomization / total if total > 0 else 0,
            "blinding_rate": has_blinding / total if total > 0 else 0,
            "adequate_sample_rate": has_adequate_sample / total if total > 0 else 0,
            "effect_size_reporting_rate": has_effect_size / total if total > 0 else 0,
        }

    async def extract_data_for_meta_analysis(
        self, extraction: FullTextExtraction
    ) -> Dict[str, Any]:
        """Extract quantitative data for meta-analysis.

        Args:
            extraction: Full text extraction

        Returns:
            Extracted data for meta-analysis
        """
        sections = extraction.sections or {}

        prompt = f"""
Extract quantitative data from this study for meta-analysis:

=== RESULTS ===
{sections.get(SectionType.RESULTS.value, "Not available")}

=== STATISTICS DETECTED ===
{chr(10).join(f"- {stat['text']}" for stat in (extraction.statistics_found or [])[:20])}

Please extract the following data:

1. PRIMARY OUTCOME DATA:
   - Outcome name
   - Effect size (standardized mean difference, odds ratio, etc.)
   - Standard error or confidence interval
   - P-value
   - Sample size (intervention group)
   - Sample size (control group)

2. SECONDARY OUTCOMES (if available)

3. SUBGROUP DATA (if available)

4. BASELINE CHARACTERISTICS:
   - Mean age
   - Gender distribution
   - Other relevant characteristics

Format your response as:
PRIMARY_OUTCOME: [outcome name]
EFFECT_SIZE: [value]
EFFECT_SIZE_TYPE: [SMD/OR/RR/MD]
CI_LOWER: [value]
CI_UPPER: [value]
P_VALUE: [value]
N_INTERVENTION: [value]
N_CONTROL: [value]
"""

        response = await self.think(prompt)

        # Parse response into structured data
        data = self._parse_data_extraction(response)

        return data

    def _parse_data_extraction(self, response: str) -> Dict[str, Any]:
        """Parse data extraction response.

        Args:
            response: Raw response text

        Returns:
            Structured data extraction
        """
        data = {}

        lines = response.strip().split("\n")
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                value = value.strip()

                # Try to convert numeric values
                try:
                    if value and value.lower() not in ["not reported", "na", "n/a"]:
                        data[key] = float(value)
                    else:
                        data[key] = None
                except ValueError:
                    data[key] = value

        return data
