MAP CATALOG — VOLUSIA COUNTY
==============================
Project Volusia — Map Layers & Geospatial Data
Version: 1.1 | Date: 2026-09-04
Owner: Project Volusia GIS Lead

---

1. PURPOSE
===========

This document catalogs all map layers available for Project Volusia reports,
dashboards, and public-facing visualizations.

---

2. AVAILABLE MAPS
===================

### Population (County-Level)
    File:    Map/volusia_county_population.html
    Source:  Census PEP (2024 estimate, 601,107)
    Status:  LIVE
    Type:    Choropleth (Leaflet HTML)
    Notes:   County-level view. Census tract-level data requires TIGER/Line GeoJSON download.
    Generated: 2026-09-04

---

3. PLANNED MAPS (Pending Data)
================================

| Map | Source | Status |
|-----|--------|--------|
| Population Density (tract-level) | Census ACS | Pending ACS API key |
| Unemployment Rate (tract-level) | BLS LAUS | Pending live BLS key |
| Median Income (tract-level) | Census ACS | Pending ACS API key |
| Employment Density | BLS QCEW | Pending data join |
| FEMA Flood zones | FEMA | Pending data download |
| VOTRAN bus routes | VOTRAN | Pending data download |

---

4. DATA SOURCES
================

| Source | Layer | Update Frequency | Format |
|--------|-------|------------------|--------|
| Census TIGER/Line | County boundary | Annual | GeoJSON |
| Census PEP | Population | Annual | CSV |
| Census ACS | Demographics | Annual | API/CSV |
| BLS LAUS | Unemployment | Monthly | API |
| BLS QCEW | Employment | Quarterly | ZIP/CSV |
| NOAA NCEI | Climate | Daily | API |

---

5. MAP TOOLS
==============

All maps are generated using:

- **Engine:** Leaflet.js (open-source)
- **Tiles:** OpenStreetMap
- **Colors:** ColorBrewer (colorblind-safe palettes)
- **Format:** Self-contained HTML (no server required)

### Generating Maps

```bash
python Tools/volusia_data/viz/map.py --input geojson_file.geojson --column column_name --output Map/output.html
```

---

6. PROJECTION STANDARD
========================

All Project Volusia maps use:
  - EPSG:4269 (NAD83) for national/regional context
  - EPSG:2236 (Florida State Plane East, NAD83) for county/local maps

---

7. ACCESS & LICENSING
=======================

All map data is sourced from public domain (U.S. government) or open-licensed
sources. Commercial data (Zillow, STR) is used only in aggregate form with
attribution.

---

Document owner: Project Volusia GIS Lead
Related: PUBLIC_DATA_SOURCE_RECON.md, METHODOLOGY.md
Next review: 2026-12-02
