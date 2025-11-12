# Comprehensive QA Test Plan - Meta-Analysis Payment Platform

**Test Date**: November 11, 2025
**QA Engineer**: Ultra-Intelligent QA Agent
**Platform Version**: Payment Ecosystem v1.0
**Test Environment**: Production (Railway + Vercel)

---

## EXECUTIVE SUMMARY

### Testing Scope
- **Backend API**: 40+ endpoints across 8 modules
- **Frontend**: 5 dashboards + onboarding flow
- **Payment System**: Subscription creation, payout distribution
- **AI Systems**: Reviewer matching, profile enrichment, research direction
- **Security**: Authentication, authorization, input validation
- **Integration**: End-to-end workflows

### Test Methodology
1. **Functional Testing**: Verify all features work as designed
2. **Integration Testing**: Test complete user workflows
3. **Security Testing**: Identify vulnerabilities
4. **Performance Testing**: Measure API response times
5. **Usability Testing**: Evaluate user experience

### Success Criteria
- All critical endpoints return 2xx responses
- No SQL injection or XSS vulnerabilities
- Payment workflows complete successfully
- Frontend components render correctly
- API response times < 2 seconds

---

## TEST ENVIRONMENT

### Backend (Railway)
- **URL**: https://meta-analysis-tool-production.up.railway.app
- **API Docs**: https://meta-analysis-tool-production.up.railway.app/docs
- **Database**: PostgreSQL on Railway
- **Stack**: FastAPI, SQLAlchemy, Stripe API

### Frontend (Vercel)
- **URL**: https://meta-analysis-tool.vercel.app
- **Stack**: Next.js, React, TailwindCSS
- **Key Routes**:
  - /admin - Admin dashboard
  - /editor - Editor dashboard
  - /earnings - Researcher earnings
  - /onboarding/researcher - Onboarding flow

### External Services
- **Stripe**: Test mode enabled
- **Google Scholar**: Scraping service
- **ORCID API**: Profile enrichment
- **Anthropic Claude**: AI analysis

---

## CRITICAL ENDPOINTS TO TEST

### 1. Subscription Management (Priority 1)
- `POST /api/v1/subscriptions/create` - Create subscription
- `GET /api/v1/subscriptions/me` - Get user subscription
- `POST /api/v1/subscriptions/{id}/cancel` - Cancel subscription
- `PUT /api/v1/subscriptions/{id}/payment-method` - Update payment method

### 2. Payout Management (Priority 1)
- `POST /api/v1/payouts/calculate-monthly` - Calculate payouts (CRON)
- `GET /api/v1/payouts/earnings` - Get user earnings
- `GET /api/v1/payouts/pool/{month}` - Get pool details
- `GET /api/v1/payouts/distributions/{month}` - Get distributions

### 3. Review Approval (Priority 1)
- `POST /api/v1/review-approval/{review_id}/approve` - Approve review
- `POST /api/v1/review-approval/{review_id}/reject` - Reject review
- `GET /api/v1/review-approval/pending` - Get pending reviews
- `GET /api/v1/review-approval/statistics` - Get approval stats

### 4. Research Direction (Tool 2) (Priority 2)
- `POST /api/v1/research-direction/generate` - Generate direction
- `GET /api/v1/research-direction/list` - List directions
- `GET /api/v1/research-direction/{id}` - Get direction details
- `POST /api/v1/research-direction/{id}/save` - Save direction

### 5. Researcher Enrichment (Priority 2)
- `POST /api/v1/researcher-enrichment/enrich` - Enrich profile
- `GET /api/v1/researcher-enrichment/{id}/status` - Check enrichment status
- `POST /api/v1/researcher-enrichment/orcid` - Fetch ORCID data
- `POST /api/v1/researcher-enrichment/scholar` - Fetch Scholar data

### 6. Authentication (Priority 1)
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### 7. Admin Dashboard (Priority 2)
- `GET /api/v1/admin/dashboard` - Admin overview
- `GET /api/v1/admin/researchers` - List researchers
- `GET /api/v1/admin/payouts/history` - Payout history
- `POST /api/v1/admin/pool/close` - Close payout pool

### 8. Existing Meta-Analysis (Priority 2)
- `POST /api/v1/meta-analysis/search` - Literature search
- `GET /api/v1/meta-analysis/{id}/results` - Get results
- `POST /api/v1/meta-analysis/{id}/screen` - Screen studies
- `POST /api/v1/meta-analysis/{id}/extract` - Extract data

---

## TEST CASES

### TC-001: Backend Health Check
**Priority**: Critical
**Type**: Smoke Test

**Steps**:
1. GET /api/v1/health
2. Verify response contains "status": "ok"
3. Check database connection status
4. Verify all services are operational

**Expected Result**: 200 OK with healthy status

---

### TC-002: User Registration
**Priority**: Critical
**Type**: Functional

**Steps**:
1. POST /api/v1/auth/register with valid data
2. Verify user created in database
3. Check JWT token returned
4. Verify email sent (if configured)

**Expected Result**: 201 Created with access_token

---

### TC-003: Create Subscription
**Priority**: Critical
**Type**: Integration

**Steps**:
1. Authenticate as test user
2. POST /api/v1/subscriptions/create with Stripe test card
3. Verify subscription created in database
4. Check $20 added to payout pool
5. Verify user.is_paying_member = true

**Expected Result**: 201 Created with subscription details

---

### TC-004: Submit and Approve Review
**Priority**: Critical
**Type**: Integration

**Steps**:
1. Create test manuscript
2. Assign reviewer via matching algorithm
3. Reviewer submits review
4. Editor approves review
5. Verify review_completions record created
6. Check review linked to current payout pool

**Expected Result**: Review approved and eligible for payout

---

### TC-005: Calculate Monthly Payouts
**Priority**: Critical
**Type**: Integration

**Steps**:
1. Set up test data: 10 subscriptions, 10 approved reviews
2. POST /api/v1/payouts/calculate-monthly (dry_run: true)
3. Verify payout_per_review calculation correct
4. Check distributions calculated for each reviewer
5. Verify no Stripe transfers in dry run mode

**Expected Result**: Payout calculation accurate

---

### TC-006: Generate Research Direction
**Priority**: High
**Type**: AI System

**Steps**:
1. POST /api/v1/research-direction/generate with papers
2. Verify AI generates 5 research directions
3. Check directions have novelty scores
4. Verify feasibility assessments
5. Validate JSON structure

**Expected Result**: 5 research directions generated

---

### TC-007: SQL Injection Prevention
**Priority**: Critical
**Type**: Security

**Steps**:
1. Send malicious payloads to all endpoints:
   - `'; DROP TABLE users; --`
   - `' OR '1'='1`
   - `UNION SELECT * FROM subscriptions`
2. Verify no SQL errors
3. Check database integrity intact

**Expected Result**: All malicious inputs rejected

---

### TC-008: XSS Prevention
**Priority**: High
**Type**: Security

**Steps**:
1. Submit XSS payloads in form fields:
   - `<script>alert('XSS')</script>`
   - `<img src=x onerror=alert('XSS')>`
2. Verify payloads sanitized
3. Check frontend renders safely

**Expected Result**: No script execution

---

### TC-009: Authorization Testing
**Priority**: Critical
**Type**: Security

**Steps**:
1. Try accessing admin endpoints as regular user
2. Try accessing other users' earnings data
3. Try approving reviews as non-editor
4. Verify 403 Forbidden responses

**Expected Result**: Unauthorized access blocked

---

### TC-010: End-to-End Workflow
**Priority**: Critical
**Type**: Integration

**Steps**:
1. User registers account
2. User completes onboarding
3. User subscribes ($100/month)
4. User submits paper for review
5. Reviewers matched and assigned
6. Reviewers submit reviews
7. Editor approves reviews
8. Monthly payout calculated
9. Reviewers receive payouts

**Expected Result**: Complete workflow succeeds

---

## BUG SEVERITY LEVELS

### Critical (P0)
- System crash or data loss
- Security vulnerabilities
- Payment processing failures
- Cannot complete core workflows

### High (P1)
- Major feature not working
- Incorrect payout calculations
- API errors (500s)
- Data integrity issues

### Medium (P2)
- Minor feature issues
- UI/UX problems
- Performance degradation
- Non-critical API errors

### Low (P3)
- Cosmetic issues
- Documentation errors
- Nice-to-have features missing

---

## TEST EXECUTION LOG

Test execution results will be recorded in:
`/Users/brandon/meta-analysis-tool/ai-management/bug-records/QA_TEST_RESULTS_[timestamp].md`

Each test case will include:
- Test ID
- Status (Pass/Fail/Blocked)
- Execution time
- Screenshots (if applicable)
- Bug IDs (if failed)

---

## BUG REPORTING TEMPLATE

### Bug ID: BUG-[NUMBER]
**Severity**: [Critical/High/Medium/Low]
**Status**: [Open/In Progress/Fixed/Closed]
**Found In**: [Endpoint/Component]
**Assigned To**: [Developer]

**Description**:
Clear description of the issue

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**:
What should happen

**Actual Behavior**:
What actually happens

**Environment**:
- Browser/OS
- Backend version
- Database state

**Screenshots/Logs**:
Relevant evidence

**Suggested Fix**:
Technical recommendation

---

## AUTOMATION OPPORTUNITIES

### High Priority
1. Create pytest test suite for all API endpoints
2. Add Selenium tests for critical frontend flows
3. Set up CI/CD test automation in GitHub Actions
4. Create performance benchmarking script

### Medium Priority
1. Add load testing with Locust
2. Create visual regression tests
3. Set up security scanning (OWASP ZAP)
4. Add API contract testing

---

## TEST COMPLETION CRITERIA

- [ ] All critical endpoints tested
- [ ] All P0/P1 bugs fixed
- [ ] Security vulnerabilities addressed
- [ ] Frontend components verified
- [ ] End-to-end workflows validated
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Test report delivered to PM

---

**Next Step**: Begin test execution starting with TC-001 (Backend Health Check)
