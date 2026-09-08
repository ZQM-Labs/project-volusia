#!/usr/bin/env python3
"""
Project Volusia — Unified Data Pipeline (v2.1)
Enhanced version with type hints, retry logic, and improved error handling.

Run: python -m volusia_data.refresh_v2
"""

from __future__ import annotations

__version__ = "2.1.0"

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional
import hashlib

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── Configuration ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "volusia.db"
LOG_PATH = ROOT / "fetch_log.jsonl"

# FIPS codes for Volusia County, FL
STATE_FIPS = "12"
COUNTY_FIPS = "127"

# Retry configuration (for transient network errors)
RETRY_TOTAL = 3
RETRY_BACKOFF_FACTOR = 0.5
RETRY_STATUS_FORCELIST = {429, 500, 502, 503, 504}

# ── Session with Retry Logic ───────────────────────────────────────────────
def _create_session() -> requests.Session:
    """Create requests session with automatic retry logic."""
    session = requests.Session()
    retry = Retry(
        total=RETRY_TOTAL,
        backoff_factor=RETRY_BACKOFF_FACTOR,
        status_forcelist=RETRY_STATUS_FORCELIST,
        allowed_methods={"GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"},
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": "Project-Volusia/2.1 (data-pipeline)",
        "Accept": "application/json, text/csv, application/xml",
    })
    return session


SESSION = _create_session()

# ── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("volusia_pipeline")


# ── Database Helpers ────────────────────────────────────────────────────────
def get_db() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> sqlite3.Connection:
    """Initialize database with required tables."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            value TEXT,
            unit TEXT,
            category TEXT DEFAULT '',
            source TEXT,
            source_url TEXT,
            vintage TEXT,
            fetched_at TEXT,
            description TEXT,
            checksum TEXT,
            signature TEXT,
            FOREIGN KEY (fetched_at) REFERENCES fetch_manifest(fetched_at)
        );
        CREATE TABLE IF NOT EXISTS time_series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_name TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT,
            source TEXT,
            vintage TEXT,
            fetched_at TEXT NOT NULL,
            FOREIGN KEY (indicator_name) REFERENCES indicators(name)
        );
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            content TEXT,
            fetched_at TEXT,
            checksum TEXT
        );
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            details TEXT,
            timestamp TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS fetch_manifest (
            fetched_at TEXT PRIMARY KEY,
            run_id TEXT,
            duration_ms INTEGER,
            status TEXT,
            indicators_count INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_indicators_source ON indicators(source);
        CREATE INDEX IF NOT EXISTS idx_indicators_category ON indicators(category);
        CREATE INDEX IF NOT EXISTS idx_ts_indicator_date ON time_series(indicator_name, fetched_at);
    """)
    conn.commit()
    return conn


def compute_checksum(value: str, source: str, vintage: str) -> str:
    """Compute SHA256 checksum for data integrity verification."""
    data = f"{value}|{source}|{vintage}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def upsert_indicator(
    name: str,
    value: str | int | float | Decimal,
    unit: str = "",
    category: str = "",
    source: str = "",
    source_url: str = "",
    vintage: str = "",
    description: str = "",
    signature: str = "",
) -> bool:
    """Insert or update an indicator with data integrity metadata."""
    if isinstance(value, Decimal):
        value = str(value)
    elif isinstance(value, (int, float)):
        value = str(value)
    
    conn = get_db()
    ts = datetime.now(timezone.utc).isoformat()
    
    checksum = compute_checksum(str(value), source, vintage)
    
    try:
        conn.execute("""
            INSERT INTO indicators 
            (name, value, unit, category, source, source_url, vintage, fetched_at, description, checksum, signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                value=excluded.value, unit=excluded.unit,
                category=excluded.category, source=excluded.source,
                source_url=excluded.source_url, vintage=excluded.vintage,
                fetched_at=excluded.fetched_at, description=excluded.description,
                checksum=excluded.checksum, signature=excluded.signature
        """, (name, str(value), unit, category, source, source_url, vintage, ts, description, checksum, signature))
        
        # Also store in time_series for historical tracking
        try:
            numeric_val = float(value)
            conn.execute("""
                INSERT OR IGNORE INTO time_series 
                (indicator_name, value, unit, source, vintage, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, numeric_val, unit, source, vintage, ts))
        except (ValueError, TypeError):
            pass
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        log.error(f"Database error upserting {name}: {e}")
        return False


def log_action(action: str, details: str = "") -> None:
    """Log an action to the audit log."""
    conn = get_db()
    conn.execute("INSERT INTO audit_log (action, details) VALUES (?, ?)",
                 (action, details))
    conn.commit()


def log_fetch(source: str, status: str, details: str = "") -> None:
    """Log a fetch attempt to the JSONL audit log."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "status": status,
        "details": details,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ═════════════════════════════════════════════════════════════════════════
# FETCHER: Census PEP (Population Estimates) — NO KEY NEEDED
# Official Census Bureau county population estimates, July 1 of each year.
# ═════════════════════════════════════════════════════════════════════════
def fetch_census_pep() -> bool:
    """Fetch population estimates from Census PEP (CSV, no API key required)."""
    url = (
        "https://www2.census.gov/programs-surveys/popest/"
        "datasets/2020-2025/counties/totals/co-est2025-alldata.csv"
    )
    source_name = "Census PEP"
    log.info(f"Fetching {source_name}...")

    try:
        resp = SESSION.get(url, timeout=30)
        resp.raise_for_status()
        lines = resp.text.strip().split("\n")
        
        if len(lines) < 2:
            log_fetch(source_name, "FAIL", "CSV has no data rows")
            return False
        
        header = lines[0].split(",")
        
        volusia_row = None
        for line in lines[1:]:
            # CSV quote-aware parsing
            if line.count('"') >= 2:
                # Handle quoted fields
                line = line.replace('"', '')
                fields = line.split(",")
            else:
                fields = line.split(",")
            
            # State=12 (Florida), County=127 (Volusia)
            if len(fields) > 4 and fields[3].strip() == STATE_FIPS and fields[4].strip() == COUNTY_FIPS:
                volusia_row = dict(zip(header, fields))
                break

        if not volusia_row:
            log_fetch(source_name, "FAIL", f"Volusia row not found (fips={STATE_FIPS}{COUNTY_FIPS})")
            return False

        # Extract population estimates with validation
        pop_data = {}
        for year in [2022, 2023, 2024, 2025]:
            key = f"POPESTIMATE{year}"
            val = volusia_row.get(key, "N/A")
            try:
                pop_data[year] = str(int(float(val)))
            except (ValueError, TypeError):
                pop_data[year] = "N/A"

        # Upsert all years available
        for year, pop in pop_data.items():
            if pop != "N/A":
                upsert_indicator(
                    f"total_population_pep_{year}", pop, "persons", "Demographics",
                    source_name, url, str(year),
                    f"Census PEP county population estimate, July 1 {year}"
                )

        log_fetch(source_name, "OK", f"pop_2024={pop_data.get(2024, 'N/A')}")
        log_action("fetch_census_pep", f"years={list(pop_data.keys())}")
        log.info(f"  OK: {len([p for p in pop_data.values() if p != 'N/A'])} years of population data")
        return True

    except requests.RequestException as e:
        log_fetch(source_name, "ERROR", f"Request failed: {e}")
        log.error(f"  ERROR: {e}")
        return False
    except Exception as e:
        log_fetch(source_name, "ERROR", f"Unexpected error: {e}")
        log.error(f"  ERROR: {e}")
        return False


# ═════════════════════════════════════════════════════════════════════════
# FETCHER: Census ACS (5-Year Estimates) — API KEY REQUIRED
# ═════════════════════════════════════════════════════════════════════════
def fetch_census_acs() -> bool:
    """Fetch demographic data from Census ACS API."""
    api_key = os.environ.get("CENSUS_API_KEY", "")
    if not api_key:
        log_fetch("Census ACS", "SKIP", "No CENSUS_API_KEY configured")
        log.info("  SKIP: Set CENSUS_API_KEY environment variable")
        return False

    # ACS 5-year 2023 — DP02 (employment status), DP05 (race/ethnicity)
    url = "https://api.census.gov/data/2023/acs/acs5"
    source_name = "Census ACS (API)"
    log.info(f"Fetching {source_name}...")

    # Multiple variable groups
    var_groups = {
        "education": "DP02_0001E,DP02_0002E,DP02_0018E",  # Educational attainment
        "poverty": "DP03_0004E,DP03_0005E,DP03_0006PE",  # Labor force + poverty
        "race": "DP05_0002E,DP05_0003E,DP05_0004E,DP05_0005E,DP05_0006E",  # Race
    }

    all_ok = True
    for group_name, vars_str in var_groups.items():
        params = {
            "get": f"NAME,{vars_str}",
            "for": f"county:{COUNTY_FIPS}",
            "in": f"state:{STATE_FIPS}",
            "key": api_key,
        }

        try:
            resp = SESSION.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            if not data or len(data) < 2:
                log_fetch(source_name, "FAIL", f"Group {group_name}: Empty response")
                all_ok = False
                continue

            # First row is header, second is data
            header = data[0]
            values = data[1]
            
            # Create mapping
            row = dict(zip(header, values))
            
            # Extract specific values
            if "DP02_0001E" in row:
                try:
                    upsert_indicator(
                        f"education_achievement_population",
                        row["DP02_0001E"], "persons", "Education",
                        source_name, url, "2023",
                        f"ACS: Population 25+ with educational attainment data"
                    )
                except (ValueError, KeyError):
                    pass

            log_fetch(source_name, "OK", f"Group {group_name}: {len(row)-2} variables")
            
        except requests.RequestException as e:
            log_fetch(source_name, "ERROR", f"Group {group_name}: {e}")
            all_ok = False
        except Exception as e:
            log_fetch(source_name, "ERROR", f"Group {group_name}: {e}")
            all_ok = False

    if all_ok:
        log_action("fetch_census_acs", f"groups_completed={len(var_groups)}")
    return all_ok


# ═════════════════════════════════════════════════════════════════════════
# FETCHER: NOAA NCEI — daily weather summaries
# ═════════════════════════════════════════════════════════════════════════
def fetch_noaa() -> bool:
    """Fetch daily weather data from NOAA NCEI API."""
    station = "USW00012838"  # Daytona Beach Intl Airport
    base_url = "https://www.ncei.noaa.gov/access/services/data/v1"
    source_name = "NOAA NCEI"
    log.info(f"Fetching {source_name}...")

    start_year = datetime.now().year - 1
    params = {
        "dataset": "daily-summaries",
        "stations": station,
        "dataTypes": "TMAX,TMIN,PRCP,AWND,SNOW",
        "startDate": f"{start_year}-01-01",
        "endDate": f"{datetime.now().year}-12-31",
        "format": "json",
        "limit": 10000,
    }

    try:
        resp = SESSION.get(base_url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            log_fetch(source_name, "FAIL", "Empty response")
            return False

        # Aggregate climate data
        tmax_vals = [int(d.get("TMAX", 0)) for d in data if d.get("TMAX")]
        tmin_vals = [int(d.get("TMIN", 0)) for d in data if d.get("TMIN")]
        prcp_vals = [int(d.get("PRCP", 0)) for d in data if d.get("PRCP")]
        
        # Calculate statistics
        stats = {
            "avg_max_temp": round(sum(tmax_vals) / len(tmax_vals), 1) if tmax_vals else 0,
            "avg_min_temp": round(sum(tmin_vals) / len(tmin_vals), 1) if tmin_vals else 0,
            "total_precip": sum(prcp_vals) if prcp_vals else 0,
            "record_temp_max": max(tmax_vals) if tmax_vals else 0,
            "record_temp_min": min(tmin_vals) if tmin_vals else 0,
        }

        # Upsert indicators
        upsert_indicator("avg_max_temp", stats["avg_max_temp"], "tenths C", "Climate",
                         source_name, f"{base_url}?station={station}", str(datetime.now().year),
                         "NOAA average daily max temperature")
        upsert_indicator("avg_min_temp", stats["avg_min_temp"], "tenths C", "Climate",
                         source_name, base_url, str(datetime.now().year),
                         "NOAA average daily min temperature")
        upsert_indicator("total_precip", stats["total_precip"], "tenths mm", "Climate",
                         source_name, base_url, str(datetime.now().year),
                         "NOAA total precipitation")

        log_fetch(source_name, "OK", f"records={len(data)}, days_processed")
        log_action("fetch_noaa", f"records={len(data)}, temp_range=[{stats['record_temp_min']}, {stats['record_temp_max']}]")
        log.info(f"  OK: {len(data)} records, avg TMAX={stats['avg_max_temp']} tenths C")
        return True

    except requests.RequestException as e:
        log_fetch(source_name, "ERROR", str(e))
        log.error(f"  ERROR: {e}")
        return False
    except Exception as e:
        log_fetch(source_name, "ERROR", str(e))
        log.error(f"  ERROR: {e}")
        return False


# ═════════════════════════════════════════════════════════════════════════
# FETCHER: BLS LAUS — Local Area Unemployment Statistics
# ═════════════════════════════════════════════════════════════════════════
def fetch_bls() -> bool:
    """Fetch unemployment data from BLS LAUS API."""
    api_key = os.environ.get("BLS_API_KEY", "")
    if not api_key:
        log_fetch("BLS LAUS", "SKIP", "No BLS_API_KEY configured")
        log.info("  SKIP: Set BLS_API_KEY environment variable")
        return False

    # LAUS series for Volusia County, FL
    series_id = "LAUST121270000000003"
    api_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    source_name = "BLS LAUS"
    log.info(f"Fetching {source_name} (series: {series_id})...")

    payload = {
        "seriesid": [series_id],
        "startyear": str(datetime.now().year - 3),
        "endyear": str(datetime.now().year),
        "registrationkey": api_key,
    }

    try:
        resp = SESSION.post(api_url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "REQUEST_SUCCEEDED":
            log_fetch(source_name, "FAIL", f"API status: {data.get('status')}")
            return False

        series_list = data.get("Results", {}).get("series", [])
        if not series_list:
            log_fetch(source_name, "FAIL", "No series in response")
            return False

        # Process observations
        rows = []
        for serie in series_list:
            for obs in serie.get("data", []):
                val_str = obs.get("value", "").strip()
                try:
                    val = float(val_str)
                    rows.append({
                        "year": int(obs["year"]),
                        "period": obs["period"],
                        "period_name": obs.get("periodName", ""),
                        "value": val,
                    })
                except (ValueError, TypeError):
                    continue

        if not rows:
            log_fetch(source_name, "FAIL", "No valid numeric rows")
            return False

        # Sort by date (newest first)
        rows.sort(key=lambda x: (x["year"], x["period"]), reverse=True)
        
        # Get latest data point
        latest = rows[0]
        
        # Calculate 3-month average if we have recent data
        recent_3mo = [r["value"] for r in rows[:3]] if len(rows) >= 3 else [latest["value"]]
        avg_val = sum(recent_3mo) / len(recent_3mo)

        upsert_indicator(
            "unemployment_rate",
            f"{avg_val:.1f}",
            "percent", "Economy",
            source_name, "https://www.bls.gov/lau/",
            f"{latest['year']} {latest['period_name']}",
            f"BLS LAUS unemployment rate (3-mo avg)"
        )

        log_fetch(source_name, "OK", f"rate={avg_val:.1f}%, points={len(rows)}")
        log_action("fetch_bls", f"rate={avg_val:.1f}%, data_points={len(rows)}")
        log.info(f"  OK: unemployment rate={avg_val:.1f}% ({len(rows)} data points)")
        return True

    except requests.RequestException as e:
        log_fetch(source_name, "ERROR", str(e))
        log.error(f"  ERROR: {e}")
        return False
    except Exception as e:
        log_fetch(source_name, "ERROR", str(e))
        log.error(f"  ERROR: {e}")
        return False


# ═════════════════════════════════════════════════════════════════════════
# FETCHER: BEA Regional — Local Area Personal Income
# ═════════════════════════════════════════════════════════════════════════
def fetch_bea() -> bool:
    """Fetch regional economic data from BEA API."""
    api_key = os.environ.get("BEA_API_KEY", "")
    if not api_key:
        log_fetch("BEA Regional", "SKIP", "No BEA_API_KEY configured")
        log.info("  SKIP: Set BEA_API_KEY environment variable")
        return False

    source_name = "BEA Regional"
    log.info(f"Fetching {source_name}...")

    base_url = "https://apps.bea.gov/api/data"
    indicators = {
        "1": ("personal_income_total", "thousands USD", "Total personal income"),
        "2": ("population_bea", "persons", "Population (BEA estimate)"),
        "3": ("per_capita_income", "USD", "Per capita personal income"),
        "4": ("median_income", "USD", "Median household income"),
    }

    all_ok = True
    latest_year = None

    for line_code, (ind_name, unit, desc) in indicators.items():
        params = {
            "UserID": api_key,
            "method": "GetData",
            "datasetname": "Regional",
            "TableName": "CAINC1",
            "GeoFips": f"{STATE_FIPS}{COUNTY_FIPS}",
            "Year": "ALL",
            "LineCode": line_code,
            "ResultFormat": "json",
        }

        try:
            resp = SESSION.get(base_url, params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            results = data.get("BEAAPI", {}).get("Results", {})
            if "Error" in results or not results.get("Data"):
                log_fetch(source_name, f"FAIL LC{line_code}", f"No data for {desc}")
                all_ok = False
                continue

            # Find most recent year
            data_list = results.get("Data", [])
            years = [int(d.get("TimePeriod", 0)) for d in data_list if d.get("TimePeriod", "").isdigit()]
            
            if not years:
                all_ok = False
                continue

            if latest_year is None or max(years) > latest_year:
                latest_year = max(years)

            for item in data_list:
                if str(item.get("TimePeriod")) == str(latest_year):
                    val_str = item.get("DataValue", "").replace(",", "").strip()
                    try:
                        val = float(val_str)
                        upsert_indicator(
                            ind_name, f"{val:.0f}", unit, "Economy",
                            source_name, "https://www.bea.gov/data/income-saving/local-area-personal-income",
                            str(latest_year), f"{desc}, Volusia County, {latest_year}"
                        )
                    except (ValueError, TypeError):
                        continue

            log_fetch(source_name, "OK", f"LC{line_code}: {desc}")

        except requests.RequestException as e:
            log_fetch(source_name, "ERROR", f"LC{line_code}: {e}")
            all_ok = False
        except Exception as e:
            log_fetch(source_name, "ERROR", f"LC{line_code}: {e}")
            all_ok = False

    if latest_year:
        log_action("fetch_bea", f"year={latest_year}, all_indicators={all_ok}")
    
    return all_ok


# ═════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE DRIVER
# ═════════════════════════════════════════════════════════════════════════
def main() -> int:
    """Run the complete data refresh pipeline."""
    log.info("=" * 60)
    log.info("Project Volusia Data Pipeline v2.1")
    log.info("=" * 60)
    
    # Initialize database
    init_db()
    
    # Record start
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    start_time = datetime.now()
    
    # Run fetchers
    results = {
        "census_pep": fetch_census_pep(),
        "census_acs": fetch_census_acs(),
        "noaa": fetch_noaa(),
        "bls_laus": fetch_bls(),
        "bearegional": fetch_bea(),
    }
    
    # Calculate duration
    duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
    
    # Record manifest
    success_count = sum(1 for v in results.values() if v or v is None)  # None = skipped due to missing key
    conn = get_db()
    conn.execute("""
        INSERT INTO fetch_manifest (run_id, duration_ms, status, indicators_count)
        VALUES (?, ?, ?, ?)
    """, (run_id, duration_ms, "completed", success_count))
    conn.commit()
    
    # Summary
    log.info("=" * 60)
    log.info(f"Pipeline complete: {success_count}/{len(results)} fetchers succeeded")
    for name, ok in results.items():
        status = "✓" if ok else ("○" if ok is None else "✗")
        log.info(f"  {status} {name}")
    log.info(f"Duration: {duration_ms}ms")
    log.info("=" * 60)
    
    # Return exit code
    if all(v is True for v in results.values()):
        return 0
    elif any(v is False for v in results.values()):
        return 1
    return 0  # Partial success (some skipped)


if __name__ == "__main__":
    sys.exit(main())