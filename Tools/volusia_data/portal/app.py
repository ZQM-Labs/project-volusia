"""
Project Volusia — FastAPI Portal
Serves HTML dashboard + JSON APIs from SQLite.
Run: python -m volusia_data.portal.app
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

app = FastAPI(title="Project Volusia — Open Data Portal")

# DB path: use env var or default to local
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
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    if not rows:
        return "<html><body><h1>Project Volusia</h1><p>No data loaded yet. Run refresh_v2.py first.</p></body></html>"

    categories = {}
    fetched_times = []
    for row in rows:
        cat = row.get("category") or "Uncategorized"
        categories.setdefault(cat, []).append(row)
        ft = row.get("updated_at") or row.get("fetched_at")
        if ft:
            fetched_times.append(ft)
    latest_updated = sorted(fetched_times)[-1] if fetched_times else "unknown"

    html_parts = [
        "<html><head><title>Project Volusia — Open Data Portal</title>",
        "<style>body{font-family:sans-serif;margin:20px;} table{border-collapse:collapse;width:100%;margin:10px 0;} th,td{border:1px solid #ddd;padding:8px;text-align:left;} th{background:#f4f4f4;} .category{margin-top:20px;font-size:1.2em;font-weight:bold;}</style>",
        "</head><body>",
        "<h1>Project Volusia — Open Data Portal</h1>",
        f"<p>Last updated: {rows[0].get('fetched_at', 'N/A') if rows else 'N/A'}</p>",
    ]

    for cat, items in sorted(categories.items()):
        html_parts.append(f'<div class="category">{cat}</div>')
        html_parts.append('<table><tr><th>Indicator</th><th>Value</th><th>Unit</th><th>Vintage</th><th>Source</th></tr>')
        for item in items:
            html_parts.append(
                f'<tr><td>{item.get("name", "")}</td>'
                f'<td>{item.get("value", "")}</td>'
                f'<td>{item.get("unit", "")}</td>'
                f'<td>{item.get("vintage", "")}</td>'
                f'<td>{item.get("source", "")}</td></tr>'
            )
        html_parts.append('</table>')

    html_parts.append('</body></html>')
    footer = (
        "<div class=\"footer\">"
        f"<p>Project Volusia · ZQM Labs · Last updated: {latest_updated or 'unknown'}"
        " · Refresh cadence: manual · SLA target: daily by 06:00 UTC"
        " · <a href=\"/api/status\">Status API</a> · <a href=\"/api/health\">Health</a></p>"
        "</div>"
    )
    html_parts.append(footer)
    return "".join(html_parts)


@app.get("/api/indicators")
def api_indicators():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    return {"count": len(rows), "indicators": rows}


@app.get("/api/datasets")
def api_datasets():
    rows = _db_rows("SELECT id, source, content, fetched_at FROM datasets ORDER BY id DESC LIMIT 50")
    return {"count": len(rows), "datasets": rows}


@app.get("/api/status")
def api_status():
    indicators = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    datasets = _db_rows("SELECT id, source, content, fetched_at FROM datasets ORDER BY id DESC LIMIT 20")
    latest_updated = None
    if indicators:
        fetched = [i.get("updated_at") or i.get("fetched_at") for i in indicators if i.get("updated_at") or i.get("fetched_at")]
        latest_updated = sorted(fetched)[-1] if fetched else None
    return {
        "service": "Project Volusia Portal",
        "version": "0.3.0",
        "status": "ok" if indicators else "degraded",
        "indicator_count": len(indicators),
        "dataset_count": len(datasets),
        "latest_updated": latest_updated,
        "refresh_cadence": "manual — run refresh_v2.py",
        "sla_target": "daily refresh by 06:00 UTC",
        "indicators": indicators,
        "recent_datasets": datasets,
    }


@app.get("/api/health")
def api_health():
    db_exists = DB_PATH.exists()
    indicator_count = 0
    if db_exists:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            indicator_count = conn.execute("SELECT COUNT(*) FROM indicators").fetchone()[0]
        finally:
            conn.close()
    return {
        "status": "healthy" if db_exists and indicator_count > 0 else "degraded",
        "db_exists": db_exists,
        "db_path": str(DB_PATH),
        "indicator_count": indicator_count,
    }


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("VOLUSIA_PORTAL_HOST", "127.0.0.1")
    port = int(os.environ.get("VOLUSIA_PORTAL_PORT", "8789"))
    uvicorn.run(app, host=host, port=port)
