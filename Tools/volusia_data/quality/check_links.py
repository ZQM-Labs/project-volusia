#!/usr/bin/env python3
"""
Project Volusia — Broken Link Detector
Checks all source URLs for accessibility (HTTP status codes).
"""

import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent.parent.parent / "volusia_data" / "volusia.db"


def check_url(url: str, timeout: int = 10) -> dict:
    """Check if a URL is accessible."""
    import urllib.request
    import urllib.error
    
    result = {
        "url": url,
        "status": "unknown",
        "status_code": None,
        "error": None,
        "response_time_ms": None,
    }
    
    try:
        start = time.time()
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "ProjectVolusia/1.0"})
        response = urllib.request.urlopen(req, timeout=timeout)
        elapsed = (time.time() - start) * 1000
        
        result["status"] = "OK"
        result["status_code"] = response.status
        result["response_time_ms"] = round(elapsed, 0)
        
    except urllib.error.HTTPError as e:
        result["status"] = "ERROR"
        result["status_code"] = e.code
        result["error"] = str(e)
    except urllib.error.URLError as e:
        result["status"] = "UNREACHABLE"
        result["error"] = str(e)
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)
    
    return result


def check_all_urls():
    """Check all unique source URLs in the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute("SELECT DISTINCT source_url FROM indicators WHERE source_url IS NOT NULL AND source_url != ''").fetchall()
    urls = [r["source_url"] for r in rows]
    
    conn.close()
    
    results = []
    for url in urls:
        result = check_url(url)
        results.append(result)
        print(f"  {result['status']:10} {result['status_code'] or '':5} {url[:80]}")
    
    return results


if __name__ == "__main__":
    print(f"Checking {len(results) if 'results' in dir() else 'all'} URLs...")
    results = check_all_urls()
    
    ok = len([r for r in results if r["status"] == "OK"])
    error = len([r for r in results if r["status"] != "OK"])
    
    print(f"\nResults: {ok} OK, {error} errors/unreachable")
