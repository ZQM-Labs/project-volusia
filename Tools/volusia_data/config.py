#!/usr/bin/env python3
"""
Project Volusia — Central Data Configuration
Single source of truth for all fetchers, portal, and pipeline.

Reads API keys from environment variables, optionally populated from a
repo-root `.env` file (never commit real keys to source control; real
environment variables always take precedence over `.env` values).
"""

import os
from pathlib import Path

# Base directories
ROOT = Path(__file__).resolve().parent.parent.parent  # Project-Volusia root
TOOLS_DIR = ROOT / "Tools"
DATA_DIR = ROOT / "Data"
CONTRIBUTION_DIR = ROOT / "CONTRIBUTION"


def _load_dotenv(path: Path | None = None) -> dict:
    """Zero-dependency .env loader (no python-dotenv required).

    Parses KEY=VALUE lines (tolerates an optional ``export `` prefix,
    ``#`` comments, and single/double-quoted values) and applies them to
    ``os.environ``.

    Precedence: variables already present in the real environment always
    win, so CI secrets and shell exports override `.env` values.
    """
    env_file = path or (ROOT / ".env")
    loaded: dict = {}
    if not env_file.is_file():
        return loaded
    try:
        text = env_file.read_text(encoding="utf-8")
    except OSError:
        return loaded
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if not key or any(ch.isspace() for ch in key):
            continue
        if key in os.environ:
            continue  # real environment wins
        os.environ[key] = value
        loaded[key] = value
    return loaded


# Populate os.environ from .env (if present) BEFORE reading configuration,
# so every consumer (pipeline, portal, contribution API) sees the same
# resolved values.
_load_dotenv()

# API keys — read from env (or .env), NEVER hardcode
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "")
BLS_API_KEY = os.environ.get("BLS_API_KEY", "")
BEA_API_KEY = os.environ.get("BEA_API_KEY", "")
NOAA_API_KEY = os.environ.get("NOAA_API_KEY", "")  # NOAA is free, no key needed

# FIPS codes for Volusia County, FL
STATE_FIPS = "12"
COUNTY_FIPS = "127"
FULL_FIPS = f"{STATE_FIPS}{COUNTY_FIPS}"  # "12127"

# Database
DB_PATH = TOOLS_DIR / "volusia_data" / "volusia.db"

# Portal
PORTAL_HOST = os.environ.get("VOLUSIA_PORTAL_HOST", "127.0.0.1")
PORTAL_PORT = int(os.environ.get("VOLUSIA_PORTAL_PORT", "8789"))

# Contribution API
CONTRIBUTION_PORT = int(os.environ.get("VOLUSIA_CONTRIBUTION_PORT", "8790"))

# Pipeline
PIPELINE_LOG = TOOLS_DIR / "volusia_data" / "pipeline.log"
PIPELINE_CACHE = TOOLS_DIR / "volusia_data" / "cache"

# GitHub integration
GITHUB_REPO = os.environ.get("GITHUB_REPO", "ZQM-Computing/project-volusia")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # For CI/CD automation

# Contribution routing
CONTRIBUTION_EMAIL = os.environ.get("CONTRIBUTION_EMAIL", "contributions@zqmlabs.com")
CGB_ADMIN_EMAIL = os.environ.get("CGB_ADMIN_EMAIL", "cgb@zqmlabs.com")

# External site
EXTERNAL_SITE_URL = os.environ.get("EXTERNAL_SITE_URL", "https://volusia.zqmlabs.com")


# Validate keys at startup (non-fatal, just log)
def validate_keys() -> dict:
    """Check which API keys are configured. Returns status dict."""
    return {
        "census": bool(CENSUS_API_KEY),
        "bls": bool(BLS_API_KEY),
        "bea": bool(BEA_API_KEY),
        "noaa": True,  # NOAA doesn't require a key
        "all_configured": bool(CENSUS_API_KEY and BLS_API_KEY and BEA_API_KEY),
    }


if __name__ == "__main__":
    status = validate_keys()
    print("Project Volusia Configuration")
    print("-" * 40)
    print(f"Root: {ROOT}")
    print(f"DB: {DB_PATH}")
    print(f"Portal: {PORTAL_HOST}:{PORTAL_PORT}")
    print(f"Contribution API: :{CONTRIBUTION_PORT}")
    print(f"External site: {EXTERNAL_SITE_URL}")
    print()
    print("API Key Status:")
    for k, v in status.items():
        if k != "all_configured":
            print(f"  {k}: {'SET' if v else 'MISSING'}")
    print(f"  all_configured: {'YES' if status['all_configured'] else 'NO — some sources will fail'}")
