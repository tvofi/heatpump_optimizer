#!/usr/bin/env python3
# Metric: count of (outdoor temperature, cop_scale, tank) inputs on which _max_pump_rise differs between the baseline
#   and the mutant that drops the max(cop, 1.0) floor (NaN == NaN counted equal).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_7f2768bd0a78b4bf.py
# EXPECTED RESULT inputs_tried=588 count  (98 outdoor values: -60..+34 C in 1 K steps plus NaN, +inf, -inf; cop_scale
#   COP_SCALE_MIN 0.5 / 1.0 / COP_SCALE_MAX; tanks dhw and buffer)
# EXPECTED RESULT inputs_differing=0 count  (compute_cop's only return is _cop_law's max(cop, 1.0): the clamp at 5103
#   is the identity on every value compute_cop can return, NaN included since max(nan, 1.0) is nan)
# EXPECTED RESULT min_cop_seen=1.0  (the floor the clamp would add)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._max_pump_rise, line 5103
#   (and thermal_model:ThermalModel.compute_cop, the value it clamps).
# Perturbation: key 7f2768bd0a78b4bf (CLAMP_DROP), line 5103 `thermal_kw = params.max_electrical_power * max(cop, 1.0)` ->
#   `thermal_kw = params.max_electrical_power * (cop)`, in memory. Direction: rise down where cop < 1 (none found).
# Null control: positive arm. The same mutant with compute_cop forced to return 0.5 (an input compute_cop never
#   produces): forced_baseline > forced_mutant, so the probe can see the clamp when it acts.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses
import math
import sys
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
from heatpump_optimizer.const import COP_SCALE_MAX, COP_SCALE_MIN  # noqa: E402

BASE = L.baseline("_max_pump_rise")
MUT = L.mutant("_max_pump_rise", "thermal_kw = params.max_electrical_power * max(cop, 1.0)",
               "thermal_kw = params.max_electrical_power * (cop)")
c = L.coord(dhw_tank_volume=200.0)


def same(a, b):
    return (a is None and b is None) or (a is not None and b is not None and (a == b or (math.isnan(a) and math.isnan(b))))


temps = [float(t) for t in range(-60, 35)] + [math.nan, math.inf, -math.inf]
tried = differ = 0
min_cop = math.inf
for scale in (COP_SCALE_MIN, 1.0, COP_SCALE_MAX):
    c._thermal_model.params = dataclasses.replace(c._thermal_model.params, cop_scale=scale)
    for t in temps:
        c._current_state = dataclasses.replace(c._current_state, outdoor_temperature=t)
        cop = c._thermal_model.compute_cop(t)
        if not math.isnan(cop):
            min_cop = min(min_cop, cop)
        for tank in ("dhw", "buffer"):
            tried += 1
            differ += int(not same(BASE(c, tank), MUT(c, tank)))
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT inputs_differing={differ} count")
print(f"RESULT min_cop_seen={min_cop}")
c._current_state = dataclasses.replace(c._current_state, outdoor_temperature=5.0)
with mock.patch.object(c._thermal_model, "compute_cop", lambda *a, **k: 0.5):
    print(f"RESULT forced_baseline={BASE(c, 'buffer'):.3f} degC/h")
    print(f"RESULT forced_mutant={MUT(c, 'buffer'):.3f} degC/h")
L.footer()
