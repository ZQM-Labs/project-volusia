# Project Volusia — System Map & Roadmap

> Complete system inventory and development roadmap.

---

## System Map

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA SOURCES (112)                                │
│                                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Federal    │ │   State     │ │   Local     │ │ Commercial  │           │
│  │  Census     │ │  FL DEP     │ │ Volusia Co  │ │  Zillow     │           │
│  │  BLS        │ │  FL DOE     │ │  VCS        │ │  Realtor    │           │
│  │  BEA        │ │  FDLE       │ │  VCSO       │ │  PurpleAir  │           │
│  │  NOAA       │ │  FDOT       │ │  Clerk      │ │  WeatherSTEM│           │
│  │  EPA        │ │  FL DOH     │ │  EDC        │ │  EarthCam   │           │
│  │  USGS       │ │  FL DACS    │ │  TPO        │ │  LiveBeaches│           │
│  │  FEMA       │ │  FL DOS     │ │  Chamber    │ │  SpotCrime  │           │
│  │  HUD        │ │             │ │  Votran     │ │             │           │
│  │  USDA       │ │             │ │  SunRail    │ │             │           │
│  │  CDC        │ │             │ │  OneVoice   │ │             │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA PIPELINE (refresh_v2.py)                        │
│                                                                             │
│  Fetch → Validate → Transform → Store → Quality Check → Audit Log          │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SQLite DATABASE (volusia.db)                            │
│                                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ indicators  │ │ time_series │ │ submissions │ │ audit_log   │           │
│  │   474 rows  │ │   414 rows  │ │   21 rows   │ │   5 rows    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           ▼                           ▼                           ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│   PORTAL (:8789)    │ │    API (:8790)      │ │   PROXY (:80)       │
│                     │ │                     │ │                     │
│  15 API endpoints   │ │  4 CRUD endpoints   │ │  Static files       │
│  12 chart endpoints │ │  Validation         │ │  /api/* → :8789     │
│  10 HTML pages      │ │  Routing            │ │  /api/v1/* → :8790  │
│  Coherence groups   │ │  Status tracking    │ │                     │
└─────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

---

## Data Inventory

### Indicators by Category

| Category | Count | % of Total | Sources |
|----------|-------|-----------|---------|
| Economy | 98 | 20.7% | 25 |
| Health | 46 | 9.7% | 11 |
| Education | 43 | 9.1% | 8 |
| Hydrography | 41 | 8.6% | 8 |
| Government | 40 | 8.4% | 14 |
| Transportation | 37 | 7.8% | 8 |
| Infrastructure | 36 | 7.6% | 9 |
| Climate | 34 | 7.2% | 6 |
| Housing | 22 | 4.6% | 7 |
| Public Safety | 19 | 4.0% | 10 |
| Demographics | 18 | 3.8% | 3 |
| Media | 17 | 3.6% | 7 |
| GIS | 9 | 1.9% | 7 |
| Boundaries | 8 | 1.7% | 5 |
| Terrain | 6 | 1.3% | 3 |
| **Total** | **474** | **100%** | **112** |

### Source Trust Distribution

| Tier | Trust Level | Count | % |
|------|-------------|-------|---|
| 1 | Government/Education (.gov/.edu/.int) | 219 | 46.2% |
| 2 | Other (commercial/org) | 255 | 53.8% |

### Data Freshness

| Status | Count | % |
|--------|-------|---|
| Current (2024-2026) | 427 | 90.1% |
| Older | 47 | 9.9% |

---

## Real-Time Sensors (56)

### Traffic (11)

| Sensor | Source | Type |
|--------|--------|------|
| FL511 cameras | FL511 | Camera |
| FDOT sensors | FDOT | Sensor |
| Volusia cameras | Volusia County | Camera |
| I-95 Express | FDOT | Sensor |
| RTMC Northeast | RTMC | Service |
| AADT data | Volusia County | Count |
| Daytona Airport | Volusia County | Airport |
| Deltona Airport | Volusia County | Airport |
| Ormond Airport | Volusia County | Airport |
| New Smyrna Airport | Volusia County | Airport |
| Massey Ranch Airpark | Volusia County | Airport |

### Weather (16)

| Sensor | Source | Measurements |
|--------|--------|--------------|
| NWS Melbourne | NWS | Temp, humidity, wind, pressure |
| NOAA Radio KIH26 | NOAA | All-hazards alerts |
| WeatherSTEM | WeatherSTEM | Local conditions |
| Weather Underground | Wunderground | Personal stations |
| AWS Weather | AWS | Global weather |
| OpenWeather | OpenWeather | Global weather |
| NOAA Weather Station | NOAA NCEI | Historical data |

### Air Quality (9)

| Monitor | Source | Measurements |
|---------|--------|--------------|
| EPA AirNow | EPA | AQI, ozone, PM2.5 |
| PurpleAir | PurpleAir | PM2.5 (2-min updates) |
| FL DEP Daytona | FL DEP | Ozone, PM2.5, PM10 |
| FL DEP Port Orange | FL DEP | Ozone |
| AQS C127-5002 | FL DEP | Official monitor |
| AQS C127-2001 | FL DEP | Historic monitor |

### Water (14)

| Sensor | Source | Type |
|--------|--------|------|
| USGS Stream | USGS | Flow, level |
| USGS Groundwater | USGS | Level |
| NOAA Tides | NOAA | Water level |
| NOAA Buoy | NOAA | Ocean conditions |
| SFWMD | SFWMD | Surface/groundwater |
| SJRWMD | SJRWMD | Surface/groundwater |
| Volusia Water | Volusia County | Local monitoring |
| Water Quality | EPA | Violations |
| Water Safety | EPA | Safety score |

### Webcams (9)

| Camera | Location | Source |
|--------|----------|--------|
| Beach Cam | New Smyrna | Volusia County |
| Beach Cam | Ponce Inlet | Volusia County |
| Beach Cam | Ormond | Volusia County |
| Beach Cam | Dunlawton | Volusia County |
| Surf Cam | Daytona Hilton | EarthCam |
| Surf Cam | Flagler Ave | EarthCam |
| Surf Cam | Bethune | East Coast Cams |
| Surf Cam | Dunlawton Ave | Live Beaches |
| Station Cam | SunRail | SunRail |

---

## API Endpoints (21)

### Portal API (port 8789)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/status` | GET | System status |
| `/api/indicators` | GET | All indicators |
| `/api/indicators/{name}` | GET | Single indicator |
| `/api/citations` | GET | Citation validation |
| `/api/coherence` | GET | Cross-source coherence |
| `/api/search` | GET | Search indicators |
| `/api/compare` | GET | Compare indicators |
| `/api/trend` | GET | Trend analysis |
| `/api/correlation` | GET | Correlation analysis |
| `/api/export/csv` | GET | CSV export |
| `/api/export/json` | GET | JSON export |
| `/api/export/full` | GET | Full export with metadata |
| `/api/datasets` | GET | Dataset history |
| `/api/executive-summary` | GET | Key metrics |
| `/api/chart/population_trend.png` | GET | Population chart |
| `/api/chart/employment_overview.png` | GET | Employment chart |
| `/api/chart/climate_summary.png` | GET | Climate chart |
| `/api/chart/unemployment_trend.png` | GET | Unemployment chart |
| `/api/chart/wage_trend.png` | GET | Wage chart |
| `/api/chart/income_overview.png` | GET | Income chart |
| `/api/chart/housing_overview.png` | GET | Housing chart |
| `/api/chart/demographics.png` | GET | Demographics chart |
| `/api/chart/education_health.png` | GET | Education/health chart |
| `/api/chart/traffic_overview.png` | GET | Traffic chart |
| `/api/chart/schools_by_type.png` | GET | Schools chart |
| `/api/chart/infrastructure.png` | GET | Infrastructure chart |

### Contribution API (port 8790)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/contributions` | POST | Submit contribution |
| `/api/v1/contributions` | GET | List contributions |
| `/api/v1/contributions/{id}` | GET | Get contribution |
| `/api/v1/contributions/{id}` | PATCH | Update contribution |
| `/api/v1/health` | GET | Health check |

### HTML Pages (10)

| URL | Description |
|-----|-------------|
| `/` | Main website |
| `/contribute/` | Contribution landing |
| `/project-volusia` | Portal with live data |
| `/data-explorer` | Filterable data table |
| `/dashboard` | Executive dashboard |
| `/sensors` | Real-time sensors |
| `/osint-recon` | OSINT sources |
| `/osint-report` | OSINT recon report |
| `/geoint` | GEOINT surface |
| `/citations` | Citation validation |

---

## Database Schema

### indicators (474 rows)

| Column | Type | Description |
|--------|------|-------------|
| name | TEXT PK | Unique indicator name |
| value | TEXT | Numeric or text value |
| unit | TEXT | Unit of measurement |
| category | TEXT | One of 15 categories |
| source | TEXT | Originating agency |
| source_url | TEXT | Specific URL to data |
| vintage | TEXT | Year or date range |
| description | TEXT | Human-readable description |
| fetched_at | TEXT | Fetch timestamp |

### time_series (414 rows)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| indicator_name | TEXT | Reference to indicator |
| value | REAL | Numeric value |
| unit | TEXT | Unit of measurement |
| source | TEXT | Source agency |
| vintage | TEXT | Year or date range |
| fetched_at | TEXT | Fetch timestamp |

### submissions (21 rows)

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

### audit_log (5 rows)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment |
| action | TEXT | Action performed |
| details | TEXT | Action details |
| created_at | TEXT | Timestamp |

---

## Services

### Running Services

| Service | Port | Status | Process |
|---------|------|--------|---------|
| Portal | 8789 | RUNNING | portal_app.py |
| Contribution API | 8790 | RUNNING | contribution_api.py |
| Reverse Proxy | 80 | RUNNING | deploy_portal.py |

### Service Dependencies

```
portal_app.py
  ├── fastapi
  ├── uvicorn
  ├── sqlite3
  └── matplotlib

contribution_api.py
  ├── fastapi
  ├── uvicorn
  └── sqlite3

deploy_portal.py
  └── http.server (stdlib)
```

---

## Documentation

| File | Lines | Purpose |
|------|-------|---------|
| README.md | 230 | Project overview |
| ARCHITECTURE.md | 310 | System architecture |
| API.md | 380 | API reference |
| DEPLOY.md | 305 | Deployment guide |
| CONTRIBUTING.md | 280 | Contribution guide |
| RESEARCH_TECHNIQUES.md | 250 | Research methodology |
| SOURCE_EXPANSION_LOG.md | 100 | Source inventory |
| SYSTEM_MAP_AND_ROADMAP.md | — | This file |

---

## Roadmap

### Phase 1 — Foundation (COMPLETE)

- [x] Database schema design
- [x] Core data pipeline
- [x] 474 indicators across 15 categories
- [x] 112 authoritative sources
- [x] FastAPI portal with 15 endpoints
- [x] Contribution API with 4 endpoints
- [x] Quality validation system
- [x] Citation scoring
- [x] 12 matplotlib charts
- [x] 10 HTML pages
- [x] Real-time sensors (56)
- [x] OSINT recon page
- [x] GEOINT surface page
- [x] Executive dashboard
- [x] Data explorer
- [x] Comprehensive documentation

### Phase 2 — Enhancement (CURRENT)

- [ ] Register Census ACS API key
- [ ] Register BLS API key
- [ ] Register BEA API key
- [ ] Deploy behind cloudflared
- [ ] Public URL (volusia.zqmlabs.com)
- [ ] SSL/TLS certificate
- [ ] Automated data refresh (cron)
- [ ] Email alerts for stale data
- [ ] Webhook integrations

### Phase 3 — Community (NEXT)

- [ ] Stakeholder interviews (2 per group)
- [ ] Content engine (weekly reports)
- [ ] YouTube data briefings
- [ ] GitHub growth strategy
- [ ] CONTRIBUTING.md promotion
- [ ] External citations
- [ ] Community Discord/Slack

### Phase 4 — Scale (FUTURE)

- [ ] PostgreSQL migration
- [ ] Redis caching
- [ ] Docker containerization
- [ ] Kubernetes orchestration
- [ ] Multi-region deployment
- [ ] API rate limiting
- [ ] OAuth authentication
- [ ] Mobile app

### Phase 5 — Monetization (FUTURE)

- [ ] SKU_CATALOG.md
- [ ] Purchase fulfillment bot
- [ ] Attestation verification API
- [ ] Research engine data product
- [ ] Hosted execution layer
- [ ] Plugin marketplace

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Total indicators | 474 |
| Categories | 15 |
| Unique sources | 112 |
| High-trust URLs | 219 (46.2%) |
| Current vintage | 427 (90.1%) |
| Real-time sensors | 56 |
| API endpoints | 21 |
| HTML pages | 10 |
| Charts | 12 |
| Submissions | 21 |
| Documentation files | 8 |
| Quality score | 100.0% |

---

## External Blockers

| Blocker | Impact | Resolution |
|---------|--------|------------|
| Census ACS API key | No detailed demographics | Free registration (5 min) |
| BLS API key | No live unemployment | Free registration (~1 day) |
| BEA API key | No per capita income | Free registration (5 min) |
| No public web server | LAN-only access | Caddy/cloudflared deployment |
| No stakeholder interviews | No user-validated requirements | Schedule 2 per group |

---

## Success Signals

### Technical
- All endpoints return 200
- All services running
- Quality score >95%
- Zero low-trust domains
- Zero incomplete citations

### Community
- GitHub stars growing
- Contributions increasing
- External citations
- Stakeholder engagement

### Data
- Freshness >90%
- Coverage across all categories
- Real-time sensors operational
- Quality validation passing

---

*Last updated: 2026-09-06*
*Status: OPERATIONAL*
