# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CashRoom Compliance System (CCS)** — a full-stack web app for Canteen Vending Services (Compass Group) to digitise daily cash reconciliation. Operators submit cash counts, managers approve them, controllers/DGMs schedule physical verification visits, and admins oversee the whole system.

**Phase 2** (in progress on `phase2-features` branch) adds a **Cash Reasonableness Test** module — a quarterly compliance control that checks whether each cash room holds appropriate funds relative to operational usage.

## Commands

### Frontend (`cd frontend`)
```bash
npm run dev       # Vite dev server on port 3000 (auto-opens browser)
npm run build     # tsc -b (strict type-check) + vite build → dist/
npm run lint      # ESLint
npm run preview   # Preview production build
```
No test runner is configured for the frontend.

### Backend (`cd backend`)
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload   # Dev server on port 8000
pytest                                    # Run tests
pytest tests/test_submissions.py -k "test_name"  # Single test
alembic upgrade head                      # Apply DB migrations
alembic revision --autogenerate -m "..."  # Generate new migration
```

### Database Utilities (`cd backend`)
```bash
python clean_db.py    # Wipe and recreate tables
python seed.py        # Seed with base data
python seed_demo.py   # Seed with demo data for all roles
```

### Full Stack (Docker)
```bash
docker compose up --build                     # Dev with SQLite
docker compose --profile prod up --build      # Prod with PostgreSQL
```

### Email Testing
```bash
docker run -p 1080:1080 -p 1025:1025 maildev/maildev  # Local mail server
# View emails at http://localhost:1080
```

## Architecture

```
frontend/  (React 19 + TypeScript + Vite)   → port 3000
backend/   (FastAPI + Python 3.13)          → port 8000
```

Backend API base URL: `VITE_API_URL` env var (defaults to `http://localhost:8001/v1`).
Swagger UI: `http://localhost:8000/docs`

### Frontend Architecture

**No React Router** — navigation is entirely state-based:
- `App.tsx` holds auth state; on login renders `AppShell`
- `AppShell` tracks `{ panel: string, ctx: object }` in local state
- All screens receive `onNavigate(panel, ctx?)` to switch views
- `renderPanel()` switch statement maps panel names → components
- Screen context (locationId, submissionId, date) passed via `ctx`

**API layer** (`src/api/`):
- `client.ts` — JWT fetch wrapper; token stored in `localStorage` as `ccs_token`
- `auth.ts` — login/logout/me/refresh; refresh token as `ccs_refresh_token`
- `types.ts` — **canonical source of truth** for all API request/response TypeScript types
- Feature modules: `submissions.ts`, `verifications.ts`, `admin.ts`, `compliance.ts`, `audit.ts`, `reports.ts`
- Login falls back to mock data (`src/mock/data.ts`) for demo accounts (password: `demo1234`)

**State**: No global state library — all local to components via hooks.

**Styling**: Custom CSS design system in `src/index.css` (no CSS-in-JS). CSS custom properties: `--g0`–`--g9` greens, `--amb`, `--red`, `--ow`. Fonts: DM Serif Display (headings) + DM Sans (body). Ant Design 6 is installed but the custom CSS is primary.

**TypeScript**: Strict mode with `noUnusedLocals` and `noUnusedParameters` — unused imports will break `npm run build`.

**Roles & panels** (`src/pages/<role>/`):

| Role | Panels |
|------|--------|
| `operator` | op-start, op-method, op-form, op-chat, op-excel, op-readonly, op-drafts, op-missed |
| `controller` | ctrl-daily-report (reuses `manager/MgrApprovals`), ctrl-dashboard, ctrl-dgm-review |
| `dgm` | dgm-dash, dgm-history, dgm-log |
| `admin` | adm-audit, adm-locations, adm-users, adm-config, adm-compliance, adm-import, adm-reports |
| `regional-controller` | rc-trends (plus adm-audit, adm-compliance, adm-reports, operator/controller access) |

DGM/Regional-Controller can receive additional operator/controller access via `access_grants` (managed by `src/utils/operatorAccess.ts`).

### Backend Architecture

```
backend/app/
├── main.py              # FastAPI app + CORS + APScheduler lifespan
├── api/v1/router.py     # Mounts all route modules under /v1
├── api/v1/              # auth, submissions, verifications, locations,
│                        # users, config, compliance, reports, audit, admin
├── core/                # config.py (Pydantic Settings), security.py (JWT/bcrypt), deps.py
├── db/                  # session.py (engine + SessionLocal), base.py
├── models/              # SQLAlchemy ORM: user, location, submission, verification, config, audit, access_grant
├── schemas/             # Pydantic request/response schemas (mirror models/)
├── services/            # email.py (fastapi-mail + Jinja2), scheduler.py (APScheduler), audit.py
└── templates/email/     # HTML email templates
```

**Database**: SQLite (`cashroom.db`) in dev; PostgreSQL in prod (set `DATABASE_URL` in `.env`).
**Migrations**: Alembic — 7 migration files in `alembic/versions/`.
**Background jobs**: APScheduler (daily 08:00 UTC submission reminders).
**Auth**: JWT access token (1 hr) + refresh token (7 days). Role enforcement via `require_roles()` in `core/deps.py`.

**Roles enum** (in `models/user.py`): OPERATOR, CONTROLLER, DGM, ADMIN, AUDITOR, REGIONAL_CONTROLLER.

**Key model fields for Phase 2**:
- `locations.cost_center` (String(50)) — financial identifier, used for grouping
- `locations.expected_cash` — imprest amount
- `submissions.sections` (JSON) — contains sA through sI, sH, sJ denomination data
- `submissions.total_cash`, `submissions.variance`, `submissions.variance_pct`

### Key Business Rules

| Rule | Detail |
|------|--------|
| Imprest Balance | Fixed cash fund per location; submissions track deviation |
| Variance Tolerance | >5% variance from imprest requires written explanation |
| Approval SLA | Manager must approve/reject within 48 hours |
| Controller DOW Rule | Warn if controller visits same location on same weekday two weeks running |
| DGM Monthly Rule | Block second DGM visit to same location in a calendar month |
| One Submission Per Day | Location cannot have two submissions for the same date |
| Fiscal Year | Oct 1 – Sep 30. Periods P1 (Oct) through P12 (Sep). Quarters Q1–Q4 |

### Environment Variables

Copy `backend/.env.example` → `backend/.env`. Key vars:
- `DATABASE_URL` — `sqlite:///./cashroom.db` (dev) or PostgreSQL connection string
- `SECRET_KEY` — JWT signing key
- `SMTP_HOST`, `SMTP_PORT` — email (default: localhost:1025 for mailcatcher)
- `EMAIL_ENABLED` — toggle email sending

## Project Structure (Non-obvious)

The project uses a **two-hub documentation system** separating engagement concerns from technical concerns:

### `control-room/` — Engagement Strategist Hub
For delivery leads, client stakeholders, and project managers. Contains business-level information.

| Folder | Purpose |
|---|---|
| `requirements/` | Business requirements, process docs, prototypes |
| `planning/` | Phase plans, build approach, implementation summaries (business-readable) |
| `progress/` | Daily status updates — check here for latest project state |
| `gap-analysis/` | Engagement-level coverage and risk summaries for stakeholders |
| `open-items/` | Blockers, pending questions, action items with owners |
| `meeting-notes/` | Client call and internal sync notes |
| `client-comms/` | Key client messages and approvals |
| `change-log/` | Scope changes and CR tracking |
| `sign-offs/` | UAT and milestone approvals |

### `codebase/` — AI Engineer & Architect Hub
For developers, AI engineers, and technical architects. Contains implementation-level information.

| Folder | Purpose |
|---|---|
| `architecture/` | System design (ARCHITECTURE.md), API reference (API_DOC.md), DB schema (DB_DESIGN.md) |
| `decisions/` | Technical decisions with rationale (repo strategy, design breakdowns) |
| `gap-analysis/` | Technical gap analysis — prototype vs codebase fit, screen modification maps |
| `implementation-plans/` | Feature-level TDD plans with test cases, file paths, code patterns |
| `developer-guide/` | Developer handover (DEVELOPER_HANDOVER.md), test cases (TEST_CASES.md) |
| `ai-instructions/` | AI assistant context (mirror of this file for reference) |

### Other

- `docs/` — Legacy location; canonical docs now in `codebase/architecture/` and `codebase/developer-guide/`
- `generate_rc_test_excel.py` — Test utility for generating Regional Controller test Excel files

## Key Documentation

### For Engagement Strategist
- `control-room/planning/` — Phase plans and build approach
- `control-room/progress/` — Daily status updates (latest state of the project)
- `control-room/gap-analysis/2026-03-25_engagement-gap-summary.md` — Coverage and risk summary
- `control-room/open-items/` — Current blockers and pending decisions
- `control-room/requirements/` — Phase 2 requirements and process document

### For AI Engineer / Architect
- `codebase/architecture/ARCHITECTURE.md` — System diagram, roles, submission lifecycle
- `codebase/architecture/API_DOC.md` — Complete API endpoint reference
- `codebase/architecture/DB_DESIGN.md` — Database ERD and schema details
- `codebase/developer-guide/DEVELOPER_HANDOVER.md` — Developer onboarding, screen-by-screen guide
- `codebase/implementation-plans/` — TDD plans with test cases and file paths
- `codebase/gap-analysis/` — Technical prototype vs codebase fit analysis
- `codebase/decisions/` — Technical decisions (repo strategy, component breakdowns)
