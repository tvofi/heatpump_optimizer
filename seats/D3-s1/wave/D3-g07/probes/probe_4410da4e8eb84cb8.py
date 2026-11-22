#!/usr/bin/env python3
# Metric: _guard_floor_hold() verdict (1 hold, 0 none) with hot water DISABLED and a dhw_temperature reading below dhw_min_temp (40 < 45 C), room above the floor.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_4410da4e8eb84cb8.py
# EXPECTED RESULT hold_baseline=0 bool
# EXPECTED RESULT hold_mutant=1 bool  (a disabled tank's reading now holds the guard)
# EXPECTED RESULT null_baseline=0 bool
# EXPECTED RESULT null_mutant=0 bool  (dhw disabled, tank above minimum: or-arm false too)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._guard_floor_hold, line 8838.
# Perturbation: key 4410da4e8eb84cb8 (BOOLOP), line 8838 `if params.dhw_enabled and state.dhw_temperature < params.dhw_min_temp:` -> `if params.dhw_enabled or state.dhw_temperature < params.dhw_min_temp:`, applied in memory (the method's source re-compiled with
#   that one line replaced, bound to a live coordinator). Direction: hold up (0 -> 1).
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
MUT = L.mutant("_guard_floor_hold", """if params.dhw_enabled and state.dhw_temperature < params.dhw_min_temp:""", """if params.dhw_enabled or state.dhw_temperature < params.dhw_min_temp:""")
kw = dict(dhw_enabled=False, dhw_temp=40.0, dhw_min=45.0)
print(f"RESULT hold_baseline={hold(BASE, **kw)}")
print(f"RESULT hold_mutant={hold(MUT, **kw)}")
nk = dict(dhw_enabled=False, dhw_temp=55.0, dhw_min=45.0)
print(f"RESULT null_baseline={hold(BASE, **nk)}")
print(f"RESULT null_mutant={hold(MUT, **nk)}")
L.footer()
