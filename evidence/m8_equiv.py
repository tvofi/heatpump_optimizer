"""Reviewer's harness for M8: does the repair's startable_steps ever read differently
with charge_running=False vs the default True, when the plan has been dropped under running=False?
Wraps dhw_planner.startable_steps; records every call where the two readings differ, over a sweep of solves."""
import sys, itertools
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import numpy as np
import heatpump_optimizer.dhw_planner as dp
import heatpump_optimizer.dhw_start as ds
import block_duty as bd

orig = ds.startable_steps
stats = {"calls": 0, "step0_on": 0, "diff": 0}
def wrapped(plan, temps, start_below, charge_running=True):
    a = orig(plan, temps, start_below, True)
    b = orig(plan, temps, start_below, False)
    stats["calls"] += 1
    if start_below is not None and np.asarray(plan)[:1].sum() > 0:
        stats["step0_on"] += 1
    if not np.array_equal(a, b):
        stats["diff"] += 1
    return orig(plan, temps, start_below, charge_running)
dp.startable_steps = wrapped

mode = sys.argv[1] if len(sys.argv) > 1 else "head"
results = {}
for hyst, tank, win, minc in itertools.product([2.0, 4.0, 7.0], [44.0, 48.0, 50.0, 51.5, 52.0, 54.0],
                                              [None, "00:15-02:00", "06:00-08:00"], [None, 50.0, 53.0]):
    plan = bd._solve_winter_mild(hyst, under_way=False, window=win, min_c=minc, tank_c=tank)[0]
    results[(hyst, tank, win, minc)] = np.asarray(plan).round(9).tolist()
import json, hashlib
print(mode, "solves", len(results), "stats", stats,
      "digest", hashlib.sha256(json.dumps(sorted(results.items(), key=str)).encode()).hexdigest()[:16])
json.dump({str(k): v for k, v in results.items()}, open(f"/tmp/claude-0/h/plans_{mode}.json", "w"))
