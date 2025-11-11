"""Test script for ReviewDrafterAgent.

This script demonstrates the ReviewDrafterAgent's capabilities including:
- Generating comprehensive peer reviews
- Analyzing different manuscript types
- Adapting to different expertise levels and review styles
- Producing quantitative scores and recommendations
"""

import asyncio
from pprint import pprint
from uuid import uuid4

from loguru import logger

from app.agents.specialized.review_drafter_agent import (
    ReviewDrafterAgent,
    ExpertiseLevel,
    ReviewStyle,
    FocusArea,
)
from app.agents.base import AgentConfig, AgentRole


# Sample manuscript for testing
SAMPLE_MANUSCRIPT = {
    "id": uuid4(),
    "title": "Machine Learning Approaches for Predicting Treatment Response in Major Depressive Disorder: A Systematic Review and Meta-Analysis",
    "abstract": """
Background: Major depressive disorder (MDD) affects over 300 million people globally, yet predicting treatment response remains challenging. Machine learning (ML) approaches offer promise for personalized treatment selection.

Objective: To systematically review and meta-analyze the performance of ML models in predicting treatment response in MDD.

Methods: We searched PubMed, Embase, PsycINFO, and Web of Science through December 2023. Studies were included if they used ML to predict treatment response in adults with MDD. We extracted data on study design, ML algorithms, input features, and predictive performance (AUC, accuracy, sensitivity, specificity). Meta-analysis was performed using random-effects models.

Results: Twenty-three studies met inclusion criteria, representing 12,847 patients. Common ML algorithms included random forest (n=12), support vector machines (n=8), and neural networks (n=6). Input features varied widely, including clinical (n=23), neuroimaging (n=8), genetic (n=5), and multimodal data (n=7). Pooled AUC for treatment response prediction was 0.74 (95% CI: 0.69-0.79), with substantial heterogeneity (I²=76%). Neuroimaging-based models showed higher performance (AUC=0.79) compared to clinical-only models (AUC=0.71), though this was not statistically significant. Risk of bias assessment revealed concerns about overfitting and lack of external validation in 65% of studies.

Conclusions: ML approaches show moderate promise for predicting MDD treatment response, but methodological limitations and lack of external validation limit clinical applicability. Future research should focus on larger, prospective studies with rigorous validation protocols.
    """,
    "content": """
1. INTRODUCTION

Major depressive disorder (MDD) is a leading cause of disability worldwide, affecting an estimated 322 million people [1]. Despite the availability of numerous treatment options, including pharmacotherapy and psychotherapy, only 30-40% of patients achieve remission with first-line treatment [2]. The trial-and-error approach to treatment selection results in prolonged suffering, increased healthcare costs, and higher risk of treatment-resistant depression [3].

Machine learning (ML) has emerged as a promising tool for precision psychiatry, offering the potential to predict individual treatment responses based on baseline characteristics [4-6]. Unlike traditional statistical approaches, ML algorithms can identify complex, non-linear patterns in high-dimensional data, making them well-suited for integrating multiple data modalities [7].

Several reviews have examined ML in psychiatry broadly [8,9], but no comprehensive meta-analysis has specifically quantified the performance of ML models for predicting treatment response in MDD. This gap in knowledge limits our ability to assess the clinical readiness of these approaches and identify methodological best practices.

The current systematic review and meta-analysis aims to: (1) synthesize evidence on ML approaches for predicting MDD treatment response, (2) quantify their predictive performance, (3) identify factors associated with model performance, and (4) assess methodological quality and risk of bias.

2. METHODS

2.1 Search Strategy
We conducted a systematic search of PubMed, Embase, PsycINFO, and Web of Science from inception through December 31, 2023. The search strategy combined terms related to: (1) major depressive disorder, (2) machine learning, and (3) treatment response or prediction. Full search terms are provided in Supplementary Table 1. We also hand-searched reference lists of included studies and recent reviews.

2.2 Eligibility Criteria
Studies were included if they: (1) enrolled adults (≥18 years) diagnosed with MDD using standardized criteria (DSM-IV/5 or ICD-10/11), (2) used supervised ML algorithms to predict treatment response or remission, (3) reported sufficient data to calculate predictive performance metrics (AUC, accuracy, sensitivity, and/or specificity), and (4) were published in English.

We excluded studies that: (1) focused on other psychiatric disorders, (2) used unsupervised learning only, (3) were conference abstracts without full text, or (4) did not report original data (e.g., reviews, editorials).

2.3 Data Extraction
Two reviewers (ABC, DEF) independently extracted data using a standardized form. Disagreements were resolved through discussion or third-party adjudication (GHI). Extracted variables included: study design, sample size, patient demographics, treatment type, ML algorithm, input features, cross-validation method, performance metrics (AUC, accuracy, sensitivity, specificity), and external validation status.

2.4 Quality Assessment
We assessed risk of bias using a modified version of the PROBAST tool [10], adapted for ML prediction models. Domains included participant selection, predictors, outcome, sample size/overfitting, and analysis. Each domain was rated as low, unclear, or high risk of bias.

2.5 Statistical Analysis
We performed random-effects meta-analysis to pool AUC values across studies using the DerSimonian-Laird method. Heterogeneity was assessed using I² statistics. Subgroup analyses examined differences by algorithm type, input modality, and external validation status. Meta-regression explored associations between sample size and model performance. Publication bias was assessed using funnel plots and Egger's test. All analyses were conducted in R (version 4.2.0) using the 'meta' and 'metafor' packages.

3. RESULTS

3.1 Study Selection
Our search identified 1,847 records. After removing duplicates, 1,203 titles and abstracts were screened, resulting in 94 full-text articles assessed for eligibility. Twenty-three studies met all inclusion criteria and were included in the meta-analysis (Figure 1).

3.2 Study Characteristics
The 23 included studies represented 12,847 unique patients with MDD. Sample sizes ranged from 85 to 2,430 patients (median=342). Fifteen studies (65%) were retrospective analyses of existing cohorts, while eight (35%) were prospective. Treatment modalities included antidepressants (n=18), psychotherapy (n=3), and combination therapy (n=2).

3.3 ML Algorithms and Features
The most common ML algorithms were random forest (n=12, 52%), support vector machines (n=8, 35%), and neural networks (n=6, 26%). Several studies compared multiple algorithms. Input features included clinical/demographic data in all studies, with additional neuroimaging (n=8), genetic (n=5), or multimodal data (n=7).

3.4 Predictive Performance
Pooled AUC for treatment response prediction was 0.74 (95% CI: 0.69-0.79), with substantial heterogeneity (I²=76%, p<0.001) (Figure 2). Pooled accuracy was 71% (95% CI: 67-75%), sensitivity 69% (95% CI: 64-74%), and specificity 72% (95% CI: 67-77%).

Subgroup analyses revealed higher performance for neuroimaging-based models (AUC=0.79, 95% CI: 0.72-0.86) compared to clinical-only models (AUC=0.71, 95% CI: 0.66-0.76), though confidence intervals overlapped. Algorithm type did not significantly predict performance (p=0.43).

Only 8 studies (35%) included external validation. Externally validated models showed lower performance (AUC=0.69) compared to internally validated models (AUC=0.76), suggesting potential overfitting in studies without external validation.

Meta-regression found no significant association between sample size and AUC (β=0.0003, p=0.24), though power was limited.

3.5 Risk of Bias
Risk of bias was high or unclear in most studies. Specific concerns included: small sample sizes relative to the number of features (65%), lack of external validation (65%), inadequate handling of missing data (43%), and insufficient reporting of model details for reproducibility (57%). Only 3 studies (13%) were rated as low risk of bias across all domains.

4. DISCUSSION

This systematic review and meta-analysis represents the first comprehensive quantitative synthesis of ML approaches for predicting treatment response in MDD. Our findings indicate moderate predictive performance (pooled AUC=0.74), with neuroimaging-based models showing promise. However, significant methodological limitations and lack of external validation limit current clinical applicability.

4.1 Interpretation of Findings
The pooled AUC of 0.74 suggests moderate discriminative ability, comparable to prediction models in other medical domains [11]. This level of performance could potentially inform treatment selection, though falls short of the threshold (AUC≥0.80) typically considered necessary for clinical decision-making [12]. The substantial heterogeneity (I²=76%) indicates variability in model performance across studies, likely reflecting differences in populations, treatments, algorithms, and features.

The trend toward better performance with neuroimaging-based models aligns with neurobiological theories of depression, though the lack of statistical significance and small number of studies warrant caution. The performance decrease in externally validated models is concerning and suggests overfitting in many studies—a common problem in ML research with limited sample sizes [13].

4.2 Limitations
Several limitations should be considered. First, included studies varied substantially in design, populations, and methods, limiting comparability. Second, we could not access individual patient data, precluding more sophisticated meta-analytic approaches. Third, most studies were retrospective analyses of convenience samples, limiting generalizability. Fourth, publication bias may inflate reported performance, though our funnel plot analysis showed no significant asymmetry. Finally, rapid advances in ML methodology mean newer techniques may not be well-represented.

4.3 Implications for Research and Practice
For clinical practice, current ML models are not yet ready for routine implementation. The moderate performance, lack of validation, and methodological concerns indicate that more rigorous research is needed before clinical deployment.

For research, our findings highlight several priorities: (1) larger, prospective studies with adequate sample sizes for the number of features, (2) mandatory external validation in independent cohorts, (3) standardized outcome definitions and reporting, (4) multimodal feature integration, and (5) implementation science studies examining real-world integration.

Future research should also explore newer deep learning architectures, particularly those designed to handle missing data and temporal dynamics. Ensemble approaches combining multiple models may improve robustness.

5. CONCLUSIONS

Machine learning shows moderate promise for predicting treatment response in MDD, but methodological limitations currently limit clinical applicability. Larger, rigorously designed studies with external validation are needed to realize the potential of precision psychiatry. Researchers should adhere to reporting guidelines (e.g., TRIPOD) and prioritize reproducibility and clinical utility over novelty alone.

REFERENCES
[1] WHO. Depression and Other Common Mental Disorders. 2017.
[2] Rush AJ, et al. Acute and longer-term outcomes in depressed outpatients requiring one or several treatment steps: a STAR*D report. Am J Psychiatry. 2006.
[3-13] Additional references omitted for brevity...
    """,
    "manuscript_type": "systematic_review",
    "keywords": [
        "machine learning",
        "major depressive disorder",
        "treatment response",
        "prediction",
        "meta-analysis",
        "precision psychiatry",
    ],
    "author_affiliations": {
        "institutions": [
            "Department of Psychiatry, University Medical Center",
            "Institute for Computational Medicine",
        ]
    },
}


async def test_basic_review_generation():
    """Test basic review generation with default settings."""
    logger.info("=" * 80)
    logger.info("TEST 1: Basic Review Generation (Expert, Constructive)")
    logger.info("=" * 80)

    config = AgentConfig(
        name="ReviewDrafter-Test1",
        role=AgentRole.QUALITY_ASSESSMENT,
        temperature=0.3,
    )

    agent = ReviewDrafterAgent(config)

    result = await agent.process(
        {
            "manuscript": SAMPLE_MANUSCRIPT,
            "expertise_level": ExpertiseLevel.EXPERT,
            "review_style": ReviewStyle.CONSTRUCTIVE,
        }
    )

    print("\n" + "=" * 80)
    print("REVIEW SUMMARY")
    print("=" * 80)
    print(f"Recommendation: {result['recommendation'].upper()}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"\nOverall Score: {result['overall_score']}/10")
    print(f"Originality: {result['originality_score']}/10")
    print(f"Methodology: {result['methodology_score']}/10")
    print(f"Clarity: {result['clarity_score']}/10")
    print(f"Significance: {result['significance_score']}/10")

    print(f"\n{'=' * 80}")
    print("STRENGTHS ({})".format(len(result["strengths"])))
    print("=" * 80)
    for i, strength in enumerate(result["strengths"], 1):
        print(f"{i}. {strength}")

    print(f"\n{'=' * 80}")
    print("WEAKNESSES ({})".format(len(result["weaknesses"])))
    print("=" * 80)
    for i, weakness in enumerate(result["weaknesses"], 1):
        print(f"{i}. {weakness}")

    print(f"\n{'=' * 80}")
    print("REASONING FOR RECOMMENDATION")
    print("=" * 80)
    print(result["reasoning"])

    print(f"\n{'=' * 80}")
    print("DETAILED COMMENTS (First 500 chars)")
    print("=" * 80)
    print(result["detailed_comments"][:500] + "...")

    return result


async def test_critical_review_style():
    """Test review generation with critical style."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Critical Review Style")
    logger.info("=" * 80)

    config = AgentConfig(
        name="ReviewDrafter-Critical",
        role=AgentRole.QUALITY_ASSESSMENT,
        temperature=0.3,
    )

    agent = ReviewDrafterAgent(config)

    result = await agent.process(
        {
            "manuscript": SAMPLE_MANUSCRIPT,
            "expertise_level": ExpertiseLevel.EXPERT,
            "review_style": ReviewStyle.CRITICAL,
            "focus_areas": [FocusArea.METHODOLOGY, FocusArea.STATISTICS],
        }
    )

    print("\nCRITICAL REVIEW RESULTS:")
    print(f"Recommendation: {result['recommendation'].upper()}")
    print(f"Methodology Score: {result['methodology_score']}/10")
    print(f"Number of Weaknesses: {len(result['weaknesses'])}")

    return result


async def test_junior_reviewer_perspective():
    """Test review generation from junior reviewer perspective."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Junior Reviewer Perspective")
    logger.info("=" * 80)

    config = AgentConfig(
        name="ReviewDrafter-Junior",
        role=AgentRole.QUALITY_ASSESSMENT,
        temperature=0.4,
    )

    agent = ReviewDrafterAgent(config)

    result = await agent.process(
        {
            "manuscript": SAMPLE_MANUSCRIPT,
            "expertise_level": ExpertiseLevel.JUNIOR,
            "review_style": ReviewStyle.SUPPORTIVE,
        }
    )

    print("\nJUNIOR REVIEWER RESULTS:")
    print(f"Recommendation: {result['recommendation'].upper()}")
    print(f"Confidence: {result['confidence']:.2f}")
    print("\nFirst Strength:")
    print(f"  {result['strengths'][0] if result['strengths'] else 'N/A'}")

    return result


async def test_focused_review():
    """Test review with specific focus areas."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Focused Review (Writing + Novelty)")
    logger.info("=" * 80)

    config = AgentConfig(
        name="ReviewDrafter-Focused",
        role=AgentRole.QUALITY_ASSESSMENT,
        temperature=0.3,
    )

    agent = ReviewDrafterAgent(config)

    result = await agent.process(
        {
            "manuscript": SAMPLE_MANUSCRIPT,
            "expertise_level": ExpertiseLevel.SENIOR,
            "review_style": ReviewStyle.CONSTRUCTIVE,
            "focus_areas": [FocusArea.WRITING, FocusArea.NOVELTY],
        }
    )

    print("\nFOCUSED REVIEW RESULTS:")
    print(f"Clarity Score: {result['clarity_score']}/10")
    print(f"Originality Score: {result['originality_score']}/10")
    print(f"\nRecommendation: {result['recommendation'].upper()}")

    return result


async def test_constructive_suggestions():
    """Test generation of constructive improvement suggestions."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: Constructive Improvement Suggestions")
    logger.info("=" * 80)

    config = AgentConfig(
        name="ReviewDrafter-Suggestions",
        role=AgentRole.QUALITY_ASSESSMENT,
        temperature=0.3,
    )

    agent = ReviewDrafterAgent(config)

    # First generate a review
    review_result = await agent.process(
        {
            "manuscript": SAMPLE_MANUSCRIPT,
            "expertise_level": ExpertiseLevel.EXPERT,
            "review_style": ReviewStyle.CONSTRUCTIVE,
        }
    )

    # Then generate constructive suggestions
    suggestions = await agent.generate_constructive_suggestions(
        weaknesses=review_result["weaknesses"],
        manuscript_context={
            "title": SAMPLE_MANUSCRIPT["title"],
            "type": SAMPLE_MANUSCRIPT["manuscript_type"],
        },
    )

    print("\nCONSTRUCTIVE SUGGESTIONS:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n{i}. Weakness: {suggestion.get('weakness', 'N/A')[:100]}...")
        print(f"   Impact: {suggestion.get('impact', 'N/A')[:100]}...")
        print(f"   Suggestion: {suggestion.get('suggestion', 'N/A')[:100]}...")

    return suggestions


async def run_all_tests():
    """Run all test scenarios."""
    logger.info("Starting ReviewDrafterAgent Comprehensive Tests")

    try:
        # Test 1: Basic review
        result1 = await test_basic_review_generation()

        # Test 2: Critical style
        result2 = await test_critical_review_style()

        # Test 3: Junior perspective
        result3 = await test_junior_reviewer_perspective()

        # Test 4: Focused review
        result4 = await test_focused_review()

        # Test 5: Constructive suggestions
        suggestions = await test_constructive_suggestions()

        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nSummary of Results:")
        print(f"  Test 1 Recommendation: {result1['recommendation']}")
        print(f"  Test 2 Recommendation: {result2['recommendation']}")
        print(f"  Test 3 Recommendation: {result3['recommendation']}")
        print(f"  Test 4 Recommendation: {result4['recommendation']}")
        print(f"  Test 5 Suggestions Generated: {len(suggestions)}")

        return {
            "basic_review": result1,
            "critical_review": result2,
            "junior_review": result3,
            "focused_review": result4,
            "suggestions": suggestions,
        }

    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise


if __name__ == "__main__":
    # Configure logging
    logger.add(
        "/Users/brandon/meta-analysis-tool/logs/review_drafter_test.log",
        rotation="10 MB",
        level="INFO",
    )

    # Run tests
    results = asyncio.run(run_all_tests())

    print("\n" + "=" * 80)
    print("Test execution completed. Check logs for detailed output.")
    print("=" * 80)
