#!/usr/bin/env python3
"""
Project Volusia-Specific Data Freshness Watchdog
Concrete implementation for Volusia County data pipeline.

Monitors indicator freshness with source-specific thresholds.
Exit 1 if any indicators are stale beyond their source's update frequency.

Usage in cron:
*/6 * * * * python /path/to/Project-Volusia/watchdog_monitoring.py

Configuration: Adjust SOURCE_THRESHOLDS below for different data sources.
"""

import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone

# Database location - relative to this script
DB_PATH = Path(__file__).parent / "Tools" / "volusia_data" / "volusia.db"

# Default threshold: 1 week
AGE_THRESHOLD_HOURS = 168

# Source-specific thresholds (hours)
# Adjust based on source update frequency
SOURCE_THRESHOLDS = {
    # Daily sources
    "NOAA NCEI": 24,  # Daily weather data
    # Monthly sources
    "BLS LAUS": 720,  # 3 months for unemployment
    # Quarterly sources
    "BLS QCEW": 2160,  # 3 months for employment/wages
    # Annual sources
    "Census ACS": 8760,  # 1 year
    "Census PEP": 8760,  # 1 year
    "BEA Regional": 8760,  # 1 year
}


def get_source_threshold(source_name):
    """Get threshold for a source, falling back to default."""
    return SOURCE_THRESHOLDS.get(source_name, AGE_THRESHOLD_HOURS)


def check_freshness():
    """
    Check all indicators for staleness.
    Exit 0 = all fresh, Exit 1 = at least one stale indicator.
    """
    if not DB_PATH.exists():
        print(json.dumps({"status": "error", "message": "Database not found", "path": str(DB_PATH)}))
        sys.exit(1)

    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT name, value, source, fetched_at, vintage FROM indicators").fetchall()

    stale = []
    healthy = []

    for name, value, source, fetched_at, vintage in rows:
        if not fetched_at:
            stale.append({"name": name, "reason": "never_fetched", "source": source})
            continue

        fetched_dt = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
        age_hours = (datetime.now(timezone.utc) - fetched_dt).total_seconds() / 3600

        threshold = get_source_threshold(source)

        if age_hours > threshold:
            stale.append(
                {
                    "name": name,
                    "source": source,
                    "age_hours": round(age_hours, 1),
                    "threshold_hours": threshold,
                    "age_days": round(age_hours / 24, 1),
                    "vintage": vintage,
                }
            )
        else:
            healthy.append({"name": name, "source": source, "age_hours": round(age_hours, 1)})

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "degraded" if stale else "ok",
        "healthy_count": len(healthy),
        "stale_count": len(stale),
    }

    if stale:
        result["stale_items"] = stale
        print(json.dumps(result, indent=2))
        sys.exit(1)

    print(json.dumps({"status": "ok", "healthy_count": len(healthy), "checked_at": result["timestamp"]}))
    sys.exit(0)


if __name__ == "__main__":
    check_freshness()
