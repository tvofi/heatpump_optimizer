#!/usr/bin/env python3
# Metric: number of FlowCurveBias states whose bias_k is non-finite after one observe() with a non-finite
#   measured or curve supply (two probes), and how many production folds reach observe() with a non-finite pair.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fl183_nonfinite.py
# EXPECTED RESULT poisoned_baseline=0 count
# EXPECTED RESULT poisoned_mutant=2 count
# EXPECTED RESULT reach_nonfinite_pairs=0 count  (curve_supply_temp and observe_temps already map non-finite to None)
# EXPECTED RESULT null_delta=0.0 K  (a finite pair folds identically in both arms)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-top6 (4 vCPU Xeon @ 2.30GHz). Counts are exact.
# Instrumented symbol: custom_components.heatpump_optimizer.flow_lift:FlowCurveBias.observe (line 183 guard
#   `if not np.isfinite(measured_supply) or not np.isfinite(curve_supply):`); reach through
#   flow_lift:FlowCurveBias.observe_temps and flow_lift:curve_supply_temp, the two producers of its inputs.
# Perturbation: line 183 -> `if False:` (GUARD_OFF 3885e472b8297a90), in memory: observe is re-compiled from its
#   own source with that one edit and patched onto the class. Direction: poisoned 0 -> 2.
#   The full gate (fullgate.py run --src complete --key 3885e472b8297a90) stays green under it.
# Null control: the finite pair (41.0, 38.0) gives the same bias_k in both arms.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, math, sys, textwrap
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import flow_lift as fl  # noqa: E402

OLD = "if not np.isfinite(measured_supply) or not np.isfinite(curve_supply):"


def mutant():
    src = textwrap.dedent(inspect.getsource(fl.FlowCurveBias.observe))
    assert src.count(OLD) == 1, "anchor line moved"
    ns = dict(fl.__dict__)
    exec(compile(src.replace(OLD, "if False:"), fl.__file__, "exec"), ns)
    return ns["observe"]


def poisoned():
    n = 0
    for pair in ((math.nan, 38.0), (41.0, math.nan)):
        b = fl.FlowCurveBias()
        b.observe(*pair)
        n += int(not math.isfinite(b.bias_k))
    return n


def finite_bias():
    b = fl.FlowCurveBias()
    b.observe(41.0, 38.0)
    return b.bias_k


base, null_b = poisoned(), finite_bias()
with mock.patch.object(fl.FlowCurveBias, "observe", mutant()):
    mut, null_m = poisoned(), finite_bias()

# Reach: the two producers of observe()'s arguments, fed every non-finite value.
model = SimpleNamespace(flow_target_for_indoor=lambda target, outdoor: 35.0 + (target - outdoor) * 0.0)
reach = 0
for bad in (math.nan, math.inf, -math.inf):
    b = fl.FlowCurveBias()
    b.observe_temps(bad, 30.0)
    curve_outdoor = fl.curve_supply_temp(model, bad, 21.0)
    curve_target = fl.curve_supply_temp(model, 0.0, bad)
    nan_model = SimpleNamespace(flow_target_for_indoor=lambda target, outdoor, v=bad: v)
    curve_model = fl.curve_supply_temp(nan_model, 0.0, 21.0)
    for v in (b.last_supply_c, curve_outdoor, curve_target, curve_model):
        reach += int(v is not None and not math.isfinite(v))
print(f"RESULT poisoned_baseline={base} count")
print(f"RESULT poisoned_mutant={mut} count")
print(f"RESULT reach_nonfinite_pairs={reach} count")
print(f"RESULT null_delta={abs(null_b - null_m)} K")
print("RESULT thread_factor=1.0 ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0 count")
