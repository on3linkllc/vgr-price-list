#!/usr/bin/env python3
"""Build index.html from the Google Sheet markdown export.
Usage: python3 generate.py sheet.md
Applies charm pricing: every price is rounded UP to the next X.99.
"""
import sys, json, math, re
from datetime import date, timedelta

def charm(v):
    v = float(str(v).replace('$','').replace(',','').strip())
    result = math.floor(v) + 0.99
    if result < v:  # e.g. 68.995 edge
        result += 1.0
    return "${:,.2f}".format(result)

def parse(md):
    rows, header = [], False
    for line in md.split('\n'):
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        cells = [c for c in cells if c]
        if not header:
            if any(re.search(r'produto|product', c, re.I) for c in cells):
                header = True
            continue
        if len(cells) >= 4 and not re.match(r'^:?-+:?$', cells[0]):
            rows.append({
                "name": cells[0],
                "wholesale": charm(cells[1]),
                "retail": charm(cells[2]),
                "status": "special" if "special" in cells[3].lower() else "stock",
            })
    return rows

def us_date(d):
    return d.strftime("%B %d, %Y").replace(" 0", " ")

md = open(sys.argv[1]).read()
rows = parse(md)
if len(rows) < 5:
    sys.exit("ERROR: parsed only %d rows — sheet format may have changed, aborting." % len(rows))

today = date.today()
html = open('template.html').read()
html = html.replace('DATA_JSON', json.dumps(rows))
html = html.replace('ISSUED_DATE', us_date(today))
html = html.replace('VALID_DATE', us_date(today + timedelta(days=30)))
open('index.html','w').write(html)
open('data.json','w').write(json.dumps(rows, indent=1))
print("OK: %d products (%d in stock)" % (len(rows), sum(r['status']=='stock' for r in rows)))
