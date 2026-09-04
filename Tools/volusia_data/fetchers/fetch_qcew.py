#!/usr/bin/env python3
"""
Project Volusia — BLS QCEW Fetcher
Fetches Quarterly Census of Employment and Wages (no API key required).

Usage:
    python Tools/volusia_data/fetchers/fetch_qcew.py [--year 2024] [--area 12127] [--output csv|json]
"""

import argparse
import csv
import io
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import requests

DEFAULT_YEAR = 2024
DEFAULT_AREA = "12127"  # Volusia County, FL

URL_TEMPLATE = (
    "https://data.bls.gov/cew/data/files/{year}/csv/"
    "{year}_annual_singlefile.zip"
)


def fetch_qcew(year=DEFAULT_YEAR, area=DEFAULT_AREA):
    """Fetch BLS QCEW data for a specific area."""
    url = URL_TEMPLATE.format(year=year)
    print(f"Fetching BLS QCEW {year} from {url}...")

    resp = requests.get(url, timeout=120)
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        csv_name = next(
            (n for n in z.namelist() if "annual" in n.lower() and n.endswith(".csv")),
            z.namelist()[0],
        )
        with z.open(csv_name) as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"))
            volusia_rows = [r for r in reader if r.get("area_fips", "").strip() == area]

    if not volusia_rows:
        print(f"ERROR: Area {area} not found in QCEW data", file=sys.stderr)
        return None

    row = volusia_rows[0]
    results = {
        "area_fips": area,
        "year": year,
        "establishments": row.get("annual_avg_estabs", "N/A"),
        "employment": row.get("annual_avg_emplvl", "N/A"),
        "avg_weekly_wage": row.get("annual_avg_wkly_wage", "N/A"),
        "source": "BLS QCEW",
        "source_url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch BLS QCEW employment data")
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR, help="Year (default: 2024)")
    parser.add_argument("--area", default=DEFAULT_AREA, help="Area FIPS (default: 12127)")
    parser.add_argument("--output", choices=["csv", "json"], default="json", help="Output format")
    parser.add_argument("--save", type=Path, help="Save output to file")
    args = parser.parse_args()

    results = fetch_qcew(args.year, args.area)
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
