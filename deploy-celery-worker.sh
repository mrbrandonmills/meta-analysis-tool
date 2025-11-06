#!/bin/bash
# Celery Worker Deployment and Verification Script for Railway
# This script helps diagnose and fix the "No workers available" issue

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================================="
echo "  Celery Worker Deployment & Verification"
echo "=========================================================="
echo ""

# Function to check health
check_health() {
    echo -e "${BLUE}Checking deployment health...${NC}"
    HEALTH=$(curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed)
    echo "$HEALTH" | jq '.'

    CELERY_STATUS=$(echo "$HEALTH" | jq -r '.checks.celery.status // "unknown"' 2>/dev/null)
    CELERY_MESSAGE=$(echo "$HEALTH" | jq -r '.checks.celery.message // "unknown"' 2>/dev/null)

    echo ""
    echo -e "Celery Status: ${YELLOW}$CELERY_STATUS${NC}"
    echo -e "Message: $CELERY_MESSAGE"
    echo ""

    if [ "$CELERY_STATUS" = "healthy" ]; then
        return 0
    else
        return 1
    fi
}

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Railway CLI not found!${NC}"
    echo "Install: npm i -g @railway/cli"
    exit 1
fi

echo -e "${GREEN}✓ Railway CLI found${NC}"
echo ""

# Initial health check
if check_health; then
    echo -e "${GREEN}=========================================================="
    echo "  🎉 Celery workers are ALREADY HEALTHY!"
    echo "==========================================================${NC}"
    echo ""
    echo "No action needed. Workers are connected and processing tasks."
    exit 0
fi

echo -e "${YELLOW}=========================================================="
echo "  ⚠ Celery workers are NOT healthy - starting diagnosis"
echo "==========================================================${NC}"
echo ""

# Step 1: Environment Variables Check
echo "Step 1: Checking required environment variables"
echo "------------------------------------------------"
echo ""
echo "The Celery worker service needs the following environment variables:"
echo ""
echo "REQUIRED:"
echo "  ✓ DATABASE_URL (should reference Postgres service)"
echo "  ✓ REDIS_URL (should reference Redis service)"
echo "  ✓ ANTHROPIC_API_KEY (for AI-powered tasks)"
echo "  ✓ SECRET_KEY (for application security)"
echo ""
echo "OPTIONAL but RECOMMENDED:"
echo "  • OPENAI_API_KEY (for OpenAI integration)"
echo "  • PUBMED_API_KEY (for literature searches)"
echo "  • PUBMED_EMAIL (for PubMed API)"
echo "  • LOG_LEVEL=INFO"
echo "  • PYTHONUNBUFFERED=1"
echo ""

echo -e "${YELLOW}Action Required: Verify worker environment variables${NC}"
echo ""
echo "1. Open Railway Dashboard: https://railway.app/dashboard"
echo "2. Navigate to: Meta-Analysis-Tool → meta-analysis-worker"
echo "3. Go to: Variables tab"
echo "4. Ensure these variables are set (copy from backend service):"
echo ""
echo "   DATABASE_URL = \${{Postgres.DATABASE_URL}}"
echo "   REDIS_URL = \${{Redis.REDIS_URL}}"
echo "   ANTHROPIC_API_KEY = <your-key>"
echo "   SECRET_KEY = <your-secret>"
echo "   OPENAI_API_KEY = <your-key> (optional)"
echo "   PYTHONUNBUFFERED = 1"
echo "   LOG_LEVEL = INFO"
echo ""
read -p "Press ENTER when variables are configured..."

echo ""

# Step 2: Build Configuration Check
echo "Step 2: Verifying build configuration"
echo "--------------------------------------"
echo ""
echo "Worker build settings should be:"
echo "  • Builder: DOCKERFILE"
echo "  • Dockerfile Path: backend/Dockerfile"
echo "  • Root Directory: / (default)"
echo "  • Watch Paths: backend/**"
echo ""
echo "Worker deploy settings should be:"
echo "  • Start Command: celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4"
echo "  • Restart Policy: ON_FAILURE"
echo "  • Healthcheck Timeout: 300 (5 minutes)"
echo ""

echo -e "${YELLOW}Action Required: Verify build settings${NC}"
echo ""
echo "In Railway Dashboard → meta-analysis-worker → Settings:"
echo "1. Check 'Source' section matches GitHub repo/branch"
echo "2. Check 'Build' section uses DOCKERFILE with path 'backend/Dockerfile'"
echo "3. Check 'Deploy' section has correct start command (see above)"
echo ""
read -p "Press ENTER when build settings are verified..."

echo ""

# Step 3: Trigger Redeploy
echo "Step 3: Triggering worker redeploy"
echo "-----------------------------------"
echo ""
echo -e "${BLUE}After verifying environment variables and build settings,${NC}"
echo -e "${BLUE}the worker service needs to be redeployed.${NC}"
echo ""

echo -e "${YELLOW}Action Required: Redeploy worker service${NC}"
echo ""
echo "In Railway Dashboard → meta-analysis-worker:"
echo "1. Click the three dots (⋯) menu"
echo "2. Select 'Redeploy'"
echo "3. Wait for build to complete (2-4 minutes)"
echo "4. Check deployment logs for errors"
echo ""
echo "Expected log messages:"
echo "  ✓ 'celery@<hostname> ready.'"
echo "  ✓ 'Connected to redis://...'"
echo "  ✓ Task modules loaded successfully"
echo ""
read -p "Press ENTER when redeploy is complete..."

echo ""

# Step 4: Verify deployment
echo "Step 4: Verifying worker connection"
echo "------------------------------------"
echo ""

for i in {1..10}; do
    echo "Attempt $i/10: Checking worker health..."
    sleep 5

    if check_health; then
        echo ""
        echo -e "${GREEN}=========================================================="
        echo "  🎉 SUCCESS! Celery workers are now HEALTHY!"
        echo "==========================================================${NC}"
        echo ""
        echo "Worker deployment completed successfully!"
        echo ""
        echo "Next steps:"
        echo "  1. Test literature search functionality"
        echo "  2. Monitor worker logs for errors"
        echo "  3. Verify task processing in production"
        echo ""
        exit 0
    fi

    echo "Workers not yet available, waiting..."
done

echo ""
echo -e "${RED}=========================================================="
echo "  ⚠ Workers still not connecting after 10 attempts"
echo "==========================================================${NC}"
echo ""
echo "Troubleshooting steps:"
echo ""
echo "1. CHECK WORKER LOGS in Railway Dashboard:"
echo "   • Look for connection errors to Redis/Postgres"
echo "   • Check for missing environment variables"
echo "   • Look for Python import errors"
echo ""
echo "2. VERIFY REDIS CONNECTION:"
echo "   • Ensure Redis service is running"
echo "   • Check REDIS_URL uses internal Railway URL"
echo "   • Format: redis://default:<password>@redis.railway.internal:6379"
echo ""
echo "3. CHECK TASK MODULE IMPORTS:"
echo "   • Worker logs should show task discovery"
echo "   • Tasks: literature_search, meta_analysis, reviewer_tasks, notifications"
echo ""
echo "4. VERIFY API KEYS:"
echo "   • ANTHROPIC_API_KEY must be set and valid"
echo "   • Tasks may fail to import without valid credentials"
echo ""
echo "5. CHECK DOCKERFILE:"
echo "   • Ensure all application code is copied correctly"
echo "   • Verify Python dependencies are installed"
echo ""
echo "Common fixes:"
echo "  • Copy ALL environment variables from backend service to worker"
echo "  • Ensure DATABASE_URL and REDIS_URL use Railway variable references"
echo "  • Check that start command doesn't have typos"
echo "  • Verify Dockerfile path is 'backend/Dockerfile' (not '/backend/Dockerfile')"
echo ""

exit 1
