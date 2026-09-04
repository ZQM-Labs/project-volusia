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
import sys
import sqlite3
import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path

# --- Force clean import (script mode only) ---
# P1-023 fix: this used to run unconditionally at module level, deleting this
# module's OWN sys.modules entry while it was still executing — so ANY import
# of volusia_data.portal_app died with KeyError at importlib finalization
# (script runs were unaffected because the module registers as "__main__").
# Guarded to script mode to preserve the original flush intent.
if __name__ == "__main__":
    for _key in list(sys.modules.keys()):
        if "volusia" in _key:
            del sys.modules[_key]

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, StreamingResponse

app = FastAPI(title="Project Volusia — Open Data Portal")

# DB path
DB_PATH = Path(
    os.environ.get(
        "VOLUSIA_DB_PATH",
        str(Path(__file__).resolve().parent / "volusia.db"),
    )
)

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
</style>
"""

# ── Coherence groups ──────────────────────────────────────────────────
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
            "PEP = Census Population Estimates (official counts). "
            "ACS = American Community Survey (survey-based, 5-year estimates). "
            "BEA = Bureau of Economic Analysis (economic geography). "
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
            "Different from Census money income."
        ),
    },
    "employment": {
        "label": "Employment",
        "indicator_names": ["employment_qcew", "unemployment_rate_bls"],
        "unit": "mixed",
        "note": (
            "QCEW employment counts jobs at establishments. "
            "BLS LAUS unemployment rate measures labor force status of residents. "
            "These measure different things — don't divide one by the other."
        ),
    },
}


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
        numeric_vals = []
        for r in rows:
            try:
                numeric_vals.append(float(r["value"]))
            except (ValueError, TypeError):
                pass
        if len(numeric_vals) >= 2:
            spread = max(numeric_vals) - min(numeric_vals)
            if spread > 0:
                disagreements.append(
                    {
                        "group_key": group_key,
                        "group_label": group["label"],
                        "note": group["note"],
                        "indicators": rows,
                        "spread": spread,
                    }
                )
    return disagreements


@app.get("/", response_class=HTMLResponse)
def index():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    if not rows:
        return "<html><body><h1>Project Volusia</h1><p>No data loaded yet. Run refresh_v2.py first.</p></body></html>"

    freshness = _get_freshness()
    category_counts = _get_category_counts()
    total = len(rows)
    disagreements = _get_coherence_disagreements()

    html_parts = [
        "<html><head><title>Project Volusia — Open Data Portal</title>",
        CSS_STYLE,
        "</head><body>",
        '<div class="header">',
        "<h1>Project Volusia</h1>",
        "<p>Open Data Portal for Volusia County, Florida</p>",
        '<div class="stats">',
        f'<div class="stat"><div class="stat-value">{total}</div><div class="stat-label">Indicators</div></div>',
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

    if disagreements:
        html_parts.append('<div class="coherence-note">')
        html_parts.append("<strong>Multiple sources, different numbers</strong>")
        html_parts.append(
            "<p>The indicators below measure the same real-world quantity "
            "from different sources with different methodologies and vintages. "
            "Read them as a range, not a single number.</p>"
        )
        html_parts.append('<div class="coherence-grid">')
        for d in disagreements:
            vals_html = ""
            for ind in d["indicators"]:
                try:
                    val = float(ind["value"])
                    vals_html += f"<span>{ind['name']}: {ind['value']} ({ind['source']}, {ind['vintage']})</span>"
                except (ValueError, TypeError):
                    pass
            html_parts.append(
                f'<div class="coherence-card">'
                f"<h4>{d['group_label']}</h4>"
                f'<div class="values">{vals_html}</div>'
                f"<p>{d['note']}</p>"
                f"</div>"
            )
        html_parts.append("</div></div>")

    categories = {}
    for row in rows:
        cat = row.get("category") or "Uncategorized"
        categories.setdefault(cat, []).append(row)

    for cat, items in sorted(categories.items()):
        html_parts.append('<div class="category">')
        html_parts.append('<div class="category-header">')
        html_parts.append(f'<span class="category-title">{cat}</span>')
        html_parts.append(f'<span class="category-count">{len(items)} indicators</span>')
        html_parts.append("</div>")
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
            html_parts.append(f"<div>Refreshed: {fetched}</div>")
            if description:
                html_parts.append(f'<div style="margin-top:0.5rem; font-style:italic;">{description}</div>')
            html_parts.append("</div></div>")
        html_parts.append("</div></div>")

    html_parts.append('<div class="footer">')
    html_parts.append(
        '<p>Project Volusia &middot; ZQM Labs &middot; <a href="https://github.com/ZQM-Computing">GitHub</a></p>'
    )
    html_parts.append("<p>Data from public U.S. government sources (Census, BLS, BEA, NOAA).</p>")
    html_parts.append("</div></div></body></html>")

    return "".join(html_parts)


@app.get("/contribute", response_class=HTMLResponse)
def contribute_page():
    """Serve the contribution landing page."""
    # Try multiple locations for the contribute page
    locations = [
        Path(__file__).resolve().parent / "portal" / "contribute.html",
        Path(__file__).resolve().parent.parent.parent / "contribute.html",
    ]
    for loc in locations:
        if loc.exists():
            return HTMLResponse(loc.read_text(encoding="utf-8"))
    return HTMLResponse("<html><body><h1>Contribute</h1><p>Contribution form loading...</p></body></html>")


@app.get("/project-volusia", response_class=HTMLResponse)
def project_volusia_portal():
    """Serve the Project Volusia portal page."""
    portal_html = Path(__file__).resolve().parent.parent.parent / "project-volusia.html"
    if portal_html.exists():
        return HTMLResponse(portal_html.read_text(encoding="utf-8"))
    return HTMLResponse("""<html><head><meta http-equiv="refresh" content="0; url=/"></head>
<body><p>Redirecting to <a href="/">Project Volusia Portal</a>...</p></body></html>""")


@app.get("/api/indicators")
def api_indicators():
    rows = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    for row in rows:
        for group_key, group in COHERENCE_GROUPS.items():
            if row["name"] in group["indicator_names"]:
                row["coherence_group"] = group_key
                row["coherence_group_label"] = group["label"]
                row["coherence_note"] = group["note"]
    return {
        "count": len(rows),
        "indicators": rows,
        "coherence_groups": list(COHERENCE_GROUPS.keys()),
    }


# ── Chart endpoints (matplotlib) ─────────────────────────────────────
def _chart_response(fig):
    """Convert matplotlib fig to PNG Response."""
    import io
    import matplotlib.pyplot as plt
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return Response(content=buf.read(), media_type="image/png")


def _chart_no_data_response(message):
    """Return a small placeholder PNG when no data is available."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import io
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=14, color='#64748b')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    fig.tight_layout()
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return Response(content=buf.read(), media_type="image/png")


@app.get("/api/chart/population_trend.png")
def chart_population_trend():
    """Line chart: Census PEP population 2020-2024."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = _db_rows(
        "SELECT name, value FROM indicators WHERE name LIKE 'total_population_pep_%' ORDER BY name"
    )
    years = []
    pops = []
    for r in rows:
        year = r["name"].split("_")[-1]
        try:
            val = int(r["value"])
        except (ValueError, TypeError):
            continue
        years.append(year)
        pops.append(val)

    if not years:
        return _chart_no_data_response("No population data available.\nRun refresh_v2.py to fetch data.")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(years, pops, marker="o", color="#1e3a5f", linewidth=2)
    ax.fill_between(years, pops, alpha=0.1, color="#1e3a5f")
    ax.set_title("Volusia County Population (Census PEP)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Population")
    ax.grid(True, alpha=0.3)
    for i, v in enumerate(pops):
        ax.annotate(f"{v:,}", (years[i], v), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=9)
    fig.tight_layout()
    return _chart_response(fig)


@app.get("/api/chart/employment_overview.png")
def chart_employment_overview():
    """Bar chart: QCEW establishments, employment, weekly wage."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = _db_rows(
        "SELECT name, value, unit FROM indicators WHERE name IN "
        "('establishments_qcew','employment_qcew','avg_weekly_wage_qcew')"
    )
    labels = []
    values = []
    for r in rows:
        label = r["name"].replace("_qcew", "").replace("_", " ").title()
        try:
            val = float(r["value"])
        except (ValueError, TypeError):
            continue
        labels.append(label)
        values.append(val)

    if not labels:
        return _chart_no_data_response("No employment data available.\nRun refresh_v2.py to fetch data.")

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["#1e3a5f", "#2b6cb0", "#63b3ed"]
    bars = ax.bar(labels, values, color=colors[: len(labels)])
    ax.set_title("Volusia County Employment Overview (QCEW 2024)")
    ax.set_ylabel("Value")
    ax.grid(True, alpha=0.3, axis="y")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{val:,.0f}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    return _chart_response(fig)


@app.get("/api/chart/unemployment_trend.png")
def chart_unemployment_trend():
    """Line chart: BLS LAUS unemployment rate over time."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = _db_rows(
        "SELECT vintage, value FROM time_series WHERE indicator_name = 'unemployment_rate_bls' ORDER BY fetched_at"
    )
    
    if not rows:
        return _chart_no_data_response("No unemployment data available.\nRun refresh_v2.py to fetch data.")
    
    periods = []
    rates = []
    for r in rows:
        try:
            val = float(r["value"])
            periods.append(r["vintage"])
            rates.append(val)
        except (ValueError, TypeError):
            continue
    
    if not periods:
        return _chart_no_data_response("No unemployment data available.")
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(periods, rates, marker="o", color="#dc2626", linewidth=2)
    ax.fill_between(range(len(rates)), rates, alpha=0.1, color="#dc2626")
    ax.set_title("Volusia County Unemployment Rate (BLS LAUS)")
    ax.set_xlabel("Period")
    ax.set_ylabel("Unemployment Rate (%)")
    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels(periods, rotation=45, ha="right")
    ax.grid(True, alpha=0.3)
    for i, v in enumerate(rates):
        ax.annotate(f"{v:.1f}%", (i, v), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=9)
    fig.tight_layout()
    return _chart_response(fig)


@app.get("/api/chart/wage_trend.png")
def chart_wage_trend():
    """Line chart: QCEW average weekly wage over time."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = _db_rows(
        "SELECT vintage, value FROM time_series WHERE indicator_name = 'avg_weekly_wage_qcew' ORDER BY fetched_at"
    )
    
    if not rows:
        return _chart_no_data_response("No wage data available.\nRun refresh_v2.py to fetch data.")
    
    periods = []
    wages = []
    for r in rows:
        try:
            val = float(r["value"])
            periods.append(r["vintage"])
            wages.append(val)
        except (ValueError, TypeError):
            continue
    
    if not periods:
        return _chart_no_data_response("No wage data available.")
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(periods, wages, marker="o", color="#059669", linewidth=2)
    ax.fill_between(range(len(wages)), wages, alpha=0.1, color="#059669")
    ax.set_title("Volusia County Avg Weekly Wage (BLS QCEW)")
    ax.set_xlabel("Period")
    ax.set_ylabel("Avg Weekly Wage (USD)")
    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels(periods, rotation=45, ha="right")
    ax.grid(True, alpha=0.3)
    for i, v in enumerate(wages):
        ax.annotate(f"${v:,.0f}", (i, v), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=9)
    fig.tight_layout()
    return _chart_response(fig)


@app.get("/api/chart/climate_summary.png")
def chart_climate_summary():
    """Bar chart: NOAA 2024 temperature and precipitation summary."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = _db_rows(
        "SELECT name, value, unit FROM indicators WHERE name LIKE 'avg_%_temp_2024' OR name = 'total_precip_2024'"
    )
    labels = []
    values = []
    for r in rows:
        label = r["name"].replace("_2024", "").replace("_", " ").title()
        try:
            val = float(r["value"])
        except (ValueError, TypeError):
            continue
        labels.append(label)
        values.append(val)

    if not labels:
        return _chart_no_data_response("No climate data available.\nRun refresh_v2.py to fetch data.")

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["#c53030", "#dd6b20", "#38a169"]
    bars = ax.bar(labels, values, color=colors[: len(labels)])
    ax.set_title("Volusia County Climate Summary 2024 (NOAA NCEI)")
    ax.set_ylabel("Value (tenths C / tenths mm)")
    ax.grid(True, alpha=0.3, axis="y")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{val:,.1f}", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    return _chart_response(fig)


@app.get("/api/coherence")
def api_coherence():
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
    fieldnames = [
        "id",
        "name",
        "value",
        "unit",
        "category",
        "source",
        "source_url",
        "vintage",
        "fetched_at",
        "description",
        "coherence_group",
        "coherence_note",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
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
    return {
        "status": "healthy" if db_exists and indicator_count > 0 else "degraded",
        "db_exists": db_exists,
        "db_path": str(DB_PATH),
        "indicator_count": indicator_count,
        "latest_refresh": freshness,
    }


@app.get("/api/status")
def api_status():
    indicators = _db_rows("SELECT * FROM indicators ORDER BY fetched_at DESC")
    latest_update = indicators[0]["fetched_at"] if indicators else "N/A"
    disagreements = _get_coherence_disagreements()
    categories = _get_category_counts()
    return {
        "system": "Project Volusia Open Data Portal",
        "status": "operational" if indicators else "degraded",
        "version": "2.0.0-coherent",
        "total_indicators": len(indicators),
        "latest_update": latest_update,
        "source_disagreements": len(disagreements),
        "categories": categories,
        "sla": {
            "data_freshness": "Monthly refresh",
            "uptime_target": "99.9%",
            "refresh_cadence": "BLS/NOAA: monthly | Census ACS: annual | BEA: annual | QCEW: quarterly",
        },
        "endpoints": {
            "homepage": "/",
            "contribute": "/contribute",
            "project_volusia": "/project-volusia",
            "indicators": "/api/indicators",
            "coherence": "/api/coherence",
            "export_csv": "/api/export/csv",
            "export_json": "/api/export/json",
            "datasets": "/api/datasets",
            "health": "/api/health",
            "status": "/api/status",
            "executive_summary": "/api/executive-summary",
            "chart_population": "/api/chart/population_trend.png",
            "chart_employment": "/api/chart/employment_overview.png",
            "chart_climate": "/api/chart/climate_summary.png",
        },
    }


@app.get("/api/executive-summary")
def api_executive_summary():
    """Executive briefing: key metrics, trends, and alerts."""
    indicators = _db_rows("SELECT * FROM indicators ORDER BY category, name")
    
    # Build metrics
    metrics = {}
    for ind in indicators:
        name = ind["name"]
        try:
            val = float(ind["value"])
        except (ValueError, TypeError):
            continue
        metrics[name] = {
            "value": val,
            "unit": ind["unit"],
            "source": ind["source"],
            "vintage": ind["vintage"],
        }
    
    # Key headlines
    headlines = []
    if "total_population_pep_2024" in metrics:
        pop = metrics["total_population_pep_2024"]
        headlines.append({
            "metric": "Population",
            "value": f"{pop['value']:,.0f}",
            "unit": pop["unit"],
            "source": pop["source"],
            "vintage": pop["vintage"],
        })
    if "unemployment_rate_bls" in metrics:
        ur = metrics["unemployment_rate_bls"]
        headlines.append({
            "metric": "Unemployment Rate",
            "value": f"{ur['value']:.1f}%",
            "unit": ur["unit"],
            "source": ur["source"],
            "vintage": ur["vintage"],
        })
    if "employment_qcew" in metrics:
        emp = metrics["employment_qcew"]
        headlines.append({
            "metric": "Employment",
            "value": f"{emp['value']:,.0f}",
            "unit": emp["unit"],
            "source": emp["source"],
            "vintage": emp["vintage"],
        })
    if "establishments_qcew" in metrics:
        est = metrics["establishments_qcew"]
        headlines.append({
            "metric": "Business Establishments",
            "value": f"{est['value']:,.0f}",
            "unit": est["unit"],
            "source": est["source"],
            "vintage": est["vintage"],
        })
    if "avg_weekly_wage_qcew" in metrics:
        wage = metrics["avg_weekly_wage_qcew"]
        headlines.append({
            "metric": "Avg Weekly Wage",
            "value": f"${wage['value']:,.0f}",
            "unit": wage["unit"],
            "source": wage["source"],
            "vintage": wage["vintage"],
        })
    
    # Data freshness summary
    fresh_count = 0
    stale_count = 0
    now = datetime.now(timezone.utc)
    for ind in indicators:
        fetched = ind.get("fetched_at")
        if fetched:
            try:
                fetched_dt = datetime.fromisoformat(fetched)
                age = (now - fetched_dt).days
                if age <= 30:
                    fresh_count += 1
                else:
                    stale_count += 1
            except (ValueError, TypeError):
                pass
    
    # System status
    operational = len(indicators) > 0 and stale_count < 3
    
    return {
        "generated_at": now.isoformat(),
        "system": "Project Volusia",
        "status": "operational" if operational else "degraded",
        "headlines": headlines,
        "data_freshness": {
            "fresh": fresh_count,
            "stale": stale_count,
            "total": fresh_count + stale_count,
        },
        "contribution_url": "/contribute",
        "api_docs": "/api/status",
    }


@app.get("/api/coherence/groups")
def api_coherence_groups():
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

    host = os.environ.get("VOLUSIA_PORTAL_HOST", "127.0.0.1")
    port = int(os.environ.get("VOLUSIA_PORTAL_PORT", "8789"))
    print(f"Starting Project Volusia Portal v2.0-coherent on http://{host}:{port}")
    print(f"Database: {DB_PATH}")

    # Auto-initialize DB if it doesn't exist
    if not DB_PATH.exists():
        print("Database not found, initializing...")
        init_db()

    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH))
        count = conn.execute("SELECT COUNT(*) FROM indicators").fetchone()[0]
        print(f"Indicators loaded: {count}")
        conn.close()
    print(f"Coherence groups: {list(COHERENCE_GROUPS.keys())}")

    # Mount contribution web form if available
    try:
        from volusia_data.portal_contribute import router as contribute_router
        app.mount("/contribute", contribute_router)
        print("Contribution form mounted at /contribute")
    except ImportError:
        print("Contribution form not available (portal_contribute.py not found)")

    uvicorn.run(app, host=host, port=port)
