#!/bin/bash

# DEPLOY_NOW.sh - One-command deployment execution
# This script guides you through the 3 manual Railway dashboard steps

set -e

echo "========================================="
echo "  Meta-Analysis Tool Deployment"
echo "========================================="
echo ""
echo "This script will guide you through deploying:"
echo "  1. Redis database (5 min)"
echo "  2. Database migrations (already in code)"
echo "  3. Celery worker service (20 min)"
echo ""
echo "Total time: ~30 minutes"
echo ""

# Check current status
echo "Checking current deployment status..."
HEALTH_CHECK=$(curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed 2>&1 || echo '{"error":"unreachable"}')

echo "$HEALTH_CHECK" | jq '.' 2>/dev/null || echo "$HEALTH_CHECK"
echo ""

# Parse status
DB_STATUS=$(echo "$HEALTH_CHECK" | jq -r '.checks.database.status // "unknown"' 2>/dev/null)
REDIS_STATUS=$(echo "$HEALTH_CHECK" | jq -r '.checks.redis.status // "unknown"' 2>/dev/null)
CELERY_STATUS=$(echo "$HEALTH_CHECK" | jq -r '.checks.celery.status // "unknown"' 2>/dev/null)

echo "Current Status:"
echo "  Database: $DB_STATUS"
echo "  Redis: $REDIS_STATUS"
echo "  Celery: $CELERY_STATUS"
echo ""

# Step 1: Redis
if [ "$REDIS_STATUS" != "healthy" ]; then
    echo "========================================="
    echo "  STEP 1: Deploy Redis"
    echo "========================================="
    echo ""
    echo "ACTION REQUIRED:"
    echo "1. Open: https://railway.app/dashboard"
    echo "2. Find project: 'meta-analysis-tool'"
    echo "3. Click '+ New' button"
    echo "4. Select 'Database'"
    echo "5. Click 'Add Redis'"
    echo "6. Wait 2-3 minutes for backend to redeploy"
    echo ""
    read -p "Press ENTER when Redis is deployed and backend has redeployed..."
    
    echo "Verifying Redis..."
    sleep 5
    HEALTH_CHECK=$(curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed)
    REDIS_STATUS=$(echo "$HEALTH_CHECK" | jq -r '.checks.redis.status // "unknown"')
    
    if [ "$REDIS_STATUS" = "healthy" ]; then
        echo "✓ Redis is healthy!"
    else
        echo "⚠ Redis status: $REDIS_STATUS"
        echo "Wait a few more minutes and run this script again."
        exit 1
    fi
else
    echo "✓ Redis already healthy, skipping..."
fi

echo ""

# Step 2: Migrations (already in code)
echo "========================================="
echo "  STEP 2: Database Migrations"
echo "========================================="
echo ""
echo "Migrations are already configured in start.sh"
echo "They run automatically on every deployment."
echo ""
echo "Testing registration endpoint..."
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"test$(date +%s)@example.com\",\"password\":\"Test123!\",\"full_name\":\"Test\"}" \
  -w "\nHTTP Status: %{http_code}\n" 2>/dev/null | head -5

echo ""
read -p "Did registration return HTTP 201? (y/n): " MIGRATIONS_OK

if [ "$MIGRATIONS_OK" != "y" ]; then
    echo ""
    echo "Migrations may not have run. Try manually redeploying backend:"
    echo "1. Go to Railway dashboard"
    echo "2. Click 'backend' service"
    echo "3. Click 'Redeploy' button"
    echo "4. Wait for deployment to complete"
    echo ""
    read -p "Press ENTER after redeploying..."
fi

echo ""

# Step 3: Celery Workers
if [ "$CELERY_STATUS" != "healthy" ]; then
    echo "========================================="
    echo "  STEP 3: Deploy Celery Workers"
    echo "========================================="
    echo ""
    echo "ACTION REQUIRED:"
    echo ""
    echo "1. Open: https://railway.app/dashboard"
    echo "2. Click '+ New' → 'Empty Service'"
    echo "3. Name: 'meta-analysis-worker'"
    echo "4. Settings → Source → Connect to GitHub"
    echo "   - Repo: mrbrandonmills/meta-analysis-tool"
    echo "   - Branch: main"
    echo "5. Settings → Build"
    echo "   - Builder: DOCKERFILE"
    echo "   - Dockerfile Path: backend/Dockerfile"
    echo "6. Settings → Deploy → Start Command:"
    echo "   celery -A app.workers.celery_app worker --loglevel=info --queues=default,search,analysis,reviewer,notifications --concurrency=4"
    echo ""
    echo "7. Settings → Variables (copy from backend service):"
    echo "   - DATABASE_URL"
    echo "   - REDIS_URL"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - SECRET_KEY"
    echo "   - OPENAI_API_KEY"
    echo "   - PYTHONUNBUFFERED=1"
    echo "   - LOG_LEVEL=INFO"
    echo ""
    echo "8. Click 'Deploy'"
    echo "9. Wait for build (5-10 minutes)"
    echo "10. Check logs show 'celery@meta-analysis-worker ready'"
    echo ""
    read -p "Press ENTER when Celery worker is deployed and ready..."
    
    echo "Verifying Celery..."
    sleep 5
    HEALTH_CHECK=$(curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed)
    CELERY_STATUS=$(echo "$HEALTH_CHECK" | jq -r '.checks.celery.status // "unknown"')
    
    if [ "$CELERY_STATUS" = "healthy" ]; then
        echo "✓ Celery is healthy!"
    else
        echo "⚠ Celery status: $CELERY_STATUS"
        echo "Check worker logs in Railway dashboard."
    fi
else
    echo "✓ Celery already healthy, skipping..."
fi

echo ""
echo "========================================="
echo "  FINAL VERIFICATION"
echo "========================================="
echo ""

# Run full verification
./verify-deployment.sh

echo ""
echo "========================================="
echo "  DEPLOYMENT COMPLETE!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Review board presentation: BOARD_PRESENTATION_STRATEGY.md"
echo "  2. Run integration tests with real research questions"
echo "  3. Practice demonstration for board meeting"
echo ""
