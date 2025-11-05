# Search Agent API Usage Guide

Quick reference for developers working with the search agent API integration.

---

## Quick Start

### Basic Usage

```python
from app.agents.specialized.search import SearchAgent
from app.agents.base import AgentConfig, AgentRole

# Create search agent
agent = SearchAgent(AgentConfig(
    role=AgentRole.SEARCH,
    name="Literature Search Agent"
))

# Perform search
results = await agent.process({
    "research_question": "What are the effects of exercise on depression?",
    "search_terms": ["exercise", "depression", "randomized controlled trial"],
    "databases": ["pubmed", "arxiv", "europepmc", "core"],
    "date_range": {
        "start_year": 2020,
        "end_year": 2025
    }
})

# Results structure
print(f"Found {results['total_results']} unique studies")
for study in results['studies']:
    print(f"{study['title']} ({study['year']})")
```

### Using Enhanced Version (Recommended)

```python
from app.agents.specialized.search_enhanced import SearchAgentEnhanced

# Create enhanced agent with rate limiting, caching, retry logic
agent = SearchAgentEnhanced(AgentConfig(
    role=AgentRole.SEARCH,
    name="Enhanced Search Agent"
))

# Same usage as basic agent, but with:
# - Automatic rate limiting (3 req/sec for PubMed)
# - Exponential backoff retry (3 attempts)
# - 1-hour response caching
# - Full PubMed abstracts via efetch
```

---

## Database-Specific Features

### PubMed

**Best For**: Medical, biomedical, life sciences research

**Coverage**: 35+ million citations from MEDLINE and life science journals

**Search Tips**:
- Use MeSH terms for better precision: `"depressive disorder"[MeSH]`
- Boolean operators: `"exercise" AND "depression"`
- Field tags: `"Smith"[Author]`, `"2024"[Publication Date]`

**Data Fields Returned**:
```python
{
    "id": "PMID:41191391",
    "pmid": "41191391",
    "title": "Study title",
    "abstract": "Full abstract text (if using enhanced version)",
    "authors": ["Smith J", "Doe J"],
    "journal": "Nature Medicine",
    "year": "2025",
    "doi": "10.1038/s41591-...",
    "keywords": ["exercise", "depression"],
    "mesh_terms": ["Exercise", "Depressive Disorder"],
    "database": "PubMed"
}
```

**Rate Limits**:
- Without API key: 3 requests/second
- With API key: 10 requests/second
- Get API key (free): https://www.ncbi.nlm.nih.gov/account/

**API Key Configuration**:
```bash
# In .env file
PUBMED_API_KEY=your_api_key_here
PUBMED_EMAIL=your.email@example.com
```

### arXiv

**Best For**: Physics, mathematics, computer science, quantitative biology preprints

**Coverage**: 2+ million preprints (not peer-reviewed)

**Search Tips**:
- Category filters: `cat:cs.AI` (AI), `cat:q-bio` (quantitative biology)
- All-field search: `all:machine learning`
- Author search: `au:Hinton`
- Title search: `ti:neural networks`

**Data Fields Returned**:
```python
{
    "id": "arXiv:2501.12345",
    "arxiv_id": "2501.12345",
    "title": "Paper title",
    "abstract": "Full abstract (always included)",
    "authors": ["John Doe", "Jane Smith"],
    "journal": "arXiv Preprint",
    "year": "2025",
    "doi": "",  # Usually empty for preprints
    "url": "http://arxiv.org/abs/2501.12345v1",
    "categories": ["cs.LG", "cs.AI"],
    "database": "arXiv"
}
```

**Note**: arXiv papers are preprints (not peer-reviewed). Use for:
- Cutting-edge research
- Pre-publication findings
- Rapid dissemination topics

### Europe PMC

**Best For**: European research, open access, broader coverage than PubMed

**Coverage**: 40+ million publications from PubMed, PMC, preprints, patents

**Search Tips**:
- Boolean operators: `"COVID-19" AND "vaccine"`
- Open access filter: `OPEN_ACCESS:y`
- Source filter: `SRC:PPR` (preprints), `SRC:PMC` (PubMed Central)

**Data Fields Returned**:
```python
{
    "id": "PMCID:PMC9876543",
    "pmc_id": "PMC9876543",
    "pmid": "38123456",  # If also in PubMed
    "title": "Study title",
    "abstract": "Abstract text (90% have abstracts)",
    "authors": ["Smith J", "Doe J", "Johnson A"],
    "journal": "Nature Medicine",
    "year": "2024",
    "doi": "10.1038/s41591-...",
    "source": "PMC",
    "database": "Europe PMC"
}
```

### CORE

**Best For**: Open access papers, institutional repositories, thesis, dissertations

**Coverage**: 200+ million open access papers from global repositories

**Search Tips**:
- Full-text search (searches entire paper, not just metadata)
- No Boolean operators needed (uses advanced ranking)
- Returns PDF download URLs when available

**Data Fields Returned**:
```python
{
    "id": "CORE:135065665",
    "title": "Paper title",
    "abstract": "Abstract (75% have abstracts)",
    "authors": ["Colin Steele"],
    "journal": "Publisher name",  # Usually publisher, not journal
    "year": "2015",
    "doi": "10.1080/...",  # 60% have DOIs
    "downloadUrl": "https://core.ac.uk/download/156622116.pdf",
    "database": "CORE"
}
```

**Unique Features**:
- PDF download links (for self-archived versions)
- Global repository coverage
- Includes grey literature (thesis, reports)

---

## Advanced Usage

### Custom Search Parameters

```python
results = await agent.process({
    "research_question": "Impact of social media on mental health in adolescents",
    "search_terms": ["social media", "mental health", "adolescents"],
    "databases": ["pubmed", "europepmc"],  # Select specific databases
    "date_range": {
        "start_year": 2018,
        "end_year": 2025
    },
    "filters": {
        "publication_types": ["randomized controlled trial", "systematic review"],
        "languages": ["eng"],
        "open_access": True
    },
    "max_results": 200  # Override default (100)
})
```

### Error Handling

```python
try:
    results = await agent.process(search_params)

    if results['total_results'] == 0:
        print("No results found. Try broader search terms.")

    # Check individual database failures
    for log in results['search_log']:
        if log['results_count'] == 0:
            print(f"{log['database']}: No results (may be API issue)")

except httpx.TimeoutException:
    print("Search timed out. Try reducing max_results or fewer databases.")

except Exception as e:
    logger.error(f"Search failed: {e}")
```

### Deduplication

The agent automatically deduplicates across databases using:
1. **DOI matching** (most reliable)
2. **PMID matching** (for PubMed/Europe PMC overlap)
3. **Title similarity** (case-insensitive, normalized)

```python
# Access deduplication stats
original_count = sum(log['results_count'] for log in results['search_log'])
unique_count = results['unique_results']
duplicates_removed = original_count - unique_count

print(f"Removed {duplicates_removed} duplicates ({duplicates_removed/original_count*100:.1f}%)")
```

### Caching (Enhanced Version Only)

```python
from app.agents.specialized.search_enhanced import SearchAgentEnhanced

agent = SearchAgentEnhanced(config)

# First search - hits API
results1 = await agent.process(params)

# Second search with same terms - uses cache (instant)
results2 = await agent.process(params)

# Cache expires after 1 hour
# Manual cache clear:
agent._cache.clear()
agent._cache_ttl.clear()
```

---

## Performance Optimization

### Parallel Database Searches

Current implementation searches sequentially. For faster results:

```python
import asyncio

async def parallel_search(search_terms, params):
    agent = SearchAgent(config)

    # Create tasks for each database
    tasks = [
        agent._search_pubmed(search_terms, params),
        agent._search_arxiv(search_terms, params),
        agent._search_europepmc(search_terms, params),
        agent._search_core(search_terms, params),
    ]

    # Execute in parallel
    results = await asyncio.gather(*tasks)

    # Combine and deduplicate
    all_results = [r for results_list in results for r in results_list]
    unique = agent._deduplicate(all_results)

    return unique
```

**Speedup**: ~4x faster (searches happen simultaneously)

### Batch Processing

For large-scale meta-analyses:

```python
async def batch_search(queries: List[Dict]):
    """Process multiple search queries in batch."""
    agent = SearchAgentEnhanced(config)  # Use enhanced for caching

    results = []
    for query in queries:
        # Rate limiting handled by enhanced agent
        result = await agent.process(query)
        results.append(result)

        # Optional: Save intermediate results
        save_checkpoint(result)

    return results

# Example usage
queries = [
    {"research_question": "Q1", "search_terms": [...]},
    {"research_question": "Q2", "search_terms": [...]},
    # ... 100 more queries
]

all_results = await batch_search(queries)
```

---

## Troubleshooting

### Common Issues

**Issue**: PubMed returns 429 (Too Many Requests)
**Solution**:
- Use enhanced version with rate limiting
- Configure API key to increase quota
- Add delays between searches: `await asyncio.sleep(1)`

**Issue**: arXiv returns 0 results
**Solution**:
- Verify HTTPS is used (not HTTP)
- Check `follow_redirects=True` in httpx client
- Test query on arXiv website first

**Issue**: Europe PMC slow response (>5 seconds)
**Solution**:
- Normal behavior for large result sets
- Reduce `max_results` parameter
- Use more specific search terms

**Issue**: CORE returns irrelevant results
**Solution**:
- CORE searches full-text (not just title/abstract)
- Use more specific/longer search terms
- Combine with other databases and filter results

**Issue**: Many duplicates across databases
**Solution**:
- Deduplication should handle this automatically
- Verify DOI/PMID fields are being extracted
- Check deduplication logic is enabled

### Debugging

Enable debug logging:

```python
from loguru import logger

logger.add("search_debug.log", level="DEBUG")

# Now all API calls, errors, retries will be logged
results = await agent.process(params)
```

View logs:
```bash
tail -f search_debug.log
```

### API Testing

Test individual APIs:

```bash
# Run comprehensive test suite
cd backend
python3 test_api_integration.py

# Test specific database
python3 -c "
import asyncio
from app.agents.specialized.search import SearchAgent
from app.agents.base import AgentConfig, AgentRole

async def test():
    agent = SearchAgent(AgentConfig(role=AgentRole.SEARCH, name='Test'))
    results = await agent._search_pubmed(['test'], {})
    print(f'Results: {len(results)}')

asyncio.run(test())
"
```

---

## API Limitations

### PubMed
- ⚠️ 3 req/sec without API key (temporary IP ban if violated)
- ⚠️ esummary doesn't include abstracts (use efetch in enhanced version)
- ⚠️ Some older papers lack DOIs
- ✅ Most reliable medical literature source

### arXiv
- ⚠️ Preprints only (not peer-reviewed)
- ⚠️ No DOIs (uses arXiv IDs instead)
- ⚠️ Limited to STEM fields
- ✅ Full abstracts always included
- ✅ Fast, reliable API

### Europe PMC
- ⚠️ Slower than PubMed (~1-2s response time)
- ⚠️ Some results lack abstracts
- ⚠️ Overlaps heavily with PubMed
- ✅ Broader coverage (preprints, patents, clinical trials)
- ✅ Open access indicators

### CORE
- ⚠️ Variable quality (depends on source repository)
- ⚠️ Full-text search can return irrelevant results
- ⚠️ Not all papers have DOIs or abstracts
- ✅ Largest open access collection
- ✅ PDF download links
- ✅ Global coverage

---

## Best Practices

### 1. Database Selection

**For medical/clinical research**:
```python
databases = ["pubmed", "europepmc"]  # PubMed + broader coverage
```

**For computer science/AI**:
```python
databases = ["arxiv", "core"]  # Preprints + open access
```

**For comprehensive systematic reviews**:
```python
databases = ["pubmed", "arxiv", "europepmc", "core"]  # All databases
```

### 2. Search Term Construction

**Use PICO framework** (Population, Intervention, Comparison, Outcome):

```python
# Good: Specific PICO terms
search_terms = ["adolescents", "cognitive behavioral therapy", "depression", "remission"]

# Bad: Too broad
search_terms = ["therapy", "mental health"]

# Bad: Too narrow
search_terms = ["adolescent females aged 13-17", "CBT delivered by licensed psychologists", ...]
```

### 3. Result Validation

```python
# Validate search quality
results = await agent.process(params)

# Check coverage across databases
for log in results['search_log']:
    print(f"{log['database']}: {log['results_count']} results")

# Flag low coverage
if results['total_results'] < 10:
    logger.warning("Low search coverage - consider broader terms")

# Flag too many results
if results['total_results'] > 1000:
    logger.warning("Too many results - consider narrower terms")
```

### 4. Documentation

Always document search strategies:

```python
search_record = {
    "date": datetime.now().isoformat(),
    "databases": results['databases_searched'],
    "search_terms": params['search_terms'],
    "filters": params.get('filters', {}),
    "results_per_database": results['search_log'],
    "total_unique": results['unique_results'],
    "deduplication_rate": f"{(1 - unique/total)*100:.1f}%"
}

# Save for reproducibility
with open("search_strategy.json", "w") as f:
    json.dump(search_record, f, indent=2)
```

---

## Migration Guide

### From Basic to Enhanced Version

**Step 1**: Change import
```python
# Old
from app.agents.specialized.search import SearchAgent

# New
from app.agents.specialized.search_enhanced import SearchAgentEnhanced as SearchAgent
```

**Step 2**: No code changes needed (same interface)

**Step 3**: Optional - configure caching
```python
agent = SearchAgentEnhanced(config)
agent._cache_duration = 7200  # 2 hours instead of 1
```

### Upgrading from Mock Data (if applicable)

If you previously had mock data:

```python
# Old (mock data)
def search_pubmed(terms):
    return MOCK_RESULTS

# New (real API)
async def search_pubmed(terms):
    agent = SearchAgent(config)
    results = await agent._search_pubmed(terms, {})
    return results
```

---

## Support and Resources

### Documentation Links
- PubMed E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- arXiv API: https://arxiv.org/help/api/user-manual
- Europe PMC API: https://europepmc.org/RestfulWebService
- CORE API: https://core.ac.uk/documentation/

### API Status Pages
- PubMed: https://www.ncbi.nlm.nih.gov/
- arXiv: https://status.arxiv.org/
- Europe PMC: https://europepmc.org/
- CORE: https://core.ac.uk/

### Getting Help
- GitHub Issues: [project-repo]/issues
- API-specific support: See documentation links above
- Internal: Contact backend team

---

**Last Updated**: November 5, 2025
**Version**: 1.0.0
**Maintained By**: Backend Development Team
