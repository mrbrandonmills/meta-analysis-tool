# Researcher Profile Enrichment System

## Overview

The Researcher Profile Enrichment system automatically enriches researcher profiles by scraping and aggregating data from multiple academic sources including Google Scholar, ORCID, and Semantic Scholar. It uses Claude AI to analyze publications and extract research domains and keywords.

## Architecture

### Components

1. **ResearcherProfileEnricher** (`app/services/researcher_profile_enricher.py`)
   - Main service class that orchestrates enrichment
   - Handles rate limiting and error recovery
   - Integrates with multiple data sources

2. **API Endpoints** (`app/api/v1/researcher_enrichment.py`)
   - POST `/api/v1/researchers/{id}/enrich` - Enrich single researcher
   - POST `/api/v1/researchers/batch-enrich` - Batch enrichment
   - GET `/api/v1/researchers/{id}/completeness` - Get profile completeness

3. **Data Sources**
   - **Google Scholar**: H-index, citations, publications, interests
   - **ORCID**: Employment, education, verified publications
   - **Semantic Scholar**: Fields of study, co-authors, abstracts
   - **Claude AI**: Domain/keyword extraction from publications

## Data Sources Integration

### Google Scholar (via `scholarly` library)

**Rate Limits**: 10 requests per minute

**Data Extracted**:
- Scholar ID
- H-index and i10-index
- Total citation count
- Research interests
- Recent publications (up to 20)
- Homepage URL

**Example**:
```python
enricher = create_enricher()
data = await enricher.search_google_scholar(
    name="Jane Smith",
    institution="Stanford University"
)
```

### ORCID API

**Rate Limits**: 24 requests per minute (public API)

**Data Extracted**:
- Verified name and biography
- Research keywords
- Employment history (past 5 positions)
- Education history (past 5 degrees)
- Publications with metadata
- External identifiers

**Requirements**:
- ORCID ID must be provided in researcher record
- Format: `0000-0002-1234-5678`

**Example**:
```python
data = await enricher.fetch_orcid_profile("0000-0002-1234-5678")
```

### Semantic Scholar API

**Rate Limits**: 100 requests per 5 minutes

**Data Extracted**:
- Author ID
- Paper count and citation count
- H-index
- Publications with citation counts
- Fields of study
- Affiliations

**Example**:
```python
data = await enricher.search_semantic_scholar(
    name="Jane Smith",
    institution="Stanford University"
)
```

### Claude AI Analysis

**Purpose**: Analyze publication titles/abstracts to extract:
- Primary research domains
- Specific keywords and topics
- Research methodology types

**Model Used**: `claude-3-haiku-20240307` (fast and cost-effective)

**Example**:
```python
publications = [
    {"title": "fMRI Study of Cognitive Load", "year": 2023},
    {"title": "Neural Correlates of Memory", "year": 2022}
]
analysis = await enricher.analyze_publications(publications)
# Returns: {"domains": [...], "keywords": [...], "methodology": [...]}
```

## Profile Completeness Scoring

The completeness score ranges from 0.0 to 1.0 (0% to 100%) based on:

| Field | Weight | Description |
|-------|--------|-------------|
| Name | 10% | Required for signup |
| Email | 10% | Required for signup |
| Institution | 10% | Required for signup |
| H-index | 15% | Academic impact metric |
| Research domains | 15% | Primary research areas |
| Keywords | 15% | Specific expertise topics |
| Publications | 10% | Publication list |
| ORCID ID | 5% | Verified identifier |
| Citation count | 5% | Academic impact |
| Co-author network | 5% | Collaboration data |

**Goal**: Achieve ≥80% completeness for effective reviewer matching.

## API Usage

### 1. Enrich Single Researcher

```bash
curl -X POST "http://localhost:8000/api/v1/researchers/{researcher_id}/enrich" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force_refresh": false}'
```

**Response**:
```json
{
  "researcher_id": "123e4567-e89b-12d3-a456-426614174000",
  "researcher_name": "Jane Smith",
  "sources_checked": ["google_scholar", "orcid", "semantic_scholar"],
  "data_found": {
    "google_scholar": {
      "h_index": 25,
      "total_citations": 1500,
      "publications": [...]
    },
    "orcid": {...},
    "semantic_scholar": {...}
  },
  "errors": [],
  "completeness_score": 0.85,
  "completeness_percentage": "85.0%",
  "status": "success"
}
```

### 2. Batch Enrichment

```bash
curl -X POST "http://localhost:8000/api/v1/researchers/batch-enrich" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "researcher_ids": ["id1", "id2", "id3"],
    "force_refresh": false
  }'
```

**Response**:
```json
{
  "total_requested": 3,
  "successful": 2,
  "failed": 1,
  "results": [...]
}
```

### 3. Get Profile Completeness

```bash
curl -X GET "http://localhost:8000/api/v1/researchers/{researcher_id}/completeness" \
  -H "Authorization: Bearer $TOKEN"
```

**Response**:
```json
{
  "researcher_id": "123e4567-e89b-12d3-a456-426614174000",
  "researcher_name": "Jane Smith",
  "completeness_score": 0.65,
  "completeness_percentage": "65.0%",
  "missing_fields": ["h_index", "publications", "orcid"],
  "recommendations": [
    "Run profile enrichment to automatically populate missing fields",
    "Add your ORCID ID for better data integration",
    "Run profile enrichment to fetch your h-index from Google Scholar"
  ]
}
```

## Rate Limiting

The enricher implements intelligent rate limiting for each API:

```python
# Google Scholar: 10 requests/minute
self.google_scholar_limiter = RateLimiter(max_requests=10, time_window=60)

# Semantic Scholar: 100 requests/5 minutes
self.semantic_scholar_limiter = RateLimiter(max_requests=100, time_window=300)

# ORCID: 24 requests/minute
self.orcid_limiter = RateLimiter(max_requests=24, time_window=60)
```

The rate limiter:
- Tracks request timestamps
- Automatically waits when limits are reached
- Prevents API blocks and 429 errors
- Implements exponential backoff for failures

## Error Handling

### Google Scholar Errors

**Issue**: Rate limiting, CAPTCHA challenges

**Solution**:
```python
try:
    data = await enricher.search_google_scholar(name, institution)
except Exception as e:
    logger.error(f"Google Scholar failed: {e}")
    # Continue with other sources
```

### ORCID API Errors

**Issue**: Invalid ORCID ID, 404 not found

**Solution**:
```python
if response.status_code == 404:
    logger.warning(f"ORCID profile not found: {orcid_id}")
    return None  # Skip, mark as incomplete
```

### Claude AI Errors

**Issue**: API errors, JSON parsing failures

**Solution**:
```python
try:
    analysis = await enricher.analyze_publications(publications)
except Exception as e:
    logger.error(f"AI analysis failed: {e}")
    # Use fallback: extract keywords from titles only
```

## Data Storage

Enriched data is stored in the `researchers` table:

```python
# Core metrics
researcher.h_index = 25
researcher.i10_index = 40
researcher.total_citations = 1500
researcher.publication_count = 45

# Arrays
researcher.expertise_keywords = ["fMRI", "cognitive load", "memory"]
researcher.research_domains = ["Neuroscience", "Psychology"]

# External IDs
researcher.google_scholar_id = "abc123"
researcher.semantic_scholar_id = "456789"

# JSONB metadata
researcher.researcher_metadata = {
    "publications": [...],
    "employment_history": [...],
    "education_history": [...],
    "last_enrichment": "2025-11-11T10:30:00Z",
    "enrichment_summary": {...}
}
```

## Caching Strategy

**Current**: Data stored in database, updated on enrichment

**Metadata tracking**:
```python
researcher.researcher_metadata["last_enrichment"] = "2025-11-11T10:30:00Z"
```

**Future Enhancement**: Implement Redis caching for 24-hour TTL to reduce API calls.

## Testing

### Run Test Suite

```bash
cd backend

# Set environment variables
export TOKEN="your_jwt_token_here"
export TEST_RESEARCHER_ID="researcher_uuid"

# Run tests
./test_researcher_enricher.sh
```

### Manual Testing

1. **Create test researcher**:
```bash
curl -X POST "http://localhost:8000/api/v1/researchers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@stanford.edu",
    "institution": "Stanford University",
    "orcid": "0000-0002-1234-5678"
  }'
```

2. **Enrich profile**:
```bash
curl -X POST "http://localhost:8000/api/v1/researchers/{id}/enrich" \
  -H "Authorization: Bearer $TOKEN"
```

3. **Check completeness**:
```bash
curl -X GET "http://localhost:8000/api/v1/researchers/{id}/completeness" \
  -H "Authorization: Bearer $TOKEN"
```

## Best Practices

### 1. Respect Rate Limits

- Use batch enrichment for multiple researchers
- Avoid enriching same researcher repeatedly
- Check `last_enrichment` timestamp before re-enriching

### 2. Handle Partial Failures

- Enrichment may succeed for some sources but fail for others
- Check `status` field: "success", "partial", or "failed"
- Review `errors` array for troubleshooting

### 3. ORCID Integration

- Encourage users to add ORCID ID during signup
- ORCID provides most reliable data
- Validate ORCID format: `0000-0002-1234-5678`

### 4. Background Processing

For large batches, use background tasks:

```python
from fastapi import BackgroundTasks

@router.post("/researchers/batch-enrich-async")
async def batch_enrich_async(
    background_tasks: BackgroundTasks,
    request: BatchEnrichmentRequest
):
    background_tasks.add_task(process_batch_enrichment, request)
    return {"status": "queued", "message": "Enrichment started"}
```

### 5. Monitoring

Log key metrics:
- Success/failure rates per source
- Average enrichment time
- Completeness score distribution
- Rate limit hit frequency

## Dependencies

Required packages in `requirements.txt`:

```
scholarly==1.7.11       # Google Scholar scraper
httpx==0.27.0           # Async HTTP client
beautifulsoup4==4.12.3  # HTML parsing (if needed)
anthropic==0.18.1       # Claude AI integration
```

## Security Considerations

### User-Agent String

Always use descriptive User-Agent:
```python
"User-Agent": "Meta-Analysis-Platform/1.0 (Contact: research@meta-analysis.com)"
```

### robots.txt Compliance

The enricher respects:
- Rate limits from each platform
- Terms of Service
- API usage policies

### Data Privacy

- Only public academic data is scraped
- No personal information beyond publicly available profiles
- ORCID data requires public profile setting

## Troubleshooting

### Issue: Google Scholar Not Finding Researcher

**Cause**: Name mismatch, common name, no profile

**Solution**:
1. Try with institution parameter for better matching
2. Check if researcher has Google Scholar profile
3. Use ORCID or Semantic Scholar as fallback

### Issue: ORCID Returns 404

**Cause**: Invalid ORCID ID, private profile

**Solution**:
1. Verify ORCID format: `0000-0002-1234-5678`
2. Check if ORCID profile is public
3. Skip ORCID enrichment if unavailable

### Issue: Rate Limit Errors

**Cause**: Too many requests in short time

**Solution**:
1. Rate limiter should handle automatically
2. Increase wait time if needed
3. Use batch processing for multiple researchers

### Issue: Claude AI Parsing Failures

**Cause**: JSON format errors in response

**Solution**:
1. Improved JSON extraction from markdown
2. Fallback to simple keyword extraction
3. Log raw response for debugging

## Performance

### Typical Enrichment Times

- **Google Scholar**: 2-5 seconds
- **ORCID**: 1-2 seconds
- **Semantic Scholar**: 1-2 seconds
- **Claude AI**: 2-3 seconds
- **Total**: 6-12 seconds per researcher

### Optimization Tips

1. **Parallel API calls** (future):
   ```python
   results = await asyncio.gather(
       search_google_scholar(name),
       fetch_orcid_profile(orcid),
       search_semantic_scholar(name)
   )
   ```

2. **Cache results**: Store in Redis for 24 hours

3. **Selective enrichment**: Only fetch missing fields

4. **Batch processing**: Process multiple researchers sequentially to respect rate limits

## Future Enhancements

1. **Redis Caching**
   - 24-hour TTL for enrichment data
   - Reduce API calls
   - Faster response times

2. **Incremental Updates**
   - Only update changed fields
   - Track last update per source
   - Reduce unnecessary API calls

3. **Co-author Network**
   - Extract from publications
   - Build researcher relationships
   - Improve reviewer matching

4. **Publication Full-Text**
   - Fetch abstracts from APIs
   - Better AI analysis
   - More accurate domain extraction

5. **Scheduled Refresh**
   - Periodic background enrichment
   - Keep profiles up-to-date
   - Automated quality maintenance

## API Documentation

Full API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Filter by tag: `researcher-enrichment`

## Support

For issues or questions:
1. Check logs: `backend/logs/`
2. Review error messages in API responses
3. Test with single researcher before batch
4. Verify API keys and authentication tokens
