"""Project Volusia — contribution API tests.

Exercises the lightweight contribution API (Tools/volusia_data/contribution_api.py)
via the TestClient. Every test runs against an isolated SQLite file in tmp_path —
the real volusia.db is never opened. Assertions target the stable public contract
documented in openapi.yaml (submit / idempotency / status / list / PATCH), not
incidental implementation details, so the suite survives light refactors.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TOOLS = Path(__file__).resolve().parent.parent / "Tools"
sys.path.insert(0, str(TOOLS))

from volusia_data import contribution_api as capi  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """TestClient bound to a throwaway database for this test only."""
    monkeypatch.setattr(capi, "DB_PATH", tmp_path / "contributions-test.db")
    return TestClient(capi.app)


def _payload(**overrides):
    body = {
        "contribution_type": "data_source",
        "content": "Volusia County parcel data source (test submission)",
        "author_name": "CI Test",
        "author_email": "",
    }
    body.update(overrides)
    return body


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_root_metadata(client):
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "Contribution API" in data["name"]
    assert "submit" in data["endpoints"]


def test_submit_returns_201_with_tracking_fields(client):
    r = client.post("/api/v1/contributions", json=_payload())
    assert r.status_code == 201
    data = r.json()
    assert data["submission_id"].startswith("SUB-")
    assert data["status"] == "queued"
    assert data["acknowledged_at"]
    assert data["estimated_review_by"]
    assert data["anonymous"] is True  # no author_email given


def test_submit_with_email_is_not_anonymous(client):
    r = client.post("/api/v1/contributions", json=_payload(author_email="a@b.example"))
    assert r.status_code == 201
    assert r.json()["anonymous"] is False


def test_submit_rejects_empty_content(client):
    r = client.post("/api/v1/contributions", json=_payload(content="   "))
    assert r.status_code == 400


def test_submit_rejects_invalid_contribution_type(client):
    r = client.post("/api/v1/contributions", json=_payload(contribution_type="bogus"))
    assert r.status_code == 400


def test_idempotent_retry_returns_existing_submission(client):
    key = "retry-check-001"
    first = client.post("/api/v1/contributions", json=_payload(idempotency_key=key))
    assert first.status_code == 201
    second = client.post("/api/v1/contributions", json=_payload(idempotency_key=key))
    assert second.status_code == 200
    assert second.json()["submission_id"] == first.json()["submission_id"]


def test_get_submission_status(client):
    sid = client.post("/api/v1/contributions", json=_payload()).json()["submission_id"]
    r = client.get(f"/api/v1/contributions/{sid}")
    assert r.status_code == 200
    assert r.json()["contribution_type"] == "data_source"
    assert client.get("/api/v1/contributions/SUB-DOES-NOT-EXIST").status_code == 404


def test_list_submissions(client):
    client.post("/api/v1/contributions", json=_payload())
    r = client.get("/api/v1/contributions")
    assert r.status_code == 200
    assert r.json()["count"] >= 1
    assert len(r.json()["submissions"]) == r.json()["count"]


def test_patch_updates_status(client):
    sid = client.post("/api/v1/contributions", json=_payload()).json()["submission_id"]
    ok = client.patch(
        f"/api/v1/contributions/{sid}",
        json={"status": "approved", "reviewer": "CI"},
    )
    assert ok.status_code == 200
    assert ok.json()["status"] == "approved"
    assert client.get(f"/api/v1/contributions/{sid}").json()["status"] == "approved"
    bad = client.patch(f"/api/v1/contributions/{sid}", json={"status": "bogus"})
    assert bad.status_code == 400
    missing = client.patch("/api/v1/contributions/SUB-MISSING", json={"status": "approved"})
    assert missing.status_code == 404


def test_invalid_api_key_rejected_valid_key_accepted(client, monkeypatch):
    monkeypatch.setattr(capi, "ALLOWED_API_KEYS", {"ci-secret"})
    wrong = client.post(
        "/api/v1/contributions",
        headers={"X-API-Key": "wrong-key"},
        json=_payload(),
    )
    assert wrong.status_code == 401
    right = client.post(
        "/api/v1/contributions",
        headers={"X-API-Key": "ci-secret"},
        json=_payload(),
    )
    assert right.status_code == 201
