# Project Volusia — Deployment & API Architecture Reference

## Overview

The Project Volusia stack consists of three layers:
1. **Backend** (FastAPI on `:8000`) — data API, indicator endpoints, gamification
2. **Nginx** (port 80, Windows NSSM) — static file serving + reverse proxy to backend
3. **cloudflared** — tunnel to `*.zqmlabs.com`

## Directory Structure

```
C:/Users/zqmco/
├── scoop/persist/nginx/           # Host-level nginx
│   ├── conf/nginx.conf            # Main nginx config (active)
│   ├── conf/mime.types            # MIME type mappings
│   ├── html/                      # Web root
│   │   ├── index.html             # React SPA entry
│   │   ├── assets/                # React hashed assets
│   │   └── data/                  # Static category pages
│   │       ├── economic/index.html
│   │       ├── tourism/index.html
│   │       ├── transportation/index.html
│   │       ├── climate/index.html
│   │       ├── demographics/index.html
│   │       ├── real-estate/index.html
│   │       ├── education/index.html
│   │       ├── government-finance/index.html
│   │       ├── public-safety/index.html
│   │       └── health/index.html
│   └── logs/                      # access.log, error.log
├── project-volusia-web/           # Static site generator
│   ├── generate.py                # Generates all static HTML pages
│   ├── data/                      # Source category data
│   │   ├── economic/
│   │   ├── tourism/
│   │   └── ...
│   ├── start-server.bat           # NSSM VolusiaWeb startup
│   ├── start-all.bat              # Start all services
│   └── index.html
├── Docker/volusia-portal/         # Backend + React app
│   ├── backend/main.py            # FastAPI application
│   ├── backend/gamification.py    # Gamification engine
│   ├── data/                      # Database (NOT read by backend)
│   │   ├── volusia.db             # Stale copy (same as volusia-portal/data/)
│   │   └── cache/                 # JSON cache files
│   │       ├── latest.json
│   │       ├── indicators.json
│   │       └── {category}.json
│   ├── data/volusia.db            # Symlink/copy of volusia-portal/data/
│   ├── src/App.tsx                # React routes
│   ├── dist/                      # React build output
│   └── scripts/
│       ├── deploy.py              # Automated deploy pipeline
│       ├── deploy.sh              # Bash wrapper
│       ├── refresh_v2.py          # Data refresh utility
│       └── generate.py            # Backend data refresh
├── Docker/                        # Docker compose (optional)
│   └── docker-compose.yml
├── volusia-portal/                # Project root (DB lives here)
│   └── data/volusia.db            # PRIMARY database (50 indicators)
└── .cloudflared/
    └── config.yml                 # Cloudflare tunnel config
```

## API Endpoints (Backend :8000)

### Health & Metadata
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/health` | GET | Health check | `{"status":"healthy","indicator_count":50,"categories":{...}}` |
| `/latest` | GET | Latest indicators | `{"indicators":[...]}` |

### Indicators
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/indicators` | GET | All 50 indicators | `{"count":50,"indicators":[...]}` |
| `/indicators/{name}` | GET | Single indicator | `{id,name,value,unit,...}` |
|| `/data/indicators.json` | GET | Full indicator JSON | `{"count":50,"indicators":[...]}` |
| `/data/latest.json` | GET | Latest data snapshot | JSON |

### Gamification
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/gamification` | GET | Gamification dashboard (SPA) | HTML page |
| `/gamification/leaderboard` | GET | Leaderboard JSON | `{"leaderboard":[...]}` |
| `/gamification/missions` | GET | Missions list | JSON |
| `/gamification/pulse` | GET | Activity pulse | HTML page |
| `/gamification/profile/{user_id}` | GET | User profile | JSON |
| `/gamification/stats/{user_id}` | GET | User stats | JSON |
| `/gamification/achievements/{user_id}` | GET | Achievements | JSON |
| `/gamification/history/{user_id}` | GET | XP history | JSON |
| `/gamification/visit/{user_id}` | POST | Record visit + award XP | `{"xp_earned":0,"level":1,...}` |
| `/gamification/xp/{user_id}` | POST | Award XP | `{"total_xp":...,...}` |
| `/gamification/contribute` | POST | Submit contribution | `{"status":"queued",...}` |

### Admin
| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/refresh` | POST | Refresh all data | `{"status":"ok"}` |
| `/categories` | GET | All categories | `{category:count,...}` |

### Category Data Files (in `data/cache/`)
- `latest.json` — Most recent data snapshot
- `indicators.json` — Complete indicator catalog (50 entries)
- `census_dp03.json` — Economic census data
- `census_dp05.json` — Demographics census data
- `tourism.json` — Tourism statistics
- `transportation.json` — Transportation data
- `climate.json` — Climate data
- `education.json` — Education data
- `government.json` — Government finance
- `safety.json` — Public safety
- `health.json` — Health data
- `redfin_volusia.json` — Real estate data

## Nginx Routing Rules (Current)

The nginx.conf uses **location specificity** to route requests. **Important: nginx.conf does NOT include `conf.d/`** — all proxy locations are inline.

1. **Exact matches** (`location = /path`) — highest priority, proxy to backend
   - `/health`, `/latest`, `/indicators` → direct proxy
   - `/data/indicators.json`, `/data/latest.json` → direct proxy
   - `/gamification` → 301 redirect to `/gamification/`
   - `/gamification/` → 301 redirect to `/gamification`
   - `/gamification/leaderboard` → proxy to backend `/gamification/leaderboard`
   - `/refresh` → proxy POST to backend `/refresh`

2. **Prefix match** (`location /gamification/`) — proxy all methods to backend
   - `/gamification/missions`, `/gamification/pulse`, `/gamification/contribute`, etc. → proxy to backend `/gamification/*`
   - Handles all GET/POST gamification endpoints

3. **Static category pages** (`location ^~ /data/`) — serves static HTML
   - `/data/` → `try_files $uri $uri/ /data/index.html`
   - Category pages are pre-generated by `project-volusia-web/generate.py`

4. **Catch-all** (`location /`) → React SPA
   - All other routes → `try_files $uri $uri/ /index.html`
   - React handles client-side routing

## Deploy Pipeline

### Quick Start
```bash
# Full deploy
python C:/Users/zqmco/Docker/volusia-portal/scripts/deploy.py

# Dry run (preview)
python C:/Users/zqmco/Docker/volusia-portal/scripts/deploy.py --dry-run

# Skip backend refresh
python C:/Users/zqmco/Docker/volusia-portal/scripts/deploy.py --skip-backend

# Skip React build
python C:/Users/zqmco/Docker/volusia-portal/scripts/deploy.py --skip-frontend
```

### Refresh Backend Data
```bash
# Via nginx (port 80)
curl -X POST http://127.0.0.1/refresh?_secret=debug_token

# Via backend directly (port 8000)
curl -X POST http://127.0.0.1:8000/refresh?_secret=debug_token
```

### Gamification
```bash
# Record a visit
curl -X POST "http://127.0.0.1/gamification/visit/test_user"

# Leaderboard
curl http://127.0.0.1/gamification/leaderboard

# Missions
curl "http://127.0.0.1/gamification/missions?user_id=test_user"

# Contribute
curl -X POST "http://127.0.0.1/gamification/contribute?user_id=test_user" -H "Content-Type: application/json" -d '{"action":"test"}'
```### Steps (automated)
1. **Refresh backend data** — `POST http://127.0.0.1:8000/refresh`
2. **Generate static pages** — `python generate.py`
3. **Build React** — `npm run build` in `volusia-portal/src/`
4. **Sync to nginx** — Copy React build + static data pages to `html/`
5. **Restart services** — `nssm restart Volusia-Nginx`
6. **Verify** — Check all 21 endpoints return 200 via HTTPS

### Manual Steps (if deploy.py fails)
```bash
# 1. Refresh backend data (via nginx tunnel)
curl -X POST http://127.0.0.1/refresh?_secret=debug_token

# 1b. Or directly via backend
curl -X POST http://127.0.0.1:8000/refresh?_secret=debug_token

# 2. Generate static pages
python C:/Users/zqmco/project-volusia-web/generate.py

# 3. Build React
cd C:/Users/zqmco/Docker/volusia-portal/src
npm run build

# 4. Sync to nginx html
xcopy /Y /Q "C:\Users\zqmco\Docker\volusia-portal\src\build\*" "C:\Users\zqmco\scoop\persist\nginx\html\" /I
xcopy /Y /Q "C:\Users\zqmco\project-volusia-web\data\*" "C:\Users\zqmco\scoop\persist\nginx\html\data\" /I /E

# 5. Restart nginx (full kill+start if config changed)
taskkill /F /FI "imagename eq nginx.exe"
nssm start Volusia-Nginx

# 6. Restart backend if needed
cd C:\Users\zqmco\Docker\volusia-portal\backend
restart-backend.bat

# 7. Verify
curl -skL https://zqmlabs.com/ -o /dev/null -w "%{http_code}\n"
```

### Service Names
| Service | NSSM Name | Port | Purpose |
|---------|-----------|------|---------|
| Nginx | `Volusia-Nginx` | 80 | Static files + reverse proxy |
| Backend | `VolusiaWeb` | 8000 | FastAPI data API |
| cloudflared | `cloudflared` | — | Tunnel to internet |

### Database Path
**PRIMARY DB**: `C:\Users\zqmco\Docker\volusia-portal\data\volusia.db`

The backend (`backend/main.py`) resolves `DB_PATH = Path(__file__).resolve().parent.parent / "data" / "volusia.db"`. Since `main.py` is at `Docker\volusia-portal\backend\main.py`, `parent.parent` is `Docker\volusia-portal\`, so the DB is at `Docker\volusia-portal\data\volusia.db`.

There is also a copy at `Docker\volusia-portal\backend\data\volusia.db` — keep both in sync.

## nginx Configuration

### Active Config
- **File**: `C:\Users\zqmco\scoop\persist\nginx\conf\nginx.conf`
- **Port**: 80 (zqmlabs.com, www.zqmlabs.com)
- **Includes**: `mime.types` from `C:/Users/zqmco/scoop/apps/nginx/current/conf/mime.types`
- **Does NOT include**: `conf.d/*.conf` (the `conf.d/default.conf` is a dead file)
- **Test command**: `C:\Users\zqmco\scoop\apps\nginx\current\nginx.exe -t -p C:\Users\zqmco\scoop\persist\nginx`

### Important: Windows Path Gotcha
- `nginx -t` with `-p /c/Users/...` (forward slashes) **FAILS** on Windows
- Use `nginx -t -p C:/Users/zqmco/scoop/persist/nginx` (Windows-style path)
- The `current` symlink chain: `current → 1.31.4 → conf → persist/nginx/conf`

### Reloading nginx on Windows
NSSM `nssm restart Volusia-Nginx` may NOT fully kill the master process on Windows. If config changes don't take effect:
```cmd
taskkill /F /FI "imagename eq nginx.exe"
nssm start Volusia-Nginx
```

## Future API Improvements
- [ ] **GraphQL endpoint** — single query for all data sources
- [ ] **WebSocket streaming** — real-time indicator updates
- [ ] **Pagination** — for large indicator sets
- [ ] **Cache headers** — `ETag` and `If-None-Match` support
- [ ] **CORS** — allow cross-origin for API consumers
- [ ] **Rate limiting** — per-IP limits on data endpoints
- [ ] **Schema validation** — JSON Schema for all responses
- [ ] **OpenAPI spec** — auto-generated docs at `/api/docs`

### API Key Structure (for future)
```
X-API-Key: ***  # Scoped to read-only data access
X-API-Secret: [REDACTED]  # For write/admin operations
```

## Troubleshooting

### POST endpoints return 405
- nginx.conf `location /gamification/` block must be present
- Verify: `grep -n "location /gamification" conf/nginx.conf`
- Fix: Kill all nginx.exe processes + `nssm start Volusia-Nginx`

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

### error.log grows too large
- Check: `type C:\Users\zqmco\scoop\persist\nginx\logs\error.log`
- Consider log rotation

### `pct_white_alone_acs` = 100.0% (FIXED 2026-09-11)
- Root cause: Duplicate DB record `pct_white_alone_acs` (id:46) with wrong value 100.0
- Fix: Deleted broken record from `volusia-portal/data/volusia.db`
- Correct value: `pctWhiteAlone` (id:12) = 68.6%
- Prevent: Data refresh scripts should deduplicate indicators by name

## Future API Improvements
- [ ] **GraphQL endpoint** — single query for all data sources
- [ ] **WebSocket streaming** — real-time indicator updates
- [ ] **Pagination** — for large indicator sets
- [ ] **Cache headers** — `ETag` and `If-None-Match` support
- [ ] **CORS** — allow cross-origin for API consumers
- [ ] **Rate limiting** — per-IP limits on data endpoints
- [ ] **Schema validation** — JSON Schema for all responses
- [ ] **OpenAPI spec** — auto-generated docs at `/api/docs`

---

*Last updated: 2026-09-11*
