#!/usr/bin/env python3
"""
Numeric validation of benchmark meta-analysis reports.

- Loads all JSON reports from tests/benchmarks/reports/*.json
- Performs basic consistency checks:
  * If status indicates insufficient evidence → no pooled effect size
  * If status indicates pooling → check effect size, CI, p-value, I² present
  * If I² is reported → check interpretation is roughly aligned
- Writes a summary file:
  tests/external_validation/NUMERIC_VALIDATION_SUMMARY.json
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "tests" / "benchmarks" / "reports"
OUT_PATH = ROOT / "tests" / "external_validation" / "NUMERIC_VALIDATION_SUMMARY.json"


def load_reports() -> List[Dict[str, Any]]:
    reports: List[Dict[str, Any]] = []
    if not REPORT_DIR.exists():
        print(f"[numeric] Report dir does not exist: {REPORT_DIR}")
        return reports

    for path in sorted(REPORT_DIR.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            data["_file"] = str(path)
            reports.append(data)
        except Exception as e:
            print(f"[numeric] Failed to load {path}: {e}")
    return reports


def is_insufficient_status(status: str) -> bool:
    status = (status or "").lower()
    return any(
        key in status
        for key in [
            "insufficient",
            "no_studies",
            "cannot_pool_high_heterogeneity",
            "cannot_pool",
        ]
    )


def validate_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a per-report validation summary.
    """
    filename = report.get("_file", "UNKNOWN")
    status = str(report.get("status", "")).lower()

    ma = report.get("meta_analysis") or {}
    het = report.get("heterogeneity") or {}

    effect_size = ma.get("effect_size")
    ci_lower = ma.get("ci_lower")
    ci_upper = ma.get("ci_upper")
    p_value = ma.get("p_value")

    i2 = het.get("i_squared")
    i2_interp = (het.get("interpretation") or "").lower()

    checks: List[str] = []
    failures: List[str] = []

    # 1) Insufficient evidence → no pooled effect
    if is_insufficient_status(status):
        if effect_size is not None:
            failures.append("Insufficient evidence status but pooled effect_size present.")
        else:
            checks.append("Insufficient evidence correctly reports no pooled effect size.")

    else:
        # 2) Pooled analysis → effect size, CI, p-value required
        if effect_size is None:
            failures.append("Pooled analysis missing effect_size.")
        if ci_lower is None or ci_upper is None:
            failures.append("Pooled analysis missing CI bounds.")
        if p_value is None:
            failures.append("Pooled analysis missing p_value.")
        if not failures:
            checks.append("Pooled analysis includes effect size, CI, and p-value.")

    # 3) Heterogeneity consistency (if reported)
    if i2 is not None:
        try:
            i2_float = float(i2)
        except Exception:
            failures.append(f"I² is not numeric: {i2}")
            i2_float = None

        if i2_float is not None:
            # Basic ranges
            if i2_float < 0 or i2_float > 100:
                failures.append(f"I² out of range: {i2_float}")
            else:
                checks.append("I² within [0, 100].")

            # Interpretation rough alignment
            if "very high" in i2_interp or "high" in i2_interp:
                if i2_float < 50:
                    failures.append(
                        f"I² interpretation 'high/very high' but numeric I²={i2_float} < 50."
                    )
            elif "low" in i2_interp:
                if i2_float > 50:
                    failures.append(
                        f"I² interpretation 'low' but numeric I²={i2_float} > 50."
                    )

    return {
        "file": filename,
        "status": status,
        "checks_passed": checks,
        "failures": failures,
        "ok": len(failures) == 0,
    }


def main() -> None:
    os.makedirs(OUT_PATH.parent, exist_ok=True)
    reports = load_reports()
    if not reports:
        print("[numeric] No reports found. Nothing to validate.")
        summary = {
            "total_reports": 0,
            "num_ok": 0,
            "num_failed": 0,
            "reports": [],
        }
        OUT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return

    per_report = [validate_report(r) for r in reports]
    num_ok = sum(1 for r in per_report if r["ok"])
    num_fail = len(per_report) - num_ok

    summary = {
        "total_reports": len(per_report),
        "num_ok": num_ok,
        "num_failed": num_fail,
        "reports": per_report,
    }

    OUT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("[numeric] Validation complete.")
    print(f"[numeric] total_reports={len(per_report)} ok={num_ok} failed={num_fail}")
    print(f"[numeric] Summary written to {OUT_PATH}")


if __name__ == "__main__":
    main()
