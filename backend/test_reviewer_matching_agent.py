"""Test script for ReviewerMatchingAgent.

This script demonstrates the reviewer matching agent's capabilities with
realistic test data.
"""
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

from loguru import logger

from app.agents.base import AgentConfig
from app.agents.specialized.reviewer_matching_agent import ReviewerMatchingAgent
from app.db.session import async_session
from app.models.manuscript import Manuscript, ManuscriptType
from app.models.researcher import Researcher


async def create_test_data(db_session):
    """Create test manuscript and researchers."""
    logger.info("Creating test data...")

    # Create test manuscript
    manuscript = Manuscript(
        id=uuid4(),
        title="Deep Learning for Medical Image Segmentation: A Systematic Review",
        abstract="""This systematic review examines the application of deep learning
        techniques, particularly convolutional neural networks (CNNs) and U-Net
        architectures, for medical image segmentation tasks. We analyze 150 studies
        focusing on brain tumor segmentation, organ segmentation, and lesion detection.
        Our findings show that transformer-based models achieve state-of-the-art
        performance but require extensive training data.""",
        keywords=[
            "deep learning",
            "medical imaging",
            "image segmentation",
            "convolutional neural networks",
            "U-Net",
            "computer vision",
            "healthcare AI",
        ],
        manuscript_type=ManuscriptType.SYSTEMATIC_REVIEW,
        author_names=[
            "Dr. Jane Smith",
            "Dr. John Doe",
            "Prof. Alice Johnson",
        ],
        author_affiliations={
            "Dr. Jane Smith": "Stanford University, Department of Computer Science",
            "Dr. John Doe": "MIT, Computer Science and AI Lab",
            "Prof. Alice Johnson": "Stanford University, School of Medicine",
        },
        status="submitted",
    )
    db_session.add(manuscript)

    # Create diverse pool of researchers
    researchers = []

    # 1. Expert in medical imaging + deep learning (PERFECT MATCH)
    r1 = Researcher(
        id=uuid4(),
        name="Dr. Sarah Chen",
        email="sarah.chen@example.edu",
        institution="UC Berkeley",
        country="United States",
        h_index=35,
        total_citations=5000,
        publication_count=80,
        expertise_keywords=[
            "deep learning",
            "medical imaging",
            "computer vision",
            "CNN",
            "image segmentation",
            "neural networks",
        ],
        research_domains=["machine_learning", "computer_vision", "clinical_medicine"],
        current_workload=2,
        response_rate=0.85,
        estimated_availability=0.8,
        last_review_date=datetime.utcnow().date() - timedelta(days=45),
        total_review_count=25,
    )
    researchers.append(r1)

    # 2. Senior expert in computer vision (GOOD MATCH)
    r2 = Researcher(
        id=uuid4(),
        name="Prof. Michael Brown",
        email="mbrown@example.edu",
        institution="Carnegie Mellon University",
        country="United States",
        h_index=52,
        total_citations=12000,
        publication_count=150,
        expertise_keywords=[
            "computer vision",
            "image processing",
            "deep learning",
            "segmentation",
            "object detection",
        ],
        research_domains=["computer_vision", "machine_learning"],
        current_workload=4,
        response_rate=0.75,
        estimated_availability=0.6,
        last_review_date=datetime.utcnow().date() - timedelta(days=90),
        total_review_count=45,
    )
    researchers.append(r2)

    # 3. Medical imaging specialist (GOOD MATCH)
    r3 = Researcher(
        id=uuid4(),
        name="Dr. Lisa Wang",
        email="lwang@example.edu",
        institution="Johns Hopkins University",
        country="United States",
        h_index=28,
        total_citations=3500,
        publication_count=65,
        expertise_keywords=[
            "medical imaging",
            "radiology",
            "image analysis",
            "machine learning",
            "clinical applications",
        ],
        research_domains=["clinical_medicine", "machine_learning"],
        current_workload=3,
        response_rate=0.80,
        estimated_availability=0.7,
        last_review_date=datetime.utcnow().date() - timedelta(days=60),
        total_review_count=30,
    )
    researchers.append(r3)

    # 4. Junior researcher in ML (MODERATE MATCH - good diversity)
    r4 = Researcher(
        id=uuid4(),
        name="Dr. Raj Patel",
        email="rpatel@example.edu",
        institution="IIT Delhi",
        country="India",
        h_index=12,
        total_citations=800,
        publication_count=25,
        expertise_keywords=[
            "machine learning",
            "deep learning",
            "neural networks",
            "image classification",
        ],
        research_domains=["machine_learning", "computer_vision"],
        current_workload=1,
        response_rate=0.90,
        estimated_availability=0.9,
        last_review_date=datetime.utcnow().date() - timedelta(days=30),
        total_review_count=8,
    )
    researchers.append(r4)

    # 5. European expert (GOOD MATCH - geographic diversity)
    r5 = Researcher(
        id=uuid4(),
        name="Prof. Elena Schmidt",
        email="eschmidt@example.edu",
        institution="ETH Zurich",
        country="Switzerland",
        h_index=40,
        total_citations=7500,
        publication_count=100,
        expertise_keywords=[
            "computer vision",
            "deep learning",
            "medical image analysis",
            "segmentation",
            "3D imaging",
        ],
        research_domains=["computer_vision", "machine_learning", "computational_biology"],
        current_workload=3,
        response_rate=0.82,
        estimated_availability=0.7,
        last_review_date=datetime.utcnow().date() - timedelta(days=75),
        total_review_count=35,
    )
    researchers.append(r5)

    # 6. Overloaded researcher (LOW AVAILABILITY)
    r6 = Researcher(
        id=uuid4(),
        name="Dr. Robert Lee",
        email="rlee@example.edu",
        institution="Oxford University",
        country="United Kingdom",
        h_index=38,
        total_citations=6000,
        publication_count=90,
        expertise_keywords=[
            "deep learning",
            "medical imaging",
            "healthcare AI",
            "image segmentation",
        ],
        research_domains=["machine_learning", "clinical_medicine"],
        current_workload=9,  # Very high workload
        response_rate=0.60,
        estimated_availability=0.2,
        last_review_date=datetime.utcnow().date() - timedelta(days=200),
        total_review_count=50,
    )
    researchers.append(r6)

    # 7. Conflict of interest - same institution as author (SHOULD FLAG)
    r7 = Researcher(
        id=uuid4(),
        name="Dr. Mark Thompson",
        email="mthompson@example.edu",
        institution="Stanford University",  # Same as manuscript author!
        country="United States",
        h_index=30,
        total_citations=4000,
        publication_count=70,
        expertise_keywords=[
            "deep learning",
            "medical imaging",
            "computer vision",
            "neural networks",
        ],
        research_domains=["machine_learning", "computer_vision"],
        current_workload=2,
        response_rate=0.85,
        estimated_availability=0.8,
        last_review_date=datetime.utcnow().date() - timedelta(days=50),
        total_review_count=28,
    )
    researchers.append(r7)

    # 8. NLP expert (POOR MATCH - wrong domain)
    r8 = Researcher(
        id=uuid4(),
        name="Prof. Amy Zhang",
        email="azhang@example.edu",
        institution="University of Washington",
        country="United States",
        h_index=42,
        total_citations=8000,
        publication_count=110,
        expertise_keywords=[
            "natural language processing",
            "text mining",
            "deep learning",
            "transformers",
            "sentiment analysis",
        ],
        research_domains=["nlp", "machine_learning"],
        current_workload=3,
        response_rate=0.78,
        estimated_availability=0.7,
        last_review_date=datetime.utcnow().date() - timedelta(days=80),
        total_review_count=40,
    )
    researchers.append(r8)

    # Add all researchers
    for researcher in researchers:
        db_session.add(researcher)

    await db_session.flush()
    logger.info(f"Created test manuscript and {len(researchers)} researchers")

    return manuscript, researchers


async def test_reviewer_matching():
    """Test the reviewer matching agent."""
    logger.info("=== Testing ReviewerMatchingAgent ===\n")

    async with async_session() as db:
        try:
            # Create test data
            manuscript, researchers = await create_test_data(db)

            # Initialize agent
            config = AgentConfig(
                name="ReviewerMatcher-Test",
                role="verification",  # Will be set to VERIFICATION by agent
                temperature=0.3,
            )
            agent = ReviewerMatchingAgent(config=config, db_session=db)

            logger.info(f"\nMatching reviewers for manuscript: '{manuscript.title[:60]}...'\n")

            # Run matching
            result = await agent.process({
                "manuscript_id": manuscript.id,
                "max_results": 8,
                "min_score": 0.2,
                "db_session": db,
                "diversity_weight": 0.2,
                "require_availability": True,
            })

            # Display results
            logger.info("=" * 80)
            logger.info("REVIEWER MATCHING RESULTS")
            logger.info("=" * 80)

            summary = result.get("summary", {})
            logger.info(f"\nSUMMARY:")
            logger.info(f"  Total matches found: {summary.get('total_matches', 0)}")
            logger.info(f"  Average overall score: {summary.get('average_overall_score', 0):.3f}")
            logger.info(f"  Average expertise score: {summary.get('average_expertise_score', 0):.3f}")
            logger.info(f"  Average availability score: {summary.get('average_availability_score', 0):.3f}")
            logger.info(f"  Conflicts detected: {summary.get('total_conflicts', 0)}")
            logger.info(f"  High confidence matches: {summary.get('high_confidence_count', 0)}")
            logger.info(f"  Unique countries: {summary.get('unique_countries', 0)}")
            logger.info(f"  Unique institutions: {summary.get('unique_institutions', 0)}")

            # Display top matches
            matches = result.get("matches", [])
            logger.info(f"\nTOP REVIEWER MATCHES:")
            logger.info("=" * 80)

            for i, match in enumerate(matches[:5], 1):
                logger.info(f"\n#{i}. {match['researcher_name']} ({match['researcher_institution']})")
                logger.info(f"     Country: {match['researcher_country']}")
                logger.info(f"     Overall Score: {match['overall_score']:.3f}")
                logger.info(f"     - Expertise: {match['expertise_score']:.3f}")
                logger.info(f"     - Availability: {match['availability_score']:.3f}")
                logger.info(f"     - Diversity: {match['diversity_score']:.3f}")
                logger.info(f"     - Conflict Risk: {match['conflict_risk']:.3f}")
                logger.info(f"     Recommendation: {match['recommendation']}")
                logger.info(f"     Confidence: {match['confidence']:.3f}")

                if match['has_conflict']:
                    logger.warning(f"     ⚠️  CONFLICTS: {', '.join(match['conflict_types'])}")

                if match['matching_keywords']:
                    logger.info(f"     Matching keywords: {', '.join(match['matching_keywords'][:5])}")

            # Display detailed reasoning for top match
            if matches:
                logger.info("\n" + "=" * 80)
                logger.info("DETAILED REASONING FOR TOP MATCH:")
                logger.info("=" * 80)
                logger.info(f"\n{matches[0]['reasoning']}")

            # AI decision
            logger.info("\n" + "=" * 80)
            logger.info("AGENT DECISION:")
            logger.info("=" * 80)
            decision = result.get("decision", {})
            logger.info(f"\nDecision: {decision.get('decision', 'N/A')}")
            logger.info(f"Reasoning: {decision.get('reasoning', 'N/A')}")
            logger.info(f"Confidence: {decision.get('confidence', 0):.3f}")

            logger.info("\n" + "=" * 80)
            logger.info("TEST COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)

            # Rollback to clean up test data
            await db.rollback()
            logger.info("\nTest data rolled back (not persisted)")

        except Exception as e:
            logger.error(f"Test failed with error: {e}")
            await db.rollback()
            raise


async def test_direct_matching():
    """Test direct matching without full workflow."""
    logger.info("\n=== Testing Direct Matching (Simplified) ===\n")

    async with async_session() as db:
        try:
            manuscript, researchers = await create_test_data(db)

            config = AgentConfig(
                name="ReviewerMatcher-Direct",
                role="verification",
                temperature=0.3,
            )
            agent = ReviewerMatchingAgent(config=config, db_session=db)

            # Call find_matching_reviewers directly
            matches = await agent.find_matching_reviewers(
                manuscript_id=manuscript.id,
                db_session=db,
                max_results=5,
                min_score=0.3,
            )

            logger.info(f"Found {len(matches)} matching reviewers:\n")

            for i, match in enumerate(matches, 1):
                logger.info(
                    f"{i}. {match['researcher_name']} - "
                    f"Score: {match['overall_score']:.3f} - "
                    f"Rec: {match['recommendation']}"
                )

            await db.rollback()
            logger.info("\nDirect matching test completed")

        except Exception as e:
            logger.error(f"Direct matching test failed: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    # Configure logger
    logger.add(
        "/Users/brandon/meta-analysis-tool/backend/logs/test_reviewer_matching_{time}.log",
        rotation="10 MB",
    )

    # Run tests
    asyncio.run(test_reviewer_matching())
    print("\n" + "=" * 80 + "\n")
    asyncio.run(test_direct_matching())
