#!/bin/bash
# Production Verification Script - Database Migration Fix
# Tests user registration and login endpoints after migration fix deployment

set -e

PROD_URL="https://meta-analysis-tool-production.up.railway.app"
TEST_EMAIL="migration-test-$(date +%s)@example.com"
TEST_PASSWORD="TestPass123"
TEST_NAME="Migration Test User"

echo "======================================"
echo "Production Migration Fix Verification"
echo "======================================"
echo ""
echo "Production URL: $PROD_URL"
echo "Test Email: $TEST_EMAIL"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check health endpoint
echo "1. Testing Health Endpoint..."
health_response=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/api/v1/health")
if [ "$health_response" = "200" ]; then
    echo -e "${GREEN}✓ Health check passed (HTTP $health_response)${NC}"
else
    echo -e "${RED}✗ Health check failed (HTTP $health_response)${NC}"
    echo "Production API may not be ready yet. Wait for Railway deployment to complete."
    exit 1
fi
echo ""

# Test user registration
echo "2. Testing User Registration..."
register_output=$(mktemp)
http_code=$(curl -s -w "%{http_code}" -X POST "$PROD_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\",
        \"full_name\": \"$TEST_NAME\"
    }" -o "$register_output")

response_body=$(cat "$register_output")

if [ "$http_code" = "201" ]; then
    echo -e "${GREEN}✓ User registration successful (HTTP $http_code)${NC}"
    echo "Response: $response_body" | jq '.' 2>/dev/null || echo "$response_body"

    # Extract user ID
    user_id=$(echo "$response_body" | jq -r '.id' 2>/dev/null || echo "unknown")
    echo "Created User ID: $user_id"
else
    echo -e "${RED}✗ User registration failed (HTTP $http_code)${NC}"
    echo "Response: $response_body"
    rm -f "$register_output"
    echo ""
    echo "MIGRATION FIX MAY HAVE FAILED!"
    echo "Check Railway logs: railway logs --service meta-analysis-tool-production"
    exit 1
fi
rm -f "$register_output"
echo ""

# Test user login
echo "3. Testing User Login..."
login_output=$(mktemp)
http_code=$(curl -s -w "%{http_code}" -X POST "$PROD_URL/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{
        \"username\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\"
    }" -o "$login_output")

response_body=$(cat "$login_output")

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ User login successful (HTTP $http_code)${NC}"

    # Extract token
    access_token=$(echo "$response_body" | jq -r '.access_token' 2>/dev/null || echo "unknown")
    token_length=${#access_token}
    echo "Access Token Length: $token_length characters"
    echo "Token Preview: ${access_token:0:50}..."
else
    echo -e "${RED}✗ User login failed (HTTP $http_code)${NC}"
    echo "Response: $response_body"
    rm -f "$login_output"
    exit 1
fi
rm -f "$login_output"
echo ""

# Test authenticated endpoint
echo "4. Testing Authenticated Endpoint..."
me_output=$(mktemp)
http_code=$(curl -s -w "%{http_code}" -X GET "$PROD_URL/api/v1/auth/me" \
    -H "Authorization: Bearer $access_token" -o "$me_output")

response_body=$(cat "$me_output")

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Authenticated request successful (HTTP $http_code)${NC}"
    echo "User Profile: $response_body" | jq '.' 2>/dev/null || echo "$response_body"
else
    echo -e "${YELLOW}⚠ Authenticated request failed (HTTP $http_code)${NC}"
    echo "Response: $response_body"
    echo "Note: This may be expected if /auth/me endpoint is not implemented yet"
fi
rm -f "$me_output"
echo ""

# Summary
echo "======================================"
echo -e "${GREEN}✓ MIGRATION FIX VERIFICATION COMPLETE${NC}"
echo "======================================"
echo ""
echo "Summary:"
echo "  ✓ Health check: PASSED"
echo "  ✓ User registration: PASSED (HTTP 201)"
echo "  ✓ User login: PASSED (HTTP 200)"
echo "  ✓ Database migrations: WORKING"
echo "  ✓ Users table: EXISTS"
echo ""
echo "Test Credentials (for manual testing):"
echo "  Email: $TEST_EMAIL"
echo "  Password: $TEST_PASSWORD"
echo ""
echo "Next Steps:"
echo "  1. Frontend team can now integrate with production API"
echo "  2. Test registration flow in production UI"
echo "  3. Monitor production logs for any errors"
echo "  4. Clean up test user from database if needed"
echo ""
echo "View Production Logs:"
echo "  railway logs --service meta-analysis-tool-production"
echo ""
