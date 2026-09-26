"""D2 verify-v1 (round 9): D2-s2-03 mechanism perturbation independent of the finder's own fix.

Metric (one line): end_mismatch = count of (scenario, store) where the end state
  HeatPumpOptimizer._deferred_energy_cost settles differs by > 1e-6 K from the
  published *_trajectory[-1], on golden scenario wood_coil only -- measured by the
  finder's harness tools/audit/round9/D2/s2/objective_identities.py (run via runpy,
  unchanged), with thermal_model.dhw_coil_draw_reduction either left alone (arm
  "coil") or replaced in memory by (draw, 0.0) in both thermal_model and optimizer
  namespaces (arm "nocoil": the coil carries no heat).
Count key: the ThermalState _deferred_energy_cost receives vs OptimizationResult trajectories.
Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v1/coil_off_settle.py [coil|nocoil]
Expected (baseline 1936d5ca + round-9 evidence 6f51db2c): coil -> end_mismatch=6;
  nocoil -> end_mismatch=0 (the mismatch is the coil coupling, not the finder's tautological
  replay swap). Tolerance exact. Machine: G3-V1 cloud container, 4 cores, py3.14.0rc2, numpy 2.4.6.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import runpy
import sys
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402,F401
from heatpump_optimizer import optimizer as optmod  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402

ARM = sys.argv[1] if len(sys.argv) > 1 else "coil"
if ARM == "nocoil":
    def _nocoil(draw_kw, wood_temp, dhw_setpoint, inlet_temp=tm.DHW_COLD_WATER_TEMP):
        return draw_kw, 0.0
    tm.dhw_coil_draw_reduction = _nocoil
    optmod.dhw_coil_draw_reduction = _nocoil
print(f"RESULT arm={ARM}")
sys.argv = ["objective_identities.py", "--only", "wood_coil"]
runpy.run_path("tools/audit/round9/D2/s2/objective_identities.py", run_name="__main__")
# thread_factor / load1 / swapins are printed by the finder's harness it wraps.
try:
    sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins_wrapper={sw}")
