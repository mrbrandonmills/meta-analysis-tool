#!/bin/bash
# Railway Deployment Automation Script
# This will deploy Redis and Celery worker to your existing Railway project

set -e

echo "=================================================="
echo "  Railway Infrastructure Deployment"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Railway CLI not found. Install from: https://docs.railway.com/guides/cli${NC}"
    exit 1
fi

# Get Railway projects
echo "Fetching your Railway projects..."
PROJECTS=$(railway list 2>&1)
echo "$PROJECTS"
echo ""

# Ask user to select project
echo -e "${YELLOW}Which project do you want to use?${NC}"
echo "1) Meta-Analysis-Tool (existing deployment)"
echo "2) meta-analysis-tool (newly created)"
read -p "Enter number (1 or 2): " PROJECT_CHOICE

if [ "$PROJECT_CHOICE" = "1" ]; then
    PROJECT_NAME="Meta-Analysis-Tool"
else
    PROJECT_NAME="meta-analysis-tool"
fi

echo ""
echo -e "${GREEN}Using project: $PROJECT_NAME${NC}"
echo ""

# Try to link to project
echo "Linking to Railway project..."
# This will require manual selection if fully interactive
# For now, we'll work with the assumption user has selected it

# Check current health
echo "Checking current deployment health..."
HEALTH=$(curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed)
echo "$HEALTH" | jq '.' || echo "$HEALTH"
echo ""

# Parse status
DB_STATUS=$(echo "$HEALTH" | jq -r '.checks.database.status // "unknown"' 2>/dev/null)
REDIS_STATUS=$(echo "$HEALTH" | jq -r '.checks.redis.status // "unknown"' 2>/dev/null)
CELERY_STATUS=$(echo "$HEALTH" | jq -r '.checks.celery.status // "unknown"' 2>/dev/null)

echo "Current Status:"
echo -e "  Database: ${GREEN}$DB_STATUS${NC}"
echo -e "  Redis: $([ "$REDIS_STATUS" = "healthy" ] && echo "${GREEN}$REDIS_STATUS${NC}" || echo "${RED}$REDIS_STATUS${NC}")"
echo -e "  Celery: $([ "$CELERY_STATUS" = "healthy" ] && echo "${GREEN}$CELERY_STATUS${NC}" || echo "${RED}$CELERY_STATUS${NC}")"
echo ""

# Step 1: Add Redis
if [ "$REDIS_STATUS" != "healthy" ]; then
    echo "=================================================="
    echo "  STEP 1: Add Redis Database"
    echo "=================================================="
    echo ""
    echo "Railway CLI doesn't support adding databases non-interactively."
    echo ""
    echo -e "${YELLOW}MANUAL ACTION REQUIRED:${NC}"
    echo "1. Open: https://railway.app/dashboard"
    echo "2. Find project: $PROJECT_NAME"
    echo "3. Click '+ New' → 'Database' → 'Add Redis'"
    echo "4. Wait 2-3 minutes for backend to redeploy"
    echo ""
    read -p "Press ENTER when Redis is added and backend has redeployed..."
    
    echo ""
    echo "Verifying Redis connection..."
    sleep 5
    
    for i in {1..5}; do
        HEALTH=$(curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed)
        REDIS_STATUS=$(echo "$HEALTH" | jq -r '.checks.redis.status // "unknown"' 2>/dev/null)
        
        if [ "$REDIS_STATUS" = "healthy" ]; then
            echo -e "${GREEN}✓ Redis is now healthy!${NC}"
            break
        else
            echo "Attempt $i/5: Redis status is $REDIS_STATUS, waiting..."
            sleep 10
        fi
    done
    
    if [ "$REDIS_STATUS" != "healthy" ]; then
        echo -e "${RED}✗ Redis is still not healthy. Check Railway dashboard for errors.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Redis is already healthy${NC}"
fi

echo ""

# Step 2: Check migrations
echo "=================================================="
echo "  STEP 2: Verify Database Migrations"
echo "=================================================="
echo ""
echo "Migrations run automatically in start.sh"
echo "Testing registration endpoint..."
echo ""

TEST_EMAIL="test-$(date +%s)@example.com"
REGISTER_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST \
    https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
    -H 'Content-Type: application/json' \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"Test123!\",\"full_name\":\"Test User\"}")

HTTP_STATUS=$(echo "$REGISTER_RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
RESPONSE_BODY=$(echo "$REGISTER_RESPONSE" | sed '/HTTP_STATUS:/d')

if [ "$HTTP_STATUS" = "201" ]; then
    echo -e "${GREEN}✓ Registration successful (HTTP 201)${NC}"
    echo "$RESPONSE_BODY" | jq '.' 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo -e "${YELLOW}⚠ Registration returned HTTP $HTTP_STATUS${NC}"
    echo "$RESPONSE_BODY" | jq '.' 2>/dev/null || echo "$RESPONSE_BODY"
    echo ""
    echo "Migrations may need to run. Try redeploying backend service."
fi

echo ""

# Step 3: Deploy Celery Worker
if [ "$CELERY_STATUS" != "healthy" ]; then
    echo "=================================================="
    echo "  STEP 3: Deploy Celery Worker Service"
    echo "=================================================="
    echo ""
    echo "Creating Celery worker configuration..."
    
    cat > /tmp/railway-worker-config.json << 'EOF'
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
    
    echo ""
    echo -e "${YELLOW}MANUAL ACTION REQUIRED:${NC}"
    echo ""
    echo "Railway CLI doesn't support creating services non-interactively."
    echo ""
    echo "Please create Celery worker in Railway dashboard:"
    echo ""
    echo "1. Go to: https://railway.app/dashboard"
    echo "2. Open project: $PROJECT_NAME"
    echo "3. Click '+ New' → 'Empty Service'"
    echo "4. Name: meta-analysis-worker"
    echo ""
    echo "5. Settings → Source:"
    echo "   - Connect GitHub: mrbrandonmills/meta-analysis-tool"
    echo "   - Branch: main"
    echo ""
    echo "6. Settings → Build:"
    echo "   - Builder: DOCKERFILE"
    echo "   - Dockerfile Path: backend/Dockerfile"
    echo ""
    echo "7. Settings → Deploy → Start Command:"
    echo "   celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4"
    echo ""
    echo "8. Settings → Variables (copy from backend service):"
    echo "   DATABASE_URL, REDIS_URL, ANTHROPIC_API_KEY, SECRET_KEY,"
    echo "   OPENAI_API_KEY, PYTHONUNBUFFERED=1, LOG_LEVEL=INFO"
    echo ""
    echo "9. Click 'Deploy'"
    echo ""
    read -p "Press ENTER when Celery worker is deployed..."
    
    echo ""
    echo "Verifying Celery workers..."
    sleep 10
    
    for i in {1..5}; do
        HEALTH=$(curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed)
        CELERY_STATUS=$(echo "$HEALTH" | jq -r '.checks.celery.status // "unknown"' 2>/dev/null)
        
        if [ "$CELERY_STATUS" = "healthy" ]; then
            echo -e "${GREEN}✓ Celery workers are now healthy!${NC}"
            break
        else
            echo "Attempt $i/5: Celery status is $CELERY_STATUS, waiting..."
            sleep 10
        fi
    done
    
    if [ "$CELERY_STATUS" != "healthy" ]; then
        echo -e "${YELLOW}⚠ Celery is still not healthy. Check worker logs in Railway.${NC}"
    fi
else
    echo -e "${GREEN}✓ Celery is already healthy${NC}"
fi

echo ""

# Final verification
echo "=================================================="
echo "  FINAL VERIFICATION"
echo "=================================================="
echo ""

FINAL_HEALTH=$(curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed)
echo "$FINAL_HEALTH" | jq '.'

DB_STATUS=$(echo "$FINAL_HEALTH" | jq -r '.checks.database.status // "unknown"' 2>/dev/null)
REDIS_STATUS=$(echo "$FINAL_HEALTH" | jq -r '.checks.redis.status // "unknown"' 2>/dev/null)
CELERY_STATUS=$(echo "$FINAL_HEALTH" | jq -r '.checks.celery.status // "unknown"' 2>/dev/null)

echo ""
echo "Final Status:"
echo -e "  Database: ${GREEN}$DB_STATUS${NC}"
echo -e "  Redis: $([ "$REDIS_STATUS" = "healthy" ] && echo "${GREEN}$REDIS_STATUS${NC}" || echo "${RED}$REDIS_STATUS${NC}")"
echo -e "  Celery: $([ "$CELERY_STATUS" = "healthy" ] && echo "${GREEN}$CELERY_STATUS${NC}" || echo "${RED}$CELERY_STATUS${NC}")"
echo ""

if [ "$DB_STATUS" = "healthy" ] && [ "$REDIS_STATUS" = "healthy" ] && [ "$CELERY_STATUS" = "healthy" ]; then
    echo "=================================================="
    echo -e "${GREEN}  🎉 ALL SYSTEMS OPERATIONAL!${NC}"
    echo "=================================================="
    echo ""
    echo "Platform is ready for:"
    echo "  ✓ Board meeting demonstration"
    echo "  ✓ Alpha testing"
    echo "  ✓ Real research questions"
    echo ""
else
    echo "=================================================="
    echo -e "${YELLOW}  ⚠ DEPLOYMENT INCOMPLETE${NC}"
    echo "=================================================="
    echo ""
    echo "Some services still need configuration."
    echo "Check Railway dashboard for errors."
    echo ""
fi

echo "Next steps:"
echo "  1. Review board presentation: open BOARD_PRESENTATION_STRATEGY.md"
echo "  2. Test with real research question"
echo "  3. Run integration tests"
echo ""

