import urllib.request, ssl, json, re
ctx = ssl._create_unverified_context()

# 1. Check safety and government-finance categories
print("=== EMPTY CATEGORIES ===")
for cat in ['safety', 'government-finance']:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:8000/data/{cat}.json", headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=5)
        data = json.loads(resp.read().decode())
        print(f"{cat}: category={data.get('category','?')} count={data.get('count','?')} indicators={data.get('indicators', data.get('data', []))}")
    except Exception as e:
        print(f"{cat}: ERROR - {e}")

# 2. Check pathway missions mapping from skill file
print()
print("=== PATHWAY MAPPING ===")
# Read the skill file to get pathway descriptions
r = open(r'C:/Users/zqmco/AppData/Local/hermes/skills/zqm/project-volusia/SKILL.md', 'r')
content_sk = r.read()
r.close()
# Find the pathways table
lines = content_sk.split('
')
in_pathways = False
for i, line in enumerate(lines):
    if 'pathway' in line.lower() or 'Pathway' in line or '| A' in line or '| B' in line:
        if '|' in line and ('A |' in line or 'Pathway' in line):
            print(f"Line {i+1}: {line.strip()[:120]}")

# 3. Check /data/ page for links to all categories
print()
print("=== DATA INDEX PAGE LINKS ===")
try:
    req = urllib.request.Request("https://zqmlabs.com/data/", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode()
    links = re.findall(r'href="(/data/[^"]+)"', html)
    print(f"Found {len(links)} links:")
    for l in sorted(set(links)):
        print(f"  {l}")
except Exception as e:
    print(f"ERROR: {e}")

# 4. Check if /data/real-estate/ static page exists
print()
print("=== REAL-ESTATE STATIC PAGE ===")
try:
    req = urllib.request.Request("https://zqmlabs.com/data/real-estate/", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode()
    # Extract first meaningful content
    title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    print(f"real-estate/ exists: {resp.getcode()} | title={title.group(1) if title else 'N/A'}")
    print(f"Has indicators: {'indicator' in html.lower() or 'economic' in html.lower()}")
except Exception as e:
    print(f"ERROR: {e}")

# 5. Check /data/ index for missing category JSON endpoints
print()
print("=== MISSING JSON ENDPOINTS ===")
for cat in ['real-estate']:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:8000/data/{cat}.json", headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=5)
        print(f"/data/{cat}.json: {resp.getcode()}")
    except Exception as e:
        print(f"/data/{cat}.json: NOT AVAILABLE ({str(e)[:40]})")
