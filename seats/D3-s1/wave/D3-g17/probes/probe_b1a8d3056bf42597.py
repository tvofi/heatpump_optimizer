#!/usr/bin/env python3
# Metric: count of random scenarios (and max |plan delta| kW) where DhwPlanner._plan_dhw_min_cost's plan differs under the mutant, split by p_total_max.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g17/probes/probe_b1a8d3056bf42597.py
# EXPECTED RESULT differing_pmax_pos=0/120 (p_total_max 1 and 3: a negative demand only raises headroom at a spare step, whose premium is 0)
# EXPECTED RESULT differing_pmax_nonpos=120/120, max delta 3 kW (p_total_max 0 or -0.5: an unclipped negative demand turns steps spare, so the refill premium and the plan move)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g17 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._plan_dhw_min_cost (dhw_planner.py:1527
#   `demand = np.clip(np.asarray(space_demand, dtype=float), 0.0, None)`).
# Perturbation: mutant b1a8d3056bf42597 (CLAMP_DROP) `demand = np.clip(np.asarray(space_demand, dtype=float), 0.0, None)` -> `demand = (np.asarray(space_demand, dtype=float))`, applied in memory: the method is re-compiled
#   from its own source with that one line edited (_g17.mutant) and called beside the untouched method.
#   Direction: plan moves (up to the full 3 kW per step) only when p_total_max <= 0 and some space demand is negative.
# Null control: space demand >= 0 (the clip is the identity) at p_total_max 0: null_differing.
# Count key: the returned plan array (kW per step).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _g17 import *  # noqa: E402,F403

OLD = 'demand = np.clip(np.asarray(space_demand, dtype=float), 0.0, None)'
NEW = 'demand = (np.asarray(space_demand, dtype=float))'
MUT = mutant('_plan_dhw_min_cost', '            demand = np.clip(np.asarray(space_demand, dtype=float), 0.0, None)', '            demand = (np.asarray(space_demand, dtype=float))', 1527)

n1, d1, w1 = sweep_min_cost(MUT, trials=120, pmax_choices=(1.0, 3.0), demand_lo=-3.0, demand_hi=4.0)
n2, d2, w2 = sweep_min_cost(MUT, trials=120, pmax_choices=(-0.5, 0.0), demand_lo=-3.0, demand_hi=4.0)
n3, d3, w3 = sweep_min_cost(MUT, trials=60, pmax_choices=(0.0,), demand_lo=0.0, demand_hi=4.0)
print(f"RESULT differing_pmax_pos={d1}/{n1} max_delta_kw={w1:.3g}")
print(f"RESULT differing_pmax_nonpos={d2}/{n2} max_delta_kw={w2:.3g}")
print(f"RESULT null_differing={d3}/{n3}")
print("RESULT reach=p_total_max is DhwPlanner.optimize's p_max (dhw_planner.py:1243), the configured maximum electrical power; a non-positive value is not established as reachable, and with p_total_max > 0 no input tried separates")
print("RESULT inputs_tried=120 random at p_total_max 1/3 with demand -3..4; 120 random at p_total_max -0.5/0 with demand -3..4; 60 at p_total_max 0 with demand 0..4 (null)")
footer()
