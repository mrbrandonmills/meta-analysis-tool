# Repository Guidelines

## Project Structure & Module Organization
`backend/` houses the FastAPI + agent runtime (Poetry-managed, see `app/agents`, `app/services`, `app/routes`) along with Alembic state, worker scripts, and Dockerfiles. `frontend/` is the Next.js 14 app (App Router in `src/app`, shared UI in `src/components`, client helpers in `src/lib`). `docs/`, `ai-management/`, and `scripts/` keep the architecture briefs, QA plans, and helper scripts (`run-all-tests.sh`, `check-coverage.sh`), while `config/` plus the root Docker/Vercel/Railway files describe each deployment target.

## Build, Test, and Development Commands
- `docker compose up -d` — start Postgres, Redis, backend, worker, and frontend the same way CI does.
- `cd backend && poetry install && poetry run uvicorn app.main:app --reload` — local API development; use `poetry run alembic upgrade head` for schema changes.
- `cd frontend && npm install && npm run dev` — run the UI; use `npm run build && npm start` only when reproducing production issues.
- `./scripts/run-all-tests.sh` — umbrella test harness shared with CI (use flags as needed).
- `cd backend && poetry run pytest -m "not slow" --cov=app` — targeted Python tests and fresh coverage.

## Coding Style & Naming Conventions
Backend code follows PEP 8 with 100-character lines, Black formatting, strict MyPy, and descriptive modules (`app/agents/search_agent.py`); keep database access inside SQLAlchemy repositories under `app/services/persistence`. Frontend files use kebab-case (`src/components/agent-card.tsx`), PascalCase exports, and tidy Tailwind utilities. Shared types belong in `src/types`, and prompt/AI config changes must be mirrored in `ai-management` for auditability.

## Testing Guidelines
Use `pytest` markers (`slow`, `integration`, `agent`) from `pytest.ini` to scope runs; CI enforces ≥80% backend coverage, so review `backend/htmlcov/index.html` before merging. Frontend changes must pass `npm run lint`, `npm run test`, and—when data viz shifts—`npm run test:coverage`. For full-stack validation lean on `comprehensive_api_test.sh` or `production_readiness_test.py`, and document any manual QA evidence in `QA_AUDIT_SUMMARY.txt` when touching flows listed in `COMPREHENSIVE_TEST_PLAN.md`.

## Commit & Pull Request Guidelines
Follow the existing short, descriptive subjects with optional tags (`Fix`, `DOCS`, `Deploy`) plus an imperative summary (e.g., `Fix: correct AgentStatusCard props`). Each PR must link the relevant architecture/test doc, include screenshots for UI changes, spell out migrations or worker config edits, and wait for the full GitHub Actions matrix (backend, frontend, e2e, security) to finish before requesting review.

## Security & Configuration Tips
Keep `.env*`, Anthropic/OpenAI keys, Supabase credentials, and `meta_analysis.db` dumps out of Git; rely on the templates in `backend/.env.example` and `frontend/.env.local.example`, rotate secrets via hosting dashboards, and scrub research data before sharing artifacts.
