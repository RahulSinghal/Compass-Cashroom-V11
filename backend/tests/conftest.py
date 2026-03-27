"""
Shared test fixtures for all milestones.
Uses a separate test.db SQLite file, seeded with demo users and locations.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.location import Location
from app.models.config import SystemConfig
from app.models.reasonableness import ReasonablenessReport  # noqa: F401 — registers model with Base
from app.core.security import hash_password

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

DEMO_PASSWORD = "demo1234"

SEED_USERS = [
    {"email": "operator@compass.com",   "name": "Alex Operator",   "role": UserRole.OPERATOR,            "location_ids": ["loc-1"]},
    {"email": "controller@compass.com", "name": "Chris Controller", "role": UserRole.CONTROLLER,          "location_ids": ["loc-1", "loc-2", "loc-3"]},
    {"email": "dgm@compass.com",        "name": "Diana DGM",        "role": UserRole.DGM,                 "location_ids": []},
    {"email": "admin@compass.com",      "name": "Adam Admin",       "role": UserRole.ADMIN,               "location_ids": []},
    {"email": "auditor@compass.com",    "name": "Audrey Auditor",   "role": UserRole.AUDITOR,             "location_ids": []},
    {"email": "rc@compass.com",         "name": "Rachel RC",        "role": UserRole.REGIONAL_CONTROLLER, "location_ids": []},
]

SEED_LOCATIONS = [
    {"id": "loc-1", "name": "The Grange Hotel",      "city": "London",   "address": "Grange Road, London",    "cost_center": "5082", "expected_cash": 9800.0},
    {"id": "loc-2", "name": "Compass HQ Canteen",    "city": "Chertsey", "address": "Compass Centre, Chertsey", "cost_center": "5082", "expected_cash": 8500.0},
    {"id": "loc-3", "name": "Euston Station Bistro", "city": "London",   "address": "Euston Station, London", "cost_center": "5104", "expected_cash": 5600.0},
    {"id": "loc-4", "name": "Heathrow T2 Outlet",    "city": "Hounslow", "address": "Heathrow Terminal 2",    "cost_center": "5117", "expected_cash": 19200.0},
    {"id": "loc-5", "name": "Leeds Arena Kitchen",   "city": "Leeds",    "address": "Arena Quarter, Leeds",   "cost_center": "5132", "expected_cash": 3700.0},
]


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create tables and seed demo data once for the whole test session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        for u in SEED_USERS:
            if not db.query(User).filter(User.email == u["email"]).first():
                db.add(User(
                    email=u["email"],
                    name=u["name"],
                    role=u["role"],
                    hashed_password=hash_password(DEMO_PASSWORD),
                    location_ids=u["location_ids"],
                    active=True,
                ))
        for l in SEED_LOCATIONS:
            if not db.get(Location, l["id"]):
                db.add(Location(
                    id=l["id"], name=l["name"], city=l["city"], address=l["address"],
                    cost_center=l.get("cost_center"), expected_cash=l.get("expected_cash", 0.0),
                ))
        if not db.get(SystemConfig, 1):
            db.add(SystemConfig(id=1))
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client(setup_db):
    """FastAPI TestClient wired to the test DB."""
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def admin_token(client):
    r = client.post("/v1/auth/login", json={"email": "admin@compass.com", "password": DEMO_PASSWORD})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def operator_token(client):
    r = client.post("/v1/auth/login", json={"email": "operator@compass.com", "password": DEMO_PASSWORD})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def controller_token(client):
    r = client.post("/v1/auth/login", json={"email": "controller@compass.com", "password": DEMO_PASSWORD})
    assert r.status_code == 200
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def seed_rt_submissions(setup_db):
    """
    Seed approved submissions with section F/H/J/A data for reasonableness tests.
    Creates 5 submissions per location (loc-1, loc-2) across Jan 2026.
    """
    from app.models.submission import Submission, SubmissionStatus, SubmissionSource
    from datetime import datetime, timezone

    db = TestingSessionLocal()
    try:
        # Check if already seeded
        existing = db.query(Submission).filter(
            Submission.submission_date == "2026-01-15",
            Submission.location_id == "loc-1",
            Submission.status == SubmissionStatus.APPROVED,
        ).first()
        if existing:
            return  # Already seeded

        operator = db.query(User).filter(User.email == "operator@compass.com").first()

        # loc-1 submissions: varying F, H, J values
        loc1_data = [
            ("2026-01-15", {"A": {"total": 500}, "F": {"total": 800},  "H": {"total": 2502}, "J": {"total": 150}}, 9800),
            ("2026-01-16", {"A": {"total": 450}, "F": {"total": 600},  "H": {"total": 2000}, "J": {"total": 200}}, 8500),
            ("2026-01-17", {"A": {"total": 600}, "F": {"total": 900},  "H": {"total": 2200}, "J": {"total": 100}}, 10200),
            ("2026-01-20", {"A": {"total": 520}, "F": {"total": 750},  "H": {"total": 2300}, "J": {"total": 180}}, 9500),
            ("2026-01-21", {"A": {"total": 480}, "F": {"total": 700},  "H": {"total": 2100}, "J": {"total": 160}}, 9000),
        ]

        # loc-2 submissions
        loc2_data = [
            ("2026-01-15", {"A": {"total": 300}, "F": {"total": 400},  "H": {"total": 1800}, "J": {"total": 250}}, 7500),
            ("2026-01-16", {"A": {"total": 350}, "F": {"total": 500},  "H": {"total": 2000}, "J": {"total": 300}}, 8000),
            ("2026-01-17", {"A": {"total": 280}, "F": {"total": 450},  "H": {"total": 1900}, "J": {"total": 200}}, 7800),
            ("2026-01-20", {"A": {"total": 320}, "F": {"total": 380},  "H": {"total": 1700}, "J": {"total": 220}}, 7200),
            ("2026-01-21", {"A": {"total": 340}, "F": {"total": 420},  "H": {"total": 1850}, "J": {"total": 280}}, 7600),
        ]

        for loc_id, data_list in [("loc-1", loc1_data), ("loc-2", loc2_data)]:
            for sub_date, sections, total_cash in data_list:
                db.add(Submission(
                    id=str(uuid.uuid4()),
                    location_id=loc_id,
                    location_name="Test Location",
                    operator_id=operator.id,
                    operator_name=operator.name,
                    submission_date=sub_date,
                    status=SubmissionStatus.APPROVED,
                    source=SubmissionSource.FORM,
                    sections=sections,
                    total_cash=total_cash,
                    expected_cash=9800.0,
                    variance=total_cash - 9800.0,
                    variance_pct=0.0,
                    submitted_at=datetime.now(timezone.utc),
                ))
        db.commit()
    finally:
        db.close()
