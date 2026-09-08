#!/usr/bin/env python3
"""
Project Volusia — Environment Validator
Checks all required configuration before running.
Run: python validate_env.py
Exit 0 = OK, Exit 1 = Issues found
"""

import os
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "volusia.db"

REQUIRED_KEYS = ["CENSUS_API_KEY", "BLS_API_KEY", "BEA_API_KEY"]
OPTIONAL_KEYS = []


def check_database():
    if DB_PATH.exists():
        print(f"✓ Database exists: {DB_PATH}")
        return True
    print(f"✗ Database missing: {DB_PATH}")
    return False


def check_api_keys():
    print("\nAPI Keys:")
    all_set = True
    for key in REQUIRED_KEYS:
        value = os.environ.get(key, "")
        if value:
            print(f"  ✓ {key}: {'*' * 8}")
        else:
            print(f"  ○ {key}: not set (pipeline will skip this source)")
        all_set = False if not value else all_set
    return True  # Keys are optional


def check_dependencies():
    print("\nDependencies:")
    deps = ["sqlite3", "requests", "fastapi", "uvicorn"]
    all_ok = True

    for dep in deps:
        try:
            __import__(dep if dep != "sqlite3" else "sqlite3")
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep}: not installed")
            all_ok = False

    return all_ok


def check_port_availability():
    import socket

    ports = [8789, 8790, 8791, 8899]
    print("\nPort Availability:")

    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("127.0.0.1", port))
        sock.close()

        if result == 0:
            print(f"  ○ Port {port}: in use")
        else:
            print(f"  ✓ Port {port}: available")


def main():
    print("=" * 60)
    print("Project Volusia Environment Check")
    print("=" * 60)

    checks = [
        ("Database", check_database),
        ("Dependencies", check_dependencies),
        ("API Keys", check_api_keys),
    ]

    results = {}
    for name, check_fn in checks:
        try:
            results[name] = check_fn()
        except Exception as e:
            print(f"✗ {name}: {e}")
            results[name] = False

    check_port_availability()

    print("\n" + "=" * 60)
    if all(results.values()):
        print("✓ Environment OK")
        return 0
    else:
        print("✗ Environment issues found")
        print("\nRun 'make install' to fix dependencies")
        print("Set missing API keys to proceed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
