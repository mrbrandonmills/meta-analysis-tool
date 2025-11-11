#!/bin/bash

# Test script for Reviewer Matcher API (Tool 4)
# Run this after starting the FastAPI server

BASE_URL="http://localhost:8000/api/v1"
TOKEN=""

echo "=========================================="
echo "Reviewer Matcher API Test Suite"
echo "=========================================="

# Step 1: Register a test user
echo ""
echo "1. Registering test user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_reviewer_matcher@example.com",
    "password": "TestPass123",
    "full_name": "Test Reviewer User",
    "institution": "Test University"
  }')
echo "Response: $REGISTER_RESPONSE"

# Step 2: Login to get token
echo ""
echo "2. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test_reviewer_matcher@example.com&password=TestPass123")
echo "Response: $LOGIN_RESPONSE"

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "ERROR: Failed to get access token"
  exit 1
fi

echo "Token: $TOKEN"

# Step 3: Create a test researcher
echo ""
echo "3. Creating test researcher..."
RESEARCHER_RESPONSE=$(curl -s -X POST "$BASE_URL/researchers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Jane Smith",
    "email": "jane.smith@university.edu",
    "institution": "Stanford University",
    "department": "Computer Science",
    "country": "USA",
    "h_index": 45,
    "i10_index": 120,
    "total_citations": 5000,
    "publication_count": 150,
    "expertise_keywords": ["machine learning", "neural networks", "deep learning"],
    "research_domains": ["artificial intelligence", "computer vision"],
    "orcid": "0000-0001-2345-6789",
    "semantic_scholar_id": "1234567"
  }')
echo "Response: $RESEARCHER_RESPONSE"

RESEARCHER_ID=$(echo $RESEARCHER_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

# Step 4: Create another test researcher
echo ""
echo "4. Creating second test researcher..."
RESEARCHER2_RESPONSE=$(curl -s -X POST "$BASE_URL/researchers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prof. John Doe",
    "email": "john.doe@mit.edu",
    "institution": "MIT",
    "department": "EECS",
    "country": "USA",
    "h_index": 60,
    "i10_index": 180,
    "total_citations": 8000,
    "publication_count": 200,
    "expertise_keywords": ["deep learning", "computer vision", "robotics"],
    "research_domains": ["artificial intelligence", "robotics"],
    "orcid": "0000-0002-3456-7890"
  }')
echo "Response: $RESEARCHER2_RESPONSE"

RESEARCHER2_ID=$(echo $RESEARCHER2_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

# Step 5: Search researchers
echo ""
echo "5. Searching researchers by keyword..."
SEARCH_RESPONSE=$(curl -s -X GET "$BASE_URL/researchers?keyword=machine%20learning&sort_by=h_index&sort_order=desc&page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN")
echo "Response: $SEARCH_RESPONSE"

# Step 6: Get researcher profile
echo ""
echo "6. Getting researcher profile..."
if [ ! -z "$RESEARCHER_ID" ]; then
  PROFILE_RESPONSE=$(curl -s -X GET "$BASE_URL/researchers/$RESEARCHER_ID" \
    -H "Authorization: Bearer $TOKEN")
  echo "Response: $PROFILE_RESPONSE"
fi

# Step 7: Update researcher
echo ""
echo "7. Updating researcher..."
if [ ! -z "$RESEARCHER_ID" ]; then
  UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/researchers/$RESEARCHER_ID" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "h_index": 50,
      "total_citations": 5500,
      "recent_review_count": 3,
      "current_workload": 2,
      "response_rate": 0.85
    }')
  echo "Response: $UPDATE_RESPONSE"
fi

# Step 8: Create a manuscript for matching
echo ""
echo "8. Creating manuscript for reviewer matching..."
MANUSCRIPT_RESPONSE=$(curl -s -X POST "$BASE_URL/manuscripts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Deep Learning for Medical Image Analysis",
    "abstract": "This paper presents a novel approach to medical image analysis using deep learning techniques...",
    "keywords": ["deep learning", "medical imaging", "computer vision"],
    "manuscript_type": "research_article"
  }')
echo "Response: $MANUSCRIPT_RESPONSE"

MANUSCRIPT_ID=$(echo $MANUSCRIPT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

# Step 9: Search for matching reviewers
echo ""
echo "9. Searching for matching reviewers..."
if [ ! -z "$MANUSCRIPT_ID" ]; then
  MATCH_RESPONSE=$(curl -s -X POST "$BASE_URL/reviewer-matches/search" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"manuscript_id\": \"$MANUSCRIPT_ID\",
      \"required_expertise\": [\"deep learning\", \"computer vision\"],
      \"research_domains\": [\"artificial intelligence\"],
      \"min_h_index\": 10,
      \"min_citations\": 500,
      \"max_current_workload\": 5,
      \"min_response_rate\": 0.5,
      \"diversity_preference\": 0.3,
      \"max_results\": 20
    }")
  echo "Response: $MATCH_RESPONSE"

  # Extract match ID for next steps
  MATCH_ID=$(echo $MATCH_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['matches'][0]['id'] if data.get('matches') else '')" 2>/dev/null)
fi

# Step 10: Get match details
echo ""
echo "10. Getting match details..."
if [ ! -z "$MATCH_ID" ]; then
  MATCH_DETAIL_RESPONSE=$(curl -s -X GET "$BASE_URL/reviewer-matches/$MATCH_ID" \
    -H "Authorization: Bearer $TOKEN")
  echo "Response: $MATCH_DETAIL_RESPONSE"
fi

# Step 11: Send invitation
echo ""
echo "11. Sending reviewer invitation..."
if [ ! -z "$MATCH_ID" ]; then
  INVITE_RESPONSE=$(curl -s -X POST "$BASE_URL/reviewer-matches/invite" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"match_id\": \"$MATCH_ID\",
      \"custom_message\": \"We would like to invite you to review this manuscript.\",
      \"deadline_days\": 14
    }")
  echo "Response: $INVITE_RESPONSE"
fi

# Step 12: Update match status
echo ""
echo "12. Updating match status to ACCEPTED..."
if [ ! -z "$MATCH_ID" ]; then
  STATUS_RESPONSE=$(curl -s -X PUT "$BASE_URL/reviewer-matches/$MATCH_ID/status" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "status": "accepted",
      "notes": "Reviewer accepted the invitation"
    }')
  echo "Response: $STATUS_RESPONSE"
fi

# Step 13: Get all matches for manuscript
echo ""
echo "13. Getting all matches for manuscript..."
if [ ! -z "$MANUSCRIPT_ID" ]; then
  ALL_MATCHES_RESPONSE=$(curl -s -X GET "$BASE_URL/manuscripts/$MANUSCRIPT_ID/matches" \
    -H "Authorization: Bearer $TOKEN")
  echo "Response: $ALL_MATCHES_RESPONSE"
fi

# Step 14: Delete test researcher
echo ""
echo "14. Cleaning up - deleting test researcher..."
if [ ! -z "$RESEARCHER_ID" ]; then
  DELETE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/researchers/$RESEARCHER_ID" \
    -H "Authorization: Bearer $TOKEN")
  echo "Response: $DELETE_RESPONSE (should be empty for 204)"
fi

echo ""
echo "=========================================="
echo "Test suite completed!"
echo "=========================================="
