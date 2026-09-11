# Architecture — Project Volusia

> System architecture, components, and data flow.
> Updated 2026-09-11 — verified against live system.

---

## System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                     External Data Sources (112+)                       │
│  Census │ BLS │ BEA │ NOAA │ EPA │ USGS │ FEMA │ HUD │ USDA │ CDC   │
│  FDLE │ FL DEP │ FL DOE │ FDOT │ Volusia County │ C2ER              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   Data Pipeline (refresh_v2.py)                        │
│  Fetch → Validate → Transform → Store → Quality Check              │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│              SQLite Database (volusia.db, WAL mode)                    │
│  indicators │ gamification │ gamification_history │ gamification_state│
│  leaderboard │ submissions │ audit_log │ time_series                 │
│  50 indicators across 11 categories                                   │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  FastAPI      │    │  React SPA    │    │ Static HTML   │
│  Backend      │    │  (Vite)       │    │ (generate.py) │
│  :8000       │    │  dist/        │    │  /data/       │
└──────┬────────┘    └──────┬────────┘    └──────┬────────┘
       │                    │                     │
       └────────────────────┼─────────────────────┘
                            ▼
┌──────────────────────────────────────────────────────────────────────┐
│         nginx (:80, Windows NSSM — Volusia-Nginx)                     │
│  • /health, /latest, /indicators → proxy to backend :8000          │
│  • /data/indicators.json, /data/latest.json → proxy to backend      │
│  • /gamification/ (all methods) → proxy to backend /gamification/   │
│  • /data/ → static category HTML pages                               │
│  • / → React SPA catch-all (try_files $uri $uri/ /index.html)       │
│  • Security headers (CSP, HSTS, X-Frame-Options)                    │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────────────┐
│                              ▼                                         │
│  ┌─────────────────────────────────┐                                │
│  │   cloudflared (HTTPS, :443)      │                                │
│  │   Routes *.zqmlabs.com → :80    │                                │
│  │   TLS termination at edge        │                                │
│  └─────────────────────────────────┘                                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Data Sources

**Tier 1 — Government** (highest trust): Census Bureau, BLS, BEA, NOAA, EPA, USGS, FEMA, HUD, USDA, CDC, FDLE, FL DEP, FL DOE, FDOT, Volusia County

**Tier 2 — Academic/Nonprofit** (verified): Universities (.edu), FRED, County Health Rankings, Zillow, Realtor.com

**Tier 3 — Commercial** (use with caution): SpotCrime, CrimeByCounty, ZipCheckup (cross-reference required)

### 2. Data Pipeline

**File**: `scripts/refresh_v2.py`

```
1. Fetch data from source (API, CSV download, scraping)
2. Validate format and range
3. Transform to standard schema
4. Store in SQLite
5. Run quality checks
6. Log to audit_log
```

Triggered via `POST /refresh` or `scripts/deploy.py`.

### 3. Database Schema

**File**: `data/volusia.db` — SQLite with WAL mode, indexed on name/category

#### indicators
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| name | TEXT | Unique indicator name |
| value | TEXT | Numeric or text value |
| unit | TEXT | Unit of measurement |
| category | TEXT | Category |
| source | TEXT | Originating agency |
| source_url | TEXT | Specific URL |
| vintage | TEXT | Year or date range |
| description | TEXT | Human-readable description |
| fetched_at | TEXT | Fetch timestamp |

#### gamification
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| user_id | TEXT | User identifier |
| total_xp | INTEGER | Cumulative XP |
| level | INTEGER | Current level |
| streak_days | INTEGER | Consecutive visit days |
| indicators_viewed | INTEGER | Indicators explored |
| datasets_downloaded | INTEGER | Downloads count |

#### Other tables
- `gamification_history` — XP history per user
- `gamification_state` — Session state (daily visit timestamps)
- `leaderboard` — Cached leaderboard rankings
- `submissions` — User contributions awaiting review
- `sqlite_sequence` — Auto-increment tracking
- `time_series` — Historical indicator values

### 4. Web Layer

#### Backend API (port 8000)
**File**: `backend/main.py`

FastAPI application with endpoints: indicators, gamification, categories, refresh, latest, health.

**DB_PATH**: `Path(__file__).resolve().parent.parent / "data" / "volusia.db"` — resolves to `C:\Users\zqmco\Docker\volusia-portal\data\volusia.db`

Features: CORS middleware, rate limiting, HMAC auth for `/refresh`, SQLite + WAL mode.

**Routes**:
- `GET /health` — Health check + indicator count + categories
- `GET /indicators` — All 50 indicators
- `GET /indicators/{name}` — Single indicator
- `GET /latest` — Latest data snapshot
- `GET /data/indicators.json` — Full indicator JSON (338 entries)
- `GET /data/latest.json` — Latest data snapshot JSON
- `GET /categories` — All categories
- `POST /refresh` — Refresh all data
- `GET /gamification` — Gamification dashboard page (SPA)
- `GET /gamification/leaderboard` — Leaderboard JSON
- `GET /gamification/missions` — Missions list
- `GET /gamification/pulse` — Activity pulse
- `GET /gamification/profile/{user_id}` — User profile
- `GET /gamification/stats/{user_id}` — User stats
- `GET /gamification/achievements/{user_id}` — Achievements
- `POST /gamification/visit/{user_id}` — Record visit (XP)
- `POST /gamification/xp/{user_id}` — Award XP
- `GET /gamification/history/{user_id}` — XP history
- `POST /gamification/contribute` — Submit contribution

#### Web Server (port 80)
**File**: `C:\Users\zqmco\scoop\persist\nginx\conf\nginx.conf`

nginx as Windows NSSM service (`Volusia-Nginx`):
- Serves React SPA at `/` (catch-all)
- Serves static category pages at `/data/`
- Proxies API endpoints to backend on `:8000`
- Security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- `location = /health` → proxy to backend
- `location = /latest` → proxy to backend
- `location = /indicators` → proxy to backend
- `location = /data/indicators.json` → proxy to backend
- `location = /data/latest.json` → proxy to backend (rewrite to `/latest`)
- `location = /gamification` → 301 redirect to `/gamification/`
- `location = /gamification/` → 301 redirect to `/gamification`
- `location /gamification/` → proxy all methods to backend `/gamification` (strips prefix)
- `location = /refresh` → proxy POST to backend `/refresh`
- `location = /gamification/leaderboard` → proxy to backend `/gamification/leaderboard`
- `location ^~ /data/` → serve static category HTML
- `location /` → React SPA catch-all (`try_files $uri $uri/ /index.html`)

**Important**: nginx.conf does NOT include `conf.d/`. All proxy locations are inline in nginx.conf. The `conf.d/default.conf` file exists but is not loaded.

**nginx -t**: `C:\Users\zqmco\scoop\apps\nginx\current\nginx.exe -t -p C:\Users\zqmco\scoop\persist\nginx`

**Note on NSSM**: On Windows, `nssm restart Volusia-Nginx` may not fully kill the master process. If config changes don't take effect, kill all nginx.exe processes with `taskkill /F /FI "imagename eq nginx.exe"` then `nssm start Volusia-Nginx`.

#### HTTPS Tunnel
**File**: `C:\Users\zqmco\.cloudflared\config.yml`

cloudflared as Windows service (`cloudflared`):
- Routes `*.zqmlabs.com` → `http://127.0.0.1:80`
- TLS termination at cloudflared edge
- DNS handled by cloudflared proxy

### 5. Frontend

#### React SPA
**File**: `volusia-portal/src/`

React 18 + Vite + TypeScript + Tailwind CSS with Nivo charts and Leaflet maps.
Build output: `dist/` → synced to nginx `html/` during deploy.

#### Static Page Generation
**File**: `project-volusia-web/generate.py`

Generates category HTML pages from backend data:
- Output: `project-volusia-web/data/{category}/index.html`
- Copied to nginx `html/data/` during deploy

### 6. Service Startup Scripts

| Script | Purpose |
|--------|---------|
| `project-volusia-web\start-server.bat` | NSSM VolusiaWeb — runs `uvicorn main:app --port 8000` from `Docker\volusia-portal\backend\` |
| `project-volusia-web\start-all.bat` | Starts all services including static site on :8089 |
| `project-volusia-web\start-backend.bat` | Starts backend only |
| `project-volusia-web\start-www-redirect.bat` | Static site redirect |

**Important**: `start-server.bat` does `cd /d C:\Users\zqmco\Docker\volusia-portal\backend` then runs uvicorn. The `DB_PATH` in `main.py` resolves relative to `backend/main.py`, so it reads from `C:\Users\zqmco\Docker\volusia-portal\data\volusia.db` (the project root's data directory, NOT `backend/data/`).

**There are TWO volusia.db files**:
- `C:\Users\zqmco\Docker\volusia-portal\data\volusia.db` — **PRIMARY** (50 indicators, what the backend reads)
- `C:\Users\zqmco\Docker\volusia-portal\backend\data\volusia.db` — **STALE COPY** (copy of primary)

### 7. Docker Compose (Optional)

**File**: `docker-compose.yml`

Defines: `frontend` (port 8080), `backend` (internal only), `searxng` (port 8081, profile: search).
Backend is NOT exposed to the internet — reached through nginx via Docker network.

### 8. Gamification Engine

**File**: `backend/gamification.py`

- 30 missions across 5 tiers
- 14 pathways (A–S)
- XP-based scoring system
- Contributor badges and stats
- Daily visit tracking with streak bonuses
- `gamification_state` table tracks per-user daily visit timestamps

### 9. Quality System

#### Validation
- Range validation per indicator
- Freshness validation per source
- Cross-source coherence checks
- Automated quality scoring

---

## Data Flow

### Ingestion
```
External Source → refresh_v2.py → SQLite (indicators)
                              → Quality Check
                              → Audit Log
```

### Deployment
```
deploy.py → POST /refresh → generate.py → npm run build
         → xcopy to nginx/html/ → nginx reload → verify all URLs
```

### API Query
```
Client → cloudflared (HTTPS) → nginx (:80)
       → backend proxy (/health, /indicators, /gamification/, /data/indicators.json, /data/latest.json)
       → nginx static files (/data/<category>/)
       → React SPA catch-all (/)
```

### Contribution
```
Submit → /gamification/contribute → SQLite (submissions)
       → Review → Approve/Reject
       → Update indicators (if approved)
```

### Gamification Flow
```
User visits site → POST /gamification/visit/{user_id} → backend
       → Check daily visit state → Award XP → Update streak
       → Log to gamification_history → Update leaderboard
```

---

## Nginx Routing Rules (Current)

The nginx.conf uses **location specificity** to route requests:

1. **Exact matches** (`location = /path`) — highest priority, proxy to backend
   - `/health`, `/latest`, `/indicators` → direct proxy
   - `/data/indicators.json`, `/data/latest.json` → direct proxy
   - `/gamification/leaderboard` → proxy to backend `/gamification/leaderboard`

2. **Prefix match** (`location /gamification/`) — proxy all methods to backend `/gamification` (strips `/gamification/` prefix)
   - `/gamification/missions`, `/gamification/pulse`, `/gamification/contribute`, etc. → work correctly
   - `/gamification/` → proxy to backend `/gamification/`
   - Handles POST `/gamification/visit/{user_id}`, etc.

3. **Static category pages** (`location ^~ /data/`) — serves static HTML
   - `/data/` → `try_files $uri $uri/ /data/index.html`
   - Category pages are pre-generated by `project-volusia-web/generate.py`

4. **Catch-all** (`location /`) → React SPA
   - All other routes → `try_files $uri $uri/ /index.html`
   - React handles client-side routing

**Important**: nginx.conf does NOT include `conf.d/`. The `conf.d/default.conf` file exists but is not loaded. All proxy locations are inline.

---

## Known Issues and Fixes (2026-09-11)

### Fixed
- **POST /gamification/visit/{user_id} returned 405**: Added `location /gamification/` proxy block to nginx.conf
- **pct_white_alone_acs = 100.0%**: Deleted broken record (id:46) from `volusia-portal/data/volusia.db`. `pctWhiteAlone` (id:12) = 68.6% is the correct value
- **nginx -t fails with path error**: Use Windows-style path: `nginx.exe -t -p C:/Users/zqmco/scoop/persist/nginx`
- **Backend reading wrong DB**: `DB_PATH` resolves to `volusia-portal/data/volusia.db` (parent of `backend/`), not `backend/data/volusia.db`. Both copies kept in sync
- **nginx.conf mime.types**: `include C:/Users/zqmco/scoop/apps/nginx/current/conf/mime.types` works through symlink chain

### Active
- **error.log is 21MB+**: Consider log rotation
- **Stale `scoop\apps\nginx\current\nginx.conf`**: Old config on port 8089, not used by NSSM
- **`conf.d/default.conf` dead file**: Contains proxy rules but is never included by nginx.conf

---

## Monitoring

### Health Checks
- `GET /health` — System status + indicator count + categories
- `GET /` — Service info
- `GET /data/indicators.json` — Full indicator list
- `GET /gamification/leaderboard` — Leaderboard JSON

### Audit Trail
- `audit_log` table tracks all pipeline runs
- `submissions` table tracks all contributions
- Console logging for errors

---

## Dependencies

### Required
- Python 3.11+, FastAPI, Uvicorn, sqlite3
- Node.js 20+, npm
- nginx (Windows NSSM)
- cloudflared (Windows service)
- SQLite 3

### Optional
- Docker + Docker Compose (optional, for containerized deployment)
- matplotlib, requests, pandas

---

## Troubleshooting

### POST endpoints return 405
- nginx.conf `location /gamification/` block must be present
- Verify: `grep -n "location /gamification" conf/nginx.conf`
- Fix: Reload nginx (or kill all nginx.exe processes and restart via NSSM)

### API returns stale data
- Backend reads from `volusia-portal/data/volusia.db` — verify correct DB
- Restart backend: kill PID and restart `uvicorn main:app --port 8000`
- Verify: `curl http://127.0.0.1:8000/indicators` shows correct count

### nginx -t fails
- Use Windows-style path: `nginx.exe -t -p C:/Users/zqmco/scoop/persist/nginx`
- Forward slashes with `-p` prefix don't work on Windows

### NSSM restart doesn't pick up config changes
- Windows NSSM doesn't always fully kill the master process
- Fix: `taskkill /F /FI "imagename eq nginx.exe"` then `nssm start Volusia-Nginx`

### Backend restart blocked (admin rights)
- PID runs as Session 0 Windows service
- Use `nssm restart VolusiaWeb` or have admin run `Restart-Service VolusiaWeb`

---

*Last updated: 2026-09-11*
