# Architecture — Project Volusia

> System architecture and data flow documentation.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Sources (112+)                         │
│  Census │ BLS │ BEA │ NOAA │ EPA │ USGS │ FEMA │ HUD │ USDA    │
│  CDC │ FDLE │ FL DEP │ Volusia County │ Universities │ C2ER   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Pipeline (refresh_v2.py)                   │
│  Fetch → Validate → Transform → Store → Quality Check           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQLite Database (volusia.db)                     │
│  indicators │ time_series │ submissions │ audit_log │ datasets  │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────┼──────────────────────────────┐
│                             ▼                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              FastAPI Backend (port 8000)               │ │
│  │  main.py — 50+ endpoints, gamification, analytics    │ │
│  │  CORS, rate limiting, HMAC auth for /refresh         │ │
│  └──────────────────────────┬────────────────────────────┘ │
│                             │                              │
│                ┌────────────┼────────────┐                │
│                ▼            ▼            ▼                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │  nginx       │ │  React SPA  │ │  Static HTML │        │
│  │  :80 (Win)  │ │  :5173      │ │  /data/      │        │
│  │              │ │  (Vite)     │ │  (generated) │        │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘        │
│         │               │               │                │
│         └───────┬───────┘               │                │
│                 ▼                       │                │
│  ┌──────────────────────────────────┐  │                │
│  │  cloudflared (port 443)          │  │                │
│  │  HTTPS, DNS *.zqmlabs.com → :80  │  │                │
│  └──────────────────────────────────┘  │                │
└─────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Data Sources

#### Tier 1 — Government (Highest Trust)
- Census Bureau, BLS, BEA, NOAA, EPA, USGS, FEMA, HUD, USDA, CDC
- FDLE, FL DEP, FL DOE, FDOT, Volusia County

#### Tier 2 — Academic/Nonprofit (Verified)
- Universities (.edu), FRED, County Health Rankings, Zillow, Realtor.com

#### Tier 3 — Commercial (Use with Caution)
- SpotCrime, CrimeByCounty, ZipCheckup (cross-reference required)

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

Triggered via `POST /refresh?secret=<TOKEN>` or `scripts/deploy.py`.

### 3. Database Schema

**File**: `data/volusia.db`

#### indicators
| Column | Type | Description |
|--------|------|-------------|
| name | TEXT PK | Unique indicator name |
| value | TEXT | Numeric or text value |
| unit | TEXT | Unit of measurement |
| category | TEXT | One of 15 categories |
| source | TEXT | Originating agency |
| source_url | TEXT | Specific URL |
| vintage | TEXT | Year or date range |
| description | TEXT | Human-readable description |
| fetched_at | TEXT | Fetch timestamp |

#### time_series
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| indicator_name | TEXT | Reference to indicator |
| value | REAL | Numeric value |
| unit | TEXT | Unit of measurement |
| source | TEXT | Source agency |
| vintage | TEXT | Year or date range |
| fetched_at | TEXT | Fetch timestamp |

#### submissions
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| submission_id | TEXT | Unique submission ID |
| contribution_type | TEXT | Type of contribution |
| content | TEXT | JSON content |
| status | TEXT | queued/approved/rejected |
| reviewer | TEXT | Assigned reviewer |
| created_at | TEXT | Submission timestamp |
| updated_at | TEXT | Last update timestamp |

### 4. Web Layer

#### Backend API (port 8000)
**File**: `backend/main.py`

- FastAPI application v3.0.0
- 50+ endpoints: indicators, datasets, gamification, analytics
- SQLite database connection
- HMAC auth for `/refresh` endpoint
- CORS middleware for zqmlabs.com
- Rate limiting middleware

#### Web Server (port 80)
**File**: `C:\Users\zqmco\scoop\persist\nginx\conf\nginx.conf`

- nginx (Windows NSSM service: `Volusia-Nginx`)
- Serves React SPA at `/` (catch-all)
- Serves static category pages at `/data/`
- Proxies API endpoints to backend on `:8000`
- Serves `/data/indicators.json` and `/data/latest.json` from backend
- Security headers (CSP, HSTS, X-Frame-Options, etc.)

#### HTTPS Tunnel
**File**: `C:\Users\zqmco\.cloudflared\config.yml`

- cloudflared (Windows service: `cloudflared`)
- Routes `*.zqmlabs.com` → `http://127.0.0.1:80`
- TLS termination at cloudflared edge
- DNS handled by cloudflared proxy

### 5. Frontend

#### React SPA
**File**: `volusia-portal/src/`

- React 18 + Vite + TypeScript + Tailwind CSS
- Nivo charts for data visualization
- Leaflet maps for geographic data
- Build output: `dist/` → synced to nginx `html/`
- Development server: `npm run dev` (port 5173)

#### Static Page Generation
**File**: `project-volusia-web/generate.py`

- Generates category HTML pages from backend data
- Output: `project-volusia-web/data/{category}/index.html`
- Copied to nginx `html/data/` during deploy

### 6. Gamification Engine

**File**: `backend/gamification.py`

- 30 missions across 5 tiers
- 14 pathways (A–S)
- XP-based scoring system
- Contributor badges and stats

### 7. Quality System

#### Validation
- Range validation per indicator
- Freshness validation per source
- Cross-source coherence checks
- Automated quality scoring

#### Data Sources by Category
| Category | Sources |
|----------|---------|
| Economic | BLS, BEA, Census, QCEW, C2ER |
| Demographics | Census PEP, ACS |
| Climate | NOAA, EPA |
| Tourism | STR, C2ER |
| Education | FL DOE, Census |
| Environment | EPA, NOAA |
| Public Safety | FDLE, FEMA |
| Transportation | FDOT, Census |
| Government Finance | Census, FL DEP |
| Health | CDC, FL DEP |
| Housing | Census, Zillow |

---

## Data Flow

### Ingestion Flow
```
Source → refresh_v2.py → SQLite (indicators)
                       → Quality Check
                       → Audit Log
```

### Deployment Flow
```
deploy.py → POST /refresh → generate.py → npm run build
         → xcopy to nginx/html/ → nginx -s reload → verify all URLs
```

### API Query Flow
```
Client → cloudflared (HTTPS) → nginx (:80)
       → backend proxy (/data/indicators.json, /latest)
       → nginx static file (/data/economic/, /data/tourism/)
       → React SPA catch-all (/)
```

### Contribution Flow
```
Submit → /api/contribute → SQLite (submissions)
              ↓
              Review → Approve/Reject
              ↓
              Update indicators (if approved)
```

---

## Security

### Authentication
- Optional HMAC secret for `/refresh` endpoint (`VOLUSIA_REFRESH_TOKEN`)
- No authentication required for reads
- CORS restricted to `zqmlabs.com`, `www.zqmlabs.com`, `localhost:8080`

### Input Validation
- JSON schema validation
- URL format validation
- Value range validation
- SQL injection prevention (parameterized queries)

### Rate Limiting
- Per-IP rate limiter (default: 60 req/min)
- Configurable via `VOLUSIA_RATE_LIMIT` env var
- Returns 429 when limit exceeded

---

## Performance

### Database
- SQLite with WAL mode
- Indexed on name, category, source
- 50+ indicators, ~100KB

### API Response Times
- Health check: <10ms
- Indicator list: <50ms
- Chart generation: <500ms
- Search: <100ms

### Caching
- Backend data cache in `data/cache/`
- React content-hashed assets (1yr nginx cache)
- Static category pages generated at deploy time

---

## Deployment

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions.

### Services
| Service | Name | Management |
|---------|------|------------|
| nginx | `Volusia-Nginx` | `nssm restart Volusia-Nginx` |
| cloudflared | `cloudflared` | `nssm restart cloudflared` |
| Backend | `VolusiaWeb` | `nssm restart VolusiaWeb` (admin) |

### nginx Configuration
```
C:\Users\zqmco\scoop\persist\nginx\conf\nginx.conf
```

Key location blocks:
- `location = /data/indicators.json` — exact proxy to backend
- `location = /data/latest.json` — rewrite to `/latest` + proxy
- `location ^~ /data/` — static category pages
- `location /` — React SPA catch-all

---

## Monitoring

### Health Checks
- `GET /health` — System status + indicator count
- `GET /` — Service info
- `GET /data/indicators.json` — Full indicator list

### Audit Trail
- `audit_log` table tracks all pipeline runs
- `submissions` table tracks all contributions
- Console logging for errors

---

## Testing

### TypeScript
```bash
npx tsc --noEmit    # Must pass with zero errors
```

### Backend
```bash
python -m pytest tests/
```

### Deployment Verify
```bash
python scripts/deploy.py --dry-run
# Or manually:
curl -sI https://zqmlabs.com/ | findstr "HTTP"
curl -s https://zqmlabs.com/data/indicators.json | python -m json.tool
```

---

## Dependencies

### Required
- Python 3.11+
- FastAPI, Uvicorn
- Node.js 20+
- npm
- Docker + Docker Compose (optional)
- SQLite 3
- nginx (Windows NSSM)
- cloudflared (Windows service)

### Optional
- matplotlib (charts)
- requests (fetches)
- pandas (processing)

---

*Last updated: 2<|fim_hole|>

# API Documentation — Project Volusia

> Complete reference for all API endpoints.

---

## Overview

The Project Volusia API is a FastAPI application serving real-time indicators for Volusia County, Florida. It runs on port 8000 and is proxied through nginx (port 80) and cloudflared (HTTPS).

**Base URL**: `http://127.0.0.1:8000` (direct) or `https://zqmlabs.com` (via cloudflared)

**Authentication**: HMAC secret required for write/admin endpoints via `?secret=` query parameter.

---

## Health & Status

### `GET /health`

Health check endpoint.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "db_exists": true,
  "indicator_count": 50,
  "categories": {"Economic": 15, "Tourism": 8, ...},
  "empty_categories": []
}
```

### `GET /`

Service info.

**Response** (200 OK):
```json
{
  "service": "Project Volusia API",
  "version": "3.0.0"
}
```

---

## Indicators

### `GET /indicators`

List all indicators.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by category |
| `limit` | integer | Max results (default: 200) |

**Response** (200 OK):
```json
{
  "count": 50,
  "indicators": [
    {
      "name": "total_population_pep_2024",
      "value": "601107",
      "unit": "people",
      "category": "Demographics",
      "source": "Census PEP",
      "source_url": "https://...",
      "vintage": "2024",
      "description": "..."
    }
  ]
}
```

### `GET /indicators/{name}`

Get a specific indicator by name.

**Response** (200 OK): Full indicator object, or 404 if not found.

### `GET /indicators/category/{category}`

Get all indicators in a category.

### `GET /categories`

List all available categories.

### `GET /datasets`

List all datasets with metadata.

### `GET /map-layers`

List all map layers.

---

## Latest Data

### `GET /latest`

Latest values for all indicators.

**Response** (200 OK): Array of latest indicator values.

### `GET /data/indicators.json`

All indicators as JSON (proxied from backend).

### `GET /data/latest.json`

Latest values as JSON (rewritten from `/latest`).

---

## Category Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/data/economic.json` | GET | Economic indicators |
| `/data/tourism.json` | GET | Tourism indicators |
| `/data/climate.json` | GET | Climate indicators |
| `/data/demographics.json` | GET | Demographics indicators |
| `/data/health.json` | GET | Health indicators |
| `/data/education.json` | GET | Education indicators |
| `/data/environment.json` | GET | Environment indicators |
| `/data/public-safety.json` | GET | Public safety indicators |
| `/data/transportation.json` | GET | Transportation indicators |
| `/data/government-finance.json` | GET | Government finance indicators |
| `/data/housing.json` | GET | Housing indicators |
| `/data/datasets.json` | GET | Dataset metadata |
| `/data/map-layers.json` | GET | Map layers |
| `/data/stakeholders.json` | GET | Stakeholder data |
| `/data/news.json` | GET | News items |
| `/data/{name}.json` | GET | Any category by name |

---

## Export

### `GET /indicators.csv`

Download all indicators as CSV.

### `GET /data/indicators.csv`

Download all indicators as CSV (data endpoint).

### `GET /api/export/{format}`

Full data export.

**Path Parameters**: `format` = `json` or `csv`

---

## Analytics

### `GET /analytics/summary`

Summary statistics.

### `GET /analytics/trends/{indicator_name}`

Time series for an indicator.

### `GET /analytics/comparison/{indicator_name}`

Cross-region comparison.

### `GET /analytics/dashboard`

Full dashboard data.

---

## Gamification

### `GET /gamification`

Gamification hub.

### `GET /api/gamification/stats/{user_id}`

User stats.

### `GET /api/gamification/missions/{user_id}`

User missions.

### `GET /api/gamification/pulse`

Gamification pulse.

### `GET /api/gamification/badges/{contributor_id}`

User badges.

### `POST /api/gamification/visit/{user_id}`

Record a visit.

### `GET /api/gamification/state/{contributor_id}`

Gamification state.

---

## Search & Discovery

### `GET /api/indicators/search`

Search indicators.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query |
| `category` | string | Filter by category |
| `source` | string | Filter by source |
| `limit` | integer | Max results |

### `GET /api/indicators/bulk`

Bulk indicator retrieval.

### `GET /api/indicators/stats`

Indicator statistics summary.

---

## Contribution

### `POST /api/contribute`

Submit a contribution.

### `GET /api/contributor`

Get contributor info.

---

## News

### `GET /news.json`

Latest news items.

### `GET /api/news.json`

API news endpoint.

---

## Admin

### `POST /refresh`

Trigger pipeline refresh.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `secret` | string | HMAC secret (`VOLUSIA_REFRESH_TOKEN`) |

**Requires authentication**. Returns 401 if invalid.

### `GET /diagnostics`

System diagnostics.

### `GET /api/keys`

API key status.

### `GET /api/fetch-status`

Data fetch status.

---

## Webhooks

### `POST /api/webhook`

Receive webhook notifications.

---

## Rate Limiting

All endpoints are rate-limited (default: 60 req/min per IP). Returns 429 when exceeded.

Configure via `VOLUSIA_RATE_LIMIT` environment variable.

---

## CORS

Allowed origins: `https://zqmlabs.com`, `https://www.zqmlabs.com`, `http://localhost:8080`, `http://127.0.0.1:8080`.

---

*Last updated: 2026-09-11*
