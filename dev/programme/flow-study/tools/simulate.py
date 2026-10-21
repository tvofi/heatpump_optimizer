"""Round-completion projection for the round-10 roster (Lean flow study).

A model, not a promise. Hour 0 = adoption. Each hour is a merge pitch: everything verdicted
whose after-edges are merged lands together (the batch proof). Dispatch is pull: a group starts
when its edges allow and its lane has room.

Scenario switches (env):
  LEAD=now|target   lead per size: round-10 measured medians, or the future-state targets
  RAMP=<h>          hours to ramp linearly from now to target (LEAD=target only)
  CAPS=<json>       lane caps; CAPS=none means only HPO_WIP_CAP 6 in total (today)
  RECHAIN=0|1       drop coordinator.py edges that exist only for file order (HOT_ONLY below)
  STACK=0|1         a remaining hot-file edge is satisfied when the predecessor is verdicted
  ADD=<h>           a new roster group arrives every <h> hours (scope creep; 0 = frozen scope)
  FLY=<h>           a fly-in (S, lane F) arrives every <h> hours
  EFF=0|1           apply EFFECTS: a merged enabler shortens the lead of every group dispatched after it
  PAR=0|1           PARALLEL edges order merges only (P1 builds beside PR G; P2's units beside P1), P2 keeps TAIL h after P1
  PRIO=0|1          dispatch PRIORITY groups first in their lane (the revision-10 CD3 order)
  RESERVE=0|1       the next critical-chain link dispatches even when its lane is at cap (CCPM capacity buffer)
  EFFX=<x>          scale every EFFECTS figure (sensitivity)
  DESIGN=0|serial|pipe  design + design-review steps for groups at or above DTH (design-seat pre-study)
  DTH=M|L|XL        the size threshold; DSCALE scales design hours, DFRAC the share of review blocks the design removes
  CUT=any|gap       P2's cut-over: 'gap' waits for an hour in which no critical-chain group is within 1.5 h of boarding
"""
import json, os, sys, functools

d = json.load(open(sys.argv[1])); H = int(sys.argv[2]) if len(sys.argv) > 2 else 200
E = os.environ.get
LEADMODE = E('LEAD', 'target'); RAMP = int(E('RAMP', '48'))
CAPS_RAW = E('CAPS', '{"A": 4, "B": 4, "C": 3, "F": 2}')
CAPS = None if CAPS_RAW == 'none' else json.loads(CAPS_RAW)
RECHAIN = E('RECHAIN', '1') == '1'; REC = E('REC', '1') == '1'; STUDYADD = E('STUDYADD', '1') == '1'; STACK = E('STACK', '0') == '1'
ADD = int(E('ADD', '0')); FLY = int(E('FLY', '4'))
INPROG = float(E('INPROG', '1.0'))  # share of today's lead still ahead of an in-progress group
KAIZEN = int(E('KAIZEN', '2'))      # >0: flow groups get their own lane K of this size
HOLD = int(E('HOLD', '12'))
EFF = E('EFF', '0') == '1'; PAR = E('PAR', '0') == '1'; PRIO = E('PRIO', '0') == '1'; CUT = E('CUT', 'any')
from simulate_rules import EFFECTS, PARALLEL, TAIL, PRIORITY, CHAIN, CUTOVER, EXPEDITE, FAST
EFFX = float(E('EFFX', '1')); RESERVE = E('RESERVE', '0') == '1'
DESIGN = E('DESIGN', '0'); DTH = E('DTH', 'L'); DSCALE = float(E('DSCALE', '1')); DFRAC = float(E('DFRAC', '0.15'))
REWORK_H = float(E('REWORK_H', '2.0')); REVAL_H = float(E('REVAL_H', '0.5'))
_ORD = {'S': 0, 'M': 1, 'L': 2, 'XL': 3}
D_HOURS = {'M': 2.0, 'L': 3.0, 'XL': 4.0}      # design seat plus design review, wall hours (mid)
DR_HOURS = {'M': 1.0, 'L': 1.0, 'XL': 1.5}     # design review only, where a design or prototype already exists
BLOCKS = {'S': 0.70, 'M': 0.75, 'L': 1.80, 'XL': 1.80}  # measured blocked verdicts per reviewed PR (review_rounds.py)
def designed(n):
    g = G.get(n, {})
    return DESIGN != '0' and _ORD.get(g.get('size'), -1) >= _ORD[DTH]
def has_design(n):
    b = G.get(n, {}).get('brief') or ''
    return any(k in b for k in ('approved design', 'prototype', '.patch'))
def d_hours(n):
    sz = G[n].get('size')
    return DSCALE * (DR_HOURS if has_design(n) else D_HOURS)[sz]
def d_gain(n):
    return DFRAC * BLOCKS[G[n].get('size')] * REWORK_H
PITCH = int(E('PITCH', '1'))        # hours between merge trains          # hours before any not-started group may dispatch (drain first)
DONE = ('done', 'rca-done')
PROC = {'instrument', 'policy', 'rca', 'record', 'docs', 'fix'}
NOW = {'S': 11, 'M': 12, 'L': 20, 'XL': 24, None: 11}
TGT = {'S': 3, 'M': 5, 'L': 8, 'XL': 12, None: 3}
# Edges between coordinator.py groups whose owning seams (architect notes) are disjoint: they
# order merges on one file, not one change on another. The RECHAIN seat confirms each one.
from simulate_rules import HOT_ONLY, added as added_edges

G = {g['group']: g for g in d['groups']}
# Flow groups go first in lane C, biggest round-time lever first.
FLOW_ORDER = ['R10-FLOW-RELAY-HOLD', 'R10-FLOW-BODY-PATCH', 'R10-FLOW-MAIN-GATE', 'R10-FLOW-YIELD-PROBE', 'R10-FLOW-DISPATCH',
              'R10-FLOW-RECHAIN', 'R10-FLOW-ROSTER-FREEZE', 'R10-FLOW-BODY-ONLY', 'R10-FLOW-PULL',
              'R10-FLOW-ANDON', 'R10-FLOW-WIP', 'R10-FLOW-JIDOKA', 'R10-FLOW-POSTMERGE', 'R10-FLOW-BOARD',
              'R10-FLOW-AUTOTRAIN', 'R10-FLOW-MQ-PROBE', 'R10-FLOW-RECORD-PITCH']
st = lambda g: (g.get('resume') or {}).get('stage')
def edges(n):
    base = [a for a in (G[n].get('after') or []) if not (RECHAIN and (n, a) in HOT_ONLY)]
    return base + ([a for a in added_edges(n, REC, STUDYADD) if a in G and a not in base] if RECHAIN else [])

@functools.lru_cache(None)
def depth(n):
    if st(G[n]) in DONE: return 0
    return 1 + max([depth(a) for a in edges(n)] or [0])

def lane(n):
    g = G[n]
    if n.startswith(('R10-FLY', 'FLY-')): return 'F'
    if KAIZEN and n.startswith('R10-FLOW'): return 'K'
    if g['kind'] in PROC or n.startswith('R10-FLOW'): return 'C'
    if any('coordinator.py' in h for h in g.get('hot_files') or []) or depth(n) >= 3: return 'A'
    return 'B'

def lead(size, t):
    if LEADMODE == 'now': return NOW[size]
    return NOW[size] + (TGT[size] - NOW[size]) * min(1.0, t / RAMP)

S = {}
for n, g in G.items():
    if st(g) in DONE: S[n] = {'merged': -1}
    elif st(g) == 'in-progress':
        S[n] = {'start': 0, 'ready': INPROG * NOW[g.get('size')], 'merged': None}
        if PRIO and n in FAST: S[n]['ready'] = min(S[n]['ready'], FAST[n])
merges = []; added = 0; flys = 0
for t in range(H + 1):
    for n in sorted([] if t % PITCH else (n for n in S if S[n].get('merged') is None and S[n]['ready'] <= t),
                    key=lambda n: S[n]['ready']):
        if all(S.get(a, {}).get('merged') is not None for a in edges(n)):
            if PAR and n in TAIL and S[n]['ready'] < S[TAIL[n][0]]['merged'] + TAIL[n][1]:
                S[n]['ready'] = S[TAIL[n][0]]['merged'] + TAIL[n][1]; continue
            if n in CUTOVER:
                near = [m for m in S if S[m].get('merged') is None and m != n and S[m]['ready'] - t <= 1.5]
                if CUT == 'gap' and any(m in CHAIN for m in near): continue
                for m in near: S[m]['ready'] += CUTOVER[n]
            S[n]['merged'] = t; merges.append((t, n))
            if EFF and n in EFFECTS:  # in-flight groups gain the enabler on their remaining share of lead
                for m in S:
                    sm = S[m]
                    if sm.get('merged') is None and sm['ready'] > t and sm['ready'] > sm['start']:
                        sm['ready'] -= EFFX * EFFECTS[n] * (sm['ready'] - t) / (sm['ready'] - sm['start'])
    if ADD and t and t % ADD == 0:
        added += 1; nm = f'ADD-{added:02d}'; k = 'instrument' if added % 5 < 3 else 'defect'
        G[nm] = {'group': nm, 'kind': k, 'size': 'S' if k == 'instrument' else 'M', 'after': []}
    if FLY and t and t % FLY == 0:
        flys += 1; nm = f'FLY-{flys:02d}'
        G[nm] = {'group': nm, 'kind': 'instrument', 'size': 'S', 'after': []}
    open_ = [n for n in S if S[n].get('merged') is None]
    wip = {k: 0 for k in 'ABCFK'}
    for n in open_: wip[lane(n)] += 1
    total = len(open_)
    cand = []
    for n in G:
        if n in S: continue
        ok = True
        for a in edges(n):
            sa = S.get(a)
            if sa and sa.get('merged') is not None: continue
            if PAR and (n, a) in PARALLEL: continue
            hot = set(G[n].get('hot_files') or []) & set(G[a].get('hot_files') or [])
            if STACK and sa and hot and sa['ready'] <= t: continue
            ok = False; break
        if ok: cand.append(n)
    cand.sort(key=lambda n: (lane(n) != 'F', (PRIORITY.index(n) if PRIO and n in PRIORITY else 99), FLOW_ORDER.index(n) if n in FLOW_ORDER else 99, -depth(n),
                             TGT[G[n].get('size')]))
    for n in cand:
        L = lane(n)
        if t < HOLD and not n.startswith(('FLY-', 'R10-FLY')) and n not in ('R10-FLOW-RECHAIN', 'R10-FLOW-BODY-PATCH', 'R10-FLOW-MAIN-GATE', 'R10-FLOW-YIELD-PROBE', 'R10-FLOW-DISPATCH', 'R10-FLOW-RELAY-HOLD') and not (PRIO and n in EXPEDITE): continue
        if CAPS is None:
            if total >= 6 and L != 'F': continue
        elif wip[L] >= (KAIZEN if L == 'K' else CAPS[L]) and not (RESERVE and n in CHAIN): continue
        dl = 0.0
        if designed(n):
            if DESIGN == 'pipe':
                d0 = max([max(0, S[a]['start']) for a in edges(n) if a in S and 'start' in S[a]] or [0])
                if t < d0 + d_hours(n): continue
                dl = REVAL_H - d_gain(n)
            else:
                dl = d_hours(n) - d_gain(n)
        cut = EFFX * sum(h for e, h in EFFECTS.items() if EFF and S.get(e, {}).get('merged') is not None and e != n)
        S[n] = {'start': t, 'ready': t + max(1.0, lead(G[n].get('size'), t) - cut + dl), 'merged': None}
        wip[L] += 1; total += 1

roster = [n for n in G if not n.startswith(('FLY-', 'ADD-')) and st(G[n]) not in DONE]
last = max((S[n]['merged'] for n in roster if S.get(n, {}).get('merged') is not None), default=None)
unmerged = [n for n in roster if S.get(n, {}).get('merged') is None]
crit = max(depth(n) for n in roster)
from simulate_rules import CHAIN as _C
chain_end = round(max(S[n]['ready'] for n in _C if n in S), 2)
print(json.dumps({'roster_open': len(roster), 'last_roster_merge_h': last, 'chain_end_ready_h': chain_end,
                  'unmerged_at_horizon': len(unmerged), 'critical_depth': crit,
                  'added': added, 'flyins': flys}))
json.dump({'merges': merges, 'state': S}, open('projection.json', 'w'))
