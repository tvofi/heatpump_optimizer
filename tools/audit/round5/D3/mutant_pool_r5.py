#!/usr/bin/env python3
"""D3 round 5 -- build the seeded mutant pool over production modules.

Metric (one line): the number of single-line production mutants generated,
per module and per operator, under the recorded seed.

Command:
    cd /tmp/hpo-d3-wt && PYTHONPATH=tests/hastub python3 \
        tools/audit/round5/D3/mutant_pool_r5.py

Expected: 40 mutants, <=4 per module, seed 20260911; prints RESULT lines.
Baseline SHA: eaa2a06af16a1b5b006f58a0f36cc92131f80225 (origin/main).
Machine: Apple M1, 8 GB, numpy 2.4.6 / OpenBLAS.

The batch is built by importing tests/mutation_table.py (the gate's own
mutation instrument) so the six operators and their candidate filter are the
same ones the nightly runs -- never a private re-implementation. Weighting is
recorded next to the pool: kind, module, and the closure-driven driver set.
"""
import json
import os
import random
import sys
from collections import Counter
from pathlib import Path

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

ROOT = Path(__file__).resolve().parents[4]          # .../hpo-d3-wt
sys.path.insert(0, str(ROOT / "tests"))
import mutation_table as MT                          # noqa: E402

SEED = 20260911
PER_FILE = 4
MAX = 40
CLOSURES = json.loads((ROOT / "tests" / "closures.json").read_text())["closures"]

# Candidate drivers: the closure's FAST scripts (brief step 2), skipping
# stress.py, edge.py, backtest.py in the pre-screen. env_drift.py is driven
# separately, with --all <baseline>, by prescreen.py.
FAST = [
    "tests/open_meteo.py", "tests/solar_alignment.py", "tests/plan_view.py",
    "tests/dst_checks.py", "tests/ha_contract.py", "tests/guard_pins.py",
    "tests/typing_ruler.py", "tests/wood_advisor.py",
    "tests/deployment_shape.py", "tests/structure.py", "tests/frontend.py",
    "tests/config_flow_steps.py", "tests/manual_plan.py", "tests/entities.py",
    "tests/validate.py", "tests/optimality.py", "tests/features.py",
]


def drivers_for(rel):
    return [s for s in FAST if rel in CLOSURES.get(s, ())]


def main():
    files = sorted((ROOT / "custom_components" / "heatpump_optimizer").rglob("*.py"))
    rng = random.Random(SEED)
    pool = []
    per_module = Counter()
    per_file_seen = {}
    for path in files:
        rel = str(path.relative_to(ROOT))
        drivers = drivers_for(rel)
        if not drivers:
            continue
        got = list(MT.candidates(path))
        rng.shuffle(got)
        chosen = got[:PER_FILE]
        per_file_seen[rel] = len(got)
        for m in chosen:
            m["drivers"] = drivers
            pool.append(m)
    rng.shuffle(pool)
    pool = pool[:MAX]
    for m in pool:
        per_module[m["file"]] += 1

    kinds = Counter(m["kind"] for m in pool)
    out = {
        "seed": SEED, "per_file": PER_FILE, "max": MAX,
        "baseline_sha": "eaa2a06af16a1b5b006f58a0f36cc92131f80225",
        "fast_drivers": FAST,
        "weights_by_kind": dict(kinds),
        "weights_by_module": dict(per_module),
        "pool": pool,
    }
    dest = Path(__file__).resolve().parent / "pool.json"
    dest.write_text(json.dumps(out, indent=1))

    print("RESULT mutants_total=%d count" % len(pool))
    print("RESULT modules_in_pool=%d count" % len(per_module))
    for k, v in sorted(kinds.items()):
        print("RESULT mutants_kind_%s=%d count" % (k, v))
    print("RESULT thread_factor=1.00 ratio")
    print("RESULT load1=%.2f ratio" % os.getloadavg()[0])
    print("RESULT pool_json=%s n/a" % dest)
    for m in pool:
        print("  %-28s:%-5d %-10s drivers=%d"
              % (os.path.basename(m["file"]), m["line"], m["kind"],
                 len(m["drivers"])))


if __name__ == "__main__":
    main()
