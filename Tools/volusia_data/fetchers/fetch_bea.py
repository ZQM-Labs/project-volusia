#!/usr/bin/env python3
"""
Project Volusia — BEA Regional Fetcher
Fetches Local Area Personal Income (CAINC1) from BEA (API key required).

Usage:
    python Tools/volusia_data/fetchers/fetch_bea.py [--geofips 12127] [--table CAINC1] [--output csv|json]
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

DEFAULT_GEOFIPS = "12127"  # Volusia County, FL
DEFAULT_TABLE = "CAINC1"

URL = "https://apps.bea.gov/api/data"

LINE_CODES = {
    "1": ("personal_income_total", "thousands USD", "Total personal income"),
    "2": ("population_bea", "persons", "Population (BEA)"),
    "3": ("per_capita_income", "USD", "Per capita personal income"),
}


def fetch_bea(geofips=DEFAULT_GEOFIPS, table=DEFAULT_TABLE):
    """Fetch BEA Regional data for a specific area."""
    api_key = os.environ.get("BEA_API_KEY", "")
    if not api_key:
        print("ERROR: BEA_API_KEY not set", file=sys.stderr)
        return None

    print(f"Fetching BEA Regional for GeoFips {geofips}, table {table}...")

    all_results = []
    for line_code, (ind_name, unit, desc) in LINE_CODES.items():
        params = {
            "UserID": api_key,
            "method": "GetData",
            "datasetname": "Regional",
            "TableName": table,
            "GeoFips": geofips,
            "Year": "ALL",
            "LineCode": line_code,
            "ResultFormat": "json",
        }

        resp = requests.get(URL, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("BEAAPI", {}).get("Results", {})
        if not results or "Error" in results:
            print(f"WARNING: LineCode={line_code} error: {results.get('Error', 'unknown')}", file=sys.stderr)
            continue

        data_list = results.get("Data", [])
        if not data_list:
            continue

        latest_year = max(
            int(d.get("TimePeriod", 0))
            for d in data_list
            if d.get("TimePeriod", "").isdigit()
        )
        latest_items = [d for d in data_list if str(d.get("TimePeriod", "")) == str(latest_year)]

        for item in latest_items:
            val_str = item.get("DataValue", "").replace(",", "").strip()
            try:
                val = float(val_str)
            except (ValueError, TypeError):
                continue
            all_results.append({
                "indicator": ind_name,
                "value": val,
                "unit": unit,
                "year": latest_year,
                "description": desc,
                "source": "BEA Regional",
                "source_url": "https://www.bea.gov/data/income-saving/local-area-personal-income",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })

    if not all_results:
        print("ERROR: No data returned from BEA", file=sys.stderr)
        return None

    return all_results


def main():
    parser = argparse.ArgumentParser(description="Fetch BEA Regional personal income data")
    parser.add_argument("--geofips", default=DEFAULT_GEOFIPS, help="GeoFIPS code (default: 12127)")
    parser.add_argument("--table", default=DEFAULT_TABLE, help="Table name (default: CAINC1)")
    parser.add_argument("--output", choices=["csv", "json"], default="json", help="Output format")
    parser.add_argument("--save", type=Path, help="Save output to file")
    args = parser.parse_args()

    results = fetch_bea(args.geofips, args.table)
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
