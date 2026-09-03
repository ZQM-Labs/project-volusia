# Public Surface Recon — ZQM Labs / Project Volusia

**Date:** 2026-09-03  
**Scope:** zqmlabs.com, github.com/ZQM-Computing  
**Classification:** Internal — Living Document

---

## 1. DNS & Infrastructure

| Field | Value |
|-------|-------|
| Domain | zqmlabs.com |
| CDN | Cloudflare |
| IPs | 104.21.71.253, 172.67.173.30, 2606:4700:3033::6815:47fd, 2606:4700:3031::ac43:ad1e |
| Server | cloudflare |
| HSTS | max-age=31536000; includeSubDomains; preload |
| Security Headers | X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, Referrer-Policy: strict-origin-when-cross-origin |

---

## 2. Website Architecture (zqmlabs.com)

### Routes
| Path | Type | Description |
|------|------|-------------|
| `/` | Static HTML | Homepage with 6 category cards |
| `/data/` | Static HTML | Data Portal hub (10 categories) |
| `/about/` | Static HTML | Mission & principles |
| `/sitemap.xml` | XML | 13 URLs, all priority 0.7-1.0 |
| `/rss.xml` | RSS | Data updates feed |

### Data Portal Categories (10)
| Category | Sources | Path |
|----------|---------|------|
| Economic | 5 | /data/economic/ |
| Tourism | 4 | /data/tourism/ |
| Real Estate & Housing | 5 | /data/real-estate/ |
| Demographics | 4 | /data/demographics/ |
| Transportation & Infrastructure | 4 | /data/transportation/ |
| Climate & Environment | 4 | /data/climate/ |
| Public Safety | 3 | /data/public-safety/ |
| Health | 3 | /data/health/ |
| Education | 3 | /data/education/ |
| Government Finance | 3 | /data/government-finance/ |

### SEO & Metadata
- Open Graph tags (title, description, image, url)
- Twitter Card (summary_large_image)
- Schema.org JSON-LD (Organization, WebSite, BreadcrumbList)
- Canonical URL, robots, RSS alternate
- Theme color: #0f172a (dark slate)

### Tech
- Static HTML + CSS (no JS framework)
- No client-side rendering detected
- No API endpoints exposed on the domain

---

## 3. GitHub Organization (ZQM-Computing)

### Profile
| Field | Value |
|-------|-------|
| Login | ZQM-Computing |
| Name | ZQM Computing |
| Type | User (not Organization) |
| Bio | Home of Project Volusia — open intelligence for Volusia County, Florida (Q4 2026–2027) |
| Location | Volusia County, Florida (remote) |
| Blog | https://zqm-computing.github.io/ZQM-Computing/ |
| Public Repos | 1 |
| Public Gists | 0 |
| Achievements | Pull Shark (x2), Quickdraw |

### Repository: volusia-portal
| Field | Value |
|-------|-------|
| Full Name | ZQM-Computing/volusia-portal |
| Description | Project Volusia — Public Data Portal & Intelligence Platform for Volusia County, Florida |
| Language | TypeScript |
| Stars | 0 |
| Forks | 0 |
| Created | 2026-09-03T02:27:00Z |
| Updated | 2026-09-03T12:40:11Z |
| Default Branch | master |
| Visibility | Public |
| Fork | No |

### Topics
community-resilience, data-driven, data-portal, florida, leaflet, nivo, open-data, open-source-intelligence, react, research, tailwind, typescript, volusia

### Implied Tech Stack
- React (frontend framework)
- TypeScript (language)
- Tailwind CSS (styling)
- Leaflet (interactive maps)
- Nivo (data visualization / D3-based)
- GitHub Pages (hosting, implied by blog URL)

---

## 4. Gap Analysis — Live vs. Local

| Component | Live (zqmlabs.com / GitHub) | Local (ZQM-GARDEN-03) | Status |
|-----------|----------------------------|----------------------|--------|
| Static website | Yes (HTML/CSS) | No | Live only |
| Data portal backend | No | Yes (portal_app.py) | Local only |
| Data pipeline | No | Yes (refresh_v2.py) | Local only |
| SQLite database | No | Yes (volusia.db, 14 indicators) | Local only |
| GitHub repo | Yes (empty/fresh) | No code pushed | Live only |
| API endpoints | No | Yes (5 endpoints) | Local only |
| Actual data display | No | Yes (via portal_app.py) | Local only |

---

## 5. Critical Gaps to Address

### 5.1 Data Not Public
The live site describes 10 data categories but displays NO actual data. The local pipeline fetches 14 real indicators but they are not accessible via the public site.

### 5.2 GitHub Repo Empty
The volusia-portal repo was created today but contains no code. The local codebase (refresh_v2.py, portal_app.py, config.py, fetchers/) is not version-controlled on GitHub.

### 5.3 No API Exposure
The local portal_app.py serves 5 API endpoints but only on localhost:8789. No public API exists.

### 5.4 Static Site ≠ Data Portal
The live /data/ page is static HTML. Users cannot query, filter, or download data. The "Data Portal" is currently a brochure, not a tool.

### 5.5 No Evidence of Backend
The GitHub repo topics suggest a React/TypeScript frontend, but no backend (Python/FastAPI/SQLite) is visible. The data pipeline we built is entirely local.

---

## 6. Recommended Improvements

### Immediate (Phase 1)
1. **Push local codebase to GitHub** — version control for refresh_v2.py, portal_app.py, fetchers/
2. **Deploy portal to GitHub Pages or Vercel** — make the data portal publicly accessible
3. **Add data export** — CSV/JSON download endpoints for all indicators
4. **Populate GitHub README** — document the project, architecture, and how to run

### Short-term (Phase 2)
5. **Connect static site to API** — replace static /data/ pages with dynamic frontend that calls the API
6. **Add data freshness indicators** — show "last updated" dates on all indicators
7. **Implement automated refresh** — cron job or GitHub Actions to run refresh_v2.py on schedule
8. **Add map visualizations** — Leaflet maps for geographic data (tract-level, property, transit)

### Medium-term (Phase 3)
9. **Custom domain for API** — api.zqmlabs.com or similar
10. **User accounts / saved queries** — let stakeholders save custom dashboards
11. **Alert system** — email/SMS when key indicators change
12. **Quarterly reports** — auto-generated PDF briefings from the data

---

## 7. Honest Limits

- No admin access to zqmlabs.com hosting (Cloudflare + unknown origin)
- No GitHub Actions workflows visible (may be private)
- No CI/CD configuration exposed
- No private repos or project boards visible
- No analytics or traffic data available

---

**Document owner:** ZQM Labs / Project Volusia  
**Next review:** 2026-12-02
