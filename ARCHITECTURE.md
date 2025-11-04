# Meta-Analysis Research Platform - Architecture

## Vision
An AI-powered research platform using specialized agents to automate and enhance meta-analysis, making it faster, more accurate, and fully explainable. Each agent represents expert knowledge in a specific domain, working together in orchestration.

## Core Principles
1. **Agent Specialization**: Each agent is an expert in one domain
2. **Explainability**: Every decision must be traceable and explainable
3. **Human-in-the-Loop**: Researchers maintain control and oversight
4. **Verification**: Results must be validated against known meta-analyses
5. **Extensibility**: Plugin architecture for different research methodologies

## System Architecture

### Layer 1: Agent Framework
**Core agent system that all specialized agents inherit from**

- `BaseAgent`: Abstract base class for all agents
  - Decision logging
  - State management
  - Communication protocol
  - Learning interface

- `AgentOrchestrator`: Coordinates agent collaboration
  - Workflow management
  - Inter-agent communication
  - Conflict resolution
  - Progress tracking

- `AgentRegistry`: Manages available agents and their capabilities
  - Plugin system for adding new agents
  - Version control for agent updates
  - Expert profile storage (who programmed this agent)

### Layer 2: Specialized Research Agents

#### Core Meta-Analysis Agents
1. **CoordinatorAgent**
   - Manages overall meta-analysis workflow
   - Delegates tasks to specialized agents
   - Synthesizes final results
   - Tracks project state

2. **SearchAgent**
   - Queries academic databases (PubMed, PsycINFO, Web of Science)
   - Semantic search for relevant studies
   - Citation network analysis
   - Handles different database APIs

3. **ScreeningAgent**
   - Applies inclusion/exclusion criteria
   - Title and abstract screening
   - Full-text screening
   - PRISMA flow diagram generation

4. **QualityAssessmentAgent**
   - Evaluates study methodology
   - Risk of bias assessment
   - Quality scoring (Newcastle-Ottawa, Cochrane tools)
   - Publication bias detection

5. **DataExtractionAgent**
   - Extracts statistics from papers
   - Identifies effect sizes, sample sizes, p-values
   - Standardizes data formats
   - Handles multiple study designs

6. **StatisticalAgent**
   - Performs meta-analysis calculations
   - Fixed/random effects models
   - Heterogeneity assessment (I², τ²)
   - Forest plot generation
   - Subgroup analysis

7. **ReportAgent**
   - Generates APA-compliant reports
   - Creates visualizations
   - Formats citations
   - Produces publication-ready documents

8. **QAAgent** (Question-Answering)
   - Natural language interface
   - Explains agent decisions
   - Provides methodological justification
   - Answers researcher questions

9. **VerificationAgent**
   - Validates results against known meta-analyses
   - Confidence scoring
   - Identifies discrepancies
   - Suggests improvements

#### Methodological Specialist Agents (Future)
- **QualitativeAgent**: Handles qualitative synthesis
- **QuantitativeAgent**: Advanced statistical methods
- **MixedMethodsAgent**: Integrates qual + quant
- **SecurityAgent**: Ensures data privacy and ethics
- **IntegrityAgent**: Checks for research fraud
- **PublishingAgent**: Automates submission to journals

### Layer 3: Backend Services

#### API Layer (FastAPI)
```
/api/v1/meta-analysis
  POST /create          - Start new meta-analysis
  GET  /status/{id}     - Get progress
  POST /ask             - Ask questions about results
  GET  /report/{id}     - Get final report
  GET  /audit/{id}      - Get decision trail

/api/v1/agents
  GET  /available       - List available agents
  GET  /profile/{name}  - Get agent profile (expert info)
  POST /configure       - Configure agent behavior

/api/v1/studies
  POST /search          - Search for studies
  GET  /screen          - Screen studies
  POST /extract         - Extract data
```

#### Data Layer
- **PostgreSQL**: Structured data (studies, results, metadata)
- **Vector DB** (Chroma/Pinecone): Semantic search over papers
- **Redis**: Caching and real-time updates
- **File Storage**: PDFs, extracted tables, images

#### LLM Integration
- **Primary**: Claude (Anthropic) for complex reasoning
- **Fallback**: GPT-4 for specific tasks
- **Local**: Fine-tuned models for data extraction
- **Prompt Templates**: Expert-programmed prompts per agent

### Layer 4: Frontend (Web Interface)

#### Researcher Dashboard
- Project creation and configuration
- Real-time progress tracking
- Agent activity visualization
- Results exploration

#### Chat Interface
- Natural language queries
- Conversational Q&A with QAAgent
- Voice input/output capability

#### Visualization Suite
- Forest plots
- Funnel plots for publication bias
- PRISMA flow diagrams
- Risk of bias summaries

#### Audit Trail Viewer
- Decision history
- Agent reasoning chains
- Confidence scores
- Override capabilities

### Layer 5: Learning & Update System

#### Agent Learning Loop
1. Agent completes task
2. Human expert reviews decisions
3. Feedback incorporated into agent prompt/weights
4. Updates pushed to agent registry
5. All instances updated on next run

#### Collective Intelligence
- Central "super agent" aggregates learnings
- Parallel agent instances share knowledge
- Continuous improvement from each study
- Version control for agent evolution

## Verification System

### Self-Validation
1. **Known Meta-Analysis Test Suite**
   - Library of published meta-analyses
   - System replicates each one
   - Compares results (effect sizes, confidence intervals)
   - Reports match percentage

2. **Cross-Validation**
   - Multiple agents independently analyze same study
   - Compare results
   - Flag disagreements
   - Consensus mechanism

3. **Statistical Checks**
   - Sanity checks on calculations
   - Reproducibility testing
   - Sensitivity analysis

### Provenance Tracking
- Every number traces back to source paper
- Every decision logged with reasoning
- Citation management
- Audit trail for peer review

## Security & Ethics

### Data Privacy
- HIPAA compliance for medical data
- Anonymization of sensitive information
- Secure storage and transmission
- Access control

### Research Ethics
- Plagiarism detection
- Proper attribution
- IRB compliance checking
- Conflict of interest tracking

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Agents**: LangGraph + Claude SDK
- **Stats**: statsmodels, scipy, metafor (via rpy2)
- **Database**: PostgreSQL + pgvector
- **Vector Search**: ChromaDB
- **Caching**: Redis
- **PDF Processing**: PyMuPDF, pdfplumber
- **NLP**: spaCy, sentence-transformers

### Frontend
- **Framework**: Next.js 14 (React)
- **UI**: Tailwind CSS + shadcn/ui
- **Charts**: Plotly, Recharts
- **State**: Zustand
- **API Client**: React Query

### Infrastructure
- **Deployment**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack

## Development Phases

### Phase 1: MVP (Current)
- Basic agent framework
- Search, screen, extract, analyze agents
- Simple web interface
- Single meta-analysis demo
- Q&A capability

### Phase 2: Verification
- Known meta-analysis test suite
- Confidence scoring
- Audit trail interface
- Expert validation

### Phase 3: Expert Programming
- Agent profile system
- Expert prompt templates
- Learning feedback loop
- Agent versioning

### Phase 4: Plugin Architecture
- Custom agent creation
- Methodological plugins
- Integration with other tools
- API for third-party agents

### Phase 5: Collective Intelligence
- Multi-project learning
- Super agent aggregation
- Cloud synchronization
- Community agent marketplace

## Success Metrics

1. **Accuracy**: >95% match with published meta-analyses
2. **Speed**: 10-100x faster than manual meta-analysis
3. **Explainability**: Every decision traceable
4. **User Trust**: Researchers willing to publish results
5. **Adoption**: Psychology departments using it
6. **Publication**: APA accepts AI-assisted meta-analyses

## Future Vision

- **Agent Marketplace**: Researchers publish expert agents
- **Living Meta-Analyses**: Continuously updated as new studies publish
- **Multi-Modal**: Image analysis, video data, sensor data
- **Global Research Network**: Agents coordinating across institutions
- **Cultural Sensitivity**: Agents trained on diverse perspectives
- **Democratization**: Free tools for underfunded researchers
