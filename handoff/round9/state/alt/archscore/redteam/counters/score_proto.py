#!/usr/bin/env python3
"""Re-score every attempt with the counters swapped in (prototype, not a new frozen score).

    python3 score_proto.py

v1 vector, with: untyped_payload_keys -> _v2, dup_pairs_v1 -> dup_pairs_v2, private_reach -> _v2,
a1_params_over_10 -> params_over_10_v2 (same weights), plus gate-only rows (weight 0, must not
rise): reflective_writes, family_orphan_overrides, unread_private_globals. C4 (flatten) is applied
by measuring the flattened tree; for 05c/05d the flattened vectors are in out/flat_*.json.
"""
import json, sys
from pathlib import Path
RT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RT.parent / "b"))
sys.argv = [sys.argv[0]]
import arch_score as A  # noqa: E402

SWAP = {"untyped_payload_keys": "untyped_payload_keys_v2", "dup_pairs_v1": "dup_pairs_v2",
        "private_reach": "private_reach_v2", "a1_params_over_10": "params_over_10_v2"}
GATE_ONLY = ("reflective_writes", "computed_attr_access", "family_orphan_overrides", "unread_private_globals")
w1 = A.weights()
A.SCORE_METRICS = {SWAP.get(k, k): v for k, v in A.SCORE_METRICS.items()}
for g in GATE_ONLY:
    A.SCORE_METRICS[g] = (None, "gate only")
W = {SWAP.get(k, k): v for k, v in w1.items()}
W.update({g: 0.0 for g in GATE_ONLY})


def vec(name):
    v = json.loads((RT / "out" / f"{name}.json").read_text())
    c = RT / "out" / f"{name}.counters.json"
    if c.exists():
        v.update(json.loads(c.read_text()))
    return v


base = vec("base")
base.update(json.loads((RT / "out" / "base.counters.json").read_text()))  # counters on the baseline tree
rows = []
for p in sorted((RT / "out").glob("[0-9]*.counters.json")):
    name = p.name[:-len(".counters.json")]
    cur = vec(name)
    b = base
    if name[:3] in ("05c", "05d"):  # C4: measure the flattened trees (flatten_coord.py)
        b, cur = vec("flat_base"), vec(f"flat_{name[:3]}")
    d = A.delta(b, cur, W)
    rows.append((name, d["admissible"], d["dS"], d["verdict"], "; ".join(d["rises"])))
for r in rows:
    print(f"{r[0]:32} adm={'y' if r[1] else 'n'} dS={r[2]:>9.4f} {r[3]:9} {r[4]}")
