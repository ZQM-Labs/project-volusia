# Research Techniques for Project Volusia

> Effective methods for finding, validating, and documenting data sources.

---

## 1. Source Discovery Techniques

### 1.1 Government Portal Mining

**Technique**: Systematically search agency websites for relevant datasets.

```
Agency → Data Portal → Search/Filter → Download/API
```

**Top Portals**:
- data.census.gov — Demographics, economics
- data.bls.gov — Employment, wages, inflation
- epa.gov/environmental-data — Air, water, land
- noaa.gov/data — Climate, weather, oceans
- usgs.gov/data — Water, geology, biology
- fema.gov/data — Flood zones, disasters

**Example**:
```
1. Go to data.census.gov
2. Search "Volusia County Florida"
3. Filter by topic (e.g., "Demographics")
4. Select table (e.g., DP05)
5. Download CSV or use API
```

### 1.2 API-First Research

**Technique**: Use agency APIs for programmatic access.

**Key APIs**:
| Agency | API Endpoint | Documentation |
|--------|-------------|---------------|
| Census | api.census.gov/data/2024/acs/acs5 | census.gov/data/developers |
| BLS | data.bls.gov/timeseries/ | bls.gov/developers |
| FRED | api.stlouisfed.org/fred/ |fred.stlouisfed.org/docs/api |
| EPA | epa.gov/enviro/echo | epa.gov/enviro/echo-api |
| NOAA | ncei.noaa.gov/access/services | ncei.noaa.gov/access |

**Example**:
```python
import requests

# Census ACS API
url = "https://api.census.gov/data/2024/acs/acs5"
params = {
    "get": "NAME,DP05_0001E",
    "for": "county:127",
    "in": "state:12"
}
r = requests.get(url, params=params)
data = r.json()
```

### 1.3 Academic Database Search

**Technique**: Search university research databases.

**Databases**:
- Google Scholar
- JSTOR
- SSRN
- ResearchGate
- University institutional repositories

**Search Terms**:
```
"Volusia County" AND (data OR statistics OR demographics)
"Volusia County" AND (economy OR employment OR housing)
"Volusia County" AND (health OR environment OR climate)
```

---

## 2. Source Validation Techniques

### 2.1 Authority Verification

**Technique**: Confirm source authority before using.

**Checklist**:
- [ ] Is the source a government agency (.gov)?
- [ ] Is it an academic institution (.edu)?
- [ ] Is it a reputable organization (.org)?
- [ ] Is the data peer-reviewed or official?
- [ ] Is the source cited elsewhere?

**Red Flags**:
- Anonymous or unverifiable sources
- Commercial sites with no attribution
- Outdated or abandoned websites
- Data without clear methodology

### 2.2 Freshness Verification

**Technique**: Check data vintage and update frequency.

**Acceptable Age by Source**:
| Source Type | Maximum Age |
|-------------|-------------|
| Census ACS | 1-2 years |
| Census PEP | 1 year |
| BLS QCEW | 1 quarter |
| BLS LAUS | 1 month |
| NOAA Climate | 1 year |
| EPA Water | 2 years |
| CDC Health | 1-2 years |
| Real Estate | 1-3 months |

### 2.3 Cross-Reference Validation

**Technique**: Compare multiple sources for same indicator.

**Process**:
```
1. Identify indicator (e.g., total population)
2. Find 2+ independent sources
3. Compare values
4. Calculate difference percentage
5. Flag if difference >5%
6. Investigate discrepancies
```

**Example**:
```
Census PEP 2024: 601,107
Census ACS 2024: 606,573
Difference: 0.9% — acceptable

If difference >5%, investigate:
- Different methodologies
- Different time periods
- Different geographic boundaries
```

### 2.4 Range Validation

**Technique**: Verify values are within expected bounds.

**Common Ranges**:
| Indicator | Min | Max |
|-----------|-----|-----|
| Population (Volusia) | 500,000 | 700,000 |
| Unemployment rate | 0% | 25% |
| Poverty rate | 0% | 30% |
| Median age | 20 | 70 |
| Median home value | $100,000 | $500,000 |
| Temperature (°F) | 30 | 100 |

---

## 3. Documentation Techniques

### 3.1 Provenance Documentation

**Technique**: Record full data lineage.

**Required Fields**:
```
- Source name
- Source URL (specific page)
- Source agency
- Vintage (year or date range)
- Fetch timestamp
- Methodology notes
- Transformation steps
```

### 3.2 Metadata Standards

**Technique**: Use consistent metadata format.

**Template**:
```json
{
  "name": "total_population_pep_2024",
  "value": "601107",
  "unit": "people",
  "category": "Demographics",
  "source": "Census PEP",
  "source_url": "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv",
  "vintage": "2024",
  "description": "Total population 2024 from Census Population Estimates Program"
}
```

### 3.3 Quality Scoring

**Technique**: Score each indicator by quality.

**Scoring Matrix**:
| Criterion | Weight | Score |
|-----------|--------|-------|
| Source authority | 30% | 0-100 |
| URL specificity | 20% | 0-100 |
| Vintage freshness | 20% | 0-100 |
| Value validity | 15% | 0-100 |
| Description quality | 15% | 0-100 |

**Formula**:
```
Quality = (Authority × 0.30) + (URL × 0.20) + (Freshness × 0.20) + (Validity × 0.15) + (Description × 0.15)
```

---

## 4. Analytical Techniques

### 4.1 Trend Analysis

**Technique**: Analyze time series data for patterns.

**Steps**:
```
1. Collect historical values
2. Plot time series
3. Calculate growth rates
4. Identify trends
5. Detect anomalies
6. Forecast future values
```

### 4.2 Correlation Analysis

**Technique**: Find relationships between indicators.

**Process**:
```
1. Select two indicators (e.g., unemployment vs poverty)
2. Collect paired observations
3. Calculate correlation coefficient
4. Test for significance
5. Document findings
```

### 4.3 Gap Analysis

**Technique**: Identify missing data.

**Process**:
```
1. List all expected indicators by category
2. Check which are present in database
3. Identify gaps
4. Prioritize by importance
5. Plan research to fill gaps
```

---

## 5. Automation Techniques

### 5.1 Scheduled Refresh

**Technique**: Automate data updates.

**Cron Schedule**:
```
# Daily refresh
0 6 * * * python Tools/volusia_data/refresh_v2.py

# Weekly report generation
0 8 * * 1 python Tools/volusia_data/reports/generate_weekly.py

# Monthly quality audit
0 9 1 * * python Tools/volusia_data/quality/validate.py
```

### 5.2 Staleness Monitoring

**Technique**: Alert when data is stale.

**Thresholds**:
```
Census ACS: >365 days
BLS LAUS: >45 days
NOAA Climate: >2 years
EPA Water: >2 years
```

### 5.3 Webhook Integration

**Technique**: Notify on data changes.

**Setup**:
```
1. Configure webhook endpoint
2. Monitor data sources for updates
3. Trigger refresh on change
4. Notify maintainers
```

---

## 6. Source-Specific Techniques

### 6.1 Census Bureau

**API Pattern**:
```
https://api.census.gov/data/{year}/{dataset}?get={variables}&for={geography}
```

**Example**:
```
https://api.census.gov/data/2024/acs/acs5?get=NAME,DP05_0001E&for=county:127&in=state:12
```

### 6.2 BLS QCEW

**CSV Pattern**:
```
https://data.bls.gov/cew/data/api/{year}/{quarter}/area/{area_code}.csv
```

**Example**:
```
https://data.bls.gov/cew/data/api/2024/1/area/12127.csv
```

### 6.3 NOAA NCEI

**API Pattern**:
```
https://www.ncei.noaa.gov/access/services/data/v1?dataset={dataset}&dataTypes={types}&stations={stations}&startDate={start}&endDate={end}&format=json
```

### 6.4 EPA ECHO

**API Pattern**:
```
https://enviro.epa.gov/enviro/efservice/{table}/ROWS/{start}:{end}/JSON
```

---

## 7. Quality Assurance

### 7.1 Automated Checks

**Pre-commit checks**:
```
1. URL format validation
2. Value range validation
3. Duplicate name check
4. Category validation
5. Vintage format check
```

### 7.2 Manual Review

**Review checklist**:
```
1. Source authority confirmed
2. URL leads to actual data
3. Vintage is current
4. Value makes sense
5. Description is informative
6. Category is appropriate
```

### 7.3 Continuous Monitoring

**Dashboard metrics**:
```
- Total indicators: 435
- High-trust sources: 193 (51.5%)
- Data freshness: 95% within thresholds
- Quality score: 100%
```

---

*Last updated: 2026-09-06*
