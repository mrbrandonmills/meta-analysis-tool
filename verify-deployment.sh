#!/bin/bash
# Railway Deployment Verification Script
# Run this after completing all deployment steps

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="https://meta-analysis-tool-production.up.railway.app"
TEST_EMAIL="deploy-test@example.com"
TEST_PASSWORD="TestPass123!"
TEST_NAME="Deployment Test User"

echo "========================================="
echo "Railway Deployment Verification"
echo "========================================="
echo ""

# Test 1: Health Check
echo "TEST 1: Health Check - All Services"
echo "-------------------------------------------"
HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "${API_URL}/api/v1/health/detailed")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep HTTP_CODE | cut -d: -f2)
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | grep -v HTTP_CODE)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Health check endpoint accessible (HTTP 200)${NC}"
    echo "$HEALTH_BODY" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_BODY"

    # Check individual service statuses from nested checks object
    DB_STATUS=$(echo "$HEALTH_BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('checks',{}).get('database',{}).get('status','unknown'))" 2>/dev/null || echo "unknown")
    REDIS_STATUS=$(echo "$HEALTH_BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('checks',{}).get('redis',{}).get('status','unknown'))" 2>/dev/null || echo "unknown")
    CELERY_STATUS=$(echo "$HEALTH_BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('checks',{}).get('celery',{}).get('status','unknown'))" 2>/dev/null || echo "unknown")

    if [ "$DB_STATUS" = "healthy" ]; then
        echo -e "${GREEN}✓ Database: healthy${NC}"
    else
        echo -e "${RED}✗ Database: ${DB_STATUS}${NC}"
    fi

    if [ "$REDIS_STATUS" = "healthy" ]; then
        echo -e "${GREEN}✓ Redis: healthy${NC}"
    else
        echo -e "${RED}✗ Redis: ${REDIS_STATUS} - DEPLOY REDIS NOW${NC}"
    fi

    if [ "$CELERY_STATUS" = "healthy" ]; then
        echo -e "${GREEN}✓ Celery: healthy${NC}"
    else
        echo -e "${YELLOW}⚠ Celery: ${CELERY_STATUS} - DEPLOY WORKER SERVICE${NC}"
    fi
else
    echo -e "${RED}✗ Health check failed (HTTP ${HTTP_CODE})${NC}"
    echo "$HEALTH_BODY"
fi
echo ""

# Test 2: User Registration (Tests Database Migrations)
echo "TEST 2: User Registration (Database Migrations)"
echo "-------------------------------------------"
REGISTER_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${API_URL}/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"${TEST_EMAIL}\",\"password\":\"${TEST_PASSWORD}\",\"full_name\":\"${TEST_NAME}\"}")
HTTP_CODE=$(echo "$REGISTER_RESPONSE" | grep HTTP_CODE | cut -d: -f2)
REGISTER_BODY=$(echo "$REGISTER_RESPONSE" | grep -v HTTP_CODE)

if [ "$HTTP_CODE" -eq 201 ]; then
    echo -e "${GREEN}✓ User registration successful (HTTP 201)${NC}"
    echo -e "${GREEN}✓ Database migrations applied correctly${NC}"
    echo "$REGISTER_BODY" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_BODY"
elif [ "$HTTP_CODE" -eq 400 ] && echo "$REGISTER_BODY" | grep -q "already registered"; then
    echo -e "${GREEN}✓ Registration endpoint working (user already exists)${NC}"
    echo -e "${GREEN}✓ Database migrations applied correctly${NC}"
elif [ "$HTTP_CODE" -eq 500 ]; then
    echo -e "${RED}✗ Registration failed (HTTP 500) - DATABASE MIGRATIONS NOT RUN${NC}"
    echo "$REGISTER_BODY"
else
    echo -e "${YELLOW}⚠ Unexpected response (HTTP ${HTTP_CODE})${NC}"
    echo "$REGISTER_BODY"
fi
echo ""

# Test 3: User Login (Tests JWT Authentication)
echo "TEST 3: User Login (JWT Authentication)"
echo "-------------------------------------------"
LOGIN_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${API_URL}/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"${TEST_EMAIL}\",\"password\":\"${TEST_PASSWORD}\"}")
HTTP_CODE=$(echo "$LOGIN_RESPONSE" | grep HTTP_CODE | cut -d: -f2)
LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | grep -v HTTP_CODE)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ User login successful (HTTP 200)${NC}"
    echo -e "${GREEN}✓ JWT authentication working${NC}"

    # Extract access token
    ACCESS_TOKEN=$(echo "$LOGIN_BODY" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$ACCESS_TOKEN" ]; then
        echo -e "${GREEN}✓ Access token received${NC}"
        echo "Token (first 20 chars): ${ACCESS_TOKEN:0:20}..."
    fi
else
    echo -e "${YELLOW}⚠ Login failed (HTTP ${HTTP_CODE}) - May need to register first${NC}"
    echo "$LOGIN_BODY"
fi
echo ""

# Test 4: Protected Endpoint (Tests Redis Session)
if [ -n "$ACCESS_TOKEN" ]; then
    echo "TEST 4: Protected Endpoint (Redis Session)"
    echo "-------------------------------------------"
    ME_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "${API_URL}/api/v1/auth/me" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}")
    HTTP_CODE=$(echo "$ME_RESPONSE" | grep HTTP_CODE | cut -d: -f2)
    ME_BODY=$(echo "$ME_RESPONSE" | grep -v HTTP_CODE)

    if [ "$HTTP_CODE" -eq 200 ]; then
        echo -e "${GREEN}✓ Protected endpoint accessible (HTTP 200)${NC}"
        echo -e "${GREEN}✓ Redis session management working${NC}"
        echo "$ME_BODY" | python3 -m json.tool 2>/dev/null || echo "$ME_BODY"
    else
        echo -e "${RED}✗ Protected endpoint failed (HTTP ${HTTP_CODE})${NC}"
        echo "$ME_BODY"
    fi
    echo ""
fi

# Summary
echo "========================================="
echo "DEPLOYMENT VERIFICATION SUMMARY"
echo "========================================="
echo ""

PASS_COUNT=0
FAIL_COUNT=0

# Count results based on statuses
if [ "$DB_STATUS" = "healthy" ]; then ((PASS_COUNT++)); else ((FAIL_COUNT++)); fi
if [ "$REDIS_STATUS" = "healthy" ]; then ((PASS_COUNT++)); else ((FAIL_COUNT++)); fi
if [ "$CELERY_STATUS" = "healthy" ]; then ((PASS_COUNT++)); else ((FAIL_COUNT++)); fi

echo "Database:     ${DB_STATUS}"
echo "Redis:        ${REDIS_STATUS}"
echo "Celery:       ${CELERY_STATUS}"
echo ""

if [ $PASS_COUNT -eq 3 ]; then
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}🎉 ALL SYSTEMS OPERATIONAL${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}Platform ready for board meeting!${NC}"
    exit 0
else
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}⚠️  DEPLOYMENT INCOMPLETE${NC}"
    echo -e "${RED}=========================================${NC}"
    echo ""
    echo "Action items:"
    if [ "$REDIS_STATUS" != "healthy" ]; then
        echo -e "${RED}1. Deploy Redis database (see FIX 1 in guide)${NC}"
    fi
    if [ "$DB_STATUS" != "healthy" ]; then
        echo -e "${RED}2. Check database connection and migrations${NC}"
    fi
    if [ "$CELERY_STATUS" != "healthy" ]; then
        echo -e "${RED}3. Deploy Celery worker service (see FIX 3 in guide)${NC}"
    fi
    echo ""
    echo "See: RAILWAY_DEPLOYMENT_GUIDE.md"
    exit 1
fi
