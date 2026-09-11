import urllib.request, ssl, json, re
ctx = ssl._create_unverified_context()

# 1. Data quality check - are indicators actually populated?
print("=== DATA QUALITY (INDICATORS) ===")
categories = ["economic","demographics","housing","transportation","tourism","safety","health","environment","education","climate","government-finance"]
for cat in categories:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:8000/data/{cat}.json", headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=5)
        data = json.loads(resp.read().decode())
        indicators = data.get('indicators', data.get('data', []))
        # Check if indicators have actual values (not empty/placeholder)
        if isinstance(indicators, list) and len(indicators) > 0:
            # Check first indicator structure
            first = indicators[0] if indicators else {}
            if isinstance(first, dict):
                has_value = any(k for k in first.keys() if 'value' in k.lower() or 'count' in k.lower() or 'amount' in k.lower() or 'population' in k.lower() or 'rate' in k.lower())
                print(f"  {cat}: {len(indicators)} indicators | sample_keys={list(first.keys())[:5]} | has_values={has_value}")
            else:
                print(f"  {cat}: {len(indicators)} indicators (non-dict)")
        elif isinstance(indicators, dict):
            print(f"  {cat}: dict with {len(indicators)} keys")
        else:
            print(f"  {cat}: EMPTY (count=0)")
    except Exception as e:
        print(f"  {cat}: ERROR - {str(e)[:50]}")

# 2. Full mission list for gamification
print()
print("=== ALL MISSIONS ===")
try:
    req = urllib.request.Request("http://127.0.0.1:8000/api/gamification/missions/test_user", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=5)
    data = json.loads(resp.read().decode())
    missions = data.get('missions', [])
    print(f"Total missions defined: {len(missions)}")
    for m in missions:
        print(f"  {m.get('id','?')}: {m.get('name','?')} (XP: {m.get('xp','?')})")
except Exception as e:
    print(f"ERROR: {e}")

# 3. Check leaderboard endpoint
print()
print("=== LEADERBOARD ===")
try:
    req = urllib.request.Request("http://127.0.0.1:8000/gamification/leaderboard", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=5)
    data = json.loads(resp.read().decode())
    if isinstance(data, dict):
        print(f"Type: dict | keys: {list(data.keys())[:5]}")
        if 'leaderboard' in data:
            lb = data['leaderboard']
            print(f"Leaderboard entries: {len(lb)}")
        elif 'rankings' in data:
            print(f"Rankings entries: {len(data['rankings'])}")
        else:
            print(json.dumps(data, indent=2)[:300])
    elif isinstance(data, list):
        print(f"List of {len(data)} entries")
        if len(data) > 0:
            print(f"First: {data[0]}")
except Exception as e:
    print(f"ERROR: {e}")

# 4. Check static pages for real indicator content
print()
print("=== STATIC PAGE CONTENT SAMPLES ===")
pages = [
    ("Economic", "https://zqmlabs.com/data/economic/"),
    ("Tourism", "https://zqmlabs.com/data/tourism/"),
    ("Climate", "https://zqmlabs.com/data/climate/"),
    ("Leaders", "https://zqmlabs.com/leaders/"),
]
for name, url in pages:
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        html = resp.read().decode()
        # Find any data values (numbers, percentages, dollar amounts)
        numbers = re.findall(r'\b\d[\d,]*\.?\d*\s*(?:%|USD|thousand|million|billion)?', html)[:5]
        has_charts = 'chart' in html.lower() or 'graph' in html.lower()
        print(f"{name}: numbers_found={len(numbers)} | sample={numbers[:3]} | charts={has_charts}")
    except Exception as e:
        print(f"{name}: ERROR - {str(e)[:50]}")
