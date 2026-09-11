import urllib.request, ssl, re
ctx = ssl._create_unverified_context()

# Check all subdomains
subdomains = ['zqmlabs.com', 'api.zqmlabs.com', 'docs.zqmlabs.com', 'data.zqmlabs.com', 'www.zqmlabs.com']
for sd in subdomains:
    for scheme in ['https://']:
        url = scheme + sd
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, context=ctx, timeout=5)
            print(f'{url}: {resp.getcode()}')
        except Exception as e:
            print(f'{url}: ERROR - {str(e)[:60]}')

print()

# Check backend health endpoints
for ep in ['/health', '/latest', '/indicators', '/data/indicators.json']:
    try:
        req = urllib.request.Request(f'http://127.0.0.1:8000{ep}', headers={'User-Agent':'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, context=ctx, timeout=5)
        data = resp.read().decode()[:200]
        print(f'Backend {ep}: {resp.getcode()} | {data[:100]}')
    except Exception as e:
        print(f'Backend {ep}: ERROR - {str(e)[:60]}')

# Check docker container status
print()
print('=== DOCKER CONTAINERS ===')
import subprocess
try:
    r = subprocess.run(['docker', 'ps', '--format', '{{.Names}}\t{{.Status}}\t{{.Ports}}'], 
                      capture_output=True, text=True, timeout=10)
    for line in r.stdout.strip().split('\n'):
        if line:
            parts = line.split('\t')
            print(f'  {parts[0]}: {parts[1]} | {parts[2] if len(parts) > 2 else ""}')
except Exception as e:
    print(f'ERROR: {e}')
