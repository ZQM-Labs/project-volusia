# Project Volusia

[![CI](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/ci.yml/badge.svg)](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/ci.yml)
[![Tests](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/tests.yml/badge.svg)](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/tests.yml)
[![Release](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/release.yml/badge.svg)](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/release.yml)

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Language](https://img.shields.io/badge/Language-Python%2C%20React%2C%20TypeScript-blue)](https://github.com/ZQM-Labs/zqm-volusia)

## About

Project Volusia is the open-source backbone of [volusia.zqmlabs.com](https://volusia.zqmlabs.com) — a data portal for Volusia County, Florida providing real-time access to economic indicators, tourism data, environmental metrics, housing statistics, public safety information, and government services.

Built by ZQM Labs as part of the ZQM-MESH network connecting communities, families, and businesses through open-source technology.

## Overview

Project Volusia provides:

- **FastAPI Backend** — REST API serving 474+ indicators across 10 categories
- **React Frontend** — Gamified data exploration interface
- **Static Generation** — Pre-built category pages for SEO and performance
- **Live Data Pipeline** — Automated data refresh from public sources

## Repositories

| Repo | Description | Language |
|---|---|---|
| [zqm-volusia](https://github.com/ZQM-Labs/zqm-volusia) | Project Volusia backend — FastAPI, data pipeline, 474 indicators | Python |
| [zqm-portal-web](https://github.com/ZQM-Computing/zqm-portal-web) | Static site generator for the Volusia portal | Python |
| [zqm-portal](https://github.com/ZQM-Computing/zqm-portal) | Portal site generator — static HTML for zqmlabs.com + volusia.zqmlabs.com | Python |
| [zqm-tools](https://github.com/ZQM-Labs/zqm-tools) | Public utilities: scripts, tools, helpers | Python |
| [zqm-nest](https://github.com/ZQM-Labs/zqm-nest) | Nest infrastructure and node management | Python |

## Data Categories

The portal covers 10 data categories:

1. **Economic** — Personal income, employment, GDP, cost of living
2. **Tourism** — Visitor spending, hotel occupancy, attractions
3. **Environment** — Air/water quality, climate data, conservation
4. **Housing** — Median home value, rent trends, vacancy rates
5. **Safety** — Crime statistics, emergency response, fire incidents
6. **Government** — Spending, budgets, permits, elections
7. **Demographics** — Population, migration, education levels
8. **Health** — Healthcare access, insurance, wellness
9. **Education** — Schools, test scores, graduation rates
10. **Gamification** — Interactive missions, leaderboards, achievements

## Quick Start

```bash
# Clone the project
git clone https://github.com/ZQM-Labs/zqm-volusia.git
cd zqm-volusia

# Install dependencies and run the backend
cd backend && pip install -r requirements.txt && python main.py

# In another terminal, build and serve the frontend
cd ../zqm-portal-web && npm install && npm run build
```

## Deployment

The full portal deploys via ZQM's automated pipeline:

1. Backend refresh — `POST http://127.0.0.1:8000/refresh`
2. Static generation — `zqm-portal-web/generate.py`
3. React build — `npm run build` in `volusia-portal/src/`
4. Sync to nginx and restart

See [zqm-portal](https://github.com/ZQM-Computing/zqm-portal) for the full deploy script.

## Subdomain

Project Volusia is served at **[volusia.zqmlabs.com](https://volusia.zqmlabs.com)**.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

**ZQM Labs** — Research, Security, and Infrastructure  
**ZQM-MESH** — Connecting communities through open-source technology  
[volusia.zqmlabs.com](https://volusia.zqmlabs.com) · [zqmlabs.com](https://zqmlabs.com) · [api.zqmlabs.com](https://api.zqmlabs.com)
