#!/usr/bin/env python3
"""
Project Volusia — Contribution Submission API
Accepts contributions from web forms, SMS, and agents.
Routes them to the appropriate CGB member for review.

Run: python contribution_api.py
"""
import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse

# Add Tools dir to path
TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

app = FastAPI(title="Project Volusia — Contribution API")

DB_PATH = Path(os.environ.get("VOLUSIA_DB_PATH", str(Path(__file__).resolve().parent / "volusia.db")))
# ── Optional API-key enforcement ────────────────────────────────────────────
# Set VOLUSIA_API_KEYS (comma-separated) to require a key. Without it,
# anonymous submissions are allowed — required by the community web form
# (WEB_FORM_DESIGN.md: "no login required for anonymous submissions").
ALLOWED_API_KEYS = {k.strip() for k in os.environ.get("VOLUSIA_API_KEYS", "").split(",") if k.strip()}

# Valid contribution types (aligned with openapi.yaml)
VALID_CONTRIBUTION_TYPES = ["data_source", "analysis", "tool", "map", "report", "community", "social_media", "educational", "direct"]


def add_business_days(start: datetime, days: int) -> datetime:
    """Advance `start` by `days` business days (Mon–Fri)."""
    cur, d = 0, start
    while cur < days:
        d += timedelta(days=1)
        if d.weekday() < 5:
            cur += 1
    return d


def check_api_key(request: Request):
    """Validate an optional API key (X-API-Key or Bearer). Returns the key or None."""
    auth = request.headers.get("Authorization", "")
    bearer = auth[7:].strip() if auth[:7].lower() == "bearer " else ""
    cred = request.headers.get("X-API-Key") or bearer
    if cred and cred not in ALLOWED_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return cred or None
# Keys are read from the VOLUSIA_API_KEYS env var (see ALLOWED_API_KEYS above).


def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _now():
    return datetime.now(timezone.utc).isoformat()


@app.post("/api/v1/contributions")
async def submit_contribution(request: Request):
    """
    Submit a new contribution to the knowledge system.
    Accepts contributions from web forms, SMS, and agents.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    check_api_key(request)

    contribution_type = body.get("contribution_type", "direct")
    content = body.get("content", body)  # accept full body when no content wrapper (may be None)
    idempotency_key = body.get("idempotency_key")

    # Validate contribution type
    if contribution_type not in VALID_CONTRIBUTION_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid contribution_type. Must be one of: {VALID_CONTRIBUTION_TYPES}")

    # Validate content is present and meaningful
    empty = content is None or (
        isinstance(content, str) and not content.strip()
    ) or (
        isinstance(content, (dict, list)) and len(content) == 0
    )
    if empty:
        raise HTTPException(status_code=400, detail="Content is required and must be non-empty")

    # Generate submission ID
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    submission_id = f"SUB-{contribution_type.upper()}-{ts}"

    # Store submission
    conn = _db()
    try:
        # Ensure the submissions table exists (first run / fresh DB).
        conn.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id TEXT UNIQUE,
                contribution_type TEXT,
                content TEXT,
                status TEXT DEFAULT 'queued',
                submitted_at TEXT,
                acknowledged_at TEXT,
                decision TEXT,
                reviewer TEXT,
                idempotency_key TEXT
            )
        """)
        conn.commit()

        # Idempotent retry: same key returns the existing submission (200).
        if idempotency_key:
            existing = conn.execute(
                "SELECT * FROM submissions WHERE idempotency_key = ? ORDER BY submitted_at DESC LIMIT 1",
                (idempotency_key,),
            ).fetchone()
            if existing:
                return JSONResponse(status_code=200, content={
                    "submission_id": existing["submission_id"],
                    "status": existing["status"],
                    "message": "Submission already exists (idempotent retry acknowledged)",
                })

        now = _now()
        conn.execute("""
            INSERT INTO submissions (submission_id, contribution_type, content, status, submitted_at, acknowledged_at, idempotency_key)
            VALUES (?, ?, ?, 'queued', ?, ?, ?)
        """, (submission_id, contribution_type, json.dumps(content), now, now, idempotency_key))
        conn.commit()

    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Duplicate submission: {e}")
    finally:
        conn.close()

    review_by = add_business_days(datetime.now(timezone.utc), 5)

    return JSONResponse(status_code=201, content={
        "submission_id": submission_id,
        "status": "queued",
        "submitted_at": now,
        "acknowledged_at": now,
        "estimated_review_by": review_by.isoformat(),
        "anonymous": True,
        "message": "Contribution received. You will receive an update within 5 business days.",
    })


@app.get("/api/v1/contributions/{submission_id}")
async def get_contribution(submission_id: str):
    """Get the status of a submission."""
    conn = _db()
    try:
        row = conn.execute("SELECT * FROM submissions WHERE submission_id = ?", (submission_id,)).fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Submission not found")

    return {
        "submission_id": row["submission_id"],
        "contribution_type": row["contribution_type"],
        "status": row["status"],
        "submitted_at": row["submitted_at"],
        "acknowledged_at": row["acknowledged_at"],
        "decision": row["decision"],
        "reviewer": row["reviewer"],
    }


@app.get("/api/v1/contributions")
async def list_contributions(limit: int = 50, offset: int = 0):
    """List recent submissions (for CGB triage)."""
    conn = _db()
    try:
        rows = conn.execute(
            "SELECT * FROM submissions ORDER BY submitted_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
    finally:
        conn.close()

    return {
        "count": len(rows),
        "submissions": [
            {
                "submission_id": r["submission_id"],
                "contribution_type": r["contribution_type"],
                "status": r["status"],
                "submitted_at": r["submitted_at"],
            }
            for r in rows
        ]
    }


@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "timestamp": _now()}


@app.get("/")
async def root():
    """Service metadata and endpoint index."""
    return {
        "name": "Project Volusia — Contribution API",
        "version": "2026-09-03",
        "anonymous_submissions": not bool(ALLOWED_API_KEYS),
        "endpoints": {
            "submit": "POST /api/v1/contributions",
            "status": "GET /api/v1/contributions/{submission_id}",
            "list": "GET /api/v1/contributions",
            "health": "GET /api/v1/health",
            "swagger": "/docs",
        },
        "spec": "See openapi.yaml in repo root",
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("VOLUSIA_CONTRIBUTION_PORT", "8790"))
    uvicorn.run(app, host="127.0.0.1", port=port)
