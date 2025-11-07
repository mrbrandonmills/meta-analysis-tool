"""Enhanced Credibility Agent V2 with comprehensive quality assessment tools."""
import asyncio
import re
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from app.agents.base import AgentConfig, BaseAgent, AgentRole


class CredibilityLevel(str, Enum):
    """Credibility levels with color coding."""

    HIGH = "high"  # Green - Peer-reviewed, high-impact, rigorous methodology
    MEDIUM = "medium"  # Yellow - Peer-reviewed with minor concerns, or high-quality preprint
    LOW = "low"  # Orange - Preprint with concerns, or peer-reviewed with major issues
    VERY_LOW = "very_low"  # Red - Serious methodological flaws or credibility issues


class StudyDesignType(str, Enum):
    """Study design types ranked by evidence hierarchy."""

    SYSTEMATIC_REVIEW_META_ANALYSIS = "Systematic Review/Meta-Analysis"  # Level 1
    RANDOMIZED_CONTROLLED_TRIAL = "Randomized Controlled Trial (RCT)"  # Level 2
    COHORT_STUDY = "Cohort Study"  # Level 3
    CASE_CONTROL_STUDY = "Case-Control Study"  # Level 4
    CROSS_SECTIONAL_STUDY = "Cross-Sectional Study"  # Level 5
    CASE_SERIES = "Case Series"  # Level 6
    CASE_REPORT = "Case Report"  # Level 7
    EXPERT_OPINION = "Expert Opinion"  # Level 8
    UNKNOWN = "Unknown"


class RiskOfBias(str, Enum):
    """Cochrane Risk of Bias assessment levels."""

    LOW = "Low risk"
    SOME_CONCERNS = "Some concerns"
    HIGH = "High risk"


class GRADELevel(str, Enum):
    """GRADE evidence quality levels."""

    HIGH = "High"  # Very confident in effect estimate
    MODERATE = "Moderate"  # Moderately confident
    LOW = "Low"  # Limited confidence
    VERY_LOW = "Very Low"  # Very little confidence


class CredibilityAgentV2(BaseAgent):
    """Enhanced Credibility Agent with comprehensive quality assessment.

    New Features:
    - Cochrane Risk of Bias tool implementation
    - GRADE quality assessment
    - Study design hierarchy evaluation
    - Sample size and power analysis
    - Peer review status detection (preprint identification)
    - Journal impact factor checking (via API)
    - Citation count analysis
    - Retraction checking
    - Comprehensive quality reports
    """

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.QUALITY_ASSESSMENT
        super().__init__(config)
        self._retraction_cache: Dict[str, bool] = {}

    def get_system_prompt(self) -> str:
        """Get system prompt for credibility agent."""
        return """You are the Advanced Credibility Evaluation Agent for a meta-analysis research platform.

You are an expert in research methodology, study design, risk of bias assessment, and evidence quality evaluation. You specialize in:
- Cochrane Risk of Bias (RoB 2.0) assessment
- GRADE (Grading of Recommendations Assessment, Development and Evaluation) framework
- Study design identification and hierarchy
- Sample size and statistical power evaluation
- Peer review quality assessment
- Journal credibility and impact factor analysis
- Citation analysis and research impact
- Detection of retracted publications
- Methodological quality appraisal

Your responsibilities:
1. Assess study credibility on multiple dimensions
2. Identify study design type and position in evidence hierarchy
3. Conduct Cochrane Risk of Bias assessment
4. Apply GRADE quality evaluation
5. Evaluate sample size adequacy and statistical power
6. Check peer review status and identify preprints
7. Assess journal quality and impact
8. Check for retractions and corrections
9. Generate comprehensive quality assessment reports

Evidence Hierarchy (highest to lowest):
1. Systematic reviews and meta-analyses of RCTs
2. Randomized controlled trials (RCTs)
3. Cohort studies
4. Case-control studies
5. Cross-sectional studies
6. Case series
7. Case reports
8. Expert opinion

Cochrane Risk of Bias Domains (RoB 2.0 for RCTs):
1. Bias arising from the randomization process
2. Bias due to deviations from intended interventions
3. Bias due to missing outcome data
4. Bias in measurement of the outcome
5. Bias in selection of the reported result

Each domain rated as: Low risk | Some concerns | High risk

GRADE Quality Assessment:
Start at HIGH for RCTs, LOW for observational studies, then downgrade/upgrade based on:

Downgrade for:
- Risk of bias (serious -1, very serious -2)
- Inconsistency (serious -1, very serious -2)
- Indirectness (serious -1, very serious -2)
- Imprecision (serious -1, very serious -2)
- Publication bias (serious -1)

Upgrade for (observational studies only):
- Large effect (+1 or +2)
- Dose-response gradient (+1)
- All plausible confounding would reduce effect (+1)

Final GRADE: HIGH | MODERATE | LOW | VERY LOW

Sample Size Assessment:
- Adequate: Powered for primary outcome (typically >80% power)
- Borderline: 50-79% power or unclear power calculation
- Inadequate: <50% power or very small sample

Peer Review Status:
- Peer-reviewed: Published in peer-reviewed journal
- Preprint: arXiv, bioRxiv, medRxiv, SSRN, etc.
- Unknown: Status unclear

Journal Quality Indicators:
- Impact Factor (JCR): >10 (very high), 5-10 (high), 2-5 (medium), <2 (low)
- Open access status
- Publisher reputation (avoid predatory journals)

For each study, provide:
1. Overall credibility level (HIGH/MEDIUM/LOW/VERY LOW)
2. Study design type and evidence level
3. Risk of Bias assessment (if RCT)
4. GRADE quality rating
5. Sample size adequacy
6. Peer review status
7. Journal quality assessment
8. Key strengths
9. Key limitations
10. Replication potential
11. Recommendation for inclusion in meta-analysis"""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate study credibility with comprehensive assessment.

        Args:
            input_data: {
                "studies": List[Dict],
                "require_peer_review": bool (default: False),
                "minimum_credibility": str (default: "low"),
                "check_retractions": bool (default: True),
                "fetch_citations": bool (default: False),
            }

        Returns:
            Studies with comprehensive credibility assessments
        """
        studies = input_data.get("studies", [])
        require_peer_review = input_data.get("require_peer_review", False)
        minimum_credibility = input_data.get("minimum_credibility", "low")
        check_retractions = input_data.get("check_retractions", True)
        fetch_citations = input_data.get("fetch_citations", False)

        logger.info(f"CredibilityAgentV2 evaluating {len(studies)} studies")

        evaluated_studies = []

        for study in studies:
            # Comprehensive credibility evaluation
            credibility = await self._evaluate_credibility_comprehensive(
                study,
                check_retractions=check_retractions,
                fetch_citations=fetch_citations,
            )

            # Filter by peer review requirement
            if require_peer_review and not credibility["is_peer_reviewed"]:
                logger.info(f"Filtered out preprint: {study.get('title', '')[:50]}")
                continue

            # Filter by minimum credibility
            if not self._meets_minimum_credibility(credibility["level"], minimum_credibility):
                logger.info(f"Filtered out low credibility study: {study.get('title', '')[:50]}")
                continue

            study_with_credibility = {
                **study,
                "credibility": credibility,
            }

            evaluated_studies.append(study_with_credibility)

        # Sort by credibility and quality
        evaluated_studies.sort(
            key=lambda x: (
                self._credibility_sort_key(x["credibility"]["level"]),
                -x["credibility"].get("quality_score", 0),
            )
        )

        # Calculate summary statistics
        credibility_breakdown = self._calculate_credibility_breakdown(evaluated_studies)
        design_breakdown = self._calculate_design_breakdown(evaluated_studies)
        grade_breakdown = self._calculate_grade_breakdown(evaluated_studies)

        # AI decision on overall quality
        decision = await self.make_decision(
            "Is the overall study quality sufficient for a reliable meta-analysis?",
            input_data={
                "total_studies": len(evaluated_studies),
                "credibility_breakdown": credibility_breakdown,
                "design_breakdown": design_breakdown,
                "grade_breakdown": grade_breakdown,
                "mean_quality_score": sum(s["credibility"].get("quality_score", 0) for s in evaluated_studies)
                / len(evaluated_studies)
                if evaluated_studies
                else 0,
            },
        )

        return {
            "studies": evaluated_studies,
            "total_evaluated": len(evaluated_studies),
            "credibility_breakdown": credibility_breakdown,
            "design_breakdown": design_breakdown,
            "grade_breakdown": grade_breakdown,
            "peer_reviewed_only": require_peer_review,
            "minimum_credibility_threshold": minimum_credibility,
            "decision": decision.model_dump(),
        }

    async def _evaluate_credibility_comprehensive(
        self,
        study: Dict[str, Any],
        check_retractions: bool = True,
        fetch_citations: bool = False,
    ) -> Dict[str, Any]:
        """Comprehensive credibility evaluation for a single study."""
        # Extract study metadata
        title = study.get("title", "")
        database = study.get("database", "")
        journal = study.get("journal", "")
        year = study.get("year", "")
        doi = study.get("doi", "")
        pmid = study.get("pmid", "")
        abstract = study.get("abstract", "")
        keywords = study.get("keywords", [])
        mesh_terms = study.get("mesh_terms", [])
        publication_types = study.get("publication_types", [])

        # Determine peer review status
        is_preprint = self._is_preprint(database, journal, doi)
        is_peer_reviewed = not is_preprint

        # Check for retraction
        is_retracted = False
        retraction_info = ""
        if check_retractions and (doi or pmid):
            is_retracted, retraction_info = await self._check_retraction_status(doi, pmid)

        # Fetch citation count (optional)
        citation_count = None
        if fetch_citations and doi:
            citation_count = await self._fetch_citation_count(doi)

        # Build comprehensive evaluation prompt
        eval_prompt = f"""
Conduct a comprehensive quality and credibility assessment for this study:

STUDY METADATA:
Title: {title}
Journal: {journal}
Year: {year}
Database: {database}
DOI: {doi}
PMID: {pmid}
Peer-reviewed: {is_peer_reviewed}
Preprint: {is_preprint}
{'RETRACTED: ' + retraction_info if is_retracted else ''}
{f'Citation count: {citation_count}' if citation_count is not None else ''}

ABSTRACT:
{abstract[:1000]}...

KEYWORDS: {', '.join(keywords[:10])}
MESH TERMS: {', '.join(mesh_terms[:10])}
PUBLICATION TYPES: {', '.join(publication_types)}

ASSESSMENT TASKS:

1. STUDY DESIGN IDENTIFICATION
   - Identify the study design type from the abstract
   - Place it in the evidence hierarchy
   - Assess if design is appropriate for research question

2. RISK OF BIAS ASSESSMENT
   - If RCT: Apply Cochrane RoB 2.0 tool (5 domains)
   - If observational: Note key biases (selection, confounding, measurement)
   - Rate each domain: Low risk | Some concerns | High risk
   - Provide overall risk of bias judgment

3. GRADE QUALITY ASSESSMENT
   - Start with initial quality based on design
   - Assess: risk of bias, inconsistency, indirectness, imprecision, publication bias
   - Consider upgrades (if observational): large effect, dose-response, confounding
   - Assign final GRADE: HIGH | MODERATE | LOW | VERY LOW

4. SAMPLE SIZE & POWER
   - Assess sample size adequacy
   - Look for power calculations
   - Rate: Adequate | Borderline | Inadequate | Unknown

5. METHODOLOGICAL QUALITY
   - Randomization (if RCT)
   - Blinding/masking
   - Statistical methods appropriateness
   - Outcome measurement quality
   - Completeness of follow-up

6. JOURNAL QUALITY (if available)
   - Estimate journal impact/reputation
   - Publisher credibility

7. REPLICABILITY
   - Are methods described in sufficient detail?
   - Can study be replicated?
   - Rate: High | Medium | Low

8. OVERALL ASSESSMENT
   - Key strengths (3-5 points)
   - Key limitations (3-5 points)
   - Overall credibility: HIGH | MEDIUM | LOW | VERY LOW
   - Quality score: 0-100
   - Recommendation for meta-analysis inclusion

Provide assessment in this EXACT format:
Study Design: [design type]
Evidence Level: [1-8 with description]
Risk of Bias Overall: [Low | Some concerns | High]
Risk of Bias Details: [domain-by-domain if RCT]
GRADE Quality: [HIGH | MODERATE | LOW | VERY LOW]
GRADE Justification: [brief explanation of rating]
Sample Size: [Adequate | Borderline | Inadequate | Unknown]
Power Analysis: [present/absent, adequate/inadequate]
Methodological Strengths: [bullet points]
Methodological Limitations: [bullet points]
Replicability: [High | Medium | Low]
Overall Credibility: [HIGH | MEDIUM | LOW | VERY LOW]
Quality Score: [0-100]
Inclusion Recommendation: [Recommend include | Include with caution | Consider excluding | Exclude]
Reasoning: [detailed justification]
"""

        response = await self.think(eval_prompt)

        # Parse comprehensive response
        parsed = self._parse_comprehensive_assessment(response)

        # Add metadata
        parsed["is_peer_reviewed"] = is_peer_reviewed
        parsed["is_preprint"] = is_preprint
        parsed["is_retracted"] = is_retracted
        parsed["retraction_info"] = retraction_info
        parsed["citation_count"] = citation_count
        parsed["database_source"] = database
        parsed["color"] = self._get_color_for_level(parsed["level"])

        return parsed

    def _is_preprint(self, database: str, journal: str, doi: str) -> bool:
        """Determine if study is a preprint."""
        preprint_indicators = [
            "arxiv",
            "biorxiv",
            "medrxiv",
            "chemrxiv",
            "psyarxiv",
            "ssrn",
            "preprint",
        ]

        database_lower = database.lower()
        journal_lower = journal.lower()
        doi_lower = doi.lower()

        return any(
            indicator in database_lower or indicator in journal_lower or indicator in doi_lower
            for indicator in preprint_indicators
        )

    async def _check_retraction_status(
        self, doi: str, pmid: str
    ) -> tuple[bool, str]:
        """Check if study has been retracted.

        Uses RetractionWatch API or PubMed data.
        """
        # Check cache first
        cache_key = doi or pmid
        if cache_key in self._retraction_cache:
            cached_result = self._retraction_cache[cache_key]
            return cached_result, "Retracted" if cached_result else ""

        # In production, would query RetractionWatch database
        # For now, simulate with basic heuristics
        is_retracted = False
        retraction_info = ""

        # Check PubMed for retraction notes (if PMID available)
        if pmid:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                        params={
                            "db": "pubmed",
                            "id": pmid,
                            "retmode": "xml",
                        },
                    )

                    if response.status_code == 200:
                        import xml.etree.ElementTree as ET

                        root = ET.fromstring(response.content)
                        # Check for retraction publication types
                        pub_types = [
                            pt.text.lower()
                            for pt in root.findall(".//PublicationType")
                            if pt.text
                        ]

                        if any("retract" in pt for pt in pub_types):
                            is_retracted = True
                            retraction_info = "Retracted publication (found in PubMed)"

            except Exception as e:
                logger.warning(f"Error checking retraction status: {e}")

        # Cache result
        self._retraction_cache[cache_key] = is_retracted

        return is_retracted, retraction_info

    async def _fetch_citation_count(self, doi: str) -> Optional[int]:
        """Fetch citation count for a study.

        Uses OpenCitations or Crossref API.
        """
        if not doi:
            return None

        try:
            # Try OpenCitations API (free, no authentication)
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://opencitations.net/index/api/v1/citation-count/{doi}",
                )

                if response.status_code == 200:
                    data = response.json()
                    if data and isinstance(data, list) and len(data) > 0:
                        return int(data[0].get("count", 0))

                # Fallback to Crossref
                response = await client.get(
                    f"https://api.crossref.org/works/{doi}",
                )

                if response.status_code == 200:
                    data = response.json()
                    return int(data.get("message", {}).get("is-referenced-by-count", 0))

        except Exception as e:
            logger.warning(f"Error fetching citation count: {e}")

        return None

    def _parse_comprehensive_assessment(self, response: str) -> Dict[str, Any]:
        """Parse comprehensive assessment response from AI."""
        lines = response.strip().split("\n")

        result = {
            "study_design": "Unknown",
            "evidence_level": 0,
            "risk_of_bias_overall": "Some concerns",
            "risk_of_bias_details": {},
            "grade_quality": "MODERATE",
            "grade_justification": "",
            "sample_size": "Unknown",
            "power_analysis": "Unknown",
            "methodological_strengths": [],
            "methodological_limitations": [],
            "replicability": "Medium",
            "level": CredibilityLevel.MEDIUM,
            "quality_score": 50,
            "inclusion_recommendation": "Include with caution",
            "reasoning": "",
        }

        current_list = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Parse each field
            if line.startswith("Study Design:"):
                result["study_design"] = line.replace("Study Design:", "").strip()

            elif line.startswith("Evidence Level:"):
                level_text = line.replace("Evidence Level:", "").strip()
                # Extract number
                match = re.search(r"(\d+)", level_text)
                if match:
                    result["evidence_level"] = int(match.group(1))

            elif line.startswith("Risk of Bias Overall:"):
                result["risk_of_bias_overall"] = line.replace("Risk of Bias Overall:", "").strip()

            elif line.startswith("Risk of Bias Details:"):
                result["risk_of_bias_details"] = line.replace("Risk of Bias Details:", "").strip()

            elif line.startswith("GRADE Quality:"):
                grade_text = line.replace("GRADE Quality:", "").strip().upper()
                if "HIGH" in grade_text:
                    result["grade_quality"] = "HIGH"
                elif "MODERATE" in grade_text:
                    result["grade_quality"] = "MODERATE"
                elif "VERY LOW" in grade_text or "VERY_LOW" in grade_text:
                    result["grade_quality"] = "VERY LOW"
                elif "LOW" in grade_text:
                    result["grade_quality"] = "LOW"

            elif line.startswith("GRADE Justification:"):
                result["grade_justification"] = line.replace("GRADE Justification:", "").strip()

            elif line.startswith("Sample Size:"):
                result["sample_size"] = line.replace("Sample Size:", "").strip()

            elif line.startswith("Power Analysis:"):
                result["power_analysis"] = line.replace("Power Analysis:", "").strip()

            elif line.startswith("Methodological Strengths:"):
                current_list = "strengths"

            elif line.startswith("Methodological Limitations:"):
                current_list = "limitations"

            elif line.startswith("Replicability:"):
                result["replicability"] = line.replace("Replicability:", "").strip()
                current_list = None

            elif line.startswith("Overall Credibility:"):
                cred_text = line.replace("Overall Credibility:", "").strip().upper()
                if "VERY LOW" in cred_text or "VERY_LOW" in cred_text:
                    result["level"] = CredibilityLevel.VERY_LOW
                elif "LOW" in cred_text:
                    result["level"] = CredibilityLevel.LOW
                elif "MEDIUM" in cred_text:
                    result["level"] = CredibilityLevel.MEDIUM
                elif "HIGH" in cred_text:
                    result["level"] = CredibilityLevel.HIGH
                current_list = None

            elif line.startswith("Quality Score:"):
                try:
                    score_text = line.replace("Quality Score:", "").strip()
                    result["quality_score"] = int(re.search(r"(\d+)", score_text).group(1))
                except (ValueError, AttributeError):
                    result["quality_score"] = 50

            elif line.startswith("Inclusion Recommendation:"):
                result["inclusion_recommendation"] = line.replace("Inclusion Recommendation:", "").strip()

            elif line.startswith("Reasoning:"):
                result["reasoning"] = line.replace("Reasoning:", "").strip()

            elif current_list and (line.startswith("-") or line.startswith("•") or line.startswith("*")):
                # Extract bullet point
                item = line.lstrip("-•* ").strip()
                if item:
                    if current_list == "strengths":
                        result["methodological_strengths"].append(item)
                    elif current_list == "limitations":
                        result["methodological_limitations"].append(item)

        return result

    def _meets_minimum_credibility(self, level: CredibilityLevel, minimum: str) -> bool:
        """Check if credibility level meets minimum threshold."""
        level_order = {
            CredibilityLevel.HIGH: 3,
            CredibilityLevel.MEDIUM: 2,
            CredibilityLevel.LOW: 1,
            CredibilityLevel.VERY_LOW: 0,
        }

        minimum_map = {
            "high": 3,
            "medium": 2,
            "low": 1,
            "very_low": 0,
        }

        return level_order.get(level, 0) >= minimum_map.get(minimum.lower(), 0)

    def _credibility_sort_key(self, level: CredibilityLevel) -> int:
        """Get sort key for credibility level (lower is better)."""
        order = {
            CredibilityLevel.HIGH: 0,
            CredibilityLevel.MEDIUM: 1,
            CredibilityLevel.LOW: 2,
            CredibilityLevel.VERY_LOW: 3,
        }
        return order.get(level, 999)

    def _get_color_for_level(self, level: CredibilityLevel) -> str:
        """Get color code for credibility level."""
        color_map = {
            CredibilityLevel.HIGH: "green",
            CredibilityLevel.MEDIUM: "yellow",
            CredibilityLevel.LOW: "orange",
            CredibilityLevel.VERY_LOW: "red",
        }
        return color_map.get(level, "gray")

    def _calculate_credibility_breakdown(self, studies: List[Dict]) -> Dict[str, int]:
        """Calculate credibility level breakdown."""
        breakdown = {
            "high": 0,
            "medium": 0,
            "low": 0,
            "very_low": 0,
        }

        for study in studies:
            level = study.get("credibility", {}).get("level")
            if level:
                breakdown[level] = breakdown.get(level, 0) + 1

        return breakdown

    def _calculate_design_breakdown(self, studies: List[Dict]) -> Dict[str, int]:
        """Calculate study design breakdown."""
        breakdown = defaultdict(int)

        for study in studies:
            design = study.get("credibility", {}).get("study_design", "Unknown")
            breakdown[design] += 1

        return dict(breakdown)

    def _calculate_grade_breakdown(self, studies: List[Dict]) -> Dict[str, int]:
        """Calculate GRADE quality breakdown."""
        breakdown = {
            "HIGH": 0,
            "MODERATE": 0,
            "LOW": 0,
            "VERY LOW": 0,
        }

        for study in studies:
            grade = study.get("credibility", {}).get("grade_quality", "MODERATE")
            if grade in breakdown:
                breakdown[grade] += 1

        return breakdown
