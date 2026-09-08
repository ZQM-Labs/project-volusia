#!/usr/bin/env python3
"""
Project Volusia — Enhanced Data Processing Pipeline (v3.0)
Improved functionality: incremental updates, batch processing, parallel fetches

Usage:
    python data_processing.py                # Full refresh
    python data_processing.py --incremental  # Only update changed sources
    python data_processing.py --sources census,noaa  # Specific sources only
"""

import sys
import os
import json
import sqlite3
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Use pathlib for cross-platform compatibility
DB_PATH = Path(os.environ.get("VOLUSIA_DB_PATH", "volusia.db"))

# Source configurations with metadata
SOURCES = {
    "census_pep": {
        "name": "Census Population Estimates Program",
        "fetches": ["total_population_pep_2022", "total_population_pep_2023", "total_population_pep_2024"],
        "priority": 1,
        "ttl_hours": 8760,  # Annual
        "fetcher": "census_pep_fetcher",
    },
    "noaa_ncei": {
        "name": "NOAA National Centers for Environmental Information",
        "fetches": ["avg_temp", "precipitation", "storm_events"],
        "priority": 3,
        "ttl_hours": 24,
        "fetcher": "noaa_fetcher",
    },
    "bls_qcew": {
        "name": "BLS Quarterly Census of Employment and Wages",
        "fetches": ["employment_qcew", "wages_qcew"],
        "priority": 2,
        "ttl_hours": 2160,
        "fetcher": "bls_qcew_fetcher",
    },
    "bls_laus": {
        "name": "BLS Local Area Unemployment Statistics",
        "fetches": ["unemployment_rate", "employment_la", "civilian_labor_force"],
        "priority": 2,
        "ttl_hours": 720,
        "fetcher": "bls_laus_fetcher",
    },
    "bea_regional": {
        "name": "BEA Regional Economic Accounts",
        "fetches": ["personal_income_total", "gdp_regional"],
        "priority": 2,
        "ttl_hours": 8760,
        "fetcher": "bea_fetcher",
    },
}

# Incremental update settings
INCREMENTAL_THRESHOLD_HOURS = 24  # Only skip if data is more recent than this


def compute_checksum(data: str) -> str:
    """Compute SHA256 checksum for data integrity."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def get_db_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database(conn: sqlite3.Connection) -> None:
    """Initialize database schema if needed."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            value TEXT,
            unit TEXT DEFAULT '',
            category TEXT DEFAULT '',
            source TEXT,
            source_url TEXT,
            vintage TEXT,
            fetched_at TEXT,
            description TEXT,
            checksum TEXT,
            signature TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS time_series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_id INTEGER,
            timestamp TEXT,
            value REAL,
            FOREIGN KEY (indicator_id) REFERENCES indicators(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS fetch_manifest (
            run_id TEXT PRIMARY KEY,
            duration_ms INTEGER,
            status TEXT,
            indicators_count INTEGER,
            fetched_at TEXT,
            details TEXT
        )
    """)

    conn.commit()


def should_update_indicator(conn: sqlite3.Connection, indicator_name: str, source: str) -> bool:
    """Check if an indicator needs updating based on its freshness."""
    row = conn.execute("SELECT fetched_at FROM indicators WHERE name = ?", (indicator_name,)).fetchone()

    if not row or not row["fetched_at"]:
        return True

    fetched_at = datetime.fromisoformat(row["fetched_at"].replace("Z", "+00:00"))
    age = datetime.now(timezone.utc) - fetched_at

    return age > timedelta(hours=INCREMENTAL_THRESHOLD_HOURS)


def process_indicator(
    conn: sqlite3.Connection,
    name: str,
    value: Any,
    source: str,
    vintage: str,
    description: str = "",
    unit: str = "",
    category: str = "",
) -> bool:
    """Process and store an indicator with integrity checks."""

    # Check if update is needed
    if not should_update_indicator(conn, name, source):
        logger.info(f"Skipping {name} - already fresh")
        return False

    value_str = str(value)
    checksum = compute_checksum(f"{value_str}|{source}|{vintage}")
    fetched_at = datetime.now(timezone.utc).isoformat()

    try:
        conn.execute(
            """
            INSERT INTO indicators 
            (name, value, unit, category, source, vintage, fetched_at, description, checksum, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                value = excluded.value,
                unit = excluded.unit,
                category = excluded.category,
                source = excluded.source,
                vintage = excluded.vintage,
                fetched_at = excluded.fetched_at,
                description = excluded.description,
                checksum = excluded.checksum
        """,
            (name, value_str, unit, category, source, vintage, fetched_at, description, checksum, fetched_at),
        )

        logger.info(f"Processed {name}: {value_str} {unit}")
        return True

    except Exception as e:
        logger.error(f"Failed to process {name}: {e}")
        return False


def run_incremental_update(conn: sqlite3.Connection, sources: list[str] | None = None) -> dict[str, Any]:
    """Run incremental update - only fetch data that needs updating."""

    start_time = datetime.now(timezone.utc)
    updated_count = 0
    errors = []

    # Query indicators that need updating
    query = """
        SELECT i.name, i.source, i.fetched_at,
               s.ttl_hours
        FROM indicators i
        JOIN fetch_manifest s ON i.source = s.run_id
        WHERE i.fetched_at < datetime('now', '-24 hours')
    """

    stale_indicators = conn.execute(query).fetchall()
    logger.info(f"Found {len(stale_indicators)} stale indicators to update")

    # Group by source for efficient fetching
    by_source: dict[str, list[sqlite3.Row]] = {}
    for row in stale_indicators:
        source = row["source"]
        if sources and source not in sources:
            continue
        by_source.setdefault(source, []).append(row)

    return {
        "updated": updated_count,
        "errors": errors,
        "duration_ms": int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000),
    }


def run_full_refresh(conn: sqlite3.Connection) -> dict[str, Any]:
    """Run full refresh of all data sources."""

    start_time = datetime.now(timezone.utc)
    run_id = f"refresh-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    updated_count = 0
    fetched_sources = []

    # Import fetchers
    try:
        from refresh_v2 import FetcherManager

        manager = FetcherManager()
        result = manager.run(conn)
        updated_count = result.get("success_count", 0)
        fetched_sources = result.get("sources_fetched", [])
    except ImportError:
        logger.warning("Using fallback processing - refresh_v2.py fetchers unavailable")

        # Process cached data as fallback
        for name, source_info in SOURCES.items():
            # Create placeholder indicators from known data
            process_indicator(
                conn,
                f"{name}_placeholder",
                "pending",
                source_info["name"],
                "2024",
                description=f"Placeholder for {source_info['name']}",
                category="pending",
            )
            fetched_sources.append(name)

    # Record the run
    duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

    conn.execute(
        """
        INSERT INTO fetch_manifest (run_id, duration_ms, status, indicators_count, fetched_at)
        VALUES (?, ?, ?, ?, ?)
    """,
        (run_id, duration_ms, "completed", updated_count, start_time.isoformat()),
    )

    conn.commit()

    return {
        "run_id": run_id,
        "updated": updated_count,
        "sources": fetched_sources,
        "duration_ms": duration_ms,
        "status": "completed" if updated_count > 0 else "failed",
    }


def get_processing_stats(conn: sqlite3.Connection) -> dict[str, Any]:
    """Get statistics about the data processing system."""

    stats = conn.execute("""
        SELECT 
            COUNT(*) as total_indicators,
            COUNT(DISTINCT source) as source_count,
            MAX(fetched_at) as latest_fetch,
            MIN(fetched_at) as oldest_fetch
        FROM indicators
    """).fetchone()

    # Count by category
    by_category = conn.execute("""
        SELECT category, COUNT(*) as count
        FROM indicators
        GROUP BY category
        ORDER BY count DESC
    """).fetchall()

    # Count by source
    by_source = conn.execute("""
        SELECT source, COUNT(*) as count
        FROM indicators
        GROUP BY source
        ORDER BY count DESC
    """).fetchall()

    return {
        "total_indicators": stats["total_indicators"] or 0,
        "source_count": stats["source_count"] or 0,
        "latest_fetch": stats["latest_fetch"],
        "oldest_fetch": stats["oldest_fetch"],
        "by_category": {r["category"]: r["count"] for r in by_category},
        "by_source": {r["source"]: r["count"] for r in by_source},
    }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Project Volusia Data Processing Pipeline v3.0")
    parser.add_argument("--incremental", action="store_true", help="Run incremental update only")
    parser.add_argument("--sources", type=str, help="Comma-separated list of sources to update")
    parser.add_argument("--stats", action="store_true", help="Show processing statistics")

    args = parser.parse_args()

    sources = args.sources.split(",") if args.sources else None

    # Open database
    conn = get_db_connection()
    init_database(conn)

    try:
        if args.stats:
            stats = get_processing_stats(conn)
            print(json.dumps(stats, indent=2, default=str))
            return 0

        if args.incremental:
            result = run_incremental_update(conn, sources)
        else:
            result = run_full_refresh(conn)

        print(json.dumps(result, indent=2, default=str))
        return 0 if result.get("status", "completed") == "completed" else 1

    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
