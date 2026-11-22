#!/usr/bin/env python3
# Metric: whether optimize() adopts the valve hold candidate (result.valve_target_schedule non-empty) and the plan's
#   objective, baseline vs mutant, on the golden smart_write scenarios (tests/golden.py SCENARIOS
#   valve_storage_smart_write and wood_two_tank_smart_write, each at winter_typical and flat prices, 24 h and 48 h),
#   counted as cells whose (adopted, objective) differ. A FORCED-TIE arm then shows the only input that separates the
#   two: the candidate solve's objective_value overwritten to exactly fixed_objective - 1e-9 (the solver double
#   returned by the instance's own _optimize_* wrapper), which no honest solve produces.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_9a06a1a7e515fa67.py
# EXPECTED RESULT natural_cells_moved=0 count (of 8)  (honest candidate objectives never land exactly on fixed - 1e-9)
# EXPECTED RESULT forced_tie_adopted_baseline=0, forced_tie_adopted_mutant=1  (the boundary itself: the tie is adopted under <=)
# EXPECTED RESULT null: the flat-price cells propose no candidate in either arm; tolerance exact
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g26 cloud (4 vCPU Intel Xeon @ 2.30GHz, 16 GB), venv-ci CPython; run while a GATE_JOBS=1 gate ran (counts exact, no timing reported).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize line 4610
#   `                    and candidate.objective_value < fixed_objective - 1e-9` (the hold candidate's adoption rule).
# Perturbation: `<` -> `<=` applied in memory (optimize recompiled from its own source, patched onto the class).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g26_common as g  # noqa: E402  (thread pin first)
import numpy as np  # noqa: E402
from unittest import mock  # noqa: E402
import golden  # noqa: E402
from profiles import solve_inputs  # noqa: E402
from heatpump_optimizer import optimizer as O  # noqa: E402
H = O.HeatPumpOptimizer
OLD = "and candidate.objective_value < fixed_objective - 1e-9"
MUT = g.mutant(H, "optimize", OLD, "and candidate.objective_value <= fixed_objective - 1e-9")


def solve(name, price, hours, mutated, force_tie=False):
    spec = dict(golden.SCENARIOS[name]); spec["price_profile"] = price; spec["hours"] = hours
    b = golden.make(**spec)
    opt = b["optimizer"]
    calls = []
    if force_tie:
        for attr in ("_optimize_with_dhw", "_optimize_space_only"):
            bound = getattr(opt, attr)

            def wrap(*a, _b=bound, **k):
                r = _b(*a, **k)
                calls.append(r.objective_value)
                if len(calls) == 2:  # the hold candidate's solve
                    r.objective_value = calls[0] - 1e-9
                return r
            setattr(opt, attr, wrap)
    with mock.patch.object(H, "optimize", MUT if mutated else H.optimize):
        r = opt.optimize(inputs=solve_inputs(
            initial_state=b["state"], prices=b["prices"], outdoor_temps=b["outdoor"], wind_speeds=b["wind"],
            precipitation=b["rain"], solar_radiation=b["solar"], start_time=golden.START))
    return int(bool(r.valve_target_schedule)), round(float(r.objective_value), 9), len(calls)


cells, moved, adopted = 0, 0, []
for name in ("valve_storage_smart_write", "wood_two_tank_smart_write"):
    for price in ("winter_typical", "flat"):
        for hours in (24, 48):
            bb, mm = solve(name, price, hours, False), solve(name, price, hours, True)
            cells += 1
            moved += int(bb[:2] != mm[:2])
            adopted.append(f"{name}/{price}/{hours}h:{bb[0]}{mm[0]}")
ft_b = solve("valve_storage_smart_write", "winter_typical", 24, False, force_tie=True)
ft_m = solve("valve_storage_smart_write", "winter_typical", 24, True, force_tie=True)
print(f"RESULT natural_cells={cells} count")
print(f"RESULT natural_cells_moved={moved} count")
print(f"RESULT adopted_baseline_mutant={adopted}")
print(f"RESULT forced_tie_solves={ft_b[2]} count")
print(f"RESULT forced_tie_adopted_baseline={ft_b[0]}")
print(f"RESULT forced_tie_adopted_mutant={ft_m[0]}")
g.trailer()
