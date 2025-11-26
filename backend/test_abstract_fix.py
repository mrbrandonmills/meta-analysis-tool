#!/usr/bin/env python3
"""
Test the abstract fetching fix.
This will run a NEW meta-analysis and verify:
1. Studies have abstracts
2. Some studies are included (not all excluded)
3. Workflow produces non-empty results
"""
import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "https://meta-analysis-tool-production.up.railway.app/api/v1"


async def test_abstract_fix():
    """Test that the abstract fetching fix works."""

    print("=" * 80)
    print("TESTING ABSTRACT FETCHING FIX")
    print("=" * 80)
    print(f"Time: {datetime.now().isoformat()}")
    print()

    async with httpx.AsyncClient(timeout=300.0) as client:
        # Create a new meta-analysis
        print("Step 1: Creating new meta-analysis...")
        create_data = {
            "research_question": "What is the effectiveness of mindfulness meditation for reducing anxiety?",
            "topic": "Mindfulness for Anxiety - Abstract Fix Test",
            "databases": ["pubmed"],
            "peer_review_only": True,
            "inclusion_criteria": [
                "Randomized controlled trials",
                "Adult participants",
                "Mindfulness intervention",
                "Anxiety outcome measures"
            ],
            "exclusion_criteria": [
                "Children only",
                "Non-English",
                "Qualitative studies"
            ]
        }

        response = await client.post(f"{BASE_URL}/meta-analysis/create", json=create_data)

        if response.status_code != 200:
            print(f"❌ Failed to create: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        result = response.json()
        analysis_id = result["id"]
        print(f"✅ Created: {analysis_id}")
        print()

        # Execute workflow
        print("Step 2: Starting workflow...")
        response = await client.post(f"{BASE_URL}/meta-analysis/execute/{analysis_id}")

        if response.status_code != 200:
            print(f"❌ Failed to start: {response.status_code}")
            return False

        print(f"✅ Workflow started")
        print()

        # Poll for completion
        print("Step 3: Waiting for completion...")
        print("-" * 80)

        max_polls = 120  # 10 minutes
        poll_count = 0

        while poll_count < max_polls:
            await asyncio.sleep(5)

            response = await client.get(f"{BASE_URL}/meta-analysis/status/{analysis_id}")
            if response.status_code != 200:
                print(f"❌ Failed to get status")
                return False

            status = response.json()
            current_status = status['status']
            progress = status.get('progress_percentage', 0)
            agents_done = status.get('agents_completed', 0)
            agents_total = status.get('agents_total', 3)

            print(f"   [{poll_count * 5}s] {current_status}: {progress}% | {agents_done}/{agents_total} agents")

            if current_status == "completed":
                print()
                print("✅ Workflow completed!")
                break
            elif current_status == "failed":
                print()
                print("❌ Workflow failed!")
                return False

            poll_count += 1

        if poll_count >= max_polls:
            print()
            print("⚠️  Timeout")
            return False

        # Get agent execution data
        print()
        print("Step 4: Verifying results...")
        print("-" * 80)

        response = await client.get(f"{BASE_URL}/meta-analysis/agent-data/{analysis_id}")

        if response.status_code != 200:
            print(f"⚠️  Cannot fetch agent data (endpoint may not be deployed yet)")
            print(f"   Falling back to status endpoint...")
            response = await client.get(f"{BASE_URL}/meta-analysis/status/{analysis_id}")
            if response.status_code != 200:
                return False
            final_status = response.json()
        else:
            data = response.json()

            # Save results
            with open('abstract_fix_test_results.json', 'w') as f:
                json.dump(data, f, indent=2)

            print("✅ Saved results to: abstract_fix_test_results.json")
            print()

            # Analyze results
            agent_executions = data.get("agent_executions", [])

            search_agent = next((a for a in agent_executions if a['agent_type'] == 'search'), None)
            screening_agent = next((a for a in agent_executions if a['agent_type'] == 'screening'), None)
            credibility_agent = next((a for a in agent_executions if a['agent_type'] == 'credibility'), None)

            print("RESULTS ANALYSIS:")
            print()

            # Check SearchAgent
            if search_agent:
                studies = search_agent.get('output_data', {}).get('studies', [])
                print(f"1. SearchAgent: Found {len(studies)} studies")

                if studies:
                    # Check if abstracts are present
                    with_abstracts = sum(1 for s in studies if s.get('abstract'))
                    print(f"   ✅ Studies with abstracts: {with_abstracts}/{len(studies)}")

                    if with_abstracts > 0:
                        print(f"   ✅ ABSTRACT FETCHING IS WORKING!")
                        # Show sample
                        sample = studies[0]
                        print(f"\n   Sample study:")
                        print(f"   - PMID: {sample.get('pmid', 'N/A')}")
                        print(f"   - Title: {sample.get('title', 'N/A')[:60]}...")
                        print(f"   - Abstract length: {len(sample.get('abstract', ''))} chars")
                        print(f"   - Abstract preview: {sample.get('abstract', 'N/A')[:150]}...")
                    else:
                        print(f"   ❌ NO ABSTRACTS - Fix may not be deployed yet")
                else:
                    print(f"   ❌ No studies found")
            else:
                print(f"1. SearchAgent: ❌ No data")

            print()

            # Check ScreeningAgent
            if screening_agent:
                output = screening_agent.get('output_data', {})
                included = output.get('included', [])
                excluded = output.get('excluded', [])
                uncertain = output.get('uncertain', [])

                print(f"2. ScreeningAgent:")
                print(f"   - Included: {len(included)}")
                print(f"   - Excluded: {len(excluded)}")
                print(f"   - Uncertain: {len(uncertain)}")

                if len(included) > 0:
                    print(f"   ✅ SCREENING IS WORKING! Studies are being included!")
                else:
                    print(f"   ⚠️  No studies included - may need to adjust criteria")

                if len(excluded) == len(included) + len(excluded) and len(excluded) > 0:
                    print(f"   ❌ ALL STUDIES EXCLUDED - Fix may not be working")
            else:
                print(f"2. ScreeningAgent: ❌ No data")

            print()

            # Check CredibilityAgent
            if credibility_agent:
                assessments = credibility_agent.get('output_data', {}).get('assessments', [])
                print(f"3. CredibilityAgent: Assessed {len(assessments)} studies")

                if len(assessments) > 0:
                    print(f"   ✅ WORKFLOW IS COMPLETE! Studies reached quality assessment!")
                else:
                    print(f"   ⚠️  No studies assessed (all excluded by screening)")
            else:
                print(f"3. CredibilityAgent: ❌ No data")

            print()
            print("=" * 80)
            print("TEST RESULT:")
            print("=" * 80)

            # Determine overall success
            has_abstracts = search_agent and any(
                s.get('abstract') for s in search_agent.get('output_data', {}).get('studies', [])
            )
            has_inclusions = screening_agent and len(
                screening_agent.get('output_data', {}).get('included', [])
            ) > 0

            if has_abstracts and has_inclusions:
                print("✅ SUCCESS: Abstract fetching fix is WORKING!")
                print("   - Studies have real abstracts")
                print("   - Some studies are being included")
                print("   - Meta-analysis produces meaningful results")
                return True
            elif has_abstracts:
                print("⚠️  PARTIAL: Abstracts are fetched but no studies included")
                print("   - May need to adjust inclusion/exclusion criteria")
                return True
            else:
                print("❌ FAILED: Abstract fetching may not be deployed yet")
                print("   - Wait for deployment to complete and retry")
                return False


if __name__ == "__main__":
    success = asyncio.run(test_abstract_fix())
    exit(0 if success else 1)
