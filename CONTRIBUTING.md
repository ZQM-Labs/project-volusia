# Contributing to Project Volusia

Thank you for your interest in contributing! This document outlines the architecture and development workflow.

## Architecture Overview

### Services

| Service | Port | File | Description |
|---------|------|------|-------------|
| Portal | 8789 | Tools/volusia_data/portal_app.py | Main data portal with dashboard and APIs |
| Contribution API | 8790 | Tools/volusia_data/contribution_api.py | REST API for submitting contributions |
| Contribute Portal | 8791 | Tools/volusia_data/portal_contribute.py | Web form frontend for contributions |
| Reverse Proxy | 80 | deploy_portal.py | Routes requests to appropriate service |

### Dual API Architecture

There are two contribution API implementations:

1. **Tools/volusia_data/contribution_api.py** (canonical) — The production implementation used by all tests and the portal. Uses raw SQLite with in-memory rate limiting.

2. **contribution-api/** (experimental) — A standalone FastAPI package with SQLAlchemy and JWT auth. This is an aspirational refactor that is not yet integrated into the pipeline.

**When contributing to contribution features**: Always target the canonical contribution_api.py. The contribution-api/ package is experimental and not covered by tests.

### Key Files

| File | Purpose |
|------|---------|
| Tools/volusia_data/refresh_v2.py | Data pipeline — fetches from Census, NOAA, BLS, BEA |
| Tools/volusia_data/config.py | Central configuration and .env loading |
| Tools/volusia_data/contribution_api.py | Contribution submission API |
| Tools/volusia_data/portal_app.py | Main portal application |
| Tools/volusia_data/portal_contribute.py | Contribution web forms |

## Development Setup

`ash
# Clone and setup
git clone https://github.com/ZQM-Labs/project-volusia.git
cd project-volusia
./scripts/dev-up.sh

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
source .venv/Scripts/activate  # Windows

# Run tests
make test

# Run linting
make lint

# Start development server
make dev
`

## Code Style

- Python 3.11+
- Line length: 88 characters (ruff default)
- Formatting: ruff format
- Linting: ruff check
- Type hints: encouraged but not required

## Testing

`ash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=volusia_data tests/

# Run specific test module
pytest tests/test_contribute.py -v
`

## Pull Request Process

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Make your changes
4. Run tests and linting (make test && make lint)
5. Commit your changes (git commit -m 'Add amazing feature')
6. Push to the branch (git push origin feature/amazing-feature)
7. Open a Pull Request

## Questions?

Open an issue with the question label for any architecture or development questions.
