# Phase 2 — Screen Modification Map

**Date**: 2026-03-25
**Purpose**: Identifies every frontend screen that needs creation or modification for the Cash Reasonableness Test module.

---

## New Screens (3 files to create)

| # | Screen | File | Role | Description |
|---|---|---|---|---|
| 1 | Cash Reasonableness Test | `frontend/src/pages/controller/CtrlReasonableness.tsx` | Controller | Full wizard: select location/date range/factor → view calculation table → enter conclusions per sub-location → mark complete → download HTML report |
| 2 | Reasonableness Reports Dashboard | `frontend/src/pages/admin/AdmReasonableness.tsx` | Admin | KPIs (total/reasonable/overfunded), reports table with filters, detail modal per report, re-download button |
| 3 | Reasonableness API Client | `frontend/src/api/reasonableness.ts` | — | API functions: generateReport(), saveReport(), listReports(), getReportDetail(), downloadReport() |

---

## Existing Screens to Modify (4 files)

### 1. `frontend/src/App.tsx` — Navigation + Panel Routing

- **Import** new CtrlReasonableness and AdmReasonableness components
- **Controller nav** (line 59-63): Add nav item `{ id: 'reasonableness', icon: '🧮', label: 'Cash Reasonableness Test', panel: 'ctrl-reasonableness' }`
- **Admin nav** (line 68-73): Add nav item `{ id: 'reasonableness', icon: '🧮', label: 'Reasonableness Reports', panel: 'adm-reasonableness' }`
- **renderPanel()** (line 248+): Add two new cases:
  - `case 'ctrl-reasonableness'` → CtrlReasonableness
  - `case 'adm-reasonableness'` → AdmReasonableness

### 2. `frontend/src/pages/admin/AdmLocations.tsx` — Location Management

- Currently shows `cost_center` as read-only display (line 280)
- **Add**: Editable `group` field (or derive grouping from shared cost_center)
- **Add**: Display sub-locations that share the same cost center
- **Add**: Default factor indicator (1.25 for single location, 1.50 for grouped)
- **Add**: group field to create/edit location form so admin can link locations (e.g. Appleton+Wausau under unit 5082)

### 3. `frontend/src/api/types.ts` — TypeScript Interfaces

Add to ApiLocation:
- `group?: string` field

Add new interfaces:
- `ReasonablenessCalculation` — per sub-location: maxF, maxH, maxJ, maxK, total, factor, expectedFund, actualFund, overUnder, cushion, netResult, status, conclusion, requiredActions, actionDetails
- `ReasonablenessReport` — id, group, costCenter, locLabels, fromDate, toDate, factor, preparer, scope, locReports[], status, savedAt, savedBy
- `SectionAEntry` — date, sA value

### 4. `frontend/src/mock/data.ts` — Mock Data

- Add `group` and `subLocs` fields to mock location data
- Add mock reasonableness report data for demo mode fallback
- Add fiscal period helper utility (or create new `utils/fiscal.ts`)

---

## Screens With No Changes

| Screen | File | Why No Change |
|---|---|---|
| OpStart, OpMethod, OpForm, OpChat, OpExcel, OpReadonly, OpDrafts, OpMissed | `pages/operator/*` | Operators don't interact with reasonableness test. Their daily submissions are read-only source data. |
| MgrApprovals, MgrHistory | `pages/manager/*` | Managers are not involved in the quarterly test. |
| CtrlDashboard, CtrlLog, CtrlHistory, CtrlDgmReview | `pages/controller/*` | Weekly verification is separate from quarterly reasonableness. |
| DGMDash, DGMLog, DGMHistory | `pages/dgm/*` | DGM visibility mentioned in doc but no dedicated screen required for Phase 2. |
| RcTrends | `pages/regional-controller/*` | Could optionally show reasonableness status but doc doesn't require it. |
| AdmUsers, AdmConfig, AdmAudit, AdmReports, AdmImport, AdmCompliance | `pages/admin/*` | No interaction with reasonableness module. |

---

## Backend Files (for reference)

| File | Change |
|---|---|
| `backend/app/models/location.py` | Add `group` column |
| `backend/app/models/reasonableness.py` | **New** — ReasonablenessReport model |
| `backend/app/schemas/reasonableness.py` | **New** — Pydantic schemas |
| `backend/app/api/v1/reasonableness.py` | **New** — API routes (generate, save, list, detail) |
| `backend/app/api/v1/router.py` | Mount `/reasonableness` routes |
| New Alembic migration | Create reasonableness_reports table + add group field to locations |

---

## Summary

| Category | Count |
|---|---|
| New screens | 2 (CtrlReasonableness + AdmReasonableness) |
| Modified screens | 2 (App.tsx routing + AdmLocations grouping) |
| Support files | 2 (api/reasonableness.ts + types.ts additions) |
| Untouched screens | 15 |
| New backend files | 3 (model + schema + routes) |
| Modified backend files | 2 (router.py + location model) |
