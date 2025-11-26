#!/usr/bin/env python3
"""Quick API test to verify meta-analysis endpoint."""
import requests
import json
import sys

BASE_URL = "https://meta-analysis-tool-production.up.railway.app/api/v1"

print("=" * 70)
print("QUICK META-ANALYSIS API TEST")
print("=" * 70)
print()

# Test 1: Create meta-analysis
print("Step 1: Creating meta-analysis...")
create_data = {
    "research_question": "What is the effectiveness of mindfulness meditation for anxiety?",
    "topic": "Mindfulness for Anxiety",
    "databases": ["pubmed"],
    "peer_review_only": True
}

try:
    response = requests.post(
        f"{BASE_URL}/meta-analysis/create", 
        json=create_data,
        timeout=30
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Created successfully!")
        print(f"   ID: {result['id']}")
        print(f"   Response: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Failed: {response.text}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("✅ API IS WORKING!")
print("=" * 70)
