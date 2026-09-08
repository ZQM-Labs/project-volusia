# Database Schema — Project Volusia

> SQLite database schema documentation.

---

## Database Location

| Environment | Path |
|-------------|------|
| Backend | `Tools/volusia_data/volusia.db` |
| Frontend | `data/` (JSON exports) |

---

## Tables

### indicators

Main table storing all economic, demographic, climate, and tourism indicators.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment primary key |
| name | TEXT UNIQUE | Unique indicator name |
| value | TEXT | Indicator value (stored as text) |
| unit | TEXT | Unit of measurement |
| category | TEXT | Category (Economic, Demographics, Climate, Tourism) |
| source | TEXT | Data source name |
| source_url | TEXT | Source URL |
| vintage | TEXT | Year or date range |
| fetched_at | TEXT | ISO timestamp of last fetch |
| description | TEXT | Human-readable description |

**Indexes**:
- `name` — UNIQUE index for fast lookups
- `category` — Index for category filtering

**Sample Data**:
```sql
SELECT * FROM indicators WHERE category = 'Economic' LIMIT 3;
```

| id | name | value | unit | category | source | vintage |
|----|------|-------|------|----------|--------|---------|
| 1 | unemployment_rate_bls | 5.3 | percent | Economic | BLS LAUS | 2026 July |
| 2 | median_household_income_acs | 66581 | dollars | Economic | Census ACS | 2023 |
| 3 | employment_qcew | 189265 | employees | Economic | BLS QCEW | 2024 |

---

### map_layers

Stores geographic data layers for the interactive map.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment primary key |
| name | TEXT | Layer name |
| category | TEXT | Layer category |
| description | TEXT | Layer description |
| source | TEXT | Data source |
| format | TEXT | GeoJSON, shapefile, etc. |
| url | TEXT | URL to fetch layer data |
| geometry | TEXT | GeoJSON geometry (optional) |

**Categories**:
- `boundary` — County boundaries, city limits
- `economic` — Business density, income by tract
- `infrastructure` — Roads, transit, schools
- `environment` — Flood zones, wetlands, conservation
- `demographic` — Population density, age distribution
- `cultural` — Historic districts, cultural sites

---

### cvb_hotels

Stores hotel occupancy data from Volusia County CVB.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment primary key |
| month_year | TEXT | Month and year (e.g., "January 2024") |
| year | INTEGER | Year |
| month | INTEGER | Month (1-12) |
| occ_current REAL | Occupancy rate (current year) |
| adr_current REAL | Average daily rate (current year) |
| revpar_current REAL | Revenue per available room (current year) |
| cdt_current REAL | Consumer demand tracker (current year) |
| source_file TEXT | Source PDF filename |
| fetched_at TEXT | ISO timestamp of last fetch |

---

### datasets

Stores dataset metadata.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment primary key |
| source | TEXT | Data source name |
| content | TEXT | Dataset content (JSON) |
| fetched_at TEXT | ISO timestamp of last fetch |

---

### audit_log

Tracks all data refresh operations.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment primary key |
| action | TEXT | Action performed |
| details | TEXT | Action details |
| timestamp TEXT | ISO timestamp |

---

## Entity Relationship Diagram

```
┌─────────────────┐     ┌─────────────────┐
│   indicators     │     │   map_layers     │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ name (UNIQUE)   │     │ name            │
│ value           │     │ category        │
│ unit            │     │ description     │
│ category        │     │ source          │
│ source          │     │ format          │
│ source_url      │     │ url             │
│ vintage         │     │ geometry        │
│ fetched_at      │     └─────────────────┘
│ description     │
└─────────────────┘
          │
          │ 1:N
          ▼
┌─────────────────┐     ┌─────────────────┐
│   audit_log      │     │   cvb_hotels     │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ action          │     │ month_year      │
│ details         │     │ year            │
│ timestamp       │     │ month           │
└─────────────────┘     │ occ_current     │
                        │ adr_current     │
                        │ revpar_current  │
                        │ cdt_current     │
                        │ source_file     │
                        │ fetched_at      │
                        └─────────────────┘
```

---

## Backup & Restore

### Backup
```bash
# Backup SQLite database
sqlite3 volusia.db ".backup volusia_backup_$(date +%Y%m%d).db"

# Export to JSON
python -c "
import sqlite3, json
conn = sqlite3.connect('volusia.db')
conn.row_factory = sqlite3.Row
for table in ['indicators', 'map_layers', 'cvb_hotels']:
    cur = conn.execute(f'SELECT * FROM {table}')
    data = [dict(r) for r in cur.fetchall()]
    with open(f'{table}_export.json', 'w') as f:
        json.dump(data, f, indent=2)
"
```

### Restore
```bash
# Restore from backup
sqlite3 volusia.db ".restore volusia_backup_20260908.db"
```

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
