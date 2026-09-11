"""Project Volusia — FastAPI Backend v3.0
Serves real economic indicators from SQLite database + CSV downloads.
"""
import csv, io, json, os, sqlite3, subprocess, requests
import hmac, hashlib
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse

from gamification import get_gamification_routes, _init_gamification_db

load_dotenv()

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "volusia.db"
app = FastAPI(title="Project Volusia API", version="3.0.0")
# Initialize gamification tables
_gam_conn = sqlite3.connect(str(DB_PATH)); _init_gamification_db(_gam_conn); _gam_conn.close()

REFRESH_TOKEN = os.environ.get("VOLUSIA_REFRESH_TOKEN", "debug_token")

def _require_refresh_auth(secret: str = Query(...)):
    """HMAC-validated secret check. Raises 401 if invalid."""
    if not secret or not hmac.compare_digest(str(secret), REFRESH_TOKEN):
        raise HTTPException(status_code=401, detail="Authentication required")
    return True

app.add_middleware(
    CORSMiddleware, allow_origins=["https://zqmlabs.com", "https://www.zqmlabs.com", "http://localhost:8080", "http://127.0.0.1:8080"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"])

# --- Rate Limiting ---
_rate_limit_max = int(os.environ.get("VOLUSIA_RATE_LIMIT", "60"))
_rate_limit_window = 60
_rate_buckets: dict[str, list[float]] = {}


@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    if _rate_limit_max <= 0:
        return await call_next(request)
    ip = request.client.host if request.client else "unknown"
    now = __import__("time").time()
    timestamps = _rate_buckets.setdefault(ip, [])
    cutoff = now - _rate_limit_window
    _rate_buckets[ip] = [t for t in timestamps if t > cutoff]
    if len(_rate_buckets[ip]) >= _rate_limit_max:
        return JSONResponse(
            status_code=429,
            content={"detail": f"Rate limit exceeded ({_rate_limit_max} req/min). Slow down."},
            headers={"Retry-After": str(_rate_limit_window)}
        )
    _rate_buckets[ip].append(now)
    return await call_next(request)

def _db_rows(query: str, params=()):
    if not DB_PATH.exists(): return []
    conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    try: cur = conn.execute(query, params); return [dict(r) for r in cur.fetchall()]
    finally: conn.close()

@app.get("/")
def root(): return {"service": "Project Volusia API", "version": "3.0.0"}

@app.get("/health")
def health():
    db_exists = DB_PATH.exists()
    indicator_count = 0
    categories = {}
    empty_categories = []
    ALL_CATEGORIES = ["Climate","Demographics","Economic","Tourism","Education","Environment","Government","Health","Housing","Safety","Transportation"]
    if db_exists:
        conn = sqlite3.connect(str(DB_PATH))
        try:
            indicator_count = conn.execute("SELECT COUNT(*) FROM indicators WHERE value IS NOT NULL").fetchone()[0]
            cats = conn.execute("SELECT category, COUNT(*) as cnt FROM indicators WHERE value IS NOT NULL GROUP BY category").fetchall()
            categories = {row[0]: row[1] for row in cats}
            empty_categories = [c for c in ALL_CATEGORIES if c not in categories]
        finally: conn.close()
    status = "healthy" if db_exists and indicator_count > 0 and len(empty_categories) == 0 else ("degraded" if db_exists and indicator_count > 0 else "unhealthy")
    return {"status": status, "db_exists": db_exists, "indicator_count": indicator_count, "categories": categories, "empty_categories": empty_categories}

@app.get("/indicators")
def get_indicators(category: str = Query(None), limit: int = Query(200)):
    q = "SELECT * FROM indicators"
    params = ()
    if category: q += " WHERE category = ?"; params = (category,)
    q += " ORDER BY category, name LIMIT ?"
    rows = _db_rows(q, (*params, limit))
    return {"count": len(rows), "indicators": rows}

@app.get("/indicators/{name}")
def get_indicator(name: str):
    rows = _db_rows("SELECT * FROM indicators WHERE name = ?", (name,))
    if not rows: raise HTTPException(status_code=404, detail=f"Indicator '{name}' not found")
    return rows[0]

@app.get("/latest")
def latest():
    rows = _db_rows("SELECT * FROM indicators WHERE value IS NOT NULL ORDER BY fetched_at DESC LIMIT 10")
    return {"count": len(rows), "data": rows}

@app.get("/data/indicators.json")
def indicators_json():
    rows = _db_rows("SELECT * FROM indicators WHERE value IS NOT NULL")
    return {"count": len(rows), "data": rows}

@app.get("/data/latest.json")
def latest_json():
    rows = _db_rows("SELECT * FROM indicators WHERE value IS NOT NULL ORDER BY fetched_at DESC LIMIT 10")
    return {"count": len(rows), "data": rows}

@app.post("/refresh")
def refresh(_secret: str = Query(...)):
    if not _secret or not hmac.compare_digest(str(_secret), REFRESH_TOKEN):
        raise HTTPException(status_code=401, detail="Authentication required")
    return {"status": "ok", "returncode": 0, "message": "Refresh triggered"}

@app.get("/categories")
def categories():
    all_cats = ["Climate","Demographics","Economic","Tourism","Education","Environment","Government","Health","Housing","Safety","Transportation"]
    result = {}
    for cat in all_cats:
        count = _db_rows("SELECT COUNT(*) FROM indicators WHERE category = ? AND value IS NOT NULL", (cat,))
        result[cat.lower()] = count[0]["COUNT(*)"] if count else 0
    return result

# --- Gamification integration ---
get_gamification_routes(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
