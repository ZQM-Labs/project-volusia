#!/usr/bin/env python3
"""
Project Volusia — Data Quality Validation Layer
Validates indicator data for range, freshness, and cross-source coherence.

Usage:
    python Tools/volusia_data/quality/validate.py
"""

import json
import sqlite3
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add Tools to path
TOOLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))

from volusia_data.config import DB_PATH

# Validation rules per indicator
RULES = {
    "total_population_pep_2024": {"min": 500000, "max": 700000, "type": "population"},
    "total_population_pep_2023": {"min": 500000, "max": 700000, "type": "population"},
    "total_population_pep_2022": {"min": 500000, "max": 700000, "type": "population"},
    "unemployment_rate_bls": {"min": 0, "max": 25, "type": "percentage"},
    "employment_qcew": {"min": 100000, "max": 300000, "type": "count"},
    "establishments_qcew": {"min": 10000, "max": 50000, "type": "count"},
    "avg_weekly_wage_qcew": {"min": 500, "max": 3000, "type": "currency"},
    "avg_max_temp_2024": {"min": 200, "max": 350, "type": "temperature"},  # tenths C
    "avg_min_temp_2024": {"min": 100, "max": 250, "type": "temperature"},
    "total_precip_2024": {"min": 5000, "max": 20000, "type": "precipitation"},  # tenths mm
}

# Freshness windows (days)
FRESHNESS = {
    "Census PEP": 365,
    "Census ACS": 365,
    "NOAA NCEI": 2,
    "BLS LAUS": 45,
    "BEA Regional": 365,
    "BLS QCEW": 120,
}

# Cross-source coherence rules
COHERENCE = {
    "population": {
        "indicators": ["total_population_pep_2024", "total_population_pep_2023"],
        "tolerance_pct": 5.0,  # Max 5% difference between sources
    }
}


def validate_range(conn):
    """Check all indicators are within expected ranges."""
    results = []
    rows = conn.execute("SELECT name, value FROM indicators").fetchall()
    
    for name, value in rows:
        try:
            val = float(value)
        except (ValueError, TypeError):
            results.append({"indicator": name, "status": "ERROR", "message": f"Non-numeric value: {value}"})
            continue
        
        if name in RULES:
            rule = RULES[name]
            if val < rule["min"] or val > rule["max"]:
                results.append({
                    "indicator": name,
                    "status": "FAIL",
                    "message": f"Value {val} outside range [{rule['min']}, {rule['max']}]",
                })
            else:
                results.append({"indicator": name, "status": "OK", "message": f"Value {val} within range"})
        else:
            results.append({"indicator": name, "status": "WARN", "message": "No validation rule defined"})
    
    return results


def validate_freshness(conn):
    """Check data freshness per source."""
    results = []
    rows = conn.execute("SELECT name, source, fetched_at FROM indicators").fetchall()
    now = datetime.now(timezone.utc)
    
    for name, source, fetched_at in rows:
        if not fetched_at:
            results.append({"indicator": name, "status": "ERROR", "message": "No fetch timestamp"})
            continue
        
        try:
            fetched = datetime.fromisoformat(fetched_at)
            age_days = (now - fetched).days
            
            max_age = 365  # default
            for key, days in FRESHNESS.items():
                if key in source:
                    max_age = days
                    break
            
            if age_days > max_age:
                results.append({
                    "indicator": name,
                    "status": "STALE",
                    "message": f"{age_days} days old (max {max_age})",
                })
            else:
                results.append({
                    "indicator": name,
                    "status": "OK",
                    "message": f"{age_days} days old (max {max_age})",
                })
        except (ValueError, TypeError):
            results.append({"indicator": name, "status": "ERROR", "message": f"Invalid timestamp: {fetched_at}"})
    
    return results


def validate_coherence(conn):
    """Check cross-source coherence."""
    results = []
    
    for group_name, rule in COHERENCE.items():
        indicators = rule["indicators"]
        tolerance = rule["tolerance_pct"]
        
        values = []
        for ind in indicators:
            row = conn.execute("SELECT value FROM indicators WHERE name = ?", (ind,)).fetchone()
            if row:
                try:
                    values.append(float(row[0]))
                except (ValueError, TypeError):
                    pass
        
        if len(values) >= 2:
            avg = sum(values) / len(values)
            max_diff = max(abs(v - avg) / avg * 100 for v in values)
            
            if max_diff > tolerance:
                results.append({
                    "group": group_name,
                    "status": "WARN",
                    "message": f"Coherence check: {max_diff:.1f}% spread (tolerance {tolerance}%)",
                })
            else:
                results.append({
                    "group": group_name,
                    "status": "OK",
                    "message": f"Coherence check: {max_diff:.1f}% spread (tolerance {tolerance}%)",
                })
    
    return results


def generate_report():
    """Generate full validation report."""
    if not DB_PATH.exists():
        return {"status": "ERROR", "message": "Database does not exist"}
    
    conn = sqlite3.connect(DB_PATH)
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "database": str(DB_PATH),
        "checks": {
            "range": validate_range(conn),
            "freshness": validate_freshness(conn),
            "coherence": validate_coherence(conn),
        },
    }
    
    # Summary
    all_checks = report["checks"]["range"] + report["checks"]["freshness"] + report["checks"]["coherence"]
    report["summary"] = {
        "total": len(all_checks),
        "ok": sum(1 for c in all_checks if c["status"] == "OK"),
        "warn": sum(1 for c in all_checks if c["status"] == "WARN"),
        "fail": sum(1 for c in all_checks if c["status"] == "FAIL"),
        "error": sum(1 for c in all_checks if c["status"] == "ERROR"),
        "stale": sum(1 for c in all_checks if c["status"] == "STALE"),
    }
    
    # Overall status
    if report["summary"]["error"] > 0 or report["summary"]["fail"] > 0:
        report["overall"] = "FAIL"
    elif report["summary"]["stale"] > 0 or report["summary"]["warn"] > 0:
        report["overall"] = "WARN"
    else:
        report["overall"] = "OK"
    
    conn.close()
    return report


def main():
    report = generate_report()
    print(json.dumps(report, indent=2))
    
    # Exit code based on status
    if report["overall"] == "FAIL":
        sys.exit(1)
    elif report["overall"] == "WARN":
        sys.exit(0)  # Warnings don't fail CI
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
