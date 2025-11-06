#!/bin/bash
# Coverage Check Script for Meta-Analysis Tool
# Generates coverage reports and checks thresholds

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Default thresholds
BACKEND_THRESHOLD=80
FRONTEND_THRESHOLD=60

# Parse arguments
OPEN_REPORT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-threshold)
            BACKEND_THRESHOLD="$2"
            shift 2
            ;;
        --frontend-threshold)
            FRONTEND_THRESHOLD="$2"
            shift 2
            ;;
        --open)
            OPEN_REPORT=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-threshold N    Set backend coverage threshold (default: 80)"
            echo "  --frontend-threshold N   Set frontend coverage threshold (default: 60)"
            echo "  --open                   Open HTML coverage report in browser"
            echo "  --help                   Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo ""
print_status "COVERAGE REPORT GENERATOR"
echo "========================="
echo ""

# Backend Coverage
print_status "Checking Backend Coverage..."
echo ""

cd backend

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    print_warning "No virtual environment found. Installing dependencies..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install -r requirements-test.txt
fi

# Set test environment
export TESTING=true
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/test_db}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export SECRET_KEY="test-secret-key"

# Run tests with coverage
print_status "Running backend tests with coverage..."
pytest tests/unit tests/integration \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=xml:coverage.xml \
    --cov-report=html:htmlcov \
    --cov-report=json:coverage.json \
    -q

echo ""
print_status "Backend Coverage Summary:"
echo "------------------------"
coverage report

# Check threshold
echo ""
print_status "Checking backend coverage threshold (${BACKEND_THRESHOLD}%)..."
if coverage report --fail-under=${BACKEND_THRESHOLD} > /dev/null 2>&1; then
    print_success "Backend coverage meets threshold (${BACKEND_THRESHOLD}%)"
    BACKEND_SUCCESS=true
else
    print_error "Backend coverage below threshold (${BACKEND_THRESHOLD}%)"
    BACKEND_SUCCESS=false
fi

# Get coverage percentage
BACKEND_COVERAGE=$(coverage json -o - | python3 -c "import sys, json; print(round(json.load(sys.stdin)['totals']['percent_covered'], 2))" 2>/dev/null || echo "N/A")
echo "Current backend coverage: ${BACKEND_COVERAGE}%"

# Open report if requested
if [ "$OPEN_REPORT" = true ]; then
    if [ -f "htmlcov/index.html" ]; then
        print_status "Opening backend coverage report..."
        if command -v open &> /dev/null; then
            open htmlcov/index.html
        elif command -v xdg-open &> /dev/null; then
            xdg-open htmlcov/index.html
        else
            print_warning "Cannot open browser automatically. Open backend/htmlcov/index.html manually."
        fi
    fi
fi

cd ..

# Frontend Coverage (if tests exist)
echo ""
print_status "Checking Frontend Coverage..."
echo ""

cd frontend

if [ ! -d "node_modules" ]; then
    print_warning "node_modules not found. Installing dependencies..."
    npm install
fi

# Check if test framework is configured
if [ -f "vitest.config.ts" ] || [ -f "vitest.config.js" ]; then
    print_status "Running frontend tests with coverage (Vitest)..."
    npm test -- --coverage --run || true
    FRONTEND_COVERAGE_EXISTS=true
elif [ -f "jest.config.js" ] || [ -f "jest.config.ts" ]; then
    print_status "Running frontend tests with coverage (Jest)..."
    npm test -- --coverage --passWithNoTests || true
    FRONTEND_COVERAGE_EXISTS=true
else
    print_warning "No test framework configured for frontend"
    FRONTEND_COVERAGE_EXISTS=false
fi

if [ "$FRONTEND_COVERAGE_EXISTS" = true ] && [ -f "coverage/coverage-summary.json" ]; then
    echo ""
    print_status "Frontend Coverage Summary:"
    echo "-------------------------"

    # Extract coverage from JSON
    FRONTEND_COVERAGE=$(cat coverage/coverage-summary.json | python3 -c "import sys, json; data=json.load(sys.stdin); print(round(data['total']['lines']['pct'], 2))" 2>/dev/null || echo "N/A")

    echo "Current frontend coverage: ${FRONTEND_COVERAGE}%"

    if (( $(echo "$FRONTEND_COVERAGE >= $FRONTEND_THRESHOLD" | bc -l 2>/dev/null || echo 0) )); then
        print_success "Frontend coverage meets threshold (${FRONTEND_THRESHOLD}%)"
        FRONTEND_SUCCESS=true
    else
        print_error "Frontend coverage below threshold (${FRONTEND_THRESHOLD}%)"
        FRONTEND_SUCCESS=false
    fi

    # Open report if requested
    if [ "$OPEN_REPORT" = true ]; then
        if [ -f "coverage/lcov-report/index.html" ]; then
            print_status "Opening frontend coverage report..."
            if command -v open &> /dev/null; then
                open coverage/lcov-report/index.html
            elif command -v xdg-open &> /dev/null; then
                xdg-open coverage/lcov-report/index.html
            else
                print_warning "Cannot open browser automatically. Open frontend/coverage/lcov-report/index.html manually."
            fi
        fi
    fi
else
    print_warning "Frontend coverage not available (tests not configured)"
    FRONTEND_SUCCESS=true  # Don't fail if tests aren't configured yet
fi

cd ..

# Final Summary
echo ""
echo "=========================================="
echo "COVERAGE SUMMARY"
echo "=========================================="
echo ""
echo "Backend Coverage:  ${BACKEND_COVERAGE}% (threshold: ${BACKEND_THRESHOLD}%)"
if [ "$FRONTEND_COVERAGE_EXISTS" = true ]; then
    echo "Frontend Coverage: ${FRONTEND_COVERAGE}% (threshold: ${FRONTEND_THRESHOLD}%)"
else
    echo "Frontend Coverage: Not configured"
fi
echo ""

# Coverage reports location
print_status "Coverage Reports:"
echo "  Backend:  backend/htmlcov/index.html"
if [ "$FRONTEND_COVERAGE_EXISTS" = true ]; then
    echo "  Frontend: frontend/coverage/lcov-report/index.html"
fi
echo ""

# Exit with appropriate code
if [ "$BACKEND_SUCCESS" = true ] && [ "$FRONTEND_SUCCESS" = true ]; then
    print_success "All coverage thresholds met!"
    exit 0
else
    print_error "Some coverage thresholds not met"
    echo ""
    echo "To improve coverage:"
    echo "  1. Add tests for uncovered code"
    echo "  2. Review coverage reports for gaps"
    echo "  3. Focus on critical paths first"
    exit 1
fi
