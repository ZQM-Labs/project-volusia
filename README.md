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

- **26+ Indicators** — Demographics, economy, climate, tourism
- **112 Data Sources** — Government agencies, academic institutions
- **Automated Pipeline** — Fetches, validates, stores in SQLite
- **REST API** — FastAPI endpoints for live data
- **Quality Validation** — Automated source verification

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

| Endpoint | Description |
|----------|-------------|
| `/api/` | Root |
| `/api/health` | Health check + indicator count |
| `/api/indicators` | All indicators (filter: `?category=Economic`) |
| `/api/indicators/{name}` | Single indicator |
| `/api/indicators.csv` | Download all as CSV |
| `/api/datasets` | Latest datasets |
| `/api/refresh` | Trigger a pipeline refresh |

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
