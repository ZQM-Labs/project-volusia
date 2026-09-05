#!/usr/bin/env python3
"""
Project Volusia — Midnight Launch Startup Script
Starts all 3 services (portal, contribution API, reverse proxy).

Run this script to start the full Project Volusia stack.
Requires: portal (:8789) and contribution API (:8790) running.

Usage:
    python start_launch.py
    
After starting, access:
    http://localhost/                    — Main website
    http://localhost/contribute/         — Contribution page
    http://localhost/api/health          — Portal health
    http://localhost/api/v1/contributions — Submit contribution
"""

import os
import subprocess
import sys
import time
from Path import Path

BASE_DIR = Path(__file__).resolve().parent
TOOLS_DIR = BASE_DIR / "Tools"

def check_port(port):
    """Check if a port is listening."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def main():
    print("=" * 60)
    print("Project Volusia — Midnight Launch")
    print("=" * 60)
    
    # Check services
    print("\n[1] Checking services...")
    
    if check_port(8789):
        print("  Portal: RUNNING")
    else:
        print("  Portal: NOT RUNNING")
        print("  Start with: python Tools/volusia_data/portal_app.py")
        sys.exit(1)
    
    if check_port(8790):
        print("  Contribution API: RUNNING")
    else:
        print("  Contribution API: NOT RUNNING")
        print("  Start with: python Tools/volusia_data/contribution_api.py")
        sys.exit(1)
    
    # Start reverse proxy
    print("\n[2] Starting reverse proxy...")
    proc = subprocess.Popen(
        [sys.executable, "deploy_portal.py"],
        cwd=BASE_DIR,
    )
    time.sleep(1)
    
    if check_port(80):
        print("  Reverse proxy: RUNNING (port 80)")
    else:
        print("  Reverse proxy: FAILED")
        sys.exit(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("All services operational!")
    print("=" * 60)
    print("\nAccess points:")
    print("  http://localhost/                    — Main website")
    print("  http://localhost/contribute/         — Contribution page")
    print("  http://localhost/api/health          — Health check")
    print("  http://localhost/api/v1/contributions — Submit contribution")
    print(f"\nReverse proxy PID: {proc.pid}")
    print("\nPress Ctrl+C to stop.")
    
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print("\nStopped.")

if __name__ == "__main__":
    main()
