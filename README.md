# Meta-Analysis Research Platform

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