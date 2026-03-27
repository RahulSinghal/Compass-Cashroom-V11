# Control Room — CLAUDE.md

Context for engagement strategist and project management tasks.

## Project Context

- **Client**: Canteen Vending Services (Compass Group)
- **Stakeholders**: Jamie Spoor (Admin/RC), Shivani Gupta (Reviewer), Alara (Admin)
- **Delivery Lead**: Pankhuri Gupta
- **Phase**: Phase 2 — Cash Reasonableness Test
- **Branch**: `feature/reasonableness-backend`
- **Repo**: `RahulSinghal/Compass-Cashroom-V11` (fork)

## What is CCS?

A system to digitise daily cash reconciliation across Compass Group locations. Operators submit daily cash counts, controllers review/approve, DGMs do physical verification visits, admins oversee. Phase 2 adds a quarterly Cash Reasonableness Test to verify cash rooms hold appropriate funds.

## Folder Structure

| Folder | What goes here |
|---|---|
| `requirements/` | Business requirements, process docs, client-provided specs |
| `planning/` | Phase plans, build approach, milestones (business-readable) |
| `progress/` | Daily status updates — **check here first for latest state** |
| `gap-analysis/` | Coverage summaries and risk assessments for stakeholders |
| `open-items/` | Blockers, pending questions, action items with owners/due dates |
| `meeting-notes/` | Client call and internal sync notes |
| `client-comms/` | Key client messages, approvals, clarifications |
| `change-log/` | Scope changes, requirement amendments |
| `sign-offs/` | Client approvals on milestones, UAT sign-offs |

## File Naming

`YYYY-MM-DD_short-description.md` — e.g., `2026-03-25_phase2-kickoff-notes.md`

## How to Update Progress

1. Create a new file in `progress/` with today's date
2. Use the template in `progress/TEMPLATE.md`
3. Include: Summary, Completed, In Progress, Blockers, Decisions Made, Next Steps
4. Convert relative dates to absolute (e.g., "Thursday" → "2026-03-05")

## Current Open Items

See `open-items/2026-03-25_open-items.md` for pending questions and blockers.

Key pending item: **Cost center mapping from Jamie Spoor** — needed to configure all production locations.

## Key Decisions Made

| Decision | Where | Rationale |
|---|---|---|
| Frontend-first build | `planning/2026-03-25_phase2-build-approach.md` | Fastest to demo, matches existing patterns |
| TDD for backend | `planning/2026-03-27_phase2-reasonableness-backend-plan.md` | Ensures existing features not disturbed |
| Fork + feature branch | `../codebase/decisions/2026-03-25_repo-strategy.md` | Keeps original repos untouched |

## For Technical Details

See `../codebase/CLAUDE.md` for architecture, code patterns, and implementation specifics.
