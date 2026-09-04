# Project Volusia — Open Data Portal & Intelligence Platform

<p align="left">
  <img src="https://github.com/ZQM-Labs/project-volusia/actions/workflows/ci.yml/badge.svg" alt="CI" />
  <img src="https://github.com/ZQM-Labs/project-volusia/actions/workflows/tests.yml/badge.svg" alt="Tests" />
  <img src="https://github.com/ZQM-Labs/project-volusia/actions/workflows/volusia-pipeline.yml/badge.svg" alt="Data Pipeline" />
</p>

**Data-driven commerce, open-source intelligence, and community resilience for Volusia County, Florida.**

Project Volusia is an open-source platform that aggregates public economic, demographic, climate, and employment data for Volusia County, FL (FIPS 12127) and serves it through a web portal, JSON API, and contribution system.

---

## Quick Start

```bash
# Clone
git clone https://github.com/ZQM-Labs/project-volusia.git
cd project-volusia

# Set up environment
cp Tools/.env.example Tools/.env
# Edit Tools/.env and add your API keys (see below)

# Run data pipeline
python Tools/volusia_data/refresh_v2.py

# Start portal
python Tools/volusia_data/portal_app.py
# Open http://127.0.0.1:8789

# Start contribution API (optional, separate terminal)
python Tools/volusia_data/contribution_api.py
# API docs at http://127.0.0.1:8790/docs
```

---

## API Keys (Free Registration)

Three sources require free API keys. Without them, the pipeline still works for the no-key sources (Census PEP, NOAA, QCEW).

| Source | Register At | Env Var |
|--------|-------------|---------|
| Census ACS | https://api.census.gov/data/key_signup.html | `CENSUS_API_KEY` |
| BLS LAUS | https://data.bls.gov/registrationEngine/ | `BLS_API_KEY` |
| BEA Regional | https://apps.bea.gov/API/signup/index.cfm | `BEA_API_KEY` |

Add keys to `Tools/.env` (see `Tools/.env.example`).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Sources (6)                         │
│  Census PEP │ Census ACS │ NOAA NCEI │ BLS LAUS │ BLS QCEW │ BEA │
└──────────────────────────────┬──────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   refresh_v2.py     │
                    │   (Unified Pipeline) │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   volusia.db        │
                    │   (SQLite, 10 rows) │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼──────┐ ┌──────▼───────┐ ┌──────▼──────────┐
    │  Portal (:8789) │ │ API (:8790)  │ │  Contribution   │
    │  HTML + JSON    │ │ Submissions  │ │  Form (:8791)   │
    │  + Chart PNGs   │ │ + Status     │ │  + Status       │
    └────────────────┘ └──────────────┘ └─────────────────┘
```

---

## Features

### Data Pipeline
- **6 fetchers**: Census PEP, Census ACS, NOAA NCEI, BLS LAUS, BLS QCEW, BEA Regional
- **Unified pipeline**: `refresh_v2.py` runs all sources, writes to SQLite
- **Scheduled refresh**: Windows Task Scheduler setup (`Tools/setup_scheduled_tasks.bat`)
- **Audit logging**: `fetch_log.jsonl` records every fetch with timestamp and status
- **Standalone CLIs**: Each fetcher can run independently with `--help`, `--output csv|json`, `--save`

### Web Portal (FastAPI, port 8789)
- **HTML dashboard**: Indicator cards with source citations and coherence groups
- **JSON API**: `/api/indicators`, `/api/coherence`, `/api/status`, `/api/health`
- **Data export**: `/api/export/csv`, `/api/export/json`
- **Chart generation**: 3 matplotlib endpoints (population trend, employment overview, climate summary)
- **SLA metadata**: Refresh cadence and uptime targets in `/api/status`
- **Contribution form**: Mounted at `/contribute` (bilingual EN/ES)

### Contribution System
- **Lightweight API** (port 8790): Anonymous-first, 9 contribution types, idempotency keys
- **Canonical API** (port 8899): SQLAlchemy + auth + rate tiers + pagination
- **Web form** (port 8791): Pathway F (community knowledge) + Pathway I (ideas), status lookup
- **Routing**: Contributions route to CGB members by type with fallback reviewers

### Data Processing Tools
- `clean.py`: Standardize columns, detect outliers (z-score), handle missing values
- `geocode.py`: Census Geocoder + OpenStreetMap Nominatim
- `aggregate.py`: Tract/zip/city to county with population-weighted means

### Visualization Tools
- `map.py`: Choropleth map generator (Leaflet HTML, no dependencies)
- `render_report.py`: Markdown template → HTML report renderer

### Monitoring
- `health_check.py`: Data freshness + API connectivity monitoring
- Returns non-zero exit code if data is stale (for cron alerting)

---

## API Endpoints

### Portal (port 8789)

| Endpoint | Type | Description |
|----------|------|-------------|
| `/` | HTML | Dashboard with indicator cards |
| `/api/indicators` | JSON | All indicators with coherence groups |
| `/api/coherence` | JSON | Source disagreement groups |
| `/api/export/csv` | CSV | Download all indicators |
| `/api/export/json` | JSON | Download with metadata |
| `/api/health` | JSON | Health check |
| `/api/status` | JSON | Full status with SLA + endpoints |
| `/api/chart/population_trend.png` | PNG | Census PEP line chart |
| `/api/chart/employment_overview.png` | PNG | QCEW bar chart |
| `/api/chart/climate_summary.png` | PNG | NOAA bar chart |
| `/contribute` | HTML | Contribution web form |

### Contribution API (port 8790)

| Endpoint | Type | Description |
|----------|------|-------------|
| `POST /api/v1/contributions` | JSON | Submit contribution |
| `GET /api/v1/contributions/{id}` | JSON | Check status |
| `GET /api/v1/contributions` | JSON | List submissions |
| `PATCH /api/v1/contributions/{id}` | JSON | Update status (CGB triage) |

---

## Project Structure

```
Project-Volusia/
├── Tools/
│   ├── volusia_data/
│   │   ├── refresh_v2.py          # Unified data pipeline
│   │   ├── portal_app.py          # FastAPI portal (port 8789)
│   │   ├── contribution_api.py    # Contribution API (port 8790)
│   │   ├── portal_contribute.py   # Web form frontend (port 8791)
│   │   ├── health_check.py        # Monitoring script
│   │   ├── config.py              # Centralized configuration
│   │   ├── fetchers/              # Standalone fetcher CLIs
│   │   │   ├── fetch_census_pep.py
│   │   │   ├── fetch_noaa.py
│   │   │   ├── fetch_qcew.py
│   │   │   ├── fetch_bls_laus.py
│   │   │   └── fetch_bea.py
│   │   ├── processing/            # Data processing tools
│   │   │   ├── clean.py
│   │   │   ├── geocode.py
│   │   │   └── aggregate.py
│   │   ├── viz/                   # Visualization tools
│   │   │   ├── map.py
│   │   │   └── render_report.py
│   │   └── portal/
│   │       └── app.py             # Deprecated (redirects to portal_app.py)
│   ├── contribution-api/          # Canonical API (SQLAlchemy, port 8899)
│   ├── collab/                    # Multi-writer collaboration tools
│   └── setup_scheduled_tasks.bat  # Windows Task Scheduler setup
├── tests/
│   ├── test_portal.py             # 7 portal endpoint tests
│   ├── test_contribution.py       # 18 contribution API tests
│   ├── test_contribute.py         # Contribution web form tests
│   └── test_fetchers.py           # 5 fetcher CLI tests
├── .github/workflows/             # 6 CI/CD workflows
├── docs/                          # Architecture decision records
├── CONTRIBUTION/                  # Contribution pathway templates (8)
├── Map/                           # Map catalog
├── Report/                        # Report templates
├── Data/                          # Data catalog + processed/published/raw
├── MISSION_STATEMENT.md
├── PROJECT_VOLUSIA_GOV.md
├── GUIDING_PRINCIPLES_VOLUSIA_COUNTY.md
├── METHODOLOGY.md
├── Q4_2026_EXECUTION_PLAN.md
├── STRATEGIC_FOCUS_Q4_2026_2027.md
├── PRIORITY_TRADEOFFS.md
├── STAKEHOLDER_INTERVIEW_GUIDE.md
├── DATA_ASSET_AUDIT_VOLUSIA.md
├── PUBLIC_DATA_SOURCE_RECON.md
├── BUILD_REPORT.md
├── Q4_2026_DELIVERY_STATUS.md
├── CONTRIBUTING.md
├── SECURITY.md
└── README.md                      # This file
```

---

## Current Data (10 Indicators)

| Indicator | Value | Source | Vintage |
|-----------|-------|--------|---------|
| Population (2024) | 601,107 | Census PEP | 2024 |
| Population (2023) | 591,936 | Census PEP | 2023 |
| Population (2022) | 580,529 | Census PEP | 2022 |
| Unemployment Rate | 5.3% | BLS LAUS | July 2026 |
| Employment | 189,265 | BLS QCEW | 2024 |
| Establishments | 16,756 | BLS QCEW | 2024 |
| Avg Weekly Wage | $1,041 | BLS QCEW | 2024 |
| Avg Max Temp | 28.1°C | NOAA NCEI | 2024 |
| Avg Min Temp | 19.1°C | NOAA NCEI | 2024 |
| Total Precipitation | 1,028 mm | NOAA NCEI | 2024 |

**Missing (need API keys):** Census ACS population, BEA per capita income, BEA total income, BEA population

---

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

- **Data sources**: Add new fetchers for public data sources
- **Tools**: Build data processing, visualization, or analysis tools
- **Documentation**: Improve docs, methodology, or data audit
- **Bug reports**: File issues with reproduction steps
- **Code**: Submit PRs with tests

### Multi-Writer Protocol

This repo uses a claim-before-edit protocol for concurrent writers. See [COLLABORATION_CONVENTIONS.md](COLLABORATION_CONVENTIONS.md).

### Contribution Pathways

Community members can contribute without code. See the 8 pathway templates in `CONTRIBUTION/templates/`:

- Data source submissions
- Analysis submissions
- Tool submissions
- Map submissions
- Report submissions
- Community input
- Social media input
- Direct contributions

---

## Governance

- **Executive Sponsor**: Alex Zelenski (zqmcomputing@gmail.com)
- **Governance Doc**: [PROJECT_VOLUSIA_GOV.md](PROJECT_VOLUSIA_GOV.md)
- **Decision Authority**: Tier 1-4 framework (strategic → technical → data → comms)
- **Meeting Cadence**: Weekly (30 min), Monthly (60 min), Quarterly (90 min)
- **Next Review**: December 2, 2026

---

## Charter & Strategy

- [MISSION_STATEMENT.md](MISSION_STATEMENT.md)
- [STRATEGIC_FOCUS_Q4_2026_2027.md](STRATEGIC_FOCUS_Q4_2026_2027.md)
- [Q4_2026_EXECUTION_PLAN.md](Q4_2026_EXECUTION_PLAN.md)
- [PRIORITY_TRADEOFFS.md](PRIORITY_TRADEOFFS.md)
- [GUIDING_PRINCIPLES_VOLUSIA_COUNTY.md](GUIDING_PRINCIPLES_VOLUSIA_COUNTY.md)
- [OPEN_INTELLIGENCE_DATA_DRIVEN_CHARTER.md](OPEN_INTELLIGENCE_DATA_DRIVEN_CHARTER.md)
- [METHODOLOGY.md](METHODOLOGY.md)

---

## Security

- [SECURITY.md](SECURITY.md) — Vulnerability reporting policy
- API keys are read from environment variables only (never hardcoded)
- `.env` file is gitignored
- Database is not tracked in git

---

## License

MIT License. See [LICENSE](LICENSE) (to be added).

---

## Links

- **ZQM Labs**: https://github.com/ZQM-Labs
- **ZQM Computing**: https://github.com/ZQM-Computing
- **ZQM Labs Pages**: https://zqm-labs.github.io/ZQM-Labs/
