#!/usr/bin/env python3
# Metric: how many of the three predictive keys (solar_reduction_factor, wind_anticipation_factor, pre_heat_urgency)
#   HeatPumpOptimizer.get_current_action puts in the action for step 0 of a real solved plan (tests/manual_plan.py
#   _build_optimizer winter_typical/winter_cold, no pins), and the pre_heat_urgency the legacy ECL110 MQTT command
#   body (heat_curve.ecl110_legacy_payload, its "context") publishes from that action.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g26/probes/probe_35d104f30f878131.py
# EXPECTED RESULT predictive_keys_baseline=3 count, predictive_keys_mutant=0 count; tolerance exact
# EXPECTED RESULT ecl110_context_pre_heat_urgency_baseline=0.16 , _mutant=None  (the published MQTT command context loses the value)
# EXPECTED RESULT null_keys_delta=0 count  (null: the same plan with predictive_info emptied -- the block is skipped in both arms)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g26 cloud (4 vCPU Intel Xeon @ 2.30GHz, 16 GB), venv-ci CPython; run while a GATE_JOBS=1 gate ran (counts exact, no timing reported).
# Instrumented symbol: custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.get_current_action line 6661
#   `        if result.predictive_info:` (the block adding the three predictive keys to the current action).
# Perturbation: `if result.predictive_info:` -> `if False:` applied in memory (the method recompiled from its own source).
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import g26_common as g  # noqa: E402  (thread pin first)
from unittest import mock  # noqa: E402
mp = g.manual_plan_module()
from heatpump_optimizer import optimizer as O  # noqa: E402
from heatpump_optimizer import heat_curve as HC  # noqa: E402
H = O.HeatPumpOptimizer
MUT = g.mutant(H, "get_current_action", "if result.predictive_info:", "if False:")
KEYS = ("solar_reduction_factor", "wind_anticipation_factor", "pre_heat_urgency")
w = mp._build_optimizer("winter_typical", "winter_cold")
result = mp._solve(w)
opt = w[0]
now = result.timestamps[0]
empty = copy.copy(result)
empty.predictive_info = {}


def arm(res, mutated):
    with mock.patch.object(H, "get_current_action", MUT if mutated else H.get_current_action):
        act = opt.get_current_action(res, now)
    body = HC.ecl110_legacy_payload("probe", act["heat_pump_on"], 0, act)
    return sum(1 for k in KEYS if k in act), body["context"]["pre_heat_urgency"], {k: act.get(k) for k in KEYS}


bk, bu, bv = arm(result, False)
mk, mu, mv = arm(result, True)
nb, _, _ = arm(empty, False)
nm, _, _ = arm(empty, True)
print(f"RESULT predictive_info_keys_in_plan={len(result.predictive_info)} count")
print(f"RESULT predictive_keys_baseline={bk} count  {bv}")
print(f"RESULT predictive_keys_mutant={mk} count  {mv}")
print(f"RESULT ecl110_context_pre_heat_urgency_baseline={bu}")
print(f"RESULT ecl110_context_pre_heat_urgency_mutant={mu}")
print(f"RESULT null_keys_delta={abs(nb - nm)} count")
g.trailer()
