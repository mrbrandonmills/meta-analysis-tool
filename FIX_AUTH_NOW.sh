#!/bin/bash
# Emergency Fix for Authentication HTTP 500 Error
# CTO-Approved Fix Script
# Estimated Time: 30 minutes

set -e  # Exit on error

echo "=============================================================================="
echo "EMERGENCY FIX: Authentication HTTP 500 Error"
echo "=============================================================================="
echo "This script will:"
echo "  1. Diagnose migration state in production"
echo "  2. Apply missing migration 003"
echo "  3. Verify authentication works"
echo "  4. Fix start.sh to prevent future silent failures"
echo "  5. Deploy the fix"
echo "=============================================================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check Railway CLI is installed
echo -e "${BLUE}Step 1: Verifying Railway CLI...${NC}"
if ! command -v railway &> /dev/null; then
    echo -e "${RED}ERROR: Railway CLI not installed${NC}"
    echo "Install with: npm install -g @railway/cli"
    exit 1
fi
echo -e "${GREEN}✓ Railway CLI found${NC}"
echo ""

# Step 2: Link to production environment
echo -e "${BLUE}Step 2: Linking to production environment...${NC}"
cd /Users/brandon/meta-analysis-tool
railway link
echo ""

# Step 3: Check current migration version
echo -e "${BLUE}Step 3: Checking current migration version...${NC}"
echo "Running: railway run alembic current"
CURRENT_VERSION=$(railway run alembic current 2>&1 || echo "ERROR")
echo "Current migration: $CURRENT_VERSION"

if echo "$CURRENT_VERSION" | grep -q "003"; then
    echo -e "${GREEN}✓ Migration 003 already applied${NC}"
    echo -e "${YELLOW}WARNING: Migrations are current but auth still failing${NC}"
    echo "This may indicate a different issue. Continuing anyway..."
else
    echo -e "${YELLOW}⚠ Migration 003 NOT applied yet${NC}"
fi
echo ""

# Step 4: Check database schema
echo -e "${BLUE}Step 4: Checking users table schema...${NC}"
echo "Checking for problematic columns (orcid, deleted_at, created_by, updated_by)..."
railway run python -c "
from sqlalchemy import create_engine, inspect
import os
engine = create_engine(os.environ['DATABASE_URL'])
inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('users')]
print('Users table columns:', columns)
extra_cols = [c for c in ['orcid', 'deleted_at', 'created_by', 'updated_by'] if c in columns]
if extra_cols:
    print('FOUND EXTRA COLUMNS:', extra_cols)
    print('Migration 003 needs to run!')
else:
    print('Schema looks correct - extra columns already removed')
" || echo "Could not check schema"
echo ""

# Step 5: Apply migrations
echo -e "${BLUE}Step 5: Applying migrations to head...${NC}"
echo "Running: railway run alembic upgrade head"
railway run alembic upgrade head

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations completed successfully${NC}"
else
    echo -e "${RED}✗ Migration failed${NC}"
    echo "Check the error above and fix manually"
    exit 1
fi
echo ""

# Step 6: Verify migration
echo -e "${BLUE}Step 6: Verifying migration version...${NC}"
NEW_VERSION=$(railway run alembic current)
echo "New migration version: $NEW_VERSION"

if echo "$NEW_VERSION" | grep -q "003"; then
    echo -e "${GREEN}✓ Migration 003 confirmed applied${NC}"
else
    echo -e "${RED}✗ Migration 003 not at head${NC}"
    exit 1
fi
echo ""

# Step 7: Test authentication
echo -e "${BLUE}Step 7: Testing authentication endpoint...${NC}"
TEST_EMAIL="cto-fix-test-$(date +%s)@example.com"
echo "Attempting to register test user: $TEST_EMAIL"

RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST \
  https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"SecurePass123!\",\"full_name\":\"CTO Fix Test\"}")

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

echo "HTTP Status: $HTTP_CODE"
echo "Response: $BODY"

if [ "$HTTP_CODE" = "201" ]; then
    echo -e "${GREEN}✓✓✓ SUCCESS! Authentication is working!${NC}"
    echo ""
    echo -e "${GREEN}User registered successfully:${NC}"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
elif [ "$HTTP_CODE" = "400" ] && echo "$BODY" | grep -q "already registered"; then
    echo -e "${GREEN}✓ Authentication works (user already exists)${NC}"
elif [ "$HTTP_CODE" = "500" ]; then
    echo -e "${RED}✗ Authentication still failing with HTTP 500${NC}"
    echo "Response: $BODY"
    echo ""
    echo "The migration ran but auth still fails. Possible causes:"
    echo "  1. Database connection pool exhausted"
    echo "  2. Different schema issue"
    echo "  3. Code issue not related to schema"
    echo ""
    echo "Next steps:"
    echo "  - Check Railway logs: railway logs"
    echo "  - Check database connections: railway run python -c 'from app.db.session import get_async_db; print(get_async_db)'"
    exit 1
else
    echo -e "${YELLOW}⚠ Unexpected response: HTTP $HTTP_CODE${NC}"
    echo "$BODY"
fi
echo ""

# Step 8: Run full validation
echo -e "${BLUE}Step 8: Running production validation tests...${NC}"
if [ -f "production_readiness_test.py" ]; then
    python3 production_readiness_test.py
    echo -e "${GREEN}✓ Validation tests complete${NC}"
else
    echo -e "${YELLOW}⚠ Validation test script not found, skipping${NC}"
fi
echo ""

# Step 9: Fix start.sh to prevent future silent failures
echo -e "${BLUE}Step 9: Fixing start.sh to fail on migration errors...${NC}"

# Create backup
cp backend/start.sh backend/start.sh.backup

# Fix the migration error handling
cat > backend/start.sh << 'EOF'
#!/bin/sh
# Railway startup script for Meta Analysis Tool Backend
# Uses /bin/sh for compatibility with minimal Docker images
# Runs uvicorn with production settings

set -e  # Exit on any error

# Verify virtual environment is accessible
if [ ! -d "/opt/venv" ]; then
    echo "ERROR: Virtual environment not found at /opt/venv"
    exit 1
fi

# Ensure PATH includes virtual environment binaries
export PATH="/opt/venv/bin:$PATH"

# Verify uvicorn is available
if ! command -v uvicorn >/dev/null 2>&1; then
    echo "ERROR: uvicorn not found in PATH"
    exit 1
fi

# Set default PORT if not provided by Railway
PORT="${PORT:-8000}"

# Verify we're in the correct directory
if [ ! -d "/app/app" ]; then
    echo "ERROR: Application directory /app/app not found"
    exit 1
fi

# Export PYTHONPATH to ensure app module can be found
export PYTHONPATH="/app:${PYTHONPATH}"

# Log startup information
echo "Starting Meta Analysis Tool Backend API..."
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Uvicorn location: $(which uvicorn)"
echo "Port: ${PORT}"
echo "Python path: ${PYTHONPATH}"

# Run database migrations - FAIL DEPLOYMENT IF MIGRATIONS FAIL
echo "Running database migrations..."
if command -v alembic >/dev/null 2>&1; then
    alembic upgrade head
    if [ $? -ne 0 ]; then
        echo "ERROR: Database migrations failed!"
        echo "Deployment cannot continue with failed migrations"
        exit 1  # CRITICAL FIX: Fail deployment instead of WARNING
    fi
    echo "✓ Database migrations completed successfully"
else
    echo "ERROR: alembic not found!"
    echo "Cannot run migrations - deployment failed"
    exit 1  # CRITICAL FIX: Fail if alembic missing
fi

# Start uvicorn with production-optimized settings
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --workers 2 \
    --loop uvloop \
    --log-level info \
    --no-access-log \
    --proxy-headers \
    --forwarded-allow-ips "*"
EOF

chmod +x backend/start.sh

echo -e "${GREEN}✓ start.sh updated to fail on migration errors${NC}"
echo ""

# Step 10: Commit and push fix
echo -e "${BLUE}Step 10: Committing and deploying fix...${NC}"
git add backend/start.sh
git commit -m "fix: Fail deployment if database migrations fail

CRITICAL FIX: Prevent silent migration failures
- Changed start.sh to exit 1 if migrations fail
- Changed start.sh to exit 1 if alembic not found
- Removed WARNING handling that allowed broken deployments

Previously, migration failures were logged as WARNING but allowed
the server to start with broken schema. This caused HTTP 500 errors
on authentication endpoints.

Now, if migrations fail, the entire deployment fails and Railway
will show the error clearly.

Fixes: Silent migration failures causing authentication HTTP 500

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

echo -e "${GREEN}✓ Changes committed${NC}"

echo "Pushing to Railway..."
git push origin main

echo -e "${GREEN}✓ Pushed to Railway${NC}"
echo ""

# Step 11: Wait for deployment
echo -e "${BLUE}Step 11: Waiting for Railway deployment...${NC}"
echo "Monitoring deployment status..."
echo "(This may take 2-3 minutes)"
echo ""

# Wait 30 seconds for deployment to start
sleep 30

# Check deployment status
for i in {1..10}; do
    echo "Checking deployment status (attempt $i/10)..."

    # Test health endpoint
    if curl -s --max-time 5 https://meta-analysis-tool-production.up.railway.app/api/v1/health | grep -q "healthy"; then
        echo -e "${GREEN}✓ Deployment successful - API is responding${NC}"
        break
    else
        echo "Still deploying..."
        sleep 15
    fi

    if [ $i -eq 10 ]; then
        echo -e "${YELLOW}⚠ Deployment taking longer than expected${NC}"
        echo "Check Railway dashboard for deployment status"
    fi
done
echo ""

# Final verification
echo -e "${BLUE}Step 12: Final verification...${NC}"
echo "Testing authentication one more time..."

FINAL_TEST_EMAIL="final-verification-$(date +%s)@example.com"
FINAL_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST \
  https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$FINAL_TEST_EMAIL\",\"password\":\"SecurePass123!\",\"full_name\":\"Final Verification\"}")

FINAL_HTTP_CODE=$(echo "$FINAL_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)

echo "Final auth test: HTTP $FINAL_HTTP_CODE"

if [ "$FINAL_HTTP_CODE" = "201" ]; then
    echo ""
    echo "=============================================================================="
    echo -e "${GREEN}✓✓✓ SUCCESS! Production is ready!${NC}"
    echo "=============================================================================="
    echo ""
    echo "Summary:"
    echo "  - Migration 003 applied ✓"
    echo "  - Authentication working ✓"
    echo "  - Start script fixed to prevent future silent failures ✓"
    echo "  - Deployed to production ✓"
    echo ""
    echo -e "${GREEN}RECOMMENDATION: GO for board meeting${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run full test suite: python3 production_readiness_test.py"
    echo "  2. Monitor Railway logs: railway logs"
    echo "  3. Prepare board demo materials"
    echo ""
else
    echo ""
    echo "=============================================================================="
    echo -e "${RED}✗ Authentication still not working${NC}"
    echo "=============================================================================="
    echo ""
    echo "HTTP Code: $FINAL_HTTP_CODE"
    echo "Response: $(echo \"$FINAL_RESPONSE\" | sed '/HTTP_CODE:/d')"
    echo ""
    echo -e "${YELLOW}RECOMMENDATION: NO-GO - further investigation needed${NC}"
    echo ""
    echo "Debugging steps:"
    echo "  1. Check Railway logs: railway logs"
    echo "  2. Check database schema manually"
    echo "  3. Check for connection pool issues"
    echo "  4. Consult with backend developer"
fi

echo ""
echo "Fix script complete."
echo "Timestamp: $(date)"
echo "=============================================================================="
