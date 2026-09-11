import os, json, re
BASE = r"C:/Users/zqmco/Docker/volusia-portal/backend"

with open(os.path.join(BASE, "gamification/scoring.py")) as f:
    scoring = f.read()

# Find the CONTRIBUTION_SCHEMA dict
print("=== CONTRIBUTION_SCHEMA ===")
schema_match = re.search(r'CONTRIBUTION_SCHEMA\s*=\s*\{(.*?)\n\}', scoring, re.DOTALL)
if schema_match:
    schema_text = schema_match.group(0)
    # Find all pathway entries
    pathways = re.findall(r"'(A|B|C|D|E|F|G|H|I|J|K|L|M|N)':\s*\{(.*?)\n\s*\}", schema_text, re.DOTALL)
    for pid, body in pathways:
        xp = re.search(r'"xp":\s*(\d+)', body)
        desc = re.search(r'"name":\s*"([^"]+)"', body)
        if desc and xp:
            print(f"  Pathway {pid}: {desc.group(1)} ({xp.group(1)} XP)")
        elif desc:
            print(f"  Pathway {pid}: {desc.group(1)}")
        elif xp:
            print(f"  Pathway {pid}: {xp.group(1)} XP")

# Find level thresholds
print()
print("=== LEVEL THRESHOLDS ===")
levels_match = re.search(r'levels\s*=\s*\[(.*?)\]', scoring, re.DOTALL)
if levels_match:
    levels_text = levels_match.group(0)
    thresholds = re.findall(r'(\d+)\s*:\s*["\'](\w+)["\']', levels_text)
    if not thresholds:
        thresholds = re.findall(r'(\d+)\s*,\s*', levels_text)
    print(f"  Level thresholds: {thresholds[:10]}")

# Find XP thresholds
xp_match = re.search(r'XP_THRESHOLDS\s*=\s*\{(.*?)\}', scoring, re.DOTALL)
if xp_match:
    print(f"  XP_THRESHOLDS: {xp_match.group(0)[:300]}")

# Find quality scoring components
print()
print("=== QUALITY SCORING ===")
quality_match = re.search(r'quality_score.*?(?=def|\Z)', scoring, re.DOTALL)
if quality_match:
    qs = quality_match.group(0)
    components = re.findall(r'(\w+):\s*\w+', qs)
    print(f"  Quality components: {components[:10]}")
    # Find the quality tier thresholds
    tier_match = re.search(r'(?:quality_tier|tier).*?(?:switch|change|level).*?(?:\n|$)', scoring)
    if tier_match:
        print(f"  Tier logic found")

# Find all unique pathway references with counts
print()
print("=== ALL PATHWAY COUNTS ===")
for pid in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','P','Q','R']:
    count = len(re.findall(rf'\b{pid}\b', scoring))
    if count > 0:
        print(f"  {pid}: {count} references")

# Find mission definitions
print()
print("=== MISSION DEFINITIONS ===")
missions = re.findall(r'missions\s*=\s*\[(.*?)\]', scoring, re.DOTALL)
if missions:
    mtext = missions[0]
    mission_names = re.findall(r'"name":\s*"([^"]+)"', mtext)
    print(f"  Mission names: {mission_names}")

