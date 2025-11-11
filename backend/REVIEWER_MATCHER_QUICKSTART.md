# Reviewer Matcher API - Quick Start Guide

## Setup

1. Start the FastAPI server:
```bash
cd /Users/brandon/meta-analysis-tool/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quick Test Flow

### 1. Get Authentication Token

```bash
# Register (first time)
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test User"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPass123"

# Extract token from response and set:
export TOKEN="your_access_token_here"
```

### 2. Add Researchers to Database

```bash
# Add first researcher
curl -X POST "http://localhost:8000/api/v1/researchers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Jane Smith",
    "email": "jane@stanford.edu",
    "institution": "Stanford University",
    "country": "USA",
    "h_index": 45,
    "total_citations": 5000,
    "publication_count": 150,
    "expertise_keywords": ["machine learning", "deep learning", "computer vision"],
    "research_domains": ["artificial intelligence"]
  }'

# Add second researcher
curl -X POST "http://localhost:8000/api/v1/researchers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prof. John Doe",
    "email": "john@mit.edu",
    "institution": "MIT",
    "country": "USA",
    "h_index": 60,
    "total_citations": 8000,
    "publication_count": 200,
    "expertise_keywords": ["deep learning", "neural networks", "nlp"],
    "research_domains": ["artificial intelligence", "natural language processing"]
  }'

# Add third researcher (international)
curl -X POST "http://localhost:8000/api/v1/researchers" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Maria Garcia",
    "email": "maria@barcelona.edu",
    "institution": "University of Barcelona",
    "country": "Spain",
    "h_index": 35,
    "total_citations": 3500,
    "publication_count": 100,
    "expertise_keywords": ["computer vision", "medical imaging", "deep learning"],
    "research_domains": ["artificial intelligence", "healthcare"]
  }'
```

### 3. Search Researchers

```bash
# Search by keyword
curl -X GET "http://localhost:8000/api/v1/researchers?keyword=deep%20learning&min_h_index=30" \
  -H "Authorization: Bearer $TOKEN"

# Filter by institution
curl -X GET "http://localhost:8000/api/v1/researchers?institution=stanford" \
  -H "Authorization: Bearer $TOKEN"

# Filter by country
curl -X GET "http://localhost:8000/api/v1/researchers?country=USA&sort_by=citations" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Create a Manuscript

```bash
curl -X POST "http://localhost:8000/api/v1/manuscripts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Deep Learning for Medical Image Segmentation",
    "abstract": "This paper presents a novel approach...",
    "keywords": ["deep learning", "medical imaging", "segmentation"],
    "manuscript_type": "research_article"
  }'

# Save the manuscript ID from response
export MANUSCRIPT_ID="manuscript-uuid-here"
```

### 5. Find Matching Reviewers

```bash
curl -X POST "http://localhost:8000/api/v1/reviewer-matches/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"manuscript_id\": \"$MANUSCRIPT_ID\",
    \"required_expertise\": [\"deep learning\", \"medical imaging\"],
    \"research_domains\": [\"artificial intelligence\"],
    \"min_h_index\": 20,
    \"min_citations\": 1000,
    \"max_current_workload\": 5,
    \"diversity_preference\": 0.3,
    \"max_results\": 10
  }"

# Save the match ID from response
export MATCH_ID="match-uuid-here"
```

### 6. Send Invitation

```bash
curl -X POST "http://localhost:8000/api/v1/reviewer-matches/invite" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"match_id\": \"$MATCH_ID\",
    \"custom_message\": \"We invite you to review this manuscript on medical imaging.\",
    \"deadline_days\": 14
  }"
```

### 7. Update Match Status

```bash
# Reviewer accepts
curl -X PUT "http://localhost:8000/api/v1/reviewer-matches/$MATCH_ID/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "accepted",
    "notes": "Reviewer accepted the invitation"
  }'
```

### 8. View All Matches for Manuscript

```bash
curl -X GET "http://localhost:8000/api/v1/manuscripts/$MANUSCRIPT_ID/matches" \
  -H "Authorization: Bearer $TOKEN"

# Filter by status
curl -X GET "http://localhost:8000/api/v1/manuscripts/$MANUSCRIPT_ID/matches?status_filter=accepted" \
  -H "Authorization: Bearer $TOKEN"
```

## Common Operations

### Update Researcher Metrics

```bash
curl -X PUT "http://localhost:8000/api/v1/researchers/{researcher_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "h_index": 50,
    "total_citations": 6000,
    "current_workload": 2,
    "response_rate": 0.9
  }'
```

### Get Researcher Profile

```bash
curl -X GET "http://localhost:8000/api/v1/researchers/{researcher_id}" \
  -H "Authorization: Bearer $TOKEN"
```

### Delete Researcher

```bash
curl -X DELETE "http://localhost:8000/api/v1/researchers/{researcher_id}" \
  -H "Authorization: Bearer $TOKEN"
```

## Run Complete Test Suite

```bash
cd /Users/brandon/meta-analysis-tool/backend
./test_reviewer_matcher_api.sh
```

## API Endpoints Summary

### Researchers
- `GET /api/v1/researchers` - Search researchers
- `GET /api/v1/researchers/{id}` - Get researcher profile
- `POST /api/v1/researchers` - Create researcher
- `PUT /api/v1/researchers/{id}` - Update researcher
- `DELETE /api/v1/researchers/{id}` - Delete researcher

### Reviewer Matching
- `POST /api/v1/reviewer-matches/search` - Find matching reviewers
- `GET /api/v1/reviewer-matches/{id}` - Get match details
- `POST /api/v1/reviewer-matches/invite` - Send invitation
- `PUT /api/v1/reviewer-matches/{id}/status` - Update status
- `GET /api/v1/manuscripts/{id}/matches` - Get all matches

## Key Features

1. **Intelligent Matching Algorithm**
   - Multi-factor scoring (expertise 50%, availability 30%, diversity 20%)
   - Conflict of interest detection
   - Geographic and institutional diversity promotion

2. **Flexible Search & Filtering**
   - Keyword and domain-based search
   - Academic metrics filtering (h-index, citations)
   - Workload and availability constraints
   - Institutional and geographic exclusions

3. **Complete Workflow Support**
   - Invitation tracking
   - Status management (pending → invited → accepted/declined)
   - Response time tracking
   - Historical review data

4. **Production-Ready**
   - JWT authentication
   - Role-based access control
   - Async database operations
   - Comprehensive error handling
   - Request validation with Pydantic

## Troubleshooting

### Authentication Issues
- Ensure token is included in Authorization header
- Token expires after 60 minutes (default) - refresh if needed

### Database Issues
- Run migrations: `alembic upgrade head`
- Check database connection in `.env`

### Import Errors
- Activate virtual environment
- Install dependencies: `pip install -r requirements.txt`

## Next Steps

1. **Frontend Integration**: Connect the React frontend to these endpoints
2. **Email Notifications**: Implement email sending for invitations
3. **Batch Operations**: Add bulk import/export for researchers
4. **Analytics Dashboard**: Create visualization for matching metrics
5. **ML Enhancement**: Train models on historical review data

## Documentation

- Full API Documentation: `REVIEWER_MATCHER_API.md`
- Interactive API Docs: http://localhost:8000/docs
- Database Models: `/backend/app/models/`

## Support

Questions? Check the main README or API documentation.
