# Project Volusia — System Map & Roadmap

> Generated: 2026-09-06
> Status: OPERATIONAL (124 indicators, 248 quality checks, 20 endpoints)

---

## I. SYSTEM ARCHITECTURE

### A. Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                               │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │Census PEP│  │Census ACS│  │Census CBP│  │ BLS QCEW │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │              │              │              │                 │
│  ┌────┴─────┐  ┌─────┴────┐  ┌─────┴────┐  ┌────┴─────┐           │
│  │ BLS LAUS │  │ BEA Reg. │  │ NOAA NCEI│  │ FDLE UCR │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │              │              │              │                 │
│  ┌────┴─────┐  ┌─────┴────┐  ┌─────┴────┐  ┌────┴─────┐           │
│  │ FL DOE   │  │ FL DOH   │  │ EPA      │  │ FCC BDC  │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │              │              │              │                 │
│  ┌────┴─────┐  ┌─────┴────┐  ┌─────┴────┐  ┌────┴─────┐           │
│  │ VCSO     │  │ VCPA     │  │ Volusia  │  │ Various  │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA PIPELINE (refresh_v2.py)                   │
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │  FETCHERS (6)   │───▶│  PROCESSING (3) │───▶│   SQLite DB     │ │
│  │  - census_pep   │    │  - clean.py     │    │  - indicators   │ │
│  │  - noaa         │    │  - geocode.py   │    │  - time_series  │ │
│  │  - qcew         │    │  - aggregate.py │    │  - submissions  │ │
│  │  - bls_laus     │    └─────────────────┘    │  - audit_log    │ │
│  │  - bea          │                           └────────┬────────┘ │
│  │  - census_acs   │                                    │          │
│  └─────────────────┘                                    │          │
│                                                         ▼          │
│                                              ┌─────────────────┐   │
│                                              │  QUALITY (89)   │   │
│                                              │  - validate.py  │   │
│                                              │  - 141 checks   │   │
│                                              └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        WEB LAYER (FastAPI)                          │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     PORTAL (:8789)                           │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │  HTML PAGES (6)                                         │ │   │
│  │  │  / (landing)  /contribute  /project-volusia  /data-     │ │   │
│  │  │  explorer  /dashboard  /osint-recon  /osint-report      │ │   │
│  │  └─────────────────────────────────────────────────────────┘ │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │  API ENDPOINTS (12)                                     │ │   │
│  │  │  /api/indicators  /api/status  /api/health             │ │   │
│  │  │  /api/export/csv  /api/export/json  /api/coherence     │ │   │
│  │  │  /api/executive-summary  /api/datasets                 │ │   │
│  │  │  /api/chart/population_trend.png                       │ │   │
│  │  │  /api/chart/employment_overview.png                    │ │   │
│  │  │  /api/chart/climate_summary.png                        │ │   │
│  │  │  /api/chart/unemployment_trend.png                     │ │   │
│  │  │  /api/chart/wage_trend.png                             │ │   │
│  │  │  /api/chart/income_overview.png                        │ │   │
│  │  │  /api/chart/housing_overview.png                       │ │   │
│  │  │  /api/chart/demographics.png                           │ │   │
│  │  │  /api/chart/education_health.png                       │ │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │               CONTRIBUTION API (:8790)                       │   │
│  │  POST /api/v1/contributions       - Submit                  │   │
│  │  GET  /api/v1/contributions/{id}  - Status                  │   │
│  │  GET  /api/v1/contributions       - List                    │   │
│  │  PATCH /api/v1/contributions/{id} - Triage                  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## II. CURRENT STATE SNAPSHOT

### A. Database Tables

| Table | Rows | Purpose |
|-------|------|---------|
| indicators | 124 | Current latest value per indicator |
| time_series | 104 | Historical values for trends |
| submissions | 21 | Contribution submissions |
| audit_log | 5 | Pipeline run history |
| datasets | 0 | Reserved |
| interviews | 0 | Stakeholder interviews |

### B. Indicator Categories

| Category | Count | % |
|----------|-------|---|
| Economy | 29 | 23% |
| Education | 20 | 16% |
| Government | 18 | 15% |
| Demographics | 15 | 12% |
| Health | 13 | 10% |
| Public Safety | 10 | 8% |
| Housing | 6 | 5% |
| Media | 4 | 3% |
| Infrastructure | 4 | 3% |
| Climate | 3 | 2% |
| Transportation | 2 | 2% |

### C. Data Sources (Top 10)

| Source | Indicators |
|--------|------------|
| Volusia County | 25 |
| Census ACS | 24 |
| Volusia County Schools | 10 |
| Census CBP | 10 |
| Volusia County EDC | 4 |
| EPA | 4 |
| Census PEP | 4 |
| Volusia County GIS | 3 |
| NOAA NCEI | 3 |
| FCC | 3 |

### D. Filesystem

```
Project-Volusia/
├── Tools/volusia_data/
│   ├── config.py                    # Centralized config + .env loader
│   ├── refresh_v2.py                # Unified data pipeline
│   ├── portal_app.py                # FastAPI portal (873 lines, 19 endpoints)
│   ├── contribution_api.py          # Contribution intake API
│   ├── portal_contribute.py         # Web form frontend (EN/ES)
│   ├── health_check.py              # Data freshness + API monitoring
│   ├── run_full_refresh.py          # Full refresh entry point
│   ├── fetchers/                    # 6 standalone fetchers
│   │   ├── fetch_census_pep.py
│   │   ├── fetch_noaa.py
│   │   ├── fetch_qcew.py
│   │   ├── fetch_bls_laus.py
│   │   ├── fetch_bea.py
│   │   └── fetch_census_acs.py
│   ├── processing/                  # 3 data processing tools
│   │   ├── clean.py
│   │   ├── geocode.py
│   │   └── aggregate.py
│   ├── quality/
│   │   └── validate.py              # 141 automated quality checks
│   ├── reports/
│   │   └── generate_weekly.py       # Weekly HTML report generator
│   ├── research/
│   │   └── interviews.py            # Stakeholder interview tracking
│   ├── contribution/
│   │   └── review.py                # Contribution review CLI
│   ├── alerts/
│   │   └── staleness_check.py       # Data staleness monitoring
│   ├── viz/
│   │   ├── map.py                   # Choropleth map generator
│   │   └── render_report.py         # Markdown → HTML renderer
│   └── portal/
│       └── app.py                   # Legacy portal (deprecated)
├── deploy_portal.py                 # Reverse proxy (port 80)
├── watchdog.py                      # Auto-restart dead services
├── start_launch.py                  # Startup all services
├── start_services.py                # Alternative startup
├── cloudflared-config.yml           # Cloudflared tunnel config
├── verify_startup.py                # Startup verification
├── index-new.html                   # Rich landing page
├── contribute.html                  # 3-pathway contribution page
├── project-volusia.html             # Portal page
├── dashboard.html                   # Executive dashboard
├── osint-recon.html                 # OSINT recon overview
├── osint-report.html                # Full OSINT report
├── Map/                             # Generated maps
│   ├── volusia_county.geojson
│   └── volusia_county_population.html
├── Reports/                         # Generated reports
│   └── weekly_2026-09-05.html
├── tests/
│   ├── test_portal.py               # 7 portal tests
│   ├── test_contribution.py         # 18 contribution tests
│   └── test_fetchers.py             # 5 fetcher tests
└── README.md                        # 289 lines
```

---

## III. ENDPOINT MAP

### A. HTML Pages (7)

| Path | Purpose | Lines |
|------|---------|-------|
| `/` | Main landing page with live indicators + charts | 307 |
| `/contribute` | 3-pathway contribution (human + AI) | 16KB |
| `/project-volusia` | Portal with live data + charts | 8.5KB |
| `/data-explorer` | Filterable data table + charts | (inline) |
| `/dashboard` | Executive dashboard with KPIs + activity feed | 13KB |
| `/osint-recon` | OSINT data sources overview | 6.4KB |
| `/osint-report` | Full OSINT recon report with findings | 7.4KB |

### B. Portal API Endpoints (12)

| Path | Type | Purpose |
|------|------|---------|
| `/api/health` | JSON | Health check |
| `/api/status` | JSON | System status + SLA |
| `/api/indicators` | JSON | All 124 indicators with provenance |
| `/api/coherence` | JSON | Source disagreement groups |
| `/api/export/csv` | CSV | Download all indicators |
| `/api/export/json` | JSON | Download with metadata |
| `/api/executive-summary` | JSON | Key metrics + freshness |
| `/api/datasets` | JSON | Dataset history |
| `/api/chart/population_trend.png` | PNG | Census PEP line chart |
| `/api/chart/employment_overview.png` | PNG | QCEW bar chart |
| `/api/chart/climate_summary.png` | PNG | NOAA bar chart |
| `/api/chart/unemployment_trend.png` | PNG | BLS LAUS line chart |
| `/api/chart/wage_trend.png` | PNG | QCEW wage line chart |
| `/api/chart/income_overview.png` | PNG | ACS income bar chart |
| `/api/chart/housing_overview.png` | PNG | Housing indicators bar chart |
| `/api/chart/demographics.png` | PNG | Racial demographics pie chart |
| `/api/chart/education_health.png` | PNG | Education/health bar chart |

### C. Contribution API Endpoints (6)

| Path | Type | Purpose |
|------|------|---------|
| `POST /api/v1/contributions` | JSON | Submit contribution |
| `GET /api/v1/contributions/{id}` | JSON | Check status |
| `GET /api/v1/contributions` | JSON | List submissions |
| `PATCH /api/v1/contributions/{id}` | JSON | Update status |
| `GET /api/v1/health` | JSON | Health check |
| `GET /` | JSON | Service metadata |

### D. Web Form Frontend (port 8791)

| Path | Language |
|------|----------|
| `/` | EN |
| `/es` | ES |
| `/f` | EN (knowledge) |
| `/es/f` | ES (knowledge) |
| `/i` | EN (ideas) |
| `/es/i` | ES (ideas) |
| `/status` | EN |
| `/es/status` | ES |

---

## IV. ROADMAP

### Phase 1: Foundation (DONE)

- [x] Mission statement + governance framework
- [x] Charter + strategic focus documents
- [x] FastAPI portal with 19 endpoints
- [x] SQLite database with 124 indicators
- [x] 3 live data sources (Census PEP, NOAA, BLS QCEW)
- [x] Contribution system (3 pathways, human + AI)
- [x] Data quality validation (141 checks)
- [x] Executive dashboard with live KPIs
- [x] 9 matplotlib charts
- [x] OSINT recon (11 categories)
- [x] Weekly report generator
- [x] Auto-restart watchdog
- [x] Reverse proxy + cloudflared config

### Phase 2: Unblock (THIS WEEK)

- [ ] Register Census ACS API key (5 min)
- [ ] Register BLS API key (~1 day)
- [ ] Register BEA API key (5 min)
- [ ] Deploy behind cloudflared (public URL)
- [ ] Windows Task Scheduler setup (06:00, 18:00 refresh)

### Phase 3: Stakeholder Acquisition (THIS MONTH)

- [ ] Interview 2 business owners
- [ ] Interview 2 residents
- [ ] Interview 2 industry movers/investors
- [ ] Present to Volusia EDC
- [ ] Create interview tracking in DB (interviews table)

### Phase 4: Content Engine (THIS MONTH)

- [ ] Weekly auto-generated HTML report
- [ ] YouTube data briefings (4 hrs/week)
- [ ] "This Week in Volusia" social thread (1 hr/week)
- [ ] Executive summary PDF export
- [ ] Newsletter signup (email collection)

### Phase 5: GitHub Growth (THIS QUARTER)

- [ ] CONTRIBUTING.md + PR template
- [ ] CI badges + topics optimization
- [ ] Publish 1.0 release
- [ ] "Why Volusia" blog post
- [ ] Cross-post to r/florida, Hacker News
- [ ] Target: 100 stars

### Phase 6: Feature Expansion (THIS QUARTER)

- [ ] Add 5 more data sources (FDOT, FDEP, local, etc.)
- [ ] Build Streamlit dashboard
- [ ] Add correlation analysis
- [ ] Add trend/change-point detection
- [ ] CSV bulk import endpoint
- [ ] Interactive map with all parcels
- [ ] Predictive models (Phase 3)

### Phase 7: Monetization (THIS QUARTER)

- [ ] Add SKU_CATALOG.md
- [ ] Add purchase-fulfillment bot
- [ ] Publish attestation methodology
- [ ] Create Upwork profile
- [ ] Target: $1,000/mo revenue

### Phase 8: Scale (NEXT QUARTER)

- [ ] Migrate to PostgreSQL
- [ ] Add rate limiting + API keys
- [ ] Dockerize all services
- [ ] Add Prometheus monitoring
- [ ] Multi-user support

### Phase 9: Regional Expansion (NEXT QUARTER)

- [ ] Orlando integration
- [ ] Titusville integration
- [ ] Palm Coast integration
- [ ] Statewide coverage

---

## V. METRICS TO TRACK

| Metric | Current | 3mo Target |
|--------|---------|------------|
| Indicators | 124 | 150 |
| Submissions | 21 | 100 |
| GitHub stars | 0 | 100 |
| Weekly visitors | 0 (LAN) | 500 |
| Stakeholder interviews | 0 | 10 |
| Revenue | $0 | $1,000/mo |
| Data sources | 33 | 40 |
| Quality checks | 248 | 300 |

---

## VI. BLOCKERS

| Blocker | Impact | Resolution |
|---------|--------|------------|
| Census ACS API key missing | No detailed demographics | Free registration (5 min) |
| BLS API key missing | No live unemployment | Free registration (~1 day) |
| BEA API key missing | No per capita income | Free registration (5 min) |
| No public web server | LAN-only access | Cloudflared deployment |
| No stakeholder interviews | No user-validated requirements | Schedule 2 per group |

---

## VII. IMMEDIATE NEXT ACTIONS (Today)

1. **Register 3 API keys** → unlocks 3 blocked sources
2. **Deploy cloudflared** → public access at volusia.zqmlabs.com
3. **Schedule stakeholder interviews** → validated requirements

---

*Document generated: 2026-09-06*
*System status: OPERATIONAL*
*Last commit: c520cbc*
