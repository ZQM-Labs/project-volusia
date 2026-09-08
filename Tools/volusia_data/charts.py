"""Chart generation for Project Volusia portal.

Provides functions to generate matplotlib chart images from indicator data.
Each chart function returns a BytesIO buffer containing PNG image data.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

# Chart configuration
CHART_CONFIG = {
    "population_trend": {
        "query": "SELECT * FROM indicators WHERE name LIKE 'total_population_pep_%' ORDER BY vintage",
        "chart_type": "bar",
        "title": "Population Trend",
        "ylabel": "Population",
        "color": "#38bdf8",
    },
    "employment_overview": {
        "query": "SELECT * FROM indicators WHERE category = 'Economy' AND (name LIKE '%employment%' OR name LIKE '%establishments%') ORDER BY name",
        "chart_type": "barh",
        "title": "Employment Overview",
        "color": "#10b981",
    },
    "unemployment_trend": {
        "query": "SELECT * FROM indicators WHERE name LIKE '%unemployment%' ORDER BY vintage",
        "chart_type": "line",
        "title": "Unemployment Trend",
        "ylabel": "Rate (%)",
        "color": "#ef4444",
        "marker": "o",
    },
    "wage_trend": {
        "query": "SELECT * FROM indicators WHERE name LIKE '%wage%' ORDER BY vintage",
        "chart_type": "line",
        "title": "Wage Trend",
        "ylabel": "Weekly Wage ($)",
        "color": "#38bdf8",
        "marker": "s",
    },
    "income_overview": {
        "query": "SELECT * FROM indicators WHERE name LIKE '%income%' ORDER BY name",
        "chart_type": "barh",
        "title": "Income Overview",
        "color": "#10b981",
    },
    "housing_overview": {
        "query": "SELECT * FROM indicators WHERE category = 'Housing' ORDER BY name",
        "chart_type": "barh",
        "title": "Housing Overview",
        "color": "#f59e0b",
    },
    "demographics": {
        "query": "SELECT * FROM indicators WHERE category = 'Demographics' ORDER BY name",
        "chart_type": "bar",
        "title": "Demographics",
        "color": "#38bdf8",
        "rotate_labels": True,
    },
    "education_health": {
        "query": "SELECT * FROM indicators WHERE category IN ('Education', 'Health') ORDER BY category, name",
        "chart_type": "bar",
        "title": "Education & Health",
        "color": "#a855f7",
        "rotate_labels": True,
    },
    "traffic_overview": {
        "query": "SELECT * FROM indicators WHERE category = 'Transportation' ORDER BY name",
        "chart_type": "barh",
        "title": "Traffic Overview",
        "color": "#10b981",
    },
    "schools_by_type": {
        "query": "SELECT * FROM indicators WHERE name LIKE 'schools_%' ORDER BY name",
        "chart_type": "pie",
        "title": "Schools by Type",
    },
    "infrastructure": {
        "query": "SELECT * FROM indicators WHERE category = 'Infrastructure' ORDER BY name",
        "chart_type": "barh",
        "title": "Infrastructure",
        "color": "#f59e0b",
    },
    "climate_summary": {
        "query": "SELECT * FROM indicators WHERE category = 'Climate' ORDER BY name",
        "chart_type": "barh",
        "title": "Climate Summary",
        "color": "#06b6d4",
    },
}


def _extract_numeric_values(rows: list[sqlite3.Row]) -> tuple[list[str], list[float]]:
    """Extract labels and numeric values from database rows."""
    labels = []
    values = []
    for r in rows:
        try:
            val = float(r["value"])
            labels.append(r["name"][:15])
            values.append(val)
        except (ValueError, TypeError, KeyError):
            continue
    return labels[:10], values[:10]


def generate_chart(db_path: str | Path, chart_name: str) -> bytes | None:
    """Generate a chart image from the CHART_CONFIG configuration.

    Returns PNG image bytes or None if chart unknown or no data.
    """
    import io

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if chart_name not in CHART_CONFIG:
        return None

    config = CHART_CONFIG[chart_name]
    chart_type = config["chart_type"]

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(config["query"]).fetchall()
    finally:
        conn.close()

    if not rows:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))
    color = config.get("color", "#38bdf8")
    title = config["title"]

    if chart_type == "pie":
        values = [float(r["value"]) for r in rows if r["value"].replace(".", "").replace("-", "").isdigit()]
        labels = [r["name"] for r in rows if r["value"].replace(".", "").replace("-", "").isdigit()]
        if values:
            ax.pie(values, labels=labels, autopct="%1.0f%%")
            ax.set_title(title)
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
    else:
        labels, values = _extract_numeric_values(rows)
        if not values:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
        elif chart_type == "bar":
            ax.bar(labels, values, color=color)
            ax.set_title(title)
            if config.get("ylabel"):
                ax.set_ylabel(config["ylabel"])
            if config.get("rotate_labels"):
                ax.tick_params(axis="x", rotation=45)
        elif chart_type == "barh":
            ax.barh(labels, values, color=color)
            ax.set_title(title)
            if config.get("ylabel"):
                ax.set_ylabel(config["ylabel"])
        elif chart_type == "line":
            marker = config.get("marker", "o")
            ax.plot(labels, values, marker=marker, color=color)
            ax.set_title(title)
            if config.get("ylabel"):
                ax.set_ylabel(config["ylabel"])
            if config.get("rotate_labels"):
                ax.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()
