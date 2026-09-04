#!/usr/bin/env python3
"""
Project Volusia — Data Aggregation Tool
Aggregate tract/zip/city data to county level with population-weighted means.

Usage:
    python Tools/volusia_data/processing/aggregate.py --input tracts.csv --to county --weight population
"""

import argparse
import csv
import sys
from pathlib import Path
from collections import defaultdict


def aggregate_to_county(rows, value_col, weight_col=None, group_col="county_fips"):
    """Aggregate data to county level."""
    groups = defaultdict(lambda: {"values": [], "weights": []})
    
    for row in rows:
        group_key = row.get(group_col, "")
        if not group_key:
            continue
        
        try:
            val = float(row.get(value_col, 0))
        except (ValueError, TypeError):
            continue
        
        weight = 1.0
        if weight_col:
            try:
                weight = float(row.get(weight_col, 1))
            except (ValueError, TypeError):
                weight = 1.0
        
        groups[group_key]["values"].append(val)
        groups[group_key]["weights"].append(weight)
    
    results = []
    for group_key, data in sorted(groups.items()):
        vals = data["values"]
        weights = data["weights"]
        
        if weight_col and sum(weights) > 0:
            weighted_sum = sum(v * w for v, w in zip(vals, weights))
            total_weight = sum(weights)
            agg_val = weighted_sum / total_weight
        else:
            agg_val = sum(vals) / len(vals) if vals else 0
        
        results.append({
            group_col: group_key,
            f"{value_col}_mean": round(agg_val, 2),
            f"{value_col}_min": min(vals) if vals else 0,
            f"{value_col}_max": max(vals) if vals else 0,
            f"{value_col}_count": len(vals),
        })
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Aggregate data to county level")
    parser.add_argument("--input", "-i", required=True, help="Input CSV file")
    parser.add_argument("--to", choices=["county", "state"], default="county",
                        help="Aggregation level")
    parser.add_argument("--value", "-v", required=True, help="Value column to aggregate")
    parser.add_argument("--weight", "-w", help="Weight column (for weighted mean)")
    parser.add_argument("--group-col", default="county_fips", help="Group-by column")
    parser.add_argument("--output", "-o", help="Output CSV file")
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

    if args.value not in rows[0]:
        print(f"ERROR: Value column '{args.value}' not found. Available: {list(rows[0].keys())}", file=sys.stderr)
        sys.exit(1)

    results = aggregate_to_county(rows, args.value, args.weight, args.group_col)

    # Output
    if results:
        output_headers = list(results[0].keys())
        output_lines = [",".join(output_headers)]
        for r in results:
            output_lines.append(",".join(str(r.get(h, '')) for h in output_headers))
        result_text = "\n".join(output_lines)
    else:
        result_text = "no data"

    if args.output:
        Path(args.output).write_text(result_text)
        print(f"Saved to {args.output}")
    else:
        print(result_text)


if __name__ == "__main__":
    main()
