#!/usr/bin/env python3
"""
Project Volusia — Data Quality Validation Layer
Validates indicator data for range, freshness, and cross-source coherence.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "volusia_data" / "volusia.db"

# Validation rules per indicator
RULES = {
    # Demographics
    "total_population_pep_2024": {"min": 500000, "max": 700000, "type": "population"},
    "total_population_pep_2023": {"min": 500000, "max": 700000, "type": "population"},
    "total_population_pep_2022": {"min": 500000, "max": 700000, "type": "population"},
    "population_2025_estimate": {"min": 500000, "max": 700000, "type": "population"},
    "median_age": {"min": 20, "max": 70, "type": "years"},
    "population_over_65": {"min": 5, "max": 40, "type": "percentage"},
    "population_under_18": {"min": 10, "max": 35, "type": "percentage"},
    "hispanic_latino": {"min": 0, "max": 50, "type": "percentage"},
    "white_alone": {"min": 0, "max": 100, "type": "percentage"},
    "black_alone": {"min": 0, "max": 50, "type": "percentage"},
    "asian_alone": {"min": 0, "max": 20, "type": "percentage"},
    "foreign_born_rate": {"min": 0, "max": 30, "type": "percentage"},
    "veterans_count": {"min": 10000, "max": 100000, "type": "count"},
    "avg_household_size": {"min": 1, "max": 5, "type": "count"},
    "persons_per_household": {"min": 1, "max": 5, "type": "count"},
    
    # Economy
    "median_household_income": {"min": 30000, "max": 150000, "type": "currency"},
    "per_capita_income_census": {"min": 20000, "max": 80000, "type": "currency"},
    "poverty_rate": {"min": 0, "max": 30, "type": "percentage"},
    "unemployment_rate_bls": {"min": 0, "max": 25, "type": "percentage"},
    "civilian_labor_force_rate": {"min": 30, "max": 80, "type": "percentage"},
    "establishments_qcew": {"min": 5000, "max": 50000, "type": "count"},
    "employment_qcew": {"min": 50000, "max": 500000, "type": "count"},
    "avg_weekly_wage_qcew": {"min": 500, "max": 3000, "type": "currency"},
    "total_employment_census": {"min": 50000, "max": 500000, "type": "count"},
    "total_annual_payroll": {"min": 1000000000, "max": 50000000000, "type": "currency"},
    "employer_firms": {"min": 1000, "max": 50000, "type": "count"},
    "female_owned_firms": {"min": 100, "max": 20000, "type": "count"},
    "male_owned_firms": {"min": 100, "max": 30000, "type": "count"},
    "retail_sales_2022": {"min": 1000000000, "max": 50000000000, "type": "currency"},
    "hospitality_sales_2022": {"min": 100000000, "max": 5000000000, "type": "currency"},
    "healthcare_revenue_2022": {"min": 100000000, "max": 10000000000, "type": "currency"},
    "transportation_revenue_2022": {"min": 100000000, "max": 2000000000, "type": "currency"},
    "edc_investment_millions": {"min": 1, "max": 1000, "type": "count"},
    "target_industries": {"min": 1, "max": 20, "type": "count"},
    "major_employers_count": {"min": 1, "max": 200, "type": "count"},
    "amazon_facility_value": {"min": 100000000, "max": 500000000, "type": "currency"},
    "farmton_development": {"min": 1000, "max": 50000, "type": "count"},
    "ormond_crossings_development": {"min": 100, "max": 5000, "type": "count"},
    "business_resources_providers": {"min": 1, "max": 50, "type": "count"},
    
    # Housing
    "median_home_value": {"min": 100000, "max": 600000, "type": "currency"},
    "median_gross_rent": {"min": 500, "max": 3000, "type": "currency"},
    "building_permits_2025": {"min": 1000, "max": 10000, "type": "count"},
    "owner_occupied_rate": {"min": 30, "max": 90, "type": "percentage"},
    "housing_units_2025": {"min": 100000, "max": 500000, "type": "count"},
    "median_home_price_zillow": {"min": 100000, "max": 600000, "type": "currency"},
    
    # Education
    "high_school_grad_rate": {"min": 70, "max": 100, "type": "percentage"},
    "bachelors_degree_rate": {"min": 10, "max": 60, "type": "percentage"},
    "school_district_grade": {"min": 0, "max": 0, "type": "skip"},
    "school_district_grade_2026": {"min": 0, "max": 0, "type": "skip"},
    "schools_total": {"min": 50, "max": 100, "type": "count"},
    "schools_elementary": {"min": 20, "max": 60, "type": "count"},
    "schools_middle": {"min": 5, "max": 20, "type": "count"},
    "schools_high": {"min": 5, "max": 20, "type": "count"},
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
    "school_district_website": {"min": 0, "max": 0, "type": "skip"},
    "fl_doe_grades": {"min": 0, "max": 0, "type": "skip"},
    
    # Health
    "uninsured_rate": {"min": 0, "max": 30, "type": "percentage"},
    "disability_rate": {"min": 0, "max": 30, "type": "percentage"},
    "hospitals_in_county": {"min": 1, "max": 10, "type": "count"},
    "covid_total_cases": {"min": 100000, "max": 300000, "type": "count"},
    "covid_total_deaths": {"min": 1000, "max": 5000, "type": "count"},
    "halifal_health_covid_peak": {"min": 50, "max": 200, "type": "count"},
    "vaccination_dose1_pct": {"min": 50, "max": 100, "type": "percentage"},
    "vaccination_series_complete": {"min": 40, "max": 100, "type": "percentage"},
    "vaccination_booster_pct": {"min": 20, "max": 100, "type": "percentage"},
    "air_quality_median_aqi": {"min": 30, "max": 100, "type": "score"},
    "air_quality_good_days": {"min": 200, "max": 365, "type": "count"},
    "superfund_sites_fl": {"min": 1, "max": 100, "type": "count"},
    "volusia_sole_source_aquifer": {"min": 0, "max": 1, "type": "count"},
    
    # Public Safety
    "crime_rate_per_100k": {"min": 500, "max": 5000, "type": "count"},
    "safety_score": {"min": 0, "max": 100, "type": "score"},
    "vcso_arrests_daily_avg": {"min": 1, "max": 50, "type": "count"},
    "spotcrime_monthly_avg": {"min": 1, "max": 50, "type": "count"},
    "sheriff_website": {"min": 0, "max": 0, "type": "skip"},
    "fdle_ucb_reports": {"min": 0, "max": 1, "type": "count"},
    "crime_by_county": {"min": 0, "max": 0, "type": "skip"},
    "spotcrime_analytics": {"min": 0, "max": 0, "type": "skip"},
    "arrest_records_portal": {"min": 0, "max": 0, "type": "skip"},
    "flccis_portal": {"min": 0, "max": 0, "type": "skip"},
    
    # Government
    "county_main_website": {"min": 0, "max": 0, "type": "skip"},
    "open_data_portal": {"min": 0, "max": 0, "type": "skip"},
    "gis_data_layers_count": {"min": 10, "max": 200, "type": "count"},
    "parcel_database_tables": {"min": 5, "max": 30, "type": "count"},
    "property_appraiser_csv": {"min": 0, "max": 1, "type": "count"},
    "elections_website": {"min": 0, "max": 0, "type": "skip"},
    "campaign_finance_portal": {"min": 0, "max": 1, "type": "count"},
    "clerk_of_court": {"min": 0, "max": 0, "type": "skip"},
    "permit_guide_portal": {"min": 0, "max": 0, "type": "skip"},
    "connect_live_portal": {"min": 0, "max": 1, "type": "count"},
    "opendata_portals": {"min": 1, "max": 10, "type": "count"},
    "gis_data_layers": {"min": 10, "max": 200, "type": "count"},
    "parcel_count": {"min": 100000, "max": 500000, "type": "count"},
    "public_libraries": {"min": 5, "max": 20, "type": "count"},
    "elections_facebook": {"min": 0, "max": 1, "type": "count"},
    "elections_twitter": {"min": 0, "max": 1, "type": "count"},
    "elections_instagram": {"min": 0, "max": 1, "type": "count"},
    "county_facebook": {"min": 0, "max": 1, "type": "count"},
    
    # Economy
    "edc_website": {"min": 0, "max": 0, "type": "skip"},
    "team_volusia": {"min": 0, "max": 0, "type": "skip"},
    "volusia_business_resources": {"min": 0, "max": 0, "type": "skip"},
    "micaPlex_incubator": {"min": 0, "max": 1, "type": "count"},
    
    # Infrastructure
    "fcc_broadband_map": {"min": 0, "max": 0, "type": "skip"},
    "internet_providers_count": {"min": 1, "max": 10, "type": "count"},
    "fiber_provider_coverage": {"min": 0, "max": 100, "type": "percentage"},
    "broadband_data_collection": {"min": 0, "max": 0, "type": "skip"},
    
    # Media
    "primary_newspaper": {"min": 0, "max": 0, "type": "skip"},
    "newspaper_founded": {"min": 1800, "max": 2026, "type": "count"},
    "newspaper_circulation": {"min": 10000, "max": 50000, "type": "count"},
    "local_news_sites": {"min": 1, "max": 20, "type": "count"},
    
    # Climate
    "avg_max_temp_2024": {"min": 200, "max": 350, "type": "temperature"},
    "avg_min_temp_2024": {"min": 100, "max": 250, "type": "temperature"},
    "total_precip_2024": {"min": 5000, "max": 20000, "type": "precipitation"},
    
    # Transportation
    "mean_travel_time_work": {"min": 10, "max": 50, "type": "time"},
    "mean_commute_time": {"min": 10, "max": 60, "type": "time"},
}

FRESHNESS = {
    "census": 365,
    "bls": 45,
    "bea": 120,
    "noaa": 2,
    "qcew": 120,
    "laus": 45,
    "pep": 365,
    "acs": 365,
    "fl doe": 365,
    "fdle": 365,
    "florida": 365,
    "cms": 365,
    "cdc": 365,
    "epa": 365,
    "fcc": 180,
}


def validate_range(conn):
    """Check all indicators are within expected ranges."""
    results = []
    rows = conn.execute("SELECT name, value FROM indicators").fetchall()
    
    for name, value in rows:
        if name in RULES and RULES[name].get("type") == "skip":
            results.append({"indicator": name, "status": "OK", "message": "Skipped"})
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
            if val >= 0:
                results.append({"indicator": name, "status": "OK", "message": "Value within default range"})
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
            if fetched.tzinfo is None:
                fetched = fetched.replace(tzinfo=timezone.utc)
            age_days = (now - fetched).days
            
            max_age = 365  # default
            for key, days in FRESHNESS.items():
                if key.lower() in source.lower():
                    max_age = days
                    break
            
            if age_days > max_age:
                results.append({"indicator": name, "status": "ERROR", "message": f"Data is {age_days} days old, max {max_age}"})
            else:
                results.append({"indicator": name, "status": "OK", "message": f"Fetched {age_days} days ago"})
        except Exception as e:
            results.append({"indicator": name, "status": "ERROR", "message": f"Invalid timestamp: {e}"})
    
    return results


def generate_report():
    """Generate full quality report."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    range_results = validate_range(conn)
    freshness_results = validate_freshness(conn)
    
    all_checks = range_results + freshness_results
    
    ok = len([c for c in all_checks if c["status"] == "OK"])
    warn = len([c for c in all_checks if c["status"] == "WARN"])
    fail = len([c for c in all_checks if c["status"] == "FAIL"])
    error = len([c for c in all_checks if c["status"] == "ERROR"])
    
    overall = "OK" if error == 0 and fail == 0 else "FAIL"
    
    report = {
        "overall": overall,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": len(all_checks),
            "ok": ok,
            "warn": warn,
            "fail": fail,
            "error": error,
        },
        "checks": {
            "range": range_results,
            "freshness": freshness_results,
        },
    }
    
    conn.close()
    return report


if __name__ == "__main__":
    report = generate_report()
    print(json.dumps(report, indent=2))
