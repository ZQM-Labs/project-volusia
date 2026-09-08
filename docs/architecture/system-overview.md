# System Architecture — Project Volusia

> High-level overview of the Project Volusia system architecture.

---

## Overview

Project Volusia is a distributed open data portal consisting of:

1. **Backend** (ZQM-Labs/project-volusia) — Data pipeline + API server
2. **Frontend** (ZQM-Computing/volusia-portal) — React web portal
3. **Infrastructure** — Cloudflare tunnel, GitHub Pages, Docker

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Sources                              │
│  Census │ BLS │ BEA │ NOAA │ C2ER │ Volusia County CVB         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ZQM-Labs/project-volusia (Backend)                  │
│              ┌────────────────────────────────────┐              │
│              │  Data Pipeline (refresh_v2.py)      │              │
│              │  - Fetch from APIs                   │              │
│              │  - Validate data                     │              │
│              │  - Store in SQLite                   │              │
│              └────────────────────────────────────┘              │
│                              │                                   │
│              ┌────────────────────────────────────┐              │
│              │  SQLite Database (volusia.db)       │              │
│              │  - indicators table                 │              │
│              │  - map_layers table                 │              │
│              │  - cvb_hotels table                 │              │
│              │  - audit_log table                  │              │
│              └────────────────────────────────────┘              │
│                              │                                   │
│              ┌────────────────────────────────────┐              │
│              │  FastAPI Server                     │              │
│              │  - Portal (:8789)                   │              │
│              │  - API (:8790)                      │              │
│              └────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ├─────────────────────────────────────┐
                              ▼                                     ▼
┌─────────────────────────────────────┐ ┌─────────────────────────────────────┐
│  Cloudflared Tunnel                  │ │  GitHub Pages                       │
│  volusia.zqmlabs.com → :80           │ │  volusia.zqmlabs.com                │
│  (Backend API access)                │ │  (Static frontend + JSON data)      │
└─────────────────────────────────────┘ └─────────────────────────────────────┘
```

---

## Components

### Backend (Python/FastAPI)

| Component | File | Purpose |
|-----------|------|---------|
| Data Pipeline | `Tools/volusia_data/refresh_v2.py` | Fetches data from sources |
| Portal App | `Tools/volusia_data/portal_app.py` | HTML dashboard + API |
| Database | `Tools/volusia_data/volusia.db` | SQLite storage |
| Config | `Tools/volusia_data/config.py` | Configuration |

### Frontend (React/TypeScript)

| Component | File | Purpose |
|-----------|------|---------|
| App | `src/App.tsx` | Main React app |
| Pages | `src/pages/*.tsx` | Page components |
| Hooks | `src/hooks/useApi.ts` | Data fetching |
| Components | `src/components/*.tsx` | UI components |

### Infrastructure

| Component | Purpose |
|-----------|---------|
| Cloudflare Tunnel | Routes traffic to backend |
| GitHub Pages | Hosts static frontend |
| Docker | Containerized deployment |
| GitHub Actions | CI/CD automation |

---

## Data Flow

1. **Data Sources** → Government APIs (Census, BLS, BEA, NOAA)
2. **Data Pipeline** → Fetches, validates, stores in SQLite
3. **SQLite Database** → Central data store
4. **JSON Export** → Static files for frontend
5. **GitHub Pages** → Serves static frontend
6. **Cloudflare Tunnel** → Routes API traffic to backend

---

## Network Architecture

```
Internet
    │
    ▼
Cloudflare DNS
    │
    ├── volusia.zqmlabs.com → GitHub Pages (frontend)
    │
    └── volusia.zqmlabs.com/api → Cloudflare Tunnel → ZQM-Node-4:8790
                                                       │
                                                       ▼
                                                FastAPI Backend
                                                       │
                                                       ▼
                                                SQLite Database
```

---

## Security

- **HTTPS**: All traffic encrypted via Cloudflare
- **CORS**: Configured for API access
- **Rate Limiting**: Implemented on API endpoints
- **Input Validation**: All user inputs validated
- **SQL Injection**: Parameterized queries only

---

## Scalability

- **Horizontal**: Multiple backend instances behind load balancer
- **Caching**: Redis/Memcached for frequently accessed data
- **CDN**: Cloudflare CDN for static assets
- **Database**: PostgreSQL migration path for larger datasets

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
