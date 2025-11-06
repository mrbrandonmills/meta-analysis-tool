# CI/CD Implementation Verification Checklist

Use this checklist to verify the CI/CD infrastructure is properly installed and configured.

**Date**: November 5, 2025
**Version**: 1.0

---

## Pre-Installation Verification

### Files Exist

Run these commands to verify all files are present:

```bash
# Workflow files
ls -la .github/workflows/backend-tests.yml
ls -la .github/workflows/frontend-tests.yml
ls -la .github/workflows/production-readiness.yml
ls -la .github/workflows/security.yml

# Configuration
ls -la .codecov.yml

# Scripts
ls -la scripts/run-all-tests.sh
ls -la scripts/check-coverage.sh
ls -la scripts/pre-commit-tests.sh

# Documentation
ls -la CI_CD_SETUP.md
ls -la CI_CD_IMPLEMENTATION_REPORT.md
ls -la CI_CD_QUICK_REFERENCE.md
ls -la CI_CD_EXECUTIVE_SUMMARY.md
```

**Expected Result**: All files exist with no errors

### Scripts Are Executable

```bash
# Verify executable permissions
test -x scripts/run-all-tests.sh && echo "✓ run-all-tests.sh is executable"
test -x scripts/check-coverage.sh && echo "✓ check-coverage.sh is executable"
test -x scripts/pre-commit-tests.sh && echo "✓ pre-commit-tests.sh is executable"
```

**Expected Result**: All three scripts report as executable

---

## Local Testing Verification

### Test Script 1: Pre-commit Tests

```bash
./scripts/pre-commit-tests.sh
```

**What to Look For**:
- ✅ Script runs without errors
- ✅ Backend checks execute (if backend changed)
- ✅ Frontend checks execute (if frontend changed)
- ✅ Exit code 0 if all pass

**Troubleshooting**:
- If Python errors: Check virtual environment
- If Node errors: Run `cd frontend && npm install`
- If permission denied: Run `chmod +x scripts/*.sh`

### Test Script 2: Coverage Check

```bash
./scripts/check-coverage.sh
```

**What to Look For**:
- ✅ Backend tests run with coverage
- ✅ Coverage percentage displayed
- ✅ HTML report generated at backend/htmlcov/index.html
- ✅ Coverage threshold check runs

**Troubleshooting**:
- If pytest not found: `cd backend && pip install -r requirements-test.txt`
- If database error: Check DATABASE_URL environment variable
- If no virtual env: Create with `python -m venv venv`

### Test Script 3: Full Test Suite

```bash
./scripts/run-all-tests.sh --backend-only
```

**What to Look For**:
- ✅ Backend tests execute
- ✅ Unit tests pass
- ✅ Integration tests pass
- ✅ Colored output appears
- ✅ Final summary shows success

**Troubleshooting**:
- If tests fail: Review test output for specific errors
- If services missing: Start PostgreSQL and Redis
- If timeout: Increase test timeout in pytest.ini

---

## GitHub Configuration Verification

### Repository Settings

Navigate to: `https://github.com/YOUR_USERNAME/meta-analysis-tool/settings`

#### Secrets Check

Go to: **Settings** → **Secrets and variables** → **Actions**

**Required Secrets**:
- [ ] `ANTHROPIC_API_KEY` exists
- [ ] `CODECOV_TOKEN` exists

**Optional Secrets** (for deployment):
- [ ] `RAILWAY_TOKEN` exists (if using Railway)
- [ ] `VERCEL_TOKEN` exists (if using Vercel)
- [ ] `VERCEL_ORG_ID` exists (if using Vercel)
- [ ] `VERCEL_PROJECT_ID` exists (if using Vercel)

#### Actions Permissions

Go to: **Settings** → **Actions** → **General**

**Required Settings**:
- [ ] "Allow all actions and reusable workflows" is selected
- [ ] "Read and write permissions" is selected
- [ ] "Allow GitHub Actions to create and approve pull requests" is checked

### Branch Protection

Go to: **Settings** → **Branches**

**Main Branch Protection**:
- [ ] Branch protection rule exists for `main`
- [ ] "Require pull request reviews before merging" is enabled
- [ ] "Require status checks to pass before merging" is enabled
- [ ] Required status checks include:
  - [ ] `Backend Tests`
  - [ ] `Frontend Tests`
  - [ ] `Security Scanning` (optional but recommended)
- [ ] "Require branches to be up to date before merging" is enabled

---

## Codecov Integration Verification

### Codecov Setup

1. Go to: https://codecov.io
2. Sign in with GitHub
3. Navigate to your repository

**Checklist**:
- [ ] Repository is visible in Codecov
- [ ] Token is copied to GitHub secrets
- [ ] Badge token is available (for README)
- [ ] Email notifications configured (optional)

### Codecov Configuration

Verify `.codecov.yml` is properly formatted:

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.codecov.yml'))" && echo "✓ .codecov.yml is valid YAML"
```

**Expected Result**: "✓ .codecov.yml is valid YAML"

---

## First Workflow Run Verification

### Trigger Workflows

```bash
# Commit and push to trigger workflows
git add .github/ scripts/ .codecov.yml README.md CI_CD_*
git commit -m "Add CI/CD infrastructure"
git push origin main
```

### Check Workflow Execution

Navigate to: `https://github.com/YOUR_USERNAME/meta-analysis-tool/actions`

**What to Look For**:
- [ ] Workflows appear in Actions tab
- [ ] At least one workflow run is visible
- [ ] Workflow status is visible (running/success/failure)

### Individual Workflow Checks

#### Backend Tests Workflow
- [ ] Workflow triggered on push
- [ ] `backend-tests` job started
- [ ] `backend-code-quality` job started
- [ ] PostgreSQL service healthy
- [ ] Redis service healthy
- [ ] Tests execute successfully
- [ ] Coverage uploaded to Codecov
- [ ] Artifacts uploaded (test results, coverage)

#### Frontend Tests Workflow
- [ ] Workflow triggered on push
- [ ] `frontend-tests` job started
- [ ] `frontend-code-quality` job started
- [ ] Dependencies installed
- [ ] Linting passes
- [ ] TypeScript check passes
- [ ] Build succeeds

#### Security Workflow
- [ ] Workflow triggered on push
- [ ] All security scan jobs start
- [ ] No critical vulnerabilities found
- [ ] No secrets detected
- [ ] CodeQL analysis completes
- [ ] Results uploaded to GitHub Security

#### Production Readiness Workflow
- [ ] Can be triggered manually
- [ ] Environment selection works
- [ ] Comprehensive tests run
- [ ] Reports generated
- [ ] Artifacts uploaded

---

## Pull Request Test

### Create Test PR

```bash
# Create test branch
git checkout -b test/ci-cd-verification

# Make trivial change
echo "# CI/CD Verification Test" >> CI_CD_TEST_FILE.md
git add CI_CD_TEST_FILE.md
git commit -m "Test CI/CD workflows"
git push origin test/ci-cd-verification
```

### Create Pull Request

Navigate to: `https://github.com/YOUR_USERNAME/meta-analysis-tool/pulls`

Click "New pull request" and create PR from `test/ci-cd-verification` to `main`

### Verify PR Checks

**On Pull Request Page**:
- [ ] Status checks section appears
- [ ] Required checks are listed:
  - [ ] Backend Tests
  - [ ] Frontend Tests
  - [ ] Security Scanning (if configured)
- [ ] All checks start automatically
- [ ] Check status updates in real-time
- [ ] Codecov bot posts comment with coverage diff
- [ ] All checks pass (green checkmarks)

### Verify Merge Protection

- [ ] "Merge pull request" button is disabled until checks pass
- [ ] Required reviews are requested (if configured)
- [ ] Status shows "All checks have passed" or similar

---

## Coverage Reporting Verification

### Check Codecov Comment

On the test pull request:
- [ ] Codecov bot posts a comment
- [ ] Comment shows coverage comparison
- [ ] Base and head coverage percentages visible
- [ ] Coverage diff shown for changed files
- [ ] Links to full reports work

### Check Codecov Dashboard

Navigate to: `https://codecov.io/gh/YOUR_USERNAME/meta-analysis-tool`

**Dashboard Checklist**:
- [ ] Repository appears in Codecov
- [ ] Coverage percentage is displayed
- [ ] Graph shows coverage trends
- [ ] Commits are listed with coverage
- [ ] Pull requests show coverage diffs
- [ ] Flags (backend/frontend) are visible
- [ ] Components are tracked

---

## Badge Verification

### Update Badge URLs

In `README.md`, replace `YOUR_USERNAME` with actual GitHub username:

```bash
# Use sed or manually edit
sed -i '' 's/YOUR_USERNAME/your-actual-username/g' README.md
git add README.md
git commit -m "Update badge URLs"
git push origin main
```

### Verify Badges Display

Visit: `https://github.com/YOUR_USERNAME/meta-analysis-tool`

**Badges Should Show**:
- [ ] Backend Tests badge (passing/green)
- [ ] Frontend Tests badge (passing/green)
- [ ] Security Scanning badge (passing/green)
- [ ] Codecov badge (with percentage)
- [ ] Production Deployment badge

**Troubleshooting**:
- If badge shows "unknown": Workflow hasn't run yet
- If badge shows "failing": Check workflow logs
- If badge doesn't appear: Check URL format

---

## Security Tab Verification

Navigate to: `https://github.com/YOUR_USERNAME/meta-analysis-tool/security`

### Security Overview
- [ ] Security tab is accessible
- [ ] No critical vulnerabilities shown
- [ ] Dependabot alerts section visible
- [ ] Code scanning section visible

### CodeQL Analysis
- [ ] CodeQL results appear in Security tab
- [ ] Analysis date is recent
- [ ] No high-severity issues
- [ ] View analysis results works

### Dependabot
- [ ] Dependabot is enabled
- [ ] Dependency alerts are visible (if any)
- [ ] Security updates can be configured

---

## Documentation Verification

### README.md
- [ ] Badges are visible at top
- [ ] CI/CD section exists
- [ ] Testing instructions are clear
- [ ] Links to documentation work

### CI/CD Documentation Files
- [ ] `CI_CD_SETUP.md` is comprehensive
- [ ] `CI_CD_QUICK_REFERENCE.md` is accessible
- [ ] `CI_CD_IMPLEMENTATION_REPORT.md` is detailed
- [ ] `CI_CD_EXECUTIVE_SUMMARY.md` is clear

---

## Performance Verification

### Workflow Execution Times

Check recent workflow runs:

**Backend Tests**:
- [ ] Completes in < 15 minutes
- [ ] Average time is 5-10 minutes

**Frontend Tests**:
- [ ] Completes in < 12 minutes
- [ ] Average time is 5-8 minutes

**Security Scanning**:
- [ ] Completes in < 20 minutes
- [ ] Average time is 10-15 minutes

**If Slower Than Expected**:
- Check for network issues
- Review resource allocation
- Consider caching improvements

---

## Final Verification

### Complete System Test

```bash
# 1. Make a change
echo "Test change" >> test_file.md

# 2. Run pre-commit
./scripts/pre-commit-tests.sh

# 3. Run full tests
./scripts/run-all-tests.sh

# 4. Check coverage
./scripts/check-coverage.sh

# 5. Commit and push
git add test_file.md
git commit -m "Final CI/CD verification test"
git push origin main

# 6. Watch workflows run
# Open: https://github.com/YOUR_USERNAME/meta-analysis-tool/actions

# 7. Verify all pass
# All workflows should complete successfully
```

### Success Criteria

All of the following must be true:

- [x] All local scripts run without errors
- [x] All GitHub workflows are configured
- [x] All workflows run and pass
- [x] Coverage uploads to Codecov
- [x] Pull requests show status checks
- [x] Badges display correctly
- [x] Security scans complete
- [x] Documentation is accessible
- [x] Execution times are acceptable

---

## Troubleshooting Common Issues

### Issue: Workflows not triggering

**Solution**:
```bash
# Check workflow YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/backend-tests.yml'))"

# Verify on correct branch
git branch --show-current

# Force trigger
git commit --allow-empty -m "Trigger workflows"
git push origin main
```

### Issue: Tests failing in CI but passing locally

**Solution**:
```bash
# Check environment differences
# CI uses: Python 3.11, Node 18, PostgreSQL 15, Redis 7

# Match CI environment locally
docker-compose up -d postgres redis
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_db
export REDIS_URL=redis://localhost:6379/0
./scripts/run-all-tests.sh
```

### Issue: Coverage not uploading

**Solution**:
```bash
# Verify Codecov token
# Go to: Settings → Secrets → Actions → CODECOV_TOKEN

# Check coverage file exists
ls -la backend/coverage.xml

# Manual upload test
cd backend
pip install codecov
codecov -t YOUR_TOKEN -f coverage.xml
```

### Issue: Security scans failing

**Solution**:
```bash
# Update dependencies
cd backend && pip install --upgrade safety bandit
cd frontend && npm audit fix

# Run locally
cd backend && safety check
cd backend && bandit -r app
cd frontend && npm audit
```

---

## Sign-Off

Once all items are checked:

**Verified by**: ___________________
**Date**: ___________________
**Status**: [ ] PASS [ ] FAIL
**Notes**: ___________________

---

## Next Steps After Verification

If all checks pass:

1. **Clean up test files**:
   ```bash
   git rm CI_CD_TEST_FILE.md test_file.md
   git commit -m "Remove test files"
   git push origin main
   ```

2. **Close test PR**: Merge or close the test/ci-cd-verification PR

3. **Update team**: Share CI_CD_QUICK_REFERENCE.md with team

4. **Schedule review**: Set calendar reminder to review in 1 month

5. **Monitor**: Check Actions tab daily for first week

---

**Checklist Version**: 1.0
**Last Updated**: November 5, 2025
**Maintained By**: Infrastructure Team
