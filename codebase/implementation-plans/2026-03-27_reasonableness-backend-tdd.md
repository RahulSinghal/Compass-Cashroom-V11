# Reasonableness Backend — TDD Implementation Plan

**Date**: 2026-03-27
**Branch**: `phase2-features`

---

## Phase 1: Model + Migration (Red -> Green)

### Tests (write first): `backend/tests/test_reasonableness.py`

| ID | Test | Validates |
|----|------|-----------|
| TC-1.1 | `test_create_reasonableness_report` | Model round-trips in DB |
| TC-1.2 | `test_report_status_enum` | Only Reasonable/Overfunded allowed |
| TC-1.3 | `test_location_reports_json_roundtrip` | JSON column stores RtLocReport[] |
| TC-1.4 | `test_location_group_column` | Location.group is queryable |

### Implementation

**CREATE** `backend/app/models/reasonableness.py`:
- `ReasonablenessStatus(str, enum.Enum)` — REASONABLE, OVERFUNDED
- `ReasonablenessReport(Base)` — id (UUID36), group_key, cost_center, location_labels, from_date (Date), to_date (Date), factor (Float), preparer, scope (nullable Text), status (Enum), location_reports (JSON), saved_by (FK users.id), created_at, updated_at

**MODIFY** `backend/app/models/location.py`:
- Add `group: Mapped[str | None] = mapped_column(String(50), nullable=True)`

**MODIFY** `backend/tests/conftest.py`:
- Add cost_center values to seed locations
- Add `seed_rt_submissions` fixture with ~10 approved submissions containing section F/H/J data

**GENERATE** Alembic migration

---

## Phase 2: Schemas (Red -> Green)

### Tests

| ID | Test | Validates |
|----|------|-----------|
| TC-2.1 | `test_generate_request_schema_valid` | Accepts valid input |
| TC-2.2 | `test_generate_request_schema_invalid` | Rejects missing fields |
| TC-2.3 | `test_save_report_body_valid` | Accepts well-formed report |
| TC-2.4 | `test_report_out_from_attributes` | ORM -> Pydantic works |
| TC-2.5 | `test_paginated_reports_schema` | Pagination structure correct |

### Implementation

**CREATE** `backend/app/schemas/reasonableness.py`:
- GenerateRequest, GenerateResponse, RtMaxValuesOut
- SaveReportBody, RtLocReportSchema
- ReportOut (from_attributes=True), PaginatedReports
- LocationGroupOut

---

## Phase 3: Business Logic (Red -> Green)

### Tests (unit-level, no HTTP)

| ID | Test | Validates |
|----|------|-----------|
| TC-3.1 | `test_total_from_max_sections` | Total = max(F) + max(H) + max(J) + max(K) |
| TC-3.2 | `test_actual_from_max_total_cash` | Actual = max(total_cash) |
| TC-3.3 | `test_net_calculation` | net = (actual - expected) + cushion |
| TC-3.4 | `test_status_overfunded_when_net_positive` | net > 0 -> Overfunded |
| TC-3.5 | `test_status_reasonable_when_net_zero_or_negative` | net <= 0 -> Reasonable |
| TC-3.6 | `test_default_cushion` | Default cushion = -$5,000 |

---

## Phase 4: API Endpoints (Red -> Green)

### Tests

**GET /v1/reasonableness/location-groups**
| TC-4.1 | Controller gets grouped locations | 200 |
| TC-4.2 | Operator forbidden | 403 |

**POST /v1/reasonableness/generate**
| TC-4.3 | Returns correct max values from submissions | 200 |
| TC-4.4 | No submissions -> zeroed results | 200 |
| TC-4.5 | from_date > to_date -> 422 | 422 |
| TC-4.6 | Operator forbidden | 403 |

**POST /v1/reasonableness/reports**
| TC-4.7 | Controller saves report | 201 |
| TC-4.8 | Saved report appears in list | 200 |
| TC-4.9 | Operator forbidden | 403 |
| TC-4.10 | Audit event logged | DB check |

**GET /v1/reasonableness/reports**
| TC-4.11 | Paginated results | 200 |
| TC-4.12 | Filter by status | 200 |
| TC-4.13 | Admin can list | 200 |

**GET /v1/reasonableness/reports/{id}**
| TC-4.14 | Get by ID | 200 |
| TC-4.15 | Unknown ID -> 404 | 404 |

### Implementation

**CREATE** `backend/app/api/v1/reasonableness.py`:
- Router with prefix="/reasonableness", tags=["Reasonableness"]
- Generate: query approved submissions, extract max from sections JSON in Python (SQLite compatible)
- Section keys: `sections["F"]["total"]`, `sections["H"]["total"]`, `sections["J"]["total"]`
- K defaults to 0; actual_fund = max(submission.total_cash)
- Roles: Controller for generate/save; Controller+Admin+RC for list/view

**MODIFY** `backend/app/api/v1/router.py`:
- Add `router.include_router(reasonableness.router)`

---

## Phase 5: Frontend Integration

**CREATE** `frontend/src/api/reasonableness.ts`
**MODIFY** `frontend/src/pages/controller/CtrlReasonableness.tsx` — swap mock -> API
**MODIFY** `frontend/src/pages/admin/AdmReasonableness.tsx` — swap mock -> API
**MODIFY** `frontend/src/api/types.ts` — add reasonableness types

Keep mock fallback for demo accounts (existing pattern).

---

## Phase 6: Verification

1. `pytest backend/tests/test_reasonableness.py -v` — all 20+ tests pass
2. `pytest backend/tests/ -v` — zero regressions
3. `npm run build` — no TypeScript errors
4. Manual: Controller generate + save, Admin list + filter + detail, Operator 403

---

## File Summary

| Action | File |
|--------|------|
| CREATE | `backend/tests/test_reasonableness.py` |
| CREATE | `backend/app/models/reasonableness.py` |
| CREATE | `backend/app/schemas/reasonableness.py` |
| CREATE | `backend/app/api/v1/reasonableness.py` |
| CREATE | `frontend/src/api/reasonableness.ts` |
| CREATE | Alembic migration |
| MODIFY | `backend/app/models/location.py` |
| MODIFY | `backend/app/api/v1/router.py` |
| MODIFY | `backend/tests/conftest.py` |
| MODIFY | `frontend/src/pages/controller/CtrlReasonableness.tsx` |
| MODIFY | `frontend/src/pages/admin/AdmReasonableness.tsx` |
| MODIFY | `frontend/src/api/types.ts` |
