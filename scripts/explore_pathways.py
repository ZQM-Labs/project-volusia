import urllib.request, ssl, re, json
ctx = ssl._create_unverified_context()

# 1. Check each pathway static page for actual CONTENT (not just 200)
print("=== PATHWAY PAGE CONTENT QUALITY ===")
pathway_slugs = {
    'A': 'data-source', 'B': 'business-owner', 'C': 'resident',
    'D': 'tourist', 'E': 'industry-mover', 'F': 'school-project',
    'G': 'social-media', 'H': 'tool', 'I': 'direct-citizenry',
    'J': 'code-feature', 'K': 'infrastructure', 'L': 'ci-cd-devops',
    'M': 'testing-qa', 'N': 'documentation'
}
for p_id, slug in pathway_slugs.items():
    try:
        req = urllib.request.Request(f"https://zqmlabs.com/data/{slug}/", headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=5)
        html = resp.read().decode()
        # Check for actual content (not just meta tags)
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        # Strip meta/head content
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
        body_text = body_match.group(1) if body_match else ''
        body_text = re.sub(r'<[^>]+>', ' ', body_text)
        body_text = re.sub(r'\s+', ' ', body_text).strip()[:200]
        has_content = len(body_text) > 100
        print(f"  Pathway {p_id} ({slug}): {'✓' if has_content else '✗'} | {body_text[:100]}")
    except Exception as e:
        print(f"  Pathway {p_id} ({slug}): ERROR - {str(e)[:40]}")

# 2. Check if /data/public-safety/ is a sitemap entry
print()
print("=== PUBLIC-SAFETY IN SITEMAP ===")
try:
    req = urllib.request.Request("https://zqmlabs.com/sitemap.xml", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=5)
    sitemap = resp.read().decode()
    has_ps = 'public-safety' in sitemap
    has_res = 'real-estate' in sitemap
    print(f"public-safety in sitemap: {has_ps}")
    print(f"real-estate in sitemap: {has_res}")
except Exception as e:
    print(f"ERROR: {e}")

# 3. Check data/ subdirectory structure for JSON files
print()
print("=== DATA/ DIRECTORY JSON FILES ===")
import os
data_dir = r'C:/Users/zqmco/scoop/persist/nginx/html/data'
json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
print(f"JSON files in html/data/: {sorted(json_files)}")
for jf in sorted(json_files):
    size = os.path.getsize(os.path.join(data_dir, jf))
    # Check if empty
    with open(os.path.join(data_dir, jf)) as f:
        content = f.read()
    try:
        d = json.loads(content)
        if isinstance(d, dict):
            ind_count = len(d.get('indicators', d.get('data', []))) if isinstance(d.get('indicators', d.get('data')), list) else 'N/A'
        else:
            ind_count = 'N/A'
    except:
        ind_count = 'PARSE_ERROR'
    print(f"  {jf}: {size} bytes, indicators={ind_count}")

# 4. Check if pathways have corresponding backend JSON endpoints
print()
print("=== PATHWAY JSON ENDPOINTS ===")
for p_id, slug in pathway_slugs.items():
    try:
        req = urllib.request.Request(f"http://127.0.0.1:8000/data/{slug}.json", headers={"User-Agent":"Mozilla/5.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=3)
        print(f"  /data/{slug}.json: {resp.getcode()}")
    except Exception as e:
        print(f"  /data/{slug}.json: NOT FOUND")

# 5. Check contribute.py for pathway support
print()
print("=== CONTRIBUTION PIPELINE ===")
contribute_path = r'C:/Users/zqmco/Docker/volusia-portal/scripts/contribute.py'
if os.path.exists(contribute_path):
    with open(contribute_path) as f:
        c = f.read()
    # Find pathway references
    for p_id in pathway_slugs.keys():
        if p_id in c:
            print(f"  Pathway {p_id}: referenced in contribute.py")
    
# 6. Check /data/ index page shows all 14 pathway links
print()
print("=== /data/ INDEX - ALL LINKS ===")
try:
    req = urllib.request.Request("https://zqmlabs.com/data/", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=5)
    html = resp.read().decode()
    all_links = re.findall(r'href="(/data/[^"]+)"', html)
    # Check for pathway links
    pathway_links = [l for l in all_links if any(slug in l for slug in pathway_slugs.values())]
    category_links = [l for l in all_links if l not in pathway_links]
    print(f"Total links: {len(all_links)}")
    print(f"Category links (in sitemap): {sorted(set(category_links))}")
    print(f"Pathway links (NOT in sitemap): {sorted(set(pathway_links))}")
except Exception as e:
    print(f"ERROR: {e}")
