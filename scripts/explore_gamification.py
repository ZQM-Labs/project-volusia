import urllib.request, ssl, re
ctx = ssl._create_unverified_context()

# 1. Check /gamification/ page for pathway links
print("=== /gamification/ PAGE CONTENT ===")
try:
    req = urllib.request.Request("https://zqmlabs.com/gamification/", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode()
    # Look for pathway references
    # Find all /data/ links on the page
    all_links = re.findall(r'href="(/data/[^"]+)"', html)
    print(f"All /data/ links on gamification page: {sorted(set(all_links))}")
    # Find pathway A-N references
    for pid in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N']:
        if f'>{pid}<' in html or f'pathway {pid}' in html.lower():
            print(f"  Pathway {pid}: visible on page")
    # Check title and main content
    title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    h1 = re.findall(r'<h[1][^>]*>(.*?)</h[1]>', html, re.IGNORECASE)
    print(f"Title: {title.group(1) if title else 'N/A'}")
    print(f"H1: {h1[:3]}")
    # Check for mission list
    mission_count = len(re.findall(r'mission', html, re.IGNORECASE))
    print(f"Mission references: {mission_count}")
except Exception as e:
    print(f"ERROR: {e}")

# 2. Check /leaders/ page content
print()
print("=== /leaders/ PAGE CONTENT ===")
try:
    req = urllib.request.Request("https://zqmlabs.com/leaders/", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode()
    title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    h1 = re.findall(r'<h[1][^>]*>(.*?)</h[1]>', html, re.IGNORECASE)
    all_links = re.findall(r'href="(/data/[^"]+)"', html)
    print(f"Title: {title.group(1) if title else 'N/A'}")
    print(f"H1: {h1[:3]}")
    print(f"Data links: {sorted(set(all_links))}")
except Exception as e:
    print(f"ERROR: {e}")

# 3. Check contribute.py for pathway structure
print()
print("=== CONTRIBUTE.PY PATHWAY STRUCTURE ===")
import os
contribute_path = r'C:/Users/zqmco/Docker/volusia-portal/scripts/contribute.py'
if os.path.exists(contribute_path):
    with open(contribute_path) as f:
        c = f.read()
    # Find pathway constants
    pathway_consts = re.findall(r'(?:PATHWAY|pathway)[_'"]?([A-N])', c)
    print(f"Pathway constants found: {sorted(set(pathway_consts))}")
    # Find key functions
    funcs = re.findall(r'def (\w+)', c)
    print(f"Functions: {funcs}")
    # Find contribution methods
    methods = re.findall(r'(?:post_|submit_|contribute|check_)\w+', c)
    print(f"Contribution methods: {sorted(set(methods))}")
    
# 4. Check scoring.py for pathway definitions
print()
print("=== SCORING.PY PATHWAY DEFINITIONS ===")
scoring_path = r'C:/Users/zqmco/Docker/volusia-portal/backend/gamification/scoring.py'
if os.path.exists(scoring_path):
    with open(scoring_path) as f:
        c = f.read()
    # Find pathway definitions
    path_defs = re.findall(r'PATHWAY[A-N]', c)
    print(f"PATHWAY constants: {sorted(set(path_defs))}")
    # Find XP values
    xp_refs = re.findall(r'(?:xp|XP|score)[^=]*=\s*(\d+)', c)
    print(f"XP values: {sorted(set(xp_refs))}")
    # Check for pathway categories
    cats = re.findall(r'"([A-N])"', c)[:20]
    print(f"Pathway letter refs: {sorted(set(cats))}")

# 5. Check if static pages have unique content per pathway
print()
print("=== UNIQUE CONTENT PER PATHWAY ===")
for p_id, slug in [('A','data-source'),('B','business-owner'),('J','code-feature')]:
    try:
        req = urllib.request.Request(f"https://zqmlabs.com/data/{slug}/", headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=5)
        html = resp.read().decode()
        # Get the body title
        title = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE)
        desc = re.search(r'<p[^>]*>(.*?)</p>', html, re.IGNORECASE)
        print(f"  {p_id} ({slug}): H1={title.group(1).strip() if title else 'N/A'}")
        print(f"    Desc={desc.group(1).strip()[:80] if desc else 'N/A'}")
    except Exception as e:
        print(f"  {p_id} ({slug}): ERROR")
