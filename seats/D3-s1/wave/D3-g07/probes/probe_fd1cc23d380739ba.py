#!/usr/bin/env python3
# Metric: _guard_floor_hold() verdict (1 hold, 0 none) with the room exactly at min_temp (17.0 == 17.0 C), hot water off.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_fd1cc23d380739ba.py
# EXPECTED RESULT hold_baseline=0 bool
# EXPECTED RESULT hold_mutant=1 bool  (a room exactly at the floor now holds the guard)
# EXPECTED RESULT null_baseline=0 bool
# EXPECTED RESULT null_mutant=0 bool  (room 17.1 C: above the floor in both arms)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._guard_floor_hold, line 8847.
# Perturbation: key fd1cc23d380739ba (CMP_BOUND), line 8847 `return any(t is not None and float(t) < floor for t in temps)` -> `return any(t is not None and float(t) <= floor for t in temps)`, applied in memory (the method's source re-compiled with
#   that one line replaced, bound to a live coordinator). Direction: hold up at the tie (0 -> 1).
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
MUT = L.mutant("_guard_floor_hold", """return any(t is not None and float(t) < floor for t in temps)""", """return any(t is not None and float(t) <= floor for t in temps)""")
kw = dict(room=17.0, min_temp=17.0)
print(f"RESULT hold_baseline={hold(BASE, **kw)}")
print(f"RESULT hold_mutant={hold(MUT, **kw)}")
nk = dict(room=17.1, min_temp=17.0)
print(f"RESULT null_baseline={hold(BASE, **nk)}")
print(f"RESULT null_mutant={hold(MUT, **nk)}")
L.footer()
