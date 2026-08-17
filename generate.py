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
    # Column-order-agnostic parser: maps columns by header name instead of
    # fixed position, and stops after the first table (a sheet may contain
    # more than one tab/table -- e.g. a "Original"/backup tab -- only the
    # first one is the live price list).
    rows, header, col = [], False, {}
    for line in md.split('\n'):
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        cells = [c for c in cells if c]
        if not cells:
            continue
        if re.match(r'^:?-+:?$', cells[0]):
            continue
        if any(re.search(r'produto|product', c, re.I) for c in cells):
            if header:
                break  # second table's header -- stop, only use the first table
            header = True
            for i, c in enumerate(cells):
                cl = c.lower()
                if 'produto' in cl or 'product' in cl:
                    col['name'] = i
                elif 'wholesale' in cl:
                    col['wholesale'] = i
                elif 'retail' in cl:
                    col['retail'] = i
                elif 'status' in cl:
                    col['status'] = i
            continue
        if not header or len(cells) < 4:
            continue
        rows.append({
            "name": cells[col['name']],
            "wholesale": charm(cells[col['wholesale']]),
            "retail": charm(cells[col['retail']]),
            "status": "special" if "special" in cells[col['status']].lower() else "stock",
        })
    return rows

import os
def img_tokens(s):
    out = []
    for m in re.findall(r'[Vv]-?\s?(\d+)\s*([A-Za-z]*)', s):
        if m[1]:
            out.append('V' + m[0] + m[1].upper())
        out.append('V' + m[0])
    if 'stepless' in s.lower():
        out.append('STEPLESS')
    return out

def find_image(name, imap):
    for t in img_tokens(name):
        if t in imap:
            return imap[t]
    return None

def us_date(d):
    return d.strftime("%B %d, %Y").replace(" 0", " ")

md = open(sys.argv[1]).read()
rows = parse(md)
try:
    imap = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img', 'map.json')))
except FileNotFoundError:
    imap = {}
for r in rows:
    r["img"] = find_image(r["name"], imap)
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
