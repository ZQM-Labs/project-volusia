#!/usr/bin/env python3
"""
Project Volusia — Weekly Report Generator
Generates an HTML report from current data and templates.

Usage:
    python Tools/volusia_data/reports/generate_weekly.py
    python Tools/volusia_data/reports/generate_weekly.py --output Reports/weekly_2026-09-04.html
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add Tools to path
TOOLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))

from volusia_data.config import DB_PATH


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_indicators():
    """Load all current indicators."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM indicators ORDER BY category, name").fetchall()
    conn.close()
    
    indicators = {}
    for r in rows:
        indicators[r["name"]] = {
            "value": r["value"],
            "unit": r["unit"],
            "category": r["category"],
            "source": r["source"],
            "vintage": r["vintage"],
            "fetched_at": r["fetched_at"],
            "description": r["description"],
        }
    return indicators


def load_contributions():
    """Load recent contributions."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM submissions ORDER BY submitted_at DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def load_interviews():
    """Load recent interviews."""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM interviews ORDER BY interview_date DESC LIMIT 10"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception:
        conn.close()
        return []


def generate_html(indicators, contributions, interviews, output_path):
    """Generate the weekly report HTML."""
    
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    
    # Build indicator table rows
    indicator_rows = ""
    for name, data in sorted(indicators.items()):
        indicator_rows += f"""
        <tr>
            <td>{name}</td>
            <td><strong>{data['value']} {data['unit']}</strong></td>
            <td>{data['source']}</td>
            <td>{data['vintage']}</td>
            <td>{data['fetched_at'][:10] if data['fetched_at'] else 'N/A'}</td>
        </tr>"""
    
    # Build contributions section
    contrib_section = ""
    if contributions:
        contrib_rows = ""
        for c in contributions:
            contrib_rows += f"""
            <tr>
                <td>{c['submission_id']}</td>
                <td>{c['contribution_type']}</td>
                <td>{c['status']}</td>
                <td>{c['reviewer']}</td>
                <td>{c['submitted_at'][:10]}</td>
            </tr>"""
        contrib_section = f"""
        <h2>Recent Contributions</h2>
        <table>
            <tr><th>ID</th><th>Type</th><th>Status</th><th>Reviewer</th><th>Date</th></tr>
            {contrib_rows}
        </table>"""
    else:
        contrib_section = "<h2>Recent Contributions</h2><p>No contributions this week.</p>"
    
    # Build interviews section
    interview_section = ""
    if interviews:
        int_rows = ""
        for i in interviews:
            themes = json.loads(i.get("themes", "[]") or "[]")
            int_rows += f"""
            <tr>
                <td>{i['stakeholder_name'] or 'Anonymous'}</td>
                <td>{i['stakeholder_role']}</td>
                <td>{i['interview_date']}</td>
                <td>{', '.join(themes)}</td>
                <td>{'Yes' if i['follow_up_required'] else 'No'}</td>
            </tr>"""
        interview_section = f"""
        <h2>Recent Interviews</h2>
        <table>
            <tr><th>Name</th><th>Role</th><th>Date</th><th>Themes</th><th>Follow-up</th></tr>
            {int_rows}
        </table>"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Volusia — Weekly Report {now.strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; line-height: 1.6; background: #f8fafc; color: #1e293b; }}
        h1 {{ color: #0f172a; border-bottom: 2px solid #0f172a; padding-bottom: 0.5rem; }}
        h2 {{ color: #1e3a5f; margin-top: 2rem; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th, td {{ border: 1px solid #e2e8f0; padding: 10px 12px; text-align: left; font-size: 0.9rem; }}
        th {{ background: #0f172a; color: white; font-weight: 600; }}
        tr:nth-child(even) {{ background: #f8fafc; }}
        .meta {{ color: #64748b; font-size: 0.9rem; }}
        .footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 0.85rem; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
        .badge-queued {{ background: #fef3c7; color: #92400e; }}
        .badge-approved {{ background: #dcfce7; color: #166534; }}
        .badge-rejected {{ background: #fee2e2; color: #991b1b; }}
    </style>
</head>
<body>
    <h1>Project Volusia — Weekly Report</h1>
    <p class="meta">Generated: {now.strftime('%Y-%m-%d %H:%M UTC')} | Data sources: Census PEP, NOAA NCEI, BLS QCEW, BLS LAUS</p>
    
    <h2>Current Indicators</h2>
    <table>
        <tr><th>Indicator</th><th>Value</th><th>Source</th><th>Vintage</th><th>Last Updated</th></tr>
        {indicator_rows}
    </table>
    
    {contrib_section}
    
    {interview_section}
    
    <div class="footer">
        <p>Project Volusia &middot; ZQM Labs &middot; <a href="https://github.com/ZQM-Labs/project-volusia">GitHub</a></p>
        <p>Data from public U.S. government sources (Census, BLS, BEA, NOAA).</p>
    </div>
</body>
</html>"""
    
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"Report saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate weekly report")
    parser.add_argument("--output", default=None, help="Output HTML file path")
    args = parser.parse_args()
    
    if not DB_PATH.exists():
        print("ERROR: Database does not exist. Run refresh_v2.py first.")
        sys.exit(1)
    
    indicators = load_indicators()
    contributions = load_contributions()
    interviews = load_interviews()
    
    if not args.output:
        date_str = datetime.now().strftime("%Y-%m-%d")
        args.output = f"Reports/weekly_{date_str}.html"
    
    # Ensure output directory exists
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    generate_html(indicators, contributions, interviews, args.output)
    print(f"Indicators: {len(indicators)}")
    print(f"Contributions: {len(contributions)}")
    print(f"Interviews: {len(interviews)}")


if __name__ == "__main__":
    main()
