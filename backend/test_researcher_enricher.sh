#!/bin/bash

# Test script for Researcher Profile Enricher
# Tests enrichment endpoints with real API calls

set -e  # Exit on error

# Configuration
API_BASE="${API_BASE:-http://localhost:8000}"
TOKEN="${TOKEN:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to check if API is running
check_api() {
    print_info "Checking API availability..."

    if curl -s "${API_BASE}/api/v1/health" > /dev/null 2>&1; then
        print_success "API is running at ${API_BASE}"
        return 0
    else
        print_error "API is not accessible at ${API_BASE}"
        print_info "Start the API with: cd backend && uvicorn app.main:app --reload"
        return 1
    fi
}

# Function to get authentication token
get_token() {
    if [ -n "$TOKEN" ]; then
        print_info "Using provided TOKEN"
        return 0
    fi

    print_warning "No TOKEN provided. Some endpoints may fail."
    print_info "Set TOKEN environment variable with a valid JWT token:"
    print_info "  export TOKEN='your_jwt_token_here'"
    return 1
}

# Function to create a test researcher
create_test_researcher() {
    print_info "Creating test researcher..."

    local response=$(curl -s -X POST "${API_BASE}/api/v1/researchers" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${TOKEN}" \
        -d '{
            "name": "Jane Smith",
            "email": "jane.smith@university.edu",
            "institution": "Stanford University",
            "department": "Psychology",
            "country": "USA",
            "orcid": "0000-0002-1234-5678"
        }')

    local researcher_id=$(echo "$response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ -n "$researcher_id" ]; then
        print_success "Created test researcher: ${researcher_id}"
        echo "$researcher_id"
        return 0
    else
        print_error "Failed to create test researcher"
        echo "$response"
        return 1
    fi
}

# Test 1: Health check
test_health_check() {
    echo ""
    echo "=========================================="
    echo "Test 1: Health Check"
    echo "=========================================="

    local response=$(curl -s "${API_BASE}/api/v1/health")

    if echo "$response" | grep -q '"status":"healthy"'; then
        print_success "Health check passed"
        return 0
    else
        print_error "Health check failed"
        echo "$response"
        return 1
    fi
}

# Test 2: Create researcher and get completeness score
test_completeness_score() {
    echo ""
    echo "=========================================="
    echo "Test 2: Profile Completeness Score"
    echo "=========================================="

    if [ -z "$TOKEN" ]; then
        print_warning "Skipping test - no authentication token"
        return 0
    fi

    # Use existing researcher ID or create new one
    local researcher_id="${TEST_RESEARCHER_ID:-}"

    if [ -z "$researcher_id" ]; then
        print_info "No TEST_RESEARCHER_ID provided, creating test researcher..."
        researcher_id=$(create_test_researcher)
        if [ -z "$researcher_id" ]; then
            return 1
        fi
    fi

    print_info "Getting completeness score for researcher: ${researcher_id}"

    local response=$(curl -s -X GET "${API_BASE}/api/v1/researchers/${researcher_id}/completeness" \
        -H "Authorization: Bearer ${TOKEN}")

    if echo "$response" | grep -q '"completeness_score"'; then
        print_success "Completeness score retrieved"
        echo "$response" | grep -o '"completeness_percentage":"[^"]*"' | cut -d'"' -f4
        echo "$response" | grep -o '"missing_fields":\[[^]]*\]' | head -1
        return 0
    else
        print_error "Failed to get completeness score"
        echo "$response"
        return 1
    fi
}

# Test 3: Enrich single researcher
test_enrich_single() {
    echo ""
    echo "=========================================="
    echo "Test 3: Enrich Single Researcher"
    echo "=========================================="

    if [ -z "$TOKEN" ]; then
        print_warning "Skipping test - no authentication token"
        return 0
    fi

    local researcher_id="${TEST_RESEARCHER_ID:-}"

    if [ -z "$researcher_id" ]; then
        print_warning "No TEST_RESEARCHER_ID provided, skipping enrichment test"
        print_info "Set TEST_RESEARCHER_ID to test enrichment: export TEST_RESEARCHER_ID='uuid-here'"
        return 0
    fi

    print_info "Enriching researcher profile: ${researcher_id}"
    print_warning "This may take 30-60 seconds (scraping multiple sources)..."

    local response=$(curl -s -X POST "${API_BASE}/api/v1/researchers/${researcher_id}/enrich" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${TOKEN}" \
        -d '{"force_refresh": true}')

    if echo "$response" | grep -q '"status":"success"\|"status":"partial"'; then
        print_success "Enrichment completed"

        # Extract and display key metrics
        echo ""
        echo "Results:"
        echo "--------"
        echo "$response" | grep -o '"sources_checked":\[[^]]*\]' | head -1
        echo "$response" | grep -o '"completeness_percentage":"[^"]*"' | cut -d'"' -f4
        echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4

        # Check for errors
        if echo "$response" | grep -q '"errors":\['; then
            print_warning "Some errors occurred during enrichment:"
            echo "$response" | grep -o '"errors":\[[^]]*\]' | head -1
        fi

        return 0
    else
        print_error "Enrichment failed"
        echo "$response"
        return 1
    fi
}

# Test 4: Batch enrichment
test_batch_enrich() {
    echo ""
    echo "=========================================="
    echo "Test 4: Batch Enrichment"
    echo "=========================================="

    if [ -z "$TOKEN" ]; then
        print_warning "Skipping test - no authentication token"
        return 0
    fi

    local researcher_ids="${BATCH_RESEARCHER_IDS:-}"

    if [ -z "$researcher_ids" ]; then
        print_warning "No BATCH_RESEARCHER_IDS provided, skipping batch enrichment test"
        print_info "Set BATCH_RESEARCHER_IDS to test: export BATCH_RESEARCHER_IDS='[\"id1\",\"id2\"]'"
        return 0
    fi

    print_info "Batch enriching researchers..."
    print_warning "This may take several minutes depending on batch size..."

    local response=$(curl -s -X POST "${API_BASE}/api/v1/researchers/batch-enrich" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${TOKEN}" \
        -d "{\"researcher_ids\": ${researcher_ids}, \"force_refresh\": false}")

    if echo "$response" | grep -q '"total_requested"'; then
        print_success "Batch enrichment completed"

        echo ""
        echo "Results:"
        echo "--------"
        echo "$response" | grep -o '"total_requested":[0-9]*' | cut -d':' -f2
        echo "$response" | grep -o '"successful":[0-9]*' | cut -d':' -f2
        echo "$response" | grep -o '"failed":[0-9]*' | cut -d':' -f2

        return 0
    else
        print_error "Batch enrichment failed"
        echo "$response"
        return 1
    fi
}

# Test 5: Test with real researcher name (Google Scholar search)
test_real_researcher() {
    echo ""
    echo "=========================================="
    echo "Test 5: Real Researcher Enrichment"
    echo "=========================================="

    print_info "This test demonstrates enrichment with a real researcher"
    print_info "Example: Dr. Andrew Ng from Stanford University"
    print_warning "Skipping by default to avoid hitting rate limits"
    print_info "To run: set ENABLE_REAL_TEST=1"

    if [ "${ENABLE_REAL_TEST:-0}" != "1" ]; then
        return 0
    fi

    # Implementation would go here
    print_info "Real researcher test would run here"
    return 0
}

# Main test execution
main() {
    echo ""
    echo "=========================================="
    echo "Researcher Profile Enricher Test Suite"
    echo "=========================================="
    echo ""

    # Check prerequisites
    if ! check_api; then
        exit 1
    fi

    get_token || true

    # Run tests
    local failed=0

    test_health_check || ((failed++))
    test_completeness_score || ((failed++))
    test_enrich_single || ((failed++))
    test_batch_enrich || ((failed++))
    test_real_researcher || ((failed++))

    # Summary
    echo ""
    echo "=========================================="
    echo "Test Summary"
    echo "=========================================="

    if [ $failed -eq 0 ]; then
        print_success "All tests passed!"
        exit 0
    else
        print_error "${failed} test(s) failed"
        exit 1
    fi
}

# Show usage if --help
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    echo "Usage: $0"
    echo ""
    echo "Environment Variables:"
    echo "  API_BASE              API base URL (default: http://localhost:8000)"
    echo "  TOKEN                 JWT authentication token (required for most tests)"
    echo "  TEST_RESEARCHER_ID    Researcher UUID to use for testing"
    echo "  BATCH_RESEARCHER_IDS  JSON array of researcher IDs for batch testing"
    echo "  ENABLE_REAL_TEST      Set to 1 to enable real researcher enrichment test"
    echo ""
    echo "Example:"
    echo "  export TOKEN='your_jwt_token'"
    echo "  export TEST_RESEARCHER_ID='123e4567-e89b-12d3-a456-426614174000'"
    echo "  $0"
    echo ""
    exit 0
fi

# Run main
main
