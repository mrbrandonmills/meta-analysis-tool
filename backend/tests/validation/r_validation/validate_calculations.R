#!/usr/bin/env Rscript

# R Validation Script for Meta-Analysis Calculations
# Validates Python calculations against R metafor package
#
# Install required packages if needed:
# install.packages("metafor")

library(metafor)

cat("=======================================================\n")
cat("META-ANALYSIS VALIDATION AGAINST R METAFOR PACKAGE\n")
cat("=======================================================\n\n")

# Simple validation dataset
yi <- c(0.50, 0.60, 0.45, 0.55, 0.48)
sei <- c(0.10, 0.15, 0.12, 0.11, 0.13)

cat("Dataset:\n")
cat("Effect sizes:", yi, "\n")
cat("Standard errors:", sei, "\n\n")

# ===================================================================
# FIXED-EFFECTS META-ANALYSIS
# ===================================================================
cat("=== FIXED-EFFECTS META-ANALYSIS ===\n")
fe_result <- rma(yi, sei, method="FE")
print(fe_result)

cat("\nKey Statistics (Fixed-Effects):\n")
cat(sprintf("Pooled effect:    %.4f\n", fe_result$beta))
cat(sprintf("Standard error:   %.4f\n", fe_result$se))
cat(sprintf("95%% CI:           [%.4f, %.4f]\n", fe_result$ci.lb, fe_result$ci.ub))
cat(sprintf("Z-value:          %.4f\n", fe_result$zval))
cat(sprintf("P-value:          %.4f\n", fe_result$pval))
cat("\n")

# ===================================================================
# RANDOM-EFFECTS META-ANALYSIS (DerSimonian-Laird)
# ===================================================================
cat("=== RANDOM-EFFECTS META-ANALYSIS (DerSimonian-Laird) ===\n")
re_dl_result <- rma(yi, sei, method="DL")
print(re_dl_result)

cat("\nKey Statistics (Random-Effects DL):\n")
cat(sprintf("Pooled effect:    %.4f\n", re_dl_result$beta))
cat(sprintf("Standard error:   %.4f\n", re_dl_result$se))
cat(sprintf("95%% CI:           [%.4f, %.4f]\n", re_dl_result$ci.lb, re_dl_result$ci.ub))
cat(sprintf("Z-value:          %.4f\n", re_dl_result$zval))
cat(sprintf("P-value:          %.4f\n", re_dl_result$pval))
cat(sprintf("Tau-squared (τ²): %.4f\n", re_dl_result$tau2))
cat("\n")

# ===================================================================
# RANDOM-EFFECTS META-ANALYSIS (REML)
# ===================================================================
cat("=== RANDOM-EFFECTS META-ANALYSIS (REML) ===\n")
re_reml_result <- rma(yi, sei, method="REML")
print(re_reml_result)

cat("\nKey Statistics (Random-Effects REML):\n")
cat(sprintf("Pooled effect:    %.4f\n", re_reml_result$beta))
cat(sprintf("Standard error:   %.4f\n", re_reml_result$se))
cat(sprintf("95%% CI:           [%.4f, %.4f]\n", re_reml_result$ci.lb, re_reml_result$ci.ub))
cat(sprintf("Z-value:          %.4f\n", re_reml_result$zval))
cat(sprintf("P-value:          %.4f\n", re_reml_result$pval))
cat(sprintf("Tau-squared (τ²): %.4f\n", re_reml_result$tau2))
cat("\n")

# ===================================================================
# HETEROGENEITY STATISTICS
# ===================================================================
cat("=== HETEROGENEITY STATISTICS ===\n")
cat(sprintf("Cochran's Q:      %.2f\n", fe_result$QE))
cat(sprintf("Degrees of freedom: %d\n", fe_result$k - 1))
cat(sprintf("Q p-value:        %.4f\n", fe_result$QEp))
cat(sprintf("I² statistic:     %.1f%%\n", fe_result$I2))
cat(sprintf("H² statistic:     %.2f\n", fe_result$H2))

if (fe_result$I2 < 25) {
  interpretation <- "low heterogeneity"
} else if (fe_result$I2 < 50) {
  interpretation <- "moderate heterogeneity"
} else if (fe_result$I2 < 75) {
  interpretation <- "substantial heterogeneity"
} else {
  interpretation <- "considerable heterogeneity"
}
cat(sprintf("Interpretation:   %s\n", interpretation))
cat("\n")

# ===================================================================
# PUBLICATION BIAS - EGGER'S TEST
# ===================================================================
cat("=== PUBLICATION BIAS (Egger's Test) ===\n")
egger_result <- regtest(fe_result, model="lm")
print(egger_result)

cat("\nEgger's Test Results:\n")
cat(sprintf("Intercept (bias): %.4f\n", egger_result$est))
cat(sprintf("Standard error:   %.4f\n", egger_result$se))
cat(sprintf("Z-value:          %.4f\n", egger_result$zval))
cat(sprintf("P-value:          %.4f\n", egger_result$pval))

if (egger_result$pval < 0.05) {
  bias_interpretation <- "Significant asymmetry detected (p < 0.05), possible publication bias"
} else if (egger_result$pval < 0.10) {
  bias_interpretation <- "Marginal asymmetry (p < 0.10), possible publication bias"
} else {
  bias_interpretation <- "No significant asymmetry detected"
}
cat(sprintf("Interpretation:   %s\n", bias_interpretation))
cat("\n")

# ===================================================================
# COCHRANE REVIEW VALIDATION DATA
# ===================================================================
cat("=== COCHRANE REVIEW VALIDATION (Exercise for Depression) ===\n")

# Data from Cochrane review (simulated/approximated)
cochrane_yi <- c(-0.729, -0.259, -0.787, -0.201, -0.273)
cochrane_sei <- c(0.196, 0.217, 0.266, 0.157, 0.283)
cochrane_studies <- c("Blumenthal 1999", "Mather 2002", "Singh 2005", "Krogh 2009", "Hoffman 2010")

cat("Studies:\n")
for (i in 1:length(cochrane_studies)) {
  cat(sprintf("  %s: ES=%.3f, SE=%.3f\n", cochrane_studies[i], cochrane_yi[i], cochrane_sei[i]))
}
cat("\n")

cochrane_re <- rma(cochrane_yi, cochrane_sei, method="DL")
print(cochrane_re)

cat("\nCochrane Replication Results:\n")
cat(sprintf("Pooled SMD:       %.3f\n", cochrane_re$beta))
cat(sprintf("95%% CI:           [%.3f, %.3f]\n", cochrane_re$ci.lb, cochrane_re$ci.ub))
cat(sprintf("I²:               %.1f%%\n", cochrane_re$I2))
cat(sprintf("τ²:               %.4f\n", cochrane_re$tau2))
cat(sprintf("Q:                %.2f (p=%.4f)\n", cochrane_re$QE, cochrane_re$QEp))
cat("\n")

# ===================================================================
# EFFECT SIZE CALCULATIONS
# ===================================================================
cat("=== EFFECT SIZE CALCULATIONS ===\n")

# Cohen's d example from Borenstein et al. (2009)
cat("Cohen's d Example (Treatment M=103, SD=5.5, n=50 vs Control M=100, SD=4.5, n=50):\n")

m1 <- 103.0
m2 <- 100.0
sd1 <- 5.5
sd2 <- 4.5
n1 <- 50
n2 <- 50

# Calculate pooled SD
pooled_sd <- sqrt(((n1-1)*sd1^2 + (n2-1)*sd2^2) / (n1 + n2 - 2))
cohens_d <- (m1 - m2) / pooled_sd

# Standard error of Cohen's d
se_d <- sqrt((n1 + n2) / (n1 * n2) + cohens_d^2 / (2 * (n1 + n2)))

# Hedge's g correction
df <- n1 + n2 - 2
j <- 1 - (3 / (4 * df - 1))
hedges_g <- j * cohens_d
se_g <- j * se_d

cat(sprintf("Pooled SD:        %.3f\n", pooled_sd))
cat(sprintf("Cohen's d:        %.3f (SE=%.4f)\n", cohens_d, se_d))
cat(sprintf("Correction J:     %.4f\n", j))
cat(sprintf("Hedge's g:        %.3f (SE=%.4f)\n", hedges_g, se_g))
cat("\n")

# ===================================================================
# SUMMARY FOR PYTHON VALIDATION
# ===================================================================
cat("=======================================================\n")
cat("VALIDATION SUMMARY FOR PYTHON IMPLEMENTATION\n")
cat("=======================================================\n\n")

cat("FIXED-EFFECTS (method='FE'):\n")
cat(sprintf("  pooled_effect = %.4f\n", fe_result$beta))
cat(sprintf("  standard_error = %.4f\n", fe_result$se))
cat(sprintf("  ci_lower = %.4f\n", fe_result$ci.lb))
cat(sprintf("  ci_upper = %.4f\n", fe_result$ci.ub))
cat(sprintf("  z_value = %.4f\n", fe_result$zval))
cat(sprintf("  p_value = %.6f\n", fe_result$pval))
cat("\n")

cat("RANDOM-EFFECTS DL (method='DL'):\n")
cat(sprintf("  pooled_effect = %.4f\n", re_dl_result$beta))
cat(sprintf("  standard_error = %.4f\n", re_dl_result$se))
cat(sprintf("  ci_lower = %.4f\n", re_dl_result$ci.lb))
cat(sprintf("  ci_upper = %.4f\n", re_dl_result$ci.ub))
cat(sprintf("  z_value = %.4f\n", re_dl_result$zval))
cat(sprintf("  p_value = %.6f\n", re_dl_result$pval))
cat(sprintf("  tau_squared = %.4f\n", re_dl_result$tau2))
cat("\n")

cat("HETEROGENEITY:\n")
cat(sprintf("  q_statistic = %.2f\n", fe_result$QE))
cat(sprintf("  df = %d\n", fe_result$k - 1))
cat(sprintf("  q_p_value = %.4f\n", fe_result$QEp))
cat(sprintf("  i_squared = %.1f\n", fe_result$I2))
cat("\n")

cat("EGGER'S TEST:\n")
cat(sprintf("  intercept = %.4f\n", egger_result$est))
cat(sprintf("  se_intercept = %.4f\n", egger_result$se))
cat(sprintf("  p_value = %.4f\n", egger_result$pval))
cat("\n")

cat("=======================================================\n")
cat("Validation script completed successfully.\n")
cat("Compare these values with Python implementation.\n")
cat("Target: <1% difference for effect sizes, <5% for heterogeneity.\n")
cat("=======================================================\n")
