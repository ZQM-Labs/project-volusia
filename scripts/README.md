# Project Volusia Utils

## Scripts

### scripts/dev-up.sh
One-command development environment setup.
```bash
./scripts/dev-up.sh
```

### scripts/health-check.sh  
Production health verification.
```bash
./scripts/health-check.sh
```

### scripts/generate-changelog.sh
Generate changelog from git commits.
```bash
./scripts/generate-changelog.sh
```

### scripts/deploy.sh
Deploy to production (stub).
```bash
./scripts/deploy.sh production
```

## Utility Modules

### Tools/volusia_data/watch_refresh.py
Watch mode for auto-refreshing pipeline.
```bash
python watch_refresh.py --interval 300
python watch_refresh.py --once
```

### Tools/volusia_data/validate_env.py
Validate environment before running.
```bash
python validate_env.py
```

## Quick Start

```bash
# Method 1: Make (recommended)
make install    # One-time setup
make test       # Run tests
make run        # Run pipeline
make portal     # Start API

# Method 2: Scripts
./scripts/dev-up.sh
source .venv/bin/activate
make test
make run

# Method 3: Docker
docker-compose up -d
curl http://localhost:8789/api/health
```