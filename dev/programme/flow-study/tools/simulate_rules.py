"""The re-chain as the R10-FLOW-RECHAIN decision seat ruled it (2026-10-21, at roster 2c76c3128,
main 5d433771a): 15 coordinator.py edges examined, 8 dropped, 7 kept, 3 required and 4 recommended
edges added. Shared by simulate.py and gen_plan.py. K7's first proposal (10 drops) was wrong on 4."""
HOT_ONLY = {  # dropped: (later, earlier)
    ('R10-RATIO-ANCHOR', 'R10-NIGHT-FOLDS'), ('R10-INPUT-STALENESS', 'R10-RATIO-ANCHOR'),
    ('R10-CURRENCY', 'R10-INPUT-STALENESS'), ('R10-LOOP-CPU', 'R10-FREQ-DEFROST'),
    ('R10-CONFIG-NOTICES', 'R10-LIVESTATE'), ('R10-PARAMS-OWNER', 'R10-CONFIG-NOTICES'),
    ('R10-ARCH-SHAPES', 'R10-PARAMS-OWNER'), ('R10-LEARNER-ETA', 'R10-ARCH-SHAPES'),
}
REQUIRED = {  # later: [earlier, ...] -- must land in the same burst as the drops
    'R10-PARAMS-OWNER': ['R10-LIVESTATE'], 'R10-ARCH-SHAPES': ['R10-LIVESTATE'],
    'R10-HEAT-METER': ['R10-PARAMS-OWNER', 'R10-ARCH-SHAPES'],
}
RECOMMENDED = {  # 0 depth each: overlapping pairs already unordered today
    'R10-LIVESTATE': ['R10-LOOP-CPU'], 'R10-LOOP-CPU': ['R10-NIGHT-FOLDS'],
    'R10-PARAMS-OWNER': ['R10-NIGHT-FOLDS', 'R10-RATIO-ANCHOR'], 'R10-ARCH-SHAPES': ['R10-INPUT-STALENESS'],
}
STUDY_ADD = {  # this study's addition, outside the seat's mandate: 0 depth (HEAT-METER waits on depth 4)
    'R10-HEAT-METER': ['R10-THERMAL-POWER-OPTION'],
    # revision 10: the last stage documents the shapes as built, so they land first (0 depth: all by about h57)
    'R10-ARCH-DOCS': ['R10-ORCH-MACHINERY', 'R10-CI-LAYOUT-P2', 'R10-FLOW-TOOLKIT-MODEL'],
}
def added(n, recommended=True, study=True):
    out = list(REQUIRED.get(n, []))
    if recommended: out += RECOMMENDED.get(n, [])
    if study: out += STUDY_ADD.get(n, [])
    return out

# ---- revision 10: finishing non-production groups earlier (FUTURE-STATE §11 items 36+) ----
# Lead hours a merged enabler removes from every group dispatched after it (EFF=1; EFFX scales all).
# Estimates, each from its brief's own figure; FUTURE-STATE §12 gives the derivation and the range.
EFFECTS = {
    'R10-CI-LAYOUT-P1': 0.4,       # W1: 7-21 min off each CI wait, about 2 waits per group not overlapped by review
    'R10-PREPR-CAP': 0.25,         # local closures re-record 10-25 min per handoff; 8+ preprs at load ~168 on 8 cores
    'R10-FLOW-DISPATCH': 0.3,      # orphaned handoffs: 9 with no PR, oldest 110 h (RCA-ORCH-CONTINUITY)
    'R10-FLOW-ANDON': 0.3,         # silent stops: 6.2 h ledger loss, 8 h unrouted block, 16 h silent ledger in 4 days
    'R10-ORCH-MACHINERY': 0.15,    # ledger aging: a stranded handoff surfaces at 4 h / 12 h, not 110 h
    'R10-BRIEFS-FOLD': 0.1,        # with RCA-FRICTION and POLICY-FIXER-MD: fewer bookkeeping blocks (#2331: 9 PRs)
    'R10-POLICY-FIXER-MD': 0.05,   # #2378: 8 PRs of fixer.md friction in the window
    'R10-TICK-OWED-LEVEL': 0.05,   # the tick re-reads 35214 OWED lines (4.5 MB) every pass
}
# (later, earlier) edges that order merges only (PAR=1): the later group builds beside the earlier one.
PARALLEL = {('R10-CI-LAYOUT-P1', 'R10-CI-LAYOUT'), ('R10-CI-LAYOUT-P2', 'R10-CI-LAYOUT-P1'),
            ('R10-ORCH-MACHINERY', 'R10-CI-LAYOUT')}
# P2's U5, U10 and U9 run after PR 1 merges (DESIGN-P2 L1374-1377), then the combined null control and review.
TAIL = {'R10-CI-LAYOUT-P2': ('R10-CI-LAYOUT-P1', 6)}
# P2's cut-over: every open PR absorbs main before it has a `gate`; one CI cycle for a PR about to board.
CUTOVER = {'R10-CI-LAYOUT-P2': 1.0}
CHAIN = ['R10-ADVISOR', 'R10-SCORES', 'R10-LIVESTATE', 'R10-PARAMS-OWNER', 'R10-HEAT-METER',
         'R10-COP-GATE', 'R10-UX-HEALTH', 'R10-ARCH-DOCS']
# The CD3 order (cost of delay / duration), highest first; lane caps still apply.
PRIORITY = ['R10-CI-RATCHET-RED', 'R10-PREPR-CAP', 'R10-TICK-OWED-LEVEL', 'R10-REPLAY-CAP',
            'R10-ROSTER-PUSH-RACE', 'R10-UPDATE-PR-SIGNALS', 'R10-HANDOVER-REFRESH',
            'R10-FLOW-RELAY-HOLD', 'R10-FLOW-BODY-PATCH', 'R10-FLOW-MAIN-GATE', 'R10-FLOW-YIELD-PROBE',
            'R10-FLOW-DISPATCH', 'R10-FLOW-ANDON', 'R10-CI-LAYOUT-P1', 'R10-CI-LAYOUT-P2',
            'R10-RCA-FRICTION', 'R10-BRIEFS-FOLD', 'R10-POLICY-FIXER-MD', 'R10-ORCH-MACHINERY',
            'R10-PLAN-ARTIFACT', 'R10-FLOW-JIDOKA', 'R10-FLOW-BOARD', 'R10-POLICY-GATE-SCOPING',
            'R10-POLICY-LINT-FAMILY']
# Not held by the drain-first HOLD (PRIO=1): the owner's CI-layout ask and the top-CD3 enablers.
EXPEDITE = ['R10-CI-LAYOUT-P1', 'R10-CI-LAYOUT-P2', 'R10-FLOW-ANDON', 'R10-BRIEFS-FOLD']
# In-progress groups with a PR up: hours to merge when given the next reviewer (PRIO=1).
FAST = {'R10-CI-LAYOUT': 6, 'R10-CI-RATCHET-RED': 3, 'R10-TICK-OWED-LEVEL': 3, 'R10-REPLAY-CAP': 3, 'R10-I5-DOCS': 3,
        'R10-PREPR-CAP': 6, 'R10-ROSTER-PUSH-RACE': 6, 'R10-UPDATE-PR-SIGNALS': 6,
        'R10-PLAN-ARTIFACT': 8, 'R10-RCA-FRICTION': 6, 'R10-HANDOVER-REFRESH': 6}
