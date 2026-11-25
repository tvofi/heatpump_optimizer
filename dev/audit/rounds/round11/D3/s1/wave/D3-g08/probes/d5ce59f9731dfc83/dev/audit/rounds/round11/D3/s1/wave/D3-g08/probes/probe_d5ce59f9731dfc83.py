#!/usr/bin/env python3
# Metric: the published valve_target_recommendation.price_ratio (and its reason's first words) that
#   HeatPumpOptimizerCoordinator._mixing_valve_view returns for one price list; key = the payload value delivered.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g08/probes/probe_d5ce59f9731dfc83.py
# Expected: prices [0.0, 0.1, 0.2]: baseline price_ratio=0.5, mutant 0.0; prices [None, 1.0, 1.0] (a slot whose total
#   is missing reads 0.0 through finite_float): baseline 1.0 with the "Prices are nearly flat" reason, mutant 0.0 with
#   the "Set to the top" reason; null (all totals > 0): moved 0. Exact (deterministic).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g08 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._mixing_valve_view
#   (coordinator.py:8176 `positives = [t for t in totals if t > 0.0]`), merged into the coordinator payload at :8227.
# Perturbation: mutant d5ce59f9731dfc83 (CMP_BOUND) `t > 0.0` -> `t >= 0.0`, compiled in memory from the method's
#   source; direction: a zero-total slot joins `positives`, price_ratio falls to 0.0.
# Inputs: SimpleNamespace coordinator (no _ctx) with a real ThermalParameters(mixing_valve_mode=<a throttling mode>)
#   and comfort band 20..23 degC; the price lists in CASES.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path.cwd()))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402
from custom_components.heatpump_optimizer import mixing_valve  # noqa: E402
from custom_components.heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

CLS = co.HeatPumpOptimizerCoordinator
OLD, NEW = "positives = [t for t in totals if t > 0.0]", "positives = [t for t in totals if t >= 0.0]"


def mutant(fn):
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(OLD) == 1, "anchor line moved"
    ns = dict(co.__dict__)
    exec(compile(src.replace(OLD, NEW, 1), co.__file__, "exec"), ns)
    return ns[fn.__name__]


MUT = mutant(CLS._mixing_valve_view)
MODE = sorted(mixing_valve.THROTTLING_MODES)[0]
PARAMS = ThermalParameters(mixing_valve_mode=MODE)


def view(fn, totals):
    me = SimpleNamespace(_thermal_params=PARAMS, _opt_config=SimpleNamespace(min_temp=20.0, max_temp=23.0),
                         _prices=[{"total": t} for t in totals])
    rec = fn(me)["valve_target_recommendation"]
    return rec["price_ratio"], " ".join(rec["reason"].split()[:3])


CASES = {
    "zero_slot": [0.0, 0.1, 0.2],
    "missing_total": [None, 1.0, 1.0],
    "nan_total": [float("nan"), 0.5, 0.6],
    "zero_and_one_positive": [0.0, 0.2],
    "negative_and_zero": [-0.1, 0.0, 0.3, 0.4],
}
NULLS = {"all_positive": [0.1, 0.2, 0.3], "negative_only_nonpos": [-0.2, 0.1, 0.4]}
print(f"RESULT throttling_mode={MODE}")
moved = 0
for name, totals in CASES.items():
    b, m = view(CLS._mixing_valve_view, totals), view(MUT, totals)
    moved += int(b != m)
    print(f"RESULT {name}_baseline=price_ratio {b[0]} reason '{b[1]}'")
    print(f"RESULT {name}_mutant=price_ratio {m[0]} reason '{m[1]}'")
print(f"RESULT cases_moved={moved} count of {len(CASES)}")
print(f"RESULT null_moved={sum(int(view(CLS._mixing_valve_view, t) != view(MUT, t)) for t in NULLS.values())} count of {len(NULLS)}")
