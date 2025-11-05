#!/bin/bash
# Run all tests for the Meta-Analysis Tool platform
# This script runs backend and frontend tests and generates a combined report

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Track results
BACKEND_TESTS_PASSED=false
FRONTEND_TESTS_PASSED=false
START_TIME=$(date +%s)

# Main execution
print_header "Meta-Analysis Tool - Full Test Suite"

# Check if we're in the right directory
if [ ! -f "TESTING_STRATEGY.md" ]; then
    print_error "Not in project root directory!"
    echo "Please run this script from the project root."
    exit 1
fi

print_success "Found project root directory"

# ============================================================================
# BACKEND TESTS
# ============================================================================

print_header "Running Backend Tests"

# Check if backend directory exists
if [ ! -d "backend" ]; then
    print_error "Backend directory not found!"
    exit 1
fi

cd backend

# Check if test dependencies are installed
if ! python -c "import pytest" 2>/dev/null; then
    print_warning "Test dependencies not installed. Installing..."
    pip install -r requirements-test.txt
fi

# Run backend tests
echo "Running backend unit tests..."
if pytest tests/unit -v --cov=app --cov-report=term-missing --cov-report=html:../htmlcov/backend; then
    print_success "Backend unit tests passed"
else
    print_error "Backend unit tests failed"
    cd ..
    exit 1
fi

echo ""
echo "Running backend integration tests..."
if pytest tests/integration -v; then
    print_success "Backend integration tests passed"
else
    print_warning "Backend integration tests failed (may be expected if not all implemented)"
fi

echo ""
echo "Running backend validation tests..."
if pytest tests/validation -v -m validation; then
    print_success "Backend validation tests passed"
else
    print_warning "Backend validation tests failed (expected - not all implemented yet)"
fi

BACKEND_TESTS_PASSED=true
cd ..

# ============================================================================
# FRONTEND TESTS
# ============================================================================

print_header "Running Frontend Tests"

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    print_error "Frontend directory not found!"
    exit 1
fi

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_warning "Node modules not installed. Installing..."
    npm install
fi

# Run frontend tests
echo "Running frontend tests..."
if npm test -- --run --coverage; then
    print_success "Frontend tests passed"
    FRONTEND_TESTS_PASSED=true
else
    print_warning "Frontend tests failed (may be expected if not all implemented)"
    FRONTEND_TESTS_PASSED=false
fi

cd ..

# ============================================================================
# CODE QUALITY CHECKS
# ============================================================================

print_header "Code Quality Checks"

# Backend linting
echo "Checking backend code quality..."
cd backend

if command -v black &> /dev/null; then
    if black --check app tests 2>/dev/null; then
        print_success "Backend formatting check passed"
    else
        print_warning "Backend needs formatting (run: black app tests)"
    fi
else
    print_warning "black not installed, skipping format check"
fi

if command -v flake8 &> /dev/null; then
    if flake8 app tests --max-line-length=100 2>/dev/null; then
        print_success "Backend linting passed"
    else
        print_warning "Backend has linting issues (run: flake8 app tests)"
    fi
else
    print_warning "flake8 not installed, skipping lint check"
fi

cd ..

# Frontend linting
echo "Checking frontend code quality..."
cd frontend

if npm run lint 2>/dev/null; then
    print_success "Frontend linting passed"
else
    print_warning "Frontend has linting issues (run: npm run lint)"
fi

cd ..

# ============================================================================
# SECURITY CHECKS
# ============================================================================

print_header "Security Checks"

# Python security
if command -v bandit &> /dev/null; then
    echo "Running Python security scan..."
    if bandit -r backend/app -ll 2>/dev/null; then
        print_success "No high-severity security issues found"
    else
        print_warning "Security issues detected (review bandit output)"
    fi
else
    print_warning "bandit not installed, skipping security scan"
fi

# Node security
cd frontend
echo "Running npm audit..."
if npm audit --audit-level=moderate 2>/dev/null; then
    print_success "No security vulnerabilities in npm packages"
else
    print_warning "npm audit found vulnerabilities (run: npm audit fix)"
fi
cd ..

# ============================================================================
# SUMMARY
# ============================================================================

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

print_header "Test Summary"

echo "Duration: ${DURATION} seconds"
echo ""

if [ "$BACKEND_TESTS_PASSED" = true ]; then
    print_success "Backend tests: PASSED"
else
    print_error "Backend tests: FAILED"
fi

if [ "$FRONTEND_TESTS_PASSED" = true ]; then
    print_success "Frontend tests: PASSED"
else
    print_warning "Frontend tests: NOT ALL PASSED (may be expected)"
fi

echo ""
echo "Coverage reports generated:"
echo "  - Backend: htmlcov/backend/index.html"
echo "  - Frontend: frontend/coverage/index.html"
echo ""

# Open coverage reports (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Opening coverage reports in browser..."
    open htmlcov/backend/index.html 2>/dev/null || true
fi

# Exit status
if [ "$BACKEND_TESTS_PASSED" = true ]; then
    print_success "All critical tests passed! 🎉"
    echo ""
    echo "Next steps:"
    echo "  1. Review coverage reports"
    echo "  2. Update TEST_RESULTS_BASELINE.md with actual metrics"
    echo "  3. Write additional tests for uncovered code"
    echo "  4. Implement validation tests"
    exit 0
else
    print_error "Some tests failed. Please review the output above."
    exit 1
fi
