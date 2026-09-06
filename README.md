# Project Volusia

> Open intelligence for Volusia County, FL. Real-time data, research, and community contribution.

---

## Overview

Project Volusia is a comprehensive open data portal for Volusia County, Florida. It aggregates 474 indicators across 15 categories from 112 authoritative sources, providing real-time sensors, research data, and community contribution capabilities.

### Key Features

- **474 Indicators** — Demographics, economy, health, education, environment, and more
- **112 Sources** — Government agencies, academic institutions, and reputable organizations
- **39 Real-Time Sensors** — Traffic cameras, weather stations, air quality monitors, water sensors, webcams
- **15 Categories** — Comprehensive coverage of county data
- **Community Contributions** — Humans and AI agents can submit data and research
- **Quality Validation** — Automated source verification and citation scoring

---

## Quick Start

### Prerequisites

- Python 3.11+
- SQLite 3
- matplotlib (for charts)

### Installation

```bash
# Clone the repository
git clone https://github.com/ZQM-Labs/project-volusia.git
cd project-volusia

# Install dependencies
pip install fastapi uvicorn matplotlib requests

# Run the portal
cd Tools
python -m volusia_data.portal_app
```

### Access

- **Portal**: http://localhost:8789
- **API**: http://localhost:8790
- **Reverse Proxy**: http://localhost:80

---

## Project Structure

```
project-volusia/
├── Tools/
│   └── volusia_data/
│       ├── portal_app.py          # FastAPI portal (port 8789)
│       ├── contribution_api.py    # Contribution API (port 8790)
│       ├── refresh_v2.py          # Data pipeline
│       ├── portal_contribute.py   # Web form frontend
│       ├── config.py              # Configuration
│       ├── volusia.db             # SQLite database (474 indicators)
│       ├── quality/
│       │   ├── validate.py        # Data quality validation
│       │   ├── citations.py       # Citation scoring
│       │   └── check_links.py     # Broken link detection
│       ├── fetchers/              # Standalone data fetchers
│       ├── processing/            # Data processing tools
│       ├── viz/                   # Visualization tools
│       ├── reports/               # Report generators
│       ├── research/              # Research tools
│       ├── alerts/                # Alerting system
│       └── contribution/          # Contribution review
├── .github/
│   └── ISSUE_TEMPLATE/            # Contribution templates
├── contribute.html                # Contribution landing page
├── sensors.html                   # Real-time sensors page
├── dashboard.html                 # Executive dashboard
├── osint-recon.html               # OSINT recon page
├── geoint.html                    # GEOINT surface page
├── citations.html                 # Citation validation page
├── CONTRIBUTING.md                # Contribution guide
├── RESEARCH_TECHNIQUES.md         # Research methodology
├── ARCHITECTURE.md                # System architecture
├── API.md                         # API documentation
└── DEPLOY.md                      # Deployment guide
```

---

## Data Categories

| Category | Indicators | Sources |
|----------|-----------|---------|
| Economy | 98 | 25 |
| Health | 46 | 11 |
| Education | 43 | 8 |
| Hydrography | 41 | 8 |
| Government | 40 | 14 |
| Transportation | 37 | 8 |
| Infrastructure | 36 | 9 |
| Climate | 34 | 6 |
| Housing | 22 | 7 |
| Public Safety | 19 | 10 |
| Demographics | 18 | 3 |
| Media | 17 | 7 |
| GIS | 9 | 7 |
| Boundaries | 8 | 5 |
| Terrain | 6 | 3 |

---

## Real-Time Sensors

### Traffic
- FL511 traffic cameras
- FDOT traffic sensors
- I-95 Express Lanes

### Weather
- NWS Melbourne station
- NOAA Weather Radio KIH26
- WeatherSTEM network

### Air Quality
- EPA AirNow
- PurpleAir network
- FL DEP monitoring stations

### Water
- USGS stream gauges
- NOAA tide gauges
- Water management districts

### Public Cameras
- Beach safety cameras (4 locations)
- Daytona Beach webcams
- Coastal camera network

---

## API Endpoints

### Portal API (port 8789)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/status` | GET | System status |
| `/api/indicators` | GET | All indicators |
| `/api/citations` | GET | Citation validation |
| `/api/search` | GET | Search indicators |
| `/api/compare` | GET | Compare indicators |
| `/api/trend` | GET | Trend analysis |
| `/api/correlation` | GET | Correlation analysis |
| `/api/export/full` | GET | Full data export |
| `/api/chart/*.png` | GET | Chart images |

### Contribution API (port 8790)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/contributions` | POST | Submit contribution |
| `/api/v1/contributions` | GET | List contributions |
| `/api/v1/contributions/{id}` | GET | Get contribution |
| `/api/v1/contributions/{id}` | PATCH | Update contribution |

---

## Quality Standards

### Source Hierarchy

| Tier | Trust | Examples |
|------|-------|----------|
| 1 | Highest | Census, BLS, BEA, NOAA, EPA, USGS |
| 2 | Verified | Universities, FRED, Zillow |
| 3 | Caution | SpotCrime, CrimeByCounty (cross-reference) |

### Validation Checks

- Source authority verification
- URL format and specificity
- Value range validation
- Vintage freshness check
- Cross-reference validation

### Quality Score

```
Score = (Authority × 0.30) + (URL × 0.20) + (Freshness × 0.20) + (Validity × 0.15) + (Description × 0.15)
```

---

## Contributing

### Humans

1. Visit https://zqmlabs.com/contribute/
2. Open a GitHub issue with label `contribution`
3. Email: zqmcomputing@gmail.com

### AI Agents

```bash
curl -X POST https://zqmlabs.com/api/v1/contributions \
  -H "Content-Type: application/json" \
  -d '{
    "contribution_type": "data_source",
    "content": {
      "title": "New Data Source",
      "source_url": "https://example.gov/data",
      "category": "Demographics"
    }
  }'
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guide.

---

## Research Techniques

1. **Source Discovery** — Government portal mining, API-first research
2. **Source Validation** — Authority, freshness, cross-reference, range
3. **Documentation** — Provenance, metadata, quality scoring
4. **Analysis** — Trend, correlation, gap analysis
5. **Automation** — Scheduled refresh, staleness monitoring

See [RESEARCH_TECHNIQUES.md](RESEARCH_TECHNIQUES.md) for full guide.

---

## Deployment

See [DEPLOY.md](DEPLOY.md) for deployment options:
- Local development
- Windows service
- Cloud deployment (future)

---

## License

Dual-licensed:
- **Open**: MIT/Apache-2.0 for public use
- **Commercial**: Contact zqmcomputing@gmail.com for licensing

---

## Contact

- **Email**: zqmcomputing@gmail.com
- **GitHub**: ZQM-Labs/project-volusia
- **Website**: https://zqmlabs.com/

---

*Last updated: 2026-09-06*
