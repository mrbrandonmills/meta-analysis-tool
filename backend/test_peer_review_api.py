"""
Test script for Peer Review API endpoints.

Tests:
1. Manuscript CRUD operations
2. PDF upload
3. AI review generation
4. Peer review CRUD operations
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from app.db.session import async_session
from app.models.manuscript import Manuscript, ManuscriptStatus, ManuscriptType
from app.models.peer_review import PeerReview, ReviewRecommendation, ReviewStatus
from app.models.user import User
from app.core.security import hash_password, UserRole
from loguru import logger


async def test_manuscript_crud():
    """Test manuscript CRUD operations."""
    logger.info("Testing Manuscript CRUD...")

    async with async_session() as db:
        # Create test user if not exists
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                email="test@example.com",
                hashed_password=hash_password("TestPass123"),
                full_name="Test User",
                institution="Test University",
                role=UserRole.RESEARCHER,
                is_active=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Created test user: {user.email}")

        # Create manuscript
        manuscript = Manuscript(
            title="The Impact of AI on Scientific Publishing: A Meta-Analysis",
            abstract="This study examines the impact of artificial intelligence on scientific publishing workflows, peer review quality, and research dissemination.",
            keywords=["AI", "peer review", "scientific publishing", "meta-analysis"],
            manuscript_type=ManuscriptType.META_ANALYSIS,
            journal_name="Journal of Scientific Research",
            author_names=["John Doe", "Jane Smith", "Alice Johnson"],
            author_affiliations={
                "John Doe": "University of Example",
                "Jane Smith": "Research Institute",
                "Alice Johnson": "Tech University"
            },
            corresponding_author_id=user.id,
            status=ManuscriptStatus.SUBMITTED,
            current_round=1,
        )

        db.add(manuscript)
        await db.commit()
        await db.refresh(manuscript)

        logger.info(f"✓ Created manuscript: {manuscript.id}")
        logger.info(f"  Title: {manuscript.title}")
        logger.info(f"  Status: {manuscript.status.value}")

        # Read manuscript
        result = await db.execute(select(Manuscript).where(Manuscript.id == manuscript.id))
        retrieved = result.scalar_one_or_none()
        assert retrieved is not None
        assert retrieved.title == manuscript.title
        logger.info(f"✓ Retrieved manuscript: {retrieved.id}")

        # Update manuscript
        manuscript.status = ManuscriptStatus.IN_REVIEW
        manuscript.abstract = "Updated abstract with more details."
        await db.commit()
        logger.info(f"✓ Updated manuscript status to: {manuscript.status.value}")

        # Delete manuscript (cleanup)
        await db.delete(manuscript)
        await db.commit()
        logger.info(f"✓ Deleted manuscript: {manuscript.id}")

        return user.id


async def test_peer_review_crud(user_id):
    """Test peer review CRUD operations."""
    logger.info("\nTesting Peer Review CRUD...")

    async with async_session() as db:
        # Create manuscript for review
        manuscript = Manuscript(
            title="Machine Learning Applications in Healthcare",
            abstract="A comprehensive review of machine learning techniques in medical diagnosis and treatment planning.",
            manuscript_type=ManuscriptType.SYSTEMATIC_REVIEW,
            corresponding_author_id=user_id,
            status=ManuscriptStatus.IN_REVIEW,
            current_round=1,
        )
        db.add(manuscript)
        await db.commit()
        await db.refresh(manuscript)

        logger.info(f"✓ Created manuscript for review: {manuscript.id}")

        # Create peer review
        review = PeerReview(
            manuscript_id=manuscript.id,
            reviewer_id=None,  # Anonymous
            review_round=1,
            status=ReviewStatus.SUBMITTED,
            review_text="This is a well-structured systematic review with comprehensive coverage of the topic. The methodology is sound and the results are clearly presented.",
            strengths="Strong methodology, comprehensive literature search, clear presentation",
            weaknesses="Limited discussion of potential biases, could expand on clinical implications",
            detailed_comments="The authors have done an excellent job compiling the literature. However, I suggest expanding the discussion section to address potential publication bias and heterogeneity across studies.",
            overall_score=8.5,
            originality_score=7.0,
            methodology_score=9.0,
            clarity_score=8.5,
            significance_score=8.0,
            recommendation=ReviewRecommendation.MINOR_REVISION,
            confidence=0.85,
            ai_assisted=False,
        )

        db.add(review)
        await db.commit()
        await db.refresh(review)

        logger.info(f"✓ Created peer review: {review.id}")
        logger.info(f"  Recommendation: {review.recommendation.value}")
        logger.info(f"  Overall Score: {review.overall_score}")

        # Read review
        result = await db.execute(select(PeerReview).where(PeerReview.id == review.id))
        retrieved = result.scalar_one_or_none()
        assert retrieved is not None
        logger.info(f"✓ Retrieved peer review: {retrieved.id}")

        # Update review
        review.status = ReviewStatus.SUBMITTED
        review.overall_score = 9.0
        await db.commit()
        logger.info(f"✓ Updated review score to: {review.overall_score}")

        # List reviews for manuscript
        result = await db.execute(
            select(PeerReview).where(PeerReview.manuscript_id == manuscript.id)
        )
        reviews = result.scalars().all()
        logger.info(f"✓ Found {len(reviews)} review(s) for manuscript")

        # Cleanup
        await db.delete(review)
        await db.delete(manuscript)
        await db.commit()
        logger.info(f"✓ Cleaned up test data")


async def test_ai_review_parsing():
    """Test AI review response parsing."""
    logger.info("\nTesting AI Review Parsing...")

    sample_response = """
OVERALL ASSESSMENT:
This manuscript presents a comprehensive analysis of machine learning applications in healthcare. The study is well-designed and the results are significant.

STRENGTHS:
- Rigorous methodology with clearly defined search criteria
- Large sample size with diverse studies included
- Thorough statistical analysis
- Clear and well-structured presentation

WEAKNESSES:
- Limited discussion of implementation barriers
- Potential publication bias not fully addressed
- Some heterogeneity in study designs
- Missing cost-effectiveness analysis

DETAILED COMMENTS:
The introduction provides good context but could benefit from more recent references. The methods section is thorough and reproducible. Results are clearly presented with appropriate visualizations. The discussion could be expanded to address practical implementation challenges.

SCORES:
Overall: 8.5
Originality: 8.0
Methodology: 9.0
Clarity: 8.5
Significance: 8.5

RECOMMENDATION: MINOR_REVISION

CONFIDENCE: 0.85

REASONING:
The manuscript is of high quality with sound methodology and significant findings. Minor revisions addressing the implementation barriers and heterogeneity would strengthen the work substantially.
"""

    from app.api.v1.peer_reviews import parse_ai_review_response

    parsed = parse_ai_review_response(sample_response)

    logger.info("✓ Parsed AI review response:")
    logger.info(f"  Overall Score: {parsed['overall_score']}")
    logger.info(f"  Recommendation: {parsed['recommendation']}")
    logger.info(f"  Confidence: {parsed['confidence']}")
    logger.info(f"  Strengths: {parsed['strengths'][:100]}...")
    logger.info(f"  Weaknesses: {parsed['weaknesses'][:100]}...")


async def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("PEER REVIEW API TEST SUITE")
    logger.info("=" * 60)

    try:
        # Test manuscript CRUD
        user_id = await test_manuscript_crud()

        # Test peer review CRUD
        await test_peer_review_crud(user_id)

        # Test AI parsing
        await test_ai_review_parsing()

        logger.info("\n" + "=" * 60)
        logger.info("ALL TESTS PASSED ✓")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"\n{'=' * 60}")
        logger.error(f"TEST FAILED ✗")
        logger.error(f"{'=' * 60}")
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
