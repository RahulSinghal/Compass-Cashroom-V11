# Phase 2 — Backend Implementation Plan

**Date**: 2026-03-27
**Feature**: Cash Reasonableness Test — Backend Layer
**Approach**: Test-Driven Development (TDD)

---

## Current Status

Frontend screens are **100% complete** with mock data:
- Controller wizard (CtrlReasonableness) — fully functional
- Admin dashboard (AdmReasonableness) — fully functional
- All calculations, validations, and HTML report generation working

**What's missing**: Backend API endpoints + database storage. Currently using in-memory mock data.

## What We're Building

| Component | Purpose |
|---|---|
| Database table | Store reasonableness reports permanently |
| 5 API endpoints | Generate calculations, save/list/view reports, get location groups |
| Frontend wiring | Swap mock data for real API calls |

## Implementation Phases

### Phase 1: Database Model + Tests
- Create `reasonableness_reports` table
- Add `group` column to existing locations table
- Write tests first, then implement (TDD)
- **Risk to existing system: None** — new table only

### Phase 2: API Schemas + Validation
- Define request/response data structures
- Validate all inputs (dates, required fields, role permissions)

### Phase 3: Business Logic + Tests
- Calculation engine: pull max values from existing submission data
- Status determination: Reasonable vs Overfunded
- 6 unit tests covering all calculation rules

### Phase 4: API Endpoints + Tests
- 5 endpoints with role-based access control
- 15 integration tests covering happy paths, permissions, edge cases
- Audit logging on report save

### Phase 5: Frontend Integration
- Create API client functions
- Update Controller screen to call real API
- Update Admin screen to call real API
- Keep mock fallback for demo accounts

### Phase 6: End-to-End Verification
- Run all backend tests (20+ tests)
- Run full existing test suite (no regressions)
- Manual testing across Controller, Admin, Operator roles

## Timeline Estimate

| Phase | Effort |
|---|---|
| Phases 1-4 (Backend) | Core development |
| Phase 5 (Frontend wiring) | Integration |
| Phase 6 (Verification) | Testing |

## Risk Assessment

| Risk | Mitigation |
|---|---|
| Existing features break | TDD + full regression suite run after each phase |
| Data format mismatch | Frontend mock data structure matches planned API response |
| Demo mode stops working | Mock data fallback preserved for demo accounts |

## Success Criteria

1. All 20+ backend tests pass
2. Existing test suite has zero regressions
3. Controller can generate, review, and save a report via real API
4. Admin can list, filter, and view report details via real API
5. Operators get 403 on all reasonableness endpoints
6. Demo accounts still work with mock data
