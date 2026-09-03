"""
Project Volusia — Unified Data Pipeline
Version: 2.0 | Date: 2026-09-03
Fixes: NOAA params, BEA API, BLS parsing, portal path, imports
"""
import os
import sys
import json
import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

# ── paths ───────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "volusia.db"
LOG_PATH = ROOT / "fetch_log.jsonl"

# ── logging ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("volusia_pipeline")

# ── db helpers ──────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            content TEXT,
            fetched_at TEXT
        );
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            details TEXT,
            timestamp TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    return conn

def upsert_indicator(name, value, unit="", category="", source="", source_url="", vintage="", description=""):
    conn = get_db()
    ts = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT INTO indicators (name, value, unit, category, source, source_url, vintage, fetched_at, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            value=excluded.value, unit=excluded.unit, category=excluded.category,
            source=excluded.source, source_url=excluded.source_url, vintage=excluded.vintage,
            fetched_at=excluded.fetched_at, description=excluded.description
    """, (name, value, unit, category, source, source_url, vintage, ts, description))
    conn.commit()

def log_action(action, details=""):
    conn = get_db()
    conn.execute("INSERT INTO audit_log (action, details) VALUES (?, ?)", (action, details))
    conn.commit()

def log_fetch(source, status, details=""):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "status": status,
        "details": details,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

# ── fetcher: Census PEP (Population Estimates) — NO KEY NEEDED ──────────
def fetch_pep():
    url = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv"
    source_name = "Census PEP"
    log.info(f"Fetching {source_name}...")

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        lines = resp.text.strip().split("\n")
        header = lines[0].split(",")

        volusia_row = None
        for line in lines[1:]:
            fields = line.split(",")
            # CSV cols: SUMLEV(0), REGION(1), DIVISION(2), STATE(3), COUNTY(4), ...
            if len(fields) > 4 and fields[3].strip() == "12" and fields[4].strip() == "127":
                volusia_row = dict(zip(header, fields))
                break

        if not volusia_row:
            log_fetch(source_name, "FAIL", "Volusia County row not found")
            return False

        pop_2024 = volusia_row.get("POPESTIMATE2024", "N/A")
        pop_2023 = volusia_row.get("POPESTIMATE2023", "N/A")
        pop_2022 = volusia_row.get("POPESTIMATE2022", "N/A")

        upsert_indicator("total_population_pep_2024", pop_2024, "persons", "Demographics",
                        source_name, url, "2024", "Census PEP county population estimate, July 1 2024")
        upsert_indicator("total_population_pep_2023", pop_2023, "persons", "Demographics",
                        source_name, url, "2023", "Census PEP county population estimate, July 1 2023")
        upsert_indicator("total_population_pep_2022", pop_2022, "persons", "Demographics",
                        source_name, url, "2022", "Census PEP county population estimate, July 1 2022")

        log_fetch(source_name, "OK", f"pop_2024={pop_2024}")
        log_action("fetch_pep", f"pop_2024={pop_2024}")
        log.info(f"  OK: pop 2024={pop_2024}")
        return True

    except Exception as e:
        log_fetch(source_name, "ERROR", str(e))
        log.error(f"  ERROR: {e}")
        return False


# ── fetcher: NOAA NCEI — FIXED PARAMS ─────────────────────────────────
def fetch_noaa():
    station = "USW00012838"
    url = "https://www.ncei.noaa.gov/access/services/data/v1"
    source_name = "NOAA NCEI"
    log.info(f"Fetching {source_name}...")

    params = {
        "dataset": "daily-summaries",
        "stations": station,
        "dataTypes": "TMAX,TMIN,PRCP",
        "startDate": "2024-01-01",
        "endDate": "2024-12-31",
        "format": "json",
        "limit": 5000,
        "offset": 0,
    }

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            log_fetch(source_name, "FAIL", "Empty response")
            return False

        tmax_vals = [int(d["TMAX"]) for d in data if "TMAX" in d]
        tmin_vals = [int(d["TMIN"]) for d in data if "TMIN" in d]
        prcp_vals = [int(d["PRCP"]) for d in data if "PRCP" in d]

        avg_tmax = round(sum(tmax_vals) / len(tmax_vals), 1) if tmax_vals else "N/A"
        avg_tmin = round(sum(tmin_vals) / len(tmin_vals), 1) if tmin_vals else "N/A"
        total_prcp = sum(prcp_vals) if prcp_vals else "N/A"

        upsert_indicator("avg_max_temp_2024", avg_tmax, "tenths C", "Climate",
                        source_name, url, "2024", f"NOAA daily avg TMAX for Daytona Beach")
        upsert_indicator("avg_min_temp_2024", avg_tmin, "tenths C", "Climate",
                        source_name, url, "2024", f"NOAA daily avg TMIN for Daytona Beach")
        upsert_indicator("total_precip_2024", total_prcp, "tenths mm", "Climate",
                        source_name, url, "2024", f"NOAA total PRCP for Daytona Beach")

        log_fetch(source_name, "OK", f"days={len(data)}, avg_tmax={avg_tmax}")
        log_action("fetch_noaa", f"days={len(data)}, avg_tmax={avg_tmax}")
        log.info(f"  OK: {len(data)} daily records, avg TMAX={avg_tmax}")
        return True

    except Exception as e:
        log_fetch(source_name, "ERROR", str(e))
        log.error(f"  ERROR: {e}")
        return False


# ── fetcher: BLS LAUS — FIXED PARSING ──────────────────────────────────
def fetch_bls():
    api_key = os.environ.get("BLS_API_KEY", "114ae7be1cef4085b7a756f201690ec7")
    series_id = "LAUCN121270000000003"
    api_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    source_name = "BLS LAUS"
    log.info(f"Fetching {source_name}...")

    payload = {
        "seriesid": [series_id],
        "startyear": "2020",
        "endyear": str(datetime.now().year),
        "registrationkey": api_key,
    }

    try:
        resp = requests.post(api_url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "REQUEST_SUCCEEDED":
            log_fetch(source_name, "FAIL", f"API status: {data.get('status')}")
            return False

        series_list = data.get("Results", {}).get("series", [])
        if not series_list:
            log_fetch(source_name, "FAIL", "No series in response")
            return False

        rows = []
        for serie in series_list:
            for obs in serie.get("data", []):
                val_str = obs.get("value", "").strip()
                try:
                    val = float(val_str)
                except (ValueError, TypeError):
                    continue  # Skip non-numeric values like "-"
                rows.append({
                    "year": int(obs["year"]),
                    "period": obs["period"],
                    "period_name": obs["periodName"],
                    "value": val,
                })

        if not rows:
            log_fetch(source_name, "FAIL", "No valid numeric rows")
            return False

        # Get latest month
        latest = rows[0]
        rate = latest["value"]
        period = latest["period_name"]
        year = latest["year"]

        upsert_indicator("unemployment_rate_bls", f"{rate}", "percent", "Economy",
                        source_name, "https://www.bls.gov/lau/", f"{period} {year}",
                        f"BLS LAUS unemployment rate for Volusia County ({period} {year})")

        log_fetch(source_name, "OK", f"rate={rate}%, period={period} {year}")
        log_action("fetch_bls", f"rate={rate}%, period={period} {year}")
        log.info(f"  OK: unemployment rate={rate}% ({period} {year})")
        return True

    except Exception as e:
        log_fetch(source_name, "ERROR", str(e))
        log.error(f"  ERROR: {e}")
        return False


# ── fetcher: BEA CAINC1 — FIXED TO USE API ─────────────────────────────
def fetch_bea():
    api_key = os.environ.get("BEA_API_KEY", "49ED5E15-6093-4A4E-ABBC-83E7BC38B324")
    source_name = "BEA Regional"
    log.info(f"Fetching {source_name}...")

    base_url = "https://apps.bea.gov/api/data"
    indicators = {
        "1": ("personal_income_total", "thousands USD", "Total personal income (thousands)"),
        "2": ("population_bea", "persons", "Population"),
        "3": ("per_capita_income", "USD", "Per capita personal income"),
    }

    all_ok = True
    for line_code, (ind_name, unit, desc) in indicators.items():
        params = {
            "UserID": api_key,
            "method": "GetData",
            "datasetname": "Regional",
            "TableName": "CAINC1",
            "GeoFips": "12127",
            "Year": "ALL",
            "LineCode": line_code,
            "ResultFormat": "json",
        }

        try:
            resp = requests.get(base_url, params=params, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            results = data.get("BEAAPI", {}).get("Results", {})
            if not results or "Error" in results:
                log_fetch(source_name, f"FAIL LineCode={line_code}", "No results")
                all_ok = False
                continue

            data_list = results.get("Data", [])
            if not data_list:
                log_fetch(source_name, f"FAIL LineCode={line_code}", "Empty data list")
                all_ok = False
                continue

            latest_year = max(int(d.get("TimePeriod", 0)) for d in data_list if d.get("TimePeriod", "").isdigit())
            latest_items = [d for d in data_list if str(d.get("TimePeriod", "")) == str(latest_year)]

            for item in latest_items:
                val_str = item.get("DataValue", "").replace(",", "").strip()
                try:
                    val = float(val_str)
                except (ValueError, TypeError):
                    continue

                upsert_indicator(ind_name, f"{val}", unit, "Economy",
                                source_name, "https://www.bea.gov/data/income-saving/local-area-personal-income",
                                str(latest_year), f"{desc} for Volusia County, {latest_year}")

            log_fetch(source_name, f"OK LineCode={line_code}", f"year={latest_year}")
            log.info(f"  OK LineCode={line_code}: {desc}")

        except Exception as e:
            log_fetch(source_name, f"ERROR LineCode={line_code}", str(e))
            log.error(f"  ERROR LineCode={line_code}: {e}")
            all_ok = False

    return all_ok


# ── fetcher: BLS QCEW — CSV fallback ───────────────────────────────────
def fetch_qcew():
    source_name = "BLS QCEW"
    url = "https://data.bls.gov/cew/data/files/2024/csv/2024_annual_singlefile.zip"
    log.info(f"Fetching {source_name}...")

    import zipfile, io, csv
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            csv_name = next((n for n in z.namelist() if "annual" in n.lower() and n.endswith(".csv")), None)
            if not csv_name:
                csv_name = z.namelist()[0]

            with z.open(csv_name) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="latin-1"))
                volusia_rows = [r for r in reader if r.get("area_fips", "").strip() == "12127"]

        if not volusia_rows:
            log_fetch(source_name, "FAIL", "Volusia rows not found")
            return False

        row = volusia_rows[0]
        establishments = row.get("annual_avg_estabs", "N/A")
        employment = row.get("annual_avg_emplvl", "N/A")
        avg_weekly_wage = row.get("annual_avg_wkly_wage", "N/A")

        upsert_indicator("establishments_qcew", establishments, "establishments", "Economy",
                        source_name, url, "2024", "BLS QCEW annual avg establishments")
        upsert_indicator("employment_qcew", employment, "employees", "Economy",
                        source_name, url, "2024", "BLS QCEW annual avg employment")
        upsert_indicator("avg_weekly_wage_qcew", avg_weekly_wage, "USD", "Economy",
                        source_name, url, "2024", "BLS QCEW annual avg weekly wage")

        log_fetch(source_name, "OK", f"establishments={establishments}")
        log_action("fetch_qcew", f"establishments={establishments}")
        log.info(f"  OK: establishments={establishments}, employment={employment}")
        return True

    except Exception as e:
        log_fetch(source_name, "ERROR", str(e))
        log.error(f"  ERROR: {e}")
        return False


# ── main ────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("Project Volusia — Data Pipeline Refresh v2.0")
    log.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    log.info("=" * 60)

    init_db()
    log_action("refresh_start")

    results = {
        "Census PEP": fetch_pep(),
        "NOAA NCEI": fetch_noaa(),
        "BLS LAUS": fetch_bls(),
        "BEA Regional": fetch_bea(),
        "BLS QCEW": fetch_qcew(),
    }

    log.info("-" * 60)
    for name, ok in results.items():
        status = "OK" if ok else "FAIL"
        log.info(f"  {status}: {name}")

    log_action("refresh_complete", json.dumps(results))
    log.info("Done.")
    return results


if __name__ == "__main__":
    main()
