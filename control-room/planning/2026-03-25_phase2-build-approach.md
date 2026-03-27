# Decision: Phase 2 Build Approach — Frontend-First with Mock Data

**Date**: 2026-03-25
**Decision**: Build frontend screens first using mock data, then wire backend later

---

## Context

Phase 2 requires 2 new screens (CtrlReasonableness + AdmReasonableness) and modifications to 2 existing screens (App.tsx + AdmLocations). An HTML prototype already exists with all UI logic and calculations.

## Decision

Frontend-first, mock data, 4-step incremental build.

## Rationale

- HTML prototype already has complete UI logic — this is a port job, not design from scratch
- Existing app already uses mock data fallback pattern (demo login with `src/mock/data.ts`)
- Zero backend dependency means screens can be demoed to client immediately
- Backend wiring becomes a simple swap later (mock → API calls)
- Matches how all other screens in the codebase were built

## Build Sequence

### Step 1 — Wire skeleton into App.tsx
- Add nav items for Controller ("Cash Reasonableness Test") and Admin ("Reasonableness Reports")
- Add panel routing cases in renderPanel()
- Create bare component shells
- **Result**: Nav items visible, tabs clickable

### Step 2 — Build CtrlReasonableness (Controller screen)
- Port calculation logic from HTML prototype (rtGetMaxValues, getFiscalPeriod, groupByFiscalPeriod)
- Mock data: locations with groups + fake submissions with sA/sF/sH/sJ values
- Build full wizard: parameter selection → calculation table → conclusions per sub-location → mark complete → download HTML report
- All self-contained with mock data, no backend needed

### Step 3 — Build AdmReasonableness (Admin screen)
- Mock saved reports array (like RTEST_STORE in prototype)
- KPI cards (total/reasonable/overfunded)
- Reports table with status badges
- Detail modal per report with all calculations and conclusions
- Re-download button

### Step 4 — Extend AdmLocations
- Add group field to location create/edit form
- Display sub-locations sharing the same cost center
- Show default factor indicator (1.25 single / 1.50 grouped)

### Later — Backend Wiring
- Build API endpoints + DB model
- Swap mock data calls for real API calls in each screen
- Same pattern used for all existing screens in the codebase

## Alternatives Considered

1. **Full-stack per screen** — slower feedback loop, can't demo until backend is ready
2. **Backend-first** — no visual progress to show client
3. **Frontend-first with mock data** (chosen) — fastest to demo, matches existing patterns
