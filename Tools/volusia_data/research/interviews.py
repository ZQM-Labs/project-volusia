#!/usr/bin/env python3
"""
Project Volusia — Stakeholder Interview Tracking System
Tracks interviews, themes, needs, and follow-ups across all four constituencies.

Usage:
    python Tools/volusia_data/research/interviews.py --add --name "Jane Doe" --role business_owner
    python Tools/volusia_data/research/interviews.py --list
    python Tools/volusia_data/research/interviews.py --themes --role business_owner
    python Tools/volusia_data/research/interviews.py --export-csv interviews.csv
"""

import argparse
import csv
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add Tools to path
TOOLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))

from volusia_data.config import DB_PATH

VALID_ROLES = ["business_owner", "resident", "tourist", "industry_mover"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_table():
    """Create interviews table if it doesn't exist."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stakeholder_name TEXT,
            stakeholder_role TEXT NOT NULL,
            interview_date TEXT,
            themes TEXT DEFAULT '[]',
            needs_identified TEXT DEFAULT '[]',
            data_gaps TEXT DEFAULT '[]',
            follow_up_required BOOLEAN DEFAULT 0,
            follow_up_date TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_interviews_role ON interviews(stakeholder_role);
        CREATE INDEX IF NOT EXISTS idx_interviews_date ON interviews(interview_date);
    """)
    conn.commit()
    conn.close()


def add_interview(args):
    """Add a new interview record."""
    init_table()
    conn = get_db()
    
    themes = json.dumps(args.themes.split(",") if args.themes else [])
    needs = json.dumps(args.needs.split(",") if args.needs else [])
    gaps = json.dumps(args.gaps.split(",") if args.gaps else [])
    
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        INSERT INTO interviews (stakeholder_name, stakeholder_role, interview_date, themes, needs_identified, data_gaps, follow_up_required, follow_up_date, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        args.name, args.role, args.date, themes, needs, gaps,
        1 if args.follow_up else 0, args.follow_up_date, args.notes, now, now
    ))
    conn.commit()
    
    # Get the ID
    row = conn.execute("SELECT id FROM interviews ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    
    print(f"Interview recorded: ID={row['id']}")
    print(f"  Name: {args.name}")
    print(f"  Role: {args.role}")
    print(f"  Date: {args.date}")
    print(f"  Themes: {themes}")
    print(f"  Follow-up: {'Yes' if args.follow_up else 'No'}")


def list_interviews(args):
    """List recent interviews."""
    init_table()
    conn = get_db()
    
    query = "SELECT * FROM interviews ORDER BY interview_date DESC"
    params = []
    
    if args.role:
        query = "SELECT * FROM interviews WHERE stakeholder_role = ? ORDER BY interview_date DESC"
        params = [args.role]
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    if not rows:
        print("No interviews recorded yet.")
        return
    
    print(f"{'ID':<5} {'Date':<12} {'Role':<18} {'Name':<25} {'Themes':<30} {'Follow-up':<10}")
    print("-" * 100)
    for r in rows:
        themes = json.loads(r["themes"]) if r["themes"] else []
        follow = "Yes" if r["follow_up_required"] else "No"
        print(f"{r['id']:<5} {r['interview_date'] or 'N/A':<12} {r['stakeholder_role']:<18} {r['stakeholder_name'] or 'Anonymous':<25} {', '.join(themes)[:28]:<30} {follow:<10}")


def show_themes(args):
    """Show aggregated themes by role."""
    init_table()
    conn = get_db()
    
    query = "SELECT themes, needs_identified, data_gaps, stakeholder_role FROM interviews"
    params = []
    
    if args.role:
        query += " WHERE stakeholder_role = ?"
        params = [args.role]
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    themes_count = {}
    needs_count = {}
    gaps_count = {}
    
    for r in rows:
        for t in json.loads(r["themes"] or "[]"):
            themes_count[t] = themes_count.get(t, 0) + 1
        for n in json.loads(r["needs_identified"] or "[]"):
            needs_count[n] = needs_count.get(n, 0) + 1
        for g in json.loads(r["data_gaps"] or "[]"):
            gaps_count[g] = gaps_count.get(g, 0) + 1
    
    print("=== Themes ===")
    for t, c in sorted(themes_count.items(), key=lambda x: -x[1]):
        print(f"  {c}x {t}")
    
    print("\n=== Needs Identified ===")
    for n, c in sorted(needs_count.items(), key=lambda x: -x[1]):
        print(f"  {c}x {n}")
    
    print("\n=== Data Gaps ===")
    for g, c in sorted(gaps_count.items(), key=lambda x: -x[1]):
        print(f"  {c}x {g}")


def export_csv(args):
    """Export interviews to CSV."""
    init_table()
    conn = get_db()
    rows = conn.execute("SELECT * FROM interviews ORDER BY interview_date DESC").fetchall()
    conn.close()
    
    if not rows:
        print("No interviews to export.")
        return
    
    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "role", "date", "themes", "needs", "data_gaps", "follow_up", "notes"])
        for r in rows:
            writer.writerow([
                r["id"],
                r["stakeholder_name"],
                r["stakeholder_role"],
                r["interview_date"],
                "; ".join(json.loads(r["themes"] or "[]")),
                "; ".join(json.loads(r["needs_identified"] or "[]")),
                "; ".join(json.loads(r["data_gaps"] or "[]")),
                "Yes" if r["follow_up_required"] else "No",
                r["notes"],
            ])
    
    print(f"Exported {len(rows)} interviews to {args.output}")


def show_summary(args):
    """Show summary statistics."""
    init_table()
    conn = get_db()
    
    total = conn.execute("SELECT COUNT(*) FROM interviews").fetchone()[0]
    by_role = conn.execute("SELECT stakeholder_role, COUNT(*) as cnt FROM interviews GROUP BY stakeholder_role").fetchall()
    follow_ups = conn.execute("SELECT COUNT(*) FROM interviews WHERE follow_up_required = 1").fetchone()[0]
    
    conn.close()
    
    print("=== Interview Summary ===")
    print(f"Total interviews: {total}")
    print(f"Follow-ups required: {follow_ups}")
    print("\nBy role:")
    for r in by_role:
        print(f"  {r['stakeholder_role']}: {r['cnt']}")


def main():
    parser = argparse.ArgumentParser(description="Stakeholder Interview Tracking")
    sub = parser.add_subparsers(dest="command")
    
    # Add command
    add_parser = sub.add_parser("add", help="Add a new interview")
    add_parser.add_argument("--name", default="", help="Stakeholder name")
    add_parser.add_argument("--role", required=True, choices=VALID_ROLES, help="Stakeholder role")
    add_parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Interview date")
    add_parser.add_argument("--themes", default="", help="Comma-separated themes")
    add_parser.add_argument("--needs", default="", help="Comma-separated needs identified")
    add_parser.add_argument("--gaps", default="", help="Comma-separated data gaps")
    add_parser.add_argument("--follow-up", action="store_true", help="Follow-up required")
    add_parser.add_argument("--follow-up-date", default="", help="Follow-up date")
    add_parser.add_argument("--notes", default="", help="Additional notes")
    
    # List command
    list_parser = sub.add_parser("list", help="List interviews")
    list_parser.add_argument("--role", choices=VALID_ROLES, help="Filter by role")
    
    # Themes command
    themes_parser = sub.add_parser("themes", help="Show aggregated themes")
    themes_parser.add_argument("--role", choices=VALID_ROLES, help="Filter by role")
    
    # Export command
    export_parser = sub.add_parser("export", help="Export to CSV")
    export_parser.add_argument("--output", default="interviews.csv", help="Output file")
    
    # Summary command
    sub.add_parser("summary", help="Show summary statistics")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_interview(args)
    elif args.command == "list":
        list_interviews(args)
    elif args.command == "themes":
        show_themes(args)
    elif args.command == "export":
        export_csv(args)
    elif args.command == "summary":
        show_summary(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
