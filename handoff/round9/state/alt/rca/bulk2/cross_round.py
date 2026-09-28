#!/usr/bin/env python3
"""Evaluate barrier-trigger rules over the v2 register (phase A1 rows, flags NOT applied).
Rule A (policy today): N>=3 in one round (judged + counted beyond).
Rule W: >=3 over any 3 consecutive rounds.  Rule T: >=5 total while open.
Prints, per class, the first round each rule fires and whether A ever fired."""
import csv, sys, collections, json
rows = list(csv.DictReader(open(sys.argv[1]), delimiter='\t'))
barriered_now = set(json.load(open(sys.argv[2])).keys()) if len(sys.argv) > 2 else set()
per = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    per[r['class_id']][int(r['round'][1:])] += 1
print(f"{'class':20} {'tot':>4} {'A_first':>7} {'W_first':>7} {'T_first':>7}  per-round")
out = {}
for c in sorted(per):
    cnt = per[c]; tot = 0; a = w = t = None
    for rd in range(1, 10):
        tot += cnt[rd]
        if a is None and cnt[rd] >= 3: a = rd
        if w is None and sum(cnt[x] for x in (rd-2, rd-1, rd)) >= 3: w = rd
        if t is None and tot >= 5: t = rd
    out[c] = dict(total=tot, A=a, W=w, T=t)
    print(f"{c:20} {tot:>4} {str(a):>7} {str(w):>7} {str(t):>7}  " + ' '.join(f"R{k}={cnt[k]}" for k in sorted(cnt)))
print()
print("A never fired, W or T fired:", [c for c, v in out.items() if v['A'] is None and (v['W'] or v['T'])])
print("W fires strictly before A:", [(c, v['W'], v['A']) for c, v in out.items() if v['W'] and (v['A'] is None or v['W'] < v['A'])])
print("T fires, W never:", [c for c, v in out.items() if v['T'] and not v['W']])
