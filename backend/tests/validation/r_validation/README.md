# R Validation Scripts

This directory contains R scripts for cross-validating the Python meta-analysis calculations against the gold-standard R `metafor` package.

## Prerequisites

Install R and the required package:

```r
install.packages("metafor")
```

## Running Validation

Execute the validation script:

```bash
cd /Users/brandon/meta-analysis-tool/backend/tests/validation/r_validation
Rscript validate_calculations.R
```

Or make it executable and run directly:

```bash
chmod +x validate_calculations.R
./validate_calculations.R
```

## What Gets Validated

The script validates:

1. **Fixed-Effects Meta-Analysis**
   - Pooled effect size
   - Standard error
   - 95% confidence intervals
   - Z-value and p-value

2. **Random-Effects Meta-Analysis (DL & REML)**
   - Pooled effect size
   - Tau-squared (between-study variance)
   - Standard error incorporating heterogeneity
   - Confidence intervals

3. **Heterogeneity Statistics**
   - Cochran's Q statistic
   - I² statistic
   - H² statistic
   - Interpretation thresholds

4. **Publication Bias**
   - Egger's regression test
   - Funnel plot asymmetry

5. **Effect Size Calculations**
   - Cohen's d
   - Hedge's g (bias-corrected)
   - Correction factors

6. **Cochrane Review Replication**
   - Real-world validation dataset
   - Exercise for depression meta-analysis

## Expected Output

The script outputs:
- Detailed results for each analysis type
- Key statistics formatted for comparison
- Summary table with all values for Python validation
- Interpretation of results

## Acceptance Criteria

Python implementation must match R metafor within:
- **Effect sizes**: ±1% (or ±0.01 units for small effects)
- **Standard errors**: ±0.001 units
- **Confidence intervals**: ±0.01 units
- **Tau-squared**: ±0.001 units
- **I² statistic**: ±5 percentage points
- **Q statistic**: ±0.1 units

## References

- Viechtbauer, W. (2010). Conducting meta-analyses in R with the metafor package. *Journal of Statistical Software*, 36(3), 1-48.
- Borenstein, M., et al. (2009). *Introduction to Meta-Analysis*. Wiley.
- Cochrane Handbook for Systematic Reviews of Interventions (current edition)
