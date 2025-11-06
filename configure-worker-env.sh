#!/bin/bash
# Configure Celery Worker Environment Variables
# This script helps set up all required environment variables for the worker service

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================================="
echo "  Celery Worker Environment Configuration"
echo "=========================================================="
echo ""

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Railway CLI not found!${NC}"
    echo "Install: npm i -g @railway/cli"
    exit 1
fi

echo -e "${GREEN}✓ Railway CLI found${NC}"
echo ""

# Instructions for manual configuration
echo -e "${CYAN}=========================================================="
echo "  Required Environment Variables for Worker Service"
echo "==========================================================${NC}"
echo ""
echo "You need to configure the following environment variables"
echo "in the Railway Dashboard for the 'meta-analysis-worker' service:"
echo ""

cat << 'EOF'
1. DATABASE_URL
   Value: ${{Postgres.DATABASE_URL}}
   Description: PostgreSQL database connection string

2. REDIS_URL
   Value: ${{Redis.REDIS_URL}}
   Description: Redis connection string for Celery broker

3. ANTHROPIC_API_KEY
   Value: <copy from backend service>
   Description: API key for Claude AI integration

4. SECRET_KEY
   Value: <copy from backend service>
   Description: Flask application secret key

5. OPENAI_API_KEY (Optional but recommended)
   Value: <copy from backend service>
   Description: API key for OpenAI integration

6. PUBMED_API_KEY (Optional)
   Value: <copy from backend service>
   Description: API key for PubMed literature searches

7. PUBMED_EMAIL (Optional)
   Value: <copy from backend service>
   Description: Email for PubMed API identification

8. PYTHONUNBUFFERED
   Value: 1
   Description: Ensures logs are flushed immediately

9. LOG_LEVEL
   Value: INFO
   Description: Application logging level

EOF

echo ""
echo -e "${YELLOW}=========================================================="
echo "  Step-by-Step Configuration Instructions"
echo "==========================================================${NC}"
echo ""

echo "1. Open Railway Dashboard in your browser:"
echo "   https://railway.app/dashboard"
echo ""

echo "2. Navigate to your project:"
echo "   → Meta-Analysis-Tool"
echo ""

echo "3. Open the backend service to view existing variables:"
echo "   → Click 'backend' service"
echo "   → Click 'Variables' tab"
echo "   → Keep this tab open for reference"
echo ""

echo "4. Open the worker service in a new tab:"
echo "   → Go back to project view"
echo "   → Click 'meta-analysis-worker' service"
echo "   → Click 'Variables' tab"
echo ""

echo "5. Add each variable to the worker service:"
echo "   → Click '+ New Variable' button"
echo "   → Enter variable name and value"
echo "   → For DATABASE_URL and REDIS_URL, use the Railway references:"
echo "     • DATABASE_URL = \${{Postgres.DATABASE_URL}}"
echo "     • REDIS_URL = \${{Redis.REDIS_URL}}"
echo "   → For other variables, copy exact values from backend service"
echo ""

echo "6. Verify all required variables are set:"
echo "   ✓ DATABASE_URL"
echo "   ✓ REDIS_URL"
echo "   ✓ ANTHROPIC_API_KEY"
echo "   ✓ SECRET_KEY"
echo "   ✓ OPENAI_API_KEY (recommended)"
echo "   ✓ PYTHONUNBUFFERED"
echo "   ✓ LOG_LEVEL"
echo ""

echo -e "${CYAN}=========================================================="
echo "  Verification"
echo "==========================================================${NC}"
echo ""

read -p "Have you configured all the variables? (y/n): " configured

if [ "$configured" != "y" ]; then
    echo ""
    echo -e "${YELLOW}Please configure the variables first, then run this script again.${NC}"
    echo ""
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Variables configured${NC}"
echo ""

echo -e "${CYAN}=========================================================="
echo "  Next Steps: Redeploy Worker Service"
echo "==========================================================${NC}"
echo ""

echo "1. In Railway Dashboard → meta-analysis-worker:"
echo "   → Click the three dots menu (⋯) in the top right"
echo "   → Select 'Redeploy'"
echo ""

echo "2. Wait for the deployment to complete (2-4 minutes)"
echo "   → Watch the deployment logs for progress"
echo "   → Look for 'celery@meta-analysis-worker ready.'"
echo ""

echo "3. Verify worker connection:"
echo "   → Run: ./verify-worker-health.sh"
echo "   → Or check: https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed"
echo ""

read -p "Press ENTER to trigger health check in 30 seconds..."

echo ""
echo "Waiting 30 seconds for deployment to start..."
sleep 30

echo ""
echo "Checking deployment health..."
echo ""

for i in {1..12}; do
    echo "Attempt $i/12: Checking worker health..."

    HEALTH=$(curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed)
    CELERY_STATUS=$(echo "$HEALTH" | jq -r '.checks.celery.status // "unknown"')
    CELERY_MESSAGE=$(echo "$HEALTH" | jq -r '.checks.celery.message // "unknown"')

    echo "  Status: $CELERY_STATUS"
    echo "  Message: $CELERY_MESSAGE"

    if [ "$CELERY_STATUS" = "healthy" ]; then
        echo ""
        echo -e "${GREEN}=========================================================="
        echo "  🎉 SUCCESS! Celery workers are HEALTHY!"
        echo "==========================================================${NC}"
        echo ""
        echo "$HEALTH" | jq '.'
        echo ""
        exit 0
    fi

    if [ $i -lt 12 ]; then
        echo "  Waiting 10 seconds before next check..."
        sleep 10
    fi
done

echo ""
echo -e "${YELLOW}=========================================================="
echo "  ⚠️  Workers not healthy after 2 minutes"
echo "==========================================================${NC}"
echo ""
echo "Please check the worker service logs in Railway Dashboard:"
echo "  → Meta-Analysis-Tool → meta-analysis-worker → Logs"
echo ""
echo "Common issues to look for:"
echo "  • Connection errors to Redis or Postgres"
echo "  • Missing environment variables"
echo "  • Python import errors"
echo "  • Invalid API keys"
echo ""
echo "For detailed troubleshooting, see: CELERY_WORKER_DEPLOYMENT.md"
echo ""

exit 1
