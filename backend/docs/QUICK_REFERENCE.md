# Quick Reference Guide - Enhanced Agents V2

## At a Glance

### SearchAgentV2 - Multi-Database Academic Search

**Purpose:** Search multiple academic databases with advanced query building

**Key Features:**
- ✓ Multi-database (PubMed, arXiv, Europe PMC, CORE)
- ✓ MeSH term expansion
- ✓ Synonym detection
- ✓ Advanced deduplication (DOI, PMID, title)
- ✓ Caching & rate limiting

**Quick Start:**
```python
from app.agents.specialized import SearchAgentV2
agent = SearchAgentV2(config)
result = await agent.process({
    "research_question": "Your question here",
    "search_terms": ["term1", "term2"],
    "databases": ["pubmed", "europepmc"],
    "expand_synonyms": True,
})
```

---

### ScreeningAgentV2 - ML-Enhanced Study Screening

**Purpose:** Screen studies using ML relevance scoring and multi-stage filtering

**Key Features:**
- ✓ ML-based relevance scores (TF-IDF + cosine similarity)
- ✓ Multi-stage screening (title → abstract → full-text)
- ✓ Inter-rater agreement (Cohen's kappa)
- ✓ PRISMA flow diagrams
- ✓ Detailed justifications

**Quick Start:**
```python
from app.agents.specialized import ScreeningAgentV2
agent = ScreeningAgentV2(config)
result = await agent.process({
    "studies": your_studies,
    "inclusion_criteria": ["criterion 1", "criterion 2"],
    "exclusion_criteria": ["exclusion 1"],
    "screening_level": "abstract",
    "use_ml_scoring": True,
})
```

---

### CredibilityAgentV2 - Comprehensive Quality Assessment

**Purpose:** Evaluate study quality using Cochrane RoB, GRADE, and evidence hierarchy

**Key Features:**
- ✓ Cochrane Risk of Bias (RoB 2.0)
- ✓ GRADE quality assessment
- ✓ Study design hierarchy
- ✓ Retraction checking
- ✓ Citation analysis
- ✓ Peer review detection

**Quick Start:**
```python
from app.agents.specialized import CredibilityAgentV2
agent = CredibilityAgentV2(config)
result = await agent.process({
    "studies": included_studies,
    "require_peer_review": True,
    "minimum_credibility": "medium",
    "check_retractions": True,
})
```

---

## Common Workflows

### 1. Exploratory Search (Fast)
```python
# Search with minimal filtering
search_result = await search_agent.process({
    "research_question": "diabetes treatment",
    "search_terms": ["diabetes", "treatment"],
    "databases": ["pubmed"],
    "max_results_per_db": 50,
    "expand_synonyms": False,
})
# → Fast results for initial exploration
```

### 2. Systematic Review (Comprehensive)
```python
# Step 1: Comprehensive search
search_result = await search_agent.process({
    "research_question": "Effect of diet on diabetes",
    "search_terms": ["diabetes", "dietary intervention"],
    "databases": ["pubmed", "europepmc", "core"],
    "expand_synonyms": True,
    "use_mesh_terms": True,
    "publication_types": ["Randomized Controlled Trial"],
})

# Step 2: Two-stage screening
abstract_screening = await screening_agent.process({
    "studies": search_result['studies'],
    "inclusion_criteria": [...],
    "screening_level": "abstract",
    "confidence_threshold": 0.7,
})

full_text_screening = await screening_agent.process({
    "studies": abstract_screening['included'],
    "screening_level": "full_text",
    "confidence_threshold": 0.8,
})

# Step 3: Quality assessment
quality_result = await credibility_agent.process({
    "studies": full_text_screening['included'],
    "require_peer_review": True,
    "minimum_credibility": "medium",
    "check_retractions": True,
})
# → High-quality studies ready for meta-analysis
```

### 3. Meta-Analysis (High Quality Only)
```python
# Search only RCTs
search_result = await search_agent.process({
    "research_question": "RCT question",
    "search_terms": ["intervention", "outcome"],
    "databases": ["pubmed"],
    "publication_types": ["Randomized Controlled Trial"],
})

# Strict screening
screening_result = await screening_agent.process({
    "studies": search_result['studies'],
    "inclusion_criteria": ["RCT", "specific population", "specific outcome"],
    "confidence_threshold": 0.85,
})

# Only high-quality studies
quality_result = await credibility_agent.process({
    "studies": screening_result['included'],
    "require_peer_review": True,
    "minimum_credibility": "high",
})
# → Only the highest quality RCTs
```

---

## Configuration Cheat Sheet

### Search Agent
```yaml
search_agent:
  default_databases: [pubmed, europepmc]
  expand_synonyms: true
  use_mesh_terms: true
  max_results_per_database: 100
```

### Screening Agent
```yaml
screening_agent:
  ml_scoring.enabled: true
  thresholds.confidence_threshold: 0.7
  batch_size: 10
```

### Credibility Agent
```yaml
credibility_agent:
  peer_review.require_peer_reviewed: false
  filtering.minimum_credibility: "low"
  retraction_checking.enabled: true
```

---

## Decision Matrix

### When to use which confidence threshold?

| Threshold | Use Case | Expected Result |
|-----------|----------|----------------|
| 0.5-0.6 | Exploratory, inclusive | Many included, few uncertain |
| 0.7 | Balanced systematic review | Moderate inclusion, some uncertain |
| 0.8-0.9 | Strict meta-analysis | Conservative inclusion, minimal uncertain |

### When to require peer review?

| Requirement | Use Case |
|-------------|----------|
| `False` | Include preprints, early evidence |
| `True` | Published evidence only, meta-analysis |

### Minimum credibility levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `very_low` | Include everything | Exploratory scoping review |
| `low` | Include most studies | Comprehensive systematic review |
| `medium` | Moderate quality filter | Standard meta-analysis |
| `high` | Only highest quality | Rigorous meta-analysis of RCTs |

---

## Output Interpretation

### Screening Results
```python
result = {
    "included": [...],       # Pass all criteria
    "excluded": [...],       # Fail criteria
    "uncertain": [...],      # Need human review
    "inclusion_rate": 0.23,  # 23% included
}
```

**What to do:**
- Review `uncertain` studies manually
- Check exclusion reasons: `result['prisma_data']['exclusion_reasons']`
- Aim for inclusion_rate of 15-30% for typical systematic reviews

### Credibility Scores
```python
credibility = {
    "level": "high",         # Color: green (85-100)
    "quality_score": 85,
    "grade_quality": "HIGH",
    "risk_of_bias_overall": "Low",
}
```

**Interpretation:**
- **GREEN (HIGH)**: Excellent quality, include with confidence
- **YELLOW (MEDIUM)**: Good quality, include with minor caveats
- **ORANGE (LOW)**: Questionable quality, consider excluding
- **RED (VERY LOW)**: Poor quality, likely exclude

---

## Troubleshooting Quick Fixes

### Problem: No search results
**Fix:** Check if terms are too specific
```python
# Add expand_synonyms: True
# Reduce number of required terms
# Try broader search terms
```

### Problem: Too many uncertain screenings
**Fix:** Lower confidence threshold
```python
"confidence_threshold": 0.6  # Was 0.8
```

### Problem: All studies excluded
**Fix:** Check if criteria are too strict
```python
# Review exclusion_criteria
# Check if inclusion_criteria are realistic
```

### Problem: API rate limit errors
**Fix:** Adjust rate limits in config
```yaml
rate_limits:
  pubmed: 2.0  # Reduce from 3.0
```

---

## Performance Tips

### Speed Optimization
1. **Cache aggressively**: Results are cached for 1 hour
2. **Limit results**: Use `max_results_per_db: 50` for testing
3. **Parallel processing**: Enabled by default for screening
4. **Disable citation fetching**: Unless specifically needed

### Cost Optimization
1. **Reduce API calls**: Enable caching, use smaller batches
2. **Filter early**: Use strict search filters to reduce screening load
3. **Disable optional features**: Citation checking, retraction checking

### Quality Optimization
1. **Multi-stage screening**: Always use title → abstract → full-text
2. **Calculate kappa**: Verify inter-rater reliability
3. **Enable all quality checks**: Cochrane RoB, GRADE, retractions
4. **Document everything**: Save all decisions and reasoning

---

## Reporting Checklist

For PRISMA compliance:

- [ ] Document search strategy (databases, terms, dates)
- [ ] Report search results by database
- [ ] Create PRISMA flow diagram
- [ ] List exclusion reasons with counts
- [ ] Assess risk of bias for all included studies
- [ ] Rate evidence quality using GRADE
- [ ] Report inter-rater agreement (kappa)
- [ ] Document any deviations from protocol

---

## Getting Help

**Documentation:**
- Full guide: `/backend/docs/AGENT_ENHANCEMENTS.md`
- Configuration: `/backend/app/config/agent_config.yaml`
- Tests: `/backend/tests/unit/test_agents/`

**Common Questions:**

**Q: How do I add a new database?**
A: Extend SearchAgentV2 with a new `_search_xxx_advanced()` method

**Q: Can I customize screening criteria on the fly?**
A: Yes, pass different `inclusion_criteria` and `exclusion_criteria` each time

**Q: How do I export PRISMA diagrams?**
A: Use `result['prisma_data']` to generate flow diagrams in your frontend

**Q: What ML model is used for screening?**
A: TF-IDF vectorization with cosine similarity (scikit-learn)

**Q: Can I train a custom screening model?**
A: Yes, modify `ScreeningClassifier` class to use your trained model

---

## Example Output Snippets

### Search Result
```json
{
  "unique_results": 132,
  "duplicates_removed": 18,
  "deduplication_stats": {
    "duplicates_by_doi": 5,
    "duplicates_by_pmid": 8,
    "duplicates_by_title": 5
  }
}
```

### Screening Result
```json
{
  "total_screened": 132,
  "included": 30,
  "excluded": 82,
  "uncertain": 20,
  "inclusion_rate": 0.227
}
```

### Quality Result
```json
{
  "credibility_breakdown": {
    "high": 15,
    "medium": 10,
    "low": 5
  },
  "design_breakdown": {
    "RCT": 20,
    "Cohort": 8,
    "Case-Control": 2
  }
}
```

---

**Last Updated:** 2024-11-06
**Version:** 2.0.0
