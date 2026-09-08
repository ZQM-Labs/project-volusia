"""HTML page templates for Project Volusia portal.

Contains functions to render HTML pages for the dashboard and other UI pages.
Separated from route handlers to keep the main app file focused on routing logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def render_dashboard(
    rows: list[dict[str, Any]],
    freshness: str,
    category_counts: dict[str, int],
    disagreements: list[dict[str, Any]],
    timeline: list[dict[str, Any]],
) -> str:
    """Render the dashboard HTML (canonical layout; portal.css overrides inline styles)."""
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
        f'<div class="stat"><div class="stat-value">{len(rows)}</div><div class="stat-label">Indicators</div></div>',
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
        html_parts.append(
            '<tr><th style="text-align:left;padding:0.5rem;">Run ID</th>'
            '<th style="text-align:right;padding:0.5rem;">Duration</th>'
            '<th style="text-align:right;padding:0.5rem;">Status</th>'
            '<th style="text-align:right;padding:0.5rem;">Indicators</th></tr>'
        )
        for t in timeline[:10]:
            html_parts.append(
                f'<tr><td style="padding:0.5rem;">{t.get("run_id", "N/A")[:12]}</td>'
                f'<td style="text-align:right;padding:0.5rem;">{t.get("duration_ms", 0)}ms</td>'
                f'<td style="text-align:right;padding:0.5rem;">{t.get("status", "N/A")}</td>'
                f'<td style="text-align:right;padding:0.5rem;">{t.get("indicators_count", 0)}</td></tr>'
            )
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

            html_parts.append(
                '<div class="card">'
                f'<div class="card-name" style="font-size:0.85rem; color:#64748b;">{name}</div>'
                f'<div class="card-value" style="font-size:1.75rem; font-weight:700;">{value}</div>'
                f'<div class="card-unit" style="font-size:0.85rem; color:#475569;">{unit}</div>'
                f'<div class="card-meta" style="margin-top:0.75rem; padding-top:0.75rem; border-top:1px solid #f1f5f9; font-size:0.75rem; color:#94a3b8;">'
                f"Source: {source} ({vintage}) · Refreshed: {fetched}"
                f"</div></div>"
            )
        html_parts.append("</div></div>")

    html_parts.append("</div></body></html>")
    return "\n".join(html_parts)


def render_simple_page(title: str, content: str, subtitle: str = "", theme: str = "dark") -> str:
    """Render a simple HTML page with the given title and content."""
    bg_color = "#0f172a" if theme == "dark" else "#f5f5f5"
    text_color = "#e2e8f0" if theme == "dark" else "#1a1a1a"
    subtitle_html = f"\n        <p>{subtitle}</p>" if subtitle else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} — Project Volusia</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background: {bg_color}; color: {text_color}; margin: 0; }}
        .header {{ background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); padding: 2rem; text-align: center; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }}
        .card {{ background: #1e293b; border-radius: 8px; padding: 1.25rem; border: 1px solid #334155; }}
        .badge {{ background: #3b82f6; color: #fff; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>{subtitle_html}
    </div>
    <div class="container">
        {content}
    </div>
</body>
</html>"""


def render_error_page(message: str, status_code: int = 500) -> str:
    """Render an error page with the given message."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error — Project Volusia</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background: #f5f5f5; text-align: center; padding: 4rem; }}
        .error {{ color: #b00020; }}
    </style>
</head>
<body>
    <h1 class="error">Error {status_code}</h1>
    <p>{message}</p>
    <a href="/">Return to dashboard</a>
</body>
</html>"""
