# ReviewDrafterAgent - API Integration Guide

This document shows how to integrate the ReviewDrafterAgent with the FastAPI backend for the `/api/v1/peer-reviews/generate` endpoint.

## API Endpoint Implementation

```python
# File: backend/app/api/v1/endpoints/peer_reviews.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.api.deps import get_db
from app.models.peer_review import PeerReview, ReviewStatus
from app.models.manuscript import Manuscript
from app.agents.specialized.review_drafter_agent import ReviewDrafterAgent, ExpertiseLevel, ReviewStyle
from app.agents.base import AgentConfig, AgentRole
from loguru import logger

router = APIRouter()


@router.post("/generate", response_model=PeerReviewResponse)
async def generate_peer_review(
    manuscript_id: UUID,
    expertise_level: str = "expert",
    review_style: str = "constructive",
    focus_areas: Optional[list[str]] = None,
    db: Session = Depends(get_db),
):
    """Generate an AI-assisted peer review for a manuscript.

    Args:
        manuscript_id: UUID of the manuscript to review
        expertise_level: Level of reviewer expertise (junior/senior/expert)
        review_style: Style of review (constructive/critical/supportive)
        focus_areas: Optional list of focus areas (methodology, writing, etc.)
        db: Database session

    Returns:
        Generated peer review data
    """
    # 1. Fetch manuscript from database
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manuscript {manuscript_id} not found"
        )

    logger.info(f"Generating AI review for manuscript: {manuscript.title[:50]}...")

    # 2. Extract manuscript content
    manuscript_data = {
        "title": manuscript.title,
        "abstract": manuscript.abstract,
        "content": _extract_manuscript_content(manuscript),  # Helper function
        "manuscript_type": manuscript.manuscript_type,
        "keywords": manuscript.keywords or [],
        "author_affiliations": manuscript.author_affiliations or {},
    }

    # 3. Initialize ReviewDrafterAgent
    agent_config = AgentConfig(
        name=f"ReviewDrafter-{manuscript_id}",
        role=AgentRole.QUALITY_ASSESSMENT,
        temperature=0.3,
        max_tokens=4096,
    )

    agent = ReviewDrafterAgent(agent_config)

    # 4. Generate review
    try:
        review_data = await agent.process({
            "manuscript": manuscript_data,
            "expertise_level": expertise_level,
            "review_style": review_style,
            "focus_areas": focus_areas or [],
        })
    except Exception as e:
        logger.error(f"Error generating review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate review: {str(e)}"
        )

    # 5. Create PeerReview database record
    peer_review = PeerReview(
        manuscript_id=manuscript_id,
        reviewer_id=None,  # AI-generated, no human reviewer
        status=ReviewStatus.DRAFT,
        review_round=manuscript.current_round,

        # Review content
        review_text=review_data["review_text"],
        strengths="\n".join(f"- {s}" for s in review_data["strengths"]),
        weaknesses="\n".join(f"- {w}" for w in review_data["weaknesses"]),
        detailed_comments=review_data["detailed_comments"],

        # Scores
        overall_score=review_data["overall_score"],
        originality_score=review_data["originality_score"],
        methodology_score=review_data["methodology_score"],
        clarity_score=review_data["clarity_score"],
        significance_score=review_data["significance_score"],

        # Recommendation
        recommendation=review_data["recommendation"],
        confidence=review_data["confidence"],

        # AI assistance tracking
        ai_assisted=True,
        ai_draft_used=True,
        ai_generated_sections={
            "summary": True,
            "strengths": True,
            "weaknesses": True,
            "detailed_comments": True,
            "scores": True,
            "recommendation": True,
        },

        # Metadata
        review_metadata={
            "expertise_level": expertise_level,
            "review_style": review_style,
            "focus_areas": focus_areas,
            "agent_version": agent.config.version,
            "agent_model": agent.config.model,
            "decision_metadata": review_data.get("decision_metadata"),
            "reasoning": review_data.get("reasoning"),
        }
    )

    db.add(peer_review)
    db.commit()
    db.refresh(peer_review)

    logger.info(f"Created AI review {peer_review.id} for manuscript {manuscript_id}")

    return peer_review


def _extract_manuscript_content(manuscript: Manuscript) -> str:
    """Extract manuscript content from PDF or text field.

    Args:
        manuscript: Manuscript database object

    Returns:
        Extracted text content (truncated to ~10 pages)
    """
    if manuscript.pdf_path:
        # Extract text from PDF (first 10 pages)
        try:
            import PyPDF2
            with open(manuscript.pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                # Extract first 10 pages
                num_pages = min(10, len(pdf_reader.pages))
                content = ""
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    content += page.extract_text()

                return content
        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            return manuscript.abstract or ""

    # Fallback to abstract if no PDF or extraction failed
    return manuscript.abstract or ""
```

## Pydantic Response Models

```python
# File: backend/app/schemas/peer_review.py

from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List, Dict
from datetime import datetime

class PeerReviewResponse(BaseModel):
    """Response model for peer review."""

    id: UUID
    manuscript_id: UUID
    reviewer_id: Optional[UUID]
    status: str

    # Review content
    review_text: str
    strengths: Optional[str]
    weaknesses: Optional[str]
    detailed_comments: Optional[str]

    # Scores
    overall_score: Optional[float] = Field(ge=1.0, le=10.0)
    originality_score: Optional[float] = Field(ge=1.0, le=10.0)
    methodology_score: Optional[float] = Field(ge=1.0, le=10.0)
    clarity_score: Optional[float] = Field(ge=1.0, le=10.0)
    significance_score: Optional[float] = Field(ge=1.0, le=10.0)

    # Recommendation
    recommendation: Optional[str]
    confidence: Optional[float] = Field(ge=0.0, le=1.0)

    # AI tracking
    ai_assisted: bool
    ai_draft_used: bool
    ai_generated_sections: Optional[Dict[str, bool]]

    # Metadata
    review_metadata: Optional[Dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenerateReviewRequest(BaseModel):
    """Request model for generating a review."""

    manuscript_id: UUID
    expertise_level: str = Field(
        default="expert",
        description="Reviewer expertise level: junior, senior, or expert"
    )
    review_style: str = Field(
        default="constructive",
        description="Review style: constructive, critical, or supportive"
    )
    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Specific focus areas: methodology, writing, statistics, novelty, literature, ethics"
    )
```

## Frontend Integration Example

```typescript
// File: frontend/src/services/peerReviewService.ts

import { apiClient } from './apiClient';

export interface GenerateReviewParams {
  manuscriptId: string;
  expertiseLevel?: 'junior' | 'senior' | 'expert';
  reviewStyle?: 'constructive' | 'critical' | 'supportive';
  focusAreas?: string[];
}

export interface PeerReviewData {
  id: string;
  manuscript_id: string;
  review_text: string;
  strengths: string;
  weaknesses: string;
  detailed_comments: string;
  overall_score: number;
  originality_score: number;
  methodology_score: number;
  clarity_score: number;
  significance_score: number;
  recommendation: string;
  confidence: number;
  ai_assisted: boolean;
  ai_draft_used: boolean;
  created_at: string;
}

export const peerReviewService = {
  /**
   * Generate an AI-assisted peer review for a manuscript
   */
  async generateReview(params: GenerateReviewParams): Promise<PeerReviewData> {
    const response = await apiClient.post('/api/v1/peer-reviews/generate', {
      manuscript_id: params.manuscriptId,
      expertise_level: params.expertiseLevel || 'expert',
      review_style: params.reviewStyle || 'constructive',
      focus_areas: params.focusAreas || [],
    });

    return response.data;
  },

  /**
   * Get a peer review by ID
   */
  async getReview(reviewId: string): Promise<PeerReviewData> {
    const response = await apiClient.get(`/api/v1/peer-reviews/${reviewId}`);
    return response.data;
  },

  /**
   * Get all reviews for a manuscript
   */
  async getManuscriptReviews(manuscriptId: string): Promise<PeerReviewData[]> {
    const response = await apiClient.get(`/api/v1/peer-reviews/manuscript/${manuscriptId}`);
    return response.data;
  },
};
```

## React Component Example

```typescript
// File: frontend/src/components/PeerReview/GenerateReviewButton.tsx

import React, { useState } from 'react';
import { Button, Modal, Select, Checkbox, message } from 'antd';
import { peerReviewService } from '@/services/peerReviewService';

interface GenerateReviewButtonProps {
  manuscriptId: string;
  onReviewGenerated?: (reviewId: string) => void;
}

export const GenerateReviewButton: React.FC<GenerateReviewButtonProps> = ({
  manuscriptId,
  onReviewGenerated,
}) => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [expertiseLevel, setExpertiseLevel] = useState<string>('expert');
  const [reviewStyle, setReviewStyle] = useState<string>('constructive');
  const [focusAreas, setFocusAreas] = useState<string[]>([]);

  const handleGenerate = async () => {
    setIsGenerating(true);

    try {
      const review = await peerReviewService.generateReview({
        manuscriptId,
        expertiseLevel: expertiseLevel as any,
        reviewStyle: reviewStyle as any,
        focusAreas,
      });

      message.success('Review generated successfully!');
      setIsModalVisible(false);

      if (onReviewGenerated) {
        onReviewGenerated(review.id);
      }
    } catch (error) {
      message.error('Failed to generate review. Please try again.');
      console.error('Error generating review:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <>
      <Button type="primary" onClick={() => setIsModalVisible(true)}>
        Generate AI Review
      </Button>

      <Modal
        title="Generate AI-Assisted Peer Review"
        visible={isModalVisible}
        onOk={handleGenerate}
        onCancel={() => setIsModalVisible(false)}
        okText="Generate Review"
        confirmLoading={isGenerating}
      >
        <div style={{ marginBottom: 16 }}>
          <label>Expertise Level:</label>
          <Select
            value={expertiseLevel}
            onChange={setExpertiseLevel}
            style={{ width: '100%' }}
          >
            <Select.Option value="junior">Junior Reviewer</Select.Option>
            <Select.Option value="senior">Senior Reviewer</Select.Option>
            <Select.Option value="expert">Expert Reviewer</Select.Option>
          </Select>
        </div>

        <div style={{ marginBottom: 16 }}>
          <label>Review Style:</label>
          <Select
            value={reviewStyle}
            onChange={setReviewStyle}
            style={{ width: '100%' }}
          >
            <Select.Option value="constructive">Constructive</Select.Option>
            <Select.Option value="critical">Critical</Select.Option>
            <Select.Option value="supportive">Supportive</Select.Option>
          </Select>
        </div>

        <div>
          <label>Focus Areas (optional):</label>
          <Checkbox.Group
            options={[
              { label: 'Methodology', value: 'methodology' },
              { label: 'Writing', value: 'writing' },
              { label: 'Statistics', value: 'statistics' },
              { label: 'Novelty', value: 'novelty' },
              { label: 'Literature', value: 'literature' },
              { label: 'Ethics', value: 'ethics' },
            ]}
            value={focusAreas}
            onChange={setFocusAreas}
          />
        </div>
      </Modal>
    </>
  );
};
```

## Usage Examples

### Basic Usage (Default Settings)
```bash
curl -X POST "http://localhost:8000/api/v1/peer-reviews/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "manuscript_id": "123e4567-e89b-12d3-a456-426614174000",
    "expertise_level": "expert",
    "review_style": "constructive"
  }'
```

### Advanced Usage (Custom Settings)
```bash
curl -X POST "http://localhost:8000/api/v1/peer-reviews/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "manuscript_id": "123e4567-e89b-12d3-a456-426614174000",
    "expertise_level": "senior",
    "review_style": "critical",
    "focus_areas": ["methodology", "statistics"]
  }'
```

### Python Client Example
```python
import httpx
import asyncio

async def generate_review(manuscript_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/peer-reviews/generate",
            json={
                "manuscript_id": manuscript_id,
                "expertise_level": "expert",
                "review_style": "constructive",
                "focus_areas": ["methodology", "writing"],
            }
        )
        return response.json()

# Usage
review = asyncio.run(generate_review("123e4567-e89b-12d3-a456-426614174000"))
print(f"Generated review: {review['id']}")
print(f"Recommendation: {review['recommendation']}")
print(f"Overall Score: {review['overall_score']}/10")
```

## Database Queries

### Get all AI-generated reviews
```sql
SELECT
  id,
  manuscript_id,
  recommendation,
  overall_score,
  confidence,
  created_at
FROM peer_reviews
WHERE ai_draft_used = TRUE
ORDER BY created_at DESC;
```

### Get review statistics by recommendation
```sql
SELECT
  recommendation,
  COUNT(*) as count,
  AVG(overall_score) as avg_score,
  AVG(confidence) as avg_confidence
FROM peer_reviews
WHERE ai_assisted = TRUE
GROUP BY recommendation
ORDER BY count DESC;
```

### Find high-confidence reviews
```sql
SELECT
  id,
  manuscript_id,
  recommendation,
  overall_score,
  confidence
FROM peer_reviews
WHERE ai_assisted = TRUE
  AND confidence >= 0.8
  AND overall_score >= 7.0
ORDER BY confidence DESC, overall_score DESC;
```

## Testing

```python
# File: backend/tests/test_review_drafter_api.py

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.models.manuscript import Manuscript, ManuscriptType, ManuscriptStatus


@pytest.fixture
def test_manuscript(db_session):
    """Create a test manuscript."""
    manuscript = Manuscript(
        title="Test Manuscript for Review Generation",
        abstract="This is a test abstract for review generation testing.",
        manuscript_type=ManuscriptType.RESEARCH_ARTICLE,
        status=ManuscriptStatus.IN_REVIEW,
    )
    db_session.add(manuscript)
    db_session.commit()
    return manuscript


def test_generate_review_success(test_client: TestClient, test_manuscript):
    """Test successful review generation."""
    response = test_client.post(
        "/api/v1/peer-reviews/generate",
        json={
            "manuscript_id": str(test_manuscript.id),
            "expertise_level": "expert",
            "review_style": "constructive",
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["manuscript_id"] == str(test_manuscript.id)
    assert data["ai_assisted"] is True
    assert data["ai_draft_used"] is True
    assert data["recommendation"] in ["accept", "minor_revision", "major_revision", "reject"]
    assert 1.0 <= data["overall_score"] <= 10.0
    assert 0.0 <= data["confidence"] <= 1.0


def test_generate_review_not_found(test_client: TestClient):
    """Test review generation with non-existent manuscript."""
    response = test_client.post(
        "/api/v1/peer-reviews/generate",
        json={
            "manuscript_id": str(uuid4()),
            "expertise_level": "expert",
        }
    )

    assert response.status_code == 404
```

## Performance Considerations

### Expected Response Times
- Simple review (abstract only): 15-30 seconds
- Full review (10 pages): 30-60 seconds
- Complex review (statistics focus): 45-90 seconds

### Rate Limiting Recommendations
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/generate")
@limiter.limit("10/hour")  # Max 10 reviews per hour per IP
async def generate_peer_review(...):
    ...
```

### Caching Strategy
```python
from functools import lru_cache
import hashlib

def get_manuscript_cache_key(manuscript_id: UUID, expertise: str, style: str) -> str:
    """Generate cache key for manuscript review."""
    return hashlib.md5(f"{manuscript_id}-{expertise}-{style}".encode()).hexdigest()

# Use Redis for caching if the same review is requested multiple times
```

## Security & Ethics Considerations

1. **Disclaimer Required**: Always display that this is AI-generated
2. **Human Oversight**: Require human reviewer to approve before submission
3. **Audit Trail**: Log all AI review generations for accountability
4. **Rate Limiting**: Prevent abuse of the AI review system
5. **Data Privacy**: Ensure manuscript content is handled securely
6. **Bias Detection**: Monitor for systematic biases in AI recommendations

## Monitoring & Logging

```python
from loguru import logger

# Log all review generations
logger.info(
    "AI review generated",
    extra={
        "manuscript_id": manuscript_id,
        "expertise_level": expertise_level,
        "review_style": review_style,
        "recommendation": review_data["recommendation"],
        "confidence": review_data["confidence"],
        "overall_score": review_data["overall_score"],
        "generation_time_seconds": generation_time,
    }
)

# Alert on low confidence reviews
if review_data["confidence"] < 0.6:
    logger.warning(
        f"Low confidence review generated: {review_data['confidence']:.2f}",
        extra={"manuscript_id": manuscript_id}
    )
```

## Future Enhancements

1. **Multi-round review support**: Track revisions and re-reviews
2. **Reviewer matching**: Match AI expertise to manuscript domain
3. **Consensus analysis**: Compare AI review with human reviews
4. **Automated suggestions**: Generate revision checklist from weaknesses
5. **Real-time collaboration**: Allow human reviewers to edit AI drafts
6. **Quality metrics**: Track AI review accuracy vs. final decisions
