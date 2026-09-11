import os, json, re
BASE = r"C:/Users/zqmco/Docker/volusia-portal/backend"

# 1. Check data cache directory
print("=== DATA CACHE ===")
cache_dir = os.path.join(BASE, "data_cache")
if os.path.exists(cache_dir):
    files = sorted(os.listdir(cache_dir))
    for f in files:
        path = os.path.join(cache_dir, f)
        size = os.path.getsize(path)
        try:
            with open(path) as fh:
                first = fh.readline().strip()[:120]
        except:
            first = "N/A"
        print(f"  {f}: {size} bytes | {first}")

# 2. Check backend directory structure
print()
print("=== BACKEND STRUCTURE ===")
for root, dirs, files in os.walk(BASE):
    level = root.replace(BASE, "").count(os.sep)
    indent = "  " * level
    if level > 4:
        continue
    print(f"{indent}{os.path.basename(root)}/")
    subindent = "  " * (level + 1)
    for file in sorted(files):
        print(f"{subindent}{file}")

# 3. Check scoring.py structure
print()
print("=== SCORING.PY ===")
scoring_path = os.path.join(BASE, "gamification/scoring.py")
if os.path.exists(scoring_path):
    with open(scoring_path) as f:
        c = f.read()
    print(f"  Size: {len(c)} chars, {len(c.splitlines())} lines")
    classes = re.findall(r'class\s+(\w+)', c)
    defs = re.findall(r'def\s+(\w+)', c)
    print(f"  Classes: {classes}")
    print(f"  Functions: {defs}")
    # Find all pathway letters A-N
    pathway_letters = set(re.findall(r'\b([A-N])\b', c))
    print(f"  Pathway letters found: {sorted(pathway_letters)}")
    # Find tier/XP thresholds
    tiers = re.findall(r'(?:tier|Tier)[^.]*?\.', c)
    print(f"  Tier references: {len(tiers)}")
