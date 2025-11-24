# Next Steps - Tier Application System

## 🎉 Backend Implementation Complete!

All backend components for the 3-tier qualification system are now implemented and ready for deployment.

---

## Quick Start Guide

### Step 1: Run Database Migration

```bash
cd /Volumes/Super\ Mastery/meta-analysis-tool/backend

# Run the migration to create new tables
alembic upgrade head
```

This will create:
- `tier_applications` table
- `qualification_verifications` table
- Add `tier`, `first_name`, `last_name` fields to `users` table
- Create all necessary enums and indexes

### Step 2: Configure Email Settings

Add to `backend/.env`:

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM_EMAIL=noreply@metaanalysistool.com
SMTP_FROM_NAME=Meta-Analysis Tool
SMTP_USE_TLS=true
```

**For Gmail:**
1. Enable 2-factor authentication
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use the app password (not your regular password)

### Step 3: Test API Endpoints

Start the backend server:

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Test endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Test tier application endpoint (requires auth)
curl http://localhost:8000/api/v1/tier-applications/my-applications \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## What's Implemented ✅

### Backend Services
- ✅ `credential_verification.py` - ORCID, Google Scholar, CrossRef, background checks
- ✅ `email_service.py` - 10+ email templates for notifications

### API Endpoints
- ✅ 9 public tier application endpoints
- ✅ 10 admin review and management endpoints

### Database
- ✅ `TierApplication` model - stores all application data
- ✅ `QualificationVerification` model - stores verification results
- ✅ User model updates - tier, first_name, last_name fields
- ✅ Migration script ready to run

### Schemas
- ✅ 15+ Pydantic schemas with validators
- ✅ Enums for tiers, statuses, reasons
- ✅ Nested schemas for complex data

### Email Templates
- ✅ Application submitted
- ✅ Verification results (passed/failed)
- ✅ Approval/denial notifications
- ✅ Appeal notifications
- ✅ Reference check requests
- ✅ More info requested

---

## What's Remaining ⏳

### 1. Frontend Implementation

**Priority: HIGH**

Need to build:
- [ ] Tier 2 application form
- [ ] Tier 3 application form
- [ ] Application status dashboard
- [ ] Admin review dashboard
- [ ] File upload components
- [ ] Appeal submission form

**Suggested Tech Stack:**
- React/Next.js (frontend already uses this)
- Form library: React Hook Form + Zod validation
- UI components: Tailwind CSS + shadcn/ui
- File uploads: react-dropzone

**Key Pages to Create:**
- `/apply/tier-2` - Tier 2 application form
- `/apply/tier-3` - Tier 3 application form
- `/dashboard/applications` - User's applications
- `/admin/applications` - Admin review dashboard
- `/applications/[id]/appeal` - Appeal form

### 2. Background Check Integration

**Priority: MEDIUM**

Current status: Placeholder implementations

Need to integrate:
- [ ] **ORI (Office of Research Integrity)**
  - Check if API available
  - If not, manual check process

- [ ] **Retraction Watch Database**
  - Check API availability
  - Alternative: Web scraping (use with caution)

- [ ] **PubPeer**
  - Check API or RSS feed
  - Alternative: Manual review

**Alternatives if APIs unavailable:**
- Manual admin review step
- Link to external databases for admin to check
- Periodic batch checks

### 3. Testing

**Priority: HIGH**

Recommended testing approach:

#### Unit Tests
```python
# Test credential verification
tests/services/test_credential_verification.py
  - test_orcid_validation()
  - test_google_scholar_scraping()
  - test_doi_verification()

# Test email service
tests/services/test_email_service.py
  - test_application_submitted_email()
  - test_approval_email()
  - test_denial_email()
```

#### Integration Tests
```python
# Test application workflow
tests/api/test_tier_applications.py
  - test_tier_2_application_submission()
  - test_auto_verification_flow()
  - test_admin_review_flow()
  - test_appeal_flow()

# Test admin endpoints
tests/api/test_admin_tier_applications.py
  - test_pending_applications()
  - test_approve_application()
  - test_deny_application()
  - test_contact_references()
```

#### End-to-End Tests
```python
# Full workflow tests
tests/e2e/test_tier_application_workflow.py
  - test_complete_tier_2_approval()
  - test_complete_tier_3_approval()
  - test_denial_and_appeal()
```

### 4. Production Deployment

**Priority: MEDIUM**

Before deploying:

- [ ] Run database migration on production
- [ ] Configure production SMTP (SendGrid recommended)
- [ ] Set up file storage (AWS S3 or similar)
- [ ] Configure CORS for frontend
- [ ] Set up monitoring and logging
- [ ] Create admin user accounts
- [ ] Test email delivery in production

**Recommended Email Service for Production:**
- SendGrid (free tier: 100 emails/day)
- AWS SES (very cheap, reliable)
- Mailgun (good for transactional emails)

### 5. Documentation

**Priority: LOW**

- [ ] API documentation (Swagger/OpenAPI)
- [ ] User guide for applications
- [ ] Admin manual for reviewing applications
- [ ] Email template customization guide

---

## Testing Checklist

### Manual Testing Flow

#### Test Tier 2 Application:

1. **Register new user**
   ```bash
   POST /api/v1/auth/register
   ```

2. **Submit Tier 2 application**
   ```bash
   POST /api/v1/tier-applications/tier-2/apply
   ```
   - Use real ORCID ID (format: 0000-0001-2345-6789)
   - Use real Google Scholar URL
   - Provide 3 DOIs

3. **Check auto-verification**
   - Monitor background task
   - Check email notifications
   - Verify status updates

4. **Admin review**
   ```bash
   GET /api/v1/admin/tier-applications/pending
   POST /api/v1/admin/tier-applications/{id}/review
   ```

5. **Test approval flow**
   - Approve application
   - Check tier access granted
   - Verify approval email sent

6. **Test denial flow**
   - Deny application
   - Submit appeal
   - Test appeal review

#### Test Tier 3 Application:

1. **Create approved Tier 2 user**
   - Manually set tier_2_reviewer in database
   - Set approved date 90+ days ago

2. **Submit Tier 3 application**
   ```bash
   POST /api/v1/tier-applications/tier-3/apply
   ```
   - Provide editorial experience
   - Upload recommendation letters
   - Add 3 professional references

3. **Test reference checks**
   ```bash
   POST /api/v1/admin/tier-applications/{id}/contact-references
   ```
   - Verify reference emails sent
   - Check reference response handling

4. **Test probationary approval**
   - Admin approves with PROBATIONARY_APPROVE
   - Verify 90-day probation period set
   - Check probation email sent

---

## Database Migration Rollback

If you need to rollback the migration:

```bash
cd backend
alembic downgrade -1
```

This will:
- Drop `tier_applications` table
- Drop `qualification_verifications` table
- Remove tier fields from `users` table
- Drop all enums

---

## API Endpoints Quick Reference

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tier-applications/tier-2/apply` | Submit Tier 2 application |
| POST | `/tier-applications/tier-3/apply` | Submit Tier 3 application |
| GET | `/tier-applications/my-applications` | Get user's applications |
| GET | `/tier-applications/{id}` | Get application details |
| GET | `/tier-applications/status/{id}` | Check application status |
| POST | `/tier-applications/{id}/appeal` | Submit appeal |
| POST | `/tier-applications/{id}/upload-cv` | Upload CV |
| POST | `/tier-applications/{id}/upload-degree` | Upload degree certificate |
| POST | `/tier-applications/{id}/upload-recommendation-letter` | Upload recommendation letter |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/tier-applications/pending` | Get pending applications |
| GET | `/admin/tier-applications/statistics` | Get dashboard statistics |
| GET | `/admin/tier-applications/{id}/details` | Get application details |
| GET | `/admin/tier-applications/{id}/verification-report` | Get verification report |
| POST | `/admin/tier-applications/{id}/review` | Review application |
| POST | `/admin/tier-applications/{id}/assign-to-advisory-board` | Escalate to board |
| POST | `/admin/tier-applications/{id}/contact-references` | Contact references |
| POST | `/admin/tier-applications/{id}/re-verify` | Re-run verification |
| GET | `/admin/tier-applications/appeals/pending` | Get pending appeals |
| POST | `/admin/tier-applications/{id}/appeal-decision` | Review appeal |

---

## File Structure Reference

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── tier_applications.py          ← User endpoints
│   │   └── admin/
│   │       └── tier_applications.py       ← Admin endpoints
│   ├── models/
│   │   ├── tier_application.py            ← Database models
│   │   └── user.py                        ← Updated User model
│   ├── schemas/
│   │   └── tier_applications.py           ← Pydantic schemas
│   ├── services/
│   │   ├── credential_verification.py     ← Verification service
│   │   └── email_service.py               ← Email service
│   └── core/
│       └── config.py                      ← Updated config
├── alembic/versions/
│   └── 010_add_tier_application_system.py ← Migration
└── tests/                                  ← To be created
    ├── services/
    ├── api/
    └── e2e/
```

---

## Resources

### Documentation
- [TIER_APPLICATION_IMPLEMENTATION_SUMMARY.md](./TIER_APPLICATION_IMPLEMENTATION_SUMMARY.md) - Complete implementation details
- [3_TIER_QUALIFICATION_SYSTEM_DESIGN.md](./3_TIER_QUALIFICATION_SYSTEM_DESIGN.md) - Original design document

### External APIs
- [ORCID API Documentation](https://info.orcid.org/documentation/api-tutorials/)
- [CrossRef API Documentation](https://www.crossref.org/documentation/retrieve-metadata/)
- [Scholarly Python Library](https://github.com/scholarly-python-package/scholarly)

### Email Services
- [SendGrid Documentation](https://docs.sendgrid.com/)
- [AWS SES Documentation](https://docs.aws.amazon.com/ses/)
- [Mailgun Documentation](https://documentation.mailgun.com/)

---

## Common Issues & Solutions

### Issue: Alembic migration fails
**Solution:** Check that database connection is working, ensure no duplicate enum types exist

### Issue: ORCID verification returns 404
**Solution:** Ensure ORCID ID format is correct (0000-0001-2345-6789), check profile is public

### Issue: Google Scholar scraping fails
**Solution:** Use scholarly library with proxy rotation, implement rate limiting

### Issue: Emails not sending
**Solution:** Check SMTP credentials, verify Gmail app password, check firewall rules

### Issue: File uploads failing
**Solution:** Ensure upload directory exists and has write permissions, check file size limits

---

## Support

For questions or issues:
1. Check implementation summary document
2. Review code comments in service files
3. Test endpoints with example requests
4. Check logs for detailed error messages

---

**Last Updated:** 2025-11-22
**Status:** Backend Complete ✅
**Next Priority:** Frontend Implementation
