"""Enhanced search agent with rate limiting, retry logic, and robust error handling."""
import asyncio
import time
from typing import Any, Dict, List
import httpx
from functools import wraps

from loguru import logger

from app.agents.base import AgentConfig, BaseAgent, AgentRole
from app.core.config import get_settings

settings = get_settings()


def rate_limit(calls_per_second: float):
    """Rate limiting decorator for API calls.

    Args:
        calls_per_second: Maximum number of calls per second
    """
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Calculate time to wait
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
    exceptions: tuple = (httpx.HTTPError, httpx.TimeoutException)
):
    """Retry a function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Result of the function call

    Raises:
        Last exception if all retries fail
    """
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


class SearchAgentEnhanced(BaseAgent):
    """Enhanced search agent with production-ready features.

    Improvements over base SearchAgent:
    - Rate limiting to respect API quotas (PubMed: 3 req/sec, others: 10 req/sec)
    - Retry logic with exponential backoff for transient failures
    - Response caching to avoid duplicate API calls
    - Better error handling and logging
    - Full abstract fetching for PubMed
    - Proper URL encoding for special characters
    """

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.SEARCH
        super().__init__(config)
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        self._cache_ttl: Dict[str, float] = {}
        self._cache_duration = 3600  # 1 hour

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

You are familiar with and have access to:
- PubMed/MEDLINE (medical & life sciences)
- arXiv (preprints: physics, math, CS, q-bio)
- Europe PMC (European research + life sciences)
- CORE (open access papers from global repositories)

Always document your search strategy completely, including:
- Databases searched
- Search terms used
- Boolean operators
- Filters applied (date range, language, study type)
- Number of results from each database
- Date of search

Follow PRISMA guidelines for reporting search methodology."""

    def _get_cache_key(self, database: str, search_terms: List[str]) -> str:
        """Generate cache key for search results."""
        return f"{database}:{':'.join(sorted(search_terms))}"

    def _get_cached_results(self, cache_key: str) -> List[Dict[str, Any]]:
        """Get cached results if still valid."""
        if cache_key in self._cache:
            if time.time() - self._cache_ttl[cache_key] < self._cache_duration:
                logger.info(f"Using cached results for {cache_key}")
                return self._cache[cache_key]
            else:
                # Expired cache
                del self._cache[cache_key]
                del self._cache_ttl[cache_key]
        return None

    def _set_cached_results(self, cache_key: str, results: List[Dict[str, Any]]):
        """Cache search results."""
        self._cache[cache_key] = results
        self._cache_ttl[cache_key] = time.time()

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
                results = await self._search_pubmed_enhanced(search_terms, input_data)
                all_results.extend(results)
                search_log.append({
                    "database": "PubMed",
                    "results_count": len(results),
                    "query": " AND ".join(search_terms),
                })
            elif database.lower() == "arxiv":
                results = await self._search_arxiv_enhanced(search_terms, input_data)
                all_results.extend(results)
                search_log.append({
                    "database": "arXiv",
                    "results_count": len(results),
                    "query": " AND ".join(search_terms),
                })
            elif database.lower() == "europepmc":
                results = await self._search_europepmc_enhanced(search_terms, input_data)
                all_results.extend(results)
                search_log.append({
                    "database": "Europe PMC",
                    "results_count": len(results),
                    "query": " AND ".join(search_terms),
                })
            elif database.lower() == "core":
                results = await self._search_core_enhanced(search_terms, input_data)
                all_results.extend(results)
                search_log.append({
                    "database": "CORE",
                    "results_count": len(results),
                    "query": " AND ".join(search_terms),
                })

        # Step 3: Deduplicate
        unique_results = self._deduplicate_enhanced(all_results)

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

    @rate_limit(calls_per_second=3.0)  # PubMed limit: 3 requests/second
    async def _search_pubmed_enhanced(
        self, search_terms: List[str], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search PubMed database with rate limiting and retry logic.

        Improvements:
        - Rate limiting (3 req/sec max)
        - Retry with exponential backoff
        - Fetch full abstracts using efetch
        - Better error handling
        - Response caching
        """
        cache_key = self._get_cache_key("pubmed", search_terms)
        cached = self._get_cached_results(cache_key)
        if cached is not None:
            return cached

        # Construct query
        query = " AND ".join([f'"{term}"' for term in search_terms])

        # PubMed E-utilities API
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

        async def fetch_pubmed_data():
            async with httpx.AsyncClient() as client:
                # Step 1: Search for IDs
                search_response = await client.get(
                    f"{base_url}esearch.fcgi",
                    params={
                        "db": "pubmed",
                        "term": query,
                        "retmax": params.get("max_results", 100),
                        "retmode": "json",
                        "email": settings.pubmed_email or "research@example.com",
                        "tool": "meta-analysis-platform",
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

                # Step 2: Fetch full details including abstracts
                # Use efetch for full records (XML format has more data)
                fetch_response = await client.get(
                    f"{base_url}efetch.fcgi",
                    params={
                        "db": "pubmed",
                        "id": ",".join(ids[:100]),  # Fetch up to 100 records
                        "retmode": "xml",
                        "rettype": "abstract",
                    },
                    timeout=60.0,
                )

                if fetch_response.status_code != 200:
                    logger.error(f"PubMed efetch failed: {fetch_response.status_code}")
                    # Fallback to esummary if efetch fails
                    return await self._fetch_pubmed_summaries(base_url, client, ids[:20])

                # Parse XML response
                return self._parse_pubmed_xml(fetch_response.content)

        try:
            results = await retry_with_backoff(fetch_pubmed_data)
            self._set_cached_results(cache_key, results)
            return results
        except Exception as e:
            logger.error(f"Error searching PubMed after retries: {e}")
            return []

    def _parse_pubmed_xml(self, xml_content: bytes) -> List[Dict[str, Any]]:
        """Parse PubMed XML response to extract full article data."""
        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(xml_content)
            results = []

            for article in root.findall('.//PubmedArticle'):
                try:
                    # Extract PMID
                    pmid_elem = article.find('.//PMID')
                    pmid = pmid_elem.text if pmid_elem is not None else ""

                    # Extract title
                    title_elem = article.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None else ""

                    # Extract abstract (concatenate all abstract text elements)
                    abstract_texts = []
                    for abstract_text in article.findall('.//AbstractText'):
                        if abstract_text.text:
                            label = abstract_text.get('Label', '')
                            text = abstract_text.text
                            if label:
                                abstract_texts.append(f"{label}: {text}")
                            else:
                                abstract_texts.append(text)
                    abstract = " ".join(abstract_texts)

                    # Extract authors
                    authors = []
                    for author in article.findall('.//Author'):
                        last_name = author.find('LastName')
                        fore_name = author.find('ForeName')
                        if last_name is not None and fore_name is not None:
                            authors.append(f"{last_name.text} {fore_name.text}")

                    # Extract journal
                    journal_elem = article.find('.//Journal/Title')
                    journal = journal_elem.text if journal_elem is not None else ""

                    # Extract publication year
                    year_elem = article.find('.//PubDate/Year')
                    year = year_elem.text if year_elem is not None else ""

                    # Extract DOI
                    doi = ""
                    for article_id in article.findall('.//ArticleId'):
                        if article_id.get('IdType') == 'doi':
                            doi = article_id.text
                            break

                    # Extract keywords
                    keywords = []
                    for keyword in article.findall('.//Keyword'):
                        if keyword.text:
                            keywords.append(keyword.text)

                    # Extract MeSH terms
                    mesh_terms = []
                    for mesh in article.findall('.//MeshHeading/DescriptorName'):
                        if mesh.text:
                            mesh_terms.append(mesh.text)

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

    async def _fetch_pubmed_summaries(
        self, base_url: str, client: httpx.AsyncClient, ids: List[str]
    ) -> List[Dict[str, Any]]:
        """Fallback method to fetch PubMed summaries (without full abstracts)."""
        try:
            summary_response = await client.get(
                f"{base_url}esummary.fcgi",
                params={
                    "db": "pubmed",
                    "id": ",".join(ids),
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
                    "pmid": pmid,
                    "title": study.get("title", ""),
                    "authors": [a.get("name", "") for a in study.get("authors", [])],
                    "journal": study.get("fulljournalname", ""),
                    "year": study.get("pubdate", "").split()[0] if study.get("pubdate") else "",
                    "abstract": "",  # Not available in summary
                    "doi": study.get("elocationid", ""),
                    "database": "PubMed",
                })

            return results

        except Exception as e:
            logger.error(f"Error fetching PubMed summaries: {e}")
            return []

    @rate_limit(calls_per_second=10.0)  # arXiv is more lenient
    async def _search_arxiv_enhanced(
        self, search_terms: List[str], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search arXiv preprint repository with enhancements."""
        cache_key = self._get_cache_key("arxiv", search_terms)
        cached = self._get_cached_results(cache_key)
        if cached is not None:
            return cached

        # Construct query for arXiv API
        query = " AND ".join(search_terms)

        # arXiv API (use HTTPS)
        base_url = "https://export.arxiv.org/api/query"

        async def fetch_arxiv_data():
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(
                    base_url,
                    params={
                        "search_query": f"all:{query}",
                        "start": 0,
                        "max_results": params.get("max_results", 50),
                    },
                    timeout=30.0,
                )

                if response.status_code != 200:
                    logger.error(f"arXiv search failed: {response.status_code}")
                    return []

                # Parse XML response
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)

                # Namespace for arXiv Atom feed
                ns = {
                    'atom': 'http://www.w3.org/2005/Atom',
                    'arxiv': 'http://arxiv.org/schemas/atom'
                }

                results = []
                entries = root.findall('atom:entry', ns)

                logger.info(f"Found {len(entries)} results in arXiv")

                for entry in entries:
                    title_elem = entry.find('atom:title', ns)
                    summary_elem = entry.find('atom:summary', ns)
                    published_elem = entry.find('atom:published', ns)
                    id_elem = entry.find('atom:id', ns)

                    # Extract authors
                    authors = []
                    for author in entry.findall('atom:author', ns):
                        name_elem = author.find('atom:name', ns)
                        if name_elem is not None:
                            authors.append(name_elem.text)

                    # Extract arXiv ID
                    arxiv_id = ""
                    if id_elem is not None:
                        arxiv_id = id_elem.text.split('/')[-1]

                    # Extract categories
                    categories = []
                    for category in entry.findall('atom:category', ns):
                        term = category.get('term')
                        if term:
                            categories.append(term)

                    results.append({
                        "id": f"arXiv:{arxiv_id}",
                        "arxiv_id": arxiv_id,
                        "title": title_elem.text.strip() if title_elem is not None else "",
                        "authors": authors,
                        "journal": "arXiv Preprint",
                        "year": published_elem.text[:4] if published_elem is not None else "",
                        "abstract": summary_elem.text.strip() if summary_elem is not None else "",
                        "doi": "",
                        "database": "arXiv",
                        "url": id_elem.text if id_elem is not None else "",
                        "categories": categories,
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
    async def _search_europepmc_enhanced(
        self, search_terms: List[str], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search Europe PMC database with enhancements."""
        cache_key = self._get_cache_key("europepmc", search_terms)
        cached = self._get_cached_results(cache_key)
        if cached is not None:
            return cached

        # Construct query
        query = " AND ".join([f'"{term}"' for term in search_terms])

        # Europe PMC API
        base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

        async def fetch_europepmc_data():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    base_url,
                    params={
                        "query": query,
                        "pageSize": params.get("max_results", 50),
                        "format": "json",
                    },
                    timeout=30.0,
                )

                if response.status_code != 200:
                    logger.error(f"Europe PMC search failed: {response.status_code}")
                    return []

                data = response.json()
                result_list = data.get("resultList", {}).get("result", [])

                logger.info(f"Found {len(result_list)} results in Europe PMC")

                results = []
                for study in result_list:
                    # Extract author list
                    authors = []
                    if "authorString" in study:
                        authors = [a.strip() for a in study["authorString"].split(",")]

                    results.append({
                        "id": f"PMCID:{study.get('pmcid', study.get('id', ''))}",
                        "pmc_id": study.get('pmcid', ''),
                        "pmid": study.get('pmid', ''),
                        "title": study.get("title", ""),
                        "authors": authors,
                        "journal": study.get("journalTitle", ""),
                        "year": str(study.get("pubYear", "")),
                        "abstract": study.get("abstractText", ""),
                        "doi": study.get("doi", ""),
                        "database": "Europe PMC",
                        "source": study.get("source", ""),
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
    async def _search_core_enhanced(
        self, search_terms: List[str], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search CORE (COnnecting REpositories) with enhancements."""
        cache_key = self._get_cache_key("core", search_terms)
        cached = self._get_cached_results(cache_key)
        if cached is not None:
            return cached

        # Construct query
        query = " ".join(search_terms)

        # CORE API v3
        base_url = "https://api.core.ac.uk/v3/search/works"

        async def fetch_core_data():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    base_url,
                    json={
                        "q": query,
                        "limit": params.get("max_results", 50),
                    },
                    timeout=30.0,
                )

                if response.status_code != 200:
                    logger.error(f"CORE search failed: {response.status_code}")
                    return []

                data = response.json()
                results_list = data.get("results", [])

                logger.info(f"Found {len(results_list)} results in CORE")

                results = []
                for study in results_list:
                    # Extract authors
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
                    })

                return results

        try:
            results = await retry_with_backoff(fetch_core_data)
            self._set_cached_results(cache_key, results)
            return results
        except Exception as e:
            logger.error(f"Error searching CORE after retries: {e}")
            return []

    def _deduplicate_enhanced(self, studies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhanced deduplication using DOI, PMID, and title similarity.

        Deduplication strategy:
        1. First pass: Remove exact DOI matches
        2. Second pass: Remove exact PMID matches
        3. Third pass: Remove similar titles (case-insensitive, normalized)
        """
        seen_dois = set()
        seen_pmids = set()
        seen_titles = set()
        unique = []

        for study in studies:
            # Normalize identifiers
            doi = study.get("doi", "").strip().lower()
            pmid = study.get("pmid", "").strip()
            title = study.get("title", "").lower().strip()

            # Check DOI first (most reliable)
            if doi and doi in seen_dois:
                continue
            if doi:
                seen_dois.add(doi)

            # Check PMID
            if pmid and pmid in seen_pmids:
                continue
            if pmid:
                seen_pmids.add(pmid)

            # Check title (least reliable, but catches most duplicates)
            if title and title in seen_titles:
                continue
            if title:
                seen_titles.add(title)

            unique.append(study)

        logger.info(
            f"Enhanced deduplication: {len(studies)} -> {len(unique)} studies "
            f"(DOIs: {len(seen_dois)}, PMIDs: {len(seen_pmids)}, Titles: {len(seen_titles)})"
        )
        return unique
