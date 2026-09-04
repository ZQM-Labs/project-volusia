# Project Volusia — Software Integration Sprint Plan

**Sprint Duration:** 2 weeks (10 working days)
**Sprint Goal:** Integrate all subsystems into a cohesive, deployable platform with automated data quality, historical tracking, and stakeholder feedback loops.
**Generated:** 2026-09-04
**Owner:** Alex Zelenski (zqmcomputing@gmail.com)

---

## Sprint Backlog

### P0 — Critical Path (Must Complete)

| ID | Task | Effort | Depends On | Acceptance Criteria |
|----|------|--------|------------|---------------------|
| S-01 | Wire API keys into `.env` and verify all 6 fetchers live | 0.5d | Key registration | `refresh_v2.py` reports 6/6 OK |
| S-02 | Add historical time series table to SQLite schema | 0.5d | — | `time_series` table exists with (indicator, date, value, source) |
| S-03 | Store all fetched values in time_series on every refresh | 0.5d | S-02 | Each fetch appends to time_series, not just upserts latest |
| S-04 | Build data quality validation layer | 1d | S-01 | Range checks, anomaly detection, freshness alerts |
| S-05 | Create end-to-end integration test | 0.5d | S-01, S-04 | Single script runs pipeline + validates DB + tests all endpoints |
| S-06 | Deploy portal behind Caddy/cloudflared (public) | 1d | S-05 | Portal accessible at https://volusia.zqmlabs.com |
| S-07 | Set up automated weekly refresh via cron/Task Scheduler | 0.5d | S-01 | Scheduled task runs refresh_v2.py twice daily |

**P0 Total:** 4.5 days

---

### P1 — High Impact (Should Complete)

| ID | Task | Effort | Depends On | Acceptance Criteria |
|----|------|--------|------------|---------------------|
| S-08 | Build automated report generator (weekly data briefing) | 1d | S-03 | Script generates HTML report from template + current data |
| S-09 | Wire contribution review → data update feedback loop | 1d | S-01 | Approved data_source contributions trigger fetcher updates |
| S-10 | Populate Map/ folder with Volusia choropleth (population, income, employment) | 1d | S-01, S-03 | 3 map HTML files in Map/ folder |
| S-11 | Add data staleness alerting (email/notification) | 0.5d | S-04 | health_check.py sends alert when data > threshold |
| S-12 | Build stakeholder interview tracking system | 1d | — | SQLite table + CLI to log interviews, themes, follow-ups |
| S-13 | Create dashboard summary endpoint (executive briefing) | 0.5d | S-03 | `/api/executive-summary` returns key deltas and trends |

**P1 Total:** 5 days

---

### P2 — Nice to Have (Stretch Goals)

| ID | Task | Effort | Depends On | Acceptance Criteria |
|----|------|--------|------------|---------------------|
| S-14 | Build Streamlit interactive dashboard | 1d | S-03 | `streamlit run viz/dashboard.py` works |
| S-15 | Add correlation analysis tool | 0.5d | S-03 | `analysis/correlation.py` generates correlation matrix |
| S-16 | Build trend analyzer (change-point detection) | 0.5d | S-03 | `analysis/trends.py` identifies significant changes |
| S-17 | Add CSV upload endpoint for bulk data import | 0.5d | S-04 | `POST /api/upload/csv` validates and stores |
| S-18 | Create public data portal v2.0 (searchable, API-driven) | 2d | S-06 | React/Next.js frontend (Phase 2 scope) |

**P2 Total:** 4.5 days (stretch)

---

## Detailed Task Specifications

### S-01: Wire API Keys

**Objective:** All 6 data sources fetch live data.

**Steps:**
1. Verify `Tools/.env` exists with `CENSUS_API_KEY`, `BLS_API_KEY`, `BEA_API_KEY`
2. Run `python Tools/volusia_data/refresh_v2.py`
3. Confirm output shows `OK: Census PEP`, `OK: Census ACS`, `OK: NOAA NCEI`, `OK: BLS LAUS`, `OK: BEA Regional`, `OK: BLS QCEW`
4. Verify `volusia.db` has 13+ indicators

**Blockers:** BLS key may take 1-2 days to activate after registration.

---

### S-02: Historical Time Series Schema

**Objective:** Store every fetched value for trend analysis.

**New table:**
```sql
CREATE TABLE IF NOT EXISTS time_series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_name TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT,
    source TEXT,
    vintage TEXT,
    fetched_at TEXT NOT NULL,
    UNIQUE(indicator_name, vintage, fetched_at)
);
```

**Index:**
```sql
CREATE INDEX idx_ts_indicator_date ON time_series(indicator_name, fetched_at);
```

---

### S-03: Store Historical Values

**Objective:** Every fetch appends to `time_series`, not just upserts `indicators`.

**Changes to `refresh_v2.py`:**
- After each `upsert_indicator()`, also `INSERT INTO time_series`
- Deduplicate on (indicator_name, vintage, fetched_at)
- Enables trend charts, change detection, and historical reports

---

### S-04: Data Quality Validation

**Objective:** Automated validation catches bad data before it reaches the portal.

**New file:** `Tools/volusia_data/quality/validate.py`

**Validation rules:**
- **Range checks:** Population 500k-700k, unemployment 0-25%, temp -10 to 50°C
- **Anomaly detection:** Z-score > 3 triggers warning
- **Freshness checks:** Each source has max age (NOAA: 2 days, BLS LAUS: 45 days, etc.)
- **Cross-source coherence:** PEP vs ACS population within 5% tolerance

**Output:** JSON report with pass/warn/fail per indicator.

---

### S-05: End-to-End Integration Test

**Objective:** Single script verifies the entire system.

**New file:** `tests/test_integration.py`

**Test flow:**
1. Run `refresh_v2.py` (or mock if no network)
2. Verify `volusia.db` has expected indicators
3. Run quality validation
4. Start portal via TestClient
5. Test all 13 endpoints return 200
6. Test contribution submission + status check
7. Test chart endpoints return PNG
8. Test export endpoints return valid CSV/JSON
9. Verify health check passes

**CI:** Add to `tests.yml` workflow.

---

### S-06: Public Deployment

**Objective:** Portal accessible at https://volusia.zqmlabs.com

**Steps:**
1. Configure Caddy reverse proxy on ZQM-Node-4
2. Set up Cloudflared tunnel (per `WEB_FORM_DESIGN.md`)
3. Point `volusia.zqmlabs.com` to tunnel
4. Update portal to bind to `0.0.0.0` (not just `127.0.0.1`)
5. Test HTTPS access from external network
6. Update README with public URL

**Caddy config:**
```
volusia.zqmlabs.com {
    reverse_proxy localhost:8789
}
```

---

### S-07: Automated Refresh

**Objective:** Data stays fresh without manual intervention.

**Steps:**
1. Run `Tools/setup_scheduled_tasks.bat` as Administrator
2. Verify tasks in Task Scheduler:
   - `ProjectVolusia_Refresh` at 06:00 daily
   - `ProjectVolusia_Refresh_PM` at 18:00 daily
3. Test manual run: `schtasks /run /tn "ProjectVolusia_Refresh"`
4. Verify `fetch_log.jsonl` shows new entries

---

### S-08: Automated Report Generator

**Objective:** Weekly HTML report generated from current data.

**New file:** `Tools/volusia_data/reports/generate_weekly.py`

**Report sections:**
1. Executive summary (key deltas vs last week)
2. Population trend (chart embed)
3. Employment overview (chart embed)
4. Climate summary (chart embed)
5. Data freshness status
6. Recent contributions received

**Output:** `Reports/weekly_YYYY-MM-DD.html`

**Schedule:** Run every Monday at 07:00 via Task Scheduler.

---

### S-09: Contribution → Data Feedback Loop

**Objective:** Approved data contributions update the knowledge base.

**New file:** `Tools/volusia_data/contribution/review.py`

**Workflow:**
1. Reviewer approves a `data_source` contribution via PATCH
2. Review script extracts structured data from contribution
3. New fetcher is registered or existing fetcher is triggered
4. Data is validated via quality layer
5. On pass, data is added to `indicators` and `time_series`
6. Contributor receives notification of acceptance

**CLI:**
```
python contribution/review.py --list-pending
python contribution/review.py --approve SUB-DIRECT-20260904120000000000
python contribution/review.py --reject SUB-DIRECT-20260904120000000000 --reason "..."
```

---

### S-10: Map Population

**Objective:** Map/ folder contains 3 interactive choropleth maps.

**Steps:**
1. Download Volusia County census tract GeoJSON from TIGER/Line
2. Join with indicator data
3. Generate maps:
   - `Map/population_density.html` — Population by tract
   - `Map/unemployment_rate.html` — Unemployment by tract (once BLS data available)
   - `Map/median_income.html` — Income by tract (once BEA data available)
4. Update `Map/MAP_CATALOG.md` with descriptions and data sources

**Tool:** `Tools/volusia_data/viz/map.py`

---

### S-11: Data Staleness Alerting

**Objective:** Automatic notification when data exceeds freshness threshold.

**Enhancement to `health_check.py`:**

**Config:**
```python
ALERT_THRESHOLD = {
    "NOAA NCEI": 2,      # days
    "BLS LAUS": 45,
    "BLS QCEW": 120,
    "Census PEP": 365,
    "Census ACS": 365,
    "BEA Regional": 365,
}
```

**Alert channels:**
- Exit code 1 (for cron/Task Scheduler detection)
- Optional: webhook to Discord/Slack
- Optional: email via SMTP (future)

**Schedule:** Run `health_check.py` daily at 08:00.

---

### S-12: Stakeholder Interview Tracking

**Objective:** Systematic tracking of stakeholder interviews and themes.

**New table:**
```sql
CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stakeholder_name TEXT,
    stakeholder_role TEXT,  -- business_owner, resident, tourist, industry_mover
    interview_date TEXT,
    themes TEXT,  -- JSON array of themes
    needs_identified TEXT,  -- JSON array
    data_gaps TEXT,  -- JSON array
    follow_up_required BOOLEAN,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
```

**New file:** `Tools/volusia_data/research/interviews.py`

**CLI:**
```
python research/interviews.py --add --name "Jane Doe" --role business_owner --date 2026-09-15
python research/interviews.py --list
python research/interviews.py --themes --role business_owner
python research/interviews.py --export-csv interviews.csv
```

---

### S-13: Executive Summary Endpoint

**Objective:** Single endpoint returns key metrics and week-over-week deltas.

**New endpoint:** `GET /api/executive-summary`

**Response:**
```json
{
  "generated_at": "2026-09-04T12:00:00Z",
  "period": "2026-08-28 to 2026-09-04",
  "headlines": [
    {"metric": "population", "current": 601107, "previous": 599000, "delta": "+2,107", "trend": "up"},
    {"metric": "unemployment_rate", "current": 5.3, "previous": 5.1, "delta": "+0.2%", "trend": "up"},
    {"metric": "employment", "current": 189265, "previous": 188000, "delta": "+1,265", "trend": "up"}
  ],
  "data_freshness": {"fresh": 8, "stale": 2},
  "recent_contributions": 3,
  "interviews_conducted": 0
}
```

---

## Sprint Schedule

### Week 1 (Days 1-5)

| Day | Focus | Tasks |
|-----|-------|-------|
| 1 | Foundation | S-01 (API keys), S-02 (schema), S-03 (historical storage) |
| 2 | Quality | S-04 (validation layer) |
| 3 | Testing | S-05 (integration test), S-07 (scheduled refresh) |
| 4 | Deployment | S-06 (Caddy/cloudflared setup) |
| 5 | Deployment | S-06 (public access testing), S-08 (report generator) |

### Week 2 (Days 6-10)

| Day | Focus | Tasks |
|-----|-------|-------|
| 6 | Feedback | S-09 (contribution review loop) |
| 7 | Maps | S-10 (choropleth maps) |
| 8 | Research | S-12 (interview tracking), S-11 (staleness alerts) |
| 9 | API | S-13 (executive summary endpoint) |
| 10 | Buffer | Remaining P0/P1 tasks, documentation update |

---

## Definition of Done

- [ ] All 6 data sources fetch live data
- [ ] Historical time series stored for all indicators
- [ ] Data quality validation passes for all sources
- [ ] End-to-end integration test passes in CI
- [ ] Portal accessible at https://volusia.zqmlabs.com
- [ ] Automated refresh running twice daily
- [ ] Weekly report generation working
- [ ] Contribution review loop functional
- [ ] 3 maps in Map/ folder
- [ ] Stakeholder interview tracking operational
- [ ] Executive summary endpoint live
- [ ] Data staleness alerting configured
- [ ] All tests passing (existing + new)
- [ ] README updated with new endpoints and features

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| BLS key activation delay | S-01 blocked | Use cached data; retry daily; escalate to BLS support |
| Cloudflared tunnel issues | S-06 blocked | Fall back to Caddy-only on LAN; document in README |
| GeoJSON data unavailable | S-10 blocked | Use county-level placeholder; add tract data later |
| Scope creep | Sprint overflow | Strict P0/P1 focus; defer P2 to next sprint |
| CI failures from new tests | S-05 blocked | Run locally first; fix before pushing |

---

## Post-Sprint (Next Sprint Candidates)

1. **Public Portal v2.0** — React frontend, searchable, mobile-first
2. **Predictive Models** — ARIMA/Prophet forecasting for economic indicators
3. **Social Media Integration** — Sentiment analysis of Volusia mentions
4. **SMS Gateway** — Twilio integration for contribution intake
5. **Regional Integration** — Orlando, Titusville, Palm Coast data
6. **Developer Portal** — API documentation, SDKs, sandbox

---

**Document owner:** Alex Zelenski / Project Volusia
**Next review:** 2026-09-18 (Sprint mid-point)
**Sprint end:** 2026-09-18
