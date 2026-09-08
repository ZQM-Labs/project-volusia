#!/usr/bin/env python3
"""
Project Volusia — Schema Migration Script
Add new columns and tables to existing database.
Run this before using refresh_v2.py with new features.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "volusia.db"


def migrate():
    if not DB_PATH.exists():
        print("Database not found - will be created by refresh_v2.py")
        return

    conn = sqlite3.connect(str(DB_PATH))

    # Check current schema
    cursor = conn.execute("PRAGMA table_info(indicators)")
    cols = {row[1] for row in cursor.fetchall()}

    print(f"Current indicators columns: {cols}")

    # Add new columns if missing
    if "checksum" not in cols:
        print("Adding checksum column...")
        conn.execute("ALTER TABLE indicators ADD COLUMN checksum TEXT")

    if "signature" not in cols:
        print("Adding signature column...")
        conn.execute("ALTER TABLE indicators ADD COLUMN signature TEXT")

    # Check for fetch_manifest table
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fetch_manifest'")
    if not cursor.fetchone():
        print("Creating fetch_manifest table...")
        conn.execute("""
            CREATE TABLE fetch_manifest (
                fetched_at TEXT PRIMARY KEY DEFAULT (datetime('now')),
                run_id TEXT,
                duration_ms INTEGER,
                status TEXT,
                indicators_count INTEGER
            )
        """)

    conn.commit()
    conn.close()
    print("Migration complete!")


if __name__ == "__main__":
    migrate()
