# Project Volusia

[![CI](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/ci.yml/badge.svg)](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/ci.yml)
[![Tests](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/tests.yml/badge.svg)](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/tests.yml)
[![Release](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/release.yml/badge.svg)](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/release.yml)

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Language](https://img.shields.io/badge/Language-Python%2C%20React%2C%20TypeScript-blue)](https://github.com/ZQM-Labs/zqm-volusia)
[![Docs](https://img.shields.io/badge/Docs-ReadTheDocs-brightgreen)](https://readthedocs.org/projects/volusia)

## About

Project Volusia is the open-source backbone of [volusia.zqmlabs.com](https://volusia.zqmlabs.com) — a data portal for Volusia County, Florida providing real-time access to economic indicators, tourism data, environmental metrics, housing statistics, public safety information, and government services.

Built by ZQM Labs as part of ZQM Computing's commitment to building sustainable open-source technologies that connect families, grow business, and encourage communities to explore our shared future.

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
| [zqm-volusia-web](https://github.com/ZQM-Labs/zqm-volusia-web) | React frontend — gamified interface, data explorer | TypeScript |
| [zqm-portal](https://github.com/ZQM-Computing/zqm-portal) | Portal site generator — static HTML for zqmlabs.com + volusia.zqmlabs.com | Python |
| [zqm-portal-web](https://github.com/ZQM-Computing/zqm-portal-web) | Static site builder for the Volusia portal | Python |
| [zqm-tools](https://github.com/ZQM-Labs/zqm-tools) | Public utilities: DRIP scripts, security tools, data tools | Python |
| [zqm-tokens](https://github.com/ZQM-Labs/zqm-tokens) | Public tokens: DRIP scripts, security utilities, renewable energy | Python |
| [zqm-whitewater](https://github.com/ZQM-Labs/zqm-whitewater) | PowerShell automation for Windows infrastructure | PowerShell |

## Data Categories

The portal covers 10 data categories, each with live indicators:

1. **Economic** — Personal income, employment, GDP, cost of living, housing affordability
2. **Tourism** — Visitor spending, hotel occupancy, attractions, seasonal trends
3. **Environment** — Air/water quality, climate data, conservation metrics
4. **Housing** — Median home value, rent trends, vacancy rates, mortgage rates
5. **Safety** — Crime statistics, emergency response, fire incidents
6. **Government** — Spending, budgets, permits, elections, public services
7. **Demographics** — Population, migration, age distribution, education levels
8. **Health** — Healthcare access, insurance, wellness, disease prevalence
9. **Education** — Schools, test scores, graduation rates, student enrollment
10. **Gamification** — Interactive missions, leaderboards, achievements, tiers

## Quick Start

```bash
# Clone the project
git clone https://github.com/ZQM-Labs/zqm-volusia.git
cd zqm-volusia

# Install dependencies and run the backend
cd backend && pip install -r requirements.txt && python main.py

# In another terminal, build and serve the frontend
cd ../volusia-portal && npm install && npm run build
```

## Deployment

The full portal deploys via [ZQM's automated pipeline](https://github.com/ZQM-Computing/zqm-portal/blob/main/scripts/deploy.py):

1. Backend refresh — `POST http://127.0.0.1:8000/refresh`
2. Static generation — `project-volusia-web/generate.py`
3. React build — `npm run build` in `volusia-portal/src/`
4. Sync to nginx and restart

## Subdomain

Project Volusia is served at **[volusia.zqmlabs.com](https://volusia.zqmlabs.com)**.

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

**ZQM Labs** — Research, Security, and Infrastructure  
**ZQM Computing** — Open-source technology connecting families, growing business, and exploring communities  
[volia.zqmlabs.com](https://volusia.zqmlabs.com) · [zqmlabs.com](https://zqmlabs.com) · [api.zqmlabs.com](https://api.zqmlabs.com)
