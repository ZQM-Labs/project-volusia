#!/usr/bin/env python3
"""
Project Volusia — BLS LAUS Fetcher
Fetches Local Area Unemployment Statistics (API key required for production).

Usage:
    python Tools/volusia_data/fetchers/fetch_bls_laus.py [--series LAUST121270000000003] [--start 2020] [--end 2026] [--output csv|json]
"""

import argparse
import csv
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

DEFAULT_SERIES = "LAUST121270000000003"  # Volusia County unemployment rate
DEFAULT_START = 2020

URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"


def fetch_bls(series=DEFAULT_SERIES, start_year=DEFAULT_START, end_year=None):
    """Fetch BLS LAUS data for a series."""
    if end_year is None:
        end_year = datetime.now().year

    api_key = os.environ.get("BLS_API_KEY", "")
    print(f"Fetching BLS LAUS series {series} ({start_year}-{end_year})...")

    payload = {
        "seriesid": [series],
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": api_key,
    }

    resp = requests.post(URL, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "REQUEST_SUCCEEDED":
        print(f"ERROR: BLS API status: {data.get('status')}", file=sys.stderr)
        return None

    series_list = data.get("Results", {}).get("series", [])
    if not series_list:
        print("ERROR: No series in response", file=sys.stderr)
        return None

    results = []
    for serie in series_list:
        for obs in serie.get("data", []):
            val_str = obs.get("value", "").strip()
            try:
                val = float(val_str)
            except (ValueError, TypeError):
                continue
            results.append({
                "year": int(obs["year"]),
                "period": obs["period"],
                "period_name": obs["periodName"],
                "value": val,
                "source": "BLS LAUS",
                "source_url": "https://www.bls.gov/lau/",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })

    if not results:
        print("ERROR: No valid numeric rows", file=sys.stderr)
        return None

    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch BLS LAUS unemployment data")
    parser.add_argument("--series", default=DEFAULT_SERIES, help="Series ID (default: LAUST121270000000003)")
    parser.add_argument("--start", type=int, default=DEFAULT_START, help="Start year (default: 2020)")
    parser.add_argument("--end", type=int, help="End year (default: current year)")
    parser.add_argument("--output", choices=["csv", "json"], default="json", help="Output format")
    parser.add_argument("--save", type=Path, help="Save output to file")
    args = parser.parse_args()

    results = fetch_bls(args.series, args.start, args.end)
    if not results:
        sys.exit(1)

    if args.output == "json":
        output = json.dumps(results, indent=2)
    else:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
        output = buf.getvalue()

    if args.save:
        args.save.write_text(output)
        print(f"Saved to {args.save}")
    else:
        print(output)


if __name__ == "__main__":
    main()
