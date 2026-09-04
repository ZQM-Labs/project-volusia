#!/usr/bin/env python3
"""
Project Volusia — Contribution Review CLI
Review, approve, or reject pending contributions.

Usage:
    python Tools/volusia_data/contribution/review.py --list-pending
    python Tools/volusia_data/contribution/review.py --approve SUB-TOOL-20260904120000000000
    python Tools/volusia_data/contribution/review.py --reject SUB-TOOL-20260904120000000000 --reason "Not applicable"
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add Tools to path
TOOLS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TOOLS))

from volusia_data.config import DB_PATH


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def list_pending():
    """List all pending submissions."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM submissions WHERE status = 'queued' ORDER BY submitted_at DESC"
    ).fetchall()
    conn.close()
    
    if not rows:
        print("No pending submissions.")
        return
    
    print(f"{'ID':<30} {'Type':<15} {'Reviewer':<25} {'Submitted':<20} {'Author':<20}")
    print("-" * 110)
    for r in rows:
        print(f"{r['submission_id']:<30} {r['contribution_type']:<15} {r['reviewer']:<25} {r['submitted_at'][:19]:<20} {r['author_name'] or 'Anonymous':<20}")


def show_submission(submission_id):
    """Show full details of a submission."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM submissions WHERE submission_id = ?", (submission_id,)
    ).fetchone()
    conn.close()
    
    if not row:
        print(f"Submission not found: {submission_id}")
        return
    
    print(f"=== {row['submission_id']} ===")
    print(f"Type: {row['contribution_type']}")
    print(f"Status: {row['status']}")
    print(f"Reviewer: {row['reviewer']}")
    print(f"Fallback: {row.get('fallback_reviewer', 'N/A')}")
    print(f"Submitted: {row['submitted_at']}")
    print(f"Author: {row['author_name'] or 'Anonymous'}")
    print(f"Email: {row['author_email'] or 'N/A'}")
    print(f"Estimated review: {row.get('estimated_review_by', 'N/A')}")
    print(f"\nContent:")
    try:
        content = json.loads(row['content'])
        print(json.dumps(content, indent=2))
    except (json.JSONDecodeError, TypeError):
        print(row['content'])


def approve(submission_id, reviewer=""):
    """Approve a submission."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM submissions WHERE submission_id = ?", (submission_id,)
    ).fetchone()
    
    if not row:
        print(f"Submission not found: {submission_id}")
        conn.close()
        return
    
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        UPDATE submissions 
        SET status = 'approved', decision = 'approved', acknowledged_at = ?, reviewer = COALESCE(NULLIF(?, ''), reviewer)
        WHERE submission_id = ?
    """, (now, reviewer, submission_id))
    conn.commit()
    conn.close()
    
    print(f"Approved: {submission_id}")


def reject(submission_id, reason="", reviewer=""):
    """Reject a submission."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM submissions WHERE submission_id = ?", (submission_id,)
    ).fetchone()
    
    if not row:
        print(f"Submission not found: {submission_id}")
        conn.close()
        return
    
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""
        UPDATE submissions 
        SET status = 'rejected', decision = 'rejected', acknowledged_at = ?, reviewer = COALESCE(NULLIF(?, ''), reviewer)
        WHERE submission_id = ?
    """, (now, reviewer, submission_id))
    conn.commit()
    conn.close()
    
    print(f"Rejected: {submission_id}")
    if reason:
        print(f"Reason: {reason}")


def list_all(status=None):
    """List all submissions, optionally filtered by status."""
    conn = get_db()
    
    if status:
        rows = conn.execute(
            "SELECT * FROM submissions WHERE status = ? ORDER BY submitted_at DESC", (status,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM submissions ORDER BY submitted_at DESC"
        ).fetchall()
    
    conn.close()
    
    if not rows:
        print("No submissions found.")
        return
    
    print(f"{'ID':<30} {'Type':<15} {'Status':<12} {'Reviewer':<25} {'Submitted':<20}")
    print("-" * 102)
    for r in rows:
        print(f"{r['submission_id']:<30} {r['contribution_type']:<15} {r['status']:<12} {r['reviewer']:<25} {r['submitted_at'][:19]:<20}")


def main():
    parser = argparse.ArgumentParser(description="Review contributions")
    sub = parser.add_subparsers(dest="command")
    
    # List pending
    sub.add_parser("list-pending", help="List pending submissions")
    
    # List all
    list_parser = sub.add_parser("list-all", help="List all submissions")
    list_parser.add_argument("--status", choices=["queued", "approved", "rejected", "under_review"], help="Filter by status")
    
    # Show
    show_parser = sub.add_parser("show", help="Show submission details")
    show_parser.add_argument("submission_id", help="Submission ID")
    
    # Approve
    approve_parser = sub.add_parser("approve", help="Approve a submission")
    approve_parser.add_argument("submission_id", help="Submission ID")
    approve_parser.add_argument("--reviewer", default="", help="Reviewer name")
    
    # Reject
    reject_parser = sub.add_parser("reject", help="Reject a submission")
    reject_parser.add_argument("submission_id", help="Submission ID")
    reject_parser.add_argument("--reason", default="", help="Rejection reason")
    reject_parser.add_argument("--reviewer", default="", help="Reviewer name")
    
    args = parser.parse_args()
    
    if args.command == "list-pending":
        list_pending()
    elif args.command == "list-all":
        list_all(args.status)
    elif args.command == "show":
        show_submission(args.submission_id)
    elif args.command == "approve":
        approve(args.submission_id, args.reviewer)
    elif args.command == "reject":
        reject(args.submission_id, args.reason, args.reviewer)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
