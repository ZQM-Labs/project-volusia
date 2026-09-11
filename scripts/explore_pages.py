import urllib.request, ssl, re
ctx = ssl._create_unverified_context()

# 1. Check /data/ index page
print("=== /data/ INDEX PAGE ===")
try:
    req = urllib.request.Request("https://zqmlabs.com/data/", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode()
    # Extract links
    links = re.findall(r'href="(/data/[^"]+)"', html)
    print(f"Links found: {len(links)}")
    for l in sorted(set(links)):
        print(f"  {l}")
    # Extract text content
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()[:500]
    print(f"\nPreview: {text[:300]}")
except Exception as e:
    print(f"ERROR: {e}")

# 2. Check /gamification/ page
print()
print("=== /gamification/ PAGE ===")
try:
    req = urllib.request.Request("https://zqmlabs.com/gamification/", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode()
    title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    # Extract missions count
    missions = re.findall(r'mission', html, re.IGNORECASE)
    print(f"Status: {resp.getcode()} | Title: {title.group(1) if title else 'N/A'}")
    # Extract pathway links
    path_links = re.findall(r'href="(/data/[a-z-]+/)"', html)
    print(f"Pathway links: {len(path_links)}")
    for p in sorted(set(path_links)):
        print(f"  {p}")
except Exception as e:
    print(f"ERROR: {e}")

# 3. Check /leaders/ page
print()
print("=== /leaders/ PAGE ===")
try:
    req = urllib.request.Request("https://zqmlabs.com/leaders/", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode()
    title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()[:500]
    print(f"Status: {resp.getcode()} | Title: {title.group(1) if title else 'N/A'}")
    print(f"Preview: {text[:300]}")
except Exception as e:
    print(f"ERROR: {e}")

# 4. Check real-estate static page content
print()
print("=== /data/real-estate/ PAGE ===")
try:
    req = urllib.request.Request("https://zqmlabs.com/data/real-estate/", headers={"User-Agent":"Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    html = resp.read().decode()
    title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()[:500]
    print(f"Status: {resp.getcode()} | Title: {title.group(1) if title else 'N/A'}")
    print(f"Preview: {text[:300]}")
except Exception as e:
    print(f"ERROR: {e}")

# 5. Check pathway pages vs sitemap discrepancy
print()
print("=== DISCREPANCY CHECK ===")
sitemap_cats = ['economic','demographics','housing','transportation','tourism','safety','health','environment','education','climate','government-finance','public-safety','real-estate']
pathway_pages = ['data-source','business-owner','resident','tourist','industry-mover','school-project','social-media','tool','direct-citizenry','code-feature','infrastructure','ci-cd-devops','testing-qa','documentation']
# Which pathway pages are in sitemap?
print("Sitemap data categories:", sitemap_cats)
print("Pathway pages (NOT in sitemap):", pathway_pages)
print("These pathway pages exist but are NOT listed in sitemap.xml")
