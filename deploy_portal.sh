#!/bin/bash
# Project Volusia Portal Deployment Script
# Deploys the FastAPI portal behind cloudflared tunnel

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "=== Project Volusia Portal Deployment ==="
echo ""

# Check if portal is already running
if pgrep -f "portal_app.py" > /dev/null 2>&1; then
    echo "Portal already running, restarting..."
    pkill -f "portal_app.py" || true
    sleep 2
fi

# Start the FastAPI portal
echo "Starting FastAPI portal on port 8789..."
python Tools/volusia_data/portal_app.py &
PORTAL_PID=$!
sleep 3

# Check if portal is healthy
if curl -s http://127.0.0.1:8789/api/health > /dev/null 2>&1; then
    echo "✓ Portal is healthy"
else
    echo "✗ Portal failed to start"
    exit 1
fi

# Start cloudflared tunnel (if authenticated)
if command -v cloudflared &> /dev/null; then
    echo "Starting cloudflared tunnel..."
    
    # Check if tunnel exists
    if cloudflared tunnel list 2>/dev/null | grep -q "volusia-portal"; then
        echo "Reusing existing tunnel: volusia-portal"
    else
        echo "Creating new tunnel: volusia-portal"
        cloudflared tunnel create volusia-portal 2>/dev/null || true
    fi
    
    # Run tunnel
    cloudflared tunnel --url http://127.0.0.1:8789 run volusia-portal &
    TUNNEL_PID=$!
    echo "Tunnel started with PID: $TUNNEL_PID"
fi

echo ""
echo "=== Deployment Complete ==="
echo "Portal: http://127.0.0.1:8789"
echo "Health: http://127.0.0.1:8789/api/health"
echo "Indicators: http://127.0.0.1:8789/api/indicators"
echo ""
if [ -n "$TUNNEL_PID" ]; then
    echo "PIDs: Portal=$PORTAL_PID, Tunnel=$TUNNEL_PID"
else
    echo "PID: Portal=$PORTAL_PID"
fi