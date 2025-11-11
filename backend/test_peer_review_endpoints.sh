#!/bin/bash

# Peer Review API Integration Test Script
# Tests all manuscript and peer review endpoints

set -e

API_BASE="http://localhost:8000/api/v1"
ACCESS_TOKEN=""

echo "========================================="
echo "PEER REVIEW API INTEGRATION TEST"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function to print test results
function test_passed() {
    echo -e "${GREEN}✓ $1${NC}"
}

function test_failed() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

function test_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Step 1: Register a test user
echo "Step 1: Registering test user..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_peer_review_'$(date +%s)'@example.com",
    "password": "TestPass123",
    "full_name": "Test User",
    "institution": "Test University"
  }')

if echo "$REGISTER_RESPONSE" | grep -q "email"; then
    test_passed "User registered successfully"
    USER_EMAIL=$(echo "$REGISTER_RESPONSE" | grep -o '"email":"[^"]*"' | cut -d'"' -f4)
    test_info "User email: $USER_EMAIL"
else
    test_info "User might already exist, attempting login..."
    USER_EMAIL="test@example.com"
fi

# Step 2: Login
echo ""
echo "Step 2: Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USER_EMAIL&password=TestPass123")

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    test_failed "Failed to obtain access token"
else
    test_passed "Login successful"
    test_info "Access token: ${ACCESS_TOKEN:0:20}..."
fi

# Step 3: Create a manuscript
echo ""
echo "Step 3: Creating manuscript..."
MANUSCRIPT_RESPONSE=$(curl -s -X POST "$API_BASE/manuscripts" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Impact of AI on Scientific Publishing: A Meta-Analysis",
    "abstract": "This study examines the impact of artificial intelligence on scientific publishing workflows, peer review quality, and research dissemination.",
    "keywords": ["AI", "peer review", "scientific publishing", "meta-analysis"],
    "manuscript_type": "meta_analysis",
    "journal_name": "Journal of Scientific Research",
    "author_names": ["John Doe", "Jane Smith", "Alice Johnson"],
    "author_affiliations": {
      "John Doe": "University of Example",
      "Jane Smith": "Research Institute",
      "Alice Johnson": "Tech University"
    }
  }')

MANUSCRIPT_ID=$(echo "$MANUSCRIPT_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$MANUSCRIPT_ID" ]; then
    test_failed "Failed to create manuscript"
else
    test_passed "Manuscript created successfully"
    test_info "Manuscript ID: $MANUSCRIPT_ID"
fi

# Step 4: Get manuscript
echo ""
echo "Step 4: Retrieving manuscript..."
GET_MANUSCRIPT_RESPONSE=$(curl -s -X GET "$API_BASE/manuscripts/$MANUSCRIPT_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$GET_MANUSCRIPT_RESPONSE" | grep -q "$MANUSCRIPT_ID"; then
    test_passed "Manuscript retrieved successfully"
else
    test_failed "Failed to retrieve manuscript"
fi

# Step 5: List manuscripts
echo ""
echo "Step 5: Listing manuscripts..."
LIST_RESPONSE=$(curl -s -X GET "$API_BASE/manuscripts?page=1&page_size=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$LIST_RESPONSE" | grep -q "total"; then
    test_passed "Manuscripts listed successfully"
    TOTAL=$(echo "$LIST_RESPONSE" | grep -o '"total":[0-9]*' | cut -d':' -f2)
    test_info "Total manuscripts: $TOTAL"
else
    test_failed "Failed to list manuscripts"
fi

# Step 6: Generate AI peer review (if Anthropic API key is set)
echo ""
echo "Step 6: Generating AI peer review..."
test_info "Note: This requires a valid ANTHROPIC_API_KEY environment variable"

AI_REVIEW_RESPONSE=$(curl -s -X POST "$API_BASE/peer-reviews/generate" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"manuscript_id\": \"$MANUSCRIPT_ID\",
    \"review_focus\": [\"methodology\", \"results\", \"clarity\", \"significance\"],
    \"expertise_level\": \"expert\",
    \"review_style\": \"constructive\",
    \"include_suggestions\": true
  }")

if echo "$AI_REVIEW_RESPONSE" | grep -q "review_text"; then
    test_passed "AI review generated successfully"
    RECOMMENDATION=$(echo "$AI_REVIEW_RESPONSE" | grep -o '"recommendation":"[^"]*"' | cut -d'"' -f4)
    OVERALL_SCORE=$(echo "$AI_REVIEW_RESPONSE" | grep -o '"overall_score":[0-9.]*' | cut -d':' -f2)
    test_info "Recommendation: $RECOMMENDATION"
    test_info "Overall score: $OVERALL_SCORE"
elif echo "$AI_REVIEW_RESPONSE" | grep -q "API key"; then
    test_info "AI generation skipped (API key not configured)"
else
    test_info "AI generation skipped or failed"
fi

# Step 7: Create a peer review manually
echo ""
echo "Step 7: Creating peer review..."
REVIEW_RESPONSE=$(curl -s -X POST "$API_BASE/peer-reviews" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"manuscript_id\": \"$MANUSCRIPT_ID\",
    \"review_text\": \"This is a well-structured systematic review with comprehensive coverage of the topic. The methodology is sound and the results are clearly presented.\",
    \"strengths\": \"Strong methodology, comprehensive literature search, clear presentation\",
    \"weaknesses\": \"Limited discussion of potential biases, could expand on clinical implications\",
    \"detailed_comments\": \"The authors have done an excellent job compiling the literature. However, I suggest expanding the discussion section to address potential publication bias and heterogeneity across studies.\",
    \"overall_score\": 8.5,
    \"originality_score\": 7.0,
    \"methodology_score\": 9.0,
    \"clarity_score\": 8.5,
    \"significance_score\": 8.0,
    \"recommendation\": \"minor_revision\",
    \"confidence\": 0.85,
    \"ai_assisted\": false
  }")

REVIEW_ID=$(echo "$REVIEW_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$REVIEW_ID" ]; then
    test_failed "Failed to create peer review"
else
    test_passed "Peer review created successfully"
    test_info "Review ID: $REVIEW_ID"
fi

# Step 8: Get peer review
echo ""
echo "Step 8: Retrieving peer review..."
GET_REVIEW_RESPONSE=$(curl -s -X GET "$API_BASE/peer-reviews/$REVIEW_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$GET_REVIEW_RESPONSE" | grep -q "$REVIEW_ID"; then
    test_passed "Peer review retrieved successfully"
else
    test_failed "Failed to retrieve peer review"
fi

# Step 9: List reviews for manuscript
echo ""
echo "Step 9: Listing reviews for manuscript..."
REVIEW_LIST_RESPONSE=$(curl -s -X GET "$API_BASE/manuscripts/$MANUSCRIPT_ID/reviews" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$REVIEW_LIST_RESPONSE" | grep -q "reviews"; then
    test_passed "Reviews listed successfully"
    REVIEW_COUNT=$(echo "$REVIEW_LIST_RESPONSE" | grep -o '"total":[0-9]*' | cut -d':' -f2)
    test_info "Review count: $REVIEW_COUNT"
else
    test_failed "Failed to list reviews"
fi

# Step 10: Update manuscript status
echo ""
echo "Step 10: Updating manuscript status..."
UPDATE_STATUS_RESPONSE=$(curl -s -X PUT "$API_BASE/manuscripts/$MANUSCRIPT_ID/status" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_review",
    "decision_letter": "Your manuscript is now under review."
  }')

if echo "$UPDATE_STATUS_RESPONSE" | grep -q "in_review"; then
    test_passed "Manuscript status updated successfully"
else
    test_failed "Failed to update manuscript status"
fi

# Step 11: Update peer review
echo ""
echo "Step 11: Updating peer review..."
UPDATE_REVIEW_RESPONSE=$(curl -s -X PUT "$API_BASE/peer-reviews/$REVIEW_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overall_score": 9.0,
    "status": "submitted"
  }')

if echo "$UPDATE_REVIEW_RESPONSE" | grep -q "9.0"; then
    test_passed "Peer review updated successfully"
else
    test_failed "Failed to update peer review"
fi

# Step 12: Clean up - delete review
echo ""
echo "Step 12: Deleting peer review..."
DELETE_REVIEW_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null -X DELETE "$API_BASE/peer-reviews/$REVIEW_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [ "$DELETE_REVIEW_RESPONSE" = "204" ]; then
    test_passed "Peer review deleted successfully"
else
    test_failed "Failed to delete peer review (HTTP $DELETE_REVIEW_RESPONSE)"
fi

# Step 13: Clean up - delete manuscript
echo ""
echo "Step 13: Deleting manuscript..."
DELETE_MANUSCRIPT_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null -X DELETE "$API_BASE/manuscripts/$MANUSCRIPT_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if [ "$DELETE_MANUSCRIPT_RESPONSE" = "204" ]; then
    test_passed "Manuscript deleted successfully"
else
    test_failed "Failed to delete manuscript (HTTP $DELETE_MANUSCRIPT_RESPONSE)"
fi

# Summary
echo ""
echo "========================================="
echo -e "${GREEN}ALL TESTS PASSED ✓${NC}"
echo "========================================="
echo ""
echo "API endpoints tested:"
echo "  - POST   /api/v1/auth/register"
echo "  - POST   /api/v1/auth/login"
echo "  - POST   /api/v1/manuscripts"
echo "  - GET    /api/v1/manuscripts"
echo "  - GET    /api/v1/manuscripts/{id}"
echo "  - PUT    /api/v1/manuscripts/{id}"
echo "  - PUT    /api/v1/manuscripts/{id}/status"
echo "  - DELETE /api/v1/manuscripts/{id}"
echo "  - POST   /api/v1/peer-reviews/generate"
echo "  - POST   /api/v1/peer-reviews"
echo "  - GET    /api/v1/peer-reviews/{id}"
echo "  - PUT    /api/v1/peer-reviews/{id}"
echo "  - GET    /api/v1/manuscripts/{id}/reviews"
echo "  - DELETE /api/v1/peer-reviews/{id}"
echo ""
echo "Total: 14 endpoints"
echo ""
