#!/usr/bin/env python3
"""
Project Volusia — Data Processing Tools
clean.py: Standardize, validate, and clean indicator datasets.

Usage:
    python Tools/volusia_data/processing/clean.py --input data.csv --output cleaned.csv
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone


def clean_column_names(headers):
    """Standardize column names: lowercase, underscores, no special chars."""
    cleaned = []
    for h in headers:
        h = h.strip().lower()
        h = re.sub(r'[^a-z0-9_]', '_', h)
        h = re.sub(r'_+', '_', h)
        h = h.strip('_')
        cleaned.append(h)
    return cleaned


def detect_outliers(values, threshold=3.0):
    """Detect outliers using z-score method. Returns set of indices."""
    numeric = []
    for i, v in enumerate(values):
        try:
            numeric.append((i, float(v)))
        except (ValueError, TypeError):
            pass
    
    if len(numeric) < 3:
        return set()
    
    mean = sum(v for _, v in numeric) / len(numeric)
    variance = sum((v - mean) ** 2 for _, v in numeric) / len(numeric)
    std = variance ** 0.5
    
    if std == 0:
        return set()
    
    outliers = set()
    for i, v in numeric:
        z = abs(v - mean) / std
        if z > threshold:
            outliers.add(i)
    
    return outliers


def handle_missing(values, strategy='skip'):
    """Handle missing values. Strategy: skip, zero, mean."""
    numeric = []
    for v in values:
        try:
            numeric.append(float(v))
        except (ValueError, TypeError):
            numeric.append(None)
    
    if strategy == 'zero':
        return [0.0 if v is None else v for v in numeric]
    elif strategy == 'mean':
        valid = [v for v in numeric if v is not None]
        mean_val = sum(valid) / len(valid) if valid else 0.0
        return [mean_val if v is None else v for v in numeric]
    else:  # skip
        return numeric


def validate_formats(rows, schema=None):
    """Validate rows against a simple schema."""
    issues = []
    for i, row in enumerate(rows):
        if schema:
            for col, dtype in schema.items():
                if col in row:
                    val = row[col]
                    if dtype == 'int':
                        try:
                            int(val)
                        except (ValueError, TypeError):
                            issues.append(f"Row {i}: {col} should be int, got '{val}'")
                    elif dtype == 'float':
                        try:
                            float(val)
                        except (ValueError, TypeError):
                            issues.append(f"Row {i}: {col} should be float, got '{val}'")
    return issues


def main():
    parser = argparse.ArgumentParser(description="Clean and standardize data")
    parser.add_argument("--input", "-i", required=True, help="Input CSV file")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--missing", choices=["skip", "zero", "mean"], default="skip",
                        help="Missing value strategy")
    parser.add_argument("--outlier-threshold", type=float, default=3.0,
                        help="Z-score threshold for outlier detection")
    parser.add_argument("--detect-outliers", action="store_true",
                        help="Add outlier flag column")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, 'r') as f:
        reader = csv.DictReader(f)
        original_headers = reader.fieldnames or []
        rows = list(reader)

    # Clean column names
    new_headers = clean_column_names(original_headers)
    header_map = dict(zip(original_headers, new_headers))
    
    cleaned_rows = []
    for row in rows:
        new_row = {header_map[k]: v for k, v in row.items()}
        cleaned_rows.append(new_row)

    # Detect outliers if requested
    if args.detect_outliers and cleaned_rows:
        for col in new_headers:
            values = [r.get(col, '') for r in cleaned_rows]
            outliers = detect_outliers(values, args.outlier_threshold)
            for i in outliers:
                cleaned_rows[i][f"{col}_outlier"] = "true"

    # Output
    output = []
    output.append(",".join(new_headers))
    for row in cleaned_rows:
        output.append(",".join(str(row.get(h, '')) for h in new_headers))

    result = "\n".join(output)
    
    if args.output:
        Path(args.output).write_text(result)
        print(f"Saved to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
