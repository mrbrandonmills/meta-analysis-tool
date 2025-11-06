#!/bin/bash
# Quick diagnostic script to identify worker deployment issues

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================================="
echo "  Celery Worker Diagnostic Report"
echo "=========================================================="
echo ""

# Check health
echo -e "${BLUE}1. Checking deployment health...${NC}"
HEALTH=$(curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed)

DB_STATUS=$(echo "$HEALTH" | jq -r '.checks.database.status // "unknown"')
REDIS_STATUS=$(echo "$HEALTH" | jq -r '.checks.redis.status // "unknown"')
CELERY_STATUS=$(echo "$HEALTH" | jq -r '.checks.celery.status // "unknown"')
CELERY_MESSAGE=$(echo "$HEALTH" | jq -r '.checks.celery.message // "unknown"')

echo ""
echo "Service Health:"
echo "  Database: $DB_STATUS"
echo "  Redis: $REDIS_STATUS"
echo "  Celery: $CELERY_STATUS - $CELERY_MESSAGE"
echo ""

if [ "$CELERY_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✅ Celery workers are HEALTHY!${NC}"
    echo ""
    echo "$HEALTH" | jq '.'
    exit 0
fi

# Diagnosis
echo -e "${YELLOW}⚠️  Celery workers are NOT healthy${NC}"
echo ""
echo "=========================================================="
echo "  Diagnostic Analysis"
echo "=========================================================="
echo ""

# Check 1: Prerequisites
echo -e "${BLUE}2. Checking prerequisites...${NC}"
echo ""

if [ "$DB_STATUS" != "healthy" ]; then
    echo -e "${RED}✗ Database is not healthy${NC}"
    echo "  Fix: Check Postgres service in Railway dashboard"
else
    echo -e "${GREEN}✓ Database is healthy${NC}"
fi

if [ "$REDIS_STATUS" != "healthy" ]; then
    echo -e "${RED}✗ Redis is not healthy${NC}"
    echo "  Fix: Ensure Redis service is running and connected"
else
    echo -e "${GREEN}✓ Redis is healthy${NC}"
fi

echo ""

# Check 2: Common issues
echo -e "${BLUE}3. Common issues checklist:${NC}"
echo ""

echo "Issue #1: Missing Environment Variables"
echo "  Required variables for worker service:"
echo "    • DATABASE_URL"
echo "    • REDIS_URL"
echo "    • ANTHROPIC_API_KEY"
echo "    • SECRET_KEY"
echo ""
echo "  Fix:"
echo "    1. Open Railway Dashboard → Meta-Analysis-Tool"
echo "    2. Select 'meta-analysis-worker' service"
echo "    3. Go to Variables tab"
echo "    4. Copy all variables from 'backend' service"
echo "    5. Ensure REDIS_URL = \${{Redis.REDIS_URL}}"
echo ""

echo "Issue #2: Incorrect Start Command"
echo "  Expected start command:"
echo "    celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4"
echo ""
echo "  Fix:"
echo "    1. Railway Dashboard → meta-analysis-worker → Settings → Deploy"
echo "    2. Check 'Start Command' matches exactly"
echo "    3. No extra spaces or line breaks"
echo ""

echo "Issue #3: Wrong Dockerfile Path"
echo "  Expected: backend/Dockerfile (no leading slash)"
echo ""
echo "  Fix:"
echo "    1. Railway Dashboard → meta-analysis-worker → Settings → Build"
echo "    2. Dockerfile Path = 'backend/Dockerfile'"
echo "    3. NOT '/backend/Dockerfile' or 'Dockerfile'"
echo ""

echo "Issue #4: Service Not Deployed Yet"
echo "  Worker service may exist but not deployed"
echo ""
echo "  Fix:"
echo "    1. Railway Dashboard → meta-analysis-worker"
echo "    2. Click three dots menu (⋯)"
echo "    3. Select 'Redeploy'"
echo "    4. Wait 2-4 minutes for build"
echo ""

echo "=========================================================="
echo "  Recommended Actions"
echo "=========================================================="
echo ""

echo "Step 1: Verify Environment Variables"
echo "--------------------------------------"
echo "Railway Dashboard → meta-analysis-worker → Variables"
echo ""
echo "Required variables:"
cat << 'EOF'
DATABASE_URL = ${{Postgres.DATABASE_URL}}
REDIS_URL = ${{Redis.REDIS_URL}}
ANTHROPIC_API_KEY = <copy-from-backend-service>
SECRET_KEY = <copy-from-backend-service>
OPENAI_API_KEY = <copy-from-backend-service> (optional)
PYTHONUNBUFFERED = 1
LOG_LEVEL = INFO
EOF
echo ""

echo "Step 2: Verify Build Settings"
echo "------------------------------"
echo "Railway Dashboard → meta-analysis-worker → Settings → Build"
echo ""
echo "  Builder: DOCKERFILE"
echo "  Dockerfile Path: backend/Dockerfile"
echo ""

echo "Step 3: Verify Deploy Settings"
echo "-------------------------------"
echo "Railway Dashboard → meta-analysis-worker → Settings → Deploy"
echo ""
echo "  Start Command:"
echo "    celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4"
echo ""

echo "Step 4: Redeploy"
echo "----------------"
echo "Railway Dashboard → meta-analysis-worker → ⋯ menu → Redeploy"
echo ""

echo "Step 5: Check Logs"
echo "------------------"
echo "Railway Dashboard → meta-analysis-worker → Logs"
echo ""
echo "Look for:"
echo "  ✓ 'celery@meta-analysis-worker ready.'"
echo "  ✓ 'Connected to redis://...'"
echo "  ✓ Task modules listed"
echo ""
echo "Watch for errors:"
echo "  ✗ Connection refused"
echo "  ✗ ModuleNotFoundError"
echo "  ✗ Missing environment variable"
echo ""

echo "=========================================================="
echo "  Next Steps"
echo "=========================================================="
echo ""
echo "After fixing the above issues:"
echo ""
echo "1. Wait 2-4 minutes for deployment"
echo "2. Run this diagnostic again:"
echo "   ./diagnose-worker.sh"
echo ""
echo "3. Or run the full deployment script:"
echo "   ./deploy-celery-worker.sh"
echo ""
echo "4. Verify health endpoint:"
echo "   curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed | jq '.checks.celery'"
echo ""

if [ "$CELERY_STATUS" = "degraded" ] && [ "$CELERY_MESSAGE" = "No workers available" ]; then
    echo -e "${YELLOW}Current Issue: Workers not connecting to Redis${NC}"
    echo ""
    echo "Most likely causes:"
    echo "  1. Environment variables not set on worker service"
    echo "  2. REDIS_URL not using Railway variable reference"
    echo "  3. Worker service not redeployed after configuration"
    echo ""
    echo "Quick fix:"
    echo "  1. Copy ALL variables from backend to worker service"
    echo "  2. Ensure REDIS_URL = \${{Redis.REDIS_URL}}"
    echo "  3. Redeploy worker service"
    echo ""
fi

echo "For detailed help, see: CELERY_WORKER_DEPLOYMENT.md"
echo ""
