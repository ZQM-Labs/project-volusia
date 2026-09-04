#!/usr/bin/env python3
"""
Project Volusia — Data Staleness Alerting
Checks if data is stale and exits with error code if so.
Can be run via cron/Task Scheduler for monitoring.

Usage:
    python Tools/volusia_data/alerts/staleness_check.py
    python Tools/volusia_data/alerts/staleness_check.py --webhook https://discord.com/api/webhooks/...
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add Tools to path
TOOLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))

from volusia_data.config import DB_PATH

# Max age in days per source
THRESHOLDS = {
    "NOAA NCEI": 2,
    "BLS LAUS": 45,
    "BLS QCEW": 120,
    "Census PEP": 365,
    "Census ACS": 365,
    "BEA Regional": 365,
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def check_staleness():
    """Check all indicators for staleness."""
    if not DB_PATH.exists():
        return [{"indicator": "DATABASE", "status": "MISSING", "message": "Database file does not exist"}]
    
    conn = get_db()
    rows = conn.execute("SELECT name, source, fetched_at FROM indicators").fetchall()
    conn.close()
    
    now = datetime.now(timezone.utc)
    stale = []
    
    for row in rows:
        name = row["name"]
        source = row["source"]
        fetched_at = row["fetched_at"]
        
        if not fetched_at:
            stale.append({"indicator": name, "source": source, "status": "MISSING", "message": "No fetch timestamp"})
            continue
        
        try:
            fetched = datetime.fromisoformat(fetched_at)
            age_days = (now - fetched).days
            
            threshold = 365  # default
            for key, days in THRESHOLDS.items():
                if key in source:
                    threshold = days
                    break
            
            if age_days > threshold:
                stale.append({
                    "indicator": name,
                    "source": source,
                    "status": "STALE",
                    "message": f"{age_days} days old (threshold: {threshold})",
                })
        except (ValueError, TypeError):
            stale.append({"indicator": name, "source": source, "status": "ERROR", "message": f"Invalid timestamp: {fetched_at}"})
    
    return stale


def send_webhook(webhook_url, stale_items):
    """Send alert to webhook (Discord, Slack, etc.)."""
    import requests
    
    content = f"⚠️ **Project Volusia Data Alert**: {len(stale_items)} indicator(s) stale\n"
    for item in stale_items:
        content += f"- `{item['indicator']}`: {item['message']}\n"
    
    payload = {"content": content}
    
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        print(f"Alert sent to webhook")
    except Exception as e:
        print(f"Failed to send webhook: {e}")


def main():
    parser = argparse.ArgumentParser(description="Check data staleness")
    parser.add_argument("--webhook", help="Webhook URL for alerts (Discord, Slack)")
    args = parser.parse_args()
    
    stale = check_staleness()
    
    if stale:
        print(f"ALERT: {len(stale)} stale indicator(s)")
        for item in stale:
            print(f"  {item['indicator']}: {item['message']}")
        
        if args.webhook:
            send_webhook(args.webhook, stale)
        
        sys.exit(1)
    else:
        print("All data fresh")
        sys.exit(0)


if __name__ == "__main__":
    main()
