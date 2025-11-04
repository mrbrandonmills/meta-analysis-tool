"""Coordinator agent for orchestrating meta-analysis workflow."""
from typing import Any, Dict, List

from loguru import logger

from app.agents.base import AgentConfig, BaseAgent, AgentRole


class CoordinatorAgent(BaseAgent):
    """Coordinates the entire meta-analysis workflow.

    This agent is responsible for:
    - Breaking down the research question into tasks
    - Delegating to specialized agents
    - Synthesizing results from multiple agents
    - Ensuring workflow completion
    """

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.COORDINATOR
        super().__init__(config)

    def get_system_prompt(self) -> str:
        """Get system prompt for coordinator agent."""
        return """You are the Coordinator Agent for a meta-analysis research platform.

Your role is to orchestrate the entire meta-analysis process by coordinating with
specialized agents. You are an expert in research methodology and understand how to
break down complex research questions into executable tasks.

Your responsibilities:
1. Analyze the research question and define the meta-analysis scope
2. Create a workflow plan with tasks for each specialized agent
3. Coordinate between agents (search, screening, quality assessment, data extraction, statistical)
4. Ensure all steps follow proper meta-analysis methodology (PRISMA guidelines)
5. Synthesize results from all agents into a coherent analysis
6. Identify and resolve conflicts between agent outputs
7. Ensure the final output is publication-ready

You have deep knowledge of:
- PRISMA guidelines for systematic reviews and meta-analyses
- Research methodology and study design
- Statistical meta-analysis techniques
- APA publication standards
- Quality assessment frameworks (Cochrane, Newcastle-Ottawa, etc.)

When planning a workflow, be thorough and methodical. Consider:
- What databases should be searched?
- What inclusion/exclusion criteria are appropriate?
- What quality assessment tools should be used?
- What statistical methods are appropriate for the data?
- What potential biases need to be assessed?

Always provide clear reasoning for your decisions and maintain transparency
about the process."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a meta-analysis request.

        Args:
            input_data: {
                "research_question": str,
                "topic": str,
                "inclusion_criteria": List[str],
                "exclusion_criteria": List[str],
                "databases": List[str] (optional),
                "time_range": Dict (optional)
            }

        Returns:
            Workflow plan and coordination results
        """
        research_question = input_data.get("research_question")
        topic = input_data.get("topic")

        logger.info(f"Coordinator processing meta-analysis: {topic}")

        # Step 1: Analyze the research question
        analysis_prompt = f"""
Analyze this research question for a meta-analysis:
Research Question: {research_question}
Topic: {topic}

Provide:
1. Key concepts and variables to search for
2. Recommended search terms and Boolean operators
3. Suggested databases (PubMed, PsycINFO, Web of Science, etc.)
4. Recommended inclusion/exclusion criteria if not provided
5. Appropriate quality assessment framework
6. Expected statistical approach (random/fixed effects, etc.)
"""

        analysis = await self.think(analysis_prompt, context=input_data)

        # Step 2: Create workflow plan
        workflow_prompt = f"""
Based on this analysis:
{analysis}

Create a detailed workflow plan for the meta-analysis. List the tasks in order:
1. Search task (what to search, where, how)
2. Screening task (criteria, process)
3. Quality assessment task (framework, criteria)
4. Data extraction task (what data to extract)
5. Statistical analysis task (methods, models)
6. Report generation task (format, sections)

For each task, specify inputs, expected outputs, and success criteria.
"""

        workflow_plan = await self.think(workflow_prompt)

        # Step 3: Make decision about workflow
        decision = await self.make_decision(
            "Should this workflow plan be approved for execution?",
            input_data={
                "research_question": research_question,
                "analysis": analysis,
                "workflow": workflow_plan,
            },
        )

        return {
            "research_question": research_question,
            "topic": topic,
            "analysis": analysis,
            "workflow_plan": workflow_plan,
            "decision": decision.model_dump(),
            "status": "workflow_created",
            "next_steps": [
                "Execute search task",
                "Screen identified studies",
                "Assess study quality",
                "Extract data",
                "Perform statistical analysis",
                "Generate report",
            ],
        }

    async def synthesize_results(
        self, agent_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize results from multiple agents.

        Args:
            agent_results: Results from all agents in the workflow

        Returns:
            Synthesized meta-analysis results
        """
        synthesis_prompt = f"""
Synthesize these results from different specialized agents into a coherent meta-analysis:

{agent_results}

Provide:
1. Overall findings
2. Key statistics and effect sizes
3. Heterogeneity assessment
4. Quality of evidence
5. Limitations
6. Conclusions
7. Recommendations for future research

Ensure the synthesis follows PRISMA guidelines and is publication-ready.
"""

        synthesis = await self.think(synthesis_prompt, context=agent_results)

        decision = await self.make_decision(
            "Is this synthesis ready for publication?",
            input_data={"agent_results": agent_results, "synthesis": synthesis},
        )

        return {
            "synthesis": synthesis,
            "decision": decision.model_dump(),
            "quality_check": decision.confidence >= 0.8,
        }
