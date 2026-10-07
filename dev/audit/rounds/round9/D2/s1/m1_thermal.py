#!/usr/bin/env python3
"""D2.M1 thermal-model sweep (round 9, seat D2-s1).

Metric definitions (one line each, printed as RESULT lines):
  conservation_max_resid_<cfg>  max |sum C*dT - (inputs - losses - refused)*dt| per step, kWh
  parity_mismatch_<cfg>        count of [row, step, store] cells where batch != scalar bits
  mono1_violations_<cfg>       single-step cells where +dP lowers any store (> 1e-12 K)
  monoN_violations_<cfg>       trajectory cells where +dP at step 0 lowers any store later (> 1e-9 K)
  monoN_worst_<cfg>            most negative store response to +dP at step 0 over a horizon, K
  dt_order_<cfg>               err(60 min)/err(15 min) against a 1-min reference (Euler predicts ~4)
  cap_snap_<cfg>               steps where a tank read above the cap moved faster than its uncapped cooling rate
Hooks: thermal_model:ThermalModel.simulate_step, _simulate_step_single,
_simulate_step_two_zone, simulate_trajectory, simulate_trajectory_batch.
Command (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv-r9/bin/python tools/audit/round9/D2/s1/m1_thermal.py
Expected: conservation <= 1e-9 kWh (measured <= 2.1e-13); parity 0; mono 0 on the six
non-wood topologies; two_tank 19 one-step / 52 trajectory (wood valve law and cap refusal,
see report.json non_findings); cap_snap 0; dt_order ~4.8 single/two-zone.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, box B4 (cloud container, linux).
Diagnostic arm (--perturb=carnot_off): sets cop_flow_carnot False on the valved
configs; two_tank monoN stays > 0 (16 / 36), which shows the two-tank drops come
from the wood-share law, not the Carnot COP. This harness backs non-findings only.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import copy
import sys
import time
from dataclasses import replace

import numpy as np

sys.path.insert(0, "custom_components")
from heatpump_optimizer import mixing_valve  # noqa: E402
from heatpump_optimizer import thermal_model as tm  # noqa: E402
from heatpump_optimizer.const import TOPOLOGY_VALVE_UPPER_DIRECT_SLAB  # noqa: E402

PERTURB = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--perturb=")), "")

_t0p, _t0t = time.process_time(), time.thread_time()

CONFIGS = {
    "single": dict(),
    "single_small": dict(room_thermal_mass=0.3, slab_thermal_mass=0.3),
    "two_zone": dict(two_zone_enabled=True),
    "valved": dict(two_zone_enabled=True, mixing_valve_mode=mixing_valve.MODE_MANUAL,
                   buffer_tank_volume=300.0),
    "valved_carnot": dict(two_zone_enabled=True, mixing_valve_mode=mixing_valve.MODE_MANUAL,
                          buffer_tank_volume=35.0, cop_flow_carnot=True),
    "valved_carnot_200": dict(two_zone_enabled=True, mixing_valve_mode=mixing_valve.MODE_MANUAL,
                              buffer_tank_volume=200.0, cop_flow_carnot=True),
    "slab_direct": dict(two_zone_enabled=True, mixing_valve_mode=mixing_valve.MODE_MANUAL,
                        buffer_tank_volume=200.0,
                        topology_layout_override=TOPOLOGY_VALVE_UPPER_DIRECT_SLAB),
    "two_tank": dict(two_zone_enabled=True, mixing_valve_mode=mixing_valve.MODE_MANUAL,
                     buffer_tank_volume=200.0, wood_tank_configured=True,
                     wood_tank_volume=500.0, cop_flow_carnot=True),
}
if PERTURB == "carnot_off":
    for c in CONFIGS.values():
        c.pop("cop_flow_carnot", None)


def params(name):
    return tm.ThermalParameters(**CONFIGS[name])


def rand_state(rng, p):
    tb = rng.uniform(20, 75)
    return tm.ThermalState(
        room_temperature=rng.uniform(15, 25), slab_temperature=rng.uniform(18, 35),
        upper_floor_temperature=rng.uniform(15, 25),
        lower_floor_temperature=rng.uniform(15, 25),
        buffer_tank_temperature=tb,
        wood_tank_temperature=(rng.uniform(15, 94) if p.wood_tank_configured else None),
    )


def enthalpy(m, s):
    p = m.params
    if not p.two_zone_enabled:
        return p.room_thermal_mass * s.room_temperature + p.slab_thermal_mass * s.slab_temperature
    cb = p.buffer_tank_thermal_mass
    if cb < 1e-6:
        cb = 0.04
    h = (p.upper_floor_thermal_mass * s.upper_floor_temperature
         + p.lower_floor_thermal_mass * s.lower_floor_temperature
         + p.slab_thermal_mass * s.slab_temperature + cb * s.buffer_tank_temperature)
    if s.wood_tank_temperature is not None and m.params.two_tank_modelled:
        h += p.wood_tank_thermal_mass * s.wood_tank_temperature
    return h


def net_flow(m, s, P, out, wind, rain, sol, ext, hum):
    """Inputs minus losses (kW) evaluated at the pre-step state s."""
    p = m.params
    if not p.two_zone_enabled:
        cop = m.compute_cop(out, humidity=hum)
        u = m.effective_heat_loss_coefficient(p.heat_loss_coefficient, wind, rain)
        return (cop * P + max(0.0, ext) + p.internal_gains + m.compute_solar_gain(sol)
                - u * (s.room_temperature - out))
    thr = mixing_valve.is_throttling(p.mixing_valve_mode)
    cop = m.compute_cop(out, humidity=hum, flow_temp=s.buffer_tank_temperature if thr else None)
    uu = m.effective_heat_loss_coefficient(p.upper_floor_heat_loss, wind, rain)
    ul = m.effective_heat_loss_coefficient(p.lower_floor_heat_loss_learned, wind * 0.5, rain * 0.5)
    qs_u, qs_l = m.solar_gain_per_zone(sol)
    f = (cop * P + max(0.0, ext) + p.internal_gains + qs_u + qs_l
         - uu * (s.upper_floor_temperature - out) - ul * (s.lower_floor_temperature - out)
         - p.buffer_tank_heat_loss_coefficient * (s.buffer_tank_temperature - 20.0))
    two_tank = thr and p.two_tank_modelled and s.wood_tank_temperature is not None
    if two_tank:
        f -= p.wood_tank_heat_loss_coefficient * (s.wood_tank_temperature - 20.0)
    return f


def conservation(name, rng, n=3000):
    m = tm.ThermalModel(params(name))
    worst = 0.0
    for _ in range(n):
        s = rand_state(rng, m.params)
        P = rng.uniform(0, 6)
        out = rng.uniform(-25, 15)
        wind, rain, sol = rng.uniform(0, 12), rng.uniform(0, 3), rng.uniform(0, 800)
        ext = rng.uniform(0, 15) if rng.random() < 0.5 else 0.0
        dt = 0.25
        n_sub = m._stability_substeps(wind, rain, dt)
        st = s
        resid = 0.0
        for _k in range(n_sub):
            h0 = enthalpy(m, st)
            flow = net_flow(m, st, P, out, wind, rain, sol, ext, None)
            if m.params.two_zone_enabled:
                nxt = m._simulate_step_two_zone(st, P, out, wind, rain, sol, dt / n_sub, ext)
                booked = m._step_buffer_refused + m._step_wood_refused
            else:
                nxt = m._simulate_step_single(st, P, out, wind, rain, sol, dt / n_sub, ext)
                booked = 0.0
            resid += (enthalpy(m, nxt) - h0) - (flow - booked) * (dt / n_sub)
            st = nxt
        # simulate_step must equal the chained sub-steps it claims to run.
        full = m.simulate_step(copy.deepcopy(s), P, out, wind, rain, sol, dt, ext)
        if full.upper_floor_temperature != st.upper_floor_temperature:
            resid = float("inf")
        worst = max(worst, abs(resid))
    return worst


def parity(name, rng, rows=24, steps=48, trials=6):
    m = tm.ThermalModel(params(name))
    mism = 0
    for t in range(trials):
        s0 = rand_state(rng, m.params)
        P = rng.uniform(0, 5, size=(rows, steps))
        out = rng.uniform(-20, 12, size=steps)
        wind = rng.uniform(0, 12, size=steps)
        rain = rng.uniform(0, 3, size=steps)
        sol = rng.uniform(0, 700, size=steps)
        ext = rng.uniform(0, 12, size=steps) * (rng.random(steps) < 0.4)
        vt = rng.uniform(19, 24, size=steps) if t % 2 else None
        hum = rng.uniform(40, 100, size=steps)
        b = m.simulate_trajectory_batch(copy.deepcopy(s0), P, out, wind, rain, sol, 0.25,
                                        ext, vt, hum, None)
        for r in range(rows):
            sc = m.simulate_trajectory(copy.deepcopy(s0), P[r], out, wind, rain, sol, 0.25,
                                       ext, vt, hum, None)
            pairs = [(sc[0], b["room"][r]), (sc[1], b["slab"][r]), (sc[2], b["upper"][r]),
                     (sc[3], b["lower"][r]), (sc[4], b["buffer"][r]), (sc[5], b["refused"][r])]
            if sc[6] is not None:
                pairs.append((sc[6], b["wood"][r]))
            for a, c in pairs:
                mism += int(np.sum(a.view(np.int64) != np.asarray(c, dtype=float).view(np.int64)))
    return mism


def stores(res):
    arrs = [res[0], res[1], res[2], res[3], res[4]]
    if res[6] is not None:
        arrs.append(res[6])
    return np.vstack(arrs)


def mono(name, rng, trials=300, steps=24, dP=0.5):
    m = tm.ThermalModel(params(name))
    one = 0
    many = 0
    worst = 0.0
    for _ in range(trials):
        s0 = rand_state(rng, m.params)
        P = rng.uniform(0, 5, size=steps)
        out = np.full(steps, rng.uniform(-20, 10))
        P2 = P.copy()
        P2[0] += dP
        a = stores(m.simulate_trajectory(copy.deepcopy(s0), P, out))
        b = stores(m.simulate_trajectory(copy.deepcopy(s0), P2, out))
        d = b - a
        if np.min(d[:, 1]) < -1e-12:
            one += 1
        if np.min(d[:, 2:]) < -1e-9:
            many += 1
        worst = min(worst, float(np.min(d)))
    return one, many, worst


def dt_order(name, rng, trials=40):
    m = tm.ThermalModel(params(name))
    ratios = []
    for _ in range(trials):
        s0 = rand_state(rng, m.params)
        P = rng.uniform(0, 4)
        out = rng.uniform(-15, 10)

        def run(dt, n):
            r = m.simulate_trajectory(copy.deepcopy(s0), np.full(n, P), np.full(n, out),
                                      dt_hours=dt)
            return stores(r)[:, -1]
        ref = run(1.0 / 60.0, 60)
        e15 = np.max(np.abs(run(0.25, 4) - ref))
        e60 = np.max(np.abs(run(1.0, 1) - ref))
        if e15 > 1e-6:
            ratios.append(e60 / e15)
    return (float(np.median(ratios)), float(np.max(ratios))) if ratios else (float("nan"),) * 2


def cap_snap(name, rng, trials=500):
    m = tm.ThermalModel(params(name))
    if not mixing_valve.is_throttling(m.params.mixing_valve_mode):
        return None
    bad = 0
    for _ in range(trials):
        s = rand_state(rng, m.params)
        s = replace(s, buffer_tank_temperature=m.params.buffer_max_temp + rng.uniform(0.5, 15))
        out = rng.uniform(-15, 10)
        hot = m.simulate_step(copy.deepcopy(s), rng.uniform(0, 6), out)
        cold = m.simulate_step(copy.deepcopy(s), 0.0, out)
        # capped charge may only hold or cool; never cool faster than P=0
        if hot.buffer_tank_temperature < cold.buffer_tank_temperature - 1e-12:
            bad += 1
    return bad


rng = np.random.default_rng(20260926)
for name in CONFIGS:
    print(f"RESULT conservation_max_resid_{name}={conservation(name, rng):.3e} kWh")
for name in CONFIGS:
    print(f"RESULT parity_mismatch_{name}={parity(name, rng)} cells")
for name in CONFIGS:
    one, many, worst = mono(name, rng)
    print(f"RESULT mono1_violations_{name}={one} trials")
    print(f"RESULT monoN_violations_{name}={many} trials")
    print(f"RESULT monoN_worst_{name}={worst:.4e} K")
for name in CONFIGS:
    med, mx = dt_order(name, rng)
    print(f"RESULT dt_order_{name}={med:.3f} ratio (max {mx:.3f})")
for name in CONFIGS:
    c = cap_snap(name, rng)
    if c is not None:
        print(f"RESULT cap_snap_{name}={c} trials")

pc, tc = time.process_time() - _t0p, time.thread_time() - _t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    with open("/proc/vmstat") as fh:
        sw = next(int(ln.split()[1]) for ln in fh if ln.startswith("pswpin"))
except (OSError, StopIteration):
    sw = -1
print(f"RESULT swapins={sw}")
