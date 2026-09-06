# Contributing to Project Volusia

> Open intelligence for Volusia County, FL. Contributions welcome from humans and AI agents.

---

## Table of Contents

1. [How to Contribute](#how-to-contribute)
2. [Contribution Types](#contribution-types)
3. [Research Methodology](#research-methodology)
4. [Data Quality Standards](#data-quality-standards)
5. [Submission Templates](#submission-templates)
6. [Review Process](#review-process)
7. [API Reference](#api-reference)

---

## How to Contribute

### Humans

1. **Web Form**: Visit `https://zqmlabs.com/contribute/`
2. **GitHub Issue**: Open an issue with label `contribution`
3. **Email**: zqmcomputing@gmail.com

### AI Agents

```bash
curl -X POST https://zqmlabs.com/api/v1/contributions \
  -H "Content-Type: application/json" \
  -d '{
    "contribution_type": "data_source",
    "content": {
      "title": "New Census Data Source",
      "description": "Census ACS 5-year estimates for Volusia County",
      "source_url": "https://data.census.gov/table/ACSDP5Y2024.DP05",
      "category": "Demographics",
      "vintage": "2024"
    }
  }'
```

---

## Contribution Types

| Type | Description | Reviewer |
|------|-------------|----------|
| `data_source` | New data source or dataset | Node-3 (Data Pipeline) |
| `analysis` | Analytical insight or report | Node-2 (Analysis) |
| `tool` | Software tool or script | Node-5 (Tool Test) |
| `map` | GIS layer or map | Node-1 (GIS) |
| `report` | Written report or brief | Report Lead |
| `community` | Community knowledge or feedback | Community Liaison |
| `social_media` | Social media content | Community Liaison |
| `educational` | Educational material | Community Liaison |
| `direct` | Direct message or suggestion | Community Liaison |

---

## Research Methodology

### Source Hierarchy

Project Volusia uses a three-tier source hierarchy:

#### Tier 1 — Primary Sources (Highest Trust)

Government agencies and official data portals:

| Agency | Domain | Data Type |
|--------|--------|-----------|
| Census Bureau | census.gov | Demographics, economics |
| BLS | bls.gov | Employment, wages |
| BEA | bea.gov | GDP, income |
| NOAA | noaa.gov | Climate, weather |
| EPA | epa.gov | Environment, water |
| USGS | usgs.gov | Water, terrain |
| FEMA | fema.gov | Flood zones |
| HUD | hud.gov | Housing |
| USDA | usda.gov | Agriculture |
| CDC | cdc.gov | Health |
| FDLE | fdle.state.fl.us | Crime |
| FL DOE | fldoe.org | Education |
| Volusia County | volusia.org | Local government |

#### Tier 2 — Secondary Sources (Verified)

Academic institutions and reputable organizations:

| Source | Domain | Use Case |
|--------|--------|----------|
| Universities | .edu | Research, forecasts |
| FRED | fred.stlouisfed.org | Economic time series |
| County Health Rankings | countyhealthrankings.org | Health data |
| Zillow | zillow.com | Housing values |
| Realtor.com | realtor.com | Housing market |

#### Tier 3 — Tertiary Sources (Use with Caution)

Commercial and crowd-sourced data:

| Source | Domain | Verification Required |
|--------|--------|----------------------|
| SpotCrime | spotcrime.com | Cross-reference with FDLE |
| CrimeByCounty | crimebycounty.com | Cross-reference with FDLE |
| ZipCheckup | zipcheckup.com | Cross-reference with EPA |

### Research Workflow

```
1. IDENTIFY → Find potential data source
2. VERIFY → Confirm source authority and freshness
3. EXTRACT → Pull data via API, download, or scraping
4. VALIDATE → Cross-reference with existing data
5. DOCUMENT → Record source, vintage, methodology
6. SUBMIT → Add to database with full provenance
```

### Source Verification Checklist

- [ ] Source is authoritative (government, academic, or reputable)
- [ ] URL is specific (not just homepage)
- [ ] Data vintage is current (within 2 years for most indicators)
- [ ] Value is within expected range
- [ ] Description is informative (not just timestamp)
- [ ] Category is appropriate
- [ ] Unit of measurement is specified

---

## Data Quality Standards

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| name | string | Unique indicator name |
| value | string | Numeric or text value |
| unit | string | Unit of measurement |
| category | string | One of 15 categories |
| source | string | Originating agency |
| source_url | string | Specific URL to data |
| vintage | string | Year or date range |
| description | string | Human-readable description |

### Validation Rules

```python
# Range validation example
"total_population_pep_2024": {"min": 500000, "max": 700000}
"unemployment_rate_bls": {"min": 0, "max": 25}
"poverty_rate": {"min": 0, "max": 30}

# Freshness validation
"census_acs": 365 days
"bls_laus": 45 days
"noaa_ncei": 2 days
"bls_qcew": 120 days
```

### Quality Scores

| Score | Meaning |
|-------|---------|
| 100 | Perfect — authoritative source, specific URL, current vintage |
| 75-99 | Good — minor issues (root URL, older vintage) |
| 50-74 | Fair — needs improvement |
| <50 | Poor — requires replacement |

---

## Submission Templates

### Data Source Contribution

```json
{
  "contribution_type": "data_source",
  "content": {
    "title": "Census ACS 5-Year DP05 Demographics",
    "description": "Demographic and housing estimates from ACS 5-year 2020-2024",
    "source_url": "https://data.census.gov/table/ACSDP5Y2024.DP05",
    "source_agency": "Census ACS",
    "category": "Demographics",
    "vintage": "2020-2024",
    "indicators": [
      {"name": "median_age", "value": "47.3", "unit": "years"},
      {"name": "total_population", "value": "606573", "unit": "people"}
    ]
  }
}
```

### Analysis Contribution

```json
{
  "contribution_type": "analysis",
  "content": {
    "title": "Volusia Employment Trend Analysis",
    "description": "Quarterly employment trend analysis 2020-2025",
    "methodology": "Time series analysis of BLS QCEW data",
    "findings": "Employment grew 8.2% over 5 years",
    "data_sources": ["bls_qcew_api", "census_cbp"]
  }
}
```

### Tool Contribution

```json
{
  "contribution_type": "tool",
  "content": {
    "title": "Census Data Fetcher",
    "description": "Python script to fetch Census ACS data via API",
    "language": "Python",
    "dependencies": ["requests", "pandas"],
    "repository": "https://github.com/ZQM-Labs/project-volusia"
  }
}
```

---

## Review Process

### Automated Checks

1. **Source validation**: URL format, domain trust
2. **Range validation**: Value within expected bounds
3. **Freshness validation**: Vintage within acceptable window
4. **Duplicate check**: No duplicate indicator names

### Human Review

1. **Triage**: Categorize and prioritize
2. **Verify**: Confirm source authority
3. **Approve/Reject**: Accept or provide feedback
4. **Integrate**: Add to database and update dashboards

### SLA

| Priority | Response Time |
|----------|---------------|
| Critical | 24 hours |
| High | 3 business days |
| Medium | 7 business days |
| Low | 14 business days |

---

## API Reference

### Submit Contribution

```
POST /api/v1/contributions
Content-Type: application/json

{
  "contribution_type": "data_source",
  "content": { ... }
}
```

Response: `201 Created`
```json
{
  "submission_id": "SUB-DATA_SOURCE-20260906082823811456",
  "status": "queued",
  "reviewer": "Node-3 (Data Pipeline)",
  "estimated_review": "3 business days"
}
```

### Check Status

```
GET /api/v1/contributions/{submission_id}
```

### List Contributions

```
GET /api/v1/contributions?status=queued&type=data_source
```

---

## Research Techniques

### Technique 1: Source Discovery

**Method**: Systematic search across government portals

```
1. Identify data need (e.g., "unemployment rate")
2. Search Census, BLS, BEA for relevant datasets
3. Verify API availability or download format
4. Document source URL and vintage
5. Extract and validate data
```

**Example**:
```python
# Fetch Census ACS data
import requests
url = "https://api.census.gov/data/2024/acs/acs5"
params = {"get": "NAME,DP05_0001E", "for": "county:127", "in": "state:12"}
response = requests.get(url, params=params)
```

### Technique 2: Cross-Reference Validation

**Method**: Compare multiple sources for same indicator

```
1. Identify indicator (e.g., "total population")
2. Find 2+ independent sources
3. Compare values and vintages
4. Flag discrepancies >5%
5. Use most authoritative source
```

**Example**:
```
Census PEP 2024: 601,107
Census ACS 2024: 606,573
Difference: 0.9% — acceptable
```

### Technique 3: Trend Analysis

**Method**: Time series analysis for data quality

```
1. Collect historical values for indicator
2. Plot time series
3. Identify anomalies or breaks
4. Investigate causes (methodology changes, etc.)
5. Document findings
```

### Technique 4: Source Authority Scoring

**Method**: Score sources by trustworthiness

```
Tier 1 (Government): 100 points
Tier 2 (Academic/Nonprofit): 75 points
Tier 3 (Commercial): 50 points
Tier 4 (Crowd-sourced): 25 points

Minimum threshold: 75 points
```

### Technique 5: Freshness Monitoring

**Method**: Track data age and flag stale indicators

```
1. Record fetch timestamp for each indicator
2. Set max age per source (e.g., Census: 365 days)
3. Flag indicators exceeding max age
4. Trigger refresh workflow
5. Alert maintainers
```

---

## Contact

- **Email**: zqmcomputing@gmail.com
- **GitHub**: ZQM-Labs/project-volusia
- **Website**: https://zqmlabs.com/

---

*Last updated: 2026-09-06*
