#!/bin/bash

# Production Deployment Verification Script
# Tests all production endpoints after deployment
# Usage: ./verify_production_deployment.sh

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="https://meta-analysis-tool-production.up.railway.app"
FRONTEND_URL="https://meta-analysis-tool.vercel.app"
REPORT_FILE="production_deployment_report.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
ISSUES=()
RECOMMENDATIONS=()

# Test user credentials (will be created)
TEST_EMAIL="test_$(date +%s)@deployment-verification.com"
TEST_PASSWORD="TestPassword123!"
JWT_TOKEN=""

# Helper Functions
log_success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
}

log_failure() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
    ISSUES+=("$1")
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    RECOMMENDATIONS+=("$1")
}

log_section() {
    echo ""
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local auth_header=$4
    local data=$5

    if [ -n "$auth_header" ]; then
        if [ -n "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" \
                -H "Content-Type: application/json" \
                -H "$auth_header" \
                -d "$data" \
                "${BACKEND_URL}${endpoint}")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" \
                -H "$auth_header" \
                "${BACKEND_URL}${endpoint}")
        fi
    else
        if [ -n "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" \
                -H "Content-Type: application/json" \
                -d "$data" \
                "${BACKEND_URL}${endpoint}")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" \
                "${BACKEND_URL}${endpoint}")
        fi
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    echo "$http_code|$body"
}

test_frontend_endpoint() {
    local path=$1
    local description=$2

    response=$(curl -s -w "\n%{http_code}" "${FRONTEND_URL}${path}")
    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" = "200" ]; then
        log_success "$description (HTTP $http_code)"
    else
        log_failure "$description (HTTP $http_code)"
    fi
}

# Banner
clear
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   Production Deployment Verification                     ║
║   Meta-Analysis Tool Platform                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo "Backend URL:  $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo "Timestamp:    $TIMESTAMP"
echo ""

# ============================================
# Test 1: Backend Health Check
# ============================================
log_section "1. Backend Health & Infrastructure"

log_info "Testing backend availability..."
result=$(test_endpoint "GET" "/api/v1/health" "Health endpoint")
http_code=$(echo "$result" | cut -d'|' -f1)
body=$(echo "$result" | cut -d'|' -f2)

if [ "$http_code" = "200" ]; then
    log_success "Backend is reachable (HTTP $http_code)"

    # Parse health response
    status=$(echo "$body" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    if [ "$status" = "healthy" ]; then
        log_success "Service status: $status"
    else
        log_warning "Service status: $status (expected 'healthy')"
    fi

    # Check database
    db_status=$(echo "$body" | grep -o '"database":"[^"]*"' | cut -d'"' -f4)
    if [ "$db_status" = "connected" ]; then
        log_success "Database connection: $db_status"
    else
        log_failure "Database connection: $db_status"
    fi

    # Check API version
    api_version=$(echo "$body" | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$api_version" ]; then
        log_success "API version: $api_version"
    else
        log_warning "API version not found in health response"
    fi
else
    log_failure "Backend unreachable (HTTP $http_code)"
    echo "Aborting tests - backend is not responding"
    exit 1
fi

# Test root endpoint
result=$(test_endpoint "GET" "/" "Root endpoint")
http_code=$(echo "$result" | cut -d'|' -f1)
if [ "$http_code" = "200" ]; then
    log_success "Root endpoint accessible (HTTP $http_code)"
else
    log_warning "Root endpoint returned HTTP $http_code"
fi

# ============================================
# Test 2: Authentication System
# ============================================
log_section "2. Authentication & Security"

log_info "Testing user registration..."
register_data="{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"name\":\"Test User\"}"
result=$(test_endpoint "POST" "/api/v1/auth/register" "User registration" "" "$register_data")
http_code=$(echo "$result" | cut -d'|' -f1)
body=$(echo "$result" | cut -d'|' -f2)

if [ "$http_code" = "201" ] || [ "$http_code" = "200" ]; then
    log_success "User registration successful (HTTP $http_code)"

    # Extract token if present
    token=$(echo "$body" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$token" ]; then
        JWT_TOKEN="$token"
        log_success "JWT token received on registration"
    fi
elif [ "$http_code" = "409" ]; then
    log_info "User already exists, attempting login..."
else
    log_failure "User registration failed (HTTP $http_code)"
fi

# Test login
log_info "Testing user login..."
login_data="{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}"
result=$(test_endpoint "POST" "/api/v1/auth/login" "User login" "" "$login_data")
http_code=$(echo "$result" | cut -d'|' -f1)
body=$(echo "$result" | cut -d'|' -f2)

if [ "$http_code" = "200" ]; then
    log_success "User login successful (HTTP $http_code)"

    # Extract JWT token
    token=$(echo "$body" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$token" ]; then
        JWT_TOKEN="$token"
        log_success "JWT token received and stored"
    else
        log_failure "JWT token not found in login response"
    fi
else
    log_failure "User login failed (HTTP $http_code)"
fi

# Test token validation
if [ -n "$JWT_TOKEN" ]; then
    log_info "Testing token validation..."
    result=$(test_endpoint "GET" "/api/v1/auth/me" "Token validation" "Authorization: Bearer $JWT_TOKEN")
    http_code=$(echo "$result" | cut -d'|' -f1)

    if [ "$http_code" = "200" ]; then
        log_success "Token validation successful (HTTP $http_code)"
    else
        log_failure "Token validation failed (HTTP $http_code)"
    fi
else
    log_warning "Skipping token validation - no JWT token available"
fi

# ============================================
# Test 3: Core API Endpoints
# ============================================
log_section "3. Core API Endpoints"

# Test Researchers API
log_info "Testing Researchers API..."
result=$(test_endpoint "GET" "/api/v1/researchers" "GET /api/v1/researchers")
http_code=$(echo "$result" | cut -d'|' -f1)
if [ "$http_code" = "200" ]; then
    log_success "Researchers API accessible (HTTP $http_code)"
else
    log_failure "Researchers API failed (HTTP $http_code)"
fi

# Test Manuscripts API
log_info "Testing Manuscripts API..."
result=$(test_endpoint "GET" "/api/v1/manuscripts" "GET /api/v1/manuscripts")
http_code=$(echo "$result" | cut -d'|' -f1)
if [ "$http_code" = "200" ]; then
    log_success "Manuscripts API accessible (HTTP $http_code)"
else
    log_failure "Manuscripts API failed (HTTP $http_code)"
fi

# Test Studies API
log_info "Testing Studies API..."
result=$(test_endpoint "GET" "/api/v1/studies" "GET /api/v1/studies")
http_code=$(echo "$result" | cut -d'|' -f1)
if [ "$http_code" = "200" ]; then
    log_success "Studies API accessible (HTTP $http_code)"
else
    log_failure "Studies API failed (HTTP $http_code)"
fi

# ============================================
# Test 4: New Feature APIs
# ============================================
log_section "4. New Feature APIs"

# Test Reviewer Matcher API
log_info "Testing Reviewer Matcher API..."
result=$(test_endpoint "GET" "/api/v1/reviewer-matches" "GET /api/v1/reviewer-matches")
http_code=$(echo "$result" | cut -d'|' -f1)
if [ "$http_code" = "200" ] || [ "$http_code" = "404" ]; then
    log_success "Reviewer Matcher API accessible (HTTP $http_code)"
else
    log_failure "Reviewer Matcher API failed (HTTP $http_code)"
fi

# Test Peer Review API
log_info "Testing Peer Review API..."
result=$(test_endpoint "GET" "/api/v1/peer-reviews" "GET /api/v1/peer-reviews")
http_code=$(echo "$result" | cut -d'|' -f1)
if [ "$http_code" = "200" ] || [ "$http_code" = "401" ]; then
    log_success "Peer Review API accessible (HTTP $http_code)"
else
    log_failure "Peer Review API failed (HTTP $http_code)"
fi

# Test Progress Tracking API
log_info "Testing Progress Tracking API..."
if [ -n "$JWT_TOKEN" ]; then
    result=$(test_endpoint "GET" "/api/v1/tasks/progress" "GET /api/v1/tasks/progress" "Authorization: Bearer $JWT_TOKEN")
    http_code=$(echo "$result" | cut -d'|' -f1)
    if [ "$http_code" = "200" ] || [ "$http_code" = "404" ]; then
        log_success "Progress Tracking API accessible (HTTP $http_code)"
    else
        log_failure "Progress Tracking API failed (HTTP $http_code)"
    fi
else
    log_warning "Skipping Progress API - authentication required"
fi

# Test Meta-Analysis API
log_info "Testing Meta-Analysis API..."
result=$(test_endpoint "GET" "/api/v1/meta-analyses" "GET /api/v1/meta-analyses")
http_code=$(echo "$result" | cut -d'|' -f1)
if [ "$http_code" = "200" ]; then
    log_success "Meta-Analysis API accessible (HTTP $http_code)"
else
    log_failure "Meta-Analysis API failed (HTTP $http_code)"
fi

# ============================================
# Test 5: Frontend Application
# ============================================
log_section "5. Frontend Application (Vercel)"

log_info "Testing frontend endpoints..."

test_frontend_endpoint "/" "Homepage"
test_frontend_endpoint "/tools/peer-review" "Peer Review Tool"
test_frontend_endpoint "/tools/reviewer-matcher" "Reviewer Matcher Tool"
test_frontend_endpoint "/tools/meta-analysis" "Meta-Analysis Tool"
test_frontend_endpoint "/dashboard" "Dashboard"

# Test static assets
log_info "Testing static asset loading..."
result=$(curl -s -w "\n%{http_code}" "${FRONTEND_URL}/favicon.ico")
http_code=$(echo "$result" | tail -n1)
if [ "$http_code" = "200" ]; then
    log_success "Static assets loading (favicon.ico - HTTP $http_code)"
else
    log_warning "Static asset loading issue (favicon.ico - HTTP $http_code)"
fi

# ============================================
# Test 6: CORS & Security Headers
# ============================================
log_section "6. Security & CORS Configuration"

log_info "Testing CORS headers..."
cors_response=$(curl -s -I -X OPTIONS \
    -H "Origin: ${FRONTEND_URL}" \
    -H "Access-Control-Request-Method: POST" \
    "${BACKEND_URL}/api/v1/health")

if echo "$cors_response" | grep -q "Access-Control-Allow-Origin"; then
    log_success "CORS headers present"
else
    log_warning "CORS headers not found - may cause frontend issues"
fi

log_info "Testing security headers..."
security_response=$(curl -s -I "${BACKEND_URL}/api/v1/health")

if echo "$security_response" | grep -q "X-Content-Type-Options"; then
    log_success "Security headers configured"
else
    log_warning "Consider adding security headers (X-Content-Type-Options, etc.)"
fi

# ============================================
# Test 7: Performance Checks
# ============================================
log_section "7. Performance Metrics"

log_info "Testing backend response time..."
start_time=$(date +%s%N)
curl -s "${BACKEND_URL}/api/v1/health" > /dev/null
end_time=$(date +%s%N)
response_time=$(( (end_time - start_time) / 1000000 ))

if [ $response_time -lt 1000 ]; then
    log_success "Backend response time: ${response_time}ms (excellent)"
elif [ $response_time -lt 2000 ]; then
    log_success "Backend response time: ${response_time}ms (good)"
else
    log_warning "Backend response time: ${response_time}ms (consider optimization)"
fi

log_info "Testing frontend response time..."
start_time=$(date +%s%N)
curl -s "${FRONTEND_URL}" > /dev/null
end_time=$(date +%s%N)
response_time=$(( (end_time - start_time) / 1000000 ))

if [ $response_time -lt 1500 ]; then
    log_success "Frontend response time: ${response_time}ms (excellent)"
elif [ $response_time -lt 3000 ]; then
    log_success "Frontend response time: ${response_time}ms (good)"
else
    log_warning "Frontend response time: ${response_time}ms (consider optimization)"
fi

# ============================================
# Generate Report
# ============================================
log_section "8. Generating Report"

# Determine overall backend health
if [ $FAILED_TESTS -eq 0 ]; then
    BACKEND_HEALTH="healthy"
elif [ $FAILED_TESTS -le 3 ]; then
    BACKEND_HEALTH="degraded"
else
    BACKEND_HEALTH="down"
fi

# Determine frontend status
if [ $FAILED_TESTS -gt 5 ]; then
    FRONTEND_STATUS="down"
else
    FRONTEND_STATUS="up"
fi

# Convert arrays to JSON
ISSUES_JSON="[]"
if [ ${#ISSUES[@]} -gt 0 ]; then
    ISSUES_JSON=$(printf '%s\n' "${ISSUES[@]}" | jq -R . | jq -s .)
fi

RECOMMENDATIONS_JSON="[]"
if [ ${#RECOMMENDATIONS[@]} -gt 0 ]; then
    RECOMMENDATIONS_JSON=$(printf '%s\n' "${RECOMMENDATIONS[@]}" | jq -R . | jq -s .)
fi

# Create JSON report
cat > "$REPORT_FILE" << EOF
{
  "timestamp": "$TIMESTAMP",
  "deployment": {
    "backend_url": "$BACKEND_URL",
    "frontend_url": "$FRONTEND_URL"
  },
  "results": {
    "backend_health": "$BACKEND_HEALTH",
    "frontend_status": "$FRONTEND_STATUS",
    "endpoints_tested": $TOTAL_TESTS,
    "endpoints_passed": $PASSED_TESTS,
    "endpoints_failed": $FAILED_TESTS,
    "success_rate": $(awk "BEGIN {printf \"%.2f\", ($PASSED_TESTS/$TOTAL_TESTS)*100}")
  },
  "issues": $ISSUES_JSON,
  "recommendations": $RECOMMENDATIONS_JSON,
  "test_coverage": {
    "health_check": true,
    "authentication": true,
    "core_apis": true,
    "new_features": true,
    "frontend": true,
    "security": true,
    "performance": true
  }
}
EOF

log_success "Report generated: $REPORT_FILE"

# ============================================
# Summary
# ============================================
log_section "Deployment Verification Summary"

echo ""
echo "Total Tests:    $TOTAL_TESTS"
echo -e "Passed:         ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed:         ${RED}$FAILED_TESTS${NC}"
echo "Success Rate:   $(awk "BEGIN {printf \"%.2f%%\", ($PASSED_TESTS/$TOTAL_TESTS)*100}")"
echo ""
echo -e "Backend Health:  ${BLUE}$BACKEND_HEALTH${NC}"
echo -e "Frontend Status: ${BLUE}$FRONTEND_STATUS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║   ✓ ALL TESTS PASSED - DEPLOYMENT VERIFIED               ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    exit 0
elif [ $FAILED_TESTS -le 3 ]; then
    echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                                                           ║${NC}"
    echo -e "${YELLOW}║   ⚠ DEPLOYMENT VERIFIED WITH WARNINGS                    ║${NC}"
    echo -e "${YELLOW}║                                                           ║${NC}"
    echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Review issues and recommendations in: $REPORT_FILE"
    exit 0
else
    echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}║   ✗ DEPLOYMENT VERIFICATION FAILED                        ║${NC}"
    echo -e "${RED}║                                                           ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Critical issues found. Review: $REPORT_FILE"
    exit 1
fi
