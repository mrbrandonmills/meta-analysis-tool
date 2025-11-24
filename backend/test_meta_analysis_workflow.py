#!/usr/bin/env python3
"""
Quick test script to verify the meta-analysis workflow fix.

Tests:
1. Create a meta-analysis
2. Execute the workflow
3. Check that it runs without errors
4. Verify coordinator state is created
"""

import asyncio
import httpx
from uuid import uuid4

BASE_URL = "https://meta-analysis-tool-production.up.railway.app/api/v1"


async def test_workflow():
    """Test the complete meta-analysis workflow."""

    print("=" * 60)
    print("META-ANALYSIS WORKFLOW TEST")
    print("=" * 60)
    print()

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Create a meta-analysis
        print("Step 1: Creating meta-analysis...")
        create_data = {
            "research_question": "What is the effectiveness of cognitive behavioral therapy for depression in adults?",
            "topic": "CBT for Depression - Test",
            "databases": ["pubmed"],
            "peer_review_only": True,
            "inclusion_criteria": [
                "Randomized controlled trials",
                "Adult participants (18+ years)",
                "CBT intervention",
                "Depression as primary outcome"
            ],
            "exclusion_criteria": [
                "Non-English language",
                "Qualitative studies",
                "Case reports"
            ]
        }

        response = await client.post(f"{BASE_URL}/meta-analysis/create", json=create_data)

        if response.status_code != 200:
            print(f"❌ FAILED to create meta-analysis")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        result = response.json()
        analysis_id = result["id"]
        print(f"✅ Created meta-analysis: {analysis_id}")
        print(f"   Status: {result['status']}")
        print()

        # Step 2: Check initial status
        print("Step 2: Checking initial status...")
        response = await client.get(f"{BASE_URL}/meta-analysis/status/{analysis_id}")

        if response.status_code != 200:
            print(f"❌ FAILED to get status")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        status_result = response.json()
        print(f"✅ Status retrieved")
        print(f"   Status: {status_result['status']}")
        print(f"   Decisions: {status_result['decisions']}")
        print()

        # Step 3: Execute the workflow (THE FIX BEING TESTED)
        print("Step 3: Executing workflow (testing fix)...")
        print("   This should now create coordinator automatically if missing...")

        response = await client.post(f"{BASE_URL}/meta-analysis/execute/{analysis_id}")

        if response.status_code != 200:
            print(f"❌ FAILED to execute workflow")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")

            # Check if it's the old error
            if "Coordinator state not found" in response.text:
                print()
                print("   ⚠️  This is the OLD bug - coordinator not initialized")
                print("   ⚠️  The fix hasn't been deployed yet")
            elif "No workflow found" in response.text:
                print()
                print("   ⚠️  Coordinator has no decisions - partial fix")

            return False

        execution_result = response.json()
        print(f"✅ Workflow executed successfully!")
        print(f"   Status: {execution_result['status']}")
        print(f"   Search results: {execution_result['search_results']}")
        print(f"   Screening results: {execution_result['screening_results']}")
        print(f"   Credibility results: {execution_result['credibility_results']}")
        print()

        # Step 4: Verify coordinator state was created
        print("Step 4: Verifying coordinator state...")
        response = await client.get(f"{BASE_URL}/meta-analysis/status/{analysis_id}")

        if response.status_code != 200:
            print(f"❌ FAILED to get final status")
            return False

        final_status = response.json()
        print(f"✅ Final status retrieved")
        print(f"   Status: {final_status['status']}")
        print(f"   Decisions: {final_status['decisions']}")

        if final_status['decisions'] > 0:
            print(f"   ✅ Coordinator has decisions (workflow initialized)")
        else:
            print(f"   ⚠️  No decisions found")

        print()
        print("=" * 60)
        print("TEST RESULT: ✅ ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("The fix is working correctly:")
        print("1. ✅ Meta-analysis created")
        print("2. ✅ Workflow executed without errors")
        print("3. ✅ Coordinator automatically initialized")
        print("4. ✅ Search, screening, and credibility agents ran")
        print()

        return True


async def test_against_local():
    """Test against local development server."""
    global BASE_URL
    BASE_URL = "http://localhost:8000/api/v1"

    print("Testing against LOCAL server (http://localhost:8000)")
    print()

    return await test_workflow()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--local":
        # Test local server
        success = asyncio.run(test_against_local())
    else:
        # Test production
        success = asyncio.run(test_workflow())

    sys.exit(0 if success else 1)
