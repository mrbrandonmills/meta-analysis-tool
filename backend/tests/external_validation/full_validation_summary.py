#!/usr/bin/env python3
"""
Full validation rollup.

Reads:
- NUMERIC_VALIDATION_SUMMARY.json
- LLM_VALIDATION_SUMMARY.json

Produces:
- FULL_VALIDATION_ROLLUP.json

This does NOT interpret LLM answers; it only verifies that prompts
exist and that numeric checks passed.
"""

import json
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[2]
NUMERIC_PATH = ROOT / "tests" / "external_validation" / "NUMERIC_VALIDATION_SUMMARY.json"
LLM_PATH = ROOT / "tests" / "external_validation" / "LLM_VALIDATION_SUMMARY.json"
OUT_PATH = ROOT / "tests" / "external_validation" / "FULL_VALIDATION_ROLLUP.json"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"_missing": True}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": str(e)}


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    numeric = load_json(NUMERIC_PATH)
    llm = load_json(LLM_PATH)

    numeric_missing = numeric.get("_missing", False)
    llm_missing = llm.get("_missing", False)

    total_reports = 0
    numeric_ok = None
    numeric_failed = None

    if not numeric_missing and "_error" not in numeric:
        total_reports = numeric.get("total_reports", 0)
        numeric_ok = numeric.get("num_ok")
        numeric_failed = numeric.get("num_failed")

    llm_total = 0
    if not llm_missing and "_error" not in llm:
        llm_total = llm.get("total_reports", 0)

    all_numeric_ok = (
        numeric_ok is not None
        and numeric_failed is not None
        and numeric_failed == 0
    )

    rollup = {
        "numeric_summary_present": not numeric_missing,
        "llm_summary_present": not llm_missing,
        "numeric_summary_error": numeric.get("_error"),
        "llm_summary_error": llm.get("_error"),
        "total_reports_numeric": total_reports,
        "total_reports_llm": llm_total,
        "numeric_all_ok": all_numeric_ok,
        "details": {
            "numeric": numeric if not numeric_missing else None,
            "llm": llm if not llm_missing else None,
        },
    }

    if all_numeric_ok and not llm_missing and "_error" not in llm:
        rollup["overall_status"] = "READY_FOR_EXTERNAL_LLM_REVIEW"
    elif all_numeric_ok:
        rollup["overall_status"] = "NUMERIC_OK_LLM_SETUP_PENDING"
    else:
        rollup["overall_status"] = "NUMERIC_ISSUES_DETECTED"

    OUT_PATH.write_text(json.dumps(rollup, indent=2), encoding="utf-8")
    print(f"[rollup] Wrote full validation rollup to {OUT_PATH}")
    print(f"[rollup] overall_status={rollup['overall_status']}")


if __name__ == "__main__":
    main()
