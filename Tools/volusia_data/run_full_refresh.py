#!/usr/bin/env python3
"""
Project Volusia — Full Refresh Entry Point.
Runs the complete data pipeline refresh and reports results.
"""

import sys
from pathlib import Path

# Ensure the volusia_data package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from refresh_v2 import main

if __name__ == "__main__":
    results = main()

    # Exit with error code if any source failed
    failed = [name for name, ok in results.items() if not ok]
    if failed:
        print(f"\nWARNING: {len(failed)} source(s) failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("\nAll sources refreshed successfully.")
        sys.exit(0)
