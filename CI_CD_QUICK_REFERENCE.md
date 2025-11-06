# CI/CD Quick Reference Guide

## 🚀 Quick Start

### First-Time Setup (5 minutes)

```bash
# 1. Update README.md badge URLs
# Replace YOUR_USERNAME with your GitHub username in README.md

# 2. Configure GitHub Secrets
# Go to: Settings → Secrets and variables → Actions
# Add:
#   - ANTHROPIC_API_KEY (required)
#   - CODECOV_TOKEN (required)

# 3. Enable Codecov
# Go to https://codecov.io, sign in, enable repository

# 4. Push to trigger workflows
git add .github/ scripts/ .codecov.yml README.md
git commit -m "Add CI/CD infrastructure"
git push origin main

# 5. Check GitHub Actions tab
# https://github.com/YOUR_USERNAME/meta-analysis-tool/actions
```

---

## 📋 Common Commands

### Local Testing

```bash
# Quick pre-commit check (1-3 min)
./scripts/pre-commit-tests.sh

# Full test suite (10-15 min)
./scripts/run-all-tests.sh

# Backend tests only
./scripts/run-all-tests.sh --backend-only

# Frontend tests only
./scripts/run-all-tests.sh --frontend-only

# With validation tests
./scripts/run-all-tests.sh --with-validation

# Check coverage
./scripts/check-coverage.sh

# Open coverage reports in browser
./scripts/check-coverage.sh --open
```

### Fixing Common Issues

```bash
# Fix Python formatting
cd backend
black app tests
isort app tests

# Fix JavaScript linting
cd frontend
npm run lint --fix

# Reset environment
rm -rf backend/venv frontend/node_modules
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-test.txt
cd ../frontend && npm install
```

---

## 🔄 Workflows Overview

| Workflow | Trigger | Runtime | Purpose |
|----------|---------|---------|---------|
| Backend Tests | Push, PR | ~5-10 min | Unit, integration, coverage |
| Frontend Tests | Push, PR | ~5-8 min | Lint, type-check, build |
| Security | Push, PR, Weekly | ~10-15 min | Vulnerabilities, secrets |
| Production Readiness | Manual, Weekly | ~20-30 min | E2E production tests |

---

## ✅ Quality Gates

### Backend (80% coverage required)
- ✅ Unit tests pass
- ✅ Integration tests pass
- ✅ Coverage >= 80%
- ✅ Black formatting
- ✅ flake8 linting
- ✅ No security issues

### Frontend (60% coverage target)
- ✅ ESLint passes
- ✅ TypeScript compiles
- ✅ Build succeeds
- ✅ No high vulnerabilities

---

## 🔧 Troubleshooting

### "Tests failing locally"
```bash
# Check environments
python --version  # Should be 3.11
node --version    # Should be 18

# Reinstall dependencies
cd backend && pip install -r requirements.txt -r requirements-test.txt
cd ../frontend && npm ci
```

### "Coverage not uploading"
```bash
# Check token in GitHub Secrets
# Verify files exist:
ls -la backend/coverage.xml
ls -la frontend/coverage/lcov.info
```

### "Workflow permissions error"
```
Settings → Actions → General
→ Enable "Read and write permissions"
→ Enable "Allow GitHub Actions to create and approve pull requests"
```

---

## 📊 Coverage Reports

### Locations
- **Backend**: `backend/htmlcov/index.html`
- **Frontend**: `frontend/coverage/lcov-report/index.html`
- **Codecov**: https://codecov.io/gh/YOUR_USERNAME/meta-analysis-tool

### Thresholds
- Backend: 80% (enforced)
- Frontend: 60% (target)
- Critical paths: 90%+ (recommended)

---

## 🛡️ Security Scans

### What's Scanned
- Python dependencies (Safety)
- Node dependencies (npm audit)
- Secrets in code (TruffleHog)
- Code patterns (CodeQL)
- Containers (Trivy)
- Security anti-patterns (Bandit)

### Where to Check
- GitHub Security tab
- Workflow artifacts
- CodeQL alerts

---

## 🔐 Required Secrets

### Essential
- `ANTHROPIC_API_KEY`: Claude API for tests
- `CODECOV_TOKEN`: Coverage upload

### Optional
- `RAILWAY_TOKEN`: Railway deployments
- `VERCEL_TOKEN`: Vercel deployments
- `SLACK_WEBHOOK`: Notifications

---

## 🌿 Branch Protection

### Recommended Settings
```
Branch: main
→ ✅ Require pull request reviews (1)
→ ✅ Require status checks:
   - Backend Tests
   - Frontend Tests
   - Security Scanning
→ ✅ Require branches up to date
```

---

## 📝 Development Workflow

```bash
# 1. Create branch
git checkout -b feature/my-feature

# 2. Make changes
# ... code changes ...

# 3. Pre-commit check
./scripts/pre-commit-tests.sh

# 4. Commit
git commit -m "Add my feature"

# 5. Full test (optional but recommended)
./scripts/run-all-tests.sh

# 6. Push
git push origin feature/my-feature

# 7. Create PR
# GitHub will automatically run all workflows

# 8. Review CI results
# Wait for all checks to pass

# 9. Merge when approved and green
```

---

## 🎯 Key Files

### Workflows
- `.github/workflows/backend-tests.yml`
- `.github/workflows/frontend-tests.yml`
- `.github/workflows/security.yml`
- `.github/workflows/production-readiness.yml`

### Configuration
- `.codecov.yml` - Coverage config

### Scripts
- `scripts/run-all-tests.sh` - Full test suite
- `scripts/check-coverage.sh` - Coverage check
- `scripts/pre-commit-tests.sh` - Quick validation

### Documentation
- `README.md` - Main readme with badges
- `CI_CD_SETUP.md` - Detailed setup guide
- `CI_CD_IMPLEMENTATION_REPORT.md` - Implementation details
- `CI_CD_QUICK_REFERENCE.md` - This file

---

## 💡 Tips

### Speed up local tests
```bash
# Run only changed tests
pytest tests/unit/test_specific.py

# Skip slow tests
pytest -m "not slow"

# Run in parallel
pytest -n auto
```

### Before pushing
```bash
# Always run pre-commit
./scripts/pre-commit-tests.sh

# Check what will be tested
git diff --name-only origin/main
```

### Debugging CI failures
```bash
# Download artifacts from failed run
# Check logs in GitHub Actions
# Run same test locally:
./scripts/run-all-tests.sh --verbose
```

---

## 📞 Getting Help

### Issues
- Check workflow logs in Actions tab
- Review this guide
- Check detailed docs: `CI_CD_SETUP.md`
- Create GitHub issue with `devops` label

### Resources
- [GitHub Actions Docs](https://docs.github.com/actions)
- [Codecov Docs](https://docs.codecov.com)
- [pytest Docs](https://docs.pytest.org)

---

## 🎓 For Professor Review

### Demo Flow
1. Show GitHub Actions tab (all green)
2. Open recent PR with test results
3. Show Codecov coverage diff
4. Run `./scripts/run-all-tests.sh` locally
5. Show security scanning results
6. Explain branch protection

### Key Points
- ✅ Enterprise-grade automation
- ✅ 80% coverage enforcement
- ✅ Multi-layer security
- ✅ Fast feedback (<10 min)
- ✅ Zero manual testing
- ✅ Production monitoring

---

**Last Updated**: November 5, 2025
**Version**: 1.0

**Need more details?** See `CI_CD_SETUP.md` for comprehensive documentation.
