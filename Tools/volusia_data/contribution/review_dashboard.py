#!/usr/bin/env python3
"""
Project Volusia — Contribution Review Dashboard
Web interface for reviewing and managing contributions.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "volusia.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def render_dashboard():
    """Render the contribution review dashboard."""
    conn = get_db()
    
    # Get statistics
    total = conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
    queued = conn.execute("SELECT COUNT(*) FROM submissions WHERE status = 'queued'").fetchone()[0]
    approved = conn.execute("SELECT COUNT(*) FROM submissions WHERE status = 'approved'").fetchone()[0]
    rejected = conn.execute("SELECT COUNT(*) FROM submissions WHERE status = 'rejected'").fetchone()[0]
    
    # Get recent submissions
    recent = conn.execute("""
        SELECT * FROM submissions 
        ORDER BY created_at DESC 
        LIMIT 50
    """).fetchall()
    
    # Get by type
    by_type = conn.execute("""
        SELECT contribution_type, COUNT(*) as cnt 
        FROM submissions 
        GROUP BY contribution_type 
        ORDER BY cnt DESC
    """).fetchall()
    
    # Get by status
    by_status = conn.execute("""
        SELECT status, COUNT(*) as cnt 
        FROM submissions 
        GROUP BY status 
        ORDER BY cnt DESC
    """).fetchall()
    
    conn.close()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Contribution Review — Project Volusia</title>
  <style>
    :root {{ --bg:#0f172a; --ink:#e2e8f0; --muted:#94a3b8; --accent:#38bdf8; --card:#1e293b; --border:#334155; --green:#10b981; --yellow:#f59e0b; --red:#ef4444; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background: var(--bg); color: var(--ink); line-height:1.6; }}
    header {{ border-bottom: 1px solid var(--border); }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
    .nav {{ display:flex; justify-content:space-between; align-items:center; }}
    .logo {{ font-weight:800; letter-spacing:-0.02em; font-size:18px; color: var(--accent); text-decoration: none; }}
    .nav a {{ color: var(--ink); text-decoration:none; font-weight:500; padding:6px 10px; border-radius:6px; margin-left: 4px; }}
    .nav a:hover {{ background:#334155; color: var(--accent); }}
    .hero {{ padding: 40px 20px; }}
    h1 {{ font-size: 32px; margin: 0 0 8px; }}
    .subtitle {{ color: var(--muted); margin-bottom: 20px; }}
    .stats {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin: 24px 0; }}
    .stat {{ background: var(--card); border:1px solid var(--border); border-radius: 12px; padding: 20px; text-align: center; }}
    .stat-value {{ font-size: 24px; font-weight: 700; color: var(--accent); }}
    .stat-label {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13px; }}
    th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); }}
    th {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; background: #0f172a; }}
    .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
    .badge-queued {{ background: #78350f; color: #f59e0b; }}
    .badge-approved {{ background: #065f46; color: #10b981; }}
    .badge-rejected {{ background: #7f1d1d; color: #ef4444; }}
    .badge-data_source {{ background: #1e3a5f; color: #38bdf8; }}
    .badge-analysis {{ background: #3b0764; color: #a855f7; }}
    .badge-tool {{ background: #064e3b; color: #10b981; }}
    .badge-map {{ background: #451a03; color: #f59e0b; }}
    .badge-report {{ background: #1f2937; color: #94a3b8; }}
    .badge-community {{ background: #4c1d95; color: #c084fc; }}
    .badge-social_media {{ background: #831843; color: #f472b6; }}
    .badge-educational {{ background: #1e40af; color: #60a5fa; }}
    .badge-direct {{ background: #374151; color: #d1d5db; }}
    .btn {{ display: inline-block; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; text-decoration: none; border: none; cursor: pointer; }}
    .btn-approve {{ background: #065f46; color: #10b981; }}
    .btn-reject {{ background: #7f1d1d; color: #ef4444; }}
    .btn-view {{ background: #1e3a5f; color: #38bdf8; }}
    footer {{ border-top:1px solid var(--border); color: var(--muted); font-size:13px; padding: 20px; text-align: center; margin-top: 40px; }}
  </style>
</head>
<body>
  <header>
    <div class="container nav">
      <a href="/" class="logo">Project Volusia</a>
      <div>
        <a href="/dashboard">Dashboard</a>
        <a href="/contribute/">Contribute</a>
        <a href="/review">Review</a>
        <a href="/data-explorer">Data</a>
      </div>
    </div>
  </header>

  <div class="hero">
    <h1>Contribution Review</h1>
    <p class="subtitle">Review and manage community contributions to Project Volusia.</p>
  </div>

  <section>
    <div class="container">
      <div class="stats">
        <div class="stat">
          <div class="stat-value">{total}</div>
          <div class="stat-label">Total</div>
        </div>
        <div class="stat">
          <div class="stat-value">{queued}</div>
          <div class="stat-label">Queued</div>
        </div>
        <div class="stat">
          <div class="stat-value">{approved}</div>
          <div class="stat-label">Approved</div>
        </div>
        <div class="stat">
          <div class="stat-value">{rejected}</div>
          <div class="stat-label">Rejected</div>
        </div>
      </div>

      <h2>By Type</h2>
      <table>
        <thead>
          <tr><th>Type</th><th>Count</th></tr>
        </thead>
        <tbody>"""
    
    for row in by_type:
        html += f"""
          <tr>
            <td><span class="badge badge-{row[0]}">{row[0]}</span></td>
            <td>{row[1]}</td>
          </tr>"""
    
    html += """
        </tbody>
      </table>

      <h2>Recent Submissions</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>"""
    
    for row in recent:
        html += f"""
          <tr>
            <td>{row['submission_id'][:20]}...</td>
            <td><span class="badge badge-{row['contribution_type']}">{row['contribution_type']}</span></td>
            <td><span class="badge badge-{row['status']}">{row['status']}</span></td>
            <td>{row['created_at'][:19]}</td>
            <td>
              <a href="/review/{row['submission_id']}" class="btn btn-view">View</a>
            </td>
          </tr>"""
    
    html += """
        </tbody>
      </table>
    </div>
  </section>

  <footer>
    <div class="container">
      &copy; ZQM Labs — Project Volusia. Community contribution review.
    </div>
  </footer>
</body>
</html>"""
    
    return html

if __name__ == "__main__":
    print(render_dashboard())
