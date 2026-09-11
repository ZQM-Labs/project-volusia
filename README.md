# Project Volusia — Backend Data Pipeline

> FastAPI backend serving 50+ live indicators, gamification engine, and automated data refresh for the Project Volusia public data portal.

---

## 🌐 Domains Served

| Domain | Repo | Branch | Purpose |
|--------|------|--------|---------|
| **volusia.zqmlabs.com** | `ZQM-Labs/volusia-zqmlabs` | `main` | Public data portal |
| **api.zqmlabs.com** | `ZQM-Labs/volusia-zqmlabs` | `main` | Backend API endpoint |
| **zqmlabs.com** | `ZQM-Computing/zqmlabs-website` | `master` | Frontend (separate repo) |

**Domain-to-repo naming rule**: `volusia-zqmlabs` serves `volusia.zqmlabs.com`.
The frontend `zqmlabs-website` serves `zqmlabs.com`. Both repos communicate
via the shared backend API on port 8000.

---

## Overview

Project Volusia is a comprehensive open data portal for Volusia County, Florida. The **backend** provides the data layer — aggregating **50+ indicators** across **15+ categories** from authoritative sources including US Census Bureau, BLS, BEA, NOAA, C2ER, and more.

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  zqmlabs.com       │────▶│  zqmlabs-website     │────▶│  volusia-zqmlabs    │
│  (React Frontend)│     │  (React + FastAPI) │     │  (FastAPI Backend) │
│  Repo:           │     │  Repo:             │     │  Repo:             │
│  ZQM-Computing/  │     │  ZQM-Computing/    │     │  ZQM-Labs/         │
│  zqmlabs-website │     │  zqmlabs-website   │     │  volusia-zqmlabs   │
│  branch: master  │     │  branch: master    │     │  branch: main      │
└─────────────────┘     └──────────────────┘     └──────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
  nginx :80              nginx :80                 volusia.db
  Cloudflare              React SPA              474 records
                          + FastAPI              gamification engine
                          + /data/*              50+ indicators
                          + /missions
```

### Data Flow

```
Government APIs ──▶ volusia-zqmlabs ──▶ zqmlabs-website ──▶ User
  (Census, BLS,      (FastAPI :8000)     (React SPA)         (Browser)
   NOAA, C2ER)          │                   │
                         │                   │
                         ▼                   ▼
                    volusia.db            nginx :80
                    (SQLite)              Cloudflare
                    474 records           zqmlabs.com
```

### Repo Domains at a Glance

| Repo Name | Serves | Branch | Domain |
|-----------|--------|--------|--------|
| `zqmlabs-website` | zqmlabs.com | `master` | Frontend + reverse proxy |
| `volusia-zqmlabs` | volusia.zqmlabs.com | `main` | Backend data pipeline |

---

## Quick Links

| Resource | URL | Repo |
|----------|-----|------|
| **Live Portal** | https://zqmlabs.com | `ZQM-Computing/zqmlabs-website` |
| **Backend API** | https://api.zqmlabs.com | `ZQM-Labs/volusia-zqmlabs` |
| **Frontend Repo** | https://github.com/ZQM-Computing/zqmlabs-website | `zqmlabs-website` |
| **Backend Repo** | https://github.com/ZQM-Labs/volusia-zqmlabs | `volusia-zqmlabs` |
| **Live Data** | https://zqmlabs.com/data | `ZQM-Computing/zqmlabs-website` |
| **API Docs** | https://zqmlabs.com/api/docs | `ZQM-Labs/volusia-zqmlabs` |
| **Connection Guide** | [DEPLOY.md](DEPLOY.md) | — |

---

## Key Features

- **50+ Live Indicators** — Economic, demographics, climate, tourism, infrastructure, safety, and more
- **Gamification Engine** — 30 missions, 5 tiers, 14 pathways (A–S)
- **Automated Refresh** — Scheduled data pulls from government APIs
- **FastAPI Backend** — High-performance async Python API
- **SQLite Database** — Persistent storage with 474 indicator records
- **Open Source** — MIT License, community contributions welcome

---

## Directory Structure

```
volusia-zqmlabs/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── gamification.py      # Gamification engine
│   ├── gamification/        # Gamification module
│   │   ├── routes.py        # API routes
│   │   └── scoring.py       # Mission scoring logic
│   ├── data/                # Data processing
│   ├── routers/             # API routers
│   ├── services/            # Business logic
│   ├── models/              # Database models
│   ├── utils/               # Utility functions
│   └── auth/                # Authentication
├── data/                    # Static data files
├── scripts/                 # Deployment and utility scripts
├── docs/                    # Documentation
├── volusia.db               # SQLite database (474 records)
├── pyproject.toml           # Python project config
├── Dockerfile               # Backend Docker container
├── deploy.py                # Deployment pipeline
└── README.md                # This file
```

---

## Development

### Backend Setup
```bash
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Refresh Data
```bash
POST http://127.0.0.1:8000/refresh?_secret=<token>
```

### Deploy
```bash
python scripts/deploy.py
```

---

## License

MIT — see [LICENSE](LICENSE)

