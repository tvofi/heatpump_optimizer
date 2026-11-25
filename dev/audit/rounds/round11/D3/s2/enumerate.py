#!/usr/bin/env python3
"""D3-s2 enumerator: the D3.M1 universe restricted to this seat's cells.

Metric: one line per inventory site of tests/mutation_table.py (the seven
RATCHETED operators) in a D3-s2 cell file that is UNPINNED (no ledger
disposition) or carries a `gap` survivor_triage verdict (a recorded survivor).
These are the "unpinned sites and surviving mutants" `--scope full` would
account for, without driving any mutant.

Run:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s2/enumerate.py [--json]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B2 (4 cores).
Expected: deterministic list; count printed as RESULT universe=<n> sites (exact).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

CELLS = ["sensor", "binary_sensor", "climate", "switch", "button", "entity",
         "store", "ledger", "snapshots", "payload", "inputs", "topology",
         "entry_config", "diagnostics", "accuracy", "services", "const",
         "__init__"]


def universe():
    files = [mt.PRODUCTION / f"{c}.py" for c in CELLS]
    budgets = mt.load_budgets()
    sites = mt.inventory(sorted(files))
    loose = {id(s) for s in mt.unpinned_sites(budgets, sites)}
    disp = mt.dispositions(budgets)
    out = []
    for s in sites:
        e = disp.get(s["anchor"])
        gap = (isinstance(e, dict) and e.get("old") == s["old"]
               and e.get("verdict") == "gap")
        if id(s) in loose or gap:
            out.append(dict(s, status="gap" if gap else "unpinned"))
    return out, len(sites)


def item_name(s):
    """One universe item's unique name: two mutants of one line differ by
    their mutated text, so its hash closes the name."""
    import hashlib
    h = hashlib.sha1(s["new"].encode()).hexdigest()[:6]
    return f"{s['file'].split('/')[-1]}:{s['line']} {s['kind']} {s['status']} m{h}"


if __name__ == "__main__":
    u, total = universe()
    if "--json" in sys.argv:
        print(json.dumps(u, indent=1))
        sys.exit(0)
    for s in u:
        print(item_name(s))
    print(f"RESULT universe={len(u)} sites")
    print(f"RESULT inventory_in_cells={total} sites")
