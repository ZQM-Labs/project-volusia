#!/usr/bin/env python3
"""
Project Volusia — Central Data Configuration
Single source of truth for all fetchers, portal, and pipeline.

Reads API keys from environment variables.
Never commit real keys to source control.
"""

import os
from pathlib import Path

# Base directories
ROOT = Path(__file__).resolve().parent.parent.parent  # Project-Volusia root
TOOLS_DIR = ROOT / "Tools"
DATA_DIR = ROOT / "Data"
CONTRIBUTION_DIR = ROOT / "CONTRIBUTION"

# API keys — read from env, NEVER hardcode
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
