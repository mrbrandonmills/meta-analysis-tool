# BUG TRACKER - Meta-Analysis Research Platform
**Last Updated:** November 5, 2025
**Status:** 6 bugs tracked (2 critical, 2 high, 2 medium)

---

## 🔴 CRITICAL BUGS (Production Blockers)

### BUG-001: Anthropic API Model 404 Error
- **ID:** BUG-001
- **Category:** AI Integration / Core Functionality
- **Severity:** 🔴 CRITICAL
- **Priority:** P0 (Must fix before ANY deployment)
- **Status:** ❌ Open
- **Reported:** 2025-11-05 23:18:46
- **Assigned To:** Backend Team / DevOps

**Description:**
Meta-analysis creation endpoint returns 500 error because agent configuration uses deprecated Anthropic model version `claude-3-5-sonnet-20241022`.

**Impact:**
- **User Impact:** 100% - Core functionality completely broken
- **Business Impact:** Platform unusable for primary use case
- **Affected Users:** ALL users
- **Downtime:** Complete system failure for meta-analysis features

**Error Message:**
```
Anthropic API error in Coordinator: Error code: 404 -
{'type': 'error', 'error': {'type': 'not_found_error',
'message': 'model: claude-3-5-sonnet-20241022'},
'request_id': 'req_011CUrEDVp6F1K975CL375u7'}. Status code: 404
```

**Reproduction Steps:**
1. Authenticate user via `/api/v1/auth/login`
2. Call `POST /api/v1/meta-analysis/create` with valid payload
3. Observe 500 Internal Server Error
4. Check logs for Anthropic API 404 error

**Root Cause:**
```python
# File: backend/app/agents/base/agent.py
# Line: 23
class AgentConfig(BaseModel):
    model: str = "claude-3-5-sonnet-20241022"  # ❌ DEPRECATED MODEL
```

**Fix:**
```python
class AgentConfig(BaseModel):
    model: str = "claude-3-5-sonnet-20250514"  # ✅ Update to latest
    # OR use environment variable:
    # model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20250514")
```

**Files to Change:**
- `backend/app/agents/base/agent.py` (line 23)

**Testing Requirements:**
- Unit test: Agent initialization with new model
- Integration test: Full meta-analysis creation flow
- Regression test: Ensure all agents work with new model

**Estimated Effort:** 1 hour
**Target Fix Date:** November 6, 2025
**Verification:** Run `python3 comprehensive_qa_audit.py` - should pass meta-analysis tests

---

### BUG-002: Frontend Not Deployed
- **ID:** BUG-002
- **Category:** Deployment / Infrastructure
- **Severity:** 🔴 CRITICAL
- **Priority:** P0 (Must fix before ANY deployment)
- **Status:** ❌ Open
- **Reported:** 2025-11-05 23:18:46
- **Assigned To:** Frontend Team / DevOps

**Description:**
Frontend application not deployed to Vercel. URL https://meta-analysis-tool.vercel.app returns 404 with `DEPLOYMENT_NOT_FOUND` error.

**Impact:**
- **User Impact:** 100% - No user interface available
- **Business Impact:** Users cannot access platform at all
- **Affected Users:** ALL users
- **Workaround:** None - API-only access requires technical knowledge

**Error:**
```
HTTP/2 404
x-vercel-error: DEPLOYMENT_NOT_FOUND
The deployment could not be found on Vercel.
```

**Reproduction Steps:**
1. Navigate to https://meta-analysis-tool.vercel.app
2. Observe 404 error
3. Check Vercel dashboard - no deployment found

**Root Cause:**
Frontend has never been deployed to Vercel OR deployment was deleted/expired.

**Fix:**
```bash
# Option 1: CLI deployment
cd frontend
npm install
npm run build
vercel --prod

# Option 2: Git integration
# 1. Go to vercel.com
# 2. Import Git repository
# 3. Configure build settings
# 4. Add environment variables
# 5. Deploy
```

**Environment Variables Required:**
```env
NEXT_PUBLIC_API_URL=https://meta-analysis-tool-production.up.railway.app
NEXT_PUBLIC_APP_NAME=Meta-Analysis Research Platform
```

**Files to Check:**
- `frontend/next.config.js` - Build configuration
- `frontend/package.json` - Build scripts
- `vercel.json` - Vercel configuration
- `.env.production` - Production environment variables

**Testing Requirements:**
- Frontend builds successfully locally
- All pages accessible after deployment
- API integration works
- Authentication flow end-to-end
- CORS headers properly configured

**Estimated Effort:** 2-4 hours
**Target Fix Date:** November 6, 2025
**Verification:** `curl -I https://meta-analysis-tool.vercel.app` should return 200 OK

---

## 🟠 HIGH SEVERITY BUGS

### BUG-003: Token Refresh API Contract Mismatch
- **ID:** BUG-003
- **Category:** Authentication / API Design
- **Severity:** 🟠 HIGH
- **Priority:** P1 (Fix before launch)
- **Status:** ❌ Open
- **Reported:** 2025-11-05 23:18:45
- **Assigned To:** Backend Team

**Description:**
Token refresh endpoint expects `refresh_token` as query parameter but should accept it in request body per REST best practices.

**Impact:**
- **User Impact:** 30% - Users forced to re-login frequently
- **Business Impact:** Poor UX, increased support requests
- **Affected Users:** All authenticated users
- **Workaround:** Use query parameter (temporary)

**Current Behavior:**
```http
POST /api/v1/auth/refresh?refresh_token={token}
```

**Expected Behavior:**
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{"refresh_token": "{token}"}
```

**Error:**
```json
{
  "detail": [{
    "type": "missing",
    "loc": ["query", "refresh_token"],
    "msg": "Field required",
    "input": null
  }]
}
```

**Reproduction Steps:**
1. Login to get access_token and refresh_token
2. Call `POST /api/v1/auth/refresh` with JSON body `{"refresh_token": "..."}`
3. Observe 422 Unprocessable Entity
4. Error indicates expects query parameter

**Root Cause:**
```python
# File: backend/app/api/v1/auth.py
# Line: 228-232
@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,  # ❌ Query parameter (default)
    db: AsyncSession = Depends(get_async_db)
):
```

**Fix:**
```python
from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,  # ✅ Request body
    db: AsyncSession = Depends(get_async_db)
):
    refresh_token = request.refresh_token
    # Rest of function unchanged
```

**Files to Change:**
- `backend/app/api/v1/auth.py` (line 228-232)

**Testing Requirements:**
- Unit test: Token refresh with request body
- Integration test: Full auth flow with refresh
- API doc verification: Swagger shows correct contract

**Estimated Effort:** 30 minutes
**Target Fix Date:** November 7, 2025
**Verification:** Token refresh test in comprehensive_qa_audit.py should pass

---

### BUG-004: Stored XSS Vulnerability in User Profile
- **ID:** BUG-004
- **Category:** Security / Input Validation
- **Severity:** 🟠 HIGH
- **Priority:** P1 (Fix before launch)
- **Status:** ❌ Open
- **Reported:** 2025-11-05 23:20:04
- **Assigned To:** Backend Team / Security Team

**Description:**
User registration accepts and stores XSS payloads without sanitization. Malicious JavaScript in `full_name` field gets stored in database and could execute in victim browsers.

**Impact:**
- **User Impact:** HIGH - Security vulnerability
- **Business Impact:** Reputation damage, legal liability
- **Affected Users:** All users who view profiles
- **Severity:** Can lead to account takeover, data theft

**Attack Vector:**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "attacker@evil.com",
  "password": "Pass123!",
  "full_name": "<script>alert('XSS')</script>",
  "institution": "Test"
}
```

**Result:**
Payload stored in database without sanitization:
```json
{
  "id": "...",
  "full_name": "<script>alert('XSS')</script>",
  "email": "attacker@evil.com"
}
```

**Reproduction Steps:**
1. Register user with XSS payload in `full_name`
2. Registration succeeds (201 Created)
3. Payload stored in database
4. When profile displayed, JavaScript executes

**Root Cause:**
No input validation or sanitization on user-provided fields.

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

**Also Add Security Headers:**
```python
# File: backend/app/main.py
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
```

**Dependencies:**
```bash
pip install bleach
# Add to requirements.txt: bleach==6.1.0
```

**Files to Change:**
- `backend/app/models/user.py` - Add validation
- `backend/app/main.py` - Add security headers
- `requirements.txt` - Add bleach dependency

**Testing Requirements:**
- Unit test: XSS payload rejected or sanitized
- Security test: Run XSS attack suite
- Regression test: Valid names still work

**Estimated Effort:** 2 hours
**Target Fix Date:** November 7, 2025
**Verification:** Run `python3 security_audit.py` - should pass XSS tests

---

## 🟡 MEDIUM SEVERITY ISSUES

### BUG-005: Rate Limiting Not Enforced
- **ID:** BUG-005
- **Category:** Security / Performance
- **Severity:** 🟡 MEDIUM
- **Priority:** P2 (Fix within first week)
- **Status:** ❌ Open
- **Reported:** 2025-11-05 23:20:04
- **Assigned To:** Backend Team / DevOps

**Description:**
Rate limiting middleware exists but not properly enforcing limits. Tested 25 rapid requests without receiving 429 Too Many Requests.

**Impact:**
- **User Impact:** LOW - Doesn't affect normal users
- **Business Impact:** Platform vulnerable to DoS attacks
- **Affected Users:** None directly
- **Risk:** Brute force attacks, API abuse

**Expected Behavior:**
- Unauthenticated: 20 requests per minute
- Authenticated: 100 requests per minute
- Response: 429 Too Many Requests when limit exceeded

**Actual Behavior:**
No rate limiting enforced - 25+ requests succeed without throttling

**Reproduction Steps:**
1. Make 25 rapid requests to `/api/v1/health`
2. All requests return 200 OK
3. No 429 responses received
4. No rate limit headers in response

**Root Cause (Investigation Needed):**
- Redis connection may be failing
- Middleware not properly initialized
- Rate limiter configuration incorrect
- Middleware order wrong

**Investigation Steps:**
```bash
# Check Redis connectivity
curl https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed

# Check middleware registration
# File: backend/app/main.py lines 126-131

# Check rate limiter initialization
# File: backend/app/core/middleware.py
```

**Potential Fixes:**
1. Verify Redis connection working
2. Check rate_limiter.init() succeeds
3. Ensure middleware registered in correct order
4. Add logging to rate limiter

**Files to Check:**
- `backend/app/core/middleware.py` - Rate limiter implementation
- `backend/app/main.py` - Middleware registration
- Railway environment - Redis URL configured

**Testing Requirements:**
- Unit test: Rate limiter logic
- Integration test: Exceed limit and verify 429
- Load test: Multiple IPs

**Estimated Effort:** 1-2 hours
**Target Fix Date:** November 8, 2025
**Verification:** Rate limiting test in security_audit.py should pass

---

### BUG-006: Celery Workers Not Running
- **ID:** BUG-006
- **Category:** Infrastructure / Background Jobs
- **Severity:** ⚠️ MEDIUM
- **Priority:** P2 (Fix within first week)
- **Status:** ❌ Open
- **Reported:** 2025-11-05 23:18:43
- **Assigned To:** DevOps / Backend Team

**Description:**
Health check reports Celery status as "degraded" with "No workers available". Background job processing unavailable.

**Impact:**
- **User Impact:** 40% - Long-running tasks may time out
- **Business Impact:** Async features don't work
- **Affected Features:**
  - Email notifications
  - Large meta-analyses (>100 studies)
  - Report generation
  - Background data processing

**Health Check Response:**
```json
{
  "checks": {
    "celery": {
      "status": "degraded",
      "message": "No workers available"
    }
  }
}
```

**Reproduction Steps:**
1. Call `/api/v1/health/detailed`
2. Check `checks.celery.status`
3. Observe "degraded" status
4. No workers listed

**Root Cause:**
Celery workers never deployed to Railway infrastructure.

**Fix:**
```bash
# Option 1: Add Railway service
railway service create celery-worker
railway service configure celery-worker \
  --start-command "celery -A app.workers.celery_app worker --loglevel=info"

# Option 2: Railway dashboard
# 1. Add new service
# 2. Use same repository
# 3. Configure start command
# 4. Add same environment variables as main app
# 5. Deploy
```

**Required Configuration:**
```toml
# railway-celery-worker.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "celery -A app.workers.celery_app worker --loglevel=info"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Environment Variables:**
- Same as main backend service
- Plus: `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`

**Files to Check:**
- `backend/app/workers/celery_app.py` - Celery configuration
- `railway.toml` - Worker configuration
- Railway dashboard - Service creation

**Testing Requirements:**
- Worker starts successfully
- Can process test task
- Health check shows workers active
- Test async job execution

**Estimated Effort:** 2-4 hours
**Target Fix Date:** November 9, 2025
**Verification:** `/api/v1/health/detailed` should show Celery "healthy"

---

## BUG STATISTICS

**Total Bugs:** 6
- 🔴 CRITICAL: 2 (33%)
- 🟠 HIGH: 2 (33%)
- 🟡 MEDIUM: 2 (33%)
- 🟢 LOW: 0 (0%)

**By Status:**
- ❌ Open: 6 (100%)
- 🔄 In Progress: 0 (0%)
- ✅ Fixed: 0 (0%)
- 🚀 Deployed: 0 (0%)

**By Category:**
- Security: 2 (33%)
- Infrastructure: 2 (33%)
- Authentication: 1 (17%)
- AI Integration: 1 (17%)

**Priority Distribution:**
- P0 (Critical): 2 bugs
- P1 (High): 2 bugs
- P2 (Medium): 2 bugs

**Estimated Total Fix Time:** 8.5-13.5 hours

---

## FIX ROADMAP

### Week 1 (Nov 6-7)
**Day 1:**
- [ ] BUG-001: Fix Anthropic model (1h)
- [ ] BUG-002: Deploy frontend (2-4h)
- [ ] Run comprehensive tests

**Day 2:**
- [ ] BUG-003: Fix token refresh (30m)
- [ ] BUG-004: Fix XSS vulnerability (2h)
- [ ] Run security audit

### Week 2 (Nov 8-10)
**Day 3:**
- [ ] BUG-005: Fix rate limiting (1-2h)
- [ ] BUG-006: Deploy Celery workers (2-4h)
- [ ] Load testing

**Day 4:**
- [ ] Beta testing
- [ ] Monitor for new issues
- [ ] Address feedback

---

## MONITORING & ALERTING

**Critical Alerts:**
- [ ] Set up Sentry for error tracking
- [ ] Configure Anthropic API health monitoring
- [ ] Monitor Vercel deployment status
- [ ] Track authentication error rates

**Performance Metrics:**
- [ ] Response time monitoring
- [ ] Database query performance
- [ ] Redis hit rate
- [ ] Celery queue depth

---

## ESCALATION POLICY

**Critical Bugs (P0):**
- Notify: CTO, Tech Lead, DevOps immediately
- Response Time: < 1 hour
- Fix Target: < 24 hours
- Communication: Hourly updates

**High Severity (P1):**
- Notify: Tech Lead, Team Lead
- Response Time: < 4 hours
- Fix Target: < 48 hours
- Communication: Daily updates

**Medium Severity (P2):**
- Notify: Team Lead
- Response Time: < 1 day
- Fix Target: < 1 week
- Communication: As needed

---

**Last Updated:** November 5, 2025, 11:25 PM
**Next Review:** After critical fixes deployed
**Maintained By:** QA Engineer Agent
