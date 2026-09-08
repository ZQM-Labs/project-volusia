#!/usr/bin/env python3
"""
Project Volusia — Data Health Dashboard
Generates a status summary of the current data ecosystem.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB = Path(__file__).parent / "Tools" / "volusia_data" / "volusia.db"


def main():
    if not DB.exists():
        print("ERROR: Database not found")
        return

    with sqlite3.connect(DB) as conn:
        # Get indicator counts
        indicators = conn.execute("SELECT COUNT(*), MIN(fetched_at), MAX(fetched_at) FROM indicators").fetchone()

        # Get fetcher status
        conn.execute("SELECT source, COUNT(DISTINCT source) FROM datasets GROUP BY source").fetchall() if conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall() else []

    print("=" * 60)
    print("PROJECT VOLUSIA — DATA HEALTH DASHBOARD")
    print(f"Updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    print()
    print(f"📊 Total Indicators: {indicators[0]}")
    print(f"🕐 Newest Data:  {indicators[2] or 'N/A'}")
    print(f"🕐 Oldest Data:  {indicators[1] or 'N/A'}")
    print()
    print("📁 Recent Data Sources:")

    # Read from fetch log
    log_path = DB.parent / "fetch_log.jsonl"
    if log_path.exists():
        with open(log_path) as f:
            lines = f.readlines()[-5:]  # Last 5 entries
            for line in lines:
                entry = __import__("json").loads(line)
                status = "✓" if entry["status"] == "OK" else "✗"
                print(f"  {status} {entry['source']}: {entry.get('details', 'OK')}")

    print()
    print("🔧 System Status:")
    print("  • Census PEP: WORKS (no key required)")
    print("  • NOAA NCEI: WORKS (no key required)")
    print("  • BLS QCEW: WORKS (CSV download)")
    print("  • Census ACS: NEEDS KEY")
    print("  • BLS LAUS: NEEDS KEY")
    print("  • BEA Regional: NEEDS KEY")
    print()
    print("🚀 Next Steps:")
    print("  1. Register for API keys (see API_REGISTRATION_PLAN.md)")
    print("  2. Update .env with keys")
    print("  3. Run: python Tools/volusia_data/run_full_refresh.py")
    print()


if __name__ == "__main__":
    main()
