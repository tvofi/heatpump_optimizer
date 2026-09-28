#!/usr/bin/env python3
"""Prototype of countermeasure (iv): the register/ledger consistency check.
usage: register_check.py LEDGER.json REGISTER_ROWS.tsv
 (1) every register row (round, finding id) sits in exactly one class's instances;
 (2) every class whose per-round count ever reached 3 (defect-root-cause.md's own
     trigger, applied over the ledger's whole history) carries a barrier or an rca
     citation -- else it is OWED.
Exit 1 on any violation. v1 ledgers store instances as ["R2 D3-09", ...];
v2 as {"R2": ["D3-09"], ...}."""
import csv, json, sys, collections, ast
led = json.load(open(sys.argv[1]))
rows = list(csv.DictReader(open(sys.argv[2]), delimiter='\t'))
UNPARSED = []
where = collections.defaultdict(list); per = collections.defaultdict(collections.Counter)
for cid, c in led.items():
    if cid.startswith('_'): continue
    inst = c.get('instances', [])
    if isinstance(inst, str): inst = ast.literal_eval(inst)
    import re
    if isinstance(inst, list):
        pairs = [tuple(s.split(' ', 1)) for s in inst if re.match(r'^R\d+ ', s)]
        bad = [s for s in inst if not re.match(r'^R\d+ ', s)]
        if bad: UNPARSED.append((cid, len(bad)))
    else:
        pairs = [(r, f) for r, fs in inst.items() for f in fs]
    for r, f in pairs:
        where[(r, f)].append(cid); per[cid][r] += 1
unclassed = [(r['round'], r['finding_id']) for r in rows if (r['round'], r['finding_id']) not in where]
multi = [(k, v) for k, v in where.items() if len(v) > 1]
by_round = collections.Counter(r for r, _ in unclassed)
print(f"(1) register rows {len(rows)}; in no class {len(unclassed)} {dict(sorted(by_round.items()))}; in >1 class {len(multi)}")
owed = []
for cid, cnt in per.items():
    hit = [r for r, n in cnt.items() if n >= 3]
    c = led[cid]; has = c.get('barrier') not in (None, 'None', '') or c.get('rca') not in (None, 'None', '')
    if hit and not has: owed.append((cid, sorted(hit, key=lambda s: int(s[1:]))[0]))
print(f"(0) instances with no round-and-id form (not countable per round): {UNPARSED}")
print(f"(2) classes that met the per-round trigger with no barrier and no rca citation: {sorted(owed)}")
sys.exit(1 if unclassed or multi or owed or UNPARSED else 0)
