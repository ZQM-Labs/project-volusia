#!/usr/bin/env python3
"""
Project Volusia — Health Check & Monitoring Script
Checks data freshness, API uptime, and data quality.
Run on a schedule to monitor system health.

Usage:
    python Tools/volusia_data/health_check.py
"""

import json
import sqlite3
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "volusia.db"

# Expected freshness windows (days)
FRESHNESS = {
    "Census PEP": 365,
    "Census ACS": 365,
    "NOAA NCEI": 2,
    "BLS LAUS": 45,
    "BEA Regional": 365,
    "BLS QCEW": 120,
}


def check_db_exists():
    """Check if database exists and has data."""
    if not DB_PATH.exists():
        return "FAIL", "Database file does not exist"
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    count = conn.execute("SELECT COUNT(*) FROM indicators").fetchone()[0]
    conn.close()
    
    if count == 0:
        return "FAIL", "Database is empty"
    
    return "OK", f"{count} indicators loaded"


def check_freshness():
    """Check data freshness per source."""
    if not DB_PATH.exists():
        return []
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT name, source, fetched_at FROM indicators").fetchall()
    conn.close()
    
    results = []
    now = datetime.now(timezone.utc)
    
    for row in rows:
        source = row["source"]
        fetched_at = row["fetched_at"]
        
        if not fetched_at:
            results.append({
                "indicator": row["name"],
                "source": source,
                "status": "UNKNOWN",
                "message": "No fetch timestamp",
            })
            continue
        
        try:
            fetched = datetime.fromisoformat(fetched_at)
            age_days = (now - fetched).days
            
            # Find matching freshness window
            max_age = 365  # default
            for key, days in FRESHNESS.items():
                if key in source:
                    max_age = days
                    break
            
            if age_days > max_age:
                status = "STALE"
                message = f"{age_days} days old (max {max_age})"
            else:
                status = "OK"
                message = f"{age_days} days old"
            
            results.append({
                "indicator": row["name"],
                "source": source,
                "status": status,
                "message": message,
            })
        except (ValueError, TypeError):
            results.append({
                "indicator": row["name"],
                "source": source,
                "status": "ERROR",
                "message": f"Invalid timestamp: {fetched_at}",
            })
    
    return results


def check_api_connectivity():
    """Check if external APIs are reachable."""
    import requests
    
    apis = {
        "Census PEP": "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv",
        "NOAA NCEI": "https://www.ncei.noaa.gov/access/services/data/v1",
        "BLS QCEW": "https://data.bls.gov/cew/data/files/2024/csv/2024_annual_singlefile.zip",
    }
    
    results = []
    for name, url in apis.items():
        try:
            resp = requests.head(url, timeout=10, allow_redirects=True)
            if resp.status_code < 400:
                results.append({"api": name, "status": "OK", "code": resp.status_code})
            else:
                results.append({"api": name, "status": "WARN", "code": resp.status_code})
        except Exception as e:
            results.append({"api": name, "status": "FAIL", "error": str(e)})
    
    return results


def main():
    print("=" * 60)
    print("Project Volusia — Health Check")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    # Database check
    status, message = check_db_exists()
    print(f"\n[{status}] Database: {message}")
    
    # Freshness check
    print("\n── Data Freshness ──")
    freshness = check_freshness()
    stale_count = 0
    for f in freshness:
        symbol = "✓" if f["status"] == "OK" else "✗"
        print(f"  {symbol} {f['indicator']}: {f['message']}")
        if f["status"] == "STALE":
            stale_count += 1
    
    # API connectivity
    print("\n── API Connectivity ──")
    apis = check_api_connectivity()
    for api in apis:
        symbol = "✓" if api["status"] == "OK" else "✗"
        detail = api.get("code", api.get("error", ""))
        print(f"  {symbol} {api['api']}: {detail}")
    
    # Summary
    print("\n── Summary ──")
    total = len(freshness)
    ok = sum(1 for f in freshness if f["status"] == "OK")
    print(f"  Fresh: {ok}/{total}")
    print(f"  Stale: {stale_count}/{total}")
    
    if stale_count > 0:
        print("\n  ACTION: Run refresh_v2.py to update stale data")
        sys.exit(1)
    else:
        print("\n  All data fresh")
        sys.exit(0)


if __name__ == "__main__":
    main()
