import urllib.request, ssl, json, re
ctx = ssl._create_unverified_context()

# 1. Check empty categories
print("=== EMPTY CATEGORIES ===")
for cat in ['safety', 'government-finance']:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:8000/data/{cat}.json", headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=5)
        data = json.loads(resp.read().decode())
        inds = data.get('indicators', data.get('data', []))
        print(f"{cat}: category={data.get('category','?')} count={data.get('count','?')} indicators={len(inds) if isinstance(inds,list) else 'dict'}")
    except Exception as e:
        print(f"{cat}: ERROR - {str(e)[:60]}")

# 2. Check /data/ index page links
print("\n=== DATA INDEX LINKS ===")
try:
    req = urllib.request.Request("https://zqmlabs.com/data/", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode()
    links = re.findall(r'href="(/data/[^"]+)"', html)
    print(f"Found {len(links)} data links:")
    for l in sorted(set(links)):
        print(f"  {l}")
except Exception as e:
    print(f"ERROR: {e}")

# 3. Check pathways section in skill
print("\n=== PATHWAY REFERENCES ===")
try:
    with open(r'C:/Users/zqmco/AppData/Local/hermes/skills/zqm/project-volusia/SKILL.md', 'r') as f:
        content = f.read()
    # Find pathway table
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('|') and (' | ' in line) and i < 100:
            # Look for pathway A-N
            if re.search(r'\b[A-N]\s*\|', line) or 'Pathway' in line or '---' in line:
                print(f"L{i+1}: {line.strip()[:130]}")
except Exception as e:
    print(f"ERROR: {e}")

# 4. Check /data/real-estate/ and whether there's a JSON endpoint
print("\n=== REAL-ESTATE ===")
try:
    req = urllib.request.Request("https://zqmlabs.com/data/real-estate/", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    print(f"Static page: {resp.getcode()}")
    html = resp.read().decode()
    # Does it link to a JSON endpoint?
    json_refs = re.findall(r'/data/real-estate\.json', html)
    print(f"Has JSON ref: {bool(json_refs)}")
except Exception as e:
    print(f"ERROR: {e}")

# 5. Check all backend routes exist (from main.py)
print("\n=== BACKEND ROUTE CHECK ===")
routes = [
    ('GET', '/health'), ('GET', '/latest'), ('GET', '/indicators'),
    ('GET', '/data/economic.json'), ('GET', '/data/demographics.json'),
    ('GET', '/data/housing.json'), ('GET', '/data/transportation.json'),
    ('GET', '/data/tourism.json'), ('GET', '/data/safety.json'),
    ('GET', '/data/health.json'), ('GET', '/data/environment.json'),
    ('GET', '/data/education.json'), ('GET', '/data/climate.json'),
    ('GET', '/data/government-finance.json'),
    ('GET', '/data/indicators.json'),
]
for method, path in routes:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:8000{path}", headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=5)
        body = resp.read().decode()
        try:
            d = json.loads(body)
            if 'indicators' in d:
                cnt = len(d['indicators']) if isinstance(d['indicators'], list) else 'dict'
            elif 'data' in d:
                cnt = len(d['data']) if isinstance(d['data'], list) else 'dict'
            else:
                cnt = 'N/A'
        except:
            cnt = 'N/A'
        print(f"  {method} {path}: {resp.getcode()} | {cnt}")
    except Exception as e:
        print(f"  {method} {path}: {str(e)[:40]}")

# 6. Leaderboard
print("\n=== LEADERBOARD ===")
try:
    req = urllib.request.Request("http://127.0.0.1:8000/gamification/leaderboard", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=5)
    data = json.loads(resp.read().decode())
    if 'leaderboard' in data:
        print(f"Leaderboard has {len(data['leaderboard'])} entries")
        for entry in data['leaderboard'][:5]:
            print(f"  {entry}")
    else:
        print(json.dumps(data, indent=2)[:500])
except Exception as e:
    print(f"ERROR: {e}")
