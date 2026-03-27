# Phase 2 — Cash Reasonableness Test: Requirements Summary

**Source**: `CashReasonableness_Process_Document.docx` (v2.0, March 2026)
**Prepared By**: Pankhuri Gupta | **Reviewed By**: Shivani Gupta, Jamie Spoor

---

## What It Is

A quarterly compliance control per cash room location. Answers: does the cash room hold an appropriate amount of fund relative to its actual operational usage?

## Key Business Rules

- **Frequency**: Once per quarter, no fixed date — controller chooses when
- **Not automated end-to-end by design** — controller must actively participate (select params, review, add notes, confirm)
- **Fiscal Year**: Oct 1 – Sep 30. Periods P1 (Oct) through P12 (Sep). Quarters Q1–Q4.
- **Factor**: 1.25 (single cash room) or 1.50 (multiple cash rooms in same unit)
- **Cushion**: $5,000 permitted by audit (editable, default -$5,000)

## Calculation Chain

1. Pull max(Line F), max(Line H), max(Line J), max(Line K) from cashroom form submissions in date range
2. Total = F + H + J + K
3. Expected Fund = Total × Factor
4. Actual Fund = max(Cashier's Fund Balance) from submissions in date range (read-only)
5. Over/(Under) = Actual − Expected
6. Net Result = Over/(Under) + Cushion
7. If Net Result > 0 → Overfunded (action may be required)

## Workflow (11 Steps)

1. Controller opens Cash Reasonableness Test tab
2. Select location (grouped by cost center) → auto-fills cost center + sub-locations
3. Select date range (From/To, capped at today)
4. Select/confirm factor multiplier (pre-suggested)
5. Enter scope description (optional)
6. Click Generate → system pulls all data and calculates
7. Review calculation table (yellow = auto-calculated, read-only)
8. Review Section A daily data (loose currency, grouped by fiscal period)
9. Enter conclusion notes per sub-location (mandatory, min 5 chars)
10. Mark each location complete (validates conclusion + required actions)
11. Generate & Download HTML report + save to Admin dashboard

## Report Output

- Format: `.html` (openable in Excel, printable to PDF)
- Naming: `CashReasonableness_LOCATION_FROM_to_TO.html`
- Replicates Excel template B.1.4 layout

## Active Locations

| Location | Cost Center | Group | Factor |
|---|---|---|---|
| APPLETON | 5082 | APPLETON/WAUSAU | 1.50 |
| WAUSAU | 5082 | APPLETON/WAUSAU | 1.50 |
| CENTRAL IL | 5104 | Single | 1.25 |
| BLOOMINGDALE | 5117 | Single | 1.25 |
| ROMEOVILLE | 5132 | Single | 1.25 |

*Note: Jamie Spoor to provide complete cost center mapping.*

## Roles

| Role | Responsibility |
|---|---|
| Branch Controller | Runs the test, enters conclusions, generates report |
| Admin/RC | Views all reports on Admin dashboard, monitors compliance |
| DGM/Regional | Visibility into whether quarterly tests are completed |
| Operator | No direct involvement — daily submissions provide source data |

## Out of Scope (Phase 2)

- Form 404 Monthly Reconciliation → Phase 3
- Alarm testing form → Phase 4
