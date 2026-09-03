#!/usr/bin/env python3
"""
Project Volusia — Standalone Portal
Serves HTML dashboard + JSON APIs from SQLite.
Run: python portal_app.py
"""
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="Project Volusia — Open Data Portal")

# DB path: use env var or default to local
DB_PATH = Path(os.environ.get("VOLUSIA_DB_PATH", str(Path(__file__).resolve().parent / "volusia.db")))
# ── SLA / refresh-cadence metadata ──────────────────────────────────────────
# Published in the portal footer and surfaced via /api/status (P2 deliverable.
SERVICE_METADATA = {
    "service": "Project Volusia Open Data Portal",
    "version": "1.1.0",
    "operator": "ZQM Labs",
    "uptime_target": "99.9%",
    "data_freshness_target": "Indicator age must stay within its source refresh cadence",
    "review_window": "5 business days",
    "refresh_cadence": {
        "Census PEP": "Annual (July population-estimates release)",
        "NOAA NCEI": "Annual batch — daily summaries for the prior calendar year",
        "BLS LAUS": "Monthly",
        "BEA Regional": "Annual (CAINC1 release)",
        "BLS QCEW": "Annual single-file (rebuild quarterly when available)",
    },
}

# Maximum acceptable days between pipeline refresh and publication, per source.
CADENCE_MAX_DAYS = {
    "Census PEP": 45,
    "NOAA NCEI": 45,
    "BLS LAUS": 45,
    "BEA Regional": 60,
    "BLS QCEW": 120,
}


def _parse_ts(value):
    """Parse an ISO-8601 timestamp to a naive UTC datetime, or None."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value.replace("Z", "+00:00")))
        if dt.tzinfo:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except (ValueError, TypeError):
        return None


def _latest_fetch(indicators, source=None):
    times = []
    for i in indicators:
        if source is not None and i.get("source") != source:
            continue
        ts = _parse_ts(i.get("fetched_at"))
        if ts:
            times.append(ts)
    return max(times) if times else None


def _staleness(indicators):
    """Per-source freshness vs the cadence table (days since last fetch)."""
    sources = sorted({i.get("source") for i in indicators if i.get("source")})
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    out = {}
    for src in sources:
        latest = _latest_fetch(indicators, src)
        max_days = CADENCE_MAX_DAYS.get(src)
        if latest is None:
            out[src] = {"status": "unknown", "days_since_fetch": None, "cadence_max_days": max_days}
            continue
        days = (now - latest).days
        if days < 0:
            days = 0
        out[src] = {
            "status": "fresh" if max_days is None or days <= max_days else "stale",
            "days_since_fetch": days,
            "cadence_max_days": max_days,
            "last_fetch": latest.isoformat(),
        }
    return out


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
        return ("<html><head><title>Project Volusia — Open Data Portal</title></head><body>"
                "<h1>Project Volusia — Open Data Portal</h1>"
                "<p>No data loaded yet. Run <code>python volusia_data/refresh_v2.py</code> first.</p>"
                "<p><a href=\"/api/status\">Status API</a> · <a href=\"/api/health\">Health</a></p>"
                "</body></html>")

    categories = {}
    for row in rows:
        cat = row.get("category") or "Uncategorized"
        categories.setdefault(cat, []).append(row)

    latest = _latest_fetch(rows)
    stamp = latest.isoformat() if latest else "N/A"

    html_parts = [
        "<html><head><title>Project Volusia — Open Data Portal</title>",
        "<style>"
        "body{font-family:sans-serif;margin:20px;color:#222;}"
        "table{border-collapse:collapse;width:100%;margin:10px 0;}"
        "th,td{border:1px solid #ddd;padding:8px;text-align:left;}"
        "th{background:#f4f4f4;}"
        ".category{margin-top:20px;font-size:1.2em;font-weight:bold;}"
        ".footer{margin-top:30px;padding-top:10px;border-top:2px solid #ddd;"
        "font-size:0.85em;color:#555;line-height:1.6;}"
        "</style>",
        "</head><body>",
        "<h1>Project Volusia — Open Data Portal</h1>",
        f"<p>Last updated: {stamp}</p>",
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

    html_parts.append(_page_footer(latest))
    html_parts.append('</body></html>')
    return "".join(html_parts)


def _page_footer(latest):
    """P2 deliverable — SLA/uptime + refresh-cadence metadata in the footer."""
    stamp = latest.isoformat() if latest else "N/A"
    cad = SERVICE_METADATA["refresh_cadence"]
    cad_html = " · ".join(f"{k}: {v}" for k, v in cad.items())
    return (
        '<div class="footer">'
        f"<p><strong>Project Volusia</strong> · ZQM Labs · Last refreshed: {stamp}</p>"
        f"<p>SLA — uptime target: {SERVICE_METADATA['uptime_target']} · data freshness target: "
        f"{SERVICE_METADATA['data_freshness_target']} · contributor review window: "
        f"{SERVICE_METADATA['review_window']}</p>"
        f"<p>Refresh cadence — {cad_html}</p>"
        '<p><a href="/api/status">Status API</a> · <a href="/api/health">Health</a> · '
        '<a href="/api/datasets">Datasets</a> · <a href="/api/indicators">Indicators</a> · '
        '<a href="/openapi.json">API spec</a></p>'
        "</div>"
    )


@app.get("/api/indicators")
def api_indicators():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    return {"count": len(rows), "indicators": rows}


@app.get("/api/datasets")
def api_datasets():
    rows = _db_rows("SELECT * FROM datasets ORDER BY id DESC LIMIT 50")
    return {"count": len(rows), "datasets": rows}


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


@app.get("/api/status")
def api_status():
    """Executive summary of the portal: counts, SLA, cadence, staleness."""
    indicators = _db_rows("SELECT * FROM indicators ORDER BY fetched_at DESC")
    latest = _latest_fetch(indicators)
    datasets = _db_rows("SELECT id, source, content, fetched_at FROM datasets ORDER BY id DESC LIMIT 20")
    categories = {}
    for ind in indicators:
        cat = ind.get("category") or "Uncategorized"
        categories[cat] = categories.get(cat, 0) + 1

    freshness = _staleness(indicators)
    stale_sources = [s for s, v in freshness.items() if v.get("status") == "stale"]

    return {
        "system": SERVICE_METADATA["service"],
        "version": SERVICE_METADATA["version"],
        "operator": SERVICE_METADATA["operator"],
        "status": "operational" if indicators else "degraded",
        "total_indicators": len(indicators),
        "dataset_rows": len(datasets),
        "latest_update": latest.isoformat() if latest else None,
        "stale_sources": stale_sources,
        "categories": categories,
        "sla": {
            "uptime_target": SERVICE_METADATA["uptime_target"],
            "data_freshness_target": SERVICE_METADATA["data_freshness_target"],
            "review_window": SERVICE_METADATA["review_window"],
            "refresh_cadence": SERVICE_METADATA["refresh_cadence"],
        },
        "per_source_freshness": freshness,
        "endpoints": {
            "homepage": "/",
            "indicators": "/api/indicators",
            "datasets": "/api/datasets",
            "health": "/api/health",
            "status": "/api/status",
            "v1": "/api/v1"
        }
    }


@app.get("/api/indicators/{name}")
def api_indicator(name: str):
    """Get a single indicator by name (matches openapi.yaml path)."""
    rows = _db_rows("SELECT * FROM indicators WHERE name = ?", (name,))
    if not rows:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return rows[0]


# ── /api/v1 aliases (aligned with openapi.yaml server prefix) ─────────────
@app.get("/api/v1/health")
def api_v1_health():
    return api_health()


@app.get("/api/v1/status")
def api_v1_status():
    return api_status()


@app.get("/api/v1/indicators")
def api_v1_indicators():
    return api_indicators()


@app.get("/api/v1/indicators/{name}")
def api_v1_indicator(name: str):
    return api_indicator(name)


@app.get("/api/v1/datasets")
def api_v1_datasets():
    return api_datasets()


if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("VOLUSIA_PORTAL_HOST", "127.0.0.1")
    port = int(os.environ.get("VOLUSIA_PORTAL_PORT", "8789"))
    uvicorn.run(app, host=host, port=port)
