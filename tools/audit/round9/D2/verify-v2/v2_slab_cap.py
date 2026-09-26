#!/usr/bin/env python3
"""V2 (independent) re-measure of D2-s2-01: settlement caps ignore house_heat_loss_scale.

Metric (one line): K by which optimizer.slab_settlement_cap differs from the slab
temperature that holds the room at target under the production dynamics, the latter
found by bisection on ThermalModel.simulate_step (pump off, slab and room held,
dT_room/dt = 0), swept over house_heat_loss_scale in the learner's clamp
[HOUSE_HEAT_LOSS_SCALE_MIN, MAX] x outdoor {-10, 0, 8} x {1-zone, 2-zone} with the
shipped defaults; plus hold_demand_kw / (the steady-state demand the dynamics imply).
Count key: the cap production returns vs the root of the production step.
Hooks: optimizer:slab_settlement_cap, optimizer:hold_demand_kw, thermal_model:ThermalModel.simulate_step.
Perturbation: --perturb multiplies the losses handed to both functions by the scale: gap -> 0.
Null control: scale 1.0 rows.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v2/v2_slab_cap.py [--perturb]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box G3-V2 (4-core linux, py3.14.0rc2). Deterministic.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import copy
import sys
import time
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from heatpump_optimizer import optimizer as om  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402
from heatpump_optimizer.const import HOUSE_HEAT_LOSS_SCALE_MIN, HOUSE_HEAT_LOSS_SCALE_MAX  # noqa: E402

t0p, t0t = time.process_time(), time.thread_time()
PERT = "--perturb" in sys.argv
TARGET = 21.0


def scaled(p):
    q = copy.copy(p)
    s = p.house_heat_loss_scale
    q.heat_loss_coefficient *= s
    q.upper_floor_heat_loss *= s
    q.lower_floor_heat_loss *= s
    return q


def cap_of(p, out):
    return om.slab_settlement_cap(scaled(p) if PERT else p, TARGET, out)


def hold_of(p, out):
    return om.hold_demand_kw(scaled(p) if PERT else p, TARGET, out)


def room_rate(m, slab, out):
    p = m.params
    s = tm.ThermalState(room_temperature=TARGET, slab_temperature=slab,
                        upper_floor_temperature=TARGET, lower_floor_temperature=TARGET,
                        buffer_tank_temperature=TARGET, outdoor_temperature=out)
    dt = 1e-4
    n = m.simulate_step(s, 0.0, out, 0.0, 0.0, 0.0, dt)
    if p.two_zone_enabled:
        return (n.lower_floor_temperature - TARGET) / dt   # the slab feeds the lower zone only
    return (n.room_temperature - TARGET) / dt


def sustaining_slab(m, out):
    lo, hi = TARGET - 30.0, TARGET + 200.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if room_rate(m, mid, out) < 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


rows = []
for tz in (False, True):
    for sc in (HOUSE_HEAT_LOSS_SCALE_MIN, 0.6, 1.0, 1.5, 2.0, HOUSE_HEAT_LOSS_SCALE_MAX):
        for out in (-10.0, 0.0, 8.0):
            p = tm.ThermalParameters()
            p.two_zone_enabled = tz
            p.internal_gains_profile = None
            p.buffer_max_temp = 1000.0          # remove the plant bound so the law itself is compared
            p.house_heat_loss_scale = sc
            m = tm.ThermalModel(p)
            gap = cap_of(p, out) - sustaining_slab(m, out)
            if tz:
                # lower zone must also be held against the upper zone at target: no inter-zone flow at equal temps
                u_dyn = m.effective_heat_loss_coefficient(p.upper_floor_heat_loss) + \
                    m.effective_heat_loss_coefficient(p.lower_floor_heat_loss_learned)
            else:
                u_dyn = m.effective_heat_loss_coefficient(p.heat_loss_coefficient)
            dem = max(0.0, u_dyn * (TARGET - out) - p.internal_gains)
            hr = hold_of(p, out) / dem if dem > 0 else float("nan")
            rows.append((tz, sc, out, gap, hr))
            print(f"# {'2z' if tz else '1z'} s={sc} out={out} cap_gap={gap:+.4f} K hold_ratio={hr:.4f}")
null = [abs(r[3]) for r in rows if r[1] == 1.0]
off = [r for r in rows if r[1] != 1.0]
print(f"RESULT cells={len(rows)} count")
print(f"RESULT cap_gap_abs_max={max(abs(r[3]) for r in off):.4f} K")
print(f"RESULT cap_gap_at_scale_max_min={min(r[3] for r in off if r[1] == HOUSE_HEAT_LOSS_SCALE_MAX):+.4f}..{max(r[3] for r in off if r[1] == HOUSE_HEAT_LOSS_SCALE_MAX):+.4f} K")
print(f"RESULT cap_gap_at_scale_2_out0_1z={[r[3] for r in rows if (not r[0]) and r[1] == 2.0 and r[2] == 0.0][0]:+.4f} K")
print(f"RESULT null_cap_gap_abs_max={max(null):.2e} K")
print(f"RESULT hold_ratio_range={min(r[4] for r in rows):.4f}..{max(r[4] for r in rows):.4f}")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(ln.split()[1]) for ln in open("/proc/vmstat") if ln.startswith("pswpin"))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
