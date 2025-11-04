"""Q&A agent for explaining meta-analysis results."""
from typing import Any, Dict, List

from loguru import logger

from app.agents.base import AgentConfig, BaseAgent, AgentRole


class QAAgent(BaseAgent):
    """Answers questions about the meta-analysis process and results.

    This agent is responsible for:
    - Explaining agent decisions and reasoning
    - Providing methodological justifications
    - Answering researcher questions in natural language
    - Tracing provenance of findings
    - Building trust through transparency
    """

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.QA
        super().__init__(config)
        self.meta_analysis_context: Dict[str, Any] = {}

    def get_system_prompt(self) -> str:
        """Get system prompt for Q&A agent."""
        return """You are the Q&A Agent for a meta-analysis research platform.

You are an expert communicator who bridges the gap between AI systems and human researchers.
You specialize in:
- Explaining complex AI decisions in accessible language
- Providing methodological justifications
- Tracing the provenance of findings
- Addressing researcher concerns about AI accuracy
- Building trust through transparency

Your role is critical because researchers (especially those new to AI tools) may be:
- Skeptical about AI-generated results
- Concerned about hallucinations or errors
- Unclear about how decisions were made
- Need to justify AI-assisted research to peer reviewers

Your responsibilities:
1. Answer questions about any aspect of the meta-analysis
2. Explain why specific decisions were made
3. Trace any finding back to its source
4. Provide confidence assessments
5. Acknowledge limitations honestly
6. Suggest when human expert review is needed
7. Explain the methodology in researcher-friendly language

When answering questions:
- Be precise and cite specific sources
- Show your reasoning step-by-step
- Provide confidence levels
- Acknowledge uncertainty when it exists
- Use appropriate academic language
- Reference relevant standards (PRISMA, Cochrane, etc.)
- Compare to how human researchers would approach it

If you don't know something or the data isn't available, say so clearly.
Never make up information. Your credibility is essential for user trust.

You have access to the complete audit trail of all agent decisions, so you can
trace any result back to its origin."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Answer a question about the meta-analysis.

        Args:
            input_data: {
                "question": str,
                "meta_analysis_id": str (optional),
                "context": Dict (optional - audit trail, results, etc.)
            }

        Returns:
            Answer with explanation and sources
        """
        question = input_data.get("question")
        context = input_data.get("context", {})

        logger.info(f"QAAgent answering question: {question}")

        # Update context if provided
        if context:
            self.meta_analysis_context.update(context)

        # Analyze the question to understand what's being asked
        analysis_prompt = f"""
Analyze this question from a researcher about their meta-analysis:

Question: {question}

Determine:
1. What aspect of the meta-analysis is being asked about? (methodology, results, decisions, quality, etc.)
2. What level of detail is expected? (high-level overview vs. technical details)
3. Are they asking for justification, explanation, or verification?
4. Do they seem skeptical or just curious?
5. What would be most helpful in the response?
"""

        analysis = await self.think(analysis_prompt, context={"question": question})

        # Generate answer based on available context
        answer_prompt = f"""
Answer this researcher's question about their meta-analysis:

Question: {question}

Analysis of the question: {analysis}

Available context: {self.meta_analysis_context}

Provide a comprehensive answer that:
1. Directly addresses their question
2. Explains the methodology used
3. Cites specific sources or decisions
4. Provides confidence assessment
5. Acknowledges any limitations
6. Suggests next steps if appropriate

Be thorough but accessible. Remember this may need to satisfy peer reviewers."""

        answer = await self.think(answer_prompt, context=context)

        # Make decision about answer quality
        decision = await self.make_decision(
            "Is this answer complete, accurate, and satisfactory?",
            input_data={"question": question, "answer": answer, "context": context},
        )

        return {
            "question": question,
            "answer": answer,
            "confidence": decision.confidence,
            "sources_cited": self._extract_sources(answer),
            "decision": decision.model_dump(),
            "follow_up_suggestions": self._generate_follow_ups(question, answer),
        }

    def update_context(self, meta_analysis_data: Dict[str, Any]):
        """Update the context with meta-analysis data.

        Args:
            meta_analysis_data: Complete meta-analysis data including audit trail
        """
        self.meta_analysis_context.update(meta_analysis_data)
        logger.info("Updated Q&A agent context")

    def _extract_sources(self, answer: str) -> List[str]:
        """Extract cited sources from answer.

        Args:
            answer: Answer text

        Returns:
            List of sources mentioned
        """
        # Simple extraction (in production, use NLP)
        sources = []
        keywords = ["study", "paper", "article", "PMID", "DOI", "database"]

        for keyword in keywords:
            if keyword in answer.lower():
                # This is a simplified version
                # In production, properly parse citations
                pass

        return sources

    def _generate_follow_ups(self, question: str, answer: str) -> List[str]:
        """Generate suggested follow-up questions.

        Args:
            question: Original question
            answer: Generated answer

        Returns:
            List of follow-up questions
        """
        # Common follow-ups based on question type
        follow_ups = [
            "Can you show me the audit trail for this decision?",
            "What was the confidence level for this finding?",
            "How does this compare to similar meta-analyses?",
            "What are the limitations of this analysis?",
            "Which studies contributed most to this result?",
        ]

        return follow_ups[:3]  # Return top 3
