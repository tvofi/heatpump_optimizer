#!/usr/bin/env python3
# Metric: _guard_floor_hold() verdict (1 hold, 0 none) with hot water enabled, the tank at 40 C under its 45 C minimum, room above the floor.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_f11665aaedbf2550.py
# EXPECTED RESULT hold_baseline=1 bool
# EXPECTED RESULT hold_mutant=0 bool  (a cold tank no longer outranks the peak/price guard)
# EXPECTED RESULT null_baseline=1 bool
# EXPECTED RESULT null_mutant=1 bool  (room 16 C under the 17 C floor: held by the room arm in both)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._guard_floor_hold, line 8838.
# Perturbation: key f11665aaedbf2550 (GUARD_OFF), line 8838 `if params.dhw_enabled and state.dhw_temperature < params.dhw_min_temp:` -> `if False:`, applied in memory (the method's source re-compiled with
#   that one line replaced, bound to a live coordinator). Direction: hold down (1 -> 0).
# Null control: the same mutant on a state where the edited condition cannot matter (null_* RESULTs, expected equal).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
from probe_guard_common import hold  # noqa: E402

BASE = L.baseline("_guard_floor_hold")
MUT = L.mutant("_guard_floor_hold", """if params.dhw_enabled and state.dhw_temperature < params.dhw_min_temp:""", """if False:""")
kw = dict(dhw_enabled=True, dhw_temp=40.0, dhw_min=45.0)
print(f"RESULT hold_baseline={hold(BASE, **kw)}")
print(f"RESULT hold_mutant={hold(MUT, **kw)}")
nk = dict(dhw_enabled=True, dhw_temp=40.0, dhw_min=45.0, room=16.0)
print(f"RESULT null_baseline={hold(BASE, **nk)}")
print(f"RESULT null_mutant={hold(MUT, **nk)}")
L.footer()
