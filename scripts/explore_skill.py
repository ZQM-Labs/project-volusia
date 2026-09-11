import urllib.request, ssl, json, re
ctx = ssl._create_unverified_context()

# Read the skill file directly to extract pathways
with open(r'C:/Users/zqmco/AppData/Local/hermes/skills/zqm/project-volusia/SKILL.md', 'r') as f:
    content = f.read()

# Find pathway table rows (lines with | A | or | B | etc)
print("=== PATHWAYS TABLE ===")
lines = content.split('\n')
for i, line in enumerate(lines):
    if re.search(r'\|[ A-N ]\s*\|', line):
        print(f"L{i+1}: {line.strip()[:140]}")

# Find mission descriptions
print()
print("=== MISSION-TO-PATHWAY MAPPING ===")
for i, line in enumerate(lines):
    if 'pathway' in line.lower() and ('mission' in line.lower() or 'task' in line.lower() or 'Tier' in line):
        print(f"L{i+1}: {line.strip()[:140]}")

# Find tier definitions
print()
print("=== TIERS ===")
tier_section = False
for i, line in enumerate(lines):
    if 'tier' in line.lower() or 'Tier' in line:
        if len(line.strip()) > 10:
            print(f"L{i+1}: {line.strip()[:140]}")
