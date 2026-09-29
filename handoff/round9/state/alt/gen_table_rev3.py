#!/usr/bin/env python3
"""Plan rev 3 section 4.1: the per-PR table over open groups of roster rev 3.

    python3 gen_table_rev3.py ROSTER_REV3.json PLAN_REV2.md > table_rev3.md

Row text for groups rev 2 already listed is carried from rev 2's table; F1.6's owner-gate and what columns
come from rev 2's row too. 'wave' is the dependency depth over open groups (1 = startable once nothing
open precedes it; F1.6, in review, is wave 1).
"""
import json, re, sys

roster = json.load(open(sys.argv[1]))
old = {}
for line in open(sys.argv[2]).read().splitlines():
    m = re.match(r'^\| \d+ \| (\S+) \| (\S+) \| [^|]* \| ([^|]*) \| ([^|]*) \| ([^|]*) \| ([^|]*) \| [^|]* \|$', line)
    if m:
        old[m.group(1)] = dict(issues=m.group(3).strip(), gate=m.group(4).strip(), carry=m.group(5).strip(),
                               what=m.group(6).strip())
G = {g['group']: g for g in roster['groups']}
open_ = {k for k, g in G.items() if g['resume'].get('stage') not in ('done', 'rca-done')}
depth = {}


def d(k):
    if k in depth:
        return depth[k]
    oa = [a for a in G[k]['after'] if a in open_]
    depth[k] = 1 + max((d(a) for a in oa), default=0)
    return depth[k]


NEW = {
    'R9-EG-A1': dict(gate='code-owned merge review', carry='—', what='Architecture score, report-only, with its calibration self-check'),
    'R9-EG-A2': dict(gate='—', carry='—', what='One copy per formula and helper (P2/P3 clones; dup_pairs_v1 121 → ≤40)'),
    'R9-EG-A3': dict(gate='—', carry='—', what='Parameter objects for solver and planner signatures'),
    'R9-F7.5': dict(gate='—', carry='—', what='The three recorded family splits renamed (en/sv away, sv compressor)'),
    'R9-EG-L0': dict(gate='settings changes are tvofi\'s hand', carry='—', what='Re-measure and close the 30 legacy round-5 issues; disposition #1655'),
    'R9-EG-B11': dict(gate='—', carry='—', what='Typed entry configuration, read once per entry (#1745)'),
    'R9-EG-A4': dict(gate='ruleset required context is tvofi\'s hand', carry='—', what='Architecture score becomes a required check'),
}
DS = {'R9-EG-B1': '+29.5', 'R9-EG-B3': '+50.9', 'R9-EG-B6': '+4.2', 'R9-EG-B2': '+3.8', 'R9-EG-B7': '+5.2',
      'R9-F10.4': '+5.6', 'R9-EG-A2': '+14.1', 'R9-F7.5': '+10.9', 'R9-EG-A3': '+0.6', 'R9-EG-B5': '≈0 (limit)'}
CARRY = {'R9-F10.4': 'metric review (retire/merge/modify, 11 defects)'}
rows = []
for k in open_:
    g = G[k]
    short = k.replace('R9-', '')
    o = old.get(short) or NEW.get(k) or {}
    fixes = set(g.get('fixes') or [])
    issues = o.get('issues') if short in old else (', '.join((f'**#{n}**' if n in fixes else f'#{n}') for n in g['issues']) or '— (filed on adoption)')
    carry = o.get('carry', '—')
    if k in CARRY:
        carry = (carry + '; ' if carry not in ('—', '') else '') + CARRY[k]
    oa = [a.replace('R9-', '') for a in g['after'] if a in open_]
    rows.append((d(k), short, g['lane'], ', '.join(oa) or '—', issues, o.get('gate', '—'), carry,
                 o.get('what', ''), DS.get(k, '—'), g['resume'].get('stage')))
rows.sort(key=lambda r: (r[0], r[2] != 'F1', r[1]))
out = ['| wave | PR | lane | open after-edges | issues (**Fixes**) | owner gate | carry in | what | expected ΔS | stage |',
       '|---|---|---|---|---|---|---|---|---|---|']
out += ['| ' + ' | '.join(str(x) for x in r) + ' |' for r in rows]
print('\n'.join(out))
print(f'{len(rows)} open groups; missing what: {[r[1] for r in rows if not r[7]]}', file=sys.stderr)
