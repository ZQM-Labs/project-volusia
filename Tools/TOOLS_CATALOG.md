TOOLS CATALOG — PROJECT VOLUSIA
================================
Project Volusia — Tools Folder Index

Version: 1.0
Date: 2026-09-02

---

1. PURPOSE
===========

This folder contains tools, scripts, templates, and configurations
used to collect, process, analyze, and visualize data for Project
Volusia. All tools are documented, version-controlled where possible,
and aligned with our open-source-first philosophy.

---

2. TOOL CATEGORIES
====================

2.1 DATA COLLECTION
--------------------
Tools for acquiring data from public sources:

  CENSUS_API_WRAPPER
    Purpose:    Fetch American Community Survey data programmatically
    Language:   Python
    Source:     https://www.census.gov/data/developers.html
    Usage:      python tools/census/fetch_acs.py --county=12127 --year=2023

  BLS_SCRAPER
    Purpose:    Download Bureau of Labor Statistics LAUS/QCEW data
    Language:   Python
    Source:     https://www.bls.gov/developers/
    Usage:      python tools/bls/fetch_bls.py --area=FL12127

  FDOT_TRAFFIC_FETCHER
    Purpose:    Pull FDOT traffic count data for Volusia County
    Language:   Python
    Source:     https://www.fdot.gov/planning/statistics/
    Usage:      python tools/fdot/fetch_traffic.py --county=volusia

  STR_PARSER
    Purpose:    Parse STR hotel performance summary reports (CSV/PDF)
    Language:   Python
    Source:     Smith Travel Research (subscription)
    Usage:      python tools/str/parse_str.py --input=report.csv

  PROPERTY_APPRAISER_SCRAPER
    Purpose:    Scrape public parcel data from Volusia County PA
    Language:   Python
    Source:     https://vcpa.volusia.org/
    Usage:      python tools/property/fetch_parcels.py --zone=daytona

  WEATHER_FETCHER
    Purpose:    Download NOAA weather data for Volusia stations
    Language:   Python
    Source:     https://www.ncei.noaa.gov/
    Usage:      python tools/noaa/fetch_weather.py --station=USW00012838

  FCC_BROADBAND_CHECK
    Purpose:    Query FCC Broadband Map for address-level access
    Language:   Python
    Source:     https://broadbandmap.fcc.gov/
    Usage:      python tools/fcc/check_broadband.py --address="123 Main St"

2.2 DATA PROCESSING
---------------------
Tools for cleaning, transforming, and standardizing data:

  DATA_CLEANER
    Purpose:    Standardize column names, handle missing values,
                detect outliers, validate formats
    Language:   Python (pandas)
    Usage:      python tools/processing/clean.py --input=raw.csv --config=clean_config.yaml

  GEOCODE_ADDRESSES
    Purpose:    Geocode addresses to lat/lon using Census Geocoder
                or OpenStreetMap Nominatim
    Language:   Python
    Source:     https://geocoding.geo.census.gov/
    Usage:      python tools/processing/geocode.py --input=addresses.csv

  AGGREGATE_TO_COUNTY
    Purpose:    Aggregate tract/zip/city data to county level
                with population-weighted means where appropriate
    Language:   Python (pandas)
    Usage:      python tools/processing/aggregate.py --input=tracts.csv --to=county

  NORMALIZE_INDICATORS
    Purpose:    Min-max normalize or z-score standardize indicators
                for cross-metric comparison
    Language:   Python (scikit-learn)
    Usage:      python tools/processing/normalize.py --input=indicators.csv

  JOIN_DATASETS
    Purpose:    Join datasets on FIPS code, zip code, or geographic
                boundary with documented join logic
    Language:   Python (pandas/geopandas)
    Usage:      python tools/processing/join.py --left=a.csv --right=b.csv --on=fips

2.3 ANALYSIS & MODELING
-------------------------
Tools for statistical analysis and machine learning:

  TREND_ANALYZER
    Purpose:    Time-series trend analysis — linear regression,
                change-point detection, seasonality decomposition
    Language:   Python (statsmodels)
    Usage:      python tools/analysis/trends.py --input=timeseries.csv

  FORECAST_MODEL
    Purpose:    ARIMA/Prophet forecasting for economic and tourism
                indicators
    Language:   Python (statsmodels/prophet)
    Usage:      python tools/analysis/forecast.py --input=tourism.csv --horizon=12

  CLUSTERING
    Purpose:    K-means or DBSCAN clustering to identify natural
                groupings in business or demographic data
    Language:   Python (scikit-learn)
    Usage:      python tools/analysis/cluster.py --input=businesses.csv

  CORRELATION_MATRIX
    Purpose:    Generate correlation matrices with significance
                testing to identify relationships
    Language:   Python (pandas/scipy)
    Usage:      python tools/analysis/correlation.py --input=indicators.csv

  SENTIMENT_ANALYZER
    Purpose:    Analyze sentiment of tourist reviews or social media
                mentions about Volusia County
    Language:   Python (transformers/VADER)
    Usage:      python tools/analysis/sentiment.py --input=reviews.csv

2.4 VISUALIZATION
-------------------
Tools for generating charts, maps, and dashboards:

  CHART_GENERATOR
    Purpose:    Generate standardized charts (line, bar, scatter,
                heatmap) from data
    Language:   Python (matplotlib/seaborn/plotly)
    Usage:      python tools/viz/chart.py --input=data.csv --type=line

  MAP_GENERATOR
    Purpose:    Generate choropleth maps of Volusia County by
                census tract, zip code, or city
    Language:   Python (geopandas/folium)
    Usage:      python tools/viz/map.py --input=geo.geojson --column=median_income

  DASHBOARD_BUILDER
    Purpose:    Build interactive dashboards (Plotly Dash or Streamlit)
                for stakeholder exploration
    Language:   Python (streamlit)
    Usage:      streamlit run tools/viz/dashboard.py

  REPORT_RENDERER
    Purpose:    Render quarterly reports from templates and data
    Language:   Python (Jinja2 + WeasyPrint/Markdown)
    Usage:      python tools/viz/render_report.py --template=q3_2026.md

2.5 INFRASTRUCTURE
--------------------
Tools for deployment, monitoring, and maintenance:

  PORTAL_DEPLOY
    Purpose:    Deploy public data portal (static site or lightweight
                web app)
    Language:   Shell/Docker
    Usage:      ./tools/infra/deploy_portal.sh

  API_SERVER
    Purpose:    Serve data via REST API (FastAPI)
    Language:   Python (FastAPI)
    Usage:      uvicorn tools.infra.api:app --host 0.0.0.0 --port 8000

  HEALTH_CHECK
    Purpose:    Monitor data freshness, API uptime, and data quality
    Language:   Python
    Usage:      python tools/infra/health_check.py

  BACKUP_SYNC
    Purpose:    Sync datasets to backup storage and version control
    Language:   Shell/Rclone
    Usage:      ./tools/infra/backup.sh

  LOG_COLLECTOR
    Purpose:    Aggregate tool logs for debugging and audit
    Language:   Python
    Usage:      python tools/infra/logs.py --since=2026-09-01

---

3. TOOL DEVELOPMENT STANDARDS
==============================

  - All tools have a --help flag explaining usage
  - All tools log their actions with timestamps
  - All tools document their dependencies in requirements.txt
  - All tools are tested against sample data before deployment
  - All tools default to open formats (CSV, JSON, GeoJSON, Parquet)
  - All tools are reviewed before being made available externally

---

4. OPEN SOURCE PRIORITY
=========================

When selecting tools for any task, we prioritize:

  1. Open-source libraries with active communities
  2. Open-source tools with permissive licenses (MIT, Apache 2.0, BSD)
  3. Open APIs with documented terms of service
  4. Public-domain data and tools

  We avoid proprietary lock-in unless no viable open alternative exists.
  When we must use a closed tool, we document the reason and maintain
  an exit strategy.

---

Document owner: Project Volusia Technical Team
Related: ../MISSION_STATEMENT.md, ../OPEN_INTELLIGENCE_DATA_DRIVEN_CHARTER.md
