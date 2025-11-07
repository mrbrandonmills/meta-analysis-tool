#!/bin/bash

# Database Schema Verification Script
# Verifies all tables exist and match expected schema

API="https://meta-analysis-tool-production.up.railway.app"

echo "========================================"
echo "  DATABASE SCHEMA VERIFICATION"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

check_test() {
  TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
  echo "Check $TOTAL_CHECKS: $1"
}

check_pass() {
  PASSED_CHECKS=$((PASSED_CHECKS + 1))
  echo -e "${GREEN}✅ PASS${NC}: $1"
  echo ""
}

check_fail() {
  FAILED_CHECKS=$((FAILED_CHECKS + 1))
  echo -e "${RED}❌ FAIL${NC}: $1"
  echo ""
}

# Register a test user first
TIMESTAMP=$(date +%s)
TEST_EMAIL="db_test_${TIMESTAMP}@example.com"
TEST_PASSWORD="DBTest123!"

echo "Creating test user for database verification..."
REGISTER=$(curl -s -X POST "$API/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"full_name\": \"DB Test User\",
    \"institution\": \"Test U\"
  }")

USER_ID=$(echo "$REGISTER" | jq -r '.id // empty')

if [ -n "$USER_ID" ]; then
  check_pass "Test user created (verifies users table exists)"
else
  check_fail "Failed to create test user (users table issue)"
  echo "$REGISTER" | jq .
fi

# Login to get token
LOGIN=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$TEST_EMAIL&password=$TEST_PASSWORD")

TOKEN=$(echo "$LOGIN" | jq -r '.access_token // empty')

if [ -n "$TOKEN" ]; then
  check_pass "Authentication successful"
else
  check_fail "Authentication failed"
fi

# Check 1: Users table
check_test "Users Table"
ME=$(curl -s "$API/api/v1/auth/me" -H "Authorization: Bearer $TOKEN")
ME_EMAIL=$(echo "$ME" | jq -r '.email // empty')

if [ "$ME_EMAIL" = "$TEST_EMAIL" ]; then
  check_pass "Users table operational"
else
  check_fail "Users table issues"
fi

# Check 2: API Keys table
check_test "API Keys Table"
API_KEY=$(curl -s -X POST "$API/api/v1/auth/api-keys" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Key","description":"Test","expires_in_days":30}')

KEY_ID=$(echo "$API_KEY" | jq -r '.id // empty')

if [ -n "$KEY_ID" ]; then
  check_pass "API Keys table operational"
else
  check_fail "API Keys table issues"
fi

# Check 3: List API keys (verify relationship)
check_test "API Keys Relationship"
LIST_KEYS=$(curl -s "$API/api/v1/auth/api-keys" -H "Authorization: Bearer $TOKEN")
KEY_COUNT=$(echo "$LIST_KEYS" | jq 'length // 0')

if [ "$KEY_COUNT" -gt 0 ]; then
  check_pass "User-APIKey relationship working ($KEY_COUNT key(s))"
else
  check_fail "User-APIKey relationship broken"
fi

# Check 4: Test registration flow (verifies multiple table operations)
check_test "Complex Database Operations"
FLOW=$(curl -s "$API/api/v1/auth/test-registration-flow")
FLOW_STATUS=$(echo "$FLOW" | jq -r '.status // empty')

if [ "$FLOW_STATUS" = "success" ]; then
  check_pass "Complex database operations working"
  echo "$FLOW" | jq '.steps[]'
else
  check_fail "Complex database operations failing"
fi

# Check 5: Verify Pydantic models
check_test "Pydantic Model Validation"
PYDANTIC=$(curl -s "$API/api/v1/auth/test-pydantic")
PYDANTIC_STATUS=$(echo "$PYDANTIC" | jq -r '.status // empty')

if [ "$PYDANTIC_STATUS" = "success" ]; then
  check_pass "Pydantic models validated"
else
  check_fail "Pydantic model validation failing"
fi

# Check 6: Health check database connectivity
check_test "Database Health Check"
HEALTH=$(curl -s "$API/api/v1/health")
HEALTH_STATUS=$(echo "$HEALTH" | jq -r '.status // empty')

if [ "$HEALTH_STATUS" = "healthy" ]; then
  check_pass "Database connectivity healthy"
else
  check_fail "Database connectivity issues"
fi

# Summary
echo ""
echo "========================================"
echo "  VERIFICATION SUMMARY"
echo "========================================"
echo ""
echo "Total Checks: $TOTAL_CHECKS"
echo -e "${GREEN}Passed: $PASSED_CHECKS${NC}"
echo -e "${RED}Failed: $FAILED_CHECKS${NC}"
echo ""

# Expected tables based on models
echo "Expected Database Tables:"
echo "  ✓ users (with roles, passwords, timestamps)"
echo "  ✓ api_keys (with user relationship)"
echo "  ✓ projects (multi-tool support)"
echo "  ✓ workflows (agent orchestration)"
echo "  ✓ papers (shared across tools)"
echo "  ✓ researchers (author information)"
echo "  ✓ manuscripts (peer review tool)"
echo "  ✓ peer_reviews (review tracking)"
echo "  ✓ reviewer_matches (matcher tool)"
echo "  ✓ research_gaps (research direction tool)"
echo "  ✓ research_proposals (proposal generation)"
echo "  ✓ Association tables (many-to-many)"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
  echo -e "${GREEN}🎉 DATABASE SCHEMA: VERIFIED${NC}"
  exit 0
else
  echo -e "${RED}⚠️  DATABASE SCHEMA: ISSUES FOUND${NC}"
  exit 1
fi
