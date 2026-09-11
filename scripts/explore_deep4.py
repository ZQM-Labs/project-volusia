import os, json
BASE = r"C:/Users/zqmco/Docker/volusia-portal/backend"

# Read test_user.json state
gdir = os.path.join(BASE, "data", "gamification")
for f in ["test_user.json", "zqmco.json"]:
    path = os.path.join(gdir, f)
    try:
        with open(path) as fh:
            state = json.load(fh)
        print(f"=== {f} ===")
        print(f"  total_xp: {state.get('total_xp',0)}")
        print(f"  level: {state.get('level','N/A')}")
        print(f"  streak: {state.get('streak',0)}")
        print(f"  quality_tier: {state.get('quality_tier','N/A')}")
        qs = state.get('quality_score',{})
        print(f"  quality_score: {json.dumps(qs, indent=2)[:300]}")
        print(f"  badges: {state.get('badges',[])}")
        pc = state.get('mission_flags',{}).get('pathway_counts',{})
        print(f"  pathway_counts: {pc}")
        pathways = state.get('mission_flags',{}).get('pathways',[])
        print(f"  pathways: {pathways}")
        print(f"  sources_contributed: {state.get('sources_contributed',[])}")
        print(f"  categories_contributed: {state.get('categories_contributed',[])}")
        print(f"  total_submissions: {state.get('mission_flags',{}).get('total_submissions',0)}")
        print()
    except Exception as e:
        print(f"  {f}: {e}")

# Check data directory structure
print()
print("=== BACKEND DATA DIRECTORY ===")
data_dir = os.path.join(BASE, "data")
for root, dirs, files in os.walk(data_dir):
    level = root.replace(data_dir, "").count(os.sep)
    if level > 3:
        continue
    indent = "  " * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = "  " * (level + 1)
    for file in sorted(files):
        path = os.path.join(root, file)
        size = os.path.getsize(path)
        print(f"{subindent}{file} ({size} bytes)")

