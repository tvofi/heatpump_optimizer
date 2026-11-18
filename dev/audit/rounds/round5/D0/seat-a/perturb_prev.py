#!/usr/bin/env python3
"""D0-a F2 perturbation harness: previous-plan warm start (#1295).

METRIC (one line): on each cell of the core grid whose race was won by the
"prev cell plan" seed, prev_gap_pct = 100*(J_base - J_warm)/|J_base| where
J_base is the shipped plan's production objective at baseline 1cc89e0 and
J_warm is the shipped plan's objective when the walk hands each optimizer the
plan the previous cell shipped, exactly as ``coordinator._warm_seeded`` copies
it onto the fresh per-solve optimizer it builds (``_prev_shipped_plan``, which
``HeatPumpOptimizer._warm_start_starts`` offers as one extra multi-start
candidate). Must be > 0 on those cells: the patch adds exactly the lead whose
absence the race measured.

COMMAND (from the tree root, at the HEAD that carries the fix):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D0/seat-a/perturb_prev.py

EXPECTED at baseline 1cc89e0 + patch (exact): RESULT prev_won_cells=18,
prev_won_improved=14, mean_prev_gap_pct=0.4878, worst_prev_gap_pct=5.9430;
no prev-won cell regresses. The injection the patch made inside ``optimize``
is production's ``_warm_seeded`` in this tree, so the harness sets the same
attribute the coordinator sets and the walk reproduces the patch's chain
without applying it. ``patch_f2.diff`` (like ``patch_f1.diff`` and
``patch_f1b.diff``) is the finding's original baseline-only form of the change
and no longer applies to this tree: it is kept as the round's evidence, not as
something to run.

Baseline SHA: 1cc89e020fff9040a9d0090a27bf22bc1dd497f0; 8-core Apple M1.
Root rule: resolves from the tree it runs in (cwd).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time
import json

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
sys.path.insert(0, os.path.join(os.getcwd(), "custom_components"))
sys.path.insert(0, os.path.join(os.getcwd(),
                                "tools/audit/round5/D0/seat-a"))

import numpy as np  # noqa: E402
from profiles import prices, weather, house  # noqa: E402
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel, ThermalParameters, ThermalState)
from heatpump_optimizer.optimizer import (  # noqa: E402
    HeatPumpOptimizer, OptimizationConfig)

import race  # noqa: E402

TMP = os.environ.get("HPO_D0A_TMP", "/tmp/audit-5/tmp/d0a")


def inputs_for(tz, dhw, pp, wp, horizon=24.0):
    cfg = house(two_zone=tz)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = dhw
    m = ThermalModel(p)
    opt = HeatPumpOptimizer(m, OptimizationConfig(
        horizon_hours=horizon, time_step_minutes=15,
        target_temp=21.0, min_temp=17.0, max_temp=23.0))
    pr = prices(pp, race.START)
    ot, wi, ra, so = weather(wp, race.START)
    n = int(round(horizon * 4))
    pr, ot, wi, ra, so = pr[:n], ot[:n], wi[:n], ra[:n], so[:n]
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0,
                      outdoor_temperature=float(ot[0]),
                      upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                      buffer_tank_temperature=40.0, dhw_temperature=48.0)
    return opt, pr, ot, wi, ra, so, st


def main():
    base = {r["cell"]: r for r in
            json.load(open(os.path.join(TMP, "race_cells_baseline.json")))}
    prev_won = [cid for cid, r in base.items()
                if r["best_seed"] == "prev cell plan"]
    print(f"# prev-plan-won cells in baseline race: {len(prev_won)}")

    # Walk the grid in the race's order, one persistent optimizer per
    # (tz, dhw) group: every solve after the first is handed the previous
    # shipped plan, the way coordinator._warm_seeded hands it to the fresh
    # optimizer it builds per solve.
    improved = 0
    deltas = []
    for tz in (False, True):
        for dhw in (False, True):
            opt = None
            for wp in race.WEATHER_PROFILES:
                for pp in race.PRICE_PROFILES:
                    cid = f"tz={int(tz)},dhw={int(dhw)},{pp},{wp},h24"
                    if cid not in base:
                        continue
                    if opt is None:
                        opt, pr, ot, wi, ra, so, st = inputs_for(
                            tz, dhw, pp, wp)
                    else:
                        _, pr, ot, wi, ra, so, st = inputs_for(tz, dhw, pp, wp)
                    res = opt.optimize(st, pr, ot, wi, ra, so, race.START)
                    opt._prev_shipped_plan = np.asarray(
                        res.power_schedule, dtype=float).copy()
                    j_new = float(res.objective_value)
                    j_old = base[cid]["j_ship"]
                    d = 100.0 * (j_old - j_new) / max(abs(j_old), 1e-12)
                    if cid in prev_won:
                        deltas.append(d)
                        if d > 0.05:
                            improved += 1
                        print(f"  {cid:50s} J {j_old:9.3f} -> {j_new:9.3f} "
                              f"({d:+6.3f}%)")
    proc = time.process_time()
    thread = time.thread_time()
    print(f"RESULT prev_won_cells={len(prev_won)} count")
    print(f"RESULT prev_won_improved={improved} count")
    if deltas:
        print(f"RESULT mean_prev_gap_pct={sum(deltas)/len(deltas):.4f} percent")
        print(f"RESULT worst_prev_gap_pct={max(deltas):.4f} percent")
    print(f"RESULT thread_factor={proc / max(thread, 1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
