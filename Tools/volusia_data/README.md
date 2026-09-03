# Project Volusia — Data Pipeline

Open-source data pipeline and web portal for Volusia County, Florida (FIPS 12127).

## Overview

Project Volusia fetches, stores, and serves public economic, demographic, climate, and infrastructure data for Volusia County from U.S. government sources:

- **Census PEP** — Population estimates (no API key required)
- **Census ACS** — American Community Survey demographic/economic tables
- **BLS LAUS** — Local Area Unemployment Statistics
- **BLS QCEW** — Quarterly Census of Employment and Wages
- **BEA Regional** — Local Area Personal Income
- **NOAA NCEI** — Daily weather summaries

## Architecture

```
refresh_v2.py          ← Unified pipeline entry point
    │
    ├── fetch_pep()    ← Census PEP CSV (no key)
    ├── fetch_census() ← Census ACS API (key) [optional]
    ├── fetch_bls()    ← BLS LAUS API + cached CSV fallback
    ├── fetch_qcew()   ← BLS QCEW ZIP download + filter
    ├── fetch_bea()    ← BEA Regional API (key)
    └── fetch_noaa()   ← NOAA NCEI API (no key)
    
portal_app.py          ← FastAPI web portal + JSON API
    │
    ├── GET /          ← HTML dashboard
    ├── GET /api/indicators  ← All indicators as JSON
    ├── GET /api/export/csv  ← CSV download
    ├── GET /api/export/json ← JSON download
    ├── GET /api/datasets     ← Dataset inventory
    ├── GET /api/health      ← Health check
    └── GET /api/status      ← Executive summary

volusia.db             ← SQLite database (14 indicators)
fetch_log.jsonl        ← Audit trail
data/                  ← Cached raw files
```

## Quick Start

### 1. Install dependencies
```bash
pip install fastapi uvicorn pandas requests
```

### 2. Run the data pipeline
```bash
python refresh_v2.py
```

### 3. Start the web portal
```bash
python portal_app.py
# Open http://localhost:8789
```

### 4. Check health
```bash
curl http://localhost:8789/api/health
```

## API Endpoints

| Endpoint | Description | Format |
|----------|-------------|--------|
| `/` | HTML dashboard with all indicators | HTML |
| `/api/indicators` | All indicators as JSON array | JSON |
| `/api/export/csv` | Download all indicators as CSV | CSV |
| `/api/export/json` | Download all indicators as JSON | JSON |
| `/api/datasets` | Dataset inventory | JSON |
| `/api/health` | Health check (db_exists, indicator_count) | JSON |
| `/api/status` | Executive summary (categories, SLA, freshness) | JSON |

## Configuration

API keys are read from environment variables with safe defaults:

| Variable | Description | Sign Up |
|----------|-------------|---------|
| `CENSUS_API_KEY` | Census ACS API key | https://api.census.gov/data/key_signup.html |
| `BLS_API_KEY` | BLS LAUS API key | https://data.bls.gov/registrationEngine/ |
| `BEA_API_KEY` | BEA Regional API key | https://apps.bea.gov/API/signup/index.cfm |
| `VOLUSIA_DB_PATH` | Override database path | — |
| `VOLUSIA_PORTAL_HOST` | Portal bind host (default: 127.0.0.1) | — |
| `VOLUSIA_PORTAL_PORT` | Portal bind port (default: 8789) | — |

## Current Indicators (14)

### Climate (3)
- avg_max_temp_2024, avg_min_temp_2024, total_precip_2024

### Demographics (3)
- total_population_pep_2022, total_population_pep_2023, total_population_pep_2024

### Economy (8)
- unemployment_rate_bls, establishments_qcew, employment_qcew, avg_weekly_wage_qcew, per_capita_income, personal_income_total, population_bea

## Refresh Cadence

| Source | Cadence | Next Refresh |
|--------|---------|--------------|
| Census PEP | Annual | 2025-07 |
| Census ACS | Annual | 2025-12 |
| BLS LAUS | Monthly | 2026-10 |
| BLS QCEW | Quarterly | 2025-Q4 |
| BEA Regional | Annual | 2025-04 |
| NOAA NCEI | Daily | Continuous |

## Project Structure

```
volusia_data/
├── __init__.py          ← Package init
├── config.py            ← Configuration (API keys, paths)
├── refresh_v2.py        ← Unified data pipeline
├── portal_app.py        ← FastAPI web portal
├── run_full_refresh.py  ← Entry point wrapper
├── volusia.db           ← SQLite database
├── fetch_log.jsonl      ← Audit trail
├── fetchers/
│   ├── __init__.py      ← Fetcher exports
│   ├── census.py        ← Census ACS fetcher
│   ├── bls.py           ← BLS LAUS fetcher
│   ├── bea.py           ← BEA Regional fetcher
│   ├── noaa.py          ← NOAA NCEI fetcher
│   ├── pep.py           ← Census PEP fetcher
│   └── bls_qcew.py      ← BLS QCEW fetcher
├── portal/
│   └── app.py           ← Legacy portal (unused)
└── data/                ← Cached raw files
    ├── CAINC1.zip       ← BEA CAINC1 (may be HTML if download fails)
    ├── qcew_2024_singlefile.zip ← BLS QCEW quarterly
    └── bea_volusia_cainc1_2022-2023.csv ← BEA cached CSV
```

## Known Issues

1. **BLS LAUS API** — Returns '-' for some values; pipeline skips non-numeric rows
2. **Census ACS** — Requires free API key for full data
3. **NOAA NCEI** — Uses daily-summaries dataset; some stations may have gaps
4. **BEA ZIP download** — BEA changed their download URL format; API is now the primary path
5. **QCEW** — Quarterly data has ~6-9 month lag; annual data is more current

## License

Open source. Data is from U.S. government public domain sources.

## Contact

- **Website:** https://zqmlabs.com
- **GitHub:** https://github.com/ZQM-Computing
- **Email:** info@zqmlabs.com

---

**Document owner:** ZQM Labs / Project Volusia  
**Last updated:** 2026-09-03
