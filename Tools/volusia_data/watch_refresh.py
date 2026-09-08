#!/usr/bin/env python3
"""
Project Volusia — Pipeline with Watch Mode
Run: python watch_refresh.py [--interval 300]
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Watch and auto-refresh data pipeline")
    parser.add_argument("--interval", type=int, default=300, help="Refresh interval in seconds (default: 300)")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    Path(__file__).resolve().parent / "volusia.db"

    def run_pipeline():
        print(f"\n{'=' * 60}")
        print(f"Pipeline run: {datetime.now().isoformat()}")
        print(f"{'=' * 60}")

        result = subprocess.run(
            [sys.executable, "refresh_v2.py"],
            cwd=Path(__file__).parent,
            capture_output=False,
            text=True,
        )

        if result.returncode == 0:
            print("✓ Pipeline completed successfully")
        else:
            print(f"✗ Pipeline failed (exit code: {result.returncode})")
            # Could add auto-retry logic here

        return result.returncode

    if args.once:
        sys.exit(run_pipeline())

    print(f"Starting pipeline watch mode (interval: {args.interval}s)")
    print("Press Ctrl+C to stop")

    try:
        while True:
            run_pipeline()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n✓ Watch mode stopped")


if __name__ == "__main__":
    main()
