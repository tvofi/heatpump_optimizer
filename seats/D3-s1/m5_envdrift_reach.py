#!/usr/bin/env python3
"""D3-s1 M5: env_drift.py --all is driven on mutants its capture never executes.

Metric (one line): of the unpinned inventory sites in the 12 cell files
(tests/mutation_table.py:inventory minus dispositions), how many lie on an
executable line that env_drift.py's production-executing child
(`env_drift.py --capture <tree> <out> --all`, traced with the gate's own
REACH_HOOK) never executes -- sites where the gate's reach rule
(`mutation_table.reach_skip`) still drives env_drift --all, because the
parent's traced run is refused (`reach_problems`: it starts git/file/uname,
and the capture child, started with PYTHONPATH reset to tests/hastub, never
loads the hook, so `processes started > recorded`).

Count key: the delivered reach row -- `reach_skip(<the run's own reach>)`
must say skippable; a fix that makes the gate's reach of env_drift usable
moves `gate_skippable` up toward `capture_never_executes`.

Instrumented symbols: tests/mutation_table.py:reach_skip / reach_problems on
tests/env_drift.py's traced baseline, and env_drift.py:capture_tree's traced
child run (prescreen.py trace-capture).
Perturbation: `--as-if-fixed` substitutes the capture child's reach for the
parent's (what a hook-preserving env_drift would deliver): gate_skippable
rises from 0 to capture_never_executes (direction up). Null control: the
same count over sites the capture DOES execute stays 0 skippable under both.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_envdrift_reach.py [--as-if-fixed]
Needs state/baselines.json (prescreen.py baseline, then trace-capture).
Expected: gate_skippable=0 at baseline; exact counts (contention-immune).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

HERE = Path(__file__).resolve().parent
CELLS = ["coordinator", "optimizer", "thermal_model", "sysid", "defrost",
         "flow_lift", "process_worker", "batchmath", "price_model", "tariff",
         "grid_fee", "dhw_planner"]


def main() -> int:
    fixed = "--as-if-fixed" in sys.argv
    base = json.loads((HERE / "state" / "baselines.json").read_text())
    ed = base["tests/env_drift.py"]
    gate_reach = ed["reach"]
    cap = ed["capture_reach"]
    assert not mt.reach_problems(cap), mt.reach_problems(cap)
    budgets = mt.load_budgets()
    inv = mt.inventory(sorted(mt.PRODUCTION / (c + ".py") for c in CELLS))
    sites = mt.unpinned_sites(budgets, inv)
    clos = mt.load_closures()["tests/env_drift.py"]
    never = gate_skip = exec_skip = executed = 0
    per = Counter()
    for m in sites:
        if m["file"] not in clos:
            continue
        cap_never = mt.reach_skip(cap, m)
        row = cap if fixed else gate_reach
        skip = mt.reach_skip(row, m)
        if cap_never:
            never += 1
            per[m["file"].rsplit("/", 1)[-1]] += 1
            gate_skip += int(skip)
        else:
            executed += 1
            exec_skip += int(skip)
    for f, n in sorted(per.items()):
        print(f"  {f}: {n}")
    print(f"RESULT unpinned_sites_in_closure={never + executed}")
    print(f"RESULT capture_never_executes={never}")
    print(f"RESULT gate_skippable={gate_skip}")
    print(f"RESULT null_capture_executes={executed}")
    print(f"RESULT null_skippable={exec_skip}")
    print(f"RESULT gate_reach_problems={len(mt.reach_problems(gate_reach))}")
    print(f"RESULT env_drift_baseline_wall_s={ed['run']['seconds']} (provisional)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
