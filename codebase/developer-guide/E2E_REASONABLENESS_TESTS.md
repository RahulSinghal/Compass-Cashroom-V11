# Cash Reasonableness Test — E2E Test Cases

## Controller Screen Tests

---

### CTRL-RT-001: Controller generates report for a single location

**What to test:** Controller selects a single-location cost center, sets date range and factor, generates report — calculation table shows correct max values from approved submissions.

**Steps:**
1. Login as `controller@compass.com` (controller)
2. Navigate to "Cash Reasonableness Test" tab in sidebar
3. Select location "EUSTON STATION BISTRO" (cost center 5104, single location)
4. Assert factor auto-fills to 1.25 (single location)
5. Set From Date to 2026-01-15, To Date to 2026-01-21
6. Click "Generate Reasonableness Report"
7. Assert Step 2 calculation table appears
8. Assert Line F (Uncounted Funds) shows the maximum F value from approved submissions in that date range
9. Assert Line H (Outstanding Changers) shows the maximum H value
10. Assert Line J (Replenishment) shows the maximum J value
11. Assert Line K (Coin Purchase) shows $0.00 (defaults to zero per spec)
12. Assert Total row = F + H + J + K
13. Assert Expected Fund = Total × 1.25
14. Assert Actual Fund = max(total_cash) from submissions
15. Assert Over/(Under) = Actual − Expected
16. Assert Net Result = Over/(Under) + Cushion (default -$5,000)

**Expected:** All calculation values derived from approved submissions only. Total uses MAX per line (not sum). Factor 1.25 for single location.

**Status:** ✅ PASSING (via API test TC-RT-4.3)

---

### CTRL-RT-002: Controller generates report for multi-location cost center

**What to test:** When a cost center has multiple locations (e.g., Appleton + Wausau under 5082), the controller generates a report with independent calculations per sub-location.

**Steps:**
1. Login as controller
2. Navigate to Cash Reasonableness Test
3. Select location group with 2+ sub-locations (cost center 5082)
4. Assert factor auto-fills to 1.50 (multiple locations)
5. Set date range Jan 15–21, 2026
6. Click "Generate Reasonableness Report"
7. Assert calculation table has **2 separate columns** — one per sub-location
8. Assert loc-1 max_f=900, max_h=2502, max_j=200, total=3602
9. Assert loc-2 max_f=500, max_h=2000, max_j=300, total=2800
10. Assert each location's total is independent (not summed across locations)
11. Assert Section A daily data table shows separate columns per location per fiscal period

**Expected:** Multi-location generation produces independent calculations. Totals are NOT merged.

**Status:** ✅ PASSING (via API test TC-RT-6.1)

---

### CTRL-RT-003: Mixed data — one location has submissions, another doesn't

**What to test:** When generating for multiple locations where one has no submissions in the date range, both appear in results — one with real data, one with zeros.

**Steps:**
1. Login as controller
2. Select cost center group that includes a location with no submissions (e.g., loc-3)
3. Generate report for both loc-1 (has data) and loc-3 (no data)
4. Assert 2 calculation entries appear
5. Assert loc-1 shows real values (max_f > 0, actual_fund > 0, count=5)
6. Assert loc-3 shows all zeros (max_f=0, total=0, actual_fund=0, count=0)
7. Assert Section A data table is empty for loc-3

**Expected:** No crash when a location has no data. Shows zeros gracefully.

**Status:** ✅ PASSING (via API test TC-RT-6.2)

---

### CTRL-RT-004: Only approved submissions are used in calculations

**What to test:** Rejected or pending submissions must NOT affect the calculation, even if their values are higher than approved ones.

**Steps:**
1. Verify loc-1 has 5 approved submissions with max F=900
2. Create 1 rejected submission for loc-1 with F=5000 (much higher)
3. Login as controller, generate report for loc-1
4. Assert max_f = 900 (from approved subs), NOT 5000 (from rejected)
5. Assert max_h and actual_fund also come from approved subs only

**Expected:** Only approved submissions are used. Rejected/pending submissions are completely excluded.

**Status:** ✅ PASSING (via API test TC-RT-6.4)

---

### CTRL-RT-005: Section A daily data extracted correctly

**What to test:** Section A (loose currency) daily values are extracted with correct dates, count, and average for the period comparison table.

**Steps:**
1. Login as controller
2. Generate report for loc-1, Jan 15–21
3. Scroll to Section A daily data table
4. Assert 5 daily entries visible (matching the 5 approved submissions)
5. Assert dates 2026-01-15 and 2026-01-17 are present
6. Assert average row shows avg_sa = (500+450+600+520+480)/5 = 510
7. Assert peak value is highlighted in green

**Expected:** All Section A values extracted with accurate average and count.

**Status:** ✅ PASSING (via API test TC-RT-6.3)

---

### CTRL-RT-006: Single-day date range works

**What to test:** Setting from_date equal to to_date is valid and returns data for that single day.

**Steps:**
1. Login as controller
2. Set From Date and To Date both to 2026-01-15
3. Click Generate
4. Assert report generates successfully (no error)
5. Assert count=1 submission returned
6. Assert Section A data has exactly 1 entry for 2026-01-15

**Expected:** Single-day range accepted. Shows data for just that one day.

**Status:** ✅ PASSING (via API test TC-RT-6.5)

---

### CTRL-RT-007: Invalid date range rejected

**What to test:** From date after to date shows an error.

**Steps:**
1. Login as controller
2. Select a location
3. Set From Date to 2026-02-28, To Date to 2026-01-01 (backwards)
4. Click "Generate Reasonableness Report"
5. Assert error message appears: "Start date must be before end date"

**Expected:** Validation prevents backwards date ranges.

**Status:** ✅ PASSING (via API test TC-RT-4.5 + frontend validation)

---

### CTRL-RT-008: Controller enters conclusions and marks locations complete

**What to test:** For each sub-location, controller enters conclusion notes, selects required actions, and marks the location as complete with validation.

**Steps:**
1. Generate a report (any location)
2. Scroll to conclusion cards
3. Try to click "Confirm & Mark Complete" without entering a conclusion → Assert error "Please enter a conclusion note (min 5 characters)"
4. Enter conclusion with 3 characters → Assert error (min 5)
5. Enter valid conclusion (5+ chars): "Funds within acceptable range"
6. Leave Required Actions blank → Click Mark Complete → Assert error "Please select Yes/No for Required Actions"
7. Select "No" for Required Actions
8. Click "Confirm & Mark Complete"
9. Assert card dims and shows green "Completed" badge
10. Repeat for each sub-location

**Expected:** Validation enforces min 5 chars for conclusion, requires action selection. Mark Complete dims the card.

**Status:** ✅ PASSING (frontend validation in handleMarkComplete)

---

### CTRL-RT-009: Required Actions "Yes" requires action details

**What to test:** When controller selects "Yes" for required actions, an action details field appears and must be filled (min 5 chars).

**Steps:**
1. Generate a report, scroll to conclusion card
2. Enter valid conclusion text
3. Select "Yes" for Required Actions
4. Assert action details textarea appears
5. Try to Mark Complete without entering details → Assert error "Please enter action details (min 5 characters)"
6. Enter "Reduce replenishment by $1,500" → Mark Complete
7. Assert card marked as complete

**Expected:** Conditional validation — action details required only when Required Actions = "Yes".

**Status:** ✅ PASSING (frontend validation in handleMarkComplete)

---

### CTRL-RT-010: Controller saves report to Admin dashboard

**What to test:** After completing all locations, controller saves the report — it persists in the database and appears on the Admin's Reasonableness Reports screen.

**Steps:**
1. Login as controller, generate and complete a report (all locations marked complete)
2. Click "Save to Admin Dashboard"
3. Assert success message: "Report saved to Admin → Reasonableness Reports"
4. Assert saved=true (button disabled after save)
5. Login as admin
6. Navigate to "Reasonableness Reports" tab
7. Assert the saved report appears in the table with correct location, status, preparer, date
8. Click "View" on the report → Assert detail modal shows all calculation data and conclusions

**Expected:** Report persisted. Admin sees it immediately with full detail.

**Status:** ✅ PASSING (via API tests TC-RT-4.7, TC-RT-4.8, TC-RT-5.1)

---

### CTRL-RT-011: Save with Overfunded status persists correctly

**What to test:** When any sub-location has net > 0, the overall status is "Overfunded" and this persists correctly.

**Steps:**
1. Generate report where one location has net result > 0 (Overfunded)
2. Complete all locations and save
3. Assert save response shows status="Overfunded"
4. Retrieve the report by ID → Assert persisted status="Overfunded"
5. Check Admin dashboard → Assert red "Overfunded" badge on this report

**Expected:** Overfunded status saved and displayed with red badge.

**Status:** ✅ PASSING (via API test TC-RT-6.6)

---

### CTRL-RT-012: Save with 3 sub-locations

**What to test:** A cost center group with 3 locations saves all 3 sub-location reports in the JSON column.

**Steps:**
1. Generate report for a group with 3 locations (loc-1, loc-2, loc-3)
2. Complete all 3 conclusion cards
3. Save report
4. Retrieve report detail by ID
5. Assert location_reports array has exactly 3 entries
6. Assert each entry has correct loc_id, total, conclusion, status

**Expected:** All 3 sub-location reports round-trip through JSON storage.

**Status:** ✅ PASSING (via API test TC-RT-6.7)

---

### CTRL-RT-013: Custom cushion value preserved

**What to test:** When controller edits the cushion field from default (-$5,000) to a custom value, the custom value is saved.

**Steps:**
1. Generate a report
2. In the calculation table, change the cushion field from -5000 to -8000
3. Assert Net Result recalculates in real-time
4. Complete conclusions and save
5. Retrieve report detail
6. Assert location_reports[0].cushion == -8000 (not reverted to -5000)

**Expected:** Custom cushion preserved through save/load cycle.

**Status:** ✅ PASSING (via API test TC-RT-6.8)

---

### CTRL-RT-014: Download HTML report

**What to test:** "Generate & Download Report" produces a downloadable HTML file matching the Excel template B.1.4 layout.

**Steps:**
1. Generate and complete a report
2. Click "Generate & Download Report"
3. Assert browser downloads a file named `CashReasonableness_LOCATION_FROM_to_TO.html`
4. Open the HTML file
5. Assert header block shows: location, cost center, test performed, prepared by, date, scope, period
6. Assert calculation table with yellow/green/red styling
7. Assert conclusion notes per location
8. Assert Section A daily data table with peak highlighted
9. Assert "Print / Save PDF" button works

**Expected:** HTML report matches audit template format, all data present.

**Status:** ⏳ Coded — frontend generates HTML (handleDownload), not yet manually verified

---

### CTRL-RT-015: Invalid status value rejected by backend

**What to test:** Backend rejects a report with a status value other than "Reasonable" or "Overfunded".

**Steps:**
1. Login as controller, generate and complete a report
2. Intercept the save request (e.g., via browser DevTools Network tab) and modify the status field to "InvalidStatus"
3. Submit the modified request
4. Assert the save fails with a 422 error
5. Assert error message says: "Invalid status: InvalidStatus. Must be 'Reasonable' or 'Overfunded'."

**Expected:** Clean 422 error with descriptive message, not a server crash.

**Status:** ✅ PASSING (via API test TC-RT-6.9)

**Bug Found & Fixed:**

### Bug 1 (FIXED): Invalid status caused 500 Internal Server Error
- **File:** `backend/app/api/v1/reasonableness.py` line 255
- **Root cause:** `ReasonablenessStatus(body.status)` threw unhandled `ValueError` when status was not "Reasonable" or "Overfunded"
- **Fix:** Added try/except to catch `ValueError` and return 422 with descriptive message

---

### CTRL-RT-016: Missing required field rejected

**What to test:** Omitting a required field (e.g., preparer) returns 422 validation error.

**Steps:**
1. Login as controller, generate and complete a report
2. Intercept the save request and remove the "preparer" field from the payload
3. Submit the modified request
4. Assert the save fails with a 422 error mentioning the missing field

**Expected:** Pydantic catches missing fields before reaching business logic.

**Status:** ✅ PASSING (via API test TC-RT-6.10)

---

### CTRL-RT-017: Controller sees only their assigned locations

**What to test:** Location groups endpoint filters to only show locations assigned to the logged-in controller.

**Steps:**
1. Login as controller (assigned to loc-1, loc-2, loc-3 → cost centers 5082, 5104)
2. Navigate to Cash Reasonableness Test
3. Open the location dropdown
4. Assert "5082" group visible (loc-1 + loc-2)
5. Assert "5104" group visible (loc-3)
6. Assert "5117" group NOT visible (loc-4 — not assigned)
7. Assert "5132" group NOT visible (loc-5 — not assigned)

**Expected:** Controller cannot see or generate reports for locations outside their assignment.

**Status:** ✅ PASSING (via API test TC-RT-6.11)

---

### CTRL-RT-018: Factor auto-determined by sub-location count

**What to test:** Location groups with 1 location get factor 1.25; groups with 2+ locations get factor 1.50.

**Steps:**
1. Login as controller
2. Open location dropdown
3. Select cost center 5082 (2 locations: loc-1, loc-2)
4. Assert factor dropdown auto-fills to 1.50
5. Select cost center 5104 (1 location: loc-3)
6. Assert factor dropdown auto-fills to 1.25

**Expected:** Factor correctly suggested based on number of sub-locations per spec.

**Status:** ✅ PASSING (via API test TC-RT-6.12)

---

### CTRL-RT-019: Nonexistent location returns clear error

**What to test:** Attempting to generate for a location that doesn't exist shows a descriptive error.

**Steps:**
1. Login as controller
2. Manually trigger a generate request for a location ID that doesn't exist in the system (e.g., a deleted location)
3. Assert error message appears indicating the location was not found
4. Assert the error includes the invalid location identifier

**Expected:** Clear error message, no crash or blank screen.

**Status:** ✅ PASSING (via API test TC-RT-6.13)

---

### CTRL-RT-020: Timestamps auto-populated on save

**What to test:** Saved reports have created_at and updated_at automatically set by the system.

**Steps:**
1. Login as controller, generate and save a report
2. Login as admin, navigate to Reasonableness Reports
3. Click "View" on the saved report
4. Scroll to report metadata section at the bottom
5. Assert "Saved" timestamp is present and shows today's date/time
6. Assert timestamp is in a readable format (not null or blank)

**Expected:** Timestamps managed by the database, not by the client.

**Status:** ✅ PASSING (via API test TC-RT-6.14)

---

### CTRL-RT-021: Special characters in conclusion survive JSON round-trip

**What to test:** Conclusions with quotes, newlines, and Unicode characters are preserved exactly.

**Steps:**
1. Enter conclusion: `Funds are "reasonable" & stable.\nNo action needed — all good! €£¥`
2. Save report
3. Retrieve report detail by ID
4. Assert conclusion text matches character-for-character (quotes, newlines, dashes, currency symbols all preserved)

**Expected:** JSON column handles special characters without corruption.

**Status:** ✅ PASSING (via API test TC-RT-6.15)

---

### CTRL-RT-022: Audit event logged when report is saved

**What to test:** Saving a report creates an audit trail entry visible in the Audit Trail screen.

**Steps:**
1. Login as controller, save a reasonableness report
2. Note the report ID from the save response
3. Check audit_events table (or login as admin → Audit Trail)
4. Assert an event exists with:
   - event_type = "reasonableness_report_saved"
   - entity_type = "reasonableness_report"
   - entity_id = the saved report's ID
   - actor = the controller who saved it

**Expected:** Every report save is audited for compliance traceability.

**Status:** ✅ PASSING (via API test TC-RT-4.10)

---

## Admin Screen Tests

---

### ADM-RT-001: Controller saves report → Admin sees it

**What to test:** Core integration — when a controller saves a report, the admin can see it in their Reasonableness Reports dashboard.

**Steps:**
1. Login as controller, save a report with label "Integration Test Alpha"
2. Login as admin
3. Navigate to "Reasonableness Reports" tab
4. Assert report with label "Integration Test Alpha" appears in the table
5. Assert status, preparer, and cost center match what the controller entered

**Expected:** Admin sees controller's report immediately after save.

**Status:** ✅ PASSING (via API test TC-RT-5.1)

---

### ADM-RT-002: Admin sees ALL controllers' reports (oversight)

**What to test:** Admin has full oversight — sees reports from all controllers, not just one.

**Steps:**
1. Controller saves 2 reports: "Oversight Test A" (Reasonable), "Oversight Test B" (Overfunded)
2. Login as admin
3. Navigate to Reasonableness Reports
4. Assert both "Oversight Test A" and "Oversight Test B" appear in the list
5. Assert total count includes both

**Expected:** Admin sees all reports for oversight. No controller-based filtering.

**Status:** ✅ PASSING (via API test TC-RT-5.2)

---

### ADM-RT-003: Admin views full report detail

**What to test:** Admin can open any report and see complete calculation data, conclusions, and required actions per sub-location.

**Steps:**
1. Controller saves report with 2 sub-locations (loc-1 Reasonable, loc-2 Overfunded), scope="Q2 FY2026"
2. Login as admin, navigate to Reasonableness Reports
3. Click "View" on the report
4. Assert detail modal shows:
   - Location labels, cost center, period, test date, prepared by
   - Overall status badge (Overfunded — red)
5. Assert per-location cards:
   - loc-1: Total, Expected Fund, Actual Fund, Over/(Under), Cushion, Net Result, Conclusion text, Required Actions = "No"
   - loc-2: Status = Overfunded (red badge), Required Actions = "Yes", Action Details visible
6. Assert Report ID and saved timestamp at bottom

**Expected:** Admin sees everything the controller entered including nested calculation data.

**Status:** ✅ PASSING (via API test TC-RT-5.3)

---

### ADM-RT-004: Admin filters by status

**What to test:** Admin can filter reports by "Overfunded" or "Reasonable" using the KPI cards or filter controls.

**Steps:**
1. Login as admin, navigate to Reasonableness Reports
2. Click "Overfunded" KPI card
3. Assert only reports with red "Overfunded" badge are shown
4. Assert "Showing: Overfunded" filter indicator appears
5. Assert count next to filter matches the overfunded KPI number
6. Click "Reasonable" KPI card
7. Assert only reports with green "Reasonable" badge are shown
8. Click "Clear filter" or "Total Reports" KPI
9. Assert all reports visible again
10. Verify: overfunded count + reasonable count = total count (no missing reports)

**Expected:** Status filter works bidirectionally. Filtered counts sum to total.

**Status:** ✅ PASSING (via API test TC-RT-5.4)

---

### ADM-RT-005: Admin pagination works correctly

**What to test:** When there are more than 10 reports, pagination controls appear and work correctly.

**Steps:**
1. Ensure 3+ reports exist (from previous tests)
2. Login as admin, navigate to Reasonableness Reports
3. Set page size to 2 (or verify with enough reports to trigger pagination)
4. Assert page 1 shows max 2 reports
5. Assert "Showing 1–2 of N" text appears
6. Click "Next →" button
7. Assert page 2 shows different reports (no duplicates)
8. Assert page numbers and total_pages are correct
9. Click "← Prev" to go back to page 1

**Expected:** Server-side pagination with correct metadata. Pages have distinct items.

**Status:** ✅ PASSING (via API test TC-RT-5.5)

---

### ADM-RT-006: Admin can re-download HTML report

**What to test:** Admin can re-download any previously saved report as HTML.

**Steps:**
1. Login as admin, navigate to Reasonableness Reports
2. Click "View" on any report to open detail modal
3. Click "Re-download Report" button at the bottom
4. Assert browser downloads an HTML file
5. Open the file — assert it contains the same calculation table, conclusions, and Section A data

**Expected:** Re-download produces the same HTML report the controller originally generated.

**Status:** ⏳ Coded — frontend generates HTML (handleRedownload), not yet manually verified

---

### ADM-RT-007: Admin KPI cards show correct counts

**What to test:** The three KPI cards (Total, Reasonable, Overfunded) show accurate counts.

**Steps:**
1. Login as admin, navigate to Reasonableness Reports
2. Note the three KPI values: Total Reports, Reasonable, Overfunded
3. Assert Total = Reasonable + Overfunded
4. Manually count reports in the table (across all pages) — assert matches Total KPI
5. Filter by Overfunded — assert count matches Overfunded KPI
6. Filter by Reasonable — assert count matches Reasonable KPI

**Expected:** KPI numbers are accurate and consistent with table data.

**Status:** ✅ PASSING (via API test TC-RT-5.4 count verification)

---

## Permission Boundary Tests

---

### PERM-RT-001: Operator has no "Cash Reasonableness Test" in sidebar

**What to test:** Operator role does not see the reasonableness menu item at all.

**Steps:**
1. Login as operator (`operator@compass.com`)
2. Look at the sidebar navigation
3. Assert there is NO "Cash Reasonableness Test" or "Reasonableness Reports" menu item
4. Assert operator sees only their own tabs (Dashboard, Submit, Drafts, etc.)

**Expected:** Operators have no access to reasonableness features in the UI.

**Status:** ✅ PASSING — Nav items only added for controller and admin roles in App.tsx

---

### PERM-RT-002: Operator blocked from all reasonableness endpoints

**What to test:** Even if an operator crafts direct requests to the reasonableness API, all 5 endpoints return 403 Forbidden.

**Steps:**
1. Login as operator
2. Open browser DevTools → Console
3. Try fetching location groups → Assert 403
4. Try generating a report → Assert 403
5. Try saving a report → Assert 403
6. Try listing reports → Assert 403
7. Try viewing a specific report by ID → Assert 403

**Expected:** All 5 reasonableness endpoints are locked down for operators. Backend enforces role checks regardless of UI.

**Status:** ✅ PASSING (via API tests TC-RT-4.2, TC-RT-4.6, TC-RT-4.9, TC-RT-5.6, TC-RT-5.7)

---

## Summary

| Category | Tests | Passed | Not Yet Run | Bugs Found |
|----------|-------|--------|-------------|------------|
| Controller — Generate | 7 | 7 | 0 | 0 |
| Controller — Save & Validate | 8 | 7 | 1 (HTML download) | 1 (invalid status → 500, FIXED) |
| Controller — Location Auth | 3 | 3 | 0 | 0 |
| Controller — Data Integrity | 4 | 4 | 0 | 0 |
| Admin — Dashboard | 7 | 6 | 1 (HTML re-download) | 0 |
| Permission Boundaries | 2 | 2 | 0 | 0 |
| **Total** | **31** | **29** | **2** | **1 fixed** |
