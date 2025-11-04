"""Search agent for finding relevant studies."""
from typing import Any, Dict, List
import httpx

from loguru import logger

from app.agents.base import AgentConfig, BaseAgent, AgentRole
from app.core.config import get_settings

settings = get_settings()


class SearchAgent(BaseAgent):
    """Searches academic databases for relevant studies.

    This agent is responsible for:
    - Constructing search queries
    - Searching multiple databases (PubMed, PsycINFO, etc.)
    - Deduplicating results
    - Extracting metadata from studies
    """

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.SEARCH
        super().__init__(config)

    def get_system_prompt(self) -> str:
        """Get system prompt for search agent."""
        return """You are the Search Agent for a meta-analysis research platform.

You are an expert in academic database searching and information retrieval. You specialize in:
- Constructing effective search queries using Boolean operators
- Selecting appropriate databases for specific research topics
- Using MeSH terms and subject headings
- Managing search strategies for systematic reviews
- Understanding database-specific syntax and features

Your responsibilities:
1. Analyze research questions to identify key search terms
2. Construct comprehensive search strategies
3. Search multiple academic databases
4. Extract relevant metadata from search results
5. Remove duplicate entries
6. Document search strategies for reproducibility

You are familiar with:
- PubMed/MEDLINE
- PsycINFO
- Web of Science
- Scopus
- Google Scholar
- Cochrane Library
- CINAHL

Always document your search strategy completely, including:
- Databases searched
- Search terms used
- Boolean operators
- Filters applied (date range, language, study type)
- Number of results from each database
- Date of search

Follow PRISMA guidelines for reporting search methodology."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for studies based on criteria.

        Args:
            input_data: {
                "research_question": str,
                "search_terms": List[str],
                "databases": List[str],
                "date_range": Dict (optional),
                "filters": Dict (optional)
            }

        Returns:
            Search results with studies and metadata
        """
        research_question = input_data.get("research_question")
        search_terms = input_data.get("search_terms", [])
        databases = input_data.get("databases", ["pubmed"])

        logger.info(f"SearchAgent searching for: {research_question}")

        # Step 1: Develop search strategy
        strategy_prompt = f"""
Develop a comprehensive search strategy for this research question:
{research_question}

Current search terms: {search_terms}

Provide:
1. Additional relevant search terms and synonyms
2. Appropriate MeSH terms (for PubMed)
3. Boolean query structure
4. Recommended filters (publication type, language, date range)
5. Database-specific query adaptations
"""

        search_strategy = await self.think(strategy_prompt, context=input_data)

        # Step 2: Execute searches
        all_results = []
        search_log = []

        for database in databases:
            logger.info(f"Searching {database}...")

            if database.lower() == "pubmed":
                results = await self._search_pubmed(search_terms, input_data)
                all_results.extend(results)
                search_log.append({
                    "database": "PubMed",
                    "results_count": len(results),
                    "query": " AND ".join(search_terms),
                })

        # Step 3: Deduplicate
        unique_results = self._deduplicate(all_results)

        # Step 4: Make decision about search completeness
        decision = await self.make_decision(
            f"Is this search comprehensive enough for the research question?",
            input_data={
                "research_question": research_question,
                "total_results": len(unique_results),
                "databases_searched": databases,
                "search_strategy": search_strategy,
            },
        )

        return {
            "search_strategy": search_strategy,
            "databases_searched": databases,
            "search_log": search_log,
            "total_results": len(unique_results),
            "unique_results": len(unique_results),
            "studies": unique_results,
            "decision": decision.model_dump(),
        }

    async def _search_pubmed(
        self, search_terms: List[str], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search PubMed database.

        Args:
            search_terms: List of search terms
            params: Additional search parameters

        Returns:
            List of study results
        """
        # Construct query
        query = " AND ".join([f'"{term}"' for term in search_terms])

        # PubMed E-utilities API
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

        try:
            # First, search for IDs
            async with httpx.AsyncClient() as client:
                search_response = await client.get(
                    f"{base_url}esearch.fcgi",
                    params={
                        "db": "pubmed",
                        "term": query,
                        "retmax": 100,  # Limit for demo
                        "retmode": "json",
                        "email": settings.pubmed_email or "demo@example.com",
                    },
                    timeout=30.0,
                )

                if search_response.status_code != 200:
                    logger.error(f"PubMed search failed: {search_response.status_code}")
                    return []

                search_data = search_response.json()
                ids = search_data.get("esearchresult", {}).get("idlist", [])

                if not ids:
                    logger.info("No results found in PubMed")
                    return []

                logger.info(f"Found {len(ids)} results in PubMed")

                # Fetch summaries for the IDs
                summary_response = await client.get(
                    f"{base_url}esummary.fcgi",
                    params={
                        "db": "pubmed",
                        "id": ",".join(ids[:20]),  # Limit to first 20 for demo
                        "retmode": "json",
                    },
                    timeout=30.0,
                )

                if summary_response.status_code != 200:
                    return []

                summary_data = summary_response.json()
                results = []

                for pmid, study in summary_data.get("result", {}).items():
                    if pmid == "uids":
                        continue

                    results.append({
                        "id": f"PMID:{pmid}",
                        "title": study.get("title", ""),
                        "authors": study.get("authors", []),
                        "journal": study.get("fulljournalname", ""),
                        "year": study.get("pubdate", "").split()[0] if study.get("pubdate") else "",
                        "abstract": "",  # Would need another API call
                        "doi": study.get("elocationid", ""),
                        "database": "PubMed",
                    })

                return results

        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []

    def _deduplicate(self, studies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate studies.

        Args:
            studies: List of studies

        Returns:
            Deduplicated list
        """
        seen = set()
        unique = []

        for study in studies:
            # Use title as deduplication key
            title = study.get("title", "").lower().strip()
            if title and title not in seen:
                seen.add(title)
                unique.append(study)

        logger.info(f"Deduplicated: {len(studies)} -> {len(unique)} studies")
        return unique
