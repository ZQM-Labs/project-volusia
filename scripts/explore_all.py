import urllib.request, ssl, json, re, os
ctx = ssl._create_unverified_context()

print("=" * 70)
print("PROJECT VOLUSIA — FULL PATHWAY EXPLORATION")
print("=" * 70)

# PATHWAYS DEFINITION (from skill)
pathways = {
    'A': 'Data Source', 'B': 'Business Owner', 'C': 'Resident',
    'D': 'Tourist', 'E': 'Industry Mover', 'F': 'School Project',
    'G': 'Social Media', 'H': 'Tool', 'I': 'Direct Citizenry',
    'J': 'Code & Feature', 'K': 'Infrastructure', 'L': 'CI/CD & DevOps',
    'M': 'Testing & QA', 'N': 'Documentation'
}

# 1. Check which pathways have backend API support
print("\n1. BACKEND API ENDPOINTS BY PATHWAY")
print("-" * 50)
# Check backend main.py for pathway-related routes
with open(r'C:/Users/zqmco/Docker/volusia-portal/backend/main.py') as f:
    main_py = f.read()
# Check for pathway references
pathway_refs = set()
for p_id, p_name in pathways.items():
    if p_id.lower() in main_py.lower() or p_name.lower() in main_py.lower():
        pathway_refs.add(p_id)
        print(f"  Pathway {p_id} ({p_name}): REFERENCED in backend/main.py")
    else:
        print(f"  Pathway {p_id} ({p_name}): NOT referenced in main.py")

# Check gamification/scoring.py for pathway references
try:
    with open(r'C:/Users/zqmco/Docker/volusia-portal/backend/gamification/scoring.py') as f:
        scoring_py = f.read()
    scoring_refs = set()
    for p_id, p_name in pathways.items():
        if p_id in scoring_py or p_name.lower() in scoring_py.lower():
            scoring_refs.add(p_id)
    print(f"\n  Referenced in scoring.py: {sorted(scoring_refs) if scoring_refs else 'NONE'}")
except Exception as e:
    print(f"\n  scoring.py check: {e}")

# 2. Check static pages for each pathway
print("\n2. STATIC PAGES FOR EACH PATHWAY")
print("-" * 50)
# Check sitemap and what pages exist
for p_id, p_name in pathways.items():
    slug = p_name.lower().replace(' ', '-').replace('&', '-').replace('/', '-')
    url = f"https://zqmlabs.com/data/{slug}/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=5)
        print(f"  {p_id} ({p_name}): {resp.getcode()} — {url}")
    except Exception as e:
        # Try alternate naming
        alt_slugs = [slug, p_name.lower()]
        found = False
        for alt in alt_slugs[:1]:
            try:
                req = urllib.request.Request(f"https://zqmlabs.com/data/{alt}/", headers={"User-Agent":"Mozilla/5.0"})
                resp = urllib.request.urlopen(req, context=ctx, timeout=5)
                print(f"  {p_id} ({p_name}): {resp.getcode()} — {alt}/")
                found = True
                break
            except: pass
        if not found:
            print(f"  {p_id} ({p_name}): NOT FOUND as static page")

# 3. Check sitemap for pathway pages
print("\n3. SITEMAP PAGE CATEGORIES")
print("-" * 50)
try:
    req = urllib.request.Request("https://zqmlabs.com/sitemap.xml", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=5)
    sitemap = resp.read().decode()
    urls = re.findall(r'<loc>(.*?)</loc>', sitemap)
    for u in sorted(urls):
        print(f"  {u}")
except Exception as e:
    print(f"ERROR: {e}")

# 4. Check what JSON endpoints exist in backend
print("\n4. ALL JSON ENDPOINTS (BACKEND)")
print("-" * 50)
categories = ["economic","demographics","housing","transportation","tourism","safety","health","environment","education","climate","government-finance","real-estate","public-safety"]
for cat in categories:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:8000/data/{cat}.json", headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=3)
        d = json.loads(resp.read().decode())
        cnt = len(d.get('indicators', d.get('data', []))) if isinstance(d.get('indicators', d.get('data')), list) else 'dict'
        print(f"  /data/{cat}.json: {resp.getcode()} ({cnt} indicators)")
    except Exception as e:
        print(f"  /data/{cat}.json: {str(e)[:40]}")

# 5. Check static page count
print("\n5. STATIC PAGE COUNT")
print("-" * 50)
html_dir = r'C:/Users/zqmco/scoop/persist/nginx/html/data'
if os.path.exists(html_dir):
    dirs = [d for d in os.listdir(html_dir) if os.path.isdir(os.path.join(html_dir, d))]
    print(f"  Static subdirectories: {sorted(dirs)}")
    files = os.listdir(html_dir)
    print(f"  Static files: {sorted(files)[:20]}")
else:
    print(f"  {html_dir} does not exist")

# 6. Check contribute.py existence
print("\n6. CONTRIBUTION SCRIPTS")
print("-" * 50)
for script in ['contribute.py', 'kb_bridge.py']:
    path = f'C:/Users/zqmco/Docker/volusia-portal/scripts/{script}'
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  {script}: EXISTS ({size} bytes)")
    else:
        print(f"  {script}: NOT FOUND")

# 7. Check backend gamification module
print("\n7. GAMIFICATION MODULE STATUS")
print("-" * 50)
for mod in ['backend/gamification/scoring.py', 'backend/gamification/missions.json', 'backend/gamification/badges.py']:
    path = f'C:/Users/zqmco/Docker/volusia-portal/{mod}'
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  {mod}: EXISTS ({size} bytes)")
    else:
        print(f"  {mod}: NOT FOUND")

print("\n" + "=" * 70)
print("EXPLORATION COMPLETE")
print("=" * 70)
