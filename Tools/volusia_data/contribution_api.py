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
from datetime import datetime, timezone
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
API_KEYS = {}  # In production, this would be in a database or auth service


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

    contribution_type = body.get("contribution_type", "direct")
    content = body.get("content", body)  # Accept full body if no content wrapper
    idempotency_key = body.get("idempotency_key")

    # Validate contribution type
    valid_types = ["data_source", "analysis", "tool", "map", "report", "community", "social_media", "educational", "direct"]
    if contribution_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid contribution_type. Must be one of: {valid_types}")

    # Generate submission ID
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    submission_id = f"SUB-{contribution_type.upper()}-{ts}"

    # Store submission
    conn = _db()
    try:
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

        now = _now()
        conn.execute("""
            INSERT INTO submissions (submission_id, contribution_type, content, status, submitted_at, idempotency_key)
            VALUES (?, ?, ?, 'queued', ?, ?)
        """, (submission_id, contribution_type, json.dumps(content), now, idempotency_key))
        conn.commit()

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e) and idempotency_key:
            # Return existing submission for idempotent retry
            row = conn.execute("SELECT * FROM submissions WHERE idempotency_key = ?", (idempotency_key,)).fetchone()
            if row:
                return JSONResponse(status_code=200, content={
                    "submission_id": row["submission_id"],
                    "status": row["status"],
                    "message": "Submission already exists (idempotent retry acknowledged)"
                })
        raise HTTPException(status_code=409, detail="Duplicate submission")
    finally:
        conn.close()

    return JSONResponse(status_code=201, content={
        "submission_id": submission_id,
        "status": "queued",
        "submitted_at": now,
        "estimated_review_by": "5 business days from acknowledgment",
        "message": "Contribution received. You will receive an update within 5 business days."
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


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("VOLUSIA_CONTRIBUTION_PORT", "8790"))
    uvicorn.run(app, host="127.0.0.1", port=port)
