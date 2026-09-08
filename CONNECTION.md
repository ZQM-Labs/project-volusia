# Project Volusia — Repository Connection Guide

> How ZQM-Labs/project-volusia and ZQM-Computing/volusia-portal work together.

---

## Quick Links

| Resource | URL |
|----------|-----|
| **Frontend Repo** | https://github.com/ZQM-Computing/volusia-portal |
| **Backend Repo** | https://github.com/ZQM-Labs/project-volusia |
| **Live Portal** | https://volusia.zqmlabs.com |
| **API Endpoint** | https://volusia.zqmlabs.com/api |

---

## This Repository: ZQM-Labs/project-volusia

**Role**: Backend data pipeline + API server

### Key Files
- `Tools/volusia_data/portal_app.py` — FastAPI portal (:8789)
- `Tools/volusia_data/refresh_v2.py` — Data refresh pipeline
- `Tools/volusia_data/volusia.db` — SQLite database
- `Data/` — Exported JSON data files

### Data Sources
- US Census Bureau (PEP, ACS DP03/DP05)
- Bureau of Labor Statistics (LAUS, QCEW)
- Bureau of Economic Analysis (Regional)
- NOAA NCEI (Daily Summaries)
- C2ER (Cost of Living Index)
- Volusia County CVB (Hotel data)

### Running Locally
```bash
cd Tools/volusia_data
python portal_app.py
# Portal: http://localhost:8789
# API: http://localhost:8790
```

### Data Refresh
```bash
cd Tools/volusia_data
python refresh_v2.py
```

---

## Companion Repository: ZQM-Computing/volusia-portal

**Role**: Frontend web portal (React/TypeScript)

### Key Files
- `src/` — React frontend source
- `data/` — Static JSON data exports
- `vite.config.ts` — Build configuration
- `.github/workflows/deploy.yml` — CI/CD

### Building
```bash
npm install
npm run build
# Output: dist/
```

### Deployment
- GitHub Actions builds and deploys to `gh-pages` branch
- CNAME: `volusia.zqmlabs.com`
- URL: https://volusia.zqmlabs.com

---

## Data Flow

```
Data Sources → refresh_v2.py → SQLite DB → JSON Export → Frontend
```

1. Backend fetches data from government APIs
2. Data is stored in SQLite database
3. JSON files are exported to `Data/` directory
4. Frontend imports JSON files and builds static site
5. GitHub Actions deploys to GitHub Pages

---

## Maintenance

### Update Data
```bash
cd Tools/volusia_data
python refresh_v2.py
```

### Export JSON for Frontend
```bash
python -c "
import sqlite3, json
conn = sqlite3.connect('volusia.db')
conn.row_factory = sqlite3.Row
cur = conn.execute('SELECT * FROM indicators ORDER BY category, name')
data = [dict(r) for r in cur.fetchall()]
with open('../data/indicators.json', 'w') as f:
    json.dump(data, f, indent=2)
"
```

---

**Last Updated**: 2026-09-07
**Maintainer**: ZQM Labs / ZQM Computing
