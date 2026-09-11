# Project Volusia — Backend Data Pipeline

> FastAPI backend serving 50+ live indicators, gamification engine, and automated data refresh for the Project Volusia public data portal.

---

## Overview

Project Volusia is a comprehensive open data portal for Volusia County, Florida. The **backend** provides the data layer — aggregating **50+ indicators** across **15+ categories** from authoritative sources including US Census Bureau, BLS, BEA, NOAA, C2ER, and more.

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  zqm-portal      │────▶│  volusia-zqmlabs     │────▶│  Data Sources   │
│  (React Frontend)│     │  (FastAPI Backend)│     │  (Census, BLS)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                       │
        ▼                       ▼
  zqmlabs.com           volusia.db (SQLite)
  nginx reverse proxy   474 indicator cache
                        gamification engine
```

---

## Quick Links

| Resource | URL |
|----------|-----|
| **Live Portal** | https://zqmlabs.com |
| **Backend API** | https://zqmlabs.com/api |
| **Frontend Repo** | https://github.com/ZQM-Computing/zqm-portal |
| **Backend Repo** | https://github.com/ZQM-Labs/volusia-zqmlabs |
| **API Docs** | https://zqmlabs.com/api/docs |
| **Connection Guide** | [DEPLOY.md](DEPLOY.md) |

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
│   ├── gamification/
│   │   ├── routes.py        # Gamification API routes
│   │   └── scoring.py       # Mission scoring logic
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile.backend   # Backend Docker container
├── scripts/
│   ├── deploy.py            # Deployment pipeline
│   ├── refresh_v2.py        # Data refresh orchestrator
│   ├── scraper.py           # Web scraping utilities
│   ├── kb_bridge.py         # Knowledge base bridge
│   └── ...                  # 20+ utility scripts
├── tests/
│   ├── test_main.py         # Backend tests
│   └── conftest.py          # Test fixtures
├── data/
│   ├── volusia.db           # SQLite database (474 indicators)
│   └── cache/               # Cached API responses
├── Tools/
│   └── verify_data.py       # Data verification tool
├── Dockerfile               # Main Dockerfile
├── docker-compose.yml       # Docker Compose orchestration
├── Makefile                 # Build targets
└── requirements.txt         # Root dependencies
```

---

## Development

### Prerequisites

- Python 3.11+
- Docker + Docker Compose
- Node.js 18+ (for frontend only)

### Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest tests/

# With Docker
docker-compose up backend
```

### Data Refresh

```bash
# Refresh all data
python scripts/refresh_v2.py

# Refresh specific category
python scripts/refresh_v2.py --category Economic
```

### Gamification

```bash
# Check mission progress
python backend/gamification.py --status

# Award mission points
python backend/gamification.py --mission mission-name
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/latest` | GET | Latest indicator data |
| `/data/{category}` | GET | Category data |
| `/indicators` | GET | All indicators |
| `/gamification/missions` | GET | Active missions |
| `/gamification/score/{user}` | GET | User score |
| `/refresh` | POST | Trigger data refresh |

---

## Deployment

See [DEPLOY.md](DEPLOY.md) for the full deployment pipeline.

The `deploy.py` script automates:
1. Backend data refresh
2. Static page generation
3. React frontend build
4. Nginx sync and restart
5. Endpoint verification (21 endpoints)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

ZQM-Labs is focused on **family, business, automation, and safety** open-source technologies. Project Volusia is one flagship initiative.

---

## License

MIT License — see [LICENSE](LICENSE).
