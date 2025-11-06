<!--
  Project: clouddev
  Purpose: guidance for AI coding agents (Copilot / assistants) to be productive in this repo.
  Keep this short, explicit, and focused on repository-specific patterns, workflows, and files.
-->

# Copilot instructions for the clouddev repository

This file gives focused, actionable guidance for an AI coding assistant working on this repository. Keep responses concise and refer to exact files when recommending edits.

## Big picture
- Monorepo with two main services: `backend` (FastAPI + SQLAlchemy + Alembic) and `frontend` (Next.js).
- Infrastructure and deployment live under `infrastructure/` (Terraform + Helm charts for k8s).
- Local development uses Docker Compose orchestrated by `Taskfile.yaml` (convenience tasks).

Key files:
- `backend/main.py` — FastAPI entrypoint and lifecycle (creates DB tables on startup).
- `backend/config/db.py` — SQLAlchemy engine, `Base`, `SessionLocal`, and Redis helpers. Use this for DB session patterns.
- `backend/requirements.txt` — runtime dependencies (FastAPI, SQLAlchemy, Alembic, psycopg2-binary, structlog, celery, redis, etc.).
- `frontend/` — Next.js app. See `frontend/README.md` and `frontend/Dockerfile` for build/deploy specifics.
- `Taskfile.yaml` — primary developer tasks (dev, build, test, db-migrate, helm install). Use it for local dev commands.

## Coding patterns & conventions
- SQLAlchemy models use the `declarative_base()` exported as `Base` in `backend/config/db.py`. Import `Base` when adding new models.
- Use typed ORM fields with `Mapped[...]` + `mapped_column(...)` (see `backend/models/*.py`). Relationship strings are used (no direct circular imports).
- JSON fields for lightweight nested data (e.g., `checklist`) are stored using `sqlalchemy.dialects.postgresql.JSON` and validated with `@validates` on the model.
- Validation and convenience methods live on models (e.g., `add_checklist_item`) — but these mutate instance state only; persist with a DB session and `commit()`.
- Logging uses `structlog` configured in `backend/config/db.py` and `backend/main.py`; preserve structured logging format when adding logs.

## Developer workflows (how to run & test)
- Start full local dev (Compose): `task dev` (uses `docker compose -f docker-compose.yaml -f docker-compose.dev.yaml --env-file .env.dev up --build`).
- Run only backend locally (inside compose): backend uses `uvicorn main:app --host 0.0.0.0 --port 8000 --reload` in the dev compose override.
- Database migrations: `task db-migrate` will run `alembic upgrade head` inside the backend container.
- Tests: `task test` runs `pytest` inside the backend container.
- Helm (local k8s): `task helm-install-devk8s` or `task helm-upgrade-devk8s` in `infrastructure/k8s`.

## Project-specific rules for changes
- When modifying models, update Alembic migrations (use `alembic revision --autogenerate -m "msg"`) and ensure `task db-migrate` applies them.
- Avoid importing `User`/`Task` classes across modules directly to prevent circular imports — prefer relationship strings (example in `Task` model).
- When adding a new environment variable, add it to the appropriate `.env.*` files and to the Helm `values-*.yaml` if it’s required in k8s.

## Integration points & external services
- Auth: Auth0 is used in the frontend and backend. Secrets are read from environment variables (see `frontend/lib/config.ts` and `docker-compose.dev.yaml`).
- Persistence: PostgreSQL (via `psycopg2-binary`). Connection string assembled in `backend/config/db.py` from env vars.
- Background: Celery + Redis (see `requirements.txt` and `config/db.py`'s Redis helpers). Use `get_redis()` for async redis access.
- Observability: AWS X-Ray and CloudWatch integrations exist in Terraform modules; keep tracing context when adding instrumentation.

## Helpful examples (copyable patterns)
- DB session dependency (use `get_db()` from `backend/config/db.py` in routes):
  - `def get_db(): db = SessionLocal(); try: yield db finally: db.close()`
- Model enum column (Task status): use `from sqlalchemy import Enum as SQLEnum` and `mapped_column(SQLEnum(MyEnum, name="my_enum"), ...)`.
- JSON validation on model: use `@validates('checklist')` to ensure shape before commit (see `backend/models/models.py`).

## When to ask the human
- If the change touches Terraform, Helm, or shared infra values (these may have live consequences) — ask before applying.
- If credentials or secrets are required, request the appropriate environment file or secret key names; do not guess or write secrets in code.

## Files to inspect for pull requests
- `backend/main.py`, `backend/config/db.py`, `backend/models/` (models and validators), `backend/routes/` (API endpoints), `Taskfile.yaml`, `docker-compose*.yaml`, `infrastructure/` (k8s & terraform).

---

If anything above is unclear or you want rules expanded (e.g., database transaction patterns, testing conventions, or specific linter/pre-commit hooks), tell me which area to expand.
