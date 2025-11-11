# ReviewerMatchingAgent - Quick Reference Card

## 🚀 Quick Start

```python
from app.agents.specialized.reviewer_matching_agent import ReviewerMatchingAgent
from app.agents.base import AgentConfig
from app.db.session import async_session

# Initialize
config = AgentConfig(name="ReviewerMatcher", role="reviewer_matching")
agent = ReviewerMatchingAgent(config=config)

# Find matches
async with async_session() as db:
    result = await agent.process({
        "manuscript_id": manuscript_id,
        "db_session": db,
        "max_results": 10,
        "min_score": 0.3,
    })
```

## 📊 Scoring Formula

```
overall_score = (
    expertise_score × 0.5 +
    availability_score × 0.3 +
    diversity_score × 0.2
) × (1 - conflict_risk)
```

### Expertise (50%)
- Keyword overlap: 70%
- Domain matching: 30%
- Uses TF-IDF + cosine similarity

### Availability (30%)
- Workload: 40%
- Response rate: 30%
- Recent activity: 20%
- Self-estimate: 10%

### Diversity (20%)
- Geographic diversity
- Institutional diversity
- Career stage diversity

### Conflicts (Penalty)
- Same institution: 0.8 risk
- Coauthor: 1.0 risk
- Recent collaboration: 0.5 risk

## 🎯 Key Methods

### Main Entry Point
```python
result = await agent.process(input_data)
# Returns: {"matches": [...], "summary": {...}, "decision": {...}}
```

### Direct Matching
```python
matches = await agent.find_matching_reviewers(
    manuscript_id=manuscript_id,
    db_session=db,
    max_results=10,
    min_score=0.3,
)
```

## 📈 Output Structure

```python
match = {
    "researcher_id": UUID,
    "researcher_name": str,
    "researcher_email": str,
    "researcher_institution": str,
    "researcher_country": str,
    "overall_score": float,      # 0.0-1.0
    "expertise_score": float,
    "availability_score": float,
    "diversity_score": float,
    "conflict_risk": float,
    "has_conflict": bool,
    "conflict_types": List[str],
    "matching_keywords": List[str],
    "matching_domains": List[str],
    "reasoning": str,            # Human-readable explanation
    "recommendation": str,        # HIGHLY_RECOMMENDED | RECOMMENDED | ACCEPTABLE | NOT_RECOMMENDED
    "confidence": float,
}
```

## 🔧 Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `manuscript_id` | UUID | **required** | Manuscript to match |
| `db_session` | AsyncSession | **required** | Database session |
| `max_results` | int | 10 | Max matches to return |
| `min_score` | float | 0.3 | Min overall score threshold |
| `diversity_weight` | float | 0.2 | Weight for diversity (0-1) |
| `require_availability` | bool | True | Filter by availability |

## 📋 Recommendation Levels

| Score Range | Conflict Risk | Recommendation |
|-------------|---------------|----------------|
| ≥ 0.7 | < 0.7 | HIGHLY_RECOMMENDED |
| 0.5-0.7 | < 0.7 | RECOMMENDED |
| 0.3-0.5 | < 0.7 | ACCEPTABLE |
| Any | ≥ 0.7 | NOT_RECOMMENDED |

## 🗄️ Database Models

### Researcher (Input)
```python
researcher.expertise_keywords: List[str]
researcher.research_domains: List[str]
researcher.current_workload: int
researcher.response_rate: float
researcher.last_review_date: date
researcher.h_index: int
researcher.institution: str
researcher.country: str
```

### ReviewerMatch (Output)
```python
Created in database with all scores, reasoning, and metadata
Status: pending → invited → accepted/declined
```

## ⚡ Performance

| Operation | Time |
|-----------|------|
| Feature extraction | ~50ms |
| Database query | ~100-200ms |
| Semantic fitting | ~200ms |
| Scoring 10 candidates | ~100-200ms |
| Save to database | ~100ms |
| **Total** | **~1-1.5s** |

## 🧪 Testing

```bash
cd /Users/brandon/meta-analysis-tool/backend
python test_reviewer_matching_agent.py
```

Creates test manuscript + 8 researchers, finds matches, shows reasoning.

## 🚨 Common Issues

### No matches found
- Check manuscript keywords are meaningful
- Lower `min_score` threshold
- Add more researchers to database

### All matches have conflicts
- Expand geographic search
- Include earlier-career researchers
- Review conflict severity

### Poor diversity
- Increase `diversity_weight` parameter
- Add international researchers
- Apply stronger diversity boost

## 📁 File Locations

```
backend/
├── app/agents/specialized/
│   └── reviewer_matching_agent.py      # 1,102 lines
├── test_reviewer_matching_agent.py     # Test suite
├── REVIEWER_MATCHING_AGENT_README.md   # Full docs
├── REVIEWER_MATCHING_SAMPLE_OUTPUT.md  # Example output
└── REVIEWER_MATCHING_QUICK_REFERENCE.md # This file
```

## 🔗 API Endpoint

```
POST /api/v1/reviewer-matcher/search
{
    "manuscript_id": "uuid",
    "max_results": 10,
    "min_score": 0.3
}
```

## 📚 Key Classes

- `SemanticMatcher`: TF-IDF + cosine similarity engine
- `ReviewerMatchingAgent`: Main agent (extends BaseAgent)
- Uses: `Manuscript`, `Researcher`, `ReviewerMatch` models

## 🎓 Algorithm Highlights

✅ Multi-factor scoring (expertise, availability, diversity)
✅ Semantic similarity matching (TF-IDF)
✅ Conflict of interest detection
✅ Geographic/institutional diversity boost
✅ Transparent reasoning generation
✅ Database integration
✅ Fast performance (~1 second)

## 💡 Pro Tips

1. **Higher diversity**: Set `diversity_weight=0.3`
2. **Stricter matching**: Set `min_score=0.5`
3. **More options**: Set `max_results=15`
4. **Fast mode**: Set `require_availability=False`
5. **Cache vectorizer**: Reuse for similar manuscripts

## 📊 Example Results

```
Top Matches:
1. Dr. Sarah Chen (UC Berkeley) - 0.847 - HIGHLY_RECOMMENDED
2. Prof. Elena Schmidt (ETH Zurich) - 0.809 - HIGHLY_RECOMMENDED
3. Dr. Lisa Wang (Johns Hopkins) - 0.782 - HIGHLY_RECOMMENDED

Summary:
- 8 matches found
- Avg score: 0.653
- 1 conflict detected
- 4 countries represented
```

---

**For detailed documentation**: See `REVIEWER_MATCHING_AGENT_README.md`
**For example output**: See `REVIEWER_MATCHING_SAMPLE_OUTPUT.md`
**For testing**: Run `python test_reviewer_matching_agent.py`
