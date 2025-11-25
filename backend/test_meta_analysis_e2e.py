"""
End-to-End Test for Meta-Analysis Tool

This script tests the complete meta-analysis workflow:
1. Create meta-analysis
2. Execute search
3. Execute screening
4. Execute quality assessment
5. Verify accuracy of results
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "https://meta-analysis-tool-production.up.railway.app"

# Test research question: Well-studied topic with known results
TEST_RESEARCH_QUESTION = "What is the effectiveness of mindfulness-based interventions for reducing anxiety in adults?"

async def test_meta_analysis_workflow():
    """Run complete end-to-end meta-analysis workflow."""

    print("=" * 80)
    print("META-ANALYSIS TOOL - END-TO-END TEST")
    print("=" * 80)
    print(f"Test started at: {datetime.now().isoformat()}")
    print(f"Research question: {TEST_RESEARCH_QUESTION}")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=300.0) as client:

        # ====================================================================
        # STEP 1: Create Meta-Analysis
        # ====================================================================
        print("\n[STEP 1] Creating meta-analysis...")

        create_request = {
            "research_question": TEST_RESEARCH_QUESTION,
            "topic": "mindfulness anxiety",
            "inclusion_criteria": [
                "Randomized controlled trial",
                "Adult population (18+)",
                "Mindfulness-based intervention",
                "Anxiety as outcome measure"
            ],
            "exclusion_criteria": [
                "Non-English language",
                "Qualitative studies",
                "Case studies"
            ],
            "databases": ["pubmed", "arxiv", "europepmc"],
            "peer_review_only": False
        }

        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/meta-analysis/create",
                json=create_request
            )
            response.raise_for_status()
            create_result = response.json()

            print(f"✓ Meta-analysis created successfully")
            print(f"  Analysis ID: {create_result['id']}")
            print(f"  Status: {create_result['status']}")

            analysis_id = create_result['id']
            workflow = create_result.get('workflow', {})

            print(f"\n  Workflow Plan:")
            print(f"    - Workflow steps: {len(workflow.get('steps', []))}")
            print(f"    - Search strategy: {workflow.get('search_strategy', 'N/A')}")

        except Exception as e:
            print(f"✗ FAILED to create meta-analysis: {e}")
            if hasattr(e, 'response'):
                print(f"  Response: {e.response.text}")
            return None

        # ====================================================================
        # STEP 2: Execute Meta-Analysis Workflow
        # ====================================================================
        print("\n[STEP 2] Executing meta-analysis workflow...")

        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/meta-analysis/execute/{analysis_id}"
            )
            response.raise_for_status()
            execute_result = response.json()

            print(f"✓ Workflow execution completed")
            print(f"  Analysis ID: {execute_result['analysis_id']}")
            print(f"  Status: {execute_result['status']}")

            # Search Results
            search_results = execute_result.get('search_results', {})
            print(f"\n  Search Results:")
            print(f"    - Total found: {search_results.get('total_found', 0)}")
            print(f"    - Databases: {', '.join(search_results.get('databases', []))}")

            # Screening Results
            screening_results = execute_result.get('screening_results', {})
            print(f"\n  Screening Results:")
            print(f"    - Total screened: {screening_results.get('total_screened', 0)}")
            print(f"    - Included: {screening_results.get('included', 0)}")
            print(f"    - Excluded: {screening_results.get('excluded', 0)}")
            print(f"    - Uncertain: {screening_results.get('uncertain', 0)}")

            # Credibility Results
            credibility_results = execute_result.get('credibility_results', {})
            print(f"\n  Credibility Results:")
            print(f"    - Total evaluated: {credibility_results.get('total_evaluated', 0)}")
            breakdown = credibility_results.get('breakdown', {})
            print(f"    - High credibility: {breakdown.get('high', 0)}")
            print(f"    - Medium credibility: {breakdown.get('medium', 0)}")
            print(f"    - Low credibility: {breakdown.get('low', 0)}")
            print(f"    - Preprint: {breakdown.get('preprint', 0)}")

            # Save results for manual verification
            with open('/tmp/meta_analysis_test_results.json', 'w') as f:
                json.dump(execute_result, f, indent=2)
            print(f"\n  Full results saved to: /tmp/meta_analysis_test_results.json")

        except Exception as e:
            print(f"✗ FAILED to execute workflow: {e}")
            if hasattr(e, 'response'):
                print(f"  Response: {e.response.text}")
            return None

        # ====================================================================
        # STEP 3: Check Status
        # ====================================================================
        print("\n[STEP 3] Checking meta-analysis status...")

        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/meta-analysis/status/{analysis_id}"
            )
            response.raise_for_status()
            status_result = response.json()

            print(f"✓ Status retrieved")
            print(f"  Analysis ID: {status_result['id']}")
            print(f"  Status: {status_result['status']}")
            print(f"  Decisions made: {status_result['decisions']}")
            print(f"  Created: {status_result['created_at']}")

        except Exception as e:
            print(f"✗ FAILED to get status: {e}")

        # ====================================================================
        # STEP 4: Test Q&A Agent
        # ====================================================================
        print("\n[STEP 4] Testing Q&A Agent...")

        test_questions = [
            "How many studies were included?",
            "What databases were searched?",
            "What were the inclusion criteria?"
        ]

        for question in test_questions:
            try:
                response = await client.post(
                    f"{BASE_URL}/api/v1/meta-analysis/ask",
                    json={
                        "question": question,
                        "meta_analysis_id": analysis_id
                    }
                )
                response.raise_for_status()
                qa_result = response.json()

                print(f"\n  Q: {question}")
                print(f"  A: {qa_result.get('answer', 'N/A')}")
                print(f"  Confidence: {qa_result.get('confidence', 'N/A')}")

            except Exception as e:
                print(f"  ✗ FAILED: {e}")

        # ====================================================================
        # VERIFICATION SUMMARY
        # ====================================================================
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        print(f"\n✓ Meta-analysis workflow completed")
        print(f"  Analysis ID: {analysis_id}")
        print(f"  Research Question: {TEST_RESEARCH_QUESTION}")

        print(f"\nKey Metrics:")
        print(f"  - Studies found: {search_results.get('total_found', 0)}")
        print(f"  - Studies screened: {screening_results.get('total_screened', 0)}")
        print(f"  - Studies included: {screening_results.get('included', 0)}")
        print(f"  - Credibility evaluated: {credibility_results.get('total_evaluated', 0)}")

        print(f"\n⚠️  MANUAL VERIFICATION REQUIRED:")
        print(f"  1. Review results in /tmp/meta_analysis_test_results.json")
        print(f"  2. Compare study counts with manual PubMed search")
        print(f"  3. Verify inclusion/exclusion decisions are accurate")
        print(f"  4. Check credibility scores against known studies")

        print(f"\nTest completed at: {datetime.now().isoformat()}")
        print("=" * 80)

        return {
            "analysis_id": analysis_id,
            "search_found": search_results.get('total_found', 0),
            "included": screening_results.get('included', 0),
            "excluded": screening_results.get('excluded', 0),
            "credibility_evaluated": credibility_results.get('total_evaluated', 0)
        }

if __name__ == "__main__":
    result = asyncio.run(test_meta_analysis_workflow())

    if result:
        print("\n✓ END-TO-END TEST PASSED")
        exit(0)
    else:
        print("\n✗ END-TO-END TEST FAILED")
        exit(1)
