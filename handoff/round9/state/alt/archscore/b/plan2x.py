#!/usr/bin/env python3
"""The 2x plan's arithmetic: baseline log-debt D, each planned group's metric targets, expected dD, and the index.

Index AI = 100 * D_ref / D (7952d8f9 = 100). 2x = AI 200 = D halved. dS of a change = D_before - D_after.
Targets are the ones each group's brief states or implies (PRE-STUDY.md section 8); a range's LOW end is used.
Printed under the frozen weights, with the dominant weight halved, and with all weights 1.0.
"""
import json, math, sys
sys.argv = [sys.argv[0]]
import arch_score as A

base = json.load(open("base_7952d8f9.json"))
base.update(json.load(open("planted1/_base.json")))
# group -> {metric: target value}; applied cumulatively in this order
PLAN = [
    ("R9-EG-B1 per-solve input record (planned)", {"hub_solve_writes": 0, "a1_params_over_10": 22}),
    ("R9-EG-B3 typed payload contract (planned)", {"untyped_payload_keys": 0}),
    ("R9-EG-B6 collaborator interfaces (planned)", {"private_reach": 13, "shared_inplace_writes": 18}),
    ("R9-EG-B2 surface public accessors (planned)", {"private_reach": 0}),
    ("R9-EG-B7 coordinator seams, 2 seams (planned, conditional)", {"coord_footprint_v1": 1900, "a1_coord_writers_multi": 90, "shared_inplace_writes": 10}),
    ("R9-F10.4 dead members + unused publics (planned + carry)", {"dead_by_reachability": 0, "public_unused": 0}),
    ("NEW R9-EG-A2 one copy per formula/helper (clone consolidation)", {"dup_pairs_v1": 40}),
    ("NEW R9-F7.5 the three recorded family splits (owner-gated rename)", {"family_splits": 0}),
    ("NEW R9-EG-A3 parameter objects for the solve/planner signatures", {"a1_params_over_10": 14}),
]


def D(v, w):
    return sum(w[m] * math.log2(1 + v[m]) for m in A.SCORE_METRICS)


for label, w in (("frozen weights", A.weights()),
                 ("untyped_payload_keys x0.5", A.weights({"untyped_payload_keys": 0.5})),
                 ("all weights 1.0", {m: 1.0 for m in A.SCORE_METRICS})):
    v = dict(base)
    d0 = D(v, w)
    print(f"== {label}: D_ref {d0:.2f}")
    for g, t in PLAN:
        before = D(v, w)
        v.update(t)
        after = D(v, w)
        print(f"  {g:66} dS {before - after:+7.2f}  AI {100 * d0 / after:6.1f}")
    print(f"  final AI {100 * d0 / D(v, w):.1f}  (2x = 200)")
    for drop in ("R9-EG-B3", "NEW R9-F7.5"):
        v = dict(base)
        for g, t in PLAN:
            if not g.startswith(drop):
                v.update(t)
        print(f"  without {drop}: AI {100 * d0 / D(v, w):.1f}")
