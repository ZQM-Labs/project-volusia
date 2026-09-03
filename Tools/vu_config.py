"""Project Volusia — centralized config for API keys and paths.

Reads sensitive values from environment variables so they never live in
source code.  Copy .env.example -> .env and fill in the keys.
"""

import os
from pathlib import Path

# Base directory for this project (where this file lives)
BASE_DIR = Path(__file__).resolve().parent.parent  # .../Project-Volusia/Tools

# ── Census Bureau API ──────────────────────────────────────────────────
# Signup: https://api.census.gov/data/key_signup.html
# Email must end in .com / .net / .org / .gov / .edu
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "").strip()
CENSUS_KEY_SET = bool(CENSUS_API_KEY)

# ── Bureau of Labor Statistics API ─────────────────────────────────────
# Signup: https://data.bls.gov/registrationEngine/
# Key arrives via email from labstat@bls.gov
BLS_API_KEY = os.environ.get("BLS_API_KEY", "").strip()
BLS_KEY_SET = bool(BLS_API_KEY)

# ── Bureau of Economic Analysis API ────────────────────────────────────
# Signup: https://apps.bea.gov/api/signup/
# Returns a 36-character UserId (XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX)
BEA_API_KEY = os.environ.get("BEA_API_KEY", "").strip()
BEA_KEY_SET = bool(BEA_API_KEY)

# ── Derived flags ──────────────────────────────────────────────────────
ALL_KEYS_SET = CENSUS_KEY_SET and BLS_KEY_SET and BEA_KEY_SET

# ── Data directory ─────────────────────────────────────────────────────
DATA_DIR = BASE_DIR / "Data"
MAP_DIR = BASE_DIR / "Map"
REPORT_DIR = BASE_DIR / "Report"
METHOD_DIR = BASE_DIR / "Methodology"
TOOLS_DIR = BASE_DIR / "Tools"

# ── Database ───────────────────────────────────────────────────────────
DB_PATH = TOOLS_DIR / "volusia_data" / "volusia.db"

# ── Portal ─────────────────────────────────────────────────────────────
PORTAL_HOST = os.environ.get("VOLUSIA_PORTAL_HOST", "127.0.0.1")
PORTAL_PORT = int(os.environ.get("VOLUSIA_PORTAL_PORT", "8789"))

# ── Volusia County FIPS ────────────────────────────────────────────────
STATE_FIPS = "12"
COUNTY_FIPS = "12127"  # full 5-digit FIPS
COUNTY_FIPS_3DIGIT = "127"
