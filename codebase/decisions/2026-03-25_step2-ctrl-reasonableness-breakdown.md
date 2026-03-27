# Step 2 Breakdown — Build CtrlReasonableness.tsx

**Date**: 2026-03-25
**Screen**: `frontend/src/pages/controller/CtrlReasonableness.tsx`
**Purpose**: Full Controller wizard for the Cash Reasonableness Test

---

## Step 2a — Parameter Selection (Step 1 card)

- Location dropdown grouped by cost center (e.g. "APPLETON (Unit 5082 — incl. sub-locations)")
- Auto-fill cost center + sub-locations when location is selected
- Date range pickers (From / To, capped at today)
- Factor multiplier dropdown (1.25 single / 1.50 multiple), pre-suggested based on sub-location count
- Prepared By field (defaults to logged-in controller name)
- Scope description text input (optional, e.g. "Daily Cashroom Reconciliations for P4 and P5, FY2026")
- "Generate Reasonableness Report" button with validation (location, dates, factor all required)

**Mock data needed**: Location config with group, costCenter, subLocs fields

---

## Step 2b — Calculation Table + Section A (Step 2 card)

### Calculation Table
- Excel-style table with parallel columns per sub-location (e.g. APPLETON | WAUSAU)
- Row: Uncounted Funds (Line F) — max value from mock submissions in date range
- Row: Outstanding Changers (Line H) — max value
- Row: Replenishment (Line J) — max value
- Row: Coin Purchase in Transit (Line K) — defaults to $0
- Row: Total = F + H + J + K (yellow background)
- Row: Factor (display selected value)
- Row: Expected Fund Amount = Total × Factor (yellow background)
- Row: Actual Fund Amount = max(total_cash) from submissions (read-only, grey background)
- Row: Over/(Under) Funded = Actual − Expected (green if negative, red if positive)
- Row: Less Cushion Permitted = -$5,000 (editable input, triggers recalculation)
- Row: Net Result = Over/Under + Cushion (green if <= 0, red if > 0)
- Comments column on the right

### Section A — Daily Data (Compare Periods)
- Table at bottom: "Loose currency in the room after deposit has been prepared"
- Columns: per location × per fiscal period (e.g. APPLETON P4 | APPLETON P5 | WAUSAU P4 | WAUSAU P5)
- Rows: one per calendar date in selected range (only dates with submission data)
- Peak balance per location highlighted in green
- Average row at bottom with yellow background
- Section A values only (sA from submissions)

**Mock data needed**: Fake submissions with sA, sF, sH, sJ, total values across 30+ days

**Utility functions needed**:
- `getFiscalPeriod(dateStr)` — returns { p: 'P4', q: 'Q2', fy: 2026, label: 'P4 / Q2 FY2026' }
- `getMaxValues(locId, fromDate, toDate)` — returns { maxF, maxH, maxJ, maxK, total, actualFund, sectionAData[] }
- `groupByFiscalPeriod(sectionAData)` — groups daily sA values by fiscal period

---

## Step 2c — Conclusions + Download (Step 3 card)

### Conclusion Per Sub-Location
- Card per sub-location (e.g. "Conclusion — APPLETON", "Conclusion — WAUSAU")
- Badge showing "Overfunded" (red) or "Reasonable" (green) based on Net Result
- Conclusion Notes textarea (mandatory, min 5 characters)
- Required Actions dropdown: Yes / No (mandatory)
- If Yes: Action Details textarea appears (mandatory, min 5 characters)
- "Confirm & Mark Complete" button per location
  - Validates all fields filled
  - Dims the card and shows green "Completed" badge
  - Each location must be independently confirmed

### Action Buttons
- "Generate & Download Report" button
  - Builds HTML file replicating Excel template B.1.4 layout
  - Header block: location, cost center, test performed, prepared by, date, scope, period
  - Calculation table with yellow/green/red styling
  - Conclusion notes and required actions per location
  - Section A daily data table
  - Triggers browser download as `CashReasonableness_LOCATION_FROM_to_TO.html`
- "Save to Admin Dashboard" button
  - Stores report in mock array (later: API call)
  - Shows success alert

---

## Dependencies

- All mock data — no backend API calls needed
- Reuses existing CSS design system (card, kpi, badge, f-field classes)
- Reuses KpiCard component with tooltips
- Port calculation and fiscal logic from HTML prototype (`CashRoom_Production_1_prototype.html` lines 2184-2836)
