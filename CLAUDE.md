# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CashRoom Compliance System (CCS)** — a full-stack web app for Canteen Vending Services (Compass Group) to digitise daily cash reconciliation. Operators submit cash counts, managers approve them, controllers/DGMs schedule physical verification visits, and admins oversee the whole system.

**Phase 2** (in progress on `feature/reasonableness-backend` branch) adds a **Cash Reasonableness Test** module — a quarterly compliance control that checks whether each cash room holds appropriate funds relative to operational usage.

## Tech Stack

```
frontend/  (React 19 + TypeScript + Vite)   → port 3000
backend/   (FastAPI + Python 3.13)          → port 8000
```

## Commands

### Frontend (`cd frontend`)
```bash
npm run dev       # Vite dev server on port 3000
npm run build     # tsc -b (strict type-check) + vite build
npm run lint      # ESLint
```

### Backend (`cd backend`)
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload   # Dev server on port 8000
pytest                                    # Run tests
alembic upgrade head                      # Apply DB migrations
```

### Docker
```bash
docker compose up --build                     # Dev with SQLite
docker compose --profile prod up --build      # Prod with PostgreSQL
```

## Project Structure

```
├── CLAUDE.md                  ← You are here (generic overview)
├── frontend/                  ← React app
├── backend/                   ← FastAPI app
├── control-room/              ← Engagement strategist hub
│   └── CLAUDE.md              ← Engagement context (stakeholders, planning, progress)
├── codebase/                  ← AI engineer / architect hub
│   └── CLAUDE.md              ← Technical context (architecture, patterns, conventions)
├── docker-compose.yml
└── README.md
```

## Context Routing

Depending on the task, read the appropriate CLAUDE.md for deeper context:

| Working on... | Read |
|---|---|
| Code, bugs, features, architecture | `codebase/CLAUDE.md` |
| Project planning, client comms, progress updates | `control-room/CLAUDE.md` |
| Both (e.g., writing progress updates about code work) | Both |

## Key Rules

- **TypeScript strict mode** — unused imports break `npm run build`
- **No React Router** — navigation is state-based via `renderPanel()` in `App.tsx`
- **Fiscal Year** — Oct 1 – Sep 30. P1=Oct through P12=Sep. Q1–Q4.
- **Roles**: OPERATOR, CONTROLLER, DGM, ADMIN, AUDITOR, REGIONAL_CONTROLLER
- **Auth**: JWT access token (1 hr) + refresh token (7 days)
- **Demo accounts**: password `demo1234`, falls back to mock data in `src/mock/data.ts`
