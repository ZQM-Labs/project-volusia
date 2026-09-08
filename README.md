# Project Volusia — Backend & Data Pipeline

> Open-source intelligence and data-driven decision-making for Volusia County, Florida.

---

## Quick Links

| Resource | URL |
|----------|-----|
| **Live Portal** | https://volusia.zqmlabs.com |
| **Frontend Repo** | https://github.com/ZQM-Computing/volusia-portal |
| **API Endpoint** | https://volusia.zqmlabs.com/api |
| **Connection Guide** | [CONNECTION.md](CONNECTION.md) |

---

## Overview

Project Volusia is a comprehensive open data portal for Volusia County, Florida. This repository contains the backend data pipeline and API server that powers the public portal.

### Key Features

- **474 Indicators** — Demographics, economy, health, education, environment, and more
- **112 Data Sources** — Government agencies, academic institutions, and reputable organizations
- **39 Real-Time Sensors** — Traffic cameras, weather stations, air quality monitors, water sensors, webcams
- **15 Categories** — Comprehensive coverage of county data
- **Automated Pipeline** — Fetches, validates, stores in SQLite
- **REST API** — FastAPI endpoints for live data
- **Community Contributions** — Humans and AI agents can submit data and research
- **Quality Validation** — Automated source verification and citation scoring
- **Paginated API** — Efficient data retrieval with limit/offset pagination
- **Rate Limiting** — Protection against abuse (10 req/60s per client)
- **Correlation Analysis** — Pearson cross-indicator correlation
- **Configurable CORS** — Secure cross-origin resource sharing

---

## Data Sources

| Source | Data | Status |
|--------|------|--------|
| US Census PEP | Population estimates | ✅ Live |
| US Census ACS | Economic/demographic profiles | ✅ Live |
| BLS LAUS | Unemployment rates | ✅ Live |
| BLS QCEW | Employment/wages | ✅ Live |
| BEA Regional | Personal income | ✅ Live |
| NOAA NCEI | Weather data | ✅ Live |
| C2ER | Cost of living index | ⚠️ Cached |
| Volusia CVB | Hotel/occupancy data | ✅ Live |

---

## Quick Start

### Prerequisites

- Python 3.11+
- SQLite 3

### Installation

```bash
# Clone the repository
git clone https://github.com/ZQM-Labs/project-volusia.git
cd project-volusia

# Install dependencies
pip install fastapi uvicorn matplotlib requests

# Run the portal
cd Tools/volusia_data
python portal_app.py
```

### Access

- **Portal**: http://localhost:8789
- **API**: http://localhost:8790

---

## Data Refresh

```bash
cd Tools/volusia_data
python refresh_v2.py
```

---

## API Endpoints

### Portal API (port 8789)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check with indicator count |
| `/api/status` | GET | System status with SLA tracking |
| `/api/indicators` | GET | Paginated indicators (limit/offset) |
| `/api/citations` | GET | Citation quality scores |
| `/api/search` | GET | Full-text search |
| `/api/compare` | GET | Compare two indicators |
| `/api/trend` | GET | Trend data by vintage |
| `/api/correlation` | GET | Pearson correlation analysis |
| `/api/export/full` | GET | Full data export (JSON/CSV) |
| `/api/export/csv` | GET | CSV export |
| `/api/export/json` | GET | JSON export |
| `/api/datasets` | GET | Dataset history |
| `/api/executive-summary` | GET | Key metrics snapshot |
| `/api/coherence` | GET | Cross-source coherence groups |
| `/api/chart/*.png` | GET | Chart images (cached 1hr) |

**Pagination:** `/api/indicators?limit=50&offset=0` — Returns `count`, `total`, `has_more`, `limit`, `offset`.

**Full endpoint reference:** [docs/api/endpoints.md](docs/api/endpoints.md)

### Contribution API (port 8790)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | Health check with DB status |
| `/api/v1/contributions` | POST | Submit contribution (rate limited) |
| `/api/v1/contributions` | GET | List contributions (paginated) |
| `/api/v1/contributions/{id}` | GET | Get contribution status |
| `/api/v1/contributions/{id}` | PATCH | Update contribution status |

**Rate Limiting:** 10 requests per 60 seconds per client. Configurable via `VOLUSIA_RATE_LIMIT` and `VOLUSIA_RATE_WINDOW` env vars. Returns `429` with `Retry-After` header when exceeded.

---

## Frontend Portal

The public-facing frontend is maintained in a separate repository:

**Repository**: https://github.com/ZQM-Computing/volusia-portal

**Tech Stack**: React 18 + Vite + TypeScript + Tailwind CSS + Nivo charts + Leaflet maps

**Deployment**: GitHub Pages → https://volusia.zqmlabs.com

---

## Connection to Frontend

See [CONNECTION.md](CONNECTION.md) for detailed documentation on how this backend connects to the ZQM-Computing frontend.

---

## License

MIT © 2026 ZQM Labs / ZQM Computing
