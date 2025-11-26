#!/usr/bin/env python3
"""
Benchmark Runner for Meta-Analysis Platform

This script loads real-world benchmark datasets and runs them through
the meta-analysis pipeline to verify external validity.

Usage:
    python run_benchmarks.py
    python run_benchmarks.py --dataset omega3_depression_v1
    python run_benchmarks.py --report
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class BenchmarkRunner:
    """
    Orchestrates external validity testing using real benchmark datasets.

    This is the "Benchmark Runner Agent" described in BACKEND_EXTERNAL_VALIDITY_TESTS.md
    """

    def __init__(self, datasets_dir: Path, reports_dir: Path):
        self.datasets_dir = datasets_dir
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_benchmark(self, benchmark_id: str) -> Dict[str, Any]:
        """Load a benchmark dataset from JSON file."""
        benchmark_file = self.datasets_dir / f"{benchmark_id}.json"

        if not benchmark_file.exists():
            raise FileNotFoundError(f"Benchmark not found: {benchmark_file}")

        with open(benchmark_file) as f:
            return json.load(f)

    def list_benchmarks(self) -> List[str]:
        """List all available benchmark datasets."""
        if not self.datasets_dir.exists():
            return []

        benchmarks = []
        for file in self.datasets_dir.glob("*.json"):
            # Exclude ground truth files
            if not file.name.endswith(".truth.json"):
                benchmark_id = file.stem
                benchmarks.append(benchmark_id)

        return sorted(benchmarks)

    def run_benchmark(self, benchmark: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a benchmark through the meta-analysis pipeline.

        NOTE: This currently simulates the pipeline. When the actual
        StatisticalAgent is ready, replace this with real API calls.

        Args:
            benchmark: Loaded benchmark data

        Returns:
            Dict containing system outputs and comparison results
        """
        benchmark_id = benchmark["id"]
        reference = benchmark["reference_paper"]
        studies = benchmark["studies"]

        print(f"\n{'='*80}")
        print(f"RUNNING BENCHMARK: {benchmark_id}")
        print(f"{'='*80}")
        print(f"Category: {benchmark['category']}")
        print(f"Reference: {reference['title']}")
        print(f"Expected effect: {reference['expected_effect_point']}")
        print(f"Expected I²: {reference['expected_i2_range']}")
        print(f"Number of studies: {len(studies)}")
        print()

        # FUTURE: Replace with actual API call
        # system_output = self._call_real_pipeline(studies)

        # CURRENT: Simulate using reference values with small variance
        system_output = self._simulate_pipeline(benchmark)

        # Compare system output to reference expectations
        comparison = self._compare_results(system_output, reference, benchmark["pass_fail_criteria"])

        result = {
            "benchmark_id": benchmark_id,
            "timestamp": datetime.now().isoformat(),
            "reference": reference,
            "system_output": system_output,
            "comparison": comparison,
            "pass": comparison["overall_pass"]
        }

        return result

    def _simulate_pipeline(self, benchmark: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate meta-analysis pipeline output.

        This will be replaced with actual StatisticalAgent calls.
        For now, return values close to expected (to verify comparison logic).
        """
        import random

        reference = benchmark["reference_paper"]

        # Simulate with small variance from expected
        variance = 0.02

        pooled_effect = reference["expected_effect_point"] + random.uniform(-variance, variance)
        ci_low = reference["expected_effect_ci"][0] + random.uniform(-variance, variance)
        ci_high = reference["expected_effect_ci"][1] + random.uniform(-variance, variance)

        i2_mid = sum(reference["expected_i2_range"]) / 2
        i2 = i2_mid + random.uniform(-5, 5)

        return {
            "pooled_effect": round(pooled_effect, 3),
            "ci_low": round(ci_low, 3),
            "ci_high": round(ci_high, 3),
            "i_squared": round(i2, 1),
            "p_value": reference["expected_p_value"],
            "model": reference["expected_effect_model"],
            "direction": reference["expected_direction"],
            "pooling_allowed": i2 <= 75.0,
            "n_studies": len(benchmark["studies"])
        }

    def _compare_results(
        self,
        system_output: Dict[str, Any],
        reference: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare system output to reference expectations.

        Implements pass/fail criteria from BACKEND_EXTERNAL_VALIDITY_TESTS.md
        """
        checks = {}

        # 1. Direction match (REQUIRED)
        expected_direction = reference["expected_direction"]
        actual_direction = system_output["direction"]

        checks["direction_match"] = {
            "expected": expected_direction,
            "actual": actual_direction,
            "pass": expected_direction == actual_direction,
            "required": True
        }

        # 2. Effect size magnitude tolerance
        expected_effect = reference["expected_effect_point"]
        actual_effect = system_output["pooled_effect"]
        tolerance = criteria["effect_size_tolerance"]

        diff = abs(actual_effect - expected_effect)

        checks["effect_magnitude"] = {
            "expected": expected_effect,
            "actual": actual_effect,
            "tolerance": tolerance,
            "difference": round(diff, 3),
            "pass": diff <= tolerance,
            "required": True
        }

        # 3. Confidence interval overlap
        expected_ci = reference["expected_effect_ci"]
        actual_ci = [system_output["ci_low"], system_output["ci_high"]]

        # CIs overlap if: max(low1, low2) < min(high1, high2)
        ci_overlap = max(expected_ci[0], actual_ci[0]) < min(expected_ci[1], actual_ci[1])

        checks["ci_overlap"] = {
            "expected": expected_ci,
            "actual": actual_ci,
            "pass": ci_overlap,
            "required": criteria["ci_overlap_required"]
        }

        # 4. Heterogeneity range
        expected_i2_range = reference["expected_i2_range"]
        actual_i2 = system_output["i_squared"]

        i2_in_range = expected_i2_range[0] <= actual_i2 <= expected_i2_range[1]

        # Allow some tolerance (within ±10% of range)
        i2_tolerance = 10
        i2_acceptable = (
            i2_in_range or
            (expected_i2_range[0] - i2_tolerance <= actual_i2 <= expected_i2_range[1] + i2_tolerance)
        )

        checks["i2_range"] = {
            "expected_range": expected_i2_range,
            "actual": actual_i2,
            "in_range": i2_in_range,
            "acceptable": i2_acceptable,
            "pass": i2_acceptable,
            "required": False  # Qualitative match acceptable
        }

        # 5. Pooling decision
        expected_pooling = reference["expected_pooling_decision"] == "allow"
        actual_pooling = system_output["pooling_allowed"]

        checks["pooling_decision"] = {
            "expected": expected_pooling,
            "actual": actual_pooling,
            "pass": expected_pooling == actual_pooling,
            "required": criteria["pooling_decision_must_match"]
        }

        # Overall pass: all REQUIRED checks must pass
        required_checks = [k for k, v in checks.items() if v.get("required", False)]
        overall_pass = all(checks[k]["pass"] for k in required_checks)

        return {
            "checks": checks,
            "required_checks_count": len(required_checks),
            "required_checks_passed": sum(1 for k in required_checks if checks[k]["pass"]),
            "overall_pass": overall_pass
        }

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all available benchmarks and generate report."""
        benchmarks = self.list_benchmarks()

        if not benchmarks:
            print("⚠️  No benchmarks found in datasets directory")
            return {"benchmarks": [], "summary": {"total": 0, "passed": 0, "failed": 0}}

        print(f"Found {len(benchmarks)} benchmark(s)")
        print()

        results = []

        for benchmark_id in benchmarks:
            try:
                benchmark = self.load_benchmark(benchmark_id)
                result = self.run_benchmark(benchmark)
                results.append(result)

                # Print result
                status = "✅ PASS" if result["pass"] else "❌ FAIL"
                print(f"{status}: {benchmark_id}")

                if not result["pass"]:
                    # Show which checks failed
                    for check_name, check_result in result["comparison"]["checks"].items():
                        if check_result.get("required") and not check_result["pass"]:
                            print(f"  ❌ {check_name}: {check_result}")

            except Exception as e:
                print(f"❌ ERROR: {benchmark_id} - {e}")
                results.append({
                    "benchmark_id": benchmark_id,
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                    "pass": False
                })

        # Generate summary
        total = len(results)
        passed = sum(1 for r in results if r.get("pass", False))
        failed = total - passed

        summary = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total * 100, 1) if total > 0 else 0
        }

        report = {
            "timestamp": datetime.now().isoformat(),
            "benchmarks": results,
            "summary": summary
        }

        # Save report
        report_file = self.reports_dir / f"REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print()
        print(f"{'='*80}")
        print("BENCHMARK SUMMARY")
        print(f"{'='*80}")
        print(f"Total: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Pass rate: {summary['pass_rate']}%")
        print()
        print(f"Report saved: {report_file}")

        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run meta-analysis benchmarks")
    parser.add_argument(
        "--dataset",
        help="Run specific benchmark dataset (e.g., omega3_depression_v1)"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate report from latest results"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available benchmarks"
    )

    args = parser.parse_args()

    # Get directories
    script_dir = Path(__file__).parent
    datasets_dir = script_dir / "datasets"
    reports_dir = script_dir / "reports"

    runner = BenchmarkRunner(datasets_dir, reports_dir)

    # List benchmarks
    if args.list:
        benchmarks = runner.list_benchmarks()
        print(f"Available benchmarks ({len(benchmarks)}):")
        for b in benchmarks:
            print(f"  - {b}")
        return 0

    # Run specific benchmark
    if args.dataset:
        try:
            benchmark = runner.load_benchmark(args.dataset)
            result = runner.run_benchmark(benchmark)

            status = "✅ PASS" if result["pass"] else "❌ FAIL"
            print()
            print(status)

            return 0 if result["pass"] else 1

        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    # Run all benchmarks
    report = runner.run_all_benchmarks()

    # Exit code: 0 if all passed, 1 if any failed
    return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
