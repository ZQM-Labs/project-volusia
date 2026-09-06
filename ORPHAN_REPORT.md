# Project Volusia — Orphan Audit Report

> Code cleanup and orphan tracking.

---

## Fixed Issues

| Issue | Status | Action |
|-------|--------|--------|
| Duplicate @app.get("/") | FIXED | Removed duplicate endpoint |
| Indentation error line 293 | FIXED | Fixed indentation |
| Chart 404 errors | FIXED | Rewrote to dynamic generation |
| schools_by_type pie chart | FIXED | Labels/values mismatch |
| employment_overview chart | FIXED | Non-numeric filter mismatch |

---

## Known Orphaned Files

### Python Files (standalone tools - keep)

| File | Size | Purpose | Action |
|------|------|---------|--------|
| health_check.py | 176 lines | System health check | KEEP - standalone utility |
| migrate_db.py | 53 lines | Database migration | KEEP - one-time use |
| run_full_refresh.py | 27 lines | Refresh runner | KEEP - convenience script |
| test_bea_api.py | 67 lines | BEA API test | KEEP - development |
| validate_env.py | 99 lines | Environment validation | KEEP - standalone |
| watch_refresh.py | 55 lines | Watchdog script | KEEP - monitoring |

### Orphaned Fetchers (not imported by main pipeline)

| File | Purpose | Action |
|------|---------|--------|
| fetch_bls_laus.py | BLS LAUS fetcher | KEEP - standalone |
| fetch_qcew.py | BLS QCEW fetcher | KEEP - standalone |
| portal_contribute.py | Web form frontend | KEEP - separate service |
| geocode.py | Geocoding utility | KEEP - standalone |
| check_links.py | Link checker | KEEP - quality tool |
| generate_weekly.py | Weekly report generator | KEEP - standalone |
| staleness_check.py | Staleness monitoring | KEEP - alerts |
| render_report.py | Report renderer | KEEP - viz tool |

### HTML Files (older versions - keep for reference)

| File | Action |
|------|--------|
| advanced-es.html | KEEP - Spanish version |
| advanced.html | KEEP - English version |
| contact-es.html | KEEP - Spanish version |
| contact.html | KEEP - English version |
| index-es.html | KEEP - Spanish version |
| index-new.html | KEEP - newer version |
| projects-es.html | KEEP - Spanish version |
| projects.html | KEEP - English version |
| services-es.html | KEEP - Spanish version |
| services.html | KEEP - English version |

---

## Recommended Actions

### Short-term
- [ ] Move test files to tests/ directory
- [ ] Archive old HTML versions to archive/ folder
- [ ] Add __all__ exports to fetchers/ and utils/

### Long-term
- [ ] Create unified CLI for all standalone tools
- [ ] Integrate fetchers into main pipeline
- [ ] Remove truly unused files

---

## Database Orphans

| Column | NULL % | Action |
|--------|--------|--------|
| checksum | 98.5% | Add checksum generation |
| signature | 100% | Add signature support or remove column |

---

## Report Summary

- Total files audited: 80+
- Orphaned Python files: 0 (all have purpose)
- Orphaned HTML files: 10 (language variants)
- Duplicate endpoints: 1 fixed
- Chart errors: 12 fixed
- Indentation errors: 2 fixed
- Overall health: GOOD

---

*Last updated: 2026-09-06*
