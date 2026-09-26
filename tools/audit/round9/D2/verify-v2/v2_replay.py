#!/usr/bin/env python3
"""V2 (independent) re-measure of D2-s2-03: DHW-path settlement replays space-only.

Metric (one line): per solve on the DHW path, the stored-heat discrepancy
sum_i C_i*(replay_end_i - published_end_i) in kWh over the space stores (upper, lower,
slab, buffer) and the wood tank, where replay_end is what
HeatPumpOptimizer._replay_end_state returns (the state _deferred_energy_cost settles)
and published_end is the last simulate_trajectory_with_dhw output of the same solve;
grid = golden wood_coil with the wood tank starting at {40, 55, 70, 85} degC x
DHW start {45, 55} degC, plus null arms: golden wood_two_tank (no coil) and the
coil scenario with dhw_wood_coil_enabled False.
Count key: the ThermalState production returns vs the trajectory production returns.
Hooks: optimizer:HeatPumpOptimizer._replay_end_state, thermal_model:ThermalModel.simulate_trajectory_with_dhw.
Perturbation / null: the coil-disabled arm must read 0. The arm with the wood tank
starting at 12 degC is NOT a null: the heating loop reheats the wood tank (to 24.6 degC)
and the coil still fires (11.3 kW-steps summed), so it reads non-zero.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v2/v2_replay.py
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box G3-V2 (4-core linux, py3.14.0rc2). +-1e-6 kWh.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import copy
import sys
import time
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import optimizer as om  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402

t0p, t0t = time.process_time(), time.thread_time()
rec = {}
_tr = tm.ThermalModel.simulate_trajectory_with_dhw
_rp = om.HeatPumpOptimizer._replay_end_state


def tr(self, *a, **k):
    out = _tr(self, *a, **k)
    rec["traj"] = (out, self.params)
    return out


def rp(self, *a, **k):
    end = _rp(self, *a, **k)
    if "traj" in rec:
        rec.setdefault("pairs", []).append((copy.deepcopy(end), rec["traj"]))
    return end


tm.ThermalModel.simulate_trajectory_with_dhw = tr
om.HeatPumpOptimizer._replay_end_state = rp


def discrepancy(name, state_over=None, cfg_over=None):
    rec.clear()
    spec = copy.deepcopy(golden.SCENARIOS[name])
    spec["state_overrides"] = {**(spec.get("state_overrides") or {}), **(state_over or {})}
    spec["config_overrides"] = {**(spec.get("config_overrides") or {}), **(cfg_over or {})}
    try:
        golden.capture(name, spec)
    except AssertionError as e:
        print(f"# {name} invariant: {e}")
    pairs = rec.get("pairs", [])
    if not pairs:
        return None
    end, (out, p) = pairs[-1]
    room, slab, upper, lower, dhw, buf, wood = out
    kwh = (p.upper_floor_thermal_mass * (end.upper_floor_temperature - upper[-1])
           + p.lower_floor_thermal_mass * (end.lower_floor_temperature - lower[-1])
           + p.slab_thermal_mass * (end.slab_temperature - slab[-1])
           + p.buffer_tank_thermal_mass * (end.buffer_tank_temperature - buf[-1]))
    wkwh = 0.0 if wood is None or end.wood_tank_temperature is None else \
        p.wood_tank_thermal_mass * (end.wood_tank_temperature - wood[-1])
    return kwh, wkwh


rows = []
for w0 in (40.0, 55.0, 70.0, 85.0):
    for d0 in (45.0, 55.0):
        r = discrepancy("wood_coil", {"wood_tank_temperature": w0, "dhw_temperature": d0})
        rows.append(r)
        print(f"# wood_coil wood0={w0} dhw0={d0}: space_kwh={r[0]:+.4f} wood_kwh={r[1]:+.4f}", flush=True)
nz = sum(1 for r in rows if abs(r[0]) + abs(r[1]) > 1e-6)
print(f"RESULT coil_cells={len(rows)} count")
print(f"RESULT coil_cells_mismatched={nz} count")
print(f"RESULT coil_space_kwh_max={max(r[0] for r in rows):.4f} kWh")
print(f"RESULT coil_wood_kwh_max={max(r[1] for r in rows):.4f} kWh")
n1 = discrepancy("wood_two_tank")
n2 = discrepancy("wood_coil", None, {"dhw_wood_coil_enabled": False})
n3 = discrepancy("wood_coil", {"wood_tank_temperature": 12.0})
for tag, n in (("null_wood_two_tank", n1), ("null_coil_disabled", n2), ("coil_wood_start12_not_null", n3)):
    print(f"RESULT {tag}_abs_kwh={'none' if n is None else f'{abs(n[0]) + abs(n[1]):.2e}'}")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(ln.split()[1]) for ln in open("/proc/vmstat") if ln.startswith("pswpin"))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
