"""Project Volusia — portal smoke tests.

These tests exercise the FastAPI portal (Tools/volusia_data/portal_app.py)
end-to-end via the TestClient. They are intentionally tolerant of an empty
database (CI runners do not run the data pipeline), asserting HTTP correctness
and response shape rather than exact indicator counts.
"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

TOOLS = Path(__file__).resolve().parent.parent / "Tools"
sys.path.insert(0, str(TOOLS))

from volusia_data.portal_app import app  # noqa: E402

client = TestClient(app)


def test_homepage():
    r = client.get("/")
    assert r.status_code == 200
    assert "Project Volusia" in r.text


def test_indicators():
    r = client.get("/api/indicators")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 0
    assert isinstance(data["indicators"], list)


def test_export_csv():
    r = client.get("/api/export/csv")
    assert r.status_code == 200
    if r.headers.get("content-type", "").startswith("text/csv"):
        assert r.text.splitlines()[0].startswith("id,name")


def test_export_json():
    r = client.get("/api/export/json")
    assert r.status_code == 200
    assert "exported_at" in r.json()


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] in {"healthy", "degraded"}


def test_status():
    r = client.get("/api/status")
    assert r.status_code == 200
    assert "sla" in r.json()


def test_datasets():
    client.get("/api/datasets")


def test_indicators_pagination():
    """Verify pagination parameters work correctly."""
    r = client.get("/api/indicators?limit=5&offset=0")
    assert r.status_code == 200
    data = r.json()
    assert "limit" in data
    assert "offset" in data
    assert "has_more" in data
    assert data["limit"] == 5
    assert data["offset"] == 0


def test_indicators_pagination_offset():
    """Verify offset skips results correctly."""
    r1 = client.get("/api/indicators?limit=2&offset=0")
    r2 = client.get("/api/indicators?limit=2&offset=2")
    assert r1.status_code == 200
    assert r2.status_code == 200
    data1 = r1.json()
    data2 = r2.json()
    # If there are enough indicators, the results should differ
    if data1["indicators"] and data2["indicators"]:
        assert data1["indicators"][0]["name"] != data2["indicators"][0]["name"]


def test_indicators_default_limit():
    """Verify default limit is 50 (not 100)."""
    r = client.get("/api/indicators")
    assert r.status_code == 200
    data = r.json()
    assert data["limit"] == 50

    assert r.status_code == 200
