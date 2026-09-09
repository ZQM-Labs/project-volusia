# Quick Reference — Project Volusia

> Quick reference card for common operations.

---

## Essential Commands

### Backend
```bash
# Start portal
cd Tools/volusia_data
python portal_app.py

# Refresh data
python refresh_v2.py

# Check database
sqlite3 volusia.db "SELECT COUNT(*) FROM indicators;"
sqlite3 volusia.db "SELECT DISTINCT category FROM indicators;"

# Export JSON
python -c "
import sqlite3, json
conn = sqlite3.connect('volusia.db')
conn.row_factory = sqlite3.Row
cur = conn.execute('SELECT * FROM indicators')
with open('data/indicators.json', 'w') as f:
    json.dump([dict(r) for r in cur.fetchall()], f, indent=2)
"
```

### Frontend
```bash
# Install
npm install

# Develop
npm run dev          # http://localhost:5173

# Build
npm run build        # dist/

# Preview
npm run preview      # http://localhost:4173

# Type check
npm run lint         # tsc --noEmit
```

### Git
```bash
# Commit
git add -A
git commit -m "description"
git push origin main

# Pull with rebase
git pull --rebase origin main

# Create branch
git checkout -b feature/name
```

---

## Ports & URLs

| Service | Port | URL |
|---------|------|-----|
| Backend Portal | 8789 | http://localhost:8789 |
| Backend API | 8790 | http://localhost:8790 |
| Frontend Dev | 5173 | http://localhost:5173 |
| Frontend Preview | 4173 | http://localhost:4173 |
| Live Portal | 443 | https://volusia.zqmlabs.com |
| Live API | 443 | https://volusia.zqmlabs.com/api |

---

## File Locations

| File | Path |
|------|------|
| Backend Portal | `Tools/volusia_data/portal_app.py` |
| Backend API | `Tools/volusia_data/portal_app.py` |
| Data Pipeline | `Tools/volusia_data/refresh_v2.py` |
| Database | `Tools/volusia_data/volusia.db` |
| Config | `Tools/volusia_data/config.py` |
| Frontend App | `src/App.tsx` |
| Frontend Hooks | `src/hooks/useApi.ts` |
| Frontend Pages | `src/pages/*.tsx` |
| Data Files | `data/*.json` |
| Build Output | `dist/` |

---

## Common SQL Queries

```sql
-- Count all indicators
SELECT COUNT(*) FROM indicators;

-- Count by category
SELECT category, COUNT(*) FROM indicators GROUP BY category;

-- Get latest indicators
SELECT name, value, unit, fetched_at 
FROM indicators 
ORDER BY fetched_at DESC 
LIMIT 10;

-- Find stale data (> 30 days)
SELECT name, fetched_at 
FROM indicators 
WHERE fetched_at < datetime('now', '-30 days');

-- Audit log
SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 20;

-- Map layers count
SELECT category, COUNT(*) FROM map_layers GROUP BY category;

-- CVB hotel data
SELECT * FROM cvb_hotels ORDER BY year DESC, month DESC LIMIT 12;
```

---

## Common API Calls

```bash
# Health check
curl http://localhost:8790/api/health

# All indicators
curl http://localhost:8790/api/indicators

# Filter by category
curl "http://localhost:8790/api/indicators?category=Economic"

# Single indicator
curl http://localhost:8790/api/indicators/unemployment_rate_bls

# Datasets
curl http://localhost:8790/api/datasets

# Map layers
curl http://localhost:8790/api/map-layers

# Download CSV
curl http://localhost:8790/api/indicators.csv -o indicators.csv

# Trigger refresh
curl -X POST http://localhost:8790/api/refresh
```

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Port already in use | `netstat -ano \| findstr :8789` then `taskkill /PID <pid> /F` |
| Database locked | Close other connections, restart portal |
| Build fails | `npm run lint` to check TypeScript errors |
| Data stale | Run `python refresh_v2.py` |
| GitHub Pages 404 | Check `gh-pages` branch has `dist/` contents |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VOLUSIA_DB_PATH` | `Tools/volusia_data/volusia.db` | Database path |
| `VOLUSIA_PORT` | `8789` | Portal port |
| `VOLUSIA_HOST` | `0.0.0.0` | Portal host |
| `CENSUS_API_KEY` | (empty) | Census API key |
| `BLS_API_KEY` | (empty) | BLS API key |
| `BEA_API_KEY` | (empty) | BEA API key |

---

## Dependencies

### Backend
```
fastapi>=0.115
uvicorn>=0.30
matplotlib>=3.8
requests>=2.31
```

### Frontend
```
react>=18.3
react-dom>=18.3
react-router-dom>=6.27
vite>=5.4
typescript>=5.6
tailwindcss>=3.4
@nivo/core>=0.87
@nivo/line>=0.87
@nivo/bar>=0.87
@nivo/pie>=0.87
@nivo/geo>=0.87
leaflet>=1.9
react-leaflet>=4.2
axios>=1.7
date-fns>=4.1
```

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
