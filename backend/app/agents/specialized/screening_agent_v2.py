"""Enhanced Screening Agent V2 with ML-based relevance scoring and embeddings."""
import asyncio
import hashlib
import json
import re
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import cohen_kappa_score
from sklearn.metrics.pairwise import cosine_similarity

from app.agents.base import AgentConfig, BaseAgent, AgentRole


class ScreeningClassifier:
    """Simple ML-based classifier for screening relevance.

    Uses TF-IDF vectors and cosine similarity for semantic matching.
    In production, this would use sentence embeddings (e.g., sentence-transformers).
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
        )
        self.criteria_vectors = None
        self.is_fitted = False

    def fit_criteria(self, inclusion_criteria: List[str], exclusion_criteria: List[str]):
        """Fit vectorizer on inclusion/exclusion criteria."""
        all_criteria = inclusion_criteria + exclusion_criteria
        if not all_criteria:
            logger.warning("No criteria provided to fit classifier")
            return

        try:
            self.criteria_vectors = self.vectorizer.fit_transform(all_criteria)
            self.is_fitted = True
            logger.info(f"Fitted screening classifier on {len(all_criteria)} criteria")
        except Exception as e:
            logger.error(f"Error fitting screening classifier: {e}")
            self.is_fitted = False

    def compute_relevance_score(
        self,
        study_text: str,
        inclusion_criteria: List[str],
        exclusion_criteria: List[str],
    ) -> Tuple[float, float, Dict[str, float]]:
        """Compute relevance scores for a study.

        Args:
            study_text: Combined title + abstract of study
            inclusion_criteria: List of inclusion criteria
            exclusion_criteria: List of exclusion criteria

        Returns:
            Tuple of (inclusion_score, exclusion_score, detailed_scores)
        """
        if not self.is_fitted or not study_text.strip():
            return 0.0, 0.0, {}

        try:
            # Vectorize study text
            study_vector = self.vectorizer.transform([study_text])

            # Vectorize criteria
            inclusion_vectors = self.vectorizer.transform(inclusion_criteria) if inclusion_criteria else None
            exclusion_vectors = self.vectorizer.transform(exclusion_criteria) if exclusion_criteria else None

            # Compute similarity scores
            inclusion_score = 0.0
            exclusion_score = 0.0
            detailed_scores = {}

            if inclusion_vectors is not None and inclusion_vectors.shape[0] > 0:
                inclusion_similarities = cosine_similarity(study_vector, inclusion_vectors)[0]
                inclusion_score = float(np.mean(inclusion_similarities))
                detailed_scores["inclusion_per_criterion"] = [
                    float(sim) for sim in inclusion_similarities
                ]

            if exclusion_vectors is not None and exclusion_vectors.shape[0] > 0:
                exclusion_similarities = cosine_similarity(study_vector, exclusion_vectors)[0]
                exclusion_score = float(np.mean(exclusion_similarities))
                detailed_scores["exclusion_per_criterion"] = [
                    float(sim) for sim in exclusion_similarities
                ]

            return inclusion_score, exclusion_score, detailed_scores

        except Exception as e:
            logger.error(f"Error computing relevance score: {e}")
            return 0.0, 0.0, {}


class ScreeningAgentV2(BaseAgent):
    """Enhanced Screening Agent with ML-based relevance scoring.

    New Features:
    - ML-based relevance scoring using TF-IDF and cosine similarity
    - Multi-stage screening (title → abstract → full-text)
    - Batch processing with progress tracking
    - Conflict resolution for uncertain cases
    - Cohen's kappa for inter-rater agreement
    - Detailed justifications for each decision
    - PRISMA flow diagram data generation
    """

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.SCREENING
        super().__init__(config)
        self.classifier = ScreeningClassifier()

    def get_system_prompt(self) -> str:
        """Get system prompt for screening agent."""
        return """You are the Advanced Screening Agent for a meta-analysis research platform.

You are an expert in systematic review methodology, study selection, and evidence synthesis. You specialize in:
- Applying PICO (Population, Intervention, Comparison, Outcome) framework
- Title and abstract screening at multiple stages
- Full-text eligibility assessment
- PRISMA (Preferred Reporting Items for Systematic Reviews) guidelines
- Inter-rater reliability and conflict resolution
- Documentation of screening decisions

Your responsibilities:
1. Apply inclusion and exclusion criteria systematically and consistently
2. Screen studies at multiple levels (title → abstract → full-text)
3. Provide detailed justifications for each screening decision
4. Identify borderline cases that need human review
5. Maintain high inter-rater reliability (Cohen's kappa > 0.8)
6. Generate PRISMA flow diagrams
7. Document reasons for exclusion at each stage

Multi-Stage Screening Process:
1. TITLE SCREENING: Quick assessment based on title alone
   - Exclude obviously irrelevant studies
   - Include if potentially relevant
   - Conservative approach (when in doubt, include)

2. ABSTRACT SCREENING: Detailed assessment of title + abstract
   - Apply PICO criteria
   - Check study design
   - Assess outcome measures
   - Flag uncertain cases for full-text review

3. FULL-TEXT SCREENING: Complete assessment of full article
   - Verify eligibility criteria
   - Extract study characteristics
   - Final inclusion/exclusion decision
   - Document specific reasons for exclusion

Decision Framework:
- INCLUDE: Meets all inclusion criteria, no exclusion criteria apply
- EXCLUDE: Fails one or more inclusion criteria OR meets exclusion criteria
- UNCERTAIN: Borderline case, needs human review or additional information

For each decision, you MUST provide:
1. Clear INCLUDE/EXCLUDE/UNCERTAIN decision
2. Detailed reasoning citing specific criteria
3. Which inclusion criteria are met/not met
4. Whether any exclusion criteria apply
5. Confidence score (0.0-1.0)
6. Recommendation for next steps (e.g., "Proceed to full-text review")

Reasons for Exclusion (use standardized categories):
- Wrong population/participants
- Wrong intervention/exposure
- Wrong comparator/control
- Wrong outcomes measured
- Wrong study design (e.g., not RCT when RCT required)
- Wrong publication type (e.g., conference abstract, editorial)
- Duplicate publication
- Language restriction
- Insufficient data/information

Always be conservative: When in doubt about excluding, mark as UNCERTAIN for human review.
Maintain consistency across similar studies to ensure high inter-rater reliability."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Screen studies with ML-enhanced relevance scoring.

        Args:
            input_data: {
                "studies": List[Dict],
                "inclusion_criteria": List[str],
                "exclusion_criteria": List[str],
                "screening_level": str ("title", "abstract", or "full_text"),
                "batch_size": int (default: 10),
                "use_ml_scoring": bool (default: True),
                "confidence_threshold": float (default: 0.7),
            }

        Returns:
            Screening results with ML scores, decisions, and PRISMA data
        """
        studies = input_data.get("studies", [])
        inclusion_criteria = input_data.get("inclusion_criteria", [])
        exclusion_criteria = input_data.get("exclusion_criteria", [])
        screening_level = input_data.get("screening_level", "abstract")
        batch_size = input_data.get("batch_size", 10)
        use_ml_scoring = input_data.get("use_ml_scoring", True)
        confidence_threshold = input_data.get("confidence_threshold", 0.7)

        logger.info(
            f"ScreeningAgentV2 screening {len(studies)} studies at '{screening_level}' level"
        )

        # Fit ML classifier on criteria
        if use_ml_scoring:
            self.classifier.fit_criteria(inclusion_criteria, exclusion_criteria)

        # Screen studies in batches
        included = []
        excluded = []
        uncertain = []

        for i in range(0, len(studies), batch_size):
            batch = studies[i : i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}/{(len(studies) + batch_size - 1) // batch_size}")

            # Process batch
            batch_results = await self._screen_batch(
                batch,
                inclusion_criteria,
                exclusion_criteria,
                screening_level,
                use_ml_scoring,
                confidence_threshold,
            )

            for study, result in zip(batch, batch_results):
                study_with_result = {**study, "screening_result": result}

                if result["decision"] == "include":
                    included.append(study_with_result)
                elif result["decision"] == "exclude":
                    excluded.append(study_with_result)
                else:  # uncertain
                    uncertain.append(study_with_result)

        # Generate PRISMA flow data
        exclusion_reasons = self._categorize_exclusion_reasons(excluded)
        prisma_data = self._generate_prisma_data(
            screening_level=screening_level,
            total=len(studies),
            included=len(included),
            excluded=len(excluded),
            uncertain=len(uncertain),
            exclusion_reasons=exclusion_reasons,
        )

        # Calculate screening statistics
        screening_stats = self._calculate_screening_stats(included, excluded, uncertain)

        # AI decision on screening quality
        decision = await self.make_decision(
            "Was the screening process thorough, consistent, and reliable?",
            input_data={
                "total_studies": len(studies),
                "included": len(included),
                "excluded": len(excluded),
                "uncertain": len(uncertain),
                "inclusion_rate": len(included) / len(studies) if studies else 0,
                "criteria": {
                    "inclusion": inclusion_criteria,
                    "exclusion": exclusion_criteria,
                },
                "screening_stats": screening_stats,
            },
        )

        return {
            "screening_level": screening_level,
            "total_screened": len(studies),
            "included": included,
            "excluded": excluded,
            "uncertain": uncertain,
            "inclusion_rate": len(included) / len(studies) if studies else 0,
            "exclusion_rate": len(excluded) / len(studies) if studies else 0,
            "uncertain_rate": len(uncertain) / len(studies) if studies else 0,
            "prisma_data": prisma_data,
            "screening_stats": screening_stats,
            "ml_scoring_used": use_ml_scoring,
            "decision": decision.model_dump(),
        }

    async def _screen_batch(
        self,
        studies: List[Dict[str, Any]],
        inclusion_criteria: List[str],
        exclusion_criteria: List[str],
        level: str,
        use_ml_scoring: bool,
        confidence_threshold: float,
    ) -> List[Dict[str, Any]]:
        """Screen a batch of studies concurrently."""
        tasks = [
            self._screen_study(
                study,
                inclusion_criteria,
                exclusion_criteria,
                level,
                use_ml_scoring,
                confidence_threshold,
            )
            for study in studies
        ]

        return await asyncio.gather(*tasks)

    async def _screen_study(
        self,
        study: Dict[str, Any],
        inclusion_criteria: List[str],
        exclusion_criteria: List[str],
        level: str,
        use_ml_scoring: bool,
        confidence_threshold: float,
    ) -> Dict[str, Any]:
        """Screen a single study with ML scoring and AI reasoning.

        Args:
            study: Study to screen
            inclusion_criteria: List of inclusion criteria
            exclusion_criteria: List of exclusion criteria
            level: Screening level (title, abstract, full_text)
            use_ml_scoring: Whether to use ML relevance scoring
            confidence_threshold: Threshold for uncertain classification

        Returns:
            Screening result with decision, reasoning, and scores
        """
        title = study.get("title", "")
        abstract = study.get("abstract", "")
        authors = study.get("authors", [])
        year = study.get("year", "")
        journal = study.get("journal", "")

        # Determine what text to use based on screening level
        if level == "title":
            study_text = title
            context_text = f"Title: {title}"
        elif level == "abstract":
            study_text = f"{title} {abstract}"
            context_text = f"Title: {title}\nAbstract: {abstract[:500]}..."
        else:  # full_text
            # In production, this would include full text if available
            study_text = f"{title} {abstract}"
            context_text = f"Title: {title}\nAbstract: {abstract}"

        # Compute ML relevance scores
        ml_scores = {}
        if use_ml_scoring and study_text.strip():
            inclusion_score, exclusion_score, detailed_scores = self.classifier.compute_relevance_score(
                study_text, inclusion_criteria, exclusion_criteria
            )
            ml_scores = {
                "inclusion_score": inclusion_score,
                "exclusion_score": exclusion_score,
                "detailed_scores": detailed_scores,
                "net_score": inclusion_score - exclusion_score,  # Positive = likely include
            }

        # Build AI screening prompt
        prompt = f"""
Screen this study for inclusion in a systematic review/meta-analysis.

SCREENING LEVEL: {level.upper()}

STUDY INFORMATION:
{context_text}
Authors: {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}
Year: {year}
Journal: {journal}

INCLUSION CRITERIA:
{self._format_criteria_list(inclusion_criteria)}

EXCLUSION CRITERIA:
{self._format_criteria_list(exclusion_criteria)}

{'ML RELEVANCE SCORES:' if use_ml_scoring and ml_scores else ''}
{self._format_ml_scores(ml_scores) if use_ml_scoring and ml_scores else ''}

Based on this {level}-level screening, make a systematic decision.

Provide your assessment in this EXACT format:
Decision: [INCLUDE/EXCLUDE/UNCERTAIN]
Reasoning: [Detailed explanation of your decision, referencing specific criteria]
Criteria Met: [List the specific inclusion criteria that ARE met]
Criteria Not Met: [List the specific criteria that are NOT met]
Exclusion Criteria Applied: [List any exclusion criteria that apply, or "None"]
Exclusion Reason Category: [If excluding, use one of: Wrong population | Wrong intervention | Wrong comparator | Wrong outcomes | Wrong study design | Wrong publication type | Duplicate | Language | Insufficient data | Other]
Confidence: [0.0-1.0]
Next Step: [Recommendation for next action]
Flags: [Any concerns or notes for human reviewers]
"""

        response = await self.think(prompt)

        # Parse AI response
        parsed = self._parse_screening_response(response)

        # Apply confidence threshold
        if parsed["confidence"] < confidence_threshold:
            parsed["decision"] = "uncertain"
            parsed["needs_human_review"] = True

        # Add ML scores to result
        parsed["ml_scores"] = ml_scores
        parsed["level"] = level

        return parsed

    def _format_criteria_list(self, criteria: List[str]) -> str:
        """Format criteria as numbered list."""
        if not criteria:
            return "  (None specified)"
        return "\n".join([f"  {i+1}. {c}" for i, c in enumerate(criteria)])

    def _format_ml_scores(self, ml_scores: Dict[str, Any]) -> str:
        """Format ML scores for display."""
        if not ml_scores:
            return ""
        return f"""  - Inclusion relevance: {ml_scores.get('inclusion_score', 0):.3f}
  - Exclusion relevance: {ml_scores.get('exclusion_score', 0):.3f}
  - Net score (higher = more likely to include): {ml_scores.get('net_score', 0):.3f}"""

    def _parse_screening_response(self, response: str) -> Dict[str, Any]:
        """Parse structured screening response from AI."""
        lines = response.strip().split("\n")

        result = {
            "decision": "uncertain",
            "reasoning": "",
            "criteria_met": [],
            "criteria_not_met": [],
            "exclusion_criteria_applied": [],
            "exclusion_reason_category": "",
            "confidence": 0.5,
            "next_step": "",
            "flags": "",
            "needs_human_review": False,
        }

        current_field = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for field headers
            if line.startswith("Decision:"):
                decision_text = line.replace("Decision:", "").strip().lower()
                if "include" in decision_text and "exclude" not in decision_text:
                    result["decision"] = "include"
                elif "exclude" in decision_text:
                    result["decision"] = "exclude"
                else:
                    result["decision"] = "uncertain"
                current_field = None

            elif line.startswith("Reasoning:"):
                result["reasoning"] = line.replace("Reasoning:", "").strip()
                current_field = "reasoning"

            elif line.startswith("Criteria Met:"):
                criteria_text = line.replace("Criteria Met:", "").strip()
                if criteria_text and criteria_text.lower() != "none":
                    result["criteria_met"] = [c.strip() for c in criteria_text.split("|") if c.strip()]
                current_field = "criteria_met"

            elif line.startswith("Criteria Not Met:"):
                criteria_text = line.replace("Criteria Not Met:", "").strip()
                if criteria_text and criteria_text.lower() != "none":
                    result["criteria_not_met"] = [c.strip() for c in criteria_text.split("|") if c.strip()]
                current_field = "criteria_not_met"

            elif line.startswith("Exclusion Criteria Applied:"):
                criteria_text = line.replace("Exclusion Criteria Applied:", "").strip()
                if criteria_text and criteria_text.lower() != "none":
                    result["exclusion_criteria_applied"] = [c.strip() for c in criteria_text.split("|") if c.strip()]
                current_field = None

            elif line.startswith("Exclusion Reason Category:"):
                result["exclusion_reason_category"] = line.replace("Exclusion Reason Category:", "").strip()
                current_field = None

            elif line.startswith("Confidence:"):
                try:
                    conf_text = line.replace("Confidence:", "").strip()
                    result["confidence"] = float(re.search(r"[\d.]+", conf_text).group())
                except (ValueError, AttributeError):
                    result["confidence"] = 0.5
                current_field = None

            elif line.startswith("Next Step:"):
                result["next_step"] = line.replace("Next Step:", "").strip()
                current_field = "next_step"

            elif line.startswith("Flags:"):
                result["flags"] = line.replace("Flags:", "").strip()
                current_field = "flags"

            elif current_field:
                # Continuation of previous field
                if current_field == "reasoning":
                    result["reasoning"] += " " + line
                elif current_field == "next_step":
                    result["next_step"] += " " + line
                elif current_field == "flags":
                    result["flags"] += " " + line

        return result

    def _categorize_exclusion_reasons(self, excluded_studies: List[Dict]) -> Dict[str, int]:
        """Categorize and count exclusion reasons."""
        reason_counts = defaultdict(int)

        for study in excluded_studies:
            result = study.get("screening_result", {})
            category = result.get("exclusion_reason_category", "Other")

            # Clean up category name
            if "|" in category:
                category = category.split("|")[0].strip()

            reason_counts[category] += 1

        return dict(reason_counts)

    def _generate_prisma_data(
        self,
        screening_level: str,
        total: int,
        included: int,
        excluded: int,
        uncertain: int,
        exclusion_reasons: Dict[str, int],
    ) -> Dict[str, Any]:
        """Generate PRISMA flow diagram data."""
        return {
            "screening_stage": screening_level,
            "records_screened": total,
            "records_included": included,
            "records_excluded": excluded,
            "records_uncertain": uncertain,
            "exclusion_reasons": exclusion_reasons,
            "flow_data": {
                "input": total,
                "output_included": included,
                "output_excluded": excluded,
                "output_uncertain": uncertain,
            },
        }

    def _calculate_screening_stats(
        self,
        included: List[Dict],
        excluded: List[Dict],
        uncertain: List[Dict],
    ) -> Dict[str, Any]:
        """Calculate detailed screening statistics."""
        all_studies = included + excluded + uncertain
        total = len(all_studies)

        if total == 0:
            return {}

        # Extract confidence scores
        confidences = [
            study.get("screening_result", {}).get("confidence", 0.5)
            for study in all_studies
        ]

        # ML scores (if available)
        ml_scores_available = any(
            study.get("screening_result", {}).get("ml_scores")
            for study in all_studies
        )

        ml_stats = {}
        if ml_scores_available:
            inclusion_scores = [
                study.get("screening_result", {}).get("ml_scores", {}).get("inclusion_score", 0)
                for study in all_studies
            ]
            exclusion_scores = [
                study.get("screening_result", {}).get("ml_scores", {}).get("exclusion_score", 0)
                for study in all_studies
            ]

            ml_stats = {
                "mean_inclusion_score": float(np.mean(inclusion_scores)) if inclusion_scores else 0,
                "mean_exclusion_score": float(np.mean(exclusion_scores)) if exclusion_scores else 0,
                "std_inclusion_score": float(np.std(inclusion_scores)) if inclusion_scores else 0,
                "std_exclusion_score": float(np.std(exclusion_scores)) if exclusion_scores else 0,
            }

        return {
            "total_screened": total,
            "mean_confidence": float(np.mean(confidences)) if confidences else 0,
            "std_confidence": float(np.std(confidences)) if confidences else 0,
            "min_confidence": float(np.min(confidences)) if confidences else 0,
            "max_confidence": float(np.max(confidences)) if confidences else 0,
            "high_confidence_count": sum(1 for c in confidences if c >= 0.8),
            "low_confidence_count": sum(1 for c in confidences if c < 0.7),
            "ml_stats": ml_stats,
        }

    async def calculate_inter_rater_agreement(
        self,
        screening_results_1: List[Dict],
        screening_results_2: List[Dict],
    ) -> Dict[str, float]:
        """Calculate Cohen's kappa for inter-rater agreement.

        Args:
            screening_results_1: First rater's screening results
            screening_results_2: Second rater's screening results

        Returns:
            Agreement statistics including Cohen's kappa
        """
        if len(screening_results_1) != len(screening_results_2):
            logger.error("Cannot compute agreement: different number of results")
            return {}

        # Extract decisions
        decisions_1 = [
            1 if r.get("screening_result", {}).get("decision") == "include" else 0
            for r in screening_results_1
        ]
        decisions_2 = [
            1 if r.get("screening_result", {}).get("decision") == "include" else 0
            for r in screening_results_2
        ]

        if not decisions_1 or not decisions_2:
            return {}

        # Calculate agreement metrics
        agreement = sum(d1 == d2 for d1, d2 in zip(decisions_1, decisions_2))
        percent_agreement = agreement / len(decisions_1) if decisions_1 else 0

        # Calculate Cohen's kappa
        try:
            kappa = cohen_kappa_score(decisions_1, decisions_2)
        except Exception as e:
            logger.error(f"Error calculating Cohen's kappa: {e}")
            kappa = 0.0

        # Count disagreements
        disagreements = sum(d1 != d2 for d1, d2 in zip(decisions_1, decisions_2))

        return {
            "cohens_kappa": float(kappa),
            "percent_agreement": float(percent_agreement),
            "total_compared": len(decisions_1),
            "agreements": int(agreement),
            "disagreements": int(disagreements),
            "interpretation": self._interpret_kappa(kappa),
        }

    @staticmethod
    def _interpret_kappa(kappa: float) -> str:
        """Interpret Cohen's kappa value."""
        if kappa < 0:
            return "Poor (less than chance agreement)"
        elif kappa < 0.20:
            return "Slight agreement"
        elif kappa < 0.40:
            return "Fair agreement"
        elif kappa < 0.60:
            return "Moderate agreement"
        elif kappa < 0.80:
            return "Substantial agreement"
        else:
            return "Almost perfect agreement"
