"""Reviewer-built instrument (disclosed per fix-review.md step 9): no committed
script computes the closure-overlap figures that `tests/deployment_shape.py`'s
census prose quotes, so this re-derives them from `tests/closures.json` itself.

Definition found by matching each side's own prose, then applied to the merged
tree: for a pair of scripts, the shared count is
``len(prod(closures[A]) & prod(closures[B]))`` where ``prod`` keeps entries under
``custom_components/`` (all files, not ``.py`` only -- the `.py`-only variant does
not reproduce 92, 90 or 57).
"""
import itertools
import json
import subprocess
import sys

W = "/Users/timmalmstrom/hpo-seats/review-2024/wt3"
REV = {"BASE": "b296779f", "OURS": "d916687db", "THEIRS": "c518447eb", "MERGED": "bab0aeb8d"}
PAIRS = [("arch_score_head.py", "deployment_shape.py"), ("entities.py", "harness_headers.py"),
         ("doc_claims.py", "entities.py"), ("doc_claims.py", "harness_headers.py"),
         ("structure.py", "typing_ruler.py"), ("finite_boundary.py", "structure.py"),
         ("finite_boundary.py", "typing_ruler.py"), ("plan_view.py", "solar_alignment.py"),
         ("boost_drift_replay.py", "plan_view.py"), ("boost_drift_replay.py", "solar_alignment.py"),
         ("golden.py", "env_drift.py"), ("card.mjs", "card_drift.mjs"),
         ("optimality.py", "validate.py"), ("optimality.py", "backtest.py"),
         ("validate.py", "edge.py"), ("edge.py", "backtest.py")]


def closures(rev):
    raw = subprocess.run(["git", "show", f"{rev}:tests/closures.json"],
                         capture_output=True, text=True, check=True, cwd=W).stdout
    return {k.replace("tests/", ""): v for k, v in json.loads(raw)["closures"].items()}


def prod(lst):
    return {x for x in lst if x.startswith("custom_components/")}


table = {}
for label, rev in REV.items():
    C = closures(rev)
    scripts = sorted(C)
    n80 = n100 = both = 0
    for a, b in itertools.combinations(scripts, 2):
        pa, pb = prod(C[a]), prod(C[b])
        if pa and pb:
            both += 1
        if pa or pb:
            j = len(pa & pb) / len(pa | pb)
            if j >= 0.80:
                n80 += 1
            if j == 1.0:
                n100 += 1
    table[label] = dict(scripts=len(scripts), pairs=len(scripts) * (len(scripts) - 1) // 2,
                        ge080=n80, eq100=n100, both_nonempty=both,
                        **{f"{a}/{b}": len(prod(C[a]) & prod(C[b])) for a, b in PAIRS})
    print(f"RESULT {label}_scripts={len(scripts)} pairs={table[label]['pairs']} "
          f"ge_080={n80} eq_100={n100} both_nonempty={both}")
    for a, b in PAIRS:
        print(f"RESULT {label}_{a}+{b}={table[label][f'{a}/{b}']}")

print("\n--- deployment_shape.py prose at each stage vs this re-derivation ---")
PROSE = {
    "BASE": None,
    "OURS": dict(shared=91, doc_claims=80, struct=72, boost=53, quad=17, golden=88, card=54),
    "THEIRS": dict(shared=91, doc_claims=81, struct=73, boost=55, quad=20, golden=89, card=56),
    "MERGED": dict(shared=92, doc_claims=82, struct=74, boost=56, quad=20, golden=90, card=57),
}
KEY = {"shared": "arch_score_head.py/deployment_shape.py", "doc_claims": "doc_claims.py/entities.py",
       "struct": "structure.py/typing_ruler.py", "boost": "boost_drift_replay.py/plan_view.py",
       "quad": "optimality.py/validate.py", "golden": "golden.py/env_drift.py",
       "card": "card.mjs/card_drift.mjs"}
for label, prose in PROSE.items():
    if not prose:
        continue
    bad = [k for k, v in prose.items() if table[label][KEY[k]] != v]
    print(f"{label}: prose figures wrong on {bad if bad else 'none'}"
          + ("" if not bad else f" -- re-derived {[table[label][KEY[k]] for k in bad]}"))
