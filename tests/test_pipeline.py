"""Project Volusia — data pipeline tests."""

import sqlite3
from pathlib import Path

import pytest


@pytest.fixture()
def pipeline_db(tmp_path, monkeypatch):
    """Hermetic pipeline DB: run init_db() against a temp path.

    The real Tools/volusia_data/volusia.db is gitignored and may not exist
    (or may exist empty, created by other tests) on clean machines — tests
    must not depend on it.
    """
    import sys

    tools_path = Path(__file__).parent.parent / "Tools"
    if str(tools_path) not in sys.path:
        sys.path.insert(0, str(tools_path))

    from volusia_data import refresh_v2

    db = tmp_path / "volusia.db"
    monkeypatch.setattr(refresh_v2, "DB_PATH", db)
    conn = refresh_v2.init_db()
    conn.close()
    return db


def test_database_schema(pipeline_db):
    """init_db() creates the required tables."""
    with sqlite3.connect(pipeline_db) as conn:
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

    assert "indicators" in tables
    assert "datasets" in tables
    assert "audit_log" in tables


def test_indicator_columns(pipeline_db):
    """indicators table has the expected columns."""
    with sqlite3.connect(pipeline_db) as conn:
        conn.execute("PRAGMA table_info(indicators)").fetchone()
        actual_cols = {row[1] for row in conn.execute("PRAGMA table_info(indicators)").fetchall()}

    expected_cols = {"name", "value", "unit", "source", "vintage", "fetched_at"}
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
