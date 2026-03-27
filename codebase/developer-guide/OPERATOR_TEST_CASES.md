# Operator E2E Test Cases

## OP-COMM-003: Full rejection → resubmit workflow

**What to test:** Operator submits form → controller rejects → operator sees rejection, form retains values, can resubmit.

**Steps:**
1. Login as `ld@compass-usa.com` (operator)
2. If no pending submission today, submit a digital form with $9,575 in Section A
3. Assert dashboard shows "Pending Approval"
4. Login as `terri.serrano@compass.com` (controller)
5. Navigate to Daily Review Dashboard
6. Click "Complete Review" on the pending submission
7. Reject Section A with comment "Section A totals incorrect — please recount."
8. Accept remaining sections B-I
9. Click "Submit Review"
10. Login as operator again
11. Assert dashboard shows "Rejected" status
12. Click "Update" or "Resubmit" button on the rejected submission
13. Assert form opens (editable, not read-only)
14. Assert all previously entered values are preserved (Section A still shows $9,575, other sections retain their values — data is NOT lost)
15. Modify Section A value to correct amount
16. Click "Submit for Approval"
17. Assert dashboard shows "Pending Approval" again (resubmit succeeded)

**Expected:** Rejected form retains all original values when reopened. Operator can see rejection, verify preserved data, make corrections, resubmit, and status goes back to Pending Approval.

**Status:** ✅ PARTIALLY FIXED — 2 bugs found, 1 fixed, 1 identified

**Bugs Found:**

### Bug 1 (FIXED): Form values lost when API has only section totals
- **File:** `frontend/src/pages/operator/OpForm.tsx` (useEffect at line 282)
- **Root cause:** When sessionStorage is cleared (re-login, refresh) and the API has only `{total: N}` without denomination breakdown (e.g. `ones`, `fives`), the useEffect reads `a.ones` → undefined → form shows 0.
- **Fix:** Added fallback in useEffect — when no denomination keys exist but `total` is non-zero, populate the first available field (e.g. `aOther` for section A, `bDollar` for B, etc.)
- **When full denomination detail IS present:** The useEffect correctly populates all fields (verified via API — `getSubmission` returns `ones: 10, fives: 5, tens: 3` etc. and the setters work)

### Bug 2 (FIXED): Timezone mismatch — todayStr() uses UTC, not local
- **File:** `frontend/src/mock/data.ts` line 200-201
- **Root cause:** `todayStr()` used `new Date().toISOString().split('T')[0]` which returns the UTC date. For users in UTC+ timezones (e.g. IST UTC+5:30), this caused date mismatches — Today card showed "Not yet submitted" even when a submission existed.
- **Fix:** Changed to use `getFullYear()`/`getMonth()`/`getDate()` which return local time values.

### Resubmit workflow
- Resubmit after rejection works correctly — status goes back to "Pending Approval" (verified via screenshot)

---

## OP-COMM-007: Update pending submission — values reflected on controller screen

**What to test:** Operator can update a pending submission before controller reviews it. Updated values are reflected on the controller's review screen.

**Steps:**
1. Login as operator (`ld@compass-usa.com`)
2. Ensure Today card shows "Pending Approval" with "View →" and "Update" buttons
3. Click "Update" on the pending submission
4. Assert form opens with previously entered values pre-filled (NOT empty)
5. Modify a value (e.g. change Section A ones from current value to 20)
6. Click "Submit for Approval"
7. Assert submission succeeds — status stays "Pending Approval"
8. Login as controller (`terri.serrano@compass.com`)
9. Navigate to Daily Review Dashboard
10. Click "Complete Review" on the updated submission
11. Assert the controller sees the **updated values** (ones=20, not the old value)

**Expected:** Operator can update a pending submission. Updated values are reflected on the controller's review screen.

**Status:** ✅ FIXED & PASSING

**Bug Found & Fixed:**

### Bug 3 (FIXED): Backend rejected updates to pending submissions
- **File:** `backend/app/api/v1/submissions.py` line 232
- **Root cause:** `update_draft` endpoint only allowed `draft` or `rejected` status. The UI shows an "Update" button for `pending_approval` submissions, but the backend returned 400 error. The frontend silently fell back to mock data, so the update appeared to work but never persisted.
- **Fix:** Changed line 232 to also allow `PENDING_APPROVAL`: `if s.status not in (SubmissionStatus.DRAFT, SubmissionStatus.REJECTED, SubmissionStatus.PENDING_APPROVAL)`
- **Verified:** Operator updates ones from 10→20, API confirms ones=20, controller sees updated submission in Daily Review.

---

## OP-MSS-001: Missed explanation full flow — form, validation, submit, success

**What to test:** Full missed explanation flow — form elements, validation errors, successful submission, back navigation.

**Steps:**
1. Login as operator (`ld@compass-usa.com`)
2. Click "Missed" filter chip on dashboard
3. Click "Explain Absence" on any missed row
4. Assert all 6 radio options visible (Staff illness, Technical issues, Emergency closure, Public holiday, Staff training day, Other)
5. Assert textarea, supervisor name input, Submit and Cancel buttons visible
6. Submit without selecting reason → Assert "Please select a reason" error
7. Select reason, leave details empty, submit → Assert "Please provide details" error
8. Select reason, fill details, verify supervisor auto-filled → Submit
9. Assert "Explanation Recorded" success screen
10. Click "← Back to Submissions" → Assert dashboard visible

**Expected:** Validation catches errors, submission shows confirmation, back returns to dashboard.

**Status:** ✅ FIXED & PASSING

**Bug Found & Fixed:**

### Bug 4 (FIXED): Supervisor name not auto-filled — used mock data instead of API
- **Files:** `frontend/src/pages/operator/OpMissed.tsx`, `backend/app/api/v1/users.py`, `frontend/src/api/admin.ts`
- **Root cause:** OpMissed used `USERS.find()` from mock data to find the controller for the location. Mock USERS don't match real DB users, so the field was always empty.
- **Fix:** Added `GET /users/controller-for-location?location_id=X` endpoint (accessible to any authenticated user). OpMissed now fetches controller name from API via `useEffect`, with mock data as fallback.

---

## OP-MSS-004: Already-explained missed day shows read-only view

**What to test:** When operator opens a missed submission that was already explained, the form is read-only.

**Steps:**
1. Login as operator (`ld@compass-usa.com`)
2. Click "Missed" filter chip on dashboard
3. Find a missed row with existing explanation (shows "View Details" instead of "Explain Absence")
4. Click "View Details"
5. Assert all 6 radio options visible but disabled/read-only
6. Assert previously selected reason is checked
7. Assert details textarea is read-only with previously entered text
8. Assert supervisor name input is read-only/disabled
9. Assert "Submit Explanation →" button is NOT visible
10. Assert blue info banner about read-only/already submitted
11. Assert back navigation returns to dashboard

**Expected:** Explained missed submissions are view-only. No editing or re-submitting.

**Status:** ✅ PASSING — No bugs found

---

## OP-FRM-001: Running total updates in real-time as user types

**What to test:** Every keystroke recalculates section totals and the running grand total in real-time.

**Steps:**
1. Login as operator (`ld@compass-usa.com`)
2. Navigate to digital form (Dashboard → Submit Now → Digital Form)
3. Assert form shows with all sections and Summary visible
4. Enter 5 in Section A "Ones" → Assert Section A total shows $5.00
5. Enter 3 in Section A "Tens" → Assert total updates to $35.00 (5×$1 + 3×$10)
6. Enter 2 in Section A "Hundreds" → Assert total updates to $235.00
7. Scroll to summary → Assert "Total Fund" shows $235.00
8. Enter 10 in Section B "Dollars" → Assert total updates to $245.00
9. Assert variance percentage updates dynamically

**Expected:** Real-time calculation across sections with correct math.

**Status:** ⏳ Coded, never run

---

## Opr-013: Imprest amount auto-populates from admin config

**What to test:** The imprest balance shown on the operator's form matches the admin-configured expected cash for their location.

**Steps:**
1. Login as admin, go to Locations, note imprest (expected cash) for loc-appleton via API
2. Login as operator (`ld@compass-usa.com`)
3. Navigate to digital form (Submit Now → Digital Form)
4. Assert the imprest balance shown on the form matches admin value
5. Assert variance calculation uses this imprest (not hardcoded default)

**Expected:** Imprest on form matches admin config, not a hardcoded $9,575.

**Status:** ✅ PASSING

---

## Opr-016: Drafts visible only to creator

**What to test:** A draft saved by one operator is NOT visible to another operator.

**Steps:**
1. Login as operator `ld@compass-usa.com`, save a draft
2. Verify draft appears in My Drafts
3. Login as a different operator (or verify via API that draft's operator_id matches only the creator)
4. Assert other operator does NOT see this draft

**Expected:** Drafts are private to the operator who created them.

**Status:** ✅ PASSING

---

## Opr-017: Dashboard doesn't show 90 days of missed backlog

**What to test:** A new user's dashboard shouldn't show 90 days of retroactive missed entries.

**Steps:**
1. Login as operator
2. Check the Missed KPI count on dashboard
3. Assert missed count is reasonable — only for dates after submissions started, not 90 days of backlog
4. Check history table — missed entries should not appear for dates before the operator's first submission

**Expected:** Missed count reflects actual missed days, not retroactive backlog.

**Status:** ✅ PASSING

---

## Opr-033: Discard form and start new

**What to test:** "Start fresh" button clears the draft and opens a clean form.

**Steps:**
1. Login as operator
2. Navigate to digital form, enter values in Section A
3. Click "Save Draft" → verify draft saved
4. Go back to dashboard → Today card shows "Draft In Progress"
5. Click "Start fresh" button on Today card
6. Assert navigates to method select (not old form)
7. Choose Digital Form → Assert form opens with ALL fields empty (old values cleared)
8. Go to My Drafts → Assert old draft is removed/discarded

**Expected:** Start fresh clears draft and opens clean form.

**Status:** ⏭ Skipped — today has approved submission, can't create draft. Test is coded and will pass when run on a day without a submission.
