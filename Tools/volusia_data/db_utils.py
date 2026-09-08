"""Database utilities for Project Volusia.

Provides connection management, query execution, and data access functions
for the SQLite database used across the portal and API modules.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

# Default database path - can be overridden via environment variable
DEFAULT_DB_PATH = Path(__file__).resolve().parent / "volusia.db"
DB_PATH = Path(os.environ.get("VOLUSIA_DB_PATH", str(DEFAULT_DB_PATH)))


def get_db_path() -> Path:
    """Get the current database path."""
    return DB_PATH


def set_db_path(path: Path) -> None:
    """Set the database path (useful for testing)."""
    global DB_PATH
    DB_PATH = path


def execute_query(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    """Execute a query and return results as a list of dicts.

    Returns an empty list if the database doesn't exist or the table is missing.
    """
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(query, params)
        return [dict(r) for r in cur.fetchall()]
    except sqlite3.OperationalError:
        return []  # Table doesn't exist yet
    finally:
        conn.close()


def execute_query_one(query: str, params: tuple = ()) -> dict[str, Any] | None:
    """Execute a query and return a single result dict, or None if no results."""
    rows = execute_query(query, params)
    return rows[0] if rows else None


def execute_insert(query: str, params: tuple = ()) -> int | None:
    """Execute an INSERT query and return the last row ID, or None on failure."""
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.execute(query, params)
        conn.commit()
        return cur.lastrowid
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def execute_update(query: str, params: tuple = ()) -> int:
    """Execute an UPDATE/DELETE query and return the number of affected rows."""
    if not DB_PATH.exists():
        return 0
    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.execute(query, params)
        conn.commit()
        return cur.rowcount
    except sqlite3.Error:
        return 0
    finally:
        conn.close()


def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    if not DB_PATH.exists():
        return False
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
    return execute_query_one(query, (table_name,)) is not None


def get_table_count(table_name: str) -> int:
    """Get the row count of a table, or 0 if it doesn't exist."""
    row = execute_query_one(f"SELECT COUNT(*) as cnt FROM {table_name}")
    return row["cnt"] if row else 0


# ── Indicator-specific queries ────────────────────────────────────────────────


def get_indicators(
    limit: int = 50,
    offset: int = 0,
    category: str | None = None,
    source: str | None = None,
) -> list[dict[str, Any]]:
    """Get indicators with optional filtering and pagination."""
    query = "SELECT * FROM indicators WHERE 1=1"
    params: list[Any] = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if source:
        query += " AND source = ?"
        params.append(source)

    query += " ORDER BY category, name LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    return execute_query(query, tuple(params))


def get_indicator_by_name(name: str) -> dict[str, Any] | None:
    """Get a single indicator by name."""
    return execute_query_one("SELECT * FROM indicators WHERE name = ?", (name,))


def get_latest_freshness() -> str:
    """Get the latest fetch timestamp across all indicators."""
    row = execute_query_one("SELECT MAX(fetched_at) as latest FROM indicators")
    if row and row.get("latest"):
        return row["latest"]
    return "N/A"


def get_indicator_count() -> int:
    """Get total number of indicators."""
    return get_table_count("indicators")


def get_source_freshness_summary() -> dict[str, dict[str, Any]]:
    """Get per-source freshness information."""
    rows = execute_query("""
        SELECT source, MAX(fetched_at) as latest, COUNT(*) as cnt
        FROM indicators GROUP BY source ORDER BY source
    """)
    return {r["source"]: {"latest": r["latest"], "count": r["cnt"]} for r in rows}


def get_categories() -> list[str]:
    """Get all distinct categories."""
    rows = execute_query("SELECT DISTINCT category FROM indicators ORDER BY category")
    return [r["category"] for r in rows if r["category"]]


def get_sources() -> list[str]:
    """Get all distinct sources."""
    rows = execute_query("SELECT DISTINCT source FROM indicators ORDER BY source")
    return [r["source"] for r in rows if r["source"]]
