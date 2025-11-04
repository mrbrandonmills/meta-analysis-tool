# Demo & Testing Guide

This guide will walk you through demonstrating the Meta-Analysis Research Platform to your psychology professor or other stakeholders.

## 🎯 Demo Objectives

Show that the platform can:
1. Understand complex research questions
2. Create systematic workflows
3. Search academic databases effectively
4. Apply screening criteria consistently
5. Explain every decision made
6. Provide confidence assessments
7. Generate audit trails for peer review

## 🚀 Pre-Demo Setup

### 1. Environment Setup

```bash
# Make sure you have the API key
export ANTHROPIC_API_KEY=your_key_here

# Start the backend
cd backend
source venv/bin/activate
python -m app.main

# In another terminal, start the frontend
cd frontend
npm run dev
```

### 2. Test the API

```bash
# Quick health check
curl http://localhost:8000/health

# Should return: {"status": "healthy"}
```

## 📖 Demo Script

### Part 1: Introduction (5 minutes)

**Key Points to Explain:**

1. **The Problem**
   - Meta-analyses take months/years
   - Huge potential for human error
   - Difficult to validate decisions
   - Resource intensive

2. **Our Solution**
   - Specialized AI agents for each task
   - Complete explainability
   - Faster and more systematic
   - Designed for academic publication

3. **Key Innovation**
   - Not just one AI - team of expert agents
   - Each agent can be programmed by domain experts
   - Full audit trail for peer review
   - Human-in-the-loop design

### Part 2: Live Demo (15 minutes)

#### Demo 1: Create a Meta-Analysis

**Research Question**: "What is the effectiveness of mindfulness-based interventions in reducing anxiety in adults?"

```bash
curl -X POST http://localhost:8000/api/v1/meta-analysis/create \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "What is the effectiveness of mindfulness-based interventions in reducing anxiety in adults?",
    "topic": "Mindfulness and Anxiety in Adults",
    "inclusion_criteria": [
      "Randomized controlled trial (RCT)",
      "Adult population (ages 18-65)",
      "Mindfulness-based intervention",
      "Anxiety as primary or secondary outcome",
      "Published in peer-reviewed journal"
    ],
    "exclusion_criteria": [
      "Non-English language",
      "Qualitative studies",
      "Case reports or case series",
      "Studies with clinical populations only (unless anxiety is primary)",
      "Unpublished dissertations"
    ],
    "databases": ["pubmed"],
    "expert_name": "Dr. [Your Professor Name]"
  }' | json_pp
```

**What to Point Out:**
- The coordinator agent analyzes the question
- Creates a systematic workflow plan
- Identifies key concepts and search terms
- Recommends appropriate methodology
- Documents everything

Save the `id` from the response for the next step.

#### Demo 2: Execute the Search and Screening

```bash
curl -X POST http://localhost:8000/api/v1/meta-analysis/execute/{analysis_id} | json_pp
```

**What to Point Out:**
1. **Search Agent**:
   - Constructs optimized PubMed queries
   - Actually searches the database
   - Returns real studies
   - Documents search strategy

2. **Screening Agent**:
   - Applies criteria systematically
   - Provides reasoning for each decision
   - Generates PRISMA-compliant data
   - Flags uncertain cases

#### Demo 3: Ask Questions (Most Impressive Part!)

This is where you demonstrate explainability and trustworthiness.

**Question 1**: "How did you decide which studies to include?"

```bash
curl -X POST http://localhost:8000/api/v1/meta-analysis/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How did you decide which studies to include?"
  }' | json_pp
```

**What to Point Out:**
- Agent explains the methodology
- References specific criteria
- Cites PRISMA guidelines
- Provides confidence level

**Question 2**: "Can you explain why Study X was excluded?"

```bash
curl -X POST http://localhost:8000/api/v1/meta-analysis/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Why would a study be excluded if it was not a randomized controlled trial?"
  }' | json_pp
```

**Question 3**: "How reliable is this analysis?"

```bash
curl -X POST http://localhost:8000/api/v1/meta-analysis/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How reliable is this analysis and how does it compare to a human-conducted meta-analysis?"
  }' | json_pp
```

**What to Point Out:**
- Honest about limitations
- Discusses confidence levels
- Explains verification process
- Acknowledges where human review is needed

#### Demo 4: Audit Trail

```bash
curl http://localhost:8000/api/v1/meta-analysis/audit/{analysis_id} | json_pp
```

**What to Point Out:**
- Complete record of all decisions
- Each decision has reasoning
- Confidence scores
- Timestamps
- Traceable to expert who programmed the agent

### Part 3: Web Interface Demo (10 minutes)

Open http://localhost:3000 in a browser.

1. **Create a Meta-Analysis**
   - Show the simple interface
   - Enter a research question
   - Demonstrate real-time feedback

2. **Interactive Q&A**
   - Ask various questions
   - Show how the agent provides follow-up suggestions
   - Demonstrate that it remembers context

3. **Agent Overview**
   - Show the available agents
   - Explain each agent's role
   - Discuss how new agents can be added

### Part 4: Advanced Features Discussion (10 minutes)

#### Agent Programming

Explain how experts can program agents:

```python
# Example: Custom screening agent with professor's methodology
def get_system_prompt(self) -> str:
    return '''You are a screening agent programmed by Dr. [Name]
    with 20 years of meta-analysis experience.

    You follow these principles:
    1. [Professor's specific methodology]
    2. [Their quality standards]
    3. [Their decision framework]

    When uncertain, you flag for human review because...
    [Their philosophy on uncertainty]
    '''
```

**Key Points:**
- Each agent can encode an expert's methodology
- Agents can learn from feedback
- Version control for agent updates
- Multiple experts can contribute

#### Verification System (Coming Soon)

Explain the verification approach:

1. **Test Suite**: Known meta-analyses
2. **Validation**: Compare our results to published results
3. **Metrics**: Report match percentage
4. **Continuous Improvement**: Learn from discrepancies

#### Collective Intelligence (Vision)

Explain the future:

1. Agent learns from each project
2. Updates shared to cloud
3. All instances benefit
4. Community of expert agents
5. Living meta-analyses that update with new research

## 🎤 Handling Questions

### Common Questions and Answers

**Q: "How do I know it's not hallucinating?"**

A:
- Every fact traces back to a source paper
- We use citations and provenance tracking
- Cross-validation between agents
- Verification against known meta-analyses
- Conservative flagging of uncertain cases

**Q: "Would peer reviewers accept this?"**

A:
- PRISMA-compliant methodology
- Complete documentation
- Audit trail shows all decisions
- Can answer any methodological question
- Designed to meet publication standards

**Q: "What if it makes a mistake?"**

A:
- Confidence scoring flags low-confidence decisions
- Human review for all uncertain cases
- Verification step catches systematic errors
- Complete audit trail allows error tracking
- Learning system improves from mistakes

**Q: "How long does this take?"**

A:
- Initial workflow: seconds
- Search: minutes (depends on database)
- Screening: minutes for 100s of studies
- Complete analysis: hours vs. months
- 10-100x faster than manual

**Q: "Can I customize the methodology?"**

A:
- Yes! Each agent uses customizable prompts
- Experts can program agents with their philosophy
- Inclusion/exclusion criteria are flexible
- Quality assessment tools are configurable
- Plugin system for custom methods (coming)

**Q: "What about non-English studies?"**

A:
- Currently focuses on English
- Multi-language support planned
- Can flag non-English studies for later review
- Translation integration possible

**Q: "Is my data private?"**

A:
- All processing is on your infrastructure
- No data sharing without consent
- Can run completely offline (after setup)
- Follows research ethics guidelines

## 🧪 Test Scenarios

### Scenario 1: Simple Meta-Analysis
- Topic: Well-defined intervention with lots of studies
- Purpose: Show core functionality
- Expected: High confidence, many studies found

### Scenario 2: Complex Meta-Analysis
- Topic: Nuanced question with multiple variables
- Purpose: Show coordinator's analytical ability
- Expected: Sophisticated workflow plan

### Scenario 3: Edge Cases
- Topic: Very few or no studies found
- Purpose: Show how system handles limits
- Expected: Honest reporting, suggestions for revision

## 📊 Success Indicators

During the demo, success looks like:

✅ System finds relevant studies
✅ Screening decisions make sense
✅ Q&A agent provides satisfactory answers
✅ Professor can see the audit trail
✅ Confidence scores are realistic
✅ System acknowledges its limitations
✅ The professor can envision using this

## 🎬 Demo Checklist

**Before the Demo:**
- [ ] Backend running and tested
- [ ] Frontend running and tested
- [ ] API key configured
- [ ] Test queries prepared
- [ ] Backup plan if internet fails
- [ ] Screenshots/videos as backup

**During the Demo:**
- [ ] Explain the vision first
- [ ] Show live functionality
- [ ] Let professor ask questions throughout
- [ ] Demonstrate Q&A agent thoroughly
- [ ] Show audit trail
- [ ] Discuss future plans

**After the Demo:**
- [ ] Provide access credentials
- [ ] Share documentation
- [ ] Schedule follow-up
- [ ] Gather feedback
- [ ] Discuss collaboration

## 🚨 Troubleshooting

### API Returns Error

```bash
# Check backend logs
tail -f backend/logs/app.log

# Common issues:
# - API key not set
# - Rate limits
# - Network timeout
```

### PubMed Search Fails

```bash
# Verify PubMed access
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=anxiety&retmode=json"

# If blocked, use cached demo data
```

### Frontend Won't Connect

```bash
# Check CORS settings
# Verify API_URL in .env
# Check browser console for errors
```

## 📝 Feedback Collection

After the demo, ask:

1. **Clarity**: Did you understand how it works?
2. **Trust**: Would you trust these results?
3. **Usefulness**: Would this save you time?
4. **Concerns**: What worries you most?
5. **Features**: What's missing?
6. **Collaboration**: Want to help program an agent?

## 🎯 Call to Action

End the demo with:

1. **Immediate**: Try it yourself with your research question
2. **Short-term**: Collaborate on agent programming
3. **Long-term**: Co-author paper on methodology
4. **Vision**: Build community of expert agents

---

**Remember**: The goal is not to show a perfect system, but to demonstrate a vision and get buy-in for the approach. Honesty about limitations builds more trust than overpromising!
