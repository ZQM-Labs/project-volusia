# Data Quality — Project Volusia

> Data quality standards and validation procedures.

---

## Quality Standards

All data in Project Volusia must meet these standards:

1. **Accuracy** — Values match source data exactly
2. **Completeness** — No missing values without documentation
3. **Timeliness** — Data refreshed within published schedule
4. **Consistency** — Same format across all records
5. **Validity** — Values within expected ranges

---

## Validation Pipeline

```
Raw Data → Fetch → Validate → Transform → Store → Verify
```

### Stage 1: Fetch
- HTTP request to source API
- Timeout: 30 seconds
- Retry: 3 attempts with exponential backoff
- Error handling: Log and skip on failure

### Stage 2: Validate
- Check for null markers: `(X)`, `N/A`, `**`, `***`, `null`
- Check for extreme values: < -999999990 or > 999999990
- Check data type: Must be numeric or text
- Check range: Within expected bounds for indicator

### Stage 3: Transform
- Convert units if needed (e.g., tenths to whole numbers)
- Normalize category names
- Add metadata (source, vintage, fetched_at)

### Stage 4: Store
- Insert or update in SQLite
- Use parameterized queries (SQL injection prevention)
- Maintain audit log

### Stage 5: Verify
- Compare count of records before/after
- Check for duplicates
- Validate referential integrity

---

## Quality Checks

### Automated Checks

| Check | Description | Action on Failure |
|-------|-------------|-------------------|
| Null detection | Filter Census null markers | Skip record |
| Range validation | Values within expected bounds | Skip record |
| Duplicate detection | Same name + source + vintage | Keep newest |
| Type validation | Numeric values parseable | Skip record |
| Freshness check | Data not older than expected | Log warning |

### Manual Checks

- Monthly review of audit_log
- Quarterly comparison with source websites
- Annual full data audit

---

## Data Freshness

| Source | Expected Freshness | Warning Threshold |
|--------|-------------------|-------------------|
| Census PEP | Within 1 year | > 13 months |
| Census ACS | Within 2 years | > 25 months |
| BLS LAUS | Within 2 months | > 3 months |
| BLS QCEW | Within 2 quarters | > 3 quarters |
| BEA Regional | Within 1 year | > 13 months |
| NOAA NCEI | Within 2 days | > 7 days |
| C2ER COLI | Within 1 quarter | > 5 months |
| Volusia CVB | Within 2 months | > 3 months |

---

## Handling Missing Data

### Why data might be missing

1. **Source API down** — Government API temporarily unavailable
2. **Data not published** — Source hasn't released new data yet
3. **Quality check failure** — Data didn't pass validation
4. **Network error** — Couldn't reach source API
5. **Parsing error** — Data format changed

### What we do

1. Log the error in `audit_log`
2. Keep previous valid data (don't overwrite with null)
3. Retry on next scheduled refresh
4. Alert maintainers if persistent

---

## Audit Trail

All data operations are logged:

```sql
SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 20;
```

| Column | Description |
|--------|-------------|
| id | Auto-increment ID |
| action | `fetch_pep`, `fetch_bls`, `refresh_start`, etc. |
| details | JSON details about the operation |
| timestamp | ISO 8601 timestamp |

---

## Reporting Issues

If you notice data quality issues:

1. Check the `fetched_at` timestamp
2. Compare with source website
3. Create an issue with:
   - Indicator name
   - Expected value
   - Actual value
   - Source URL

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
