#!/usr/bin/env python3
"""
Project Volusia — Standalone Portal
Serves HTML dashboard + JSON APIs from SQLite.

Coherence-aware: surfaces source disagreements, vintage differences,
and provenance metadata so stakeholders see multi-source reality
rather than a flattened single number.

Run: python Tools/volusia_data/portal_app.py
"""

import os
import sqlite3
import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, StreamingResponse

# Import central config
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from volusia_data.config import (
    DB_PATH, PORTAL_HOST, PORTAL_PORT,
    EXTERNAL_SITE_URL, validate_keys
)

app = FastAPI(title="Project Volusia — Open Data Portal")

# ── Coherence metadata ──────────────────────────────────────────────────────
# Indicator groupings that represent the same real-world quantity from
# different sources. When multiple indicators match a group, the portal
# surfaces the disagreement instead of hiding it.
COHERENCE_GROUPS = {
    "population": {
        "label": "Population",
        "indicator_names": [
            "total_population_pep_2024",
            "total_population_pep_2023",
            "total_population_pep_2022",
            "total_population_acs",
            "population_bea",
        ],
        "unit": "persons",
        "note": "Different sources use different methodologies and vintages. "
                "PEP = Census Population Estimates Program (official counts). "
                "ACS = American Community Survey (survey-based). "
                "BEA = Bureau of Economic Analysis (economic geography). "
                "Treat as a range, not a single number.",
    },
    "income": {
        "label": "Income",
        "indicator_names": [
            "per_capita_income",
            "personal_income_total",
        ],
        "unit": "USD",
        "note": "BEA personal income measures all income received by residents "
                "(wages, benefits, investment income, government transfers). "
                "Different from Census money income.",
    },
    "employment": {
        "label": "Employment",
        "indicator_names": [
            "employment_qcew",
            "unemployment_rate_bls",
        ],
        "unit": "mixed",
        "note": "QCEW employment counts jobs at establishments. "
                "BLS LAUS unemployment rate measures labor force status of residents. "
                "These measure different things — don't divide one by the other.",
    },
}

CSS_STYLE = """
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: #f8fafc; color: #1e293b; line-height: 1.6; }
.header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
          color: white; padding: 2rem; text-align: center; }
.header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
.header p { opacity: 0.9; font-size: 0.95rem; }
.stats { display: flex; justify-content: center; gap: 2rem; padding: 1.5rem;
         background: white; border-bottom: 1px solid #e2e8f0; flex-wrap: wrap; }
.stat { text-align: center; }
.stat-value { font-size: 1.5rem; font-weight: bold; color: #0f172a; }
.stat-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; }
.container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
.category { margin-bottom: 2rem; }
.category-header { display: flex; align-items: center; gap: 0.5rem;
                   margin-bottom: 1rem; padding-bottom: 0.5rem;
                   border-bottom: 2px solid #e2e8f0; }
.category-title { font-size: 1.25rem; font-weight: 600; color: #0f172a; }
.category-count { background: #e2e8f0; padding: 0.25rem 0.75rem;
                  border-radius: 999px; font-size: 0.8rem; color: #475569; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1rem; }
.card { background: white; border-radius: 8px; padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s; }
.card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.card-name { font-size: 0.85rem; color: #64748b; margin-bottom: 0.5rem; }
.card-value { font-size: 1.75rem; font-weight: 700; color: #0f172a; margin-bottom: 0.25rem; }
.card-unit { font-size: 0.85rem; color: #475569; }
.card-meta { margin-top: 0.75rem; padding-top: 0.75rem;
             border-top: 1px solid #f1f5f9; font-size: 0.75rem; color: #94a3b8; }
.card-source { margin-bottom: 0.25rem; }
.coherence-note { background: #fef3c7; border-left: 4px solid #f59e0b;
                  padding: 1rem; margin: 1rem 0; border-radius: 4px; }
.coherence-note strong { color: #92400e; }
.coherence-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                  gap: 1rem; margin-top: 1rem; }
.coherence-card { background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px;
                  padding: 1rem; }
.coherence-card h4 { font-size: 0.9rem; color: #92400e; margin-bottom: 0.5rem; }
.coherence-card p { font-size: 0.8rem; color: #78350f; line-height: 1.4; }
.coherence-card .values { margin-top: 0.5rem; font-size: 0.85rem; }
.coherence-card .values span { display: inline-block; background: #fde68a;
                               padding: 0.15rem 0.5rem; margin: 0.15rem;
                               border-radius: 4px; font-weight: 600; }
.footer { text-align: center; padding: 2rem; color: #94a3b8; font-size: 0.85rem;
          border-top: 1px solid #e2e8f0; margin-top: 2rem; }
.footer a { color: #3b82f6; text-decoration: none; }
.footer a:hover { text-decoration: underline; }
.export-bar { display: flex; gap: 0.5rem; justify-content: center; padding: 1rem;
              background: white; border-bottom: 1px solid #e2e8f0; flex-wrap: wrap; }
.export-btn { padding: 0.5rem 1rem; background: #0f172a; color: white;
              border: none; border-radius: 4px; cursor: pointer;
              font-size: 0.85rem; text-decoration: none; }
.export-btn:hover { background: #1e3a5f; }
.key-status { display: inline-flex; align-items: center; gap: 0.5rem;
              padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.8rem;
              margin-top: 0.5rem; }
.key-status.ok { background: #dcfce7; color: #166534; }
.key-status.missing { background: #fee2e2; color: #991b1b; }
.key-status.missing::before { content: "!"; background: #ef4444; color: white;
                              width: 1rem; height: 1rem; border-radius: 50%;
                              display: inline-flex; align-items: center;
                              justify-content: center; font-weight: bold;
                              font-size: 0.7rem; }
</style>
"""

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
    if not DB_PATH.exists():
        return {}
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT category, COUNT(*) as cnt FROM indicators GROUP BY category ORDER BY category"
        ).fetchall()
        return {r["category"]: r["cnt"] for r in rows}
    finally:
        conn.close()

def _get_coherence_disagreements():
    """Find indicators that belong to the same coherence group but disagree."""
    disagreements = []
    for group_key, group in COHERENCE_GROUPS.items():
        rows = _db_rows(
            "SELECT * FROM indicators WHERE name IN ({}) ORDER BY vintage DESC".format(
                ",".join("?" for _ in group["indicator_names"])
            ),
            group["indicator_names"],
        )
        if len(rows) < 2:
            continue
        # Check if values differ meaningfully
        numeric_vals = []
        for r in rows:
            try:
                numeric_vals.append(float(r["value"]))
            except (ValueError, TypeError):
                pass
        if len(numeric_vals) >= 2:
            spread = max(numeric_vals) - min(numeric_vals)
            if spread > 0:
                disagreements.append({
                    "group_key": group_key,
                    "group_label": group["label"],
                    "note": group["note"],
                    "indicators": rows,
                    "spread": spread,
                })
    return disagreements

@app.get("/", response_class=HTMLResponse)
def index():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    if not rows:
        return (
            "<html><body><h1>Project Volusia</h1>"
            "<p>No data loaded yet. Run refresh_v2.py first.</p></body></html>"
        )

    freshness = _get_freshness()
    category_counts = _get_category_counts()
    total = len(rows)
    disagreements = _get_coherence_disagreements()
    key_status = validate_keys()

    html_parts = [
        "<html><head><title>Project Volusia — Open Data Portal</title>",
        CSS_STYLE,
        "</head><body>",
        '<div class="header">',
        "<h1>Project Volusia</h1>",
        "<p>Open Data Portal for Volusia County, Florida</p>",
        '<div class="key-status {}">API Keys: {} of 3 configured</div>'.format(
            "ok" if key_status["all_configured"] else "missing",
            sum([key_status["census"], key_status["bls"], key_status["bea"]]),
        ),
        "</div>",
        '<div class="stats">',
        f'<div class="stat"><div class="stat-value">{total}</div>'
        f'<div class="stat-label">Indicators</div></div>',
        f'<div class="stat"><div class="stat-value">{len(category_counts)}</div>'
        f'<div class="stat-label">Categories</div></div>',
        f'<div class="stat"><div class="stat-value">{len(disagreements)}</div>'
        f'<div class="stat-label">Source Disagreements</div></div>',
        f'<div class="stat"><div class="stat-value">{freshness[:10] if freshness != "N/A" else "N/A"}</div>'
        f'<div class="stat-label">Last Updated</div></div>',
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

    # ── Coherence disagreements panel ──
    if disagreements:
        html_parts.append('<div class="coherence-note">')
        html_parts.append('<strong>Multiple sources, different numbers</strong>')
        html_parts.append(
            '<p>The indicators below measure the same real-world quantity '
            'from different sources with different methodologies and vintages. '
            'Read them as a range, not a single number.</p>'
        )
        html_parts.append('<div class="coherence-grid">')
        for d in disagreements:
            vals_html = ""
            for ind in d["indicators"]:
                try:
                    val = float(ind["value"])
                    vals_html += (
                        f'<span>{ind["name"]}: {ind["value"]} '
                        f'({ind["source"]}, {ind["vintage"]})</span>'
                    )
                except (ValueError, TypeError):
                    pass
            html_parts.append(
                f'<div class="coherence-card">'
                f'<h4>{d["group_label"]}</h4>'
                f'<div class="values">{vals_html}</div>'
                f'<p>{d["note"]}</p>'
                f'</div>'
            )
        html_parts.append('</div></div>')

    # ── Category cards ──
    categories = {}
    for row in rows:
        cat = row.get("category") or "Uncategorized"
        categories.setdefault(cat, []).append(row)

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
                html_parts.append(
                    f'<div style="margin-top:0.5rem; font-style:italic;">{description}</div>'
                )
            html_parts.append('</div></div>')
        html_parts.append('</div></div>')

    html_parts.append('<div class="footer">')
    html_parts.append('<p>Project Volusia &middot; ZQM Labs</p>')
    html_parts.append(
        f'<p>Data refreshed regularly from public U.S. government sources '
        f'(Census, BLS, BEA, NOAA). '
        f'<a href="{EXTERNAL_SITE_URL}">External site</a></p>'
    )
    html_parts.append('</div></div></body></html>')

    return "".join(html_parts)


@app.get("/api/indicators")
def api_indicators():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    # Add coherence group info
    for row in rows:
        for group_key, group in COHERENCE_GROUPS.items():
            if row["name"] in group["indicator_names"]:
                row["coherence_group"] = group_key
                row["coherence_group_label"] = group["label"]
                row["coherence_note"] = group["note"]
    return {"count": len(rows), "indicators": rows, "coherence_groups": list(COHERENCE_GROUPS.keys())}


@app.get("/api/coherence")
def api_coherence():
    """Returns detected disagreements between sources measuring the same quantity."""
    disagreements = _get_coherence_disagreements()
    return {
        "disagreements": disagreements,
        "groups_defined": list(COHERENCE_GROUPS.keys()),
        "total_disagreements": len(disagreements),
    }


@app.get("/api/export/csv")
def export_csv():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    if not rows:
        return Response(content="No data available", media_type="text/plain")

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "id", "name", "value", "unit", "category", "source",
            "source_url", "vintage", "fetched_at", "description",
            "coherence_group", "coherence_note",
        ],
    )
    writer.writeheader()
    for row in rows:
        enriched = dict(row)
        for group_key, group in COHERENCE_GROUPS.items():
            if row["name"] in group["indicator_names"]:
                enriched["coherence_group"] = group_key
                enriched["coherence_note"] = group["note"]
        writer.writerow(enriched)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=volusia_indicators.csv"},
    )


@app.get("/api/export/json")
def export_json():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    for row in rows:
        for group_key, group in COHERENCE_GROUPS.items():
            if row["name"] in group["indicator_names"]:
                row["coherence_group"] = group_key
                row["coherence_note"] = group["note"]
    return {
        "count": len(rows),
        "indicators": rows,
        "coherence_groups": list(COHERENCE_GROUPS.keys()),
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }


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
    key_status = validate_keys()
    return {
        "status": "healthy" if db_exists and indicator_count > 0 else "degraded",
        "db_exists": db_exists,
        "db_path": str(DB_PATH),
        "indicator_count": indicator_count,
        "latest_refresh": freshness,
        "api_keys_configured": {
            "census": key_status["census"],
            "bls": key_status["bls"],
            "bea": key_status["bea"],
        },
    }


@app.get("/api/status")
def api_status():
    """Executive summary of the portal and data freshness."""
    indicators = _db_rows("SELECT * FROM indicators ORDER BY fetched_at DESC")
    latest_update = indicators[0]["fetched_at"] if indicators else "N/A"
    disagreements = _get_coherence_disagreements()
    categories = _get_category_counts()
    key_status = validate_keys()

    return {
        "system": "Project Volusia Open Data Portal",
        "status": "operational" if indicators else "degraded",
        "version": "1.0.0",
        "total_indicators": len(indicators),
        "latest_update": latest_update,
        "source_disagreements": len(disagreements),
        "categories": categories,
        "api_keys": {
            "census": key_status["census"],
            "bls": key_status["bls"],
            "bea": key_status["bea"],
            "all_configured": key_status["all_configured"],
        },
        "sla": {
            "data_freshness": "Monthly refresh",
            "uptime_target": "99.9%",
            "refresh_cadence": "BLS/NOAA: monthly | Census ACS: annual | BEA: annual | QCEW: quarterly",
        },
        "endpoints": {
            "homepage": "/",
            "indicators": "/api/indicators",
            "coherence": "/api/coherence",
            "export_csv": "/api/export/csv",
            "export_json": "/api/export/json",
            "datasets": "/api/datasets",
            "health": "/api/health",
            "status": "/api/status",
        },
    }


@app.get("/api/coherence/groups")
def api_coherence_groups():
    """Returns the defined coherence groups and their members."""
    return {
        "groups": [
            {
                "key": k,
                "label": v["label"],
                "unit": v["unit"],
                "note": v["note"],
                "indicator_names": v["indicator_names"],
            }
            for k, v in COHERENCE_GROUPS.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    print(f"Starting Project Volusia Portal on http://{PORTAL_HOST}:{PORTAL_PORT}")
    print(f"Database: {DB_PATH}")
    key_status = validate_keys()
    if not key_status["all_configured"]:
        print("WARNING: Not all API keys configured — some data sources will fail")
    uvicorn.run(app, host=PORTAL_HOST, port=PORTAL_PORT)
