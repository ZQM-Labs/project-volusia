DATA CATALOG — VOLUSIA COUNTY
===============================
Project Volusia — Data Folder Index

Version: 1.0
Date: 2026-09-02

---

1. PURPOSE
===========

This folder contains datasets, data catalogs, and data-source
documentation for Project Volusia. All data is sourced from
public, verifiable, and documented origins. Where we use
third-party data, we cite the source, date accessed, and
any transformations applied.

---

2. DATA CATEGORIES
====================

2.1 ECONOMIC DATA
-----------------
Sources:
  - US Bureau of Labor Statistics (BLS) — Local Area Unemployment
    Statistics (LAUS), Quarterly Census of Employment and Wages (QCEW)
    https://www.bls.gov/lau/
    https://www.bls.gov/cew/

  - US Census Bureau — American Community Survey (ACS) 5-Year Estimates
    https://data.census.gov/
    Table IDs: DP03 (Economic Characteristics), DP05 (Demographic)
    Geography: Volusia County, FL (FIPS 12127)

  - Florida Department of Economic Opportunity — Labor Market Statistics
    http://floridajobs.org/labor-market-information

  - US Bureau of Economic Analysis (BEA) — Local Area Personal Income
    https://www.bea.gov/data/income-saving/local-area-personal-income
    Table CAINC1 (Personal Income by Major Source)

2.2 TOURISM DATA
----------------
Sources:
  - Volusia County Convention & Visitors Bureau — Annual Tourism Reports
    https://www.visitdaytonabeach.com/research

  - STR (Smith Travel Research) — Hotel Performance Data
    (subscription; summary reports often public via CVB)

  - Florida Department of Business & Professional Regulation —
    Restaurant and lodging license counts
    https://www.myfloridalicense.com/

  - National Park Service — Visitor Use Statistics
    Canaveral National Seashore
    https://www.nps.gov/cana/learn/management/statistics.htm

2.3 REAL ESTATE & HOUSING
--------------------------
Sources:
  - Zillow Research — Home Value Index (ZHVI), Rent Index (ZORI)
    https://www.zillow.com/research/data/
    Geography: Volusia County, FL

  - Realtor.com Research & Insights — Market Trends
    https://www.realtor.com/research/data/

  - Volusia County Property Appraiser — Parcel Data, Sales History
    https://vcpa.volusia.org/

  - US Census Bureau — Building Permits Survey
    https://www.census.gov/construction/bps/
    Geography: Volusia County, FL

  - Florida Housing Data Clearinghouse (Shimberg Center)
    http://flhousingdata.shimberg.ufl.edu/

2.4 DEMOGRAPHIC DATA
---------------------
Sources:
  - US Census Bureau — Decennial Census 2020
    https://data.census.gov/

  - US Census Bureau — Population Estimates Program (PEP)
    https://www.census.gov/programs-surveys/popest.html

  - Florida Office of Economic and Demographic Research (EDR)
    http://edr.state.fl.us/

  - CDC PLACES — Health Data by Census Tract
    https://places.cdc.gov/

2.5 TRANSPORTATION & INFRASTRUCTURE
------------------------------------
Sources:
  - Florida Department of Transportation (FDOT) — Traffic Data
    https://www.fdot.gov/planning/statistics/

  - Volusia County Public Transit (VOTRAN) — Ridership Reports
    https://www.volusia.org/services/public-transit/

  - US DOT — National Bridge Inventory
    https://www.fhwa.dot.gov/bridge/nbi.cfm

  - FCC Broadband Map — Internet Access by Address
    https://broadbandmap.fcc.gov/

2.6 CLIMATE & ENVIRONMENT
--------------------------
Sources:
  - NOAA National Centers for Environmental Information (NCEI)
    https://www.ncei.noaa.gov/

  - USGS — Water Data for Volusia County
    https://waterdata.usgs.gov/fl/nwis/nwis

  - FEMA — Flood Map Service Center
    https://msc.fema.gov/

  - Florida Department of Environmental Protection —
    Environmental data and permits
    https://floridadep.gov/

2.7 PUBLIC SAFETY
------------------
Sources:
  - Volusia County Sheriff's Office — Crime Statistics
    https://www.volusia.org/services/public-safety/

  - Florida Department of Law Enforcement — Uniform Crime Reports
    https://www.fdle.state.fl.us/CR/CR.aspx

  - US FBI — Uniform Crime Reporting (UCR)
    https://ucr.fbi.gov/

2.8 HEALTH DATA
----------------
Sources:
  - Florida Department of Health — CHARTS (Community Health Status)
    http://www.flhealthcharts.com/

  - CDC — Behavioral Risk Factor Surveillance System (BRFSS)
    https://www.cdc.gov/brfss/

  - County Health Rankings (Robert Wood Johnson Foundation)
    https://www.countyhealthrankings.org/

2.9 EDUCATION DATA
-------------------
Sources:
  - Florida Department of Education — School Report Cards
    https://www.fldoe.org/accountability/

  - National Center for Education Statistics (NCES) —
    School District Demographics
    https://nces.ed.gov/

  - US Census Bureau — Educational Attainment (ACS Table S1501)

2.10 GOVERNMENT FINANCE
------------------------
Sources:
  - Volusia County — Annual Comprehensive Financial Report (ACFR)
    https://www.volusia.org/services/finance/

  - Florida Department of Financial Services — Local Government Data
    https://myfloridacfo.com/division/aa/

  - US Census Bureau — Annual Survey of State and Local
    Government Finances
    https://www.census.gov/programs-surveys/gov-finances.html

---

3. DATA STANDARDS
===================

All data in this folder follows these standards:

  SOURCE      — Every dataset cites its origin
  DATE        — Date of access and date of data are both recorded
  FORMAT      — Machine-readable (CSV, JSON, GeoJSON, Parquet)
  LICENSE     — Public domain or open license documented
  TRANSFORM   — Any cleaning, joining, or calculation is documented
  LIMITATION  — Known gaps, biases, or caveats are stated

---

4. HOW TO CONTRIBUTE DATA
===========================

  1. Verify the source is public and documented
  2. Record the URL, date accessed, and license
  3. Document any transformations in a README alongside the data
  4. Submit for review before inclusion in official analyses

---

Document owner: Project Volusia Data Team
Related: ../MISSION_STATEMENT.md, ../OPEN_INTELLIGENCE_DATA_DRIVEN_CHARTER.md
