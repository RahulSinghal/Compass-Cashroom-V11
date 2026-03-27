# Gap Analysis — Engagement Summary

**Date**: 2026-03-25
**Purpose**: High-level coverage and risk summary for stakeholder communication

---

## Overall Coverage: ~95%

The HTML prototype implements nearly all requirements from the Process Document (v2.0). The remaining gaps are minor and manageable within the Phase 2 timeline.

## What's Fully Covered

- Complete calculation engine matching the Excel template B.1.4
- Controller wizard: location selection, date range, factor, conclusions
- Admin dashboard: KPIs, report listing, filtering, detail view
- HTML report generation matching audit template format
- All field validations per Section 9 of the process document
- Fiscal year logic (Oct-Sep, P1-P12, Q1-Q4)
- Location grouping by cost center (e.g., Appleton+Wausau under 5082)

## Open Gaps Requiring Client Input

| # | Gap | Impact | Owner | Status |
|---|---|---|---|---|
| 1 | Cost center mapping incomplete | Cannot configure all locations | Jamie Spoor | **Pending — ASAP** |
| 2 | DGM/Regional visibility into reports | Role may lack access to compliance data | Shivani Gupta | Open — confirm if needed for Phase 2 |
| 3 | Quarterly email reminder trigger logic | Controllers won't get automated reminders | Shivani / Jamie | Open — when in quarter? who triggers? |

## Low-Risk Gaps (Dev Team Handles)

| # | Gap | Effort | Notes |
|---|---|---|---|
| 4 | Admin re-download button | Trivial | ~30 min fix |
| 5 | From < To date validation | Trivial | Missing input validation |

## Codebase Fit Assessment

- **Risk: Low** — Phase 2 is a self-contained module that reads existing submission data
- **No changes** to existing submissions, users, or approval workflows
- **1 new database table** (reasonableness_reports)
- **1 minor change** to existing Location table (add group column)
- **All existing API routes untouched**

## Key Decision for Client

The system is designed so controllers must **actively participate** (select parameters, review data, enter conclusions, confirm each location). This is intentional per the process document — the test is NOT fully automated.
