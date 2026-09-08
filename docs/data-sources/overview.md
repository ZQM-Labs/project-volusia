# Data Sources — Project Volusia

> Documentation for all data sources used by Project Volusia.

---

## Overview

Project Volusia aggregates data from 8 authoritative sources across 4 categories:

| Category | Count | Sources |
|----------|-------|---------|
| Economic | 13 | BLS LAUS, BLS QCEW, BEA Regional, C2ER |
| Demographics | 8 | Census PEP, Census ACS DP05 |
| Climate | 6 | NOAA NCEI |
| Tourism | 3 | Volusia County CVB |

---

## Source Details

### US Census Bureau — Population Estimates Program (PEP)

| Field | Value |
|-------|-------|
| **URL** | https://www.census.gov/programs-surveys/pest.html |
| **API** | CSV download (no key required) |
| **Update Frequency** | Annual |
| **License** | Public Domain |
| **Indicators** | `total_population_pep_2022`, `total_population_pep_2023`, `total_population_pep_2024` |

**Data URL**: https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/totals/co-est2024-alldata.csv

---

### US Census Bureau — American Community Survey (ACS)

| Field | Value |
|-------|-------|
| **URL** | https://data.census.gov |
| **API** | data.census.gov API (key optional) |
| **Update Frequency** | Annual (5-year estimates) |
| **License** | Public Domain |
| **Tables** | DP03 (Economic), DP05 (Demographic) |

**Indicators**:
- `median_household_income_acs` — Median household income
- `unemployment_rate_acs` — Unemployment rate
- `poverty_rate_acs` — Poverty rate
- `per_capita_income_acs` — Per capita income
- `median_age_acs` — Median age
- `total_population_acs` — Total population

---

### Bureau of Labor Statistics — LAUS

| Field | Value |
|-------|-------|
| **URL** | https://www.bls.gov/lau/ |
| **API** | BLS Public Data API v2 |
| **Update Frequency** | Monthly |
| **License** | Public Domain |
| **Series ID** | LAUCN12127000000003 |

**Indicators**:
- `unemployment_rate_bls` — Unemployment rate

---

### Bureau of Labor Statistics — QCEW

| Field | Value |
|-------|-------|
| **URL** | https://www.bls.gov/cew/ |
| **API** | BLS QCEW API |
| **Update Frequency** | Quarterly |
| **License** | Public Domain |

**Indicators**:
- `establishments_qcew` — Number of establishments
- `employment_qcew` — Total employment
- `avg_weekly_wage_qcew` — Average weekly wage

---

### Bureau of Economic Analysis — Regional

| Field | Value |
|-------|-------|
| **URL** | https://www.bea.gov/data/income-saving/local-area-personal-income |
| **API** | BEA API (key required for production) |
| **Update Frequency** | Annual |
| **License** | Public Domain |

**Indicators**:
- `per_capita_income_bea` — Per capita personal income
- `personal_income_total` — Total personal income
- `population_bea` — Population (BEA)

---

### NOAA National Centers for Environmental Information

| Field | Value |
|-------|-------|
| **URL** | https://www.ncei.noaa.gov/ |
| **API** | NCEI API v1 |
| **Update Frequency** | Daily |
| **License** | Public Domain |
| **Station** | USW00012838 (Daytona Beach) |

**Indicators**:
- `avg_max_temp` — Average maximum temperature
- `avg_min_temp` — Average minimum temperature
- `total_precip` — Total precipitation

---

### C2ER — Cost of Living Index

| Field | Value |
|-------|-------|
| **URL** | https://www.c2er.org/ |
| **API** | CSV download (currently broken, using cached) |
| **Update Frequency** | Quarterly |
| **License** | Licensed |

**Indicators**:
- `col_overall_index` — Overall cost of living index
- `cost_of_living_index` — Housing cost index

---

### Volusia County Convention & Visitors Bureau

| Field | Value |
|-------|-------|
| **URL** | https://www.daytonabeach.com/ |
| **API** | PDF parsing (manual) |
| **Update Frequency** | Monthly |
| **License** | Public Record |

**Indicators**:
- `hotel_occupancy_pct` — Hotel occupancy rate
- `avg_daily_rate` — Average daily rate (ADR)
- `revpar` — Revenue per available room

---

## Adding New Data Sources

See [Adding Sources](adding-sources.md) for instructions on how to add new data sources.

---

## Data Quality

All data goes through quality checks:

1. **Validation** — Values checked against known ranges
2. **Deduplication** — Duplicate entries removed
3. **Null Handling** — Census null markers filtered out
4. **Audit Trail** — All fetches logged to `audit_log` table

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
