#!/usr/bin/env python3
"""
Project Volusia — Data Sync Script
Exports data from SQLite to JSON files for frontend consumption.

Usage:
    python scripts/sync_data.py
    
This script:
1. Exports all indicators to data/indicators.json
2. Exports by category to data/{category}.json
3. Exports map layers to data/map-layers.json
4. Exports datasets to data/datasets.json
5. Exports health check to data/health.json
6. Exports stakeholders to data/stakeholders.json
7. Exports news to data/news.json
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "Tools" / "volusia_data" / "volusia.db"
OUTPUT_DIR = Path(__file__).parent.parent / "data"

def export_indicators():
    """Export all indicators."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    cur = conn.execute("SELECT * FROM indicators ORDER BY category, name")
    indicators = [dict(r) for r in cur.fetchall()]
    
    with open(OUTPUT_DIR / "indicators.json", "w") as f:
        json.dump(indicators, f, indent=2)
    
    print(f"Exported {len(indicators)} indicators")
    return indicators

def export_by_category(indicators):
    """Export indicators by category."""
    categories = set(i["category"] for i in indicators)
    
    for cat in categories:
        cat_items = [i for i in indicators if i["category"] == cat]
        fname = cat.lower() + ".json"
        with open(OUTPUT_DIR / fname, "w") as f:
            json.dump(cat_items, f, indent=2)
        print(f"Exported {len(cat_items)} {cat} indicators")

def export_map_layers():
    """Export map layers."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    try:
        cur = conn.execute("SELECT * FROM map_layers ORDER BY category, name")
        layers = [dict(r) for r in cur.fetchall()]
        
        with open(OUTPUT_DIR / "map-layers.json", "w") as f:
            json.dump(layers, f, indent=2)
        
        print(f"Exported {len(layers)} map layers")
    except Exception as e:
        print(f"Map layers export: {e}")

def export_datasets():
    """Export datasets."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    cur = conn.execute("SELECT * FROM datasets ORDER BY id DESC LIMIT 50")
    datasets = [dict(r) for r in cur.fetchall()]
    
    with open(OUTPUT_DIR / "datasets.json", "w") as f:
        json.dump(datasets, f, indent=2)
    
    print(f"Exported {len(datasets)} datasets")

def export_health():
    """Export health check."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    cur = conn.execute("SELECT COUNT(*) as count FROM indicators")
    count = cur.fetchone()["count"]
    
    cur = conn.execute("SELECT DISTINCT category FROM indicators ORDER BY category")
    categories = [r["category"] for r in cur.fetchall()]
    
    health = {
        "status": "healthy" if count > 0 else "degraded",
        "db_exists": True,
        "indicator_count": count,
        "categories": categories,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    with open(OUTPUT_DIR / "health.json", "w") as f:
        json.dump(health, f, indent=2)
    
    print(f"Exported health check: {count} indicators")

def export_stakeholders():
    """Export stakeholder groups."""
    stakeholders = [
        {
            "id": "business",
            "name": "Business Owners",
            "description": "Free market benchmarks, customer demographics, industry trends, pricing intelligence, and demand signals.",
            "icon": "🏪",
            "highlights": [
                "Local market snapshot & competitor landscape",
                "Customer demographics & spending patterns",
                "Business formation & licensing data",
                "Quarterly economic briefings"
            ]
        },
        {
            "id": "residents",
            "name": "Residents",
            "description": "Employment data, wage trends, cost-of-living metrics, school performance, health outcomes, and public spending.",
            "icon": "🏠",
            "highlights": [
                "Employment & wage trends by sector",
                "Cost of living breakdown",
                "School & health data by area",
                "Open budget & public spending"
            ]
        },
        {
            "id": "tourists",
            "name": "Tourists",
            "description": "Real-time conditions, honest reviews, local business availability, event calendars, and safety information.",
            "icon": "🏖️",
            "highlights": [
                "Real-time surf, weather & traffic",
                "Verified reviews & local availability",
                "Event calendars & booking",
                "Parking & transit information"
            ]
        },
        {
            "id": "leaders",
            "name": "Leaders",
            "description": "Capital flow data, permitting velocity, infrastructure status, workforce availability, and demographic shifts.",
            "icon": "📊",
            "highlights": [
                "Capital flow & investment tracking",
                "Permitting & licensing velocity",
                "Workforce availability & wages",
                "Infrastructure capacity data"
            ]
        }
    ]
    
    with open(OUTPUT_DIR / "stakeholders.json", "w") as f:
        json.dump(stakeholders, f, indent=2)
    
    print(f"Exported {len(stakeholders)} stakeholder groups")

def export_news():
    """Export news items."""
    news = [
        {
            "id": "1",
            "title": "Project Volusia v2.0 Launched — Live Data Now Available",
            "summary": "Real economic, demographic, and climate indicators now live from Census, BLS, BEA, and NOAA.",
            "date": "2026-09-05",
            "category": "Platform"
        },
        {
            "id": "2",
            "title": "Q2 2026 Economic Briefing Published",
            "summary": "Unemployment at 4.6%, total employment at 189,265, per capita income at $59,259.",
            "date": "2026-08-15",
            "category": "Economic"
        },
        {
            "id": "3",
            "title": "New Climate Data Available",
            "summary": "NOAA annual climate summary: avg max temp 27.9°C, total precipitation 1,028mm.",
            "date": "2026-07-20",
            "category": "Climate"
        },
        {
            "id": "4",
            "title": "Population Growth Continues — 601,107 (2024)",
            "summary": "Volusia County adds ~9,000 residents year-over-year, reaching 601,107.",
            "date": "2026-06-30",
            "category": "Demographic"
        }
    ]
    
    with open(OUTPUT_DIR / "news.json", "w") as f:
        json.dump(news, f, indent=2)
    
    print(f"Exported {len(news)} news items")

def main():
    """Run all exports."""
    print("=" * 60)
    print("Project Volusia — Data Sync")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    indicators = export_indicators()
    export_by_category(indicators)
    export_map_layers()
    export_datasets()
    export_health()
    export_stakeholders()
    export_news()
    
    print()
    print("Data sync complete!")

if __name__ == "__main__":
    main()
