#!/usr/bin/env python3
"""
Project Volusia — Census PEP Fetcher
Fetches county population estimates from Census Bureau (no API key required).

Usage:
    python Tools/volusia_data/fetchers/fetch_census_pep.py [--year 2024] [--county 127] [--output csv|json]
"""

import argparse
import csv
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

DEFAULT_YEAR = 2024
DEFAULT_COUNTY = "127"  # Volusia County, FL
DEFAULT_STATE = "12"

URL_TEMPLATE = (
    "https://www2.census.gov/programs-surveys/popest/"
    "datasets/2020-{year}/counties/totals/co-est{year}-alldata.csv"
)


def fetch_pep(year=DEFAULT_YEAR, county=DEFAULT_COUNTY, state=DEFAULT_STATE):
    """Fetch Census PEP data for a specific county."""
    url = URL_TEMPLATE.format(year=year)
    print(f"Fetching Census PEP {year} from {url}...")

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    lines = resp.text.strip().split("\n")
    header = lines[0].split(",")

    volusia_row = None
    for line in lines[1:]:
        fields = line.split(",")
        if len(fields) > 4 and fields[3].strip() == state and fields[4].strip() == county:
            volusia_row = dict(zip(header, fields))
            break

    if not volusia_row:
        print(f"ERROR: County {county} in state {state} not found", file=sys.stderr)
        return None

    results = []
    for y in range(2020, year + 1):
        pop_key = f"POPESTIMATE{y}"
        if pop_key in volusia_row:
            results.append({
                "year": y,
                "population": int(volusia_row[pop_key]),
                "source": "Census PEP",
                "source_url": url,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch Census PEP population data")
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR, help="End year (default: 2024)")
    parser.add_argument("--county", default=DEFAULT_COUNTY, help="County FIPS (default: 127)")
    parser.add_argument("--state", default=DEFAULT_STATE, help="State FIPS (default: 12)")
    parser.add_argument("--output", choices=["csv", "json"], default="json", help="Output format")
    parser.add_argument("--save", type=Path, help="Save output to file")
    args = parser.parse_args()

    results = fetch_pep(args.year, args.county, args.state)
    if not results:
        sys.exit(1)

    if args.output == "json":
        output = json.dumps(results, indent=2)
    else:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["year", "population", "source", "source_url", "fetched_at"])
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
