# Meta-Analysis Research Platform

[![Backend CI/CD](https://github.com/YOUR_USERNAME/meta-analysis-tool/actions/workflows/backend-ci-cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/meta-analysis-tool/actions/workflows/backend-ci-cd.yml)
[![Frontend CI/CD](https://github.com/YOUR_USERNAME/meta-analysis-tool/actions/workflows/frontend-ci-cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/meta-analysis-tool/actions/workflows/frontend-ci-cd.yml)
[![E2E Tests](https://github.com/YOUR_USERNAME/meta-analysis-tool/actions/workflows/e2e-tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/meta-analysis-tool/actions/workflows/e2e-tests.yml)
[![Security Scanning](https://github.com/YOUR_USERNAME/meta-analysis-tool/actions/workflows/security.yml/badge.svg)](https://github.com/YOUR_USERNAME/meta-analysis-tool/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/meta-analysis-tool/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/meta-analysis-tool)
[![Railway](https://img.shields.io/badge/Railway-Backend-0B0D0E?logo=railway)](https://meta-analysis-api.railway.app)
[![Vercel](https://img.shields.io/badge/Vercel-Frontend-000000?logo=vercel)](https://meta-analysis-tool.vercel.app)
[![Test Coverage](https://img.shields.io/badge/coverage-80%25-brightgreen)](https://codecov.io/gh/YOUR_USERNAME/meta-analysis-tool)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178C6?logo=typescript)](https://www.typescriptlang.org/)

An AI-powered research platform that uses specialized agents to automate and enhance meta-analysis, making it faster, more accurate, and fully explainable.

## 🎯 Vision

Transform research by creating a multi-agent system where each agent represents expert knowledge in a specific domain. This platform enables:

- **Expert-Programmed Agents**: Each agent can be "programmed" by domain experts with their methodology and philosophy
- **Full Explainability**: Every decision is traceable with complete audit trails
- **Collective Intelligence**: Agents learn from each research project and share knowledge
- **Cultural Sensitivity**: Designed to enhance research quality without flattening cultural nuances
- **Human-in-the-Loop**: Researchers maintain control while AI handles tedious tasks

## 🚀 Current Status: MVP

This MVP demonstrates the core concept with:

✅ Multi-agent architecture with specialized research agents
✅ Coordinator, Search, Screening, and Q&A agents implemented
✅ FastAPI backend with REST endpoints
✅ Complete audit trail and decision tracking
✅ Natural language Q&A interface
✅ Real PubMed integration for study search
✅ PRISMA-compliant screening workflow

## 🏗️ Architecture

### Agent Framework

Every agent inherits from `BaseAgent` and implements:
- Expert-encoded system prompts
- Decision-making with reasoning and confidence
- Communication with other agents
- Complete audit logging

### Specialized Agents

1. **CoordinatorAgent**: Orchestrates the entire workflow
2. **SearchAgent**: Searches PubMed and other databases
3. **ScreeningAgent**: Applies inclusion/exclusion criteria
4. **QAAgent**: Answers questions and explains decisions
5. More agents coming: Quality Assessment, Data Extraction, Statistical, Report, Verification

## 📋 Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd meta-analysis-tool
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Run with Docker
docker-compose up -d

# Or run locally
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

See [Quick Start Guide](docs/QUICKSTART.md) for detailed instructions.

## 📖 Usage Example

```bash
# Create a meta-analysis
curl -X POST http://localhost:8000/api/v1/meta-analysis/create \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "What is the effect of mindfulness on anxiety?",
    "topic": "Mindfulness and Anxiety",
    "databases": ["pubmed"]
  }'

# Ask questions about the process
curl -X POST http://localhost:8000/api/v1/meta-analysis/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How did you decide which studies to include?"}'
```

## 🎓 For Researchers

### Why Use This?

- **Save Time**: Months of work → Days
- **Reduce Errors**: Systematic, reproducible process
- **Build Trust**: Complete audit trail for peer review
- **Stay in Control**: Human oversight at every step

### Addressing Concerns

**"How do I know it's accurate?"**
- Every finding traces to source papers
- Verification against known meta-analyses
- Confidence scores on every decision
- Flags uncertain cases for human review

**"Will peer reviewers accept this?"**
- PRISMA-compliant methodology
- APA-format reports
- Complete methodological documentation
- Q&A agent can answer reviewer questions

See [Demo Guide](docs/DEMO.md) for a complete walkthrough.

## 📚 Documentation

- [Quick Start Guide](docs/QUICKSTART.md) - Get running in 10 minutes
- [Architecture Overview](ARCHITECTURE.md) - How the system works
- [Demo Guide](docs/DEMO.md) - How to demonstrate the platform
- [API Documentation](docs/API.md) - API reference

## 🧪 Testing & CI/CD

This project uses comprehensive automated testing and continuous integration to ensure code quality and reliability.

### Running Tests Locally

```bash
# Run all tests (backend + frontend)
./scripts/run-all-tests.sh

# Run backend tests only
./scripts/run-all-tests.sh --backend-only

# Run frontend tests only
./scripts/run-all-tests.sh --frontend-only

# Include validation tests (experimental)
./scripts/run-all-tests.sh --with-validation

# Check coverage and generate reports
./scripts/check-coverage.sh

# Open coverage reports in browser
./scripts/check-coverage.sh --open

# Quick pre-commit checks
./scripts/pre-commit-tests.sh
```

### CI/CD Workflows

Our GitHub Actions workflows automatically test every change:

#### Backend Tests
- **Trigger**: Push to main/develop, Pull requests
- **Coverage**: Unit tests, integration tests, validation tests
- **Quality Gates**: 80% code coverage required
- **Security**: Bandit security scanning
- **Runtime**: ~5-10 minutes

#### Frontend Tests
- **Trigger**: Push to main/develop, Pull requests
- **Coverage**: Linting, type checking, tests, build verification
- **Quality Gates**: 60% code coverage target
- **Security**: npm audit, ESLint
- **Runtime**: ~5-8 minutes

#### Security Scanning
- **Trigger**: Push, Pull requests, Weekly schedule
- **Scans**:
  - Dependency vulnerabilities (Safety, npm audit)
  - Secret detection (TruffleHog)
  - Code analysis (CodeQL)
  - Container scanning (Trivy)
  - Security linting (Bandit)
- **Runtime**: ~10-15 minutes

#### Production Readiness
- **Trigger**: Manual or weekly schedule
- **Tests**:
  - Comprehensive test suite against production
  - Performance testing
  - Health checks
  - API validation
- **Reporting**: Automated issue creation on failures
- **Runtime**: ~20-30 minutes

### Test Coverage

We maintain high test coverage standards:
- **Backend**: 80% minimum coverage (enforced in CI)
- **Frontend**: 60% target coverage (new tests being added)
- **Critical paths**: 90%+ coverage required

Coverage reports are automatically uploaded to [Codecov](https://codecov.io) and visible in pull requests.

### Quality Standards

All code must pass:
- ✅ Unit tests and integration tests
- ✅ Code formatting (Black, Prettier)
- ✅ Linting (flake8, ESLint)
- ✅ Type checking (mypy, TypeScript)
- ✅ Security scans (no high/critical vulnerabilities)
- ✅ Coverage thresholds

### Development Workflow

```bash
# 1. Make your changes
git checkout -b feature/my-feature

# 2. Run pre-commit checks
./scripts/pre-commit-tests.sh

# 3. Commit if checks pass
git commit -m "Add my feature"

# 4. Run full test suite
./scripts/run-all-tests.sh

# 5. Check coverage
./scripts/check-coverage.sh

# 6. Push and create PR
git push origin feature/my-feature
```

### Continuous Deployment

- **Production**: Automatic deployment on merge to `main`
- **Staging**: Automatic deployment on merge to `develop`
- **Platforms**: Railway (backend), Vercel (frontend)
- **Post-deploy**: Smoke tests verify deployment health

## 🗺️ Roadmap

- [x] **Phase 1 (MVP)**: Core agents and workflow
- [ ] **Phase 2**: Verification system and validation
- [ ] **Phase 3**: Full pipeline (quality, extraction, statistics, reports)
- [ ] **Phase 4**: Expert programming and learning
- [ ] **Phase 5**: Plugin architecture and marketplace
- [ ] **Phase 6**: Collective intelligence and living meta-analyses

## 🤝 Contributing

We welcome contributions from:
- Researchers with domain expertise
- Developers improving the code
- Anyone with ideas for new agents

## 📧 Contact

Questions or feedback? Create an issue on GitHub!

---

**Built with**: Python, FastAPI, Claude (Anthropic), React/Next.js
**License**: [Your license]