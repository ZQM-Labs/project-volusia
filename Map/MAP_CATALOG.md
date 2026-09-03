MAP CATALOG — VOLUSIA COUNTY
==============================
Project Volusia — Map Layers & Geospatial Data
Version: 1.0 | Date: 2026-09-03
Owner: Project Volusia GIS Lead

---

1. PURPOSE
==========

This document catalogs all map layers available for Project Volusia reports,
dashboards, and public-facing visualizations.

---

2. LAYER CATEGORIES
=====================

2.1 ADMINISTRATIVE BOUNDARIES
------------------------------
  - Volusia County boundary (EPSG:4269)
  - City boundaries (Daytona Beach, DeLand, New Smyrna Beach, Ormond Beach,
    Port Orange, Deltona, etc.)
  - Census tracts (2020)
  - Zip Code Tabulation Areas (ZCTAs)
  - School district boundary (Volusia County Schools)

2.2 DEMOGRAPHIC & SOCIOECONOMIC
---------------------------------
  - Median household income by tract (ACS DP03)
  - Poverty rate by tract (ACS DP03)
  - Educational attainment by tract (ACS S1501)
  - Population density by tract (ACS DP05)
  - Age distribution by tract (ACS DP05)

2.3 ECONOMIC & BUSINESS
-------------------------
  - Business density by ZIP (Census CBP)
  - Employment by industry (BLS QCEW)
  - Building permits by jurisdiction (Census BPS)
  - Tourist development tax receipts by district

2.4 INFRASTRUCTURE & TRANSPORTATION
-------------------------------------
  - VOTRAN bus routes and stops
  - FDOT traffic count stations
  - FCC broadband availability by block
  - National Bridge Inventory (FHWA)

2.5 ENVIRONMENT & CLIMATE
---------------------------
  - FEMA flood zones
  - Wetlands (FL DEP)
  - Sea level rise projections (NOAA)
  - Hurricane evacuation zones

2.6 HISTORIC & CULTURAL
-------------------------
  - National Register of Historic Places
  - Florida Master Site File (archaeological)
  - Museum and cultural facility locations

---

3. DATA SOURCES
================

| Layer | Source | Update Frequency | Format |
|-------|--------|------------------|--------|
| County boundary | Census TIGER/Line | Annual | Shapefile/GeoJSON |
| City boundaries | Census TIGER/Line | Annual | Shapefile/GeoJSON |
| Census tracts | Census TIGER/Line | Decennial | Shapefile/GeoJSON |
| Demographics | Census ACS 5-Year | Annual | API/CSV |
| Business density | Census CBP | Annual | API/CSV |
| Building permits | Census BPS | Monthly/Annual | API/CSV |
| Broadband | FCC | Semi-annual | API |
| Flood zones | FEMA | As updated | Shapefile |

---

4. PROJECTION STANDARD
=======================

All Project Volusia maps use:
  - EPSG:4269 (NAD83) for national/regional context
  - EPSG:2236 (Florida State Plane East, NAD83) for county/local maps

---

5. ACCESS & LICENSING
======================

All map data is sourced from public domain (U.S. government) or open-licensed
sources. Commercial data (Zillow, STR) is used only in aggregate form with
attribution.

---

Document owner: Project Volusia GIS Lead
Related: PUBLIC_DATA_SOURCE_RECON.md, METHODOLOGY.md
Next review: 2026-12-02
