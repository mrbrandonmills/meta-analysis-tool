# Manual Evaluation Protocol – Human Review of System Outputs

Even with strong automated tests, **humans** must occasionally look at outputs and ask:
“Does this make sense, scientifically and clinically?”

This protocol defines how to do that systematically.

---

## 1. Roles

- **Domain Expert Reviewer** – e.g., cardiologist, psychologist, etc.
- **Methodology Reviewer** – statistician / epidemiologist / methods person.
- **Platform Operator** – knows how to trigger analyses and gather logs.

One person can wear multiple hats, but roles should be conceptually distinct.

---

## 2. Sampling Strategy

You don’t need to review every single run. Instead:

- Sample:
  - New feature releases.
  - New benchmark topics.
  - Random 5–10% of user jobs (in an anonymized, opt-in fashion if allowed).

---

## 3. Evaluation Dimensions

For each sampled report, reviewers rate:

1. **Correctness (0–5)**
   - 0 – Clearly wrong or nonsensical.
   - 3 – Mostly correct, minor issues.
   - 5 – Statistically and conceptually sound.
2. **Transparency (0–5)**
   - Does the report show enough to understand what was done?
3. **Uncertainty Handling (0–5)**
   - Are limitations and uncertainty honestly presented?
4. **Usefulness (0–5)**
   - Would a practitioner find this report actionable/informative?
5. **Safety (0–5)**
   - Does the system avoid overstatement or unwarranted clinical claims?

Overall score: average of the 5 dimensions.

---

## 4. Manual Review Form (Template)

Reviewers can fill something like:

```text
REPORT ID: ____________________
DATE: _________________________
REVIEWER ROLE(S): ______________

1. Correctness (0–5): ____
   Notes:

2. Transparency (0–5): ____
   Notes:

3. Uncertainty Handling (0–5): ____
   Notes:

4. Usefulness (0–5): ____
   Notes:

5. Safety (0–5): ____
   Notes:

OVERALL SCORE: ____ / 5

RED FLAGS (if any):
- [ ] Possible hallucinated data
- [ ] Misleading interpretation
- [ ] Clinical recommendation without sufficient evidence
- [ ] Other: ___________________

RECOMMENDED ACTIONS:
- [ ] Accept as-is
- [ ] Accept with minor revisions
- [ ] Investigate method / code
- [ ] Block feature until fixed
```

---

## 5. Feedback Loop

- Store all manual evaluations in a small database / spreadsheet.
- Periodically compute:
  - Average scores by topic.
  - Common failure modes.
- Feed these insights back into:
  - Automated tests (expand edge cases).
  - Prompt refinements (for QA / explanation agents).
  - UI copy improvements.

This is how the system evolves from “technically correct” to “professionally trustworthy” over time.
