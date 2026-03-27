# Gap Analysis: HTML Prototype vs Process Document

**Date**: 2026-03-25
**Prototype**: `CashRoom_Production 1.html` (v5.0)
**Document**: `CashReasonableness_Process_Document.docx` (v2.0)

---

## Coverage: ~95% Complete

The HTML prototype implements nearly everything in the process document.

## Fully Implemented

- Fiscal year/period logic (Oct=P1, Q1-Q4 mapping)
- Location grouping by cost center (Appleton+Wausau under 5082)
- Factor multiplier dropdown (1.25/1.50) with auto-suggestion
- Full calculation chain: max(F,H,J,K) → Total → Expected → Over/Under → Cushion → Net Result
- Editable cushion (default -$5,000)
- Conclusion notes per sub-location (min 5 chars validation)
- Required Actions Yes/No with conditional action details
- Mark Complete per location with validation
- Section A daily data grouped by fiscal period, peak highlighted green, average row yellow
- Excel-style B.1.4 report HTML generation and download
- Admin Reasonableness Reports dashboard with KPIs, table, detail modal
- All field validations per Section 9 of document
- Line K defaults to $0 (per spec)
- Net Result color-coded (green/red), no warning symbols (per spec)
- File naming convention matches spec

## Gaps Found

| # | Gap | Doc Reference | Severity | Notes |
|---|---|---|---|---|
| 1 | Admin detail modal missing "Re-download Excel Report" button | Section 8.2 | Minor | Trivial to add |
| 2 | DGM/Regional Leader have no view into reasonableness reports | Section 4 (Roles) | Minor | Only Controller + Admin have access currently |
| 3 | No From < To date validation | Section 9.1 | Minor | From date can exceed To date without error |
| 4 | Quarterly email reminder to controllers when test is due | Section 1.1 | Medium | Backend scheduler feature — not prototype scope |
| 5 | Cost center mapping incomplete | Section 3.1 / Item #1 | Pending | Awaiting Jamie Spoor's complete list |

## Not Gaps (Correctly Handled)

- Line K = $0 → per doc: "Defaults to $0 if not captured separately"
- Actual Fund is read-only → correct per spec
- Net Result shows dollar value only, no warning symbols → per doc
- Section A = loose currency only, no other sections → per Jamie's confirmation
