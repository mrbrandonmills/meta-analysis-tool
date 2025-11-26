#!/usr/bin/env python3
"""
Run a live meta-analysis on mindfulness meditation for anxiety.
"""
import asyncio
import httpx
import json

BASE_URL = "https://meta-analysis-tool-production.up.railway.app/api/v1"

async def run_meta_analysis():
    """Run complete meta-analysis workflow."""
    
    print("=" * 70)
    print("LIVE META-ANALYSIS: Mindfulness Meditation for Anxiety Reduction")
    print("=" * 70)
    print()
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        # Step 1: Create meta-analysis
        print("Step 1: Creating meta-analysis...")
        create_data = {
            "research_question": "What is the effectiveness of mindfulness meditation interventions for reducing anxiety in adults?",
            "topic": "Mindfulness Meditation for Anxiety Reduction",
            "databases": ["pubmed"],
            "peer_review_only": True,
            "inclusion_criteria": [
                "Randomized controlled trials (RCTs)",
                "Adult participants (18+ years)",
                "Mindfulness meditation intervention",
                "Anxiety as primary or secondary outcome",
                "Published in peer-reviewed journals",
                "English language"
            ],
            "exclusion_criteria": [
                "Non-randomized studies",
                "Children/adolescents only",
                "Other meditation types (not mindfulness-based)",
                "No anxiety outcomes reported",
                "Qualitative studies",
                "Case reports or series"
            ]
        }
        
        response = await client.post(f"{BASE_URL}/meta-analysis/create", json=create_data)
        
        if response.status_code != 200:
            print(f"❌ Failed to create: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
        
        result = response.json()
        analysis_id = result["id"]
        print(f"✅ Created successfully!")
        print(f"   ID: {analysis_id}")
        if "topic" in result:
            print(f"   Topic: {result['topic']}")
        print()
        
        # Step 2: Execute workflow
        print("Step 2: Starting workflow in background...")
        response = await client.post(f"{BASE_URL}/meta-analysis/execute/{analysis_id}")
        
        if response.status_code != 200:
            print(f"❌ Failed to start: {response.status_code}")
            return None
        
        exec_result = response.json()
        print(f"✅ Workflow started!")
        print(f"   Status: {exec_result['status']}")
        print()
        
        # Step 3: Poll for completion
        print("Step 3: Monitoring progress...")
        print("-" * 70)
        
        max_polls = 120  # 10 minutes max
        poll_count = 0
        
        while poll_count < max_polls:
            await asyncio.sleep(5)
            
            response = await client.get(f"{BASE_URL}/meta-analysis/status/{analysis_id}")
            if response.status_code != 200:
                print(f"   ❌ Failed to get status")
                return None
            
            status = response.json()
            current_status = status['status']
            progress = status.get('progress_percentage', 0)
            agents_done = status.get('agents_completed', 0)
            agents_total = status.get('agents_total', 3)
            
            # Show progress with agent details
            agent_progress = status.get('agent_progress', [])
            if agent_progress:
                latest_agent = agent_progress[-1]['agent_name']
                print(f"   [{poll_count * 5}s] {current_status.upper()}: {progress}% | {latest_agent} | {agents_done}/{agents_total} agents")
            else:
                print(f"   [{poll_count * 5}s] {current_status.upper()}: {progress}% | Initializing... | {agents_done}/{agents_total} agents")
            
            if current_status == "completed":
                print()
                print("=" * 70)
                print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
                print("=" * 70)
                print()
                return {"analysis_id": analysis_id, "status": status}
            elif current_status == "failed":
                print()
                print("❌ Workflow failed!")
                return None
            
            poll_count += 1
        
        print()
        print("⚠️  Timeout after 10 minutes")
        return None

if __name__ == "__main__":
    result = asyncio.run(run_meta_analysis())
    
    if result:
        print("Final Results:")
        print(json.dumps(result['status'], indent=2))
        print()
        print(f"Analysis ID: {result['analysis_id']}")
        
        # Save to file for PDF generation
        with open('meta_analysis_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print("✅ Results saved to meta_analysis_result.json")
    else:
        print("❌ Meta-analysis failed")
        exit(1)
