#!/bin/bash

# Comprehensive Meta-Analysis Workflow Test Script
# Tests the complete flow from project creation to report generation

API="https://meta-analysis-tool-production.up.railway.app"
TIMESTAMP=$(date +%s)
TEST_EMAIL="workflow_test_${TIMESTAMP}@example.com"
TEST_PASSWORD="WorkflowTest123!"

echo "========================================"
echo "  META-ANALYSIS WORKFLOW TEST"
echo "========================================"
echo ""
echo "API: $API"
echo "Test User: $TEST_EMAIL"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

test_step() {
  TOTAL_TESTS=$((TOTAL_TESTS + 1))
  echo "----------------------------------------"
  echo "Test $TOTAL_TESTS: $1"
  echo "----------------------------------------"
}

test_pass() {
  PASSED_TESTS=$((PASSED_TESTS + 1))
  echo -e "${GREEN}✅ PASS${NC}: $1"
  echo ""
}

test_fail() {
  FAILED_TESTS=$((FAILED_TESTS + 1))
  echo -e "${RED}❌ FAIL${NC}: $1"
  echo ""
}

# Step 1: Register user
test_step "User Registration"
REGISTER_RESPONSE=$(curl -s -X POST "$API/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"full_name\": \"Workflow Test User\",
    \"institution\": \"Test University\"
  }")

USER_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.id // empty')
if [ -n "$USER_ID" ]; then
  test_pass "User registered successfully (ID: $USER_ID)"
else
  test_fail "User registration failed"
  echo "$REGISTER_RESPONSE" | jq .
  exit 1
fi

# Step 2: Login
test_step "User Login"
LOGIN_RESPONSE=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$TEST_EMAIL&password=$TEST_PASSWORD")

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')
if [ -n "$ACCESS_TOKEN" ]; then
  test_pass "Login successful"
else
  test_fail "Login failed"
  echo "$LOGIN_RESPONSE" | jq .
  exit 1
fi

# Step 3: Create Meta-Analysis Project
test_step "Create Meta-Analysis Project"
CREATE_RESPONSE=$(curl -s -X POST "$API/api/v1/meta-analysis/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "research_question": "What is the effect of mindfulness meditation on anxiety in adults?",
    "topic": "Mindfulness and Anxiety Meta-Analysis",
    "inclusion_criteria": [
      "Randomized controlled trials",
      "Adult participants (18+ years)",
      "Mindfulness-based intervention",
      "Anxiety as primary or secondary outcome"
    ],
    "exclusion_criteria": [
      "Non-English language",
      "Qualitative studies",
      "Case studies",
      "Children or adolescents"
    ],
    "databases": ["pubmed"],
    "peer_review_only": true
  }')

echo "$CREATE_RESPONSE" | jq .
ANALYSIS_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id // empty')
WORKFLOW_STATUS=$(echo "$CREATE_RESPONSE" | jq -r '.status // empty')

if [ "$WORKFLOW_STATUS" = "workflow_created" ] && [ -n "$ANALYSIS_ID" ]; then
  test_pass "Meta-analysis project created (ID: $ANALYSIS_ID)"
else
  test_fail "Meta-analysis creation failed"
  echo "Response: $CREATE_RESPONSE"
  exit 1
fi

# Step 4: Execute Meta-Analysis Workflow
test_step "Execute Meta-Analysis Workflow"
EXECUTE_RESPONSE=$(curl -s -X POST "$API/api/v1/meta-analysis/execute/$ANALYSIS_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$EXECUTE_RESPONSE" | jq .

EXEC_STATUS=$(echo "$EXECUTE_RESPONSE" | jq -r '.status // empty')
SEARCH_RESULTS=$(echo "$EXECUTE_RESPONSE" | jq -r '.search_results.total_found // 0')

if [ "$EXEC_STATUS" = "in_progress" ]; then
  test_pass "Workflow execution started (Found $SEARCH_RESULTS studies)"
else
  test_fail "Workflow execution failed"
  echo "Response: $EXECUTE_RESPONSE"
fi

# Step 5: Check Status
test_step "Check Analysis Status"
STATUS_RESPONSE=$(curl -s "$API/api/v1/meta-analysis/status/$ANALYSIS_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$STATUS_RESPONSE" | jq .

STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // empty')
DECISIONS=$(echo "$STATUS_RESPONSE" | jq -r '.decisions // 0')

if [ -n "$STATUS" ]; then
  test_pass "Status check successful (Status: $STATUS, Decisions: $DECISIONS)"
else
  test_fail "Status check failed"
fi

# Step 6: Get Audit Trail
test_step "Retrieve Audit Trail"
AUDIT_RESPONSE=$(curl -s "$API/api/v1/meta-analysis/audit/$ANALYSIS_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$AUDIT_RESPONSE" | jq . | head -30

AUDIT_COUNT=$(echo "$AUDIT_RESPONSE" | jq 'length // 0')

if [ "$AUDIT_COUNT" -gt 0 ]; then
  test_pass "Audit trail retrieved ($AUDIT_COUNT entries)"
else
  test_fail "Audit trail empty or failed"
fi

# Step 7: Ask Q&A Question
test_step "Q&A Agent Question"
QA_RESPONSE=$(curl -s -X POST "$API/api/v1/meta-analysis/ask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{
    \"question\": \"How did you decide which studies to include in this meta-analysis?\",
    \"meta_analysis_id\": \"$ANALYSIS_ID\"
  }")

echo "$QA_RESPONSE" | jq .

QA_ANSWER=$(echo "$QA_RESPONSE" | jq -r '.answer // empty')
QA_CONFIDENCE=$(echo "$QA_RESPONSE" | jq -r '.confidence // 0')

if [ -n "$QA_ANSWER" ]; then
  test_pass "Q&A agent responded (Confidence: $QA_CONFIDENCE)"
else
  test_fail "Q&A agent failed"
fi

# Step 8: Get Report
test_step "Generate Report"
REPORT_RESPONSE=$(curl -s "$API/api/v1/meta-analysis/report/$ANALYSIS_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$REPORT_RESPONSE" | jq .

REPORT_STATUS=$(echo "$REPORT_RESPONSE" | jq -r '.status // empty')

if [ "$REPORT_STATUS" = "report_ready" ]; then
  test_pass "Report generation successful"
else
  test_fail "Report generation failed"
fi

# Step 9: List Available Agents
test_step "List Available Agents"
AGENTS_RESPONSE=$(curl -s "$API/api/v1/agents/available" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

AGENT_COUNT=$(echo "$AGENTS_RESPONSE" | jq '.agents | length // 0')

if [ "$AGENT_COUNT" -gt 0 ]; then
  test_pass "Retrieved $AGENT_COUNT agents"
  echo "$AGENTS_RESPONSE" | jq '.agents[].name'
else
  test_fail "Failed to retrieve agents"
fi

# Final Summary
echo ""
echo "========================================"
echo "  TEST SUMMARY"
echo "========================================"
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
  echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
  echo ""
  echo "Meta-Analysis Workflow: ✅ OPERATIONAL"
  exit 0
else
  echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
  echo ""
  echo "Meta-Analysis Workflow: ❌ NEEDS ATTENTION"
  exit 1
fi
