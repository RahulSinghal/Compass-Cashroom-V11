# Phase 2 Fit Analysis: Where It Plugs Into Existing Codebase

**Date**: 2026-03-25
**Repo**: Compass-Cashroom-V11 (fork, branch `phase2-features`)

---

## What Already Exists (Reusable)

| Phase 2 Need | Exists? | Where |
|---|---|---|
| Locations with cost_center | Yes | `backend/app/models/location.py` — `cost_center` field (String(50)) |
| Daily form data (sA, sF, sH, sJ) | Yes | `backend/app/models/submission.py` — `sections` JSON column |
| Imprest balance per location | Yes | `locations.expected_cash` field |
| Controller role + nav | Yes | `frontend/src/pages/controller/` |
| Admin role + nav | Yes | `frontend/src/pages/admin/` |
| Auth + role-based guards | Yes | `backend/app/core/deps.py` — `require_roles()` |
| Audit logging | Yes | `backend/app/services/audit.py` — `log_event()` |

## What's Missing (Must Build)

### Location Grouping
- Locations are currently flat — no `group` or `sub_locations` concept
- Need: add `group` field to Location model so Appleton+Wausau can be queried together
- Alternative: derive grouping from shared `cost_center` value (5082)

### Backend — New Files
| File | Purpose |
|---|---|
| `backend/app/models/reasonableness.py` | `ReasonablenessReport` table |
| `backend/app/schemas/reasonableness.py` | Pydantic request/response schemas |
| `backend/app/api/v1/reasonableness.py` | API endpoints (generate, save, list, detail) |
| New Alembic migration | Create table + location group field |

### Backend — Files to Modify
| File | Change |
|---|---|
| `backend/app/api/v1/router.py` | Mount `/reasonableness` routes |
| `backend/app/models/location.py` | Add `group` field |
| `backend/app/models/__init__.py` | Import new model |

### Frontend — New Files
| File | Purpose |
|---|---|
| `frontend/src/pages/controller/CtrlReasonableness.tsx` | Full wizard UI |
| `frontend/src/pages/admin/AdmReasonableness.tsx` | Reports dashboard |
| `frontend/src/api/reasonableness.ts` | API client |

### Frontend — Files to Modify
| File | Change |
|---|---|
| `frontend/src/App.tsx` | Add nav items for Controller + Admin |
| `frontend/src/api/types.ts` | Add TypeScript interfaces |
| `frontend/src/pages/admin/AdmLocations.tsx` | Expose group editing |

## Data Flow

```
Existing: submissions.sections (JSON with sA, sF, sH, sJ per daily form)
    ↓
New API: POST /v1/reasonableness/generate
    body: { location_group, from_date, to_date, factor }
    ↓
Query: SELECT MAX(sections->sF), MAX(sections->sH), MAX(sections->sJ),
       MAX(total_cash) FROM submissions
       WHERE location_id IN (group locations) AND date BETWEEN from/to
    ↓
Return: { maxF, maxH, maxJ, maxK, total, actualFund, sectionAData[] }
    ↓
Frontend: calculates Expected, Over/Under, Net Result
    ↓
Save: POST /v1/reasonableness/save → stores report in new table
```

## Impact Assessment

- **Existing tables**: No schema changes to `submissions` or `users`
- **Location table**: 1 new column (`group`)
- **New table**: 1 (`reasonableness_reports`)
- **Existing API routes**: Untouched
- **Risk**: Low — self-contained module that reads existing data
