# Get indicator names by category
import sqlite3
db = r'C:/Users/zqmco/Docker/volusia-portal/backend/data/volusia.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Full indicator names per category
cur.execute('SELECT category, name, value, unit, source FROM indicators ORDER BY category, name')
rows = cur.fetchall()
current_cat = None
for row in rows:
    if row[0] != current_cat:
        current_cat = row[0]
        print(f'\n{current_cat}:')
    print(f'  {row[1]} = {row[2]} {row[3]} (src: {row[4]})')

# Check what 'auto' source means
cur.execute("SELECT DISTINCT source FROM indicators ORDER BY source")
print('\n=== DISTINCT SOURCES ===')
for row in cur.fetchall():
    print(f'  {row[0]}')

conn.close()
