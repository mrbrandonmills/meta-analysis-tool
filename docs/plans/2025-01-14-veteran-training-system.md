# Veteran Lead Training System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete veteran lead training system that incorporates presentation scripts, tracks trainee progress, and uses AI to assess performance against script mastery criteria.

**Architecture:** Full-stack system with PostgreSQL database for training content and progress tracking, FastAPI backend with AI assessment agent using Anthropic Claude, and Next.js/React frontend for training interface. AI agent analyzes trainee performance transcripts against reference scripts to identify gaps and provide coaching.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, Alembic, PostgreSQL, Anthropic Claude API, Next.js 13, React 18, TypeScript, TailwindCSS

---

## Phase 1: Database Schema & Models

### Task 1: Create Training Content Database Schema

**Files:**
- Create: `backend/alembic/versions/005_veteran_training_system.py`
- Reference: `backend/alembic/versions/004_add_pdf_full_text_models.py`

**Step 1: Create Alembic migration file**

```bash
cd backend
alembic revision -m "Add veteran training system schema"
```

Expected: New migration file created in `backend/alembic/versions/`

**Step 2: Write migration with training tables**

Edit the generated file:

```python
"""Add veteran training system schema

Revision ID: 005
Revises: 004
Create Date: 2025-01-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Training Scripts table
    op.create_table(
        'training_scripts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('script_type', sa.String(50), nullable=False),  # 'presentation', 'phone_booking'
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('key_points', JSONB, nullable=False),  # List of critical script elements
        sa.Column('mastery_criteria', JSONB, nullable=False),  # Assessment criteria
        sa.Column('version', sa.Integer, default=1, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('idx_training_scripts_type_active', 'training_scripts', ['script_type', 'is_active'])

    # Training Sessions table
    op.create_table(
        'training_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('trainee_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('script_id', UUID(as_uuid=True), sa.ForeignKey('training_scripts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_type', sa.String(50), nullable=False),  # 'practice', 'evaluation', 'live'
        sa.Column('transcript', sa.Text, nullable=True),  # Trainee's delivery transcript
        sa.Column('recording_url', sa.String(500), nullable=True),
        sa.Column('duration_seconds', sa.Integer, nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(50), default='in_progress'),  # 'in_progress', 'completed', 'abandoned'
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_training_sessions_trainee', 'training_sessions', ['trainee_id', 'created_at'])

    # AI Assessments table
    op.create_table(
        'training_assessments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('session_id', UUID(as_uuid=True), sa.ForeignKey('training_sessions.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('overall_score', sa.Float, nullable=False),  # 0-100
        sa.Column('key_points_covered', JSONB, nullable=False),  # Which key points were hit
        sa.Column('strengths', JSONB, nullable=False),  # AI-identified strengths
        sa.Column('improvement_areas', JSONB, nullable=False),  # AI-identified gaps
        sa.Column('specific_feedback', sa.Text, nullable=False),  # Detailed AI feedback
        sa.Column('tone_analysis', JSONB, nullable=True),  # Tone, confidence, empathy scores
        sa.Column('recommendation', sa.String(50), nullable=False),  # 'ready', 'needs_practice', 'needs_coaching'
        sa.Column('ai_model', sa.String(100), nullable=False),
        sa.Column('assessed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_training_assessments_session', 'training_assessments', ['session_id'])

    # Trainee Progress table
    op.create_table(
        'trainee_progress',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('trainee_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('script_id', UUID(as_uuid=True), sa.ForeignKey('training_scripts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mastery_level', sa.String(50), default='beginner'),  # 'beginner', 'intermediate', 'advanced', 'master'
        sa.Column('total_sessions', sa.Integer, default=0),
        sa.Column('average_score', sa.Float, nullable=True),
        sa.Column('best_score', sa.Float, nullable=True),
        sa.Column('last_session_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('certified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('certification_level', sa.String(50), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index('idx_trainee_progress_unique', 'trainee_progress', ['trainee_id', 'script_id'], unique=True)


def downgrade() -> None:
    op.drop_table('trainee_progress')
    op.drop_table('training_assessments')
    op.drop_table('training_sessions')
    op.drop_table('training_scripts')
```

**Step 3: Run migration**

```bash
alembic upgrade head
```

Expected: Tables created successfully

**Step 4: Verify migration**

```bash
psql $DATABASE_URL -c "\dt training_*"
```

Expected output: Lists training_scripts, training_sessions, training_assessments, trainee_progress

**Step 5: Commit**

```bash
git add backend/alembic/versions/005_veteran_training_system.py
git commit -m "feat: add veteran training system database schema

- Add training_scripts table for script content
- Add training_sessions table for practice sessions
- Add training_assessments table for AI evaluations
- Add trainee_progress table for progress tracking"
```

---

### Task 2: Create SQLAlchemy Models

**Files:**
- Create: `backend/app/models/training.py`
- Reference: `backend/app/models/project.py`

**Step 1: Create training models file**

```python
"""Training system models"""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from backend.app.db.base_class import Base


class TrainingScript(Base):
    """Reference scripts for veteran lead training"""
    __tablename__ = "training_scripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    script_type = Column(String(50), nullable=False)  # 'presentation', 'phone_booking'
    content = Column(Text, nullable=False)
    key_points = Column(JSONB, nullable=False)  # List[str] of critical elements
    mastery_criteria = Column(JSONB, nullable=False)  # Dict[str, str] of assessment criteria
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    sessions = relationship("TrainingSession", back_populates="script")
    progress_records = relationship("TraineeProgress", back_populates="script")


class TrainingSession(Base):
    """Individual training session records"""
    __tablename__ = "training_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainee_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    script_id = Column(UUID(as_uuid=True), ForeignKey('training_scripts.id', ondelete='CASCADE'), nullable=False)
    session_type = Column(String(50), nullable=False)  # 'practice', 'evaluation', 'live'
    transcript = Column(Text, nullable=True)
    recording_url = Column(String(500), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default='in_progress')
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    trainee = relationship("User", back_populates="training_sessions")
    script = relationship("TrainingScript", back_populates="sessions")
    assessment = relationship("TrainingAssessment", back_populates="session", uselist=False)


class TrainingAssessment(Base):
    """AI-generated assessments of training sessions"""
    __tablename__ = "training_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('training_sessions.id', ondelete='CASCADE'), nullable=False, unique=True)
    overall_score = Column(Float, nullable=False)  # 0-100
    key_points_covered = Column(JSONB, nullable=False)  # Dict[str, bool]
    strengths = Column(JSONB, nullable=False)  # List[str]
    improvement_areas = Column(JSONB, nullable=False)  # List[str]
    specific_feedback = Column(Text, nullable=False)
    tone_analysis = Column(JSONB, nullable=True)  # Dict[str, float]
    recommendation = Column(String(50), nullable=False)  # 'ready', 'needs_practice', 'needs_coaching'
    ai_model = Column(String(100), nullable=False)
    assessed_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    session = relationship("TrainingSession", back_populates="assessment")


class TraineeProgress(Base):
    """Aggregate progress tracking per trainee per script"""
    __tablename__ = "trainee_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trainee_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    script_id = Column(UUID(as_uuid=True), ForeignKey('training_scripts.id', ondelete='CASCADE'), nullable=False)
    mastery_level = Column(String(50), default='beginner')
    total_sessions = Column(Integer, default=0)
    average_score = Column(Float, nullable=True)
    best_score = Column(Float, nullable=True)
    last_session_at = Column(DateTime(timezone=True), nullable=True)
    certified_at = Column(DateTime(timezone=True), nullable=True)
    certification_level = Column(String(50), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    trainee = relationship("User", back_populates="training_progress")
    script = relationship("TrainingScript", back_populates="progress_records")
```

**Step 2: Update User model with relationships**

Edit `backend/app/models/user.py`, add to User class:

```python
# Training relationships
training_sessions = relationship("TrainingSession", back_populates="trainee")
training_progress = relationship("TraineeProgress", back_populates="trainee")
```

**Step 3: Register models in __init__.py**

Edit `backend/app/models/__init__.py`:

```python
from backend.app.models.training import (
    TrainingScript,
    TrainingSession,
    TrainingAssessment,
    TraineeProgress
)
```

**Step 4: Verify models import**

```bash
cd backend
python -c "from app.models.training import TrainingScript; print('Models loaded successfully')"
```

Expected: "Models loaded successfully"

**Step 5: Commit**

```bash
git add backend/app/models/training.py backend/app/models/user.py backend/app/models/__init__.py
git commit -m "feat: add training system SQLAlchemy models

- TrainingScript model for reference scripts
- TrainingSession model for practice sessions
- TrainingAssessment model for AI evaluations
- TraineeProgress model for aggregate tracking
- Add relationships to User model"
```

---

## Phase 2: AI Assessment Agent

### Task 3: Create Training Assessment Agent

**Files:**
- Create: `backend/app/agents/specialized/training_assessor.py`
- Reference: `backend/app/agents/specialized/credibility_agent_v2.py`

**Step 1: Write the failing test**

Create `backend/tests/unit/test_agents/test_training_assessor.py`:

```python
"""Tests for Training Assessment Agent"""
import pytest
from backend.app.agents.specialized.training_assessor import TrainingAssessorAgent


@pytest.fixture
def reference_script():
    """Sample reference script"""
    return {
        "content": "Hey guys, can you see and hear me ok? Great! How are you guys doing today? Go ahead and grab your spouse/partner, I'm going to get your info pulled up.",
        "key_points": [
            "greeting_and_tech_check",
            "spouse_inclusion",
            "rapport_building",
            "professional_tone"
        ],
        "mastery_criteria": {
            "greeting_and_tech_check": "Must confirm audio/video working before proceeding",
            "spouse_inclusion": "Must explicitly invite spouse to join the call",
            "rapport_building": "Must use warm, conversational tone",
            "professional_tone": "Must thank for service and show respect"
        }
    }


@pytest.fixture
def good_trainee_transcript():
    """Trainee who followed script well"""
    return "Hi there! Can you see and hear me okay? Excellent! How are you both doing today? Please go ahead and have your spouse join us, I'm pulling up your information now."


@pytest.fixture
def poor_trainee_transcript():
    """Trainee who missed key points"""
    return "Hello. Let me get your file. Okay I have your veteran burial benefits request here."


@pytest.mark.asyncio
async def test_assess_good_performance(reference_script, good_trainee_transcript):
    """Should score high when key points are covered"""
    agent = TrainingAssessorAgent()

    assessment = await agent.assess_performance(
        trainee_transcript=good_trainee_transcript,
        reference_script=reference_script["content"],
        key_points=reference_script["key_points"],
        mastery_criteria=reference_script["mastery_criteria"]
    )

    assert assessment["overall_score"] >= 80
    assert assessment["key_points_covered"]["greeting_and_tech_check"] is True
    assert assessment["key_points_covered"]["spouse_inclusion"] is True
    assert assessment["recommendation"] == "ready"
    assert len(assessment["strengths"]) > 0


@pytest.mark.asyncio
async def test_assess_poor_performance(reference_script, poor_trainee_transcript):
    """Should score low and identify gaps when key points missed"""
    agent = TrainingAssessorAgent()

    assessment = await agent.assess_performance(
        trainee_transcript=poor_trainee_transcript,
        reference_script=reference_script["content"],
        key_points=reference_script["key_points"],
        mastery_criteria=reference_script["mastery_criteria"]
    )

    assert assessment["overall_score"] < 60
    assert assessment["key_points_covered"]["greeting_and_tech_check"] is False
    assert assessment["key_points_covered"]["spouse_inclusion"] is False
    assert assessment["recommendation"] in ["needs_practice", "needs_coaching"]
    assert len(assessment["improvement_areas"]) > 0


@pytest.mark.asyncio
async def test_tone_analysis(reference_script, good_trainee_transcript):
    """Should analyze tone and confidence"""
    agent = TrainingAssessorAgent()

    assessment = await agent.assess_performance(
        trainee_transcript=good_trainee_transcript,
        reference_script=reference_script["content"],
        key_points=reference_script["key_points"],
        mastery_criteria=reference_script["mastery_criteria"]
    )

    assert "tone_analysis" in assessment
    assert "warmth" in assessment["tone_analysis"]
    assert "confidence" in assessment["tone_analysis"]
    assert "professionalism" in assessment["tone_analysis"]
```

**Step 2: Run test to verify it fails**

```bash
pytest backend/tests/unit/test_agents/test_training_assessor.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'backend.app.agents.specialized.training_assessor'"

**Step 3: Implement the agent**

Create `backend/app/agents/specialized/training_assessor.py`:

```python
"""AI Agent for assessing veteran lead training performance"""
import anthropic
import os
from typing import Dict, List, Any
import json


class TrainingAssessorAgent:
    """Assesses trainee performance against reference scripts using Claude"""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

    async def assess_performance(
        self,
        trainee_transcript: str,
        reference_script: str,
        key_points: List[str],
        mastery_criteria: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Assess trainee's performance against reference script

        Returns:
            {
                "overall_score": float (0-100),
                "key_points_covered": Dict[str, bool],
                "strengths": List[str],
                "improvement_areas": List[str],
                "specific_feedback": str,
                "tone_analysis": Dict[str, float],
                "recommendation": str  # 'ready', 'needs_practice', 'needs_coaching'
            }
        """

        prompt = self._build_assessment_prompt(
            trainee_transcript,
            reference_script,
            key_points,
            mastery_criteria
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse structured response
        assessment_text = response.content[0].text
        assessment = self._parse_assessment(assessment_text)

        return assessment

    def _build_assessment_prompt(
        self,
        trainee_transcript: str,
        reference_script: str,
        key_points: List[str],
        mastery_criteria: Dict[str, str]
    ) -> str:
        """Build the assessment prompt for Claude"""

        criteria_text = "\n".join([
            f"- {key}: {criteria}"
            for key, criteria in mastery_criteria.items()
        ])

        return f"""You are an expert trainer evaluating a veteran benefits sales representative's performance.

REFERENCE SCRIPT (what they should say):
{reference_script}

KEY POINTS THAT MUST BE COVERED:
{", ".join(key_points)}

MASTERY CRITERIA:
{criteria_text}

TRAINEE'S ACTUAL DELIVERY:
{trainee_transcript}

Assess the trainee's performance and provide a structured evaluation in JSON format:

{{
  "overall_score": <0-100, where 100 is perfect adherence to script>,
  "key_points_covered": {{
    {", ".join([f'"{kp}": true/false' for kp in key_points])}
  }},
  "strengths": [
    "<specific strength 1>",
    "<specific strength 2>"
  ],
  "improvement_areas": [
    "<specific gap 1>",
    "<specific gap 2>"
  ],
  "specific_feedback": "<detailed coaching feedback paragraph>",
  "tone_analysis": {{
    "warmth": <0-10, friendliness and rapport>,
    "confidence": <0-10, certainty and authority>,
    "professionalism": <0-10, respect and polish>,
    "empathy": <0-10, understanding and care>
  }},
  "recommendation": "<'ready', 'needs_practice', or 'needs_coaching'>"
}}

Evaluation criteria for overall_score:
- 90-100: Excellent - Hit all key points with great tone
- 80-89: Good - Hit most key points with good tone
- 70-79: Acceptable - Hit key points but tone needs work
- 60-69: Needs Practice - Missed some key points
- Below 60: Needs Coaching - Missed multiple key points

Be specific in feedback. Quote exact phrases from their delivery. Explain precisely what to improve."""

    def _parse_assessment(self, assessment_text: str) -> Dict[str, Any]:
        """Parse Claude's JSON response into structured assessment"""
        try:
            # Extract JSON from response (may have markdown code blocks)
            if "```json" in assessment_text:
                start = assessment_text.find("```json") + 7
                end = assessment_text.find("```", start)
                json_text = assessment_text[start:end].strip()
            elif "```" in assessment_text:
                start = assessment_text.find("```") + 3
                end = assessment_text.find("```", start)
                json_text = assessment_text[start:end].strip()
            else:
                json_text = assessment_text.strip()

            assessment = json.loads(json_text)

            # Validate required fields
            required_fields = [
                "overall_score", "key_points_covered", "strengths",
                "improvement_areas", "specific_feedback", "recommendation"
            ]
            for field in required_fields:
                if field not in assessment:
                    raise ValueError(f"Missing required field: {field}")

            return assessment

        except (json.JSONDecodeError, ValueError) as e:
            # Fallback if parsing fails
            return {
                "overall_score": 0,
                "key_points_covered": {},
                "strengths": [],
                "improvement_areas": ["Assessment parsing failed - manual review required"],
                "specific_feedback": f"Could not parse AI response: {str(e)}\n\nRaw response:\n{assessment_text}",
                "tone_analysis": {},
                "recommendation": "needs_coaching"
            }
```

**Step 4: Run tests to verify they pass**

```bash
pytest backend/tests/unit/test_agents/test_training_assessor.py -v
```

Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add backend/app/agents/specialized/training_assessor.py backend/tests/unit/test_agents/test_training_assessor.py
git commit -m "feat: implement AI training assessment agent

- Assess trainee performance against reference scripts
- Score key points covered (0-100)
- Analyze tone (warmth, confidence, professionalism, empathy)
- Generate specific coaching feedback
- Recommend ready/practice/coaching status
- Includes comprehensive test coverage"
```

---

## Phase 3: API Endpoints

### Task 4: Create Training API Endpoints

**Files:**
- Create: `backend/app/api/v1/training.py`
- Modify: `backend/app/api/v1/__init__.py`
- Reference: `backend/app/api/v1/meta_analysis.py`

**Step 1: Write the failing test**

Create `backend/tests/integration/test_api/test_training_api.py`:

```python
"""Integration tests for Training API"""
import pytest
from httpx import AsyncClient
from backend.app.main import app
from backend.app.models.training import TrainingScript


@pytest.mark.asyncio
async def test_create_training_script(async_client: AsyncClient, admin_token: str):
    """Should create a training script"""
    response = await async_client.post(
        "/api/v1/training/scripts",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Burial Will Kit Presentation - Part 1",
            "script_type": "presentation",
            "content": "Hey guys, can you see and hear me ok?",
            "key_points": ["greeting_and_tech_check", "spouse_inclusion"],
            "mastery_criteria": {
                "greeting_and_tech_check": "Must confirm audio/video working",
                "spouse_inclusion": "Must invite spouse to join"
            }
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Burial Will Kit Presentation - Part 1"
    assert data["script_type"] == "presentation"
    assert "id" in data


@pytest.mark.asyncio
async def test_start_training_session(async_client: AsyncClient, user_token: str, training_script_id: str):
    """Should start a training session"""
    response = await async_client.post(
        "/api/v1/training/sessions/start",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "script_id": training_script_id,
            "session_type": "practice"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["script_id"] == training_script_id
    assert "id" in data


@pytest.mark.asyncio
async def test_submit_session_for_assessment(
    async_client: AsyncClient,
    user_token: str,
    training_session_id: str
):
    """Should submit session and get AI assessment"""
    response = await async_client.post(
        f"/api/v1/training/sessions/{training_session_id}/submit",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "transcript": "Hi there! Can you see and hear me okay? Please have your spouse join us."
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "assessment" in data
    assert "overall_score" in data["assessment"]
    assert "specific_feedback" in data["assessment"]
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_get_trainee_progress(async_client: AsyncClient, user_token: str):
    """Should return trainee's progress across all scripts"""
    response = await async_client.get(
        "/api/v1/training/progress",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        progress = data[0]
        assert "script_id" in progress
        assert "mastery_level" in progress
        assert "total_sessions" in progress
        assert "average_score" in progress
```

**Step 2: Run test to verify it fails**

```bash
pytest backend/tests/integration/test_api/test_training_api.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'backend.app.api.v1.training'"

**Step 3: Implement the API routes**

Create `backend/app/api/v1/training.py`:

```python
"""Training API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from datetime import datetime

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.training import (
    TrainingScript,
    TrainingSession,
    TrainingAssessment,
    TraineeProgress
)
from backend.app.api.dependencies import get_current_user, get_current_admin_user
from backend.app.agents.specialized.training_assessor import TrainingAssessorAgent
from pydantic import BaseModel


router = APIRouter()


# Request/Response Models
class CreateScriptRequest(BaseModel):
    title: str
    script_type: str
    content: str
    key_points: List[str]
    mastery_criteria: dict


class StartSessionRequest(BaseModel):
    script_id: str
    session_type: str  # 'practice', 'evaluation', 'live'


class SubmitSessionRequest(BaseModel):
    transcript: str
    duration_seconds: int | None = None
    recording_url: str | None = None


@router.post("/scripts", status_code=status.HTTP_201_CREATED)
async def create_training_script(
    request: CreateScriptRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new training script (admin only)"""
    script = TrainingScript(
        title=request.title,
        script_type=request.script_type,
        content=request.content,
        key_points=request.key_points,
        mastery_criteria=request.mastery_criteria
    )

    db.add(script)
    await db.commit()
    await db.refresh(script)

    return {
        "id": str(script.id),
        "title": script.title,
        "script_type": script.script_type,
        "key_points": script.key_points,
        "created_at": script.created_at.isoformat()
    }


@router.get("/scripts")
async def list_training_scripts(
    script_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all active training scripts"""
    query = select(TrainingScript).where(TrainingScript.is_active == True)

    if script_type:
        query = query.where(TrainingScript.script_type == script_type)

    result = await db.execute(query)
    scripts = result.scalars().all()

    return [
        {
            "id": str(script.id),
            "title": script.title,
            "script_type": script.script_type,
            "key_points": script.key_points,
            "version": script.version
        }
        for script in scripts
    ]


@router.post("/sessions/start", status_code=status.HTTP_201_CREATED)
async def start_training_session(
    request: StartSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new training session"""
    # Verify script exists
    script_result = await db.execute(
        select(TrainingScript).where(TrainingScript.id == uuid.UUID(request.script_id))
    )
    script = script_result.scalar_one_or_none()

    if not script:
        raise HTTPException(status_code=404, detail="Training script not found")

    session = TrainingSession(
        trainee_id=current_user.id,
        script_id=script.id,
        session_type=request.session_type,
        started_at=datetime.utcnow(),
        status="in_progress"
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "id": str(session.id),
        "script_id": str(session.script_id),
        "session_type": session.session_type,
        "status": session.status,
        "started_at": session.started_at.isoformat()
    }


@router.post("/sessions/{session_id}/submit")
async def submit_training_session(
    session_id: str,
    request: SubmitSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit session for AI assessment"""
    # Get session
    session_result = await db.execute(
        select(TrainingSession)
        .where(TrainingSession.id == uuid.UUID(session_id))
        .where(TrainingSession.trainee_id == current_user.id)
    )
    session = session_result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")

    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Session already completed")

    # Get script
    script_result = await db.execute(
        select(TrainingScript).where(TrainingScript.id == session.script_id)
    )
    script = script_result.scalar_one()

    # Update session
    session.transcript = request.transcript
    session.duration_seconds = request.duration_seconds
    session.recording_url = request.recording_url
    session.completed_at = datetime.utcnow()
    session.status = "completed"

    # Run AI assessment
    assessor = TrainingAssessorAgent()
    assessment_result = await assessor.assess_performance(
        trainee_transcript=request.transcript,
        reference_script=script.content,
        key_points=script.key_points,
        mastery_criteria=script.mastery_criteria
    )

    # Save assessment
    assessment = TrainingAssessment(
        session_id=session.id,
        overall_score=assessment_result["overall_score"],
        key_points_covered=assessment_result["key_points_covered"],
        strengths=assessment_result["strengths"],
        improvement_areas=assessment_result["improvement_areas"],
        specific_feedback=assessment_result["specific_feedback"],
        tone_analysis=assessment_result.get("tone_analysis"),
        recommendation=assessment_result["recommendation"],
        ai_model="claude-sonnet-4-20250514"
    )

    db.add(assessment)

    # Update progress
    progress_result = await db.execute(
        select(TraineeProgress)
        .where(TraineeProgress.trainee_id == current_user.id)
        .where(TraineeProgress.script_id == script.id)
    )
    progress = progress_result.scalar_one_or_none()

    if not progress:
        progress = TraineeProgress(
            trainee_id=current_user.id,
            script_id=script.id,
            total_sessions=1,
            average_score=assessment_result["overall_score"],
            best_score=assessment_result["overall_score"],
            last_session_at=datetime.utcnow()
        )
        db.add(progress)
    else:
        progress.total_sessions += 1
        # Update average score
        progress.average_score = (
            (progress.average_score * (progress.total_sessions - 1) + assessment_result["overall_score"])
            / progress.total_sessions
        )
        progress.best_score = max(progress.best_score or 0, assessment_result["overall_score"])
        progress.last_session_at = datetime.utcnow()

    # Update mastery level based on average score
    if progress.average_score >= 90:
        progress.mastery_level = "master"
    elif progress.average_score >= 80:
        progress.mastery_level = "advanced"
    elif progress.average_score >= 70:
        progress.mastery_level = "intermediate"
    else:
        progress.mastery_level = "beginner"

    await db.commit()
    await db.refresh(assessment)

    return {
        "id": str(session.id),
        "status": session.status,
        "completed_at": session.completed_at.isoformat(),
        "assessment": {
            "overall_score": assessment.overall_score,
            "key_points_covered": assessment.key_points_covered,
            "strengths": assessment.strengths,
            "improvement_areas": assessment.improvement_areas,
            "specific_feedback": assessment.specific_feedback,
            "tone_analysis": assessment.tone_analysis,
            "recommendation": assessment.recommendation
        }
    }


@router.get("/progress")
async def get_trainee_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trainee's progress across all scripts"""
    result = await db.execute(
        select(TraineeProgress, TrainingScript)
        .join(TrainingScript)
        .where(TraineeProgress.trainee_id == current_user.id)
    )

    records = result.all()

    return [
        {
            "script_id": str(record.TrainingScript.id),
            "script_title": record.TrainingScript.title,
            "script_type": record.TrainingScript.script_type,
            "mastery_level": record.TraineeProgress.mastery_level,
            "total_sessions": record.TraineeProgress.total_sessions,
            "average_score": record.TraineeProgress.average_score,
            "best_score": record.TraineeProgress.best_score,
            "last_session_at": record.TraineeProgress.last_session_at.isoformat() if record.TraineeProgress.last_session_at else None,
            "certified_at": record.TraineeProgress.certified_at.isoformat() if record.TraineeProgress.certified_at else None
        }
        for record in records
    ]


@router.get("/sessions")
async def list_training_sessions(
    script_id: str | None = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List trainee's training sessions"""
    query = (
        select(TrainingSession)
        .where(TrainingSession.trainee_id == current_user.id)
        .order_by(TrainingSession.created_at.desc())
        .limit(limit)
    )

    if script_id:
        query = query.where(TrainingSession.script_id == uuid.UUID(script_id))

    result = await db.execute(query)
    sessions = result.scalars().all()

    return [
        {
            "id": str(session.id),
            "script_id": str(session.script_id),
            "session_type": session.session_type,
            "status": session.status,
            "started_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None
        }
        for session in sessions
    ]
```

**Step 4: Register router in API**

Edit `backend/app/api/v1/__init__.py`:

```python
from backend.app.api.v1 import training

# In the setup_routes() function, add:
app.include_router(training.router, prefix="/api/v1/training", tags=["training"])
```

**Step 5: Run tests to verify they pass**

```bash
pytest backend/tests/integration/test_api/test_training_api.py -v
```

Expected: All tests PASS

**Step 6: Commit**

```bash
git add backend/app/api/v1/training.py backend/app/api/v1/__init__.py backend/tests/integration/test_api/test_training_api.py
git commit -m "feat: add training system API endpoints

- POST /training/scripts - Create training script (admin)
- GET /training/scripts - List active scripts
- POST /training/sessions/start - Start training session
- POST /training/sessions/{id}/submit - Submit for AI assessment
- GET /training/progress - Get trainee progress
- GET /training/sessions - List training sessions
- Includes comprehensive integration tests"
```

---

## Phase 4: Seed Veteran Scripts

### Task 5: Create Script Seeding Command

**Files:**
- Create: `backend/scripts/seed_veteran_scripts.py`

**Step 1: Create seeding script**

```python
"""Seed veteran training scripts from VetScripts directory"""
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.app.models.training import TrainingScript
from backend.app.core.config import settings
import PyPDF2


async def seed_scripts():
    """Seed training scripts from VetScripts"""

    # Create async session
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Script 1: Burial Will Kit Presentation
        burial_script = TrainingScript(
            title="Burial Will Kit Presentation - Complete",
            script_type="presentation",
            content="""
WARM UP (1-2 minutes)
Hey guys, can you see and hear me ok? Great! How are you guys doing today? Go ahead and grab your spouse/partner, I'm going to get your info pulled up. Let me know when you're ready. Before we get started (NAME) what is the reason you filled out the request for your Veteran Burial Benefits? What branch did you serve in?

Well, thank you for your service to our country, I don't think our veterans hear that enough these days, so again thank you!

(If they have a spouse) - Also, (spouse) I want to make sure to thank you for your sacrifice as well because we understand that when one person serves the family does.

What branch did you serve in?
What was your job in the (Branch)?
How connected are you with any of the veterans you may have served with? Do you still stay in touch?
How involved are you with any of the VSO's?

Well (Name)s you're Probably wondering who I am and what we are doing here on a video chat, right? *let them answer* To make sure we don't lose connection - is your device plugged in or fully charged, I know zoom can definitely drain your battery? *let them answer*

Okay, I don't know if I told you over the phone (name) but Globe Life AO takes care of all the permanent benefits for veterans, police, fire fighters. My name is (your name), and I cover the Veterans VSO Benefits.

When we are finished, all this will get emailed to you.

A1: INTRODUCTION
They have me play a quick Video from The National general of The VFW before we get started

[Play Dan West Video]

Ok so here's the thing, I have a waiting List of Thousands of VSO Member's and I know you requested this so I kindly do ask for your Undivided attention for every minute I'm with you is, another minute I'm away from one of my VSO member's requesting my time. Is that fair?

Now (veteran) are you a member of any major VSOs like the VFW, AMVETS, American Legion or any other major Veteran Service Organizations? Do you attend your meetings regularly? So I assume this is the first time someone is getting to sit down and go over everything with you?

A2: COPY OF LETTER (share screen and show safe families letter "GROUP CODE PAVET")

When you submitted your request you received an email or a letter in your email explaining the details of the program, that looks just like this. I'm sure you probably already read through it and have looked it over right? (NOD HEAD YES!)

(IF NO ACT SHOCKED!)

Well, like it says in the letter, my job is to issue your benefits and explain all your options. After I answer all of your questions about your options and help activate your benefits you are eligible for, the veterans service organization would like your opinion on a report form that goes directly back to them. Does that sound fair? Great!

A3: REASONS FOR MEETING ON ZOOM (CONCERNED TONE)

As the letter/email explains, your veterans service organization doesn't know your personal situation, but they've found that all veterans have a very serious gap in their personal burial benefits and estate planning. So what they've done is set up a permanent benefits program for All veterans to fill in the gap, that EVEN the VA does NOT take care of. The VA does a good job of taking care of veterans while they are living and the VSOs ensure that Veterans and their families are taken care of after.

The VFW, AMVETs, and the American Legion all sat at a ROUND table and realized that there were many misconceptions between what most veterans thought they were getting, vs what they ARE actually getting even if They're 100% disabled and/or retired.

So they have us meeting for 1 of 3 reasons:
-First To deliver your Veteran Burial & Will Kit information, and fill out your Veteran Estate preparation Survey.
-Second is the No Veteran Left Behind Program
- Third and Most important Reason is to See if you are able to Qualify for THE VETERANS FINAL EXPENSE BENEFITS that all Veterans are trying to qualify for. I will Let you know right now, it is harder to qualify for than Civilian Life Insurance.

If you're able to qualify today, we will work together to find a plan that covers your family and works with your Lifestyle during your open enrollment period for this is your 1 time shot. I have thousands of VSO members that are actively requesting my time and our services. Does that make sense? *NOD YES*

Let's get started with your veteran survey.
""",
            key_points=[
                "greeting_and_tech_check",
                "spouse_inclusion",
                "thank_for_service",
                "rapport_building",
                "organization_introduction",
                "show_dan_west_video",
                "request_undivided_attention",
                "confirm_vso_membership",
                "show_safe_families_letter",
                "explain_meeting_purpose",
                "three_meeting_reasons",
                "open_enrollment_urgency",
                "transition_to_survey"
            ],
            mastery_criteria={
                "greeting_and_tech_check": "Must confirm audio/video working and device charged before proceeding",
                "spouse_inclusion": "Must explicitly invite spouse/partner to join and wait for them",
                "thank_for_service": "Must thank both veteran and spouse for their service and sacrifice",
                "rapport_building": "Must ask 3-4 personal questions about service, connections, VSO involvement",
                "organization_introduction": "Must introduce Globe Life AO and explain role covering VSO Benefits",
                "show_dan_west_video": "Must announce playing Dan West video from VFW National General",
                "request_undivided_attention": "Must explain busy schedule and respectfully request full attention",
                "confirm_vso_membership": "Must ask about VSO membership and confirm this is first comprehensive review",
                "show_safe_families_letter": "Must screen share and reference the letter they received (GROUP CODE PAVET)",
                "explain_meeting_purpose": "Must explain gap in VA coverage and VSO solution in concerned tone",
                "three_meeting_reasons": "Must clearly state all three meeting reasons: (1) Burial Kit delivery, (2) No Veteran Left Behind, (3) Final Expense Benefits qualification",
                "open_enrollment_urgency": "Must emphasize this is 'one time shot' during open enrollment period",
                "transition_to_survey": "Must smoothly transition to veteran survey after agreement"
            },
            version=1,
            is_active=True
        )

        db.add(burial_script)

        # Script 2: Phone Booking Script
        phone_script = TrainingScript(
            title="PAVET Phone Booking Script",
            script_type="phone_booking",
            content="""
Hi (Name)?... Hi (Name). This is just (Your Name) with AO Globe life and the Veteran Service Organization. I'm calling about the veterans burial guide and will kit you requested. Are you the veteran in the family or did you request this for another family member?

So I'm calling because your veterans burial kit has been processed. It's my job to issue your burial kit and most importantly explain the updated Veteran Burial Benefits and updates Via zoom. The benefits cover you and a spouse or significant other, do you have a spouse or partner that lives with you? Ok and are you retired or still working?

Great, they have your benefits package processed and I just need to explain it for you and (your spouse). It doesn't take long but it is very important to go over your 2024 Veteran Burial Benefits and updates Via zoom. Are you familiar with zoom? Ok, not a problem I can either send you the zoom link via email or if you've downloaded then I can just give you the meeting ID. What is easier for you?

[proceed to walk through zoom]

(IF NOT AVAILABLE)

Oh. Not a problem. I actually work by appointment only. Now what typically works best for you? Mornings, afternoons or evenings? (Proceed to down close two times)

Okay great. I can get this taken care of for you at either (This time) or (This time…)
(Always give them options on the same day or the next day)

I just want to confirm that "time" works for you 100% because me saying yes to you is me saying no to another veteran or their family. Does that make sense? Okay great! We will see you (and your spouse) on (Appointment Time)
""",
            key_points=[
                "greeting_and_identification",
                "kit_processed_statement",
                "spouse_partner_inquiry",
                "employment_status",
                "zoom_familiarity_check",
                "offer_two_timing_options",
                "appointment_confirmation_urgency"
            ],
            mastery_criteria={
                "greeting_and_identification": "Must greet by name and identify as AO Globe Life and VSO representative",
                "kit_processed_statement": "Must state burial kit has been processed and explain need for zoom meeting",
                "spouse_partner_inquiry": "Must ask about spouse/partner and whether they're retired or working",
                "zoom_familiarity_check": "Must confirm zoom familiarity and offer email link or meeting ID options",
                "offer_two_timing_options": "Must always provide exactly two time options, same day or next day",
                "appointment_confirmation_urgency": "Must use 'saying yes to you is saying no to another veteran' language to confirm commitment",
                "professional_tone": "Must maintain warm but professional tone throughout 2-3 minute call"
            },
            version=1,
            is_active=True
        )

        db.add(phone_script)

        await db.commit()

        print("✅ Successfully seeded veteran training scripts:")
        print("   1. Burial Will Kit Presentation - Complete")
        print("   2. PAVET Phone Booking Script")
        print(f"\n   Total key points: {len(burial_script.key_points) + len(phone_script.key_points)}")
        print(f"   Total mastery criteria: {len(burial_script.mastery_criteria) + len(phone_script.mastery_criteria)}")


if __name__ == "__main__":
    asyncio.run(seed_scripts())
```

**Step 2: Run seeding script**

```bash
cd backend
python scripts/seed_veteran_scripts.py
```

Expected output:
```
✅ Successfully seeded veteran training scripts:
   1. Burial Will Kit Presentation - Complete
   2. PAVET Phone Booking Script

   Total key points: 20
   Total mastery criteria: 20
```

**Step 3: Verify scripts in database**

```bash
psql $DATABASE_URL -c "SELECT title, script_type, array_length(key_points, 1) as key_points_count FROM training_scripts;"
```

Expected: Shows 2 scripts with key point counts

**Step 4: Commit**

```bash
git add backend/scripts/seed_veteran_scripts.py
git commit -m "feat: add veteran training scripts seeding

- Seed Burial Will Kit Presentation script (13 key points)
- Seed PAVET Phone Booking Script (7 key points)
- Complete mastery criteria for AI assessment
- Total 20 key points across both scripts"
```

---

## Phase 5: Frontend Training Interface

### Task 6: Create Training Dashboard Page

**Files:**
- Create: `frontend/src/pages/training/index.tsx`
- Create: `frontend/src/components/training/ScriptCard.tsx`
- Create: `frontend/src/components/training/ProgressOverview.tsx`

**Step 1: Create training dashboard page**

```typescript
// frontend/src/pages/training/index.tsx
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import { api } from '@/lib/api'
import ScriptCard from '@/components/training/ScriptCard'
import ProgressOverview from '@/components/training/ProgressOverview'

interface TrainingScript {
  id: string
  title: string
  script_type: string
  key_points: string[]
  version: number
}

interface TraineeProgress {
  script_id: string
  script_title: string
  script_type: string
  mastery_level: string
  total_sessions: number
  average_score: number | null
  best_score: number | null
  last_session_at: string | null
}

export default function TrainingDashboard() {
  const router = useRouter()
  const [scripts, setScripts] = useState<TrainingScript[]>([])
  const [progress, setProgress] = useState<TraineeProgress[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTrainingData()
  }, [])

  const loadTrainingData = async () => {
    try {
      const [scriptsRes, progressRes] = await Promise.all([
        api.get('/training/scripts'),
        api.get('/training/progress')
      ])
      setScripts(scriptsRes.data)
      setProgress(progressRes.data)
    } catch (error) {
      console.error('Failed to load training data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getScriptProgress = (scriptId: string) => {
    return progress.find(p => p.script_id === scriptId)
  }

  const startPractice = async (scriptId: string) => {
    try {
      const response = await api.post('/training/sessions/start', {
        script_id: scriptId,
        session_type: 'practice'
      })
      router.push(`/training/practice/${response.data.id}`)
    } catch (error) {
      console.error('Failed to start practice session:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading training dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Veteran Lead Training</h1>
          <p className="mt-2 text-gray-600">
            Master the presentation scripts and track your progress
          </p>
        </div>

        {/* Progress Overview */}
        <ProgressOverview progress={progress} />

        {/* Training Scripts */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Available Scripts</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {scripts.map(script => (
              <ScriptCard
                key={script.id}
                script={script}
                progress={getScriptProgress(script.id)}
                onStartPractice={() => startPractice(script.id)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
```

**Step 2: Create ScriptCard component**

```typescript
// frontend/src/components/training/ScriptCard.tsx
interface ScriptCardProps {
  script: {
    id: string
    title: string
    script_type: string
    key_points: string[]
  }
  progress?: {
    mastery_level: string
    total_sessions: number
    average_score: number | null
    best_score: number | null
  }
  onStartPractice: () => void
}

const masteryLevelColors = {
  beginner: 'bg-gray-100 text-gray-800',
  intermediate: 'bg-blue-100 text-blue-800',
  advanced: 'bg-purple-100 text-purple-800',
  master: 'bg-green-100 text-green-800'
}

const masteryLevelLabels = {
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  advanced: 'Advanced',
  master: 'Master'
}

export default function ScriptCard({ script, progress, onStartPractice }: ScriptCardProps) {
  const masteryLevel = progress?.mastery_level || 'beginner'

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{script.title}</h3>
          <p className="text-sm text-gray-500 capitalize">{script.script_type}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${masteryLevelColors[masteryLevel]}`}>
          {masteryLevelLabels[masteryLevel]}
        </span>
      </div>

      {/* Key Points */}
      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">
          {script.key_points.length} Key Points to Master
        </p>
      </div>

      {/* Progress Stats */}
      {progress && (
        <div className="grid grid-cols-3 gap-4 mb-4 py-3 border-t border-gray-100">
          <div>
            <p className="text-xs text-gray-500">Sessions</p>
            <p className="text-lg font-semibold text-gray-900">{progress.total_sessions}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Average</p>
            <p className="text-lg font-semibold text-gray-900">
              {progress.average_score ? `${progress.average_score.toFixed(0)}%` : '-'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Best</p>
            <p className="text-lg font-semibold text-gray-900">
              {progress.best_score ? `${progress.best_score.toFixed(0)}%` : '-'}
            </p>
          </div>
        </div>
      )}

      {/* Actions */}
      <button
        onClick={onStartPractice}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        {progress ? 'Practice Again' : 'Start Practice'}
      </button>
    </div>
  )
}
```

**Step 3: Create ProgressOverview component**

```typescript
// frontend/src/components/training/ProgressOverview.tsx
interface ProgressOverviewProps {
  progress: Array<{
    mastery_level: string
    total_sessions: number
    average_score: number | null
  }>
}

export default function ProgressOverview({ progress }: ProgressOverviewProps) {
  const totalSessions = progress.reduce((sum, p) => sum + p.total_sessions, 0)
  const averageScore = progress.length > 0
    ? progress.reduce((sum, p) => sum + (p.average_score || 0), 0) / progress.length
    : 0

  const masteryBreakdown = {
    beginner: progress.filter(p => p.mastery_level === 'beginner').length,
    intermediate: progress.filter(p => p.mastery_level === 'intermediate').length,
    advanced: progress.filter(p => p.mastery_level === 'advanced').length,
    master: progress.filter(p => p.mastery_level === 'master').length
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Progress Overview</h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Total Sessions */}
        <div>
          <p className="text-sm text-gray-600 mb-1">Total Sessions</p>
          <p className="text-3xl font-bold text-gray-900">{totalSessions}</p>
        </div>

        {/* Average Score */}
        <div>
          <p className="text-sm text-gray-600 mb-1">Average Score</p>
          <p className="text-3xl font-bold text-blue-600">
            {averageScore > 0 ? `${averageScore.toFixed(0)}%` : '-'}
          </p>
        </div>

        {/* Scripts in Progress */}
        <div>
          <p className="text-sm text-gray-600 mb-1">Scripts in Progress</p>
          <p className="text-3xl font-bold text-gray-900">{progress.length}</p>
        </div>

        {/* Mastered Scripts */}
        <div>
          <p className="text-sm text-gray-600 mb-1">Mastered Scripts</p>
          <p className="text-3xl font-bold text-green-600">{masteryBreakdown.master}</p>
        </div>
      </div>

      {/* Mastery Level Breakdown */}
      {progress.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-100">
          <p className="text-sm font-medium text-gray-700 mb-3">Mastery Level Distribution</p>
          <div className="flex gap-2">
            {masteryBreakdown.beginner > 0 && (
              <div className="px-3 py-1 bg-gray-100 text-gray-800 rounded text-sm">
                {masteryBreakdown.beginner} Beginner
              </div>
            )}
            {masteryBreakdown.intermediate > 0 && (
              <div className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                {masteryBreakdown.intermediate} Intermediate
              </div>
            )}
            {masteryBreakdown.advanced > 0 && (
              <div className="px-3 py-1 bg-purple-100 text-purple-800 rounded text-sm">
                {masteryBreakdown.advanced} Advanced
              </div>
            )}
            {masteryBreakdown.master > 0 && (
              <div className="px-3 py-1 bg-green-100 text-green-800 rounded text-sm">
                {masteryBreakdown.master} Master
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
```

**Step 4: Test the page loads**

```bash
cd frontend
npm run dev
```

Navigate to http://localhost:3000/training

Expected: Training dashboard renders with scripts and progress

**Step 5: Commit**

```bash
git add frontend/src/pages/training/index.tsx frontend/src/components/training/
git commit -m "feat: add training dashboard UI

- Training dashboard page with script cards
- Progress overview component with stats
- ScriptCard component with mastery levels
- Start practice session functionality
- Responsive grid layout"
```

---

## Phase 6: Practice Session Interface

### Task 7: Create Practice Session Page

**Files:**
- Create: `frontend/src/pages/training/practice/[sessionId].tsx`
- Create: `frontend/src/components/training/ScriptViewer.tsx`
- Create: `frontend/src/components/training/TranscriptRecorder.tsx`

**Step 1: Create practice session page**

```typescript
// frontend/src/pages/training/practice/[sessionId].tsx
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import { api } from '@/lib/api'
import ScriptViewer from '@/components/training/ScriptViewer'
import TranscriptRecorder from '@/components/training/TranscriptRecorder'

interface TrainingSession {
  id: string
  script_id: string
  status: string
}

interface TrainingScript {
  id: string
  title: string
  content: string
  key_points: string[]
}

export default function PracticeSession() {
  const router = useRouter()
  const { sessionId } = router.query
  const [session, setSession] = useState<TrainingSession | null>(null)
  const [script, setScript] = useState<TrainingScript | null>(null)
  const [transcript, setTranscript] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (sessionId) {
      loadSession()
    }
  }, [sessionId])

  const loadSession = async () => {
    try {
      // In real implementation, would fetch session details from API
      // For now, fetch script list and find the one for this session
      const scriptsRes = await api.get('/training/scripts')
      setScript(scriptsRes.data[0]) // Simplified - would match to session
    } catch (error) {
      console.error('Failed to load session:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async () => {
    if (!transcript.trim()) {
      alert('Please record or enter your practice transcript first')
      return
    }

    setSubmitting(true)
    try {
      const response = await api.post(`/training/sessions/${sessionId}/submit`, {
        transcript,
        duration_seconds: Math.floor(transcript.length / 5) // Rough estimate
      })

      // Navigate to results page
      router.push(`/training/results/${sessionId}`)
    } catch (error) {
      console.error('Failed to submit session:', error)
      alert('Failed to submit for assessment. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading practice session...</p>
        </div>
      </div>
    )
  }

  if (!script) {
    return <div>Script not found</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/training')}
            className="text-blue-600 hover:text-blue-800 mb-4 inline-flex items-center"
          >
            ← Back to Training
          </button>
          <h1 className="text-2xl font-bold text-gray-900">{script.title}</h1>
          <p className="text-gray-600">Practice Session</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Script Reference */}
          <ScriptViewer script={script} />

          {/* Recording Area */}
          <TranscriptRecorder
            transcript={transcript}
            onTranscriptChange={setTranscript}
            onSubmit={handleSubmit}
            submitting={submitting}
          />
        </div>
      </div>
    </div>
  )
}
```

**Step 2: Create ScriptViewer component**

```typescript
// frontend/src/components/training/ScriptViewer.tsx
interface ScriptViewerProps {
  script: {
    title: string
    content: string
    key_points: string[]
  }
}

export default function ScriptViewer({ script }: ScriptViewerProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 h-fit sticky top-8">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Reference Script</h2>

      {/* Key Points */}
      <div className="mb-4 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm font-medium text-blue-900 mb-2">Key Points to Cover:</p>
        <ul className="space-y-1">
          {script.key_points.map((point, index) => (
            <li key={index} className="text-sm text-blue-800 flex items-start">
              <span className="mr-2">•</span>
              <span className="capitalize">{point.replace(/_/g, ' ')}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Script Content */}
      <div className="prose prose-sm max-w-none">
        <div className="whitespace-pre-wrap text-gray-700 text-sm leading-relaxed">
          {script.content}
        </div>
      </div>
    </div>
  )
}
```

**Step 3: Create TranscriptRecorder component**

```typescript
// frontend/src/components/training/TranscriptRecorder.tsx
import { useState } from 'react'

interface TranscriptRecorderProps {
  transcript: string
  onTranscriptChange: (transcript: string) => void
  onSubmit: () => void
  submitting: boolean
}

export default function TranscriptRecorder({
  transcript,
  onTranscriptChange,
  onSubmit,
  submitting
}: TranscriptRecorderProps) {
  const [isRecording, setIsRecording] = useState(false)

  const startRecording = () => {
    // In production, would use Web Speech API or recording library
    setIsRecording(true)
    alert('Voice recording would start here (not implemented in this demo)')
  }

  const stopRecording = () => {
    setIsRecording(false)
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Practice Delivery</h2>

      {/* Recording Controls */}
      <div className="mb-4">
        <div className="flex gap-3 mb-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium inline-flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <circle cx="10" cy="10" r="8" />
              </svg>
              Start Recording
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium inline-flex items-center"
            >
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <rect x="6" y="6" width="8" height="8" />
              </svg>
              Stop Recording
            </button>
          )}
        </div>
        <p className="text-sm text-gray-500">
          Or type your practice script below for assessment
        </p>
      </div>

      {/* Transcript Input */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Practice Transcript
        </label>
        <textarea
          value={transcript}
          onChange={(e) => onTranscriptChange(e.target.value)}
          placeholder="Type or speak your practice delivery here..."
          className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          disabled={submitting}
        />
        <p className="mt-2 text-sm text-gray-500">
          {transcript.length} characters
        </p>
      </div>

      {/* Submit Button */}
      <button
        onClick={onSubmit}
        disabled={!transcript.trim() || submitting}
        className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {submitting ? (
          <span className="inline-flex items-center">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Getting AI Assessment...
          </span>
        ) : (
          'Submit for AI Assessment'
        )}
      </button>
    </div>
  )
}
```

**Step 4: Test practice session flow**

```bash
npm run dev
```

Navigate to training dashboard → Click "Start Practice" → Verify practice page loads

Expected: Can view script, type transcript, submit button enabled when text entered

**Step 5: Commit**

```bash
git add frontend/src/pages/training/practice/ frontend/src/components/training/ScriptViewer.tsx frontend/src/components/training/TranscriptRecorder.tsx
git commit -m "feat: add practice session interface

- Practice session page with script reference
- ScriptViewer component showing key points
- TranscriptRecorder with text input and recording controls
- Submit for AI assessment functionality
- Responsive two-column layout"
```

---

## Phase 7: Assessment Results Interface

### Task 8: Create Assessment Results Page

**Files:**
- Create: `frontend/src/pages/training/results/[sessionId].tsx`
- Create: `frontend/src/components/training/AssessmentResults.tsx`
- Create: `frontend/src/components/training/KeyPointsChecklist.tsx`

**Step 1: Create results page**

```typescript
// frontend/src/pages/training/results/[sessionId].tsx
import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import { api } from '@/lib/api'
import AssessmentResults from '@/components/training/AssessmentResults'
import KeyPointsChecklist from '@/components/training/KeyPointsChecklist'

interface Assessment {
  overall_score: number
  key_points_covered: Record<string, boolean>
  strengths: string[]
  improvement_areas: string[]
  specific_feedback: string
  tone_analysis: {
    warmth: number
    confidence: number
    professionalism: number
    empathy: number
  }
  recommendation: string
}

export default function TrainingResults() {
  const router = useRouter()
  const { sessionId } = router.query
  const [assessment, setAssessment] = useState<Assessment | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (sessionId) {
      loadAssessment()
    }
  }, [sessionId])

  const loadAssessment = async () => {
    try {
      // In real implementation, fetch assessment from API
      // For now, using mock data
      const mockAssessment: Assessment = {
        overall_score: 85,
        key_points_covered: {
          greeting_and_tech_check: true,
          spouse_inclusion: true,
          thank_for_service: false,
          rapport_building: true
        },
        strengths: [
          "Excellent greeting and tech check",
          "Successfully included spouse",
          "Good rapport building questions"
        ],
        improvement_areas: [
          "Missing thank you for service",
          "Could be more conversational"
        ],
        specific_feedback: "Great job! You hit most key points...",
        tone_analysis: {
          warmth: 8,
          confidence: 7,
          professionalism: 9,
          empathy: 6
        },
        recommendation: "ready"
      }
      setAssessment(mockAssessment)
    } catch (error) {
      console.error('Failed to load assessment:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Analyzing your performance...</p>
        </div>
      </div>
    )
  }

  if (!assessment) {
    return <div>Assessment not found</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/training')}
            className="text-blue-600 hover:text-blue-800 mb-4 inline-flex items-center"
          >
            ← Back to Training
          </button>
          <h1 className="text-2xl font-bold text-gray-900">AI Assessment Results</h1>
        </div>

        <div className="space-y-6">
          {/* Assessment Results */}
          <AssessmentResults assessment={assessment} />

          {/* Key Points Checklist */}
          <KeyPointsChecklist keyPointsCovered={assessment.key_points_covered} />

          {/* Actions */}
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/training')}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Practice Another Script
            </button>
            <button
              onClick={() => router.push(`/training/practice/${sessionId}`)}
              className="flex-1 px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Practice This Again
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
```

**Step 2: Create AssessmentResults component**

```typescript
// frontend/src/components/training/AssessmentResults.tsx
interface AssessmentResultsProps {
  assessment: {
    overall_score: number
    strengths: string[]
    improvement_areas: string[]
    specific_feedback: string
    tone_analysis: {
      warmth: number
      confidence: number
      professionalism: number
      empathy: number
    }
    recommendation: string
  }
}

const recommendationConfig = {
  ready: {
    color: 'bg-green-100 text-green-800 border-green-200',
    label: 'Ready for Live Calls',
    icon: '✓'
  },
  needs_practice: {
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    label: 'Needs More Practice',
    icon: '⚠'
  },
  needs_coaching: {
    color: 'bg-red-100 text-red-800 border-red-200',
    label: 'Needs Coaching',
    icon: '!'
  }
}

export default function AssessmentResults({ assessment }: AssessmentResultsProps) {
  const recommendation = recommendationConfig[assessment.recommendation]
  const scoreColor = assessment.overall_score >= 80 ? 'text-green-600' :
                      assessment.overall_score >= 70 ? 'text-yellow-600' :
                      'text-red-600'

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      {/* Score & Recommendation */}
      <div className="flex items-center justify-between mb-6 pb-6 border-b border-gray-200">
        <div>
          <p className="text-sm text-gray-600 mb-1">Overall Score</p>
          <p className={`text-5xl font-bold ${scoreColor}`}>
            {assessment.overall_score}%
          </p>
        </div>
        <div className={`px-6 py-3 rounded-lg border-2 ${recommendation.color}`}>
          <span className="text-2xl mr-2">{recommendation.icon}</span>
          <span className="font-semibold">{recommendation.label}</span>
        </div>
      </div>

      {/* Tone Analysis */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Tone Analysis</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(assessment.tone_analysis).map(([key, value]) => (
            <div key={key}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-gray-600 capitalize">{key}</span>
                <span className="text-sm font-semibold text-gray-900">{value}/10</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${value * 10}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Strengths */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Strengths</h3>
        <ul className="space-y-2">
          {assessment.strengths.map((strength, index) => (
            <li key={index} className="flex items-start text-gray-700">
              <span className="text-green-500 mr-2">✓</span>
              <span>{strength}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Improvement Areas */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Areas for Improvement</h3>
        <ul className="space-y-2">
          {assessment.improvement_areas.map((area, index) => (
            <li key={index} className="flex items-start text-gray-700">
              <span className="text-yellow-500 mr-2">→</span>
              <span>{area}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Specific Feedback */}
      <div className="p-4 bg-blue-50 rounded-lg">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">Detailed Coaching Feedback</h3>
        <p className="text-sm text-blue-800 leading-relaxed">{assessment.specific_feedback}</p>
      </div>
    </div>
  )
}
```

**Step 3: Create KeyPointsChecklist component**

```typescript
// frontend/src/components/training/KeyPointsChecklist.tsx
interface KeyPointsChecklistProps {
  keyPointsCovered: Record<string, boolean>
}

export default function KeyPointsChecklist({ keyPointsCovered }: KeyPointsChecklistProps) {
  const totalPoints = Object.keys(keyPointsCovered).length
  const coveredPoints = Object.values(keyPointsCovered).filter(Boolean).length
  const coveragePercent = (coveredPoints / totalPoints) * 100

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Key Points Coverage</h3>
        <span className="text-sm font-medium text-gray-600">
          {coveredPoints} / {totalPoints} covered ({coveragePercent.toFixed(0)}%)
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-3 mb-6">
        <div
          className="bg-blue-600 h-3 rounded-full transition-all"
          style={{ width: `${coveragePercent}%` }}
        />
      </div>

      {/* Checklist */}
      <div className="space-y-3">
        {Object.entries(keyPointsCovered).map(([point, covered]) => (
          <div
            key={point}
            className={`flex items-center p-3 rounded-lg border-2 ${
              covered
                ? 'bg-green-50 border-green-200'
                : 'bg-red-50 border-red-200'
            }`}
          >
            <div className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 ${
              covered ? 'bg-green-500' : 'bg-red-500'
            }`}>
              {covered ? (
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <span className={`capitalize font-medium ${
              covered ? 'text-green-900' : 'text-red-900'
            }`}>
              {point.replace(/_/g, ' ')}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
```

**Step 4: Test results page**

```bash
npm run dev
```

Navigate to `/training/results/test-session-id`

Expected: Assessment results display with score, strengths, improvements, key points checklist

**Step 5: Commit**

```bash
git add frontend/src/pages/training/results/ frontend/src/components/training/AssessmentResults.tsx frontend/src/components/training/KeyPointsChecklist.tsx
git commit -m "feat: add AI assessment results interface

- Assessment results page with overall score
- Tone analysis visualization (warmth, confidence, etc)
- Strengths and improvement areas display
- Key points coverage checklist
- Recommendation status (ready/practice/coaching)
- Practice again and return to dashboard actions"
```

---

## Success Criteria

✅ **Database Schema Complete**
- Training scripts, sessions, assessments, and progress tables created
- Relationships established with User model
- Indexes for performance

✅ **AI Assessment Agent Working**
- Evaluates trainee transcripts against reference scripts
- Scores 0-100 based on key points coverage
- Analyzes tone (warmth, confidence, professionalism, empathy)
- Generates specific coaching feedback
- Recommends ready/practice/coaching

✅ **API Endpoints Functional**
- Create/list training scripts
- Start/submit training sessions
- AI assessment integration
- Progress tracking

✅ **Veteran Scripts Seeded**
- Burial Will Kit Presentation script (13 key points)
- PAVET Phone Booking Script (7 key points)
- Complete mastery criteria for assessment

✅ **Frontend Training Interface**
- Training dashboard with script cards
- Progress overview with stats
- Practice session interface with script reference
- Assessment results with detailed feedback
- Key points checklist visualization

✅ **AI Assessment Integration**
- Real-time assessment using Claude
- Structured scoring and feedback
- Progress tracking updates after each session
- Mastery level progression

---

## Deployment Notes

**Environment Variables Needed:**
```bash
# Backend
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql+asyncpg://...

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

**Database Migration:**
```bash
cd backend
alembic upgrade head
python scripts/seed_veteran_scripts.py
```

**Testing:**
```bash
# Backend tests
pytest backend/tests/ -v

# Frontend tests (if added)
cd frontend
npm test
```

---

## Next Steps After Completion

1. **Voice Recording Integration**
   - Integrate Web Speech API for live recording
   - Add audio file upload support
   - Transcribe audio using Whisper API

2. **Advanced Analytics**
   - Coach dashboard to view all trainees
   - Aggregate performance metrics
   - Certification workflow

3. **Real-time Practice**
   - Live practice sessions with AI prompting
   - Real-time feedback during delivery
   - Interactive role-play scenarios

4. **Mobile App**
   - React Native mobile training app
   - Offline practice mode
   - Push notifications for practice reminders
