# Reviewer Matcher API Documentation (Tool 4)

## Overview

The Reviewer Matcher API provides a comprehensive system for managing researchers and matching them with manuscripts for peer review. It implements intelligent matching algorithms that consider expertise, availability, diversity, and conflict of interest detection.

## Architecture

### Components

1. **Researchers API** (`/api/v1/researchers`)
   - CRUD operations for researcher database
   - Search and filtering capabilities
   - Pagination support

2. **Reviewer Matcher API** (`/api/v1/reviewer-matches`)
   - Intelligent reviewer matching algorithm
   - Invitation management
   - Status tracking
   - Conflict detection

### Database Models

- **Researcher**: Stores researcher profiles with academic metrics
- **ReviewerMatch**: Stores match results with scores and status
- **Manuscript**: Manuscript information for review matching

## API Endpoints

### Researchers Management

#### 1. Search Researchers
```http
GET /api/v1/researchers
```

**Query Parameters:**
- `page` (int, default: 1): Page number
- `page_size` (int, default: 50, max: 100): Items per page
- `keyword` (string, optional): Search by expertise keyword
- `domain` (string, optional): Filter by research domain
- `institution` (string, optional): Filter by institution
- `country` (string, optional): Filter by country
- `min_h_index` (int, optional): Minimum h-index
- `min_citations` (int, optional): Minimum total citations
- `sort_by` (string, default: "h_index"): Sort field (h_index, citations, name, recent_reviews, publications, response_rate)
- `sort_order` (string, default: "desc"): Sort order (asc, desc)

**Response:**
```json
{
  "total": 150,
  "page": 1,
  "page_size": 50,
  "researchers": [
    {
      "id": "uuid",
      "name": "Dr. Jane Smith",
      "email": "jane.smith@university.edu",
      "institution": "Stanford University",
      "department": "Computer Science",
      "country": "USA",
      "h_index": 45,
      "i10_index": 120,
      "total_citations": 5000,
      "publication_count": 150,
      "expertise_keywords": ["machine learning", "neural networks"],
      "research_domains": ["artificial intelligence"],
      "recent_review_count": 3,
      "total_review_count": 25,
      "average_review_time_days": 21.5,
      "estimated_availability": 0.7,
      "current_workload": 2,
      "response_rate": 0.85,
      "created_at": "2025-01-01T00:00:00",
      "updated_at": "2025-01-10T00:00:00"
    }
  ]
}
```

#### 2. Get Researcher Profile
```http
GET /api/v1/researchers/{researcher_id}
```

**Response:** Single researcher object (same structure as search results)

#### 3. Create Researcher
```http
POST /api/v1/researchers
```

**Request Body:**
```json
{
  "name": "Dr. Jane Smith",
  "email": "jane.smith@university.edu",
  "institution": "Stanford University",
  "department": "Computer Science",
  "country": "USA",
  "orcid": "0000-0001-2345-6789",
  "h_index": 45,
  "i10_index": 120,
  "total_citations": 5000,
  "publication_count": 150,
  "expertise_keywords": ["machine learning", "neural networks"],
  "research_domains": ["artificial intelligence"],
  "semantic_scholar_id": "1234567",
  "google_scholar_id": "ABC123XYZ"
}
```

**Response:** Created researcher object with ID

#### 4. Update Researcher
```http
PUT /api/v1/researchers/{researcher_id}
```

**Request Body:** Partial update (all fields optional)
```json
{
  "h_index": 50,
  "total_citations": 5500,
  "recent_review_count": 3,
  "current_workload": 2,
  "response_rate": 0.85
}
```

**Response:** Updated researcher object

#### 5. Delete Researcher
```http
DELETE /api/v1/researchers/{researcher_id}
```

**Response:** 204 No Content

---

### Reviewer Matching

#### 1. Search for Matching Reviewers
```http
POST /api/v1/reviewer-matches/search
```

**Request Body:**
```json
{
  "manuscript_id": "manuscript-uuid",
  "required_expertise": ["deep learning", "computer vision"],
  "research_domains": ["artificial intelligence"],
  "exclude_institutions": ["Same Institution"],
  "exclude_countries": ["Author Country"],
  "exclude_researcher_ids": ["uuid1", "uuid2"],
  "min_h_index": 10,
  "min_citations": 500,
  "max_current_workload": 5,
  "min_response_rate": 0.5,
  "diversity_preference": 0.3,
  "max_results": 20
}
```

**Algorithm:**

1. **Filtering Phase:**
   - Filter by required expertise (keywords + domains)
   - Apply minimum academic metrics (h-index, citations)
   - Filter by workload capacity
   - Apply exclusion filters (institutions, countries, specific researchers)

2. **Scoring Phase:**
   - **Expertise Score (50% weight):**
     - Keyword matching: 70%
     - Domain matching: 30%

   - **Availability Score (30% weight):**
     - Current workload (40%): Lower is better
     - Response rate (30%): Higher is better
     - Recent review activity (20%): Moderate is best
     - Estimated availability (10%): 0.0 to 1.0

   - **Diversity Score (20% weight):**
     - Geographic diversity (different countries)
     - Institutional diversity (different institutions)
     - Career stage diversity

3. **Conflict Detection:**
   - Institutional conflicts
   - Co-authorship conflicts
   - Recent collaboration conflicts
   - Advisor-advisee relationships

4. **Final Ranking:**
   - Calculate overall score (weighted average)
   - Apply conflict penalties
   - Sort by overall score (descending)
   - Limit to max_results

**Response:**
```json
{
  "manuscript_id": "uuid",
  "total_candidates": 45,
  "matches": [
    {
      "id": "match-uuid",
      "manuscript_id": "manuscript-uuid",
      "researcher_id": "researcher-uuid",
      "researcher_name": "Dr. Jane Smith",
      "researcher_institution": "Stanford University",
      "researcher_country": "USA",
      "researcher_h_index": 45,
      "researcher_email": "jane.smith@university.edu",
      "expertise_score": 0.85,
      "availability_score": 0.72,
      "diversity_score": 0.90,
      "overall_score": 0.82,
      "rank": 1,
      "has_conflict": false,
      "conflict_types": [],
      "conflict_details": {},
      "matching_keywords": ["deep learning", "computer vision"],
      "matching_domains": ["artificial intelligence"],
      "expertise_overlap": {
        "keyword_matches": 2,
        "total_keywords": 2,
        "domain_matches": 1,
        "total_domains": 1
      },
      "reasoning": "Expertise match: 0.85, Availability: 0.72, Diversity: 0.90.",
      "confidence": 0.82,
      "status": "pending",
      "created_at": "2025-01-10T00:00:00"
    }
  ],
  "search_criteria": { ... },
  "timestamp": "2025-01-10T00:00:00"
}
```

#### 2. Get Match Details
```http
GET /api/v1/reviewer-matches/{match_id}
```

**Response:** Single match object with full details

#### 3. Send Invitation
```http
POST /api/v1/reviewer-matches/invite
```

**Request Body:**
```json
{
  "match_id": "match-uuid",
  "custom_message": "We would like to invite you to review...",
  "deadline_days": 14
}
```

**Response:**
```json
{
  "match_id": "uuid",
  "researcher_id": "uuid",
  "status": "invited",
  "invitation_sent_at": "2025-01-10T00:00:00",
  "message": "Invitation sent successfully"
}
```

#### 4. Update Match Status
```http
PUT /api/v1/reviewer-matches/{match_id}/status
```

**Request Body:**
```json
{
  "status": "accepted",
  "notes": "Reviewer accepted the invitation"
}
```

**Valid Status Transitions:**
- PENDING → INVITED
- INVITED → ACCEPTED
- INVITED → DECLINED
- INVITED → NO_RESPONSE
- Any → WITHDRAWN

**Response:** Updated match object

#### 5. Get All Matches for Manuscript
```http
GET /api/v1/manuscripts/{manuscript_id}/matches
```

**Query Parameters:**
- `status_filter` (MatchStatus, optional): Filter by match status

**Response:**
```json
{
  "manuscript_id": "uuid",
  "total_matches": 15,
  "pending": 5,
  "invited": 6,
  "accepted": 3,
  "declined": 1,
  "matches": [ ... ]
}
```

## Authentication

All endpoints require JWT authentication using Bearer token:

```http
Authorization: Bearer <access_token>
```

**Required Roles:**
- Researchers API: `researcher` or `admin`
- Reviewer Matcher API: `researcher` or `admin` (read-only for `viewer`)

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid researcher ID format"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied. Required roles: ['admin', 'researcher']"
}
```

### 404 Not Found
```json
{
  "detail": "Researcher not found: <id>"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message"
}
```

## Scoring Algorithm Details

### Expertise Score Calculation

```python
expertise_score = (keyword_match_ratio * 0.7) + (domain_match_ratio * 0.3)

# Example:
# Required: ["deep learning", "computer vision"]
# Researcher: ["deep learning", "neural networks", "computer vision"]
# keyword_match_ratio = 2/2 = 1.0
# domain_match_ratio = 1/1 = 1.0
# expertise_score = (1.0 * 0.7) + (1.0 * 0.3) = 1.0
```

### Availability Score Calculation

```python
workload_score = {
  0: 1.0,
  1-2: 0.8,
  3-5: 0.5,
  >5: 0.2
}

availability_score = (
  workload_score * 0.4 +
  response_rate * 0.3 +
  activity_score * 0.2 +
  estimated_availability * 0.1
)
```

### Diversity Score Calculation

```python
diversity_score = 1.0
if same_country:
    diversity_score -= 0.3
if same_institution:
    diversity_score -= 0.5

diversity_score = max(0.0, diversity_score)
```

### Overall Score Calculation

```python
overall_score = (
  expertise_score * 0.5 +
  availability_score * (0.5 - diversity_preference) +
  diversity_score * diversity_preference
)

# Apply conflict penalty
if has_conflict:
    overall_score *= (1.0 - conflict_risk * 0.5)
```

## Testing

Run the comprehensive test suite:

```bash
cd /Users/brandon/meta-analysis-tool/backend
chmod +x test_reviewer_matcher_api.sh
./test_reviewer_matcher_api.sh
```

The test script will:
1. Register a test user
2. Login and get access token
3. Create test researchers
4. Search researchers with filters
5. Create a manuscript
6. Search for matching reviewers
7. Send invitations
8. Update match statuses
9. Clean up test data

## Example Use Cases

### 1. Find Reviewers for ML Paper

```bash
curl -X POST "http://localhost:8000/api/v1/reviewer-matches/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "manuscript_id": "manuscript-uuid",
    "required_expertise": ["machine learning", "deep learning"],
    "research_domains": ["artificial intelligence"],
    "min_h_index": 20,
    "min_citations": 1000,
    "max_current_workload": 3,
    "diversity_preference": 0.4,
    "max_results": 10
  }'
```

### 2. Search High-Impact Researchers

```bash
curl -X GET "http://localhost:8000/api/v1/researchers?min_h_index=50&min_citations=5000&sort_by=citations&sort_order=desc" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Update Researcher Workload

```bash
curl -X PUT "http://localhost:8000/api/v1/researchers/{id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_workload": 3,
    "recent_review_count": 2,
    "estimated_availability": 0.6
  }'
```

## Performance Considerations

- **Pagination:** Use appropriate page_size (default: 50, max: 100)
- **Caching:** Consider caching researcher profiles for frequently accessed data
- **Async Operations:** All database operations are async for better performance
- **Indexing:** Database indexes on frequently queried fields (h_index, citations, keywords)

## Future Enhancements

1. **Machine Learning Integration:**
   - Train ML models on historical review data
   - Predict reviewer response likelihood
   - Improve expertise matching accuracy

2. **Real-time Notifications:**
   - WebSocket support for invitation updates
   - Email notifications for invitations

3. **Advanced Analytics:**
   - Review turnaround time predictions
   - Reviewer performance metrics
   - Network analysis of collaborations

4. **External API Integration:**
   - ORCID profile auto-import
   - Semantic Scholar API integration
   - Google Scholar scraping

## License

Internal API - Proprietary

## Support

For issues or questions, contact the development team.
