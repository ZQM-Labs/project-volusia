#!/usr/bin/env python3
"""
Project Volusia — Startup Verification Script
Verifies all services are running and healthy.

Usage:
    python verify_startup.py
"""

import json
import socket
import sys
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TOOLS_DIR = BASE_DIR / "Tools"

SERVICES = [
    {"name": "Portal", "port": 8789, "path": "/api/health"},
    {"name": "Contribution API", "port": 8790, "path": "/api/v1/health"},
    {"name": "Reverse Proxy", "port": 80, "path": "/api/health"},
]

ENDPOINTS = [
    ("/", "text/html"),
    ("/contribute/", "text/html"),
    ("/project-volusia", "text/html"),
    ("/data-explorer", "text/html"),
    ("/api/health", "application/json"),
    ("/api/status", "application/json"),
    ("/api/indicators", "application/json"),
    ("/api/executive-summary", "application/json"),
    ("/api/chart/population_trend.png", "image/png"),
    ("/api/chart/employment_overview.png", "image/png"),
    ("/api/chart/climate_summary.png", "image/png"),
    ("/api/chart/unemployment_trend.png", "image/png"),
    ("/api/chart/wage_trend.png", "image/png"),
]


def check_port(port):
    """Check if a port is listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex(("127.0.0.1", port)) == 0


def check_endpoint(path, expected_type=None):
    """Check if an endpoint returns 200."""
    try:
        url = f"http://127.0.0.1{path}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.status
            content_type = resp.headers.get("Content-Type", "").split(";")[0]
            if expected_type and expected_type not in content_type:
                return False, f"Expected {expected_type}, got {content_type}"
            return True, f"OK ({content_type})"
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 60)
    print("Project Volusia — Startup Verification")
    print("=" * 60)
    
    all_ok = True
    
    # Check services
    print("\n[1] Service Status")
    for service in SERVICES:
        if check_port(service["port"]):
            print(f"  ✓ {service['name']} (port {service['port']})")
        else:
            print(f"  ✗ {service['name']} (port {service['port']}) — NOT RUNNING")
            all_ok = False
    
    # Check endpoints
    print("\n[2] Endpoint Status")
    for path, expected_type in ENDPOINTS:
        ok, msg = check_endpoint(path, expected_type)
        if ok:
            print(f"  ✓ {path}")
        else:
            print(f"  ✗ {path} — {msg}")
            all_ok = False
    
    # Check database
    print("\n[3] Database Status")
    db_path = TOOLS_DIR / "volusia_data" / "volusia.db"
    if db_path.exists():
        import sqlite3
        conn = sqlite3.connect(db_path)
        indicators = conn.execute("SELECT COUNT(*) FROM indicators").fetchone()[0]
        submissions = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
        conn.close()
        print(f"  ✓ Database: {indicators} indicators, {submissions} submissions")
    else:
        print(f"  ✗ Database not found")
        all_ok = False
    
    # Check quality
    print("\n[4] Data Quality")
    try:
        sys.path.insert(0, str(TOOLS_DIR))
        from volusia_data.quality.validate import generate_report
        report = generate_report()
        if report["overall"] == "OK":
            print(f"  ✓ Quality: {report['summary']['ok']}/{report['summary']['total']} checks passing")
        else:
            print(f"  ⚠ Quality: {report['overall']}")
    except Exception as e:
        print(f"  ✗ Quality check failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ ALL CHECKS PASSED — System is ready!")
    else:
        print("✗ SOME CHECKS FAILED — Review output above")
    print("=" * 60)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
