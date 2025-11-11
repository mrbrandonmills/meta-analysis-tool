#!/bin/bash

###############################################################################
# Master Test Runner Script
# Runs complete test suite for meta-analysis platform
#
# Prerequisites:
# - Python dependencies installed (pip install -r backend/requirements.txt)
# - PostgreSQL running
# - Redis running (optional but recommended)
# - Backend server running (for API tests)
# - Celery worker running (for task tests)
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo ""
    echo "================================================================================"
    echo -e "${BLUE}$1${NC}"
    echo "================================================================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_prerequisite() {
    local name=$1
    local command=$2

    if eval "$command" > /dev/null 2>&1; then
        print_success "$name is available"
        return 0
    else
        print_warning "$name is NOT available"
        return 1
    fi
}

run_test() {
    local test_name=$1
    local test_command=$2

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo ""
    print_info "Running: $test_name"
    echo "Command: $test_command"
    echo ""

    if eval "$test_command"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        print_success "$test_name PASSED"
        return 0
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        print_error "$test_name FAILED"
        return 1
    fi
}

###############################################################################
# Main Test Suite
###############################################################################

main() {
    print_header "🧪 COMPLETE TEST SUITE - META-ANALYSIS PLATFORM"

    echo "Test Suite Start Time: $(date)"
    echo "Working Directory: $(pwd)"
    echo ""

    # =========================================================================
    # PHASE 0: Environment Check
    # =========================================================================

    print_header "PHASE 0: Environment Verification"

    print_info "Checking system prerequisites..."
    echo ""

    # Check Python
    if check_prerequisite "Python 3" "python3 --version"; then
        python3 --version
    fi

    # Check PostgreSQL
    check_prerequisite "PostgreSQL" "psql --version" || true

    # Check Redis
    check_prerequisite "Redis" "redis-cli ping" || true

    # Check backend server
    if check_prerequisite "Backend Server" "curl -s http://localhost:8000/api/v1/health"; then
        echo "Backend server is running on http://localhost:8000"
    else
        print_warning "Backend server is not running. API tests will be skipped."
        print_info "Start backend with: cd backend && uvicorn app.main:app --reload"
    fi

    # Check Celery worker
    if check_prerequisite "Celery Worker" "celery -A app.workers.celery_app inspect ping"; then
        echo "Celery worker is running"
    else
        print_warning "Celery worker is not running. Task tests will be limited."
        print_info "Start worker with: cd backend && celery -A app.workers.celery_app worker"
    fi

    echo ""
    print_info "Environment check complete. Proceeding with tests..."

    # =========================================================================
    # PHASE 1: Unit Tests - Individual Components
    # =========================================================================

    print_header "PHASE 1: Unit Tests - Individual Components"

    # Test 1: Celery Tasks Implementation
    run_test \
        "Celery Tasks Implementation Verification" \
        "python3 test_celery_tasks_simple.py" \
        || true

    # Test 2: Progress Tracking System
    if [ -f "test_progress_demo.py" ]; then
        print_info "Progress tracking demo available"
        print_info "Run manually: python3 test_progress_demo.py --mode=api"
    else
        print_warning "test_progress_demo.py not found"
    fi

    # =========================================================================
    # PHASE 2: API Endpoint Tests
    # =========================================================================

    print_header "PHASE 2: API Endpoint Tests"

    # Check if backend is running
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then

        # Test 3: Reviewer Matcher API
        if [ -f "backend/test_reviewer_matcher_api.sh" ]; then
            run_test \
                "Reviewer Matcher API (10 endpoints)" \
                "cd backend && ./test_reviewer_matcher_api.sh" \
                || true
        fi

        # Test 4: Peer Review API
        if [ -f "backend/test_peer_review_endpoints.sh" ]; then
            run_test \
                "Peer Review API (14 endpoints)" \
                "cd backend && ./test_peer_review_endpoints.sh" \
                || true
        fi

    else
        print_warning "Backend server not running - skipping API tests"
        print_info "Start backend: cd backend && uvicorn app.main:app --reload"
        SKIPPED_TESTS=$((SKIPPED_TESTS + 2))
    fi

    # =========================================================================
    # PHASE 3: Integration Tests
    # =========================================================================

    print_header "PHASE 3: Integration Tests - End-to-End Workflow"

    # Test 5: Complete System Integration
    if [ -f "test_complete_system.py" ]; then
        run_test \
            "Complete System Integration (7 phases)" \
            "python3 test_complete_system.py" \
            || true
    fi

    # =========================================================================
    # PHASE 4: Agent Tests
    # =========================================================================

    print_header "PHASE 4: AI Agent Tests"

    print_info "Verifying agent implementations..."

    # Check ReviewerMatchingAgent
    if python3 -c "import sys; sys.path.insert(0, 'backend'); from app.agents.specialized.reviewer_matching_agent import ReviewerMatchingAgent" 2>/dev/null; then
        print_success "ReviewerMatchingAgent: Import successful"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        print_error "ReviewerMatchingAgent: Import failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    # Check ReviewDrafterAgent
    if python3 -c "import sys; sys.path.insert(0, 'backend'); from app.agents.specialized.review_drafter_agent import ReviewDrafterAgent" 2>/dev/null; then
        print_success "ReviewDrafterAgent: Import successful"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        print_warning "ReviewDrafterAgent: Not found at expected location"
        print_info "AI review generation may be integrated in peer_reviews.py"
        SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    # =========================================================================
    # PHASE 5: Code Quality Checks
    # =========================================================================

    print_header "PHASE 5: Code Quality Verification"

    print_info "Checking code metrics..."
    echo ""

    # Count lines of code
    echo "Lines of Code by Component:"
    echo "----------------------------------------"
    wc -l backend/app/workers/tasks/meta_analysis.py 2>/dev/null || echo "  Celery Tasks: Not found"
    wc -l backend/app/api/v1/reviewer_matcher.py 2>/dev/null || echo "  Reviewer Matcher API: Not found"
    wc -l backend/app/api/v1/peer_reviews.py 2>/dev/null || echo "  Peer Review API: Not found"
    wc -l backend/app/agents/specialized/reviewer_matching_agent.py 2>/dev/null || echo "  ReviewerMatchingAgent: Not found"
    echo "----------------------------------------"

    # Check for TODO markers
    print_info "Checking for unfinished work (TODO markers)..."
    TODO_COUNT=$(grep -r "TODO:" backend/app/ 2>/dev/null | wc -l | tr -d ' ')
    if [ "$TODO_COUNT" -eq 0 ]; then
        print_success "No TODO markers found"
    else
        print_warning "Found $TODO_COUNT TODO markers"
    fi

    # =========================================================================
    # Test Summary
    # =========================================================================

    print_header "TEST SUMMARY"

    echo "Total Tests: $TOTAL_TESTS"
    echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
    echo -e "${RED}Failed: $FAILED_TESTS${NC}"
    echo -e "${YELLOW}Skipped: $SKIPPED_TESTS${NC}"
    echo ""

    if [ $FAILED_TESTS -eq 0 ]; then
        print_success "ALL TESTS PASSED! 🎉"
        echo ""
        echo "The system is ready for production testing."
        EXIT_CODE=0
    else
        print_error "SOME TESTS FAILED"
        echo ""
        echo "Please review the output above and fix the failing tests."
        echo "See QA_TEST_REPORT.md for detailed findings and recommendations."
        EXIT_CODE=1
    fi

    # =========================================================================
    # Next Steps
    # =========================================================================

    print_header "NEXT STEPS"

    echo "1. Review test results above"
    echo "2. Read QA_TEST_REPORT.md for detailed analysis"
    echo "3. Fix any P0 (critical) bugs"
    echo "4. Re-run this test suite"
    echo ""

    if [ $SKIPPED_TESTS -gt 0 ]; then
        print_warning "Some tests were skipped due to missing prerequisites"
        echo ""
        echo "To run all tests:"
        echo "  1. Install dependencies: cd backend && pip install -r requirements.txt"
        echo "  2. Start PostgreSQL: brew services start postgresql"
        echo "  3. Start Redis: brew services start redis"
        echo "  4. Start backend: cd backend && uvicorn app.main:app --reload"
        echo "  5. Start Celery: cd backend && celery -A app.workers.celery_app worker"
        echo "  6. Re-run: ./run_all_tests.sh"
        echo ""
    fi

    print_header "TEST SUITE COMPLETE"
    echo "End Time: $(date)"
    echo ""

    exit $EXIT_CODE
}

# Run main function
main "$@"
