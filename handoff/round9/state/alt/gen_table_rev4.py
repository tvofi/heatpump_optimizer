#!/usr/bin/env python3
"""Schedule tables for plan rev 4 from the roster alone: open groups, their depth over open groups only, the longest
open chain, and one row per open group.   python3 gen_table_rev4.py ALT-ROSTER.json > table_rev4.md"""
import json, sys
r = json.load(open(sys.argv[1])); G = {g['group']: g for g in r['groups']}
DONE = ('done', 'rca-done')
opn = {k: g for k, g in G.items() if g['resume']['stage'] not in DONE}
s = lambda x: x.replace('R9-', '')
depth, best = {}, {}
def d(k):
    if k not in depth:
        ps = [a for a in opn[k]['after'] if a in opn]
        depth[k] = 1 + max((d(a) for a in ps), default=0)
        best[k] = max(((d(a), a) for a in ps), default=(0, None))[1]
    return depth[k]
for k in opn: d(k)
end = max(opn, key=lambda k: (depth[k], k)); chain = []
while end: chain.append(s(end)); end = best[end]
chain.reverse()
ea4 = 'R9-EG-A4'; c2 = []; e = ea4
while e: c2.append(s(e)); e = best[e]
print(f'Open groups: {len(opn)} of {len(G)}. Longest open chain ({len(chain)}): {" → ".join(chain)}.')
print(f'EG-A4 chain ({len(c2)}): {" → ".join(reversed(c2))}.\n')
print('| depth | PR | lane | open after-edges | issues (**Fixes**) | owner gate | fixer / reviewer | stage |')
print('|---|---|---|---|---|---|---|---|')
for k in sorted(opn, key=lambda k: (depth[k], G[k]['lane'], k)):
    g = G[k]; iss = ', '.join((f'**#{i}**' if i in g['fixes'] else f'#{i}') for i in g['issues']) or '—'
    af = ', '.join(s(a) for a in g['after'] if a in opn) or '—'
    gate = 'yes' if g['owner_gate'] else '—'
    print(f'| {depth[k]} | {s(k)} | {g["lane"]} | {af} | {iss} | {gate} | {g["model"]["fixer"]} / {g["model"]["reviewer"]} | {g["resume"]["stage"]} |')
