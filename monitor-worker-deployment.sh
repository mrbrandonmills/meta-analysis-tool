#!/bin/bash
# Continuous Worker Health Monitor
# Monitors the worker service health after configuration changes

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================================="
echo "  Celery Worker Deployment Monitor"
echo "=========================================================="
echo ""
echo "This script will continuously monitor the worker health"
echo "after you configure the environment variables."
echo ""
echo -e "${YELLOW}IMPORTANT: Before running this monitor${NC}"
echo ""
echo "1. Open Railway Dashboard:"
echo "   https://railway.app/dashboard"
echo ""
echo "2. Configure worker environment variables:"
echo "   See: RAILWAY_WORKER_FIX.md for detailed instructions"
echo ""
echo "3. Redeploy the worker service"
echo ""
echo "4. Then run this monitor to track the deployment"
echo ""

read -p "Have you configured the variables and redeployed? (y/n): " ready

if [ "$ready" != "y" ]; then
    echo ""
    echo "Please complete the configuration first, then run this script again."
    echo ""
    echo "Quick reference:"
    echo "  1. Add these variables to meta-analysis-worker service:"
    echo "     - DATABASE_URL = \${{Postgres.DATABASE_URL}}"
    echo "     - REDIS_URL = \${{Redis.REDIS_URL}}"
    echo "     - ANTHROPIC_API_KEY = <from backend service>"
    echo "     - SECRET_KEY = <from backend service>"
    echo "     - PYTHONUNBUFFERED = 1"
    echo "     - LOG_LEVEL = INFO"
    echo ""
    echo "  2. Redeploy the worker service (⋯ menu → Redeploy)"
    echo ""
    exit 0
fi

echo ""
echo -e "${BLUE}Starting health monitoring...${NC}"
echo ""
echo "Checking every 15 seconds for up to 5 minutes"
echo "Press Ctrl+C to stop monitoring"
echo ""

ATTEMPT=0
MAX_ATTEMPTS=20  # 20 attempts × 15 seconds = 5 minutes

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$TIMESTAMP] Attempt $ATTEMPT/$MAX_ATTEMPTS"

    HEALTH=$(curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed)

    if [ $? -ne 0 ]; then
        echo -e "  ${RED}✗ Failed to fetch health endpoint${NC}"
        echo "  Waiting 15 seconds..."
        sleep 15
        continue
    fi

    DB_STATUS=$(echo "$HEALTH" | jq -r '.checks.database.status // "unknown"')
    REDIS_STATUS=$(echo "$HEALTH" | jq -r '.checks.redis.status // "unknown"')
    CELERY_STATUS=$(echo "$HEALTH" | jq -r '.checks.celery.status // "unknown"')
    CELERY_MESSAGE=$(echo "$HEALTH" | jq -r '.checks.celery.message // "unknown"')

    echo "  Database: $DB_STATUS"
    echo "  Redis: $REDIS_STATUS"
    echo "  Celery: $CELERY_STATUS - $CELERY_MESSAGE"

    if [ "$CELERY_STATUS" = "healthy" ]; then
        echo ""
        echo -e "${GREEN}=========================================================="
        echo "  🎉 SUCCESS! Celery workers are HEALTHY!"
        echo "==========================================================${NC}"
        echo ""
        echo "Full health status:"
        echo "$HEALTH" | jq '.'
        echo ""
        echo -e "${GREEN}Worker deployment completed successfully!${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Test literature search functionality in the application"
        echo "  2. Monitor worker logs for any errors during task processing"
        echo "  3. Check worker performance metrics in Railway Dashboard"
        echo ""
        exit 0
    fi

    if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
        echo "  Workers not yet healthy, waiting 15 seconds..."
        sleep 15
    fi
done

echo ""
echo -e "${YELLOW}=========================================================="
echo "  ⚠️  Workers not healthy after 5 minutes"
echo "==========================================================${NC}"
echo ""
echo "Current status:"
echo "$HEALTH" | jq '.'
echo ""
echo "Troubleshooting steps:"
echo ""
echo "1. Check worker service logs in Railway Dashboard:"
echo "   → Meta-Analysis-Tool → meta-analysis-worker → Deployments"
echo "   → Click on latest deployment to view logs"
echo ""
echo "2. Look for error messages:"
echo "   • Connection refused → Check REDIS_URL variable"
echo "   • Missing environment variable → Add the missing variable"
echo "   • Module not found → Check Dockerfile path"
echo "   • Invalid API key → Verify ANTHROPIC_API_KEY"
echo ""
echo "3. Verify environment variables:"
echo "   → Ensure DATABASE_URL = \${{Postgres.DATABASE_URL}}"
echo "   → Ensure REDIS_URL = \${{Redis.REDIS_URL}}"
echo "   → Check all required variables are present"
echo ""
echo "4. If you made changes, redeploy and run this monitor again:"
echo "   ./monitor-worker-deployment.sh"
echo ""
echo "5. For detailed diagnostics, run:"
echo "   ./diagnose-worker.sh"
echo ""

exit 1
