"""Tests for the contribution front-end (portal_contribute.py).

Covers the WEB_FORM_DESIGN.md URL surface: landing pages, form pages,
form submission (via the TestClient fallback path), status lookup, and
EN/ES parity. The contribution API is owned by another writer (in-flight
edits all session) — tests import it but never modify it.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "Tools"))

from volusia_data import portal_contribute as pc  # noqa: E402


@pytest.fixture()
def client(monkeypatch, tmp_path):
    """Isolated TestClient: temp DB + force fallback (no HTTP server in CI)."""
    # contribution_api reads DB_PATH at call time → monkeypatch works even
    # if the module initialized before the test.
    monkeypatch.setattr(
        "volusia_data.contribution_api.DB_PATH", tmp_path / "test.db"
    )
    # Force the in-process fallback (nothing listens on :0).
    monkeypatch.setattr(pc, "API_BASE_URL", "http://127.0.0.1:0")
    return TestClient(pc.app)


# ----------------------------------------------------------------- landing
def test_landing_en(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Project Volusia" in resp.text


def test_landing_es(client):
    resp = client.get("/es")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Inicio" in resp.text


# ----------------------------------------------------------------- form pages
def test_form_f_en(client):
    resp = client.get("/f")
    assert resp.status_code == 200
    assert "Share knowledge" in resp.text
    assert "<form" in resp.text


def test_form_f_es(client):
    resp = client.get("/es/f")
    assert resp.status_code == 200
    assert "Compartir conocimiento" in resp.text


def test_form_i_en(client):
    resp = client.get("/i")
    assert resp.status_code == 200
    assert "Share a thought" in resp.text


def test_form_i_es(client):
    resp = client.get("/es/i")
    assert resp.status_code == 200
    assert "Compartir una idea" in resp.text


# ----------------------------------------------------------------- submission
def test_submit_f_success(client):
    resp = client.post("/f", data={
        "content": "Test knowledge share",
        "basis": "My experience",
        "author_name": "Test User",
        "author_email": "test@example.com",
    })
    assert resp.status_code == 200
    # Success page shows the reference number
    assert "reference" in resp.text.lower() or "submitted" in resp.text.lower()


def test_submit_i_success(client):
    resp = client.post("/i", data={
        "content": "A thought",
        "author_name": "Thinker",
    })
    assert resp.status_code == 200
    assert "reference" in resp.text.lower() or "submitted" in resp.text.lower()


def test_submit_empty_content_errors(client):
    resp = client.post("/f", data={"content": ""})
    assert resp.status_code == 200
    # Error path re-renders the form (never a success page)
    assert "<form" in resp.text


# ----------------------------------------------------------------- status
def test_status_empty(client):
    resp = client.get("/status")
    assert resp.status_code == 200
    assert "Submission ID" in resp.text


def test_status_with_unknown_id(client):
    resp = client.get("/status?id=nonexistent-id-12345")
    assert resp.status_code == 200
    # Unknown ID → form re-rendered, no result block
    assert "Submission ID" in resp.text


def test_status_es(client):
    resp = client.get("/es/status")
    assert resp.status_code == 200
    assert "Consultar estado" in resp.text


# ----------------------------------------------------------------- round-trip
def test_submit_then_status(client):
    """Submit a contribution, then look up its reference on the status page."""
    # Submit
    submit_resp = client.post("/i", data={
        "content": "Round-trip test thought",
        "author_name": "Tester",
    })
    assert submit_resp.status_code == 200
    # Extract reference from the success page (it appears in a <code> block)
    import re
    match = re.search(r"<code>([a-f0-9-]{36})</code>", submit_resp.text)
    assert match, "expected a submission_id reference in <code> block"
    ref = match.group(1)

    # Look it up
    status_resp = client.get(f"/status?id={ref}")
    assert status_resp.status_code == 200
    assert ref in status_resp.text
    assert "received" in status_resp.text.lower() or "submitted" in status_resp.text.lower()
