#!/bin/bash
# Quick test runner for development
# Runs fast tests only (unit tests, skips slow validation tests)

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Running quick tests (unit tests only)...${NC}"
echo ""

cd backend

# Run only unit tests, skip slow tests
pytest tests/unit -v -m "not slow" --tb=short

echo ""
echo -e "${GREEN}✅ Quick tests complete!${NC}"
echo ""
echo "For full test suite, run: ./scripts/run_all_tests.sh"
