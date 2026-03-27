# Codebase — Technical Reference Hub

For AI engineers, developers, and architects working on the CashRoom Compliance System.

## Folder Structure

| Folder | Purpose | Who Writes |
|---|---|---|
| `architecture/` | System design, API reference, DB schema | Dev Lead, Architect |
| `decisions/` | Technical decisions with rationale (repo strategy, design breakdowns) | Dev Lead |
| `gap-analysis/` | Prototype vs codebase fit, technical gaps, screen modification maps | Dev Lead |
| `implementation-plans/` | Feature-level TDD plans, implementation strategies with test cases | Dev Lead, AI Engineer |
| `developer-guide/` | Onboarding, handover docs, test case reference | Dev Lead |
## Quick Links

- **AI Context**: `CLAUDE.md` — full technical context for Claude Code
- **Architecture**: `architecture/ARCHITECTURE.md` — system diagram, roles, submission lifecycle
- **API Reference**: `architecture/API_DOC.md` — complete endpoint reference
- **DB Schema**: `architecture/DB_DESIGN.md` — ERD and table details
- **Getting Started**: `developer-guide/DEVELOPER_HANDOVER.md` — screen-by-screen guide

## Tech Stack

- **Frontend**: React 19 + TypeScript + Vite (port 3000)
- **Backend**: FastAPI + Python 3.13 (port 8000)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Migrations**: Alembic
- **Auth**: JWT (access + refresh tokens)
- **Tests**: pytest (backend), no frontend test runner

## Key Patterns

- State-based navigation (no React Router) — `AppShell` tracks `{ panel, ctx }`
- Mock data fallback for demo accounts (`src/mock/data.ts`)
- Role-based API guards via `require_roles()` dependency
- Audit logging via `services/audit.py`
- Pydantic schemas with `from_attributes=True` for ORM serialization
- Paginated list endpoints with `page`/`page_size` query params
