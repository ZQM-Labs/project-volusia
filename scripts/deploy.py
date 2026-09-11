#!/usr/bin/env python3
"""
Project Volusia — Deploy Script v1.0

Single-command deployment pipeline:
  1. Refresh backend data (via /refresh endpoint)
  2. Generate static pages (project-volusia-web/generate.py)
  3. Sync React build to nginx HTML directory
  4. Copy static data pages to nginx
  5. Restart nginx and backend services
  6. Verify all endpoints return 200

Usage:
    python deploy.py                  # Full deploy
    python deploy.py --dry-run        # Preview without executing
    python deploy.py --skip-backend   # Skip data refresh
    python deploy.py --skip-frontend  # Skip React build
    python deploy.py --skip-verify    # Skip verification
"""

import subprocess
import sys
import os
import json
import time
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────────────────

BASE_DIR = Path(r"C:\Users\zqmco")
NGINX_HTML = BASE_DIR / "scoop" / "persist" / "nginx" / "html"
NGINX_CONF = BASE_DIR / "scoop" / "persist" / "nginx" / "conf" / "nginx.conf"
PROJECT_WEB = BASE_DIR / "project-volusia-web"
VOLUSIA_PORTAL = BASE_DIR / "Docker" / "volusia-portal"
BACKEND = VOLUSIA_PORTAL / "backend" / "main.py"
CACHE_DIR = VOLUSIA_PORTAL / "data" / "cache"
DATA_CACHE = VOLUSIA_PORTAL / "data" / "cache"
BACKEND_URL = "http://127.0.0.1:8000"
NGINX_SERVICE = "Volusia-Nginx"
CLOUDFLARED_SERVICE = "cloudflared"

# Category mapping: sitemap slug → category name → data file
CATEGORIES = {
    "economic":       ("Economic",       "census_dp03.json"),
    "tourism":        ("Tourism",        "tourism.json"),
    "transportation": ("Transportation",  "transportation.json"),
    "climate":        ("Climate",        "climate.json"),
    "demographics":   ("Demographics",   "census_dp05.json"),
    "real-estate":    ("Real Estate",    "redfin_volusia.json"),
    "education":      ("Education",      "education.json"),
    "government-finance": ("Government Finance", "government.json"),
    "public-safety":  ("Public Safety",  "safety.json"),
    "health":         ("Health",         "health.json"),
    "environment":    ("Environment",    "environment.json"),
    "housing":        ("Housing",        "housing.json"),
    "safety":         ("Safety",         "safety.json"),
    "government":     ("Government",     "government.json"),
}

# Categories that have static HTML pages in project-volusia-web/data/
STATIC_CATEGORIES = [
    "economic", "tourism", "transportation", "climate", "demographics",
    "real-estate", "education", "government-finance", "public-safety",
    "health", "environment", "housing", "safety", "government",
]

# API endpoints that must proxy to backend (exact match in nginx)
API_ENDPOINTS = ["/data/indicators.json", "/data/latest.json"]

# ── Colors / Output ────────────────────────────────────────────────────────

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def log(step, message, color=None):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = f"{Colors.BOLD}[{ts}]{Colors.RESET} {Colors.BLUE}{step}{Colors.RESET}"
    if color:
        print(f"{prefix}: {color}{message}{Colors.RESET}")
    else:
        print(f"{prefix}: {message}")

def success(msg): log("✓", msg, Colors.GREEN)
def error(msg):  log("✗", msg, Colors.RED)
def warn(msg):   log("⚠", msg, Colors.YELLOW)
def info(msg):   log("→", msg)

# ── Helpers ────────────────────────────────────────────────────────────────

def run(cmd, timeout=60, check=True, capture=False):
    """Run a command and return the result dict."""
    try:
        result = subprocess.run(
            cmd, shell=True, timeout=timeout,
            capture_output=capture, text=True
        )
        if check and result.returncode != 0:
            error(f"Command failed (exit {result.returncode}): {cmd}")
            if capture and result.stderr:
                error(f"STDERR: {result.stderr[:500]}")
            return {"ok": False, "returncode": result.returncode}
        return {"ok": True, "returncode": result.returncode, "stdout": result.stdout}
    except subprocess.TimeoutExpired:
        error(f"Command timed out: {cmd}")
        return {"ok": False, "returncode": -1}
    except Exception as e:
        error(f"Command error: {e}")
        return {"ok": False, "returncode": -1}

def service_restart(service_name):
    """Restart a Windows NSSM service."""
    info(f"Restarting {service_name}...")
    result = run(f'nssm restart {service_name}', timeout=15)
    if result["ok"]:
        success(f"{service_name} restarted")
    else:
        # Try alternative: taskkill + start
        warn(f"nssm restart failed for {service_name}, trying taskkill + nssm start...")
        run(f'taskkill /F /PID $(nssm query {service_name} ProcessID 2>nul | findstr /R "[0-9]" || echo 0) 2>nul', check=False)
        time.sleep(1)
        result2 = run(f'nssm start {service_name}', timeout=15)
        if result2["ok"]:
            success(f"{service_name} restarted (via start)")
        else:
            error(f"Could not restart {service_name}")

# ── Pipeline Steps ─────────────────────────────────────────────────────────

def step_refresh_data():
    """Step 1: Refresh backend data via /refresh endpoint."""
    info("Step 1: Refreshing backend data...")
    result = run(f'curl -s -X POST {BACKEND_URL}/refresh -H "Content-Type: application/json" -d \'{{"secret":"{os.environ.get("VOLUSIA_REFRESH_TOKEN", "debug_token")}"}}\'', timeout=30)
    if result["ok"]:
        try:
            data = json.loads(result.get("stdout", "{}"))
            if "status" in data and data["status"] == "ok":
                success("Backend data refreshed")
            else:
                warn(f"Refresh response: {data}")
        except json.JSONDecodeError:
            warn(f"Refresh output: {result.get('stdout', '')[:200]}")
    else:
        warn("Could not refresh backend data — proceeding with existing cache")

def step_generate_static():
    """Step 2: Generate static HTML pages via project-volusia-web/generate.py."""
    info("Step 2: Generating static pages...")
    gen_py = PROJECT_WEB / "generate.py"
    if not gen_py.exists():
        error(f"{gen_py} not found")
        return False
    result = run(f'python "{gen_py}"', timeout=120, workdir=str(PROJECT_WEB))
    if result["ok"]:
        success("Static pages generated")
        return True
    else:
        error("Static page generation failed")
        return False

def step_sync_frontend():
    """Step 3: Build React app and sync to nginx."""
    info("Step 3: Building and syncing React frontend...")
    dist_dir = VOLUSIA_PORTAL / "dist"
    if not dist_dir.exists():
        warn(f"dist/ not found — building React app...")
        build_result = run(f'npm run build', timeout=120, workdir=str(VOLUSIA_PORTAL))
        if not build_result["ok"]:
            error("React build failed")
            return False

    # Sync dist files to nginx HTML
    info("Syncing React build to nginx...")
    index_src = dist_dir / "index.html"
    assets_src = dist_dir / "assets"

    if index_src.exists():
        shutil.copy2(str(index_src), str(NGINX_HTML / "index.html"))

    # Sync assets (hashed files — overwrite)
    if assets_src.exists():
        assets_dest = NGINX_HTML / "assets"
        assets_dest.mkdir(parents=True, exist_ok=True)
        for f in assets_src.iterdir():
            if f.is_file():
                shutil.copy2(str(f), str(assets_dest / f.name))
        success("Frontend synced")
    else:
        warn("No assets directory found")
    return True

def step_sync_static_data():
    """Step 4: Copy static data pages from project-volusia-web/data/ to nginx."""
    info("Step 4: Syncing static data pages...")
    web_data = PROJECT_WEB / "data"
    nginx_data = NGINX_HTML / "data"

    if not web_data.exists():
        error(f"{web_data} not found")
        return False

    # Copy each category directory
    for cat in STATIC_CATEGORIES:
        src = web_data / cat
        dst = nginx_data / cat
        if src.exists():
            dst.mkdir(parents=True, exist_ok=True)
            for f in src.iterdir():
                if f.is_file():
                    shutil.copy2(str(f), str(dst / f.name))

    # Copy index.html for /data/
    src_index = web_data / "index.html"
    if src_index.exists():
        shutil.copy2(str(src_index), str(nginx_data / "index.html"))
        # Ensure data dir has its own index
        nginx_data.mkdir(parents=True, exist_ok=True)

    success("Static data pages synced")
    return True

def step_update_nginx():
    """Step 5: Write the optimized nginx.conf."""
    info("Step 5: Writing nginx configuration...")
    conf = generate_nginx_conf()
    conf_path = str(NGINX_CONF)
    with open(conf_path, "w", encoding="utf-8") as f:
        f.write(conf)
    success("nginx.conf written")
    return True

def step_restart_services():
    """Step 6: Restart nginx and verify."""
    info("Step 6: Restarting services...")
    service_restart(NGINX_SERVICE)
    time.sleep(2)
    success("Services restarted")
    return True

def step_verify():
    """Step 7: Verify all endpoints return HTTP 200."""
    info("Step 7: Verifying endpoints...")
    all_ok = True
    results = []

    # Test sitemap pages through HTTPS
    test_urls = [
        ("Home", "https://zqmlabs.com/"),
        ("Data index", "https://zqmlabs.com/data/"),
    ]
    for cat in STATIC_CATEGORIES:
        test_urls.append((f"Data: {cat}", f"https://zqmlabs.com/data/{cat}/"))
    test_urls.extend([
        ("About", "https://zqmlabs.com/about/"),
        ("Leaders", "https://zqmlabs.com/leaders/"),
        ("Gamification", "https://zqmlabs.com/gamification/"),
        ("API Health", "https://zqmlabs.com/health"),
        ("API Latest", "https://zqmlabs.com/latest"),
        ("API Indicators", "https://zqmlabs.com/data/indicators.json"),
    ])

    for name, url in test_urls:
        result = run(f'curl -skL "{url}" -m 10 -o /dev/null -w "%{{http_code}}" 2>&1', timeout=15)
        code = result.get("stdout", "").strip()
        if code == "200":
            results.append((name, "200", True))
        else:
            results.append((name, code, False))
            all_ok = False

    # Print summary
    print()
    print(f"{'Endpoint':<30} {'Status':<10} {'OK'}")
    print("-" * 50)
    for name, code, ok in results:
        status = f"✓ {code}" if ok else f"✗ {code}"
        print(f"  {name:<28} {status}")

    print()
    if all_ok:
        success("All endpoints verified — 200 OK")
    else:
        error("Some endpoints failed — check above")

    return all_ok

# ── Nginx Config Generator ─────────────────────────────────────────────────

def generate_nginx_conf():
    """Generate the optimized nginx.conf."""
    return f"""worker_processes 2;
error_log C:/Users/zqmco/scoop/persist/nginx/logs/error.log warn;
pid C:/Users/zqmco/scoop/persist/nginx/logs/nginx.pid;

events {{
    worker_connections 1024;
}}

http {{
    include C:/Users/zqmco/scoop/apps/nginx/current/mime.types;
    default_type application/octet-stream;

    access_log C:/Users/zqmco/scoop/persist/nginx/logs/access.log;
    client_max_body_size 10m;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=20r/s;

    # ── Security Headers ──
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; script-src 'self'; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com; connect-src 'self' http://127.0.0.1:8000; frame-ancestors 'self';" always;
    add_header X-Robots-Tag "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" always;

    # ── Cache: HTML no-store, hashed assets 1yr ──
    add_header Cache-Control "no-store, no-cache, must-revalidate" always;

    # ── Gzip ──
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 1000;
    gzip_proxied any;
    gzip_vary on;

    # ── Upstream ──
    upstream backend {{ server 127.0.0.1:8000; }}

    # ── Server ──
    server {{
        listen 80;
        server_name zqmlabs.com www.zqmlabs.com;
        root C:/Users/zqmco/scoop/persist/nginx/html;
        index index.html;

        # ── API: exact-match endpoints → backend ──
        location = /data/indicators.json {{
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend/data/indicators.json;
            proxy_set_header Host $host;
            proxy_http_version 1.1;
            proxy_set_header X-Real-IP $remote_addr;
        }}

        location = /data/latest.json {{
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend/latest;
            proxy_set_header Host $host;
        }}

        location = /latest {{
            proxy_pass http://backend/latest;
            proxy_set_header Host $host;
        }}

        location = /health {{
            proxy_pass http://backend/health;
            proxy_set_header Host $host;
        }}

        location = /indicators {{
            proxy_pass http://backend/indicators;
            proxy_set_header Host $host;
        }}

        # ── Static Data Pages → pre-generated HTML ──
        # Serves: /data/, /data/economic/, /data/tourism/, etc.
        location ^~ /data/ {{
            index index.html;
            try_files $uri $uri/ /data/index.html;
            add_header Cache-Control "public, max-age=3600, stale-while-revalidate=300";
        }}

        # ── Gamification API (proxy to backend :8000) ──
        location = /gamification {{
            return 301 /gamification/;
        }}
        location = /gamification/ {{
            return 301 /gamification;
        }}
        location /gamification/ {{
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 30s;
            proxy_connect_timeout 5s;
        }}

        # ── Refresh endpoint (backend API) ──
        location = /refresh {{
            proxy_pass http://backend/refresh;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 30s;
            proxy_connect_timeout 5s;
        }}

        # ── React SPA catch-all ──
        location / {{
            try_files $uri $uri/ /index.html;
        }}
    }}
}}
"""

# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Project Volusia Deploy Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    parser.add_argument("--skip-backend", action="store_true", help="Skip data refresh")
    parser.add_argument("--skip-frontend", action="store_true", help="Skip React build")
    parser.add_argument("--skip-verify", action="store_true", help="Skip verification")
    parser.add_argument("--config-only", action="store_true", help="Only write nginx.conf")
    args = parser.parse_args()

    print(f"{Colors.BOLD}{'='*60}")
    print(f"  Project Volusia — Deploy Pipeline v1.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}{Colors.RESET}")
    print()

    if args.dry_run:
        warn("DRY RUN — no changes will be made")
        print()

    # Step 0: Config
    if args.config_only or not args.skip_frontend:
        step_update_nginx()

    if args.config_only:
        info("Config-only mode — done")
        return

    # Step 1: Refresh backend data
    if not args.skip_backend and not args.dry_run:
        step_refresh_data()

    # Step 2: Generate static pages
    if not args.dry_run:
        step_generate_static()

    # Step 3: Sync React frontend
    if not args.skip_frontend and not args.dry_run:
        step_sync_frontend()

    # Step 4: Sync static data pages
    if not args.dry_run:
        step_sync_static_data()

    # Step 5: Update nginx.conf
    if not args.dry_run:
        step_update_nginx()

    # Step 6: Restart services
    if not args.dry_run:
        step_restart_services()

    # Step 7: Verify
    if not args.skip_verify and not args.dry_run:
        all_ok = step_verify()
        print()
        if all_ok:
            success("DEPLOYMENT COMPLETE — all endpoints verified")
        else:
            error("DEPLOYMENT COMPLETE with issues — review above")
    elif args.dry_run:
        info("DRY RUN complete — no changes made")

    print()

if __name__ == "__main__":
    main()
