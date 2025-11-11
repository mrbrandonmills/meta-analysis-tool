# Researcher Enrichment Quick Start Guide

## Installation

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Set environment variables** (`.env`):
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

3. **Run migrations** (if needed):
```bash
alembic upgrade head
```

4. **Start the API**:
```bash
uvicorn app.main:app --reload
```

## Quick Test

### 1. Create a Test Researcher

```bash
curl -X POST "http://localhost:8000/api/v1/researchers" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Researcher",
    "email": "test@university.edu",
    "institution": "Test University",
    "orcid": "0000-0002-1234-5678"
  }'
```

**Response** will include the new researcher ID.

### 2. Check Initial Completeness

```bash
curl -X GET "http://localhost:8000/api/v1/researchers/RESEARCHER_ID/completeness" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected**: ~30% completeness (only basic fields filled)

### 3. Enrich the Profile

```bash
curl -X POST "http://localhost:8000/api/v1/researchers/RESEARCHER_ID/enrich" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force_refresh": true}'
```

**Wait**: 30-60 seconds for enrichment to complete.

**Response** will show:
- Sources checked (Google Scholar, ORCID, Semantic Scholar)
- Data found from each source
- New completeness score (should be 70-90%)

### 4. Verify Results

```bash
curl -X GET "http://localhost:8000/api/v1/researchers/RESEARCHER_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Check**:
- `h_index` populated
- `total_citations` updated
- `expertise_keywords` added
- `research_domains` populated
- `researcher_metadata.publications` filled

## Common Use Cases

### Use Case 1: Import Researchers from Journal

```python
# After importing researchers from manuscript submissions
from app.services.researcher_profile_enricher import create_enricher

enricher = create_enricher()
for researcher_id in new_researchers:
    await enricher.enrich_researcher_profile(researcher_id, db)
await enricher.close()
```

### Use Case 2: Batch Update All Researchers

```bash
# Get all researcher IDs
curl -X GET "http://localhost:8000/api/v1/researchers" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Batch enrich (max 50 at a time)
curl -X POST "http://localhost:8000/api/v1/researchers/batch-enrich" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "researcher_ids": ["id1", "id2", "id3"],
    "force_refresh": false
  }'
```

### Use Case 3: Show User Profile Completeness

```javascript
// Frontend: Display profile completeness widget
const response = await fetch(`/api/v1/researchers/${userId}/completeness`, {
  headers: { 'Authorization': `Bearer ${token}` }
});

const data = await response.json();

console.log(`Profile is ${data.completeness_percentage} complete`);
console.log('Missing fields:', data.missing_fields);
console.log('Recommendations:', data.recommendations);
```

### Use Case 4: Check if Researcher is Ready for Matching

```python
from app.services.researcher_profile_enricher import create_enricher

enricher = create_enricher()
completeness = await enricher.calculate_profile_completeness(researcher)

if completeness >= 0.8:
    # Researcher is ready for reviewer matching
    print("✓ Profile complete enough for matching")
else:
    print(f"✗ Profile only {completeness*100:.1f}% complete")
    print("Please run enrichment to improve completeness")
```

## Troubleshooting

### Problem: "Researcher not found" error

**Solution**: Verify researcher ID is correct UUID format

```bash
# List all researchers
curl -X GET "http://localhost:8000/api/v1/researchers" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Problem: Google Scholar returns no data

**Solution**:
1. Check if researcher has Google Scholar profile
2. Try searching manually: https://scholar.google.com
3. Use ORCID or Semantic Scholar as alternative

### Problem: Rate limit errors (429)

**Solution**:
1. Wait 60 seconds and retry
2. Use batch processing instead of individual calls
3. The system should handle rate limiting automatically

### Problem: ORCID 404 error

**Solution**:
1. Verify ORCID ID format: `0000-0002-1234-5678`
2. Check if profile is public: https://orcid.org/ORCID-ID
3. Remove ORCID from researcher if invalid

### Problem: Enrichment takes too long

**Expected**: 30-60 seconds per researcher

**If slower**:
1. Check API response times
2. Look for network issues
3. Review logs for errors

## Running Tests

```bash
cd backend

# Set environment variables
export TOKEN="your_jwt_token_here"
export TEST_RESEARCHER_ID="researcher_uuid"

# Run test suite
./test_researcher_enricher.sh

# Run specific test
./test_researcher_enricher.sh --help
```

## Monitoring

### Check Enrichment Status

```python
# In researcher_metadata JSONB field:
{
  "last_enrichment": "2025-11-11T10:30:00Z",
  "enrichment_summary": {
    "sources_checked": ["google_scholar", "orcid"],
    "completeness_score": 0.85,
    "errors": []
  }
}
```

### Key Metrics to Monitor

1. **Completeness Distribution**:
   - How many researchers have >80% completeness?
   - What's the average completeness score?

2. **Enrichment Success Rate**:
   - % of successful enrichments
   - Common failure sources

3. **API Performance**:
   - Average enrichment time
   - Rate limit hit frequency

## Next Steps

1. **Set up scheduled enrichment**: Refresh profiles monthly
2. **Integrate with signup flow**: Enrich on user registration
3. **Add to manuscript import**: Auto-enrich imported authors
4. **Monitor completeness**: Track improvement over time

## API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/researchers/{id}/enrich` | POST | Enrich single researcher |
| `/api/v1/researchers/batch-enrich` | POST | Batch enrich multiple |
| `/api/v1/researchers/{id}/completeness` | GET | Get completeness score |

Full documentation: http://localhost:8000/docs (tag: researcher-enrichment)

## Support

- **Documentation**: `RESEARCHER_ENRICHMENT.md`
- **API Docs**: http://localhost:8000/docs
- **Test Script**: `test_researcher_enricher.sh`
