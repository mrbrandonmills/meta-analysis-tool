"""Research Direction Agent - Identifies gaps and generates novel research directions.

This agent analyzes completed meta-analysis results to:
1. Identify gaps in the literature (methodological, population, outcome, etc.)
2. Generate novel research questions
3. Create detailed research proposals with methodology
4. Assess feasibility and potential impact
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentConfig, BaseAgent, AgentRole
from app.models.meta_analysis import MetaAnalysis
from app.models.research_gap import ResearchGap, GapType, GapPriority
from app.models.research_proposal import ResearchProposal, ProposalStatus, ProposalType


class ResearchDirectionAgent(BaseAgent):
    """Analyzes meta-analysis results to identify research gaps and generate novel research directions.

    This agent uses Claude AI to perform sophisticated analysis of meta-analysis results,
    identifying patterns, gaps, and opportunities for future research.
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the Research Direction Agent.

        Args:
            config: Agent configuration, defaults to standard research direction config
        """
        if config is None:
            config = AgentConfig(
                name="ResearchDirectionAgent",
                role=AgentRole.SPECIALIST,
                model="claude-sonnet-4-5-20250929",
                temperature=0.4,  # Slightly higher for creative research ideas
                max_tokens=8192,  # Longer output for detailed proposals
                expert_profile="Research Methodology Expert specializing in gap analysis and proposal generation"
            )
        super().__init__(config)
        logger.info("ResearchDirectionAgent initialized")

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Research Direction Agent."""
        return """You are a world-class research methodology expert specializing in identifying research gaps and generating novel research directions.

Your expertise includes:
- Systematic literature review methodology
- Meta-analysis interpretation and heterogeneity analysis
- Research design across multiple disciplines
- Publication bias detection and implications
- Moderator analysis and subgroup effects
- Translational research and practical applications
- Grant writing and research proposal development
- Feasibility assessment and resource planning

When analyzing meta-analysis results, you:
1. Critically examine effect sizes, confidence intervals, and heterogeneity
2. Identify patterns in included/excluded studies
3. Detect methodological limitations and biases
4. Recognize understudied populations, contexts, or outcomes
5. Generate creative yet scientifically rigorous research questions
6. Design feasible studies with appropriate methodology
7. Assess potential impact and contribution to the field

Always provide evidence-based reasoning, cite specific patterns from the data, and ensure your suggestions are actionable and realistic."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process meta-analysis results and generate research directions.

        Args:
            input_data: Contains meta_analysis_results, research_question, included_studies

        Returns:
            Dictionary with gaps_identified, research_questions, research_proposals
        """
        logger.info("Processing meta-analysis for research direction generation")

        try:
            # Extract input data
            meta_analysis_results = input_data.get("meta_analysis_results", {})
            research_question = input_data.get("research_question", "")
            included_studies = input_data.get("included_studies", [])
            focus_areas = input_data.get("focus_areas", [])
            max_proposals = input_data.get("max_proposals", 5)

            # Validate input
            if not meta_analysis_results or not research_question:
                raise ValueError("Missing required input: meta_analysis_results and research_question")

            # Step 1: Identify gaps in the literature
            logger.info("Step 1: Identifying research gaps")
            gaps_identified = await self._identify_gaps(
                meta_analysis_results,
                research_question,
                included_studies,
                focus_areas
            )

            # Step 2: Generate novel research questions
            logger.info("Step 2: Generating research questions")
            research_questions = await self._generate_questions(
                gaps_identified,
                meta_analysis_results,
                research_question
            )

            # Step 3: Create detailed research proposals
            logger.info("Step 3: Creating research proposals")
            research_proposals = await self._create_proposals(
                research_questions,
                gaps_identified,
                meta_analysis_results,
                max_proposals
            )

            # Step 4: Rank proposals by priority
            logger.info("Step 4: Ranking proposals")
            priority_ranking = self._rank_proposals(research_proposals)

            # Calculate completeness score
            completeness_score = self._calculate_completeness(
                gaps_identified,
                research_questions,
                research_proposals
            )

            result = {
                "gaps_identified": gaps_identified,
                "research_questions": research_questions,
                "research_proposals": research_proposals,
                "priority_ranking": priority_ranking,
                "completeness_score": completeness_score,
                "generated_at": datetime.utcnow().isoformat()
            }

            logger.info(f"Research direction generation complete: {len(gaps_identified)} gaps, "
                       f"{len(research_questions)} questions, {len(research_proposals)} proposals")

            return result

        except Exception as e:
            logger.error(f"Error in research direction generation: {e}")
            raise

    async def _identify_gaps(
        self,
        meta_analysis_results: Dict[str, Any],
        research_question: str,
        included_studies: List[Dict],
        focus_areas: List[str]
    ) -> List[Dict[str, Any]]:
        """Identify gaps in the literature based on meta-analysis results.

        Args:
            meta_analysis_results: Results from meta-analysis
            research_question: Original research question
            included_studies: List of included studies
            focus_areas: Specific areas to focus on (optional)

        Returns:
            List of identified gaps with details
        """
        # Prepare context for Claude
        context = self._prepare_gap_analysis_context(
            meta_analysis_results,
            research_question,
            included_studies,
            focus_areas
        )

        prompt = f"""Analyze this meta-analysis and identify significant gaps in the literature.

{context}

Please identify 5-7 significant research gaps. For each gap, provide:

1. **gap_type**: Choose from: population, intervention, outcome, methodology, theoretical, geographic, temporal, interdisciplinary
2. **title**: Brief, descriptive title (max 100 chars)
3. **description**: Detailed description of the gap (2-3 sentences)
4. **evidence**: Specific evidence from the meta-analysis supporting this gap (cite numbers, patterns)
5. **severity**: critical, high, medium, or low
6. **impact_potential**: Score 0.0-1.0 indicating potential impact if addressed
7. **feasibility_score**: Score 0.0-1.0 indicating how feasible it is to address
8. **reasoning**: Your expert reasoning for why this is a significant gap

Focus on gaps that are:
- Supported by concrete evidence from the meta-analysis
- Significant enough to warrant new research
- Feasible to address with realistic resources
- Likely to advance the field meaningfully

Return ONLY valid JSON array format:
[
  {{
    "gap_type": "methodology",
    "title": "Lack of longitudinal studies",
    "description": "...",
    "evidence": "Only 2 of 45 studies used longitudinal designs...",
    "severity": "high",
    "impact_potential": 0.85,
    "feasibility_score": 0.65,
    "reasoning": "..."
  }},
  ...
]"""

        try:
            response = await self.think(prompt)

            # Parse JSON response
            gaps = self._parse_json_response(response)

            # Validate and enhance gaps
            validated_gaps = []
            for gap in gaps:
                if self._validate_gap(gap):
                    # Add additional metadata
                    gap["confidence"] = self._calculate_gap_confidence(gap, meta_analysis_results)
                    gap["identified_at"] = datetime.utcnow().isoformat()
                    validated_gaps.append(gap)

            logger.info(f"Identified {len(validated_gaps)} research gaps")
            return validated_gaps

        except Exception as e:
            logger.error(f"Error identifying gaps: {e}")
            return []

    async def _generate_questions(
        self,
        gaps_identified: List[Dict],
        meta_analysis_results: Dict,
        research_question: str
    ) -> List[Dict[str, Any]]:
        """Generate novel research questions based on identified gaps.

        Args:
            gaps_identified: List of identified gaps
            meta_analysis_results: Meta-analysis results
            research_question: Original research question

        Returns:
            List of research questions with rationale
        """
        # Prepare context
        gaps_summary = self._summarize_gaps(gaps_identified)

        prompt = f"""Based on these identified research gaps, generate 7-10 novel, specific research questions.

Original Research Question: {research_question}

Meta-Analysis Summary:
- Number of studies: {meta_analysis_results.get('n_studies', 'N/A')}
- Pooled effect size: {meta_analysis_results.get('pooled_effect', 'N/A')}
- Heterogeneity (I²): {meta_analysis_results.get('heterogeneity', 'N/A')}
- Publication bias: {meta_analysis_results.get('publication_bias', 'N/A')}

Identified Gaps:
{gaps_summary}

For each research question, provide:

1. **question**: The specific, answerable research question (using PICO format where applicable)
2. **rationale**: Why this question is important and how it addresses identified gaps (2-3 sentences)
3. **gap_addressed**: Which gap(s) this question addresses (reference gap titles)
4. **expected_contribution**: What new knowledge this would contribute
5. **feasibility**: Score 0.0-1.0 based on required resources, time, and complexity
6. **novelty_score**: Score 0.0-1.0 indicating how novel/innovative the question is
7. **priority**: high, medium, or low

Ensure questions are:
- Specific and answerable
- Novel (not already addressed in the meta-analysis)
- Scientifically rigorous
- Feasible to investigate
- Build on the meta-analysis findings

Return ONLY valid JSON array format:
[
  {{
    "question": "Does the intervention effect vary by age group (children vs adults)?",
    "rationale": "...",
    "gap_addressed": "Population diversity gap",
    "expected_contribution": "...",
    "feasibility": 0.75,
    "novelty_score": 0.60,
    "priority": "high"
  }},
  ...
]"""

        try:
            response = await self.think(prompt)
            questions = self._parse_json_response(response)

            # Validate and enhance
            validated_questions = []
            for question in questions:
                if self._validate_question(question):
                    question["generated_at"] = datetime.utcnow().isoformat()
                    validated_questions.append(question)

            logger.info(f"Generated {len(validated_questions)} research questions")
            return validated_questions

        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return []

    async def _create_proposals(
        self,
        research_questions: List[Dict],
        gaps_identified: List[Dict],
        meta_analysis_results: Dict,
        max_proposals: int
    ) -> List[Dict[str, Any]]:
        """Create detailed research proposals for top research questions.

        Args:
            research_questions: Generated research questions
            gaps_identified: Identified gaps
            meta_analysis_results: Meta-analysis results
            max_proposals: Maximum number of proposals to generate

        Returns:
            List of detailed research proposals
        """
        # Select top questions by feasibility and impact
        top_questions = self._select_top_questions(research_questions, max_proposals)

        proposals = []
        for idx, question_data in enumerate(top_questions):
            logger.info(f"Creating proposal {idx + 1}/{len(top_questions)}")

            proposal = await self._create_single_proposal(
                question_data,
                gaps_identified,
                meta_analysis_results
            )

            if proposal:
                proposals.append(proposal)

        logger.info(f"Created {len(proposals)} detailed research proposals")
        return proposals

    async def _create_single_proposal(
        self,
        question_data: Dict,
        gaps_identified: List[Dict],
        meta_analysis_results: Dict
    ) -> Optional[Dict[str, Any]]:
        """Create a single detailed research proposal.

        Args:
            question_data: Research question data
            gaps_identified: All identified gaps
            meta_analysis_results: Meta-analysis results

        Returns:
            Detailed research proposal
        """
        question = question_data.get("question", "")

        prompt = f"""Create a detailed research proposal for this research question.

Research Question: {question}

Question Context:
- Rationale: {question_data.get('rationale', '')}
- Gap Addressed: {question_data.get('gap_addressed', '')}
- Expected Contribution: {question_data.get('expected_contribution', '')}

Meta-Analysis Context:
- Original Research Question: {meta_analysis_results.get('research_question', '')}
- Number of Studies: {meta_analysis_results.get('n_studies', 'N/A')}
- Key Findings: {meta_analysis_results.get('key_findings', '')}

Create a comprehensive research proposal with:

1. **title**: Compelling, descriptive title (max 200 chars)
2. **research_question**: Refined version of the question
3. **background**: Background and significance (3-4 sentences)
4. **significance**: Why this research matters (2-3 sentences)
5. **innovation**: What's innovative about this approach (2-3 sentences)
6. **methodology**:
   - **design**: Study design (e.g., "Randomized Controlled Trial", "Observational Cohort", "Systematic Review")
   - **population**: Target population and sample size estimate
   - **intervention**: Intervention/exposure (if applicable)
   - **comparator**: Comparison/control (if applicable)
   - **outcomes**: Primary and secondary outcomes (array)
   - **measures**: Specific measures/instruments to use (array)
   - **analysis_plan**: Statistical analysis approach (2-3 sentences)
   - **data_collection**: Data collection methods
7. **expected_outcomes**: Expected findings (2-3 sentences)
8. **expected_impact**: Potential impact on field and practice (2-3 sentences)
9. **timeline**: Estimated duration (e.g., "12-18 months")
10. **feasibility_score**: 0.0-1.0 score
11. **impact_score**: 0.0-1.0 score
12. **novelty_score**: 0.0-1.0 score
13. **budget_estimate**: Rough budget category (e.g., "Low ($0-$50K)", "Medium ($50K-$250K)", "High ($250K+)")
14. **key_challenges**: Main challenges to address (array)
15. **mitigation_strategies**: How to address challenges (array)

Return ONLY valid JSON format:
{{
  "title": "...",
  "research_question": "...",
  "background": "...",
  ...
}}"""

        try:
            response = await self.think(prompt)
            proposal = self._parse_json_response(response)

            # Validate and enhance
            if self._validate_proposal(proposal):
                proposal["generated_at"] = datetime.utcnow().isoformat()
                proposal["status"] = "draft"
                proposal["source_question"] = question
                return proposal

            return None

        except Exception as e:
            logger.error(f"Error creating proposal: {e}")
            return None

    def _rank_proposals(self, proposals: List[Dict]) -> List[str]:
        """Rank proposals by composite score of impact, feasibility, and novelty.

        Args:
            proposals: List of research proposals

        Returns:
            List of proposal titles in priority order
        """
        # Calculate composite score for each proposal
        scored_proposals = []
        for proposal in proposals:
            impact = proposal.get("impact_score", 0.5)
            feasibility = proposal.get("feasibility_score", 0.5)
            novelty = proposal.get("novelty_score", 0.5)

            # Weighted composite: impact (40%), feasibility (35%), novelty (25%)
            composite_score = (impact * 0.40) + (feasibility * 0.35) + (novelty * 0.25)

            scored_proposals.append({
                "title": proposal.get("title", ""),
                "score": composite_score
            })

        # Sort by score (descending)
        scored_proposals.sort(key=lambda x: x["score"], reverse=True)

        return [p["title"] for p in scored_proposals]

    def _calculate_completeness(
        self,
        gaps: List[Dict],
        questions: List[Dict],
        proposals: List[Dict]
    ) -> float:
        """Calculate completeness score of the research direction analysis.

        Args:
            gaps: Identified gaps
            questions: Generated questions
            proposals: Created proposals

        Returns:
            Completeness score 0.0-1.0
        """
        # Base scores
        gap_score = min(len(gaps) / 5.0, 1.0)  # Target: 5+ gaps
        question_score = min(len(questions) / 7.0, 1.0)  # Target: 7+ questions
        proposal_score = min(len(proposals) / 3.0, 1.0)  # Target: 3+ proposals

        # Diversity score (check gap types)
        unique_gap_types = len(set(g.get("gap_type", "") for g in gaps))
        diversity_score = min(unique_gap_types / 4.0, 1.0)  # Target: 4+ types

        # Quality score (average of all feasibility scores)
        all_feasibility = [g.get("feasibility_score", 0.5) for g in gaps]
        all_feasibility.extend([q.get("feasibility", 0.5) for q in questions])
        all_feasibility.extend([p.get("feasibility_score", 0.5) for p in proposals])
        quality_score = sum(all_feasibility) / len(all_feasibility) if all_feasibility else 0.5

        # Weighted composite
        completeness = (
            gap_score * 0.25 +
            question_score * 0.25 +
            proposal_score * 0.25 +
            diversity_score * 0.10 +
            quality_score * 0.15
        )

        return round(completeness, 3)

    # Helper methods

    def _prepare_gap_analysis_context(
        self,
        meta_analysis_results: Dict,
        research_question: str,
        included_studies: List[Dict],
        focus_areas: List[str]
    ) -> str:
        """Prepare context for gap analysis."""
        context_parts = [
            f"**Research Question**: {research_question}",
            f"\n**Number of Studies**: {len(included_studies)}",
        ]

        # Add meta-analysis statistics
        if "pooled_effect" in meta_analysis_results:
            context_parts.append(f"\n**Pooled Effect Size**: {meta_analysis_results['pooled_effect']}")
        if "confidence_interval" in meta_analysis_results:
            ci = meta_analysis_results["confidence_interval"]
            context_parts.append(f"**95% CI**: [{ci.get('lower', 'N/A')}, {ci.get('upper', 'N/A')}]")
        if "heterogeneity" in meta_analysis_results:
            context_parts.append(f"\n**Heterogeneity (I²)**: {meta_analysis_results['heterogeneity']}%")
        if "publication_bias" in meta_analysis_results:
            context_parts.append(f"**Publication Bias**: {meta_analysis_results['publication_bias']}")

        # Add study characteristics
        if included_studies:
            study_years = [s.get("year", 0) for s in included_studies if s.get("year")]
            if study_years:
                context_parts.append(f"\n**Study Years**: {min(study_years)} - {max(study_years)}")

            # Sample characteristics
            total_n = sum(s.get("sample_size", 0) for s in included_studies)
            context_parts.append(f"**Total Sample Size**: {total_n}")

        # Add focus areas if specified
        if focus_areas:
            context_parts.append(f"\n**Focus Areas**: {', '.join(focus_areas)}")

        # Add key findings
        if "key_findings" in meta_analysis_results:
            context_parts.append(f"\n**Key Findings**:\n{meta_analysis_results['key_findings']}")

        return "\n".join(context_parts)

    def _summarize_gaps(self, gaps: List[Dict]) -> str:
        """Create a concise summary of identified gaps."""
        if not gaps:
            return "No gaps identified."

        summary_parts = []
        for idx, gap in enumerate(gaps, 1):
            summary_parts.append(
                f"{idx}. [{gap.get('gap_type', 'unknown').upper()}] {gap.get('title', '')}\n"
                f"   - {gap.get('description', '')}\n"
                f"   - Evidence: {gap.get('evidence', 'N/A')}\n"
                f"   - Severity: {gap.get('severity', 'N/A')}"
            )

        return "\n\n".join(summary_parts)

    def _select_top_questions(self, questions: List[Dict], max_count: int) -> List[Dict]:
        """Select top research questions by composite score."""
        # Calculate composite score
        for question in questions:
            feasibility = question.get("feasibility", 0.5)
            novelty = question.get("novelty_score", 0.5)
            priority_map = {"high": 1.0, "medium": 0.6, "low": 0.3}
            priority = priority_map.get(question.get("priority", "medium"), 0.6)

            question["composite_score"] = (feasibility * 0.4) + (novelty * 0.3) + (priority * 0.3)

        # Sort and select top
        questions.sort(key=lambda x: x.get("composite_score", 0), reverse=True)
        return questions[:max_count]

    def _parse_json_response(self, response: str) -> Any:
        """Parse JSON from Claude response, handling markdown code blocks."""
        try:
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            response = response.strip()
            return json.loads(response)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}\nResponse: {response[:500]}")
            # Try to extract JSON array or object
            import re
            json_match = re.search(r'(\[.*\]|\{.*\})', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            return [] if "[" in response else {}

    def _validate_gap(self, gap: Dict) -> bool:
        """Validate a research gap has required fields."""
        required = ["gap_type", "title", "description", "evidence", "severity"]
        return all(gap.get(field) for field in required)

    def _validate_question(self, question: Dict) -> bool:
        """Validate a research question has required fields."""
        required = ["question", "rationale", "expected_contribution"]
        return all(question.get(field) for field in required)

    def _validate_proposal(self, proposal: Dict) -> bool:
        """Validate a research proposal has required fields."""
        required = ["title", "research_question", "methodology"]
        return all(proposal.get(field) for field in required)

    def _calculate_gap_confidence(self, gap: Dict, meta_analysis_results: Dict) -> float:
        """Calculate confidence score for an identified gap."""
        # Base confidence on evidence strength
        evidence = gap.get("evidence", "")
        confidence = 0.6  # Base confidence

        # Increase if specific numbers cited
        import re
        if re.search(r'\d+', evidence):
            confidence += 0.1

        # Increase for high severity
        if gap.get("severity") == "critical":
            confidence += 0.15
        elif gap.get("severity") == "high":
            confidence += 0.10

        # Adjust based on sample size
        n_studies = meta_analysis_results.get("n_studies", 0)
        if n_studies > 20:
            confidence += 0.1
        elif n_studies < 5:
            confidence -= 0.1

        return min(max(confidence, 0.0), 1.0)

    async def analyze_meta_analysis(
        self,
        db: AsyncSession,
        meta_analysis_id: UUID,
        focus_areas: Optional[List[str]] = None,
        max_proposals: int = 5
    ) -> Dict[str, Any]:
        """High-level method to analyze a completed meta-analysis.

        Args:
            db: Database session
            meta_analysis_id: ID of completed meta-analysis
            focus_areas: Specific areas to focus on
            max_proposals: Maximum number of proposals to generate

        Returns:
            Complete research direction analysis
        """
        logger.info(f"Analyzing meta-analysis {meta_analysis_id} for research directions")

        # Fetch meta-analysis from database
        result = await db.execute(
            select(MetaAnalysis).where(MetaAnalysis.id == meta_analysis_id)
        )
        meta_analysis = result.scalar_one_or_none()

        if not meta_analysis:
            raise ValueError(f"Meta-analysis {meta_analysis_id} not found")

        # Prepare input data
        # Note: In production, you'd fetch included_studies from the database
        # For now, we'll create a mock structure
        input_data = {
            "meta_analysis_results": {
                "research_question": meta_analysis.research_question,
                "topic": meta_analysis.topic,
                "n_studies": 0,  # Would come from actual analysis
                "pooled_effect": "N/A",  # Would come from actual analysis
                "heterogeneity": "N/A",  # Would come from actual analysis
                "publication_bias": "N/A",  # Would come from actual analysis
                "key_findings": "Analysis results would be loaded here"
            },
            "research_question": meta_analysis.research_question,
            "included_studies": [],  # Would come from actual analysis
            "focus_areas": focus_areas or [],
            "max_proposals": max_proposals
        }

        # Process
        return await self.process(input_data)
