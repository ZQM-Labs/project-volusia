# Contributing to Project Volusia

> Guidelines for contributing to the Volusia County data portal.

---

## How to Contribute

Project Volusia welcomes contributions of all kinds:
- **Data submissions** — New indicators, corrections, updates
- **Code contributions** — Bug fixes, features, improvements
- **Documentation** — Typo fixes, clarity improvements, new docs
- **Source validation** — Finding and verifying new data sources

---

## Submitting Data

All data updates go through the submission workflow:

1. **Submit**: `POST /api/contribute` with your data
2. **Review**: Community or admin reviews the submission
3. **Approve/Reject**: Status changes to `approved` or `rejected`
4. **Ingest**: Approved submissions update the database

### Contribution Format

```json
{
  "name": "indicator_name",
  "value": "numeric_value",
  "unit": "unit_of_measure",
  "category": "CategoryName",
  "source": "Source Agency",
  "source_url": "https://url.to.source",
  "vintage": "2024",
  "description": "Human-readable description"
}
```

### Requirements
- **Tier 1 sources preferred** — Government agencies, universities
- **Tier 2 acceptable** — Verified nonprofits, academic sources
- **Tier 3 require cross-reference** — Must cite 2+ sources
- **No AI-generated data** — All data must have traceable sources

### Check Submission Status
```
GET /api/contributor
```

---

## Code Contributions

### Project Structure
```
volusia-portal/
├── backend/          FastAPI application (main.py)
├── volusia-portal/   React frontend (src/)
├── project-volusia-web/  Static page generator
├── scripts/          Deployment and utility scripts
├── data/             Database and cache files
└── docs/             Documentation
```

### Development

```bash
# Backend
cd volusia-portal
pip install -r requirements.txt
python backend/main.py
# API: http://localhost:8000

# Frontend
cd volusia-portal/src
npm install
npm run dev        # http://localhost:5173
npm run build      # Production build
```

### TypeScript
```bash
npx tsc --noEmit   # Must pass with zero errors
```

### Testing
```bash
python -m pytest tests/
```

---

## Deployment

All deployments use the automated pipeline:

```bash
# Full deploy
python scripts/deploy.py

# Dry run
python scripts/deploy.py --dry-run

# Skip steps
python scripts/deploy.py --skip-backend --skip-frontend
```

See [DEPLOY.md](DEPLOY.md) for full deployment documentation.

---

## Commit Guidelines

1. Use descriptive commit messages
2. Reference related issues
3. Include data source citations when adding new indicators
4. Update documentation when changing APIs or deployment

---

## Documentation

Documentation lives in the repo root:

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick links |
| `ARCHITECTURE.md` | System architecture, components |
| `API.md` | Complete API reference |
| `DEPLOY.md` | Deployment instructions |
| `CONTRIBUTING.md` | This file |

---

## Code of Conduct

- Be respectful and constructive
- Cite data sources accurately
- Do not fabricate or alter data
- Follow the tiered data quality system

---

## License

MIT License — see LICENSE file.

---

*Last updated: 2026-09-11*
