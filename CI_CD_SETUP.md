# CI/CD Infrastructure Setup Guide

## Overview

This document describes the complete CI/CD infrastructure for the Meta-Analysis Tool project. The implementation demonstrates enterprise-level DevOps practices with automated testing, security scanning, and deployment pipelines.

## Architecture

### Workflow Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions CI/CD                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Backend    │  │  Frontend    │  │  Security    │     │
│  │    Tests     │  │   Tests      │  │  Scanning    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                  │              │
│         └─────────────────┴──────────────────┘              │
│                           │                                 │
│                  ┌────────▼─────────┐                       │
│                  │   Codecov        │                       │
│                  │   Coverage       │                       │
│                  └────────┬─────────┘                       │
│                           │                                 │
│                  ┌────────▼─────────┐                       │
│                  │  Production      │                       │
│                  │  Readiness       │                       │
│                  └──────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## Workflows

### 1. Backend Tests (`backend-tests.yml`)

**Purpose**: Validate backend code quality, run tests, and enforce coverage standards.

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Only when backend files change

**Jobs**:

#### backend-tests
- **Runtime**: ~5-10 minutes
- **Services**: PostgreSQL 15, Redis 7
- **Steps**:
  1. Checkout code
  2. Setup Python 3.11 with pip caching
  3. Install dependencies (requirements.txt + requirements-test.txt)
  4. Run unit tests with coverage (pytest + coverage)
  5. Run integration tests
  6. Run validation tests (allow failures)
  7. Generate coverage reports (XML, HTML, term)
  8. Upload to Codecov
  9. Enforce 80% coverage threshold
  10. Publish test results and artifacts

#### backend-code-quality
- **Runtime**: ~3-5 minutes
- **Steps**:
  1. Black formatting check
  2. isort import sorting check
  3. flake8 linting
  4. mypy type checking (continue-on-error)
  5. Bandit security scanning
  6. Upload security reports

**Exit Criteria**:
- All unit tests pass
- All integration tests pass
- Coverage >= 80%
- Code formatting compliant
- No linting errors

### 2. Frontend Tests (`frontend-tests.yml`)

**Purpose**: Validate frontend code quality, run tests, and check builds.

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Only when frontend files change

**Jobs**:

#### frontend-tests
- **Runtime**: ~5-8 minutes
- **Steps**:
  1. Checkout code
  2. Setup Node.js 18 with npm caching
  3. Install dependencies (npm ci)
  4. Run ESLint
  5. Run TypeScript type checking (tsc --noEmit)
  6. Run tests with coverage (if configured)
  7. Build Next.js application
  8. Upload to Codecov (if coverage exists)
  9. Check 60% coverage threshold (soft requirement)
  10. Upload artifacts

#### frontend-code-quality
- **Runtime**: ~3-5 minutes
- **Steps**:
  1. Prettier formatting check
  2. ESLint with detailed report
  3. Check for console statements
  4. Bundle size analysis
  5. Upload reports

#### frontend-security
- **Runtime**: ~2-3 minutes
- **Steps**:
  1. npm audit for vulnerabilities
  2. Check outdated dependencies
  3. Upload audit reports

**Exit Criteria**:
- Linting passes
- Type checking passes
- Build succeeds
- Tests pass (when configured)

### 3. Security Scanning (`security.yml`)

**Purpose**: Comprehensive security scanning across the entire codebase.

**Triggers**:
- Push to `main` or `develop`
- Pull requests to `main`
- Weekly schedule (Mondays at 2 AM UTC)
- Manual trigger (workflow_dispatch)

**Jobs**:

#### dependency-scan-python
- Safety check for Python vulnerabilities
- Reports uploaded as artifacts

#### dependency-scan-node
- npm audit for JavaScript vulnerabilities
- Reports uploaded as artifacts

#### secret-scanning
- TruffleHog for exposed secrets
- Full repository history scan
- Only verified secrets reported

#### codeql-analysis
- GitHub CodeQL for Python and JavaScript
- Security and quality queries
- Results uploaded to GitHub Security tab

#### trivy-scan
- Container and filesystem scanning
- SARIF format for GitHub integration
- JSON format for artifacts

#### bandit-scan
- Python security linting
- Medium+ severity and confidence
- JSON reports uploaded

#### dependency-review
- Pull request only
- Checks for new vulnerable dependencies
- Enforces license compliance

#### security-summary
- Aggregates all scan results
- Generates comprehensive summary
- Fails if critical issues found

**Exit Criteria**:
- No verified secrets detected
- No critical vulnerabilities
- CodeQL analysis passes
- License compliance maintained

### 4. Production Readiness (`production-readiness.yml`)

**Purpose**: End-to-end testing against production/staging environments.

**Triggers**:
- Manual trigger with environment selection
- Weekly schedule (Sundays at 3 AM UTC)
- Push to `main` (comprehensive test files)

**Jobs**:

#### comprehensive-test-suite
- **Runtime**: ~15-20 minutes
- Runs `comprehensive_test_suite.py` against production
- Tests all API endpoints
- Validates workflow completeness
- Generates JSON test results

#### production-readiness-test
- **Runtime**: ~15-20 minutes
- Runs `production_readiness_test.py`
- Comprehensive production validation
- Generates markdown reports
- All results uploaded as artifacts

#### performance-test
- **Runtime**: ~5-10 minutes
- Basic performance testing
- Health endpoint checks
- Metrics validation
- Response time analysis

#### create-issue-on-failure
- Automatically creates GitHub issue
- Includes workflow run links
- Tags with appropriate labels
- Provides debugging checklist

#### notify-success
- Generates success summary
- Lists completed tests
- Provides confidence report

**Exit Criteria**:
- All production tests pass
- Performance metrics acceptable
- Health checks successful

## Coverage Configuration

### Codecov Setup (`.codecov.yml`)

**Project Coverage**:
- Target: 80%
- Threshold: 2% drop allowed
- Enforced in CI

**Patch Coverage**:
- Target: 70%
- Threshold: 5% drop allowed
- Applies to new code in PRs

**Flags**:
- `backend`: Backend Python code (80% target)
- `frontend`: Frontend TypeScript code (60% target)
- `unit`: Unit tests
- `integration`: Integration tests

**Components**:
- `agents`: AI agent code
- `api`: API endpoints
- `services`: Business logic
- `db`: Database layer
- `frontend_components`: React components
- `frontend_pages`: Next.js pages

**Ignored Paths**:
- Test files
- Migrations
- Config files
- `__init__.py` files
- Build artifacts

## Test Execution Scripts

### 1. `run-all-tests.sh`

**Purpose**: Complete local test suite execution

**Features**:
- Runs backend and frontend tests
- Optional validation tests
- Coverage reporting
- Colored output
- Detailed summary

**Options**:
```bash
--backend-only       # Backend tests only
--frontend-only      # Frontend tests only
--with-validation    # Include experimental tests
--no-coverage        # Skip coverage
--verbose            # Detailed output
```

**Usage**:
```bash
# Run everything
./scripts/run-all-tests.sh

# Backend only with validation
./scripts/run-all-tests.sh --backend-only --with-validation

# Verbose mode
./scripts/run-all-tests.sh --verbose
```

### 2. `check-coverage.sh`

**Purpose**: Generate and validate coverage reports

**Features**:
- Backend coverage with threshold check (80%)
- Frontend coverage with threshold check (60%)
- HTML report generation
- Browser integration
- JSON/XML/HTML outputs

**Options**:
```bash
--backend-threshold N   # Custom backend threshold
--frontend-threshold N  # Custom frontend threshold
--open                 # Open reports in browser
```

**Usage**:
```bash
# Standard coverage check
./scripts/check-coverage.sh

# Custom thresholds
./scripts/check-coverage.sh --backend-threshold 85 --frontend-threshold 70

# Open in browser
./scripts/check-coverage.sh --open
```

### 3. `pre-commit-tests.sh`

**Purpose**: Fast pre-commit validation

**Features**:
- Detects changed files
- Runs only relevant checks
- Quick linting and formatting
- Fast unit tests only
- Common issue detection

**Checks**:
- Black formatting
- isort import sorting
- flake8 linting
- ESLint
- TypeScript type checking
- Console statement detection
- TODO/FIXME detection
- Debugging code detection

**Usage**:
```bash
# Before committing
./scripts/pre-commit-tests.sh

# Auto-fix issues
cd backend && black app tests && isort app tests
cd frontend && npm run lint --fix
```

## GitHub Secrets Required

Set these secrets in GitHub repository settings:

### Required
- `ANTHROPIC_API_KEY`: Claude API key for backend tests
- `CODECOV_TOKEN`: Codecov upload token

### Optional (for deployment)
- `RAILWAY_TOKEN`: Railway CLI token
- `VERCEL_TOKEN`: Vercel deployment token
- `VERCEL_ORG_ID`: Vercel organization ID
- `VERCEL_PROJECT_ID`: Vercel project ID
- `SLACK_WEBHOOK`: Slack notifications (optional)

## Setup Instructions

### 1. Initial Repository Setup

```bash
# Clone repository
git clone <repo-url>
cd meta-analysis-tool

# Initialize git if needed
git init
git remote add origin <repo-url>

# Create main branch
git checkout -b main
```

### 2. Configure GitHub Secrets

```bash
# Go to: https://github.com/YOUR_USERNAME/meta-analysis-tool/settings/secrets/actions
# Add required secrets (see above)
```

### 3. Set Up Codecov

```bash
# 1. Go to https://codecov.io
# 2. Sign in with GitHub
# 3. Enable repository: meta-analysis-tool
# 4. Copy CODECOV_TOKEN
# 5. Add to GitHub secrets
```

### 4. Update Badge URLs

Edit `README.md` and replace `YOUR_USERNAME` with your GitHub username:

```markdown
[![Backend Tests](https://github.com/YOUR_USERNAME/meta-analysis-tool/workflows/Backend%20Tests/badge.svg)]
[![codecov](https://codecov.io/gh/YOUR_USERNAME/meta-analysis-tool/branch/main/graph/badge.svg)]
```

### 5. Enable Branch Protection

Go to: Settings > Branches > Add rule

**Branch name pattern**: `main`

**Enable**:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
  - Backend Tests
  - Frontend Tests
  - Security Scanning
- ✅ Require branches to be up to date
- ✅ Include administrators

### 6. First Push

```bash
# Add all CI/CD files
git add .github/ scripts/ .codecov.yml README.md

# Commit
git commit -m "Add production-grade CI/CD infrastructure"

# Push
git push origin main
```

### 7. Verify Workflows

```bash
# Go to: https://github.com/YOUR_USERNAME/meta-analysis-tool/actions
# Verify all workflows run successfully
# Check coverage reports on Codecov
```

## Monitoring and Maintenance

### Daily
- Check failed workflow runs
- Review security scan results
- Monitor coverage trends

### Weekly
- Review production readiness reports
- Update dependencies
- Check for outdated packages

### Monthly
- Review and update workflow configurations
- Optimize test execution times
- Update documentation

## Troubleshooting

### Tests Failing Locally

```bash
# Check Python environment
cd backend
python --version  # Should be 3.11
pip list

# Check Node environment
cd frontend
node --version  # Should be 18
npm list

# Reset environment
rm -rf backend/venv frontend/node_modules
./scripts/run-all-tests.sh
```

### Coverage Not Uploading

```bash
# Verify Codecov token
echo $CODECOV_TOKEN

# Check coverage files exist
ls -la backend/coverage.xml
ls -la frontend/coverage/lcov.info

# Manual upload
cd backend
codecov -t $CODECOV_TOKEN -f coverage.xml -F backend
```

### Workflow Permission Errors

```bash
# Go to: Settings > Actions > General
# Ensure "Read and write permissions" enabled
# Enable "Allow GitHub Actions to create and approve pull requests"
```

### Security Scan False Positives

Edit `.github/workflows/security.yml` to adjust severity levels:

```yaml
# Trivy
severity: 'CRITICAL,HIGH'  # Remove MEDIUM

# Bandit
--severity-level high      # Increase from medium
```

## Best Practices

### For Developers

1. **Run pre-commit checks** before committing
2. **Check coverage** before creating PR
3. **Fix linting** errors immediately
4. **Review security** scan results
5. **Keep dependencies** up to date

### For Reviewers

1. **Check CI status** before reviewing
2. **Review coverage** diff in PR
3. **Verify tests** cover new code
4. **Check security** scan results
5. **Ensure documentation** updated

### For Maintainers

1. **Monitor workflow** execution times
2. **Optimize slow** tests
3. **Update dependencies** regularly
4. **Review security** policies
5. **Maintain documentation**

## Metrics and Reporting

### Key Metrics

- **Test Success Rate**: Target 100%
- **Coverage**: Backend 80%, Frontend 60%
- **Build Time**: Backend <10min, Frontend <8min
- **Security Issues**: 0 critical/high
- **Deployment Success**: >99%

### Reports Generated

1. **Test Results**: XML/HTML/JSON
2. **Coverage Reports**: Codecov dashboard
3. **Security Scans**: GitHub Security tab
4. **Production Readiness**: Weekly artifacts
5. **Performance**: Response time metrics

## Future Enhancements

### Planned Improvements

1. **E2E Testing**: Add Playwright/Cypress tests
2. **Visual Regression**: Add screenshot comparisons
3. **Load Testing**: Implement Locust tests
4. **Chaos Engineering**: Add failure injection
5. **A/B Testing**: Deployment strategies
6. **Observability**: Enhanced monitoring
7. **Auto-scaling**: Load-based scaling
8. **Multi-region**: Geographic distribution

### Under Consideration

- Canary deployments
- Blue-green deployments
- Feature flags
- Automated rollbacks
- Cost optimization
- Performance budgets

## Support and Resources

### Documentation
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Codecov Docs](https://docs.codecov.com)
- [pytest Docs](https://docs.pytest.org)
- [Jest Docs](https://jestjs.io)

### Internal Resources
- [Architecture Overview](ARCHITECTURE.md)
- [Testing Strategy](TESTING_STRATEGY.md)
- [Production Readiness](PRODUCTION_READINESS_REPORT.md)

### Contact
- **DevOps Issues**: Create GitHub issue with `devops` label
- **Security Issues**: Create GitHub issue with `security` label
- **CI/CD Questions**: Create discussion in GitHub Discussions

---

**Last Updated**: 2025-11-05
**Maintained By**: Infrastructure Team
**Review Schedule**: Monthly
