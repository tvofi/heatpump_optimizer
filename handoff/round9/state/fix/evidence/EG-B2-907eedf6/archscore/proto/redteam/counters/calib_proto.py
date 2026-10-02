#!/usr/bin/env python3
"""Corpus holdout with the counters swapped in: does any counter block or flip a labelled merge?

    python3 calib_proto.py
Compares the frozen v1 verdict with the prototype (score_proto.py's swap + gate-only rows) per
corpus case. A counter missing on either side (historic tree it cannot read) falls back to the
v1 metric it replaces / drops the gate row, and is listed.
"""
import csv, json, sys
from pathlib import Path
RT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RT.parent / "b"))
sys.argv = [sys.argv[0]]
import arch_score as A  # noqa: E402

SWAP = {"untyped_payload_keys": "untyped_payload_keys_v2", "dup_pairs_v1": "dup_pairs_v2",
        "private_reach": "private_reach_v2", "a1_params_over_10": "params_over_10_v2"}
GATE_ONLY = ("reflective_writes", "computed_attr_access", "family_orphan_overrides", "unread_private_globals")
w1 = A.weights()
M1 = dict(A.SCORE_METRICS)
M2 = {SWAP.get(k, k): v for k, v in M1.items()}
for g in GATE_ONLY:
    M2[g] = (None, "gate only")
W2 = {SWAP.get(k, k): v for k, v in w1.items()}
W2.update({g: 0.0 for g in GATE_ONLY})


def counters(sha):
    p = RT / "corpus" / f"{sha}.counters.json"
    return json.loads(p.read_text()) if p.exists() else {}


rows = list(csv.DictReader(open(RT.parent / "a2" / "corpus.tsv"), delimiter="\t"))
by = {r["sha"][:8]: r for r in rows}
flips, n = [], 0
print(f"{'case':9} {'label':8} {'v1':9} {'dS1':>8}  {'proto':9} {'dS2':>8}  rises(proto)")
for c in A.cases():
    if c["set"] != "corpus":
        continue
    r = by[c["id"]]
    cb, ca = counters(r["parent"][:8]), counters(r["sha"][:8])
    A.SCORE_METRICS = M1
    d1 = A.delta(c["base"], c["cur"], w1)
    b2, a2 = dict(c["base"]), dict(c["cur"])
    for old, new in SWAP.items():
        for vec, cc in ((b2, cb), (a2, ca)):
            vec[new] = cc.get(new) if cc.get(new) is not None else vec.get(old)
    for g in GATE_ONLY:
        b2[g], a2[g] = cb.get(g), ca.get(g)
    A.SCORE_METRICS = M2
    d2 = A.delta(b2, a2, W2)
    n += 1
    ok1, ok2 = A.expected_ok(c["label"], d1["verdict"]), A.expected_ok(c["label"], d2["verdict"])
    mark = "" if d1["verdict"] == d2["verdict"] else "  <-- changed"
    if mark:
        flips.append(c["id"])
    print(f"{c['id']:9} {c['label']:8} {d1['verdict']:9} {d1['dS']:>8.3f}  {d2['verdict']:9} {d2['dS']:>8.3f}  "
          f"{'; '.join(d2['rises'])[:90]}{mark}  ok {int(ok1)}->{int(ok2)}")
print(f"\n{n} corpus cases; verdict changed on {len(flips)}: {', '.join(flips) or 'none'}")
