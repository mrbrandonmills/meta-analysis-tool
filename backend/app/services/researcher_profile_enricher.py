"""Researcher Profile Enricher - Enriches researcher profiles by scraping academic data sources.

This service integrates with:
- Google Scholar (via scholarly library)
- ORCID API
- Semantic Scholar API
- Claude AI for publication analysis

It extracts comprehensive researcher data including:
- Publications and citations
- H-index and academic metrics
- Research domains and keywords
- Co-author networks
- Employment and education history
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import httpx
from loguru import logger
from scholarly import scholarly
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.researcher import Researcher


class RateLimiter:
    """Simple rate limiter for API requests."""

    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[float] = []

    async def acquire(self):
        """Wait if necessary to respect rate limit."""
        now = time.time()

        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests
                        if now - req_time < self.time_window]

        if len(self.requests) >= self.max_requests:
            # Wait until oldest request expires
            sleep_time = self.time_window - (now - self.requests[0]) + 0.1
            logger.debug(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)
            return await self.acquire()

        self.requests.append(now)


class ResearcherProfileEnricher:
    """Service for enriching researcher profiles from academic data sources."""

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """Initialize enricher with API credentials.

        Args:
            anthropic_api_key: Optional Anthropic API key (uses settings if not provided)
        """
        self.settings = get_settings()
        self.anthropic_api_key = anthropic_api_key or self.settings.anthropic_api_key

        # Rate limiters for different APIs
        self.google_scholar_limiter = RateLimiter(max_requests=10, time_window=60)
        self.semantic_scholar_limiter = RateLimiter(max_requests=100, time_window=300)
        self.orcid_limiter = RateLimiter(max_requests=24, time_window=60)

        # HTTP client with proper User-Agent
        self.http_client = httpx.AsyncClient(
            headers={
                "User-Agent": "Meta-Analysis-Platform/1.0 (Contact: research@meta-analysis.com)",
                "Accept": "application/json"
            },
            timeout=30.0
        )

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()

    async def enrich_researcher_profile(
        self,
        researcher_id: UUID,
        db: AsyncSession
    ) -> Dict[str, any]:
        """Enrich researcher profile with data from multiple sources.

        Args:
            researcher_id: UUID of researcher to enrich
            db: Database session

        Returns:
            Dict with enrichment results and completeness score

        Raises:
            ValueError: If researcher not found
        """
        # Fetch researcher
        result = await db.execute(
            select(Researcher).where(Researcher.id == researcher_id)
        )
        researcher = result.scalar_one_or_none()

        if not researcher:
            raise ValueError(f"Researcher not found: {researcher_id}")

        logger.info(f"Enriching profile for researcher: {researcher.name} ({researcher_id})")

        enrichment_data = {
            "researcher_id": str(researcher_id),
            "researcher_name": researcher.name,
            "sources_checked": [],
            "data_found": {},
            "errors": []
        }

        # 1. Google Scholar enrichment
        try:
            google_scholar_data = await self.search_google_scholar(
                researcher.name,
                researcher.institution
            )
            if google_scholar_data:
                enrichment_data["sources_checked"].append("google_scholar")
                enrichment_data["data_found"]["google_scholar"] = google_scholar_data
                await self._apply_google_scholar_data(researcher, google_scholar_data)
        except Exception as e:
            logger.error(f"Google Scholar enrichment failed: {e}")
            enrichment_data["errors"].append(f"Google Scholar: {str(e)}")

        # 2. ORCID enrichment (if ORCID ID provided)
        if researcher.orcid:
            try:
                orcid_data = await self.fetch_orcid_profile(researcher.orcid)
                if orcid_data:
                    enrichment_data["sources_checked"].append("orcid")
                    enrichment_data["data_found"]["orcid"] = orcid_data
                    await self._apply_orcid_data(researcher, orcid_data)
            except Exception as e:
                logger.error(f"ORCID enrichment failed: {e}")
                enrichment_data["errors"].append(f"ORCID: {str(e)}")

        # 3. Semantic Scholar enrichment
        try:
            semantic_data = await self.search_semantic_scholar(
                researcher.name,
                researcher.institution
            )
            if semantic_data:
                enrichment_data["sources_checked"].append("semantic_scholar")
                enrichment_data["data_found"]["semantic_scholar"] = semantic_data
                await self._apply_semantic_scholar_data(researcher, semantic_data)
        except Exception as e:
            logger.error(f"Semantic Scholar enrichment failed: {e}")
            enrichment_data["errors"].append(f"Semantic Scholar: {str(e)}")

        # 4. Analyze publications with Claude AI to extract domains/keywords
        if researcher.researcher_metadata and "publications" in researcher.researcher_metadata:
            try:
                publications = researcher.researcher_metadata["publications"][:10]  # Top 10
                analysis = await self.analyze_publications(publications)
                if analysis:
                    enrichment_data["data_found"]["ai_analysis"] = analysis
                    await self._apply_ai_analysis(researcher, analysis)
            except Exception as e:
                logger.error(f"AI publication analysis failed: {e}")
                enrichment_data["errors"].append(f"AI Analysis: {str(e)}")

        # 5. Calculate completeness score
        completeness_score = await self.calculate_profile_completeness(researcher)
        enrichment_data["completeness_score"] = completeness_score
        enrichment_data["completeness_percentage"] = f"{completeness_score * 100:.1f}%"

        # Update researcher metadata
        if not researcher.researcher_metadata:
            researcher.researcher_metadata = {}

        researcher.researcher_metadata["last_enrichment"] = datetime.utcnow().isoformat()
        researcher.researcher_metadata["enrichment_summary"] = enrichment_data

        # Commit changes
        await db.commit()
        await db.refresh(researcher)

        logger.info(
            f"Enrichment complete for {researcher.name}: "
            f"{completeness_score * 100:.1f}% complete, "
            f"{len(enrichment_data['sources_checked'])} sources checked"
        )

        return enrichment_data

    async def search_google_scholar(
        self,
        name: str,
        institution: Optional[str] = None
    ) -> Optional[Dict]:
        """Search Google Scholar and extract researcher profile.

        Args:
            name: Researcher name
            institution: Optional institution for better matching

        Returns:
            Dict with Google Scholar data or None if not found
        """
        await self.google_scholar_limiter.acquire()

        try:
            logger.info(f"Searching Google Scholar for: {name}")

            # Search for researcher
            search_query = scholarly.search_author(name)
            author = next(search_query, None)

            if not author:
                logger.warning(f"No Google Scholar profile found for: {name}")
                return None

            # Fill in author details
            author = scholarly.fill(author)

            # Extract data
            data = {
                "scholar_id": author.get("scholar_id"),
                "name": author.get("name"),
                "affiliation": author.get("affiliation"),
                "email": author.get("email_domain"),
                "h_index": author.get("hindex"),
                "i10_index": author.get("i10index"),
                "total_citations": author.get("citedby"),
                "interests": author.get("interests", []),
                "homepage": author.get("homepage"),
                "publications": []
            }

            # Extract recent publications (limit to 20 for performance)
            publications = author.get("publications", [])[:20]
            for pub in publications:
                data["publications"].append({
                    "title": pub.get("bib", {}).get("title"),
                    "year": pub.get("bib", {}).get("pub_year"),
                    "citation_count": pub.get("num_citations", 0),
                    "venue": pub.get("bib", {}).get("venue"),
                    "authors": pub.get("bib", {}).get("author"),
                })

            logger.info(
                f"Found Google Scholar profile: h-index={data['h_index']}, "
                f"citations={data['total_citations']}, "
                f"publications={len(data['publications'])}"
            )

            return data

        except StopIteration:
            logger.warning(f"No Google Scholar results for: {name}")
            return None
        except Exception as e:
            logger.error(f"Google Scholar search error: {e}")
            raise

    async def fetch_orcid_profile(self, orcid_id: str) -> Optional[Dict]:
        """Fetch profile from ORCID API.

        Args:
            orcid_id: ORCID identifier (e.g., 0000-0002-1234-5678)

        Returns:
            Dict with ORCID data or None if not found
        """
        await self.orcid_limiter.acquire()

        try:
            logger.info(f"Fetching ORCID profile: {orcid_id}")

            # Clean ORCID ID
            orcid_clean = orcid_id.replace("https://orcid.org/", "").strip()

            # ORCID public API endpoint
            url = f"https://pub.orcid.org/v3.0/{orcid_clean}"

            response = await self.http_client.get(
                url,
                headers={"Accept": "application/json"}
            )

            if response.status_code == 404:
                logger.warning(f"ORCID profile not found: {orcid_id}")
                return None

            response.raise_for_status()
            orcid_data = response.json()

            # Extract relevant data
            person = orcid_data.get("person", {})
            activities = orcid_data.get("activities-summary", {})

            data = {
                "orcid": orcid_clean,
                "name": self._extract_orcid_name(person),
                "biography": person.get("biography", {}).get("content"),
                "keywords": self._extract_orcid_keywords(person),
                "employment": self._extract_orcid_employment(activities),
                "education": self._extract_orcid_education(activities),
                "publications": self._extract_orcid_publications(activities),
                "external_ids": self._extract_orcid_external_ids(person)
            }

            logger.info(
                f"ORCID data retrieved: {len(data['publications'])} publications, "
                f"{len(data['keywords'])} keywords"
            )

            return data

        except httpx.HTTPError as e:
            logger.error(f"ORCID API error: {e}")
            raise
        except Exception as e:
            logger.error(f"ORCID processing error: {e}")
            raise

    async def search_semantic_scholar(
        self,
        name: str,
        institution: Optional[str] = None
    ) -> Optional[Dict]:
        """Search Semantic Scholar API for researcher.

        Args:
            name: Researcher name
            institution: Optional institution for better matching

        Returns:
            Dict with Semantic Scholar data or None if not found
        """
        await self.semantic_scholar_limiter.acquire()

        try:
            logger.info(f"Searching Semantic Scholar for: {name}")

            # Search for author
            url = "https://api.semanticscholar.org/graph/v1/author/search"
            params = {
                "query": name,
                "fields": "authorId,name,affiliations,paperCount,citationCount,hIndex,papers,papers.title,papers.year,papers.citationCount,papers.fieldsOfStudy"
            }

            response = await self.http_client.get(url, params=params)
            response.raise_for_status()

            results = response.json()
            authors = results.get("data", [])

            if not authors:
                logger.warning(f"No Semantic Scholar results for: {name}")
                return None

            # Take first match (could improve matching logic)
            author = authors[0]

            data = {
                "author_id": author.get("authorId"),
                "name": author.get("name"),
                "affiliations": author.get("affiliations", []),
                "paper_count": author.get("paperCount", 0),
                "citation_count": author.get("citationCount", 0),
                "h_index": author.get("hIndex"),
                "publications": [],
                "fields_of_study": set()
            }

            # Extract publication data
            papers = author.get("papers", [])[:20]  # Limit to 20
            for paper in papers:
                pub_data = {
                    "title": paper.get("title"),
                    "year": paper.get("year"),
                    "citation_count": paper.get("citationCount", 0)
                }
                data["publications"].append(pub_data)

                # Collect fields of study
                fields = paper.get("fieldsOfStudy", [])
                data["fields_of_study"].update(fields)

            data["fields_of_study"] = list(data["fields_of_study"])

            logger.info(
                f"Semantic Scholar data: h-index={data['h_index']}, "
                f"papers={data['paper_count']}, "
                f"citations={data['citation_count']}"
            )

            return data

        except httpx.HTTPError as e:
            logger.error(f"Semantic Scholar API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Semantic Scholar processing error: {e}")
            raise

    async def analyze_publications(self, publications: List[Dict]) -> Optional[Dict]:
        """Use Claude AI to analyze publications and extract domains/keywords.

        Args:
            publications: List of publication dicts with title, abstract, etc.

        Returns:
            Dict with extracted domains, keywords, methodology
        """
        try:
            logger.info(f"Analyzing {len(publications)} publications with Claude AI")

            # Format publications for prompt
            publications_text = "\n\n".join([
                f"Title: {pub.get('title', 'Unknown')}\n"
                f"Year: {pub.get('year', 'N/A')}\n"
                f"Citations: {pub.get('citation_count', 0)}"
                for pub in publications
            ])

            prompt = f"""Analyze these academic publications and extract:
1. Primary research domains (e.g., psychology, neuroscience, computer science, biology)
2. Specific research keywords and topics (e.g., fMRI, cognitive load, machine learning)
3. Research methodology types (e.g., experimental, computational, clinical, theoretical)

Publications:
{publications_text}

Return ONLY a valid JSON object with this exact structure:
{{
  "domains": ["domain1", "domain2", "domain3"],
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "methodology": ["method1", "method2"]
}}

Ensure the JSON is valid and properly formatted."""

            # Call Anthropic API
            response = await self.http_client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1024,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )

            response.raise_for_status()
            result = response.json()

            # Extract text content
            content = result.get("content", [])
            if not content:
                logger.warning("No content in Claude API response")
                return None

            text = content[0].get("text", "")

            # Parse JSON from response
            try:
                # Try to extract JSON from response (handle markdown code blocks)
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()

                analysis = json.loads(text)

                logger.info(
                    f"AI analysis complete: {len(analysis.get('domains', []))} domains, "
                    f"{len(analysis.get('keywords', []))} keywords"
                )

                return analysis

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude response as JSON: {e}")
                logger.debug(f"Raw response: {text}")
                return None

        except httpx.HTTPError as e:
            logger.error(f"Claude API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Publication analysis error: {e}")
            raise

    async def calculate_profile_completeness(self, researcher: Researcher) -> float:
        """Calculate profile completeness score (0.0-1.0).

        Scoring breakdown:
        - Name, email, institution: 30% (10% each, required for signup)
        - H-index: 15%
        - Research domains: 15%
        - Keywords: 15%
        - Publications list: 10%
        - ORCID ID: 5%
        - Citation count: 5%
        - Co-author network: 5%

        Args:
            researcher: Researcher model instance

        Returns:
            Completeness score from 0.0 to 1.0
        """
        score = 0.0

        # Required fields (30% total)
        if researcher.name:
            score += 0.10
        if researcher.email:
            score += 0.10
        if researcher.institution:
            score += 0.10

        # H-index (15%)
        if researcher.h_index is not None and researcher.h_index > 0:
            score += 0.15

        # Research domains (15%)
        if researcher.research_domains and len(researcher.research_domains) > 0:
            score += 0.15

        # Keywords (15%)
        if researcher.expertise_keywords and len(researcher.expertise_keywords) > 0:
            score += 0.15

        # Publications list (10%)
        if researcher.researcher_metadata and "publications" in researcher.researcher_metadata:
            publications = researcher.researcher_metadata["publications"]
            if publications and len(publications) > 0:
                score += 0.10

        # ORCID ID (5%)
        if researcher.orcid:
            score += 0.05

        # Citation count (5%)
        if researcher.total_citations > 0:
            score += 0.05

        # Co-author network (5%)
        if researcher.coauthor_ids and len(researcher.coauthor_ids) > 0:
            score += 0.05

        return min(score, 1.0)  # Cap at 1.0

    # Helper methods for applying enrichment data

    async def _apply_google_scholar_data(
        self,
        researcher: Researcher,
        data: Dict
    ):
        """Apply Google Scholar data to researcher model."""
        if data.get("h_index") is not None:
            researcher.h_index = data["h_index"]

        if data.get("i10_index") is not None:
            researcher.i10_index = data["i10_index"]

        if data.get("total_citations") is not None:
            researcher.total_citations = data["total_citations"]

        if data.get("scholar_id"):
            researcher.google_scholar_id = data["scholar_id"]

        if data.get("interests"):
            # Merge with existing keywords
            existing_keywords = set(researcher.expertise_keywords or [])
            new_keywords = existing_keywords.union(data["interests"])
            researcher.expertise_keywords = list(new_keywords)[:50]  # Limit to 50

        if data.get("publications"):
            researcher.publication_count = len(data["publications"])
            if not researcher.researcher_metadata:
                researcher.researcher_metadata = {}
            researcher.researcher_metadata["publications"] = data["publications"]

    async def _apply_orcid_data(
        self,
        researcher: Researcher,
        data: Dict
    ):
        """Apply ORCID data to researcher model."""
        if data.get("keywords"):
            existing_keywords = set(researcher.expertise_keywords or [])
            new_keywords = existing_keywords.union(data["keywords"])
            researcher.expertise_keywords = list(new_keywords)[:50]

        if data.get("employment"):
            if not researcher.researcher_metadata:
                researcher.researcher_metadata = {}
            researcher.researcher_metadata["employment_history"] = data["employment"]

        if data.get("education"):
            if not researcher.researcher_metadata:
                researcher.researcher_metadata = {}
            researcher.researcher_metadata["education_history"] = data["education"]

    async def _apply_semantic_scholar_data(
        self,
        researcher: Researcher,
        data: Dict
    ):
        """Apply Semantic Scholar data to researcher model."""
        if data.get("author_id"):
            researcher.semantic_scholar_id = data["author_id"]

        if data.get("h_index") is not None and not researcher.h_index:
            researcher.h_index = data["h_index"]

        if data.get("citation_count") is not None:
            researcher.total_citations = max(
                researcher.total_citations,
                data["citation_count"]
            )

        if data.get("fields_of_study"):
            existing_domains = set(researcher.research_domains or [])
            new_domains = existing_domains.union(data["fields_of_study"])
            researcher.research_domains = list(new_domains)[:20]

    async def _apply_ai_analysis(
        self,
        researcher: Researcher,
        analysis: Dict
    ):
        """Apply AI analysis results to researcher model."""
        if analysis.get("domains"):
            existing_domains = set(researcher.research_domains or [])
            new_domains = existing_domains.union(analysis["domains"])
            researcher.research_domains = list(new_domains)[:20]

        if analysis.get("keywords"):
            existing_keywords = set(researcher.expertise_keywords or [])
            new_keywords = existing_keywords.union(analysis["keywords"])
            researcher.expertise_keywords = list(new_keywords)[:50]

        if analysis.get("methodology"):
            if not researcher.researcher_metadata:
                researcher.researcher_metadata = {}
            researcher.researcher_metadata["methodology"] = analysis["methodology"]

    # Helper methods for ORCID data extraction

    def _extract_orcid_name(self, person: Dict) -> Optional[str]:
        """Extract name from ORCID person data."""
        name_data = person.get("name", {})
        given_names = name_data.get("given-names", {}).get("value", "")
        family_name = name_data.get("family-name", {}).get("value", "")
        return f"{given_names} {family_name}".strip() if given_names or family_name else None

    def _extract_orcid_keywords(self, person: Dict) -> List[str]:
        """Extract keywords from ORCID person data."""
        keywords_data = person.get("keywords", {}).get("keyword", [])
        return [kw.get("content") for kw in keywords_data if kw.get("content")]

    def _extract_orcid_employment(self, activities: Dict) -> List[Dict]:
        """Extract employment history from ORCID activities."""
        employments = activities.get("employments", {}).get("affiliation-group", [])
        result = []
        for emp_group in employments[:5]:  # Limit to 5 most recent
            summaries = emp_group.get("summaries", [])
            for summary in summaries:
                emp = summary.get("employment-summary", {})
                result.append({
                    "organization": emp.get("organization", {}).get("name"),
                    "role": emp.get("role-title"),
                    "start_date": self._parse_orcid_date(emp.get("start-date")),
                    "end_date": self._parse_orcid_date(emp.get("end-date"))
                })
        return result

    def _extract_orcid_education(self, activities: Dict) -> List[Dict]:
        """Extract education history from ORCID activities."""
        educations = activities.get("educations", {}).get("affiliation-group", [])
        result = []
        for edu_group in educations[:5]:
            summaries = edu_group.get("summaries", [])
            for summary in summaries:
                edu = summary.get("education-summary", {})
                result.append({
                    "organization": edu.get("organization", {}).get("name"),
                    "degree": edu.get("role-title"),
                    "start_date": self._parse_orcid_date(edu.get("start-date")),
                    "end_date": self._parse_orcid_date(edu.get("end-date"))
                })
        return result

    def _extract_orcid_publications(self, activities: Dict) -> List[Dict]:
        """Extract publications from ORCID activities."""
        works = activities.get("works", {}).get("group", [])
        result = []
        for work_group in works[:20]:  # Limit to 20
            summaries = work_group.get("work-summary", [])
            for summary in summaries:
                result.append({
                    "title": summary.get("title", {}).get("title", {}).get("value"),
                    "type": summary.get("type"),
                    "publication_date": self._parse_orcid_date(
                        summary.get("publication-date")
                    )
                })
        return result

    def _extract_orcid_external_ids(self, person: Dict) -> Dict[str, str]:
        """Extract external identifiers from ORCID person data."""
        external_ids = person.get("external-identifiers", {}).get("external-identifier", [])
        result = {}
        for ext_id in external_ids:
            id_type = ext_id.get("external-id-type")
            id_value = ext_id.get("external-id-value")
            if id_type and id_value:
                result[id_type] = id_value
        return result

    def _parse_orcid_date(self, date_data: Optional[Dict]) -> Optional[str]:
        """Parse ORCID date format to ISO string."""
        if not date_data:
            return None
        year = date_data.get("year", {}).get("value")
        month = date_data.get("month", {}).get("value")
        day = date_data.get("day", {}).get("value")

        if year:
            date_str = str(year)
            if month:
                date_str += f"-{int(month):02d}"
                if day:
                    date_str += f"-{int(day):02d}"
            return date_str
        return None


# Factory function for easy instantiation
def create_enricher(anthropic_api_key: Optional[str] = None) -> ResearcherProfileEnricher:
    """Create and return a ResearcherProfileEnricher instance.

    Args:
        anthropic_api_key: Optional API key (uses settings if not provided)

    Returns:
        ResearcherProfileEnricher instance
    """
    return ResearcherProfileEnricher(anthropic_api_key=anthropic_api_key)
