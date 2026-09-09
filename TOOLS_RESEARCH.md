# Tools Research — Project Volusia Expansion

> Research on tools and services that can help expand Project Volusia.

---

## Priority Matrix

| Priority | Tool | Category | Impact | Effort | Cost |
|----------|------|----------|--------|--------|------|
| 🔴 High | FRED API | Data Source | High | Low | Free |
| 🔴 High | TanStack Query | Frontend | High | Low | Free |
| 🔴 High | Uptime Kuma | Monitoring | High | Low | Free |
| 🟡 Medium | Metabase | Visualization | Medium | Medium | Free |
| 🟡 Medium | Prefect | Pipeline | Medium | Medium | Free |
| 🟡 Medium | Docusaurus | Docs | Medium | Medium | Free |
| 🟢 Low | Kepler.gl | Maps | Low | High | Free |
| 🟢 Low | Hasura | Backend | Low | High | Free |

---

## 🔴 HIGH PRIORITY

### 1. FRED API (Federal Reserve Economic Data)

| Field | Value |
|-------|-------|
| **URL** | https://fred.stlouisfed.org/docs/api/fred/ |
| **Description** | Economic time series data from the Federal Reserve |
| **Use Case** | Interest rates, GDP, inflation, employment, monetary data |
| **License** | Public Domain (free key required) |
| **Integration** | REST API, Python (`fredapi` library) |

**Why**: Adds 800,000+ economic time series indicators. Perfect for the Economic category.

**Implementation**:
```python
# Install
pip install fredapi

# Usage
from fredapi import Fred
fred = Fred(api_key='YOUR_KEY')
data =fred.get_series('UNRATE')  # Unemployment rate
```

**Key Series for Volusia**:
- `UNRATE` — Unemployment rate
- `GDP` — Gross Domestic Product
- `CPIAUCSL` — Consumer Price Index
- `FEDFUNDS` — Federal Funds Rate
- `MORTGAGE30US` — 30-Year Mortgage Rate

---

### 2. TanStack Query (React Query)

| Field | Value |
|-------|-------|
| **URL** | https://tanstack.com/query |
| **Description** | Powerful data fetching and caching for React |
| **Use Case** | API calls, caching, background updates, optimistic updates |
| **License** | MIT |
| **Integration** | React, Vue, Solid, Svelte |

**Why**: Dramatically improves data loading performance and user experience.

**Implementation**:
```bash
npm install @tanstack/react-query
```

```tsx
import { useQuery } from '@tanstack/react-query'

function useIndicators() {
  return useQuery({
    queryKey: ['indicators'],
    queryFn: () => fetch('/data/indicators.json').then(r => r.json()),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}
```

---

### 3. Uptime Kuma

| Field | Value |
|-------|-------|
| **URL** | https://github.com/louislam/uptime-kuma |
| **Description** | Self-hosted monitoring tool |
| **Use Case** | Uptime monitoring, alerts, status page |
| **License** | MIT |
| **Integration** | HTTP, TCP, Ping, DNS |

**Why**: Monitor backend API, frontend, and data pipeline health.

**Implementation**:
```bash
docker run -d --restart=always -p 3001:3001 -v uptime-kuma:/app/data --name uptime-kuma louislam/uptime-kuma:1
```

---

## 🟡 MEDIUM PRIORITY

### 4. Metabase

| Field | Value |
|-------|-------|
| **URL** | https://www.metabase.com/ |
| **Description** | Simple, open-source analytics tool |
| **Use Case** | Self-serve analytics, dashboards, alerts |
| **License** | AGPL (open source) |
| **Integration** | SQLite, PostgreSQL, MySQL, etc. |

**Why**: Non-technical users can create their own charts and dashboards.

**Implementation**:
```bash
docker run -d -p 3000:3000 --name metabase metabase/metabase
```

---

### 5. Prefect

| Field | Value |
|-------|-------|
| **URL** | https://www.prefect.io/ |
| **Description** | Modern workflow orchestration for data pipelines |
| **Use Case** | ETL, data ingestion, monitoring |
| **License** | Apache 2.0 |
| **Integration** | Python, REST API |

**Why**: Replace cron-based refresh with proper workflow orchestration.

**Implementation**:
```bash
pip install prefect
```

```python
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(cache_key_fn=task_input_key, cache_expiration=timedelta(hours=1))
def fetch_census_pep():
    # Fetch data
    pass

@flow
def refresh_pipeline():
    fetch_census_pep()
    # ... other tasks
```

---

### 6. Docusaurus

| Field | Value |
|-------|-------|
| **URL** | https://docusaurus.io/ |
| **Description** | Static site generator for documentation |
| **Use Case** | Docs, blogs, versioning, search |
| **License** | MIT |
| **Integration** | React, Markdown, MDX |

**Why**: Professional documentation site with search, versioning, and blog.

**Implementation**:
```bash
npx create-docusaurus@latest docs classic
cd docs
npm start
```

---

## 🟢 LOW PRIORITY (Future)

### 7. Kepler.gl

| Field | Value |
|-------|-------|
| **URL** | https://kepler.gl/ |
| **Description** | Open-source geospatial analysis tool |
| **Use Case** | Large-scale geospatial data visualization |
| **License** | MIT |
| **integration** | React, Mapbox, deck.gl |

**Why**: Advanced geospatial visualizations beyond Leaflet.

---

### 8. Hasura

| Field | Value |
|-------|-------|
| **URL** | https://hasura.io/ |
| **Description** | Instant GraphQL API for PostgreSQL |
| **Use Case** | Real-time GraphQL, permissions |
| **License** | Apache 2.0 (open source) |
| **Integration** | PostgreSQL, REST, GraphQL |

**Why**: Auto-generated GraphQL API from database schema.

---

## Additional Data Sources

### Government APIs

| Source | URL | Data | Status |
|--------|-----|------|--------|
| Census Bureau | https://www.census.gov/data/developers.html | Population, demographics | ✅ Integrated |
| BLS | https://www.bls.gov/developers/ | Employment, wages | ⚠️ Needs key |
| BEA | https://apps.bea.gov/API/signup/index.cfm | Income, GDP | ⚠️ Needs key |
| NOAA | https://www.ncdc.noaa.gov/cdo-web/webservices/v2 | Weather, climate | ✅ Integrated |
| FRED | https://fred.stlouisfed.org/docs/api/fred/ | Economic time series | 🔲 Not integrated |
| Data.gov | https://data.gov/ | Federal datasets | 🔲 Not integrated |
| Socrata | https://dev.socrata.com/ | Government datasets | 🔲 Not integrated |

### Commercial APIs (Free Tiers)

| Source | URL | Data | Free Tier |
|--------|-----|------|-----------|
| OpenWeatherMap | https://openweathermap.org/api | Weather | 1,000 calls/day |
| Zillow | https://www.zillow.com/howto/api/APIOverview.htm | Housing | Limited |
| Realtor.com | https://rapidapi.com/apidojo/api/realtor | Real estate | 500 calls/month |
| Walk Score | https://www.walkscore.com/professional/api.php | Walkability | Limited |
| GreatSchools | https://www.greatschools.org/api/ | School ratings | Limited |

---

## Deployment Options

| Platform | Best For | Free Tier | Notes |
|----------|----------|-----------|-------|
| GitHub Pages | Static frontend | ✅ Unlimited | Current choice |
| Vercel | Next.js frontend | ✅ 100GB bandwidth | Better performance |
| Netlify | Static sites | ✅ 100GB bandwidth | Forms, identity |
| Cloudflare Pages | Global CDN | ✅ Unlimited | Workers, R2 |
| Railway | Full-stack apps | ✅ $5 credit/month | PostgreSQL, cron |
| Fly.io | Global deployment | ✅ 3 VMs | Docker, PostgreSQL |
| Render | Web services | ✅ 750 hours/month | PostgreSQL, cron |

---

## Monitoring Stack

| Tool | Purpose | Self-Hosted |
|------|---------|-------------|
| Uptime Kuma | Uptime monitoring | ✅ |
| Netdata | System metrics | ✅ |
| Plausible | Web analytics | ✅ |
| GoatCounter | Privacy analytics | ✅ |
| Sentry | Error tracking | ✅ (limited free) |

---

## Recommended Next Steps

1. **Get FRED API key** — Add economic time series data
2. **Add TanStack Query** — Improve frontend data loading
3. **Deploy Uptime Kuma** — Monitor backend health
4. **Add Metabase** — Self-serve analytics for users
5. **Migrate to Prefect** — Proper pipeline orchestration
6. **Create Docusaurus docs** — Professional documentation site

---

**Last Updated**: 2026-09-09
**Maintainer**: ZQM Labs / ZQM Computing
