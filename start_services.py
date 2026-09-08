#!/usr/bin/env python3
"""
Project Volusia — Unified Startup Script
Starts all services for the midnight launch.

Usage:
    python start_services.py

Access:
    http://localhost/           — Main website + contribution form
    http://localhost/contribute/ — Dedicated contribution page
    http://localhost/api/        — Portal API (proxied to :8789)
    http://localhost/api/v1/     — Contribution API (proxied to :8790)
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).resolve().parent
TOOLS_DIR = BASE_DIR / "Tools"
STATIC_DIR = Path(os.environ.get("VOLUSIA_STATIC_DIR", str(BASE_DIR / "Tools" / "volusia_data" / "static")))

PORTAL_PORT = 8789
CONTRIBUTE_PORT = 8790
PROXY_PORT = 80

processes = []


def start_service(name, cmd, cwd=None):
    """Start a subprocess and track it."""
    print(f"  Starting {name}...")
    proc = subprocess.Popen(
        cmd,
        cwd=cwd or BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    processes.append((name, proc))
    time.sleep(1)

    # Check if it started
    if proc.poll() is not None:
        output = proc.stdout.read().decode() if proc.stdout else ""
        print(f"  FAILED to start {name}: {output[:500]}")
        return False

    print(f"  {name} started (PID: {proc.pid})")
    return True


def main():
    print("=" * 60)
    print("Project Volusia — Service Startup")
    print("=" * 60)

    # 1. Initialize DB
    print("\n[1/4] Initializing database...")
    sys.path.insert(0, str(TOOLS_DIR))
    from volusia_data.refresh_v2 import init_db, upsert_indicator

    # Initialize database and seed default data
    conn = init_db()
    row = conn.execute("SELECT COUNT(*) FROM indicators WHERE name = 'unemployment_rate_bls'").fetchone()
    if row[0] == 0:
        upsert_indicator(
            "unemployment_rate_bls",
            "5.3",
            "percent",
            "Economy",
            "BLS LAUS",
            "https://www.bls.gov/lau/",
            "July 2026",
            "BLS LAUS unemployment rate for Volusia County (July 2026)",
        )
        print("  Seeded unemployment rate (5.3%, July 2026)")
    conn.close()

    # 2. Start Portal (port 8789)
    print("\n[2/4] Starting Portal...")
    start_service(
        "Portal",
        [sys.executable, "-m", "volusia_data.portal_app"],
        cwd=TOOLS_DIR,
    )

    # 3. Start Contribution API (port 8790)
    print("\n[3/4] Starting Contribution API...")
    start_service(
        "Contribution API",
        [sys.executable, "-m", "volusia_data.contribution_api"],
        cwd=TOOLS_DIR,
    )

    # 4. Start Reverse Proxy (port 80)
    print("\n[4/4] Starting Reverse Proxy...")
    start_service(
        "Reverse Proxy",
        [sys.executable, "deploy_portal.py"],
        cwd=BASE_DIR,
    )

    # Summary
    print("\n" + "=" * 60)
    print("All services started!")
    print("=" * 60)
    print("\nAccess points:")
    print("  http://localhost/           — Main website")
    print("  http://localhost/contribute/ — Contribution page")
    print("  http://localhost/api/health  — Portal health")
    print("  http://localhost/api/v1/contributions — Submit contribution")
    print("\nPress Ctrl+C to stop all services.")

    # Wait for interrupt
    try:
        while True:
            time.sleep(1)
            # Check if any process died
            for name, proc in processes:
                if proc.poll() is not None:
                    output = proc.stdout.read().decode() if proc.stdout else ""
                    print(f"\n  {name} stopped unexpectedly: {output[:200]}")
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        for name, proc in processes:
            print(f"  Stopping {name}...")
            proc.terminate()
            proc.wait(timeout=5)
        print("All services stopped.")


if __name__ == "__main__":
    main()
