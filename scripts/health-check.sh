#!/bin/bash
# health-check.sh - Production health verification
# Usage: ./scripts/health-check.sh

set -e

echo "🏥 Project Volusia Health Check"
echo "================================"
echo ""

# Check if database exists
DB_PATH="Tools/volusia_data/volusia.db"
if [ -f "$DB_PATH" ]; then
    echo "✓ Database: $DB_PATH"
else
    echo "✗ Database: NOT FOUND"
    exit 1
fi

# Check indicator count
COUNT=$(python -c "import sqlite3; print(sqlite3.connect('$DB_PATH').execute('SELECT COUNT(*) FROM indicators').fetchone()[0])")
echo "✓ Indicators: $COUNT"

# Check API endpoints
echo ""
echo "API Endpoints:"
for endpoint in api/health api/indicators api/status; do
    if curl -sf "http://localhost:8789/$endpoint" > /dev/null 2>&1; then
        echo "  ✓ /$endpoint"
    else
        echo "  ○ /$endpoint (not running)"
    fi
done

# Check Contribution API (port 8790)
echo ""
echo "Contribution API:"
if curl -sf "http://localhost:8790/api/v1/health" > /dev/null 2>&1; then
    echo "  ✓ /api/v1/health (port 8790)"
else
    echo "  ○ /api/v1/health (not running)"
fi

echo ""
echo "✅ Health check complete"