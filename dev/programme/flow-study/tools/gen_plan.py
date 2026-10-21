"""Render the projected schedule (projection.json) of the shadow roster as markdown tables."""
import json, functools, collections
d = json.load(open('shadow-r10-groups.json')); G = {g['group']: g for g in d['groups']}
P = json.load(open('projection.json'))['state']
DONE = ('done', 'rca-done'); PROC = {'instrument', 'policy', 'rca', 'record', 'docs', 'fix'}
st = lambda n: (G[n].get('resume') or {}).get('stage')
from simulate_rules import HOT_ONLY
edges = lambda n: [a for a in G[n].get('after') or [] if (n, a) not in HOT_ONLY]
@functools.lru_cache(None)
def depth(n): return 0 if st(n) in DONE else 1 + max([depth(a) for a in edges(n)] or [0])
def lane(n):
    if n.startswith('R10-FLOW'): return 'K'
    if G[n]['kind'] in PROC or n.startswith('R10-FLOW'): return 'C'
    if any('coordinator.py' in h for h in G[n].get('hot_files') or []) or depth(n) >= 3: return 'A'
    return 'B'
rows = sorted((P[n]['merged'], round(P[n]['start']), n) for n in G if n in P and P[n].get('merged', -1) != -1)
out = ['| day | merge h | start h | group | lane | size | kind | stage now | after (as re-chained) |',
       '|---|---|---|---|---|---|---|---|---|']
for m, s0, n in rows:
    g = G[n]
    out.append(f"| {m // 24} | {m} | {s0} | {n} | {lane(n)} | {g.get('size') or '-'} | {g['kind']} | {st(n)} | {', '.join(edges(n)) or '—'} |")
day = collections.Counter(m // 24 for m, _, _ in rows)
summary = ' · '.join(f'day {k}: {v}' for k, v in sorted(day.items()))
open('schedule.md', 'w').write(summary + '\n\n' + '\n'.join(out) + '\n')
print(summary, len(rows))
