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
    "total_precip_2024": {"min": 5000, "max": 20000, "type": "precipitation"},

    "population_2025_estimate": {"min": 500000, "max": 700000, "type": "population"},
    "median_household_income": {"min": 30000, "max": 150000, "type": "currency"},
    "per_capita_income_census": {"min": 20000, "max": 80000, "type": "currency"},
    "poverty_rate": {"min": 0, "max": 30, "type": "percentage"},
    "median_home_value": {"min": 100000, "max": 600000, "type": "currency"},
    "median_gross_rent": {"min": 500, "max": 3000, "type": "currency"},
    "building_permits_2025": {"min": 1000, "max": 10000, "type": "count"},

    "crime_rate_per_100k": {"min": 500, "max": 5000, "type": "count"},
    "safety_score": {"min": 0, "max": 100, "type": "score"},
    "vcso_arrests_daily_avg": {"min": 1, "max": 50, "type": "count"},
    "spotcrime_monthly_avg": {"min": 1, "max": 50, "type": "count"},
    "school_district_grade": {"min": 0, "max": 0, "type": "skip"},
    "schools_a_grade": {"min": 0, "max": 100, "type": "count"},
    "schools_ab_grade_pct": {"min": 0, "max": 100, "type": "percentage"},
    "schools_df_grade": {"min": 0, "max": 20, "type": "count"},
    "ela_proficiency": {"min": 0, "max": 100, "type": "percentage"},
    "math_proficiency": {"min": 0, "max": 100, "type": "percentage"},
    "algebra1_proficiency": {"min": 0, "max": 100, "type": "percentage"},
    "geometry_proficiency": {"min": 0, "max": 100, "type": "percentage"},
    "biology_proficiency": {"min": 0, "max": 100, "type": "percentage"},
    "us_history_proficiency": {"min": 0, "max": 100, "type": "percentage"},
    "civics_proficiency": {"min": 0, "max": 100, "type": "percentage"},
    "major_employers_count": {"min": 1, "max": 200, "type": "count"},
    "edc_investment_millions": {"min": 1, "max": 1000, "type": "count"},
    "target_industries": {"min": 1, "max": 20, "type": "count"},
    "opendata_portals": {"min": 1, "max": 10, "type": "count"},
    "gis_data_layers": {"min": 10, "max": 200, "type": "count"},
    "parcel_count": {"min": 100000, "max": 500000, "type": "count"},
    "median_home_price_zillow": {"min": 100000, "max": 600000, "type": "currency"},
    "avg_household_size": {"min": 1, "max": 5, "type": "count"},
    "persons_per_household": {"min": 1, "max": 5, "type": "count"},
    "mean_commute_time": {"min": 10, "max": 60, "type": "time"},
    "business_resources_providers": {"min": 1, "max": 50, "type": "count"},

    "high_school_grad_rate": {"min": 70, "max": 100, "type": "percentage"},
    "bachelors_degree_rate": {"min": 10, "max": 60, "type": "percentage"},
    "civilian_labor_force_rate": {"min": 30, "max": 80, "type": "percentage"},
    "uninsured_rate": {"min": 0, "max": 30, "type": "percentage"},
    "disability_rate": {"min": 0, "max": 30, "type": "percentage"},
    "foreign_born_rate": {"min": 0, "max": 30, "type": "percentage"},
    "owner_occupied_rate": {"min": 30, "max": 90, "type": "percentage"},
    "mean_travel_time_work": {"min": 10, "max": 50, "type": "time"},
    "veterans_count": {"min": 10000, "max": 100000, "type": "count"},
    "housing_units_2025": {"min": 100000, "max": 500000, "type": "count"},
    "employer_establishments": {"min": 5000, "max": 50000, "type": "count"},
    "total_employment_census": {"min": 50000, "max": 500000, "type": "count"},
    "total_annual_payroll": {"min": 1000000000, "max": 50000000000, "type": "currency"},
    "employer_firms": {"min": 1000, "max": 50000, "type": "count"},
    "female_owned_firms": {"min": 100, "max": 20000, "type": "count"},
    "male_owned_firms": {"min": 100, "max": 30000, "type": "count"},
    "retail_sales_2022": {"min": 1000000000, "max": 50000000000, "type": "currency"},
    "hospitality_sales_2022": {"min": 100000000, "max": 5000000000, "type": "currency"},
    "healthcare_revenue_2022": {"min": 100000000, "max": 10000000000, "type": "currency"},
    "transportation_revenue_2022": {"min": 100000000, "max": 2000000000, "type": "currency"},
    "median_age": {"min": 20, "max": 70, "type": "years"},
    "population_over_65": {"min": 5, "max": 40, "type": "percentage"},
    "population_under_18": {"min": 10, "max": 35, "type": "percentage"},
    "hispanic_latino": {"min": 0, "max": 50, "type": "percentage"},
    "white_alone": {"min": 0, "max": 100, "type": "percentage"},
    "black_alone": {"min": 0, "max": 50, "type": "percentage"},
    "asian_alone": {"min": 0, "max": 20, "type": "percentage"},
  # tenths mm
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
        if name in RULES and RULES[name].get("type") == "skip":
            results.append({"indicator": name, "status": "OK", "message": "Skipped (non-numeric)"})
            continue
        
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
