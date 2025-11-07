#!/bin/bash

# Test Setup Verification Script
# Verifies that all test infrastructure is properly configured

set -e

echo "🧪 Meta-Analysis Tool - Test Setup Verification"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 (MISSING)"
        ((FAILED++))
        return 1
    fi
}

check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (MISSING)"
        ((FAILED++))
        return 1
    fi
}

warn_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} $1 (OPTIONAL - recommended for production)"
        ((WARNINGS++))
    fi
}

echo "📁 Checking Test Directory Structure..."
echo "---------------------------------------"

# Backend test structure
check_directory "backend/tests"
check_directory "backend/tests/unit"
check_directory "backend/tests/unit/test_agents"
check_directory "backend/tests/integration"
check_directory "backend/tests/integration/test_api"
check_directory "backend/tests/integration/test_workflows"

# Frontend test structure
check_directory "frontend/tests"
check_directory "frontend/tests/components"
check_directory "frontend/tests/hooks"
check_directory "frontend/tests/integration"

# E2E test structure
check_directory "tests/e2e"

echo ""
echo "📄 Checking Backend Test Files..."
echo "----------------------------------"

check_file "backend/tests/conftest.py"
check_file "backend/pytest.ini"
check_file "backend/requirements-test.txt"
check_file "backend/tests/unit/test_agents/test_search_agent.py"
check_file "backend/tests/unit/test_agents/test_screening_agent.py"
check_file "backend/tests/unit/test_agents/test_qa_agent.py"
check_file "backend/tests/unit/test_agents/test_coordinator_agent.py"
check_file "backend/tests/integration/test_api/test_auth_api.py"
check_file "backend/tests/integration/test_workflows/test_complete_workflow.py"

echo ""
echo "📄 Checking Frontend Test Files..."
echo "-----------------------------------"

check_file "frontend/tests/setup.ts"
check_file "frontend/vitest.config.ts"
check_file "frontend/tests/components/meta-analysis-form.test.tsx"
check_file "frontend/tests/hooks/useMetaAnalysis.test.ts"
check_file "frontend/tests/integration/api-client.test.ts"

echo ""
echo "📄 Checking E2E Test Files..."
echo "------------------------------"

check_file "tests/e2e/playwright.config.ts"
check_file "tests/e2e/package.json"
check_file "tests/e2e/auth.spec.ts"
check_file "tests/e2e/meta-analysis-workflow.spec.ts"

echo ""
echo "📄 Checking CI/CD Workflows..."
echo "-------------------------------"

check_file ".github/workflows/backend-tests.yml"
check_file ".github/workflows/frontend-tests.yml"
check_file ".github/workflows/e2e-tests.yml"
warn_file ".github/workflows/production-readiness.yml"
warn_file ".github/workflows/security.yml"

echo ""
echo "📄 Checking Documentation..."
echo "-----------------------------"

check_file "TESTING.md"
check_file "CONTRIBUTING_TESTS.md"
check_file "TEST_SUITE_SUMMARY.md"
check_file "README.md"

echo ""
echo "🔧 Checking Test Dependencies..."
echo "---------------------------------"

# Check if backend dependencies exist
if [ -f "backend/requirements-test.txt" ]; then
    echo -e "${GREEN}✓${NC} Backend test dependencies file exists"
    if command -v pip &> /dev/null; then
        if pip list | grep -q "pytest"; then
            echo -e "${GREEN}✓${NC} pytest is installed"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠${NC} pytest not installed (run: pip install -r backend/requirements-test.txt)"
            ((WARNINGS++))
        fi
    else
        echo -e "${YELLOW}⚠${NC} pip not found (skipping dependency check)"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}✗${NC} Backend test dependencies missing"
    ((FAILED++))
fi

# Check if frontend dependencies exist
if [ -f "frontend/package.json" ]; then
    echo -e "${GREEN}✓${NC} Frontend package.json exists"
    if [ -d "frontend/node_modules" ]; then
        echo -e "${GREEN}✓${NC} Frontend node_modules exists"
        ((PASSED++))
        if [ -d "frontend/node_modules/vitest" ]; then
            echo -e "${GREEN}✓${NC} Vitest is installed"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠${NC} Vitest not found (run: npm install)"
            ((WARNINGS++))
        fi
    else
        echo -e "${YELLOW}⚠${NC} Frontend dependencies not installed (run: npm install)"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}✗${NC} Frontend package.json missing"
    ((FAILED++))
fi

# Check if E2E dependencies exist
if [ -f "tests/e2e/package.json" ]; then
    echo -e "${GREEN}✓${NC} E2E package.json exists"
    if [ -d "tests/e2e/node_modules" ]; then
        echo -e "${GREEN}✓${NC} E2E node_modules exists"
        ((PASSED++))
        if [ -d "tests/e2e/node_modules/@playwright" ]; then
            echo -e "${GREEN}✓${NC} Playwright is installed"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠${NC} Playwright not found (run: cd tests/e2e && npm install)"
            ((WARNINGS++))
        fi
    else
        echo -e "${YELLOW}⚠${NC} E2E dependencies not installed (run: cd tests/e2e && npm install)"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠${NC} E2E package.json missing"
    ((WARNINGS++))
fi

echo ""
echo "📊 Summary"
echo "=========="
echo -e "${GREEN}Passed:${NC}   $PASSED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Failed:${NC}   $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Test infrastructure setup is complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Install dependencies:"
    echo "   Backend:  cd backend && pip install -r requirements-test.txt"
    echo "   Frontend: cd frontend && npm install"
    echo "   E2E:      cd tests/e2e && npm install && npx playwright install --with-deps"
    echo ""
    echo "2. Run tests:"
    echo "   Backend:  cd backend && pytest"
    echo "   Frontend: cd frontend && npm test"
    echo "   E2E:      cd tests/e2e && npx playwright test"
    echo ""
    echo "3. View documentation:"
    echo "   - TESTING.md for comprehensive guide"
    echo "   - CONTRIBUTING_TESTS.md for contribution guidelines"
    echo "   - TEST_SUITE_SUMMARY.md for implementation details"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some required files are missing. Please check the errors above.${NC}"
    echo ""
    echo "Run this script again after fixing the issues."
    exit 1
fi
