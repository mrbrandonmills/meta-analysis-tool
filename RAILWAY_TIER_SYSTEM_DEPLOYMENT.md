# Railway Deployment Guide - Tier Application System

**Date:** 2025-11-22
**Production URL:** https://meta-analysis-tool-production.up.railway.app

---

## Overview

This guide shows how to deploy the tier application system to Railway production environment. The system requires PostgreSQL (already configured on Railway) and will run the migration to create new tables.

---

## Prerequisites

✅ Railway CLI installed (`railway 4.11.0` confirmed)
✅ Backend code committed to GitHub
✅ PostgreSQL database running on Railway
✅ Production URLs:
  - Backend: https://meta-analysis-tool-production.up.railway.app
  - Frontend: https://meta-analysis-tool.vercel.app

---

## Step 1: Link to Railway Project

```bash
cd "/Volumes/Super Mastery/meta-analysis-tool/backend"

# Link to the Railway project
railway link
```

**Expected prompts:**
- Select your team/account
- Select project: `meta-analysis-tool-production`
- Select environment: `production`

**Verify link:**
```bash
railway status
```

Should show:
```
Project: meta-analysis-tool-production
Environment: production
Service: backend
```

---

## Step 2: Push Latest Code to GitHub

The tier application system files need to be pushed to GitHub so Railway can deploy them.

```bash
cd "/Volumes/Super Mastery/meta-analysis-tool"

# Check what files are new/modified
git status

# Add all tier application files
git add backend/app/models/tier_application.py
git add backend/app/schemas/tier_applications.py
git add backend/app/services/credential_verification.py
git add backend/app/services/email_service.py
git add backend/app/api/v1/tier_applications.py
git add backend/app/api/v1/admin/tier_applications.py
git add backend/app/core/config.py
git add backend/app/models/user.py
git add backend/app/models/__init__.py
git add backend/alembic/versions/010_add_tier_application_system.py
git add backend/alembic/versions/004_add_pdf_full_text_models.py

# Add documentation
git add TIER_APPLICATION_IMPLEMENTATION_SUMMARY.md
git add NEXT_STEPS_TIER_SYSTEM.md
git add RAILWAY_TIER_SYSTEM_DEPLOYMENT.md

# Commit
git commit -m "Add 3-tier qualification system with applications, verification, and admin review

- Implement automatic credential verification (ORCID, Google Scholar, CrossRef)
- Add comprehensive email notification system (10+ templates)
- Create tier 2 and tier 3 application API endpoints
- Build admin review and approval workflow endpoints
- Add TierApplication and QualificationVerification database models
- Update User model with tier, first_name, last_name fields
- Create migration 010 for tier application system
- Add Pydantic schemas with validators
- Configure SMTP email settings
- Fix migration 004 down_revision reference

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push origin main
```

Railway will automatically detect the push and start deploying.

---

## Step 3: Wait for Railway Deployment

```bash
# Watch deployment logs
railway logs -f
```

Wait for:
- ✅ Build complete
- ✅ Deploy successful
- ✅ Service healthy

This typically takes 2-4 minutes.

---

## Step 4: Run Database Migration on Railway

Once deployment is complete, run the migration:

```bash
cd "/Volumes/Super Mastery/meta-analysis-tool/backend"

# Run migration on Railway's PostgreSQL database
railway run alembic upgrade heads
```

**What this does:**
- Connects to Railway's PostgreSQL database
- Runs migration `010_add_tier_application_system.py`
- Creates `tier_applications` table
- Creates `qualification_verifications` table
- Adds `tier`, `first_name`, `last_name` to `users` table
- Creates all necessary enums and indexes

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 009_add_admin_action_table -> 010_add_tier_application_system, Add tier application system with 3-tier qualification structure
```

---

## Step 5: Configure Environment Variables on Railway

Add SMTP email configuration to Railway:

```bash
# Option 1: Using Railway dashboard
# Go to: https://railway.com/project/b0e4e10d-b739-4b8e-88e9-ba3e9d99968c
# Navigate to: backend service → Variables
# Add the following variables

# Option 2: Using Railway CLI
railway variables set SMTP_HOST=smtp.gmail.com
railway variables set SMTP_PORT=587
railway variables set SMTP_FROM_EMAIL=noreply@metaanalysistool.com
railway variables set SMTP_FROM_NAME="Meta-Analysis Tool"
railway variables set SMTP_USE_TLS=true

# Set username and password (use app-specific password for Gmail)
railway variables set SMTP_USERNAME=your-email@gmail.com
railway variables set SMTP_PASSWORD=your-app-password
```

**For Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Create a new app password for "Meta-Analysis Tool"
3. Copy the 16-character password
4. Use it as `SMTP_PASSWORD`

**After adding variables:**
Railway will automatically redeploy the service.

---

## Step 6: Verify Deployment

### 6.1 Check Health Endpoint

```bash
curl https://meta-analysis-tool-production.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-22T..."
}
```

### 6.2 Check API Documentation

Visit: https://meta-analysis-tool-production.up.railway.app/docs

You should see new endpoints:
- `/api/v1/tier-applications/tier-2/apply`
- `/api/v1/tier-applications/tier-3/apply`
- `/api/v1/tier-applications/my-applications`
- `/api/v1/admin/tier-applications/pending`
- And 15+ more tier application endpoints

### 6.3 Test Database Tables Created

```bash
# Connect to Railway database
railway connect postgres

# Check if tier_applications table exists
\dt tier_applications

# Check if qualification_verifications table exists
\dt qualification_verifications

# Check users table structure (should have tier, first_name, last_name)
\d users

# Exit
\q
```

---

## Step 7: Create Admin User for Testing

Create an admin user to test the admin review endpoints:

```bash
# Option 1: Using Railway shell
railway run python3

# Then in Python:
from app.models.user import User
from app.core.security import get_password_hash
from app.db.base import SessionLocal
import uuid

db = SessionLocal()

# Create admin user
admin = User(
    id=uuid.uuid4(),
    email="admin@metaanalysistool.com",
    hashed_password=get_password_hash("Admin123!"),
    first_name="Admin",
    last_name="User",
    is_superuser=True,
    is_verified=True,
    is_active=True,
    tier="tier_1_researcher"
)

db.add(admin)
db.commit()
print(f"Admin user created: {admin.email}")
```

---

## Step 8: Test API Endpoints

### 8.1 Register and Login

```bash
# Register new user
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User"
  }'

# Login
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "Test123!"
  }'

# Save the access_token from response
TOKEN="<your_access_token_here>"
```

### 8.2 Submit Tier 2 Application

```bash
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/tier-applications/tier-2/apply \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "degree_type": "PhD",
    "degree_institution": "Stanford University",
    "degree_field": "Computer Science",
    "degree_year": 2018,
    "orcid_id": "0000-0001-2345-6789",
    "google_scholar_url": "https://scholar.google.com/citations?user=EXAMPLE",
    "publication_dois": ["10.1000/example1", "10.1000/example2", "10.1000/example3"],
    "total_reviews_completed": 5,
    "journals_reviewed_for": [
      {"journal_name": "Nature", "years": "2020-2023", "review_count": 3},
      {"journal_name": "Science", "years": "2021-2023", "review_count": 2}
    ],
    "max_concurrent_reviews": 3,
    "preferred_review_timeframe_days": 14,
    "review_languages": ["English"],
    "expertise_domains": ["Machine Learning", "Computer Vision"],
    "expertise_keywords": ["deep learning", "neural networks", "image recognition", "computer vision", "AI", "machine learning", "CNN", "transformer", "attention", "classification"],
    "research_methodologies": ["Experimental", "Quantitative", "Computational"],
    "conflicts_of_interest_disclosed": true,
    "research_misconduct_question": false,
    "cope_guidelines_accepted": true
  }'
```

Expected response:
```json
{
  "application_id": "uuid-here",
  "user_id": "uuid-here",
  "tier_applied_for": "tier_2_reviewer",
  "status": "submitted",
  "submitted_at": "2025-11-22T...",
  "estimated_review_time_days": 5
}
```

### 8.3 Check Application Status

```bash
curl -X GET https://meta-analysis-tool-production.up.railway.app/api/v1/tier-applications/my-applications \
  -H "Authorization: Bearer $TOKEN"
```

### 8.4 Admin Review (as admin user)

```bash
# Login as admin
ADMIN_TOKEN="<admin_access_token_here>"

# Get pending applications
curl -X GET https://meta-analysis-tool-production.up.railway.app/api/v1/admin/tier-applications/pending \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Approve application
curl -X POST https://meta-analysis-tool-production.up.railway.app/api/v1/admin/tier-applications/{application_id}/review \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "APPROVE",
    "admin_notes": "Strong credentials, approved"
  }'
```

---

## Troubleshooting

### Issue: Migration fails with "relation already exists"

**Solution:** The table was created in a previous attempt. Check current migration version:

```bash
railway run alembic current
```

If already at `010_add_tier_application_system`, you're good!

### Issue: SMTP emails not sending

**Solution:** Check Railway logs for email errors:

```bash
railway logs -f | grep -i "email\|smtp"
```

Verify SMTP credentials are correct in Railway variables.

### Issue: Background verification not running

**Solution:** Check if Celery/Redis are configured:

```bash
railway variables | grep -i redis
```

For MVP, background tasks may run synchronously (blocking). This is fine for testing.

### Issue: "No module named 'scholarly'"

**Solution:** Ensure `requirements.txt` includes `scholarly==1.7.11`. Redeploy:

```bash
git push origin main
```

---

## Monitoring

### Check Application Logs

```bash
# Real-time logs
railway logs -f

# Filter for tier applications
railway logs -f | grep -i "tier\|application\|verification"

# Check for errors
railway logs -f | grep -i "error\|traceback"
```

### Check Database

```bash
# Connect to database
railway connect postgres

# Count applications
SELECT COUNT(*) FROM tier_applications;

# Check recent applications
SELECT id, tier_applied_for, status, submitted_at
FROM tier_applications
ORDER BY submitted_at DESC
LIMIT 10;

# Check verification records
SELECT COUNT(*) FROM qualification_verifications;
```

---

## Rollback (if needed)

If something goes wrong, rollback the migration:

```bash
# Rollback one migration
railway run alembic downgrade -1

# This will:
# - Drop tier_applications table
# - Drop qualification_verifications table
# - Remove tier fields from users table
# - Drop all enums
```

---

## Next Steps After Deployment

1. **Test All Endpoints** - Use Postman or the Swagger UI at `/docs`
2. **Configure Email Templates** - Customize email content in `email_service.py`
3. **Set Up Monitoring** - Add error tracking (Sentry, LogRocket)
4. **Build Frontend Forms** - Create React components for applications
5. **Integrate Background Checks** - Add ORI, Retraction Watch, PubPeer APIs
6. **Write Tests** - Add integration and E2E tests
7. **Update Documentation** - Add API examples to Swagger docs

---

## Environment Variables Summary

Required on Railway:

```bash
# Already configured (existing)
DATABASE_URL=<postgresql://...>  # Auto-configured by Railway
ANTHROPIC_API_KEY=sk-ant-...
SECRET_KEY=...
STRIPE_SECRET_KEY=sk_live_...

# New for tier system
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@metaanalysistool.com
SMTP_FROM_NAME=Meta-Analysis Tool
SMTP_USE_TLS=true
```

---

## Success Checklist

- [ ] Code pushed to GitHub
- [ ] Railway deployment successful
- [ ] Migration `010` completed
- [ ] Tables created (tier_applications, qualification_verifications)
- [ ] SMTP variables configured
- [ ] Health endpoint returns 200
- [ ] API docs show tier endpoints
- [ ] Test application submitted successfully
- [ ] Email confirmation sent (or logged)
- [ ] Admin can review application

---

## Support

For issues:
1. Check Railway logs: `railway logs -f`
2. Review migration output
3. Test endpoints with Swagger UI
4. Check SMTP configuration
5. Verify database tables exist

**Railway Dashboard:** https://railway.com/project/b0e4e10d-b739-4b8e-88e9-ba3e9d99968c

---

**Last Updated:** 2025-11-22
**Migration Version:** 010_add_tier_application_system
**Status:** Ready for Deployment ✅
