# Project Volusia — Backend

[![CI](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/ci.yml/badge.svg)](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/ci.yml)
[![Tests](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/tests.yml/badge.svg)](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/tests.yml)
[![Release](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/release.yml/badge.svg)](https://github.com/ZQM-Labs/zqm-volusia/actions/workflows/release.yml)

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Language](https://img.shields.io/badge/Language-Python%2C%20FastAPI%2C%20SQLAlchemy-blue)](https://github.com/ZQM-Labs/zqm-volusia)

## About

Project Volusia is the backend data pipeline serving the Volusia County open data portal at [volusia.zqmlabs.com](https://volusia.zqmlabs.com). It aggregates 474 indicators across 10 categories from authoritative government sources including US Census Bureau, BLS, BEA, NOAA, CDC, and county open data portals.

**The React frontend is in [zqm-volusia-web](https://github.com/ZQM-Labs/zqm-volusia-web).**

## Architecture

```
zqmlabs.com ──┐
              ├── zqm-portal (ZQM company portal, advertising services)
              │
volusia.zqmlabs.com ──┤
                      │
              ├── zqm-volusia-web (React + Vite + TypeScript frontend)
              │       │
              │       └── /data/* → zqm-volusia backend
              │
              └── zqm-volusia (FastAPI backend, data pipeline)
                      │
                      ├── PostgreSQL (volusia.db — 27 indicators live)
                      ├── Redis (caching)
                      └── Celery (background tasks)
```

## Key Features

- **474 Indicators** — Across 10 categories: economic, demographic, environmental, housing, safety, government, health, education, infrastructure, and social
- **18+ Map Layers** — Interactive geographic data via Leaflet
- **Real-Time Data** — Direct from government APIs
- **Gamification** — 30 missions, 5 tiers, 14 pathways (A-N)
- **Open Source** — MIT License, community contributions welcome

## Quick Links

| Resource | URL |
|---|---|
| **Live Portal** | [volusia.zqmlabs.com](https://volusia.zqmlabs.com) |
| **Frontend Repo** | [ZQM-Labs/zqm-volusia-web](https://github.com/ZQM-Labs/zqm-volusia-web) |
| **Backend API** | [https://volusia.zqmlabs.com/api](https://volusia.zqmlabs.com/api) |
| **Data Indicators** | [https://volusia.zqmlabs.com/data/indicators.json](https://volusia.zqmlabs.com/data/indicators.json) |
| **Connection Guide** | [CONNECTION.md](CONNECTION.md) |
| **Deploy Pipeline** | [deploy.py](deploy.py) |

## Categories

Economic | Demographic | Environmental | Housing | Safety | Government | Health | Education | Infrastructure | Social

## Stack

| Layer | Tech |
|-------|------|
| Framework | FastAPI, SQLAlchemy, Celery |
| Database | PostgreSQL, Redis |
| Frontend | React 18 + Vite + TypeScript (zqm-volusia-web) |
| Charts | Nivo (D3-based) |
| Maps | Leaflet + react-leaflet |
| Styling | Tailwind CSS |
| Cache | Redis |
| Queue | Celery |

## Deployment

### Backend Refresh
```bash
python3 deploy.py --skip-generate --skip-restart
```

### Full Pipeline
```bash
python3 deploy.py  # refresh → generate → build → sync → restart → verify
```

### Manual Restart
```bash
nssm restart VolusiaWeb  # Requires admin rights
```

## Development

1. Clone this repo: `git clone https://github.com/ZQM-Labs/zqm-volusia.git`
2. Copy `.env.example` to `.env` and configure
3. Install dependencies: `pip install -r requirements.txt`
4. Run the backend: `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Frontend runs separately in `zqm-volusia-web`

## Contribution Guide

We welcome contributions! Here's how to get started:

1. **Fork** this repo: `gh repo fork ZQM-Labs/zqm-volusia`
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make changes** and commit them
4. **Open a PR** with a clear description
5. **Wait for review** — maintainers respond within a few days

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

**Project Volusia** — Open data for Volusia County, Florida  
**Backend** · **[volusia.zqmlabs.com](https://volusia.zqmlabs.com)** · **[GitHub](https://github.com/ZQM-Labs/zqm-volusia)**
