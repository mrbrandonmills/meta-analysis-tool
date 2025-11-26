#!/usr/bin/env python3
"""
LLM validation prompt generator.

- Reads all Markdown reports from tests/benchmarks/reports/*.md
- For each, generates:
  * A Claude prompt
  * A Gemini prompt
- Writes them to:
  tests/external_validation/LLM_VALIDATION_SUMMARY.json

Intended flow:
- Human opens Claude / Gemini
- Copies prompt + report content
- Asks model to verify methodology and coherence of conclusions.
"""

import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "tests" / "benchmarks" / "reports"
OUT_PATH = ROOT / "tests" / "external_validation" / "LLM_VALIDATION_SUMMARY.json"


def load_markdown_reports() -> List[Path]:
    if not REPORT_DIR.exists():
        print(f"[llm] Report dir does not exist: {REPORT_DIR}")
        return []
    return sorted(REPORT_DIR.glob("*.md"))


def build_claude_prompt(filename: str) -> str:
    return f"""
You are an expert in meta-analysis methodology and publication standards.

I will paste the FULL text of a meta-analysis report from a research platform.
Your job is to independently verify whether the report is:

1. Methodologically coherent
2. Internally consistent (numbers, interpretations, and heterogeneity)
3. Aligned with standard meta-analytic practice (e.g., PRISMA/Cochrane)
4. Transparent about limitations and uncertainty

For the pasted report, please:

A. Summarize the main research question and findings in 3–5 sentences.
B. Evaluate whether the handling of:
   - study inclusion/exclusion
   - heterogeneity (I², Q test)
   - effect size reporting (estimate, CI, p-value)
   - risk of bias / credibility assessment
   is methodologically sound.

C. List any red flags, inconsistencies, or ambiguous decisions you detect.
D. Provide a 0–100 score for overall methodological credibility of this report.
E. Provide specific recommendations for improvement, if any.

Report filename: {filename}

IMPORTANT:
- Do NOT invent additional data.
- Base your critique solely on the contents of the report that I paste.
"""


def build_gemini_prompt(filename: str) -> str:
    return f"""
You are reviewing a meta-analysis report for statistical and methodological quality.

I will provide the full text of the report.
Please review it and respond with:

1. A brief summary (3–5 sentences) of the question, methods, and main findings.
2. An assessment of:
   - Whether the decision to pool or not pool studies is justified given heterogeneity.
   - Whether the effect size estimates and confidence intervals are presented clearly.
   - Whether limitations and risk of bias are discussed appropriately.

3. Any inconsistencies or potential errors you notice in:
   - Logic
   - Interpretation of I² and heterogeneity
   - Interpretation of significance/non-significance

4. A 0–100 rating for:
   - Statistical soundness
   - Clarity of reporting
   - Transparency about uncertainty

Give your answer as a structured JSON-like bullet list, not actual JSON.

Report filename: {filename}

Use only the information in the report; do not assume additional unpublished data.
"""


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    md_files = load_markdown_reports()
    entries: List[Dict[str, Any]] = []

    if not md_files:
        print("[llm] No Markdown reports found. Nothing to generate.")
    else:
        for path in md_files:
            entry = {
                "report_file": str(path),
                "claude_prompt": build_claude_prompt(path.name).strip(),
                "gemini_prompt": build_gemini_prompt(path.name).strip(),
            }
            entries.append(entry)

    summary = {
        "total_reports": len(entries),
        "entries": entries,
        "instructions": (
            "For each entry, open the listed report file, copy its full contents, "
            "and paste it together with the corresponding claude_prompt or "
            "gemini_prompt into the respective model. Save the model's critique "
            "separately if you want a full external review archive."
        ),
    }

    OUT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[llm] Wrote LLM validation prompts for {len(entries)} reports to {OUT_PATH}")


if __name__ == "__main__":
    main()
