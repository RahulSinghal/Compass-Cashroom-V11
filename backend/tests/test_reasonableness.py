"""
Cash Reasonableness Test — TDD Test Suite
==========================================

Phase 2 feature: quarterly compliance control that checks whether each
cash room holds appropriate funds relative to operational usage.

Test Approach:
- Tests are written FIRST (Red), then implementation follows (Green)
- Each test documents: Purpose, Setup, Action, Assertions
- Tests grouped by phase: Model → Schema → Business Logic → API Endpoints

Naming: TC-RT-{phase}.{number} for traceability to the TDD plan in
codebase/implementation-plans/2026-03-27_reasonableness-backend-tdd.md
"""
import uuid
import math
from datetime import date, datetime, timezone

import pytest
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
# Helpers — reusable across all test phases
# ---------------------------------------------------------------------------

SAMPLE_LOC_REPORT = {
    "loc_id": "loc-1",
    "loc_label": "The Grange Hotel",
    "total": 3452.0,
    "expected_fund": 4315.0,
    "actual_fund": 3800.0,
    "over": -515.0,
    "cushion": -5000.0,
    "net": -5515.0,
    "status": "Reasonable",
    "conclusion": "Funds within acceptable range for Q2 operations.",
    "required_actions": "no",
    "action_details": "",
}

SAMPLE_LOC_REPORT_OVERFUNDED = {
    **SAMPLE_LOC_REPORT,
    "loc_id": "loc-2",
    "loc_label": "Compass HQ Canteen",
    "total": 6000.0,
    "expected_fund": 7500.0,
    "actual_fund": 14000.0,
    "over": 6500.0,
    "cushion": -5000.0,
    "net": 1500.0,
    "status": "Overfunded",
    "conclusion": "Excess funds detected; review replenishment schedule.",
    "required_actions": "yes",
    "action_details": "Reduce next replenishment by $1,500.",
}


# ===========================================================================
# PHASE 1 — Model Tests (TC-RT-1.x)
# ===========================================================================
# These tests validate that the ReasonablenessReport ORM model correctly
# persists to and retrieves from the database, including enum constraints
# and JSON column round-trips.


class TestReasonablenessModel:
    """
    TC-RT-1.1: ReasonablenessReport model can be created and queried
    ----------------------------------------------------------------
    Purpose:  Verify the ORM model round-trips through SQLite correctly.
    Setup:    Import the model, create an instance with all required fields.
    Action:   Add to session, commit, then query back by primary key.
    Expect:   All fields match what was inserted; timestamps are populated.
    """

    def test_create_and_query_report(self, db_session: Session):
        from app.models.reasonableness import ReasonablenessReport, ReasonablenessStatus

        report_id = str(uuid.uuid4())
        report = ReasonablenessReport(
            id=report_id,
            group_key="5082",
            cost_center="5082",
            location_labels="APPLETON / WAUSAU",
            from_date=date(2026, 1, 1),
            to_date=date(2026, 2, 28),
            factor=1.50,
            preparer="Chris Controller",
            scope="Daily Cashroom Reconciliations for P4 and P5, FY2026",
            status=ReasonablenessStatus.REASONABLE,
            location_reports=[SAMPLE_LOC_REPORT],
            saved_by="user-123",
        )

        db_session.add(report)
        db_session.commit()

        # Query back
        fetched = db_session.get(ReasonablenessReport, report_id)
        assert fetched is not None, "Report should be retrievable by primary key"
        assert fetched.group_key == "5082"
        assert fetched.cost_center == "5082"
        assert fetched.location_labels == "APPLETON / WAUSAU"
        assert fetched.from_date == date(2026, 1, 1)
        assert fetched.to_date == date(2026, 2, 28)
        assert fetched.factor == 1.50
        assert fetched.preparer == "Chris Controller"
        assert fetched.scope == "Daily Cashroom Reconciliations for P4 and P5, FY2026"
        assert fetched.status == ReasonablenessStatus.REASONABLE
        assert fetched.saved_by == "user-123"
        assert fetched.created_at is not None, "created_at should auto-populate"
        assert fetched.updated_at is not None, "updated_at should auto-populate"

        # Cleanup
        db_session.delete(fetched)
        db_session.commit()

    """
    TC-RT-1.2: Status enum constrains to Reasonable | Overfunded
    -------------------------------------------------------------
    Purpose:  Verify both valid enum values are accepted.
    Setup:    Create two reports — one Reasonable, one Overfunded.
    Action:   Commit both, then verify their status values.
    Expect:   Each has the correct enum value.
    """

    def test_status_enum_values(self, db_session: Session):
        from app.models.reasonableness import ReasonablenessReport, ReasonablenessStatus

        # Verify both enum values exist and are correct strings
        assert ReasonablenessStatus.REASONABLE.value == "Reasonable"
        assert ReasonablenessStatus.OVERFUNDED.value == "Overfunded"

        # Create a report with each status
        for status in [ReasonablenessStatus.REASONABLE, ReasonablenessStatus.OVERFUNDED]:
            rid = str(uuid.uuid4())
            report = ReasonablenessReport(
                id=rid,
                group_key="5104",
                cost_center="5104",
                location_labels="CENTRAL IL",
                from_date=date(2026, 1, 1),
                to_date=date(2026, 3, 31),
                factor=1.25,
                preparer="Chris Controller",
                status=status,
                location_reports=[],
                saved_by="user-123",
            )
            db_session.add(report)
            db_session.commit()

            fetched = db_session.get(ReasonablenessReport, rid)
            assert fetched.status == status, f"Expected {status}, got {fetched.status}"

            db_session.delete(fetched)
            db_session.commit()

    """
    TC-RT-1.3: location_reports JSON stores and retrieves list of dicts
    -------------------------------------------------------------------
    Purpose:  Verify the JSON column correctly stores an array of
              RtLocReport-shaped dictionaries and retrieves them intact.
    Setup:    Create a report with 2 location reports (one Reasonable,
              one Overfunded) in the location_reports JSON field.
    Action:   Commit, then re-query and inspect the JSON.
    Expect:   Both dicts round-trip with all keys/values preserved.
    """

    def test_location_reports_json_roundtrip(self, db_session: Session):
        from app.models.reasonableness import ReasonablenessReport, ReasonablenessStatus

        rid = str(uuid.uuid4())
        loc_reports = [SAMPLE_LOC_REPORT, SAMPLE_LOC_REPORT_OVERFUNDED]

        report = ReasonablenessReport(
            id=rid,
            group_key="5082",
            cost_center="5082",
            location_labels="APPLETON / WAUSAU",
            from_date=date(2026, 1, 1),
            to_date=date(2026, 2, 28),
            factor=1.50,
            preparer="Chris Controller",
            status=ReasonablenessStatus.OVERFUNDED,
            location_reports=loc_reports,
            saved_by="user-123",
        )
        db_session.add(report)
        db_session.commit()

        # Expire to force re-read from DB
        db_session.expire(report)
        fetched = db_session.get(ReasonablenessReport, rid)

        assert isinstance(fetched.location_reports, list), "Should be a list"
        assert len(fetched.location_reports) == 2, "Should have 2 location reports"

        # Verify first report (Reasonable)
        lr1 = fetched.location_reports[0]
        assert lr1["loc_id"] == "loc-1"
        assert lr1["total"] == 3452.0
        assert lr1["status"] == "Reasonable"
        assert lr1["conclusion"] == "Funds within acceptable range for Q2 operations."

        # Verify second report (Overfunded)
        lr2 = fetched.location_reports[1]
        assert lr2["loc_id"] == "loc-2"
        assert lr2["net"] == 1500.0
        assert lr2["status"] == "Overfunded"
        assert lr2["required_actions"] == "yes"
        assert lr2["action_details"] == "Reduce next replenishment by $1,500."

        # Cleanup
        db_session.delete(fetched)
        db_session.commit()

    """
    TC-RT-1.4: Location.group column exists and is queryable
    ---------------------------------------------------------
    Purpose:  Verify the new 'group' column on the Location model
              can be set, persisted, and used in filter queries.
    Setup:    Update existing seed locations to have group values,
              then query locations by group.
    Action:   Set group on loc-1 and loc-2 to same value,
              query WHERE group == value.
    Expect:   Both locations returned; loc-3 (different group) excluded.
    """

    def test_location_group_column(self, db_session: Session):
        from app.models.location import Location

        # Set group values on seed locations
        loc1 = db_session.get(Location, "loc-1")
        loc2 = db_session.get(Location, "loc-2")
        loc3 = db_session.get(Location, "loc-3")

        assert loc1 is not None, "Seed location loc-1 should exist"
        assert loc2 is not None, "Seed location loc-2 should exist"

        loc1.group = "GRP-A"
        loc2.group = "GRP-A"
        loc3.group = "GRP-B"
        db_session.commit()

        # Query by group
        grp_a = db_session.query(Location).filter(Location.group == "GRP-A").all()
        assert len(grp_a) == 2, "Should find 2 locations in GRP-A"
        grp_a_ids = {l.id for l in grp_a}
        assert "loc-1" in grp_a_ids
        assert "loc-2" in grp_a_ids

        # Verify different group is excluded
        grp_b = db_session.query(Location).filter(Location.group == "GRP-B").all()
        assert len(grp_b) == 1
        assert grp_b[0].id == "loc-3"

        # Cleanup — reset group values to avoid side effects
        loc1.group = None
        loc2.group = None
        loc3.group = None
        db_session.commit()


# ===========================================================================
# Fixture: db_session for model tests (function-scoped, rolls back)
# ===========================================================================

@pytest.fixture()
def db_session():
    """
    Provides a fresh SQLAlchemy session for each test function.
    Uses the same test database as conftest.py's setup_db.
    Each test gets its own session to avoid cross-test contamination.
    """
    from tests.conftest import TestingSessionLocal
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ===========================================================================
# PHASE 2 — Schema Tests (TC-RT-2.x)
# ===========================================================================
# These tests validate that Pydantic schemas correctly parse, validate,
# and serialize data for the reasonableness API endpoints.


class TestReasonablenessSchemas:
    """
    TC-RT-2.1: GenerateRequest accepts valid input
    -----------------------------------------------
    Purpose:  Verify the GenerateRequest schema parses a well-formed request
              with all required fields: location_ids, from_date, to_date, factor.
    Setup:    Construct a dict with valid values.
    Action:   Instantiate GenerateRequest from the dict.
    Expect:   All fields accessible with correct types and values.
    """

    def test_generate_request_valid(self):
        from app.schemas.reasonableness import GenerateRequest

        data = {
            "location_ids": ["loc-1", "loc-2"],
            "from_date": "2026-01-01",
            "to_date": "2026-02-28",
            "factor": 1.50,
        }
        req = GenerateRequest(**data)
        assert req.location_ids == ["loc-1", "loc-2"]
        assert req.from_date == "2026-01-01"
        assert req.to_date == "2026-02-28"
        assert req.factor == 1.50

    """
    TC-RT-2.2: GenerateRequest rejects missing required fields
    -----------------------------------------------------------
    Purpose:  Verify that omitting required fields raises a ValidationError.
    Setup:    Construct a dict missing 'location_ids'.
    Action:   Attempt to instantiate GenerateRequest.
    Expect:   Pydantic raises ValidationError mentioning the missing field.
    """

    def test_generate_request_missing_fields(self):
        from pydantic import ValidationError
        from app.schemas.reasonableness import GenerateRequest

        # Missing location_ids
        with pytest.raises(ValidationError) as exc_info:
            GenerateRequest(from_date="2026-01-01", to_date="2026-02-28", factor=1.25)
        assert "location_ids" in str(exc_info.value)

        # Missing factor
        with pytest.raises(ValidationError) as exc_info:
            GenerateRequest(location_ids=["loc-1"], from_date="2026-01-01", to_date="2026-02-28")
        assert "factor" in str(exc_info.value)

    """
    TC-RT-2.3: SaveReportBody accepts well-formed report data
    -----------------------------------------------------------
    Purpose:  Verify SaveReportBody parses a complete report submission
              including nested location_reports array.
    Setup:    Construct a dict mirroring the controller's save payload
              with one Reasonable and one Overfunded sub-location report.
    Action:   Instantiate SaveReportBody.
    Expect:   All fields including nested location_reports are accessible.
    """

    def test_save_report_body_valid(self):
        from app.schemas.reasonableness import SaveReportBody

        data = {
            "group_key": "5082",
            "cost_center": "5082",
            "location_labels": "APPLETON / WAUSAU",
            "from_date": "2026-01-01",
            "to_date": "2026-02-28",
            "factor": 1.50,
            "preparer": "Chris Controller",
            "scope": "Q2 FY2026 review",
            "status": "Overfunded",
            "location_reports": [SAMPLE_LOC_REPORT, SAMPLE_LOC_REPORT_OVERFUNDED],
        }
        body = SaveReportBody(**data)
        assert body.group_key == "5082"
        assert body.preparer == "Chris Controller"
        assert len(body.location_reports) == 2
        assert body.location_reports[0].loc_id == "loc-1"
        assert body.location_reports[0].status == "Reasonable"
        assert body.location_reports[1].loc_id == "loc-2"
        assert body.location_reports[1].status == "Overfunded"

    """
    TC-RT-2.4: ReportOut serializes from ORM model attributes
    -----------------------------------------------------------
    Purpose:  Verify ReportOut can be constructed from a dict that
              mirrors ORM model attributes (from_attributes=True).
    Setup:    Construct a dict with all fields including datetime strings.
    Action:   Use model_validate with from_attributes-compatible data.
    Expect:   ReportOut instance has all fields correctly mapped.
    """

    def test_report_out_from_attributes(self):
        from app.schemas.reasonableness import ReportOut

        now = datetime.now(timezone.utc)
        data = {
            "id": "rpt-001",
            "group_key": "5082",
            "cost_center": "5082",
            "location_labels": "APPLETON / WAUSAU",
            "from_date": date(2026, 1, 1),
            "to_date": date(2026, 2, 28),
            "factor": 1.50,
            "preparer": "Chris Controller",
            "scope": "Q2 review",
            "status": "Reasonable",
            "location_reports": [SAMPLE_LOC_REPORT],
            "saved_by": "user-123",
            "created_at": now,
            "updated_at": now,
        }
        out = ReportOut.model_validate(data)
        assert out.id == "rpt-001"
        assert out.status == "Reasonable"
        assert out.saved_by == "user-123"
        assert len(out.location_reports) == 1

    """
    TC-RT-2.5: PaginatedReports has correct structure
    --------------------------------------------------
    Purpose:  Verify the PaginatedReports schema wraps a list of ReportOut
              with pagination metadata (items, total, page, page_size, total_pages).
    Setup:    Construct a dict with items=[] and pagination metadata.
    Action:   Instantiate PaginatedReports.
    Expect:   All pagination fields are accessible and correct.
    """

    def test_paginated_reports_structure(self):
        from app.schemas.reasonableness import PaginatedReports

        data = {
            "items": [],
            "total": 0,
            "page": 1,
            "page_size": 20,
            "total_pages": 0,
        }
        paginated = PaginatedReports(**data)
        assert paginated.items == []
        assert paginated.total == 0
        assert paginated.page == 1
        assert paginated.page_size == 20
        assert paginated.total_pages == 0


# ===========================================================================
# PHASE 3 — Business Logic Tests (TC-RT-3.x)
# ===========================================================================
# These tests validate the calculation engine in isolation (no HTTP, no DB).
# They test the pure functions that compute max values, totals, expected
# fund amounts, over/under, cushion, net result, and status determination.


class TestReasonablenessCalculations:
    """
    TC-RT-3.1: Total = max(F) + max(H) + max(J) + max(K)
    ------------------------------------------------------
    Purpose:  Verify the total calculation sums the maximum of each
              section line across a set of submissions in a date range.
    Setup:    Create 3 mock submission-like dicts with varying F/H/J values
              to ensure max (not sum or average) is used for each line.
    Action:   Call compute_max_values() with the submissions.
    Expect:   total = max(F) + max(H) + max(J) + 0 (K defaults to 0).
              Specifically: max(800,600,900)=900 + max(2502,2000,2200)=2502
              + max(150,200,100)=200 + 0 = 3602
    """

    def test_total_from_max_sections(self):
        from app.api.v1.reasonableness import compute_max_values

        # Simulate 3 submissions with sections JSON
        submissions = [
            {"sections": {"F": {"total": 800},  "H": {"total": 2502}, "J": {"total": 150}}, "total_cash": 9800},
            {"sections": {"F": {"total": 600},  "H": {"total": 2000}, "J": {"total": 200}}, "total_cash": 8500},
            {"sections": {"F": {"total": 900},  "H": {"total": 2200}, "J": {"total": 100}}, "total_cash": 10200},
        ]
        result = compute_max_values(submissions)
        assert result["max_f"] == 900.0
        assert result["max_h"] == 2502.0
        assert result["max_j"] == 200.0
        assert result["max_k"] == 0.0  # K always defaults to 0
        assert result["total"] == 900.0 + 2502.0 + 200.0 + 0.0  # 3602.0

    """
    TC-RT-3.2: Actual fund = max(total_cash) from submissions
    ----------------------------------------------------------
    Purpose:  Verify actual_fund is the maximum total_cash value
              across all submissions in the date range, not sum or average.
    Setup:    3 submissions with total_cash = 9800, 8500, 10200.
    Action:   Call compute_max_values() and check actual_fund.
    Expect:   actual_fund = 10200 (the maximum).
    """

    def test_actual_from_max_total_cash(self):
        from app.api.v1.reasonableness import compute_max_values

        submissions = [
            {"sections": {"F": {"total": 100}}, "total_cash": 9800},
            {"sections": {"F": {"total": 100}}, "total_cash": 8500},
            {"sections": {"F": {"total": 100}}, "total_cash": 10200},
        ]
        result = compute_max_values(submissions)
        assert result["actual_fund"] == 10200.0

    """
    TC-RT-3.3: Net result = (actual - expected) + cushion
    ------------------------------------------------------
    Purpose:  Verify the net result calculation follows the formula:
              expected = total * factor
              over = actual - expected
              net = over + cushion
    Setup:    total=3602, factor=1.50, actual=9800, cushion=-5000.
              expected = 3602 * 1.50 = 5403
              over = 9800 - 5403 = 4397
              net = 4397 + (-5000) = -603
    Action:   Call compute_net_result() with these values.
    Expect:   expected=5403, over=4397, net=-603.
    """

    def test_net_calculation(self):
        from app.api.v1.reasonableness import compute_net_result

        result = compute_net_result(
            total=3602.0,
            factor=1.50,
            actual_fund=9800.0,
            cushion=-5000.0,
        )
        assert result["expected_fund"] == pytest.approx(5403.0)
        assert result["over"] == pytest.approx(4397.0)
        assert result["net"] == pytest.approx(-603.0)

    """
    TC-RT-3.4: Status is 'Overfunded' when net > 0
    -------------------------------------------------
    Purpose:  Verify status determination when net result is positive.
    Setup:    total=6000, factor=1.25, actual=14000, cushion=-5000.
              expected = 7500, over = 6500, net = 1500 (> 0)
    Action:   Call compute_net_result() and check status.
    Expect:   status = "Overfunded".
    """

    def test_status_overfunded_when_net_positive(self):
        from app.api.v1.reasonableness import compute_net_result

        result = compute_net_result(
            total=6000.0,
            factor=1.25,
            actual_fund=14000.0,
            cushion=-5000.0,
        )
        assert result["net"] > 0
        assert result["status"] == "Overfunded"

    """
    TC-RT-3.5: Status is 'Reasonable' when net <= 0
    -------------------------------------------------
    Purpose:  Verify status determination when net result is zero or negative.
    Setup:    Case A: net exactly 0. Case B: net negative.
    Action:   Call compute_net_result() for each case.
    Expect:   Both return status = "Reasonable".
    """

    def test_status_reasonable_when_net_zero_or_negative(self):
        from app.api.v1.reasonableness import compute_net_result

        # Case A: net exactly 0
        # total=4000, factor=1.25, actual=10000, cushion=-5000
        # expected=5000, over=5000, net=0
        result_zero = compute_net_result(total=4000.0, factor=1.25, actual_fund=10000.0, cushion=-5000.0)
        assert result_zero["net"] == pytest.approx(0.0)
        assert result_zero["status"] == "Reasonable"

        # Case B: net negative
        # total=3602, factor=1.50, actual=9800, cushion=-5000
        # expected=5403, over=4397, net=-603
        result_neg = compute_net_result(total=3602.0, factor=1.50, actual_fund=9800.0, cushion=-5000.0)
        assert result_neg["net"] < 0
        assert result_neg["status"] == "Reasonable"

    """
    TC-RT-3.6: Default cushion is -$5,000
    ----------------------------------------
    Purpose:  Verify that when no cushion is provided, the default
              value of -5000 is used in the calculation.
    Setup:    total=4000, factor=1.25, actual=10000 (no cushion arg).
              expected=5000, over=5000, net=5000+(-5000)=0
    Action:   Call compute_net_result() without cushion parameter.
    Expect:   net = 0 (using default cushion of -5000).
    """

    def test_default_cushion(self):
        from app.api.v1.reasonableness import compute_net_result

        result = compute_net_result(total=4000.0, factor=1.25, actual_fund=10000.0)
        assert result["net"] == pytest.approx(0.0)  # over=5000 + cushion(-5000) = 0

    """
    TC-RT-3.7: compute_max_values handles empty submissions list
    -------------------------------------------------------------
    Purpose:  Verify graceful handling when no submissions exist
              for a location in the given date range.
    Setup:    Empty list of submissions.
    Action:   Call compute_max_values([]).
    Expect:   All max values are 0, actual_fund is 0, section_a_data is empty.
    """

    def test_compute_max_values_empty(self):
        from app.api.v1.reasonableness import compute_max_values

        result = compute_max_values([])
        assert result["max_f"] == 0.0
        assert result["max_h"] == 0.0
        assert result["max_j"] == 0.0
        assert result["max_k"] == 0.0
        assert result["total"] == 0.0
        assert result["actual_fund"] == 0.0
        assert result["section_a_data"] == []

    """
    TC-RT-3.8: compute_max_values extracts Section A data
    -------------------------------------------------------
    Purpose:  Verify that Section A (loose currency) daily values are
              extracted from submissions for the period comparison table.
    Setup:    3 submissions with different Section A totals and dates.
    Action:   Call compute_max_values() and check section_a_data.
    Expect:   section_a_data has 3 entries with correct date/sA pairs,
              avg_sa is the average of all sA values.
    """

    def test_compute_max_values_section_a(self):
        from app.api.v1.reasonableness import compute_max_values

        submissions = [
            {"sections": {"A": {"total": 500}, "F": {"total": 100}}, "total_cash": 5000, "submission_date": "2026-01-15"},
            {"sections": {"A": {"total": 300}, "F": {"total": 200}}, "total_cash": 4000, "submission_date": "2026-01-16"},
            {"sections": {"A": {"total": 700}, "F": {"total": 150}}, "total_cash": 6000, "submission_date": "2026-01-17"},
        ]
        result = compute_max_values(submissions)
        assert len(result["section_a_data"]) == 3
        assert result["section_a_data"][0] == {"date": "2026-01-15", "sA": 500.0}
        assert result["avg_sa"] == pytest.approx(500.0)  # (500+300+700)/3
        assert result["count"] == 3


# ===========================================================================
# PHASE 4 — API Endpoint Tests (TC-RT-4.x)
# ===========================================================================
# These tests hit the actual FastAPI endpoints via TestClient. They verify
# HTTP status codes, response shapes, role-based access, pagination,
# and audit logging. Uses conftest fixtures: client, controller_token,
# operator_token, admin_token, seed_rt_submissions.


class TestLocationGroupsEndpoint:
    """
    TC-RT-4.1: Controller gets location groups
    --------------------------------------------
    Purpose:  Verify GET /v1/reasonableness/location-groups returns locations
              grouped by cost_center, with correct sub_locs and default_factor.
    Setup:    Seed locations have cost_center values (5082 for loc-1+loc-2, etc).
              Controller has access to loc-1, loc-2, loc-3.
    Action:   GET /v1/reasonableness/location-groups with controller token.
    Expect:   200 OK. Returns array of groups. Group "5082" has 2 sub_locs
              and default_factor=1.50. Group "5104" has 1 sub_loc and factor=1.25.
    """

    def test_controller_gets_groups(self, client, controller_token):
        r = client.get(
            "/v1/reasonableness/location-groups",
            headers={"Authorization": f"Bearer {controller_token}"},
        )
        assert r.status_code == 200
        groups = r.json()
        assert isinstance(groups, list)
        assert len(groups) >= 2  # At least 5082 and 5104

        # Find the 5082 group (loc-1 + loc-2)
        grp_5082 = next((g for g in groups if g["cost_center"] == "5082"), None)
        assert grp_5082 is not None, "Should have group for cost_center 5082"
        assert len(grp_5082["sub_locs"]) == 2
        assert grp_5082["default_factor"] == 1.50  # Multiple locations

        # Find the 5104 group (loc-3 only)
        grp_5104 = next((g for g in groups if g["cost_center"] == "5104"), None)
        assert grp_5104 is not None, "Should have group for cost_center 5104"
        assert len(grp_5104["sub_locs"]) == 1
        assert grp_5104["default_factor"] == 1.25  # Single location

    """
    TC-RT-4.2: Operator is forbidden from location groups
    -------------------------------------------------------
    Purpose:  Verify operators cannot access the location groups endpoint.
    Setup:    Use operator token.
    Action:   GET /v1/reasonableness/location-groups.
    Expect:   403 Forbidden.
    """

    def test_operator_forbidden(self, client, operator_token):
        r = client.get(
            "/v1/reasonableness/location-groups",
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        assert r.status_code == 403


class TestGenerateEndpoint:
    """
    TC-RT-4.3: Generate returns correct max values from submissions
    ----------------------------------------------------------------
    Purpose:  Verify POST /v1/reasonableness/generate pulls max(F), max(H),
              max(J) and max(total_cash) from approved submissions.
    Setup:    seed_rt_submissions creates 5 approved submissions for loc-1
              with F values [800, 600, 900, 750, 700] → max=900,
              H values [2502, 2000, 2200, 2300, 2100] → max=2502,
              J values [150, 200, 100, 180, 160] → max=200,
              total_cash [9800, 8500, 10200, 9500, 9000] → max=10200.
    Action:   POST /generate with loc-1, date range Jan 15-21 2026.
    Expect:   200 OK. calculations[0] has max_f=900, max_h=2502, max_j=200,
              actual_fund=10200, total=3602.
    """

    def test_generate_max_values(self, client, controller_token, seed_rt_submissions):
        r = client.post(
            "/v1/reasonableness/generate",
            headers={"Authorization": f"Bearer {controller_token}"},
            json={
                "location_ids": ["loc-1"],
                "from_date": "2026-01-15",
                "to_date": "2026-01-21",
                "factor": 1.50,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data["calculations"]) == 1

        calc = data["calculations"][0]
        assert calc["loc_id"] == "loc-1"
        assert calc["loc_label"] == "The Grange Hotel"
        assert calc["max_f"] == 900.0
        assert calc["max_h"] == 2502.0
        assert calc["max_j"] == 200.0
        assert calc["max_k"] == 0.0
        assert calc["total"] == 3602.0  # 900 + 2502 + 200 + 0
        assert calc["actual_fund"] == 10200.0
        assert calc["count"] == 5  # 5 submissions

    """
    TC-RT-4.4: Generate with no submissions returns zeroed results
    ---------------------------------------------------------------
    Purpose:  Verify graceful handling when a location has no approved
              submissions in the requested date range.
    Setup:    loc-3 has no seeded submissions.
    Action:   POST /generate with loc-3, date range Jan 2026.
    Expect:   200 OK. calculations[0] has all zeros.
    """

    def test_generate_no_submissions(self, client, controller_token, seed_rt_submissions):
        r = client.post(
            "/v1/reasonableness/generate",
            headers={"Authorization": f"Bearer {controller_token}"},
            json={
                "location_ids": ["loc-3"],
                "from_date": "2026-01-15",
                "to_date": "2026-01-21",
                "factor": 1.25,
            },
        )
        assert r.status_code == 200
        calc = r.json()["calculations"][0]
        assert calc["max_f"] == 0.0
        assert calc["actual_fund"] == 0.0
        assert calc["total"] == 0.0

    """
    TC-RT-4.5: Generate validates from_date <= to_date
    ----------------------------------------------------
    Purpose:  Verify the endpoint rejects invalid date ranges.
    Setup:    from_date is after to_date.
    Action:   POST /generate with from_date=2026-02-28, to_date=2026-01-01.
    Expect:   422 error.
    """

    def test_generate_invalid_dates(self, client, controller_token):
        r = client.post(
            "/v1/reasonableness/generate",
            headers={"Authorization": f"Bearer {controller_token}"},
            json={
                "location_ids": ["loc-1"],
                "from_date": "2026-02-28",
                "to_date": "2026-01-01",
                "factor": 1.50,
            },
        )
        assert r.status_code == 422

    """
    TC-RT-4.6: Operator cannot generate
    --------------------------------------
    Purpose:  Verify operators are forbidden from generating reports.
    Setup:    Use operator token.
    Action:   POST /generate.
    Expect:   403 Forbidden.
    """

    def test_generate_operator_forbidden(self, client, operator_token):
        r = client.post(
            "/v1/reasonableness/generate",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "location_ids": ["loc-1"],
                "from_date": "2026-01-15",
                "to_date": "2026-01-21",
                "factor": 1.50,
            },
        )
        assert r.status_code == 403


class TestSaveAndListReports:
    """
    TC-RT-4.7: Controller saves report successfully
    --------------------------------------------------
    Purpose:  Verify POST /v1/reasonableness/reports creates a report
              and returns 201 with the saved report details.
    Setup:    Construct a complete SaveReportBody payload.
    Action:   POST /reports with controller token.
    Expect:   201 Created. Response has id, status, saved_by, timestamps.
    """

    def test_save_report(self, client, controller_token):
        r = client.post(
            "/v1/reasonableness/reports",
            headers={"Authorization": f"Bearer {controller_token}"},
            json={
                "group_key": "5082",
                "cost_center": "5082",
                "location_labels": "The Grange Hotel / Compass HQ Canteen",
                "from_date": "2026-01-15",
                "to_date": "2026-01-21",
                "factor": 1.50,
                "preparer": "Chris Controller",
                "scope": "Q2 FY2026 review",
                "status": "Reasonable",
                "location_reports": [SAMPLE_LOC_REPORT],
            },
        )
        assert r.status_code == 201
        body = r.json()
        assert "id" in body
        assert body["status"] == "Reasonable"
        assert body["preparer"] == "Chris Controller"
        assert body["created_at"] is not None

    """
    TC-RT-4.8: Saved report appears in list
    ------------------------------------------
    Purpose:  Verify that after saving, the report is returned by GET /reports.
    Setup:    Save a report with a unique location_labels, then list all.
    Action:   POST /reports, then GET /reports.
    Expect:   The saved report appears in the list items.
    """

    def test_save_then_list(self, client, controller_token):
        # Save
        client.post(
            "/v1/reasonableness/reports",
            headers={"Authorization": f"Bearer {controller_token}"},
            json={
                "group_key": "5104",
                "cost_center": "5104",
                "location_labels": "Euston Station Bistro",
                "from_date": "2026-01-01",
                "to_date": "2026-01-31",
                "factor": 1.25,
                "preparer": "Chris Controller",
                "status": "Overfunded",
                "location_reports": [SAMPLE_LOC_REPORT_OVERFUNDED],
            },
        )

        # List
        r = client.get(
            "/v1/reasonableness/reports",
            headers={"Authorization": f"Bearer {controller_token}"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1
        labels = [item["location_labels"] for item in data["items"]]
        assert "Euston Station Bistro" in labels

    """
    TC-RT-4.9: Operator cannot save reports
    ------------------------------------------
    Purpose:  Verify operators are forbidden from saving reports.
    Setup:    Use operator token.
    Action:   POST /reports.
    Expect:   403 Forbidden.
    """

    def test_save_operator_forbidden(self, client, operator_token):
        r = client.post(
            "/v1/reasonableness/reports",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "group_key": "5082",
                "cost_center": "5082",
                "location_labels": "Test",
                "from_date": "2026-01-01",
                "to_date": "2026-01-31",
                "factor": 1.50,
                "preparer": "Test",
                "status": "Reasonable",
                "location_reports": [],
            },
        )
        assert r.status_code == 403

    """
    TC-RT-4.10: Audit event is logged when report is saved
    --------------------------------------------------------
    Purpose:  Verify saving a report creates an audit trail entry.
    Setup:    Save a report, then query the audit_events table.
    Action:   POST /reports, then check DB for audit event.
    Expect:   An AuditEvent with event_type='reasonableness_report_saved'
              exists with the report's entity_id.
    """

    def test_save_creates_audit_event(self, client, controller_token):
        r = client.post(
            "/v1/reasonableness/reports",
            headers={"Authorization": f"Bearer {controller_token}"},
            json={
                "group_key": "5082",
                "cost_center": "5082",
                "location_labels": "Audit Test Report",
                "from_date": "2026-01-15",
                "to_date": "2026-01-21",
                "factor": 1.50,
                "preparer": "Chris Controller",
                "status": "Reasonable",
                "location_reports": [SAMPLE_LOC_REPORT],
            },
        )
        assert r.status_code == 201
        report_id = r.json()["id"]

        # Check audit event in DB
        from tests.conftest import TestingSessionLocal
        from app.models.audit import AuditEvent
        db = TestingSessionLocal()
        try:
            event = db.query(AuditEvent).filter(
                AuditEvent.event_type == "reasonableness_report_saved",
                AuditEvent.entity_id == report_id,
            ).first()
            assert event is not None, "Audit event should be created"
            assert event.entity_type == "reasonableness_report"
        finally:
            db.close()


class TestListAndDetailReports:
    """
    TC-RT-4.11: List reports with pagination
    -------------------------------------------
    Purpose:  Verify GET /reports returns paginated results with
              correct total, page, page_size, total_pages metadata.
    Setup:    Previous tests have saved multiple reports.
    Action:   GET /reports?page=1&page_size=2 with controller token.
    Expect:   200 OK. Response has items (max 2), total >= 2,
              page=1, page_size=2, total_pages >= 1.
    """

    def test_list_paginated(self, client, controller_token):
        r = client.get(
            "/v1/reasonableness/reports?page=1&page_size=2",
            headers={"Authorization": f"Bearer {controller_token}"},
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data["items"]) <= 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total"] >= 1
        assert data["total_pages"] >= 1

    """
    TC-RT-4.12: Filter reports by status
    ---------------------------------------
    Purpose:  Verify GET /reports?status=Overfunded returns only overfunded reports.
    Setup:    Previous tests saved both Reasonable and Overfunded reports.
    Action:   GET /reports?status=Overfunded.
    Expect:   200 OK. All items have status "Overfunded".
    """

    def test_filter_by_status(self, client, controller_token):
        r = client.get(
            "/v1/reasonableness/reports?status=Overfunded",
            headers={"Authorization": f"Bearer {controller_token}"},
        )
        assert r.status_code == 200
        data = r.json()
        for item in data["items"]:
            assert item["status"] == "Overfunded"

    """
    TC-RT-4.13: Admin can list reports
    -------------------------------------
    Purpose:  Verify admin role has access to list reports.
    Setup:    Use admin token.
    Action:   GET /reports.
    Expect:   200 OK.
    """

    def test_admin_can_list(self, client, admin_token):
        r = client.get(
            "/v1/reasonableness/reports",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert r.status_code == 200

    """
    TC-RT-4.14: Get single report by ID
    --------------------------------------
    Purpose:  Verify GET /reports/{id} returns the full report detail
              including the nested location_reports JSON.
    Setup:    Save a report, capture its ID.
    Action:   GET /reports/{id}.
    Expect:   200 OK. Response matches the saved report with all fields.
    """

    def test_get_by_id(self, client, controller_token):
        # Save first
        save_r = client.post(
            "/v1/reasonableness/reports",
            headers={"Authorization": f"Bearer {controller_token}"},
            json={
                "group_key": "5082",
                "cost_center": "5082",
                "location_labels": "Detail Test",
                "from_date": "2026-01-15",
                "to_date": "2026-01-21",
                "factor": 1.50,
                "preparer": "Chris Controller",
                "status": "Reasonable",
                "location_reports": [SAMPLE_LOC_REPORT, SAMPLE_LOC_REPORT_OVERFUNDED],
            },
        )
        report_id = save_r.json()["id"]

        # Get by ID
        r = client.get(
            f"/v1/reasonableness/reports/{report_id}",
            headers={"Authorization": f"Bearer {controller_token}"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == report_id
        assert body["location_labels"] == "Detail Test"
        assert len(body["location_reports"]) == 2
        assert body["location_reports"][0]["loc_id"] == "loc-1"

    """
    TC-RT-4.15: 404 for non-existent report
    -------------------------------------------
    Purpose:  Verify GET /reports/{id} returns 404 for unknown IDs.
    Setup:    Use a random UUID that doesn't exist.
    Action:   GET /reports/{random-uuid}.
    Expect:   404 Not Found.
    """

    def test_not_found(self, client, controller_token):
        r = client.get(
            "/v1/reasonableness/reports/nonexistent-id-12345",
            headers={"Authorization": f"Bearer {controller_token}"},
        )
        assert r.status_code == 404
