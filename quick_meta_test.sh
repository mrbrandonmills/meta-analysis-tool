#!/bin/bash

API="https://meta-analysis-tool-production.up.railway.app"

echo "=== QUICK META-ANALYSIS API TEST ==="
echo ""

# Step 1: Register
echo "1. Registering user..."
TIMESTAMP=$(date +%s)
EMAIL="quick_test_${TIMESTAMP}@example.com"

REGISTER=$(curl -s -X POST "$API/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"Test123!\",\"full_name\":\"Quick Test\",\"institution\":\"Test U\"}")

USER_ID=$(echo "$REGISTER" | jq -r '.id // empty')
if [ -z "$USER_ID" ]; then
  echo "❌ Registration failed"
  echo "$REGISTER" | jq .
  exit 1
fi
echo "✅ User registered: $USER_ID"

# Step 2: Login
echo ""
echo "2. Logging in..."
LOGIN=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=Test123!")

TOKEN=$(echo "$LOGIN" | jq -r '.access_token // empty')
if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  echo "$LOGIN" | jq .
  exit 1
fi
echo "✅ Login successful"

# Step 3: Create meta-analysis (with 60s timeout)
echo ""
echo "3. Creating meta-analysis (with 60s timeout)..."
echo "   This calls Anthropic API with model: claude-sonnet-4-5-20250929"
echo ""

START_TIME=$(date +%s)
CREATE=$(curl -s --max-time 60 -X POST "$API/api/v1/meta-analysis/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "research_question": "What is the effect of exercise on depression?",
    "topic": "Exercise and Depression",
    "inclusion_criteria": ["RCTs", "Adults"],
    "exclusion_criteria": ["Non-English"]
  }' 2>&1)

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

ANALYSIS_ID=$(echo "$CREATE" | jq -r '.id // empty')

if [ -z "$ANALYSIS_ID" ]; then
  echo "❌ Meta-analysis creation failed (took ${DURATION}s)"
  echo ""
  echo "Response:"
  echo "$CREATE"
  exit 1
fi

echo "✅ Meta-analysis created: $ANALYSIS_ID (took ${DURATION}s)"
echo ""
echo "Full response:"
echo "$CREATE" | jq .
echo ""
echo "=== TEST COMPLETE ==="
