# FAQ — Project Volusia

> Frequently asked questions about Project Volusia.

---

## General

### What is Project Volusia?

Project Volusia is an open-source data portal for Volusia County, Florida. It aggregates economic, demographic, climate, and tourism data from government sources and presents it in an easy-to-use web interface.

### Who is this for?

- **Business owners** — Market research, industry benchmarks
- **Residents** — Cost of living, school data, community info
- **Tourists** — Visitor trends, hotel occupancy, events
- **Leaders** — Capital flows, workforce data, permitting

### Is this free?

Yes! Project Volusia is completely free and open-source under the MIT License.

### How often is data updated?

| Source | Frequency |
|--------|-----------|
| Census PEP | Annual |
| Census ACS | Annual (5-year estimates) |
| BLS LAUS | Monthly |
| BLS QCEW | Quarterly |
| BEA Regional | Annual |
| NOAA NCEI | Daily |
| C2ER COLI | Quarterly |
| Volusia CVB | Monthly |

---

## Technical

### What technologies are used?

**Backend**: Python, FastAPI, SQLite
**Frontend**: React, TypeScript, Vite, Tailwind CSS, Nivo, Leaflet

### Can I run this locally?

Yes! See the [Deployment Guide](deployment/guide.md) for instructions.

### How do I add a new data source?

See the [Data Sources Guide](data-sources/adding-sources.md) for instructions.

### How do I contribute?

See the [Contributing Guide](contributing/guide.md) for instructions.

---

## Data

### Where does the data come from?

All data comes from authoritative government sources:
- US Census Bureau
- Bureau of Labor Statistics (BLS)
- Bureau of Economic Analysis (BEA)
- NOAA National Centers for Environmental Information
- Volusia County Convention & Visitors Bureau

### How accurate is the data?

Data is sourced directly from government APIs and validated through automated quality checks. See [Data Quality](data-sources/quality.md) for details.

### Can I download the data?

Yes! All data is available as JSON files or CSV download via the API.

### Why is some data missing?

Some data may be missing due to:
- Source API downtime
- Data not yet published by source
- Quality checks filtering out invalid values

Check the `fetched_at` timestamp to see when data was last updated.

---

## Deployment

### How is this deployed?

- **Frontend**: GitHub Pages (https://volusia.zqmlabs.com)
- **Backend**: ZQM-Node-4 (192.168.1.219) via Cloudflare Tunnel

### Can I deploy my own instance?

Yes! See the [Deployment Guide](deployment/guide.md) for Docker and manual deployment instructions.

### What about custom domains?

The frontend uses `volusia.zqmlabs.com` via CNAME. You can configure your own domain in GitHub Pages settings.

---

## Contributing

### How do I report a bug?

Create an issue at https://github.com/ZQM-Labs/project-volusia/issues with:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots (if applicable)

### How do I request a feature?

Create an issue with the "feature request" label at https://github.com/ZQM-Labs/project-volusia/issues.

### Can I submit data?

Yes! See [Data Source Contribution](data-sources/adding-sources.md) for how to contribute new data sources.

### Do I need programming skills?

Not necessarily! You can contribute by:
- Reporting bugs
- Suggesting features
- Contributing data sources
- Improving documentation
- Translating content

---

## Legal

### What is the license?

MIT License — you can use, modify, and distribute freely.

### Can I use this commercially?

Yes! The MIT License allows commercial use.

### Who maintains this?

ZQM Labs / ZQM Computing (zqmcomputing@gmail.com)

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
