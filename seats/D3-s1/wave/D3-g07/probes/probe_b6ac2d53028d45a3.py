#!/usr/bin/env python3
# Metric: _interval_space_power() in kW (None = "skip this sample", printed as -1) with a power entity configured,
#   the pump's observed mode hot-water-only (space_heat False, dhw True), the plan allocating 1.5 kW to hot water and
#   0 kW to space, and the meter reading 1.5 kW.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_b6ac2d53028d45a3.py
# EXPECTED RESULT space_kw_baseline=-1 kW  (None: a mode heating no rooms carries no space sample)
# EXPECTED RESULT space_kw_mutant=0.0 kW  (a confident 0 kW space sample reaches the heat-loss learner)
# EXPECTED RESULT off_baseline=-1 kW, off_mutant=0.0 kW  (mode off: no space, no hot water, meter 0 kW)
# EXPECTED RESULT null_baseline=2.0 kW, null_mutant=2.0 kW  (space-heat mode, 2 kW planned and measured)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._interval_space_power, line 5049.
# Perturbation: key b6ac2d53028d45a3 (GUARD_OFF), line 5049
#   `if self._pump_signals.mode_observed and not self._pump_signals.space_heat:` -> `if False:`, in memory.
#   Direction: None -> 0.0 kW (a skipped interval becomes a 0 kW sample).
# Null control: an observed space-heat mode, where the guard is not taken in either arm.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402

BASE = L.baseline("_interval_space_power")
MUT = L.mutant("_interval_space_power",
               "if self._pump_signals.mode_observed and not self._pump_signals.space_heat:", "if False:")


def run(fn, measured, space_heat, dhw, power, dhw_power):
    c = L.coord(heat_pump_power_entity="sensor.hp_power")
    s = c._pump_signals
    c._pump_signals = dataclasses.replace(
        s, mode=dataclasses.replace(s.mode, space_heat=space_heat, dhw=dhw, known=True), mode_observed=True)
    c._measured_power = measured
    c._immersion_active = False
    c._current_action = {"power": power, "dhw_power": dhw_power}
    v = fn(c)
    return -1.0 if v is None else float(v)


print(f"RESULT space_kw_baseline={run(BASE, 1.5, False, True, 0.0, 1.5):g} kW")
print(f"RESULT space_kw_mutant={run(MUT, 1.5, False, True, 0.0, 1.5):g} kW")
print(f"RESULT off_baseline={run(BASE, 0.0, False, False, 0.0, 0.0):g} kW")
print(f"RESULT off_mutant={run(MUT, 0.0, False, False, 0.0, 0.0):g} kW")
print(f"RESULT null_baseline={run(BASE, 2.0, True, True, 2.0, 0.0):g} kW")
print(f"RESULT null_mutant={run(MUT, 2.0, True, True, 2.0, 0.0):g} kW")
L.footer()
