#!/usr/bin/env python3
"""
Fetch and verify REAL study data from the completed meta-analysis.
This proves whether we're pulling actual PubMed studies or simulated data.

Analysis ID: 2e08b849-4a0a-4fa5-84ef-7426f5e7a922
"""
import asyncio
import httpx
import json
from typing import Dict, List, Any

BASE_URL = "https://meta-analysis-tool-production.up.railway.app/api/v1"
ANALYSIS_ID = "2e08b849-4a0a-4fa5-84ef-7426f5e7a922"


async def verify_real_studies():
    """Fetch and verify that studies are REAL PubMed publications."""

    print("=" * 80)
    print("VERIFYING REAL STUDY DATA - NO SIMULATED DATA ALLOWED")
    print("=" * 80)
    print(f"Analysis ID: {ANALYSIS_ID}")
    print()

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Fetch complete agent execution data
        print("Fetching agent execution data from production...")
        response = await client.get(f"{BASE_URL}/meta-analysis/agent-data/{ANALYSIS_ID}")

        if response.status_code != 200:
            print(f"❌ Failed to fetch data: {response.status_code}")
            print(f"   Response: {response.text}")
            return

        data = response.json()
        agent_executions = data.get("agent_executions", [])

        print(f"✅ Fetched data for {len(agent_executions)} agents")
        print()

        # Save raw data
        with open('agent_execution_data_raw.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("✅ Saved raw data to: agent_execution_data_raw.json")
        print()

        # Analyze each agent
        search_studies = []
        screening_decisions = []
        credibility_assessments = []

        for execution in agent_executions:
            agent_type = execution["agent_type"]
            output_data = execution.get("output_data", {})

            print("-" * 80)
            print(f"AGENT: {agent_type.upper()}")
            print(f"Status: {execution['status']}")
            print()

            if agent_type == "search":
                # Extract studies from SearchAgent
                studies = output_data.get("studies", [])
                search_studies = studies

                print(f"📚 SearchAgent Found: {len(studies)} STUDIES")
                print()

                if studies:
                    print("VERIFYING REAL PUBMED DATA:")
                    print()

                    # Check each study for PMID (proof of real data)
                    real_studies = 0
                    for i, study in enumerate(studies, 1):
                        pmid = study.get("pmid")
                        title = study.get("title", "N/A")
                        authors = study.get("authors", "N/A")
                        year = study.get("year", "N/A")
                        journal = study.get("journal", "N/A")

                        if pmid:
                            real_studies += 1
                            print(f"  ✅ Study {i}: REAL PubMed Entry")
                            print(f"     PMID: {pmid}")
                            print(f"     Title: {title[:70]}...")
                            print(f"     Authors: {authors[:50] if isinstance(authors, str) else authors}")
                            print(f"     Journal: {journal}")
                            print(f"     Year: {year}")
                            print(f"     Verify at: https://pubmed.ncbi.nlm.nih.gov/{pmid}/")
                            print()
                        else:
                            print(f"  ⚠️  Study {i}: NO PMID - May be simulated!")
                            print(f"     Title: {title[:70]}...")
                            print()

                    print(f"VERIFICATION RESULT:")
                    print(f"  Real studies with PMIDs: {real_studies}/{len(studies)}")

                    if real_studies == len(studies):
                        print(f"  ✅ ALL STUDIES ARE REAL - 100% VERIFIED")
                    elif real_studies > 0:
                        print(f"  ⚠️  MIXED - Some studies may be simulated")
                    else:
                        print(f"  ❌ NO PMIDS FOUND - DATA MAY BE SIMULATED")

                else:
                    print("  ❌ NO STUDIES FOUND")

            elif agent_type == "screening":
                # Extract screening decisions
                decisions = output_data.get("decisions", [])
                screening_decisions = decisions

                print(f"📋 ScreeningAgent Made: {len(decisions)} DECISIONS")
                print()

                included = [d for d in decisions if d.get("decision") == "include"]
                excluded = [d for d in decisions if d.get("decision") == "exclude"]

                print(f"  Included: {len(included)}")
                print(f"  Excluded: {len(excluded)}")
                print()

                if decisions:
                    print("SAMPLE DECISIONS (first 5):")
                    for i, decision in enumerate(decisions[:5], 1):
                        pmid = decision.get("pmid", "N/A")
                        dec = decision.get("decision", "N/A")
                        reason = decision.get("reason", "N/A")

                        print(f"\n  Decision {i}:")
                        print(f"    PMID: {pmid}")
                        print(f"    Result: {dec.upper()}")
                        print(f"    Reason: {reason[:150]}...")

                    print()
                    print(f"CRITICAL ISSUE: All {len(excluded)} studies were excluded!")
                    print(f"This means NO STUDIES passed screening.")

            elif agent_type == "credibility":
                # Extract credibility assessments
                assessments = output_data.get("assessments", [])
                credibility_assessments = assessments

                print(f"⭐ CredibilityAgent Assessed: {len(assessments)} STUDIES")
                print()

                if len(assessments) == 0:
                    print("  ❌ ZERO STUDIES REACHED CREDIBILITY ASSESSMENT")
                    print("  ❌ This means ALL studies were excluded during screening!")
                    print("  ❌ The meta-analysis is EMPTY")

            print()

        # Final Summary
        print("=" * 80)
        print("FINAL VERIFICATION SUMMARY")
        print("=" * 80)
        print()

        print(f"1. SearchAgent: Found {len(search_studies)} studies")
        if search_studies:
            pmid_count = sum(1 for s in search_studies if s.get('pmid'))
            print(f"   ✅ Studies with PMIDs: {pmid_count}/{len(search_studies)}")
            if pmid_count == len(search_studies):
                print(f"   ✅ DATA VERIFIED: All studies are REAL PubMed publications")
            else:
                print(f"   ⚠️  WARNING: Some studies may be simulated")
        else:
            print(f"   ❌ No studies found")

        print()
        print(f"2. ScreeningAgent: Made {len(screening_decisions)} decisions")
        included_count = sum(1 for d in screening_decisions if d.get('decision') == 'include')
        excluded_count = sum(1 for d in screening_decisions if d.get('decision') == 'exclude')
        print(f"   Included: {included_count}")
        print(f"   Excluded: {excluded_count}")

        if excluded_count == len(screening_decisions) and len(screening_decisions) > 0:
            print(f"   ❌ CRITICAL: ALL STUDIES EXCLUDED - Meta-analysis is EMPTY")
            print(f"   ❌ This is a MAJOR PROBLEM for the workflow")

        print()
        print(f"3. CredibilityAgent: Assessed {len(credibility_assessments)} studies")
        if len(credibility_assessments) == 0:
            print(f"   ❌ ZERO STUDIES - Nothing reached quality assessment")

        print()
        print("=" * 80)
        print("CONCLUSION:")
        print("=" * 80)

        if len(search_studies) > 0 and all(s.get('pmid') for s in search_studies):
            print("✅ DATA INTEGRITY: Studies are REAL PubMed publications")
            print("✅ NO SIMULATED DATA DETECTED")
        else:
            print("❌ DATA INTEGRITY ISSUE: Cannot verify all studies are real")

        print()

        if excluded_count == len(screening_decisions) and len(screening_decisions) > 0:
            print("❌ WORKFLOW ISSUE: All studies excluded during screening")
            print("❌ The screening criteria are TOO STRICT")
            print("❌ Need to review and fix screening logic")

        print()
        print("Full data saved to: agent_execution_data_raw.json")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(verify_real_studies())
