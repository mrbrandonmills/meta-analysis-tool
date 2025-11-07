# Agent Enhancements Documentation

Comprehensive documentation for enhanced SearchAgent V2, ScreeningAgent V2, and CredibilityAgent V2.

## Table of Contents

1. [Overview](#overview)
2. [SearchAgent V2](#searchagent-v2)
3. [ScreeningAgent V2](#screeningagent-v2)
4. [CredibilityAgent V2](#credibilityagent-v2)
5. [Configuration](#configuration)
6. [Usage Examples](#usage-examples)
7. [Algorithm Details](#algorithm-details)
8. [Performance Considerations](#performance-considerations)

---

## Overview

The enhanced agents provide production-ready, research-grade capabilities for systematic literature review and meta-analysis. Each agent implements state-of-the-art algorithms and follows established methodological guidelines (PRISMA, Cochrane, GRADE).

### Key Improvements

**SearchAgent V2:**
- Multi-database support (PubMed, arXiv, Europe PMC, CORE)
- Advanced Boolean query construction
- MeSH term expansion
- Intelligent synonym detection
- Enhanced deduplication (DOI, PMID, fuzzy title matching)
- Result caching and rate limiting

**ScreeningAgent V2:**
- ML-based relevance scoring using TF-IDF and cosine similarity
- Multi-stage screening (title → abstract → full-text)
- Batch processing with parallel execution
- Inter-rater reliability metrics (Cohen's kappa)
- Detailed decision justifications

**CredibilityAgent V2:**
- Cochrane Risk of Bias (RoB 2.0) assessment
- GRADE quality evaluation
- Study design hierarchy classification
- Retraction checking
- Citation count analysis
- Journal quality assessment

---

## SearchAgent V2

### Features

#### 1. Multi-Database Search

Searches across multiple academic databases simultaneously:

- **PubMed/MEDLINE**: Medical and life sciences literature
- **arXiv**: Preprints in physics, mathematics, computer science, quantitative biology
- **Europe PMC**: European biomedical and life sciences literature
- **CORE**: Open access research papers from global repositories

#### 2. Advanced Query Building

**Boolean Operators:**
```python
# AND: Narrow search (all terms must be present)
"diabetes AND treatment AND outcomes"

# OR: Broaden search (any term can be present)
"diabetes OR 'diabetes mellitus' OR diabetic"

# NOT: Exclude terms
"diabetes NOT gestational"
```

**Field-Specific Searches (PubMed):**
```python
# Search in title/abstract only
"diabetes[Title/Abstract]"

# Search in MeSH terms
"Diabetes Mellitus, Type 2[MeSH Terms]"

# Search by author
"Smith J[Author]"
```

**MeSH Term Expansion:**
```python
# Automatically expands "diabetes" to include MeSH terms:
# - Diabetes Mellitus
# - Diabetes Mellitus, Type 2
# - Blood Glucose
# - Glycated Hemoglobin A
```

#### 3. Synonym Detection

Automatically expands search terms with medical synonyms:

```python
Input: "diabetes"
Expanded: ["diabetes", "diabetes mellitus", "diabetic", "DM"]

Input: "cancer"
Expanded: ["cancer", "neoplasm", "tumor", "malignancy", "carcinoma"]
```

#### 4. Enhanced Deduplication

Three-stage deduplication strategy:

1. **DOI Matching** (exact match, most reliable)
2. **PMID Matching** (exact match, reliable)
3. **Title Similarity** (fuzzy matching using Jaccard similarity)

```python
# Example: These would be detected as duplicates
Study 1: "The Effect of Treatment on Diabetes: A Study"
Study 2: "The Effect of Treatment on Diabetes: A Study."
# (normalized titles match despite punctuation differences)
```

#### 5. Caching and Performance

- **Result Caching**: Stores search results for 1 hour to avoid repeated API calls
- **Rate Limiting**: Respects API quotas (PubMed: 3 req/s, others: 10 req/s)
- **Retry Logic**: Exponential backoff for transient failures

### Usage

```python
from app.agents.specialized.search_agent_v2 import SearchAgentV2
from app.agents.base import AgentConfig, AgentRole

# Initialize agent
config = AgentConfig(
    name="AdvancedSearchAgent",
    role=AgentRole.SEARCH,
)
agent = SearchAgentV2(config)

# Perform search
result = await agent.process({
    "research_question": "What is the effect of dietary intervention on type 2 diabetes?",
    "search_terms": ["diabetes", "dietary intervention", "glycemic control"],
    "databases": ["pubmed", "europepmc"],
    "boolean_operator": "AND",
    "expand_synonyms": True,
    "mesh_terms": ["Diabetes Mellitus, Type 2", "Diet Therapy"],
    "publication_types": ["Randomized Controlled Trial"],
    "max_results_per_db": 100,
})

# Access results
print(f"Total studies found: {result['total_results']}")
print(f"Unique studies: {result['unique_results']}")
print(f"Duplicates removed: {result['duplicates_removed']}")

for study in result['studies']:
    print(f"- {study['title']}")
    print(f"  Database: {study['database']}")
    print(f"  DOI: {study.get('doi', 'N/A')}")
```

### Output Structure

```python
{
    "search_strategy": "AI-generated search strategy text...",
    "original_terms": ["diabetes", "treatment"],
    "expanded_terms": ["diabetes", "diabetes mellitus", "diabetic", ...],
    "mesh_terms": ["Diabetes Mellitus, Type 2", ...],
    "boolean_operator": "AND",
    "databases_searched": ["pubmed", "europepmc"],
    "search_log": [
        {
            "database": "PubMed",
            "query": "(\"diabetes\"[Title/Abstract] AND \"treatment\"[Title/Abstract])",
            "results_count": 87,
            "timestamp": "2024-01-15 10:30:00"
        },
        ...
    ],
    "total_results": 150,
    "unique_results": 132,
    "duplicates_removed": 18,
    "deduplication_stats": {
        "total_input": 150,
        "duplicates_by_doi": 5,
        "duplicates_by_pmid": 8,
        "duplicates_by_title": 5,
        ...
    },
    "studies": [
        {
            "id": "PMID:12345",
            "pmid": "12345",
            "title": "Study title...",
            "abstract": "Study abstract...",
            "authors": ["Smith J", "Doe J"],
            "journal": "Journal Name",
            "year": "2023",
            "doi": "10.1234/example",
            "keywords": ["diabetes", "RCT"],
            "mesh_terms": ["Diabetes Mellitus, Type 2"],
            "database": "PubMed"
        },
        ...
    ],
    "decision": {...},  # AI assessment of search completeness
    "timestamp": "2024-01-15 10:30:00"
}
```

---

## ScreeningAgent V2

### Features

#### 1. ML-Based Relevance Scoring

Uses **TF-IDF vectorization** and **cosine similarity** to compute relevance scores:

```python
# For each study:
inclusion_score = cosine_similarity(study_vector, inclusion_criteria_vectors)
exclusion_score = cosine_similarity(study_vector, exclusion_criteria_vectors)
net_score = inclusion_score - exclusion_score  # Positive = likely include
```

#### 2. Multi-Stage Screening

Implements PRISMA-recommended multi-stage screening:

**Stage 1: Title Screening**
- Quick assessment based on title alone
- Conservative approach (when in doubt, include)
- Filters out obviously irrelevant studies

**Stage 2: Abstract Screening**
- Detailed assessment of title + abstract
- Applies PICO criteria
- Uses ML scoring
- Flags uncertain cases

**Stage 3: Full-Text Screening**
- Complete assessment of full article
- Verifies all eligibility criteria
- Final inclusion/exclusion decision

#### 3. Decision Categories

- **INCLUDE**: Meets all inclusion criteria
- **EXCLUDE**: Fails inclusion criteria OR meets exclusion criteria
- **UNCERTAIN**: Borderline case requiring human review

#### 4. Standardized Exclusion Reasons

```python
exclusion_categories = [
    "Wrong population",
    "Wrong intervention",
    "Wrong comparator",
    "Wrong outcomes",
    "Wrong study design",
    "Wrong publication type",
    "Duplicate publication",
    "Language restriction",
    "Insufficient data"
]
```

#### 5. Inter-Rater Agreement

Calculates **Cohen's kappa** to measure screening reliability:

```python
# Kappa interpretation:
# < 0.00: Poor agreement
# 0.00-0.20: Slight agreement
# 0.21-0.40: Fair agreement
# 0.41-0.60: Moderate agreement
# 0.61-0.80: Substantial agreement
# 0.81-1.00: Almost perfect agreement
```

### Usage

```python
from app.agents.specialized.screening_agent_v2 import ScreeningAgentV2

agent = ScreeningAgentV2(config)

result = await agent.process({
    "studies": studies_to_screen,
    "inclusion_criteria": [
        "Randomized controlled trials (RCTs)",
        "Adults aged 18+ with type 2 diabetes",
        "Dietary or lifestyle intervention",
        "Glycemic control outcomes (HbA1c)"
    ],
    "exclusion_criteria": [
        "Case reports or case series",
        "Pediatric populations",
        "Animal studies",
        "Editorial or opinion pieces"
    ],
    "screening_level": "abstract",  # Options: title, abstract, full_text
    "batch_size": 10,
    "use_ml_scoring": True,
    "confidence_threshold": 0.7,
})

# Access results
print(f"Total screened: {result['total_screened']}")
print(f"Included: {len(result['included'])}")
print(f"Excluded: {len(result['excluded'])}")
print(f"Uncertain: {len(result['uncertain'])}")
print(f"Inclusion rate: {result['inclusion_rate']:.1%}")

# PRISMA flow diagram data
prisma = result['prisma_data']
print(f"PRISMA exclusion reasons: {prisma['exclusion_reasons']}")
```

### Output Structure

```python
{
    "screening_level": "abstract",
    "total_screened": 132,
    "included": [
        {
            ...study_data...,
            "screening_result": {
                "decision": "include",
                "reasoning": "This RCT meets all inclusion criteria...",
                "criteria_met": ["RCT design", "Adult population", ...],
                "criteria_not_met": [],
                "exclusion_criteria_applied": [],
                "confidence": 0.85,
                "next_step": "Proceed to full-text review",
                "ml_scores": {
                    "inclusion_score": 0.78,
                    "exclusion_score": 0.12,
                    "net_score": 0.66
                },
                "level": "abstract",
                "needs_human_review": False
            }
        },
        ...
    ],
    "excluded": [...],
    "uncertain": [...],
    "inclusion_rate": 0.23,
    "exclusion_rate": 0.62,
    "uncertain_rate": 0.15,
    "prisma_data": {
        "screening_stage": "abstract",
        "records_screened": 132,
        "records_included": 30,
        "records_excluded": 82,
        "records_uncertain": 20,
        "exclusion_reasons": {
            "Wrong study design": 35,
            "Wrong population": 20,
            "Wrong outcomes": 15,
            "Insufficient data": 12
        }
    },
    "screening_stats": {
        "mean_confidence": 0.78,
        "std_confidence": 0.12,
        "high_confidence_count": 85,
        "low_confidence_count": 20,
        "ml_stats": {
            "mean_inclusion_score": 0.65,
            "mean_exclusion_score": 0.25
        }
    },
    "ml_scoring_used": True,
    "decision": {...}
}
```

### Inter-Rater Agreement Example

```python
# Compare two independent screenings
agreement = await agent.calculate_inter_rater_agreement(
    screening_results_1=rater1_results,
    screening_results_2=rater2_results
)

print(f"Cohen's kappa: {agreement['cohens_kappa']:.3f}")
print(f"Interpretation: {agreement['interpretation']}")
print(f"Agreement: {agreement['percent_agreement']:.1%}")
print(f"Disagreements: {agreement['disagreements']}")
```

---

## CredibilityAgent V2

### Features

#### 1. Cochrane Risk of Bias (RoB 2.0)

For **Randomized Controlled Trials**, assesses 5 domains:

1. **Randomization Process**
   - Was allocation sequence random?
   - Was allocation concealed?
   - Were baseline differences concerning?

2. **Deviations from Intended Interventions**
   - Were participants/personnel aware of interventions?
   - Were deviations from protocol balanced?
   - Was analysis appropriate?

3. **Missing Outcome Data**
   - Were data available for all/most participants?
   - Was missingness balanced across groups?
   - Could missingness depend on true value?

4. **Measurement of Outcome**
   - Was outcome measurement appropriate?
   - Did measurement differ between groups?
   - Were assessors aware of intervention?

5. **Selection of Reported Result**
   - Was outcome pre-specified?
   - Were all planned outcomes reported?
   - Evidence of selective reporting?

Each domain rated: **Low risk | Some concerns | High risk**

#### 2. GRADE Quality Assessment

Evaluates evidence quality on 4 levels: **HIGH | MODERATE | LOW | VERY LOW**

**Starting Point:**
- RCTs start at HIGH
- Observational studies start at LOW

**Downgrade for:**
- Risk of bias (serious -1, very serious -2)
- Inconsistency across studies (-1 or -2)
- Indirectness/applicability (-1 or -2)
- Imprecision/wide confidence intervals (-1 or -2)
- Publication bias (-1)

**Upgrade for (observational only):**
- Large magnitude of effect (+1 or +2)
- Dose-response gradient (+1)
- All plausible confounding would reduce effect (+1)

#### 3. Study Design Hierarchy

Classifies studies by evidence level:

| Level | Design Type | Description |
|-------|------------|-------------|
| 1 | Systematic Review/Meta-Analysis | Highest quality evidence |
| 2 | Randomized Controlled Trial (RCT) | Gold standard for interventions |
| 3 | Cohort Study | Follow groups over time |
| 4 | Case-Control Study | Compare cases to controls |
| 5 | Cross-Sectional Study | Snapshot in time |
| 6 | Case Series | Multiple case descriptions |
| 7 | Case Report | Single case description |
| 8 | Expert Opinion | Lowest quality evidence |

#### 4. Retraction Checking

Checks multiple sources for retractions:
- PubMed retraction notices
- RetractionWatch database (when available)
- Publisher retraction notices

#### 5. Citation Analysis

Fetches citation counts from:
- OpenCitations (free API)
- Crossref (free API)
- Semantic Scholar (optional)

### Usage

```python
from app.agents.specialized.credibility_agent_v2 import CredibilityAgentV2

agent = CredibilityAgentV2(config)

result = await agent.process({
    "studies": included_studies,
    "require_peer_review": True,  # Filter out preprints
    "minimum_credibility": "medium",  # Filter low-quality studies
    "check_retractions": True,
    "fetch_citations": False,  # Set True to enable citation checking
})

# Access results
for study in result['studies']:
    cred = study['credibility']
    print(f"\n{study['title']}")
    print(f"  Credibility: {cred['level'].upper()} ({cred['color']})")
    print(f"  Quality Score: {cred['quality_score']}/100")
    print(f"  Study Design: {cred['study_design']}")
    print(f"  Evidence Level: {cred['evidence_level']}")
    print(f"  Risk of Bias: {cred['risk_of_bias_overall']}")
    print(f"  GRADE: {cred['grade_quality']}")
    print(f"  Peer-reviewed: {cred['is_peer_reviewed']}")

    if cred['is_retracted']:
        print(f"  ⚠️ RETRACTED: {cred['retraction_info']}")
```

### Output Structure

```python
{
    "studies": [
        {
            ...study_data...,
            "credibility": {
                "level": "high",  # CredibilityLevel enum
                "quality_score": 85,  # 0-100
                "study_design": "Randomized Controlled Trial (RCT)",
                "evidence_level": 2,
                "risk_of_bias_overall": "Low",
                "risk_of_bias_details": "Randomization: Low | Deviations: Low | ...",
                "grade_quality": "HIGH",
                "grade_justification": "Well-designed RCT with no serious concerns",
                "sample_size": "Adequate",
                "power_analysis": "Present, adequate (>80% power)",
                "methodological_strengths": [
                    "Randomization with concealment",
                    "Double-blind design",
                    "Intent-to-treat analysis",
                    "Complete outcome data"
                ],
                "methodological_limitations": [
                    "Single-center study",
                    "Limited generalizability"
                ],
                "replicability": "High",
                "inclusion_recommendation": "Recommend include",
                "reasoning": "Excellent quality RCT...",
                "is_peer_reviewed": True,
                "is_preprint": False,
                "is_retracted": False,
                "retraction_info": "",
                "citation_count": 42,
                "database_source": "PubMed",
                "color": "green"
            }
        },
        ...
    ],
    "total_evaluated": 30,
    "credibility_breakdown": {
        "high": 15,
        "medium": 10,
        "low": 5,
        "very_low": 0
    },
    "design_breakdown": {
        "Randomized Controlled Trial (RCT)": 20,
        "Cohort Study": 8,
        "Case-Control Study": 2
    },
    "grade_breakdown": {
        "HIGH": 15,
        "MODERATE": 10,
        "LOW": 5,
        "VERY LOW": 0
    },
    "peer_reviewed_only": True,
    "minimum_credibility_threshold": "medium",
    "decision": {...}
}
```

---

## Configuration

See `backend/app/config/agent_config.yaml` for comprehensive configuration options.

### Quick Start Presets

#### 1. Fast Search (Exploratory)
```yaml
search_agent:
  default_databases: [pubmed]
  max_results_per_database: 50
screening_agent:
  thresholds.confidence_threshold: 0.6
credibility_agent:
  filtering.minimum_credibility: "low"
```

#### 2. Comprehensive Search (Systematic Review)
```yaml
search_agent:
  default_databases: [pubmed, europepmc, core]
  max_results_per_database: 200
  expand_synonyms: true
screening_agent:
  thresholds.confidence_threshold: 0.8
  inter_rater.enable_conflict_resolution: true
credibility_agent:
  assessment_frameworks.cochrane_rob.enabled: true
  filtering.minimum_credibility: "medium"
```

#### 3. High Quality Only (Meta-Analysis)
```yaml
search_agent:
  publication_types: ["Randomized Controlled Trial"]
screening_agent:
  thresholds.confidence_threshold: 0.85
credibility_agent:
  peer_review.require_peer_reviewed: true
  filtering.minimum_credibility: "high"
```

---

## Usage Examples

### Complete Workflow Example

```python
from app.agents.specialized.search_agent_v2 import SearchAgentV2
from app.agents.specialized.screening_agent_v2 import ScreeningAgentV2
from app.agents.specialized.credibility_agent_v2 import CredibilityAgentV2
from app.agents.base import AgentConfig, AgentRole

# 1. SEARCH
search_agent = SearchAgentV2(AgentConfig(name="Search", role=AgentRole.SEARCH))

search_results = await search_agent.process({
    "research_question": "What is the effect of dietary intervention on type 2 diabetes?",
    "search_terms": ["type 2 diabetes", "dietary intervention", "HbA1c"],
    "databases": ["pubmed", "europepmc"],
    "expand_synonyms": True,
    "publication_types": ["Randomized Controlled Trial"],
})

print(f"✓ Found {search_results['unique_results']} unique studies")

# 2. SCREENING
screening_agent = ScreeningAgentV2(AgentConfig(name="Screening", role=AgentRole.SCREENING))

screening_results = await screening_agent.process({
    "studies": search_results['studies'],
    "inclusion_criteria": [
        "Randomized controlled trials",
        "Adults with type 2 diabetes",
        "Dietary intervention",
        "HbA1c outcome measured"
    ],
    "exclusion_criteria": [
        "Type 1 diabetes",
        "Pediatric population",
        "Animal studies"
    ],
    "screening_level": "abstract",
    "use_ml_scoring": True,
})

print(f"✓ Included {len(screening_results['included'])} studies")
print(f"✓ Excluded {len(screening_results['excluded'])} studies")
print(f"✓ Uncertain {len(screening_results['uncertain'])} studies (need human review)")

# 3. QUALITY ASSESSMENT
credibility_agent = CredibilityAgentV2(AgentConfig(name="Quality", role=AgentRole.QUALITY_ASSESSMENT))

quality_results = await credibility_agent.process({
    "studies": screening_results['included'],
    "require_peer_review": True,
    "minimum_credibility": "medium",
    "check_retractions": True,
})

print(f"✓ High quality: {quality_results['credibility_breakdown']['high']} studies")
print(f"✓ Medium quality: {quality_results['credibility_breakdown']['medium']} studies")

# 4. GENERATE REPORT
high_quality_studies = [
    s for s in quality_results['studies']
    if s['credibility']['level'] == 'high'
]

print(f"\n=== FINAL STUDIES FOR META-ANALYSIS ===")
print(f"Total: {len(high_quality_studies)} high-quality RCTs")
for study in high_quality_studies:
    print(f"- {study['title']}")
    print(f"  Quality: {study['credibility']['quality_score']}/100")
    print(f"  GRADE: {study['credibility']['grade_quality']}")
```

---

## Algorithm Details

### TF-IDF Relevance Scoring

**Term Frequency-Inverse Document Frequency** (TF-IDF) measures term importance:

```
TF-IDF(term, document) = TF(term, document) × IDF(term)

where:
TF(term, doc) = (Number of times term appears in doc) / (Total terms in doc)
IDF(term) = log(Total documents / Documents containing term)
```

**Cosine Similarity** measures document similarity:

```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)

where A and B are TF-IDF vectors
```

### Title Similarity (Jaccard Index)

```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|

Example:
Title 1: "the effect of treatment on diabetes"
Title 2: "the effect of treatment on diabetic patients"

Words in common: {the, effect, of, treatment, on} = 5
Total unique words: {the, effect, of, treatment, on, diabetes, diabetic, patients} = 8

Jaccard = 5/8 = 0.625 (62.5% similar)
```

### Cohen's Kappa

Measures inter-rater agreement beyond chance:

```
κ = (p_o - p_e) / (1 - p_e)

where:
p_o = observed agreement
p_e = expected agreement by chance

Interpretation:
< 0.00: Poor
0.00-0.20: Slight
0.21-0.40: Fair
0.41-0.60: Moderate
0.61-0.80: Substantial
0.81-1.00: Almost perfect
```

---

## Performance Considerations

### API Rate Limits

| Database | Rate Limit | Retry Strategy |
|----------|-----------|----------------|
| PubMed E-utilities | 3 req/s | Exponential backoff |
| Europe PMC | 10 req/s | Exponential backoff |
| arXiv | 10 req/s | Exponential backoff |
| CORE | 10 req/s | Exponential backoff |

### Caching Strategy

- **Search results**: Cached for 1 hour
- **Retraction status**: Cached indefinitely (rarely changes)
- **Cache invalidation**: Automatic after TTL expires

### Parallel Processing

- **Screening**: Processes studies in batches of 10 concurrently
- **Credibility assessment**: Sequential to avoid API rate limits
- **Search**: Sequential per database, parallel across databases

### Cost Optimization

**API Calls per Workflow (estimated):**

| Step | Claude API Calls | External API Calls |
|------|------------------|-------------------|
| Search (100 studies) | 1-2 | 4-8 (database APIs) |
| Screening (100 studies) | 100-110 | 0 |
| Quality Assessment (30 studies) | 30-35 | 30-60 (retraction/citations) |
| **Total** | **~150** | **~70** |

**Tips to reduce costs:**
1. Enable aggressive caching
2. Use smaller batches for exploratory searches
3. Filter aggressively during screening
4. Disable citation fetching unless needed

---

## Troubleshooting

### Common Issues

**1. PubMed API Errors**
```
Error: HTTP 429 Too Many Requests
Solution: Rate limiting is too aggressive. Adjust rate_limits.pubmed in config.
```

**2. Empty Search Results**
```
Issue: No results found despite broad query
Solution: Check if terms are too specific. Try expand_synonyms: true
```

**3. Low Screening Confidence**
```
Issue: Many studies classified as "uncertain"
Solution: Adjust confidence_threshold (lower = fewer uncertain cases)
```

**4. Retraction Checking Timeout**
```
Issue: Retraction checking takes too long
Solution: Disable or reduce check_retractions: false in config
```

### Debug Mode

Enable detailed logging in configuration:

```yaml
general:
  logging:
    level: "DEBUG"
    log_ai_prompts: true
    log_ai_responses: true
```

---

## Best Practices

### 1. Search Strategy

- Start with core concepts, then expand
- Use MeSH terms for medical topics
- Test queries on small result sets first
- Document all search strings for reproducibility

### 2. Screening

- Always use multi-stage screening (title → abstract → full-text)
- Review uncertain cases manually
- Calculate inter-rater agreement on sample
- Target Cohen's kappa > 0.8

### 3. Quality Assessment

- Use Cochrane RoB for all RCTs
- Apply GRADE to determine evidence certainty
- Check for retractions before inclusion
- Document quality assessment decisions

### 4. Reporting

Follow **PRISMA guidelines** for systematic reviews:
- Document search strategy
- Report flow diagram
- List reasons for exclusion
- Assess risk of bias
- Grade evidence quality

---

## References

1. **PRISMA**: Page MJ, et al. The PRISMA 2020 statement. BMJ 2021;372:n71.
2. **Cochrane RoB 2.0**: Sterne JAC, et al. RoB 2: a revised tool for assessing risk of bias in randomised trials. BMJ 2019;366:l4898.
3. **GRADE**: Guyatt GH, et al. GRADE: an emerging consensus on rating quality of evidence. BMJ 2008;336:924-6.
4. **Cohen's Kappa**: Cohen J. A coefficient of agreement for nominal scales. Educational and Psychological Measurement 1960;20(1):37-46.

---

## Support

For issues, questions, or feature requests:
- GitHub Issues: [Create an issue](https://github.com/yourusername/meta-analysis-tool/issues)
- Documentation: See `/backend/docs/`
- Configuration: See `/backend/app/config/agent_config.yaml`
