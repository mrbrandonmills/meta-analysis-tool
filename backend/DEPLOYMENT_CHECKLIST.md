# Railway Deployment Checklist

## ⚠️ CRITICAL: Run This Before EVERY Deployment

This checklist prevents import-time errors that cause Railway to fall back to old deployments.

## 1. Pre-Deployment Verification

### A. Check for Import-Time Errors
```bash
cd /Users/brandon/meta-analysis-tool/backend

# Test imports locally
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from app.main import app
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ IMPORT ERROR: {e}')
    sys.exit(1)
"
```

### B. Verify All Referenced Names Exist
Common patterns that cause failures:
- ✅ Check enums have all referenced values (e.g., `UserRole.EDITOR`, `UserRole.ADMIN`)
- ✅ Check imported functions exist in source modules
- ✅ Check function signatures match at call sites
- ✅ Check all model fields exist
- ✅ Verify FastAPI parameter types (`Path` vs `Query` for path params)

### C. Test Router Registration
```python
# In main.py, verify all routers are imported and registered:
from app.api.v1 import (
    meta_analysis, agents, studies, auth, health, reports,
    manuscripts, peer_reviews, researchers, reviewer_matcher,
    progress, researcher_enrichment, research_direction,
    subscriptions, payouts, review_approval
)

# All routers must have app.include_router() calls
```

## 2. Local Testing

```bash
# Start the app locally
uvicorn app.main:app --reload

# In another terminal, verify route count:
curl -s http://localhost:8080/openapi.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Total routes: {len(data[\"paths\"])}')
# Should be 76+ routes, not 28
"
```

## 3. Deploy to Railway

```bash
# Commit changes
git add -A
git commit -m "Your commit message"

# Push to GitHub
git push

# Deploy to Railway
railway up --detach
```

## 4. Post-Deployment Verification

### A. Wait for Build (90-120 seconds)
```bash
sleep 120
```

### B. Check for Errors
```bash
# Check deployment logs for errors
railway logs --deployment | grep -E "Error|Exception|ImportError" | tail -20

# Should see NO errors, only:
# - "Starting Meta-Analysis Research Platform"
# - "✓ Meta-Analysis Research Platform started successfully"
# - "Application startup complete"
```

### C. Verify Route Count
```bash
curl -s https://meta-analysis-tool-production.up.railway.app/openapi.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
paths = data.get('paths', {})
print(f'Total routes: {len(paths)}')

# Check payment routes
payment_routes = [p for p in paths.keys() if any(x in p for x in ['subscription', 'payout', 'approval', 'direction'])]
print(f'Payment routes: {len(payment_routes)}')

if len(paths) < 70:
    print('❌ DEPLOYMENT FAILED: Route count too low')
    sys.exit(1)
if len(payment_routes) < 15:
    print('❌ DEPLOYMENT FAILED: Payment routes missing')
    sys.exit(1)
print('✅ All routes registered successfully')
"
```

### D. Test Health Check
```bash
curl -s https://meta-analysis-tool-production.up.railway.app/api/v1/health
# Should return: {"status":"healthy"}
```

## 5. If Deployment Fails

### A. Immediate Actions
1. **DO NOT deploy again without fixing**
2. Check logs: `railway logs --deployment | tail -100`
3. Look for the FIRST error (usually an ImportError or AttributeError)
4. Railway will automatically fall back to last working deployment

### B. Common Error Patterns

#### Error: "cannot import name 'X' from 'Y'"
**Cause:** Trying to import a name that doesn't exist in the module
**Fix:** Either add the missing export or change the import

#### Error: "module 'X' has no attribute 'Y'"
**Cause:** Referencing an attribute/enum value that doesn't exist
**Fix:** Add the missing attribute to the enum/class

#### Error: "Cannot use Query for path param"
**Cause:** Using `Query()` instead of `Path()` for URL path parameters
**Fix:** Change `Query(...)` to `Path(...)` for parameters in curly braces like `{user_id}`

#### Error: "Worker process died unexpectedly"
**Cause:** Import-time error crashing all worker processes
**Fix:** Check the logs for the specific ImportError

### C. Debugging Process
```bash
# 1. Read deployment logs
railway logs --deployment | grep -E "Error|Exception|Traceback" -A 10 > /tmp/error.log

# 2. Identify the root error (first error in logs)
cat /tmp/error.log

# 3. Fix the error locally

# 4. Test locally
python3 -c "from app.main import app; print('✅ Imports work')"

# 5. Re-deploy
git add -A && git commit -m "Fix import error" && git push && railway up --detach
```

## 6. Historical Issues (For Reference)

### Issue 1: Missing EDITOR Role (2025-01-12)
**Error:** `AttributeError: 'UserRole' has no attribute 'EDITOR'`
**Cause:** `require_editor = RoleChecker([UserRole.EDITOR])` but `EDITOR` not in enum
**Fix:** Added `EDITOR = "editor"` to `UserRole` enum

### Issue 2: Wrong Stripe Parameter (2025-01-12)
**Error:** `TypeError: create_subscription() got unexpected keyword argument 'price_amount_cents'`
**Cause:** Called with `price_amount_cents=10000` but method expects `tier="standard"`
**Fix:** Changed parameter name to match method signature

### Issue 3: app.api.deps Module Missing
**Error:** `ModuleNotFoundError: No module named 'app.api.deps'`
**Cause:** Imported from non-existent `app.api.deps` module
**Fix:** Changed to import from `app.core.security` and `app.db.session`

### Issue 4: Query vs Path Parameters
**Error:** `AssertionError: Cannot use Query for path param`
**Cause:** Used `Query()` for URL path parameters
**Fix:** Changed to `Path()` for path parameters

## 7. Prevention Strategies

### A. Before Writing New Code
1. Check what enums/classes exist before referencing them
2. Verify function signatures before calling them
3. Use correct FastAPI parameter types

### B. Code Review Checklist
- [ ] All imports resolve correctly
- [ ] All enum values exist
- [ ] All function calls match signatures
- [ ] Path params use `Path()`, not `Query()`
- [ ] No circular imports

### C. Automated Checks (TODO)
Create pre-commit hook:
```bash
#!/bin/bash
# .git/hooks/pre-commit
python3 -c "from app.main import app" || exit 1
```

## 8. Emergency Rollback

If deployment is completely broken:
```bash
# Find last working deployment ID from Railway dashboard
# Manually redeploy that version through Railway UI
```

## Remember
- ✅ Test imports locally BEFORE deploying
- ✅ Check deployment logs for errors
- ✅ Verify route count after deployment
- ✅ NEVER deploy again without fixing errors
- ✅ Document all new error patterns here
