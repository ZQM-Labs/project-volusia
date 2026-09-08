# Project Volusia Cron Jobs

## Schedule Definition

All times in Eastern Daylight Time (UTC-4) during DST, Eastern Standard Time (UTC-5) otherwise.

---

## 1. DATA PIPELINE REFRESH

**Schedule:** Every Monday at 06:00 EDT

**Command:**
```yaml
name: volusia-data-refresh
schedule: "0 6 * * 1"  # Every Monday at 06:00
prompt: |
  Run the Project Volusia data refresh pipeline. Update all indicators from live sources.
  Report any fetch failures or data quality issues.
skills:
  - ci-cd-and-automation
script: |
  #!/bin/bash
  cd /Z:/14_Projects/Active/Project-Volusia
  python Tools/volusia_data/refresh_v2.py
```

**Monitoring:**
- Exit 0 → healthy, log "refresh completed successfully"
- Exit 1 → degraded, alert with failure details
- Stale data detection via watchdog_monitoring.py

---

## 2. DATA FRESHNESS WATCHDOG

**Schedule:** Every 6 hours (00:00, 06:00, 12:00, 18:00 EDT)

**Command:**
```yaml
name: volusia-data-watchdog
schedule: "0 */6 * * *"  # Every 6 hours
prompt: |
  Check data freshness. If any indicators are stale beyond their source thresholds, log an alert.
  Include specific indicator names and ages in the alert.
no_agent: true
script: |
  #!/usr/bin/env python3
  import json, sqlite3, sys
  from pathlib import Path
  from datetime import datetime, timezone, timedelta
  
  DB_PATH = Path(__file__).parent / "volusia.db"
  SOURCE_THRESHOLDS = {
      "NOAA NCEI": 24,      # Daily
      "BLS LAUS": 720,      # Monthly
      "Census PEP": 8760,   # Annual
  }
  
  if not DB_PATH.exists():
      print(json.dumps({"status": "error", "message": "Database not found"}))
      sys.exit(1)
  
  with sqlite3.connect(DB_PATH) as conn:
      rows = conn.execute("SELECT name, source, fetched_at FROM indicators").fetchall()
  
  stale = []
  for name, source, fetched_at in rows:
      if fetched_at:
          age_hours = (datetime.now(timezone.utc) - datetime.fromisoformat(fetched_at.replace("Z","+00:00"))).total_seconds() / 3600
          threshold = SOURCE_THRESHOLDS.get(source, 168)
          if age_hours > threshold:
              stale.append({"name": name, "age_hours": round(age_hours, 1)})
  
  if stale:
      print(json.dumps({"status": "ALERT", "stale_count": len(stale), "stale_items": stale}))
      sys.exit(1)
  
  print(json.dumps({"status": "ok", "checked_at": datetime.now(timezone.utc).isoformat()}))
  sys.exit(0)
```

---

## 3. PORTAL HEALTH CHECK

**Schedule:** Every 30 minutes

**Command:**
```yaml
name: volusia-portal-health
schedule: "*/30 * * * *"  # Every 30 minutes
prompt: |
  Check if the FastAPI portal is responding at http://127.0.0.1:8789/api/health.
  If down, attempt restart and alert if persist.
no_agent: true
script: |
  #!/usr/bin/env python3
  import urllib.request, json, sys, subprocess
  
  try:
      with urllib.request.urlopen("http://127.0.0.1:8789/api/health", timeout=5) as r:
          data = json.loads(r.read())
          print(json.dumps({"status": "healthy", "response": data}))
          sys.exit(0)
  except Exception as e:
      print(f"ALERT: Portal health check failed: {e}")
      # Attempt restart
      try:
          subprocess.run(["pkill", "-f", "portal_app.py"], timeout=5)
      except: pass
      sys.exit(1)
```

---

## 4. STAKEHOLDER FEEDBACK DIGEST

**Schedule:** Daily at 09:00 EDT

**Prompt:**
```
Check the CONTRIBUTION folder for new community input submissions.
Summarize any new entries and prepare them for CGB review.
Flag any submissions that need immediate attention (data quality warnings, etc.)
```

**Skills:** data-aggregation, verification

---

Document owner: ZQM Labs / Project Volusia
Next review: 2026-12-02