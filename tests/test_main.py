"""Project Volusia — Backend Test Suite v3.0
Tests for API endpoints, database integrity, and gamification system.
"""
import pytest
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "volusia.db"


@pytest.fixture
def db_conn():
    """Get a test database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def test_db_exists():
    """Database file exists."""
    assert DB_PATH.exists(), f"Database not found at {DB_PATH}"


def test_indicators_table(db_conn):
    """Indicators table has data."""
    count = db_conn.execute("SELECT COUNT(*) FROM indicators").fetchone()[0]
    assert count > 0, "No indicators found in database"


def test_indicators_with_values(db_conn):
    """Some indicators have non-null values."""
    count = db_conn.execute(
        "SELECT COUNT(*) FROM indicators WHERE value IS NOT NULL"
    ).fetchone()[0]
    assert count > 0, "No indicators with values found"


def test_categories(db_conn):
    """Expected categories present."""
    categories = set(
        row[0] for row in db_conn.execute(
            "SELECT DISTINCT category FROM indicators"
        ).fetchall()
    )
    expected = {"Climate", "Demographics", "Economic", "Tourism", "Education",
                "Environment", "Government", "Health", "Housing", "Safety",
                "Transportation"}
    missing = expected - categories
    assert not missing, f"Missing categories: {missing}"


def test_gamification_tables(db_conn):
    """Gamification tables exist."""
    tables = set(
        row[0] for row in db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'gam%'"
        ).fetchall()
    )
    assert "gamification" in tables, "gamification table missing"
    assert "leaderboard" in tables, "leaderboard table missing"


def test_health_endpoint(client):
    """Health endpoint returns valid response."""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "indicator_count" in data


def test_indicators_endpoint(client):
    """Indicators endpoint returns valid response."""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    response = client.get("/indicators")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "indicators" in data


def test_latest_endpoint(client):
    """Latest endpoint returns recent data."""
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    response = client.get("/latest")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data