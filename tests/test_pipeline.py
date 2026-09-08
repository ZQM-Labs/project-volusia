"""Project Volusia — data pipeline tests."""

import sqlite3
from pathlib import Path

import pytest


def test_database_schema():
    """Verify database has required tables."""
    db_path = Path(__file__).parent.parent / "Tools" / "volusia_data" / "volusia.db"

    # Database may not exist in CI, so skip if missing
    if not db_path.exists():
        pytest.skip("Database not present")

    with sqlite3.connect(db_path) as conn:
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

    assert "indicators" in tables
    assert "datasets" in tables
    assert "audit_log" in tables


def test_indicator_columns():
    """Verify indicators table schema."""
    db_path = Path(__file__).parent.parent / "Tools" / "volusia_data" / "volusia.db"

    if not db_path.exists():
        pytest.skip("Database not present")

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA table_info(indicators)").fetchone()

    expected_cols = {"name", "value", "unit", "source", "vintage", "fetched_at"}
    actual_cols = {row[1] for row in conn.execute("PRAGMA table_info(indicators)").fetchall()}

    assert expected_cols.issubset(actual_cols)


def test_watchdog_script_runs():
    """Verify watchdog script executes without crash."""
    import subprocess

    result = subprocess.run(
        ["python", "-m", "volusia_data.watchdog_monitoring"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
        timeout=30,
    )
    # Exit 0 = healthy, 1 = stale data, both are valid outcomes
    assert result.returncode in {0, 1}


def test_refresh_pipeline_imports():
    """Verify refresh pipeline can be imported."""
    import sys

    tools_path = Path(__file__).parent.parent / "Tools"
    if str(tools_path) not in sys.path:
        sys.path.insert(0, str(tools_path))

    from volusia_data import refresh_v2

    assert hasattr(refresh_v2, "main")
    assert hasattr(refresh_v2, "fetch_census_pep")


def test_portal_app_health():
    """FastAPI health endpoint returns correct shape."""
    from fastapi.testclient import TestClient
    import sys

    tools_path = Path(__file__).parent.parent / "Tools"
    if str(tools_path) not in sys.path:
        sys.path.insert(0, str(tools_path))

    from volusia_data.portal_app import app

    client = TestClient(app)
    r = client.get("/api/health")

    assert r.status_code == 200
    data = r.json()
    assert data["status"] in {"healthy", "degraded"}
    assert "indicator_count" in data
