"""Reviewer Matching Agent - Intelligent manuscript-to-reviewer matching system.

This agent implements the "Medium writer pool" algorithm for matching manuscripts
to expert reviewers based on expertise, availability, diversity, and conflict detection.
"""
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import numpy as np
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentConfig, BaseAgent, AgentRole
from app.models.manuscript import Manuscript
from app.models.researcher import Researcher
from app.models.reviewer_match import ReviewerMatch, ConflictType


class SemanticMatcher:
    """Semantic matching engine for manuscript-reviewer matching.

    Uses TF-IDF vectorization and cosine similarity for semantic matching.
    In production, could be upgraded to sentence-transformers for better results.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=300,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
        )
        self.is_fitted = False

    def fit(self, texts: List[str]):
        """Fit vectorizer on a corpus of texts."""
        if not texts:
            logger.warning("No texts provided to fit semantic matcher")
            return

        try:
            self.vectorizer.fit(texts)
            self.is_fitted = True
            logger.info(f"Fitted semantic matcher on {len(texts)} texts")
        except Exception as e:
            logger.error(f"Error fitting semantic matcher: {e}")
            self.is_fitted = False

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not self.is_fitted or not text1.strip() or not text2.strip():
            return 0.0

        try:
            vectors = self.vectorizer.transform([text1, text2])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0

    def compute_keyword_overlap(self, keywords1: List[str], keywords2: List[str]) -> float:
        """Compute keyword overlap score.

        Args:
            keywords1: First set of keywords
            keywords2: Second set of keywords

        Returns:
            Overlap score (0.0 to 1.0)
        """
        if not keywords1 or not keywords2:
            return 0.0

        # Convert to lowercase sets
        set1 = {k.lower().strip() for k in keywords1}
        set2 = {k.lower().strip() for k in keywords2}

        # Calculate Jaccard similarity
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        if union == 0:
            return 0.0

        return intersection / union


class ReviewerMatchingAgent(BaseAgent):
    """Intelligent Reviewer Matching Agent.

    Matches manuscripts to expert reviewers using a sophisticated multi-factor
    scoring algorithm that considers:
    - Expertise matching (50% weight)
    - Availability scoring (30% weight)
    - Diversity scoring (20% weight)
    - Conflict detection (penalty multiplier)

    Features:
    - Semantic similarity using TF-IDF/cosine similarity
    - Keyword overlap analysis
    - Domain expertise matching
    - Workload and availability assessment
    - Geographic and institutional diversity
    - Comprehensive conflict of interest detection
    - Detailed reasoning and scoring transparency
    """

    def __init__(self, config: AgentConfig, db_session: Optional[AsyncSession] = None):
        """Initialize reviewer matching agent.

        Args:
            config: Agent configuration
            db_session: Database session for queries (optional, can be provided per request)
        """
        config.role = AgentRole.REVIEWER_MATCHING
        super().__init__(config)
        self.semantic_matcher = SemanticMatcher()
        self.db_session = db_session

    def get_system_prompt(self) -> str:
        """Get system prompt for reviewer matching agent."""
        return """You are an Advanced Reviewer Matching Agent for an academic peer review platform.

You are an expert in:
- Academic peer review best practices and ethics
- Conflict of interest detection and management
- Research domain and expertise assessment
- Editorial decision-making for journal operations
- Academic community diversity and inclusion
- Workload balancing for reviewers

Your responsibilities:
1. Match manuscripts to qualified expert reviewers with high precision
2. Evaluate expertise alignment through semantic analysis and keyword matching
3. Assess reviewer availability and current workload
4. Promote geographic, institutional, and career-stage diversity
5. Detect and flag conflicts of interest rigorously
6. Provide detailed, transparent reasoning for all matching decisions
7. Balance quality, speed, and fairness in reviewer selection

Expertise Matching Criteria:
- Keyword overlap: Direct match between manuscript and reviewer keywords
- Domain alignment: Broader field/discipline matching
- Semantic similarity: Conceptual relevance beyond exact keywords
- Publication history: Reviewer's track record in related areas

Availability Assessment:
- Current workload: Number of active reviews
- Response rate: Historical acceptance and completion rates
- Recent activity: Time since last review
- Estimated availability: Self-reported capacity

Diversity Considerations:
- Geographic diversity: Prefer reviewers from different countries/regions
- Institutional diversity: Avoid clustering from same institutions
- Career stage diversity: Balance senior and junior reviewers
- Perspective diversity: Include varied methodological approaches

Conflict of Interest Detection (CRITICAL):
- Same institution: HIGH RISK - Same university/organization
- Coauthorship: CRITICAL RISK - Past or present coauthor relationships
- Recent collaboration: MEDIUM RISK - Joint projects within 2 years
- Advisor-advisee: CRITICAL RISK - Past or present mentorship
- Competitor: MEDIUM RISK - Working on directly competing research
- Personal relationship: Variable risk based on nature

Decision Framework:
For each potential reviewer, provide:
1. Overall match score (0.0-1.0) with component breakdowns
2. Detailed expertise alignment explanation
3. Availability assessment and workload concerns
4. Diversity contributions to the reviewer panel
5. Any detected conflicts with severity levels
6. Confidence in the matching decision (0.0-1.0)
7. Recommendation: HIGHLY_RECOMMENDED | RECOMMENDED | ACCEPTABLE | NOT_RECOMMENDED

Always prioritize academic integrity: When in doubt about conflicts, flag for human review.
Strive for reviewer panels that are expert, available, diverse, and conflict-free."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Find matching reviewers for a manuscript.

        Args:
            input_data: {
                "manuscript_id": UUID,
                "max_results": int (default: 10),
                "min_score": float (default: 0.3),
                "db_session": AsyncSession (optional),
                "diversity_weight": float (default: 0.2),
                "require_availability": bool (default: True),
            }

        Returns:
            Matching results with ranked reviewers
        """
        manuscript_id = input_data.get("manuscript_id")
        max_results = input_data.get("max_results", 10)
        min_score = input_data.get("min_score", 0.3)
        db_session = input_data.get("db_session") or self.db_session
        diversity_weight = input_data.get("diversity_weight", 0.2)
        require_availability = input_data.get("require_availability", True)

        if not manuscript_id:
            raise ValueError("manuscript_id is required")

        if not db_session:
            raise ValueError("Database session is required")

        logger.info(f"ReviewerMatchingAgent matching reviewers for manuscript {manuscript_id}")

        # Find matching reviewers
        matches = await self.find_matching_reviewers(
            manuscript_id=manuscript_id,
            db_session=db_session,
            max_results=max_results,
            min_score=min_score,
            diversity_weight=diversity_weight,
            require_availability=require_availability,
        )

        # Generate summary statistics
        summary = self._generate_matching_summary(matches)

        # AI decision on matching quality
        decision = await self.make_decision(
            "Is this reviewer matching result of high quality and suitable for peer review?",
            input_data={
                "manuscript_id": str(manuscript_id),
                "total_matches": len(matches),
                "avg_score": summary.get("average_overall_score", 0),
                "conflicts_detected": summary.get("total_conflicts", 0),
                "diversity_score": summary.get("diversity_score", 0),
            },
        )

        return {
            "manuscript_id": str(manuscript_id),
            "matches": matches,
            "summary": summary,
            "decision": decision.model_dump(),
        }

    async def find_matching_reviewers(
        self,
        manuscript_id: UUID,
        db_session: AsyncSession,
        max_results: int = 10,
        min_score: float = 0.3,
        diversity_weight: float = 0.2,
        require_availability: bool = True,
    ) -> List[Dict[str, Any]]:
        """Find and rank matching reviewers for a manuscript.

        Args:
            manuscript_id: ID of the manuscript
            db_session: Database session
            max_results: Maximum number of matches to return
            min_score: Minimum overall score threshold
            diversity_weight: Weight for diversity scoring (0.0-1.0)
            require_availability: Whether to filter by availability

        Returns:
            List of reviewer matches with scores and reasoning
        """
        # 1. Fetch manuscript
        manuscript = await self._fetch_manuscript(manuscript_id, db_session)
        if not manuscript:
            raise ValueError(f"Manuscript {manuscript_id} not found")

        # 2. Extract manuscript features
        manuscript_features = self._extract_manuscript_features(manuscript)

        # 3. Fetch potential reviewers
        candidates = await self._fetch_candidate_reviewers(
            manuscript_features,
            db_session,
            require_availability=require_availability,
        )

        if not candidates:
            logger.warning("No candidate reviewers found")
            return []

        # 4. Fit semantic matcher on manuscript + reviewer corpus
        corpus = [manuscript_features["text"]] + [
            self._build_reviewer_text(r) for r in candidates
        ]
        self.semantic_matcher.fit(corpus)

        # 5. Score each candidate
        scored_matches = []
        for candidate in candidates:
            match_data = await self._score_candidate(
                manuscript=manuscript,
                manuscript_features=manuscript_features,
                candidate=candidate,
                diversity_weight=diversity_weight,
            )

            # Apply minimum score filter
            if match_data["overall_score"] >= min_score:
                scored_matches.append(match_data)

        # 6. Rank by overall score
        scored_matches.sort(key=lambda x: x["overall_score"], reverse=True)

        # 7. Apply diversity boost (re-rank slightly to promote diversity)
        scored_matches = self._apply_diversity_boost(scored_matches)

        # 8. Take top N
        top_matches = scored_matches[:max_results]

        # 9. Save to database
        await self._save_matches_to_db(manuscript_id, top_matches, db_session)

        logger.info(
            f"Found {len(top_matches)} matching reviewers for manuscript {manuscript_id} "
            f"(from {len(candidates)} candidates)"
        )

        return top_matches

    async def _fetch_manuscript(
        self, manuscript_id: UUID, db_session: AsyncSession
    ) -> Optional[Manuscript]:
        """Fetch manuscript from database."""
        result = await db_session.execute(
            select(Manuscript).where(Manuscript.id == manuscript_id)
        )
        return result.scalar_one_or_none()

    def _extract_manuscript_features(self, manuscript: Manuscript) -> Dict[str, Any]:
        """Extract features from manuscript for matching.

        Args:
            manuscript: Manuscript object

        Returns:
            Dictionary of extracted features
        """
        # Combine title and abstract
        text = f"{manuscript.title or ''} {manuscript.abstract or ''}"

        # Extract keywords
        keywords = manuscript.keywords or []

        # Infer research domain from keywords/title
        domains = self._infer_domains(text, keywords)

        # Get author information for conflict detection
        authors = manuscript.author_names or []
        affiliations = manuscript.author_affiliations or {}

        return {
            "text": text,
            "title": manuscript.title or "",
            "abstract": manuscript.abstract or "",
            "keywords": keywords,
            "domains": domains,
            "authors": authors,
            "affiliations": affiliations,
            "manuscript_type": manuscript.manuscript_type.value if manuscript.manuscript_type else "research_article",
        }

    def _infer_domains(self, text: str, keywords: List[str]) -> List[str]:
        """Infer research domains from text and keywords.

        This is a simple keyword-based approach. In production, use a trained
        classifier or hierarchical taxonomy.
        """
        domains = []
        text_lower = text.lower()
        keywords_lower = [k.lower() for k in keywords]

        # Domain detection rules (expand as needed)
        domain_patterns = {
            "machine_learning": ["machine learning", "deep learning", "neural network", "ai", "artificial intelligence"],
            "computational_biology": ["bioinformatics", "genomics", "proteomics", "computational biology"],
            "clinical_medicine": ["clinical trial", "patient", "treatment", "diagnosis", "therapy"],
            "neuroscience": ["brain", "neuron", "cognitive", "neural", "fmri"],
            "computer_vision": ["image", "vision", "object detection", "segmentation", "visual"],
            "nlp": ["natural language", "text mining", "sentiment", "language model"],
            "systems_biology": ["pathway", "network", "systems biology", "metabolic"],
            "epidemiology": ["epidemic", "disease", "public health", "population health"],
        }

        for domain, patterns in domain_patterns.items():
            if any(pattern in text_lower or pattern in " ".join(keywords_lower) for pattern in patterns):
                domains.append(domain)

        return domains if domains else ["general"]

    async def _fetch_candidate_reviewers(
        self,
        manuscript_features: Dict[str, Any],
        db_session: AsyncSession,
        require_availability: bool = True,
    ) -> List[Researcher]:
        """Fetch candidate reviewers from database.

        Args:
            manuscript_features: Extracted manuscript features
            db_session: Database session
            require_availability: Whether to filter by availability

        Returns:
            List of candidate researchers
        """
        # Build query
        query = select(Researcher)

        # Filter by domains if available (optional enhancement)
        domains = manuscript_features.get("domains", [])
        if domains and domains != ["general"]:
            # Match researchers with overlapping research domains
            query = query.where(
                or_(
                    *[Researcher.research_domains.contains([domain]) for domain in domains]
                )
            )

        # Filter by availability if required
        if require_availability:
            query = query.where(
                and_(
                    Researcher.current_workload < 10,  # Not overloaded
                    or_(
                        Researcher.estimated_availability > 0.3,
                        Researcher.estimated_availability.is_(None),  # Include if unknown
                    )
                )
            )

        # Limit to active researchers (reviewed recently)
        two_years_ago = datetime.utcnow().date() - timedelta(days=730)
        query = query.where(
            or_(
                Researcher.last_review_date >= two_years_ago,
                Researcher.last_review_date.is_(None),  # Include if unknown
            )
        )

        result = await db_session.execute(query)
        candidates = result.scalars().all()

        return list(candidates)

    def _build_reviewer_text(self, researcher: Researcher) -> str:
        """Build text representation of researcher for semantic matching."""
        keywords = " ".join(researcher.expertise_keywords or [])
        domains = " ".join(researcher.research_domains or [])
        return f"{keywords} {domains}"

    async def _score_candidate(
        self,
        manuscript: Manuscript,
        manuscript_features: Dict[str, Any],
        candidate: Researcher,
        diversity_weight: float,
    ) -> Dict[str, Any]:
        """Score a single candidate reviewer.

        Args:
            manuscript: Manuscript object
            manuscript_features: Extracted manuscript features
            candidate: Candidate researcher
            diversity_weight: Weight for diversity scoring

        Returns:
            Match data with all scores and reasoning
        """
        # 1. Expertise Score (50% weight)
        expertise_score, expertise_details = self._compute_expertise_score(
            manuscript_features, candidate
        )

        # 2. Availability Score (30% weight)
        availability_score, availability_details = self._compute_availability_score(candidate)

        # 3. Diversity Score (20% weight)
        diversity_score, diversity_details = self._compute_diversity_score(candidate)

        # 4. Conflict Detection
        conflict_risk, conflict_details = self._detect_conflicts(
            manuscript_features, candidate
        )

        # 5. Calculate overall score
        # Base score: weighted combination
        base_score = (
            expertise_score * 0.5 +
            availability_score * 0.3 +
            diversity_score * diversity_weight
        )

        # Apply conflict penalty
        overall_score = base_score * (1 - conflict_risk)

        # 6. Generate reasoning
        reasoning = self._generate_matching_reasoning(
            candidate=candidate,
            expertise_score=expertise_score,
            expertise_details=expertise_details,
            availability_score=availability_score,
            availability_details=availability_details,
            diversity_score=diversity_score,
            diversity_details=diversity_details,
            conflict_risk=conflict_risk,
            conflict_details=conflict_details,
            overall_score=overall_score,
        )

        # 7. Determine recommendation level
        recommendation = self._determine_recommendation(overall_score, conflict_risk)

        return {
            "researcher_id": candidate.id,
            "researcher_name": candidate.name,
            "researcher_email": candidate.email,
            "researcher_institution": candidate.institution,
            "researcher_country": candidate.country,
            "overall_score": round(overall_score, 3),
            "expertise_score": round(expertise_score, 3),
            "availability_score": round(availability_score, 3),
            "diversity_score": round(diversity_score, 3),
            "conflict_risk": round(conflict_risk, 3),
            "has_conflict": conflict_risk > 0.5,  # High conflict threshold
            "conflict_types": conflict_details.get("types", []),
            "matching_keywords": expertise_details.get("matching_keywords", []),
            "matching_domains": expertise_details.get("matching_domains", []),
            "expertise_details": expertise_details,
            "availability_details": availability_details,
            "diversity_details": diversity_details,
            "conflict_details": conflict_details,
            "reasoning": reasoning,
            "recommendation": recommendation,
            "confidence": self._calculate_confidence(expertise_score, conflict_risk),
        }

    def _compute_expertise_score(
        self,
        manuscript_features: Dict[str, Any],
        candidate: Researcher,
    ) -> Tuple[float, Dict[str, Any]]:
        """Compute expertise matching score.

        Formula: expertise_score = 0.7 * keyword_match + 0.3 * domain_match

        Args:
            manuscript_features: Manuscript features
            candidate: Candidate researcher

        Returns:
            Tuple of (expertise_score, details)
        """
        manuscript_keywords = manuscript_features.get("keywords", [])
        manuscript_domains = manuscript_features.get("domains", [])
        manuscript_text = manuscript_features.get("text", "")

        candidate_keywords = candidate.expertise_keywords or []
        candidate_domains = candidate.research_domains or []
        candidate_text = self._build_reviewer_text(candidate)

        # 1. Keyword overlap (70%)
        keyword_overlap = self.semantic_matcher.compute_keyword_overlap(
            manuscript_keywords, candidate_keywords
        )

        # 2. Semantic similarity (additional signal)
        semantic_sim = self.semantic_matcher.compute_similarity(
            manuscript_text, candidate_text
        )

        # Combine keyword overlap with semantic similarity
        keyword_match = 0.6 * keyword_overlap + 0.4 * semantic_sim

        # 3. Domain matching (30%)
        domain_match = self.semantic_matcher.compute_keyword_overlap(
            manuscript_domains, candidate_domains
        )

        # 4. Final expertise score
        expertise_score = 0.7 * keyword_match + 0.3 * domain_match

        # Find matching keywords and domains
        matching_keywords = list(
            set(k.lower() for k in manuscript_keywords) &
            set(k.lower() for k in candidate_keywords)
        )
        matching_domains = list(
            set(d.lower() for d in manuscript_domains) &
            set(d.lower() for d in candidate_domains)
        )

        details = {
            "keyword_match": round(keyword_match, 3),
            "keyword_overlap": round(keyword_overlap, 3),
            "semantic_similarity": round(semantic_sim, 3),
            "domain_match": round(domain_match, 3),
            "matching_keywords": matching_keywords,
            "matching_domains": matching_domains,
            "total_candidate_keywords": len(candidate_keywords),
            "total_manuscript_keywords": len(manuscript_keywords),
        }

        return expertise_score, details

    def _compute_availability_score(
        self, candidate: Researcher
    ) -> Tuple[float, Dict[str, Any]]:
        """Compute availability score.

        Formula:
        availability_score = (
            workload_factor * 0.4 +
            response_rate * 0.3 +
            recent_activity * 0.2 +
            estimated_availability * 0.1
        )

        Args:
            candidate: Candidate researcher

        Returns:
            Tuple of (availability_score, details)
        """
        # 1. Workload factor (40%) - lower workload = higher score
        workload = candidate.current_workload or 0
        workload_factor = max(0, 1 - (workload / 10))  # Normalize by max workload of 10

        # 2. Response rate (30%)
        response_rate = candidate.response_rate or 0.5  # Default to average

        # 3. Recent activity (20%) - more recent = higher score
        recent_activity = self._compute_recency_score(candidate.last_review_date)

        # 4. Estimated availability (10%)
        estimated_availability = candidate.estimated_availability or 0.5

        # Weighted combination
        availability_score = (
            workload_factor * 0.4 +
            response_rate * 0.3 +
            recent_activity * 0.2 +
            estimated_availability * 0.1
        )

        details = {
            "current_workload": workload,
            "workload_factor": round(workload_factor, 3),
            "response_rate": round(response_rate, 3),
            "recent_activity": round(recent_activity, 3),
            "estimated_availability": round(estimated_availability, 3),
            "last_review_date": candidate.last_review_date.isoformat() if candidate.last_review_date else None,
            "days_since_last_review": self._days_since_last_review(candidate.last_review_date),
        }

        return availability_score, details

    def _compute_recency_score(self, last_review_date: Optional[Any]) -> float:
        """Compute recency score based on last review date.

        Args:
            last_review_date: Date of last review

        Returns:
            Recency score (0.0-1.0)
        """
        if not last_review_date:
            return 0.5  # Default for unknown

        days_ago = self._days_since_last_review(last_review_date)

        if days_ago < 30:
            return 1.0  # Very recent
        elif days_ago < 90:
            return 0.8  # Recent
        elif days_ago < 180:
            return 0.6  # Moderately recent
        elif days_ago < 365:
            return 0.4  # Last year
        else:
            return 0.2  # Older

    def _days_since_last_review(self, last_review_date: Optional[Any]) -> Optional[int]:
        """Calculate days since last review."""
        if not last_review_date:
            return None

        # Handle both date and datetime objects
        if isinstance(last_review_date, datetime):
            last_date = last_review_date.date()
        else:
            last_date = last_review_date

        delta = datetime.utcnow().date() - last_date
        return delta.days

    def _compute_diversity_score(
        self, candidate: Researcher
    ) -> Tuple[float, Dict[str, Any]]:
        """Compute diversity contribution score.

        This is a simplified version. In practice, diversity should be computed
        relative to the existing reviewer panel.

        Args:
            candidate: Candidate researcher

        Returns:
            Tuple of (diversity_score, details)
        """
        # Placeholder: In production, compare against selected reviewers
        # For now, give bonus for certain attributes

        diversity_score = 0.5  # Base score
        contributions = []

        # Geographic diversity
        if candidate.country and candidate.country not in ["United States", "United Kingdom"]:
            diversity_score += 0.2
            contributions.append("geographic")

        # Career stage diversity (infer from h-index)
        h_index = candidate.h_index or 0
        if 5 <= h_index <= 20:  # Mid-career
            diversity_score += 0.15
            contributions.append("mid_career")
        elif h_index > 40:  # Senior
            diversity_score += 0.1
            contributions.append("senior")

        # Cap at 1.0
        diversity_score = min(1.0, diversity_score)

        details = {
            "country": candidate.country,
            "institution": candidate.institution,
            "h_index": h_index,
            "contributions": contributions,
        }

        return diversity_score, details

    def _detect_conflicts(
        self,
        manuscript_features: Dict[str, Any],
        candidate: Researcher,
    ) -> Tuple[float, Dict[str, Any]]:
        """Detect conflicts of interest.

        Args:
            manuscript_features: Manuscript features
            candidate: Candidate researcher

        Returns:
            Tuple of (conflict_risk, details)
        """
        conflict_risk = 0.0
        conflict_types = []
        details_list = []

        # Get manuscript author information
        authors = manuscript_features.get("authors", [])
        affiliations = manuscript_features.get("affiliations", {})

        # 1. Check same institution (HIGH risk)
        for affiliation in affiliations.values():
            if isinstance(affiliation, str):
                affiliation_lower = affiliation.lower()
                if candidate.institution and candidate.institution.lower() in affiliation_lower:
                    conflict_risk = max(conflict_risk, 0.8)
                    conflict_types.append(ConflictType.INSTITUTION.value)
                    details_list.append(f"Same institution: {candidate.institution}")
                    break

        # 2. Check coauthor relationship (CRITICAL risk)
        # This would require checking candidate's coauthor list
        coauthor_ids = candidate.coauthor_ids or []
        # In production, fetch manuscript author IDs and check overlap
        # For now, simple name matching
        for author in authors:
            if candidate.name.lower() in author.lower() or author.lower() in candidate.name.lower():
                conflict_risk = 1.0  # Maximum risk
                conflict_types.append(ConflictType.COAUTHOR.value)
                details_list.append(f"Author match: {author}")
                break

        # 3. Recent collaboration (MEDIUM risk)
        # Would need collaboration database
        # Placeholder: check if institution collaborator
        inst_collaborators = candidate.institution_collaborators or []
        if inst_collaborators:
            # In production, check if any manuscript authors in this list
            pass

        # 4. Recent review activity on similar topics (MINOR risk)
        # If reviewer just reviewed a very similar paper, might be biased
        # This requires review history - placeholder for now

        details = {
            "risk_score": round(conflict_risk, 3),
            "types": conflict_types,
            "details": details_list,
            "has_critical_conflict": conflict_risk >= 0.8,
        }

        return conflict_risk, details

    def _generate_matching_reasoning(
        self,
        candidate: Researcher,
        expertise_score: float,
        expertise_details: Dict[str, Any],
        availability_score: float,
        availability_details: Dict[str, Any],
        diversity_score: float,
        diversity_details: Dict[str, Any],
        conflict_risk: float,
        conflict_details: Dict[str, Any],
        overall_score: float,
    ) -> str:
        """Generate human-readable reasoning for the match."""
        reasoning_parts = []

        # Header
        reasoning_parts.append(
            f"Reviewer: {candidate.name} ({candidate.institution or 'Unknown institution'})"
        )
        reasoning_parts.append(f"Overall Match Score: {overall_score:.2f}/1.0")
        reasoning_parts.append("")

        # Expertise
        reasoning_parts.append(f"EXPERTISE MATCH ({expertise_score:.2f}/1.0):")
        if expertise_details.get("matching_keywords"):
            reasoning_parts.append(
                f"  - Matching keywords: {', '.join(expertise_details['matching_keywords'][:5])}"
            )
        if expertise_details.get("matching_domains"):
            reasoning_parts.append(
                f"  - Matching domains: {', '.join(expertise_details['matching_domains'])}"
            )
        reasoning_parts.append(
            f"  - Keyword overlap: {expertise_details.get('keyword_overlap', 0):.2f}"
        )
        reasoning_parts.append(
            f"  - Semantic similarity: {expertise_details.get('semantic_similarity', 0):.2f}"
        )
        reasoning_parts.append("")

        # Availability
        reasoning_parts.append(f"AVAILABILITY ({availability_score:.2f}/1.0):")
        reasoning_parts.append(
            f"  - Current workload: {availability_details.get('current_workload', 0)} reviews"
        )
        reasoning_parts.append(
            f"  - Response rate: {availability_details.get('response_rate', 0):.2f}"
        )
        days_since = availability_details.get("days_since_last_review")
        if days_since:
            reasoning_parts.append(f"  - Last review: {days_since} days ago")
        reasoning_parts.append("")

        # Diversity
        reasoning_parts.append(f"DIVERSITY ({diversity_score:.2f}/1.0):")
        if diversity_details.get("contributions"):
            reasoning_parts.append(
                f"  - Contributions: {', '.join(diversity_details['contributions'])}"
            )
        reasoning_parts.append(f"  - Country: {diversity_details.get('country', 'Unknown')}")
        reasoning_parts.append("")

        # Conflicts
        reasoning_parts.append(f"CONFLICTS ({conflict_risk:.2f} risk):")
        if conflict_details.get("types"):
            reasoning_parts.append(
                f"  - Detected: {', '.join(conflict_details['types'])}"
            )
            for detail in conflict_details.get("details", []):
                reasoning_parts.append(f"    * {detail}")
        else:
            reasoning_parts.append("  - No conflicts detected")
        reasoning_parts.append("")

        return "\n".join(reasoning_parts)

    def _determine_recommendation(self, overall_score: float, conflict_risk: float) -> str:
        """Determine recommendation level.

        Args:
            overall_score: Overall match score
            conflict_risk: Conflict risk score

        Returns:
            Recommendation string
        """
        if conflict_risk > 0.7:
            return "NOT_RECOMMENDED"
        elif overall_score >= 0.7:
            return "HIGHLY_RECOMMENDED"
        elif overall_score >= 0.5:
            return "RECOMMENDED"
        elif overall_score >= 0.3:
            return "ACCEPTABLE"
        else:
            return "NOT_RECOMMENDED"

    def _calculate_confidence(self, expertise_score: float, conflict_risk: float) -> float:
        """Calculate confidence in the matching decision.

        Args:
            expertise_score: Expertise match score
            conflict_risk: Conflict risk score

        Returns:
            Confidence score (0.0-1.0)
        """
        # High confidence when expertise is clear and no conflicts
        base_confidence = expertise_score

        # Reduce confidence if conflicts detected
        confidence = base_confidence * (1 - conflict_risk * 0.5)

        return round(confidence, 3)

    def _apply_diversity_boost(
        self, scored_matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply diversity boost to promote panel diversity.

        This re-ranks matches slightly to ensure geographic and institutional
        diversity in the final panel.

        Args:
            scored_matches: List of scored matches (sorted by overall_score)

        Returns:
            Re-ranked matches with diversity boost applied
        """
        if len(scored_matches) <= 3:
            return scored_matches  # Too few to worry about diversity

        # Track countries and institutions
        selected_countries = set()
        selected_institutions = set()

        boosted_matches = []

        for match in scored_matches:
            country = match.get("researcher_country")
            institution = match.get("researcher_institution")

            # Apply diversity boost
            diversity_boost = 0.0

            if country and country not in selected_countries:
                diversity_boost += 0.05  # Small boost for new country
                selected_countries.add(country)

            if institution and institution not in selected_institutions:
                diversity_boost += 0.03  # Small boost for new institution
                selected_institutions.add(institution)

            # Update overall score
            if diversity_boost > 0:
                match["overall_score"] = min(1.0, match["overall_score"] + diversity_boost)
                match["diversity_boost_applied"] = diversity_boost

            boosted_matches.append(match)

        # Re-sort after boosting
        boosted_matches.sort(key=lambda x: x["overall_score"], reverse=True)

        return boosted_matches

    def _generate_matching_summary(
        self, matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate summary statistics for matching results.

        Args:
            matches: List of matches

        Returns:
            Summary dictionary
        """
        if not matches:
            return {
                "total_matches": 0,
                "average_overall_score": 0,
                "average_expertise_score": 0,
                "average_availability_score": 0,
                "average_diversity_score": 0,
                "total_conflicts": 0,
                "high_confidence_count": 0,
            }

        scores = {
            "overall": [m["overall_score"] for m in matches],
            "expertise": [m["expertise_score"] for m in matches],
            "availability": [m["availability_score"] for m in matches],
            "diversity": [m["diversity_score"] for m in matches],
        }

        conflicts = sum(1 for m in matches if m["has_conflict"])
        high_confidence = sum(1 for m in matches if m["confidence"] >= 0.7)

        # Geographic diversity
        countries = set(m["researcher_country"] for m in matches if m["researcher_country"])
        institutions = set(m["researcher_institution"] for m in matches if m["researcher_institution"])

        return {
            "total_matches": len(matches),
            "average_overall_score": round(float(np.mean(scores["overall"])), 3),
            "std_overall_score": round(float(np.std(scores["overall"])), 3),
            "average_expertise_score": round(float(np.mean(scores["expertise"])), 3),
            "average_availability_score": round(float(np.mean(scores["availability"])), 3),
            "average_diversity_score": round(float(np.mean(scores["diversity"])), 3),
            "total_conflicts": conflicts,
            "conflict_rate": round(conflicts / len(matches), 3),
            "high_confidence_count": high_confidence,
            "high_confidence_rate": round(high_confidence / len(matches), 3),
            "unique_countries": len(countries),
            "unique_institutions": len(institutions),
            "diversity_score": round(len(countries) / len(matches), 3),  # Simple diversity metric
        }

    async def _save_matches_to_db(
        self,
        manuscript_id: UUID,
        matches: List[Dict[str, Any]],
        db_session: AsyncSession,
    ) -> None:
        """Save reviewer matches to database.

        Args:
            manuscript_id: Manuscript ID
            matches: List of match data
            db_session: Database session
        """
        for rank, match_data in enumerate(matches, start=1):
            reviewer_match = ReviewerMatch(
                manuscript_id=manuscript_id,
                researcher_id=match_data["researcher_id"],
                expertise_score=match_data["expertise_score"],
                availability_score=match_data["availability_score"],
                diversity_score=match_data["diversity_score"],
                overall_score=match_data["overall_score"],
                rank=rank,
                conflict_risk=match_data["conflict_risk"],
                conflict_types=match_data["conflict_types"],
                conflict_details=match_data["conflict_details"],
                has_conflict=match_data["has_conflict"],
                matching_keywords=match_data["matching_keywords"],
                matching_domains=match_data["matching_domains"],
                expertise_overlap=match_data["expertise_details"],
                estimated_workload=match_data["availability_details"],
                geographic_region=match_data["researcher_country"],
                institution_type=None,  # Could infer from institution name
                career_stage=self._infer_career_stage(match_data),
                reasoning=match_data["reasoning"],
                confidence=match_data["confidence"],
                match_metadata={
                    "recommendation": match_data["recommendation"],
                    "diversity_boost": match_data.get("diversity_boost_applied", 0),
                },
            )

            db_session.add(reviewer_match)

        try:
            await db_session.flush()
            logger.info(f"Saved {len(matches)} reviewer matches to database")
        except Exception as e:
            logger.error(f"Error saving matches to database: {e}")
            raise

    def _infer_career_stage(self, match_data: Dict[str, Any]) -> str:
        """Infer career stage from h-index and other metrics."""
        h_index = match_data.get("diversity_details", {}).get("h_index", 0)

        if h_index < 10:
            return "early_career"
        elif h_index < 25:
            return "mid_career"
        else:
            return "senior"
