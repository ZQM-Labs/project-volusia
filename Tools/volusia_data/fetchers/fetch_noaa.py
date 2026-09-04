#!/usr/bin/env python3
"""
Project Volusia — NOAA NCEI Fetcher
Fetches daily weather summaries from NOAA (no API key required).

Usage:
    python Tools/volusia_data/fetchers/fetch_noaa.py [--station USW00012838] [--year 2024] [--output csv|json]
"""

import argparse
import csv
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

DEFAULT_STATION = "USW00012838"  # Daytona Beach Intl Airport
DEFAULT_YEAR = 2024

URL = "https://www.ncei.noaa.gov/access/services/data/v1"


def fetch_noaa(station=DEFAULT_STATION, year=DEFAULT_YEAR):
    """Fetch NOAA daily summaries for a station."""
    print(f"Fetching NOAA NCEI for station {station}, year {year}...")

    params = {
        "dataset": "daily-summaries",
        "stations": station,
        "dataTypes": "TMAX,TMIN,PRCP",
        "startDate": f"{year}-01-01",
        "endDate": f"{year}-12-31",
        "format": "json",
        "limit": 5000,
    }

    resp = requests.get(URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if not data:
        print("ERROR: Empty response from NOAA", file=sys.stderr)
        return None

    # Aggregate
    tmax_vals = [int(d["TMAX"]) for d in data if "TMAX" in d]
    tmin_vals = [int(d["TMIN"]) for d in data if "TMIN" in d]
    prcp_vals = [int(d["PRCP"]) for d in data if "PRCP" in d]

    results = {
        "station": station,
        "year": year,
        "days_counted": len(data),
        "avg_tmax": round(sum(tmax_vals) / len(tmax_vals), 1) if tmax_vals else None,
        "avg_tmin": round(sum(tmin_vals) / len(tmin_vals), 1) if tmin_vals else None,
        "total_prcp": sum(prcp_vals) if prcp_vals else None,
        "source": "NOAA NCEI",
        "source_url": URL,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch NOAA NCEI weather data")
    parser.add_argument("--station", default=DEFAULT_STATION, help="Station ID (default: USW00012838)")
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR, help="Year (default: 2024)")
    parser.add_argument("--output", choices=["csv", "json"], default="json", help="Output format")
    parser.add_argument("--save", type=Path, help="Save output to file")
    args = parser.parse_args()

    results = fetch_noaa(args.station, args.year)
    if not results:
        sys.exit(1)

    if args.output == "json":
        output = json.dumps(results, indent=2)
    else:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(results.keys()))
        writer.writeheader()
        writer.writerow(results)
        output = buf.getvalue()

    if args.save:
        args.save.write_text(output)
        print(f"Saved to {args.save}")
    else:
        print(output)


if __name__ == "__main__":
    main()
