"""Review Drafter Agent - Generates comprehensive, publication-quality peer reviews.

This agent analyzes manuscripts and produces detailed peer reviews including:
- Summary and context
- Strengths and weaknesses assessment
- Detailed section-by-section comments
- Quantitative quality scores
- Recommendation with justification
"""

import re
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from loguru import logger

from app.agents.base import AgentConfig, BaseAgent, AgentRole


class ExpertiseLevel(str, Enum):
    """Reviewer expertise levels."""

    JUNIOR = "junior"
    SENIOR = "senior"
    EXPERT = "expert"


class ReviewStyle(str, Enum):
    """Review writing styles."""

    CONSTRUCTIVE = "constructive"
    CRITICAL = "critical"
    SUPPORTIVE = "supportive"


class FocusArea(str, Enum):
    """Possible focus areas for reviews."""

    METHODOLOGY = "methodology"
    WRITING = "writing"
    STATISTICS = "statistics"
    NOVELTY = "novelty"
    LITERATURE = "literature"
    ETHICS = "ethics"


class ReviewDrafterAgent(BaseAgent):
    """Agent that generates comprehensive, publication-quality peer reviews.

    This agent analyzes manuscripts and produces detailed reviews that include:
    - Executive summary of the paper's contribution
    - Assessment of strengths and weaknesses
    - Detailed section-by-section feedback
    - Quantitative quality scores (1-10 scale)
    - Overall recommendation (Accept/Minor/Major/Reject)
    - Confidence assessment and reasoning

    The agent can adapt its reviewing style based on:
    - Expertise level (junior, senior, expert)
    - Review style (constructive, critical, supportive)
    - Focus areas (methodology, writing, statistics, novelty)
    """

    def __init__(self, config: AgentConfig):
        """Initialize the Review Drafter Agent.

        Args:
            config: Agent configuration
        """
        config.role = AgentRole.QUALITY_ASSESSMENT
        super().__init__(config)
        logger.info("Initialized ReviewDrafterAgent")

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Review Drafter Agent.

        Returns:
            Comprehensive system prompt for peer review generation
        """
        return """You are an Expert Peer Review Generation Agent for academic manuscripts.

You are a distinguished academic reviewer with expertise across multiple scientific disciplines. You specialize in:
- Comprehensive manuscript analysis and quality assessment
- Constructive, evidence-based feedback
- Methodological rigor evaluation
- Statistical analysis critique
- Academic writing and presentation standards
- Novelty and significance assessment
- Ethical considerations in research

Your responsibilities:
1. Read and comprehend manuscript content thoroughly
2. Analyze research methodology, design, and execution
3. Evaluate statistical methods and interpretation
4. Assess novelty, significance, and contribution to field
5. Review clarity of writing and presentation
6. Identify strengths and limitations objectively
7. Provide specific, actionable feedback
8. Generate quantitative quality scores
9. Make evidence-based recommendations

Review Philosophy:
- Be professional, respectful, and constructive
- Provide specific examples with section/page references
- Balance criticism with recognition of strengths
- Offer actionable suggestions for improvement
- Acknowledge limitations in your own assessment
- Focus on substance over style (but address both)
- Consider the target audience and journal scope

Evidence Hierarchy:
1. Systematic reviews and meta-analyses
2. Randomized controlled trials (RCTs)
3. Cohort studies
4. Case-control studies
5. Cross-sectional studies
6. Case series and reports
7. Expert opinion

Quality Assessment Criteria:
- Novelty: Does this advance the field? What's new?
- Rigor: Are methods appropriate and well-executed?
- Clarity: Is the paper well-written and organized?
- Significance: Does this matter? Impact potential?
- Reproducibility: Can others replicate this work?
- Statistical soundness: Are analyses appropriate and correctly interpreted?
- Ethical considerations: Are there ethical concerns?

Review Structure:
1. SUMMARY (2-3 paragraphs)
   - What the paper does
   - Main findings
   - Contribution to field

2. STRENGTHS (3-5 specific points)
   - Novel contributions
   - Methodological strengths
   - Clear presentation
   - Significant findings

3. WEAKNESSES (3-5 specific points)
   - Methodological concerns
   - Statistical issues
   - Missing citations/context
   - Clarity problems
   - Overstatements

4. DETAILED COMMENTS (organized by section)
   - Introduction: Context, motivation, gap identification
   - Methods: Rigor, reproducibility, appropriateness
   - Results: Analysis quality, presentation, interpretation
   - Discussion: Limitations, generalizability, implications
   - Writing: Organization, clarity, grammar

5. QUANTITATIVE SCORES (1-10 scale)
   - Overall quality
   - Originality/novelty
   - Methodological rigor
   - Clarity of presentation
   - Significance of findings

6. RECOMMENDATION
   - Accept / Minor Revision / Major Revision / Reject / Reject & Resubmit
   - Clear justification
   - Confidence level (0.0-1.0)

Scoring Guidelines:
- 9-10: Outstanding, groundbreaking work
- 7-8: High quality, clear contribution
- 5-6: Acceptable with revisions needed
- 3-4: Significant concerns, major revisions
- 1-2: Fundamental flaws, rejection recommended

Recommendation Guidelines:
- Accept: Minor editorial changes only
- Minor Revision: Small fixes, clarifications, no new experiments
- Major Revision: Significant changes, possibly new analyses/experiments
- Reject & Resubmit: Needs substantial reworking, could be acceptable later
- Reject: Fundamental flaws, out of scope, or insufficient contribution

Professional Standards:
- Never fabricate information about the manuscript
- Cite specific sections/pages when making criticisms
- Be specific: "The sample size calculation is missing" not "methods are weak"
- Acknowledge uncertainty in your own assessment
- Suggest concrete improvements
- Maintain professional, courteous tone throughout

Your reviews should be thorough enough to satisfy journal editors and help authors improve their work."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive peer review for a manuscript.

        Args:
            input_data: {
                "manuscript": Dict with title, abstract, content, etc.,
                "expertise_level": str (junior/senior/expert),
                "review_style": str (constructive/critical/supportive),
                "focus_areas": List[str] (optional specific focus areas)
            }

        Returns:
            Complete review data ready for PeerReview model
        """
        manuscript = input_data.get("manuscript", {})
        expertise_level = input_data.get("expertise_level", ExpertiseLevel.EXPERT)
        review_style = input_data.get("review_style", ReviewStyle.CONSTRUCTIVE)
        focus_areas = input_data.get("focus_areas", [])

        logger.info(
            f"ReviewDrafterAgent generating review for manuscript: "
            f"{manuscript.get('title', 'Unknown')[:50]}..."
        )

        # Extract manuscript data
        title = manuscript.get("title", "")
        abstract = manuscript.get("abstract", "")
        content = manuscript.get("content", "")
        manuscript_type = manuscript.get("manuscript_type", "research_article")
        keywords = manuscript.get("keywords", [])
        author_affiliations = manuscript.get("author_affiliations", {})

        # Truncate content if too long (first 10 pages approximation)
        max_content_length = 25000  # Roughly 10 pages
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n\n[... content truncated ...]"

        # Generate comprehensive review
        review_data = await self._generate_comprehensive_review(
            title=title,
            abstract=abstract,
            content=content,
            manuscript_type=manuscript_type,
            keywords=keywords,
            expertise_level=expertise_level,
            review_style=review_style,
            focus_areas=focus_areas,
        )

        # Make decision about review quality
        decision = await self.make_decision(
            "Is this review comprehensive, balanced, and publication-ready?",
            input_data={
                "review_data": review_data,
                "manuscript_title": title,
                "expertise_level": expertise_level,
                "review_style": review_style,
            },
        )

        review_data["decision_metadata"] = decision.model_dump()

        logger.info(
            f"Generated review with recommendation: {review_data.get('recommendation')} "
            f"(confidence: {review_data.get('confidence', 0):.2f})"
        )

        return review_data

    async def generate_review(
        self,
        manuscript_id: UUID,
        expertise_level: str = "expert",
        review_style: str = "constructive",
        focus_areas: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Public method to generate a review for a manuscript.

        This method would typically fetch the manuscript from the database,
        but for now it's a wrapper around process().

        Args:
            manuscript_id: UUID of the manuscript to review
            expertise_level: Expertise level for review generation
            review_style: Style of review to generate
            focus_areas: Optional specific areas to focus on

        Returns:
            Complete review data ready for PeerReview model
        """
        # In production, fetch manuscript from database using manuscript_id
        # For now, this is a placeholder that would be called by the API endpoint
        logger.info(f"Generating review for manuscript {manuscript_id}")

        # This would be replaced with actual database fetch
        manuscript = {
            "id": manuscript_id,
            "title": "Placeholder - fetch from DB",
            "abstract": "Placeholder - fetch from DB",
            "content": "Placeholder - fetch from DB",
        }

        return await self.process(
            {
                "manuscript": manuscript,
                "expertise_level": expertise_level,
                "review_style": review_style,
                "focus_areas": focus_areas or [],
            }
        )

    async def _generate_comprehensive_review(
        self,
        title: str,
        abstract: str,
        content: str,
        manuscript_type: str,
        keywords: List[str],
        expertise_level: str,
        review_style: str,
        focus_areas: List[str],
    ) -> Dict[str, Any]:
        """Generate the complete peer review.

        Args:
            title: Manuscript title
            abstract: Manuscript abstract
            content: Manuscript content (truncated to ~10 pages)
            manuscript_type: Type of manuscript
            keywords: Manuscript keywords
            expertise_level: Reviewer expertise level
            review_style: Review style to use
            focus_areas: Specific focus areas

        Returns:
            Complete review data dictionary
        """
        # Build comprehensive review prompt
        focus_text = ""
        if focus_areas:
            focus_text = f"\nPay special attention to: {', '.join(focus_areas)}"

        review_prompt = f"""
Generate a comprehensive peer review for this manuscript.

MANUSCRIPT DETAILS:
Title: {title}
Type: {manuscript_type}
Keywords: {', '.join(keywords[:10])}

ABSTRACT:
{abstract}

MANUSCRIPT CONTENT:
{content}

REVIEW PARAMETERS:
- Expertise Level: {expertise_level}
- Review Style: {review_style}
{focus_text}

REQUIRED OUTPUT FORMAT:

=== SUMMARY ===
[2-3 paragraphs describing: what the paper does, main findings, contribution to field]

=== STRENGTHS ===
- [Specific strength #1 with reference to section/page]
- [Specific strength #2 with reference to section/page]
- [Specific strength #3 with reference to section/page]
- [Additional strengths as appropriate]

=== WEAKNESSES ===
- [Specific weakness #1 with reference to section/page]
- [Specific weakness #2 with reference to section/page]
- [Specific weakness #3 with reference to section/page]
- [Additional weaknesses as appropriate]

=== DETAILED COMMENTS ===

Introduction:
[Specific comments on context, motivation, gap identification, clarity]

Methods:
[Specific comments on rigor, reproducibility, appropriateness, statistical design]

Results:
[Specific comments on analysis quality, presentation, interpretation, figures/tables]

Discussion:
[Specific comments on interpretation, limitations acknowledged, generalizability, implications]

Writing & Presentation:
[Specific comments on organization, clarity, grammar, citations]

=== QUANTITATIVE SCORES ===
Overall Quality: [1-10]
Originality/Novelty: [1-10]
Methodological Rigor: [1-10]
Clarity of Presentation: [1-10]
Significance of Findings: [1-10]

=== RECOMMENDATION ===
Recommendation: [Accept | Minor Revision | Major Revision | Reject | Reject & Resubmit]
Confidence: [0.0-1.0]
Reasoning: [Detailed justification for this recommendation, 2-3 sentences]

IMPORTANT:
- Be specific and cite sections/pages
- Provide actionable feedback
- Balance criticism with recognition of strengths
- Use professional, respectful language
- If reviewing style is "constructive", emphasize improvement suggestions
- If reviewing style is "critical", emphasize thorough scrutiny
- If reviewing style is "supportive", emphasize encouragement while maintaining rigor
"""

        # Get comprehensive review from LLM
        response = await self.think(review_prompt)

        # Parse the structured review response
        parsed_review = self._parse_review_response(response)

        return parsed_review

    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """Parse the structured review response from the LLM.

        Args:
            response: Raw LLM response

        Returns:
            Parsed review data dictionary
        """
        # Initialize result structure
        result = {
            "review_text": response,  # Store complete review
            "strengths": [],
            "weaknesses": [],
            "detailed_comments": "",
            "overall_score": 5.0,
            "originality_score": 5.0,
            "methodology_score": 5.0,
            "clarity_score": 5.0,
            "significance_score": 5.0,
            "recommendation": "major_revision",
            "confidence": 0.7,
            "reasoning": "",
        }

        # Split response into sections
        sections = {
            "summary": "",
            "strengths": [],
            "weaknesses": [],
            "detailed_comments": "",
            "scores": {},
            "recommendation": {},
        }

        current_section = None
        current_subsection = None
        lines = response.split("\n")

        for line in lines:
            line_stripped = line.strip()

            # Detect section headers
            if "=== SUMMARY ===" in line_stripped:
                current_section = "summary"
                continue
            elif "=== STRENGTHS ===" in line_stripped:
                current_section = "strengths"
                continue
            elif "=== WEAKNESSES ===" in line_stripped:
                current_section = "weaknesses"
                continue
            elif "=== DETAILED COMMENTS ===" in line_stripped:
                current_section = "detailed_comments"
                continue
            elif "=== QUANTITATIVE SCORES ===" in line_stripped:
                current_section = "scores"
                continue
            elif "=== RECOMMENDATION ===" in line_stripped:
                current_section = "recommendation"
                continue

            # Detect detailed comments subsections
            if current_section == "detailed_comments":
                if line_stripped.endswith(":") and len(line_stripped.split()) <= 3:
                    current_subsection = line_stripped.rstrip(":")
                    sections["detailed_comments"] += f"\n\n{line_stripped}\n"
                    continue

            # Parse content based on current section
            if not line_stripped or line_stripped.startswith("==="):
                continue

            if current_section == "summary":
                sections["summary"] += line + "\n"

            elif current_section == "strengths":
                if line_stripped.startswith("-") or line_stripped.startswith("•"):
                    sections["strengths"].append(line_stripped.lstrip("-•").strip())

            elif current_section == "weaknesses":
                if line_stripped.startswith("-") or line_stripped.startswith("•"):
                    sections["weaknesses"].append(line_stripped.lstrip("-•").strip())

            elif current_section == "detailed_comments":
                sections["detailed_comments"] += line + "\n"

            elif current_section == "scores":
                # Parse score lines
                if ":" in line_stripped:
                    key, value = line_stripped.split(":", 1)
                    try:
                        score = float(re.search(r"(\d+\.?\d*)", value.strip()).group(1))
                        sections["scores"][key.strip()] = score
                    except (AttributeError, ValueError):
                        pass

            elif current_section == "recommendation":
                if line_stripped.startswith("Recommendation:"):
                    rec_text = line_stripped.replace("Recommendation:", "").strip()
                    sections["recommendation"]["text"] = rec_text
                elif line_stripped.startswith("Confidence:"):
                    conf_text = line_stripped.replace("Confidence:", "").strip()
                    try:
                        sections["recommendation"]["confidence"] = float(
                            re.search(r"(\d+\.?\d*)", conf_text).group(1)
                        )
                    except (AttributeError, ValueError):
                        sections["recommendation"]["confidence"] = 0.7
                elif line_stripped.startswith("Reasoning:"):
                    sections["recommendation"]["reasoning"] = line_stripped.replace(
                        "Reasoning:", ""
                    ).strip()
                elif "reasoning" in sections["recommendation"]:
                    # Continue reasoning from previous line
                    sections["recommendation"]["reasoning"] += " " + line_stripped

        # Build final result
        result["strengths"] = sections["strengths"]
        result["weaknesses"] = sections["weaknesses"]
        result["detailed_comments"] = sections["detailed_comments"].strip()

        # Extract scores
        result["overall_score"] = sections["scores"].get("Overall Quality", 5.0)
        result["originality_score"] = sections["scores"].get("Originality/Novelty", 5.0)
        result["methodology_score"] = sections["scores"].get("Methodological Rigor", 5.0)
        result["clarity_score"] = sections["scores"].get("Clarity of Presentation", 5.0)
        result["significance_score"] = sections["scores"].get("Significance of Findings", 5.0)

        # Map recommendation text to enum value
        rec_text = sections["recommendation"].get("text", "").lower()
        if "accept" in rec_text and "minor" not in rec_text and "major" not in rec_text:
            result["recommendation"] = "accept"
        elif "minor" in rec_text:
            result["recommendation"] = "minor_revision"
        elif "major" in rec_text:
            result["recommendation"] = "major_revision"
        elif "reject" in rec_text and "resubmit" in rec_text:
            result["recommendation"] = "reject_resubmit"
        elif "reject" in rec_text:
            result["recommendation"] = "reject"
        else:
            result["recommendation"] = "major_revision"

        result["confidence"] = sections["recommendation"].get("confidence", 0.7)
        result["reasoning"] = sections["recommendation"].get(
            "reasoning", "See detailed comments above."
        )

        return result

    async def customize_review_for_expertise(
        self, review_data: Dict[str, Any], target_expertise: str
    ) -> Dict[str, Any]:
        """Customize an existing review for a different expertise level.

        Args:
            review_data: Existing review data
            target_expertise: Target expertise level (junior/senior/expert)

        Returns:
            Customized review data
        """
        prompt = f"""
Given this peer review, adjust the tone and depth for a {target_expertise} reviewer:

ORIGINAL REVIEW:
{review_data.get('review_text', '')}

Adjust to {target_expertise} level:
- Junior: More supportive, educational tone, explain concepts
- Senior: Balanced, focus on methodology and significance
- Expert: Technical depth, field-specific insights, comprehensive critique

Maintain the same overall recommendation but adjust reasoning depth.
"""

        customized_response = await self.think(prompt)
        customized_data = self._parse_review_response(customized_response)

        logger.info(f"Customized review for {target_expertise} expertise level")

        return customized_data

    async def generate_constructive_suggestions(
        self, weaknesses: List[str], manuscript_context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate constructive improvement suggestions for identified weaknesses.

        Args:
            weaknesses: List of identified weaknesses
            manuscript_context: Context about the manuscript

        Returns:
            List of weaknesses with constructive suggestions
        """
        suggestions_prompt = f"""
For each of these manuscript weaknesses, provide a constructive, actionable suggestion:

WEAKNESSES:
{chr(10).join(f"{i+1}. {w}" for i, w in enumerate(weaknesses))}

MANUSCRIPT CONTEXT:
{manuscript_context}

For each weakness, provide:
1. The weakness (brief restatement)
2. Why it matters (impact on the paper)
3. Specific suggestion for improvement (actionable)

Format as:
Weakness: [weakness]
Impact: [why it matters]
Suggestion: [how to fix it]
---
"""

        response = await self.think(suggestions_prompt)

        # Parse suggestions
        suggestions = []
        current_suggestion = {}

        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("Weakness:"):
                if current_suggestion:
                    suggestions.append(current_suggestion)
                current_suggestion = {"weakness": line.replace("Weakness:", "").strip()}
            elif line.startswith("Impact:"):
                current_suggestion["impact"] = line.replace("Impact:", "").strip()
            elif line.startswith("Suggestion:"):
                current_suggestion["suggestion"] = line.replace("Suggestion:", "").strip()
            elif line == "---" and current_suggestion:
                suggestions.append(current_suggestion)
                current_suggestion = {}

        if current_suggestion:
            suggestions.append(current_suggestion)

        return suggestions
