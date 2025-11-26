#!/usr/bin/env python3
"""Quick check of the abstract fix results."""
import httpx
import json

analysis_id = "bf35f7e9-51eb-4c39-badb-14ffb74ebd2a"
url = f"https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/agent-data/{analysis_id}"

response = httpx.get(url, timeout=30.0)
data = response.json()

print("=" * 80)
print("ABSTRACT FIX VERIFICATION RESULTS")
print("=" * 80)
print()

agents = data.get('agent_executions', [])

for agent in agents:
    agent_type = agent['agent_type']
    output_data = agent.get('output_data', {})

    print(f"{agent_type.upper()}:")
    print("-" * 80)

    if agent_type == 'search':
        studies = output_data.get('studies', [])
        print(f"Found: {len(studies)} studies")
        if studies:
            with_abstracts = sum(1 for s in studies if s.get('abstract'))
            print(f"With abstracts: {with_abstracts}/{len(studies)}")

            if with_abstracts > 0:
                print("\n✅ ABSTRACT FETCHING IS WORKING!")
                sample = studies[0]
                print(f"\nSample study:")
                print(f"  PMID: {sample.get('pmid', 'N/A')}")
                print(f"  Title: {sample.get('title', 'N/A')[:70]}...")
                abstract = sample.get('abstract', '')
                print(f"  Abstract length: {len(abstract)} chars")
                if abstract:
                    print(f"  Abstract preview: {abstract[:200]}...")
            else:
                print("\n❌ NO ABSTRACTS - Fix not working")

    elif agent_type == 'screening':
        included = output_data.get('included', [])
        excluded = output_data.get('excluded', [])
        uncertain = output_data.get('uncertain', [])

        print(f"Included: {len(included)}")
        print(f"Excluded: {len(excluded)}")
        print(f"Uncertain: {len(uncertain)}")

        if len(included) > 0:
            print("\n✅ SUCCESS! Studies are being INCLUDED!")
            sample = included[0]
            print(f"\nSample included study:")
            print(f"  PMID: {sample.get('pmid', 'N/A')}")
            print(f"  Title: {sample.get('title', 'N/A')[:70]}...")
            result = sample.get('screening_result', {})
            print(f"  Reasoning: {result.get('reasoning', 'N/A')[:150]}...")
        else:
            print("\n⚠️  All studies excluded")

    elif agent_type == 'credibility':
        assessments = output_data.get('assessments', [])
        print(f"Assessed: {len(assessments)} studies")

        if len(assessments) > 0:
            print("\n✅ Studies reached quality assessment!")
            sample = assessments[0]
            print(f"\nSample assessment:")
            print(f"  PMID: {sample.get('pmid', 'N/A')}")
            print(f"  Score: {sample.get('score', 'N/A')}/10")
            print(f"  Quality: {sample.get('quality_rating', 'N/A')}")

    print()

# Save full data
with open('fix_verification_results.json', 'w') as f:
    json.dump(data, f, indent=2)

print("=" * 80)
print("Full data saved to: fix_verification_results.json")
print("=" * 80)
