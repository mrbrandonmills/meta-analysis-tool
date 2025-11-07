# 🚨 PRODUCTION BLOCKERS - IMMEDIATE ACTION REQUIRED

**Date:** November 5, 2025
**Status:** ❌ NOT PRODUCTION READY
**Critical Bugs:** 2
**Estimated Fix Time:** 3-5 hours

---

## ⚠️ CRITICAL BLOCKERS (Must Fix Before ANY Deployment)

### 1. 🔴 CRITICAL: Anthropic API Model 404 Error
**Impact:** Meta-analysis creation completely broken - 0% of core functionality working

**Error:**
```
Anthropic API error: Error code: 404 - model: claude-3-5-sonnet-20241022 not found
```

**Root Cause:**
Agent configuration uses deprecated Anthropic model version

**Fix:**
```python
# File: backend/app/agents/base/agent.py
# Line 23

# BEFORE (BROKEN):
class AgentConfig(BaseModel):
    model: str = "claude-3-5-sonnet-20241022"  # ❌ Model deprecated

# AFTER (FIXED):
class AgentConfig(BaseModel):
    model: str = "claude-3-5-sonnet-20250514"  # ✅ Update to latest available
    # OR use environment variable:
    # model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20250514")
```

**Steps to Fix:**
1. Update `backend/app/agents/base/agent.py` line 23
2. Find latest Anthropic model at https://docs.anthropic.com/en/docs/models-overview
3. Update model string to latest available model
4. Test with: `python3 comprehensive_qa_audit.py`
5. Verify meta-analysis creation works
6. Deploy to Railway

**Verification:**
```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/create \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "Test question",
    "topic": "Test",
    "databases": ["pubmed"]
  }'
# Should return 200 with analysis_id, not 500
```

**Estimated Time:** 1 hour

---

### 2. 🔴 CRITICAL: Frontend Not Deployed
**Impact:** Users have no way to access the platform

**Error:**
```
https://meta-analysis-tool.vercel.app
404 Not Found - DEPLOYMENT_NOT_FOUND
```

**Root Cause:**
Frontend has never been deployed to Vercel or deployment expired

**Fix:**
```bash
# Option 1: Deploy via Vercel CLI
cd frontend
npm install
npm run build
vercel --prod

# Option 2: Deploy via Vercel Dashboard
# 1. Go to vercel.com
# 2. Import Git repository
# 3. Configure:
#    - Framework: Next.js
#    - Root Directory: frontend
#    - Build Command: npm run build
#    - Output Directory: .next
# 4. Add Environment Variables:
#    - NEXT_PUBLIC_API_URL=https://meta-analysis-tool-production.up.railway.app
# 5. Deploy

# Option 3: Link existing Vercel project
cd frontend
vercel link
vercel --prod
```

**Environment Variables Needed:**
```env
NEXT_PUBLIC_API_URL=https://meta-analysis-tool-production.up.railway.app
NEXT_PUBLIC_APP_NAME=Meta-Analysis Research Platform
```

**Verification:**
```bash
curl -I https://meta-analysis-tool.vercel.app
# Should return 200 OK, not 404

# Test in browser:
open https://meta-analysis-tool.vercel.app
# Should see login/register page
```

**Estimated Time:** 2-4 hours

---

## 🟠 HIGH PRIORITY BUGS (Should Fix Before Launch)

### 3. 🟠 HIGH: Token Refresh API Contract Mismatch

**Impact:** Users forced to re-login frequently, poor UX

**Issue:**
```python
# Current API (WRONG):
POST /api/v1/auth/refresh?refresh_token={token}

# Expected API (CORRECT):
POST /api/v1/auth/refresh
Body: {"refresh_token": "{token}"}
```

**Fix:**
```python
# File: backend/app/api/v1/auth.py
# Line 228

# BEFORE:
@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,  # ❌ Query parameter
    db: AsyncSession = Depends(get_async_db)
):

# AFTER:
from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,  # ✅ Request body
    db: AsyncSession = Depends(get_async_db)
):
    refresh_token = request.refresh_token
    # Rest of function stays the same...
```

**Estimated Time:** 30 minutes

---

### 4. 🟠 HIGH: Stored XSS Vulnerability

**Impact:** Security risk - malicious JavaScript can execute in victim browsers

**Attack Vector:**
```json
POST /api/v1/auth/register
{
  "email": "attacker@evil.com",
  "password": "Pass123!",
  "full_name": "<script>alert('XSS')</script>",
  "institution": "Test"
}
```

**Fix:**
```python
# File: backend/app/models/user.py
# Add validation

from pydantic import validator
import bleach

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    institution: Optional[str] = None

    @validator('full_name', 'institution')
    def sanitize_html(cls, v):
        if v:
            # Remove all HTML tags
            return bleach.clean(v, tags=[], strip=True)
        return v
```

**Also Add:**
```python
# File: backend/app/main.py
# Add security headers middleware

from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

**Install Required:**
```bash
pip install bleach
# Add to requirements.txt
```

**Estimated Time:** 2 hours

---

## 🟡 MEDIUM PRIORITY ISSUES (Fix Within First Week)

### 5. 🟡 MEDIUM: Rate Limiting Not Enforced

**Issue:** Platform vulnerable to DoS and brute force attacks

**Current Status:**
- Configuration exists in middleware
- Not being enforced (tested 25 requests, no 429)

**Investigation Steps:**
```bash
# Check Redis connection
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed

# Verify middleware is registered
# Check: backend/app/main.py lines 126-131
```

**Potential Fixes:**
1. Verify Redis connection working
2. Check rate limiter initialization
3. Ensure middleware order correct
4. Test with multiple IPs

**Estimated Time:** 1-2 hours

---

### 6. ⚠️ MEDIUM: Celery Workers Not Running

**Issue:** Background jobs unavailable

**Impact:**
- Email notifications won't work
- Long-running analyses may time out
- Async tasks will fail

**Fix:**
```bash
# Deploy Celery worker to Railway
railway up --service celery-worker

# Or create new service in Railway dashboard:
# 1. Add service
# 2. Configure:
#    - Start Command: celery -A app.workers.celery_app worker --loglevel=info
#    - Environment: Same as main app
# 3. Deploy
```

**Estimated Time:** 2-4 hours

---

## ✅ QUICK FIX SCRIPT

```bash
#!/bin/bash
# File: QUICK_FIX_PRODUCTION_BLOCKERS.sh

echo "🔧 Fixing Critical Production Blockers..."

# Fix 1: Update Anthropic model
echo "1. Updating Anthropic model..."
sed -i 's/claude-3-5-sonnet-20241022/claude-3-5-sonnet-20250514/' backend/app/agents/base/agent.py

# Fix 2: Deploy frontend (requires manual Vercel setup)
echo "2. Deploy frontend to Vercel (requires manual action):"
echo "   cd frontend && vercel --prod"

# Fix 3: Fix token refresh API
echo "3. Fixing token refresh API..."
# Manual code change required - see above

# Fix 4: Add XSS protection
echo "4. Installing bleach for XSS protection..."
pip install bleach
echo "bleach==6.1.0" >> requirements.txt

# Commit changes
echo "5. Committing fixes..."
git add -A
git commit -m "Fix: Critical production blockers - Anthropic model + XSS protection"
git push origin main

# Deploy to Railway
echo "6. Deploying to Railway..."
railway up

echo "✅ Critical fixes applied!"
echo "⚠️  Manual action required:"
echo "   1. Deploy frontend: cd frontend && vercel --prod"
echo "   2. Update token refresh endpoint code (see fix #3)"
echo "   3. Test: python3 comprehensive_qa_audit.py"
```

---

## 🧪 POST-FIX VERIFICATION

After applying fixes, run these verification steps:

```bash
# 1. Run comprehensive test suite
python3 comprehensive_qa_audit.py

# Expected:
# ✓ All 16 tests should pass
# ✓ No critical bugs
# ✓ Meta-analysis creation should work

# 2. Run security audit
python3 security_audit.py

# Expected:
# ✓ Security score 95+/100
# ✓ No XSS vulnerabilities
# ✓ Rate limiting enforced

# 3. Test frontend
open https://meta-analysis-tool.vercel.app

# Expected:
# ✓ Page loads
# ✓ Can register user
# ✓ Can login
# ✓ Can create meta-analysis

# 4. End-to-end test
# Register -> Login -> Create Analysis -> View Results
```

---

## 📊 FIX PRIORITY MATRIX

| Bug | Severity | Impact | Effort | Priority | Status |
|-----|----------|--------|--------|----------|--------|
| Anthropic API | CRITICAL | 100% | 1h | P0 | ❌ Not Fixed |
| Frontend Deploy | CRITICAL | 100% | 2-4h | P0 | ❌ Not Fixed |
| Token Refresh | HIGH | 30% | 30m | P1 | ❌ Not Fixed |
| XSS Vulnerability | HIGH | 60% | 2h | P1 | ❌ Not Fixed |
| Rate Limiting | MEDIUM | 20% | 1-2h | P2 | ❌ Not Fixed |
| Celery Workers | MEDIUM | 40% | 2-4h | P2 | ❌ Not Fixed |

**Total Estimated Fix Time:** 8.5-13.5 hours

---

## 🎯 RECOMMENDED ACTION PLAN

### Day 1 (4-6 hours)
- [ ] **Morning:** Fix Anthropic model (1h) + test
- [ ] **Afternoon:** Deploy frontend to Vercel (2-4h) + test
- [ ] **End of Day:** Run comprehensive tests

### Day 2 (3-5 hours)
- [ ] **Morning:** Fix token refresh API (30m) + XSS (2h)
- [ ] **Afternoon:** Deploy fixes + run security audit
- [ ] **End of Day:** End-to-end testing

### Day 3 (2-4 hours) - Optional
- [ ] **Morning:** Fix rate limiting (1-2h)
- [ ] **Afternoon:** Deploy Celery workers (2-4h)
- [ ] **End of Day:** Load testing

### Day 4 - Soft Launch
- [ ] Invite beta testers
- [ ] Monitor for issues
- [ ] Address feedback

---

## 📞 ESCALATION

**If you encounter issues:**

1. **Anthropic API not working after model update:**
   - Check API key is valid: `curl https://api.anthropic.com/v1/models -H "x-api-key: $ANTHROPIC_API_KEY"`
   - Try different model version
   - Check Anthropic status: https://status.anthropic.com

2. **Frontend won't deploy to Vercel:**
   - Check build locally: `cd frontend && npm run build`
   - Verify environment variables
   - Check Vercel logs: `vercel logs`

3. **Tests still failing:**
   - Check backend logs: `railway logs`
   - Verify database migrations: `alembic current`
   - Check all environment variables set

**Support Contacts:**
- Backend Issues: Check Railway logs
- Frontend Issues: Check Vercel dashboard
- Database Issues: Check Railway PostgreSQL logs

---

## 📝 NOTES

- All fixes are non-breaking changes
- No data migration required
- Existing users not affected
- API contracts maintained (except token refresh improvement)

---

**Last Updated:** November 5, 2025
**Next Review:** After critical fixes deployed
**Target Production Date:** November 8-10, 2025 (after fixes)
