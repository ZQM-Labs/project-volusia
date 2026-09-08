# Adding New Data Sources — Project Volusia

> How to add new data sources to Project Volusia.

---

## Overview

This guide walks you through the process of adding a new data source to Project Volusia.

---

## Prerequisites

- Python 3.11+
- Git
- Understanding of REST APIs

---

## Step 1: Identify the Data Source

Before adding a source:

1. **Verify public access** — Source must be publicly accessible
2. **Check license** — Must allow redistribution (Public Domain, MIT, Apache, etc.)
3. **Evaluate quality** — Authoritative source (government, academic, reputable)
4. **Check update frequency** — Regularly updated

---

## Step 2: Add to Data Pipeline

### Edit `Tools/volusia_data/refresh_v2.py`

Add a new fetch function:

```python
def fetch_new_source():
    """Fetch data from New Source API."""
    print("Fetching New Source...")
    try:
        url = "https://api.example.com/data"
        data = http_get_json(url)
        if data:
            # Extract and validate data
            value = data.get("indicator_value")
            if value and is_valid_value(value):
                upsert_indicator(
                    "new_indicator_name",
                    value,
                    "unit",
                    "Category",
                    "New Source Name",
                    url,
                    "2024",
                    "Description of the indicator"
                )
    except Exception as e:
        print(f"  New Source error: {e}")
    print("  New Source done")
```

### Add to `run_pipeline()`

```python
def run_pipeline():
    ...
    fetch_new_source()
    ...
```

---

## Step 3: Add Tests

Create a test in `tests/test_pipeline.py`:

```python
def test_fetch_new_source():
    """Test fetching from new source."""
    # Mock the HTTP response
    # Assert data is fetched and stored correctly
```

---

## Step 4: Update Documentation

1. Add entry to `docs/data-sources/overview.md`
2. Create `docs/data-sources/sources/new-source.md`
3. Update `docs/data-sources/adding-sources.md` (this file)

---

## Step 5: Commit and Push

```bash
git add .
git commit -m "feat: add new data source (New Source Name)"
git push origin main
```

---

## Example: Adding Census PEP

Here's a real example from the codebase:

```python
def fetch_census_pep():
    """Fetch Census Population Estimates Program data."""
    print("Fetching Census PEP...")
    url = "https://www2.census.gov/programs-surveys/pest/datasets/2020-2024/counties/totals/co-est2024-alldata.csv"
    content = http_get(url)
    if not content:
        return
    
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        if row.get("STATE") == STATE_FIPS and row.get("COUNTY") == COUNTY_CODE:
            year = row.get("YEAR", "2024")
            pop = row.get("POPESTIMATE")
            if pop and is_valid_value(pop):
                upsert_indicator(
                    f"total_population_pep_{year}",
                    pop, "persons", "Demographics",
                    "Census PEP", url,
                    year, f"Census PEP population estimate, July 1 {year}"
                )
    print("  Census PEP done")
```

---

## Validation Checklist

- [ ] Source URL is accessible
- [ ] Data format is correct (JSON, CSV, etc.)
- [ ] Values are within expected range
- [ ] No null markers present
- [ ] Category is one of: Economic, Demographics, Climate, Tourism, Housing, Education, Health, Transportation, Public Safety, Business
- [ ] Source name is normalized
- [ ] Vintage (year/date) is included
- [ ] Description is human-readable
- [ ] Tests pass

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
