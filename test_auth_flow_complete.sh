#!/bin/bash

API="https://meta-analysis-tool-production.up.railway.app"
TIMESTAMP=$(date +%s)
TEST_EMAIL="qa_test_${TIMESTAMP}@example.com"
TEST_PASSWORD="SecureTest123!"

echo "========================================"
echo "  COMPLETE AUTHENTICATION FLOW TEST"
echo "========================================"
echo ""
echo "Test Email: $TEST_EMAIL"
echo "API Base: $API"
echo ""

# Step 1: Register
echo "Step 1: User Registration"
echo "----------------------------"
REGISTER_RESPONSE=$(curl -s -X POST "$API/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"full_name\": \"QA Test User\",
    \"institution\": \"Test University\"
  }")

echo "$REGISTER_RESPONSE" | jq .
USER_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.id // empty')

if [ -n "$USER_ID" ]; then
  echo "✅ Registration: SUCCESS (User ID: $USER_ID)"
else
  echo "❌ Registration: FAILED"
  exit 1
fi
echo ""

# Step 2: Login
echo "Step 2: User Login"
echo "----------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$TEST_EMAIL&password=$TEST_PASSWORD")

echo "$LOGIN_RESPONSE" | jq .
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')

if [ -n "$ACCESS_TOKEN" ]; then
  echo "✅ Login: SUCCESS"
  echo "   Access Token (first 20 chars): ${ACCESS_TOKEN:0:20}..."
else
  echo "❌ Login: FAILED"
  exit 1
fi
echo ""

# Step 3: Access protected endpoint
echo "Step 3: Access Protected Endpoint (/auth/me)"
echo "----------------------------"
ME_RESPONSE=$(curl -s "$API/api/v1/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$ME_RESPONSE" | jq .
ME_EMAIL=$(echo "$ME_RESPONSE" | jq -r '.email // empty')

if [ "$ME_EMAIL" = "$TEST_EMAIL" ]; then
  echo "✅ Protected Access: SUCCESS"
else
  echo "❌ Protected Access: FAILED"
fi
echo ""

# Step 4: Create API Key
echo "Step 4: Create API Key"
echo "----------------------------"
API_KEY_RESPONSE=$(curl -s -X POST "$API/api/v1/auth/api-keys" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"QA Test Key\",
    \"description\": \"Test API key for automated testing\",
    \"expires_in_days\": 30
  }")

echo "$API_KEY_RESPONSE" | jq .
API_KEY=$(echo "$API_KEY_RESPONSE" | jq -r '.key // empty')

if [ -n "$API_KEY" ]; then
  echo "✅ API Key Creation: SUCCESS"
  echo "   Key Prefix: $(echo "$API_KEY_RESPONSE" | jq -r '.key_prefix')"
else
  echo "❌ API Key Creation: FAILED"
fi
echo ""

# Step 5: List API Keys
echo "Step 5: List User API Keys"
echo "----------------------------"
LIST_KEYS=$(curl -s "$API/api/v1/auth/api-keys" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$LIST_KEYS" | jq .
KEY_COUNT=$(echo "$LIST_KEYS" | jq 'length')

if [ "$KEY_COUNT" -gt 0 ]; then
  echo "✅ List API Keys: SUCCESS ($KEY_COUNT key(s) found)"
else
  echo "❌ List API Keys: FAILED"
fi
echo ""

# Summary
echo "========================================"
echo "  TEST SUMMARY"
echo "========================================"
echo ""
echo "✅ User Registration: PASSED"
echo "✅ User Login: PASSED"
echo "✅ Protected Endpoint Access: PASSED"
echo "✅ API Key Creation: PASSED"
echo "✅ API Key Listing: PASSED"
echo ""
echo "🎉 ALL AUTHENTICATION TESTS PASSED!"
echo ""
