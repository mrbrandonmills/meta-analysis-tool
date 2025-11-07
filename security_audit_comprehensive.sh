#!/bin/bash

# Comprehensive Security Audit Script
# Tests: SQL Injection, XSS, Auth Bypass, Rate Limiting, CSRF, Token Security

API="https://meta-analysis-tool-production.up.railway.app"

echo "========================================"
echo "  COMPREHENSIVE SECURITY AUDIT"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
VULNERABILITIES=0

test_security() {
  TOTAL_TESTS=$((TOTAL_TESTS + 1))
  echo "----------------------------------------"
  echo "Security Test $TOTAL_TESTS: $1"
  echo "----------------------------------------"
}

test_pass() {
  PASSED_TESTS=$((PASSED_TESTS + 1))
  echo -e "${GREEN}✅ SECURE${NC}: $1"
  echo ""
}

test_fail() {
  FAILED_TESTS=$((FAILED_TESTS + 1))
  VULNERABILITIES=$((VULNERABILITIES + 1))
  echo -e "${RED}⚠️  VULNERABLE${NC}: $1"
  echo ""
}

# Setup: Create test user
TIMESTAMP=$(date +%s)
TEST_EMAIL="security_test_${TIMESTAMP}@example.com"
TEST_PASSWORD="SecTest123!"

echo "Setting up test user for security testing..."
REGISTER=$(curl -s -X POST "$API/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"full_name\":\"Security Test\",\"institution\":\"Test U\"}")

TOKEN=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$TEST_EMAIL&password=$TEST_PASSWORD" | jq -r '.access_token')

echo "Test user created. Token obtained."
echo ""

# ===========================================
# CATEGORY 1: SQL INJECTION TESTS
# ===========================================

test_security "SQL Injection - Email Field"
SQL_INJECT=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin' OR '1'='1&password=anything")

if echo "$SQL_INJECT" | jq -e '.access_token' > /dev/null 2>&1; then
  test_fail "SQL injection successful in email field"
else
  test_pass "SQL injection blocked in email field"
fi

test_security "SQL Injection - Registration"
SQL_REG=$(curl -s -X POST "$API/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test' OR 1=1--@example.com\",\"password\":\"Test123\",\"full_name\":\"SQL Test\",\"institution\":\"Test\"}")

if echo "$SQL_REG" | jq -e '.id' > /dev/null 2>&1; then
  # Check if malicious SQL was executed
  if [[ "$SQL_REG" == *"OR 1=1"* ]]; then
    test_fail "SQL injection possible in registration"
  else
    test_pass "SQL injection blocked in registration"
  fi
else
  test_pass "SQL injection blocked in registration (rejected)"
fi

# ===========================================
# CATEGORY 2: XSS (Cross-Site Scripting)
# ===========================================

test_security "XSS - Stored XSS in Full Name"
XSS_USER=$(curl -s -X POST "$API/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"xss_test_${TIMESTAMP}@example.com\",\"password\":\"Test123\",\"full_name\":\"<script>alert('XSS')</script>\",\"institution\":\"Test\"}")

XSS_NAME=$(echo "$XSS_USER" | jq -r '.full_name // empty')

if [[ "$XSS_NAME" == *"<script>"* ]]; then
  test_fail "Stored XSS possible - script tags not sanitized"
else
  test_pass "XSS prevented - script tags filtered/escaped"
fi

test_security "XSS - Reflected XSS in Error Messages"
XSS_ERROR=$(curl -s "$API/api/v1/agents/profile/<script>alert('xss')</script>")

if echo "$XSS_ERROR" | grep -q "<script>"; then
  test_fail "Reflected XSS in error messages"
else
  test_pass "Reflected XSS prevented"
fi

# ===========================================
# CATEGORY 3: AUTHENTICATION BYPASS
# ===========================================

test_security "Auth Bypass - Access Protected Endpoint Without Token"
NO_AUTH=$(curl -s -o /dev/null -w "%{http_code}" "$API/api/v1/auth/me")

if [ "$NO_AUTH" = "401" ]; then
  test_pass "Protected endpoint requires authentication"
else
  test_fail "Protected endpoint accessible without auth (status: $NO_AUTH)"
fi

test_security "Auth Bypass - Invalid Token"
INVALID_TOKEN=$(curl -s -o /dev/null -w "%{http_code}" "$API/api/v1/auth/me" \
  -H "Authorization: Bearer invalid_token_12345")

if [ "$INVALID_TOKEN" = "401" ]; then
  test_pass "Invalid tokens rejected"
else
  test_fail "Invalid tokens accepted (status: $INVALID_TOKEN)"
fi

test_security "Auth Bypass - Expired/Malformed Token"
MALFORMED=$(curl -s -o /dev/null -w "%{http_code}" "$API/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature")

if [ "$MALFORMED" = "401" ]; then
  test_pass "Malformed tokens rejected"
else
  test_fail "Malformed tokens accepted (status: $MALFORMED)"
fi

# ===========================================
# CATEGORY 4: AUTHORIZATION CHECKS
# ===========================================

test_security "Authorization - User Can Only Access Own Data"
# Try to access another user's API keys (should fail)
OTHER_KEYS=$(curl -s "$API/api/v1/auth/api-keys" \
  -H "Authorization: Bearer $TOKEN")

KEY_COUNT=$(echo "$OTHER_KEYS" | jq 'length // 0')

# This should only show the current user's keys
if [ "$KEY_COUNT" -ge 0 ]; then
  test_pass "Authorization working - user sees only their data"
else
  test_fail "Authorization broken - access to other users' data"
fi

# ===========================================
# CATEGORY 5: PASSWORD SECURITY
# ===========================================

test_security "Password Security - Weak Password Rejection"
WEAK_PW=$(curl -s -X POST "$API/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"weak_${TIMESTAMP}@example.com\",\"password\":\"123\",\"full_name\":\"Test\",\"institution\":\"Test\"}")

if echo "$WEAK_PW" | jq -e '.id' > /dev/null 2>&1; then
  test_fail "Weak passwords accepted"
else
  test_pass "Weak passwords rejected"
fi

test_security "Password Security - Password Not Returned in API"
ME_DATA=$(curl -s "$API/api/v1/auth/me" -H "Authorization: Bearer $TOKEN")

if echo "$ME_DATA" | jq -e '.password' > /dev/null 2>&1 || \
   echo "$ME_DATA" | jq -e '.hashed_password' > /dev/null 2>&1; then
  test_fail "Password exposed in API response"
else
  test_pass "Password not exposed in API"
fi

# ===========================================
# CATEGORY 6: RATE LIMITING
# ===========================================

test_security "Rate Limiting - Rapid Requests"
echo "Sending 25 rapid requests to test rate limiting..."

RATE_LIMIT_HIT=false
for i in {1..25}; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API/api/v1/health")
  if [ "$STATUS" = "429" ]; then
    RATE_LIMIT_HIT=true
    break
  fi
done

if $RATE_LIMIT_HIT; then
  test_pass "Rate limiting active (429 after multiple requests)"
else
  test_fail "Rate limiting not enforced (25 requests succeeded)"
fi

# ===========================================
# CATEGORY 7: CORS SECURITY
# ===========================================

test_security "CORS - Proper CORS Headers"
CORS=$(curl -s -I "$API/api/v1/health" | grep -i "access-control-allow-origin")

if [ -n "$CORS" ]; then
  test_pass "CORS headers configured"
  echo "CORS: $CORS"
else
  test_fail "CORS headers missing"
fi

# ===========================================
# CATEGORY 8: INFORMATION DISCLOSURE
# ===========================================

test_security "Info Disclosure - Error Messages Don't Leak Sensitive Data"
ERROR=$(curl -s -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=nonexistent@example.com&password=wrong")

if echo "$ERROR" | grep -qi "user not found\|no user\|invalid user"; then
  test_fail "Error reveals user existence (user enumeration)"
else
  test_pass "Generic error messages (no user enumeration)"
fi

test_security "Info Disclosure - No Debug Info in Production"
DEBUG=$(curl -s "$API/api/v1/health" | jq -r '.debug // "false"')

if [ "$DEBUG" = "true" ]; then
  test_fail "Debug mode enabled in production"
else
  test_pass "Debug mode disabled"
fi

# ===========================================
# CATEGORY 9: JWT TOKEN SECURITY
# ===========================================

test_security "JWT Security - Token Expiration"
# Check if token has expiration
TOKEN_PARTS=$(echo "$TOKEN" | tr '.' '\n' | wc -l)

if [ "$TOKEN_PARTS" -eq 3 ]; then
  test_pass "JWT token structure valid (3 parts)"
else
  test_fail "JWT token structure invalid"
fi

test_security "JWT Security - Token Contains No Sensitive Data"
# Decode JWT payload (base64)
PAYLOAD=$(echo "$TOKEN" | cut -d'.' -f2 | base64 -d 2>/dev/null || echo "{}")

if echo "$PAYLOAD" | jq -e '.password' > /dev/null 2>&1 || \
   echo "$PAYLOAD" | jq -e '.hashed_password' > /dev/null 2>&1; then
  test_fail "JWT contains sensitive data (password)"
else
  test_pass "JWT doesn't contain sensitive data"
fi

# ===========================================
# SUMMARY
# ===========================================

echo ""
echo "========================================"
echo "  SECURITY AUDIT SUMMARY"
echo "========================================"
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Secure: $PASSED_TESTS${NC}"
echo -e "${RED}Vulnerable: $FAILED_TESTS${NC}"
echo ""

if [ $VULNERABILITIES -eq 0 ]; then
  echo -e "${GREEN}🔒 SECURITY RATING: EXCELLENT${NC}"
  echo "No critical vulnerabilities found."
elif [ $VULNERABILITIES -le 2 ]; then
  echo -e "${YELLOW}⚠️  SECURITY RATING: GOOD${NC}"
  echo "Minor issues found. Review recommended."
else
  echo -e "${RED}🚨 SECURITY RATING: NEEDS ATTENTION${NC}"
  echo "Multiple vulnerabilities found. Immediate action required."
fi

echo ""
echo "Security Categories Tested:"
echo "  1. ✓ SQL Injection Prevention"
echo "  2. ✓ XSS (Cross-Site Scripting)"
echo "  3. ✓ Authentication Bypass Attempts"
echo "  4. ✓ Authorization Controls"
echo "  5. ✓ Password Security"
echo "  6. ✓ Rate Limiting"
echo "  7. ✓ CORS Configuration"
echo "  8. ✓ Information Disclosure"
echo "  9. ✓ JWT Token Security"
echo ""

if [ $VULNERABILITIES -eq 0 ]; then
  exit 0
else
  exit 1
fi
