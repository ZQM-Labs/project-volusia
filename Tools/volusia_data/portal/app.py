"""
Project Volusia — Legacy Portal (DEPRECATED)

This file is deprecated. Use Tools/volusia_data/portal_app.py instead.
The new portal includes coherence groups, SLA footer, export endpoints,
chart generation, and contribution form mounting.

This file is kept for reference only. It will be removed in a future release.
"""

import os
import sys
import sqlite3
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Add Tools dir to path so volusia_data is importable
TOOLS_DIR = Path(__file__).resolve().parents[2]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

app = FastAPI(title="Project Volusia — Open Data Portal (DEPRECATED)")

DB_PATH = Path(os.environ.get("VOLUSIA_DB_PATH", str(Path(__file__).resolve().parents[1] / "volusia.db")))


def _db_rows(query, params=()):
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(query, params)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


@app.get("/", response_class=HTMLResponse)
def index():
    return """<html><body>
    <h1>Project Volusia — DEPRECATED PORTAL</h1>
    <p>This portal version is deprecated. Please use the new portal at 
    <code>python Tools/volusia_data/portal_app.py</code></p>
    <p>The new portal includes coherence groups, SLA footer, export endpoints, 
    chart generation, and contribution form mounting.</p>
    </body></html>"""


@app.get("/api/indicators")
def api_indicators():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    return {"count": len(rows), "indicators": rows, "deprecated": True}


@app.get("/api/health")
def api_health():
    return {"status": "deprecated", "message": "Use Tools/volusia_data/portal_app.py"}


if __name__ == "__main__":
    import uvicorn
    print("WARNING: Running deprecated portal. Use Tools/volusia_data/portal_app.py instead.")
    uvicorn.run(app, host="127.0.0.1", port=8789)
