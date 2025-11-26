# Meta-Analysis Platform – Testing Overview

This folder contains the **real**, non-placeholder test specifications for your meta-analysis platform.  
Everything here is written so an AI assistant (Claude / “agent orchestra”) or a human QA can follow it **step‑by‑step**.

The suite is split into 4 pillars:

1. **Integrity Guardrails (Internal Validity)**
2. **External Validity (Real‑World Benchmarks)**
3. **Frontend Experience & UX Safety**
4. **Scientific / Editorial Compliance & Human Review**

Each markdown file in this folder has:

- A **Purpose** section
- A **“For Claude / Agent” system prompt** block
- Concrete **test cases / checklists**
- **Pass / fail criteria**

You can treat this folder as the *testing brain* of the project. The code implements the guardrails; these docs define how we **prove** they work in the wild.
