# Deployment Guide — Project Volusia

> How to deploy Project Volusia backend and frontend.

---

## Overview

Project Volusia has two deployment targets:

1. **Backend** — ZQM-Node-4 (192.168.1.219) via Cloudflare Tunnel
2. **Frontend** — GitHub Pages (https://volusia.zqmlabs.com)

---

## Backend Deployment

### Prerequisites

- Python 3.11+
- SQLite 3
- Cloudflare Tunnel (cloudflared)

### Local Development

```bash
# Clone repository
git clone https://github.com/ZQM-Labs/project-volusia.git
cd project-volusia

# Install dependencies
pip install fastapi uvicorn matplotlib requests

# Run portal
cd Tools/volusia_data
python portal_app.py
```

### Production Deployment (ZQM-Node-4)

1. **SSH into ZQM-Node-4**:
   ```bash
   ssh root@192.168.1.219
   ```

2. **Clone/Update repository**:
   ```bash
   cd /opt/project-volusia
   git pull origin main
   pip install -r requirements.txt
   ```

3. **Run with systemd** (recommended):
   ```ini
   # /etc/systemd/system/volusia-portal.service
   [Unit]
   Description=Project Volusia Portal
   After=network.target

   [Service]
   Type=simple
   User=volusia
   WorkingDirectory=/opt/project-volusia/Tools/volusia_data
   ExecStart=/usr/bin/python portal_app.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

4. **Enable and start**:
   ```bash
   sudo systemctl enable volusia-portal
   sudo systemctl start volusia-portal
   ```

### Cloudflare Tunnel Setup

1. **Install cloudflared**:
   ```bash
   # Windows
   choco install cloudflared

   # Linux
   curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
   chmod +x /usr/local/bin/cloudflared
   ```

2. **Configure tunnel**:
   ```yaml
   # ~/.cloudflared/config.yml
   tunnel: volusia
   credentials-file: ~/.cloudflared/volusia.json

   ingress:
     - hostname: volusia.zqmlabs.com
       service: http://localhost:80
       originRequest:
         noTLSVerify: true
     - service: http://localhost:80
   ```

3. **Run tunnel**:
   ```bash
   cloudflared tunnel --config ~/.cloudflared/config.yml run
   ```

---

## Frontend Deployment

### GitHub Pages (Automatic)

1. **Push to master**:
   ```bash
   git add .
   git commit -m "Update frontend"
   git push origin master
   ```

2. **GitHub Actions** automatically:
   - Installs dependencies
   - Builds the project
   - Deploys to `gh-pages` branch
   - Updates https://volusia.zqmlabs.com

### Manual Deployment

1. **Build**:
   ```bash
   npm install
   npm run build
   ```

2. **Deploy to gh-pages**:
   ```bash
   # Using peaceiris/actions-gh-pages
   # Or manually:
   cd dist
   git init
   git add -A
   git commit -m "Deploy"
   git push -f git@github.com:ZQM-Computing/volusia-portal.git master:gh-pages
   ```

---

## Docker Deployment

### Build Image

```bash
docker build -t zqmcomputing/volusia-portal:latest .
```

### Run Container

```bash
docker run -d   --name volusia-portal   -p 8080:80   --restart unless-stopped   zqmcomputing/volusia-portal:latest
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  portal:
    build: .
    ports:
      - "8080:80"
    restart: unless-stopped
    volumes:
      - ./data:/usr/share/nginx/html/data:ro
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VOLUSIA_DB_PATH` | `Tools/volusia_data/volusia.db` | SQLite database path |
| `VOLUSIA_PORT` | `8789` | Portal port |
| `VOLUSIA_HOST` | `0.0.0.0` | Portal host |
| `CENSUS_API_KEY` | (empty) | Census API key (optional) |
| `BLS_API_KEY` | (empty) | BLS API key (optional) |
| `BEA_API_KEY` | (empty) | BEA API key (optional) |

---

## Monitoring

### Health Check

```bash
# Backend health
curl http://localhost:8790/api/health

# Frontend health
curl -I https://volusia.zqmlabs.com
```

### Logs

```bash
# Backend logs
sudo journalctl -u volusia-portal -f

# GitHub Actions logs
# https://github.com/ZQM-Computing/volusia-portal/actions
```

---

## Troubleshooting

### Backend not starting
1. Check Python version: `python --version` (need 3.11+)
2. Check dependencies: `pip install -r requirements.txt`
3. Check port: `netstat -ano | findstr :8789`

### Frontend not updating
1. Check GitHub Actions status
2. Verify CNAME file exists in `gh-pages` branch
3. Check DNS: `nslookup volusia.zqmlabs.com`

### Cloudflare Tunnel down
1. Check tunnel status: `cloudflared tunnel list`
2. Restart tunnel: `cloudflared tunnel run volusia`

---

**Last Updated**: 2026-09-08
**Maintainer**: ZQM Labs / ZQM Computing
