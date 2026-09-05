#!/usr/bin/env python3
"""
Project Volusia — Auto-Restart Watchdog
Monitors services and restarts them if they die.
Run as Administrator for full functionality.

Usage:
    python watchdog.py
"""

import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TOOLS_DIR = BASE_DIR / "Tools"
LOG_FILE = BASE_DIR / "watchdog.log"

SERVICES = [
    {
        "name": "Portal",
        "port": 8789,
        "command": [sys.executable, "-m", "volusia_data.portal_app"],
        "cwd": str(TOOLS_DIR),
    },
    {
        "name": "Contribution API",
        "port": 8790,
        "command": [sys.executable, "-m", "volusia_data.contribution_api"],
        "cwd": str(TOOLS_DIR),
    },
]

RESTART_COOLDOWN = 30  # seconds between restart attempts
MAX_RESTARTS_PER_HOUR = 10


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")


def check_port(port):
    """Check if a port is listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex(("127.0.0.1", port)) == 0


def is_running(process):
    """Check if a process is still alive."""
    return process is not None and process.poll() is None


def start_service(service):
    """Start a service subprocess."""
    log(f"Starting {service['name']}...")
    try:
        proc = subprocess.Popen(
            service["command"],
            cwd=service["cwd"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        time.sleep(2)
        if check_port(service["port"]):
            log(f"{service['name']} started successfully (PID: {proc.pid})")
            return proc
        else:
            log(f"{service['name']} failed to start")
            return None
    except Exception as e:
        log(f"Error starting {service['name']}: {e}")
        return None


def main():
    log("=" * 60)
    log("Project Volusia Watchdog Starting")
    log("=" * 60)

    processes = {}
    restart_counts = {}

    # Initial start
    for service in SERVICES:
        proc = start_service(service)
        if proc:
            processes[service["name"]] = proc
            restart_counts[service["name"]] = 0

    # Monitor loop
    while True:
        time.sleep(10)

        for service in SERVICES:
            name = service["name"]
            port = service["port"]

            # Check if port is responding
            if not check_port(port):
                log(f"ALERT: {name} (port {port}) not responding")

                # Check restart count
                count = restart_counts.get(name, 0)
                if count >= MAX_RESTARTS_PER_HOUR:
                    log(f"ERROR: {name} exceeded max restarts per hour, waiting...")
                    time.sleep(300)  # Wait 5 minutes
                    restart_counts[name] = 0
                    continue

                # Kill old process if still running
                old_proc = processes.get(name)
                if is_running(old_proc):
                    old_proc.terminate()
                    old_proc.wait(timeout=5)

                # Restart
                proc = start_service(service)
                if proc:
                    processes[name] = proc
                    restart_counts[name] = count + 1
                else:
                    log(f"Failed to restart {name}")


if __name__ == "__main__":
    main()
