"""
Config loader for Project Volusia data fetchers.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# API keys
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "219da6650a20b62aeddf68859781e2ba45580569").strip()
BLS_API_KEY = os.environ.get("BLS_API_KEY", "114ae7be1cef4085b7a756f201690ec7").strip()
BEA_API_KEY = os.environ.get("BEA_API_KEY", "49ED5E15-6093-4A4E-ABBC-83E7BC38B324").strip()

# FIPS codes
STATE_FIPS = "12"
COUNTY_FIPS = "127"
FULL_FIPS = STATE_FIPS + COUNTY_FIPS  # "12127"

# Database
DB_PATH = Path(__file__).resolve().parent / "volusia.db"

# Portal
PORTAL_HOST = os.environ.get("VOLUSIA_PORTAL_HOST", "127.0.0.1")
PORTAL_PORT = int(os.environ.get("VOLUSIA_PORTAL_PORT", "8789"))
