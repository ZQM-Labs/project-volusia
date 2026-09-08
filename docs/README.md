# Project Volusia — Documentation Index

> Complete documentation for the Project Volusia open data portal.

---

## Quick Start

| I want to... | Go to |
|--------------|-------|
| Understand the architecture | [Architecture](architecture/system-overview.md) |
| Use the API | [API Reference](api/endpoints.md) |
| Add a data source | [Data Sources](data-sources/adding-sources.md) |
| Deploy the portal | [Deployment](deployment/guide.md) |
| Contribute code | [Contributing](contributing/guide.md) |
| Fix a problem | [Troubleshooting](troubleshooting/common-issues.md) |
| Get quick answers | [FAQ](troubleshooting/faq.md) |
| Connect frontend to backend | [Connection Guide](../CONNECTION.md) |

---

## Documentation Structure

```
docs/
├── architecture/
│   ├── system-overview.md      # High-level system architecture
│   ├── data-flow.md            # How data moves through the system
│   ├── database-schema.md      # SQLite schema documentation
│   └── security.md             # Security considerations
├── api/
│   ├── endpoints.md            # API endpoint reference
│   ├── authentication.md       # API authentication
│   └── rate-limiting.md        # Rate limiting policies
├── data-sources/
│   ├── overview.md             # Data source overview
│   ├── adding-sources.md       # How to add new sources
│   ├── quality.md              # Data quality standards
│   └── sources/                # Individual source docs
│       ├── census-pep.md
│       ├── census-acs.md
│       ├── bls-laus.md
│       ├── bls-qcew.md
│       ├── bea-regional.md
│       ├── noaa-ncei.md
│       └── cvb-hotels.md
├── deployment/
│   ├── guide.md                # Deployment guide
│   ├── docker.md               # Docker deployment
│   ├── github-pages.md         # GitHub Pages setup
│   └── cloudflare.md           # Cloudflare tunnel setup
├── contributing/
│   ├── guide.md                # Contributing guide
│   ├── code-style.md           # Code style guide
│   ├── pull-request.md         # PR process
│   └── issues.md               # Issue reporting
├── troubleshooting/
│   ├── common-issues.md        # Common issues and fixes
│   └── faq.md                  # FAQ
└── README.md                   # This file
