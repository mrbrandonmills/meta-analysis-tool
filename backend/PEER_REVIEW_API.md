# Peer Review API Documentation

## Overview

The Peer Review API (Tool 3) provides a complete AI-powered manuscript review system with the following capabilities:

- **Manuscript Management**: Upload, create, update, and manage manuscripts
- **PDF Processing**: Upload PDFs with automatic title/abstract extraction
- **AI Review Generation**: Generate comprehensive peer reviews using Claude AI
- **Review Management**: Create, edit, and manage peer reviews
- **Multi-round Reviews**: Support for revision rounds and review tracking

## Architecture

```
/api/v1/manuscripts/          # Manuscript CRUD
/api/v1/manuscripts/upload    # PDF upload endpoint
/api/v1/peer-reviews/         # Peer review CRUD
/api/v1/peer-reviews/generate # AI review generation
```

## Database Models

### Manuscript
- **ID**: UUID
- **Title**: Text (required)
- **Abstract**: Text (optional)
- **Keywords**: Array of strings
- **Manuscript Type**: Enum (research_article, review, systematic_review, meta_analysis, etc.)
- **Status**: Enum (submitted, desk_review, in_review, revision_requested, accepted, rejected)
- **PDF Path**: File storage path
- **Author Information**: Names and affiliations
- **Review Scores**: Quality, methodology, novelty scores
- **Editorial Decision**: Decision and reasoning

### PeerReview
- **ID**: UUID
- **Manuscript ID**: Foreign key to manuscript
- **Reviewer ID**: Optional foreign key to researcher
- **Review Round**: Integer
- **Status**: Enum (invited, accepted, in_progress, submitted)
- **Review Text**: Main review content
- **Strengths/Weaknesses**: Structured feedback
- **Scores**: Overall, originality, methodology, clarity, significance (1-10 scale)
- **Recommendation**: Enum (accept, minor_revision, major_revision, reject)
- **AI Metadata**: Tracking for AI assistance

## API Endpoints

### 1. Manuscript Endpoints

#### POST /api/v1/manuscripts/upload
Upload a manuscript PDF with automatic metadata extraction.

**Request**: `multipart/form-data`
```json
{
  "file": "manuscript.pdf",
  "manuscript_id": "optional-uuid-to-attach-to-existing",
  "auto_extract": true
}
```

**Response**: `201 Created`
```json
{
  "manuscript_id": "550e8400-e29b-41d4-a716-446655440000",
  "pdf_path": "/data/manuscripts/20231110_120000_manuscript.pdf",
  "file_size_bytes": 2458624,
  "extracted_title": "The Impact of AI on Scientific Publishing",
  "extracted_abstract": "This study examines...",
  "message": "PDF uploaded and new manuscript created successfully"
}
```

**Features**:
- Accepts PDF files up to 50MB
- Extracts title and abstract using PyMuPDF
- Creates new manuscript or attaches to existing
- Stores PDF with unique timestamp-based filename
- Validates file type and size

---

#### POST /api/v1/manuscripts
Create a new manuscript submission.

**Request**:
```json
{
  "title": "The Impact of AI on Scientific Publishing: A Meta-Analysis",
  "abstract": "This study examines the impact of artificial intelligence...",
  "keywords": ["AI", "peer review", "scientific publishing"],
  "manuscript_type": "meta_analysis",
  "journal_name": "Journal of Scientific Research",
  "author_names": ["John Doe", "Jane Smith"],
  "author_affiliations": {
    "John Doe": "University of Example",
    "Jane Smith": "Research Institute"
  }
}
```

**Response**: `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "The Impact of AI on Scientific Publishing: A Meta-Analysis",
  "abstract": "This study examines...",
  "manuscript_type": "meta_analysis",
  "status": "submitted",
  "submission_date": "2024-11-10T12:00:00Z",
  "has_pdf": false,
  "review_count": 0,
  "created_at": "2024-11-10T12:00:00Z",
  "updated_at": "2024-11-10T12:00:00Z"
}
```

---

#### GET /api/v1/manuscripts
List manuscripts for the current user.

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `status_filter`: Filter by status (optional)
- `manuscript_type`: Filter by type (optional)
- `journal_name`: Filter by journal name (optional)

**Response**: `200 OK`
```json
{
  "total": 15,
  "manuscripts": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "The Impact of AI on Scientific Publishing",
      "status": "in_review",
      "submission_date": "2024-11-10T12:00:00Z",
      "review_count": 2,
      "has_pdf": true
    }
  ],
  "page": 1,
  "page_size": 20
}
```

---

#### GET /api/v1/manuscripts/{manuscript_id}
Get a specific manuscript by ID.

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "The Impact of AI on Scientific Publishing",
  "abstract": "This study examines...",
  "keywords": ["AI", "peer review"],
  "manuscript_type": "meta_analysis",
  "status": "in_review",
  "review_count": 2,
  "quality_score": {"overall": 8.5, "methodology": 9.0},
  "has_pdf": true
}
```

---

#### PUT /api/v1/manuscripts/{manuscript_id}
Update a manuscript.

**Request**:
```json
{
  "title": "Updated Title",
  "abstract": "Updated abstract",
  "keywords": ["new", "keywords"]
}
```

**Response**: `200 OK` (Returns updated manuscript)

---

#### PUT /api/v1/manuscripts/{manuscript_id}/status
Update manuscript status and editorial decision.

**Request**:
```json
{
  "status": "accepted",
  "decision_letter": "We are pleased to accept your manuscript..."
}
```

**Response**: `200 OK` (Returns updated manuscript)

---

#### DELETE /api/v1/manuscripts/{manuscript_id}
Delete a manuscript.

**Response**: `204 No Content`

**Features**:
- Deletes associated PDF file
- Cascade deletes all peer reviews
- Only corresponding author can delete

---

### 2. Peer Review Endpoints

#### POST /api/v1/peer-reviews/generate
Generate an AI-powered peer review using Claude.

**Request**:
```json
{
  "manuscript_id": "550e8400-e29b-41d4-a716-446655440000",
  "review_focus": ["methodology", "results", "clarity", "significance"],
  "expertise_level": "expert",
  "review_style": "constructive",
  "include_suggestions": true
}
```

**Response**: `200 OK`
```json
{
  "manuscript_id": "550e8400-e29b-41d4-a716-446655440000",
  "review_text": "This manuscript presents a comprehensive analysis...",
  "strengths": "Strong methodology, comprehensive literature search...",
  "weaknesses": "Limited discussion of potential biases...",
  "detailed_comments": "The authors have done an excellent job...",
  "overall_score": 8.5,
  "originality_score": 7.0,
  "methodology_score": 9.0,
  "clarity_score": 8.5,
  "significance_score": 8.0,
  "recommendation": "MINOR_REVISION",
  "confidence": 0.85,
  "ai_reasoning": "The manuscript is of high quality with sound methodology...",
  "review_focus_areas": ["methodology", "results", "clarity", "significance"],
  "estimated_time_saved_hours": 4.0
}
```

**AI Review Features**:
- Analyzes manuscript title, abstract, and full text (first 10 pages)
- Generates comprehensive structured review
- Provides quantitative scores (1-10 scale)
- Makes evidence-based recommendation
- Explains reasoning and confidence level
- Customizable by expertise level and review style
- Does NOT auto-save (user can edit before submission)

**Review Styles**:
- `constructive`: Balanced, helpful feedback
- `critical`: Rigorous, detailed critique
- `supportive`: Encouraging, improvement-focused

**Expertise Levels**:
- `expert`: Senior researcher perspective
- `senior`: Mid-career researcher
- `junior`: Early-career researcher

---

#### POST /api/v1/peer-reviews
Create and submit a peer review.

**Request**:
```json
{
  "manuscript_id": "550e8400-e29b-41d4-a716-446655440000",
  "review_text": "This is a well-structured systematic review...",
  "strengths": "Strong methodology, comprehensive coverage...",
  "weaknesses": "Limited discussion of biases...",
  "detailed_comments": "The authors have done an excellent job...",
  "confidential_comments": "I recommend acceptance with minor revisions.",
  "overall_score": 8.5,
  "originality_score": 7.0,
  "methodology_score": 9.0,
  "clarity_score": 8.5,
  "significance_score": 8.0,
  "recommendation": "minor_revision",
  "confidence": 0.85,
  "ai_assisted": true
}
```

**Response**: `201 Created`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "manuscript_id": "550e8400-e29b-41d4-a716-446655440000",
  "review_round": 1,
  "status": "submitted",
  "recommendation": "minor_revision",
  "overall_score": 8.5,
  "ai_assisted": true,
  "submission_date": "2024-11-10T13:00:00Z"
}
```

---

#### GET /api/v1/peer-reviews/{review_id}
Get a specific peer review by ID.

**Response**: `200 OK`
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "manuscript_id": "550e8400-e29b-41d4-a716-446655440000",
  "review_text": "This is a well-structured systematic review...",
  "strengths": "Strong methodology...",
  "weaknesses": "Limited discussion...",
  "overall_score": 8.5,
  "recommendation": "minor_revision",
  "status": "submitted"
}
```

---

#### PUT /api/v1/peer-reviews/{review_id}
Update an existing peer review.

**Request**:
```json
{
  "review_text": "Updated review text...",
  "overall_score": 9.0,
  "status": "submitted"
}
```

**Response**: `200 OK` (Returns updated review)

---

#### GET /api/v1/manuscripts/{manuscript_id}/reviews
List all peer reviews for a manuscript.

**Query Parameters**:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

**Response**: `200 OK`
```json
{
  "total": 3,
  "reviews": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "review_round": 1,
      "status": "submitted",
      "recommendation": "minor_revision",
      "overall_score": 8.5,
      "submission_date": "2024-11-10T13:00:00Z"
    }
  ],
  "page": 1,
  "page_size": 20
}
```

---

#### DELETE /api/v1/peer-reviews/{review_id}
Delete a peer review.

**Response**: `204 No Content`

---

## Authentication

All endpoints require JWT authentication via Bearer token:

```
Authorization: Bearer <access_token>
```

Obtain tokens via `/api/v1/auth/login` endpoint.

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Only PDF files are allowed"
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
  "detail": "Access denied. Required roles: [researcher]"
}
```

### 404 Not Found
```json
{
  "detail": "Manuscript not found or access denied"
}
```

### 413 Payload Too Large
```json
{
  "detail": "File too large. Maximum size is 50MB, got 75.5MB"
}
```

### 500 Internal Server Error
```json
{
  "detail": "AI review generation failed: API key invalid"
}
```

## Status Codes

- `200 OK`: Successful GET/PUT request
- `201 Created`: Successful POST request
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File size exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

- **Authenticated users**: 100 requests/minute
- **Unauthenticated users**: 20 requests/minute
- **AI generation endpoint**: Special rate limiting may apply based on Anthropic API limits

## File Storage

PDFs are stored in: `{data_dir}/manuscripts/`

Format: `{timestamp}_{original_filename}.pdf`

Example: `20231110_120000_manuscript.pdf`

## Workflow Example

### 1. Complete Manuscript Submission Flow

```bash
# 1. Login
POST /api/v1/auth/login
{
  "username": "researcher@university.edu",
  "password": "SecurePass123"
}
# Returns: { "access_token": "eyJ...", "token_type": "bearer" }

# 2. Upload PDF
POST /api/v1/manuscripts/upload
Headers: Authorization: Bearer eyJ...
Body: multipart/form-data with PDF file
# Returns: manuscript_id and extracted metadata

# 3. Update manuscript details
PUT /api/v1/manuscripts/{manuscript_id}
{
  "keywords": ["AI", "peer review"],
  "journal_name": "Nature Reviews"
}

# 4. Generate AI review
POST /api/v1/peer-reviews/generate
{
  "manuscript_id": "{manuscript_id}",
  "review_style": "constructive"
}
# Returns: comprehensive AI-generated review

# 5. Edit and submit review
POST /api/v1/peer-reviews
{
  "manuscript_id": "{manuscript_id}",
  "review_text": "[Edited AI review]",
  "overall_score": 8.5,
  "recommendation": "minor_revision",
  "ai_assisted": true
}

# 6. View all reviews
GET /api/v1/manuscripts/{manuscript_id}/reviews
# Returns: list of all reviews for the manuscript

# 7. Update manuscript status
PUT /api/v1/manuscripts/{manuscript_id}/status
{
  "status": "revision_requested"
}
```

## Dependencies

- **FastAPI**: Web framework
- **SQLAlchemy**: ORM and database
- **PyMuPDF (fitz)**: PDF metadata extraction
- **Anthropic SDK**: Claude AI integration
- **Pydantic**: Request/response validation
- **PostgreSQL/SQLite**: Database backend

## Configuration

Required environment variables:

```env
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...
DATA_DIR=./data
SECRET_KEY=your-secret-key
```

## Testing

Run the test suite:

```bash
python test_peer_review_api.py
```

Tests cover:
- Manuscript CRUD operations
- Peer review CRUD operations
- AI review parsing
- Database relationships
- Access control

## Future Enhancements

1. **Real-time collaboration**: Multiple reviewers commenting simultaneously
2. **Reviewer anonymization**: Blind/double-blind review support
3. **Version control**: Track manuscript revisions and review iterations
4. **Notification system**: Email alerts for status changes
5. **Analytics dashboard**: Review statistics and insights
6. **Integration with journal systems**: Direct submission to publishers
7. **OCR support**: Extract text from scanned PDFs
8. **Multi-language support**: Review generation in multiple languages

## Support

For issues or questions:
- API Documentation: `/docs` (Swagger UI)
- Alternative docs: `/redoc` (ReDoc)
- Health check: `/api/v1/health`
