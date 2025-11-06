#!/bin/bash
# Quick Worker Health Verification Script

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Checking Celery worker health..."
echo ""

HEALTH=$(curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed)

echo "Full Health Response:"
echo "$HEALTH" | jq '.'
echo ""

CELERY_STATUS=$(echo "$HEALTH" | jq -r '.checks.celery.status // "unknown"')
CELERY_MESSAGE=$(echo "$HEALTH" | jq -r '.checks.celery.message // "unknown"')

echo "=========================================================="
echo "  Celery Worker Status"
echo "=========================================================="
echo ""
echo "Status: $CELERY_STATUS"
echo "Message: $CELERY_MESSAGE"
echo ""

if [ "$CELERY_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✅ SUCCESS! Workers are healthy and connected!${NC}"
    exit 0
else
    echo -e "${RED}❌ FAILED! Workers are not healthy${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Check worker service logs in Railway Dashboard"
    echo "  2. Verify environment variables are set correctly"
    echo "  3. Run: ./diagnose-worker.sh for detailed diagnostics"
    exit 1
fi
