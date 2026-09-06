# Project Volusia — Source Expansion Log

## 2026-09-06 — Deep Source Dive (32 new sources)

### Federal Sources (12)
| Source | URL | Category |
|--------|-----|----------|
| Census ACS API | api.census.gov/data/2024/acs/acs5 | Demographics |
| Census DP03 | data.census.gov/table/ACSDP5Y2024.DP03 | Economy |
| Census DP05 | data.census.gov/table/ACSDP5Y2024.DP05 | Demographics |
| FRED St. Louis | fred.stlouisfed.org | Economy |
| BLS QCEW API | data.bls.gov/cew/data/api/ | Economy |
| BLS QCEW Series | data.bls.gov/timeseries/ENU1212720010 | Economy |
| EPA ECHO | echo.epa.gov | Health |
| EPA AirNow | airnow.gov | Climate |
| EPA TRI | epa.gov/toxics-release-inventory-tri-program | Health |
| HUD Data Portal | huduser.gov/portal/datasets/pdr.html | Government |
| FEMA NFH | msc.fema.gov | Hydrography |
| USDA NASS | quickstats.nass.usda.gov | Economy |

### Florida State Sources (10)
| Source | URL | Category |
|--------|-----|----------|
| FL DEP Water Quality | floridadep.gov/dear/water-quality-assessment | Hydrography |
| FL DEP Geodata | geodata.dep.state.fl.us | GIS |
| FL DEP Protecting FL | protectingfloridatogether.gov | Hydrography |
| FL DEP Resilient | floridadep.gov/rcp/resilient-florida-program | Climate |
| FL DOE Grades | fldoe.org | Education |
| FL DOH Charts | flhealthcharts.gov | Health |
| FL DOH Vital | floridahealth.gov/statistics-data/vital-statistics/ | Health |
| FL DOS Elections | dos.elections.myflorida.com | Government |
| FL DACS | fdacs.gov | Economy |
| FDOT Projects | cflroads.com | Transportation |

### Local Sources (4)
| Source | URL | Category |
|--------|-----|----------|
| Volusia EDC Research | volusiabusiness.org/research-center/ | Economy |
| Volusia TPO | volusiatpo.org | Transportation |
| One Voice for Volusia | onevoiceforvolusia.org/data | Government |
| Volusia Health Dept | volusia.floridahealth.gov | Health |

### Commercial/Academic (6)
| Source | URL | Category |
|--------|-----|----------|
| Zillow Data | zillow.com/research/data/ | Housing |
| BEA Regional API | apps.bea.gov/API/signup/index.cfm | Economy |
| UCF Forecast | business.ucf.edu/centers-institutes/... | Economy |
| EIA State FL | eia.gov/state/?sid=FL | Infrastructure |
| FERC | ferc.gov | Infrastructure |
| GridInfo | gridinfo.com | Infrastructure |

## Current State (2026-09-06)

```
Indicators:     266
Categories:     15
Sources:        70+
Quality checks: 532
Endpoints:      39+
```

## Category Breakdown

| Category | Count |
|----------|-------|
| Economy | 47 |
| Transportation | 27 |
| Government | 27 |
| Health | 26 |
| Education | 25 |
| Infrastructure | 22 |
| Hydrography | 13 |
| Demographics | 18 |
| Climate | 11 |
| Public Safety | 13 |
| Boundaries | 8 |
| GIS | 9 |
| Terrain | 6 |
| Housing | 10 |
| Media | 4 |

## Next Steps

1. Register Census ACS, BLS, BEA API keys for live data fetching
2. Deploy behind cloudflared for public access
3. Schedule stakeholder interviews for validated requirements
4. Create content engine (weekly reports, YouTube briefings)
5. GitHub growth strategy (CONTRIBUTING.md, releases, blog posts)

---

*Last updated: 2026-09-06*
*Status: OPERATIONAL*
