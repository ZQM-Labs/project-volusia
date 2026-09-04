#!/usr/bin/env python3
"""
Project Volusia — Geocoding Tool
Geocode addresses using Census Geocoder or OpenStreetMap Nominatim.

Usage:
    python Tools/volusia_data/processing/geocode.py --input addresses.csv --output geocoded.csv
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

import requests


CENSUS_GEOCODER = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode_census(address):
    """Geocode using US Census Bureau Geocoder."""
    params = {
        "address": address,
        "benchmark": "4",  # Public_AR_Current
        "format": "json",
    }
    try:
        resp = requests.get(CENSUS_GEOCODER, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        matches = data.get("result", {}).get("addressMatches", [])
        if matches:
            best = matches[0]
            coords = best.get("coordinates", {})
            return {
                "lat": coords.get("y"),
                "lon": coords.get("x"),
                "matched_address": best.get("matchedAddress", ""),
                "source": "Census Geocoder",
            }
    except Exception as e:
        print(f"Census geocode error: {e}", file=sys.stderr)
    
    return None


def geocode_nominatim(address):
    """Geocode using OpenStreetMap Nominatim."""
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
    }
    headers = {
        "User-Agent": "ProjectVolusia/1.0 (zqmcomputing@gmail.com)",
    }
    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        if data:
            best = data[0]
            return {
                "lat": best.get("lat"),
                "lon": best.get("lon"),
                "matched_address": best.get("display_name", ""),
                "source": "Nominatim",
            }
    except Exception as e:
        print(f"Nominatim geocode error: {e}", file=sys.stderr)
    
    return None


def main():
    parser = argparse.ArgumentParser(description="Geocode addresses")
    parser.add_argument("--input", "-i", required=True, help="Input CSV with 'address' column")
    parser.add_argument("--output", "-o", help="Output CSV file")
    parser.add_argument("--provider", choices=["census", "nominatim", "both"], default="census",
                        help="Geocoding provider")
    parser.add_argument("--rate-limit", type=float, default=1.0,
                        help="Seconds between requests (default: 1.0)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("ERROR: No rows in input", file=sys.stderr)
        sys.exit(1)

    # Check for address column
    if 'address' not in rows[0]:
        print("ERROR: Input must have an 'address' column", file=sys.stderr)
        sys.exit(1)

    results = []
    for i, row in enumerate(rows):
        address = row.get('address', '')
        if not address:
            results.append({**row, "lat": "", "lon": "", "geocode_source": ""})
            continue

        print(f"Geocoding {i+1}/{len(rows)}: {address[:60]}...")

        result = None
        if args.provider in ("census", "both"):
            result = geocode_census(address)
        if not result and args.provider in ("nominatim", "both"):
            result = geocode_nominatim(address)

        if result:
            results.append({
                **row,
                "lat": result["lat"],
                "lon": result["lon"],
                "matched_address": result["matched_address"],
                "geocode_source": result["source"],
            })
        else:
            results.append({**row, "lat": "", "lon": "", "geocode_source": "FAILED"})

        if i < len(rows) - 1:
            time.sleep(args.rate_limit)

    # Output
    output_headers = list(rows[0].keys()) + ["lat", "lon", "matched_address", "geocode_source"]
    output_lines = [",".join(output_headers)]
    for r in results:
        output_lines.append(",".join(str(r.get(h, '')) for h in output_headers))

    result_text = "\n".join(output_lines)

    if args.output:
        Path(args.output).write_text(result_text)
        print(f"Saved to {args.output}")
    else:
        print(result_text)


if __name__ == "__main__":
    main()
