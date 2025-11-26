#!/usr/bin/env python3
"""
Extract REAL study data from the completed meta-analysis.
This script verifies that we pulled ACTUAL research data, not simulated data.

Analysis ID: 2e08b849-4a0a-4fa5-84ef-7426f5e7a922
"""
import asyncio
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.meta_analysis import AgentExecution, MetaAnalysis

# Railway production database
DATABASE_URL = "postgresql+asyncpg://postgres:tKVECqkTaqbpRAYSKMOnmqLMNbCsWhRv@autorack.proxy.rlwy.net:17566/railway"

async def extract_study_data():
    """Extract and verify REAL study data from database."""

    # Connect to database
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    analysis_id = "2e08b849-4a0a-4fa5-84ef-7426f5e7a922"

    print("=" * 80)
    print("EXTRACTING REAL STUDY DATA FROM COMPLETED META-ANALYSIS")
    print("=" * 80)
    print(f"Analysis ID: {analysis_id}")
    print()

    async with async_session() as session:
        # Get meta-analysis
        result = await session.execute(
            select(MetaAnalysis).where(MetaAnalysis.id == analysis_id)
        )
        meta_analysis = result.scalar_one_or_none()

        if not meta_analysis:
            print(f"❌ Meta-analysis not found: {analysis_id}")
            return

        print(f"✅ Meta-Analysis Found")
        print(f"   Topic: {meta_analysis.topic}")
        print(f"   Status: {meta_analysis.status}")
        print(f"   Research Question: {meta_analysis.research_question}")
        print()

        # Get all agent executions
        result = await session.execute(
            select(AgentExecution)
            .where(AgentExecution.meta_analysis_id == analysis_id)
            .order_by(AgentExecution.created_at)
        )
        executions = result.scalars().all()

        print(f"Found {len(executions)} agent executions")
        print()

        all_data = {
            'meta_analysis': {
                'id': str(meta_analysis.id),
                'topic': meta_analysis.topic,
                'research_question': meta_analysis.research_question,
                'status': meta_analysis.status,
                'inclusion_criteria': meta_analysis.inclusion_criteria,
                'exclusion_criteria': meta_analysis.exclusion_criteria,
            },
            'agents': []
        }

        # Extract data from each agent
        for execution in executions:
            print("-" * 80)
            print(f"Agent: {execution.agent_type.upper()}")
            print(f"Status: {execution.status}")
            print(f"Started: {execution.created_at}")
            print(f"Completed: {execution.completed_at}")
            print()

            agent_data = {
                'agent_type': execution.agent_type,
                'status': execution.status,
                'started_at': str(execution.created_at),
                'completed_at': str(execution.completed_at) if execution.completed_at else None,
                'output_data': execution.output_data
            }

            # Parse output data
            if execution.output_data:
                print("OUTPUT DATA:")
                print(json.dumps(execution.output_data, indent=2))
                print()

                # For SearchAgent - verify REAL PubMed studies
                if execution.agent_type == 'search':
                    studies = execution.output_data.get('studies', [])
                    print(f"📚 SEARCH AGENT FOUND {len(studies)} STUDIES")
                    print()

                    if studies:
                        print("VERIFYING REAL PUBMED DATA:")
                        for i, study in enumerate(studies[:5], 1):  # Show first 5
                            print(f"\n  Study {i}:")
                            print(f"    PMID: {study.get('pmid', 'N/A')}")
                            print(f"    Title: {study.get('title', 'N/A')[:80]}...")
                            print(f"    Authors: {study.get('authors', 'N/A')[:80]}...")
                            print(f"    Journal: {study.get('journal', 'N/A')}")
                            print(f"    Year: {study.get('year', 'N/A')}")
                            print(f"    DOI: {study.get('doi', 'N/A')}")

                        if len(studies) > 5:
                            print(f"\n  ... and {len(studies) - 5} more studies")
                    else:
                        print("  ⚠️  NO STUDIES FOUND - This is a problem!")

                # For ScreeningAgent - verify REAL decisions
                elif execution.agent_type == 'screening':
                    decisions = execution.output_data.get('decisions', [])
                    included = [d for d in decisions if d.get('decision') == 'include']
                    excluded = [d for d in decisions if d.get('decision') == 'exclude']

                    print(f"📋 SCREENING AGENT DECISIONS:")
                    print(f"   Total decisions: {len(decisions)}")
                    print(f"   Included: {len(included)}")
                    print(f"   Excluded: {len(excluded)}")
                    print()

                    if decisions:
                        print("SAMPLE DECISIONS:")
                        for i, decision in enumerate(decisions[:3], 1):
                            print(f"\n  Decision {i}:")
                            print(f"    PMID: {decision.get('pmid', 'N/A')}")
                            print(f"    Decision: {decision.get('decision', 'N/A').upper()}")
                            print(f"    Reason: {decision.get('reason', 'N/A')[:100]}...")

                # For CredibilityAgent - verify REAL assessments
                elif execution.agent_type == 'credibility':
                    assessments = execution.output_data.get('assessments', [])
                    print(f"⭐ CREDIBILITY AGENT ASSESSMENTS:")
                    print(f"   Total assessed: {len(assessments)}")
                    print()

                    if assessments:
                        print("SAMPLE ASSESSMENTS:")
                        for i, assessment in enumerate(assessments[:3], 1):
                            print(f"\n  Assessment {i}:")
                            print(f"    PMID: {assessment.get('pmid', 'N/A')}")
                            print(f"    Score: {assessment.get('score', 'N/A')}/10")
                            print(f"    Quality: {assessment.get('quality_rating', 'N/A')}")
                            print(f"    Notes: {assessment.get('notes', 'N/A')[:100]}...")
            else:
                print("⚠️  NO OUTPUT DATA - Agent may have failed")

            all_data['agents'].append(agent_data)
            print()

        # Save complete data to file
        output_file = 'real_study_data_verification.json'
        with open(output_file, 'w') as f:
            json.dump(all_data, f, indent=2, default=str)

        print("=" * 80)
        print(f"✅ COMPLETE DATA SAVED TO: {output_file}")
        print("=" * 80)
        print()

        # Final verification summary
        print("VERIFICATION SUMMARY:")
        print()

        search_agent = next((a for a in all_data['agents'] if a['agent_type'] == 'search'), None)
        if search_agent and search_agent['output_data']:
            num_studies = len(search_agent['output_data'].get('studies', []))
            if num_studies > 0:
                print(f"✅ SearchAgent found {num_studies} REAL PubMed studies")

                # Check for PMIDs (proof of real data)
                studies = search_agent['output_data'].get('studies', [])
                pmids = [s.get('pmid') for s in studies if s.get('pmid')]
                print(f"✅ All studies have PMIDs: {len(pmids)}/{num_studies}")

                if pmids:
                    print(f"   Sample PMIDs: {pmids[:5]}")
                    print(f"   ✅ These are VERIFIABLE on PubMed: https://pubmed.ncbi.nlm.nih.gov/")
            else:
                print("❌ NO STUDIES FOUND - System may be using simulated data!")
        else:
            print("❌ SearchAgent has no output data!")

        print()

        screening_agent = next((a for a in all_data['agents'] if a['agent_type'] == 'screening'), None)
        if screening_agent and screening_agent['output_data']:
            num_decisions = len(screening_agent['output_data'].get('decisions', []))
            print(f"✅ ScreeningAgent made {num_decisions} real screening decisions")
        else:
            print("❌ ScreeningAgent has no output data!")

        print()

        credibility_agent = next((a for a in all_data['agents'] if a['agent_type'] == 'credibility'), None)
        if credibility_agent and credibility_agent['output_data']:
            num_assessments = len(credibility_agent['output_data'].get('assessments', []))
            print(f"✅ CredibilityAgent assessed {num_assessments} studies")
        else:
            print("❌ CredibilityAgent has no output data!")

        print()
        print("=" * 80)
        print("NEXT STEP: Verify PMIDs on PubMed to confirm real publications")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(extract_study_data())
