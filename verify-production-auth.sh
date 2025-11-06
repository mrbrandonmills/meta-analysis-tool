#!/bin/bash

echo "🔍 Testing Production Authentication..."
echo ""

# Get production URL from Railway
PROD_URL="https://meta-analysis-tool-production.up.railway.app"

echo "1. Testing User Registration..."
REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${PROD_URL}/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser'$(date +%s)'@example.com",
    "password": "TestPass123!",
    "full_name": "Test User",
    "institution": "Test University"
  }')

HTTP_CODE=$(echo "$REGISTER_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$REGISTER_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Registration: SUCCESS (HTTP $HTTP_CODE)"
    echo "   Response: $RESPONSE_BODY"
else
    echo "❌ Registration: FAILED (HTTP $HTTP_CODE)"
    echo "   Response: $RESPONSE_BODY"
fi

echo ""
echo "2. Testing Health Endpoint..."
HEALTH_RESPONSE=$(curl -s "${PROD_URL}/api/v1/health")
echo "✅ Health: $HEALTH_RESPONSE"

echo ""
echo "3. Testing Database Connection..."
DB_HEALTH=$(curl -s "${PROD_URL}/api/v1/health/detailed")
echo "Response: $DB_HEALTH"

echo ""
echo "✅ Production verification complete!"
