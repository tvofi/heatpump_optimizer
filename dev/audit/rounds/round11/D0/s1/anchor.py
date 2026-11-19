"""D0-s1-01's perturbation arm: the DHW path's space multi-start, given the space-only path's thermostat anchors.

Metric: per DHW-path cell, gap = f_prod(call 0) - f_best(call 0), objective units, where call 0 is the
first optimizer:_multi_start_minimize call _solve_space makes (through _relaxed_plans) around the
planner's first DHW plan, f_prod its value at production's result.x and f_best the best feasible
challenger race.py recorded for that call (out/<cell>.json). Count key: the call's own objective at the
x the production seam returns.
The arm re-solves the cell with race.py's `thermostat-anchor` perturbation (the thermostat seed_power of
HeatPumpOptimizer._compute_baseline_power, and bang-bang at 1.0, _LOW_ENERGY_START_FRACTION and, on
two-zone, _DEEP_LOW_ENERGY_START_FRACTION of its energy, appended to the call's candidates) and prints
the gap left. Expected direction: down (to ~0 where the anchors are what the seeds challenger supplied).
Run:  PYTHONPATH=tests/hastub ~/venv-ci/bin/python3 dev/audit/rounds/round11/D0/s1/anchor.py [substring filter]
Needs race.py's out/*.json for the cells (race.py --all). Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B1.
Writes nothing.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE)]
import numpy as np  # noqa: E402

import race  # noqa: E402
import cells as cellmod  # noqa: E402

DHW_ARMS = ("dhw-6h", "dhw-24h", "dhw-48h", "twozone-dhw-24h", "pinned-dhw-24h", "wood-coil",
            "coord_dhw", "coord_all_features")


def main():
    flt = sys.argv[1] if len(sys.argv) > 1 else ""
    before, after = [], []
    for cell in cellmod.cells():
        if flt not in cell or cell.split("/")[2] not in DHW_ARMS:
            continue
        p = race.OUT / (cell.replace("/", "__") + ".json")
        if not p.exists():
            print(f"MISSING {cell}")
            continue
        d = json.loads(p.read_text())
        c0 = d["calls"][0]
        if not c0.get("has_dhw_arg") or "gap" not in c0:
            continue
        cap, opt, res = race.capture_cell(cell, "thermostat-anchor")
        call = cap.calls[0]
        fp = race.fval(call, call["x"])
        g0 = c0["gap"]
        g1 = fp - c0["f_best"]
        before.append(g0)
        after.append(g1)
        print(f"RESULT gap_before[{cell}]={g0:.6g} objective")
        print(f"RESULT gap_after[{cell}]={g1:.6g} objective  (f_prod {c0['f_prod']:.6f} -> {fp:.6f})")
    b, a = np.array(before), np.array(after)
    print(f"RESULT cells={len(b)} count")
    print(f"RESULT cells_gap_before_gt_0.1={int(np.sum(b > 0.1))} count")
    print(f"RESULT cells_gap_after_gt_0.1={int(np.sum(a > 0.1))} count")
    print(f"RESULT sum_gap_before={b.sum():.6g} objective")
    print(f"RESULT sum_gap_after={a.sum():.6g} objective")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
