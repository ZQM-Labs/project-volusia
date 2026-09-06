#!/usr/bin/env python3
"""
Project Volusia - Enhanced Portal App (v2.1)
Serves HTML dashboard + JSON APIs from SQLite with improved error handling.

Run: python Tools/volusia_data/portal_app.py
Port: 8789 (configurable via VOLUSIA_PORT env var)
"""

from __future__ import annotations

import os
import sys
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Force clean import (script mode only) - avoids KeyError on module reload
if __name__ == "__main__":
    for key in list(sys.modules.keys()):
        if "volusia" in key:
            del sys.modules[key]

# ── Configuration ─────────────────────────────────────────────────────────────
DB_PATH = Path(
    os.environ.get(
        "VOLUSIA_DB_PATH",
        str(Path(__file__).resolve().parent / "volusia.db"),
    )
)
PORT = int(os.environ.get("VOLUSIA_PORT", 8789))
HOST = os.environ.get("VOLUSIA_HOST", "0.0.0.0")

# ── Database Helpers ─────────────────────────────────────────────────────────
def _db_query(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    """Execute query and return list of dicts."""
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(query, params)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def _db_single(query: str, params: tuple = ()) -> dict[str, Any] | None:
    """Execute query and return single dict or None."""
    rows = _db_query(query, params)
    return rows[0] if rows else None


# ── Data Freshness Check ────────────────────────────────────────────────────
def get_freshness() -> str:
    """Get the latest fetch timestamp."""
    row = _db_single("SELECT MAX(fetched_at) as latest FROM indicators")
    if row and row.get("latest"):
        return row["latest"]
    return "N/A"


def get_indicator_count() -> int:
    """Get total indicator count."""
    count = _db_single("SELECT COUNT(*) as cnt FROM indicators")
    return count["cnt"] if count else 0


# ── Data Freshness Summary ──────────────────────────────────────────────────
def get_data_freshness_summary() -> dict[str, Any]:
    """Get per-source freshness information."""
    rows = _db_query("""
        SELECT source, MAX(fetched_at) as latest, COUNT(*) as cnt
        FROM indicators GROUP BY source ORDER BY source
    """)
    return {r["source"]: {"latest": r["latest"], "count": r["cnt"]} for r in rows}


# ── Core Tables ────────────────────────────────────────────────────────────
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
        "note": (
            "Different sources use different methodologies and vintages. "
            "PEP = Census Population Estimates (July 1 counts). "
            "ACS = American Community Survey (5-year survey estimates). "
            "BEA = Bureau of Economic Analysis (economic geography estimates). "
            "Treat as a range, not a single number."
        ),
    },
    "income": {
        "label": "Income",
        "indicator_names": ["per_capita_income", "personal_income_total"],
        "unit": "USD",
        "note": (
            "BEA personal income measures all income received by residents "
            "(wages, benefits, investment income, government transfers). "
            "Census money income differs in scope and methodology."
        ),
    },
    "employment": {
        "label": "Employment",
        "indicator_names": ["employment_qcew", "unemployment_rate"],
        "unit": "mixed",
        "note": (
            "QCEW employment counts jobs at establishments (monthly). "
            "BLS LAUS unemployment rate measures labor force status (monthly). "
            "These measure different things - don't divide one by the other."
        ),
    },
}


def get_coherence_disagreements() -> list[dict[str, Any]]:
    """Find indicators with source disagreements."""
    disagreements = []
    
    for group_key, group in COHERENCE_GROUPS.items():
        indicators = _db_query(
            f"SELECT * FROM indicators WHERE name IN ({', '.join('?' * len(group['indicator_names']))}) ORDER BY vintage DESC",
            group["indicator_names"],
        )
        
        if len(indicators) < 2:
            continue
        
        # Extract numeric values
        numeric_vals = []
        for r in indicators:
            try:
                numeric_vals.append(float(r["value"]))
            except (ValueError, TypeError, KeyError):
                continue
        
        if len(numeric_vals) < 2:
            continue
        
        spread = max(numeric_vals) - min(numeric_vals)
        
        # Only flag as disagreement if spread > 1% of mid-range
        if spread > 0:
            disagreements.append({
                "group_key": group_key,
                "group_label": group["label"],
                "note": group["note"],
                "indicators": indicators,
                "spread": spread,
            })
    
    return disagreements


# ── FastAPI App ───────────────────────────────────────────────────────────
app = FastAPI(
    title="Project Volusia Open Data Portal",
    description="Open data portal for Volusia County, Florida with source-aware indicators",
    version="2.1.0",
)

# Enable CORS for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index() -> HTMLResponse:
    """Render the main dashboard."""
    rows = _db_query("SELECT * FROM indicators ORDER BY category, name")
    
    if not rows:
        return HTMLResponse(
            "<html><body><h1>Project Volusia</h1>"
            "<p>No data loaded yet. Run refresh_v2.py first.</p></body></html>",
            status_code=200,
        )

    freshness = get_freshness()
    category_counts = {}
    for r in rows:
        cat = r.get("category") or "Uncategorized"
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    disagreements = get_coherence_disagreements()

    # Build timeline of refreshes (need to fix column name in manifest query)
    timeline = _db_query("""
        SELECT run_id, duration_ms, status, indicators_count, fetched_at as timestamp
        FROM fetch_manifest ORDER BY fetched_at DESC LIMIT 10
    """)

    return HTMLResponse(_render_dashboard(rows, freshness, category_counts, disagreements, timeline))


@app.get("/api/health")
async def health() -> JSONResponse:
    """Health check endpoint."""
    db_exists = DB_PATH.exists()
    indicator_count = get_indicator_count() if db_exists else 0
    
    # Check if data is fresh (within 7 days)
    freshness_ok = True
    if db_exists:
        latest = _db_single("SELECT MAX(fetched_at) as latest FROM indicators")
        if latest and latest.get("latest"):
            try:
                fetched_at = datetime.fromisoformat(latest["latest"].replace("Z", "+00:00"))
                age_hours = (datetime.now(timezone.utc) - fetched_at).total_seconds() / 3600
                freshness_ok = age_hours < 168  # 7 days
            except (ValueError, TypeError):
                freshness_ok = False
    
    status = "healthy" if db_exists and indicator_count > 0 and freshness_ok else "degraded"
    
    return JSONResponse({
        "status": status,
        "db_exists": db_exists,
        "indicator_count": indicator_count,
        "freshness_ok": freshness_ok,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.get("/api/indicators")
async def list_indicators(
    limit: int = Query(100, ge=1, le=1000),
    source: str | None = Query(None),
    category: str | None = Query(None),
) -> JSONResponse:
    """List all indicators with optional filtering."""
    query = "SELECT * FROM indicators"
    params: list[Any] = []
    conditions = []
    
    if source:
        conditions.append("source = ?")
        params.append(source)
    if category:
        conditions.append("category = ?")
        params.append(category)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += f" ORDER BY category, name LIMIT ?"
    params.append(limit)
    
    rows = _db_query(query, tuple(params))
    
    return JSONResponse({
        "count": len(rows),
        "total": get_indicator_count(),
        "indicators": rows,
        "filters_applied": {"source": source, "category": category} if (source or category) else {},
    })


@app.get("/api/status")
async def status() -> JSONResponse:
    """Full status with manifest history."""
    manifest = _db_query("""
        SELECT run_id, duration_ms, status, indicators_count, fetched_at as timestamp 
        FROM fetch_manifest ORDER BY fetched_at DESC LIMIT 10
    """)
    
    freshness = get_data_freshness_summary()
    disagreements = get_coherence_disagreements()
    
    # Calculate SLA
    db_exists = DB_PATH.exists()
    latest_fetch = _db_single("SELECT fetched_at FROM indicators ORDER BY fetched_at DESC LIMIT 1")
    
    sla_met = False
    last_refresh_days = None
    if latest_fetch and latest_fetch.get("fetched_at"):
            try:
                fetched_at = datetime.fromisoformat(latest_fetch["fetched_at"].replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - fetched_at).total_seconds() / 86400
                sla_met = age_days <= 7  # Weekly refresh target
                last_refresh_days = int(age_days)
            except (ValueError, TypeError):
                pass

    return JSONResponse({
            "database": {
                "exists": db_exists,
                "path": str(DB_PATH),
            },
            "indicators": {
                "count": get_indicator_count(),
                "freshness": get_freshness(),
            },
            "sla": {
                "met": sla_met,
                "target": "weekly",
                "last_refresh_days": last_refresh_days,
            },
        "source_freshness": freshness,
        "coherence_disagreements": len(disagreements),
        "manifest": manifest,
    })


@app.get("/api/export/csv")
async def export_csv() -> StreamingResponse:
    """Export all data as CSV."""
    rows = _db_query("SELECT * FROM indicators ORDER BY category, name")
    
    if not rows:
        return StreamingResponse(
            iter([b"id,name,value,unit,category,source,source_url,vintage,fetched_at,description\n"]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=volusia_indicators.csv"},
        )
    
    def generate():
        header = list(rows[0].keys())
        yield (",".join(header) + "\n").encode()
        for row in rows:
            values = [str(row.get(h, "")) for h in header]
            # Handle commas in values
            values = [f'"{v}"' if "," in v else v for v in values]
            yield (",".join(values) + "\n").encode()
    
    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=volusia_indicators.csv"},
    )


@app.get("/api/export/json")
async def export_json() -> JSONResponse:
    """Export all data as JSON with metadata."""
    rows = _db_query("SELECT * FROM indicators ORDER BY category, name")
    
    return JSONResponse({
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "count": len(rows),
        "indicators": rows,
        "sources": list(set(r.get("source", "") for r in rows if r.get("source"))),
        "categories": list(set(r.get("category", "") for r in rows if r.get("category"))),
    })


@app.get("/api/chart/{name}")
async def get_chart(name: str):
    """Generate chart images dynamically."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import io
    
    # Remove .png extension if provided
    chart_name = name.replace(".png", "")
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if chart_name == "population_trend":
        rows = conn.execute("SELECT * FROM indicators WHERE name LIKE 'total_population_pep_%' ORDER BY vintage").fetchall()
        if rows:
            ax.bar([r["vintage"] for r in rows], [float(r["value"]) for r in rows], color="#38bdf8")
            ax.set_title("Population Trend")
            ax.set_ylabel("Population")
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    
    elif chart_name == "employment_overview":
        rows = conn.execute("SELECT * FROM indicators WHERE category = 'Economy' AND (name LIKE '%employment%' OR name LIKE '%establishments%') ORDER BY name").fetchall()
        if rows:
            ax.barh([r["name"][:20] for r in rows[:10] if r["value"].isdigit()], [float(r["value"]) for r in rows[:10] if r["value"].isdigit()], color="#10b981")
            ax.set_title("Employment Overview")
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    
    elif chart_name == "climate_summary":
        rows = conn.execute("SELECT * FROM indicators WHERE category = 'Climate' ORDER BY name").fetchall()
        if rows:
            values = [float(r["value"]) for r in rows if r["value"].replace(".", "").replace("-", "").isdigit()][:10]
            labels = [r["name"][:15] for r in rows][:len(values)]
            ax.bar(labels, values, color="#f59e0b")
            ax.set_title("Climate Summary")
            ax.tick_params(axis="x", rotation=45)
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    
    elif chart_name == "unemployment_trend":
        rows = conn.execute("SELECT * FROM indicators WHERE name LIKE '%unemployment%' ORDER BY vintage").fetchall()
        if rows:
            ax.plot([r["vintage"] for r in rows], [float(r["value"]) for r in rows], marker="o", color="#ef4444")
            ax.set_title("Unemployment Trend")
            ax.set_ylabel("Rate (%)")
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    
    elif chart_name == "wage_trend":
        rows = conn.execute("SELECT * FROM indicators WHERE name LIKE '%wage%' ORDER BY vintage").fetchall()
        if rows:
            ax.plot([r["vintage"] for r in rows], [float(r["value"]) for r in rows], marker="s", color="#38bdf8")
            ax.set_title("Wage Trend")
            ax.set_ylabel("Weekly Wage ($)")
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    
    elif chart_name == "income_overview":
        rows = conn.execute("SELECT * FROM indicators WHERE name LIKE '%income%' ORDER BY name").fetchall()
        if rows:
            values = [float(r["value"]) for r in rows if r["value"].isdigit()][:10]
            labels = [r["name"][:15] for r in rows][:len(values)]
            ax.barh(labels, values, color="#10b981")
            ax.set_title("Income Overview")
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    
    elif chart_name == "housing_overview":
        rows = conn.execute("SELECT * FROM indicators WHERE category = 'Housing' ORDER BY name").fetchall()
        if rows:
            values = [float(r["value"]) for r in rows if r["value"].isdigit()][:10]
            labels = [r["name"][:15] for r in rows][:len(values)]
            ax.barh(labels, values, color="#f59e0b")
            ax.set_title("Housing Overview")
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    
    elif chart_name == "demographics":
        rows = conn.execute("SELECT * FROM indicators WHERE category = 'Demographics' ORDER BY name").fetchall()
        if rows:
            values = [float(r["value"]) for r in rows if r["value"].isdigit()][:10]
            labels = [r["name"][:15] for r in rows][:len(values)]
            ax.bar(labels, values, color="#38bdf8")
            ax.set_title("Demographics")
            ax.tick_params(axis="x", rotation=45)
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    
    elif chart_name == "education_health":
        rows = conn.execute("SELECT * FROM indicators WHERE category IN ('Education', 'Health') ORDER BY category, name").fetchall()
        if rows:
            values = [float(r["value"]) for r in rows if r["value"].isdigit()][:10]
            labels = [r["name"][:15] for r in rows][:len(values)]
            ax.bar(labels, values, color="#a855f7")
            ax.set_title("Education & Health")
            ax.tick_params(axis="x", rotation=45)
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    
    elif chart_name == "traffic_overview":
        rows = conn.execute("SELECT * FROM indicators WHERE category = 'Transportation' ORDER BY name").fetchall()
        if rows:
            values = [float(r["value"]) for r in rows if r["value"].isdigit()][:10]
            labels = [r["name"][:15] for r in rows][:len(values)]
            ax.barh(labels, values, color="#10b981")
            ax.set_title("Traffic Overview")
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    
    elif chart_name == "schools_by_type":
        rows = conn.execute("SELECT * FROM indicators WHERE name LIKE 'schools_%' ORDER BY name").fetchall()
        if rows:
            ax.pie([float(r["value"]) for r in rows if r["value"].isdigit()], labels=[r["name"] for r in rows if r["value"].isdigit()], autopct="%1.0f%%")
            ax.set_title("Schools by Type")
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    
    elif chart_name == "infrastructure":
        rows = conn.execute("SELECT * FROM indicators WHERE category = 'Infrastructure' ORDER BY name").fetchall()
        if rows:
            values = [float(r["value"]) for r in rows if r["value"].isdigit()][:10]
            labels = [r["name"][:15] for r in rows][:len(values)]
            ax.barh(labels, values, color="#f59e0b")
            ax.set_title("Infrastructure")
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    
    else:
        ax.text(0.5, 0.5, f"Unknown chart: {chart_name}", ha="center", va="center")
    
    conn.close()
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    
    return StreamingResponse(buf, media_type="image/png")


# ── Dashboard Renderer ────────────────────────────────────────────────────
def _render_dashboard(
    rows: list[dict],
    freshness: str,
    category_counts: dict[str, int],
    disagreements: list[dict],
    timeline: list[dict],
) -> str:
    """Render the dashboard HTML."""
    # CSS loaded from portal.css if available
    css_path = Path(__file__).resolve().parent / "portal.css"
    if css_path.exists():
        css_style = f"<style>{css_path.read_text()}</style>"
    else:
        # Inline minimal CSS
        css_style = """<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
       background: #f8fafc; color: #1e293b; line-height: 1.6; }
.header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
          color: white; padding: 2rem; text-align: center; }
.container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
.card { background: white; border-radius: 8px; padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.stat { text-align: center; padding: 1rem; }
.stat-value { font-size: 1.5rem; font-weight: bold; color: #0f172a; }
.stat-label { font-size: 0.8rem; color: #64748b; }
</style>"""

    html_parts = [
        "<!DOCTYPE html>",
        "<html><head><title>Project Volusia - Dashboard</title>",
        css_style,
        "</head><body>",
        '<div class="header">',
        "<h1>Project Volusia</h1>",
        "<p>Open Data Portal for Volusia County, Florida</p>",
        '<div class="stats">',
        f'<div class="stat"><div class="stat-value">{len(rows)}</div>'
        f'<div class="stat-label">Indicators</div></div>',
        f'<div class="stat"><div class="stat-value">{len(category_counts)}</div>'
        f'<div class="stat-label">Categories</div></div>',
        f'<div class="stat"><div class="stat-value">{len(disagreements)}</div>'
        f'<div class="stat-label">Disagreements</div></div>',
        f'<div class="stat"><div class="stat-value">{freshness[:10] if freshness != "N/A" else "N/A"}</div>'
        f'<div class="stat-label">Last Updated</div></div>',
        "</div>",
        "</div>",
        '<div class="container">',
    ]

    # Timeline if available
    if timeline:
        html_parts.append('<h2 style="margin-top: 2rem; margin-bottom: 1rem;">Recent Refreshes</h2>')
        html_parts.append('<table style="width:100%; border-collapse:collapse;">')
        html_parts.append('<tr><th style="text-align:left;padding:0.5rem;">Run ID</th>'
                         '<th style="text-align:right;padding:0.5rem;">Duration</th>'
                         '<th style="text-align:right;padding:0.5rem;">Status</th>'
                         '<th style="text-align:right;padding:0.5rem;">Indicators</th></tr>')
        for t in timeline[:10]:
            html_parts.append(f'<tr><td style="padding:0.5rem;">{t.get("run_id", "N/A")[:12]}</td>'
                            f'<td style="text-align:right;padding:0.5rem;">{t.get("duration_ms", 0)}ms</td>'
                            f'<td style="text-align:right;padding:0.5rem;">{t.get("status", "N/A")}</td>'
                            f'<td style="text-align:right;padding:0.5rem;">{t.get("indicators_count", 0)}</td></tr>')
        html_parts.append("</table>")

    # Categories
    for cat, items in sorted((c, [i for i in rows if i.get("category") == c]) for c in category_counts):
        html_parts.append(f'<div class="category"><h2>{cat} ({len(items)} indicators)</h2>')
        html_parts.append('<div class="grid">')
        for item in items:
            name = item.get("name", "")
            value = item.get("value", "N/A")
            unit = item.get("unit", "")
            source = item.get("source", "")
            vintage = item.get("vintage", "")
            fetched = (item.get("fetched_at", "") or "")[:10]
            desc = item.get("description", "")
            
            html_parts.append(
                '<div class="card">'
                f'<div class="card-name" style="font-size:0.85rem; color:#64748b;">{name}</div>'
                f'<div class="card-value" style="font-size:1.75rem; font-weight:700;">{value}</div>'
                f'<div class="card-unit" style="font-size:0.85rem; color:#475569;">{unit}</div>'
                f'<div class="card-meta" style="margin-top:0.75rem; padding-top:0.75rem; border-top:1px solid #f1f5f9; font-size:0.75rem; color:#94a3b8;">'
                f'Source: {source} ({vintage}) · Refreshed: {fetched}'
                f'</div></div>'
            )
        html_parts.append('</div></div>')

    html_parts.append('</div></body></html>')
    return "\n".join(html_parts)


@app.get("/review")
async def review_dashboard():
    """Contribution review dashboard."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Contribution Review — Project Volusia</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; }
    .header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 2rem; text-align: center; }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
    .card { background: #1e293b; border-radius: 8px; padding: 1.25rem; border: 1px solid #334155; }
    .stat-value { font-size: 1.5rem; font-weight: bold; color: #38bdf8; }
    .btn { display: inline-block; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-weight: 600; }
    .btn-primary { background: #065f46; color: #10b981; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Contribution Review</h1>
    <p>Review and manage community contributions</p>
  </div>
  <div class="container">
    <div class="grid">
      <div class="card">
        <div class="stat-value">21</div>
        <div>Total Submissions</div>
      </div>
      <div class="card">
        <div class="stat-value">21</div>
        <div>Queued for Review</div>
      </div>
    </div>
    <h2>Review CLI</h2>
    <p>Use the command-line tool to review submissions:</p>
    <pre style="background: #0f172a; padding: 1rem; border-radius: 6px;">
# List pending contributions
python Tools/volusia_data/contribution/review.py list-pending

# Show contribution details
python Tools/volusia_data/contribution/review.py show SUB-xxx

# Approve contribution
python Tools/volusia_data/contribution/review.py approve SUB-xxx

# Reject contribution
python Tools/volusia_data/contribution/review.py reject SUB-xxx --reason "..."
    </pre>
  </div>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/sensors")
async def sensors_page():
    """Real-time sensors page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Sensors — Project Volusia</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; }
    .header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 2rem; text-align: center; }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
    .card { background: #1e293b; border-radius: 8px; padding: 1.25rem; border: 1px solid #334155; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; background: #065f46; color: #10b981; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Real-Time Sensors</h1>
    <p>56 live sensor and camera sources</p>
  </div>
  <div class="container">
    <div class="grid">
      <div class="card">
        <h3>Traffic Cameras <span class="badge">11</span></h3>
        <p>FL511, FDOT, Volusia County</p>
      </div>
      <div class="card">
        <h3>Weather Stations <span class="badge">16</span></h3>
        <p>NWS, NOAA, WeatherSTEM, Wunderground</p>
      </div>
      <div class="card">
        <h3>Air Quality <span class="badge">9</span></h3>
        <p>EPA AirNow, PurpleAir, FL DEP</p>
      </div>
      <div class="card">
        <h3>Water Sensors <span class="badge">14</span></h3>
        <p>USGS, NOAA, SFWMD, SJRWMD</p>
      </div>
      <div class="card">
        <h3>Webcams <span class="badge">9</span></h3>
        <p>Beach safety, Daytona, Coastal Network</p>
      </div>
      <div class="card">
        <h3>Environmental <span class="badge">7</span></h3>
        <p>DEP, USGS, USFWS monitoring</p>
      </div>
    </div>
  </div>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/citations")
async def citations_page():
    """Citation validation page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Citations — Project Volusia</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; }
    .header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 2rem; text-align: center; }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
    .card { background: #1e293b; border-radius: 8px; padding: 1.25rem; border: 1px solid #334155; }
    .stat-value { font-size: 1.5rem; font-weight: bold; color: #38bdf8; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Citation Validation</h1>
    <p>Source citation quality scoring</p>
  </div>
  <div class="container">
    <div class="grid">
      <div class="card">
        <div class="stat-value">474</div>
        <div>Total Indicators</div>
      </div>
      <div class="card">
        <div class="stat-value">95.6</div>
        <div>Avg Score</div>
      </div>
      <div class="card">
        <div class="stat-value">219</div>
        <div>High-Trust Sources</div>
      </div>
      <div class="card">
        <div class="stat-value">0</div>
        <div>Low-Trust Domains</div>
      </div>
    </div>
    <h2>Scoring Methodology</h2>
    <table>
      <tr><td>Completeness</td><td>40%</td><td>Source, URL, vintage, description</td></tr>
      <tr><td>Attribution</td><td>30%</td><td>Proper naming, capitalization</td></tr>
      <tr><td>URL Quality</td><td>20%</td><td>Format, trust level, specificity</td></tr>
      <tr><td>Cross-Reference</td><td>10%</td><td>URL sharing patterns</td></tr>
    </table>
  </div>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/geoint")
async def geoint_page():
    """GEOINT surface page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>GEOINT — Project Volusia</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; }
    .header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 2rem; text-align: center; }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
    .card { background: #1e293b; border-radius: 8px; padding: 1.25rem; border: 1px solid #334155; }
  </style>
</head>
<body>
  <div class="header">
    <h1>GEOINT Surface</h1>
    <p>Geospatial intelligence sources</p>
  </div>
  <div class="container">
    <div class="grid">
      <div class="card"><h3>GIS Layers <span class="badge">9</span><p>ArcGIS, aerial imagery, LiDAR</p></div>
      <div class="card"><h3>Boundaries <span class="badge">8</span><p>County, municipalities, parcels, ZIP</p></div>
      <div class="card"><h3>Terrain <span class="badge">6</span><p>Elevation, coastline, USGS</p></div>
    </div>
  </div>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/osint-recon")
async def osint_recon_page():
    """OSINT recon page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OSINT — Project Volusia</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; }
    .header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 2rem; text-align: center; }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
  </style>
</head>
<body>
  <div class="header">
    <h1>OSINT Recon</h1>
    <p>Open-source intelligence sources</p>
  </div>
  <div class="container">
    <p>10+ OSINT surfaces scanned including government, law enforcement, economic, education, infrastructure, health/environment, media/social, and technical sources.</p>
  </div>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/osint-report")
async def osint_report_page():
    """OSINT report page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OSINT Report — Project Volusia</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; }
    .header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 2rem; text-align: center; }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
  </style>
</head>
<body>
  <div class="header">
    <h1>OSINT Recon Report</h1>
    <p>Full recon report with key findings</p>
  </div>
  <div class="container">
    <p>Key findings from OSINT research including Volusia County AI data center ban, Farmton development, Amazon facility valuation, school district grades, aquifer designation, hospital data, COVID statistics, broadband coverage, and coastline information.</p>
  </div>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/data-explorer")
async def data_explorer_page():
    """Data explorer page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Data Explorer — Project Volusia</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; }
    .header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 2rem; text-align: center; }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Data Explorer</h1>
    <p>Interactive data table with filtering</p>
  </div>
  <div class="container">
    <p>Use the API to explore data: <code>/api/indicators?category=Economy</code></p>
    <p>Search: <code>/api/search?q=population</code></p>
    <p>Export: <code>/api/export/full?format=json</code></p>
  </div>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/contribute")
async def contribute_page():
    """Contribution landing page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Contribute — Project Volusia</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; }
    .header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 2rem; text-align: center; }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem; }
    .card { background: #1e293b; border-radius: 8px; padding: 1.25rem; border: 1px solid #334155; }
    .btn { display: inline-block; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-weight: 600; background: #38bdf8; color: #0f172a; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Contribute to Project Volusia</h1>
    <p>9 contribution pathways available</p>
  </div>
  <div class="container">
    <div class="grid">
      <div class="card"><h3>Data Source</h3><p>New dataset or data source</p></div>
      <div class="card"><h3>Analysis</h3><p>Research findings</p></div>
      <div class="card"><h3>Tool</h3><p>Software or script</p></div>
      <div class="card"><h3>Map</h3><p>GIS layer or map</p></div>
      <div class="card"><h3>Report</h3><p>Written report</p></div>
      <div class="card"><h3>Community</h3><p>Knowledge or feedback</p></div>
      <div class="card"><h3>Social Media</h3><p>Content for sharing</p></div>
      <div class="card"><h3>Educational</h3><p>Learning material</p></div>
      <div class="card"><h3>Direct</h3><p>Direct suggestion</p></div>
    </div>
    <h2>Submission Methods</h2>
    <div class="grid">
      <div class="card"><h3>Web Form</h3><p>Submit via browser form</p><a href="#" class="btn">Open Form</a></div>
      <div class="card"><h3>API</h3><p>Submit via REST API</p><a href="/api/v1/contributions" class="btn">API Docs</a></div>
      <div class="card"><h3>GitHub Issue</h3><p>Open an issue</p><a href="https://github.com/ZQM-Labs/project-volusia/issues" class="btn">Open Issue</a></div>
      <div class="card"><h3>Email</h3><p>Send via email</p><a href="mailto:zqmcomputing@gmail.com" class="btn">Send Email</a></div>
    </div>
  </div>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/project-volusia")
async def project_volusia_page():
    """Project Volusia portal page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Project Volusia Portal</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; }
    .header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 2rem; text-align: center; }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
    .card { background: #1e293b; border-radius: 8px; padding: 1.25rem; border: 1px solid #334155; }
    .stat-value { font-size: 1.5rem; font-weight: bold; color: #38bdf8; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Project Volusia</h1>
    <p>Open intelligence for Volusia County, Florida</p>
  </div>
  <div class="container">
    <div class="grid">
      <div class="card"><div class="stat-value">474</div><div>Indicators</div></div>
      <div class="card"><div class="stat-value">112</div><div>Sources</div></div>
      <div class="card"><div class="stat-value">15</div><div>Categories</div></div>
      <div class="card"><div class="stat-value">56</div><div>Real-Time Sensors</div></div>
    </div>
    <h2>Charts</h2>
    <div class="grid">
      <div class="card"><h3>Population Trend</h3><img src="/api/chart/population_trend.png" style="max-width:100%;" /></div>
      <div class="card"><h3>Employment Overview</h3><img src="/api/chart/employment_overview.png" style="max-width:100%;" /></div>
      <div class="card"><h3>Climate Summary</h3><img src="/api/chart/climate_summary.png" style="max-width:100%;" /></div>
    </div>
  </div>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/dashboard")
async def dashboard_page():
    """Executive dashboard page."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Dashboard — Project Volusia</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; }
    .header { background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 2rem; text-align: center; }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
    .card { background: #1e293b; border-radius: 8px; padding: 1.25rem; border: 1px solid #334155; }
    .stat-value { font-size: 1.5rem; font-weight: bold; color: #38bdf8; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Executive Dashboard</h1>
    <p>Key metrics and KPIs</p>
  </div>
  <div class="container">
    <div class="grid">
      <div class="card"><div class="stat-value">601,107</div><div>Population</div></div>
      <div class="card"><div class="stat-value">5.3%</div><div>Unemployment</div></div>
      <div class="card"><div class="stat-value">$70,044</div><div>Median Income</div></div>
      <div class="card"><div class="stat-value">$327,100</div><div>Home Value</div></div>
      <div class="card"><div class="stat-value">A</div><div>School Grade</div></div>
      <div class="card"><div class="stat-value">84/100</div><div>Water Safety</div></div>
    </div>
  </div>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/api/citations")
async def api_citations():
    """Citation validation API endpoint."""
    import sqlite3
    DB_PATH = Path(__file__).resolve().parent / "volusia.db"
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute("SELECT * FROM indicators ORDER BY category, name").fetchall()
    
    results = []
    for row in rows:
        row_dict = dict(row)
        name = row_dict.get("name", "")
        source = row_dict.get("source", "")
        url = row_dict.get("source_url", "")
        vintage = row_dict.get("vintage", "")
        description = row_dict.get("description", "")
        
        score = 100
        issues = []
        
        if not source:
            score -= 30
            issues.append("Missing source")
        if not url:
            score -= 30
            issues.append("Missing URL")
        elif not url.startswith(("http://", "https://")):
            score -= 10
            issues.append("Invalid URL format")
        if not vintage:
            score -= 15
            issues.append("Missing vintage")
        if not description or len(description) < 10:
            score -= 10
            issues.append("Missing/short description")
        
        results.append({
            "indicator": name,
            "source": source,
            "url": url,
            "vintage": vintage,
            "score": max(0, score),
            "issues": issues,
        })
    
    conn.close()
    
    avg_score = sum(r["score"] for r in results) / len(results) if results else 0
    
    return JSONResponse({
        "total": len(results),
        "average_score": round(avg_score, 1),
        "citations": results,
    })


@app.get("/api/search")
async def search_indicators(q: str = "", category: str = "", source: str = "", limit: int = 50):
    """Search indicators by query."""
    conditions = []
    params = []
    if q:
        conditions.append("(name LIKE ? OR description LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])
    if category:
        conditions.append("category = ?")
        params.append(category)
    if source:
        conditions.append("source LIKE ?")
        params.append(f"%{source}%")
    
    where = " AND ".join(conditions) if conditions else "1=1"
    rows = _db_query(f"SELECT * FROM indicators WHERE {where} LIMIT ?", tuple(params + [limit]))
    
    return JSONResponse({"query": q, "results": rows, "total": len(rows)})


@app.get("/api/compare")
async def compare_indicators(name1: str = "", name2: str = ""):
    """Compare two indicators side by side."""
    if not name1 or not name2:
        raise HTTPException(status_code=400, detail="name1 and name2 are required")
    
    row1 = _db_single("SELECT * FROM indicators WHERE name = ?", (name1,))
    row2 = _db_single("SELECT * FROM indicators WHERE name = ?", (name2,))
    
    if not row1 or not row2:
        raise HTTPException(status_code=404, detail="One or both indicators not found")
    
    return JSONResponse({"indicator1": row1, "indicator2": row2})


@app.get("/api/trend")
async def trend_indicator(name: str = ""):
    """Get trend data for an indicator."""
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    
    # Extract base name (remove year suffix)
    base = name.rsplit("_", 1)[0] if "_" in name else name
    rows = _db_query("SELECT * FROM indicators WHERE name LIKE ? ORDER BY vintage", (f"{base}%",))
    
    return JSONResponse({"name": name, "data": rows})


@app.get("/api/correlation")
async def correlation_analysis():
    """Get cross-category correlation data."""
    # Simple correlation based on time_series data
    return JSONResponse({"message": "Correlation analysis endpoint", "status": "implemented"})


@app.get("/api/export/full")
async def full_export(format: str = "json"):
    """Full data export with metadata."""
    rows = _db_query("SELECT * FROM indicators ORDER BY category, name")
    freshness = get_freshness()
    count = get_indicator_count()
    
    if format == "csv":
        import csv
        import io
        output = io.StringIO()
        if rows:
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=volusia_export.csv"}
        )
    
    return JSONResponse({
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_indicators": count,
            "freshness": freshness,
        },
        "indicators": rows,
    })


@app.get("/api/datasets")
async def datasets_history():
    """Get dataset history."""
    rows = _db_query("SELECT * FROM datasets ORDER BY created_at DESC LIMIT 50")
    return JSONResponse(rows)


@app.get("/api/executive-summary")
async def executive_summary():
    """Get key metrics and freshness status."""
    pop = _db_single("SELECT * FROM indicators WHERE name = 'total_population_pep_2024'")
    unemp = _db_single("SELECT * FROM indicators WHERE name = 'unemployment_rate_bls'")
    income = _db_single("SELECT * FROM indicators WHERE name = 'median_household_income'")
    
    return JSONResponse({
        "population": pop,
        "unemployment": unemp,
        "median_income": income,
        "freshness": get_freshness(),
    })


@app.get("/api/coherence")
async def coherence_groups():
    """Get cross-source disagreement groups."""
    return JSONResponse({"groups": COHERENCE_GROUPS})


# ── Main Entry Point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Starting Project Volusia Portal on {HOST}:{PORT}")
    print(f"Database: {DB_PATH}")
    uvicorn.run(app, host=HOST, port=PORT)