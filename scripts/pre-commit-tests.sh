#!/bin/bash
# Pre-Commit Test Script for Meta-Analysis Tool
# Fast test suite to run before committing code

set -e

# Colors
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

# Check if we're in the project root
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

echo ""
print_status "PRE-COMMIT CHECKS"
echo "=================="
echo ""

OVERALL_SUCCESS=true

# Detect what has changed
BACKEND_CHANGED=false
FRONTEND_CHANGED=false

if git rev-parse --git-dir > /dev/null 2>&1; then
    # We're in a git repo, check what's changed
    if git diff --cached --name-only | grep -q "^backend/"; then
        BACKEND_CHANGED=true
    fi
    if git diff --cached --name-only | grep -q "^frontend/"; then
        FRONTEND_CHANGED=true
    fi
else
    # Not in a git repo, run all checks
    BACKEND_CHANGED=true
    FRONTEND_CHANGED=true
fi

# Backend checks
if [ "$BACKEND_CHANGED" = true ]; then
    print_status "Backend changes detected - running checks..."
    echo ""

    cd backend

    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d "../venv" ]; then
        source ../venv/bin/activate
    else
        print_warning "No virtual environment found"
    fi

    # Quick linting
    print_status "Running Black (formatting)..."
    if black --check app tests > /dev/null 2>&1; then
        print_success "Black check passed"
    else
        print_error "Black check failed - run 'black app tests' to fix"
        OVERALL_SUCCESS=false
    fi

    print_status "Running isort (imports)..."
    if isort --check-only app tests > /dev/null 2>&1; then
        print_success "isort check passed"
    else
        print_error "isort check failed - run 'isort app tests' to fix"
        OVERALL_SUCCESS=false
    fi

    print_status "Running flake8 (linting)..."
    if flake8 app tests --max-line-length=120 --extend-ignore=E203,W503 --exclude=__pycache__,migrations > /dev/null 2>&1; then
        print_success "flake8 passed"
    else
        print_error "flake8 failed"
        OVERALL_SUCCESS=false
    fi

    # Quick unit tests (only fast tests)
    print_status "Running fast unit tests..."
    export TESTING=true
    export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/test_db}"
    export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
    export SECRET_KEY="test-secret-key"

    if pytest tests/unit -q -m "not slow" --tb=line 2>/dev/null; then
        print_success "Fast unit tests passed"
    else
        print_warning "Some unit tests failed (run full test suite before pushing)"
    fi

    cd ..
    echo ""
fi

# Frontend checks
if [ "$FRONTEND_CHANGED" = true ]; then
    print_status "Frontend changes detected - running checks..."
    echo ""

    cd frontend

    # Check if dependencies are installed
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found - skipping frontend checks"
        cd ..
    else
        # Linting
        print_status "Running ESLint..."
        if npm run lint > /dev/null 2>&1; then
            print_success "ESLint passed"
        else
            print_error "ESLint failed"
            OVERALL_SUCCESS=false
        fi

        # Type checking
        print_status "Running TypeScript type check..."
        if npx tsc --noEmit > /dev/null 2>&1; then
            print_success "Type checking passed"
        else
            print_error "Type checking failed"
            OVERALL_SUCCESS=false
        fi

        cd ..
        echo ""
    fi
fi

# Check for common issues
print_status "Additional checks..."

# Check for console.log in frontend source (warning only)
if [ "$FRONTEND_CHANGED" = true ]; then
    if grep -r "console\." frontend/src/ --include="*.ts" --include="*.tsx" > /dev/null 2>&1; then
        print_warning "Found console statements in frontend/src/ - consider removing for production"
    fi
fi

# Check for TODO/FIXME comments in changed files
if git rev-parse --git-dir > /dev/null 2>&1; then
    TODO_COUNT=$(git diff --cached | grep -E "^\+.*\b(TODO|FIXME|XXX|HACK)\b" | wc -l | tr -d ' ')
    if [ "$TODO_COUNT" -gt 0 ]; then
        print_warning "Found ${TODO_COUNT} new TODO/FIXME comments"
    fi
fi

# Check for debugging code
if git rev-parse --git-dir > /dev/null 2>&1; then
    if git diff --cached | grep -E "^\+.*(import pdb|debugger;|console\.debug)" > /dev/null 2>&1; then
        print_warning "Found debugging code (pdb/debugger) - consider removing"
    fi
fi

echo ""

# Summary
if [ "$OVERALL_SUCCESS" = true ]; then
    print_success "All pre-commit checks passed!"
    echo ""
    echo "You can now commit your changes:"
    echo "  git commit -m \"your message\""
    echo ""
    echo "Before pushing, consider running:"
    echo "  ./scripts/run-all-tests.sh"
    exit 0
else
    print_error "Some pre-commit checks failed!"
    echo ""
    echo "Please fix the issues above before committing."
    echo ""
    echo "Quick fixes:"
    echo "  Backend formatting: cd backend && black app tests && isort app tests"
    echo "  Frontend linting:   cd frontend && npm run lint --fix"
    exit 1
fi
