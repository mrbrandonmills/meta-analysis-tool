#!/bin/bash
# Complete Test Suite Runner for Meta-Analysis Tool
# This script runs all tests (backend and frontend) locally

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if we're in the project root
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

# Parse command line arguments
RUN_BACKEND=true
RUN_FRONTEND=true
RUN_VALIDATION=false
COVERAGE_REPORT=true
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            RUN_FRONTEND=false
            shift
            ;;
        --frontend-only)
            RUN_BACKEND=false
            shift
            ;;
        --with-validation)
            RUN_VALIDATION=true
            shift
            ;;
        --no-coverage)
            COVERAGE_REPORT=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-only       Run only backend tests"
            echo "  --frontend-only      Run only frontend tests"
            echo "  --with-validation    Include validation tests (may take longer)"
            echo "  --no-coverage        Skip coverage reporting"
            echo "  --verbose           Show detailed test output"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Track overall success
OVERALL_SUCCESS=true

echo ""
print_status "META-ANALYSIS TOOL - COMPLETE TEST SUITE"
echo "=========================================="
echo ""

# Run Backend Tests
if [ "$RUN_BACKEND" = true ]; then
    print_status "Running Backend Tests..."
    echo ""

    cd backend

    # Check if virtual environment exists
    if [ ! -d "venv" ] && [ ! -d "../venv" ]; then
        print_warning "No virtual environment found. Creating one..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    else
        if [ -d "venv" ]; then
            source venv/bin/activate
        else
            source ../venv/bin/activate
        fi
    fi

    # Set test environment variables
    export TESTING=true
    export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/test_db}"
    export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
    export SECRET_KEY="${SECRET_KEY:-test-secret-key}"

    # Run unit tests
    print_status "Running unit tests..."
    if [ "$COVERAGE_REPORT" = true ]; then
        if [ "$VERBOSE" = true ]; then
            pytest tests/unit -v --cov=app --cov-report=term-missing --cov-report=xml --cov-report=html
        else
            pytest tests/unit --cov=app --cov-report=term-missing --cov-report=xml --cov-report=html -q
        fi
    else
        if [ "$VERBOSE" = true ]; then
            pytest tests/unit -v
        else
            pytest tests/unit -q
        fi
    fi

    if [ $? -eq 0 ]; then
        print_success "Unit tests passed"
    else
        print_error "Unit tests failed"
        OVERALL_SUCCESS=false
    fi
    echo ""

    # Run integration tests
    print_status "Running integration tests..."
    if [ "$VERBOSE" = true ]; then
        pytest tests/integration -v
    else
        pytest tests/integration -q
    fi

    if [ $? -eq 0 ]; then
        print_success "Integration tests passed"
    else
        print_error "Integration tests failed"
        OVERALL_SUCCESS=false
    fi
    echo ""

    # Run validation tests if requested
    if [ "$RUN_VALIDATION" = true ]; then
        print_status "Running validation tests..."
        if [ "$VERBOSE" = true ]; then
            pytest tests/validation -v -m validation || true
        else
            pytest tests/validation -q -m validation || true
        fi
        print_warning "Validation tests completed (failures allowed)"
        echo ""
    fi

    # Show coverage report
    if [ "$COVERAGE_REPORT" = true ]; then
        echo ""
        print_status "Backend Coverage Report:"
        echo "------------------------"
        coverage report
        echo ""
        print_success "Coverage report generated: backend/htmlcov/index.html"
    fi

    cd ..
fi

# Run Frontend Tests
if [ "$RUN_FRONTEND" = true ]; then
    print_status "Running Frontend Tests..."
    echo ""

    cd frontend

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found. Installing dependencies..."
        npm install
    fi

    # Run linting
    print_status "Running ESLint..."
    npm run lint
    if [ $? -eq 0 ]; then
        print_success "Linting passed"
    else
        print_error "Linting failed"
        OVERALL_SUCCESS=false
    fi
    echo ""

    # Run TypeScript type checking
    print_status "Running TypeScript type checking..."
    npx tsc --noEmit
    if [ $? -eq 0 ]; then
        print_success "Type checking passed"
    else
        print_error "Type checking failed"
        OVERALL_SUCCESS=false
    fi
    echo ""

    # Run tests (if configured)
    print_status "Running frontend tests..."
    if [ -f "vitest.config.ts" ] || [ -f "vitest.config.js" ]; then
        if [ "$COVERAGE_REPORT" = true ]; then
            npm test -- --coverage --run
        else
            npm test -- --run
        fi
    elif [ -f "jest.config.js" ] || [ -f "jest.config.ts" ]; then
        if [ "$COVERAGE_REPORT" = true ]; then
            npm test -- --coverage --passWithNoTests
        else
            npm test -- --passWithNoTests
        fi
    else
        print_warning "No test framework configured for frontend"
    fi

    if [ $? -eq 0 ]; then
        print_success "Frontend tests passed"
    else
        print_error "Frontend tests failed"
        OVERALL_SUCCESS=false
    fi
    echo ""

    # Run build check
    print_status "Running build check..."
    npm run build > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        print_success "Build check passed"
    else
        print_error "Build check failed"
        OVERALL_SUCCESS=false
    fi
    echo ""

    cd ..
fi

# Final summary
echo ""
echo "=========================================="
if [ "$OVERALL_SUCCESS" = true ]; then
    print_success "ALL TESTS PASSED!"
    echo ""
    echo "Next steps:"
    echo "  1. Review coverage reports"
    echo "  2. Commit your changes"
    echo "  3. Push to trigger CI/CD pipeline"
    exit 0
else
    print_error "SOME TESTS FAILED!"
    echo ""
    echo "Next steps:"
    echo "  1. Review the errors above"
    echo "  2. Fix failing tests"
    echo "  3. Run tests again"
    exit 1
fi
