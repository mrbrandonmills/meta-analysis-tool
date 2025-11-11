"""Unit tests for Research Direction Agent.

This script tests the ResearchDirectionAgent in isolation without requiring
a running server or database.
"""

import asyncio
import json
from datetime import datetime

from loguru import logger

from app.agents.specialized.research_direction_agent import ResearchDirectionAgent


async def test_agent_initialization():
    """Test that the agent initializes correctly."""
    print("\n" + "="*60)
    print("TEST 1: Agent Initialization")
    print("="*60)

    try:
        agent = ResearchDirectionAgent()
        assert agent is not None
        assert agent.config.name == "ResearchDirectionAgent"
        assert agent.config.temperature == 0.4
        assert agent.config.max_tokens == 8192
        print("✓ Agent initialized successfully")
        print(f"  - Name: {agent.config.name}")
        print(f"  - Model: {agent.config.model}")
        print(f"  - Temperature: {agent.config.temperature}")
        print(f"  - Max tokens: {agent.config.max_tokens}")
        return True
    except Exception as e:
        print(f"✗ Agent initialization failed: {e}")
        return False


async def test_gap_identification():
    """Test gap identification with mock data."""
    print("\n" + "="*60)
    print("TEST 2: Gap Identification")
    print("="*60)

    try:
        agent = ResearchDirectionAgent()

        # Mock meta-analysis results
        mock_results = {
            "research_question": "What is the effect of exercise on depression?",
            "n_studies": 25,
            "pooled_effect": "0.45 (moderate effect)",
            "confidence_interval": {"lower": 0.32, "upper": 0.58},
            "heterogeneity": 65,  # High heterogeneity
            "publication_bias": "Egger test suggests possible publication bias (p=0.03)",
            "key_findings": "Exercise shows moderate effects on depression reduction across studies"
        }

        mock_studies = [
            {"title": "Study 1", "year": 2020, "sample_size": 120},
            {"title": "Study 2", "year": 2021, "sample_size": 85},
            {"title": "Study 3", "year": 2019, "sample_size": 200}
        ]

        print("Identifying gaps in mock meta-analysis...")
        print(f"  - Research question: {mock_results['research_question']}")
        print(f"  - Number of studies: {mock_results['n_studies']}")
        print(f"  - Heterogeneity: {mock_results['heterogeneity']}%")

        gaps = await agent._identify_gaps(
            meta_analysis_results=mock_results,
            research_question=mock_results["research_question"],
            included_studies=mock_studies,
            focus_areas=["methodology", "populations"]
        )

        if gaps and len(gaps) > 0:
            print(f"✓ Identified {len(gaps)} research gaps")
            for i, gap in enumerate(gaps[:3], 1):  # Show first 3
                print(f"\n  Gap {i}:")
                print(f"    - Type: {gap.get('gap_type', 'N/A')}")
                print(f"    - Title: {gap.get('title', 'N/A')[:60]}...")
                print(f"    - Severity: {gap.get('severity', 'N/A')}")
                print(f"    - Impact Potential: {gap.get('impact_potential', 'N/A')}")
            return True
        else:
            print("✗ No gaps identified")
            return False

    except Exception as e:
        print(f"✗ Gap identification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_question_generation():
    """Test research question generation."""
    print("\n" + "="*60)
    print("TEST 3: Research Question Generation")
    print("="*60)

    try:
        agent = ResearchDirectionAgent()

        # Mock gaps
        mock_gaps = [
            {
                "gap_type": "methodology",
                "title": "Lack of longitudinal studies",
                "description": "Most studies are cross-sectional",
                "evidence": "Only 3 of 25 studies used longitudinal designs",
                "severity": "high"
            },
            {
                "gap_type": "population",
                "title": "Limited diversity in samples",
                "description": "Most studies focus on Western populations",
                "evidence": "85% of studies conducted in US/Europe",
                "severity": "critical"
            }
        ]

        mock_results = {
            "n_studies": 25,
            "pooled_effect": "0.45",
            "heterogeneity": 65,
            "publication_bias": "Possible bias detected"
        }

        print("Generating research questions from gaps...")
        print(f"  - Number of gaps: {len(mock_gaps)}")

        questions = await agent._generate_questions(
            gaps_identified=mock_gaps,
            meta_analysis_results=mock_results,
            research_question="What is the effect of exercise on depression?"
        )

        if questions and len(questions) > 0:
            print(f"✓ Generated {len(questions)} research questions")
            for i, q in enumerate(questions[:3], 1):  # Show first 3
                print(f"\n  Question {i}:")
                print(f"    - {q.get('question', 'N/A')[:80]}...")
                print(f"    - Priority: {q.get('priority', 'N/A')}")
                print(f"    - Feasibility: {q.get('feasibility', 'N/A')}")
                print(f"    - Novelty: {q.get('novelty_score', 'N/A')}")
            return True
        else:
            print("✗ No questions generated")
            return False

    except Exception as e:
        print(f"✗ Question generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_proposal_creation():
    """Test research proposal creation."""
    print("\n" + "="*60)
    print("TEST 4: Research Proposal Creation")
    print("="*60)

    try:
        agent = ResearchDirectionAgent()

        # Mock research question
        mock_question = {
            "question": "Does the duration of exercise intervention moderate its effect on depression?",
            "rationale": "High heterogeneity suggests moderator effects",
            "gap_addressed": "Methodological gap in intervention duration",
            "expected_contribution": "Clarify optimal intervention duration",
            "feasibility": 0.75,
            "novelty_score": 0.65,
            "priority": "high"
        }

        mock_gaps = [
            {
                "gap_type": "methodology",
                "title": "Intervention duration variability",
                "description": "Studies vary widely in intervention duration (4-52 weeks)"
            }
        ]

        mock_results = {
            "research_question": "What is the effect of exercise on depression?",
            "n_studies": 25,
            "key_findings": "Moderate effect size with high heterogeneity"
        }

        print("Creating research proposal...")
        print(f"  - Question: {mock_question['question'][:60]}...")

        proposal = await agent._create_single_proposal(
            question_data=mock_question,
            gaps_identified=mock_gaps,
            meta_analysis_results=mock_results
        )

        if proposal:
            print("✓ Research proposal created successfully")
            print(f"\n  Proposal Details:")
            print(f"    - Title: {proposal.get('title', 'N/A')[:60]}...")
            print(f"    - Design: {proposal.get('methodology', {}).get('design', 'N/A')}")
            print(f"    - Timeline: {proposal.get('timeline', 'N/A')}")
            print(f"    - Feasibility: {proposal.get('feasibility_score', 'N/A')}")
            print(f"    - Impact: {proposal.get('impact_score', 'N/A')}")
            print(f"    - Novelty: {proposal.get('novelty_score', 'N/A')}")
            print(f"    - Budget: {proposal.get('budget_estimate', 'N/A')}")
            return True
        else:
            print("✗ Proposal creation returned None")
            return False

    except Exception as e:
        print(f"✗ Proposal creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_process():
    """Test the complete research direction process."""
    print("\n" + "="*60)
    print("TEST 5: Full Research Direction Process")
    print("="*60)

    try:
        agent = ResearchDirectionAgent()

        # Complete mock input
        input_data = {
            "meta_analysis_results": {
                "research_question": "What is the effectiveness of cognitive behavioral therapy for anxiety disorders?",
                "topic": "CBT for Anxiety",
                "n_studies": 45,
                "pooled_effect": "0.62 (moderate-to-large effect)",
                "confidence_interval": {"lower": 0.48, "upper": 0.76},
                "heterogeneity": 72,
                "publication_bias": "Funnel plot asymmetry detected",
                "key_findings": "CBT shows consistent moderate-to-large effects across anxiety disorders with high heterogeneity"
            },
            "research_question": "What is the effectiveness of cognitive behavioral therapy for anxiety disorders?",
            "included_studies": [
                {"title": f"Study {i}", "year": 2018 + i % 5, "sample_size": 50 + i * 10}
                for i in range(10)
            ],
            "focus_areas": ["methodology", "populations", "outcomes"],
            "max_proposals": 3
        }

        print("Running complete research direction analysis...")
        print(f"  - Research question: {input_data['research_question'][:60]}...")
        print(f"  - Number of studies: {input_data['meta_analysis_results']['n_studies']}")
        print(f"  - Max proposals: {input_data['max_proposals']}")

        result = await agent.process(input_data)

        if result:
            print("✓ Full process completed successfully")
            print(f"\n  Results:")
            print(f"    - Gaps identified: {len(result.get('gaps_identified', []))}")
            print(f"    - Questions generated: {len(result.get('research_questions', []))}")
            print(f"    - Proposals created: {len(result.get('research_proposals', []))}")
            print(f"    - Completeness score: {result.get('completeness_score', 0):.2f}")
            print(f"    - Priority ranking: {len(result.get('priority_ranking', []))} proposals ranked")

            # Validate structure
            assert 'gaps_identified' in result
            assert 'research_questions' in result
            assert 'research_proposals' in result
            assert 'completeness_score' in result

            print("\n  ✓ All expected fields present")
            print("  ✓ Data structure is valid")

            return True
        else:
            print("✗ Process returned None")
            return False

    except Exception as e:
        print(f"✗ Full process failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_helper_methods():
    """Test helper methods."""
    print("\n" + "="*60)
    print("TEST 6: Helper Methods")
    print("="*60)

    try:
        agent = ResearchDirectionAgent()

        # Test _rank_proposals
        mock_proposals = [
            {"title": "Proposal A", "impact_score": 0.8, "feasibility_score": 0.6, "novelty_score": 0.5},
            {"title": "Proposal B", "impact_score": 0.6, "feasibility_score": 0.9, "novelty_score": 0.7},
            {"title": "Proposal C", "impact_score": 0.9, "feasibility_score": 0.5, "novelty_score": 0.8},
        ]

        ranking = agent._rank_proposals(mock_proposals)
        print(f"✓ Proposal ranking: {ranking}")

        # Test _calculate_completeness
        mock_gaps = [{"gap_type": "methodology"} for _ in range(5)]
        mock_questions = [{"question": "Q"} for _ in range(7)]
        mock_proposals_full = [{"title": "P"} for _ in range(3)]

        completeness = agent._calculate_completeness(mock_gaps, mock_questions, mock_proposals_full)
        print(f"✓ Completeness score: {completeness:.3f}")

        # Test _parse_json_response
        test_json = '```json\n{"test": "value"}\n```'
        parsed = agent._parse_json_response(test_json)
        assert parsed == {"test": "value"}
        print("✓ JSON parsing works correctly")

        return True

    except Exception as e:
        print(f"✗ Helper methods test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("RESEARCH DIRECTION AGENT - UNIT TEST SUITE")
    print("=" * 60)

    # Configure logger
    logger.remove()
    logger.add(lambda msg: None)  # Suppress logs during testing

    tests = [
        ("Agent Initialization", test_agent_initialization),
        ("Gap Identification", test_gap_identification),
        ("Question Generation", test_question_generation),
        ("Proposal Creation", test_proposal_creation),
        ("Full Process", test_full_process),
        ("Helper Methods", test_helper_methods),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
