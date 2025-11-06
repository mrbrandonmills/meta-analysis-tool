#!/bin/bash

echo "Testing full authentication flow..."

# Step 1: Register (may fail if user exists, that's ok)
echo "1. Testing registration..."
REGISTER_RESP=$(curl -s -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"flowtest@example.com","password":"FlowTest123","full_name":"Flow Test","institution":"Test U"}')
echo "$REGISTER_RESP" | jq -C '.'

# Step 2: Login
echo -e "\n2. Testing login..."
LOGIN_RESP=$(curl -s -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=flowtest@example.com&password=FlowTest123")
echo "$LOGIN_RESP" | jq -C '.'
TOKEN=$(echo "$LOGIN_RESP" | jq -r '.access_token')

# Step 3: Get current user
echo -e "\n3. Testing /auth/me with token..."
curl -s -H "Authorization: Bearer $TOKEN" https://meta-analysis-tool-production.up.railway.app/api/v1/auth/me | jq -C '.'

echo -e "\nFull auth flow complete!"
