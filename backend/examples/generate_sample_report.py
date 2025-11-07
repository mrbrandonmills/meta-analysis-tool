"""Example script demonstrating APA report generation.

This script shows how to:
1. Generate a complete APA-formatted report
2. Customize sections
3. Create visualizations
4. Export to multiple formats
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.apa_report_generator import APAReportGenerator


def create_sample_analysis_data():
    """Create sample analysis data for demonstration."""
    return {
        "id": "sample-meta-analysis-001",
        "title": "Effects of Mindfulness-Based Interventions on Anxiety: A Meta-Analysis",
        "topic": "mindfulness and anxiety",
        "research_question": "What is the effect of mindfulness-based interventions on anxiety levels in adults?",

        # Study counts
        "num_studies": 25,
        "num_participants": 1847,
        "num_identified": 458,
        "num_screened": 156,

        # Effect sizes and statistics
        "pooled_effect_size": 0.63,
        "ci_lower": 0.48,
        "ci_upper": 0.78,
        "p_value": 0.001,
        "i_squared": 42.3,

        # Methods information
        "year_range": "2010-2024",
        "search_date": "January 15, 2024",
        "databases": ["PubMed", "PsycINFO", "Web of Science", "Cochrane Library"],
        "search_terms": ["mindfulness", "mindfulness-based", "MBSR", "MBCT", "anxiety", "anxious"],
        "inclusion_criteria": [
            "Randomized controlled trials (RCTs)",
            "Adult participants (age 18+)",
            "Mindfulness-based intervention (MBSR, MBCT, or similar)",
            "Validated anxiety outcome measure",
            "Published in peer-reviewed journals",
        ],
        "exclusion_criteria": [
            "Non-English language publications",
            "Qualitative studies",
            "Case studies or case series",
            "Insufficient statistical data for meta-analysis",
        ],
        "analysis_method": "random-effects model",

        # Report metadata
        "authors": ["Smith, John D.", "Jones, Alice B.", "Brown, Katherine L."],
        "institution": "Department of Psychology, University of Research Excellence",
        "author_note": """
John D. Smith, Department of Psychology, University of Research Excellence.

This research was supported by Grant R01-MH123456 from the National Institute
of Mental Health.

Correspondence concerning this article should be addressed to John D. Smith,
Department of Psychology, University of Research Excellence, 123 Research Way,
Research City, RC 12345. Email: john.smith@research.edu
        """,
        "keywords": ["meta-analysis", "mindfulness", "anxiety", "randomized controlled trial", "systematic review"],
        "limitations": [
            "Limited to English-language publications",
            "Moderate heterogeneity across studies (I² = 42.3%)",
            "Potential publication bias cannot be ruled out",
            "Variability in intervention duration and format",
            "Different anxiety measures used across studies",
        ],

        # Individual studies
        "studies": [
            {
                "authors": ["Hofmann, S. G.", "Sawyer, A. T.", "Witt, A. A.", "Oh, D."],
                "year": 2010,
                "title": "The effect of mindfulness-based therapy on anxiety and depression: A meta-analytic review",
                "journal": "Journal of Consulting and Clinical Psychology",
                "volume": 78,
                "issue": 2,
                "pages": "169-183",
                "doi": "10.1037/a0018555",
                "sample_size": 209,
                "design": "RCT",
                "effect_size": 0.59,
                "ci_lower": 0.23,
                "ci_upper": 0.95,
                "standard_error": 0.18,
                "quality_rating": "High",
            },
            {
                "authors": ["Khoury, B.", "Lecomte, T.", "Fortin, G.", "Masse, M."],
                "year": 2013,
                "title": "Mindfulness-based therapy: A comprehensive meta-analysis",
                "journal": "Clinical Psychology Review",
                "volume": 33,
                "issue": 6,
                "pages": "763-771",
                "doi": "10.1016/j.cpr.2013.05.005",
                "sample_size": 142,
                "design": "RCT",
                "effect_size": 0.71,
                "ci_lower": 0.42,
                "ci_upper": 1.00,
                "standard_error": 0.15,
                "quality_rating": "High",
            },
            {
                "authors": ["Goyal, M.", "Singh, S.", "Sibinga, E. M.", "Gould, N. F."],
                "year": 2014,
                "title": "Meditation programs for psychological stress and well-being: A systematic review and meta-analysis",
                "journal": "JAMA Internal Medicine",
                "volume": 174,
                "issue": 3,
                "pages": "357-368",
                "doi": "10.1001/jamainternmed.2013.13018",
                "sample_size": 186,
                "design": "RCT",
                "effect_size": 0.38,
                "ci_lower": 0.12,
                "ci_upper": 0.64,
                "standard_error": 0.13,
                "quality_rating": "Moderate",
            },
            {
                "authors": ["Hoge, E. A.", "Bui, E.", "Marques, L.", "Metcalf, C. A."],
                "year": 2013,
                "title": "Randomized controlled trial of mindfulness meditation for generalized anxiety disorder",
                "journal": "Journal of Clinical Psychiatry",
                "volume": 74,
                "issue": 8,
                "pages": "786-792",
                "doi": "10.4088/JCP.12m08083",
                "sample_size": 89,
                "design": "RCT",
                "effect_size": 0.89,
                "ci_lower": 0.48,
                "ci_upper": 1.30,
                "standard_error": 0.21,
                "quality_rating": "High",
            },
            {
                "authors": ["Kuyken, W.", "Hayes, R.", "Barrett, B.", "Byng, R."],
                "year": 2015,
                "title": "Effectiveness and cost-effectiveness of mindfulness-based cognitive therapy",
                "journal": "The Lancet",
                "volume": 386,
                "issue": 9988,
                "pages": "63-73",
                "doi": "10.1016/S0140-6736(14)62222-4",
                "sample_size": 424,
                "design": "RCT",
                "effect_size": 0.42,
                "ci_lower": 0.18,
                "ci_upper": 0.66,
                "standard_error": 0.12,
                "quality_rating": "High",
            },
        ],
    }


def create_custom_sections():
    """Create custom section content for demonstration."""
    return {
        "abstract": """
Objective: This meta-analysis examined the effectiveness of mindfulness-based
interventions (MBIs) in reducing anxiety symptoms in adult populations.

Method: A systematic search of PubMed, PsycINFO, Web of Science, and Cochrane
Library databases was conducted through January 2024. Included studies were
randomized controlled trials of MBIs with validated anxiety outcome measures.
Effect sizes were pooled using a random-effects model.

Results: Twenty-five studies with 1,847 participants met inclusion criteria.
The pooled effect size indicated a moderate, statistically significant reduction
in anxiety (d = 0.63, 95% CI [0.48, 0.78], p < .001). Heterogeneity was moderate
(I² = 42.3%), suggesting some variability in intervention effects.

Conclusions: MBIs demonstrate consistent efficacy in reducing anxiety symptoms.
These findings support the integration of mindfulness practices into anxiety
treatment protocols. Future research should examine optimal intervention duration
and format.
        """,
        "introduction": """
Anxiety disorders represent one of the most prevalent mental health conditions
worldwide, affecting approximately 264 million people globally (World Health
Organization, 2017). Traditional treatment approaches include cognitive-behavioral
therapy (CBT) and pharmacological interventions. However, these approaches are
not universally effective, and many individuals seek complementary or alternative
treatments.

Mindfulness-based interventions (MBIs) have emerged as promising approaches for
anxiety reduction. Rooted in Buddhist meditation practices, mindfulness involves
paying attention to present-moment experience with an attitude of openness and
acceptance (Kabat-Zinn, 1990). The most well-established MBIs include
Mindfulness-Based Stress Reduction (MBSR; Kabat-Zinn, 1982) and Mindfulness-Based
Cognitive Therapy (MBCT; Segal, Williams, & Teasdale, 2002).

Previous research has suggested that MBIs may reduce anxiety through multiple
mechanisms, including enhanced emotional regulation, decreased rumination, and
improved attention control (Hölzel et al., 2011). However, findings across
individual studies have been inconsistent, with effect sizes ranging from small
to large.

Several narrative reviews and meta-analyses have examined MBIs for anxiety, but
these have been limited by narrow inclusion criteria or outdated search periods.
The present meta-analysis aimed to provide a comprehensive, updated synthesis of
the evidence for MBIs in anxiety reduction.
        """,
    }


def main():
    """Main execution function."""
    print("=" * 80)
    print("APA REPORT GENERATION EXAMPLE")
    print("=" * 80)
    print()

    # Initialize generator
    output_dir = Path(__file__).parent / "sample_reports"
    generator = APAReportGenerator(output_dir=output_dir)

    print(f"Output directory: {output_dir}")
    print()

    # Create sample data
    print("Creating sample analysis data...")
    analysis_data = create_sample_analysis_data()
    print(f"  ✓ Analysis ID: {analysis_data['id']}")
    print(f"  ✓ Number of studies: {analysis_data['num_studies']}")
    print(f"  ✓ Pooled effect size: {analysis_data['pooled_effect_size']}")
    print()

    # Generate report with default content
    print("Generating report with auto-generated content...")
    print("  Format: Word (.docx)")
    result = generator.generate_report(
        analysis_data=analysis_data,
        format="docx",
    )
    print(f"  ✓ Generated: {result['docx_path']}")
    print()

    # Generate report with custom sections
    print("Generating report with custom sections...")
    print("  Format: Both Word and PDF")
    custom_sections = create_custom_sections()
    result = generator.generate_report(
        analysis_data=analysis_data,
        format="both",
        custom_sections=custom_sections,
    )
    print(f"  ✓ Word document: {result['docx_path']}")
    print(f"  ✓ PDF document: {result['pdf_path']}")
    print()

    # Generate visualizations
    print("Generating visualizations...")
    studies = analysis_data["studies"]

    forest_path = generator.generate_forest_plot(studies)
    print(f"  ✓ Forest plot: {forest_path}")

    funnel_path = generator.generate_funnel_plot(studies)
    print(f"  ✓ Funnel plot: {funnel_path}")
    print()

    # Summary
    print("=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print()
    print("Files created:")
    print(f"  1. {output_dir}")
    print(f"     - APA-formatted Word documents")
    print(f"     - Publication-ready PDF documents")
    print(f"     - Forest plot (effect sizes visualization)")
    print(f"     - Funnel plot (publication bias assessment)")
    print()
    print("Next steps:")
    print("  1. Review generated reports")
    print("  2. Customize sections as needed")
    print("  3. Add additional studies or modify data")
    print("  4. Export to your preferred format")
    print()
    print("For API usage, see: docs/APA_REPORT_GENERATION.md")
    print()


if __name__ == "__main__":
    main()
