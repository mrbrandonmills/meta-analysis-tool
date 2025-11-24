# Comprehensive Testing Strategy & Execution Plan
**Date:** November 22, 2025
**Platform:** Meta-Analysis Research Platform v1.0
**Production URL:** https://meta-analysis-tool-production.up.railway.app

---

## EXECUTIVE SUMMARY

This document outlines a complete testing strategy for validating:
1. Medium-style peer review membership area (10 mock researchers)
2. Editor role with AI researcher matching system
3. Five complete meta-analysis test runs

**Estimated Time:** 4-6 hours total
**Prerequisites:** Production system running, database accessible
**Expected Outcomes:** Full system validation with documented results

---

## 1. TEST ENVIRONMENT SETUP

### 1.1 Test Data Requirements

```json
{
  "mock_researchers": 10,
  "mock_editors": 2,
  "test_manuscripts": 5,
  "test_papers": 50,
  "meta_analysis_runs": 5
}
```

### 1.2 API Base URLs

```bash
# Production
BACKEND_URL="https://meta-analysis-tool-production.up.railway.app"
FRONTEND_URL="https://meta-analysis-tool.vercel.app"

# API Endpoints
AUTH_URL="${BACKEND_URL}/api/v1/auth"
RESEARCHER_URL="${BACKEND_URL}/api/v1/researchers"
REVIEWER_MATCHER_URL="${BACKEND_URL}/api/v1/reviewer-matcher"
PEER_REVIEW_URL="${BACKEND_URL}/api/v1/peer-reviews"
META_ANALYSIS_URL="${BACKEND_URL}/api/v1/meta-analysis"
MANUSCRIPT_URL="${BACKEND_URL}/api/v1/manuscripts"
```

---

## 2. PHASE 1: MOCK RESEARCHER SETUP (10 Users)

### 2.1 Researcher Profiles

Create 10 diverse researcher profiles to test the full spectrum of qualifications:

#### **Tier 1: Expert Researchers (3 users)**
```json
{
  "researchers": [
    {
      "id": "expert_1",
      "email": "dr.sarah.chen@stanford.edu",
      "password": "SecurePass123!",
      "profile": {
        "full_name": "Dr. Sarah Chen",
        "institution": "Stanford University",
        "department": "Psychology",
        "position": "Associate Professor",
        "country": "United States",
        "orcid": "0000-0001-1234-5678",
        "google_scholar": "https://scholar.google.com/citations?user=EXAMPLE1",
        "h_index": 28,
        "total_citations": 3400,
        "expertise_domains": ["Psychology", "Neuroscience"],
        "expertise_keywords": [
          "cognitive psychology",
          "fMRI",
          "neural networks",
          "decision making",
          "attention",
          "working memory"
        ],
        "methodologies": ["Meta-analysis", "fMRI", "RCT", "Systematic Review"],
        "review_experience": "50+",
        "journals_reviewed": [
          "Nature Neuroscience",
          "Psychological Science",
          "Journal of Neuroscience"
        ],
        "max_concurrent_reviews": 4,
        "preferred_timeframe": 14,
        "languages": ["English", "Chinese"],
        "current_capacity": "Available"
      }
    },
    {
      "id": "expert_2",
      "email": "prof.james.wilson@mit.edu",
      "password": "SecurePass123!",
      "profile": {
        "full_name": "Prof. James Wilson",
        "institution": "MIT",
        "department": "Computer Science",
        "position": "Full Professor",
        "country": "United States",
        "orcid": "0000-0002-2345-6789",
        "google_scholar": "https://scholar.google.com/citations?user=EXAMPLE2",
        "h_index": 42,
        "total_citations": 8200,
        "expertise_domains": ["Computer Science", "Engineering"],
        "expertise_keywords": [
          "machine learning",
          "deep learning",
          "artificial intelligence",
          "neural networks",
          "computer vision"
        ],
        "methodologies": ["Experimental Design", "Statistical Analysis", "Meta-analysis"],
        "review_experience": "50+",
        "journals_reviewed": [
          "IEEE Transactions on Pattern Analysis",
          "NeurIPS",
          "ICML"
        ],
        "max_concurrent_reviews": 5,
        "preferred_timeframe": 21,
        "languages": ["English"],
        "current_capacity": "Available"
      }
    },
    {
      "id": "expert_3",
      "email": "dr.maria.garcia@oxford.ac.uk",
      "password": "SecurePass123!",
      "profile": {
        "full_name": "Dr. Maria Garcia",
        "institution": "University of Oxford",
        "department": "Medicine",
        "position": "Senior Research Fellow",
        "country": "United Kingdom",
        "orcid": "0000-0003-3456-7890",
        "google_scholar": "https://scholar.google.com/citations?user=EXAMPLE3",
        "h_index": 35,
        "total_citations": 5600,
        "expertise_domains": ["Medicine", "Biology"],
        "expertise_keywords": [
          "clinical trials",
          "cardiology",
          "evidence-based medicine",
          "systematic reviews",
          "meta-analysis"
        ],
        "methodologies": ["RCT", "Meta-analysis", "Systematic Review", "Cohort Study"],
        "review_experience": "21-50",
        "journals_reviewed": [
          "The Lancet",
          "JAMA",
          "BMJ"
        ],
        "max_concurrent_reviews": 3,
        "preferred_timeframe": 14,
        "languages": ["English", "Spanish"],
        "current_capacity": "Available"
      }
    }
  ]
}
```

#### **Tier 2: Mid-Level Researchers (4 users)**
```json
{
  "researchers": [
    {
      "id": "mid_1",
      "email": "dr.ahmed.hassan@toronto.ca",
      "password": "SecurePass123!",
      "profile": {
        "full_name": "Dr. Ahmed Hassan",
        "institution": "University of Toronto",
        "department": "Social Sciences",
        "position": "Assistant Professor",
        "country": "Canada",
        "orcid": "0000-0004-4567-8901",
        "h_index": 12,
        "total_citations": 680,
        "expertise_domains": ["Social Sciences", "Psychology"],
        "expertise_keywords": [
          "social psychology",
          "group dynamics",
          "behavioral research",
          "survey methods"
        ],
        "methodologies": ["Survey Research", "Meta-analysis", "Cross-sectional Study"],
        "review_experience": "11-20",
        "max_concurrent_reviews": 3,
        "preferred_timeframe": 14,
        "languages": ["English", "Arabic"],
        "current_capacity": "Available"
      }
    },
    {
      "id": "mid_2",
      "email": "dr.lisa.brown@unimelb.edu.au",
      "password": "SecurePass123!",
      "profile": {
        "full_name": "Dr. Lisa Brown",
        "institution": "University of Melbourne",
        "department": "Education",
        "position": "Lecturer",
        "country": "Australia",
        "orcid": "0000-0005-5678-9012",
        "h_index": 9,
        "total_citations": 420,
        "expertise_domains": ["Education", "Psychology"],
        "expertise_keywords": [
          "educational psychology",
          "learning outcomes",
          "pedagogy",
          "student engagement"
        ],
        "methodologies": ["Mixed Methods", "Qualitative Research", "Meta-analysis"],
        "review_experience": "6-10",
        "max_concurrent_reviews": 2,
        "preferred_timeframe": 21,
        "languages": ["English"],
        "current_capacity": "Limited availability"
      }
    },
    {
      "id": "mid_3",
      "email": "dr.pierre.dupont@sorbonne.fr",
      "password": "SecurePass123!",
      "profile": {
        "full_name": "Dr. Pierre Dupont",
        "institution": "Sorbonne University",
        "department": "Chemistry",
        "position": "Associate Researcher",
        "country": "France",
        "orcid": "0000-0006-6789-0123",
        "h_index": 14,
        "total_citations": 920,
        "expertise_domains": ["Chemistry", "Physics"],
        "expertise_keywords": [
          "organic chemistry",
          "spectroscopy",
          "synthesis",
          "materials science"
        ],
        "methodologies": ["Experimental Design", "Statistical Analysis"],
        "review_experience": "11-20",
        "max_concurrent_reviews": 3,
        "preferred_timeframe": 14,
        "languages": ["French", "English"],
        "current_capacity": "Available"
      }
    },
    {
      "id": "mid_4",
      "email": "dr.yuki.tanaka@tokyo.ac.jp",
      "password": "SecurePass123!",
      "profile": {
        "full_name": "Dr. Yuki Tanaka",
        "institution": "University of Tokyo",
        "department": "Engineering",
        "position": "Associate Professor",
        "country": "Japan",
        "orcid": "0000-0007-7890-1234",
        "h_index": 16,
        "total_citations": 1100,
        "expertise_domains": ["Engineering", "Computer Science"],
        "expertise_keywords": [
          "robotics",
          "automation",
          "control systems",
          "mechatronics"
        ],
        "methodologies": ["Experimental Design", "Simulation", "Meta-analysis"],
        "review_experience": "11-20",
        "max_concurrent_reviews": 3,
        "preferred_timeframe": 14,
        "languages": ["Japanese", "English"],
        "current_capacity": "Available"
      }
    }
  ]
}
```

#### **Tier 3: Early-Career Researchers (3 users)**
```json
{
  "researchers": [
    {
      "id": "early_1",
      "email": "dr.emma.johnson@ucl.ac.uk",
      "password": "SecurePass123!",
      "profile": {
        "full_name": "Dr. Emma Johnson",
        "institution": "University College London",
        "department": "Biology",
        "position": "Postdoctoral Researcher",
        "country": "United Kingdom",
        "orcid": "0000-0008-8901-2345",
        "h_index": 5,
        "total_citations": 180,
        "expertise_domains": ["Biology"],
        "expertise_keywords": [
          "molecular biology",
          "genetics",
          "cell culture",
          "PCR"
        ],
        "methodologies": ["Experimental Design", "Statistical Analysis"],
        "review_experience": "1-5",
        "max_concurrent_reviews": 2,
        "preferred_timeframe": 21,
        "languages": ["English"],
        "current_capacity": "Available"
      }
    },
    {
      "id": "early_2",
      "email": "dr.carlos.rodriguez@unam.mx",
      "password": "SecurePass123!",
      "profile": {
        "full_name": "Dr. Carlos Rodriguez",
        "institution": "UNAM",
        "department": "Physics",
        "position": "Junior Researcher",
        "country": "Mexico",
        "orcid": "0000-0009-9012-3456",
        "h_index": 4,
        "total_citations": 120,
        "expertise_domains": ["Physics"],
        "expertise_keywords": [
          "quantum mechanics",
          "condensed matter",
          "spectroscopy"
        ],
        "methodologies": ["Experimental Design", "Statistical Analysis"],
        "review_experience": "1-5",
        "max_concurrent_reviews": 1,
        "preferred_timeframe": 30,
        "languages": ["Spanish", "English"],
        "current_capacity": "Limited availability"
      }
    },
    {
      "id": "early_3",
      "email": "dr.priya.sharma@iitd.ac.in",
      "password": "SecurePass123!",
      "profile": {
        "full_name": "Dr. Priya Sharma",
        "institution": "IIT Delhi",
        "department": "Computer Science",
        "position": "Assistant Professor",
        "country": "India",
        "orcid": "0000-0010-0123-4567",
        "h_index": 6,
        "total_citations": 240,
        "expertise_domains": ["Computer Science"],
        "expertise_keywords": [
          "data mining",
          "big data",
          "databases",
          "algorithms"
        ],
        "methodologies": ["Experimental Design", "Statistical Analysis"],
        "review_experience": "6-10",
        "max_concurrent_reviews": 2,
        "preferred_timeframe": 14,
        "languages": ["English", "Hindi"],
        "current_capacity": "Available"
      }
    }
  ]
}
```

### 2.2 Mock Researcher Creation Script

Save this as `scripts/create_mock_researchers.py`:

```python
#!/usr/bin/env python3
"""
Create 10 mock researchers for testing the peer review system.
"""
import requests
import json
import time
from typing import Dict, List

BASE_URL = "https://meta-analysis-tool-production.up.railway.app"

def register_researcher(researcher_data: Dict) -> Dict:
    """Register a new researcher."""
    url = f"{BASE_URL}/api/v1/auth/register"

    payload = {
        "email": researcher_data["email"],
        "password": researcher_data["password"],
        "full_name": researcher_data["profile"]["full_name"],
        "institution": researcher_data["profile"]["institution"]
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()

def complete_researcher_profile(access_token: str, researcher_data: Dict) -> Dict:
    """Complete the researcher profile with all fields."""
    url = f"{BASE_URL}/api/v1/researchers/me"

    headers = {"Authorization": f"Bearer {access_token}"}
    payload = researcher_data["profile"]

    response = requests.put(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def subscribe_researcher(access_token: str) -> Dict:
    """Subscribe researcher to premium ($100/month)."""
    url = f"{BASE_URL}/api/v1/subscriptions/create"

    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "payment_method_id": "pm_test_card",  # Test Stripe token
        "billing_email": "test@example.com"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def create_all_researchers(researchers: List[Dict]) -> List[Dict]:
    """Create all mock researchers."""
    results = []

    for researcher in researchers:
        try:
            print(f"Creating researcher: {researcher['profile']['full_name']}...")

            # 1. Register
            auth_response = register_researcher(researcher)
            access_token = auth_response["access_token"]
            user_id = auth_response["user_id"]

            # 2. Complete profile
            profile_response = complete_researcher_profile(access_token, researcher)

            # 3. Subscribe (makes them a reviewer)
            subscription_response = subscribe_researcher(access_token)

            results.append({
                "id": researcher["id"],
                "user_id": user_id,
                "email": researcher["email"],
                "access_token": access_token,
                "profile": profile_response,
                "subscription": subscription_response
            })

            print(f"✓ Created: {researcher['profile']['full_name']}")
            time.sleep(1)  # Rate limiting

        except Exception as e:
            print(f"✗ Failed to create {researcher['profile']['full_name']}: {e}")
            continue

    return results

# Main execution
if __name__ == "__main__":
    # Load researcher data from JSON files
    with open("test_data/expert_researchers.json") as f:
        experts = json.load(f)["researchers"]

    with open("test_data/mid_level_researchers.json") as f:
        mid_level = json.load(f)["researchers"]

    with open("test_data/early_career_researchers.json") as f:
        early_career = json.load(f)["researchers"]

    all_researchers = experts + mid_level + early_career

    print(f"Creating {len(all_researchers)} mock researchers...")
    results = create_all_researchers(all_researchers)

    # Save results
    with open("test_results/mock_researchers_created.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Created {len(results)} researchers successfully")
    print(f"Results saved to: test_results/mock_researchers_created.json")
```

---

## 3. PHASE 2: TEST EDITOR ROLE & AI MATCHING

### 3.1 Create Mock Editors (2 users)

```json
{
  "editors": [
    {
      "id": "editor_1",
      "email": "chief.editor@journal.org",
      "password": "SecurePass123!",
      "profile": {
        "full_name": "Dr. Robert Chen",
        "institution": "Harvard Medical School",
        "position": "Chief Editor",
        "h_index": 45,
        "editorial_experience": "15 years"
      }
    },
    {
      "id": "editor_2",
      "email": "associate.editor@journal.org",
      "password": "SecurePass123!",
      "profile": {
        "full_name": "Dr. Jennifer Park",
        "institution": "Johns Hopkins University",
        "position": "Associate Editor",
        "h_index": 32,
        "editorial_experience": "8 years"
      }
    }
  ]
}
```

### 3.2 Test Manuscript Submissions

Create 5 test manuscripts covering different research domains:

```json
{
  "manuscripts": [
    {
      "id": "ms_001",
      "title": "Machine Learning Approaches for Predicting Cognitive Decline",
      "abstract": "This systematic review examines machine learning algorithms for predicting cognitive decline in aging populations...",
      "keywords": ["machine learning", "cognitive psychology", "neural networks", "aging"],
      "research_domain": "Psychology",
      "required_expertise": {
        "domains": ["Psychology", "Computer Science"],
        "keywords": ["machine learning", "cognitive psychology", "neural networks"],
        "min_h_index": 10,
        "min_reviews": 5
      },
      "expected_matches": ["expert_1", "expert_2", "mid_1"]
    },
    {
      "id": "ms_002",
      "title": "Meta-Analysis of Cardiovascular Outcomes in Clinical Trials",
      "abstract": "We conducted a comprehensive meta-analysis of randomized controlled trials examining cardiovascular outcomes...",
      "keywords": ["cardiology", "clinical trials", "meta-analysis", "RCT"],
      "research_domain": "Medicine",
      "required_expertise": {
        "domains": ["Medicine"],
        "keywords": ["cardiology", "clinical trials", "meta-analysis"],
        "min_h_index": 15,
        "min_reviews": 10
      },
      "expected_matches": ["expert_3"]
    },
    {
      "id": "ms_003",
      "title": "Deep Learning for Computer Vision: A Systematic Review",
      "abstract": "This paper reviews deep learning architectures for computer vision tasks...",
      "keywords": ["deep learning", "computer vision", "neural networks", "AI"],
      "research_domain": "Computer Science",
      "required_expertise": {
        "domains": ["Computer Science", "Engineering"],
        "keywords": ["deep learning", "computer vision", "neural networks"],
        "min_h_index": 20,
        "min_reviews": 15
      },
      "expected_matches": ["expert_2"]
    },
    {
      "id": "ms_004",
      "title": "Educational Psychology: Learning Outcomes in Higher Education",
      "abstract": "This study examines factors affecting learning outcomes in university settings...",
      "keywords": ["educational psychology", "learning outcomes", "pedagogy"],
      "research_domain": "Education",
      "required_expertise": {
        "domains": ["Education", "Psychology"],
        "keywords": ["educational psychology", "learning outcomes"],
        "min_h_index": 5,
        "min_reviews": 5
      },
      "expected_matches": ["mid_2", "early_1"]
    },
    {
      "id": "ms_005",
      "title": "Molecular Biology Techniques in Genetic Research",
      "abstract": "A review of molecular biology techniques applied to genetic research...",
      "keywords": ["molecular biology", "genetics", "PCR", "cell culture"],
      "research_domain": "Biology",
      "required_expertise": {
        "domains": ["Biology", "Medicine"],
        "keywords": ["molecular biology", "genetics"],
        "min_h_index": 3,
        "min_reviews": 3
      },
      "expected_matches": ["early_1", "expert_3"]
    }
  ]
}
```

### 3.3 AI Matching Test Script

Save as `scripts/test_reviewer_matching.py`:

```python
#!/usr/bin/env python3
"""
Test the AI reviewer matching system with 5 manuscripts.
"""
import requests
import json
from typing import Dict, List

BASE_URL = "https://meta-analysis-tool-production.up.railway.app"

def submit_manuscript(access_token: str, manuscript: Dict) -> Dict:
    """Submit a manuscript for review."""
    url = f"{BASE_URL}/api/v1/manuscripts/upload"

    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "title": manuscript["title"],
        "abstract": manuscript["abstract"],
        "keywords": manuscript["keywords"],
        "research_domain": manuscript["research_domain"]
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def find_reviewers(access_token: str, manuscript_id: str, criteria: Dict) -> Dict:
    """Use AI to find matching reviewers."""
    url = f"{BASE_URL}/api/v1/reviewer-matcher/match/search"

    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "manuscript_id": manuscript_id,
        "required_expertise_keywords": criteria["keywords"],
        "required_expertise_domains": criteria["domains"],
        "min_h_index": criteria.get("min_h_index", 5),
        "max_results": 10
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def test_all_manuscripts(editor_token: str, manuscripts: List[Dict]) -> List[Dict]:
    """Test matching for all manuscripts."""
    results = []

    for manuscript in manuscripts:
        try:
            print(f"\n{'='*60}")
            print(f"Testing manuscript: {manuscript['title']}")
            print(f"{'='*60}")

            # 1. Submit manuscript
            submission = submit_manuscript(editor_token, manuscript)
            manuscript_id = submission["manuscript_id"]
            print(f"✓ Manuscript submitted (ID: {manuscript_id})")

            # 2. Find matching reviewers
            matches = find_reviewers(
                editor_token,
                manuscript_id,
                manuscript["required_expertise"]
            )

            print(f"\n✓ Found {len(matches['matches'])} matching reviewers:")
            for i, match in enumerate(matches["matches"], 1):
                print(f"  {i}. {match['researcher_name']}")
                print(f"     H-index: {match['h_index']}")
                print(f"     Expertise Score: {match['expertise_score']:.2f}")
                print(f"     Availability Score: {match['availability_score']:.2f}")
                print(f"     Overall Score: {match['overall_score']:.2f}")
                print(f"     Conflicts: {len(match.get('conflicts', []))}")
                print()

            # Validate expected matches
            matched_ids = [m["researcher_id"] for m in matches["matches"]]
            expected_ids = manuscript.get("expected_matches", [])

            validation = {
                "all_expected_found": all(eid in matched_ids for eid in expected_ids),
                "unexpected_matches": [mid for mid in matched_ids if mid not in expected_ids],
                "missing_expected": [eid for eid in expected_ids if eid not in matched_ids]
            }

            results.append({
                "manuscript_id": manuscript_id,
                "title": manuscript["title"],
                "matches_found": len(matches["matches"]),
                "validation": validation,
                "top_matches": matches["matches"][:5]
            })

            print(f"{'='*60}\n")

        except Exception as e:
            print(f"✗ Error testing {manuscript['title']}: {e}")
            continue

    return results

# Main execution
if __name__ == "__main__":
    # Load editor credentials
    with open("test_results/mock_researchers_created.json") as f:
        researchers = json.load(f)

    # Use first expert as temporary editor (will be manually assigned editor role)
    editor_token = researchers[0]["access_token"]

    # Load manuscripts
    with open("test_data/test_manuscripts.json") as f:
        manuscripts = json.load(f)["manuscripts"]

    print("Starting AI reviewer matching tests...")
    results = test_all_manuscripts(editor_token, manuscripts)

    # Save results
    with open("test_results/reviewer_matching_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Tested {len(results)} manuscripts")
    print("Results saved to: test_results/reviewer_matching_results.json")
```

---

## 4. PHASE 3: PEER REVIEW WORKFLOW TESTING

### 4.1 End-to-End Peer Review Test

```python
#!/usr/bin/env python3
"""
Test the complete peer review workflow from submission to approval.
"""
import requests
import json
from typing import Dict

BASE_URL = "https://meta-analysis-tool-production.up.railway.app"

def generate_ai_review(reviewer_token: str, manuscript_id: str) -> Dict:
    """Generate AI-assisted peer review."""
    url = f"{BASE_URL}/api/v1/peer-reviews/generate"

    headers = {"Authorization": f"Bearer {reviewer_token}"}
    payload = {
        "manuscript_id": manuscript_id,
        "review_type": "full",
        "ai_assistance_level": "high"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def submit_review(reviewer_token: str, review_data: Dict) -> Dict:
    """Submit completed review."""
    url = f"{BASE_URL}/api/v1/peer-reviews/submit"

    headers = {"Authorization": f"Bearer {reviewer_token}"}
    response = requests.post(url, json=review_data, headers=headers)
    response.raise_for_status()
    return response.json()

def editor_approve_review(editor_token: str, review_id: str) -> Dict:
    """Editor approves the review."""
    url = f"{BASE_URL}/api/v1/peer-reviews/{review_id}/approve"

    headers = {"Authorization": f"Bearer {editor_token}"}
    payload = {
        "approval_notes": "Review meets quality standards. Approved for payout.",
        "quality_rating": 4.5
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def test_peer_review_workflow():
    """Test complete workflow: generate → submit → approve."""

    # Load test data
    with open("test_results/mock_researchers_created.json") as f:
        researchers = json.load(f)

    with open("test_results/reviewer_matching_results.json") as f:
        matches = json.load(f)

    # Get first manuscript and its top reviewer
    first_match = matches[0]
    manuscript_id = first_match["manuscript_id"]
    top_reviewer = first_match["top_matches"][0]

    # Find reviewer token
    reviewer = next(r for r in researchers if r["user_id"] == top_reviewer["researcher_id"])
    reviewer_token = reviewer["access_token"]

    # Editor token (assume first researcher is also editor for testing)
    editor_token = researchers[0]["access_token"]

    print("Step 1: Generating AI-assisted review...")
    ai_review = generate_ai_review(reviewer_token, manuscript_id)
    print(f"✓ AI review generated (ID: {ai_review['review_id']})")

    print("\nStep 2: Submitting review...")
    review_data = {
        **ai_review,
        "reviewer_comments": "Added my expert perspective to the AI-generated review.",
        "recommendation": "MINOR_REVISION"
    }
    submitted_review = submit_review(reviewer_token, review_data)
    print(f"✓ Review submitted (ID: {submitted_review['review_id']})")

    print("\nStep 3: Editor reviewing and approving...")
    approved_review = editor_approve_review(editor_token, submitted_review["review_id"])
    print(f"✓ Review approved (Eligible for payout: {approved_review['eligible_for_payout']})")

    return {
        "manuscript_id": manuscript_id,
        "review_id": submitted_review["review_id"],
        "reviewer_id": top_reviewer["researcher_id"],
        "approval_status": approved_review["approval_status"],
        "eligible_for_payout": approved_review["eligible_for_payout"]
    }

if __name__ == "__main__":
    result = test_peer_review_workflow()

    with open("test_results/peer_review_workflow_result.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\n✓ Peer review workflow test complete")
```

---

## 5. PHASE 4: META-ANALYSIS TEST RUNS (5 Complete Runs)

### 5.1 Meta-Analysis Test Cases

```json
{
  "meta_analyses": [
    {
      "id": "ma_001",
      "title": "Effectiveness of Cognitive Behavioral Therapy for Anxiety",
      "description": "Meta-analysis of CBT interventions for anxiety disorders",
      "research_question": "Is CBT effective for treating anxiety disorders compared to control conditions?",
      "databases": ["PubMed", "PsycINFO"],
      "inclusion_criteria": {
        "study_design": "RCT",
        "population": "Adults with anxiety disorders",
        "intervention": "Cognitive Behavioral Therapy",
        "outcome": "Anxiety symptom reduction"
      },
      "expected_papers": 50-100,
      "estimated_duration": "30-60 minutes"
    },
    {
      "id": "ma_002",
      "title": "Machine Learning Accuracy in Medical Diagnosis",
      "description": "Meta-analysis of ML algorithms for disease diagnosis",
      "research_question": "What is the diagnostic accuracy of machine learning algorithms in medical imaging?",
      "databases": ["PubMed", "IEEE Xplore"],
      "inclusion_criteria": {
        "study_design": "Diagnostic accuracy studies",
        "intervention": "Machine learning algorithms",
        "outcome": "Diagnostic accuracy (sensitivity, specificity)"
      },
      "expected_papers": 40-80,
      "estimated_duration": "30-60 minutes"
    },
    {
      "id": "ma_003",
      "title": "Educational Interventions for STEM Learning",
      "description": "Meta-analysis of teaching interventions in STEM education",
      "research_question": "Do active learning strategies improve student outcomes in STEM courses?",
      "databases": ["ERIC", "PubMed"],
      "inclusion_criteria": {
        "population": "University students in STEM courses",
        "intervention": "Active learning strategies",
        "outcome": "Academic performance"
      },
      "expected_papers": 30-60,
      "estimated_duration": "30-60 minutes"
    },
    {
      "id": "ma_004",
      "title": "Cardiovascular Outcomes of Drug Interventions",
      "description": "Meta-analysis of cardiovascular drug trials",
      "research_question": "What are the cardiovascular outcomes of statin therapy in primary prevention?",
      "databases": ["PubMed", "Cochrane"],
      "inclusion_criteria": {
        "study_design": "RCT",
        "population": "Adults without cardiovascular disease",
        "intervention": "Statin therapy",
        "outcome": "Major adverse cardiovascular events"
      },
      "expected_papers": 20-40,
      "estimated_duration": "20-40 minutes"
    },
    {
      "id": "ma_005",
      "title": "Effects of Mindfulness on Mental Health",
      "description": "Meta-analysis of mindfulness interventions",
      "research_question": "Are mindfulness-based interventions effective for reducing depression and anxiety?",
      "databases": ["PubMed", "PsycINFO"],
      "inclusion_criteria": {
        "study_design": "RCT",
        "intervention": "Mindfulness-based interventions",
        "outcome": "Depression and anxiety scores"
      },
      "expected_papers": 40-70,
      "estimated_duration": "30-50 minutes"
    }
  ]
}
```

### 5.2 Meta-Analysis Execution Script

```python
#!/usr/bin/env python3
"""
Execute 5 complete meta-analysis runs and validate results.
"""
import requests
import json
import time
from typing import Dict, List

BASE_URL = "https://meta-analysis-tool-production.up.railway.app"

def create_meta_analysis(access_token: str, analysis_config: Dict) -> Dict:
    """Create a new meta-analysis."""
    url = f"{BASE_URL}/api/v1/meta-analysis/create"

    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "title": analysis_config["title"],
        "description": analysis_config["description"],
        "research_question": analysis_config["research_question"],
        "databases": analysis_config["databases"],
        "inclusion_criteria": analysis_config["inclusion_criteria"]
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def check_analysis_status(access_token: str, analysis_id: str) -> Dict:
    """Check the status of a running meta-analysis."""
    url = f"{BASE_URL}/api/v1/meta-analysis/{analysis_id}/status"

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_analysis_report(access_token: str, analysis_id: str) -> Dict:
    """Get the final meta-analysis report."""
    url = f"{BASE_URL}/api/v1/meta-analysis/{analysis_id}/report"

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def wait_for_completion(access_token: str, analysis_id: str, timeout: int = 3600) -> Dict:
    """Wait for meta-analysis to complete."""
    start_time = time.time()

    while True:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Analysis {analysis_id} exceeded timeout of {timeout}s")

        status = check_analysis_status(access_token, analysis_id)

        print(f"Status: {status['status']} | Progress: {status.get('progress', 0)}%")

        if status["status"] in ["COMPLETED", "FAILED", "ERROR"]:
            return status

        time.sleep(30)  # Check every 30 seconds

def run_meta_analysis(access_token: str, config: Dict) -> Dict:
    """Run a complete meta-analysis from start to finish."""
    print(f"\n{'='*60}")
    print(f"Starting: {config['title']}")
    print(f"{'='*60}")

    # 1. Create analysis
    print("Step 1: Creating meta-analysis...")
    creation_response = create_meta_analysis(access_token, config)
    analysis_id = creation_response["analysis_id"]
    print(f"✓ Created (ID: {analysis_id})")

    # 2. Wait for completion
    print("\nStep 2: Waiting for completion...")
    final_status = wait_for_completion(access_token, analysis_id)

    if final_status["status"] != "COMPLETED":
        print(f"✗ Analysis failed: {final_status.get('error', 'Unknown error')}")
        return {
            "config": config,
            "analysis_id": analysis_id,
            "status": "FAILED",
            "error": final_status.get("error")
        }

    # 3. Get report
    print("\nStep 3: Retrieving report...")
    report = get_analysis_report(access_token, analysis_id)

    print(f"\n✓ Analysis complete!")
    print(f"  Papers found: {report['papers_found']}")
    print(f"  Papers included: {report['papers_included']}")
    print(f"  Effect size: {report.get('effect_size', 'N/A')}")
    print(f"  Heterogeneity (I²): {report.get('heterogeneity_i2', 'N/A')}")

    return {
        "config": config,
        "analysis_id": analysis_id,
        "status": "COMPLETED",
        "report_summary": {
            "papers_found": report["papers_found"],
            "papers_included": report["papers_included"],
            "effect_size": report.get("effect_size"),
            "heterogeneity_i2": report.get("heterogeneity_i2"),
            "publication_bias": report.get("publication_bias")
        }
    }

def run_all_analyses(access_token: str, analyses: List[Dict]) -> List[Dict]:
    """Run all 5 meta-analyses."""
    results = []

    for analysis in analyses:
        try:
            result = run_meta_analysis(access_token, analysis)
            results.append(result)
            time.sleep(60)  # Cooldown between analyses
        except Exception as e:
            print(f"✗ Error running {analysis['title']}: {e}")
            results.append({
                "config": analysis,
                "status": "ERROR",
                "error": str(e)
            })

    return results

# Main execution
if __name__ == "__main__":
    # Load researcher credentials
    with open("test_results/mock_researchers_created.json") as f:
        researchers = json.load(f)

    # Use first researcher's token
    access_token = researchers[0]["access_token"]

    # Load meta-analysis configurations
    with open("test_data/meta_analysis_configs.json") as f:
        configs = json.load(f)["meta_analyses"]

    print(f"Starting {len(configs)} meta-analysis runs...")
    results = run_all_analyses(access_token, configs)

    # Save results
    with open("test_results/meta_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Summary
    completed = sum(1 for r in results if r["status"] == "COMPLETED")
    failed = sum(1 for r in results if r["status"] in ["FAILED", "ERROR"])

    print(f"\n{'='*60}")
    print("META-ANALYSIS TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total runs: {len(results)}")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(completed/len(results)*100):.1f}%")
    print(f"\nResults saved to: test_results/meta_analysis_results.json")
```

---

## 6. TEST EXECUTION PLAN

### 6.1 Execution Sequence

```bash
# 1. Setup test environment
mkdir -p test_data test_results scripts

# 2. Create test data files
# Copy JSON configurations from this document into test_data/

# 3. Run Phase 1: Create mock researchers
python3 scripts/create_mock_researchers.py

# 4. Manually assign editor roles to 2 users via admin dashboard

# 5. Run Phase 2: Test AI matching
python3 scripts/test_reviewer_matching.py

# 6. Run Phase 3: Test peer review workflow
python3 scripts/test_peer_review_workflow.py

# 7. Run Phase 4: Execute meta-analyses
python3 scripts/run_meta_analyses.py

# 8. Generate final report
python3 scripts/generate_test_report.py
```

### 6.2 Success Criteria

```
Phase 1: Mock Researchers
✓ 10 researchers created successfully
✓ All profiles complete with diverse qualifications
✓ All subscriptions active

Phase 2: AI Matching
✓ All 5 manuscripts submitted
✓ AI matching returns relevant reviewers
✓ Scoring algorithm works correctly
✓ Conflict detection identifies issues
✓ Expected matches appear in top results

Phase 3: Peer Review
✓ AI can generate review drafts
✓ Reviewers can submit reviews
✓ Editors can approve/reject reviews
✓ Payout eligibility tracked correctly

Phase 4: Meta-Analysis
✓ All 5 analyses complete successfully
✓ Papers found and screened correctly
✓ Statistical analysis produces valid results
✓ Reports generated in APA format
✓ Processing time within acceptable limits
```

---

## 7. FINAL DELIVERABLES

### 7.1 Test Result Documents

1. **System Integrity Report** ✓ (Already created)
2. **Onboarding Qualification Review** ✓ (Already created)
3. **Mock Researcher Creation Results** (test_results/mock_researchers_created.json)
4. **AI Matching Test Results** (test_results/reviewer_matching_results.json)
5. **Peer Review Workflow Results** (test_results/peer_review_workflow_result.json)
6. **Meta-Analysis Test Results** (test_results/meta_analysis_results.json)
7. **Comprehensive Test Report** (COMPREHENSIVE_TEST_REPORT.md)
8. **Recommendations Document** (FINAL_RECOMMENDATIONS.md)

### 7.2 Comprehensive Test Report Template

```markdown
# Comprehensive Platform Test Report
**Date:** November 22, 2025
**Tester:** Claude AI Assistant
**Duration:** [X] hours

## Executive Summary
[Summary of all tests performed, overall system health, key findings]

## Test Results

### 1. System Integrity
- ✓ Backend health check: PASSED
- ✓ API endpoints: ALL OPERATIONAL
- ✓ Database connectivity: CONFIRMED
- ✓ Frontend deployment: LIVE

### 2. Mock Researcher Creation
- Created: 10/10 researchers
- Subscribed: 10/10 researchers
- Profile completion: 100%
- Issues: [None | List issues]

### 3. AI Reviewer Matching
- Manuscripts tested: 5/5
- Matching accuracy: [X]%
- Average match quality score: [X.XX]
- Conflict detection: [Pass/Fail]
- Top-5 relevance: [Pass/Fail]

### 4. Peer Review Workflow
- Reviews generated: [X]/[X]
- Reviews submitted: [X]/[X]
- Reviews approved: [X]/[X]
- Payout tracking: [Pass/Fail]

### 5. Meta-Analysis Runs
- Total runs: 5
- Completed successfully: [X]/5
- Average duration: [X] minutes
- Papers processed: [X] total
- Report quality: [Pass/Fail]

## Issues Found
[List all bugs, errors, or unexpected behaviors]

## Recommendations
[List all improvements and next steps]

## Conclusion
[Final assessment of system readiness]
```

---

## 8. NEXT STEPS AFTER TESTING

1. **Address Critical Issues:**
   - Fix any blocking bugs found during testing
   - Implement missing features identified

2. **Implement Recommendations:**
   - Add ORCID verification
   - Enhance editor qualification process
   - Add training modules

3. **Production Readiness:**
   - Load testing with concurrent users
   - Security audit
   - Performance optimization
   - Monitoring setup

4. **Launch Preparation:**
   - Beta user recruitment
   - Documentation completion
   - Support system setup
   - Marketing materials

---

**End of Testing Strategy**

Ready to begin execution with Phase 1: Creating mock researchers.
