"""
Project Volusia Data Backend
============================
Fetchers, database layer, and portal for Volusia County open data.

Key modules:
    - refresh_v2: Data pipeline and fetchers
    - contribution_api: Contribution submission API
    - portal_app: Main portal web application
    - portal_contribute: Contribution web form
    - charts: Chart generation utilities
    - db_utils: Database helper functions
    - config: Configuration and environment variables
    - systems_integration: Cross-system integration checks
"""

__version__ = "0.1.0"

# Export key functions for convenient imports
from . import db_utils
from . import page_templates
from .config import DB_PATH, PORTAL_PORT, CONTRIBUTION_PORT
from .refresh_v2 import init_db, upsert_indicator, get_db

__all__ = [
    "__version__",
    "DB_PATH",
    "PORTAL_PORT",
    "CONTRIBUTION_PORT",
    "init_db",
    "upsert_indicator",
    "get_db",
    "db_utils",
    "page_templates",
]
