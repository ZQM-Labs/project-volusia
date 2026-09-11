#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Project Volusia — Deploy Pipeline (bash wrapper)
# Usage: ./deploy.sh [options]
#   --dry-run       Preview without executing
#   --skip-backend  Skip data refresh
#   --skip-frontend Skip React build
#   --skip-verify   Skip verification

PYTHON="python3"
SCRIPT="scripts/deploy.py"

echo "=== Project Volusia — Deploy Pipeline ==="
echo ""

# Run Python deploy script
$PYTHON "$SCRIPT" "$@"

echo ""
echo "=== Deploy complete ==="