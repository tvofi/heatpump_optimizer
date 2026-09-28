import json, re, sys
roster = json.load(open('roster-rev2.json'))
plan = open('alt/handoff/round9/state/ALT-ENDGAME-PLAN.md').read()
old = {}
for line in plan.splitlines():
    m = re.match(r'^\| \d+ \| (\S+) \| (\S+) \| [^|]* \| ([^|]*) \| ([^|]*) \| ([^|]*) \| ([^|]*) \| [^|]* \|$', line)
    if m: old[m.group(1)] = dict(issues=m.group(3).strip(), gate=m.group(4).strip(), carry=m.group(5).strip(), what=m.group(6).strip())
G = {g['group']: g for g in roster['groups']}
open_ = {k for k, g in G.items() if g['resume'].get('stage') not in ('done', 'rca-done')}
depth = {}
def d(k):
    if k in depth: return depth[k]
    oa = [a for a in G[k]['after'] if a in open_]
    depth[k] = 1 + max((d(a) for a in oa), default=0)
    return depth[k]
NEW = {
 'R9-EG-B9': dict(gate='—', carry='—', what='Boost overlay acts on a copy; tile and advisor stop borrowing the what-if cache (sev:high actuation)'),
 'R9-EG-B10': dict(gate='—', carry='—', what='Solve lifecycle: dropped re-solve, override identity, per-entry fallback streak'),
 'R9-EG-R0': dict(gate='tvofi reviews the move list', carry='—', what='Register v2 data: rounds 1-9 classified, enum, RCA docs in-tree'),
 'R9-EG-R1': dict(gate='policy clauses; audit-verify.js code-owned', carry='—', what='Deterministic register fold and its check'),
 'R9-F10.1c': dict(gate='override-length fix or exemption', carry='—', what='P7 tracer: config and straddle arms'),
 'R9-F10.7': dict(gate='host Profiler run (tvofi)', carry='—', what='nightly-ha loop-stall heartbeat (v6.6.0 freeze diagnosis)'),
 'R9-F7.4': dict(gate='away and sv compressor: rename or allow', carry='—', what='Declared entity families and one contiguity check (N-name-sort barrier)'),
 'R9-F11.7': dict(gate='tests.yml code-owned', carry='—', what='graders-head-copy governance arm under the Actions token'),
}
CARRY = {'R9-EG-B1': 'H1-H4, P12 (#1736)', 'R9-F1.7': 'P10 barrier', 'R9-F1.8': 'P8 feed currency', 'R9-F2.4': 'P4 refusal',
         'R9-F10.3': 'I2 strace', 'R9-F10.4': 'N-structure-blind; #1545', 'R9-F11.4': 'merge_shape_guard (#1041)'}
rows = []
for k in open_:
    g = G[k]; short = k.replace('R9-', '')
    o = old.get(short) or NEW.get(k) or {}
    fixes = set(g.get('fixes') or [])
    issues = o.get('issues') if short in old else ', '.join((f'**#{n}**' if n in fixes else f'#{n}') for n in g['issues']) or '—'
    carry = o.get('carry', '—')
    if k in CARRY: carry = (carry + '; ' if carry not in ('—', '') else '') + CARRY[k]
    oa = [a.replace('R9-', '') for a in g['after'] if a in open_]
    rows.append((d(k), short, g['lane'], ', '.join(oa) or '—', issues, o.get('gate', '—'), carry, o.get('what', ''), g['resume'].get('stage')))
rows.sort(key=lambda r: (r[0], r[2] != 'F1', r[1]))
out = ['| wave | PR | lane | open after-edges | issues (**Fixes**) | owner gate | carry in | what | stage |', '|---|---|---|---|---|---|---|---|---|']
out += [f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} |' for r in rows]
open('table_rev2.md', 'w').write('\n'.join(out) + '\n')
print(len(rows), 'open groups;', 'missing what:', [r[1] for r in rows if not r[7]])
