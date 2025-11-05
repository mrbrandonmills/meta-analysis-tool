"""Statistical agent for meta-analysis calculations.

This agent performs rigorous meta-analysis calculations following established
statistical methods from Borenstein et al. (2009) "Introduction to Meta-Analysis"
and the Cochrane Handbook for Systematic Reviews.

All formulas are mathematically correct and peer-reviewable for academic publication.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy import stats
from scipy.optimize import minimize_scalar
import warnings

from loguru import logger

from app.agents.base import AgentConfig, BaseAgent, AgentRole
from app.core.config import get_settings

settings = get_settings()


class EffectSizeCalculator:
    """Calculate effect sizes from various study statistics.

    References:
    - Borenstein et al. (2009). Introduction to Meta-Analysis. Wiley.
    - Cooper et al. (2009). The Handbook of Research Synthesis and Meta-Analysis.
    """

    @staticmethod
    def cohens_d(mean_treatment: float, mean_control: float,
                 sd_treatment: float, sd_control: float,
                 n_treatment: int, n_control: int) -> Dict[str, float]:
        """Calculate Cohen's d for continuous outcomes.

        Cohen's d represents standardized mean difference between two groups.

        Formula (pooled SD):
        d = (M₁ - M₂) / SD_pooled

        SD_pooled = sqrt[((n₁-1)*SD₁² + (n₂-1)*SD₂²) / (n₁ + n₂ - 2)]

        SE(d) = sqrt[(n₁ + n₂)/(n₁ * n₂) + d²/(2(n₁ + n₂))]

        Reference: Borenstein et al. (2009), Chapter 4, equations 4.18-4.20

        Args:
            mean_treatment: Mean of treatment group
            mean_control: Mean of control group
            sd_treatment: Standard deviation of treatment group
            sd_control: Standard deviation of control group
            n_treatment: Sample size of treatment group
            n_control: Sample size of control group

        Returns:
            Dictionary with effect_size, standard_error, variance, ci_lower, ci_upper
        """
        # Calculate pooled standard deviation
        pooled_sd = np.sqrt(
            ((n_treatment - 1) * sd_treatment**2 + (n_control - 1) * sd_control**2) /
            (n_treatment + n_control - 2)
        )

        # Calculate Cohen's d
        d = (mean_treatment - mean_control) / pooled_sd

        # Calculate standard error of d
        # Formula: SE = sqrt[(n1 + n2)/(n1*n2) + d²/(2*(n1 + n2))]
        se = np.sqrt(
            (n_treatment + n_control) / (n_treatment * n_control) +
            d**2 / (2 * (n_treatment + n_control))
        )

        variance = se**2

        # 95% confidence interval (z = 1.96)
        ci_lower = d - 1.96 * se
        ci_upper = d + 1.96 * se

        return {
            "effect_size": float(d),
            "standard_error": float(se),
            "variance": float(variance),
            "ci_lower": float(ci_lower),
            "ci_upper": float(ci_upper),
            "method": "Cohen's d (pooled SD)"
        }

    @staticmethod
    def hedges_g(mean_treatment: float, mean_control: float,
                 sd_treatment: float, sd_control: float,
                 n_treatment: int, n_control: int) -> Dict[str, float]:
        """Calculate Hedge's g (bias-corrected Cohen's d).

        Hedge's g corrects for small-sample bias in Cohen's d.

        Correction factor J:
        J = 1 - 3/(4*df - 1)
        where df = n₁ + n₂ - 2

        g = J * d

        Reference: Hedges (1981), Borenstein et al. (2009), Chapter 4

        Args:
            Same as cohens_d

        Returns:
            Dictionary with corrected effect_size and statistics
        """
        # First calculate Cohen's d
        cohens_result = EffectSizeCalculator.cohens_d(
            mean_treatment, mean_control,
            sd_treatment, sd_control,
            n_treatment, n_control
        )

        d = cohens_result["effect_size"]

        # Calculate correction factor J
        df = n_treatment + n_control - 2
        j = 1 - (3 / (4 * df - 1))

        # Apply correction
        g = j * d
        se_g = j * cohens_result["standard_error"]

        return {
            "effect_size": float(g),
            "standard_error": float(se_g),
            "variance": float(se_g**2),
            "ci_lower": float(g - 1.96 * se_g),
            "ci_upper": float(g + 1.96 * se_g),
            "correction_factor": float(j),
            "method": "Hedge's g (bias-corrected)"
        }

    @staticmethod
    def odds_ratio(events_treatment: int, n_treatment: int,
                   events_control: int, n_control: int) -> Dict[str, float]:
        """Calculate odds ratio for binary outcomes.

        OR = (a*d) / (b*c)
        where a = events_treatment, b = non-events_treatment,
              c = events_control, d = non-events_control

        Log OR is used for meta-analysis:
        ln(OR) = ln(a*d/b*c)
        SE[ln(OR)] = sqrt(1/a + 1/b + 1/c + 1/d)

        Reference: Borenstein et al. (2009), Chapter 5

        Args:
            events_treatment: Number of events in treatment group
            n_treatment: Total in treatment group
            events_control: Number of events in control group
            n_control: Total in control group

        Returns:
            Dictionary with odds_ratio (natural scale), log_or, and statistics
        """
        # Apply continuity correction if any cell is 0
        if events_treatment == 0 or events_control == 0 or \
           events_treatment == n_treatment or events_control == n_control:
            logger.warning("Applying continuity correction (0.5) to zero cells")
            a = events_treatment + 0.5
            b = n_treatment - events_treatment + 0.5
            c = events_control + 0.5
            d = n_control - events_control + 0.5
        else:
            a = events_treatment
            b = n_treatment - events_treatment
            c = events_control
            d = n_control - events_control

        # Calculate odds ratio
        or_value = (a * d) / (b * c)
        log_or = np.log(or_value)

        # Standard error of log OR
        se_log_or = np.sqrt(1/a + 1/b + 1/c + 1/d)

        # Confidence interval on log scale
        log_ci_lower = log_or - 1.96 * se_log_or
        log_ci_upper = log_or + 1.96 * se_log_or

        # Convert back to natural scale
        ci_lower = np.exp(log_ci_lower)
        ci_upper = np.exp(log_ci_upper)

        return {
            "odds_ratio": float(or_value),
            "log_odds_ratio": float(log_or),
            "effect_size": float(log_or),  # For meta-analysis pooling
            "standard_error": float(se_log_or),
            "variance": float(se_log_or**2),
            "ci_lower": float(ci_lower),
            "ci_upper": float(ci_upper),
            "method": "Odds Ratio"
        }

    @staticmethod
    def risk_ratio(events_treatment: int, n_treatment: int,
                   events_control: int, n_control: int) -> Dict[str, float]:
        """Calculate risk ratio (relative risk) for binary outcomes.

        RR = (a/n₁) / (c/n₂)
        ln(RR) = ln(a/n₁) - ln(c/n₂)
        SE[ln(RR)] = sqrt(1/a - 1/n₁ + 1/c - 1/n₂)

        Reference: Borenstein et al. (2009), Chapter 5

        Args:
            Same as odds_ratio

        Returns:
            Dictionary with risk_ratio and statistics
        """
        # Apply continuity correction if needed
        if events_treatment == 0 or events_control == 0:
            logger.warning("Applying continuity correction (0.5) to zero cells")
            a = events_treatment + 0.5
            n1 = n_treatment
            c = events_control + 0.5
            n2 = n_control
        else:
            a = events_treatment
            n1 = n_treatment
            c = events_control
            n2 = n_control

        # Calculate risk ratio
        risk_treatment = a / n1
        risk_control = c / n2
        rr = risk_treatment / risk_control
        log_rr = np.log(rr)

        # Standard error of log RR
        se_log_rr = np.sqrt(1/a - 1/n1 + 1/c - 1/n2)

        # Confidence interval
        log_ci_lower = log_rr - 1.96 * se_log_rr
        log_ci_upper = log_rr + 1.96 * se_log_rr

        ci_lower = np.exp(log_ci_lower)
        ci_upper = np.exp(log_ci_upper)

        return {
            "risk_ratio": float(rr),
            "log_risk_ratio": float(log_rr),
            "effect_size": float(log_rr),  # For meta-analysis pooling
            "standard_error": float(se_log_rr),
            "variance": float(se_log_rr**2),
            "ci_lower": float(ci_lower),
            "ci_upper": float(ci_upper),
            "method": "Risk Ratio"
        }

    @staticmethod
    def fishers_z(correlation: float, n: int) -> Dict[str, float]:
        """Fisher's Z transformation for correlations.

        Z = 0.5 * ln[(1 + r) / (1 - r)] = arctanh(r)
        SE(Z) = 1 / sqrt(n - 3)

        Reference: Borenstein et al. (2009), Chapter 6

        Args:
            correlation: Pearson correlation coefficient (-1 to 1)
            n: Sample size

        Returns:
            Dictionary with Fisher's Z and statistics
        """
        if not -1 <= correlation <= 1:
            raise ValueError(f"Correlation must be between -1 and 1, got {correlation}")

        if n < 4:
            raise ValueError(f"Sample size must be at least 4, got {n}")

        # Fisher's Z transformation
        z = np.arctanh(correlation)

        # Standard error
        se = 1 / np.sqrt(n - 3)

        # Confidence interval on Z scale
        ci_lower_z = z - 1.96 * se
        ci_upper_z = z + 1.96 * se

        # Convert back to correlation scale
        ci_lower_r = np.tanh(ci_lower_z)
        ci_upper_r = np.tanh(ci_upper_z)

        return {
            "fishers_z": float(z),
            "effect_size": float(z),  # For meta-analysis pooling
            "standard_error": float(se),
            "variance": float(se**2),
            "ci_lower_z": float(ci_lower_z),
            "ci_upper_z": float(ci_upper_z),
            "ci_lower_r": float(ci_lower_r),
            "ci_upper_r": float(ci_upper_r),
            "original_correlation": float(correlation),
            "method": "Fisher's Z transformation"
        }


class MetaAnalysisCalculator:
    """Perform meta-analysis calculations.

    Implements fixed-effects and random-effects models following standard methods.
    """

    @staticmethod
    def fixed_effects(effect_sizes: np.ndarray,
                     standard_errors: np.ndarray) -> Dict[str, float]:
        """Fixed-effects meta-analysis using inverse variance weighting.

        Pooled effect size:
        ES_pooled = Σ(w_i * ES_i) / Σ(w_i)
        where w_i = 1 / SE_i²

        Standard error:
        SE_pooled = sqrt(1 / Σ(w_i))

        Reference: Borenstein et al. (2009), Chapter 11

        Args:
            effect_sizes: Array of effect sizes
            standard_errors: Array of standard errors

        Returns:
            Dictionary with pooled effect size and statistics
        """
        # Calculate weights (inverse variance)
        variances = standard_errors**2
        weights = 1 / variances

        # Calculate pooled effect size
        pooled_es = np.sum(weights * effect_sizes) / np.sum(weights)

        # Calculate standard error
        pooled_se = np.sqrt(1 / np.sum(weights))
        pooled_variance = pooled_se**2

        # Calculate 95% confidence interval
        ci_lower = pooled_es - 1.96 * pooled_se
        ci_upper = pooled_es + 1.96 * pooled_se

        # Calculate z-value and p-value
        z_value = pooled_es / pooled_se
        p_value = 2 * (1 - stats.norm.cdf(abs(z_value)))

        return {
            "pooled_effect": float(pooled_es),
            "standard_error": float(pooled_se),
            "variance": float(pooled_variance),
            "ci_lower": float(ci_lower),
            "ci_upper": float(ci_upper),
            "z_value": float(z_value),
            "p_value": float(p_value),
            "weights": weights.tolist(),
            "model": "fixed-effects"
        }

    @staticmethod
    def calculate_heterogeneity(effect_sizes: np.ndarray,
                                standard_errors: np.ndarray) -> Dict[str, float]:
        """Calculate heterogeneity statistics (Q, I², τ²).

        Cochran's Q statistic:
        Q = Σ[w_i * (ES_i - ES_pooled)²]
        where w_i = 1/SE_i² (fixed-effects weights)

        I² statistic:
        I² = ((Q - df) / Q) * 100%
        where df = k - 1 (k = number of studies)

        Reference:
        - Cochran (1954) for Q statistic
        - Higgins & Thompson (2002) for I²
        - Borenstein et al. (2009), Chapter 16

        Args:
            effect_sizes: Array of effect sizes
            standard_errors: Array of standard errors

        Returns:
            Dictionary with Q, I², τ², and p-value
        """
        k = len(effect_sizes)

        if k < 2:
            return {
                "q_statistic": 0.0,
                "df": 0,
                "q_p_value": 1.0,
                "i_squared": 0.0,
                "tau_squared": 0.0,
                "interpretation": "Cannot assess heterogeneity with < 2 studies"
            }

        # Calculate fixed-effects pooled estimate
        fe_result = MetaAnalysisCalculator.fixed_effects(effect_sizes, standard_errors)
        pooled_es = fe_result["pooled_effect"]
        weights = np.array(fe_result["weights"])

        # Calculate Q statistic
        q_statistic = np.sum(weights * (effect_sizes - pooled_es)**2)

        # Degrees of freedom
        df = k - 1

        # P-value for Q (chi-square distribution)
        q_p_value = 1 - stats.chi2.cdf(q_statistic, df)

        # Calculate I²
        # I² = ((Q - df) / Q) * 100%, constrained to [0, 100]
        if q_statistic > df:
            i_squared = ((q_statistic - df) / q_statistic) * 100
        else:
            i_squared = 0.0

        # Interpret heterogeneity (Higgins et al. 2003)
        if i_squared < 25:
            interpretation = "low heterogeneity"
        elif i_squared < 50:
            interpretation = "moderate heterogeneity"
        elif i_squared < 75:
            interpretation = "substantial heterogeneity"
        else:
            interpretation = "considerable heterogeneity"

        return {
            "q_statistic": float(q_statistic),
            "df": int(df),
            "q_p_value": float(q_p_value),
            "i_squared": float(i_squared),
            "interpretation": interpretation
        }

    @staticmethod
    def dersimonian_laird_tau_squared(effect_sizes: np.ndarray,
                                     standard_errors: np.ndarray) -> float:
        """Calculate tau-squared using DerSimonian-Laird method.

        τ² = (Q - df) / (Σw_i - Σw_i²/Σw_i)

        where w_i = 1/SE_i² (fixed-effects weights)

        Reference: DerSimonian & Laird (1986), Borenstein et al. (2009), Chapter 12

        Args:
            effect_sizes: Array of effect sizes
            standard_errors: Array of standard errors

        Returns:
            tau_squared estimate (between-study variance)
        """
        k = len(effect_sizes)

        if k < 2:
            return 0.0

        # Calculate Q statistic and df
        het = MetaAnalysisCalculator.calculate_heterogeneity(effect_sizes, standard_errors)
        q = het["q_statistic"]
        df = het["df"]

        # Calculate weights
        variances = standard_errors**2
        weights = 1 / variances

        # Calculate tau-squared
        sum_weights = np.sum(weights)
        sum_weights_squared = np.sum(weights**2)

        denominator = sum_weights - (sum_weights_squared / sum_weights)

        if denominator > 0:
            tau_squared = max(0, (q - df) / denominator)
        else:
            tau_squared = 0.0

        return float(tau_squared)

    @staticmethod
    def reml_tau_squared(effect_sizes: np.ndarray,
                        standard_errors: np.ndarray) -> float:
        """Calculate tau-squared using Restricted Maximum Likelihood (REML).

        REML is generally preferred over DerSimonian-Laird for small number of studies.

        Uses iterative optimization to maximize the restricted likelihood.

        Reference: Viechtbauer (2005), Borenstein et al. (2009), Chapter 12

        Args:
            effect_sizes: Array of effect sizes
            standard_errors: Array of standard errors

        Returns:
            tau_squared estimate via REML
        """
        k = len(effect_sizes)

        if k < 2:
            return 0.0

        variances = standard_errors**2

        def neg_reml_likelihood(tau_sq):
            """Negative REML log-likelihood to minimize."""
            # Weights under current tau_squared
            weights = 1 / (variances + tau_sq)
            sum_weights = np.sum(weights)

            # Pooled estimate
            pooled = np.sum(weights * effect_sizes) / sum_weights

            # Log-likelihood components
            log_det = np.sum(np.log(variances + tau_sq))
            ss = np.sum(weights * (effect_sizes - pooled)**2)

            # REML log-likelihood (simplified)
            reml_ll = -0.5 * (log_det + ss + np.log(sum_weights))

            return -reml_ll  # Minimize negative LL

        # Optimize tau-squared (bounded between 0 and reasonable upper limit)
        result = minimize_scalar(
            neg_reml_likelihood,
            bounds=(0, np.var(effect_sizes) * 10),
            method='bounded'
        )

        return float(result.x)

    @staticmethod
    def random_effects(effect_sizes: np.ndarray,
                      standard_errors: np.ndarray,
                      method: str = "DL") -> Dict[str, float]:
        """Random-effects meta-analysis.

        Incorporates between-study heterogeneity (τ²) into weights.

        Weights:
        w_i* = 1 / (SE_i² + τ²)

        Pooled effect:
        ES_pooled = Σ(w_i* * ES_i) / Σ(w_i*)

        Reference: Borenstein et al. (2009), Chapter 12

        Args:
            effect_sizes: Array of effect sizes
            standard_errors: Array of standard errors
            method: "DL" (DerSimonian-Laird) or "REML" (default: "DL")

        Returns:
            Dictionary with pooled effect size and statistics
        """
        if method == "REML":
            tau_squared = MetaAnalysisCalculator.reml_tau_squared(
                effect_sizes, standard_errors
            )
        else:  # DerSimonian-Laird
            tau_squared = MetaAnalysisCalculator.dersimonian_laird_tau_squared(
                effect_sizes, standard_errors
            )

        # Calculate random-effects weights
        variances = standard_errors**2
        re_weights = 1 / (variances + tau_squared)

        # Calculate pooled effect size
        pooled_es = np.sum(re_weights * effect_sizes) / np.sum(re_weights)

        # Calculate standard error
        pooled_se = np.sqrt(1 / np.sum(re_weights))
        pooled_variance = pooled_se**2

        # Calculate 95% confidence interval
        ci_lower = pooled_es - 1.96 * pooled_se
        ci_upper = pooled_es + 1.96 * pooled_se

        # Calculate z-value and p-value
        z_value = pooled_es / pooled_se
        p_value = 2 * (1 - stats.norm.cdf(abs(z_value)))

        return {
            "pooled_effect": float(pooled_es),
            "standard_error": float(pooled_se),
            "variance": float(pooled_variance),
            "ci_lower": float(ci_lower),
            "ci_upper": float(ci_upper),
            "z_value": float(z_value),
            "p_value": float(p_value),
            "tau_squared": float(tau_squared),
            "weights": re_weights.tolist(),
            "model": f"random-effects ({method})"
        }


class PublicationBiasAssessment:
    """Assess publication bias in meta-analysis."""

    @staticmethod
    def eggers_test(effect_sizes: np.ndarray,
                   standard_errors: np.ndarray) -> Dict[str, float]:
        """Egger's regression test for funnel plot asymmetry.

        Regresses standardized effect (ES/SE) on precision (1/SE).

        Significant intercept suggests funnel plot asymmetry,
        which may indicate publication bias.

        Reference: Egger et al. (1997), Sterne & Egger (2001)

        Args:
            effect_sizes: Array of effect sizes
            standard_errors: Array of standard errors

        Returns:
            Dictionary with intercept, p-value, and interpretation
        """
        if len(effect_sizes) < 3:
            return {
                "intercept": 0.0,
                "se_intercept": 0.0,
                "t_value": 0.0,
                "p_value": 1.0,
                "interpretation": "Too few studies for Egger's test (need ≥3)"
            }

        # Calculate precision and standardized effect
        precision = 1 / standard_errors
        standardized_effect = effect_sizes / standard_errors

        # Simple linear regression: standardized_effect ~ precision
        # Using scipy.stats.linregress
        slope, intercept, r_value, p_value, se = stats.linregress(
            precision, standardized_effect
        )

        # The intercept is what we care about for Egger's test
        # Calculate t-statistic for intercept
        n = len(effect_sizes)
        df = n - 2

        # Standard error of intercept (from regression)
        mse = np.sum((standardized_effect - (intercept + slope * precision))**2) / df
        se_intercept = np.sqrt(mse * (1/n + np.mean(precision)**2 / np.sum((precision - np.mean(precision))**2)))

        t_value = intercept / se_intercept if se_intercept > 0 else 0
        p_value_intercept = 2 * (1 - stats.t.cdf(abs(t_value), df))

        # Interpretation
        if p_value_intercept < 0.05:
            interpretation = "Significant asymmetry detected (p<0.05), possible publication bias"
        elif p_value_intercept < 0.10:
            interpretation = "Marginal asymmetry (p<0.10), possible publication bias"
        else:
            interpretation = "No significant asymmetry detected"

        return {
            "intercept": float(intercept),
            "se_intercept": float(se_intercept),
            "t_value": float(t_value),
            "p_value": float(p_value_intercept),
            "df": int(df),
            "interpretation": interpretation
        }

    @staticmethod
    def funnel_plot_data(effect_sizes: np.ndarray,
                        standard_errors: np.ndarray,
                        pooled_effect: float) -> Dict[str, Any]:
        """Generate data for funnel plot.

        Funnel plot shows effect sizes vs. precision (or SE).
        Asymmetry suggests publication bias.

        Args:
            effect_sizes: Array of effect sizes
            standard_errors: Array of standard errors
            pooled_effect: Pooled effect size from meta-analysis

        Returns:
            Dictionary with plot data and reference lines
        """
        # Calculate precision
        precision = 1 / standard_errors

        # Generate reference lines for funnel
        # 95% confidence region around pooled effect
        se_range = np.linspace(0, np.max(standard_errors) * 1.1, 100)
        ci_lower = pooled_effect - 1.96 * se_range
        ci_upper = pooled_effect + 1.96 * se_range

        return {
            "studies": [
                {
                    "effect_size": float(es),
                    "standard_error": float(se),
                    "precision": float(1/se)
                }
                for es, se in zip(effect_sizes, standard_errors)
            ],
            "pooled_effect": float(pooled_effect),
            "reference_lines": {
                "se_range": se_range.tolist(),
                "ci_lower": ci_lower.tolist(),
                "ci_upper": ci_upper.tolist()
            }
        }


class StatisticalAgent(BaseAgent):
    """Statistical agent for meta-analysis calculations.

    This agent performs rigorous, peer-reviewable meta-analysis calculations
    following established statistical methods.

    Capabilities:
    - Effect size calculations (Cohen's d, Hedge's g, OR, RR, Fisher's Z)
    - Fixed-effects and random-effects meta-analysis
    - Heterogeneity assessment (Q, I², τ²)
    - Publication bias assessment (Egger's test, funnel plots)
    - Forest plot data generation
    """

    def __init__(self, config: AgentConfig):
        config.role = AgentRole.STATISTICAL
        super().__init__(config)

        self.effect_calculator = EffectSizeCalculator()
        self.meta_calculator = MetaAnalysisCalculator()
        self.bias_assessor = PublicationBiasAssessment()

    def get_system_prompt(self) -> str:
        """Get system prompt for statistical agent."""
        return """You are the Statistical Analysis Agent for a meta-analysis research platform.

You are an expert biostatistician specializing in meta-analysis. You have deep knowledge of:
- Effect size calculations and standardization
- Fixed-effects and random-effects models
- Heterogeneity assessment (I², τ², Q statistic)
- Publication bias detection
- Statistical inference and hypothesis testing
- Meta-regression and subgroup analysis
- Sensitivity analysis

Your role is to:
1. Guide researchers in selecting appropriate statistical methods
2. Interpret statistical results in plain language
3. Flag potential issues with data quality or heterogeneity
4. Recommend sensitivity analyses when needed
5. Explain statistical concepts clearly for non-statisticians

You follow best practices from:
- Borenstein et al. "Introduction to Meta-Analysis" (2009)
- Cochrane Handbook for Systematic Reviews
- PRISMA reporting guidelines

You are conservative in your interpretations and always acknowledge limitations."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform meta-analysis calculations.

        Args:
            input_data: {
                "studies": List of studies with effect size data,
                "effect_type": Type of effect size ("continuous", "binary", "correlation"),
                "model": "fixed" or "random" (default: "random"),
                "tau_method": "DL" or "REML" (default: "DL")
            }

        Returns:
            Complete meta-analysis results with all statistics
        """
        studies = input_data.get("studies", [])
        effect_type = input_data.get("effect_type", "continuous")
        model = input_data.get("model", "random")
        tau_method = input_data.get("tau_method", "DL")

        if len(studies) < 2:
            raise ValueError("Need at least 2 studies for meta-analysis")

        logger.info(f"StatisticalAgent performing meta-analysis on {len(studies)} studies")

        # Step 1: Calculate effect sizes for each study
        effect_sizes_data = []

        for i, study in enumerate(studies):
            try:
                if effect_type == "continuous":
                    es_result = self._calculate_continuous_effect(study)
                elif effect_type == "binary":
                    es_result = self._calculate_binary_effect(study)
                elif effect_type == "correlation":
                    es_result = self._calculate_correlation_effect(study)
                else:
                    raise ValueError(f"Unknown effect_type: {effect_type}")

                es_result["study_id"] = study.get("study_id", f"Study_{i+1}")
                es_result["study_name"] = study.get("study_name", f"Study {i+1}")
                effect_sizes_data.append(es_result)

            except Exception as e:
                logger.error(f"Error calculating effect size for study {i}: {e}")
                raise ValueError(f"Failed to calculate effect size for study {i}: {e}")

        # Extract effect sizes and standard errors
        effect_sizes = np.array([es["effect_size"] for es in effect_sizes_data])
        standard_errors = np.array([es["standard_error"] for es in effect_sizes_data])

        # Step 2: Calculate heterogeneity
        heterogeneity = self.meta_calculator.calculate_heterogeneity(
            effect_sizes, standard_errors
        )

        # Step 3: Perform meta-analysis
        if model == "fixed":
            ma_result = self.meta_calculator.fixed_effects(effect_sizes, standard_errors)
        else:  # random
            ma_result = self.meta_calculator.random_effects(
                effect_sizes, standard_errors, method=tau_method
            )
            # Add heterogeneity to result
            if "tau_squared" in ma_result:
                heterogeneity["tau_squared"] = ma_result["tau_squared"]

        # Step 4: Publication bias assessment
        eggers = self.bias_assessor.eggers_test(effect_sizes, standard_errors)
        funnel = self.bias_assessor.funnel_plot_data(
            effect_sizes, standard_errors, ma_result["pooled_effect"]
        )

        # Step 5: Generate forest plot data
        forest_plot = self._generate_forest_plot_data(
            effect_sizes_data, ma_result, heterogeneity
        )

        # Step 6: Use LLM to interpret results
        interpretation = await self._interpret_results(
            ma_result, heterogeneity, eggers, len(studies)
        )

        # Step 7: Make decision about result quality
        decision = await self.make_decision(
            "Are these meta-analysis results reliable and suitable for publication?",
            input_data={
                "n_studies": len(studies),
                "heterogeneity": heterogeneity,
                "publication_bias": eggers,
                "pooled_effect_p_value": ma_result["p_value"]
            }
        )

        return {
            "meta_analysis": ma_result,
            "heterogeneity": heterogeneity,
            "publication_bias": {
                "eggers_test": eggers,
                "funnel_plot": funnel
            },
            "forest_plot": forest_plot,
            "individual_studies": effect_sizes_data,
            "interpretation": interpretation,
            "decision": decision.model_dump(),
            "n_studies": len(studies),
            "effect_type": effect_type,
            "model_used": model
        }

    def _calculate_continuous_effect(self, study: Dict[str, Any]) -> Dict[str, float]:
        """Calculate effect size for continuous outcomes."""
        # Check if study provides effect size directly or raw data
        if "effect_size" in study and "standard_error" in study:
            # Pre-calculated effect size
            return {
                "effect_size": study["effect_size"],
                "standard_error": study["standard_error"],
                "variance": study.get("variance", study["standard_error"]**2),
                "ci_lower": study.get("ci_lower", study["effect_size"] - 1.96 * study["standard_error"]),
                "ci_upper": study.get("ci_upper", study["effect_size"] + 1.96 * study["standard_error"]),
                "method": study.get("method", "Pre-calculated")
            }
        else:
            # Calculate from raw data
            method = study.get("es_method", "hedges_g")  # Default to bias-corrected

            if method == "cohens_d":
                return self.effect_calculator.cohens_d(
                    study["mean_treatment"],
                    study["mean_control"],
                    study["sd_treatment"],
                    study["sd_control"],
                    study["n_treatment"],
                    study["n_control"]
                )
            else:  # hedges_g (default)
                return self.effect_calculator.hedges_g(
                    study["mean_treatment"],
                    study["mean_control"],
                    study["sd_treatment"],
                    study["sd_control"],
                    study["n_treatment"],
                    study["n_control"]
                )

    def _calculate_binary_effect(self, study: Dict[str, Any]) -> Dict[str, float]:
        """Calculate effect size for binary outcomes."""
        method = study.get("es_method", "odds_ratio")

        if method == "risk_ratio":
            return self.effect_calculator.risk_ratio(
                study["events_treatment"],
                study["n_treatment"],
                study["events_control"],
                study["n_control"]
            )
        else:  # odds_ratio (default)
            return self.effect_calculator.odds_ratio(
                study["events_treatment"],
                study["n_treatment"],
                study["events_control"],
                study["n_control"]
            )

    def _calculate_correlation_effect(self, study: Dict[str, Any]) -> Dict[str, float]:
        """Calculate effect size for correlations."""
        return self.effect_calculator.fishers_z(
            study["correlation"],
            study["n"]
        )

    def _generate_forest_plot_data(self, effect_sizes_data: List[Dict[str, Any]],
                                   ma_result: Dict[str, float],
                                   heterogeneity: Dict[str, float]) -> Dict[str, Any]:
        """Generate data structure for forest plot visualization."""
        # Individual study data for forest plot
        studies_plot = []
        for i, es in enumerate(effect_sizes_data):
            studies_plot.append({
                "study_id": es.get("study_id", f"Study_{i+1}"),
                "study_name": es.get("study_name", f"Study {i+1}"),
                "effect_size": es["effect_size"],
                "ci_lower": es["ci_lower"],
                "ci_upper": es["ci_upper"],
                "weight": ma_result["weights"][i] / sum(ma_result["weights"]) * 100,  # Percentage
                "sample_size": es.get("n", None)
            })

        # Overall pooled effect
        pooled = {
            "effect_size": ma_result["pooled_effect"],
            "ci_lower": ma_result["ci_lower"],
            "ci_upper": ma_result["ci_upper"],
            "p_value": ma_result["p_value"]
        }

        return {
            "studies": studies_plot,
            "pooled": pooled,
            "heterogeneity": {
                "i_squared": heterogeneity["i_squared"],
                "q_statistic": heterogeneity["q_statistic"],
                "q_p_value": heterogeneity["q_p_value"],
                "tau_squared": heterogeneity.get("tau_squared", 0.0)
            },
            "model": ma_result["model"]
        }

    async def _interpret_results(self, ma_result: Dict[str, float],
                                 heterogeneity: Dict[str, float],
                                 eggers: Dict[str, float],
                                 n_studies: int) -> str:
        """Use LLM to interpret meta-analysis results in plain language."""
        prompt = f"""
Interpret these meta-analysis results for a research audience:

Meta-Analysis Results:
- Pooled effect size: {ma_result['pooled_effect']:.3f} (95% CI: {ma_result['ci_lower']:.3f} to {ma_result['ci_upper']:.3f})
- P-value: {ma_result['p_value']:.4f}
- Model: {ma_result['model']}
- Number of studies: {n_studies}

Heterogeneity:
- I² = {heterogeneity['i_squared']:.1f}% ({heterogeneity['interpretation']})
- Q = {heterogeneity['q_statistic']:.2f}, p = {heterogeneity['q_p_value']:.4f}
{f"- τ² = {heterogeneity.get('tau_squared', 0):.4f}" if 'tau_squared' in heterogeneity else ""}

Publication Bias:
- Egger's test: {eggers['interpretation']}
- p-value: {eggers['p_value']:.4f}

Provide:
1. Summary of the main finding (2-3 sentences)
2. Interpretation of effect size magnitude
3. Assessment of heterogeneity and what it means
4. Comment on publication bias
5. Any limitations or caveats
6. Clinical/practical significance (if applicable)

Use clear, academic language suitable for a research paper's results section.
"""

        interpretation = await self.think(prompt)
        return interpretation
