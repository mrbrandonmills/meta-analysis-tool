#!/usr/bin/env python3
"""
Convert benchmark rollup reports to individual scenario reports.

Reads REPORT_*.json files from benchmarks/reports/ and extracts
each benchmark into a separate report file with the format expected
by the numeric validator.
"""

import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "tests" / "benchmarks" / "reports"


def interpret_i2(i2: float) -> str:
    """Interpret I² value into qualitative category."""
    if i2 < 25:
        return "very low"
    elif i2 < 50:
        return "low"
    elif i2 < 75:
        return "moderate"
    else:
        return "high"


def convert_benchmark_to_report(benchmark: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a single benchmark entry to expected report format."""
    system_output = benchmark.get("system_output", {})

    # Determine status
    passed = benchmark.get("pass", False)
    pooling_allowed = system_output.get("pooling_allowed", False)

    if passed and pooling_allowed:
        status = "success"
    elif not pooling_allowed:
        status = "cannot_pool_high_heterogeneity"
    else:
        status = "insufficient_evidence"

    # Get I² and interpretation
    i2 = system_output.get("i_squared")
    i2_interp = interpret_i2(i2) if i2 is not None else None

    # Build report in expected format
    report = {
        "benchmark_id": benchmark.get("benchmark_id"),
        "timestamp": benchmark.get("timestamp"),
        "status": status,
        "meta_analysis": {
            "effect_size": system_output.get("pooled_effect"),
            "ci_lower": system_output.get("ci_low"),
            "ci_upper": system_output.get("ci_high"),
            "p_value": system_output.get("p_value"),
            "model": system_output.get("model"),
        },
        "heterogeneity": {
            "i_squared": i2,
            "interpretation": i2_interp,
        },
        "n_studies": system_output.get("n_studies"),
        "reference": benchmark.get("reference"),
    }

    return report


def main() -> None:
    if not REPORT_DIR.exists():
        print("[convert] Report directory does not exist")
        return

    # Find all REPORT_*.json files
    report_files = sorted(REPORT_DIR.glob("REPORT_*.json"))

    if not report_files:
        print("[convert] No REPORT_*.json files found")
        return

    # Use the most recent report
    latest_report = report_files[-1]
    print(f"[convert] Processing {latest_report.name}")

    with latest_report.open("r") as f:
        data = json.load(f)

    benchmarks = data.get("benchmarks", [])

    if not benchmarks:
        print("[convert] No benchmarks found in report")
        return

    # Convert each benchmark to individual report
    for benchmark in benchmarks:
        benchmark_id = benchmark.get("benchmark_id", "unknown")
        report = convert_benchmark_to_report(benchmark)

        # Save as individual JSON file
        output_path = REPORT_DIR / f"{benchmark_id}.json"
        with output_path.open("w") as f:
            json.dump(report, f, indent=2)

        print(f"[convert] Created {output_path.name}")

    print(f"[convert] Converted {len(benchmarks)} benchmarks to individual reports")


if __name__ == "__main__":
    main()
