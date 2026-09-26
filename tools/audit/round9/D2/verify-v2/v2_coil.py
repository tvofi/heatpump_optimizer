#!/usr/bin/env python3
"""V2 (independent) re-measure of D2-s1-02: coil debit vs DHW tank's scaled draw.

Metric (one line): heat that vanishes per step with the wood coil active =
q_coil*dt - (DHW debit spared by the coil), read from the production calls
(thermal_model:dhw_coil_draw_reduction's returned (reduced, q_coil) and
ThermalModel.simulate_dhw_step's recorded _step_dhw_draw_kw with vs without the
reduction), in kWh; checked against the closed form q_coil*(1-scale)*dt; and the
REACH on the golden wood_coil scenario's published solve: steps of its published
DHW trajectory where the coil fires with the tank below DHW_MIXED_USE_TEMP, and the
kWh vanished over that published trajectory.
Count key: values the production functions return (hooked by wrapper), not inputs.
Hooks: thermal_model:dhw_coil_draw_reduction, ThermalModel.simulate_dhw_step,
ThermalModel.simulate_trajectory_with_dhw, optimizer:HeatPumpOptimizer.optimize.
Perturbation: --perturb=mixuse (DHW_MIXED_USE_TEMP -> inlet + 1e-3 in memory): vanished -> 0.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v2/v2_coil.py [--perturb=mixuse]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box G3-V2 (4-core linux, py3.14.0rc2). Deterministic.
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
from heatpump_optimizer import thermal_model as tm  # noqa: E402
from heatpump_optimizer import optimizer as om  # noqa: E402

t0p, t0t = time.process_time(), time.thread_time()
PERT = "--perturb=mixuse" in sys.argv

_orig_red = tm.dhw_coil_draw_reduction
_orig_dhw = tm.ThermalModel.simulate_dhw_step
_orig_traj = tm.ThermalModel.simulate_trajectory_with_dhw
calls = []          # per trajectory call: list of step events
pending = {}


def red(draw_kw, wood_temp, dhw_setpoint, inlet_temp=tm.DHW_COLD_WATER_TEMP):
    r, q = _orig_red(draw_kw, wood_temp, dhw_setpoint, inlet_temp)
    pending["ev"] = (draw_kw, r, q)
    return r, q


def dhw_step(self, dhw_temp, dhw_power_thermal, hour_of_day, ambient_temp=tm.DHW_AMBIENT_TEMP,
             dt_hours=0.25, draw_power=None):
    out = _orig_dhw(self, dhw_temp, dhw_power_thermal, hour_of_day, ambient_temp, dt_hours, draw_power)
    ev = pending.pop("ev", None)
    if ev is not None and calls:
        nominal, reduced, q = ev
        debit_with = self._step_dhw_draw_kw          # production's scaled debit of the reduced draw
        span = max(tm.DHW_MIXED_USE_TEMP - self.params.dhw_inlet_reference, 1e-6)
        scale = min(1.0, max(0.0, dhw_temp - self.params.dhw_inlet_reference) / span)
        debit_without = nominal * scale               # the same step with no coil
        vanished = (q - (debit_without - debit_with)) * dt_hours
        closed = q * (1.0 - scale) * dt_hours
        calls[-1].append((dhw_temp, q, vanished, closed))
    return out


def traj(self, *a, **k):
    calls.append([])
    return _orig_traj(self, *a, **k)


tm.dhw_coil_draw_reduction = red
tm.ThermalModel.simulate_dhw_step = dhw_step
tm.ThermalModel.simulate_trajectory_with_dhw = traj
if PERT:
    tm.DHW_MIXED_USE_TEMP = 10.0 + 1e-3  # replaced below once inlet is known

# 1. Sweep: my own model (defaults + coil), one step, DHW 20..60, wood 40..90, draw = pattern peak.
from heatpump_optimizer import mixing_valve  # noqa: E402
p = tm.ThermalParameters(two_zone_enabled=True, mixing_valve_mode=mixing_valve.MODE_MANUAL, buffer_tank_volume=300.0, wood_tank_configured=True, wood_tank_volume=300.0,
                         dhw_enabled=True, dhw_tank_volume=180.0, dhw_wood_coil_enabled=True)
assert p.dhw_coil_active
m = tm.ThermalModel(p)
if PERT:
    tm.DHW_MIXED_USE_TEMP = p.dhw_inlet_reference + 1e-3
peak_draw = max(m.dhw_draw_rate(h + 0.5) for h in range(24))
sw_n = sw_bad = 0
sw_max = 0.0
sw_identity_err = 0.0
for dhw0 in (20.0, 30.0, 35.0, 38.0, 42.0, 50.0, 60.0):
    for wood0 in (40.0, 60.0, 90.0):
        s = tm.ThermalState(room_temperature=21.0, slab_temperature=24.0, upper_floor_temperature=21.0,
                            lower_floor_temperature=21.0, buffer_tank_temperature=40.0,
                            dhw_temperature=dhw0, wood_tank_temperature=wood0)
        m.simulate_trajectory_with_dhw(initial_state=copy.deepcopy(s), space_power_schedule=np.zeros(1),
                                       dhw_power_schedule=np.zeros(1), outdoor_temps=np.zeros(1),
                                       start_hour=7.0, dt_hours=0.25, dhw_draw_rates=np.full(1, peak_draw))
        for (t, q, v, c) in calls[-1]:
            sw_n += 1
            sw_bad += v > 1e-12
            sw_max = max(sw_max, v)
            sw_identity_err = max(sw_identity_err, abs(v - c))
print(f"RESULT sweep_cells={sw_n} count (peak pattern draw {peak_draw:.3f} kW)")
print(f"RESULT sweep_cells_vanishing={sw_bad} count")
print(f"RESULT sweep_vanished_max={sw_max:.6f} kWh_per_step")
print(f"RESULT sweep_closed_form_abs_err_max={sw_identity_err:.2e} kWh")

# 2. Reach: golden wood_coil, published solve.
calls.clear()
last = {}
_opt = om.HeatPumpOptimizer.optimize


def optw(self, *a, **k):
    r = _opt(self, *a, **k)
    last["r"] = r
    return r


om.HeatPumpOptimizer.optimize = optw
spec = copy.deepcopy(golden.SCENARIOS["wood_coil"])
try:
    golden.capture("wood_coil", spec)
except AssertionError as e:
    print(f"# invariant: {e}")
r = last["r"]
pub = np.asarray(r.dhw_temp_trajectory, dtype=float)
match = None
for evs in reversed(calls):
    if len(evs) and len(evs) <= len(pub) - 1:
        temps = np.array([e[0] for e in evs])
        if len(evs) == len(pub) - 1 and np.allclose(temps, pub[:-1], atol=1e-9):
            match = evs
            break
print(f"RESULT golden_wood_coil_published_steps={len(pub) - 1} count")
print(f"RESULT golden_wood_coil_dhw_min={pub.min():.3f} degC")
if match is None:
    print("RESULT golden_wood_coil_trajectory_matched=0")
else:
    firing = [e for e in match if e[1] > 0.0]
    below = [e for e in firing if e[0] < tm.DHW_MIXED_USE_TEMP]
    print("RESULT golden_wood_coil_trajectory_matched=1")
    print(f"RESULT golden_wood_coil_coil_steps={len(firing)} count")
    print(f"RESULT golden_wood_coil_coil_steps_below_40C={len(below)} count")
    print(f"RESULT golden_wood_coil_vanished_total={sum(e[2] for e in match):.6f} kWh")
    print(f"RESULT golden_wood_coil_coil_heat_total={sum(e[1] for e in match) * 0.25:.6f} kWh")

pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(ln.split()[1]) for ln in open("/proc/vmstat") if ln.startswith("pswpin"))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
