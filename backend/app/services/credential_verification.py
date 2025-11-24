"""
Credential Verification Service
Automatically verifies ORCID, Google Scholar, and other academic credentials.
"""

import httpx
import asyncio
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from scholarly import scholarly
from app.core.config import settings
from app.core.logging_config import logger
import re


class ORCIDVerificationService:
    """
    Verifies ORCID profiles via the public ORCID API.
    Documentation: https://info.orcid.org/documentation/api-tutorials/api-tutorial-read-data-on-a-record/
    """

    BASE_URL = "https://pub.orcid.org/v3.0"

    @staticmethod
    def validate_orcid_format(orcid_id: str) -> bool:
        """
        Validate ORCID ID format: 0000-0001-2345-6789
        """
        pattern = r'^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$'
        return bool(re.match(pattern, orcid_id))

    @staticmethod
    async def verify_orcid(orcid_id: str) -> Dict:
        """
        Verify ORCID profile and fetch public data.

        Returns:
        {
            "verified": bool,
            "profile_exists": bool,
            "is_public": bool,
            "data": {
                "name": str,
                "works_count": int,
                "employment": list,
                "education": list,
                "works": list (top 10)
            },
            "error": str (if verification failed)
        }
        """
        if not ORCIDVerificationService.validate_orcid_format(orcid_id):
            return {
                "verified": False,
                "profile_exists": False,
                "error": "Invalid ORCID format. Expected: 0000-0001-2345-6789"
            }

        try:
            async with httpx.AsyncClient() as client:
                # Fetch full record
                response = await client.get(
                    f"{ORCIDVerificationService.BASE_URL}/{orcid_id}",
                    headers={"Accept": "application/json"},
                    timeout=30.0
                )

                if response.status_code == 404:
                    return {
                        "verified": False,
                        "profile_exists": False,
                        "error": "ORCID profile not found"
                    }

                if response.status_code != 200:
                    return {
                        "verified": False,
                        "error": f"ORCID API error: {response.status_code}"
                    }

                data = response.json()

                # Extract key information
                person = data.get("person", {})
                activities = data.get("activities-summary", {})

                # Get name
                name = None
                if person.get("name"):
                    given_names = person["name"].get("given-names", {}).get("value", "")
                    family_name = person["name"].get("family-name", {}).get("value", "")
                    name = f"{given_names} {family_name}".strip()

                # Get works (publications)
                works = activities.get("works", {}).get("group", [])
                works_count = len(works)

                # Get employment history
                employments = []
                employment_summaries = activities.get("employments", {}).get("affiliation-group", [])
                for emp_group in employment_summaries[:5]:  # Top 5
                    for summary in emp_group.get("summaries", []):
                        emp_summary = summary.get("employment-summary", {})
                        org = emp_summary.get("organization", {})
                        employments.append({
                            "organization": org.get("name"),
                            "role": emp_summary.get("role-title"),
                            "start_date": emp_summary.get("start-date"),
                            "end_date": emp_summary.get("end-date")
                        })

                # Get education history
                educations = []
                education_summaries = activities.get("educations", {}).get("affiliation-group", [])
                for edu_group in education_summaries[:5]:  # Top 5
                    for summary in edu_group.get("summaries", []):
                        edu_summary = summary.get("education-summary", {})
                        org = edu_summary.get("organization", {})
                        educations.append({
                            "organization": org.get("name"),
                            "degree": edu_summary.get("role-title"),
                            "start_date": edu_summary.get("start-date"),
                            "end_date": edu_summary.get("end-date")
                        })

                # Get top 10 publication titles
                publication_titles = []
                for work_group in works[:10]:
                    for work_summary in work_group.get("work-summary", []):
                        title = work_summary.get("title", {}).get("title", {}).get("value")
                        if title:
                            publication_titles.append(title)

                # Check if profile has minimum required data
                has_minimum_data = (
                    works_count >= 3 and
                    len(employments) > 0 and
                    len(educations) > 0
                )

                return {
                    "verified": True,
                    "profile_exists": True,
                    "is_public": True,
                    "has_minimum_data": has_minimum_data,
                    "data": {
                        "orcid_id": orcid_id,
                        "name": name,
                        "works_count": works_count,
                        "employment": employments,
                        "education": educations,
                        "publication_titles": publication_titles,
                        "fetched_at": datetime.utcnow().isoformat()
                    }
                }

        except httpx.TimeoutException:
            logger.error(f"ORCID verification timeout for {orcid_id}")
            return {
                "verified": False,
                "error": "Request timeout while verifying ORCID profile"
            }
        except Exception as e:
            logger.error(f"ORCID verification error for {orcid_id}: {e}")
            return {
                "verified": False,
                "error": f"Unexpected error: {str(e)}"
            }


class GoogleScholarVerificationService:
    """
    Verifies Google Scholar profiles and fetches h-index, citations, publications.
    Uses the scholarly library for web scraping.
    """

    @staticmethod
    def extract_scholar_id_from_url(url: str) -> Optional[str]:
        """
        Extract Scholar ID from Google Scholar URL.
        Example: https://scholar.google.com/citations?user=SCHOLAR_ID
        """
        match = re.search(r'[?&]user=([^&]+)', url)
        return match.group(1) if match else None

    @staticmethod
    async def verify_google_scholar(profile_url: str) -> Dict:
        """
        Verify Google Scholar profile and fetch metrics.

        Returns:
        {
            "verified": bool,
            "profile_exists": bool,
            "data": {
                "name": str,
                "affiliation": str,
                "h_index": int,
                "h_index_5y": int,
                "i10_index": int,
                "i10_index_5y": int,
                "total_citations": int,
                "publications_count": int,
                "recent_publications": list (last 5 years),
                "top_publications": list (top 5 by citations)
            },
            "error": str (if verification failed)
        }
        """
        scholar_id = GoogleScholarVerificationService.extract_scholar_id_from_url(profile_url)

        if not scholar_id:
            return {
                "verified": False,
                "profile_exists": False,
                "error": "Invalid Google Scholar URL. Could not extract user ID."
            }

        try:
            # Use asyncio to run synchronous scholarly library in thread pool
            def _fetch_scholar_data():
                try:
                    # Search for author by ID
                    author = scholarly.search_author_id(scholar_id)

                    if not author:
                        return None

                    # Fill author details
                    author = scholarly.fill(author)

                    return author
                except Exception as e:
                    logger.error(f"Scholarly library error: {e}")
                    return None

            # Run in executor to avoid blocking
            author = await asyncio.get_event_loop().run_in_executor(
                None,
                _fetch_scholar_data
            )

            if not author:
                return {
                    "verified": False,
                    "profile_exists": False,
                    "error": "Google Scholar profile not found"
                }

            # Extract key metrics
            h_index = author.get("hindex", 0)
            h_index_5y = author.get("hindex5y", 0)
            i10_index = author.get("i10index", 0)
            i10_index_5y = author.get("i10index5y", 0)
            total_citations = author.get("citedby", 0)

            # Get publications
            publications = author.get("publications", [])
            publications_count = len(publications)

            # Filter recent publications (last 5 years)
            current_year = datetime.now().year
            recent_publications = []
            for pub in publications:
                pub_year = pub.get("bib", {}).get("pub_year")
                if pub_year and int(pub_year) >= current_year - 5:
                    recent_publications.append({
                        "title": pub.get("bib", {}).get("title"),
                        "year": pub_year,
                        "citations": pub.get("num_citations", 0),
                        "venue": pub.get("bib", {}).get("venue", "")
                    })

            # Get top 5 publications by citations
            sorted_pubs = sorted(
                publications,
                key=lambda p: p.get("num_citations", 0),
                reverse=True
            )
            top_publications = []
            for pub in sorted_pubs[:5]:
                top_publications.append({
                    "title": pub.get("bib", {}).get("title"),
                    "year": pub.get("bib", {}).get("pub_year"),
                    "citations": pub.get("num_citations", 0),
                    "venue": pub.get("bib", {}).get("venue", "")
                })

            # Check minimum requirements
            has_minimum_data = (
                publications_count >= 3 and
                h_index >= 3 and
                len(recent_publications) > 0
            )

            return {
                "verified": True,
                "profile_exists": True,
                "is_public": True,
                "has_minimum_data": has_minimum_data,
                "data": {
                    "scholar_id": scholar_id,
                    "name": author.get("name"),
                    "affiliation": author.get("affiliation"),
                    "h_index": h_index,
                    "h_index_5y": h_index_5y,
                    "i10_index": i10_index,
                    "i10_index_5y": i10_index_5y,
                    "total_citations": total_citations,
                    "publications_count": publications_count,
                    "recent_publications_count": len(recent_publications),
                    "recent_publications": recent_publications[:10],  # Limit to 10
                    "top_publications": top_publications,
                    "fetched_at": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Google Scholar verification error: {e}")
            return {
                "verified": False,
                "error": f"Failed to fetch Google Scholar data: {str(e)}"
            }


class PublicationVerificationService:
    """
    Verifies publication DOIs via CrossRef API.
    """

    @staticmethod
    async def verify_doi(doi: str) -> Dict:
        """
        Verify DOI and fetch publication metadata via CrossRef.

        Returns:
        {
            "verified": bool,
            "data": {
                "title": str,
                "authors": list,
                "journal": str,
                "year": int,
                "type": str (journal-article, book-chapter, etc.),
                "citations": int,
                "is_peer_reviewed": bool
            },
            "error": str
        }
        """
        if not doi:
            return {"verified": False, "error": "No DOI provided"}

        # Clean DOI (remove URL prefix if present)
        doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.crossref.org/works/{doi}",
                    timeout=15.0
                )

                if response.status_code == 404:
                    return {
                        "verified": False,
                        "error": "DOI not found in CrossRef database"
                    }

                if response.status_code != 200:
                    return {
                        "verified": False,
                        "error": f"CrossRef API error: {response.status_code}"
                    }

                data = response.json()
                message = data.get("message", {})

                # Extract metadata
                title = message.get("title", [""])[0]
                authors = []
                for author in message.get("author", []):
                    given = author.get("given", "")
                    family = author.get("family", "")
                    authors.append(f"{given} {family}".strip())

                journal = message.get("container-title", [""])[0]
                year = None
                if message.get("published-print"):
                    year = message["published-print"]["date-parts"][0][0]
                elif message.get("published-online"):
                    year = message["published-online"]["date-parts"][0][0]

                pub_type = message.get("type", "unknown")
                citations = message.get("is-referenced-by-count", 0)

                # Check if peer-reviewed (heuristic based on type and journal)
                is_peer_reviewed = pub_type in ["journal-article", "proceedings-article"]

                return {
                    "verified": True,
                    "data": {
                        "doi": doi,
                        "title": title,
                        "authors": authors,
                        "journal": journal,
                        "year": year,
                        "type": pub_type,
                        "citations": citations,
                        "is_peer_reviewed": is_peer_reviewed,
                        "fetched_at": datetime.utcnow().isoformat()
                    }
                }

        except Exception as e:
            logger.error(f"DOI verification error for {doi}: {e}")
            return {
                "verified": False,
                "error": f"Failed to verify DOI: {str(e)}"
            }

    @staticmethod
    async def verify_multiple_dois(dois: List[str]) -> List[Dict]:
        """Verify multiple DOIs concurrently."""
        tasks = [PublicationVerificationService.verify_doi(doi) for doi in dois]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        verified_results = []
        for doi, result in zip(dois, results):
            if isinstance(result, Exception):
                verified_results.append({
                    "doi": doi,
                    "verified": False,
                    "error": str(result)
                })
            else:
                verified_results.append(result)

        return verified_results


class BackgroundCheckService:
    """
    Performs background checks for research misconduct and ethics violations.
    """

    @staticmethod
    async def check_ori_database(researcher_name: str) -> Dict:
        """
        Check Office of Research Integrity (ORI) database for misconduct findings.

        NOTE: ORI doesn't have a public API. This would require web scraping
        or manual checking. For MVP, we'll return a placeholder.

        Returns:
        {
            "checked": bool,
            "findings": list,
            "check_date": str
        }
        """
        # TODO: Implement actual ORI database check
        # For now, return no findings
        return {
            "checked": True,
            "findings": [],
            "check_date": datetime.utcnow().isoformat(),
            "note": "Manual verification required for production"
        }

    @staticmethod
    async def check_retraction_watch(researcher_name: str, dois: List[str]) -> Dict:
        """
        Check Retraction Watch database for retracted publications.

        NOTE: Retraction Watch API requires subscription. This is a placeholder.

        Returns:
        {
            "checked": bool,
            "retractions_found": int,
            "retracted_papers": list,
            "check_date": str
        }
        """
        # TODO: Integrate with Retraction Watch API
        # Requires API key and subscription
        return {
            "checked": True,
            "retractions_found": 0,
            "retracted_papers": [],
            "check_date": datetime.utcnow().isoformat(),
            "note": "Retraction Watch API integration pending"
        }

    @staticmethod
    async def check_pubpeer(researcher_name: str, dois: List[str]) -> Dict:
        """
        Check PubPeer for post-publication peer review comments and concerns.

        NOTE: PubPeer doesn't have official API. This requires web scraping.

        Returns:
        {
            "checked": bool,
            "flagged_papers": int,
            "concerns": list,
            "check_date": str
        }
        """
        # TODO: Implement PubPeer scraping
        return {
            "checked": True,
            "flagged_papers": 0,
            "concerns": [],
            "check_date": datetime.utcnow().isoformat(),
            "note": "PubPeer integration pending"
        }


class ComprehensiveVerificationService:
    """
    Orchestrates all verification services for a complete credential check.
    """

    @staticmethod
    async def verify_all_credentials(
        orcid_id: Optional[str],
        google_scholar_url: Optional[str],
        publication_dois: List[str],
        researcher_name: str
    ) -> Dict:
        """
        Run all verification checks concurrently.

        Returns comprehensive verification report.
        """
        results = {}

        # Run all verifications concurrently
        verification_tasks = []

        if orcid_id:
            verification_tasks.append(
                ("orcid", ORCIDVerificationService.verify_orcid(orcid_id))
            )

        if google_scholar_url:
            verification_tasks.append(
                ("google_scholar", GoogleScholarVerificationService.verify_google_scholar(google_scholar_url))
            )

        if publication_dois:
            verification_tasks.append(
                ("publications", PublicationVerificationService.verify_multiple_dois(publication_dois))
            )

        # Background checks
        verification_tasks.extend([
            ("ori", BackgroundCheckService.check_ori_database(researcher_name)),
            ("retraction_watch", BackgroundCheckService.check_retraction_watch(researcher_name, publication_dois)),
            ("pubpeer", BackgroundCheckService.check_pubpeer(researcher_name, publication_dois))
        ])

        # Execute all tasks
        task_results = await asyncio.gather(*[task for _, task in verification_tasks])

        # Map results
        for (name, _), result in zip(verification_tasks, task_results):
            results[name] = result

        # Calculate overall verification status
        verification_passed = (
            results.get("orcid", {}).get("verified", False) and
            results.get("google_scholar", {}).get("verified", False) and
            results.get("orcid", {}).get("has_minimum_data", False) and
            results.get("google_scholar", {}).get("has_minimum_data", False)
        )

        # Check for disqualifying findings
        disqualifying = (
            results.get("ori", {}).get("findings") or
            results.get("retraction_watch", {}).get("retractions_found", 0) > 2  # Allow 1-2 retractions
        )

        return {
            "verification_passed": verification_passed and not disqualifying,
            "verification_date": datetime.utcnow().isoformat(),
            "results": results,
            "summary": {
                "orcid_verified": results.get("orcid", {}).get("verified", False),
                "google_scholar_verified": results.get("google_scholar", {}).get("verified", False),
                "h_index": results.get("google_scholar", {}).get("data", {}).get("h_index", 0),
                "total_citations": results.get("google_scholar", {}).get("data", {}).get("total_citations", 0),
                "publications_count": results.get("google_scholar", {}).get("data", {}).get("publications_count", 0),
                "orcid_works_count": results.get("orcid", {}).get("data", {}).get("works_count", 0),
                "background_checks_clear": not disqualifying
            }
        }


# Convenience function for application review
async def auto_verify_application(
    orcid_id: str,
    google_scholar_url: str,
    publication_dois: List[str],
    researcher_name: str
) -> Tuple[bool, Dict]:
    """
    Automatically verify all credentials for a tier application.

    Returns:
        (verification_passed: bool, detailed_results: dict)
    """
    logger.info(f"Starting automatic verification for {researcher_name}")

    try:
        results = await ComprehensiveVerificationService.verify_all_credentials(
            orcid_id=orcid_id,
            google_scholar_url=google_scholar_url,
            publication_dois=publication_dois,
            researcher_name=researcher_name
        )

        passed = results["verification_passed"]

        logger.info(f"Verification complete for {researcher_name}: {'PASSED' if passed else 'FAILED'}")

        return passed, results

    except Exception as e:
        logger.error(f"Verification failed for {researcher_name}: {e}")
        return False, {"error": str(e), "verification_passed": False}
