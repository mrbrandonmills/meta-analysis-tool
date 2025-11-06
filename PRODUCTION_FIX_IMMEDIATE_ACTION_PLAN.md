# IMMEDIATE ACTION PLAN - Production Fix
## Meta-Analysis Platform - Critical Auth Failure

**Status:** 🔴 CRITICAL - Platform Non-Functional
**Issue:** Database migrations not applied, authentication broken (HTTP 500)
**Impact:** 0% of user-facing features work
**Fix Time:** 30 minutes
**Total Time to Ready:** 4 hours

---

## ⏰ TIMELINE

```
NOW:        Execute Phase 1 (Database Fix)
+30 min:    Authentication working
+1.5 hours: Core features verified
+2.5 hours: All bugs fixed
+3 hours:   Security audit complete
+3.5 hours: Demo rehearsed
+4 hours:   READY FOR PROFESSOR EVALUATION ✅
```

---

## PHASE 1: FIX DATABASE (30 MINUTES) 🔴 CRITICAL

### Owner: DevOps Engineer

### Step 1: Connect to Railway (2 minutes)
```bash
# If not already linked
railway link

# Verify connection
railway status
```

### Step 2: Run Database Migrations (5 minutes)
```bash
# Run migrations on production database
railway run alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001_multi_tool_schema, Initial schema
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Remove duplicate name column
INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, Align schema with models
```

**If Errors Occur:**
- Check database URL: `railway variables | grep DATABASE_URL`
- Check connection: `railway connect postgres`
- View logs: `railway logs --tail 100`

### Step 3: Verify Migrations Applied (3 minutes)
```bash
# Check current migration version
railway run alembic current

# Should show: 003_align_schema_with_models (head)
```

```bash
# Verify tables exist
railway connect postgres
```

Then in psql:
```sql
-- List all tables
\dt

-- Should see:
-- users
-- api_keys
-- workflows
-- workflow_steps
-- studies
-- agents
-- agent_decisions
-- audit_logs

-- Verify users table structure
\d users

-- Should show columns: id, email, hashed_password, full_name, etc.

-- Exit psql
\q
```

### Step 4: Update Railway Startup Command (5 minutes)

**In Railway Dashboard:**
1. Go to backend service
2. Settings → Deploy
3. Update START_COMMAND:
```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
4. Save and redeploy (automatic)

### Step 5: Test Authentication (10 minutes)

**Test 1: User Registration**
```bash
curl -X POST "https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "qa-test-'$(date +%s)'@example.com",
    "password": "TestPass123!",
    "full_name": "QA Test User"
  }'
```

**Expected:** HTTP 201 with user data
```json
{
  "id": "uuid-here",
  "email": "qa-test-xxx@example.com",
  "full_name": "QA Test User",
  "role": "researcher",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-11-05T19:30:00Z"
}
```

**Current (BROKEN):** HTTP 500 with InvalidRequestError

**Test 2: User Login**
```bash
# Save email for reuse
EMAIL="qa-test-1762399557@example.com"

curl -X POST "https://meta-analysis-tool-production.up.railway.app/api/v1/auth/login" \
  -d "username=$EMAIL&password=TestPass123!"
```

**Expected:** HTTP 200 with tokens
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Test 3: Token Authentication**
```bash
# Extract token from login response
TOKEN="<access_token_from_above>"

curl -X GET "https://meta-analysis-tool-production.up.railway.app/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** HTTP 200 with user data

### Step 6: Verify Health Check (2 minutes)
```bash
curl -s "https://meta-analysis-tool-production.up.railway.app/api/v1/health/detailed" | python3 -m json.tool
```

**Expected:**
```json
{
  "status": "healthy",
  "checks": {
    "database": {"status": "healthy", "message": "Database connection successful"},
    "redis": {"status": "healthy", "message": "Redis connection successful"},
    "celery": {"status": "healthy" or "degraded", "message": "..."}
  }
}
```

### Step 7: Notify Team (3 minutes)
```bash
# Update team on Slack/email
"✅ Database migrations applied successfully
✅ Users table created
✅ Authentication endpoints now responding HTTP 201/200
✅ Ready for Phase 2 testing"
```

---

## PHASE 2: VERIFY FEATURES (1 HOUR)

### Owner: QA Engineer

### Step 1: Re-run Automated Test Suites (10 minutes)
```bash
cd /Users/brandon/meta-analysis-tool

# Production readiness test
python3 production_readiness_test.py

# Comprehensive test suite
python3 comprehensive_test_suite.py --env production
```

**Expected Results:**
- Authentication tests: ✅ PASS (was FAIL)
- Meta-analysis tests: Can now execute (was SKIP)
- Overall status: GO or GO_WITH_CAUTIONS (was NO-GO)

### Step 2: Test Meta-Analysis Creation (15 minutes)

**Manual Test:**
```bash
# 1. Register new user
EMAIL="demo-$(date +%s)@example.com"
curl -X POST "https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'$EMAIL'",
    "password": "DemoPass123!",
    "full_name": "Demo User"
  }'

# 2. Login
TOKEN=$(curl -s -X POST "https://meta-analysis-tool-production.up.railway.app/api/v1/auth/login" \
  -d "username=$EMAIL&password=DemoPass123!" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3. Create meta-analysis
curl -X POST "https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "What is the effect of exercise on depression?",
    "inclusion_criteria": ["RCTs", "Adult participants", "Depression diagnosis"],
    "exclusion_criteria": ["Animal studies", "Non-English"],
    "databases": ["pubmed"],
    "peer_review_only": true
  }'
```

**Expected:** HTTP 201 with workflow ID

### Step 3: Test Literature Search (10 minutes)
```bash
curl -X POST "https://meta-analysis-tool-production.up.railway.app/api/v1/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "exercise and depression",
    "search_terms": ["exercise", "depression", "randomized controlled trial"],
    "databases": ["pubmed"],
    "max_results": 20
  }'
```

**Expected:** HTTP 200 with studies array

### Step 4: Test End-to-End Workflow (15 minutes)
- Create project
- Execute search
- Review results
- Attempt meta-analysis execution
- Check workflow status
- Verify audit trail

### Step 5: Document Issues Found (10 minutes)
- Log any errors encountered
- Screenshot failures
- Note performance issues
- Record unexpected behaviors

---

## PHASE 3: FIX BUGS (1 HOUR)

### Owner: Development Team

### Priority 1: Critical Bugs
- Fix any workflow execution failures
- Resolve agent communication issues
- Fix data validation errors

### Priority 2: High Priority Bugs
- UI/UX issues
- Performance degradation
- Error message clarity

### Priority 3: Medium Priority
- Minor UI glitches
- Non-critical validation
- Cosmetic issues

**Re-test After Each Fix**

---

## PHASE 4: SECURITY AUDIT (30 MINUTES)

### Owner: Senior Engineer / Security Specialist

### Test 1: SQL Injection Prevention
```bash
# Test malicious inputs
curl -X POST "https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"' OR '1'='1@test.com","password":"test123"}'
```
**Expected:** HTTP 400/422 (rejected)

### Test 2: XSS Prevention
```bash
curl -X POST "https://meta-analysis-tool-production.up.railway.app/api/v1/meta-analysis/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"research_question":"<script>alert('"'"'XSS'"'"')</script>","databases":["pubmed"]}'
```
**Expected:** Input sanitized or rejected

### Test 3: JWT Token Security
```bash
# Test expired token
# Test invalid token
# Test token refresh
# Verify token expiration (30 min access, 7 day refresh)
```

### Test 4: Rate Limiting (if implemented)
```bash
# Send 100+ requests rapidly
# Verify rate limit kicks in
```

### Test 5: Authorization Checks
```bash
# Try to access other user's projects
# Verify 403 Forbidden returned
```

---

## PHASE 5: DEMO PREP (30 MINUTES)

### Owner: PM + QA Engineer

### Prepare Demo Data
1. Create demo user account
2. Create sample meta-analysis project
3. Pre-populate with search results
4. Generate sample report
5. Prepare Q&A examples

### Demo Script
```
1. Show login (30 sec)
2. Dashboard overview (1 min)
3. Create new meta-analysis (2 min)
4. Execute literature search (2 min)
5. Review search results (2 min)
6. Show agent pipeline (1 min)
7. Demonstrate Q&A with agents (2 min)
8. Show audit trail (1 min)
9. Generate and download report (2 min)
10. Q&A with professor (5 min)

Total: ~15 minutes
```

### Rehearse
- Practice full demo flow
- Time each section
- Prepare for common questions
- Have backup plan if something fails

---

## PHASE 6: FINAL GO/NO-GO (15 MINUTES)

### Owner: PM + QA Engineer + CTO

### Checklist
- [ ] ✅ Authentication working (registration, login, token)
- [ ] ✅ Meta-analysis creation working
- [ ] ✅ Literature search functional
- [ ] ✅ Workflow execution completes
- [ ] ✅ Reports generated successfully
- [ ] ✅ Security tests passing
- [ ] ✅ Performance acceptable (<2s response times)
- [ ] ✅ Demo rehearsed and polished
- [ ] ✅ Backup plan prepared
- [ ] ✅ Team confident

### Decision
- **GO:** Proceed with professor evaluation
- **NO-GO:** Identify blockers, fix, and reassess

---

## ROLLBACK PLAN (If Things Go Wrong)

### If Migrations Fail
```bash
# Rollback migrations
railway run alembic downgrade -1

# Fix migration script
# Re-run migrations
```

### If Auth Still Broken After Migrations
```bash
# Check logs
railway logs --tail 100 | grep -i error

# Verify environment variables
railway variables | grep -E "(DATABASE_URL|SECRET_KEY)"

# Connect to database directly
railway connect postgres
# Manually verify schema
```

### If Demo Fails
**Backup Demo Strategy:**
- Show architecture documentation
- Walk through code and design
- Discuss methodology and testing
- Present roadmap and vision
- Acknowledge current limitation
- Offer follow-up demo after fix

---

## SUCCESS CRITERIA

### Technical Success
- ✅ All auth tests passing
- ✅ Meta-analysis workflow functional
- ✅ Security audit passing
- ✅ Performance targets met

### Demo Success
- ✅ Professor can register and login
- ✅ Professor can create meta-analysis
- ✅ Professor can see agent pipeline work
- ✅ Professor can download report
- ✅ Professor is impressed with quality

### Academic Success
- ✅ Research validity demonstrated
- ✅ Statistical rigor proven
- ✅ Explainability shown
- ✅ PRISMA compliance verified
- ✅ Professor endorses platform

---

## CONTACTS

**QA Engineer:** Production Readiness Specialist
**DevOps Engineer:** Railway deployment expert
**Backend Lead:** Database and migrations
**PM:** Coordination and decision-making
**CTO:** Final approval

---

## QUICK REFERENCE COMMANDS

**Check Migration Status:**
```bash
railway run alembic current
```

**Apply Migrations:**
```bash
railway run alembic upgrade head
```

**View Logs:**
```bash
railway logs --tail 100
```

**Connect to Database:**
```bash
railway connect postgres
```

**Test Auth:**
```bash
curl -X POST "https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!","full_name":"Test"}'
```

**Run Test Suites:**
```bash
python3 production_readiness_test.py
python3 comprehensive_test_suite.py --env production
```

---

## WHAT TO COMMUNICATE TO PROFESSOR

### If Ready (GO Status)
"The platform is fully functional and ready for evaluation. I can demonstrate:
- Complete meta-analysis workflow
- Agent collaboration and decision-making
- Statistical analysis and reporting
- Audit trail and explainability
- PRISMA-compliant methodology"

### If Not Ready (NO-GO Status)
"We've identified a critical deployment issue that prevented demonstration-ready status. The underlying technology is sound, but we need [X hours] to resolve the deployment configuration. We can:
1. Reschedule for [specific time]
2. Present architecture and design today, live demo tomorrow
3. Walk through code and methodology without live execution"

**ALWAYS be transparent about status. Academic credibility depends on honesty.**

---

**END OF ACTION PLAN**
**Execute phases in order. Do not skip steps.**
**Report status after each phase completion.**

🔴 **CURRENT STATUS: PHASE 1 NOT STARTED**
⏰ **TIME TO READY: 4 HOURS**
🎯 **TARGET: PROFESSOR EVALUATION READY**

**LET'S GO! 🚀**
