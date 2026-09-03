#!/usr/bin/env python3
"""
Project Volusia — Standalone Portal
Serves HTML dashboard + JSON APIs from SQLite.
Run: python portal_app.py
"""
import os
import sqlite3
import csv
import io
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, StreamingResponse

app = FastAPI(title="Project Volusia — Open Data Portal")

# DB path: use env var or default to local
DB_PATH = Path(os.environ.get("VOLUSIA_DB_PATH", str(Path(__file__).resolve().parent / "volusia.db")))

CSS_STYLE = """<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.6; }
.header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); color: white; padding: 2rem; text-align: center; }
.header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
.header p { opacity: 0.9; font-size: 0.95rem; }
.stats { display: flex; justify-content: center; gap: 2rem; padding: 1.5rem; background: white; border-bottom: 1px solid #e2e8f0; flex-wrap: wrap; }
.stat { text-align: center; }
.stat-value { font-size: 1.5rem; font-weight: bold; color: #0f172a; }
.stat-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; }
.container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
.category { margin-bottom: 2rem; }
.category-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #e2e8f0; }
.category-title { font-size: 1.25rem; font-weight: 600; color: #0f172a; }
.category-count { background: #e2e8f0; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.8rem; color: #475569; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
.card { background: white; border-radius: 8px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.2s, box-shadow 0.2s; }
.card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.card-name { font-size: 0.85rem; color: #64748b; margin-bottom: 0.5rem; }
.card-value { font-size: 1.75rem; font-weight: 700; color: #0f172a; margin-bottom: 0.25rem; }
.card-unit { font-size: 0.85rem; color: #475569; }
.card-meta { margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #f1f5f9; font-size: 0.75rem; color: #94a3b8; }
.card-source { margin-bottom: 0.25rem; }
.footer { text-align: center; padding: 2rem; color: #94a3b8; font-size: 0.85rem; border-top: 1px solid #e2e8f0; margin-top: 2rem; }
.footer a { color: #3b82f6; text-decoration: none; }
.footer a:hover { text-decoration: underline; }
.export-bar { display: flex; gap: 0.5rem; justify-content: center; padding: 1rem; background: white; border-bottom: 1px solid #e2e8f0; }
.export-btn { padding: 0.5rem 1rem; background: #0f172a; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.85rem; text-decoration: none; }
.export-btn:hover { background: #1e3a5f; }
</style>"""

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


def _get_freshness():
    """Get the most recent fetch timestamp across all indicators."""
    if not DB_PATH.exists():
        return "N/A"
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT MAX(fetched_at) as latest FROM indicators").fetchone()
        return row["latest"] if row and row["latest"] else "N/A"
    finally:
        conn.close()


def _get_category_counts():
    """Get count of indicators per category."""
    if not DB_PATH.exists():
        return {}
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT category, COUNT(*) as cnt FROM indicators GROUP BY category ORDER BY category").fetchall()
        return {r["category"]: r["cnt"] for r in rows}
    finally:
        conn.close()


@app.get("/", response_class=HTMLResponse)
def index():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    if not rows:
        return "<html><body><h1>Project Volusia</h1><p>No data loaded yet. Run refresh_v2.py first.</p></body></html>"

    freshness = _get_freshness()
    category_counts = _get_category_counts()
    total = len(rows)

    categories = {}
    for row in rows:
        cat = row.get("category") or "Uncategorized"
        categories.setdefault(cat, []).append(row)

    html_parts = [
        "<html><head><title>Project Volusia — Open Data Portal</title>",
        CSS_STYLE,
        "</head><body>",
        '<div class="header">',
        "<h1>Project Volusia</h1>",
        "<p>Open Data Portal for Volusia County, Florida</p>",
        "</div>",
        '<div class="stats">',
        f'<div class="stat"><div class="stat-value">{total}</div><div class="stat-label">Indicators</div></div>',
        f'<div class="stat"><div class="stat-value">{len(category_counts)}</div><div class="stat-label">Categories</div></div>',
        f'<div class="stat"><div class="stat-value">{freshness[:10] if freshness != "N/A" else "N/A"}</div><div class="stat-label">Last Updated</div></div>',
        "</div>",
        '<div class="export-bar">',
        '<a class="export-btn" href="/api/indicators">JSON API</a>',
        '<a class="export-btn" href="/api/export/csv">Export CSV</a>',
        '<a class="export-btn" href="/api/export/json">Export JSON</a>',
        '<a class="export-btn" href="/api/health">Health Check</a>',
        '<a class="export-btn" href="/api/status">Status</a>',
        "</div>",
        '<div class="container">',
    ]

    for cat, items in sorted(categories.items()):
        html_parts.append('<div class="category">')
        html_parts.append('<div class="category-header">')
        html_parts.append(f'<span class="category-title">{cat}</span>')
        html_parts.append(f'<span class="category-count">{len(items)} indicators</span>')
        html_parts.append('</div>')
        html_parts.append('<div class="grid">')
        for item in items:
            name = item.get("name", "")
            value = item.get("value", "N/A")
            unit = item.get("unit", "")
            source = item.get("source", "")
            vintage = item.get("vintage", "")
            fetched = item.get("fetched_at", "")[:10] if item.get("fetched_at") else ""
            description = item.get("description", "")
            html_parts.append('<div class="card">')
            html_parts.append(f'<div class="card-name">{name}</div>')
            html_parts.append(f'<div class="card-value">{value}</div>')
            html_parts.append(f'<div class="card-unit">{unit}</div>')
            html_parts.append('<div class="card-meta">')
            html_parts.append(f'<div class="card-source">Source: {source} ({vintage})</div>')
            html_parts.append(f'<div>Refreshed: {fetched}</div>')
            if description:
                html_parts.append(f'<div style="margin-top:0.5rem; font-style:italic;">{description}</div>')
            html_parts.append('</div></div>')
        html_parts.append('</div></div>')

    html_parts.append('<div class="footer">')
    html_parts.append('<p>Project Volusia &middot; ZQM Labs &middot; <a href="https://github.com/ZQM-Computing">GitHub</a></p>')
    html_parts.append('<p>Data refreshed regularly from public U.S. government sources (Census, BLS, BEA, NOAA).</p>')
    html_parts.append('</div></div></body></html>')

    return "".join(html_parts)


@app.get("/api/indicators")
def api_indicators():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    return {"count": len(rows), "indicators": rows}


@app.get("/api/export/csv")
def export_csv():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    if not rows:
        return Response(content="No data available", media_type="text/plain")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "name", "value", "unit", "category", "source", "source_url", "vintage", "fetched_at", "description"])
    writer.writeheader()
    writer.writerows(rows)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=volusia_indicators.csv"}
    )


@app.get("/api/export/json")
def export_json():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    return {"count": len(rows), "indicators": rows, "exported_at": datetime.now(timezone.utc).isoformat()}


@app.get("/api/datasets")
def api_datasets():
    rows = _db_rows("SELECT * FROM datasets ORDER BY id DESC LIMIT 50")
    return {"count": len(rows), "datasets": rows}


@app.get("/api/health")
def api_health():
    db_exists = DB_PATH.exists()
    indicator_count = 0
    freshness = "N/A"
    if db_exists:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        try:
            indicator_count = conn.execute("SELECT COUNT(*) FROM indicators").fetchone()[0]
            row = conn.execute("SELECT MAX(fetched_at) as latest FROM indicators").fetchone()
            freshness = row["latest"] if row and row["latest"] else "N/A"
        finally:
            conn.close()
    return {
        "status": "healthy" if db_exists and indicator_count > 0 else "degraded",
        "db_exists": db_exists,
        "db_path": str(DB_PATH),
        "indicator_count": indicator_count,
        "latest_refresh": freshness,
    }


@app.get("/api/status")
def api_status():
    """Executive summary of the portal and data freshness."""
    indicators = _db_rows("SELECT * FROM indicators ORDER BY fetched_at DESC")
    latest_update = indicators[0]["fetched_at"] if indicators else "N/A"
    stale_count = sum(1 for i in indicators if not i.get("vintage"))
    categories = _get_category_counts()

    return {
        "system": "Project Volusia Open Data Portal",
        "status": "operational",
        "total_indicators": len(indicators),
        "latest_update": latest_update,
        "stale_indicators": stale_count,
        "categories": categories,
        "sla": {
            "data_freshness": "Monthly refresh",
            "uptime_target": "99.9%",
            "refresh_cadence": "BLS/NOAA: monthly | Census ACS: annual | BEA: annual | QCEW: quarterly"
        },
        "endpoints": {
            "homepage": "/",
            "indicators": "/api/indicators",
            "export_csv": "/api/export/csv",
            "export_json": "/api/export/json",
            "datasets": "/api/datasets",
            "health": "/api/health",
            "status": "/api/status"
        }
    }


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("VOLUSIA_PORTAL_HOST", "127.0.0.1")
    port = int(os.environ.get("VOLUSIA_PORTAL_PORT", "8789"))
    print(f"Starting Project Volusia Portal on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
