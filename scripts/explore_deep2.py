import os, json, re
BASE = r"C:/Users/zqmco/Docker/volusia-portal/backend"

# Read scoring.py
with open(os.path.join(BASE, "gamification/scoring.py")) as f:
    scoring = f.read()

# Read gamification routes
with open(os.path.join(BASE, "gamification/routes.py")) as f:
    routes = f.read()

# Read gamification main module
with open(os.path.join(BASE, "gamification.py")) as f:
    gamel = f.read()

# 1. Scoring engine pathways mapping
print("=== PATHWAY SCORING WEIGHTS (from scoring.py) ===")
# Find pathway dictionary/sections
pathway_sections = re.findall(r'(?:pathway|PATHWAY|P\d+)[^\n]*', scoring)
for s in pathway_sections[:20]:
    print(f"  {s.strip()[:120]}")

# Find the CONTRIBUTION_SCHEMA or pathway dict
print()
schema = re.search(r'CONTRIBUTION_SCHEMA\s*=\s*({.*?})', scoring, re.DOTALL)
if schema:
    print(f"CONTRIBUTION_SCHEMA found ({len(schema.group(0))} chars)")
    # Extract pathway keys
    pk = re.findall(r"'(A|B|C|D|E|F|G|H|I|J|K|L|M|N)'", schema.group(0))
    print(f"Pathways in schema: {pk}")

# 2. Data cache contents
print()
print("=== DATA CACHE FILES ===")
cache_dir = os.path.join(BASE, "data", "cache")
if os.path.exists(cache_dir):
    for f in sorted(os.listdir(cache_dir)):
        path = os.path.join(cache_dir, f)
        try:
            with open(path) as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                keys = list(data.keys())[:5]
                print(f"  {f}: {len(json.dumps(data))} bytes | keys: {keys}")
            elif isinstance(data, list):
                print(f"  {f}: {len(data)} items")
        except:
            print(f"  {f}: (not JSON)")

# 3. Gamification test states
print()
print("=== GAMIFICATION STATES ===")
gdir = os.path.join(BASE, "data", "gamification")
if os.path.exists(gdir):
    for f in sorted(os.listdir(gdir)):
        path = os.path.join(gdir, f)
        try:
            with open(path) as fh:
                data = json.load(fh)
            print(f"  {f}: {json.dumps(data)[:200]}")
        except:
            print(f"  {f}: (not JSON)")

# 4. Routes structure
print()
print("=== GAMIFICATION ROUTES ===")
# Find route decorators
route_decs = re.findall(r'@router\.\w+\(.*?["\']([^"\']+)["\']', routes)
for r in route_decs:
    print(f"  Route: {r}")
# Find function signatures
route_funcs = re.findall(r'async def (\w+)', routes)
for rf in route_funcs:
    print(f"  Handler: {rf}")

# 5. Quality tiers
print()
print("=== QUALITY TIERS ===")
tier_sections = re.findall(r'QualityTier\.?\w*', scoring)
tiers = re.findall(r'(?:T[1-5]|tier_[a-z]+)', scoring)
unique_tiers = sorted(set(tiers))
print(f"  Tier identifiers: {unique_tiers}")

# 6. Level thresholds
print()
level_match = re.search(r'level.*?(?:=|:).*?(?:\{|\[)', scoring, re.DOTALL)
if level_match:
    print(f"  Level definition: {level_match.group(0)[:200]}")

