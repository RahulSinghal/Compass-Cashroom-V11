# Codebase — CLAUDE.md

Technical context for AI engineers, developers, and architects working on CCS.

## Architecture

```
frontend/  (React 19 + TypeScript + Vite)   → port 3000
backend/   (FastAPI + Python 3.13)          → port 8000
```

Backend API base URL: `VITE_API_URL` env var (defaults to `http://localhost:8000/v1`).
Swagger UI: `http://localhost:8000/docs`

## Frontend Architecture

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
- Feature modules: `submissions.ts`, `verifications.ts`, `admin.ts`, `compliance.ts`, `audit.ts`, `reports.ts`, `reasonableness.ts`
- Login falls back to mock data (`src/mock/data.ts`) for demo accounts (password: `demo1234`)

**State**: No global state library — all local to components via hooks.

**Styling**: Custom CSS design system in `src/index.css` (no CSS-in-JS). CSS custom properties: `--g0`–`--g9` greens, `--amb`, `--red`, `--ow`. Fonts: DM Serif Display (headings) + DM Sans (body). Ant Design 6 is installed but the custom CSS is primary.

**TypeScript**: Strict mode with `noUnusedLocals` and `noUnusedParameters` — unused imports will break `npm run build`.

**Roles & panels** (`src/pages/<role>/`):

| Role | Panels |
|------|--------|
| `operator` | op-start, op-method, op-form, op-chat, op-excel, op-readonly, op-drafts, op-missed |
| `controller` | ctrl-daily-report, ctrl-dashboard, ctrl-dgm-review, ctrl-reasonableness |
| `dgm` | dgm-dash, dgm-history, dgm-log |
| `admin` | adm-audit, adm-locations, adm-users, adm-config, adm-import, adm-reports, adm-reasonableness |
| `regional-controller` | rc-biz-dash, rc-trends (plus adm-audit, adm-reports, operator/controller access) |

DGM/Regional-Controller can receive additional operator/controller access via `access_grants` (managed by `src/utils/operatorAccess.ts`).

## Backend Architecture

```
backend/app/
├── main.py              # FastAPI app + CORS + APScheduler lifespan
├── api/v1/router.py     # Mounts all route modules under /v1
├── api/v1/              # auth, submissions, verifications, locations,
│                        # users, config, compliance, reports, audit, admin,
│                        # business_dashboard, reasonableness
├── core/                # config.py (Pydantic Settings), security.py (JWT/bcrypt), deps.py
├── db/                  # session.py (engine + SessionLocal), base.py
├── models/              # SQLAlchemy ORM: user, location, submission, verification,
│                        # config, audit, access_grant, reasonableness
├── schemas/             # Pydantic request/response schemas (mirror models/)
├── services/            # email.py (fastapi-mail + Jinja2), scheduler.py (APScheduler), audit.py
└── templates/email/     # HTML email templates
```

**Database**: SQLite (`cashroom.db`) in dev; PostgreSQL in prod (set `DATABASE_URL` in `.env`).
**Migrations**: Alembic — migration files in `alembic/versions/`.
**Background jobs**: APScheduler (daily 08:00 UTC submission reminders).
**Auth**: JWT access token (1 hr) + refresh token (7 days). Role enforcement via `require_roles()` in `core/deps.py`.

**Roles enum** (in `models/user.py`): OPERATOR, CONTROLLER, DGM, ADMIN, AUDITOR, REGIONAL_CONTROLLER.

**Key model fields for Phase 2**:
- `locations.cost_center` (String(50)) — financial identifier, used for grouping
- `locations.group` (String(50)) — location grouping for reasonableness
- `locations.expected_cash` — imprest amount
- `submissions.sections` (JSON) — contains section A through I denomination data
- `submissions.total_cash`, `submissions.variance`, `submissions.variance_pct`

## Key Business Rules

| Rule | Detail |
|------|--------|
| Imprest Balance | Fixed cash fund per location; submissions track deviation |
| Variance Tolerance | >5% variance from imprest requires written explanation |
| Approval SLA | Manager must approve/reject within 48 hours |
| Controller DOW Rule | Warn if controller visits same location on same weekday two weeks running |
| DGM Monthly Rule | Block second DGM visit to same location in a calendar month |
| One Submission Per Day | Location cannot have two submissions for the same date |
| Fiscal Year | Oct 1 – Sep 30. Periods P1 (Oct) through P12 (Sep). Quarters Q1–Q4 |
| Reasonableness Factor | 1.25 (single location) or 1.50 (multiple locations in same cost center) |
| Reasonableness Cushion | Default -$5,000 permitted by audit (editable by controller) |
| Reasonableness Status | Net > 0 → Overfunded, Net ≤ 0 → Reasonable |

## Environment Variables

Copy `backend/.env.example` → `backend/.env`. Key vars:
- `DATABASE_URL` — `sqlite:///./cashroom.db` (dev) or PostgreSQL connection string
- `SECRET_KEY` — JWT signing key
- `SMTP_HOST`, `SMTP_PORT` — email (default: localhost:1025 for mailcatcher)
- `EMAIL_ENABLED` — toggle email sending

## Codebase Documentation

| Folder | Contents |
|---|---|
| `architecture/` | ARCHITECTURE.md, API_DOC.md, DB_DESIGN.md |
| `decisions/` | Technical decisions with rationale |
| `gap-analysis/` | Prototype vs codebase fit, screen modification maps |
| `implementation-plans/` | TDD plans with test cases and file paths |
| `developer-guide/` | DEVELOPER_HANDOVER.md, TEST_CASES.md, E2E test docs, DockerSetup.md |

## Testing

**Backend** (pytest):
```bash
cd backend
pytest                                          # Full suite
pytest tests/test_reasonableness.py -v          # Reasonableness tests only (54 tests)
pytest tests/test_submissions.py -k "test_name" # Single test
```

**Frontend** (Playwright E2E):
```bash
cd frontend
npx playwright test                              # All E2E specs
npx playwright test e2e/rc-bizdash.spec.ts       # Single spec
```

No frontend unit test runner configured.

## For Project Management Context

See `../control-room/CLAUDE.md` for stakeholders, planning, and progress tracking.
