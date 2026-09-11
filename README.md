# volusia-zqmlabs

Backend data pipeline for [volusia.zqmlabs.com](https://volusia.zqmlabs.com) — the Project Volusia public data portal.

---

## Domain-to-Repo Mapping

| Domain | Repo | Branch | Purpose |
|--------|------|--------|---------|
| volusia.zqmlabs.com | `ZQM-Labs/volusia-zqmlabs` | `main` | Backend data pipeline |
| api.zqmlabs.com | `ZQM-Labs/volusia-zqmlabs` | `main` | Backend API (shared with zqmlabs.com) |

---

## Modular Architecture Context

volusia-zqmlabs is the **backend data layer** of the ZQM modular architecture. It provides:
- 50 indicators across 11 categories
- Data refresh pipeline
- Shared data with zqmlabs-backend

## Repo Map

```
volusia-zqmlabs <-> zqmlabs-backend (data sharing)
volusia-zqmlabs <-> zqmlabs-frontend (via zqmlabs-backend proxy)
zqmlabs-frontend -> volusia.zqmlabs.com (direct)
```

## Development

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /health` — Health check
- `GET /latest` — Latest indicator data
- `GET /data/indicators.json` — All 50 indicators
- `GET /refresh?_secret=...` — Manual data refresh

## Data

50 indicators across 11 categories:
- Economic, Tourism, Demographics, Infrastructure, Environment,
- Education, Healthcare, Housing, Safety, Governance, Quality of Life

## Cross-References

- **zqmlabs-backend** — Serves zqmlabs.com API (separate repo)
- **zqmlabs-frontend** — React SPA for zqmlabs.com (separate repo)
- **zqmlabs-gamification** — Gamification service (separate repo)
