.PHONY: help install test test-fast lint run clean dev release

# Project Volusia Makefile - Developer QOL Improvements
# Usage: make [target]

help:
	@echo "Project Volusia Development Tools"
	@echo ""
	@echo "Development:"
	@echo "  dev       - Start dev environment with auto-reload"
	@echo "  install   - Install dependencies"
	@echo "  run       - Run the data pipeline"
	@echo "  portal    - Run the API portal"
	@echo ""
	@echo "Quality:"
	@echo "  test      - Run all tests"
	@echo "  test-fast - Run tests, skipping live-network fetcher tests"
	@echo "  lint      - Run linting and formatting checks"
	@echo "  format    - Auto-format code"
	@echo "  safety    - Security check dependencies"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean     - Clean up cache files"
	@echo "  migrate   - Run database migrations"
	@echo "  release   - Create a release"
	@echo "  changelog - Generate changelog from commits"

# Install dependencies
install:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"
	pip install pre-commit
	pre-commit install

# Run tests with pytest
test:
	pytest tests/ -v --tb=short --durations=0

# Fast test loop: skip live-network fetcher tests
test-fast:
	pytest tests/ -m "not network" -v --tb=short

# Run linting
lint:
	ruff check .
	ruff format --check .

# Auto-format code
format:
	ruff format .
	ruff check --fix .

# Run pipeline
run:
	python Tools/volusia_data/refresh_v2.py

# Run portal
portal:
	python Tools/volusia_data/portal_app.py

# Run dev with auto-reload
dev:
	python -m venv .venv && \
	. .venv/bin/activate && \
	pip install -e ".[dev]" && \
	pre-commit install && \
	echo "✓ Dev environment ready. Run 'make run' or 'make portal'"

# Clean cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov/ dist/ build/ 2>/dev/null || true

# Run database migrations
migrate:
	python Tools/volusia_data/migrate_db.py

# Security check
safety:
	pip install safety
	safety check

# Generate changelog (requires git conventional commits)
changelog:
	@echo "# Changelog"
	git log --oneline --since="1 week ago" --pretty=format:"- %s" 2>/dev/null || echo "No recent commits"

# Create release (requires proper auth)
release:
	@echo "Creating release..."
	gh release create $$(git describe --tags --abbrev=0) \
		--title "Release $$(git describe --tags --abbrev=0)" \
		--notes "Auto-generated release"