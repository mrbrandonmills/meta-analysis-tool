"""Database seed data for development and testing.

Run with: python -m app.db.seeds
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.base import SessionLocal, engine
from app.models import (
    User,
    Project,
    Paper,
    Researcher,
    Manuscript,
    PeerReview,
    ReviewerMatch,
    ResearchGap,
    ResearchProposal,
    Workflow,
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_users(db: Session) -> List[User]:
    """Create sample users."""
    from app.core.security import UserRole

    users = [
        User(
            id=uuid.uuid4(),
            email="admin@academic-platform.com",
            hashed_password=hash_password("Admin123!"),
            full_name="Master Admin",
            institution="Platform Administration",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            is_superuser=True,
        ),
        User(
            id=uuid.uuid4(),
            email="master@meta-analysis.com",
            hashed_password=hash_password("MasterAdmin2024!"),
            full_name="Platform Master Admin",
            institution="Meta-Analysis Platform HQ",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            is_superuser=True,
        ),
        User(
            id=uuid.uuid4(),
            email="researcher@stanford.edu",
            hashed_password=hash_password("Research123!"),
            full_name="Dr. Sarah Chen",
            institution="Stanford University",
            role=UserRole.RESEARCHER,
            is_active=True,
            is_verified=True,
        ),
        User(
            id=uuid.uuid4(),
            email="editor@nature.com",
            hashed_password=hash_password("Editor123!"),
            full_name="Dr. James Wilson",
            institution="Nature Publishing Group",
            role=UserRole.EDITOR,
            is_active=True,
            is_verified=True,
        ),
        User(
            id=uuid.uuid4(),
            email="reviewer@mit.edu",
            hashed_password=hash_password("Review123!"),
            full_name="Dr. Maria Rodriguez",
            institution="MIT",
            role=UserRole.REVIEWER,
            is_active=True,
            is_verified=True,
        ),
    ]

    for user in users:
        db.add(user)

    db.commit()
    db.refresh(users[0])
    print(f"Created {len(users)} users")
    return users


def create_researchers(db: Session) -> List[Researcher]:
    """Create sample researchers."""
    researchers = [
        Researcher(
            id=uuid.uuid4(),
            orcid="0000-0001-1111-1111",
            name="Dr. Alan Turing",
            email="turing@princeton.edu",
            institution="Princeton University",
            department="Computer Science",
            country="USA",
            h_index=42,
            i10_index=85,
            total_citations=5420,
            publication_count=127,
            expertise_keywords=["artificial intelligence", "machine learning", "computation"],
            research_domains=["AI", "Computer Science", "Mathematics"],
            recent_review_count=3,
            total_review_count=18,
            average_review_time_days=21.5,
            estimated_availability=0.7,
            current_workload=2,
            response_rate=0.85,
        ),
        Researcher(
            id=uuid.uuid4(),
            orcid="0000-0002-2222-2222",
            name="Dr. Ada Lovelace",
            email="lovelace@oxford.ac.uk",
            institution="University of Oxford",
            department="Mathematics",
            country="UK",
            h_index=38,
            i10_index=72,
            total_citations=4215,
            publication_count=98,
            expertise_keywords=["algorithms", "programming", "mathematical analysis"],
            research_domains=["Mathematics", "Computer Science"],
            recent_review_count=5,
            total_review_count=25,
            average_review_time_days=18.3,
            estimated_availability=0.6,
            current_workload=3,
            response_rate=0.92,
        ),
        Researcher(
            id=uuid.uuid4(),
            orcid="0000-0003-3333-3333",
            name="Dr. Grace Hopper",
            email="hopper@yale.edu",
            institution="Yale University",
            department="Computer Science",
            country="USA",
            h_index=51,
            i10_index=102,
            total_citations=7830,
            publication_count=156,
            expertise_keywords=["compilers", "programming languages", "software engineering"],
            research_domains=["Computer Science", "Software Engineering"],
            recent_review_count=2,
            total_review_count=32,
            average_review_time_days=15.7,
            estimated_availability=0.8,
            current_workload=1,
            response_rate=0.88,
        ),
    ]

    for researcher in researchers:
        db.add(researcher)

    db.commit()
    print(f"Created {len(researchers)} researchers")
    return researchers


def create_papers(db: Session) -> List[Paper]:
    """Create sample papers."""
    papers = [
        Paper(
            id=uuid.uuid4(),
            title="Attention Is All You Need: Transformer Architecture for Neural Networks",
            abstract="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms...",
            authors=["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
            journal="Neural Information Processing Systems",
            year=2017,
            doi="10.5555/3295222.3295349",
            keywords=["transformers", "attention", "neural networks", "deep learning"],
            database_source="arxiv",
            credibility_level="high",
            credibility_score=0.92,
            citation_count=85432,
            inclusion_status="included",
        ),
        Paper(
            id=uuid.uuid4(),
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            abstract="We introduce BERT, a new language representation model which stands for Bidirectional Encoder Representations from Transformers...",
            authors=["Devlin, J.", "Chang, M.W.", "Lee, K."],
            journal="NAACL-HLT",
            year=2019,
            doi="10.18653/v1/N19-1423",
            pmid="31234567",
            keywords=["BERT", "transformers", "NLP", "pre-training"],
            database_source="pubmed",
            credibility_level="high",
            credibility_score=0.95,
            citation_count=67821,
            inclusion_status="included",
        ),
        Paper(
            id=uuid.uuid4(),
            title="GPT-3: Language Models are Few-Shot Learners",
            abstract="We demonstrate that scaling up language models greatly improves task-agnostic, few-shot performance...",
            authors=["Brown, T.B.", "Mann, B.", "Ryder, N."],
            journal="NeurIPS",
            year=2020,
            arxiv_id="2005.14165",
            keywords=["GPT-3", "language models", "few-shot learning", "large models"],
            database_source="arxiv",
            credibility_level="high",
            credibility_score=0.94,
            citation_count=52341,
            inclusion_status="included",
        ),
        Paper(
            id=uuid.uuid4(),
            title="A Systematic Review of Transformer Applications in Healthcare",
            abstract="This systematic review examines the application of transformer architectures in medical imaging and diagnosis...",
            authors=["Smith, J.", "Johnson, K.", "Williams, P."],
            journal="Journal of Medical AI",
            year=2023,
            doi="10.1234/jmai.2023.001",
            pmid="37123456",
            keywords=["healthcare", "medical AI", "transformers", "diagnosis"],
            database_source="pubmed",
            credibility_level="medium",
            credibility_score=0.78,
            sample_size=1250,
            citation_count=234,
            inclusion_status="screening",
        ),
    ]

    for paper in papers:
        db.add(paper)

    db.commit()
    print(f"Created {len(papers)} papers")
    return papers


def create_projects(db: Session, users: List[User], papers: List[Paper]) -> List[Project]:
    """Create sample projects."""
    researcher = users[1]  # Dr. Sarah Chen

    projects = [
        Project(
            id=uuid.uuid4(),
            user_id=researcher.id,
            tool_type="meta_analysis",
            title="Effectiveness of Transformer Models in NLP Tasks: A Meta-Analysis",
            description="Systematic review and meta-analysis of transformer-based models across various NLP benchmarks",
            status="in_progress",
            config={
                "inclusion_criteria": ["Published 2017-2024", "Peer-reviewed", "English language"],
                "databases": ["PubMed", "arXiv", "IEEE Xplore"],
                "search_terms": ["transformer", "BERT", "GPT", "attention mechanism"],
            },
            findings={
                "total_papers_found": 1247,
                "after_deduplication": 892,
                "after_screening": 156,
                "included_in_analysis": 42,
            },
        ),
        Project(
            id=uuid.uuid4(),
            user_id=researcher.id,
            tool_type="research_direction",
            title="Identifying Research Gaps in AI Ethics",
            description="Gap analysis of current AI ethics research to identify understudied areas",
            status="draft",
            config={
                "focus_areas": ["algorithmic bias", "privacy", "transparency", "accountability"],
                "time_period": "2020-2024",
            },
        ),
    ]

    for project in projects:
        db.add(project)

    db.commit()

    # Associate papers with first project
    if projects and papers:
        from app.models.associations import project_papers
        for paper in papers[:3]:  # Associate first 3 papers
            db.execute(
                project_papers.insert().values(
                    project_id=projects[0].id,
                    paper_id=paper.id,
                    role="included",
                )
            )
        db.commit()

    print(f"Created {len(projects)} projects")
    return projects


def create_manuscripts(db: Session, users: List[User]) -> List[Manuscript]:
    """Create sample manuscripts."""
    author = users[1]  # Dr. Sarah Chen

    manuscripts = [
        Manuscript(
            id=uuid.uuid4(),
            title="Novel Approaches to Few-Shot Learning Using Transformer Architectures",
            abstract="We present a new method for few-shot learning that leverages transformer attention mechanisms...",
            keywords=["few-shot learning", "transformers", "meta-learning"],
            manuscript_type="research_article",
            corresponding_author_id=author.id,
            author_names=["Sarah Chen", "John Doe", "Jane Smith"],
            journal_name="Machine Learning Journal",
            status="in_review",
            current_round=1,
            quality_score=0.85,
            methodology_score=0.88,
            novelty_score=0.82,
        ),
        Manuscript(
            id=uuid.uuid4(),
            title="A Comprehensive Survey of Attention Mechanisms in Deep Learning",
            abstract="This survey provides a comprehensive overview of attention mechanisms used in modern deep learning...",
            keywords=["attention mechanisms", "deep learning", "survey"],
            manuscript_type="review",
            corresponding_author_id=author.id,
            author_names=["Sarah Chen", "Maria Rodriguez"],
            journal_name="AI Review",
            status="desk_review",
            desk_review_decision="send_to_review",
            quality_score=0.91,
        ),
    ]

    for manuscript in manuscripts:
        db.add(manuscript)

    db.commit()
    print(f"Created {len(manuscripts)} manuscripts")
    return manuscripts


def create_reviewer_matches(
    db: Session, manuscripts: List[Manuscript], researchers: List[Researcher]
) -> List[ReviewerMatch]:
    """Create sample reviewer matches."""
    if not manuscripts or not researchers:
        return []

    matches = [
        ReviewerMatch(
            id=uuid.uuid4(),
            manuscript_id=manuscripts[0].id,
            researcher_id=researchers[0].id,  # Dr. Alan Turing
            expertise_score=0.92,
            availability_score=0.75,
            overall_score=0.87,
            rank=1,
            conflict_risk=0.05,
            has_conflict=False,
            matching_keywords=["machine learning", "neural networks", "artificial intelligence"],
            reasoning="High expertise match in machine learning and AI. Good publication record. Available for review.",
            confidence=0.89,
            status="pending",
        ),
        ReviewerMatch(
            id=uuid.uuid4(),
            manuscript_id=manuscripts[0].id,
            researcher_id=researchers[1].id,  # Dr. Ada Lovelace
            expertise_score=0.85,
            availability_score=0.65,
            overall_score=0.78,
            rank=2,
            conflict_risk=0.03,
            has_conflict=False,
            matching_keywords=["algorithms", "mathematical analysis"],
            reasoning="Strong mathematical background. Relevant expertise in algorithms.",
            confidence=0.82,
            status="pending",
        ),
        ReviewerMatch(
            id=uuid.uuid4(),
            manuscript_id=manuscripts[0].id,
            researcher_id=researchers[2].id,  # Dr. Grace Hopper
            expertise_score=0.88,
            availability_score=0.85,
            overall_score=0.87,
            rank=1,
            conflict_risk=0.02,
            has_conflict=False,
            matching_keywords=["software engineering", "programming languages"],
            reasoning="Excellent availability and relevant software engineering expertise.",
            confidence=0.86,
            status="pending",
        ),
    ]

    for match in matches:
        db.add(match)

    db.commit()
    print(f"Created {len(matches)} reviewer matches")
    return matches


def create_research_gaps(db: Session, projects: List[Project]) -> List[ResearchGap]:
    """Create sample research gaps."""
    if not projects:
        return []

    # Find research direction project
    rd_project = next((p for p in projects if p.tool_type == "research_direction"), None)
    if not rd_project:
        return []

    gaps = [
        ResearchGap(
            id=uuid.uuid4(),
            project_id=rd_project.id,
            title="Limited Research on AI Ethics in Non-Western Contexts",
            description="Most AI ethics research focuses on Western perspectives. There is a significant gap in understanding ethical implications in diverse cultural contexts.",
            gap_type="geographic",
            domain="AI Ethics",
            impact_potential=0.89,
            feasibility_score=0.75,
            novelty_score=0.92,
            priority="high",
            geographic_coverage=["North America", "Europe"],
            understudied_populations=["Global South", "Indigenous Communities"],
            reasoning="Literature review shows 87% of AI ethics papers originate from North America and Europe.",
            confidence=0.91,
        ),
        ResearchGap(
            id=uuid.uuid4(),
            project_id=rd_project.id,
            title="Lack of Longitudinal Studies on Algorithmic Bias",
            description="Most bias studies are cross-sectional. Limited research on how algorithmic bias evolves over time.",
            gap_type="methodology",
            domain="Algorithmic Fairness",
            impact_potential=0.85,
            feasibility_score=0.68,
            novelty_score=0.87,
            priority="high",
            temporal_trend="increasing",
            reasoning="Only 3 longitudinal studies found in 5-year literature search.",
            confidence=0.88,
        ),
    ]

    for gap in gaps:
        db.add(gap)

    db.commit()
    print(f"Created {len(gaps)} research gaps")
    return gaps


def create_research_proposals(
    db: Session, projects: List[Project], gaps: List[ResearchGap]
) -> List[ResearchProposal]:
    """Create sample research proposals."""
    if not projects or not gaps:
        return []

    rd_project = next((p for p in projects if p.tool_type == "research_direction"), None)
    if not rd_project:
        return []

    proposals = [
        ResearchProposal(
            id=uuid.uuid4(),
            project_id=rd_project.id,
            gap_id=gaps[0].id if gaps else None,
            title="Cross-Cultural Study of AI Ethics Frameworks",
            proposal_type="grant_application",
            status="draft",
            research_question="How do cultural values influence the development and adoption of AI ethics frameworks across different regions?",
            background="Current AI ethics research predominantly reflects Western values...",
            significance="This research will provide insights into culturally-sensitive AI governance...",
            methodology="Mixed-methods approach combining surveys, interviews, and case studies across 5 continents...",
            expected_impact="Results will inform development of culturally-adaptive AI ethics guidelines...",
            study_design="Comparative case study",
            novelty_score=0.91,
            feasibility_score=0.73,
            impact_score=0.87,
            predicted_citation_count=45.2,
            funding_likelihood=0.68,
            ai_generated=True,
        ),
    ]

    for proposal in proposals:
        db.add(proposal)

    db.commit()
    print(f"Created {len(proposals)} research proposals")
    return proposals


def create_workflows(db: Session, projects: List[Project]) -> List[Workflow]:
    """Create sample workflows."""
    if not projects:
        return []

    meta_project = projects[0]

    workflows = [
        Workflow(
            id=uuid.uuid4(),
            project_id=meta_project.id,
            agent_name="SearchAgent",
            agent_role="search",
            input_data={"query": "transformer language models", "databases": ["PubMed", "arXiv"]},
            output_data={"papers_found": 1247, "databases_searched": 2},
            decisions=[
                {
                    "decision": "Search completed successfully",
                    "reasoning": "Found 1247 papers matching criteria",
                    "confidence": 0.95,
                }
            ],
            status="completed",
            started_at=datetime.utcnow() - timedelta(days=7),
            completed_at=datetime.utcnow() - timedelta(days=7, hours=-1),
            duration_seconds=3620.5,
            confidence_score=0.95,
            quality_score=0.92,
        ),
        Workflow(
            id=uuid.uuid4(),
            project_id=meta_project.id,
            agent_name="ScreeningAgent",
            agent_role="screening",
            input_data={"papers_to_screen": 892, "criteria": "inclusion_criteria"},
            output_data={"papers_included": 156, "papers_excluded": 736},
            decisions=[
                {
                    "decision": "Screening completed",
                    "reasoning": "Applied inclusion/exclusion criteria to 892 papers",
                    "confidence": 0.88,
                }
            ],
            status="completed",
            started_at=datetime.utcnow() - timedelta(days=6),
            completed_at=datetime.utcnow() - timedelta(days=5),
            duration_seconds=7842.3,
            confidence_score=0.88,
            quality_score=0.85,
        ),
        Workflow(
            id=uuid.uuid4(),
            project_id=meta_project.id,
            agent_name="CredibilityAgent",
            agent_role="credibility",
            input_data={"papers_to_assess": 156},
            output_data={"high_quality": 42, "medium_quality": 89, "low_quality": 25},
            status="in_progress",
            started_at=datetime.utcnow() - timedelta(hours=2),
            confidence_score=0.82,
        ),
    ]

    for workflow in workflows:
        db.add(workflow)

    db.commit()
    print(f"Created {len(workflows)} workflows")
    return workflows


def seed_database():
    """Seed the database with sample data."""
    print("Starting database seeding...")

    db = SessionLocal()

    try:
        # Create data in dependency order
        print("\n1. Creating users...")
        users = create_users(db)

        print("\n2. Creating researchers...")
        researchers = create_researchers(db)

        print("\n3. Creating papers...")
        papers = create_papers(db)

        print("\n4. Creating projects...")
        projects = create_projects(db, users, papers)

        print("\n5. Creating workflows...")
        workflows = create_workflows(db, projects)

        print("\n6. Creating manuscripts...")
        manuscripts = create_manuscripts(db, users)

        print("\n7. Creating reviewer matches...")
        matches = create_reviewer_matches(db, manuscripts, researchers)

        print("\n8. Creating research gaps...")
        gaps = create_research_gaps(db, projects)

        print("\n9. Creating research proposals...")
        proposals = create_research_proposals(db, projects, gaps)

        print("\n" + "=" * 60)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nSample Login Credentials:")
        print("-" * 60)
        print("MASTER ADMIN ACCOUNTS:")
        print("  Email: admin@academic-platform.com")
        print("  Password: Admin123!")
        print("")
        print("  Email: master@meta-analysis.com")
        print("  Password: MasterAdmin2024!")
        print("")
        print("REGULAR USERS:")
        print("\nResearcher:")
        print("  Email: researcher@stanford.edu")
        print("  Password: Research123!")
        print("\nEditor:")
        print("  Email: editor@nature.com")
        print("  Password: Editor123!")
        print("\nReviewer:")
        print("  Email: reviewer@mit.edu")
        print("  Password: Review123!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def clear_database():
    """Clear all data from the database (DANGER!)."""
    print("WARNING: This will delete ALL data from the database!")
    response = input("Type 'DELETE ALL DATA' to confirm: ")

    if response != "DELETE ALL DATA":
        print("Aborted.")
        return

    db = SessionLocal()

    try:
        # Delete in reverse dependency order
        print("Deleting all data...")

        # Use the Base metadata to get all tables
        from app.db.base import Base

        for table in reversed(Base.metadata.sorted_tables):
            print(f"  Clearing table: {table.name}")
            db.execute(table.delete())

        db.commit()
        print("All data deleted successfully.")

    except Exception as e:
        print(f"Error during deletion: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        clear_database()
    else:
        seed_database()
