"""Enhanced Search Agent V2 with advanced query building and multi-database support."""
import asyncio
import hashlib
import re
import time
from collections import defaultdict
from functools import wraps
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx
from loguru import logger

from app.agents.base import AgentConfig, BaseAgent, AgentRole
from app.core.config import get_settings

settings = get_settings()


def rate_limit(calls_per_second: float):
    """Rate limiting decorator for API calls."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            result = await func(*args, **kwargs)
            last_called[0] = time.time()
            return result

        return wrapper

    return decorator


async def retry_with_backoff(
    func,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (httpx.HTTPError, httpx.TimeoutException),
):
    """Retry a function with exponential backoff."""
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(f"All {max_retries + 1} attempts failed")

    raise last_exception


class QueryBuilder:
    """Advanced query builder with Boolean operators and field-specific searches."""

    @staticmethod
    def build_pubmed_query(
        terms: List[str],
        boolean_op: str = "AND",
        mesh_terms: Optional[List[str]] = None,
        date_range: Optional[Dict[str, str]] = None,
        publication_types: Optional[List[str]] = None,
    ) -> str:
        """Build advanced PubMed query with MeSH terms and filters.

        Args:
            terms: Search terms
            boolean_op: Boolean operator (AND, OR, NOT)
            mesh_terms: MeSH (Medical Subject Headings) terms
            date_range: Date range filter {"mindate": "YYYY/MM/DD", "maxdate": "YYYY/MM/DD"}
            publication_types: Publication type filters (e.g., ["Clinical Trial", "RCT"])

        Returns:
            Formatted PubMed query string
        """
        query_parts = []

        # Add main search terms
        if terms:
            term_query = f" {boolean_op} ".join([f'"{term}"[Title/Abstract]' for term in terms])
            query_parts.append(f"({term_query})")

        # Add MeSH terms
        if mesh_terms:
            mesh_query = " OR ".join([f'"{mesh}"[MeSH Terms]' for mesh in mesh_terms])
            query_parts.append(f"({mesh_query})")

        # Add publication type filters
        if publication_types:
            pub_type_query = " OR ".join([f'"{pt}"[Publication Type]' for pt in publication_types])
            query_parts.append(f"({pub_type_query})")

        final_query = " AND ".join(query_parts) if query_parts else ""
        return final_query

    @staticmethod
    def build_arxiv_query(
        terms: List[str],
        categories: Optional[List[str]] = None,
        date_range: Optional[Dict[str, str]] = None,
    ) -> str:
        """Build arXiv query with category filters.

        Args:
            terms: Search terms
            categories: arXiv categories (e.g., ["cs.AI", "q-bio.QM"])
            date_range: Date range filter

        Returns:
            Formatted arXiv query string
        """
        query_parts = []

        # Main search
        if terms:
            query_parts.append(" AND ".join(terms))

        # Category filters
        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            query_parts.append(f"({cat_query})")

        return " AND ".join(query_parts) if query_parts else ""

    @staticmethod
    def expand_with_synonyms(term: str) -> List[str]:
        """Expand search term with common synonyms (simplified version).

        In production, this would use a medical ontology API like UMLS or BioPortal.

        Args:
            term: Original search term

        Returns:
            List of terms including synonyms
        """
        # Common medical synonym mappings (simplified)
        synonym_map = {
            "diabetes": ["diabetes mellitus", "diabetic", "DM"],
            "cancer": ["neoplasm", "tumor", "malignancy", "carcinoma"],
            "hypertension": ["high blood pressure", "HTN", "elevated blood pressure"],
            "depression": ["depressive disorder", "major depressive disorder", "MDD"],
            "covid": ["covid-19", "sars-cov-2", "coronavirus"],
            "alzheimer": ["alzheimer's disease", "AD", "dementia"],
            "obesity": ["overweight", "adiposity", "BMI"],
        }

        term_lower = term.lower()
        synonyms = [term]

        for key, syn_list in synonym_map.items():
            if key in term_lower:
                synonyms.extend(syn_list)
                break

        return list(set(synonyms))


class SearchAgentV2(BaseAgent):
    """Enhanced Search Agent with advanced query building and multi-database support.

    New Features:
    - Advanced Boolean query construction
    - MeSH term expansion
    - Synonym detection
    - Field-specific searches (title, abstract, keywords)
    - Enhanced deduplication (DOI, PMID, title similarity)
    - Result caching
    - Pagination support
    - Rate limiting and retry logic
    """

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.SEARCH
        super().__init__(config)
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        self._cache_ttl: Dict[str, float] = {}
        self._cache_duration = 3600  # 1 hour
        self.query_builder = QueryBuilder()

    def get_system_prompt(self) -> str:
        """Get system prompt for search agent."""
        return """You are the Advanced Search Agent for a meta-analysis research platform.

You are an expert in academic database searching, information retrieval, and systematic review methodology. You specialize in:
- Constructing effective Boolean search queries with AND, OR, NOT operators
- Identifying and using MeSH (Medical Subject Headings) terms
- Expanding search terms with synonyms and related concepts
- Field-specific searches (title, abstract, keywords, full-text)
- Database-specific query syntax optimization
- PRISMA guidelines for systematic review search methodology

Your responsibilities:
1. Analyze research questions to identify key concepts and search terms
2. Develop comprehensive, reproducible search strategies
3. Use MeSH terms and controlled vocabularies appropriately
4. Apply Boolean logic to combine search concepts
5. Search multiple databases with database-specific optimizations
6. Deduplicate results across databases
7. Document complete search methodology for reproducibility

Available Databases:
- PubMed/MEDLINE: Medical and life sciences (uses MeSH terms)
- arXiv: Preprints in physics, math, CS, quantitative biology
- Europe PMC: European biomedical literature
- CORE: Open access papers from global repositories

Advanced Features:
- Boolean operators: AND (narrow), OR (broaden), NOT (exclude)
- Field tags: [Title/Abstract], [MeSH Terms], [Author], [Journal]
- Proximity operators: NEAR, ADJ (when supported)
- Truncation: * for word variations (e.g., diabet* finds diabetes, diabetic)
- Phrase searching: "exact phrase" in quotes
- Date range filtering
- Publication type filtering (RCT, Meta-Analysis, etc.)

Always provide:
1. Complete search strategy with all terms and operators
2. Database-specific query adaptations
3. Number of results from each database
4. Deduplication statistics
5. Date and time of search
6. Any limitations or potential gaps

Follow PRISMA-S (PRISMA Search) extension guidelines for reporting."""

    def _get_cache_key(self, database: str, query: str, filters: Optional[Dict] = None) -> str:
        """Generate cache key from search parameters."""
        cache_str = f"{database}:{query}:{filters or {}}"
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _get_cached_results(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached results if still valid."""
        if cache_key in self._cache:
            if time.time() - self._cache_ttl[cache_key] < self._cache_duration:
                logger.info(f"Using cached results for {cache_key[:8]}...")
                return self._cache[cache_key]
            else:
                del self._cache[cache_key]
                del self._cache_ttl[cache_key]
        return None

    def _set_cached_results(self, cache_key: str, results: List[Dict[str, Any]]):
        """Cache search results."""
        self._cache[cache_key] = results
        self._cache_ttl[cache_key] = time.time()
        logger.debug(f"Cached {len(results)} results for key {cache_key[:8]}...")

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for studies with advanced query building.

        Args:
            input_data: {
                "research_question": str,
                "search_terms": List[str],
                "databases": List[str] (default: ["pubmed"]),
                "boolean_operator": str (default: "AND"),
                "expand_synonyms": bool (default: True),
                "mesh_terms": List[str] (optional),
                "date_range": Dict (optional),
                "publication_types": List[str] (optional),
                "max_results_per_db": int (default: 100),
            }

        Returns:
            Search results with enhanced metadata and strategy documentation
        """
        research_question = input_data.get("research_question", "")
        search_terms = input_data.get("search_terms", [])
        databases = input_data.get("databases", ["pubmed"])
        boolean_op = input_data.get("boolean_operator", "AND")
        expand_synonyms = input_data.get("expand_synonyms", True)
        mesh_terms = input_data.get("mesh_terms")
        date_range = input_data.get("date_range")
        publication_types = input_data.get("publication_types")
        max_results = input_data.get("max_results_per_db", 100)

        logger.info(f"SearchAgentV2 searching for: {research_question}")

        # Step 1: Use AI to develop comprehensive search strategy
        strategy_prompt = f"""
Develop a comprehensive search strategy for this systematic review research question:

Research Question: {research_question}
Initial Search Terms: {search_terms}

Provide:
1. Core concepts to search (PICO elements if applicable)
2. Additional relevant search terms and synonyms for each concept
3. Appropriate MeSH terms for PubMed (if medical/health topic)
4. Boolean query structure recommendation (which concepts to AND/OR)
5. Recommended filters:
   - Date range (if relevant)
   - Publication types (RCT, systematic review, etc.)
   - Language restrictions
6. Database-specific adaptations needed
7. Potential limitations or gaps in the search strategy

Format your response as:
CORE CONCEPTS: [list]
SEARCH TERMS: [organized by concept]
MESH TERMS: [list with explanations]
BOOLEAN STRUCTURE: [query structure]
FILTERS: [recommended filters]
LIMITATIONS: [any known limitations]
"""

        search_strategy = await self.think(strategy_prompt, context=input_data)

        # Step 2: Extract MeSH terms from AI response if not provided
        if not mesh_terms and "pubmed" in [db.lower() for db in databases]:
            mesh_terms = self._extract_mesh_terms_from_strategy(search_strategy)

        # Step 3: Expand terms with synonyms if requested
        expanded_terms = []
        if expand_synonyms:
            for term in search_terms:
                expanded_terms.extend(self.query_builder.expand_with_synonyms(term))
            expanded_terms = list(set(expanded_terms))
            logger.info(f"Expanded {len(search_terms)} terms to {len(expanded_terms)} with synonyms")
        else:
            expanded_terms = search_terms

        # Step 4: Execute searches across databases
        all_results = []
        search_log = []

        for database in databases:
            db_lower = database.lower()
            logger.info(f"Searching {database}...")

            try:
                if db_lower == "pubmed":
                    results = await self._search_pubmed_advanced(
                        terms=expanded_terms,
                        boolean_op=boolean_op,
                        mesh_terms=mesh_terms,
                        date_range=date_range,
                        publication_types=publication_types,
                        max_results=max_results,
                    )
                    query = self.query_builder.build_pubmed_query(
                        expanded_terms, boolean_op, mesh_terms, date_range, publication_types
                    )

                elif db_lower == "arxiv":
                    results = await self._search_arxiv_advanced(
                        terms=expanded_terms,
                        date_range=date_range,
                        max_results=max_results,
                    )
                    query = self.query_builder.build_arxiv_query(expanded_terms, date_range=date_range)

                elif db_lower == "europepmc":
                    results = await self._search_europepmc_advanced(
                        terms=expanded_terms,
                        boolean_op=boolean_op,
                        date_range=date_range,
                        max_results=max_results,
                    )
                    query = f" {boolean_op} ".join([f'"{t}"' for t in expanded_terms])

                elif db_lower == "core":
                    results = await self._search_core_advanced(
                        terms=expanded_terms,
                        max_results=max_results,
                    )
                    query = " ".join(expanded_terms)

                else:
                    logger.warning(f"Unknown database: {database}")
                    continue

                all_results.extend(results)
                search_log.append({
                    "database": database,
                    "query": query,
                    "results_count": len(results),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                })

            except Exception as e:
                logger.error(f"Error searching {database}: {e}")
                search_log.append({
                    "database": database,
                    "query": "Error occurred",
                    "results_count": 0,
                    "error": str(e),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                })

        # Step 5: Advanced deduplication
        unique_results, dedup_stats = self._deduplicate_advanced(all_results)

        # Step 6: AI decision on search completeness
        decision = await self.make_decision(
            "Is this search comprehensive and reproducible enough for a systematic review?",
            input_data={
                "research_question": research_question,
                "total_results": len(all_results),
                "unique_results": len(unique_results),
                "databases_searched": databases,
                "search_strategy": search_strategy,
                "deduplication_rate": (len(all_results) - len(unique_results)) / len(all_results)
                if all_results
                else 0,
            },
        )

        return {
            "search_strategy": search_strategy,
            "original_terms": search_terms,
            "expanded_terms": expanded_terms,
            "mesh_terms": mesh_terms or [],
            "boolean_operator": boolean_op,
            "databases_searched": databases,
            "search_log": search_log,
            "total_results": len(all_results),
            "unique_results": len(unique_results),
            "duplicates_removed": len(all_results) - len(unique_results),
            "deduplication_stats": dedup_stats,
            "studies": unique_results,
            "decision": decision.model_dump(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _extract_mesh_terms_from_strategy(self, strategy_text: str) -> List[str]:
        """Extract MeSH terms from AI-generated strategy."""
        mesh_terms = []
        lines = strategy_text.split("\n")
        in_mesh_section = False

        for line in lines:
            if "MESH TERMS:" in line.upper():
                in_mesh_section = True
                continue
            if in_mesh_section:
                if line.strip().startswith("-") or line.strip().startswith("*"):
                    # Extract term (remove markdown, bullets, explanations)
                    term = line.strip().lstrip("-*").split("(")[0].split(":")[0].strip()
                    if term:
                        mesh_terms.append(term)
                elif line.strip() and line.strip().isupper():
                    # Hit next section
                    break

        logger.info(f"Extracted {len(mesh_terms)} MeSH terms from strategy")
        return mesh_terms

    @rate_limit(calls_per_second=3.0)
    async def _search_pubmed_advanced(
        self,
        terms: List[str],
        boolean_op: str = "AND",
        mesh_terms: Optional[List[str]] = None,
        date_range: Optional[Dict[str, str]] = None,
        publication_types: Optional[List[str]] = None,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """Advanced PubMed search with MeSH terms and filters."""
        query = self.query_builder.build_pubmed_query(
            terms, boolean_op, mesh_terms, date_range, publication_types
        )

        cache_key = self._get_cache_key("pubmed", query, {"date_range": date_range})
        cached = self._get_cached_results(cache_key)
        if cached is not None:
            return cached

        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

        async def fetch_pubmed_data():
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Search for IDs
                search_params = {
                    "db": "pubmed",
                    "term": query,
                    "retmax": max_results,
                    "retmode": "json",
                    "email": settings.pubmed_email or "research@example.com",
                    "tool": "meta-analysis-platform-v2",
                }

                if date_range:
                    search_params["mindate"] = date_range.get("mindate", "")
                    search_params["maxdate"] = date_range.get("maxdate", "")

                search_response = await client.get(f"{base_url}esearch.fcgi", params=search_params)

                if search_response.status_code != 200:
                    logger.error(f"PubMed search failed: {search_response.status_code}")
                    return []

                search_data = search_response.json()
                ids = search_data.get("esearchresult", {}).get("idlist", [])

                if not ids:
                    logger.info("No results found in PubMed")
                    return []

                logger.info(f"Found {len(ids)} results in PubMed")

                # Fetch full records with abstracts
                fetch_response = await client.get(
                    f"{base_url}efetch.fcgi",
                    params={
                        "db": "pubmed",
                        "id": ",".join(ids),
                        "retmode": "xml",
                        "rettype": "abstract",
                    },
                )

                if fetch_response.status_code != 200:
                    logger.error(f"PubMed efetch failed: {fetch_response.status_code}")
                    return []

                return self._parse_pubmed_xml(fetch_response.content)

        try:
            results = await retry_with_backoff(fetch_pubmed_data)
            self._set_cached_results(cache_key, results)
            return results
        except Exception as e:
            logger.error(f"Error searching PubMed after retries: {e}")
            return []

    def _parse_pubmed_xml(self, xml_content: bytes) -> List[Dict[str, Any]]:
        """Parse PubMed XML response."""
        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(xml_content)
            results = []

            for article in root.findall(".//PubmedArticle"):
                try:
                    pmid = article.find(".//PMID")
                    pmid = pmid.text if pmid is not None else ""

                    title = article.find(".//ArticleTitle")
                    title = title.text if title is not None else ""

                    # Extract abstract
                    abstract_texts = []
                    for abstract_text in article.findall(".//AbstractText"):
                        if abstract_text.text:
                            label = abstract_text.get("Label", "")
                            text = abstract_text.text
                            if label:
                                abstract_texts.append(f"{label}: {text}")
                            else:
                                abstract_texts.append(text)
                    abstract = " ".join(abstract_texts)

                    # Extract authors
                    authors = []
                    for author in article.findall(".//Author"):
                        last_name = author.find("LastName")
                        fore_name = author.find("ForeName")
                        if last_name is not None and fore_name is not None:
                            authors.append(f"{last_name.text} {fore_name.text}")

                    journal = article.find(".//Journal/Title")
                    journal = journal.text if journal is not None else ""

                    year = article.find(".//PubDate/Year")
                    year = year.text if year is not None else ""

                    # Extract DOI
                    doi = ""
                    for article_id in article.findall(".//ArticleId"):
                        if article_id.get("IdType") == "doi":
                            doi = article_id.text
                            break

                    # Extract keywords
                    keywords = [kw.text for kw in article.findall(".//Keyword") if kw.text]

                    # Extract MeSH terms
                    mesh_terms = [
                        mesh.text for mesh in article.findall(".//MeshHeading/DescriptorName") if mesh.text
                    ]

                    # Extract publication types
                    pub_types = [pt.text for pt in article.findall(".//PublicationType") if pt.text]

                    results.append({
                        "id": f"PMID:{pmid}",
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "authors": authors,
                        "journal": journal,
                        "year": year,
                        "doi": doi,
                        "keywords": keywords,
                        "mesh_terms": mesh_terms,
                        "publication_types": pub_types,
                        "database": "PubMed",
                    })
                except Exception as e:
                    logger.warning(f"Error parsing PubMed article: {e}")
                    continue

            logger.info(f"Parsed {len(results)} complete PubMed records")
            return results

        except Exception as e:
            logger.error(f"Error parsing PubMed XML: {e}")
            return []

    @rate_limit(calls_per_second=10.0)
    async def _search_arxiv_advanced(
        self,
        terms: List[str],
        date_range: Optional[Dict[str, str]] = None,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """Advanced arXiv search."""
        query = self.query_builder.build_arxiv_query(terms, date_range=date_range)

        cache_key = self._get_cache_key("arxiv", query)
        cached = self._get_cached_results(cache_key)
        if cached is not None:
            return cached

        base_url = "https://export.arxiv.org/api/query"

        async def fetch_arxiv_data():
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(
                    base_url,
                    params={
                        "search_query": f"all:{query}",
                        "start": 0,
                        "max_results": max_results,
                    },
                )

                if response.status_code != 200:
                    logger.error(f"arXiv search failed: {response.status_code}")
                    return []

                import xml.etree.ElementTree as ET

                root = ET.fromstring(response.content)
                ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

                results = []
                entries = root.findall("atom:entry", ns)

                logger.info(f"Found {len(entries)} results in arXiv")

                for entry in entries:
                    title = entry.find("atom:title", ns)
                    summary = entry.find("atom:summary", ns)
                    published = entry.find("atom:published", ns)
                    id_elem = entry.find("atom:id", ns)

                    authors = []
                    for author in entry.findall("atom:author", ns):
                        name = author.find("atom:name", ns)
                        if name is not None:
                            authors.append(name.text)

                    arxiv_id = id_elem.text.split("/")[-1] if id_elem is not None else ""

                    categories = [cat.get("term") for cat in entry.findall("atom:category", ns) if cat.get("term")]

                    results.append({
                        "id": f"arXiv:{arxiv_id}",
                        "arxiv_id": arxiv_id,
                        "title": title.text.strip() if title is not None else "",
                        "authors": authors,
                        "journal": "arXiv Preprint",
                        "year": published.text[:4] if published is not None else "",
                        "abstract": summary.text.strip() if summary is not None else "",
                        "doi": "",
                        "database": "arXiv",
                        "url": id_elem.text if id_elem is not None else "",
                        "categories": categories,
                        "is_preprint": True,
                    })

                return results

        try:
            results = await retry_with_backoff(fetch_arxiv_data)
            self._set_cached_results(cache_key, results)
            return results
        except Exception as e:
            logger.error(f"Error searching arXiv after retries: {e}")
            return []

    @rate_limit(calls_per_second=10.0)
    async def _search_europepmc_advanced(
        self,
        terms: List[str],
        boolean_op: str = "AND",
        date_range: Optional[Dict[str, str]] = None,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """Advanced Europe PMC search."""
        query = f" {boolean_op} ".join([f'"{term}"' for term in terms])

        cache_key = self._get_cache_key("europepmc", query)
        cached = self._get_cached_results(cache_key)
        if cached is not None:
            return cached

        base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

        async def fetch_europepmc_data():
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    base_url,
                    params={
                        "query": query,
                        "pageSize": max_results,
                        "format": "json",
                    },
                )

                if response.status_code != 200:
                    logger.error(f"Europe PMC search failed: {response.status_code}")
                    return []

                data = response.json()
                result_list = data.get("resultList", {}).get("result", [])

                logger.info(f"Found {len(result_list)} results in Europe PMC")

                results = []
                for study in result_list:
                    authors = []
                    if "authorString" in study:
                        authors = [a.strip() for a in study["authorString"].split(",")]

                    results.append({
                        "id": f"PMCID:{study.get('pmcid', study.get('id', ''))}",
                        "pmc_id": study.get("pmcid", ""),
                        "pmid": study.get("pmid", ""),
                        "title": study.get("title", ""),
                        "authors": authors,
                        "journal": study.get("journalTitle", ""),
                        "year": str(study.get("pubYear", "")),
                        "abstract": study.get("abstractText", ""),
                        "doi": study.get("doi", ""),
                        "database": "Europe PMC",
                        "source": study.get("source", ""),
                        "is_open_access": study.get("isOpenAccess", "N") == "Y",
                    })

                return results

        try:
            results = await retry_with_backoff(fetch_europepmc_data)
            self._set_cached_results(cache_key, results)
            return results
        except Exception as e:
            logger.error(f"Error searching Europe PMC after retries: {e}")
            return []

    @rate_limit(calls_per_second=10.0)
    async def _search_core_advanced(
        self,
        terms: List[str],
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """Advanced CORE search."""
        query = " ".join(terms)

        cache_key = self._get_cache_key("core", query)
        cached = self._get_cached_results(cache_key)
        if cached is not None:
            return cached

        base_url = "https://api.core.ac.uk/v3/search/works"

        async def fetch_core_data():
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    base_url,
                    json={
                        "q": query,
                        "limit": max_results,
                    },
                )

                if response.status_code != 200:
                    logger.error(f"CORE search failed: {response.status_code}")
                    return []

                data = response.json()
                results_list = data.get("results", [])

                logger.info(f"Found {len(results_list)} results in CORE")

                results = []
                for study in results_list:
                    authors = []
                    if "authors" in study:
                        authors = [a.get("name", "") for a in study["authors"] if "name" in a]

                    results.append({
                        "id": f"CORE:{study.get('id', '')}",
                        "title": study.get("title", ""),
                        "authors": authors,
                        "journal": study.get("publisher", ""),
                        "year": str(study.get("yearPublished", "")),
                        "abstract": study.get("abstract", ""),
                        "doi": study.get("doi", ""),
                        "database": "CORE",
                        "downloadUrl": study.get("downloadUrl", ""),
                        "is_open_access": True,  # CORE only indexes OA
                    })

                return results

        try:
            results = await retry_with_backoff(fetch_core_data)
            self._set_cached_results(cache_key, results)
            return results
        except Exception as e:
            logger.error(f"Error searching CORE after retries: {e}")
            return []

    def _deduplicate_advanced(
        self, studies: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """Advanced deduplication using multiple identifiers and fuzzy title matching.

        Strategy:
        1. DOI matching (exact)
        2. PMID matching (exact)
        3. Title similarity (normalized, case-insensitive)
        4. Author + year matching (fallback)

        Returns:
            Tuple of (unique_studies, deduplication_stats)
        """
        seen_dois: Set[str] = set()
        seen_pmids: Set[str] = set()
        seen_titles: Set[str] = set()
        unique = []

        duplicates_by_doi = 0
        duplicates_by_pmid = 0
        duplicates_by_title = 0

        for study in studies:
            # Normalize identifiers
            doi = study.get("doi", "").strip().lower()
            pmid = study.get("pmid", "").strip()
            title = self._normalize_title(study.get("title", ""))

            is_duplicate = False

            # Check DOI first (most reliable)
            if doi and doi in seen_dois:
                duplicates_by_doi += 1
                is_duplicate = True
            elif doi:
                seen_dois.add(doi)

            # Check PMID
            if not is_duplicate and pmid and pmid in seen_pmids:
                duplicates_by_pmid += 1
                is_duplicate = True
            elif pmid:
                seen_pmids.add(pmid)

            # Check normalized title
            if not is_duplicate and title:
                # Check for exact match
                if title in seen_titles:
                    duplicates_by_title += 1
                    is_duplicate = True
                else:
                    # Check for highly similar titles (fuzzy matching)
                    for seen_title in seen_titles:
                        if self._titles_are_similar(title, seen_title):
                            duplicates_by_title += 1
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        seen_titles.add(title)

            if not is_duplicate:
                unique.append(study)

        dedup_stats = {
            "total_input": len(studies),
            "duplicates_removed": len(studies) - len(unique),
            "duplicates_by_doi": duplicates_by_doi,
            "duplicates_by_pmid": duplicates_by_pmid,
            "duplicates_by_title": duplicates_by_title,
            "unique_dois": len(seen_dois),
            "unique_pmids": len(seen_pmids),
            "unique_titles": len(seen_titles),
        }

        logger.info(
            f"Advanced deduplication: {len(studies)} -> {len(unique)} studies "
            f"(DOI: {duplicates_by_doi}, PMID: {duplicates_by_pmid}, Title: {duplicates_by_title})"
        )

        return unique, dedup_stats

    @staticmethod
    def _normalize_title(title: str) -> str:
        """Normalize title for comparison."""
        # Convert to lowercase
        title = title.lower().strip()
        # Remove punctuation
        title = re.sub(r'[^\w\s]', '', title)
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title)
        return title

    @staticmethod
    def _titles_are_similar(title1: str, title2: str, threshold: float = 0.9) -> bool:
        """Check if two titles are similar using simple similarity metric."""
        if not title1 or not title2:
            return False

        # Simple Jaccard similarity on words
        words1 = set(title1.split())
        words2 = set(title2.split())

        if not words1 or not words2:
            return False

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        similarity = intersection / union if union > 0 else 0

        return similarity >= threshold
