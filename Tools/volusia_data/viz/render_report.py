#!/usr/bin/env python3
"""
Project Volusia — Report Renderer
Render quarterly reports from templates and data.

Usage:
    python Tools/volusia_data/viz/render_report.py --template q4_2026.md --output report.html
"""

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone


def load_indicators_from_db(db_path):
    """Load current indicators from SQLite."""
    if not Path(db_path).exists():
        return {}
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.execute("SELECT name, value, unit, source, vintage FROM indicators ORDER BY category, name")
    indicators = {}
    for row in cur.fetchall():
        indicators[row["name"]] = {
            "value": row["value"],
            "unit": row["unit"],
            "source": row["source"],
            "vintage": row["vintage"],
        }
    conn.close()
    return indicators


def render_template(template_path, indicators, output_path):
    """Render a markdown template with indicator values."""
    
    template = Path(template_path).read_text(encoding="utf-8")
    
    # Replace {{indicator_name}} placeholders
    for name, data in indicators.items():
        placeholder = "{{" + name + "}}"
        value_str = f"{data['value']} {data['unit']}" if data['unit'] else data['value']
        template = template.replace(placeholder, value_str)
    
    # Replace {{date}}
    template = template.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
    
    # Convert markdown to HTML (basic)
    html = markdown_to_html(template)
    
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"Report saved to {output_path}")


def markdown_to_html(md):
    """Basic markdown to HTML conversion."""
    lines = md.split("\n")
    html_parts = []
    in_table = False
    
    html_parts.append("""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Project Volusia Report</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }
        h1 { color: #0f172a; border-bottom: 2px solid #0f172a; padding-bottom: 0.5rem; }
        h2 { color: #1e3a5f; margin-top: 2rem; }
        h3 { color: #2b6cb0; }
        table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #f4f4f4; }
        .footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; color: #666; font-size: 0.9rem; }
    </style>
</head>
<body>""")
    
    for line in lines:
        line = line.strip()
        
        if line.startswith("# "):
            html_parts.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_parts.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            html_parts.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if all(set(c) <= set("-: ") for c in cells):
                continue  # Skip separator
            if not in_table:
                html_parts.append("<table><thead><tr>")
                for c in cells:
                    html_parts.append(f"<th>{c}</th>")
                html_parts.append("</tr></thead><tbody>")
                in_table = True
            else:
                html_parts.append("<tr>")
                for c in cells:
                    html_parts.append(f"<td>{c}</td>")
                html_parts.append("</tr>")
        elif line.startswith("- "):
            html_parts.append(f"<li>{line[2:]}</li>")
        elif line == "":
            if in_table:
                html_parts.append("</tbody></table>")
                in_table = False
            html_parts.append("<br>")
        else:
            html_parts.append(f"<p>{line}</p>")
    
    if in_table:
        html_parts.append("</tbody></table>")
    
    html_parts.append('<div class="footer"><p>Project Volusia &middot; ZQM Labs &middot; Data from public U.S. government sources.</p></div>')
    html_parts.append("</body></html>")
    
    return "\n".join(html_parts)


def main():
    parser = argparse.ArgumentParser(description="Render quarterly report")
    parser.add_argument("--template", "-t", required=True, help="Markdown template file")
    parser.add_argument("--output", "-o", required=True, help="Output HTML file")
    parser.add_argument("--db", default="Tools/volusia_data/volusia.db", help="SQLite database path")
    args = parser.parse_args()

    template_path = Path(args.template)
    if not template_path.exists():
        print(f"ERROR: Template file not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    indicators = load_indicators_from_db(args.db)
    render_template(args.template, indicators, args.output)


if __name__ == "__main__":
    main()
