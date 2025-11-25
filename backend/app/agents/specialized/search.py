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

You are familiar with and have access to:
- PubMed/MEDLINE (medical & life sciences) ✅
- arXiv (preprints: physics, math, CS, q-bio) ✅
- Europe PMC (European biomedical research) ✅
- CORE (open access papers globally) ✅
- DOAJ (Directory of Open Access Journals) ✅
- Semantic Scholar (AI-powered with citations) ✅
- Crossref (DOI metadata, all disciplines) ✅
- BASE (Bielefeld Academic Search Engine, multidisciplinary) ✅

Planned for future integration (require API keys/subscriptions):
- Google Scholar (comprehensive, all disciplines)
- Scopus (citation tracking, all disciplines)
- Web of Science (citation tracking, all disciplines)
- IEEE Xplore (computer science & engineering)
- JSTOR (humanities & social sciences)
- ScienceDirect (Elsevier journals)
- PsycINFO (psychology)
- ERIC (education)
- Cochrane Library (healthcare evidence)
- CINAHL (nursing & allied health)

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
            elif database.lower() == "arxiv":
                results = await self._search_arxiv(search_terms, input_data)
                all_results.extend(results)
                search_log.append({
                    "database": "arXiv",
                    "results_count": len(results),
                    "query": " AND ".join(search_terms),
                })
            elif database.lower() == "europepmc":
                results = await self._search_europepmc(search_terms, input_data)
                all_results.extend(results)
                search_log.append({
                    "database": "Europe PMC",
                    "results_count": len(results),
                    "query": " AND ".join(search_terms),
                })
            elif database.lower() == "core":
                results = await self._search_core(search_terms, input_data)
                all_results.extend(results)
                search_log.append({
                    "database": "CORE",
                    "results_count": len(results),
                    "query": " AND ".join(search_terms),
                })
            elif database.lower() == "doaj":
                results = await self._search_doaj(search_terms, input_data)
                all_results.extend(results)
                search_log.append({
                    "database": "DOAJ",
                    "results_count": len(results),
                    "query": " AND ".join(search_terms),
                })
            elif database.lower() == "semantic_scholar":
                results = await self._search_semantic_scholar(search_terms, input_data)
                all_results.extend(results)
                search_log.append({
                    "database": "Semantic Scholar",
                    "results_count": len(results),
                    "query": " AND ".join(search_terms),
                })
            elif database.lower() == "crossref":
                results = await self._search_crossref(search_terms, input_data)
                all_results.extend(results)
                search_log.append({
                    "database": "Crossref",
                    "results_count": len(results),
                    "query": " AND ".join(search_terms),
                })
            elif database.lower() == "base":
                results = await self._search_base(search_terms, input_data)
                all_results.extend(results)
                search_log.append({
                    "database": "BASE",
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

                # Fetch full abstracts using efetch
                logger.info(f"Fetching abstracts for {len(ids[:20])} studies...")
                abstract_response = await client.get(
                    f"{base_url}efetch.fcgi",
                    params={
                        "db": "pubmed",
                        "id": ",".join(ids[:20]),
                        "retmode": "xml",
                        "rettype": "abstract",
                    },
                    timeout=30.0,
                )

                # Parse abstracts from XML
                abstracts = {}
                if abstract_response.status_code == 200:
                    import xml.etree.ElementTree as ET
                    try:
                        root = ET.fromstring(abstract_response.content)
                        for article in root.findall(".//PubmedArticle"):
                            pmid_elem = article.find(".//PMID")
                            abstract_elem = article.find(".//AbstractText")

                            if pmid_elem is not None and abstract_elem is not None:
                                pmid = pmid_elem.text
                                abstract_text = abstract_elem.text or ""
                                abstracts[pmid] = abstract_text

                        logger.info(f"Successfully fetched {len(abstracts)} abstracts")
                    except Exception as e:
                        logger.warning(f"Error parsing abstracts XML: {e}")
                else:
                    logger.warning(f"Failed to fetch abstracts: {abstract_response.status_code}")

                results = []

                for pmid, study in summary_data.get("result", {}).items():
                    if pmid == "uids":
                        continue

                    # Get abstract from fetched data
                    abstract = abstracts.get(pmid, "")

                    results.append({
                        "id": f"PMID:{pmid}",
                        "pmid": pmid,  # Add explicit PMID field
                        "title": study.get("title", ""),
                        "authors": study.get("authors", []),
                        "journal": study.get("fulljournalname", ""),
                        "year": study.get("pubdate", "").split()[0] if study.get("pubdate") else "",
                        "abstract": abstract,  # Now includes real abstract!
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

    async def _search_arxiv(
        self, search_terms: List[str], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search arXiv preprint repository.

        Args:
            search_terms: List of search terms
            params: Additional search parameters

        Returns:
            List of study results
        """
        # Construct query for arXiv API
        query = " AND ".join(search_terms)

        # arXiv API (use HTTPS to avoid redirects)
        base_url = "https://export.arxiv.org/api/query"

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(
                    base_url,
                    params={
                        "search_query": f"all:{query}",
                        "start": 0,
                        "max_results": 50,  # Limit for demo
                    },
                    timeout=30.0,
                )

                if response.status_code != 200:
                    logger.error(f"arXiv search failed: {response.status_code}")
                    return []

                # Parse XML response (arXiv returns Atom feed)
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

                    results.append({
                        "id": f"arXiv:{arxiv_id}",
                        "title": title_elem.text.strip() if title_elem is not None else "",
                        "authors": authors,
                        "journal": "arXiv Preprint",
                        "year": published_elem.text[:4] if published_elem is not None else "",
                        "abstract": summary_elem.text.strip() if summary_elem is not None else "",
                        "doi": "",
                        "database": "arXiv",
                        "url": id_elem.text if id_elem is not None else "",
                    })

                return results

        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            return []

    async def _search_europepmc(
        self, search_terms: List[str], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search Europe PMC database.

        Args:
            search_terms: List of search terms
            params: Additional search parameters

        Returns:
            List of study results
        """
        # Construct query
        query = " AND ".join([f'"{term}"' for term in search_terms])

        # Europe PMC API
        base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    base_url,
                    params={
                        "query": query,
                        "pageSize": 50,  # Limit for demo
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

        except Exception as e:
            logger.error(f"Error searching Europe PMC: {e}")
            return []

    async def _search_core(
        self, search_terms: List[str], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search CORE (COnnecting REpositories) for open access papers.

        Args:
            search_terms: List of search terms
            params: Additional search parameters

        Returns:
            List of study results
        """
        # Construct query
        query = " ".join(search_terms)

        # CORE API v3 (search endpoint doesn't require API key)
        base_url = "https://api.core.ac.uk/v3/search/works"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    base_url,
                    json={
                        "q": query,
                        "limit": 50,  # Limit for demo
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

        except Exception as e:
            logger.error(f"Error searching CORE: {e}")
            return []

    async def _search_doaj(
        self, search_terms: List[str], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search Directory of Open Access Journals (DOAJ).

        Args:
            search_terms: List of search terms
            params: Additional search parameters

        Returns:
            List of study results
        """
        query = " AND ".join(search_terms)
        base_url = "https://doaj.org/api/search/articles"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    base_url,
                    params={
                        "q": query,
                        "pageSize": 50,
                    },
                    timeout=30.0,
                )

                if response.status_code != 200:
                    logger.error(f"DOAJ search failed: {response.status_code}")
                    return []

                data = response.json()
                results_list = data.get("results", [])

                logger.info(f"Found {len(results_list)} results in DOAJ")

                results = []
                for study in results_list:
                    bibjson = study.get("bibjson", {})

                    # Extract authors
                    authors = []
                    for author in bibjson.get("author", []):
                        name = author.get("name", "")
                        if name:
                            authors.append(name)

                    # Extract identifiers
                    doi = ""
                    for identifier in bibjson.get("identifier", []):
                        if identifier.get("type") == "doi":
                            doi = identifier.get("id", "")
                            break

                    results.append({
                        "id": f"DOAJ:{study.get('id', '')}",
                        "title": bibjson.get("title", ""),
                        "authors": authors,
                        "journal": bibjson.get("journal", {}).get("title", ""),
                        "year": str(bibjson.get("year", "")),
                        "abstract": bibjson.get("abstract", ""),
                        "doi": doi,
                        "database": "DOAJ",
                        "url": study.get("link", [{}])[0].get("url", "") if study.get("link") else "",
                    })

                return results

        except Exception as e:
            logger.error(f"Error searching DOAJ: {e}")
            return []

    async def _search_semantic_scholar(
        self, search_terms: List[str], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search Semantic Scholar - AI-powered research tool with citation data.

        Args:
            search_terms: List of search terms
            params: Additional search parameters

        Returns:
            List of study results
        """
        query = " ".join(search_terms)
        base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    base_url,
                    params={
                        "query": query,
                        "limit": 50,
                        "fields": "paperId,title,authors,year,abstract,venue,citationCount,openAccessPdf,externalIds",
                    },
                    timeout=30.0,
                )

                if response.status_code != 200:
                    logger.error(f"Semantic Scholar search failed: {response.status_code}")
                    return []

                data = response.json()
                papers = data.get("data", [])

                logger.info(f"Found {len(papers)} results in Semantic Scholar")

                results = []
                for paper in papers:
                    # Extract authors
                    authors = [a.get("name", "") for a in paper.get("authors", [])]

                    # Get DOI or other IDs
                    external_ids = paper.get("externalIds", {})
                    doi = external_ids.get("DOI", "")
                    pmid = external_ids.get("PubMed", "")

                    # Get PDF URL if available
                    pdf_url = ""
                    if paper.get("openAccessPdf"):
                        pdf_url = paper.get("openAccessPdf", {}).get("url", "")

                    results.append({
                        "id": f"S2:{paper.get('paperId', '')}",
                        "pmid": pmid if pmid else None,
                        "title": paper.get("title", ""),
                        "authors": authors,
                        "journal": paper.get("venue", ""),
                        "year": str(paper.get("year", "")),
                        "abstract": paper.get("abstract", ""),
                        "doi": doi,
                        "database": "Semantic Scholar",
                        "citation_count": paper.get("citationCount", 0),
                        "pdf_url": pdf_url,
                    })

                return results

        except Exception as e:
            logger.error(f"Error searching Semantic Scholar: {e}")
            return []

    async def _search_crossref(
        self, search_terms: List[str], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search Crossref - DOI registration agency with extensive metadata.

        Args:
            search_terms: List of search terms
            params: Additional search parameters

        Returns:
            List of study results
        """
        query = " ".join(search_terms)
        base_url = "https://api.crossref.org/works"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    base_url,
                    params={
                        "query": query,
                        "rows": 50,
                        "mailto": settings.pubmed_email or "demo@example.com",  # Polite API usage
                    },
                    timeout=30.0,
                )

                if response.status_code != 200:
                    logger.error(f"Crossref search failed: {response.status_code}")
                    return []

                data = response.json()
                items = data.get("message", {}).get("items", [])

                logger.info(f"Found {len(items)} results in Crossref")

                results = []
                for item in items:
                    # Extract authors
                    authors = []
                    for author in item.get("author", []):
                        given = author.get("given", "")
                        family = author.get("family", "")
                        if given and family:
                            authors.append(f"{given} {family}")
                        elif family:
                            authors.append(family)

                    # Extract year
                    year = ""
                    if "published" in item:
                        date_parts = item["published"].get("date-parts", [[]])[0]
                        if date_parts:
                            year = str(date_parts[0])
                    elif "created" in item:
                        date_parts = item["created"].get("date-parts", [[]])[0]
                        if date_parts:
                            year = str(date_parts[0])

                    # Get abstract
                    abstract = item.get("abstract", "")

                    results.append({
                        "id": f"DOI:{item.get('DOI', '')}",
                        "title": item.get("title", [""])[0] if item.get("title") else "",
                        "authors": authors,
                        "journal": item.get("container-title", [""])[0] if item.get("container-title") else "",
                        "year": year,
                        "abstract": abstract,
                        "doi": item.get("DOI", ""),
                        "database": "Crossref",
                        "type": item.get("type", ""),
                        "publisher": item.get("publisher", ""),
                    })

                return results

        except Exception as e:
            logger.error(f"Error searching Crossref: {e}")
            return []

    async def _search_base(
        self, search_terms: List[str], params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search BASE (Bielefeld Academic Search Engine) - large multidisciplinary index.

        Args:
            search_terms: List of search terms
            params: Additional search parameters

        Returns:
            List of study results
        """
        query = " AND ".join([f'"{term}"' for term in search_terms])
        base_url = "https://api.base-search.net/cgi-bin/BaseHttpSearchInterface.fcgi"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    base_url,
                    params={
                        "func": "PerformSearch",
                        "query": query,
                        "hits": 50,
                        "format": "json",
                    },
                    timeout=30.0,
                )

                if response.status_code != 200:
                    logger.error(f"BASE search failed: {response.status_code}")
                    return []

                data = response.json()
                docs = data.get("response", {}).get("docs", [])

                logger.info(f"Found {len(docs)} results in BASE")

                results = []
                for doc in docs:
                    # Extract authors
                    authors = doc.get("dcauthor", [])
                    if isinstance(authors, str):
                        authors = [authors]

                    results.append({
                        "id": f"BASE:{doc.get('dcidentifier', [''])[0] if isinstance(doc.get('dcidentifier'), list) else doc.get('dcidentifier', '')}",
                        "title": doc.get("dctitle", [""])[0] if isinstance(doc.get("dctitle"), list) else doc.get("dctitle", ""),
                        "authors": authors,
                        "journal": doc.get("dccollection", [""])[0] if isinstance(doc.get("dccollection"), list) else doc.get("dccollection", ""),
                        "year": str(doc.get("dcyear", "")),
                        "abstract": doc.get("dcsubject", [""])[0] if isinstance(doc.get("dcsubject"), list) else doc.get("dcsubject", ""),  # BASE doesn't always have abstracts
                        "doi": doc.get("dclink", [""])[0] if isinstance(doc.get("dclink"), list) and "doi.org" in str(doc.get("dclink", [""])[0]) else "",
                        "database": "BASE",
                        "type": doc.get("dctypenorm", [""])[0] if isinstance(doc.get("dctypenorm"), list) else doc.get("dctypenorm", ""),
                    })

                return results

        except Exception as e:
            logger.error(f"Error searching BASE: {e}")
            return []
