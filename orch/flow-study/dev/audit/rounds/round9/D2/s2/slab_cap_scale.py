"""D2-s2 / D2.M3 -- the terminal settlement's steady state ignores the learned heat-loss scale.

Metric (one line): room_drift_Kph = (room after one 1-minute simulate_step - target) / dt at
  pump off, room (two-zone: both zones) at the target and slab at
  optimizer:slab_settlement_cap(params, target, out) -- the cap is documented as the slab
  temperature that SUSTAINS the target, so the drift must be 0; swept over
  house_heat_loss_scale s in {0.3,0.5,0.75,1,1.5,2,3} x out in {-15,-5,0,5} x {1-zone, 2-zone}.
  Null control: s = 1 (the drift is ~0 there).
  Also cap_gap_K = the cap that zeroes the drift (bisected through simulate_step) - the
  production cap, and the slab heat the terminal cost cannot see, slab_mass * cap_gap (kWh).
  And hold_ratio = optimizer:hold_demand_kw / the whole-house demand at the scaled loss.
  count key: the float slab_settlement_cap / hold_demand_kw return (production seams), judged by
  the ThermalModel.simulate_step the same params drive.
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D2/s2/slab_cap_scale.py [--perturb]
Expect (baseline 1936d5ca, box B5): see REPORT, deterministic.
Perturbation (--perturb): in memory, slab_settlement_cap and hold_demand_kw are called with the
  zone losses pre-multiplied by house_heat_loss_scale (the one-factor fix) -> max |drift| and
  |cap_gap| fall to ~0 (direction: to_zero).
Instrumented: optimizer:slab_settlement_cap, optimizer:hold_demand_kw, thermal_model:ThermalModel.simulate_step
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
from profiles import house  # noqa: E402
from heatpump_optimizer import optimizer as optmod  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

PERTURB = "--perturb" in sys.argv
_cap = optmod.slab_settlement_cap
_hold = optmod.hold_demand_kw


def _scaled(params):
    q = copy.copy(params)
    s = params.house_heat_loss_scale
    q.heat_loss_coefficient = params.heat_loss_coefficient * s
    q.upper_floor_heat_loss = params.upper_floor_heat_loss * s
    q.lower_floor_heat_loss = params.lower_floor_heat_loss * s
    return q


def cap_fn(params, target, out):
    return _cap(_scaled(params) if PERTURB else params, target, out)


def hold_fn(params, target, out, solar=0.0):
    return _hold(_scaled(params) if PERTURB else params, target, out, solar)


t0 = time.process_time(); tt0 = time.thread_time()
DT = 1.0 / 60.0


def drift(m, target, out, slab):
    st = ThermalState(room_temperature=target, slab_temperature=slab, outdoor_temperature=out,
                      upper_floor_temperature=target, lower_floor_temperature=target,
                      dhw_temperature=50.0, buffer_tank_temperature=target)
    new = m.simulate_step(st, 0.0, out, 0.0, 0.0, 0.0, DT)
    if m.params.two_zone_enabled:
        return (new.lower_floor_temperature - target) / DT
    return (new.room_temperature - target) / DT


rows = []
null_rows = []
hold_ratios = []
for tz in (False, True):
    for s in (0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0):
        cfg = house(two_zone=tz, dhw=False)
        p = ThermalParameters.from_config(cfg)
        p.house_heat_loss_scale = s
        p.buffer_max_temp = 200.0  # keep the plant bound out of the identity
        m = ThermalModel(p)
        target = 21.0
        for out in (-15.0, -5.0, 0.0, 5.0):
            c = cap_fn(p, target, out)
            d = drift(m, target, out, c)
            lo, hi = target, target + 80.0
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if drift(m, target, out, mid) < 0:
                    lo = mid
                else:
                    hi = mid
            gap = lo - c
            kwh = p.slab_thermal_mass * gap
            (null_rows if s == 1.0 else rows).append((tz, s, out, c, d, gap, kwh))
            # whole-house demand at the loss the dynamics use (no wind/rain)
            if tz:
                u = m.effective_heat_loss_coefficient(p.upper_floor_heat_loss) + \
                    m.effective_heat_loss_coefficient(p.lower_floor_heat_loss_learned)
            else:
                u = m.effective_heat_loss_coefficient(p.heat_loss_coefficient)
            true_d = max(0.0, u * (target - out) - p.internal_gains)
            if true_d > 1e-9:
                hold_ratios.append(hold_fn(p, target, out) / true_d)
for r in rows:
    print(f"# two_zone={r[0]!s:5s} scale={r[1]:4.2f} out={r[2]:6.1f} cap={r[3]:7.3f} drift={r[4]:+8.4f} K/h cap_gap={r[5]:+7.3f} K slab_kwh_unseen={r[6]:+7.3f}")
cpu = time.process_time() - t0; tcpu = time.thread_time() - tt0
print(f"RESULT cells={len(rows)} count")
print(f"RESULT drift_max_abs_Kph={max(abs(r[4]) for r in rows):.4f}")
print(f"RESULT cap_gap_max_K={max(r[5] for r in rows):.3f}")
print(f"RESULT cap_gap_min_K={min(r[5] for r in rows):.3f}")
print(f"RESULT slab_kwh_unseen_max={max(r[6] for r in rows):.3f}")
gaps_up = sorted(r[5] for r in rows if r[1] > 1.0)
print(f"RESULT cap_gap_max_drop_worst_K={gaps_up[-2]:.3f}")
print(f"RESULT null_drift_max_abs_Kph={max(abs(r[4]) for r in null_rows):.2e}")
print(f"RESULT null_cap_gap_max_abs_K={max(abs(r[5]) for r in null_rows):.2e}")
print(f"RESULT hold_ratio_min={min(hold_ratios):.4f}")
print(f"RESULT hold_ratio_max={max(hold_ratios):.4f}")
print(f"RESULT perturbed={int(PERTURB)}")
print(f"RESULT thread_factor={cpu / max(tcpu, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
